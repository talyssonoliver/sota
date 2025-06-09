#!/usr/bin/env python3
"""
Phase 7 Human-in-the-Loop (HITL) Integration Test Suite

Comprehensive tests for all Phase 7 HITL components including:
- HITL policy engine
- Checkpoint management and lifecycle
- Risk assessment algorithms
- Notification systems (dashboard, email, Slack)
- Dashboard widgets and API integration
- Task metadata extension with HITL support
- Workflow integration and automation
"""

import asyncio
import json
import logging
import os
import tempfile
import unittest
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import yaml

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from orchestration.hitl_engine import (
    HITLPolicyEngine, HITLCheckpoint, HITLReviewDecision,
    CheckpointStatus, RiskLevel, HITLAuditEntry
)
from orchestration.notification_handlers import (
    NotificationHandler, DashboardNotificationHandler, 
    EmailNotificationHandler, SlackNotificationHandler
)
from orchestration.hitl_task_metadata import (
    HITLTaskMetadata, HITLCheckpointMetadata, HITLTaskMetadataManager
)
from dashboard.hitl_widgets import (
    HITLPendingReviewsWidget, HITLApprovalActionsWidget,
    HITLMetricsWidget, HITLWorkflowStatusWidget, HITLDashboardManager
)
from api.hitl_routes import create_hitl_blueprint
from flask import Flask


