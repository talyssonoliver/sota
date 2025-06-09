#!/usr/bin/env python3
"""
HITL Engine Integration Tests

Focused tests for HITL engine integration with existing system components.
"""

import unittest
import asyncio
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys

sys.path.append(str(Path(__file__).parent.parent))

from orchestration.hitl_engine import HITLPolicyEngine, HITLCheckpoint, CheckpointStatus, RiskLevel
from orchestration.states import TaskStatus


class TestHITLEngineIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for HITL engine with existing components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create comprehensive test config
        self.test_config = {
            'global_settings': {
                'default_timeout_hours': 24,
                'escalation_timeout_hours': 72,
                'enable_notifications': True,
                'enable_audit_logging': True,
                'max_retries': 3
            },
            'checkpoint_triggers': {
                'agent_prompt': {
                    'enabled': True,
                    'risk_threshold': 'medium',
                    'timeout_hours': 24,
                    'required_approvers': 1,
                    'auto_approve_patterns': ['simple_crud', 'documentation_update']
                },
                'output_evaluation': {
                    'enabled': True,
                    'risk_threshold': 'high',
                    'timeout_hours': 12,
                    'required_approvers': 2,
                    'critical_patterns': ['security_config', 'database_migration']
                },
                'qa_validation': {
                    'enabled': True,
                    'risk_threshold': 'medium',
                    'timeout_hours': 8,
                    'required_approvers': 1
                },
                'documentation': {
                    'enabled': False,  # Disabled for low-risk documentation
                    'risk_threshold': 'low',
                    'timeout_hours': 48,
                    'required_approvers': 1
                },
                'task_transitions': {
                    'enabled': True,
                    'risk_threshold': 'high',
                    'timeout_hours': 6,
                    'required_approvers': 2
                }
            },
            'task_type_policies': {
                'backend': {
                    'enabled': True,
                    'default_risk_level': 'medium',
                    'auto_approve_low_risk': True,
                    'risk_patterns': {
                        'high': ['security_config', 'auth_implementation', 'database_migration'],
                        'medium': ['api_endpoint', 'business_logic', 'integration'],
                        'low': ['simple_crud', 'data_formatting', 'validation']
                    }
                },
                'frontend': {
                    'enabled': True,
                    'default_risk_level': 'low',
                    'auto_approve_low_risk': True,
                    'risk_patterns': {
                        'high': ['authentication_ui', 'payment_flow', 'admin_interface'],
                        'medium': ['complex_form', 'data_visualization', 'user_workflow'],
                        'low': ['styling', 'static_content', 'simple_component']
                    }
                },
                'design': {
                    'enabled': False,  # Design tasks typically low risk
                    'default_risk_level': 'low',
                    'auto_approve_low_risk': True
                },
                'infrastructure': {
                    'enabled': True,
                    'default_risk_level': 'high',
                    'auto_approve_low_risk': False,
                    'risk_patterns': {
                        'high': ['production_deployment', 'security_config', 'database_config'],
                        'medium': ['staging_deployment', 'monitoring_setup', 'backup_config'],
                        'low': ['documentation', 'logging_config']
                    }
                },
                'qa': {
                    'enabled': True,
                    'default_risk_level': 'medium',
                    'auto_approve_low_risk': True
                }
            },
            'escalation_policies': {
                'high_risk': {
                    'escalation_levels': ['team_lead', 'technical_director', 'cto'],
                    'notification_channels': ['dashboard', 'email', 'slack'],
                    'escalation_delay_hours': 8
                },
                'medium_risk': {
                    'escalation_levels': ['team_lead', 'technical_director'],
                    'notification_channels': ['dashboard', 'email'],
                    'escalation_delay_hours': 24
                },
                'low_risk': {
                    'escalation_levels': ['team_lead'],
                    'notification_channels': ['dashboard'],
                    'escalation_delay_hours': 48
                }
            },
            'notification_templates': {
                'checkpoint_created': {
                    'subject': 'Review Required: {task_id} - {checkpoint_type}',
                    'body': 'A new HITL checkpoint requires your review.\n\nTask: {task_id}\nType: {checkpoint_type}\nRisk Level: {risk_level}\n\nPlease review at: {review_url}'
                },
                'checkpoint_approved': {
                    'subject': 'Approved: {task_id} - {checkpoint_type}',
                    'body': 'Checkpoint has been approved by {reviewer_id}.\n\nComments: {comments}'
                },
                'checkpoint_rejected': {
                    'subject': 'Rejected: {task_id} - {checkpoint_type}',
                    'body': 'Checkpoint has been rejected by {reviewer_id}.\n\nReason: {comments}'
                },
                'checkpoint_escalated': {
                    'subject': 'ESCALATED: {task_id} - {checkpoint_type}',
                    'body': 'Checkpoint has been escalated due to timeout.\n\nOriginal timeout: {timeout_hours} hours\nEscalation level: {escalation_level}'
                }
            },
            'integration_settings': {
                'dashboard': {
                    'enabled': True,
                    'base_url': 'http://localhost:5000',
                    'refresh_interval_seconds': 30
                },
                'email': {
                    'enabled': True,
                    'smtp_server': 'smtp.company.com',
                    'smtp_port': 587,
                    'use_tls': True
                },
                'slack': {
                    'enabled': True,
                    'webhook_url': 'https://hooks.slack.com/services/...',
                    'default_channel': '#engineering-reviews'
                }
            }
        }
        
        # Create config file
        self.config_path = Path(self.temp_dir) / "hitl_policies.yaml"
        with open(self.config_path, 'w') as f:
            yaml.dump(self.test_config, f)
        
        self.engine = HITLPolicyEngine(str(self.config_path))
      
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    async def test_task_status_integration(self):
        """Test integration with existing task status system."""
        # Test that HITL checkpoints can block task progression
        checkpoint = self.engine.create_checkpoint(
            task_id="BE-07",
            checkpoint_type="agent_prompt",
            task_type="backend",
            content={"prompt": "Implement authentication system"},
            risk_factors=["auth_implementation", "security_config"]
        )
        
        # High risk should create pending checkpoint
        self.assertEqual(checkpoint.status, CheckpointStatus.PENDING)
        self.assertEqual(checkpoint.risk_level, RiskLevel.HIGH)
        
        # Task should be blocked
        pending = self.engine.get_pending_checkpoints_for_task("BE-07")
        self.assertEqual(len(pending), 1)
    
    async def test_risk_pattern_detection(self):
        """Test risk pattern detection from content."""
        # High risk backend patterns
        high_risk_checkpoint = self.engine.create_checkpoint(
            task_id="BE-08",
            checkpoint_type="output_evaluation",
            task_type="backend",
            content={"code": "class AuthenticationService:\n    def login(self, username, password):\n        # Security implementation"},
            risk_factors=["auth_implementation", "security_config"]
        )
        
        self.assertEqual(high_risk_checkpoint.risk_level, RiskLevel.HIGH)        
        # Low risk frontend patterns
        low_risk_checkpoint = self.engine.create_checkpoint(
            task_id="FE-05",
            checkpoint_type="output_evaluation",
            task_type="frontend",
            content={"code": ".button { background-color: blue; }"},
            risk_factors=["styling"]
        )
        
        self.assertEqual(low_risk_checkpoint.risk_level, RiskLevel.LOW)
        # Should be auto-approved for frontend styling
        self.assertEqual(low_risk_checkpoint.status, CheckpointStatus.APPROVED)
    
    async def test_disabled_checkpoint_types(self):
        """Test that disabled checkpoint types are skipped."""
        # Documentation checkpoints should be disabled
        checkpoint = self.engine.create_checkpoint(
            task_id="DOC-01",
            checkpoint_type="documentation",
            task_type="design",
            content={"documentation": "User guide update"},
            risk_factors=[]
        )
          # Should be auto-approved since documentation checkpoints are disabled
        self.assertEqual(checkpoint.status, CheckpointStatus.APPROVED)
      
    async def test_infrastructure_high_risk_default(self):
        """Test that infrastructure tasks default to high risk."""
        checkpoint = self.engine.create_checkpoint(
            task_id="INFRA-03",
            checkpoint_type="task_transitions",
            task_type="infrastructure",
            content={"deployment": "Production database migration"},
            risk_factors=["production_deployment", "database_config"]
        )
        
        self.assertEqual(checkpoint.risk_level, RiskLevel.HIGH)
        self.assertEqual(checkpoint.status, CheckpointStatus.PENDING)
        # Infrastructure with auto_approve_low_risk: False should never auto-approve
      
    async def test_escalation_policy_selection(self):
        """Test correct escalation policy selection based on risk level."""
        # Create high risk checkpoint
        checkpoint = self.engine.create_checkpoint(
            task_id="BE-09",
            checkpoint_type="output_evaluation",
            task_type="backend",
            content={"code": "Database migration script"},
            risk_factors=["database_migration", "production_deployment"]
        )
        
        # Simulate timeout
        checkpoint.created_at = datetime.now() - timedelta(hours=25)
        
        escalation_policy = self.engine._get_escalation_policy(checkpoint.risk_level)
        self.assertEqual(len(escalation_policy['escalation_levels']), 3)  # team_lead, technical_director, cto
        self.assertIn('slack', escalation_policy['notification_channels'])
    
    async def test_batch_checkpoint_processing(self):
        """Test processing multiple checkpoints efficiently."""
        # Create multiple checkpoints
        checkpoints = []        
        for i in range(5):
            checkpoint = self.engine.create_checkpoint(
                task_id=f"BE-{10+i}",
                checkpoint_type="agent_prompt",
                task_type="backend",
                content={"prompt": f"Simple CRUD operation {i}"},
                risk_factors=["simple_crud"]
            )
            checkpoints.append(checkpoint)
        
        # All should be auto-approved (low risk)
        for checkpoint in checkpoints:
            self.assertEqual(checkpoint.status, CheckpointStatus.APPROVED)
        
        # Verify no pending checkpoints
        all_pending = self.engine.get_pending_checkpoints()
        self.assertEqual(len(all_pending), 0)
    
    async def test_checkpoint_retry_mechanism(self):
        """Test checkpoint retry mechanism for failed reviews."""
        checkpoint = self.engine.create_checkpoint(
            task_id="BE-11",
            checkpoint_type="output_evaluation",
            task_type="backend",
            content={"code": "Complex business logic"},
            risk_factors=["business_logic", "complex_logic"]
        )
        
        # Simulate rejection
        from orchestration.hitl_engine import HITLReviewDecision
        decision = HITLReviewDecision(
            checkpoint_id=checkpoint.checkpoint_id,
            decision="reject",
            reviewer_id="test_reviewer",
            comments="Needs improvement",
            reviewed_at=datetime.now()
        )
        
        await self.engine.process_decision(decision)
        
        # Verify rejection recorded
        updated_checkpoint = self.engine.get_checkpoint(checkpoint.checkpoint_id)
        self.assertEqual(updated_checkpoint.status, CheckpointStatus.REJECTED)
          # Create retry checkpoint
        retry_checkpoint = self.engine.create_checkpoint(
            task_id="BE-11",
            checkpoint_type="output_evaluation",
            task_type="backend",
            content={"code": "Improved business logic"},
            risk_factors=["business_logic"],
            parent_checkpoint_id=checkpoint.checkpoint_id
        )
        self.assertEqual(retry_checkpoint.status, CheckpointStatus.PENDING)    
    async def test_notification_template_rendering(self):
        """Test notification template rendering with checkpoint data."""
        checkpoint = self.engine.create_checkpoint(
            task_id="BE-12",
            checkpoint_type="qa_validation",
            task_type="backend",
            content={"test_results": "All tests passing"},
            risk_factors=["integration"]
        )
        
        # Test template rendering
        template = self.engine.policies['notification_templates']['checkpoint_created']
        
        rendered_subject = template['subject'].format(
            task_id=checkpoint.task_id,
            checkpoint_type=checkpoint.checkpoint_type
        )
        
        self.assertEqual(rendered_subject, "Review Required: BE-12 - qa_validation")
        
        rendered_body = template['body'].format(
            task_id=checkpoint.task_id,
            checkpoint_type=checkpoint.checkpoint_type,
            risk_level=checkpoint.risk_level.value,
            review_url="http://localhost:5000/review/checkpoint-123"
        )
        self.assertIn("medium", rendered_body)
        self.assertIn("medium", rendered_body)
    
    async def test_concurrent_checkpoint_handling(self):
        """Test handling multiple concurrent checkpoints for same task."""
        checkpoint1 = self.engine.create_checkpoint(
            task_id="BE-13",
            checkpoint_type="agent_prompt",
            task_type="backend",
            content={"prompt": "Design API"},
            risk_factors=["api_endpoint"]
        )
        
        checkpoint2 = self.engine.create_checkpoint(
            task_id="BE-13",
            checkpoint_type="output_evaluation",
            task_type="backend",
            content={"code": "API implementation"},
            risk_factors=["api_endpoint", "integration"]
        )
        
        # Both should be pending
        pending_for_task = self.engine.get_pending_checkpoints_for_task("BE-13")
        self.assertEqual(len(pending_for_task), 2)
        
        # Approve first checkpoint
        from orchestration.hitl_engine import HITLReviewDecision
        decision1 = HITLReviewDecision(
            checkpoint_id=checkpoint1.checkpoint_id,
            decision="approve",
            reviewer_id="test_reviewer",
            comments="Good design",
            reviewed_at=datetime.now()
        )
        
        await self.engine.process_decision(decision1)
        
        # Should still have one pending
        pending_for_task = self.engine.get_pending_checkpoints_for_task("BE-13")
        self.assertEqual(len(pending_for_task), 1)
        self.assertEqual(pending_for_task[0].checkpoint_id, checkpoint2.checkpoint_id)


if __name__ == '__main__':
    unittest.main(verbosity=2)
