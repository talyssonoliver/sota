"""
Tests for performance validator - Analyzes code performance patterns and suggests optimizations.
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.infrastructure.tools.validation.core.performance_validator import PerformanceValidator
from src.infrastructure.tools.validation.core.issue_model import IssueType, SeverityLevel


class TestPerformanceValidator:
    """Test cases for PerformanceValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)
        
        # Create test files
        self.create_test_files()
        
        self.validator = PerformanceValidator(root_path=self.root_path)

    def create_test_files(self):
        """Create test files for performance validation."""
        # File with complex function
        complex_file = self.root_path / "complex_code.py"
        complex_file.write_text("""
def complex_function(data):
    result = []
    for item in data:
        if item > 0:
            for subitem in item:
                if subitem % 2 == 0:
                    for x in range(len(subitem)):
                        if x > 5:
                            result.append(x * 2)
                        else:
                            result.append(x)
                else:
                    result.append(subitem)
            else:
                result.append(item)
        elif item < 0:
            result.append(-item)
        else:
            result.append(0)
    return result

def very_long_function():
    # This function has many lines to test line count validation
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    line8 = 8
    line9 = 9
    line10 = 10
    line11 = 11
    line12 = 12
    line13 = 13
    line14 = 14
    line15 = 15
    line16 = 16
    line17 = 17
    line18 = 18
    line19 = 19
    line20 = 20
    line21 = 21
    line22 = 22
    line23 = 23
    line24 = 24
    line25 = 25
    line26 = 26
    line27 = 27
    line28 = 28
    line29 = 29
    line30 = 30
    line31 = 31
    line32 = 32
    line33 = 33
    line34 = 34
    line35 = 35
    line36 = 36
    line37 = 37
    line38 = 38
    line39 = 39
    line40 = 40
    line41 = 41
    line42 = 42
    line43 = 43
    line44 = 44
    line45 = 45
    line46 = 46
    line47 = 47
    line48 = 48
    line49 = 49
    line50 = 50
    line51 = 51
    line52 = 52
    line53 = 53
    line54 = 54
    line55 = 55
    return line55
""")

        # File with performance anti-patterns
        antipattern_file = self.root_path / "antipatterns.py"
        antipattern_file.write_text("""
import time
import os
import *  # Wildcard import

def bad_performance():
    # List append in loop
    result = []
    for i in range(100):
        result.append(i * 2)
    
    # Length check anti-patterns
    if len(result) > 0:
        print("Has items")
    
    if len(result) == 0:
        print("Empty")
    
    # String formatting
    message = "Hello {}".format("world")
    
    # Range with len
    for i in range(len(result)):
        print(result[i])
    
    # Dictionary keys iteration
    data = {"a": 1, "b": 2}
    for key in data.keys():
        print(key)
    
    return result

def inefficient_patterns():
    # String concatenation in loop
    text = ""
    for i in range(10):
        text += str(i)
    
    # Nested loops
    for i in range(10):
        for j in range(10):
            print(i * j)
    
    # Global variable
    global global_var
    global_var = 10
    
    # Inefficient dictionary access
    data = {"key": "value"}
    if "key" in data.keys():
        print(data["key"])
    
    return text
""")

        # File with slow imports
        slow_import_file = self.root_path / "slow_imports.py"
        slow_import_file.write_text("""
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
""")

        # Very large file (for file size validation)
        large_file = self.root_path / "large_file.py"
        large_content = "# Large file\n" + "print('line')\n" * 600  # 601 lines total
        large_file.write_text(large_content)

        # Syntax error file (for error handling tests)
        error_file = self.root_path / "syntax_error.py"
        error_file.write_text("""
def broken_function(
    # Missing closing parenthesis and colon
    pass
""")

    def test_initialization(self):
        """Test validator initialization."""
        assert self.validator.root_path == self.root_path
        assert self.validator.performance_issues == []
        assert self.validator.import_times == {}
        assert self.validator.complexity_scores == {}

    def test_validate_performance(self):
        """Test full performance validation."""
        result = self.validator.validate_performance()
        
        # Should return boolean
        assert isinstance(result, bool)
        
        # Should have collected files
        assert len(self.validator.python_files) > 0
        
        # Should have found some issues
        assert len(self.validator.issues) > 0

    def test_check_function_complexity(self):
        """Test function complexity checking."""
        # Set low complexity threshold for testing
        self.validator.config["complexity_threshold"] = 5
        
        self.validator._collect_files()
        self.validator._check_function_complexity()
        
        # Should find high complexity issues
        complexity_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.HIGH_COMPLEXITY
        ]
        
        # Debug: print all issues if none found
        if len(complexity_issues) == 0:
            print(f"Found {len(self.validator.issues)} total issues:")
            for issue in self.validator.issues:
                print(f"  - {issue.issue_type}: {issue.message}")
        
        assert len(complexity_issues) > 0
        
        # Check issue details
        issue = complexity_issues[0]
        assert issue.category == "performance"
        assert "complexity" in issue.message.lower()
        assert issue.severity == SeverityLevel.WARNING
        assert not issue.auto_fixable

    def test_check_function_length(self):
        """Test function length checking."""
        # Set low line threshold for testing
        self.validator.config["max_function_lines"] = 10
        
        self.validator._collect_files()
        self.validator._check_function_complexity()
        
        # Should find long function issues
        long_function_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.FUNCTION_TOO_LONG
        ]
        assert len(long_function_issues) > 0
        
        # Check issue details
        issue = long_function_issues[0]
        assert issue.category == "performance"
        assert "too long" in issue.message.lower()
        assert issue.severity == SeverityLevel.WARNING

    def test_calculate_complexity(self):
        """Test cyclomatic complexity calculation."""
        import ast
        
        # Simple function (complexity = 1)
        simple_code = "def simple(): return 1"
        simple_tree = ast.parse(simple_code)
        simple_func = simple_tree.body[0]
        assert self.validator._calculate_complexity(simple_func) == 1
        
        # Function with if statement (complexity = 2)
        if_code = """
def with_if(x):
    if x > 0:
        return x
    return 0
"""
        if_tree = ast.parse(if_code)
        if_func = if_tree.body[0]
        assert self.validator._calculate_complexity(if_func) == 2
        
        # Function with multiple conditions
        complex_code = """
def complex_func(x, y):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                try:
                    result = i * y
                except ValueError:
                    result = 0
                if result > 10 and result < 100:
                    return result
    return 0
"""
        complex_tree = ast.parse(complex_code)
        complex_func = complex_tree.body[0]
        complexity = self.validator._calculate_complexity(complex_func)
        assert complexity > 5  # Should be quite complex

    def test_check_import_performance(self):
        """Test import performance checking."""
        # Set low import time threshold for testing
        self.validator.config["performance_thresholds"] = {"max_import_time": 0.001}
        
        self.validator._collect_files()
        self.validator._check_import_performance()
        
        # May or may not find slow imports depending on system
        # Just check that it doesn't crash and creates some records
        assert isinstance(self.validator.import_times, dict)

    def test_extract_imports(self):
        """Test import extraction from files."""
        slow_import_file = self.root_path / "slow_imports.py"
        imports = self.validator._extract_imports(slow_import_file)
        
        # Should find the imports we added
        expected_imports = {"sys", "os", "time", "json", "pathlib", "datetime"}
        assert imports.intersection(expected_imports)

    def test_measure_import_time(self):
        """Test import time measurement."""
        # Test with standard library module
        import_time = self.validator._measure_import_time("os")
        assert isinstance(import_time, float)
        assert import_time >= 0
        
        # Should cache results
        cached_time = self.validator._measure_import_time("os")
        assert cached_time == import_time
        
        # Test with non-existent module
        fake_time = self.validator._measure_import_time("nonexistent_module_12345")
        assert fake_time == 0.0

    def test_check_performance_antipatterns(self):
        """Test performance anti-pattern detection."""
        self.validator._collect_files()
        self.validator._check_performance_antipatterns()
        
        # Should find anti-pattern issues
        antipattern_issues = [
            issue for issue in self.validator.issues 
            if "anti-pattern" in issue.message.lower()
        ]
        assert len(antipattern_issues) > 0
        
        # Check for specific patterns
        issue_messages = [issue.message.lower() for issue in antipattern_issues]
        
        # Should detect various anti-patterns from our test file
        assert any("wildcard" in msg or "*" in msg for msg in issue_messages)

    def test_check_file_sizes(self):
        """Test file size checking."""
        # Set low file size threshold
        self.validator.config["max_file_lines"] = 100
        
        self.validator._collect_files()
        self.validator._check_file_sizes()
        
        # Should find large file issues
        large_file_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.STRUCTURE_ISSUE and "too large" in issue.message.lower()
        ]
        assert len(large_file_issues) > 0
        
        # Check issue details
        issue = large_file_issues[0]
        assert issue.category == "performance"
        assert "lines" in issue.message
        assert issue.severity == SeverityLevel.WARNING

    def test_check_inefficient_patterns(self):
        """Test inefficient pattern detection."""
        self.validator._collect_files()
        self.validator._check_inefficient_patterns()
        
        # Should find inefficient patterns
        inefficient_issues = [
            issue for issue in self.validator.issues 
            if "inefficient" in issue.message.lower()
        ]
        assert len(inefficient_issues) > 0
        
        # Check issue details
        for issue in inefficient_issues:
            assert issue.category == "performance"
            assert issue.severity == SeverityLevel.INFO
            assert not issue.auto_fixable

    def test_get_performance_report(self):
        """Test performance report generation."""
        self.validator._collect_files()
        self.validator.validate_performance()
        
        report = self.validator.get_performance_report()
        
        # Check report structure
        assert "total_files_analyzed" in report
        assert "performance_issues" in report
        assert "complexity_issues" in report
        assert "import_performance" in report
        assert "complexity_scores" in report
        assert "recommendations" in report
        
        # Check data types
        assert isinstance(report["total_files_analyzed"], int)
        assert isinstance(report["performance_issues"], int)
        assert isinstance(report["complexity_issues"], int)
        assert isinstance(report["import_performance"], dict)
        assert isinstance(report["complexity_scores"], dict)
        assert isinstance(report["recommendations"], list)
        
        # Should have analyzed some files
        assert report["total_files_analyzed"] > 0

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        # Add some test issues
        self.validator.add_issue(
            category="performance",
            issue_type=IssueType.HIGH_COMPLEXITY,
            file_path="test.py",
            message="High complexity detected"
        )
        
        self.validator.add_issue(
            category="performance", 
            issue_type=IssueType.PERFORMANCE_ISSUE,
            file_path="test.py",
            message="Slow import detected"
        )
        
        self.validator.add_issue(
            category="performance",
            issue_type=IssueType.FUNCTION_TOO_LONG,
            file_path="test.py", 
            message="Function too long"
        )
        
        recommendations = self.validator._generate_recommendations()
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should contain relevant recommendations
        rec_text = " ".join(recommendations).lower()
        assert any(keyword in rec_text for keyword in ["refactor", "complex", "function"])

    def test_error_handling_syntax_errors(self):
        """Test handling of files with syntax errors."""
        self.validator._collect_files()
        
        # Should not crash on syntax errors
        try:
            self.validator._check_function_complexity()
            self.validator._check_performance_antipatterns()
            self.validator._check_inefficient_patterns()
        except Exception as e:
            pytest.fail(f"Should handle syntax errors gracefully: {e}")
        
        # May generate analysis error issues
        error_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.ANALYSIS_ERROR
        ]
        # Could be 0 or more depending on whether the syntax error file is processed

    def test_empty_project_handling(self):
        """Test handling of project with no Python files."""
        empty_dir = Path(tempfile.mkdtemp())
        validator = PerformanceValidator(root_path=empty_dir)
        
        result = validator.validate_performance()
        
        # Should handle empty project gracefully
        assert isinstance(result, bool)
        assert len(validator.python_files) == 0
        assert len(validator.issues) == 0

    def test_configuration_customization(self):
        """Test custom configuration handling."""
        custom_config = {
            "complexity_threshold": 3,
            "max_function_lines": 20,
            "max_file_lines": 200,
            "performance_thresholds": {
                "max_import_time": 0.5
            }
        }
        
        self.validator.config.update(custom_config)
        self.validator._collect_files()
        self.validator.validate_performance()
        
        # Should use custom thresholds
        assert self.validator.config["complexity_threshold"] == 3
        assert self.validator.config["max_function_lines"] == 20

    def test_has_errors_integration(self):
        """Test error detection integration."""
        # Initially no errors
        assert not self.validator.has_errors()
        
        # Add error-level issue
        self.validator.add_issue(
            category="performance",
            issue_type=IssueType.ANALYSIS_ERROR,
            file_path="test.py",
            message="Critical performance error",
            severity="error"
        )
        
        assert self.validator.has_errors()

    @patch('builtins.__import__')
    def test_import_measurement_with_exception(self, mock_import):
        """Test import time measurement when import raises exception."""
        mock_import.side_effect = ImportError("Module not found")
        
        import_time = self.validator._measure_import_time("fake_module")
        assert import_time == 0.0

    @patch('builtins.__import__')
    def test_import_measurement_with_system_exit(self, mock_import):
        """Test import time measurement when import calls sys.exit()."""
        mock_import.side_effect = SystemExit("Module called sys.exit()")
        
        import_time = self.validator._measure_import_time("exit_module")
        assert import_time == 0.0

    def test_async_function_complexity(self):
        """Test complexity calculation for async functions."""
        # Create file with async function
        async_file = self.root_path / "async_code.py"
        async_file.write_text("""
async def async_complex_function(data):
    result = []
    async for item in data:
        if item > 0:
            for subitem in item:
                if subitem % 2 == 0:
                    result.append(subitem)
                else:
                    async with some_context():
                        result.append(await process(subitem))
            else:
                result.append(item)
        elif item < 0:
            result.append(-item)
        else:
            result.append(0)
    return result
""")
        
        # Set low complexity threshold
        self.validator.config["complexity_threshold"] = 5
        self.validator._collect_files()
        self.validator._check_function_complexity()
        
        # Should detect complexity in async function
        complexity_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.HIGH_COMPLEXITY and "async_complex_function" in issue.message
        ]
        assert len(complexity_issues) > 0

    def test_comprehension_complexity(self):
        """Test complexity calculation includes comprehensions."""
        import ast
        
        # Function with list comprehension
        comp_code = """
def with_comprehensions():
    result = [x for x in range(10) if x % 2 == 0]
    result2 = {k: v for k, v in items.items() if v > 0}
    result3 = {x for x in data if x not in exclude}
    result4 = (x * 2 for x in numbers if x > threshold)
    return result, result2, result3, result4
"""
        comp_tree = ast.parse(comp_code)
        comp_func = comp_tree.body[0]
        complexity = self.validator._calculate_complexity(comp_func)
        assert complexity >= 5  # Base 1 + 4 comprehensions

    def test_performance_report_empty_state(self):
        """Test performance report with no issues."""
        empty_validator = PerformanceValidator(root_path=Path(tempfile.mkdtemp()))
        report = empty_validator.get_performance_report()
        
        assert report["total_files_analyzed"] == 0
        assert report["performance_issues"] == 0
        assert report["complexity_issues"] == 0
        assert report["import_performance"] == {}
        assert report["complexity_scores"] == {}
        assert report["recommendations"] == []