class TestHITLPolicyEngine(unittest.TestCase):
    """Test cases for HITL policy engine core functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create test config
        self.test_config = {
            'global_settings': {
                'default_timeout_hours': 24,
                'escalation_timeout_hours': 72,
                'enable_notifications': True,
                'enable_audit_logging': True
            },
            'checkpoint_triggers': {
                'agent_prompt': {
                    'enabled': True,
                    'risk_threshold': 'medium',
                    'timeout_hours': 24,
                    'required_approvers': 1
                },
                'output_evaluation': {
                    'enabled': True,
                    'risk_threshold': 'high',
                    'timeout_hours': 12,
                    'required_approvers': 2
                }
            },
            'task_type_policies': {
                'backend': {
                    'enabled': True,
                    'default_risk_level': 'medium',
                    'auto_approve_low_risk': True
                }
            },
            'escalation_policies': {
                'high_risk': {
                    'escalation_levels': ['team_lead', 'technical_director'],
                    'notification_channels': ['dashboard', 'email', 'slack']
                }
            }
        }
        
        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "hitl_policies.yaml"
        with open(self.config_path, 'w') as f:
            yaml.dump(self.test_config, f)
        
        self.engine = HITLPolicyEngine(str(self.config_path))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_policy_loading(self):
        """Test policy configuration loading."""
        self.assertIsNotNone(self.engine.policies)
        self.assertEqual(
            self.engine.policies['global_settings']['default_timeout_hours'], 
            24
        )
        self.assertTrue(
            self.engine.policies['checkpoint_triggers']['agent_prompt']['enabled']
        )
    
    def test_checkpoint_creation(self):
        """Test checkpoint creation with proper metadata."""
        checkpoint = self.engine.create_checkpoint(
            task_id="BE-07",
            checkpoint_type="agent_prompt",
            task_type="backend",
            content={"prompt": "Test prompt"},
            risk_factors=["complex_logic", "external_dependency"]
        )
        
        self.assertIsInstance(checkpoint, HITLCheckpoint)
        self.assertEqual(checkpoint.task_id, "BE-07")
        self.assertEqual(checkpoint.checkpoint_type, "agent_prompt")
        self.assertEqual(checkpoint.status, CheckpointStatus.PENDING)
        self.assertIn("complex_logic", checkpoint.risk_factors)
    
    def test_risk_assessment(self):
        """Test risk assessment algorithm."""
        # High risk scenario
        high_risk_factors = ["complex_logic", "external_dependency", "security_sensitive"]
        risk_level = self.engine._assess_risk("backend", high_risk_factors)
        self.assertEqual(risk_level, RiskLevel.HIGH)
        
        # Low risk scenario
        low_risk_factors = ["simple_crud"]
        risk_level = self.engine._assess_risk("backend", low_risk_factors)
        self.assertEqual(risk_level, RiskLevel.LOW)
    
    def test_checkpoint_approval(self):
        """Test checkpoint approval process."""
        checkpoint = self.engine.create_checkpoint(
            task_id="BE-07",
            checkpoint_type="agent_prompt",
            task_type="backend",
            content={"prompt": "Test prompt"}
        )
        
        decision = HITLReviewDecision(
            checkpoint_id=checkpoint.checkpoint_id,
            decision="approve",
            reviewer_id="test_reviewer",
            comments="Looks good",
            reviewed_at=datetime.now()
        )
        
        result = asyncio.run(self.engine.process_decision(decision))
        self.assertTrue(result)
          # Verify checkpoint status updated
        updated_checkpoint = self.engine.get_checkpoint(checkpoint.checkpoint_id)
        self.assertEqual(updated_checkpoint.status, CheckpointStatus.APPROVED)
    
    def test_checkpoint_rejection(self):
        """Test checkpoint rejection process."""
        checkpoint = self.engine.create_checkpoint(
            task_id="BE-07",
            checkpoint_type="output_evaluation",
            task_type="backend",
            content={"output": "test output"}
        )
        
        decision = HITLReviewDecision(
            checkpoint_id=checkpoint.checkpoint_id,
            decision="reject",
            reviewer_id="test_reviewer",
            comments="Needs improvement",
            reviewed_at=datetime.now()
        )
                
        result = asyncio.run(self.engine.process_decision(decision))
        self.assertTrue(result)
        
        # Verify checkpoint status updated
        updated_checkpoint = self.engine.get_checkpoint(checkpoint.checkpoint_id)
        self.assertEqual(updated_checkpoint.status, CheckpointStatus.REJECTED)
    
    def test_timeout_handling(self):
        """Test checkpoint timeout handling."""
        # Create checkpoint with past timeout
        checkpoint = self.engine.create_checkpoint(
            task_id="BE-07",
            checkpoint_type="agent_prompt",
            task_type="backend",
            content={"prompt": "Test prompt"}
        )
        checkpoint.created_at = datetime.now() - timedelta(hours=25)
          # Process timeouts
        timed_out = self.engine.process_timeouts()
        self.assertTrue(len(timed_out) > 0)
        
        # Verify checkpoint was escalated
        updated_checkpoint = self.engine.get_checkpoint(checkpoint.checkpoint_id)
        self.assertEqual(updated_checkpoint.status, CheckpointStatus.ESCALATED)
    
    def test_audit_logging(self):
        """Test audit logging functionality."""
        checkpoint = self.engine.create_checkpoint(
            task_id="BE-07",
            checkpoint_type="agent_prompt",
            task_type="backend",
            content={"prompt": "Test prompt"}        )
        
        # Process a decision to create audit entry
        decision = HITLReviewDecision(
            checkpoint_id=checkpoint.checkpoint_id,
            decision="approve",
            reviewer_id="test_reviewer",
            comments="Approved",
            reviewed_at=datetime.now()
        )
        
        asyncio.run(self.engine.process_decision(decision))
        
        # Verify audit entries created
        audit_entries = self.engine.get_audit_trail(checkpoint.checkpoint_id)
        self.assertTrue(len(audit_entries) >= 2)
        
        # Check that we have both 'created' and 'approved' entries
        actions = [entry.action for entry in audit_entries]
        self.assertIn("created", actions)
        self.assertIn("approved", actions)
        
        # The approved action should be the latest (last in chronological order)
        self.assertEqual(audit_entries[-1].action, "approved")
    
    def test_auto_approval_low_risk(self):
        """Test automatic approval of low-risk checkpoints."""
        checkpoint = self.engine.create_checkpoint(
            task_id="BE-07",
            checkpoint_type="agent_prompt",
            task_type="backend",
            content={"prompt": "Simple CRUD operation"},
            risk_factors=["simple_crud"]
        )
        
        # Low risk should be auto-approved based on policy
        self.assertEqual(checkpoint.status, CheckpointStatus.APPROVED)


class TestNotificationHandlers(unittest.TestCase):
    """Test cases for notification system."""
    
    def setUp(self):
        """Set up test environment."""
        self.checkpoint = HITLCheckpoint(
            checkpoint_id="test-checkpoint-1",
            task_id="BE-07",
            checkpoint_type="agent_prompt",
            task_type="backend",
            content={"prompt": "Test prompt"},
            risk_level=RiskLevel.MEDIUM,
            status=CheckpointStatus.PENDING,
            created_at=datetime.now()
        )
    
    def test_dashboard_notification_handler(self):
        """Test dashboard notification handler."""
        handler = DashboardNotificationHandler()
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            
            result = handler.send_notification(
                checkpoint=self.checkpoint,
                notification_type="checkpoint_created",
                recipients=["dashboard"],
                metadata={"url": "http://localhost:5000"}
            )
            
            self.assertTrue(result)
            mock_post.assert_called_once()
    
    def test_email_notification_handler(self):
        """Test email notification handler."""
        config = {
            'smtp_server': 'smtp.test.com',
            'smtp_port': 587,
            'username': 'test@test.com',
            'password': 'password',
            'from_email': 'test@test.com'
        }
        
        handler = EmailNotificationHandler(config)
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = handler.send_notification(
                checkpoint=self.checkpoint,
                notification_type="checkpoint_created",
                recipients=["reviewer@test.com"],
                metadata={}
            )
            
            self.assertTrue(result)
            mock_server.send_message.assert_called_once()
    
    def test_slack_notification_handler(self):
        """Test Slack notification handler."""
        config = {'webhook_url': 'https://hooks.slack.com/test'}
        handler = SlackNotificationHandler(config)
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            
            result = handler.send_notification(
                checkpoint=self.checkpoint,
                notification_type="checkpoint_created",
                recipients=["#engineering"],
                metadata={}
            )
            
            self.assertTrue(result)
            mock_post.assert_called_once()


class TestHITLTaskMetadata(unittest.TestCase):
    """Test cases for HITL task metadata extension."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir) / "hitl_metadata"
        self.manager = HITLTaskMetadataManager(str(self.storage_path))
        
        self.test_metadata = HITLTaskMetadata(
            task_id="BE-07",
            hitl_enabled=True,
            risk_assessment={
                "level": "medium",
                "factors": ["complex_logic"],
                "score": 65
            },
            current_phase="agent_prompt",
            checkpoints=[]
        )
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_metadata_storage_and_retrieval(self):
        """Test storing and retrieving HITL metadata."""
        # Store metadata
        self.manager.store_metadata(self.test_metadata)
        
        # Retrieve metadata
        retrieved = self.manager.get_metadata("BE-07")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.task_id, "BE-07")
        self.assertTrue(retrieved.hitl_enabled)
        self.assertEqual(retrieved.risk_assessment["level"], "medium")
    
    def test_checkpoint_tracking(self):
        """Test checkpoint tracking in metadata."""
        checkpoint = HITLCheckpointMetadata(
            checkpoint_id="checkpoint-1",
            checkpoint_type="agent_prompt",
            status="pending",
            created_at=datetime.now(),
            risk_level="medium"
        )
        
        self.test_metadata.checkpoints.append(checkpoint)
        self.manager.store_metadata(self.test_metadata)
        
        # Retrieve and verify checkpoint
        retrieved = self.manager.get_metadata("BE-07")
        self.assertEqual(len(retrieved.checkpoints), 1)
        self.assertEqual(retrieved.checkpoints[0].checkpoint_id, "checkpoint-1")
    
    def test_phase_tracking(self):
        """Test workflow phase tracking."""
        self.test_metadata.current_phase = "output_evaluation"
        self.manager.store_metadata(self.test_metadata)
        
        retrieved = self.manager.get_metadata("BE-07")
        self.assertEqual(retrieved.current_phase, "output_evaluation")
    
    def test_serialization(self):
        """Test metadata serialization and deserialization."""
        # Test to_dict
        data = self.test_metadata.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["task_id"], "BE-07")
        
        # Test from_dict
        reconstructed = HITLTaskMetadata.from_dict(data)
        self.assertEqual(reconstructed.task_id, "BE-07")
        self.assertEqual(reconstructed.risk_assessment["level"], "medium")


