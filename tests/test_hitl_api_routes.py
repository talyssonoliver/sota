#!/usr/bin/env python3
"""
HITL API Routes Tests

Comprehensive tests for HITL REST API endpoints.
"""

import unittest
import json
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from flask import Flask
import sys

sys.path.append(str(Path(__file__).parent.parent))

from api.hitl_routes import create_hitl_blueprint
from orchestration.hitl_engine import HITLPolicyEngine, HITLCheckpoint, CheckpointStatus, RiskLevel


class TestHITLAPIRoutes(unittest.TestCase):
    """Test HITL API routes functionality."""
    
    def setUp(self):
        """Set up test Flask app with HITL routes."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Create mock HITL engine
        self.mock_hitl_engine = MagicMock()
        
        # Create test checkpoints
        self.test_checkpoints = [
            {
                'checkpoint_id': 'cp-1',
                'task_id': 'BE-07',
                'checkpoint_type': 'agent_prompt',
                'task_type': 'backend',
                'status': 'pending',
                'risk_level': 'high',
                'created_at': datetime.now().isoformat(),
                'timeout_at': (datetime.now() + timedelta(hours=24)).isoformat(),
                'content': {'prompt': 'Create API endpoint'},
                'risk_factors': ['api_design', 'security']
            },
            {
                'checkpoint_id': 'cp-2',
                'task_id': 'FE-05',
                'checkpoint_type': 'output_evaluation',
                'task_type': 'frontend',
                'status': 'pending',
                'risk_level': 'medium',
                'created_at': datetime.now().isoformat(),
                'timeout_at': (datetime.now() + timedelta(hours=12)).isoformat(),
                'content': {'code': 'React component'},
                'risk_factors': ['complex_form']
            }
        ]
        
        # Register HITL blueprint
        hitl_bp = create_hitl_blueprint(self.mock_hitl_engine)
        self.app.register_blueprint(hitl_bp, url_prefix='/api/hitl')
        
        self.client = self.app.test_client()
    
    def test_get_checkpoints_endpoint(self):
        """Test GET /api/hitl/checkpoints endpoint."""
        self.mock_hitl_engine.get_pending_checkpoints.return_value = self.test_checkpoints
        
        response = self.client.get('/api/hitl/checkpoints')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('checkpoints', data)
        self.assertEqual(len(data['checkpoints']), 2)
        self.assertEqual(data['checkpoints'][0]['checkpoint_id'], 'cp-1')
    
    def test_get_checkpoints_with_filters(self):
        """Test GET /api/hitl/checkpoints with filters."""
        filtered_checkpoints = [self.test_checkpoints[0]]  # Only high risk
        self.mock_hitl_engine.get_pending_checkpoints.return_value = filtered_checkpoints
        
        response = self.client.get('/api/hitl/checkpoints?risk_level=high&task_type=backend')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data['checkpoints']), 1)
        self.assertEqual(data['checkpoints'][0]['risk_level'], 'high')
        self.assertEqual(data['checkpoints'][0]['task_type'], 'backend')
    
    def test_get_single_checkpoint(self):
        """Test GET /api/hitl/checkpoints/<checkpoint_id> endpoint."""
        self.mock_hitl_engine.get_checkpoint.return_value = self.test_checkpoints[0]
        
        response = self.client.get('/api/hitl/checkpoints/cp-1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('checkpoint', data)
        self.assertEqual(data['checkpoint']['checkpoint_id'], 'cp-1')
    
    def test_get_nonexistent_checkpoint(self):
        """Test GET /api/hitl/checkpoints/<checkpoint_id> for nonexistent checkpoint."""
        self.mock_hitl_engine.get_checkpoint.return_value = None
        
        response = self.client.get('/api/hitl/checkpoints/nonexistent')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_approve_checkpoint(self):
        """Test POST /api/hitl/checkpoints/<checkpoint_id>/approve endpoint."""
        self.mock_hitl_engine.process_decision.return_value = True
        
        response = self.client.post('/api/hitl/checkpoints/cp-1/approve',
                                   json={
                                       'reviewer_id': 'john.doe',
                                       'comments': 'Looks good to me'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'approved')
        self.assertEqual(data['reviewer_id'], 'john.doe')
        
        # Verify engine was called correctly
        self.mock_hitl_engine.process_decision.assert_called_once()
        call_args = self.mock_hitl_engine.process_decision.call_args[0][0]
        self.assertEqual(call_args.checkpoint_id, 'cp-1')
        self.assertEqual(call_args.decision, 'approve')
        self.assertEqual(call_args.reviewer_id, 'john.doe')
    
    def test_reject_checkpoint(self):
        """Test POST /api/hitl/checkpoints/<checkpoint_id>/reject endpoint."""
        self.mock_hitl_engine.process_decision.return_value = True
        
        response = self.client.post('/api/hitl/checkpoints/cp-1/reject',
                                   json={
                                       'reviewer_id': 'jane.smith',
                                       'comments': 'Needs improvement in error handling'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'rejected')
        
        # Verify decision object
        call_args = self.mock_hitl_engine.process_decision.call_args[0][0]
        self.assertEqual(call_args.decision, 'reject')
        self.assertEqual(call_args.comments, 'Needs improvement in error handling')
    
    def test_escalate_checkpoint(self):
        """Test POST /api/hitl/checkpoints/<checkpoint_id>/escalate endpoint."""
        self.mock_hitl_engine.escalate_checkpoint.return_value = True
        
        response = self.client.post('/api/hitl/checkpoints/cp-1/escalate',
                                   json={
                                       'reviewer_id': 'team.lead',
                                       'reason': 'Requires senior architect review'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'escalated')
        
        # Verify escalation was called
        self.mock_hitl_engine.escalate_checkpoint.assert_called_once_with('cp-1', 'team.lead')
    
    def test_approve_checkpoint_missing_data(self):
        """Test approval endpoint with missing required data."""
        response = self.client.post('/api/hitl/checkpoints/cp-1/approve',
                                   json={'comments': 'Missing reviewer_id'},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_approval_engine_failure(self):
        """Test approval when engine returns failure."""
        self.mock_hitl_engine.process_decision.return_value = False
        
        response = self.client.post('/api/hitl/checkpoints/cp-1/approve',
                                   json={
                                       'reviewer_id': 'user',
                                       'comments': 'Test'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_batch_approve_checkpoints(self):
        """Test POST /api/hitl/checkpoints/batch/approve endpoint."""
        self.mock_hitl_engine.process_decision.return_value = True
        
        response = self.client.post('/api/hitl/checkpoints/batch/approve',
                                   json={
                                       'checkpoint_ids': ['cp-1', 'cp-2'],
                                       'reviewer_id': 'batch.reviewer',
                                       'comments': 'Batch approval'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['processed_count'], 2)
        self.assertEqual(data['successful_count'], 2)
        self.assertEqual(data['failed_count'], 0)
        
        # Verify engine was called twice
        self.assertEqual(self.mock_hitl_engine.process_decision.call_count, 2)
    
    def test_batch_reject_checkpoints(self):
        """Test POST /api/hitl/checkpoints/batch/reject endpoint."""
        self.mock_hitl_engine.process_decision.return_value = True
        
        response = self.client.post('/api/hitl/checkpoints/batch/reject',
                                   json={
                                       'checkpoint_ids': ['cp-1', 'cp-2'],
                                       'reviewer_id': 'batch.reviewer',
                                       'comments': 'Batch rejection'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['processed_count'], 2)
    
    def test_batch_with_partial_failures(self):
        """Test batch processing with some failures."""
        # Mock engine to return True for first call, False for second
        self.mock_hitl_engine.process_decision.side_effect = [True, False]
        
        response = self.client.post('/api/hitl/checkpoints/batch/approve',
                                   json={
                                       'checkpoint_ids': ['cp-1', 'cp-2'],
                                       'reviewer_id': 'user',
                                       'comments': 'Test batch'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['processed_count'], 2)
        self.assertEqual(data['successful_count'], 1)
        self.assertEqual(data['failed_count'], 1)
        self.assertEqual(len(data['failed_checkpoints']), 1)
    
    def test_get_metrics_endpoint(self):
        """Test GET /api/hitl/metrics endpoint."""
        mock_metrics = {
            'total_checkpoints': 100,
            'pending_count': 5,
            'approved_count': 80,
            'rejected_count': 10,
            'escalated_count': 5,
            'average_review_time_hours': 3.5,
            'approval_rate': 85.0,
            'escalation_rate': 5.0
        }
        
        self.mock_hitl_engine.get_metrics.return_value = mock_metrics
        
        response = self.client.get('/api/hitl/metrics')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('metrics', data)
        self.assertEqual(data['metrics']['total_checkpoints'], 100)
        self.assertEqual(data['metrics']['approval_rate'], 85.0)
    
    def test_get_metrics_with_filters(self):
        """Test GET /api/hitl/metrics with date filters."""
        mock_metrics = {
            'total_checkpoints': 50,
            'period': '7_days'
        }
        
        self.mock_hitl_engine.get_metrics.return_value = mock_metrics
        
        response = self.client.get('/api/hitl/metrics?period=7_days')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['metrics']['total_checkpoints'], 50)
    
    def test_get_task_checkpoints(self):
        """Test GET /api/hitl/tasks/<task_id>/checkpoints endpoint."""
        task_checkpoints = [self.test_checkpoints[0]]  # Only BE-07 checkpoint
        self.mock_hitl_engine.get_checkpoints_for_task.return_value = task_checkpoints
        
        response = self.client.get('/api/hitl/tasks/BE-07/checkpoints')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('checkpoints', data)
        self.assertEqual(len(data['checkpoints']), 1)
        self.assertEqual(data['checkpoints'][0]['task_id'], 'BE-07')
    
    def test_get_audit_trail(self):
        """Test GET /api/hitl/checkpoints/<checkpoint_id>/audit endpoint."""
        mock_audit_entries = [
            {
                'timestamp': datetime.now().isoformat(),
                'action': 'created',
                'user_id': 'system',
                'details': 'Checkpoint created automatically'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'action': 'approved',
                'user_id': 'john.doe',
                'details': 'Approved with comments: Looks good'
            }
        ]
        
        self.mock_hitl_engine.get_audit_trail.return_value = mock_audit_entries
        
        response = self.client.get('/api/hitl/checkpoints/cp-1/audit')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('audit_trail', data)
        self.assertEqual(len(data['audit_trail']), 2)
        self.assertEqual(data['audit_trail'][1]['action'], 'approved')
    
    def test_create_checkpoint_endpoint(self):
        """Test POST /api/hitl/checkpoints endpoint."""
        mock_checkpoint = self.test_checkpoints[0]
        self.mock_hitl_engine.create_checkpoint.return_value = mock_checkpoint
        
        checkpoint_data = {
            'task_id': 'BE-08',
            'checkpoint_type': 'agent_prompt',
            'task_type': 'backend',
            'content': {'prompt': 'Create new service'},
            'risk_factors': ['complex_logic']
        }
        
        response = self.client.post('/api/hitl/checkpoints',
                                   json=checkpoint_data,
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('checkpoint', data)
        
        # Verify engine was called correctly
        self.mock_hitl_engine.create_checkpoint.assert_called_once()
    
    def test_dashboard_data_endpoint(self):
        """Test GET /api/hitl/dashboard endpoint."""
        mock_dashboard_data = {
            'pending_reviews': self.test_checkpoints,
            'metrics': {
                'total_pending': 2,
                'high_risk_count': 1
            },
            'workflow_status': {
                'active_tasks': 5,
                'blocked_tasks': 2
            }
        }
        
        with patch('api.hitl_routes.HITLDashboardManager') as mock_manager_class:
            mock_manager = mock_manager_class.return_value
            mock_manager.get_dashboard_data.return_value = mock_dashboard_data
            
            response = self.client.get('/api/hitl/dashboard')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            self.assertIn('pending_reviews', data)
            self.assertIn('metrics', data)
            self.assertIn('workflow_status', data)
    
    def test_task_dashboard_data_endpoint(self):
        """Test GET /api/hitl/dashboard/tasks/<task_id> endpoint."""
        mock_task_data = {
            'task_id': 'BE-07',
            'workflow_status': {
                'current_phase': 'agent_prompt',
                'blocked_on_review': True
            },
            'pending_checkpoints': [self.test_checkpoints[0]]
        }
        
        with patch('api.hitl_routes.HITLDashboardManager') as mock_manager_class:
            mock_manager = mock_manager_class.return_value
            mock_manager.get_task_dashboard_data.return_value = mock_task_data
            
            response = self.client.get('/api/hitl/dashboard/tasks/BE-07?task_type=backend')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            self.assertEqual(data['task_id'], 'BE-07')
            self.assertTrue(data['workflow_status']['blocked_on_review'])
    
    def test_error_handling(self):
        """Test API error handling."""
        # Test with invalid JSON
        response = self.client.post('/api/hitl/checkpoints/cp-1/approve',
                                   data='invalid json',
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        # Test engine exception
        self.mock_hitl_engine.process_decision.side_effect = Exception("Database error")
        
        response = self.client.post('/api/hitl/checkpoints/cp-1/approve',
                                   json={
                                       'reviewer_id': 'user',
                                       'comments': 'test'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_cors_headers(self):
        """Test CORS headers in responses."""
        response = self.client.get('/api/hitl/checkpoints')
        
        # Should include CORS headers for dashboard integration
        self.assertIn('Access-Control-Allow-Origin', response.headers)
    
    def test_rate_limiting_headers(self):
        """Test rate limiting headers."""
        response = self.client.get('/api/hitl/metrics')
        
        # Should include rate limiting info
        self.assertIn('X-RateLimit-Remaining', response.headers)


if __name__ == '__main__':
    unittest.main(verbosity=2)
