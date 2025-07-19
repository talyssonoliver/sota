"""
Tests for HITL CLI Interface

Comprehensive test suite for the Human-in-the-Loop command-line interface.
"""
import sys
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.interfaces.cli.hitl_cli import HITLCLIManager
from src.core.workflows.hitl.types import CheckpointStatus, RiskLevel

class TestHITLCLIManager(unittest.TestCase):
    """Test cases for HITLCLIManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.cli_manager = HITLCLIManager()
        # Create mocks with proper spec to ensure interface compliance
        self.mock_hitl_engine = Mock(spec=['get_pending_checkpoints', 'get_checkpoint', 'process_decision', 
                                           'get_decision_history', 'get_checkpoint_metrics', 'get_alerts',
                                           'record_alert_acknowledgment', 'get_auto_approval_candidates', 'get_metrics',
                                           'escalate_checkpoint', 'export_checkpoint_data', 'get_audit_trail'])
        self.mock_metadata_manager = Mock(spec=['get_task', 'save_task', 'get_task_metadata'])
        self.mock_dashboard_manager = Mock(spec=['update_dashboard', 'get_dashboard_data'])
        self.cli_manager.hitl_engine = self.mock_hitl_engine
        self.cli_manager.metadata_manager = self.mock_metadata_manager
        self.cli_manager.dashboard_manager = self.mock_dashboard_manager

    def test_list_pending_checkpoints_all(self):
        """Test listing all pending checkpoints."""
        mock_checkpoints = [{'checkpoint_id': 'hitl_BE-07_abc12345', 'task_id': 'BE-07', 'checkpoint_type': 'output_evaluation', 'risk_level': 'high', 'reviewers': ['Backend Engineer', 'Technical Lead']}, {'checkpoint_id': 'hitl_FE-05_def45678', 'task_id': 'FE-05', 'checkpoint_type': 'qa_validation', 'risk_level': 'medium', 'reviewers': ['QA Engineer']}]
        self.mock_hitl_engine.get_pending_checkpoints.return_value = mock_checkpoints
        result = self.cli_manager.list_pending_checkpoints()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['checkpoint_id'], 'hitl_BE-07_abc12345')
        self.assertEqual(result[1]['checkpoint_id'], 'hitl_FE-05_def45678')
        self.mock_hitl_engine.get_pending_checkpoints.assert_called_once_with()

    def test_list_pending_checkpoints_filtered_by_task(self):
        """Test listing checkpoints filtered by task ID."""
        mock_checkpoints = [{'checkpoint_id': 'hitl_BE-07_abc12345', 'task_id': 'BE-07', 'checkpoint_type': 'output_evaluation', 'risk_level': 'high', 'reviewers': ['Backend Engineer']}]
        self.mock_hitl_engine.get_pending_checkpoints.return_value = mock_checkpoints
        result = self.cli_manager.list_pending_checkpoints(task_id='BE-07')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['task_id'], 'BE-07')
        self.mock_hitl_engine.get_pending_checkpoints.assert_called_once_with('BE-07')

    def test_list_pending_checkpoints_filtered_by_reviewer(self):
        """Test listing checkpoints filtered by reviewer."""
        mock_checkpoints = [{'checkpoint_id': 'hitl_BE-07_abc12345', 'task_id': 'BE-07', 'checkpoint_type': 'output_evaluation', 'risk_level': 'high', 'reviewers': ['Backend Engineer', 'Technical Lead']}, {'checkpoint_id': 'hitl_FE-05_def45678', 'task_id': 'FE-05', 'checkpoint_type': 'qa_validation', 'risk_level': 'medium', 'reviewers': ['QA Engineer']}]
        self.mock_hitl_engine.get_pending_checkpoints.return_value = mock_checkpoints
        result = self.cli_manager.list_pending_checkpoints(reviewer='Backend Engineer')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['checkpoint_id'], 'hitl_BE-07_abc12345')
        self.assertIn('Backend Engineer', result[0]['reviewers'])

    def test_show_checkpoint_details(self):
        """Test showing checkpoint details."""
        # Create mock checkpoint with proper spec
        mock_checkpoint = Mock(spec=['checkpoint_id', 'task_id', 'checkpoint_type', 'status', 'risk_level',
                                    'created_at', 'deadline', 'description', 'reviewers', 'content',
                                    'mitigation_suggestions', 'metadata'])
        mock_checkpoint.checkpoint_id = 'hitl_BE-07_abc1234545'
        mock_checkpoint.task_id = 'BE-07'
        mock_checkpoint.checkpoint_type = 'output_evaluation'
        mock_checkpoint.status = CheckpointStatus.PENDING
        mock_checkpoint.risk_level = RiskLevel.HIGH
        mock_checkpoint.created_at = datetime(2025, 6, 8, 10, 0, 0)
        mock_checkpoint.deadline = datetime(2025, 6, 8, 18, 0, 0)
        mock_checkpoint.description = 'Review critical code changes'
        mock_checkpoint.reviewers = ['Backend Engineer', 'Technical Lead']
        mock_checkpoint.content = {'files': ['service.py', 'models.py']}
        mock_checkpoint.mitigation_suggestions = ['Run security scan', 'Add unit tests']
        mock_checkpoint.metadata = {'priority': 'high'}
        self.mock_hitl_engine.get_checkpoint.return_value = mock_checkpoint
        result = self.cli_manager.show_checkpoint_details('hitl_BE-07_abc1234545')
        self.assertIsNotNone(result)
        self.assertEqual(result['checkpoint_id'], 'hitl_BE-07_abc1234545')
        self.assertEqual(result['task_id'], 'BE-07')
        self.assertEqual(result['status'], 'pending')
        self.assertEqual(result['risk_level'], 'high')
        self.assertEqual(len(result['mitigation_suggestions']), 2)
        self.mock_hitl_engine.get_checkpoint.assert_called_once_with('hitl_BE-07_abc1234545')

    def test_show_checkpoint_details_not_found(self):
        """Test showing details for non-existent checkpoint."""
        self.mock_hitl_engine.get_checkpoint.return_value = None
        result = self.cli_manager.show_checkpoint_details('hitl_BE-07_nonexistent')
        self.assertIsNone(result)
        self.mock_hitl_engine.get_checkpoint.assert_called_once_with('hitl_BE-07_nonexistent')

    def test_approve_checkpoint_success(self):
        """Test successful checkpoint approval."""
        self.mock_hitl_engine.process_decision.return_value = True
        result = self.cli_manager.approve_checkpoint('hitl_BE-07_abc12345', 'alice', 'Looks good to me')
        self.assertTrue(result)
        self.mock_hitl_engine.process_decision.assert_called_once()
        call_args = self.mock_hitl_engine.process_decision.call_args
        self.assertEqual(call_args[0][0], 'hitl_BE-07_abc12345')
        decision = call_args[0][1]
        self.assertEqual(decision['decision'], 'approved')
        self.assertEqual(decision['reviewer'], 'alice')
        self.assertEqual(decision['comments'], 'Looks good to me')

    def test_approve_checkpoint_failure(self):
        """Test failed checkpoint approval."""
        self.mock_hitl_engine.process_decision.return_value = False
        result = self.cli_manager.approve_checkpoint('hitl_BE-07_abc12345', 'alice', 'Looks good to me')
        self.assertFalse(result)

    def test_reject_checkpoint_success(self):
        """Test successful checkpoint rejection."""
        self.mock_hitl_engine.process_decision.return_value = True
        result = self.cli_manager.reject_checkpoint('hitl_BE-07_abc12345', 'bob', 'Security concerns', 'Missing input validation')
        self.assertTrue(result)
        self.mock_hitl_engine.process_decision.assert_called_once()
        call_args = self.mock_hitl_engine.process_decision.call_args
        decision = call_args[0][1]
        self.assertEqual(decision['decision'], 'rejected')
        self.assertEqual(decision['reviewer'], 'bob')
        self.assertEqual(decision['reason'], 'Security concerns')
        self.assertEqual(decision['comments'], 'Missing input validation')

    def test_escalate_checkpoint_success(self):
        """Test successful checkpoint escalation."""
        self.mock_hitl_engine.escalate_checkpoint.return_value = True
        result = self.cli_manager.escalate_checkpoint('hitl_BE-07_abc12345', 'charlie', 'Needs management review', 2)
        self.assertTrue(result)
        self.mock_hitl_engine.escalate_checkpoint.assert_called_once()
        call_args = self.mock_hitl_engine.escalate_checkpoint.call_args
        self.assertEqual(call_args[0][0], 'hitl_BE-07_abc12345')
        escalation_data = call_args[0][1]
        self.assertEqual(escalation_data['escalated_by'], 'charlie')
        self.assertEqual(escalation_data['reason'], 'Needs management review')
        self.assertEqual(escalation_data['escalation_level'], 2)

    def test_show_audit_trail_by_checkpoint(self):
        """Test showing audit trail for specific checkpoint."""
        mock_audit_entries = [{'timestamp': '2025-06-08T10:00:00', 'action': 'created', 'user': 'system', 'checkpoint_id': 'hitl_BE-07_abc12345', 'details': 'Checkpoint created for output evaluation'}, {'timestamp': '2025-06-08T10:30:00', 'action': 'approved', 'user': 'alice', 'checkpoint_id': 'hitl_BE-07_abc12345', 'details': 'Approved after code review'}]
        self.mock_hitl_engine.get_audit_trail.return_value = mock_audit_entries
        result = self.cli_manager.show_audit_trail(checkpoint_id='hitl_BE-07_abc12345')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['action'], 'created')
        self.assertEqual(result[1]['action'], 'approved')
        self.mock_hitl_engine.get_audit_trail.assert_called_once_with(checkpoint_id='hitl_BE-07_abc12345')

    def test_show_audit_trail_by_task(self):
        """Test showing audit trail for specific task."""
        mock_audit_entries = [{'timestamp': '2025-06-08T10:00:00', 'action': 'created', 'user': 'system', 'task_id': 'BE-07', 'details': 'Task checkpoint created'}]
        self.mock_hitl_engine.get_audit_trail.return_value = mock_audit_entries
        result = self.cli_manager.show_audit_trail(task_id='BE-07')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['task_id'], 'BE-07')
        self.mock_hitl_engine.get_audit_trail.assert_called_once_with(task_id='BE-07')

    def test_show_metrics(self):
        """Test showing HITL metrics."""
        mock_metrics = {'checkpoints': {'total_created': 50, 'approved': 35, 'rejected': 10, 'escalated': 3, 'pending': 2}, 'response_times': {'average_hours': 4.2, 'median_hours': 3.8, 'sla_breaches': 2}, 'risk_distribution': {'low': 20, 'medium': 15, 'high': 10, 'critical': 5}}
        self.mock_hitl_engine.get_metrics.return_value = mock_metrics
        result = self.cli_manager.show_metrics(days=7)
        self.assertEqual(result['checkpoints']['total_created'], 50)
        self.assertEqual(result['response_times']['average_hours'], 4.2)
        self.assertEqual(result['risk_distribution']['critical'], 5)
        self.mock_hitl_engine.get_metrics.assert_called_once_with(days=7)

    def test_export_checkpoint_data_json(self):
        """Test exporting checkpoint data to JSON."""
        mock_checkpoint = Mock()
        mock_checkpoint.checkpoint_id = 'hitl_BE-07_abc12345'
        mock_checkpoint.task_id = 'BE-07'
        mock_checkpoint.checkpoint_type = 'output_evaluation'
        mock_checkpoint.status = CheckpointStatus.PENDING
        mock_checkpoint.risk_level = RiskLevel.HIGH
        mock_checkpoint.created_at = datetime(2025, 6, 8, 10, 0, 0)
        mock_checkpoint.deadline = None
        mock_checkpoint.description = 'Review critical code changes'
        mock_checkpoint.reviewers = ['Backend Engineer']
        mock_checkpoint.content = {'files': ['service.py']}
        mock_checkpoint.mitigation_suggestions = ['Run security scan']
        mock_checkpoint.metadata = {'priority': 'high'}
        self.mock_hitl_engine.get_checkpoint.return_value = mock_checkpoint
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        try:
            result = self.cli_manager.export_checkpoint_data('hitl_BE-07_abc12345', temp_path)
            self.assertTrue(result)
            with open(temp_path, 'r') as f:
                exported_data = json.load(f)
            self.assertEqual(exported_data['checkpoint_id'], 'hitl_BE-07_abc12345')
            self.assertEqual(exported_data['task_id'], 'BE-07')
            self.assertEqual(exported_data['status'], 'pending')
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_export_checkpoint_data_not_found(self):
        """Test exporting data for non-existent checkpoint."""
        self.mock_hitl_engine.get_checkpoint.return_value = None
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        try:
            result = self.cli_manager.export_checkpoint_data('nonexistent', temp_path)
            self.assertFalse(result)
        finally:
            Path(temp_path).unlink(missing_ok=True)

class TestHITLCLICommands(unittest.TestCase):
    """Test cases for HITL CLI command functions."""

    @patch('src.interfaces.cli.hitl_cli.HITLCLIManager')
    @patch('builtins.print')
    def test_cmd_list_checkpoints_empty(self, mock_print, mock_manager_class):
        """Test list command with no checkpoints."""
        mock_manager = Mock()
        mock_manager.list_pending_checkpoints.return_value = []
        mock_manager_class.return_value = mock_manager
        from src.interfaces.cli.hitl_cli import cmd_list_checkpoints
        args = Mock()
        args.task_id = None
        args.reviewer = None
        cmd_list_checkpoints(args)
        mock_print.assert_called_with('No pending checkpoints found.')

    @patch('src.interfaces.cli.hitl_cli.HITLCLIManager')
    @patch('builtins.print')
    def test_cmd_list_checkpoints_with_data(self, mock_print, mock_manager_class):
        """Test list command with checkpoints."""
        mock_checkpoints = [{'checkpoint_id': 'hitl_BE-07_abc12345', 'task_id': 'BE-07', 'checkpoint_type': 'output_evaluation', 'risk_level': 'high', 'reviewers': ['Backend Engineer'], 'deadline': '2025-06-08T18:00:00'}]
        mock_manager = Mock()
        mock_manager.list_pending_checkpoints.return_value = mock_checkpoints
        mock_manager_class.return_value = mock_manager
        from src.interfaces.cli.hitl_cli import cmd_list_checkpoints
        args = Mock()
        args.task_id = None
        args.reviewer = None
        cmd_list_checkpoints(args)
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        checkpoint_output = '\n'.join(print_calls)
        self.assertIn('hitl_BE-07_abc12345', checkpoint_output)
        self.assertIn('BE-07', checkpoint_output)
        self.assertIn('output_evaluation', checkpoint_output)

    @patch('src.interfaces.cli.hitl_cli.HITLCLIManager')
    @patch('builtins.print')
    def test_cmd_show_checkpoint_found(self, mock_print, mock_manager_class):
        """Test show command with existing checkpoint."""
        mock_details = {'checkpoint_id': 'hitl_BE-07_abc12345', 'task_id': 'BE-07', 'checkpoint_type': 'output_evaluation', 'status': 'pending', 'risk_level': 'high', 'created_at': '2025-06-08T10:00:00', 'deadline': '2025-06-08T18:00:00', 'reviewers': ['Backend Engineer'], 'description': 'Review critical code changes', 'mitigation_suggestions': ['Run security scan', 'Add unit tests'], 'content': {'files': ['service.py']}}
        mock_manager = Mock()
        mock_manager.show_checkpoint_details.return_value = mock_details
        mock_manager_class.return_value = mock_manager
        from src.interfaces.cli.hitl_cli import cmd_show_checkpoint
        args = Mock()
        args.checkpoint_id = 'hitl_BE-07_abc12345'
        cmd_show_checkpoint(args)
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        output = '\n'.join(print_calls)
        self.assertIn('hitl_BE-07_abc12345', output)
        self.assertIn('BE-07', output)
        self.assertIn('output_evaluation', output)
        self.assertIn('Run security scan', output)

    @patch('src.interfaces.cli.hitl_cli.HITLCLIManager')
    @patch('builtins.print')
    def test_cmd_show_checkpoint_not_found(self, mock_print, mock_manager_class):
        """Test show command with non-existent checkpoint."""
        mock_manager = Mock()
        mock_manager.show_checkpoint_details.return_value = None
        mock_manager_class.return_value = mock_manager
        from src.interfaces.cli.hitl_cli import cmd_show_checkpoint
        args = Mock()
        args.checkpoint_id = 'nonexistent'
        cmd_show_checkpoint(args)
        mock_print.assert_any_call('❌ Checkpoint nonexistent not found.')

    @patch('src.interfaces.cli.hitl_cli.HITLCLIManager')
    @patch('builtins.print')
    @patch('builtins.input')
    def test_cmd_approve_checkpoint_with_confirmation(self, mock_input, mock_print, mock_manager_class):
        """Test approve command with user confirmation."""
        mock_details = {'checkpoint_id': 'hitl_BE-07_abc12345', 'task_id': 'BE-07', 'checkpoint_type': 'output_evaluation', 'risk_level': 'high'}
        mock_manager = Mock()
        mock_manager.show_checkpoint_details.return_value = mock_details
        mock_manager.approve_checkpoint.return_value = True
        mock_manager_class.return_value = mock_manager
        mock_input.return_value = 'y'
        from src.interfaces.cli.hitl_cli import cmd_approve_checkpoint
        args = Mock()
        args.checkpoint_id = 'hitl_BE-07_abc12345'
        args.reviewer = 'alice'
        args.comments = 'Looks good'
        args.force = False
        cmd_approve_checkpoint(args)
        mock_manager.approve_checkpoint.assert_called_once_with('hitl_BE-07_abc12345', 'alice', 'Looks good')
        mock_print.assert_any_call('✅ Checkpoint hitl_BE-07_abc12345 approved by alice')

    @patch('src.interfaces.cli.hitl_cli.HITLCLIManager')
    @patch('builtins.print')
    @patch('builtins.input')
    def test_cmd_approve_checkpoint_cancelled(self, mock_input, mock_print, mock_manager_class):
        """Test approve command cancelled by user."""
        mock_details = {'checkpoint_id': 'hitl_BE-07_abc12345', 'task_id': 'BE-07', 'checkpoint_type': 'output_evaluation', 'risk_level': 'high'}
        mock_manager = Mock()
        mock_manager.show_checkpoint_details.return_value = mock_details
        mock_manager_class.return_value = mock_manager
        mock_input.return_value = 'n'
        from src.interfaces.cli.hitl_cli import cmd_approve_checkpoint
        args = Mock()
        args.checkpoint_id = 'hitl_BE-07_abc12345'
        args.reviewer = 'alice'
        args.comments = 'Looks good'
        args.force = False
        cmd_approve_checkpoint(args)
        mock_manager.approve_checkpoint.assert_not_called()
        mock_print.assert_any_call('❌ Approval cancelled.')
if __name__ == '__main__':
    unittest.main()