class TestHITLDashboardWidgets(unittest.TestCase):
    """Test cases for HITL dashboard widgets."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_hitl_engine = MagicMock()
        self.mock_checkpoints = [
            HITLCheckpoint(
                checkpoint_id="checkpoint-1",
                task_id="BE-07",
                checkpoint_type="agent_prompt",
                task_type="backend",
                content={"prompt": "Test"},
                risk_level=RiskLevel.MEDIUM,
                status=CheckpointStatus.PENDING,
                created_at=datetime.now()
            )
        ]
        self.mock_hitl_engine.get_pending_checkpoints.return_value = self.mock_checkpoints
    
    def test_pending_reviews_widget(self):
        """Test pending reviews widget."""
        widget = HITLPendingReviewsWidget()
        
        with patch.object(widget, 'hitl_engine', self.mock_hitl_engine):
            data = widget.get_data()
            
            self.assertIn('pending_reviews', data)
            self.assertEqual(len(data['pending_reviews']), 1)
            self.assertEqual(data['pending_reviews'][0]['checkpoint_id'], 'checkpoint-1')
    
    def test_approval_actions_widget(self):
        """Test approval actions widget."""
        widget = HITLApprovalActionsWidget()
        
        with patch.object(widget, 'hitl_engine', self.mock_hitl_engine):
            # Test approval action
            result = widget.process_action('checkpoint-1', 'approve', 'test_reviewer', 'Good to go')
            self.assertTrue(result)
            
            # Verify engine method called
            self.mock_hitl_engine.process_decision.assert_called_once()
    
    def test_metrics_widget(self):
        """Test HITL metrics widget."""
        widget = HITLMetricsWidget()
        
        mock_metrics = {
            'total_checkpoints': 10,
            'pending_count': 3,
            'approved_count': 6,
            'rejected_count': 1,
            'average_review_time': 2.5
        }
        
        with patch.object(widget, 'hitl_engine') as mock_engine:
            mock_engine.get_metrics.return_value = mock_metrics
            
            data = widget.get_data()
            
            self.assertEqual(data['metrics']['total_checkpoints'], 10)
            self.assertEqual(data['metrics']['pending_count'], 3)
    
    def test_workflow_status_widget(self):
        """Test workflow status widget with HITL integration."""
        widget = HITLWorkflowStatusWidget()
        
        mock_status = {
            'current_phase': 'agent_prompt',
            'hitl_checkpoints': ['checkpoint-1'],
            'blocked_on_review': True,
            'next_checkpoint': 'output_evaluation'
        }
        
        with patch.object(widget, 'get_workflow_status', return_value=mock_status):
            data = widget.get_data()
            
            self.assertEqual(data['workflow_status']['current_phase'], 'agent_prompt')
            self.assertTrue(data['workflow_status']['blocked_on_review'])
    
    def test_dashboard_manager(self):
        """Test HITL dashboard manager coordination."""
        manager = HITLDashboardManager()
        
        with patch.object(manager, 'hitl_engine', self.mock_hitl_engine):
            dashboard_data = manager.get_dashboard_data()
            
            self.assertIn('pending_reviews', dashboard_data)
            self.assertIn('metrics', dashboard_data)
            self.assertIn('workflow_status', dashboard_data)


class TestHITLAPIRoutes(unittest.TestCase):
    """Test cases for HITL API routes."""
    
    def setUp(self):
        """Set up test Flask app with HITL routes."""
        self.app = Flask(__name__)
        self.mock_hitl_engine = MagicMock()
        
        # Register HITL blueprint with mocked engine
        hitl_bp = create_hitl_blueprint(self.mock_hitl_engine)
        self.app.register_blueprint(hitl_bp, url_prefix='/api/hitl')
        
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    def test_get_checkpoints_endpoint(self):
        """Test getting checkpoints via API."""
        mock_checkpoints = [
            {
                'checkpoint_id': 'checkpoint-1',
                'task_id': 'BE-07',
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        self.mock_hitl_engine.get_pending_checkpoints.return_value = mock_checkpoints
        
        response = self.client.get('/api/hitl/checkpoints')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('checkpoints', data)
        self.assertEqual(len(data['checkpoints']), 1)
    
    def test_approve_checkpoint_endpoint(self):
        """Test approving checkpoint via API."""
        self.mock_hitl_engine.process_decision.return_value = True
        
        response = self.client.post('/api/hitl/checkpoints/checkpoint-1/approve', 
                                   json={
                                       'reviewer_id': 'test_reviewer',
                                       'comments': 'Approved'
                                   })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_reject_checkpoint_endpoint(self):
        """Test rejecting checkpoint via API."""
        self.mock_hitl_engine.process_decision.return_value = True
        
        response = self.client.post('/api/hitl/checkpoints/checkpoint-1/reject',
                                   json={
                                       'reviewer_id': 'test_reviewer',
                                       'comments': 'Needs work'
                                   })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_get_metrics_endpoint(self):
        """Test getting HITL metrics via API."""
        mock_metrics = {
            'total_checkpoints': 10,
            'pending_count': 3,
            'approved_count': 6,
            'rejected_count': 1
        }
        
        self.mock_hitl_engine.get_metrics.return_value = mock_metrics
        
        response = self.client.get('/api/hitl/metrics')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['metrics']['total_checkpoints'], 10)
    
    def test_batch_approve_endpoint(self):
        """Test batch approval via API."""
        self.mock_hitl_engine.process_decision.return_value = True
        
        response = self.client.post('/api/hitl/checkpoints/batch/approve',
                                   json={
                                       'checkpoint_ids': ['checkpoint-1', 'checkpoint-2'],
                                       'reviewer_id': 'test_reviewer',
                                       'comments': 'Batch approved'
                                   })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['processed_count'], 2)


class TestHITLWorkflowIntegration(unittest.TestCase):
    """Test cases for HITL workflow integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        config_path = Path(self.temp_dir) / "hitl_policies.yaml"
        
        # Create minimal config
        config = {
            'global_settings': {'default_timeout_hours': 24},
            'checkpoint_triggers': {
                'agent_prompt': {'enabled': True, 'risk_threshold': 'medium'}
            },
            'task_type_policies': {
                'backend': {'enabled': True, 'auto_approve_low_risk': True}
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        self.hitl_engine = HITLPolicyEngine(str(config_path))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_workflow_checkpoint_trigger(self):
        """Test triggering checkpoints in workflow phases."""
        # Simulate workflow reaching checkpoint trigger
        checkpoint = self.hitl_engine.create_checkpoint(
            task_id="BE-07",
            checkpoint_type="agent_prompt",
            task_type="backend",
            content={"prompt": "Create new API endpoint"},
            risk_factors=["api_design", "security"]
        )
        
        self.assertIsNotNone(checkpoint)
        self.assertEqual(checkpoint.checkpoint_type, "agent_prompt")
        self.assertEqual(checkpoint.status, CheckpointStatus.PENDING)
    
    def test_workflow_progression_blocking(self):
        """Test that workflow blocks on pending checkpoints."""
        # Create pending checkpoint
        checkpoint = self.hitl_engine.create_checkpoint(
            task_id="BE-07",
            checkpoint_type="output_evaluation",
            task_type="backend",
            content={"output": "Generated code"},
            risk_factors=["complex_logic"]
        )
        
        # Check if task should be blocked
        pending_checkpoints = self.hitl_engine.get_pending_checkpoints_for_task("BE-07")
        self.assertTrue(len(pending_checkpoints) > 0)
        
        # Workflow should be blocked until approval
        self.assertEqual(checkpoint.status, CheckpointStatus.PENDING)
    
    def test_workflow_progression_after_approval(self):
        """Test that workflow continues after checkpoint approval."""
        # Create and approve checkpoint
        checkpoint = self.hitl_engine.create_checkpoint(
            task_id="BE-07",
            checkpoint_type="agent_prompt",
            task_type="backend",
        )
        
        decision = HITLReviewDecision(
            checkpoint_id=checkpoint.checkpoint_id,
            decision="approve",
            reviewer_id="test_reviewer",
            comments="Good to go",
            reviewed_at=datetime.now()
        )
        
        asyncio.run(self.hitl_engine.process_decision(decision))
        
        # Verify no pending checkpoints for task
        pending_checkpoints = self.hitl_engine.get_pending_checkpoints_for_task("BE-07")
        self.assertEqual(len(pending_checkpoints), 0)


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Create test suite
    test_classes = [
        TestHITLPolicyEngine,
        TestNotificationHandlers,
        TestHITLTaskMetadata,
        TestHITLDashboardWidgets,
        TestHITLAPIRoutes,
        TestHITLWorkflowIntegration
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Phase 7 HITL Test Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
    
    # Exit with error code if tests failed
    if result.failures or result.errors:
        sys.exit(1)
