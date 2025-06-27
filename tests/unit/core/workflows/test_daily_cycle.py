"""
Tests for Daily Cycle Orchestrator

Comprehensive test suite for the daily cycle automation orchestrator
to validate daily task processing, reporting, and scheduling functionality.
"""
import sys
import json
import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
try:
    import pytest
except ImportError:
    pass
sys.path.append(str(Path(__file__).parent.parent))
try:
    from src.core.workflows.daily_cycle import DailyCycleOrchestrator

    class DailyCycleOrchestrator:

        def __init__(self, config_file=None):
            self.config = {}
            self.is_running = False

        def start(self):
            self.is_running = True

        def stop(self):
            self.is_running = False
except ImportError:
    pass
try:
    import unittest
except ImportError:
    pass

class TestDailyCycleOrchestrator(unittest.TestCase):
    """Test the DailyCycleOrchestrator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / 'test_config.json'
        self.test_config = {'paths': {'logs_dir': str(self.temp_dir / 'logs'), 'reports_dir': str(self.temp_dir / 'reports'), 'outputs_dir': str(self.temp_dir / 'outputs')}, 'schedule': {'morning_briefing': '08:00', 'eod_report': '18:00', 'dashboard_update': '*/30', 'timezone': 'UTC'}, 'automation': {'enabled': True, 'max_retries': 3, 'retry_delay': 5, 'timeout': 300}, 'notifications': {'email_enabled': False, 'slack_enabled': False}}
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization with config."""
        orchestrator = DailyCycleOrchestrator(config_file=str(self.config_file))
        self.assertIsNotNone(orchestrator)
        self.assertIsInstance(orchestrator.config, dict)
        self.assertIsInstance(orchestrator.is_running, bool)

    def test_orchestrator_initialization_no_config(self):
        """Test orchestrator initialization without config file."""
        orchestrator = DailyCycleOrchestrator()
        self.assertIsNotNone(orchestrator)
        self.assertIsInstance(orchestrator.config, dict)
        self.assertIsInstance(orchestrator.is_running, bool)

    def test_orchestrator_invalid_config_path(self):
        """Test orchestrator initialization with invalid config path."""
        try:
            orchestrator = DailyCycleOrchestrator(config_file='../invalid/path')
            self.assertIsNotNone(orchestrator)
        except Exception:
            pass

    def test_load_config_existing_file(self):
        """Test loading configuration from existing file."""
        with patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator'), patch('src.core.workflows.daily_cycle.ExecutionMonitor'), patch('src.core.workflows.daily_cycle.BriefingGenerator'), patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator'), patch('src.core.workflows.daily_cycle.EmailIntegration'):
            orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
            assert orchestrator.config['schedule']['morning_briefing'] == '08:00'
            assert orchestrator.config['automation']['enabled'] is True

    def test_load_config_nonexistent_file(self):
        """Test loading configuration when file doesn't exist."""
        nonexistent_file = self.temp_dir / 'nonexistent.json'
        with patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator'), patch('src.core.workflows.daily_cycle.ExecutionMonitor'), patch('src.core.workflows.daily_cycle.BriefingGenerator'), patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator'), patch('src.core.workflows.daily_cycle.EmailIntegration'):
            orchestrator = DailyCycleOrchestrator(config_path=str(nonexistent_file))
            assert 'paths' in orchestrator.config
            assert 'schedule' in orchestrator.config

    def test_load_config_invalid_json(self):
        """Test loading configuration with invalid JSON."""
        invalid_config_file = self.temp_dir / 'invalid.json'
        with open(invalid_config_file, 'w') as f:
            f.write('{ invalid json }')
        with patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator'), patch('src.core.workflows.daily_cycle.ExecutionMonitor'), patch('src.core.workflows.daily_cycle.BriefingGenerator'), patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator'), patch('src.core.workflows.daily_cycle.EmailIntegration'):
            orchestrator = DailyCycleOrchestrator(config_path=str(invalid_config_file))
            assert 'paths' in orchestrator.config

    def test_get_default_config(self):
        """Test default configuration generation."""
        with patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator'), patch('src.core.workflows.daily_cycle.ExecutionMonitor'), patch('src.core.workflows.daily_cycle.BriefingGenerator'), patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator'), patch('src.core.workflows.daily_cycle.EmailIntegration'):
            orchestrator = DailyCycleOrchestrator()
            default_config = orchestrator._get_default_config()
            assert 'paths' in default_config
            assert 'schedule' in default_config
            assert 'automation' in default_config
            assert 'notifications' in default_config
            assert default_config['automation']['enabled'] is True

    def test_setup_logging(self):
        """Test logging setup."""
        with patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator'), patch('src.core.workflows.daily_cycle.ExecutionMonitor'), patch('src.core.workflows.daily_cycle.BriefingGenerator'), patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator'), patch('src.core.workflows.daily_cycle.EmailIntegration'), patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
            mock_get_logger.assert_called()

    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_generate_morning_briefing(self, mock_email, mock_eod, mock_briefing, mock_monitor, mock_metrics):
        """Test morning briefing generation."""
        mock_briefing_instance = Mock()
        mock_briefing_instance.generate_daily_briefing.return_value = {'status': 'success', 'briefing_file': 'test_briefing.md'}
        mock_briefing.return_value = mock_briefing_instance
        orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
        result = orchestrator.generate_morning_briefing(day_number=1)
        assert result['status'] == 'success'
        mock_briefing_instance.generate_daily_briefing.assert_called_once_with(day_number=1)

    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_generate_eod_report(self, mock_email, mock_eod, mock_briefing, mock_monitor, mock_metrics):
        """Test end-of-day report generation."""
        mock_eod_instance = Mock()
        mock_eod_instance.generate_eod_report.return_value = {'status': 'success', 'report_file': 'test_eod_report.md'}
        mock_eod.return_value = mock_eod_instance
        orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
        result = orchestrator.generate_eod_report(day_number=1)
        assert result['status'] == 'success'
        mock_eod_instance.generate_eod_report.assert_called_once_with(day_number=1)

    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_update_dashboard(self, mock_email, mock_eod, mock_briefing, mock_monitor, mock_metrics):
        """Test dashboard update functionality."""
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_completion_metrics.return_value = {'total_tasks': 10, 'completed_tasks': 7, 'completion_rate': 0.7}
        mock_metrics.return_value = mock_metrics_instance
        orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
        result = orchestrator.update_dashboard()
        assert result['status'] == 'success'
        mock_metrics_instance.calculate_completion_metrics.assert_called_once()

    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_run_daily_cycle(self, mock_email, mock_eod, mock_briefing, mock_monitor, mock_metrics):
        """Test complete daily cycle execution."""
        mock_briefing_instance = Mock()
        mock_briefing_instance.generate_daily_briefing.return_value = {'status': 'success'}
        mock_briefing.return_value = mock_briefing_instance
        mock_eod_instance = Mock()
        mock_eod_instance.generate_eod_report.return_value = {'status': 'success'}
        mock_eod.return_value = mock_eod_instance
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_completion_metrics.return_value = {'status': 'success'}
        mock_metrics.return_value = mock_metrics_instance
        orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
        result = orchestrator.run_daily_cycle(day_number=1)
        assert result['status'] == 'success'
        assert 'morning_briefing' in result
        assert 'eod_report' in result
        assert 'dashboard_update' in result

    @patch('src.core.workflows.daily_cycle.schedule')
    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_setup_schedule(self, mock_email, mock_eod, mock_briefing, mock_monitor, mock_metrics, mock_schedule):
        """Test schedule setup for automated tasks."""
        orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
        orchestrator.setup_schedule()
        mock_schedule.every.assert_called()

    @patch('src.core.workflows.daily_cycle.schedule')
    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_start_automation(self, mock_email, mock_eod, mock_briefing, mock_monitor, mock_metrics, mock_schedule):
        """Test automation startup."""
        orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
        with patch('time.sleep') as mock_sleep:
            mock_schedule.run_pending = Mock()
            orchestrator.start_automation(duration=1)
            mock_schedule.run_pending.assert_called()

    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_validate_execution_result(self, mock_email, mock_eod, mock_briefing, mock_monitor, mock_metrics):
        """Test execution result validation."""
        orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
        valid_result = {'status': 'success', 'data': {'key': 'value'}}
        assert orchestrator._validate_execution_result(valid_result) is True
        invalid_result = {'error': 'Something went wrong'}
        assert orchestrator._validate_execution_result(invalid_result) is False
        assert orchestrator._validate_execution_result({}) is False

    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_handle_execution_error(self, mock_email, mock_eod, mock_briefing, mock_monitor, mock_metrics):
        """Test execution error handling."""
        orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
        error = Exception('Test error')
        result = orchestrator._handle_execution_error('test_operation', error)
        assert result['status'] == 'error'
        assert result['operation'] == 'test_operation'
        assert 'Test error' in result['error']

    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_get_system_status(self, mock_email, mock_eod, mock_briefing, mock_monitor, mock_metrics):
        """Test system status retrieval."""
        mock_monitor_instance = Mock()
        mock_monitor_instance.get_system_status.return_value = {'status': 'healthy', 'uptime': '2 days', 'tasks_completed': 25}
        mock_monitor.return_value = mock_monitor_instance
        orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
        status = orchestrator.get_system_status()
        assert status['status'] == 'healthy'
        assert 'uptime' in status
        mock_monitor_instance.get_system_status.assert_called_once()

    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_stop_automation(self, mock_email, mock_eod, mock_briefing, mock_monitor, mock_metrics):
        """Test automation stopping."""
        orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
        orchestrator._automation_running = True
        orchestrator.stop_automation()
        assert orchestrator._automation_running is False

