"""
Comprehensive tests for DailyCycleOrchestrator configuration loading.

Tests configuration loading, validation, and orchestrator initialization.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.core.workflows.daily_cycle import DailyCycleOrchestrator


class TestDailyCycleOrchestratorConfig:
    """Test the DailyCycleOrchestrator configuration system."""

    def test_default_initialization(self):
        """Test orchestrator initialization with default config."""
        with patch.object(DailyCycleOrchestrator, "_load_config") as mock_load:
            mock_load.return_value = {"test": "config"}
            orchestrator = DailyCycleOrchestrator()
            
            assert orchestrator.config_path == "config/daily_cycle.json"
            assert orchestrator.config == {"test": "config"}
            mock_load.assert_called_once()

    def test_custom_config_path_initialization(self):
        """Test orchestrator initialization with custom config path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump({"custom": "config"}, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            with patch.object(DailyCycleOrchestrator, "_load_config") as mock_load:
                mock_load.return_value = {"custom": "config"}
                orchestrator = DailyCycleOrchestrator(config_path=tmp_path)
                
                assert orchestrator.config_path == tmp_path
                mock_load.assert_called_once()
        finally:
            os.unlink(tmp_path)

    def test_invalid_config_path_validation(self):
        """Test validation error handling for invalid config path."""
        with pytest.raises(ValueError, match="Invalid config path"):
            DailyCycleOrchestrator(config_path="/nonexistent/path/config.json")

    def test_get_default_config(self):
        """Test default configuration structure."""
        orchestrator = DailyCycleOrchestrator.__new__(DailyCycleOrchestrator)
        default_config = orchestrator._get_default_config()
        
        # Check main config sections exist
        expected_sections = ["paths", "automation", "email", "dashboard", "logging"]
        for section in expected_sections:
            assert section in default_config
        
        # Check specific default values
        assert default_config["automation"]["enabled"] is True
        assert default_config["automation"]["morning_briefing_time"] == "09:00"
        assert default_config["automation"]["eod_report_time"] == "17:00"
        assert default_config["email"]["enabled"] is False
        assert default_config["dashboard"]["api_port"] == 5000
        assert default_config["logging"]["level"] == "INFO"

    def test_load_config_with_existing_file(self):
        """Test loading configuration from existing file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            test_config = {
                "automation": {"enabled": False, "morning_briefing_time": "08:00"},
                "email": {"enabled": True, "smtp_port": 465},
                "custom_section": {"test_value": "test"}
            }
            json.dump(test_config, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            orchestrator = DailyCycleOrchestrator.__new__(DailyCycleOrchestrator)
            orchestrator.config_path = tmp_path
            config = orchestrator._load_config()
            
            # Check that custom values override defaults
            assert config["automation"]["enabled"] is False
            assert config["automation"]["morning_briefing_time"] == "08:00"
            assert config["email"]["enabled"] is True
            assert config["email"]["smtp_port"] == 465
            assert config["custom_section"]["test_value"] == "test"
            
            # Check that defaults are preserved for unspecified values
            assert config["automation"]["eod_report_time"] == "17:00"  # default preserved
            assert config["dashboard"]["api_port"] == 5000  # default preserved
        finally:
            os.unlink(tmp_path)

    def test_load_config_with_nonexistent_file(self):
        """Test loading configuration when file doesn't exist."""
        orchestrator = DailyCycleOrchestrator.__new__(DailyCycleOrchestrator)
        orchestrator.config_path = "/nonexistent/config.json"
        config = orchestrator._load_config()
        
        # Should return default config
        default_config = orchestrator._get_default_config()
        assert config == default_config

    def test_load_config_with_invalid_json(self):
        """Test loading configuration with malformed JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_file.write('{"invalid": json content}')  # Invalid JSON
            tmp_path = tmp_file.name
        
        try:
            orchestrator = DailyCycleOrchestrator.__new__(DailyCycleOrchestrator)
            orchestrator.config_path = tmp_path
            
            with patch('builtins.print') as mock_print:
                config = orchestrator._load_config()
                
                # Should return default config and print error
                default_config = orchestrator._get_default_config()
                assert config == default_config
                mock_print.assert_called_once()
                assert "Error loading config" in str(mock_print.call_args)
        finally:
            os.unlink(tmp_path)

    def test_config_merging_behavior(self):
        """Test how loaded config merges with defaults."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            # Only specify some values, leaving others to use defaults
            partial_config = {
                "automation": {
                    "enabled": False,
                    "morning_briefing_time": "07:00"
                    # eod_report_time not specified - should use default
                },
                "email": {
                    "enabled": True
                    # other email settings not specified - should use defaults
                }
                # dashboard and logging sections not specified - should use defaults
            }
            json.dump(partial_config, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            orchestrator = DailyCycleOrchestrator.__new__(DailyCycleOrchestrator)
            orchestrator.config_path = tmp_path
            config = orchestrator._load_config()
            
            # Check that specified values are used
            assert config["automation"]["enabled"] is False
            assert config["automation"]["morning_briefing_time"] == "07:00"
            assert config["email"]["enabled"] is True
            
            # Check that unspecified values use defaults
            assert config["automation"]["eod_report_time"] == "17:00"
            assert config["email"]["smtp_server"] == "localhost"
            assert config["email"]["smtp_port"] == 587
            assert config["dashboard"]["api_port"] == 5000
            assert config["logging"]["level"] == "INFO"
        finally:
            os.unlink(tmp_path)

    def test_logging_initialization_flag(self):
        """Test logging initialization tracking."""
        with patch.object(DailyCycleOrchestrator, "_load_config") as mock_load:
            mock_load.return_value = {"test": "config"}
            orchestrator = DailyCycleOrchestrator()
            
            assert orchestrator._logging_initialized is False
            assert orchestrator._logger is None

    def test_lazy_loaded_properties_initialization(self):
        """Test that lazy-loaded properties are initialized as None."""
        with patch.object(DailyCycleOrchestrator, "_load_config") as mock_load:
            mock_load.return_value = {"test": "config"}
            orchestrator = DailyCycleOrchestrator()
            
            assert orchestrator._metrics_calculator is None
            assert orchestrator._execution_monitor is None
            assert orchestrator._briefing_generator is None
            assert orchestrator._eod_report_generator is None
            assert orchestrator._email_integration is None

    @patch('src.core.workflows.daily_cycle.CompletionMetricsCalculator')
    def test_metrics_calculator_lazy_loading(self, mock_metrics_class):
        """Test lazy loading of metrics calculator."""
        mock_instance = Mock()
        mock_metrics_class.return_value = mock_instance
        
        with patch.object(DailyCycleOrchestrator, "_load_config") as mock_load:
            mock_load.return_value = {"test": "config"}
            orchestrator = DailyCycleOrchestrator()
            
            # First access should create instance
            result1 = orchestrator.metrics_calculator
            assert result1 == mock_instance
            mock_metrics_class.assert_called_once()
            
            # Second access should return same instance
            result2 = orchestrator.metrics_calculator
            assert result2 == mock_instance
            # Should not create another instance
            assert mock_metrics_class.call_count == 1

    @patch('src.core.workflows.daily_cycle.ExecutionMonitor')
    def test_execution_monitor_lazy_loading(self, mock_monitor_class):
        """Test lazy loading of execution monitor."""
        mock_instance = Mock()
        mock_monitor_class.return_value = mock_instance
        
        with patch.object(DailyCycleOrchestrator, "_load_config") as mock_load:
            mock_load.return_value = {"test": "config"}
            orchestrator = DailyCycleOrchestrator()
            
            result1 = orchestrator.execution_monitor
            assert result1 == mock_instance
            mock_monitor_class.assert_called_once()
            
            result2 = orchestrator.execution_monitor
            assert result2 == mock_instance
            assert mock_monitor_class.call_count == 1

    @patch('src.core.workflows.daily_cycle.BriefingGenerator')
    def test_briefing_generator_lazy_loading(self, mock_generator_class):
        """Test lazy loading of briefing generator."""
        mock_instance = Mock()
        mock_generator_class.return_value = mock_instance
        
        with patch.object(DailyCycleOrchestrator, "_load_config") as mock_load:
            mock_load.return_value = {"test": "config"}
            orchestrator = DailyCycleOrchestrator()
            
            result1 = orchestrator.briefing_generator
            assert result1 == mock_instance
            mock_generator_class.assert_called_once()
            
            result2 = orchestrator.briefing_generator
            assert result2 == mock_instance
            assert mock_generator_class.call_count == 1

    @patch('src.core.workflows.daily_cycle.EndOfDayReportGenerator')
    def test_eod_report_generator_lazy_loading(self, mock_eod_class):
        """Test lazy loading of end-of-day report generator."""
        mock_instance = Mock()
        mock_eod_class.return_value = mock_instance
        
        with patch.object(DailyCycleOrchestrator, "_load_config") as mock_load:
            mock_load.return_value = {"test": "config"}
            orchestrator = DailyCycleOrchestrator()
            
            result1 = orchestrator.eod_report_generator
            assert result1 == mock_instance
            mock_eod_class.assert_called_once()
            
            result2 = orchestrator.eod_report_generator
            assert result2 == mock_instance
            assert mock_eod_class.call_count == 1

    @patch('src.core.workflows.daily_cycle.EmailIntegration')
    def test_email_integration_lazy_loading(self, mock_email_class):
        """Test lazy loading of email integration."""
        mock_instance = Mock()
        mock_email_class.return_value = mock_instance
        
        with patch.object(DailyCycleOrchestrator, "_load_config") as mock_load:
            mock_load.return_value = {"test": "config"}
            orchestrator = DailyCycleOrchestrator()
            
            result1 = orchestrator.email_integration
            assert result1 == mock_instance
            mock_email_class.assert_called_once_with("config/daily_cycle.json")
            
            result2 = orchestrator.email_integration
            assert result2 == mock_instance
            assert mock_email_class.call_count == 1

    def test_config_sections_structure(self):
        """Test that default config has expected structure and types."""
        orchestrator = DailyCycleOrchestrator.__new__(DailyCycleOrchestrator)
        config = orchestrator._get_default_config()
        
        # Test paths section
        assert isinstance(config["paths"], dict)
        required_paths = ["logs_dir", "briefings_dir", "reports_dir", "templates_dir"]
        for path_key in required_paths:
            assert path_key in config["paths"]
            assert isinstance(config["paths"][path_key], str)
        
        # Test automation section
        assert isinstance(config["automation"], dict)
        assert isinstance(config["automation"]["enabled"], bool)
        assert isinstance(config["automation"]["morning_briefing_time"], str)
        assert isinstance(config["automation"]["eod_report_time"], str)
        assert isinstance(config["automation"]["check_interval"], int)
        assert isinstance(config["automation"]["max_retries"], int)
        assert isinstance(config["automation"]["auto_dashboard_update"], bool)
        
        # Test email section
        assert isinstance(config["email"], dict)
        assert isinstance(config["email"]["enabled"], bool)
        assert isinstance(config["email"]["smtp_port"], int)
        assert isinstance(config["email"]["use_tls"], bool)
        assert isinstance(config["email"]["recipients"], dict)
        
        # Test dashboard section
        assert isinstance(config["dashboard"], dict)
        assert isinstance(config["dashboard"]["api_port"], int)
        assert isinstance(config["dashboard"]["refresh_interval"], int)
        
        # Test logging section
        assert isinstance(config["logging"], dict)
        assert isinstance(config["logging"]["level"], str)
        assert isinstance(config["logging"]["format"], str)
        assert isinstance(config["logging"]["file_rotation"], bool)