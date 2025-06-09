#!/usr/bin/env python3
"""
HITL Dashboard Widget Tests

Comprehensive tests for all HITL dashboard widgets and integration.
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dashboard.hitl_widgets import (
    HITLPendingReviewsWidget, HITLApprovalActionsWidget,
    HITLMetricsWidget, HITLWorkflowStatusWidget, HITLDashboardManager
)
from orchestration.hitl_engine import HITLCheckpoint, CheckpointStatus, RiskLevel


class TestHITLPendingReviewsWidget(unittest.TestCase):
    """Test pending reviews widget functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.widget = HITLPendingReviewsWidget()
        
        # Mock checkpoints
        self.mock_checkpoints = [
            HITLCheckpoint(
                checkpoint_id="cp-1",
                task_id="BE-07",
                checkpoint_type="agent_prompt",
                task_type="backend",
                content={"prompt": "Create API endpoint"},
                risk_level=RiskLevel.HIGH,
                status=CheckpointStatus.PENDING,
                created_at=datetime.now() - timedelta(hours=2),
                timeout_at=datetime.now() + timedelta(hours=22)
            ),
            HITLCheckpoint(
                checkpoint_id="cp-2",
                task_id="FE-05",
                checkpoint_type="output_evaluation",
                task_type="frontend",
                content={"code": "React component"},
                risk_level=RiskLevel.MEDIUM,
                status=CheckpointStatus.PENDING,
                created_at=datetime.now() - timedelta(hours=1),
                timeout_at=datetime.now() + timedelta(hours=11)
            ),
            HITLCheckpoint(
                checkpoint_id="cp-3",
                task_id="INFRA-02",
                checkpoint_type="task_transitions",
                task_type="infrastructure",
                content={"deployment": "Production setup"},
                risk_level=RiskLevel.HIGH,
                status=CheckpointStatus.ESCALATED,
                created_at=datetime.now() - timedelta(hours=25),
                timeout_at=datetime.now() - timedelta(hours=1)
            )
        ]
    
    def test_get_data_structure(self):
        """Test data structure returned by widget."""
        with patch.object(self.widget, 'hitl_engine') as mock_engine:
            mock_engine.get_pending_checkpoints.return_value = self.mock_checkpoints
            
            data = self.widget.get_data()
            
            # Verify structure
            self.assertIn('pending_reviews', data)
            self.assertIn('summary', data)
            self.assertIn('filters', data)
            
            # Verify content
            reviews = data['pending_reviews']
            self.assertEqual(len(reviews), 3)
            
            # Check first review structure
            review = reviews[0]
            self.assertIn('checkpoint_id', review)
            self.assertIn('task_id', review)
            self.assertIn('checkpoint_type', review)
            self.assertIn('risk_level', review)
            self.assertIn('status', review)
            self.assertIn('created_at', review)
            self.assertIn('time_remaining', review)
    
    def test_priority_sorting(self):
        """Test that reviews are sorted by priority."""
        with patch.object(self.widget, 'hitl_engine') as mock_engine:
            mock_engine.get_pending_checkpoints.return_value = self.mock_checkpoints
            
            data = self.widget.get_data()
            reviews = data['pending_reviews']
            
            # Should be sorted by priority (escalated first, then by risk level, then by time)
            self.assertEqual(reviews[0]['status'], 'escalated')
            self.assertEqual(reviews[1]['risk_level'], 'high')
            self.assertEqual(reviews[2]['risk_level'], 'medium')
    
    def test_time_remaining_calculation(self):
        """Test time remaining calculation."""
        with patch.object(self.widget, 'hitl_engine') as mock_engine:
            mock_engine.get_pending_checkpoints.return_value = [self.mock_checkpoints[0]]
            
            data = self.widget.get_data()
            review = data['pending_reviews'][0]
            
            # Should show approximately 22 hours remaining
            self.assertIn('22', review['time_remaining'])
            self.assertIn('hours', review['time_remaining'])
    
    def test_overdue_checkpoint(self):
        """Test handling of overdue checkpoints."""
        with patch.object(self.widget, 'hitl_engine') as mock_engine:
            mock_engine.get_pending_checkpoints.return_value = [self.mock_checkpoints[2]]
            
            data = self.widget.get_data()
            review = data['pending_reviews'][0]
            
            # Should show overdue status
            self.assertIn('overdue', review['time_remaining'].lower())
    
    def test_filtering_capabilities(self):
        """Test filtering options."""
        with patch.object(self.widget, 'hitl_engine') as mock_engine:
            mock_engine.get_pending_checkpoints.return_value = self.mock_checkpoints
            
            data = self.widget.get_data()
            filters = data['filters']
            
            # Should provide filter options
            self.assertIn('risk_levels', filters)
            self.assertIn('task_types', filters)
            self.assertIn('checkpoint_types', filters)
            
            # Check filter values
            self.assertIn('high', filters['risk_levels'])
            self.assertIn('backend', filters['task_types'])
            self.assertIn('agent_prompt', filters['checkpoint_types'])
    
    def test_summary_statistics(self):
        """Test summary statistics calculation."""
        with patch.object(self.widget, 'hitl_engine') as mock_engine:
            mock_engine.get_pending_checkpoints.return_value = self.mock_checkpoints
            
            data = self.widget.get_data()
            summary = data['summary']
            
            self.assertEqual(summary['total_pending'], 3)
            self.assertEqual(summary['high_risk_count'], 2)
            self.assertEqual(summary['escalated_count'], 1)
            self.assertEqual(summary['overdue_count'], 1)


