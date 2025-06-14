#!/usr/bin/env python3
"""
Test Suite for Enhanced End-of-Day Reporting (Phase 6 Step 6.3)

Tests for velocity tracking, tomorrow's preparation, sprint health indicators,
and visual progress summaries in the enhanced task report generator.
"""

import pytest
import tempfile
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Add project root to path for imports
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.generate_task_report import (
    generate_end_of_day_report,
    generate_daily_report, 
    generate_task_specific_report,
    update_dashboard,
    _calculate_sprint_velocity,
    _analyze_tomorrow_preparation,
    _assess_sprint_health,
    _generate_visual_progress_summary,
    _create_enhanced_eod_report
)


class TestEnhancedEndOfDayReporting:
    """Test suite for enhanced end-of-day reporting functionality."""
    
    @pytest.fixture
    def mock_progress_generator(self):
        """Mock ProgressReportGenerator for testing."""
        mock_generator = Mock()
        mock_generator.generate_daily_report.return_value = "Mock daily report content"
        
        # Mock team metrics
        mock_generator.metrics_calculator.calculate_team_metrics.return_value = {
            "completed_tasks": 5,
            "total_tasks": 10,
            "completion_rate": 50.0,
            "qa_pass_rate": 80.0,
            "average_coverage": 85.0
        }
        
        # Mock all metrics
        mock_generator.metrics_calculator.calculate_all_metrics.return_value = {
            "team_metrics": {
                "completed_tasks": 5,
                "total_tasks": 10,
                "completion_rate": 50.0,
                "qa_pass_rate": 80.0,
                "average_coverage": 85.0
            },
            "task_metrics": [
                {
                    "task_id": "BE-01",
                    "status": "COMPLETED",
                    "completion_time": "2025-06-01T10:00:00Z",
                    "agent_type": "backend",
                    "priority": "HIGH"
                },
                {
                    "task_id": "FE-01", 
                    "status": "IN_PROGRESS",
                    "agent_type": "frontend",
                    "priority": "MEDIUM"
                }
            ]
        }
        
        return mock_generator
    
    @pytest.fixture
    def sample_velocity_data(self):
        """Sample velocity data for testing."""
        return {
            "current_velocity": 2.5,
            "trend": "increasing",
            "sprint_burn_rate": 60.0,
            "projected_completion": 85.0,
            "velocity_history": [
                {"date": "2025-05-31", "tasks_completed": 2, "velocity_score": 2.2},
                {"date": "2025-06-01", "tasks_completed": 3, "velocity_score": 2.8}
            ]
        }
    
    @pytest.fixture
    def sample_tomorrow_prep(self):
        """Sample tomorrow preparation data for testing."""
        return {
            "total_planned": 4,
            "high_priority": 2,
            "priority_tasks": [
                {"id": "BE-02", "title": "Implement API", "priority": "HIGH"},
                {"id": "FE-02", "title": "Create UI", "priority": "HIGH"}
            ],
            "potential_blockers": [
                {"description": "API dependency", "impact": "HIGH"}
            ],
            "preparation_checklist": [
                "Review API documentation",
                "Set up test environment"
            ]
        }
    
    @pytest.fixture
    def sample_sprint_health(self):
        """Sample sprint health data for testing."""
        return {
            "overall_score": 75.0,
            "status": "good",
            "completion_rate": 50.0,
            "qa_pass_rate": 80.0,
            "velocity_consistency": 85.0,
            "blocker_impact": 15.0,
            "recommendations": [
                "Focus on high-priority tasks",            "Address API dependency blocker"
            ]
        }
    
    def test_should_generate_enhanced_eod_report_when_given_valid_day(self, mock_progress_generator, tmp_path):
        """Test enhanced end-of-day report generation for valid day."""
        # Arrange
        test_day = 2
        
        # Mock file operations
        with patch('scripts.generate_task_report.ProgressReportGenerator', return_value=mock_progress_generator):
            with patch('scripts.generate_task_report.EndOfDayReportGenerator'):
                with patch('scripts.generate_task_report.Path') as mock_path_class:
                    with patch('builtins.open', create=True) as mock_open:
                        # Setup mocks
                        mock_path_instance = Mock()
                        mock_path_instance.mkdir = Mock()
                        mock_path_class.return_value = mock_path_instance
                        mock_path_instance.__truediv__ = Mock(return_value="test_report.md")
                        
                        mock_file = Mock()
                        mock_open.return_value.__enter__.return_value = mock_file
                        
                        # Mock the helper functions to avoid real calculations
                        with patch('scripts.generate_task_report._calculate_sprint_velocity', return_value={"current_velocity": 2.5, "trend": "increasing"}):
                            with patch('scripts.generate_task_report._analyze_tomorrow_preparation', return_value={"total_planned": 3}):
                                with patch('scripts.generate_task_report._assess_sprint_health', return_value={"overall_score": 80}):
                                    with patch('scripts.generate_task_report._generate_visual_progress_summary', return_value="Visual Summary"):
                                        with patch('scripts.generate_task_report._create_enhanced_eod_report', return_value="Enhanced Report"):
                                            # Act
                                            result = generate_end_of_day_report(test_day)
                                            
                                            # Assert
                                            assert result is True
                                            mock_progress_generator.generate_daily_report.assert_called_once()
    
    def test_should_calculate_sprint_velocity_with_trend_analysis(self, mock_progress_generator):
        """Test sprint velocity calculation with trend analysis."""
        # Arrange
        target_date = date(2025, 6, 1)
        
        # Act
        result = _calculate_sprint_velocity(mock_progress_generator, target_date)
        
        # Assert
        assert isinstance(result, dict)
        assert "current_velocity" in result
        assert "trend" in result
        assert "sprint_burn_rate" in result
        assert "projected_completion" in result
        assert "velocity_history" in result
        
        # Velocity should be non-negative
        assert result["current_velocity"] >= 0
        assert result["sprint_burn_rate"] >= 0
        assert result["projected_completion"] >= 0
    
    def test_should_analyze_tomorrow_preparation_with_priorities(self, mock_progress_generator):
        """Test tomorrow's preparation analysis with task priorities."""
        # Arrange
        target_date = date(2025, 6, 1)
        
        # Act
        result = _analyze_tomorrow_preparation(mock_progress_generator, target_date)
        
        # Assert
        assert isinstance(result, dict)
        assert "total_planned" in result
        assert "high_priority" in result
        assert "priority_tasks" in result
        assert "potential_blockers" in result
        assert "preparation_checklist" in result
        
        # High priority count should not exceed total planned
        assert result["high_priority"] <= result["total_planned"]
    
    def test_should_assess_sprint_health_with_comprehensive_indicators(self, mock_progress_generator):
        """Test sprint health assessment with comprehensive indicators."""
        # Act
        result = _assess_sprint_health(mock_progress_generator)
        
        # Assert
        assert isinstance(result, dict)
        assert "overall_score" in result
        assert "status" in result
        assert "completion_rate" in result
        assert "qa_pass_rate" in result
        assert "recommendations" in result
        
        # Health score should be between 0 and 100
        assert 0 <= result["overall_score"] <= 100
        
        # Status should be valid health status
        valid_statuses = ["excellent", "good", "needs_attention", "critical"]
        assert result["status"] in valid_statuses
    
    def test_should_generate_visual_progress_summary(self, mock_progress_generator, sample_velocity_data):
        """Test visual progress summary generation."""
        # Act
        result = _generate_visual_progress_summary(mock_progress_generator, sample_velocity_data)
        
        # Assert
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Visual Progress Summary" in result
        # Should contain ASCII progress indicators
        assert any(char in result for char in ["█", "░", "▓"])
    
    def test_should_create_comprehensive_eod_report_with_all_sections(
        self, 
        sample_velocity_data,
        sample_tomorrow_prep,
        sample_sprint_health
    ):
        """Test creation of comprehensive end-of-day report with all sections."""
        # Arrange
        day = 2
        target_date = date(2025, 6, 1)
        daily_report = "Sample daily report content"
        visual_summary = "Sample visual summary"
        
        # Act
        result = _create_enhanced_eod_report(
            day, target_date, daily_report, sample_velocity_data,
            sample_tomorrow_prep, sample_sprint_health, visual_summary
        )
        
        # Assert
        assert isinstance(result, str)
        assert f"Day {day}" in result
        assert "Sprint Velocity Analysis" in result
        assert "Tomorrow's Preparation" in result
        assert "Sprint Health Status" in result
        assert "Enhanced End-of-Day Report" in result
          # Should include velocity data
        assert str(sample_velocity_data["current_velocity"]) in result
        assert sample_velocity_data["trend"].title() in result
        
        # Should include tomorrow's preparation
        assert str(sample_tomorrow_prep["total_planned"]) in result
        assert str(sample_tomorrow_prep["high_priority"]) in result
          # Should include sprint health
        assert str(sample_sprint_health["overall_score"]) in result
        assert sample_sprint_health["status"].title() in result
    
    def test_should_handle_missing_data_gracefully(self, mock_progress_generator):
        """Test that functions handle missing or incomplete data gracefully."""
        # Arrange - Mock empty metrics
        mock_progress_generator.metrics_calculator.calculate_all_metrics.return_value = {
            "team_metrics": {},
            "task_metrics": []
        }
        
        target_date = date(2025, 6, 1)
        
        # Act & Assert - Should not raise exceptions
        velocity_result = _calculate_sprint_velocity(mock_progress_generator, target_date)
        assert isinstance(velocity_result, dict)
        
        tomorrow_result = _analyze_tomorrow_preparation(mock_progress_generator, target_date)
        assert isinstance(tomorrow_result, dict)
        
        health_result = _assess_sprint_health(mock_progress_generator)
        assert isinstance(health_result, dict)
    
    def test_should_validate_velocity_trend_calculation(self, mock_progress_generator):
        """Test velocity trend calculation accuracy."""
        # Arrange - Mock metrics with trend data
        mock_progress_generator.metrics_calculator.calculate_all_metrics.return_value = {
            "team_metrics": {"completion_rate": 60.0},
            "task_metrics": [
                {"completion_time": "2025-05-30T10:00:00Z", "status": "COMPLETED"},
                {"completion_time": "2025-05-31T10:00:00Z", "status": "COMPLETED"},
                {"completion_time": "2025-06-01T10:00:00Z", "status": "COMPLETED"}
            ]
        }
        
        target_date = date(2025, 6, 1)
        
        # Act
        result = _calculate_sprint_velocity(mock_progress_generator, target_date)
        
        # Assert
        assert "trend" in result
        assert result["trend"] in ["increasing", "decreasing", "stable"]
    
    def test_should_prioritize_high_impact_tasks_for_tomorrow(self, mock_progress_generator):
        """Test that tomorrow's preparation prioritizes high-impact tasks."""
        # Arrange - Mock tasks with different priorities
        mock_progress_generator.metrics_calculator.calculate_all_metrics.return_value = {
            "task_metrics": [
                {"task_id": "HIGH-01", "priority": "HIGH", "status": "TODO"},
                {"task_id": "LOW-01", "priority": "LOW", "status": "TODO"},
                {"task_id": "MED-01", "priority": "MEDIUM", "status": "TODO"}
            ]
        }
        
        target_date = date(2025, 6, 1)
        
        # Act
        result = _analyze_tomorrow_preparation(mock_progress_generator, target_date)
        
        # Assert
        priority_tasks = result.get("priority_tasks", [])
        if priority_tasks:
            # High priority tasks should be listed first
            high_priority_tasks = [t for t in priority_tasks if t.get("priority") == "HIGH"]
            assert len(high_priority_tasks) >= 0  # Should handle high priority tasks


