"""
test_generate_briefing_comprehensive.py - Optimized Test Structure

Migrated from: tests/workflows\\test_generate_briefing_comprehensive.py
New location: tests/unit\\core\\test_generate_briefing_comprehensive.py

Part of the optimized test pyramid reorganization:
- Tests now mirror src/ structure
- Proper categorization (unit/integration/e2e)
- Improved mocking and isolation

Comprehensive Tests for Briefing Generator

Extended test suite for the briefing generation system
to validate daily briefing creation, metrics integration, and report formatting.
"""
import tempfile
import shutil
import pytest
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
try:
    from src.core.workflows.generate_briefing import BriefingGenerator
except ImportError:
    pass

class TestBriefingGenerator:
    """Test BriefingGenerator class comprehensively."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.briefing_generator = BriefingGenerator()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_briefing_generator_initialization(self):
        """Test briefing generator initialization."""
        generator = BriefingGenerator()
        assert hasattr(generator, 'logger')
        assert hasattr(generator, 'generate_daily_briefing')

    def test_generate_daily_briefing_basic(self):
        """Test basic daily briefing generation."""
        result = self.briefing_generator.generate_daily_briefing(day_number=1)
        assert result['status'] == 'success'
        assert 'briefing_file' in result
        assert result['day_number'] == 1

    def test_generate_daily_briefing_with_custom_date(self):
        """Test daily briefing generation with custom date."""
        custom_date = datetime(2024, 6, 15)
        result = self.briefing_generator.generate_daily_briefing(day_number=5, target_date=custom_date)
        assert result['status'] == 'success'
        assert result['target_date'] == custom_date.isoformat()

    def test_generate_briefing_content_structure(self):
        """Test briefing content structure and formatting."""
        result = self.briefing_generator.generate_daily_briefing(day_number=2)
        assert result['status'] == 'success'
        assert 'briefing_content' in result
        assert 'metrics_summary' in result
        assert 'system_status' in result

    @patch('builtins.open', create=True)
    def test_generate_briefing_file_output(self, mock_open):
        """Test briefing file generation and output."""
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        result = self.briefing_generator.generate_daily_briefing(day_number=1, output_dir=str(self.temp_dir))
        assert result['status'] == 'success'
        assert 'briefing_file' in result
        mock_open.assert_called()
        mock_file.write.assert_called()

    def test_generate_briefing_error_handling(self):
        """Test error handling in briefing generation."""
        # Temporarily replace the metrics calculator with one that raises an error
        original_calculator = self.briefing_generator.metrics_calculator
        error_calculator = Mock()
        error_calculator.calculate_completion_metrics.side_effect = Exception('Metrics calculation failed')
        self.briefing_generator.metrics_calculator = error_calculator
        
        result = self.briefing_generator.generate_daily_briefing(day_number=1)
        assert result['status'] == 'error'
        assert 'error' in result
        assert 'Metrics calculation failed' in result['error']
        
        # Restore original calculator
        self.briefing_generator.metrics_calculator = original_calculator

    def test_generate_briefing_with_recommendations(self):
        """Test briefing generation with performance recommendations."""
        # Override the mock objects to return specific data
        original_calculator = self.briefing_generator.metrics_calculator
        custom_calculator = Mock()
        custom_calculator.calculate_completion_metrics.return_value = {
            'total_tasks': 20, 'completed_tasks': 10, 'completion_rate': 0.5, 
            'bottlenecks': ['qa_validation', 'dependency_resolution'], 
            'recommendations': ['Increase QA resources', 'Review dependency management']
        }
        self.briefing_generator.metrics_calculator = custom_calculator
        
        original_monitor = self.briefing_generator.execution_monitor
        custom_monitor = Mock()
        custom_monitor.get_system_status.return_value = {
            'status': 'degraded', 
            'warnings': ['High memory usage', 'Slow response times']
        }
        self.briefing_generator.execution_monitor = custom_monitor
        
        result = self.briefing_generator.generate_daily_briefing(day_number=3)
        assert result['status'] == 'success'
        assert 'recommendations' in result
        assert len(result['recommendations']) >= 2
        assert 'warnings' in result
        
        # Restore original objects
        self.briefing_generator.metrics_calculator = original_calculator
        self.briefing_generator.execution_monitor = original_monitor

    def test_generate_weekly_summary(self):
        """Test weekly summary generation."""
        result = self.briefing_generator.generate_weekly_summary(week_number=1)
        assert result['status'] == 'success'
        assert result['week_number'] == 1
        assert result['weekly_completion_rate'] == 0.84
        assert 'daily_breakdown' in result

    def test_load_briefing_template(self):
        """Test loading briefing template (uses default when file doesn't exist)."""
        # Test with non-existent file to use default template
        template = self.briefing_generator.load_briefing_template('nonexistent_template.yaml')
        assert template['title'].format(day_number=1) == 'Daily Sprint Briefing - Day 1'
        assert 'sections' in template
        assert template['format'] == 'markdown'

    @patch('pathlib.Path.exists')
    def test_load_briefing_template_not_found(self, mock_exists):
        """Test loading non-existent briefing template."""
        mock_exists.return_value = False
        template = self.briefing_generator.load_briefing_template('nonexistent.yaml')
        assert template is not None
        assert 'title' in template
        assert 'sections' in template

    def test_format_briefing_markdown(self):
        """Test markdown formatting of briefing content."""
        briefing_data = {'day_number': 1, 'date': datetime.now().isoformat(), 'metrics_summary': {'total_tasks': 10, 'completed_tasks': 8, 'completion_rate': 0.8}, 'system_status': {'status': 'healthy', 'uptime': '24 hours'}, 'recommendations': ['Continue current pace', 'Review remaining tasks']}
        markdown_content = self.briefing_generator.format_briefing_markdown(briefing_data)
        assert '# Daily Sprint Briefing' in markdown_content
        assert 'Day 1' in markdown_content
        assert '80.0%' in markdown_content
        assert 'healthy' in markdown_content
        assert 'Continue current pace' in markdown_content

    def test_format_briefing_json(self):
        """Test JSON formatting of briefing content."""
        briefing_data = {'day_number': 2, 'metrics': {'completion_rate': 0.75}, 'status': 'active'}
        json_content = self.briefing_generator.format_briefing_json(briefing_data)
        parsed_json = json.loads(json_content)
        assert parsed_json['day_number'] == 2
        assert parsed_json['metrics']['completion_rate'] == 0.75
        assert parsed_json['status'] == 'active'

    def test_calculate_trend_analysis(self):
        """Test trend analysis calculation."""
        historical_data = [{'day': 1, 'completion_rate': 0.7}, {'day': 2, 'completion_rate': 0.75}, {'day': 3, 'completion_rate': 0.8}, {'day': 4, 'completion_rate': 0.85}]
        trend_analysis = self.briefing_generator.calculate_trend_analysis(historical_data)
        assert trend_analysis['trend'] == 'improving'
        assert trend_analysis['average_rate'] == 0.775
        assert trend_analysis['rate_change'] > 0

    def test_calculate_trend_analysis_declining(self):
        """Test trend analysis for declining performance."""
        historical_data = [{'day': 1, 'completion_rate': 0.9}, {'day': 2, 'completion_rate': 0.8}, {'day': 3, 'completion_rate': 0.7}, {'day': 4, 'completion_rate': 0.6}]
        trend_analysis = self.briefing_generator.calculate_trend_analysis(historical_data)
        assert trend_analysis['trend'] == 'declining'
        assert trend_analysis['rate_change'] < 0

    def test_generate_performance_alerts(self):
        """Test performance alert generation."""
        # Override the mock calculator to return specific metrics
        original_calculator = self.briefing_generator.metrics_calculator
        custom_calculator = Mock()
        custom_calculator.calculate_completion_metrics.return_value = {
            'completion_rate': 0.3, 'failed_tasks': 5, 'overdue_tasks': 3
        }
        self.briefing_generator.metrics_calculator = custom_calculator
        
        alerts = self.briefing_generator.generate_performance_alerts()
        assert len(alerts) > 0
        alert_types = [alert['type'] for alert in alerts]
        assert 'low_completion_rate' in alert_types
        assert any(('30%' in alert['message'] for alert in alerts))
        
        # Restore original calculator
        self.briefing_generator.metrics_calculator = original_calculator

    def test_validate_briefing_data(self):
        """Test briefing data validation."""
        valid_data = {'day_number': 1, 'date': datetime.now().isoformat(), 'metrics_summary': {'total_tasks': 10, 'completed_tasks': 8}, 'system_status': {'status': 'healthy'}}
        is_valid = self.briefing_generator.validate_briefing_data(valid_data)
        assert is_valid is True
        invalid_data = {'day_number': 'invalid', 'metrics_summary': 'invalid'}
        is_valid = self.briefing_generator.validate_briefing_data(invalid_data)
        assert is_valid is False

    def test_send_briefing_email(self):
        """Test email sending functionality."""
        briefing_content = 'Daily briefing content'
        recipients = ['team@example.com', 'manager@example.com']
        result = self.briefing_generator.send_briefing_email(briefing_content, recipients, subject='Daily Sprint Briefing - Day 1')
        assert result['status'] == 'success'
        assert result['recipients'] == recipients
        assert result['subject'] == 'Daily Sprint Briefing - Day 1'

    def test_send_slack_notification(self):
        """Test Slack notification sending."""
        briefing_summary = {'day_number': 1, 'completion_rate': 0.8, 'status': 'on_track'}
        result = self.briefing_generator.send_slack_notification(briefing_summary, webhook_url='https://hooks.slack.com/test')
        assert result['status'] == 'success'
        assert result['webhook_url'] == 'https://hooks.slack.com/test'

class TestBriefingGeneratorIntegration:
    """Test integration scenarios for briefing generation."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.briefing_generator = BriefingGenerator()

    def teardown_method(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('builtins.open', create=True)
    def test_complete_briefing_workflow(self, mock_open):
        """Test complete briefing generation workflow."""
        # Override the mock objects to return specific data
        original_calculator = self.briefing_generator.metrics_calculator
        custom_calculator = Mock()
        custom_calculator.calculate_completion_metrics.return_value = {
            'total_tasks': 25, 'completed_tasks': 20, 'completion_rate': 0.8, 
            'agent_performance': {
                'backend_engineer': {'completed': 8, 'total': 10}, 
                'frontend_engineer': {'completed': 7, 'total': 8}, 
                'qa_engineer': {'completed': 5, 'total': 7}
            }
        }
        self.briefing_generator.metrics_calculator = custom_calculator
        
        original_monitor = self.briefing_generator.execution_monitor
        custom_monitor = Mock()
        custom_monitor.get_system_status.return_value = {
            'status': 'healthy', 'uptime': '72 hours', 
            'resource_usage': {'memory': '55%', 'cpu': '40%', 'disk': '25%'}
        }
        self.briefing_generator.execution_monitor = custom_monitor
        
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = self.briefing_generator.generate_daily_briefing(day_number=3, output_dir=str(self.temp_dir), include_email=False, include_slack=False)
        assert result['status'] == 'success'
        assert result['day_number'] == 3
        assert 'briefing_file' in result
        assert 'metrics_summary' in result
        assert 'system_status' in result
        mock_open.assert_called()
        mock_file.write.assert_called()
        custom_calculator.calculate_completion_metrics.assert_called()
        custom_monitor.get_system_status.assert_called()
        
        # Restore original objects
        self.briefing_generator.metrics_calculator = original_calculator
        self.briefing_generator.execution_monitor = original_monitor
if __name__ == '__main__':
    pytest.main([__file__])