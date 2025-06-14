"""
Comprehensive Tests for Briefing Generator

Extended test suite for the briefing generation system
to validate daily briefing creation, metrics integration, and report formatting.
"""

import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import yaml

from src.core.workflows.generate_briefing import BriefingGenerator


class TestBriefingGenerator:
    """Test BriefingGenerator class comprehensively."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.briefing_generator = BriefingGenerator()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_briefing_generator_initialization(self):
        """Test briefing generator initialization."""
        generator = BriefingGenerator()
        
        assert hasattr(generator, 'logger')
        assert hasattr(generator, 'generate_daily_briefing')
    
    @patch('orchestration.generate_briefing.CompletionMetricsCalculator')
    @patch('orchestration.generate_briefing.ExecutionMonitor')
    def test_generate_daily_briefing_basic(self, mock_monitor, mock_metrics):
        """Test basic daily briefing generation."""
        # Setup mocks
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_completion_metrics.return_value = {
            'total_tasks': 10,
            'completed_tasks': 7,
            'completion_rate': 0.7,
            'in_progress_tasks': 2,
            'pending_tasks': 1
        }
        mock_metrics.return_value = mock_metrics_instance
        
        mock_monitor_instance = Mock()
        mock_monitor_instance.get_system_status.return_value = {
            'status': 'healthy',
            'uptime': '24 hours',
            'active_agents': 5,
            'last_update': datetime.now().isoformat()
        }
        mock_monitor.return_value = mock_monitor_instance
        
        # Test briefing generation
        result = self.briefing_generator.generate_daily_briefing(day_number=1)
        
        assert result['status'] == 'success'
        assert 'briefing_file' in result
        assert result['day_number'] == 1
        mock_metrics_instance.calculate_completion_metrics.assert_called_once()
        mock_monitor_instance.get_system_status.assert_called_once()
    
    @patch('orchestration.generate_briefing.CompletionMetricsCalculator')
    @patch('orchestration.generate_briefing.ExecutionMonitor')
    def test_generate_daily_briefing_with_custom_date(self, mock_monitor, mock_metrics):
        """Test daily briefing generation with custom date."""
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_completion_metrics.return_value = {
            'total_tasks': 15,
            'completed_tasks': 12,
            'completion_rate': 0.8
        }
        mock_metrics.return_value = mock_metrics_instance
        
        mock_monitor_instance = Mock()
        mock_monitor_instance.get_system_status.return_value = {'status': 'healthy'}
        mock_monitor.return_value = mock_monitor_instance
        
        custom_date = datetime(2024, 6, 15)
        result = self.briefing_generator.generate_daily_briefing(
            day_number=5,
            target_date=custom_date
        )
        
        assert result['status'] == 'success'
        assert result['target_date'] == custom_date.isoformat()
    
    @patch('orchestration.generate_briefing.CompletionMetricsCalculator')
    @patch('orchestration.generate_briefing.ExecutionMonitor')
    def test_generate_briefing_content_structure(self, mock_monitor, mock_metrics):
        """Test briefing content structure and formatting."""
        # Setup comprehensive mock data
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_completion_metrics.return_value = {
            'total_tasks': 25,
            'completed_tasks': 20,
            'completion_rate': 0.8,
            'in_progress_tasks': 3,
            'pending_tasks': 2,
            'failed_tasks': 0,
            'agent_completion_rates': {
                'backend_engineer': 0.85,
                'frontend_engineer': 0.75,
                'qa_engineer': 0.9
            },
            'task_categories': {
                'backend': 10,
                'frontend': 8,
                'qa': 7
            }
        }
        mock_metrics.return_value = mock_metrics_instance
        
        mock_monitor_instance = Mock()
        mock_monitor_instance.get_system_status.return_value = {
            'status': 'healthy',
            'uptime': '48 hours',
            'active_agents': 6,
            'memory_usage': '65%',
            'cpu_usage': '45%',
            'disk_usage': '30%'
        }
        mock_monitor.return_value = mock_monitor_instance
        
        result = self.briefing_generator.generate_daily_briefing(day_number=2)
        
        assert result['status'] == 'success'
        assert 'briefing_content' in result
        assert 'metrics_summary' in result
        assert 'system_status' in result
        
        # Verify metrics are included
        assert result['metrics_summary']['total_tasks'] == 25
        assert result['metrics_summary']['completion_rate'] == 0.8
        
        # Verify system status is included
        assert result['system_status']['status'] == 'healthy'
        assert result['system_status']['active_agents'] == 6
    
    @patch('orchestration.generate_briefing.CompletionMetricsCalculator')
    @patch('orchestration.generate_briefing.ExecutionMonitor')
    @patch('builtins.open', create=True)
    def test_generate_briefing_file_output(self, mock_open, mock_monitor, mock_metrics):
        """Test briefing file generation and output."""
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_completion_metrics.return_value = {
            'total_tasks': 5,
            'completed_tasks': 4,
            'completion_rate': 0.8
        }
        mock_metrics.return_value = mock_metrics_instance
        
        mock_monitor_instance = Mock()
        mock_monitor_instance.get_system_status.return_value = {'status': 'healthy'}
        mock_monitor.return_value = mock_monitor_instance
        
        # Mock file writing
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = self.briefing_generator.generate_daily_briefing(
            day_number=1,
            output_dir=str(self.temp_dir)
        )
        
        assert result['status'] == 'success'
        assert 'briefing_file' in result
        mock_open.assert_called()
        mock_file.write.assert_called()
    
    @patch('orchestration.generate_briefing.CompletionMetricsCalculator')
    @patch('orchestration.generate_briefing.ExecutionMonitor')
    def test_generate_briefing_error_handling(self, mock_monitor, mock_metrics):
        """Test error handling in briefing generation."""
        # Setup mock to raise exception
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_completion_metrics.side_effect = Exception("Metrics calculation failed")
        mock_metrics.return_value = mock_metrics_instance
        
        mock_monitor_instance = Mock()
        mock_monitor_instance.get_system_status.return_value = {'status': 'healthy'}
        mock_monitor.return_value = mock_monitor_instance
        
        result = self.briefing_generator.generate_daily_briefing(day_number=1)
        
        assert result['status'] == 'error'
        assert 'error' in result
        assert 'Metrics calculation failed' in result['error']
    
    @patch('orchestration.generate_briefing.CompletionMetricsCalculator')
    @patch('orchestration.generate_briefing.ExecutionMonitor')
    def test_generate_briefing_with_recommendations(self, mock_monitor, mock_metrics):
        """Test briefing generation with performance recommendations."""
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_completion_metrics.return_value = {
            'total_tasks': 20,
            'completed_tasks': 10,
            'completion_rate': 0.5,  # Low completion rate
            'bottlenecks': ['qa_validation', 'dependency_resolution'],
            'recommendations': [
                'Increase QA resources',
                'Review dependency management'
            ]
        }
        mock_metrics.return_value = mock_metrics_instance
        
        mock_monitor_instance = Mock()
        mock_monitor_instance.get_system_status.return_value = {
            'status': 'degraded',
            'warnings': ['High memory usage', 'Slow response times']
        }
        mock_monitor.return_value = mock_monitor_instance
        
        result = self.briefing_generator.generate_daily_briefing(day_number=3)
        
        assert result['status'] == 'success'
        assert 'recommendations' in result
        assert len(result['recommendations']) >= 2
        assert 'warnings' in result
    
    @patch('orchestration.generate_briefing.CompletionMetricsCalculator')
    @patch('orchestration.generate_briefing.ExecutionMonitor')
    def test_generate_weekly_summary(self, mock_monitor, mock_metrics):
        """Test weekly summary generation."""
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_weekly_metrics.return_value = {
            'week_number': 1,
            'total_tasks_week': 50,
            'completed_tasks_week': 42,
            'weekly_completion_rate': 0.84,
            'daily_breakdown': {
                'day_1': {'completed': 8, 'total': 10},
                'day_2': {'completed': 9, 'total': 10},
                'day_3': {'completed': 7, 'total': 10},
                'day_4': {'completed': 8, 'total': 10},
                'day_5': {'completed': 10, 'total': 10}
            }
        }
        mock_metrics.return_value = mock_metrics_instance
        
        mock_monitor_instance = Mock()
        mock_monitor_instance.get_weekly_status.return_value = {
            'average_uptime': '99.2%',
            'peak_resource_usage': {'memory': '78%', 'cpu': '65%'}
        }
        mock_monitor.return_value = mock_monitor_instance
        
        result = self.briefing_generator.generate_weekly_summary(week_number=1)
        
        assert result['status'] == 'success'
        assert result['week_number'] == 1
        assert result['weekly_completion_rate'] == 0.84
        assert 'daily_breakdown' in result
    
    @patch('orchestration.generate_briefing.yaml')
    @patch('orchestration.generate_briefing.Path')
    def test_load_briefing_template(self, mock_path, mock_yaml):
        """Test loading briefing template."""
        mock_template = {
            'title': 'Daily Sprint Briefing - Day {day_number}',
            'sections': [
                'summary',
                'metrics',
                'system_status',
                'recommendations'
            ],
            'format': 'markdown'
        }
        
        mock_yaml.safe_load.return_value = mock_template
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        template = self.briefing_generator.load_briefing_template('custom_template.yaml')
        
        assert template['title'].format(day_number=1) == 'Daily Sprint Briefing - Day 1'
        assert 'sections' in template
        assert template['format'] == 'markdown'
    
    @patch('orchestration.generate_briefing.Path')
    def test_load_briefing_template_not_found(self, mock_path):
        """Test loading non-existent briefing template."""
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        template = self.briefing_generator.load_briefing_template('nonexistent.yaml')
        
        # Should return default template
        assert template is not None
        assert 'title' in template
        assert 'sections' in template
    
    def test_format_briefing_markdown(self):
        """Test markdown formatting of briefing content."""
        briefing_data = {
            'day_number': 1,
            'date': datetime.now().isoformat(),
            'metrics_summary': {
                'total_tasks': 10,
                'completed_tasks': 8,
                'completion_rate': 0.8
            },
            'system_status': {
                'status': 'healthy',
                'uptime': '24 hours'
            },
            'recommendations': [
                'Continue current pace',
                'Review remaining tasks'
            ]
        }
        
        markdown_content = self.briefing_generator.format_briefing_markdown(briefing_data)
        
        assert '# Daily Sprint Briefing' in markdown_content
        assert 'Day 1' in markdown_content
        assert '80.0%' in markdown_content  # Completion rate
        assert 'healthy' in markdown_content
        assert 'Continue current pace' in markdown_content
    
    def test_format_briefing_json(self):
        """Test JSON formatting of briefing content."""
        briefing_data = {
            'day_number': 2,
            'metrics': {'completion_rate': 0.75},
            'status': 'active'
        }
        
        json_content = self.briefing_generator.format_briefing_json(briefing_data)
        
        # Should be valid JSON
        parsed_json = json.loads(json_content)
        assert parsed_json['day_number'] == 2
        assert parsed_json['metrics']['completion_rate'] == 0.75
        assert parsed_json['status'] == 'active'
    
    def test_calculate_trend_analysis(self):
        """Test trend analysis calculation."""
        historical_data = [
            {'day': 1, 'completion_rate': 0.7},
            {'day': 2, 'completion_rate': 0.75},
            {'day': 3, 'completion_rate': 0.8},
            {'day': 4, 'completion_rate': 0.85}
        ]
        
        trend_analysis = self.briefing_generator.calculate_trend_analysis(historical_data)
        
        assert trend_analysis['trend'] == 'improving'
        assert trend_analysis['average_rate'] == 0.775
        assert trend_analysis['rate_change'] > 0
    
    def test_calculate_trend_analysis_declining(self):
        """Test trend analysis for declining performance."""
        historical_data = [
            {'day': 1, 'completion_rate': 0.9},
            {'day': 2, 'completion_rate': 0.8},
            {'day': 3, 'completion_rate': 0.7},
            {'day': 4, 'completion_rate': 0.6}
        ]
        
        trend_analysis = self.briefing_generator.calculate_trend_analysis(historical_data)
        
        assert trend_analysis['trend'] == 'declining'
        assert trend_analysis['rate_change'] < 0
    
    @patch('orchestration.generate_briefing.CompletionMetricsCalculator')
    @patch('orchestration.generate_briefing.ExecutionMonitor')
    def test_generate_performance_alerts(self, mock_monitor, mock_metrics):
        """Test performance alert generation."""
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_completion_metrics.return_value = {
            'completion_rate': 0.3,  # Very low
            'failed_tasks': 5,
            'overdue_tasks': 3
        }
        mock_metrics.return_value = mock_metrics_instance
        
        alerts = self.briefing_generator.generate_performance_alerts()
        
        assert len(alerts) > 0
        alert_types = [alert['type'] for alert in alerts]
        assert 'low_completion_rate' in alert_types
        assert any('30%' in alert['message'] for alert in alerts)
    
    def test_validate_briefing_data(self):
        """Test briefing data validation."""
        valid_data = {
            'day_number': 1,
            'date': datetime.now().isoformat(),
            'metrics_summary': {
                'total_tasks': 10,
                'completed_tasks': 8
            },
            'system_status': {
                'status': 'healthy'
            }
        }
        
        is_valid = self.briefing_generator.validate_briefing_data(valid_data)
        assert is_valid is True
        
        # Test invalid data
        invalid_data = {
            'day_number': 'invalid',  # Should be int
            'metrics_summary': 'invalid'  # Should be dict
        }
        
        is_valid = self.briefing_generator.validate_briefing_data(invalid_data)
        assert is_valid is False
    
    @patch('orchestration.generate_briefing.smtplib')
    def test_send_briefing_email(self, mock_smtp):
        """Test email sending functionality."""
        mock_server = Mock()
        mock_smtp.SMTP.return_value = mock_server
        
        briefing_content = "Daily briefing content"
        recipients = ['team@example.com', 'manager@example.com']
        
        result = self.briefing_generator.send_briefing_email(
            briefing_content,
            recipients,
            subject="Daily Sprint Briefing - Day 1"
        )
        
        assert result['status'] == 'success'
        mock_server.send_message.assert_called()
        mock_server.quit.assert_called()
    
    @patch('orchestration.generate_briefing.requests')
    def test_send_slack_notification(self, mock_requests):
        """Test Slack notification sending."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        mock_requests.post.return_value = mock_response
        
        briefing_summary = {
            'day_number': 1,
            'completion_rate': 0.8,
            'status': 'on_track'
        }
        
        result = self.briefing_generator.send_slack_notification(
            briefing_summary,
            webhook_url='https://hooks.slack.com/test'
        )
        
        assert result['status'] == 'success'
        mock_requests.post.assert_called_once()