class TestHITLApprovalActionsWidget(unittest.TestCase):
    """Test approval actions widget functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.widget = HITLApprovalActionsWidget()
        self.mock_engine = MagicMock()
        self.widget.hitl_engine = self.mock_engine
    
    def test_approve_checkpoint(self):
        """Test checkpoint approval."""
        self.mock_engine.process_decision.return_value = True
        
        result = self.widget.process_action(
            checkpoint_id="cp-1",
            action="approve",
            reviewer_id="john.doe",
            comments="Looks good"
        )
        
        self.assertTrue(result['success'])
        self.mock_engine.process_decision.assert_called_once()
        
        # Verify decision object
        call_args = self.mock_engine.process_decision.call_args[0][0]
        self.assertEqual(call_args.checkpoint_id, "cp-1")
        self.assertEqual(call_args.decision, "approve")
        self.assertEqual(call_args.reviewer_id, "john.doe")
        self.assertEqual(call_args.comments, "Looks good")
    
    def test_reject_checkpoint(self):
        """Test checkpoint rejection."""
        self.mock_engine.process_decision.return_value = True
        
        result = self.widget.process_action(
            checkpoint_id="cp-2",
            action="reject",
            reviewer_id="jane.smith",
            comments="Needs improvement"
        )
        
        self.assertTrue(result['success'])
        
        # Verify decision object
        call_args = self.mock_engine.process_decision.call_args[0][0]
        self.assertEqual(call_args.decision, "reject")
        self.assertEqual(call_args.comments, "Needs improvement")
    
    def test_escalate_checkpoint(self):
        """Test checkpoint escalation."""
        self.mock_engine.escalate_checkpoint.return_value = True
        
        result = self.widget.process_action(
            checkpoint_id="cp-3",
            action="escalate",
            reviewer_id="admin",
            comments="Requires senior review"
        )
        
        self.assertTrue(result['success'])
        self.mock_engine.escalate_checkpoint.assert_called_once_with("cp-3", "admin")
    
    def test_batch_approval(self):
        """Test batch approval functionality."""
        self.mock_engine.process_decision.return_value = True
        
        result = self.widget.process_batch_action(
            checkpoint_ids=["cp-1", "cp-2", "cp-3"],
            action="approve",
            reviewer_id="team.lead",
            comments="Batch approved"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['processed_count'], 3)
        self.assertEqual(self.mock_engine.process_decision.call_count, 3)
    
    def test_invalid_action(self):
        """Test handling of invalid actions."""
        result = self.widget.process_action(
            checkpoint_id="cp-1",
            action="invalid_action",
            reviewer_id="user",
            comments="Test"
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_engine_failure_handling(self):
        """Test handling of engine failures."""
        self.mock_engine.process_decision.return_value = False
        
        result = self.widget.process_action(
            checkpoint_id="cp-1",
            action="approve",
            reviewer_id="user",
            comments="Test"
        )
        
        self.assertFalse(result['success'])


class TestHITLMetricsWidget(unittest.TestCase):
    """Test HITL metrics widget functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.widget = HITLMetricsWidget()
        self.mock_engine = MagicMock()
        self.widget.hitl_engine = self.mock_engine
        
        # Mock metrics data
        self.mock_metrics = {
            'total_checkpoints': 150,
            'pending_count': 8,
            'approved_count': 120,
            'rejected_count': 15,
            'escalated_count': 7,
            'average_review_time_hours': 4.5,
            'approval_rate': 85.7,
            'escalation_rate': 5.0,
            'by_task_type': {
                'backend': {'total': 80, 'approved': 65, 'rejected': 10, 'pending': 5},
                'frontend': {'total': 45, 'approved': 40, 'rejected': 3, 'pending': 2},
                'infrastructure': {'total': 25, 'approved': 15, 'rejected': 2, 'pending': 1}
            },
            'by_risk_level': {
                'high': {'total': 50, 'approved': 35, 'rejected': 10, 'pending': 5},
                'medium': {'total': 70, 'approved': 60, 'rejected': 5, 'pending': 2},
                'low': {'total': 30, 'approved': 25, 'rejected': 0, 'pending': 1}
            },
            'daily_trends': [
                {'date': '2024-01-15', 'created': 12, 'processed': 10},
                {'date': '2024-01-16', 'created': 15, 'processed': 14},
                {'date': '2024-01-17', 'created': 8, 'processed': 12}
            ]
        }
    
    def test_get_metrics_data(self):
        """Test metrics data retrieval."""
        self.mock_engine.get_metrics.return_value = self.mock_metrics
        
        data = self.widget.get_data()
        
        self.assertIn('metrics', data)
        self.assertIn('charts', data)
        
        metrics = data['metrics']
        self.assertEqual(metrics['total_checkpoints'], 150)
        self.assertEqual(metrics['approval_rate'], 85.7)
    
    def test_chart_data_generation(self):
        """Test chart data generation."""
        self.mock_engine.get_metrics.return_value = self.mock_metrics
        
        data = self.widget.get_data()
        charts = data['charts']
        
        # Should have multiple chart types
        self.assertIn('status_distribution', charts)
        self.assertIn('task_type_breakdown', charts)
        self.assertIn('risk_level_distribution', charts)
        self.assertIn('daily_trends', charts)
        
        # Verify chart structure
        status_chart = charts['status_distribution']
        self.assertIn('labels', status_chart)
        self.assertIn('data', status_chart)
        self.assertEqual(len(status_chart['labels']), len(status_chart['data']))
    
    def test_performance_indicators(self):
        """Test performance indicator calculations."""
        self.mock_engine.get_metrics.return_value = self.mock_metrics
        
        data = self.widget.get_data()
        metrics = data['metrics']
        
        # Should calculate key performance indicators
        self.assertIn('average_review_time_hours', metrics)
        self.assertIn('approval_rate', metrics)
        self.assertIn('escalation_rate', metrics)
        
        # Values should be calculated correctly
        self.assertEqual(metrics['approval_rate'], 85.7)
        self.assertEqual(metrics['escalation_rate'], 5.0)
    
    def test_trend_analysis(self):
        """Test trend analysis."""
        self.mock_engine.get_metrics.return_value = self.mock_metrics
        
        data = self.widget.get_data()
        charts = data['charts']
        
        trend_chart = charts['daily_trends']
        self.assertEqual(len(trend_chart['data']), 2)  # created and processed lines
        self.assertEqual(len(trend_chart['labels']), 3)  # 3 days of data