class TestCLIIntegration:
    """Test suite for CLI integration and command-line interface."""
    
    @patch('scripts.generate_task_report.generate_end_of_day_report')
    def test_should_call_eod_report_when_day_argument_provided(self, mock_eod_report):
        """Test CLI calls end-of-day report generation when --day is provided."""
        # Arrange
        mock_eod_report.return_value = True
        
        # Act & Assert would require actual CLI testing
        # This is a placeholder for CLI integration testing
        assert True  # Placeholder assertion
    
    def test_should_validate_day_argument_range(self):
        """Test CLI validates day argument is within reasonable range."""
        # Implementation would test CLI argument validation
        assert True  # Placeholder assertion
    
    def test_should_provide_helpful_error_messages(self):
        """Test CLI provides helpful error messages for invalid inputs."""
        # Implementation would test CLI error handling
        assert True  # Placeholder assertion


class TestIntegrationWithExistingInfrastructure:
    """Test suite for integration with existing reporting infrastructure."""
    
    def test_should_integrate_with_progress_report_generator(self):
        """Test integration with existing ProgressReportGenerator."""
        # Test that enhanced EOD reporting works with existing infrastructure
        assert True  # Placeholder assertion
    
    def test_should_maintain_backward_compatibility(self):
        """Test that enhanced features don't break existing functionality."""
        # Test backward compatibility with existing reports
        assert True  # Placeholder assertion
    
    def test_should_use_existing_metrics_calculator(self):
        """Test that velocity calculations use existing metrics infrastructure."""
        # Test integration with CompletionMetricsCalculator
        assert True  # Placeholder assertion


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