class TestBriefingGeneratorIntegration:
    """Test integration scenarios for briefing generation."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.briefing_generator = BriefingGenerator()
    
    def teardown_method(self):
        """Clean up integration test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('orchestration.generate_briefing.CompletionMetricsCalculator')
    @patch('orchestration.generate_briefing.ExecutionMonitor')
    @patch('builtins.open', create=True)
    def test_complete_briefing_workflow(self, mock_open, mock_monitor, mock_metrics):
        """Test complete briefing generation workflow."""
        # Setup comprehensive mocks
        mock_metrics_instance = Mock()
        mock_metrics_instance.calculate_completion_metrics.return_value = {
            'total_tasks': 25,
            'completed_tasks': 20,
            'completion_rate': 0.8,
            'agent_performance': {
                'backend_engineer': {'completed': 8, 'total': 10},
                'frontend_engineer': {'completed': 7, 'total': 8},
                'qa_engineer': {'completed': 5, 'total': 7}
            }
        }
        mock_metrics.return_value = mock_metrics_instance
        
        mock_monitor_instance = Mock()
        mock_monitor_instance.get_system_status.return_value = {
            'status': 'healthy',
            'uptime': '72 hours',
            'resource_usage': {
                'memory': '55%',
                'cpu': '40%',
                'disk': '25%'
            }
        }
        mock_monitor.return_value = mock_monitor_instance
        
        # Mock file operations
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Test complete workflow
        result = self.briefing_generator.generate_daily_briefing(
            day_number=3,
            output_dir=str(self.temp_dir),
            include_email=False,
            include_slack=False
        )
        
        # Verify complete workflow execution
        assert result['status'] == 'success'
        assert result['day_number'] == 3
        assert 'briefing_file' in result
        assert 'metrics_summary' in result
        assert 'system_status' in result
        
        # Verify file was written
        mock_open.assert_called()
        mock_file.write.assert_called()
        
        # Verify metrics were calculated
        mock_metrics_instance.calculate_completion_metrics.assert_called()
        mock_monitor_instance.get_system_status.assert_called()


if __name__ == '__main__':
    pytest.main([__file__])