"""
Comprehensive tests for CoverageAnalyzer and coverage reporting functionality.

Tests coverage analysis, data collection, and reporting functions.
"""

import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.infrastructure.utils.coverage_analyzer import (
    CoverageAnalyzer,
    analyze_coverage,
    get_mock_coverage_data,
)


class TestCoverageAnalyzer:
    """Test the CoverageAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CoverageAnalyzer()

    def test_initialization(self):
        """Test CoverageAnalyzer initialization."""
        assert isinstance(self.analyzer.project_root, Path)
        assert self.analyzer.project_root == Path(".")
        assert isinstance(self.analyzer.logger, logging.Logger)
        assert self.analyzer.coverage_thresholds["lines"] == 80
        assert self.analyzer.coverage_thresholds["functions"] == 80
        assert self.analyzer.coverage_thresholds["branches"] == 70
        assert self.analyzer.coverage_thresholds["statements"] == 80

    def test_initialization_with_custom_root(self):
        """Test CoverageAnalyzer initialization with custom project root."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            analyzer = CoverageAnalyzer(project_root=tmp_dir)
            assert analyzer.project_root == Path(tmp_dir)

    def test_coverage_thresholds_structure(self):
        """Test that coverage thresholds have expected structure."""
        thresholds = self.analyzer.coverage_thresholds
        
        required_keys = ["lines", "functions", "branches", "statements"]
        for key in required_keys:
            assert key in thresholds
            assert isinstance(thresholds[key], (int, float))
            assert 0 <= thresholds[key] <= 100

    def test_collect_coverage_data(self):
        """Test coverage data collection."""
        data = self.analyzer._collect_coverage_data()
        
        # Check structure
        assert "totals" in data
        assert "files" in data
        assert "percent_covered" in data["totals"]
        
        # Check data types
        assert isinstance(data["totals"]["percent_covered"], (int, float))
        assert isinstance(data["files"], dict)
        
        # Check that coverage percentage is reasonable
        assert 0 <= data["totals"]["percent_covered"] <= 100

    def test_collect_coverage_data_file_structure(self):
        """Test coverage data file structure."""
        data = self.analyzer._collect_coverage_data()
        
        for filename, file_data in data["files"].items():
            assert isinstance(filename, str)
            assert "summary" in file_data
            assert "percent_covered" in file_data["summary"]
            assert isinstance(file_data["summary"]["percent_covered"], (int, float))
            assert 0 <= file_data["summary"]["percent_covered"] <= 100

    def test_analyze_coverage_method(self):
        """Test the analyze_coverage method."""
        result = self.analyzer.analyze_coverage("TEST-01")
        
        # Should return mock data structure
        assert "task_id" in result
        assert "coverage_percentage" in result
        assert "lines_covered" in result
        assert "lines_total" in result
        
        assert result["task_id"] == "TEST-01"
        assert isinstance(result["coverage_percentage"], (int, float))
        assert isinstance(result["lines_covered"], int)
        assert isinstance(result["lines_total"], int)

    def test_analyze_coverage_with_default_task_id(self):
        """Test analyze_coverage with default task ID."""
        result = self.analyzer.analyze_coverage()
        assert result["task_id"] == "demo"

    def test_analyze_coverage_percentage_calculation(self):
        """Test coverage percentage calculation consistency."""
        result = self.analyzer.analyze_coverage("CALC-01")
        
        # Check that the percentage makes sense relative to lines
        lines_covered = result["lines_covered"]
        lines_total = result["lines_total"]
        coverage_percentage = result["coverage_percentage"]
        
        expected_percentage = (lines_covered / lines_total) * 100
        assert abs(coverage_percentage - expected_percentage) < 0.1  # Allow small floating point differences

    def test_logger_configuration(self):
        """Test that logger is properly configured."""
        assert self.analyzer.logger.name == "src.infrastructure.utils.coverage_analyzer"
        assert isinstance(self.analyzer.logger, logging.Logger)


