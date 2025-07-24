"""
Integration tests for Human-in-the-Loop (HITL) System with other components.

Tests the complete HITL workflow, including:
- Human approval workflows
- Checkpoint creation and management
- Dashboard integration for approvals
- Notification system integration
- Timeout and escalation handling
"""

# Add project root to path
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.workflows.hitl.policy_engine import HITLPolicyEngine
from src.core.workflows.hitl.types import CheckpointStatus
from src.core.workflows.notification_handlers import NotificationHandler
from src.infrastructure.utils.escalation_system import EscalationEngine


@pytest.fixture
def integration_environment():
    """Set up integration test environment for HITL system."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create HITL storage
        hitl_dir = Path(temp_dir) / "hitl"
        hitl_dir.mkdir(parents=True, exist_ok=True)

        # Create HITL policy configuration
        hitl_config = {
            "checkpoint_triggers": {
                "high_risk_operation": {
                    "risk_level": "HIGH",
                    "requires_approval": True,
                    "timeout_hours": 2,
                    "approvers": ["tech_lead", "security_team"],
                },
                "production_deployment": {
                    "risk_level": "CRITICAL",
                    "requires_approval": True,
                    "timeout_hours": 1,
                    "approvers": ["tech_lead", "ops_team", "security_team"],
                },
                "data_migration": {
                    "risk_level": "HIGH",
                    "requires_approval": True,
                    "timeout_hours": 4,
                    "approvers": ["data_team", "tech_lead"],
                },
            },
            "escalation_policies": {
                "HIGH": {
                    "escalate_after_minutes": 60,
                    "escalate_to": ["manager", "director"],
                },
                "CRITICAL": {
                    "escalate_after_minutes": 30,
                    "escalate_to": ["director", "vp_engineering"],
                },
            },
            "notification_settings": {
                "channels": ["email", "slack", "dashboard"],
                "reminder_interval_minutes": 30,
            },
        }

        # Write config
        config_file = hitl_dir / "hitl_policies.yaml"
        with open(config_file, "w") as f:
            yaml.dump(hitl_config, f)

        # Create test checkpoints
        test_checkpoints = [
            {
                "id": "CHK-001",
                "task_id": "BE-05",
                "checkpoint_type": "high_risk_operation",
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "context": {
                    "operation": "Delete user data",
                    "affected_records": 1000,
                    "requester": "backend_service",
                },
            },
            {
                "id": "CHK-002",
                "task_id": "OPS-01",
                "checkpoint_type": "production_deployment",
                "status": "approved",
                "created_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                "approved_by": "john.doe@example.com",
                "approved_at": datetime.now().isoformat(),
                "context": {
                    "version": "v2.1.0",
                    "changes": ["API updates", "Database migrations"],
                },
            },
        ]

        yield {
            "temp_dir": temp_dir,
            "hitl_dir": hitl_dir,
            "hitl_config": hitl_config,
            "config_file": config_file,
            "test_checkpoints": test_checkpoints,
        }


class TestHITLIntegration(unittest.TestCase):
    """Integration tests for HITL System."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        config_path = Path(self.temp_dir) / "hitl_policies.yaml"

        # Create minimal config
        config = {
            "checkpoint_triggers": {},
            "global_settings": {"default_timeout_hours": 24},
        }
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        self.hitl_engine = HITLPolicyEngine(config_path=str(config_path))
        self.mock_escalation = Mock(spec=EscalationEngine)
        self.mock_notifier = Mock(spec=NotificationHandler)

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_complete_approval_workflow(self):
        """Test end-to-end human approval workflow."""
        # Create checkpoint requiring approval
        checkpoint = await self.hitl_engine.create_checkpoint(
            task_id="TEST-01",
            checkpoint_type="high_risk_operation",
            context={
                "operation": "Bulk data update",
                "affected_records": 5000,
                "risk_assessment": "Potential data loss if misconfigured",
            },
        )

        # Verify checkpoint created
        self.assertEqual(checkpoint.status, CheckpointStatus.PENDING)
        self.assertTrue(checkpoint.requires_approval)

        # Simulate notification to approvers
        with patch.object(self.hitl_engine, "notify_approvers") as mock_notify:
            mock_notify.return_value = {
                "email": {"sent": 2, "failed": 0},
                "slack": {"posted": True},
                "dashboard": {"updated": True},
            }

            # Send approval request
            notification_result = await self.hitl_engine.request_approval(checkpoint.id)

            # Verify notifications sent
            mock_notify.assert_called_once()
            self.assertEqual(notification_result["email"]["sent"], 2)

        # Simulate dashboard interaction
        with patch(
            "src.interfaces.dashboard.components.hitl_widgets.HITLApprovalWidget"
        ) as mock_widget:
            widget = mock_widget.return_value

            # Dashboard displays pending approval
            pending_approvals = await self.hitl_engine.get_pending_approvals()
            widget.display_approvals(pending_approvals)

            # User approves via dashboard
            approval_data = {
                "checkpoint_id": checkpoint.id,
                "approved_by": "tech.lead@example.com",
                "comments": "Reviewed and approved. Proceed with caution.",
                "conditions": ["Monitor closely", "Rollback plan ready"],
            }

            # Process approval
            result = await self.hitl_engine.process_approval(
                checkpoint.id,
                approved_by=approval_data["approved_by"],
                comments=approval_data["comments"],
                conditions=approval_data["conditions"],
            )

            # Verify approval processed
            self.assertEqual(result.status, CheckpointStatus.APPROVED)
            self.assertEqual(result.approved_by, "tech.lead@example.com")
            self.assertIsNotNone(result.approved_at)

    async def test_checkpoint_timeout_and_escalation(self):
        """Test checkpoint timeout detection and escalation."""
        # Create checkpoint with short timeout
        checkpoint = await self.hitl_engine.create_checkpoint(
            task_id="TEST-02",
            checkpoint_type="production_deployment",
            context={"version": "v3.0.0"},
            timeout_minutes=1,  # 1 minute timeout for testing
        )

        # Mock time passage
        with patch("time.time") as mock_time:
            current_time = time.time()
            mock_time.return_value = current_time

            # Initially not timed out
            is_timed_out = await self.hitl_engine.check_timeout(checkpoint.id)
            self.assertFalse(is_timed_out)

            # Advance time past timeout
            mock_time.return_value = current_time + 120  # 2 minutes later

            # Check timeout
            is_timed_out = await self.hitl_engine.check_timeout(checkpoint.id)
            self.assertTrue(is_timed_out)

            # Mock escalation system
            with patch.object(
                self.hitl_engine, "escalation_system", self.mock_escalation
            ):
                # Process timeout (should trigger escalation)
                escalation_result = await self.hitl_engine.handle_timeout(checkpoint.id)
                # Verify timeout handling completed
                self.assertIsNotNone(escalation_result)

                # Verify escalation created
                self.mock_escalation.create_escalation.assert_called_once()
                call_args = self.mock_escalation.create_escalation.call_args

                self.assertIn("HITL Approval Timeout", call_args[1]["title"])
                self.assertEqual(call_args[1]["priority"], "HIGH")
                self.assertEqual(
                    call_args[1]["context"]["checkpoint_id"], checkpoint.id
                )

    async def test_multi_approver_workflow(self):
        """Test checkpoints requiring multiple approvals."""
        # Create checkpoint requiring multiple approvers
        checkpoint = await self.hitl_engine.create_checkpoint(
            task_id="TEST-03",
            checkpoint_type="data_migration",
            context={
                "source_db": "production",
                "target_db": "analytics",
                "records": 1000000,
            },
            required_approvers=["data_team", "security_team", "tech_lead"],
        )

        # First approval
        result1 = await self.hitl_engine.process_approval(
            checkpoint.id,
            approved_by="data.engineer@example.com",
            approver_role="data_team",
        )

        # Should still be pending (needs more approvals)
        self.assertEqual(result1.status, CheckpointStatus.PENDING)
        self.assertEqual(len(result1.approvals), 1)

        # Second approval
        result2 = await self.hitl_engine.process_approval(
            checkpoint.id,
            approved_by="security.analyst@example.com",
            approver_role="security_team",
        )

        # Still pending (needs one more)
        self.assertEqual(result2.status, CheckpointStatus.PENDING)
        self.assertEqual(len(result2.approvals), 2)

        # Final approval
        result3 = await self.hitl_engine.process_approval(
            checkpoint.id,
            approved_by="tech.lead@example.com",
            approver_role="tech_lead",
        )

        # Now fully approved
        self.assertEqual(result3.status, CheckpointStatus.APPROVED)
        self.assertEqual(len(result3.approvals), 3)

    async def test_rejection_workflow(self):
        """Test checkpoint rejection and handling."""
        # Create checkpoint
        checkpoint = await self.hitl_engine.create_checkpoint(
            task_id="TEST-04",
            checkpoint_type="high_risk_operation",
            context={"operation": "Purge old data"},
        )

        # Reject checkpoint
        rejection_result = await self.hitl_engine.process_rejection(
            checkpoint.id,
            rejected_by="security.lead@example.com",
            reason="Missing data retention compliance check",
            recommendations=[
                "Add compliance verification step",
                "Document retention policy adherence",
                "Get legal team approval",
            ],
        )

        # Verify rejection
        self.assertEqual(rejection_result.status, CheckpointStatus.REJECTED)
        self.assertEqual(rejection_result.rejected_by, "security.lead@example.com")
        self.assertIsNotNone(rejection_result.rejection_reason)

        # Test task should be blocked
        can_proceed = await self.hitl_engine.can_task_proceed("TEST-04")
        self.assertFalse(can_proceed)

        # Test notification of rejection
        with patch.object(self.hitl_engine, "notify_rejection") as mock_notify:
            await self.hitl_engine.notify_task_owner(checkpoint.id, "rejection")

            mock_notify.assert_called_once()

    async def test_dashboard_integration(self):
        """Test HITL integration with dashboard components."""
        # Create multiple checkpoints
        checkpoints = []
        for i in range(5):
            cp = await self.hitl_engine.create_checkpoint(
                task_id=f"TEST-{i:02d}",
                checkpoint_type="high_risk_operation",
                context={"index": i},
            )
            checkpoints.append(cp)

        # Approve some checkpoints
        for i in [0, 2]:
            await self.hitl_engine.process_approval(
                checkpoints[i].id, approved_by="approver@example.com"
            )

        # Mock dashboard widget
        with patch(
            "src.interfaces.dashboard.components.hitl_widgets.HITLApprovalWidget"
        ) as mock_widget:
            widget = mock_widget.return_value

            # Get dashboard data
            dashboard_data = await self.hitl_engine.get_dashboard_data()

            # Verify data structure
            self.assertIn("pending_approvals", dashboard_data)
            self.assertIn("recent_approvals", dashboard_data)
            self.assertIn("metrics", dashboard_data)

            self.assertEqual(dashboard_data["metrics"]["total_checkpoints"], 5)
            self.assertEqual(dashboard_data["metrics"]["pending_count"], 3)
            self.assertEqual(dashboard_data["metrics"]["approved_count"], 2)

            # Widget updates with data
            widget.update_display(dashboard_data)
            widget.update_display.assert_called_once()

    async def test_concurrent_approval_handling(self):
        """Test handling of concurrent approval attempts."""
        # Create checkpoint
        checkpoint = await self.hitl_engine.create_checkpoint(
            task_id="TEST-CONCURRENT", checkpoint_type="high_risk_operation"
        )

        # Simulate concurrent approval attempts
        import asyncio

        async def approve_concurrent(approver_id):
            """Attempt to approve concurrently."""
            try:
                result = await self.hitl_engine.process_approval(
                    checkpoint.id, approved_by=f"approver{approver_id}@example.com"
                )
                return (approver_id, "success", result)
            except Exception as e:
                return (approver_id, "error", str(e))

        # Launch concurrent approvals
        tasks = [approve_concurrent(i) for i in range(3)]

        results = await asyncio.gather(*tasks)

        # Only one should succeed
        successes = [r for r in results if r[1] == "success"]
        self.assertEqual(len(successes), 1)

        # Verify final state
        final_checkpoint = await self.hitl_engine.get_checkpoint(checkpoint.id)
        self.assertEqual(final_checkpoint.status, CheckpointStatus.APPROVED)
        self.assertEqual(len(final_checkpoint.approvals), 1)

    async def test_notification_integration(self):
        """Test HITL notification system integration."""
        # Create checkpoint
        checkpoint = await self.hitl_engine.create_checkpoint(
            task_id="TEST-NOTIFY",
            checkpoint_type="production_deployment",
            context={"urgency": "high"},
        )

        # Mock notification channels
        mock_channels = {
            "email": Mock(return_value={"sent": True}),
            "slack": Mock(return_value={"posted": True}),
            "dashboard": Mock(return_value={"updated": True}),
        }

        with patch.object(self.hitl_engine, "notification_channels", mock_channels):
            # Send initial notification
            await self.hitl_engine.notify_approvers(checkpoint.id)

            # Verify all channels notified
            for channel, mock_handler in mock_channels.items():
                mock_handler.assert_called()

            # Test reminder notifications
            await self.hitl_engine.send_reminder(checkpoint.id)

            # Each channel should be called twice now
            for channel, mock_handler in mock_channels.items():
                self.assertEqual(mock_handler.call_count, 2)

    async def test_audit_trail(self):
        """Test HITL audit trail functionality."""
        # Create checkpoint
        checkpoint = await self.hitl_engine.create_checkpoint(
            task_id="TEST-AUDIT",
            checkpoint_type="data_migration",
            context={"sensitivity": "high"},
        )

        # Perform various actions
        actions = [
            ("request_approval", {"requested_by": "system"}),
            ("add_comment", {"by": "reviewer1", "comment": "Needs review"}),
            ("add_comment", {"by": "reviewer2", "comment": "LGTM"}),
            ("approve", {"by": "tech.lead@example.com"}),
        ]

        for action, metadata in actions:
            await self.hitl_engine.add_audit_entry(checkpoint.id, action, metadata)

        # Get audit trail
        audit_trail = await self.hitl_engine.get_audit_trail(checkpoint.id)

        # Verify all actions recorded
        self.assertEqual(len(audit_trail), len(actions))

        # Verify chronological order
        timestamps = [entry["timestamp"] for entry in audit_trail]
        self.assertEqual(timestamps, sorted(timestamps))

        # Verify action details
        action_types = [entry["action"] for entry in audit_trail]
        expected_actions = [a[0] for a in actions]
        self.assertEqual(action_types, expected_actions)

    async def test_performance_with_many_checkpoints(self):
        """Test HITL system performance with many checkpoints."""
        import time

        # Create many checkpoints
        num_checkpoints = 100
        start_time = time.time()

        checkpoints = []
        for i in range(num_checkpoints):
            cp = await self.hitl_engine.create_checkpoint(
                task_id=f"PERF-{i:03d}",
                checkpoint_type="high_risk_operation",
                context={"index": i},
            )
            checkpoints.append(cp)

        creation_time = time.time() - start_time
        avg_creation = creation_time / num_checkpoints

        # Should handle high volume efficiently
        self.assertLess(avg_creation, 0.01)  # < 10ms per checkpoint

        # Test query performance
        start_time = time.time()
        pending = await self.hitl_engine.get_pending_approvals()
        query_time = time.time() - start_time

        # Query should be fast
        self.assertLess(query_time, 0.1)  # < 100ms
        self.assertEqual(len(pending), num_checkpoints)

        # Test bulk operations
        start_time = time.time()

        # Approve half of them
        for i in range(0, num_checkpoints, 2):
            await self.hitl_engine.process_approval(
                checkpoints[i].id, approved_by="bulk.approver@example.com"
            )

        bulk_time = time.time() - start_time
        avg_approval = bulk_time / (num_checkpoints // 2)

        # Bulk operations should be efficient
        self.assertLess(avg_approval, 0.02)  # < 20ms per approval


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
