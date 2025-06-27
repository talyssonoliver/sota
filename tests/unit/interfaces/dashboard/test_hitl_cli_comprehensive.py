"""
Comprehensive Tests for HITL CLI

Extended test suite for the Human-in-the-Loop CLI interface
to validate command-line operations, validation, and user interactions.
"""
import argparse
import logging
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch
try:
    from src.interfaces.cli.hitl_cli import HITLCLIManager, setup_logging
except ImportError as e:
    logging.error(f'Failed to import HITL CLI components: {e}')

    class HITLCLIManager:
        """Mock HITLCLIManager."""

        def __init__(self, *args, **kwargs):
            pass

    def setup_logging():
        """Mock setup_logging function."""
        pass

class TestHITLCLIManager:
    """Test HITLCLIManager class comprehensively."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch('cli.hitl_cli.HITLPolicyEngine'), patch('cli.hitl_cli.HITLTaskMetadataManager'), patch('cli.hitl_cli.HITLDashboardManager'):
            self.cli_manager = HITLCLIManager()

    def test_cli_manager_initialization(self):
        """Test CLI manager initialization."""
        with patch('cli.hitl_cli.HITLPolicyEngine') as mock_engine, patch('cli.hitl_cli.HITLTaskMetadataManager') as mock_metadata, patch('cli.hitl_cli.HITLDashboardManager') as mock_dashboard:
            manager = HITLCLIManager()
            mock_engine.assert_called_once()
            mock_metadata.assert_called_once()
            mock_dashboard.assert_called_once()

    def test_list_pending_checkpoints(self):
        """Test listing pending checkpoints."""
        mock_checkpoints = [Mock(checkpoint_id='hitl_BE-07_abc123', task_id='BE-07', risk_level='high', created_at=datetime.now(), deadline=datetime.now() + timedelta(hours=4), reviewers=['john.doe'], checkpoint_type='output_evaluation'), Mock(checkpoint_id='hitl_FE-01_def456', task_id='FE-01', risk_level='medium', created_at=datetime.now(), deadline=datetime.now() + timedelta(hours=8), reviewers=['jane.smith'], checkpoint_type='qa_validation')]
        with patch.object(self.cli_manager.hitl_engine, 'get_pending_checkpoints', return_value=mock_checkpoints):
            result = self.cli_manager.list_pending_checkpoints()
            assert len(result) == 2
            assert result[0]['checkpoint_id'] == 'hitl_BE-07_abc123'
            assert result[1]['task_id'] == 'FE-01'

    def test_list_pending_checkpoints_by_reviewer(self):
        """Test listing pending checkpoints for specific reviewer."""
        mock_checkpoints = [Mock(checkpoint_id='hitl_BE-07_abc123', reviewers=['john.doe', 'jane.smith'], task_id='BE-07'), Mock(checkpoint_id='hitl_FE-01_def456', reviewers=['jane.smith'], task_id='FE-01')]
        with patch.object(self.cli_manager.hitl_engine, 'get_pending_checkpoints', return_value=mock_checkpoints):
            result = self.cli_manager.list_pending_checkpoints(reviewer='john.doe')
            assert len(result) == 1
            assert result[0]['checkpoint_id'] == 'hitl_BE-07_abc123'

    def test_list_pending_checkpoints_by_task(self):
        """Test listing pending checkpoints for specific task."""
        mock_checkpoints = [Mock(checkpoint_id='hitl_BE-07_abc123', task_id='BE-07'), Mock(checkpoint_id='hitl_BE-07_def456', task_id='BE-07'), Mock(checkpoint_id='hitl_FE-01_ghi789', task_id='FE-01')]
        with patch.object(self.cli_manager.hitl_engine, 'get_pending_checkpoints', return_value=mock_checkpoints):
            result = self.cli_manager.list_pending_checkpoints(task_id='BE-07')
            assert len(result) == 2
            assert all((cp['task_id'] == 'BE-07' for cp in result))

    def test_get_checkpoint_details(self):
        """Test getting detailed checkpoint information."""
        mock_checkpoint = Mock(checkpoint_id='hitl_BE-07_abc123', task_id='BE-07', checkpoint_type='output_evaluation', risk_level='high', status='pending', created_at=datetime.now(), deadline=datetime.now() + timedelta(hours=4), reviewers=['john.doe'], risk_factors=['database_changes', 'security_impact'], content={'code_changes': 'Added new API endpoint'}, approvals=[], rejections=[], escalation_level=0)
        with patch.object(self.cli_manager.hitl_engine, 'get_checkpoint', return_value=mock_checkpoint):
            result = self.cli_manager.get_checkpoint_details('hitl_BE-07_abc123')
            assert result['checkpoint_id'] == 'hitl_BE-07_abc123'
            assert result['task_id'] == 'BE-07'
            assert result['risk_level'] == 'high'
            assert 'risk_factors' in result
            assert 'content' in result

    def test_show_checkpoint_details(self):
        """Test showing checkpoint details (alternative method)."""
        mock_checkpoint = Mock(checkpoint_id='hitl_BE-07_abc123', task_id='BE-07', checkpoint_type='output_evaluation', status=Mock(value='pending'), risk_level=Mock(value='high'), created_at=datetime.now(), deadline=datetime.now() + timedelta(hours=4), reviewers=['john.doe'], description='Test checkpoint', content={'code_changes': 'Added new API'}, mitigation_suggestions=['Review code', 'Test thoroughly'], metadata={'version': '1.0'})
        with patch.object(self.cli_manager.hitl_engine, 'get_checkpoint', return_value=mock_checkpoint):
            result = self.cli_manager.show_checkpoint_details('hitl_BE-07_abc123')
            assert result['checkpoint_id'] == 'hitl_BE-07_abc123'
            assert result['task_id'] == 'BE-07'
            assert result['checkpoint_type'] == 'output_evaluation'
            assert result['status'] == 'pending'
            assert result['risk_level'] == 'high'

    def test_get_checkpoint_details_not_found(self):
        """Test getting details for non-existent checkpoint."""
        with patch.object(self.cli_manager.hitl_engine, 'get_checkpoint', return_value=None):
            result = self.cli_manager.get_checkpoint_details('nonexistent')
            assert result is None

    def test_approve_checkpoint(self):
        """Test approving a checkpoint."""
        with patch.object(self.cli_manager.hitl_engine, 'approve_checkpoint', return_value=True) as mock_approve:
            result = self.cli_manager.approve_checkpoint(checkpoint_id='hitl_BE-07_abc123', reviewer='john.doe', comments='Looks good, approved')
            assert result is True
            mock_approve.assert_called_once_with('hitl_BE-07_abc123', 'john.doe', 'Looks good, approved')

    def test_approve_checkpoint_failure(self):
        """Test checkpoint approval failure."""
        with patch.object(self.cli_manager.hitl_engine, 'approve_checkpoint', return_value=False):
            result = self.cli_manager.approve_checkpoint(checkpoint_id='hitl_BE-07_abc123', reviewer='john.doe', comments='Approved')
            assert result is False

    def test_reject_checkpoint(self):
        """Test rejecting a checkpoint."""
        with patch.object(self.cli_manager.hitl_engine, 'reject_checkpoint', return_value=True) as mock_reject:
            result = self.cli_manager.reject_checkpoint(checkpoint_id='hitl_BE-07_abc123', reviewer='john.doe', reason='Code quality issues', comments='Needs refactoring')
            assert result is True
            mock_reject.assert_called_once_with('hitl_BE-07_abc123', 'john.doe', 'Code quality issues', 'Needs refactoring')

    def test_escalate_checkpoint(self):
        """Test escalating a checkpoint."""
        with patch.object(self.cli_manager.hitl_engine, 'escalate_checkpoint', return_value=True) as mock_escalate:
            result = self.cli_manager.escalate_checkpoint(checkpoint_id='hitl_BE-07_abc123', escalated_by='john.doe', reason='Need senior review')
            assert result is True
            mock_escalate.assert_called_once_with('hitl_BE-07_abc123', 'john.doe', 'Need senior review')

    def test_get_checkpoint_history(self):
        """Test getting checkpoint history."""
        mock_history = [{'timestamp': datetime.now().isoformat(), 'action': 'created', 'user': 'system', 'details': {'checkpoint_type': 'output_evaluation'}}, {'timestamp': datetime.now().isoformat(), 'action': 'reviewed', 'user': 'john.doe', 'details': {'decision': 'approved'}}]
        with patch.object(self.cli_manager.hitl_engine, 'get_audit_trail', return_value=mock_history):
            result = self.cli_manager.get_checkpoint_history('hitl_BE-07_abc123')
            assert len(result) == 2
            assert result[0]['action'] == 'created'
            assert result[1]['user'] == 'john.doe'

    def test_show_audit_trail(self):
        """Test showing audit trail with various filters."""
        mock_audit_entries = [Mock(to_dict=lambda: {'timestamp': datetime.now().isoformat(), 'action': 'created', 'user': 'system', 'checkpoint_id': 'hitl_BE-07_abc123', 'task_id': 'BE-07', 'details': {'type': 'output_evaluation'}}), {'timestamp': datetime.now().isoformat(), 'action': 'approved', 'user': 'john.doe', 'checkpoint_id': 'hitl_BE-07_abc123', 'task_id': 'BE-07', 'details': {'decision': 'approved'}}]
        with patch.object(self.cli_manager.hitl_engine, 'get_audit_trail', return_value=mock_audit_entries):
            result = self.cli_manager.show_audit_trail(checkpoint_id='hitl_BE-07_abc123')
            assert len(result) == 2
            result = self.cli_manager.show_audit_trail(task_id='BE-07')
            assert len(result) == 2
            result = self.cli_manager.show_audit_trail()
            assert len(result) == 2

    def test_get_hitl_metrics(self):
        """Test getting HITL metrics."""
        mock_metrics = {'total_checkpoints': 50, 'pending_checkpoints': 5, 'approved_checkpoints': 40, 'rejected_checkpoints': 3, 'escalated_checkpoints': 2, 'average_review_time_hours': 4.5, 'approval_rate': 0.89}
        with patch.object(self.cli_manager.hitl_engine, 'get_metrics', return_value=mock_metrics):
            result = self.cli_manager.get_hitl_metrics(days=30)
            assert result['total_checkpoints'] == 50
            assert result['approval_rate'] == 0.89
            assert result['average_review_time_hours'] == 4.5

    def test_show_metrics(self):
        """Test showing HITL metrics with various time periods."""
        mock_metrics = {'checkpoints': {'total_created': 100, 'approved': 85, 'rejected': 10, 'escalated': 5, 'pending': 0}, 'response_times': {'average_hours': 3.2, 'median_hours': 2.8, 'sla_breaches': 2}, 'risk_distribution': {'low': 30, 'medium': 45, 'high': 20, 'critical': 5}}
        with patch.object(self.cli_manager.hitl_engine, 'get_metrics', return_value=mock_metrics):
            result = self.cli_manager.show_metrics(days=7)
            assert result['checkpoints']['total_created'] == 100
            assert result['response_times']['average_hours'] == 3.2
            assert result['risk_distribution']['high'] == 20

    def test_get_reviewer_stats(self):
        """Test getting reviewer statistics."""
        mock_stats = {'john.doe': {'checkpoints_reviewed': 20, 'checkpoints_approved': 18, 'checkpoints_rejected': 2, 'average_review_time_hours': 3.2}, 'jane.smith': {'checkpoints_reviewed': 15, 'checkpoints_approved': 14, 'checkpoints_rejected': 1, 'average_review_time_hours': 5.1}}
        with patch.object(self.cli_manager.hitl_engine, 'get_reviewer_statistics', return_value=mock_stats):
            result = self.cli_manager.get_reviewer_stats()
            assert 'john.doe' in result
            assert 'jane.smith' in result
            assert result['john.doe']['checkpoints_reviewed'] == 20

    def test_export_checkpoint_data(self):
        """Test exporting checkpoint data."""
        mock_checkpoint_details = {'checkpoint_id': 'hitl_BE-07_abc123', 'task_id': 'BE-07', 'status': 'approved', 'created_at': '2024-01-01T12:00:00', 'content': {'changes': 'Added new feature'}}
        with patch.object(self.cli_manager, 'show_checkpoint_details', return_value=mock_checkpoint_details), patch('builtins.open', create=True) as mock_open, patch('json.dump') as mock_json_dump:
            result = self.cli_manager.export_checkpoint_data('hitl_BE-07_abc123', 'export.json')
            assert result is True
            mock_open.assert_called_once()
            mock_json_dump.assert_called_once()

    def test_export_checkpoint_data_yaml(self):
        """Test exporting checkpoint data to YAML format."""
        mock_checkpoint_details = {'checkpoint_id': 'hitl_BE-07_abc123', 'task_id': 'BE-07', 'status': 'approved'}
        with patch.object(self.cli_manager, 'show_checkpoint_details', return_value=mock_checkpoint_details), patch('builtins.open', create=True) as mock_open, patch('yaml.dump') as mock_yaml_dump, patch('pathlib.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path_instance.suffix = '.yaml'
            mock_path.return_value = mock_path_instance
            result = self.cli_manager.export_checkpoint_data('hitl_BE-07_abc123', 'export.yaml')
            assert result is True
            mock_yaml_dump.assert_called_once()

    def test_export_checkpoint_data_not_found(self):
        """Test exporting data for non-existent checkpoint."""
        with patch.object(self.cli_manager, 'show_checkpoint_details', return_value=None):
            result = self.cli_manager.export_checkpoint_data('nonexistent', 'export.json')
            assert result is False

    def test_import_checkpoint_data(self):
        """Test importing checkpoint data."""
        mock_data = [{'checkpoint_id': 'hitl_BE-07_abc123', 'task_id': 'BE-07', 'status': 'pending'}]
        with patch('builtins.open', create=True) as mock_open, patch('json.load', return_value=mock_data), patch.object(self.cli_manager.hitl_engine, 'import_checkpoint', return_value=True):
            result = self.cli_manager.import_checkpoint_data('import.json')
            assert result is True

    def test_validate_checkpoint_integrity(self):
        """Test validating checkpoint data integrity."""
        mock_checkpoint = Mock(checkpoint_id='hitl_BE-07_abc123', task_id='BE-07', created_at=datetime.now(), status='pending')
        with patch.object(self.cli_manager.hitl_engine, 'get_checkpoint', return_value=mock_checkpoint):
            result = self.cli_manager.validate_checkpoint_integrity('hitl_BE-07_abc123')
            assert result['valid'] is True
            assert 'errors' in result
            assert 'warnings' in result

class TestHITLCLICommands:
    """Test HITL CLI command-line interface."""

    def test_setup_logging_default(self):
        """Test logging setup with default settings."""
        with patch('logging.basicConfig') as mock_config:
            setup_logging()
            mock_config.assert_called_once()
            args, kwargs = mock_config.call_args
            assert kwargs['level'] == 20

    def test_setup_logging_verbose(self):
        """Test logging setup with verbose mode."""
        with patch('logging.basicConfig') as mock_config:
            setup_logging(verbose=True)
            mock_config.assert_called_once()
            args, kwargs = mock_config.call_args
            assert kwargs['level'] == 10

    def test_list_command_execution(self):
        """Test list command execution."""
        mock_args = argparse.Namespace(command='list', reviewer=None, task_id=None, format='table', verbose=False)
        mock_checkpoints = [{'checkpoint_id': 'hitl_BE-07_abc123', 'task_id': 'BE-07', 'risk_level': 'high', 'deadline': '2024-01-01T16:00:00'}]
        with patch('cli.hitl_cli.HITLCLIManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.list_pending_checkpoints.return_value = mock_checkpoints
            mock_manager_class.return_value = mock_manager
            from src.interfaces.cli.hitl_cli import handle_list_command
            result = handle_list_command(mock_args)
            assert result == 0
            mock_manager.list_pending_checkpoints.assert_called_once()

    def test_details_command_execution(self):
        """Test details command execution."""
        mock_args = argparse.Namespace(command='details', checkpoint_id='hitl_BE-07_abc123', format='json', verbose=False)
        mock_details = {'checkpoint_id': 'hitl_BE-07_abc123', 'task_id': 'BE-07', 'status': 'pending', 'content': {'changes': 'Added new feature'}}
        with patch('cli.hitl_cli.HITLCLIManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.get_checkpoint_details.return_value = mock_details
            mock_manager_class.return_value = mock_manager
            from src.interfaces.cli.hitl_cli import handle_details_command
            result = handle_details_command(mock_args)
            assert result == 0
            mock_manager.get_checkpoint_details.assert_called_once_with('hitl_BE-07_abc123')

    def test_approve_command_execution(self):
        """Test approve command execution."""
        mock_args = argparse.Namespace(command='approve', checkpoint_id='hitl_BE-07_abc123', reviewer='john.doe', comments='Approved after review', verbose=False)
        with patch('cli.hitl_cli.HITLCLIManager') as mock_manager_class, patch('cli.hitl_cli.validate_checkpoint_id', return_value='hitl_BE-07_abc123'), patch('cli.hitl_cli.validate_reviewer_name', return_value='john.doe'):
            mock_manager = Mock()
            mock_manager.approve_checkpoint.return_value = True
            mock_manager_class.return_value = mock_manager
            from src.interfaces.cli.hitl_cli import handle_approve_command
            result = handle_approve_command(mock_args)
            assert result == 0
            mock_manager.approve_checkpoint.assert_called_once()

    def test_reject_command_execution(self):
        """Test reject command execution."""
        mock_args = argparse.Namespace(command='reject', checkpoint_id='hitl_BE-07_abc123', reviewer='john.doe', reason='Code quality issues', comments='Needs refactoring', verbose=False)
        with patch('cli.hitl_cli.HITLCLIManager') as mock_manager_class, patch('cli.hitl_cli.validate_checkpoint_id', return_value='hitl_BE-07_abc123'), patch('cli.hitl_cli.validate_reviewer_name', return_value='john.doe'):
            mock_manager = Mock()
            mock_manager.reject_checkpoint.return_value = True
            mock_manager_class.return_value = mock_manager
            from src.interfaces.cli.hitl_cli import handle_reject_command
            result = handle_reject_command(mock_args)
            assert result == 0
            mock_manager.reject_checkpoint.assert_called_once()

    def test_escalate_command_execution(self):
        """Test escalate command execution."""
        mock_args = argparse.Namespace(command='escalate', checkpoint_id='hitl_BE-07_abc123', escalated_by='john.doe', reason='Need senior review', verbose=False)
        with patch('cli.hitl_cli.HITLCLIManager') as mock_manager_class, patch('cli.hitl_cli.validate_checkpoint_id', return_value='hitl_BE-07_abc123'), patch('cli.hitl_cli.validate_reviewer_name', return_value='john.doe'):
            mock_manager = Mock()
            mock_manager.escalate_checkpoint.return_value = True
            mock_manager_class.return_value = mock_manager
            from src.interfaces.cli.hitl_cli import handle_escalate_command
            result = handle_escalate_command(mock_args)
            assert result == 0
            mock_manager.escalate_checkpoint.assert_called_once()

    def test_metrics_command_execution(self):
        """Test metrics command execution."""
        mock_args = argparse.Namespace(command='metrics', days=30, format='table', verbose=False)
        mock_metrics = {'total_checkpoints': 100, 'approval_rate': 0.85, 'average_review_time_hours': 4.2}
        with patch('cli.hitl_cli.HITLCLIManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.get_hitl_metrics.return_value = mock_metrics
            mock_manager_class.return_value = mock_manager
            from src.interfaces.cli.hitl_cli import handle_metrics_command
            result = handle_metrics_command(mock_args)
            assert result == 0
            mock_manager.get_hitl_metrics.assert_called_once_with(days=30)

    def test_export_command_execution(self):
        """Test export command execution."""
        mock_args = argparse.Namespace(command='export', output_file='checkpoints.json', format='json', verbose=False)
        with patch('cli.hitl_cli.HITLCLIManager') as mock_manager_class, patch('cli.hitl_cli.validate_file_path', return_value=Path('checkpoints.json')):
            mock_manager = Mock()
            mock_manager.export_checkpoint_data.return_value = True
            mock_manager_class.return_value = mock_manager
            from src.interfaces.cli.hitl_cli import handle_export_command
            result = handle_export_command(mock_args)
            assert result == 0
            mock_manager.export_checkpoint_data.assert_called_once()

class TestHITLCLIValidation:
    """Test HITL CLI input validation."""

    def test_validate_checkpoint_id_valid(self):
        """Test valid checkpoint ID validation."""
        from src.interfaces.cli.hitl_cli import validate_checkpoint_id
        valid_ids = ['hitl_BE-07_abc12345', 'hitl_FE-123_def67890', 'hitl_TL-01_xyz98765']
        for checkpoint_id in valid_ids:
            result = validate_checkpoint_id(checkpoint_id)
            assert result == checkpoint_id

    def test_validate_checkpoint_id_invalid(self):
        """Test invalid checkpoint ID validation."""
        from src.interfaces.cli.hitl_cli import validate_checkpoint_id
        invalid_ids = ['invalid_format', 'hitl_INVALID_short', 'missing_prefix_BE-07_abc123', 'hitl_BE-07']
        for checkpoint_id in invalid_ids:
            with self.assertRaises(Exception):
                validate_checkpoint_id(checkpoint_id)

    def test_validate_reviewer_name_valid(self):
        """Test valid reviewer name validation."""
        from src.interfaces.cli.hitl_cli import validate_reviewer_name
        valid_names = ['john.doe', 'jane-smith', 'user123', 'admin']
        for name in valid_names:
            result = validate_reviewer_name(name)
            assert result == name

    def test_validate_reviewer_name_invalid(self):
        """Test invalid reviewer name validation."""
        from src.interfaces.cli.hitl_cli import validate_reviewer_name
        invalid_names = ['', '123invalid', 'user@domain', 'very_long_name_that_exceeds_the_maximum_length_limit']
        for name in invalid_names:
            with self.assertRaises(Exception):
                validate_reviewer_name(name)

class TestHITLCLIIntegration:
    """Test HITL CLI integration scenarios."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / 'test_export.json'

    def teardown_method(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_review_workflow(self):
        """Test complete checkpoint review workflow."""
        with patch('cli.hitl_cli.HITLCLIManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.list_pending_checkpoints.return_value = [{'checkpoint_id': 'hitl_BE-07_abc123', 'task_id': 'BE-07', 'risk_level': 'high'}]
            mock_manager.get_checkpoint_details.return_value = {'checkpoint_id': 'hitl_BE-07_abc123', 'content': {'changes': 'Added new API'}, 'risk_factors': ['database_changes']}
            mock_manager.approve_checkpoint.return_value = True
            mock_manager_class.return_value = mock_manager
            cli_manager = HITLCLIManager()
            pending = cli_manager.list_pending_checkpoints()
            assert len(pending) == 1
            details = cli_manager.get_checkpoint_details('hitl_BE-07_abc123')
            assert details['checkpoint_id'] == 'hitl_BE-07_abc123'
            approved = cli_manager.approve_checkpoint('hitl_BE-07_abc123', 'john.doe', 'Reviewed and approved')
            assert approved is True

    def test_bulk_operations_workflow(self):
        """Test bulk operations on multiple checkpoints."""
        with patch('cli.hitl_cli.HITLCLIManager') as mock_manager_class:
            mock_manager = Mock()
            mock_checkpoints = [{'checkpoint_id': f'hitl_BE-{i:02d}_abc{i}23', 'task_id': f'BE-{i:02d}'} for i in range(1, 6)]
            mock_manager.list_pending_checkpoints.return_value = mock_checkpoints
            mock_manager.approve_checkpoint.return_value = True
            mock_manager_class.return_value = mock_manager
            cli_manager = HITLCLIManager()
            pending = cli_manager.list_pending_checkpoints()
            assert len(pending) == 5
            approval_results = []
            for checkpoint in pending:
                result = cli_manager.approve_checkpoint(checkpoint['checkpoint_id'], 'bulk_reviewer', 'Bulk approval')
                approval_results.append(result)
            assert all(approval_results)
            assert mock_manager.approve_checkpoint.call_count == 5

    def test_error_handling_workflow(self):
        """Test error handling in CLI workflows."""
        with patch('cli.hitl_cli.HITLCLIManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.get_checkpoint_details.return_value = None
            mock_manager.approve_checkpoint.return_value = False
            mock_manager_class.return_value = mock_manager
            cli_manager = HITLCLIManager()
            details = cli_manager.get_checkpoint_details('nonexistent')
            assert details is None
            approved = cli_manager.approve_checkpoint('hitl_BE-07_abc123', 'john.doe', 'Approval attempt')
            assert approved is False

    def test_data_export_import_workflow(self):
        """Test data export and import workflow."""
        export_data = [{'checkpoint_id': 'hitl_BE-07_abc123', 'task_id': 'BE-07', 'status': 'approved', 'created_at': '2024-01-01T12:00:00'}]
        with patch('cli.hitl_cli.HITLCLIManager') as mock_manager_class, patch('builtins.open', create=True) as mock_open, patch('json.dump') as mock_json_dump, patch('json.load', return_value=export_data):
            mock_manager = Mock()
            mock_manager.export_checkpoint_data.return_value = True
            mock_manager.import_checkpoint_data.return_value = True
            mock_manager_class.return_value = mock_manager
            cli_manager = HITLCLIManager()
            export_result = cli_manager.export_checkpoint_data(str(self.test_file), format='json')
            assert export_result is True
            import_result = cli_manager.import_checkpoint_data(str(self.test_file))
            assert import_result is True
if __name__ == '__main__':
    unittest.main()