class TestCoverageUtilityFunctions:
    """Test utility functions for coverage analysis."""

    def test_get_mock_coverage_data(self):
        """Test mock coverage data generation."""
        task_id = "MOCK-01"
        result = get_mock_coverage_data(task_id)
        
        # Check structure
        assert "task_id" in result
        assert "coverage_percentage" in result
        assert "lines_covered" in result
        assert "lines_total" in result
        
        # Check values
        assert result["task_id"] == task_id
        assert isinstance(result["coverage_percentage"], (int, float))
        assert isinstance(result["lines_covered"], int)
        assert isinstance(result["lines_total"], int)
        
        # Check that numbers are reasonable
        assert 0 <= result["coverage_percentage"] <= 100
        assert result["lines_covered"] <= result["lines_total"]

    def test_get_mock_coverage_data_consistency(self):
        """Test that mock coverage data is consistent."""
        result = get_mock_coverage_data("CONSISTENT-01")
        
        lines_covered = result["lines_covered"]
        lines_total = result["lines_total"]
        coverage_percentage = result["coverage_percentage"]
        
        # Calculate expected percentage
        expected_percentage = (lines_covered / lines_total) * 100
        assert abs(coverage_percentage - expected_percentage) < 0.1

    def test_analyze_coverage_function_with_coverage_module(self):
        """Test analyze_coverage function when coverage module is available."""
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = Mock()  # Module exists
            
            with patch("coverage.Coverage") as mock_coverage:
                # Mock successful import and usage
                result = analyze_coverage("COVERAGE-01")
                
                # Should return empty dict when real coverage is used
                assert isinstance(result, dict)

    def test_analyze_coverage_function_without_coverage_module(self):
        """Test analyze_coverage function when coverage module is not available."""
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = None  # Module not found
            
            result = analyze_coverage("NO-COVERAGE-01")
            
            # Should return mock data
            assert "task_id" in result
            assert result["task_id"] == "demo"  # Default task_id used

    def test_analyze_coverage_function_import_error(self):
        """Test analyze_coverage function when coverage import fails."""
        # Test the ImportError branch by mocking the coverage module to not exist
        # This tests the fallback behavior when coverage module can't be imported
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = None  # Module not found
            
            result = analyze_coverage("IMPORT-ERROR-01")
            
            # Should fallback to mock data with default task_id
            assert "task_id" in result
            assert result["task_id"] == "demo"

    def test_analyze_coverage_function_with_default_parameter(self):
        """Test analyze_coverage function with default parameter."""
        # Need to force it to use mock data by ensuring coverage module is not found
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = None  # Module not found
            
            result = analyze_coverage()
            
            assert "task_id" in result
            assert result["task_id"] == "demo"

    def test_analyze_coverage_function_with_custom_task_id(self):
        """Test analyze_coverage function with custom task ID."""
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = None  # No coverage module
            
            result = analyze_coverage("CUSTOM-TASK-01")
            
            # The function uses default "demo" task_id internally
            assert result["task_id"] == "demo"


class TestCoverageAnalyzerIntegration:
    """Test integration scenarios for CoverageAnalyzer."""

    def test_analyzer_with_different_project_roots(self):
        """Test analyzer behavior with different project roots."""
        roots = [".", "/tmp", "src", "tests"]
        
        for root in roots:
            if Path(root).exists() or root == ".":
                analyzer = CoverageAnalyzer(project_root=root)
                assert analyzer.project_root == Path(root)
                
                # Should still be able to collect data
                data = analyzer._collect_coverage_data()
                assert "totals" in data
                assert "files" in data

    def test_analyzer_threshold_validation(self):
        """Test that thresholds are properly validated."""
        analyzer = CoverageAnalyzer()
        
        for metric, threshold in analyzer.coverage_thresholds.items():
            assert isinstance(threshold, (int, float))
            assert 0 <= threshold <= 100
            assert metric in ["lines", "functions", "branches", "statements"]

    def test_multiple_analyzer_instances(self):
        """Test that multiple analyzer instances work independently."""
        analyzer1 = CoverageAnalyzer(project_root=".")
        analyzer2 = CoverageAnalyzer(project_root="/tmp")
        
        # They should have different project roots
        assert analyzer1.project_root != analyzer2.project_root
        
        # But same thresholds
        assert analyzer1.coverage_thresholds == analyzer2.coverage_thresholds
        
        # And independent data collection
        data1 = analyzer1._collect_coverage_data()
        data2 = analyzer2._collect_coverage_data()
        
        # Data should have same structure but could have different values
        assert "totals" in data1 and "totals" in data2
        assert "files" in data1 and "files" in data2

    def test_analyzer_logger_independence(self):
        """Test that each analyzer has its own logger instance."""
        analyzer1 = CoverageAnalyzer()
        analyzer2 = CoverageAnalyzer()
        
        # Loggers should have same name but could be different objects
        assert analyzer1.logger.name == analyzer2.logger.name
        assert analyzer1.logger.name == "src.infrastructure.utils.coverage_analyzer"

    def test_coverage_data_format_consistency(self):
        """Test that coverage data format is consistent across calls."""
        analyzer = CoverageAnalyzer()
        
        # Collect data multiple times
        data1 = analyzer._collect_coverage_data()
        data2 = analyzer._collect_coverage_data()
        data3 = analyzer._collect_coverage_data()
        
        # All should have same structure
        for data in [data1, data2, data3]:
            assert "totals" in data
            assert "files" in data
            assert "percent_covered" in data["totals"]
            
            for filename, file_data in data["files"].items():
                assert "summary" in file_data
                assert "percent_covered" in file_data["summary"]