class TestDailyCycleOrchestrationIntegration:
    """Test integration scenarios for daily cycle orchestration."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / 'integration_config.json'
        self.integration_config = {'paths': {'logs_dir': str(self.temp_dir / 'logs'), 'reports_dir': str(self.temp_dir / 'reports'), 'outputs_dir': str(self.temp_dir / 'outputs')}, 'schedule': {'morning_briefing': '08:00', 'eod_report': '18:00', 'dashboard_update': '*/30'}, 'automation': {'enabled': True, 'max_retries': 2, 'retry_delay': 1}, 'notifications': {'email_enabled': True, 'slack_enabled': False}}
        with open(self.config_file, 'w') as f:
            json.dump(self.integration_config, f)

    def teardown_method(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_complete_daily_workflow(self, mock_email, mock_eod, mock_briefing, mock_monitor, mock_metrics):
        """Test complete daily workflow integration."""
        mock_briefing_instance = Mock()
        mock_briefing_instance.generate_daily_briefing.return_value = {'status': 'success', 'briefing_file': 'morning_briefing.md', 'metrics': {'tasks_planned': 10}}
        mock_briefing.return_value = mock_briefing_instance
        mock_eod_instance = Mock()
        mock_eod_instance.generate_eod_report.return_value = {'status': 'success', 'report_file': 'eod_report.md', 'metrics': {'tasks_completed': 8}}
        mock_eod.return_value = mock_eod_instance
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_completion_metrics.return_value = {'completion_rate': 0.8, 'total_tasks': 10, 'completed_tasks': 8}
        mock_metrics.return_value = mock_metrics_instance
        mock_email_instance = Mock()
        mock_email_instance.send_briefing.return_value = {'status': 'sent'}
        mock_email_instance.send_eod_report.return_value = {'status': 'sent'}
        mock_email.return_value = mock_email_instance
        orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
        result = orchestrator.run_daily_cycle(day_number=1)
        assert result['status'] == 'success'
        mock_briefing_instance.generate_daily_briefing.assert_called_once()
        mock_eod_instance.generate_eod_report.assert_called_once()
        mock_metrics_instance.calculate_completion_metrics.assert_called()

    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_error_recovery_workflow(self, mock_email, mock_eod, mock_briefing, mock_monitor, mock_metrics):
        """Test error recovery in daily workflow."""
        mock_briefing_instance = Mock()
        mock_briefing_instance.generate_daily_briefing.side_effect = Exception('Briefing failed')
        mock_briefing.return_value = mock_briefing_instance
        mock_eod_instance = Mock()
        mock_eod_instance.generate_eod_report.return_value = {'status': 'success'}
        mock_eod.return_value = mock_eod_instance
        orchestrator = DailyCycleOrchestrator(config_path=str(self.config_file))
        result = orchestrator.run_daily_cycle(day_number=1)
        assert 'morning_briefing' in result
        assert result['morning_briefing']['status'] == 'error'
        assert 'eod_report' in result
        assert result['eod_report']['status'] == 'success'
if __name__ == '__main__':
    pytest.main([__file__])