class TestHITLWorkflowStatusWidget(unittest.TestCase):
    """Test workflow status widget with HITL integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.widget = HITLWorkflowStatusWidget()
        self.mock_engine = MagicMock()
        self.widget.hitl_engine = self.mock_engine
    
    def test_workflow_status_with_pending_checkpoints(self):
        """Test workflow status when checkpoints are pending."""
        # Mock pending checkpoints
        self.mock_engine.get_pending_checkpoints_for_task.return_value = [
            HITLCheckpoint(
                checkpoint_id="cp-1",
                task_id="BE-07",
                checkpoint_type="agent_prompt",
                task_type="backend",
                content={},
                risk_level=RiskLevel.HIGH,
                status=CheckpointStatus.PENDING,
                created_at=datetime.now()
            )
        ]
        
        with patch.object(self.widget, 'get_workflow_status') as mock_workflow:
            mock_workflow.return_value = {
                'current_phase': 'agent_prompt',
                'task_status': 'in_progress',
                'progress_percentage': 25
            }
            
            data = self.widget.get_data("BE-07")
            status = data['workflow_status']
            
            self.assertTrue(status['blocked_on_review'])
            self.assertEqual(len(status['pending_checkpoints']), 1)
            self.assertEqual(status['current_phase'], 'agent_prompt')
    
    def test_workflow_status_without_pending_checkpoints(self):
        """Test workflow status when no checkpoints are pending."""
        self.mock_engine.get_pending_checkpoints_for_task.return_value = []
        
        with patch.object(self.widget, 'get_workflow_status') as mock_workflow:
            mock_workflow.return_value = {
                'current_phase': 'output_evaluation',
                'task_status': 'in_progress',
                'progress_percentage': 75
            }
            
            data = self.widget.get_data("BE-07")
            status = data['workflow_status']
            
            self.assertFalse(status['blocked_on_review'])
            self.assertEqual(len(status['pending_checkpoints']), 0)
    
    def test_next_checkpoint_prediction(self):
        """Test prediction of next checkpoint."""
        self.mock_engine.get_pending_checkpoints_for_task.return_value = []
        
        with patch.object(self.widget, 'get_workflow_status') as mock_workflow:
            mock_workflow.return_value = {
                'current_phase': 'agent_prompt',
                'task_status': 'in_progress',
                'progress_percentage': 25
            }
            
            data = self.widget.get_data("BE-07", task_type="backend")
            status = data['workflow_status']
            
            # Should predict next checkpoint based on workflow phase
            self.assertIn('next_checkpoint', status)
            self.assertEqual(status['next_checkpoint'], 'output_evaluation')


class TestHITLDashboardManager(unittest.TestCase):
    """Test HITL dashboard manager coordination."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = HITLDashboardManager()
        self.mock_engine = MagicMock()
        
        # Patch all widget engines
        patcher = patch.object(HITLDashboardManager, 'hitl_engine', self.mock_engine)
        patcher.start()
        self.addCleanup(patcher.stop)
    
    def test_full_dashboard_data(self):
        """Test complete dashboard data aggregation."""
        # Mock data for each widget
        self.mock_engine.get_pending_checkpoints.return_value = []
        self.mock_engine.get_metrics.return_value = {
            'total_checkpoints': 100,
            'pending_count': 5
        }
        
        with patch.object(HITLWorkflowStatusWidget, 'get_workflow_status') as mock_workflow:
            mock_workflow.return_value = {
                'current_phase': 'agent_prompt',
                'task_status': 'in_progress'
            }
            
            data = self.manager.get_dashboard_data()
            
            # Should contain data from all widgets
            self.assertIn('pending_reviews', data)
            self.assertIn('metrics', data)
            self.assertIn('workflow_status', data)
            self.assertIn('last_updated', data)
    
    def test_task_specific_dashboard(self):
        """Test task-specific dashboard data."""
        self.mock_engine.get_pending_checkpoints_for_task.return_value = []
        
        with patch.object(HITLWorkflowStatusWidget, 'get_workflow_status') as mock_workflow:
            mock_workflow.return_value = {
                'current_phase': 'output_evaluation',
                'task_status': 'in_progress'
            }
            
            data = self.manager.get_task_dashboard_data("BE-07", "backend")
            
            self.assertIn('task_id', data)
            self.assertEqual(data['task_id'], "BE-07")
            self.assertIn('workflow_status', data)
    
    def test_real_time_updates(self):
        """Test real-time update capabilities."""
        # Test that dashboard data includes timestamp
        data = self.manager.get_dashboard_data()
        self.assertIn('last_updated', data)
        
        # Timestamp should be recent
        import datetime
        last_updated = datetime.datetime.fromisoformat(data['last_updated'])
        now = datetime.datetime.now()
        self.assertLess((now - last_updated).total_seconds(), 5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
