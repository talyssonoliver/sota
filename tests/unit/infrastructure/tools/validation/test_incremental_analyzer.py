"""
Test suite for Incremental Analyzer using TDD approach.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.infrastructure.tools.validation.core.incremental_analyzer import (
    ChangeType,
    FileChange,
    IncrementalAnalyzer,
    IncrementalResult,
)


class TestIncrementalAnalyzer:
    """Test incremental analyzer for pull request validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)

        # Create test git repository
        self.create_test_git_repo()

        self.analyzer = IncrementalAnalyzer(self.root_path, base_branch="main")

    def create_test_git_repo(self):
        """Create a test git repository with history."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=self.root_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=self.root_path
        )
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.root_path)

        # Create initial files
        main_file = self.root_path / "main.py"
        main_file.write_text(
            """
'''Main module.'''

def hello_world():
    '''Say hello to the world.'''
    return "Hello, World!"

def add_numbers(a, b):
    '''Add two numbers.'''
    return a + b
"""
        )

        utils_file = self.root_path / "utils.py"
        utils_file.write_text(
            """
'''Utility functions.'''

def multiply(a, b):
    '''Multiply two numbers.'''
    return a * b

def divide(a, b):
    '''Divide two numbers.'''
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
"""
        )

        # Add and commit initial files
        subprocess.run(["git", "add", "."], cwd=self.root_path)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.root_path)

        # Create main branch
        subprocess.run(["git", "branch", "main"], cwd=self.root_path)
        subprocess.run(["git", "checkout", "main"], cwd=self.root_path)

        # Create feature branch with changes
        subprocess.run(["git", "checkout", "-b", "feature-branch"], cwd=self.root_path)

        # Modify existing file
        main_file.write_text(
            """
'''Main module with improvements.'''

def hello_world():
    '''Say hello to the world.'''
    return "Hello, World!"

def add_numbers(a, b):
    '''Add two numbers with validation.'''
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Arguments must be numbers")
    return a + b

def subtract_numbers(a, b):
    '''Subtract two numbers.'''
    return a - b
"""
        )

        # Add new file
        new_file = self.root_path / "new_module.py"
        new_file.write_text(
            """
'''New module with additional functionality.'''

def power(base, exponent):
    '''Calculate power of a number.'''
    return base ** exponent

def factorial(n):
    '''Calculate factorial of a number.'''
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
"""
        )

        # Commit changes
        subprocess.run(["git", "add", "."], cwd=self.root_path)
        subprocess.run(["git", "commit", "-m", "Add new features"], cwd=self.root_path)

    def test_initialization(self):
        """Test analyzer initialization."""
        assert self.analyzer.root_path == self.root_path
        assert self.analyzer.base_branch == "main"
        assert self.analyzer.changes == []
        assert self.analyzer.baseline_report is None
        assert self.analyzer.current_report is None
        assert self.analyzer.unified_validator is not None

    @patch("subprocess.run")
    def test_get_file_changes(self, mock_run):
        """Test getting file changes from git."""
        # Mock git diff output
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = """M\tmain.py
A\tnew_module.py
D\tdeleted_file.py"""

        with patch.object(self.analyzer, "_get_line_changes") as mock_lines:
            mock_lines.return_value = (10, 5)

            changes = self.analyzer._get_file_changes("main")

            assert len(changes) == 3

            # Check change types
            change_types = [c.change_type for c in changes]
            assert ChangeType.MODIFIED in change_types
            assert ChangeType.ADDED in change_types
            assert ChangeType.DELETED in change_types

            # Check file paths
            file_paths = [c.file_path for c in changes]
            assert "main.py" in file_paths
            assert "new_module.py" in file_paths
            assert "deleted_file.py" in file_paths

    @patch("subprocess.run")
    def test_get_line_changes(self, mock_run):
        """Test getting line changes for a file."""
        # Mock git diff --numstat output
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "15\t3\tmain.py"

        lines_added, lines_deleted = self.analyzer._get_line_changes("main.py", "main")

        assert lines_added == 15
        assert lines_deleted == 3

        # Should call git diff --numstat
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "git" in call_args
        assert "diff" in call_args
        assert "--numstat" in call_args

    @patch("subprocess.run")
    def test_get_baseline_report(self, mock_run):
        """Test getting baseline report from target branch."""
        # Mock git worktree commands
        mock_run.return_value.returncode = 0

        # Patch the UnifiedValidator class since the method creates new instances
        with patch(
            "src.infrastructure.tools.validation.core.incremental_analyzer.Validator"
        ) as mock_validator_class:
            mock_validator_instance = Mock()
            mock_validator_instance.run_validation.return_value = {
                "summary": {"total_issues": 5, "critical_issues": 1},
                "phase_results": {},
            }
            mock_validator_class.return_value = mock_validator_instance

            baseline_report = self.analyzer._get_baseline_report("main")

            # Should return validation report
            assert baseline_report is not None
            assert "summary" in baseline_report
            assert baseline_report["summary"]["total_issues"] == 5

    def test_analyze_changed_files(self):
        """Test analyzing only changed files."""
        # Set up mock changes
        self.analyzer.changes = [
            FileChange("main.py", ChangeType.MODIFIED, 10, 5, is_new_file=False),
            FileChange("new_module.py", ChangeType.ADDED, 20, 0, is_new_file=True),
            FileChange("deleted_file.py", ChangeType.DELETED, 0, 15, is_new_file=False),
        ]

        # Patch the UnifiedValidator class since the method creates new instances
        with patch(
            "src.infrastructure.tools.validation.core.incremental_analyzer.Validator"
        ) as mock_validator_class:
            mock_validator_instance = Mock()
            mock_validator_instance.run_validation.return_value = {
                "detailed_issues": [
                    {"category": "syntax", "severity": "error", "file": "main.py"},
                    {
                        "category": "style",
                        "severity": "warning",
                        "file": "new_module.py",
                    },
                ],
                "summary": {"total_issues": 2},
            }
            mock_validator_class.return_value = mock_validator_instance

            result = self.analyzer._analyze_changed_files()

            assert "issues" in result
            assert "files_analyzed" in result
            assert "summary" in result
            assert len(result["issues"]) == 2
            assert result["files_analyzed"] == 2  # Only Python files that exist

    def test_calculate_incremental_metrics(self):
        """Test calculating incremental metrics."""
        # Set up baseline report
        self.analyzer.baseline_report = {"summary": {"total_issues": 10}}

        # Set up focused results
        focused_results = {
            "issues": [
                {"category": "syntax", "severity": "error"},
                {"category": "style", "severity": "warning"},
                {"category": "performance", "severity": "info"},
            ],
            "files_analyzed": 2,
        }

        # Set up changes
        self.analyzer.changes = [
            FileChange("main.py", ChangeType.MODIFIED, 10, 5, is_new_file=False),
            FileChange("new_module.py", ChangeType.ADDED, 20, 0, is_new_file=True),
        ]

        result = self.analyzer._calculate_incremental_metrics(focused_results)

        assert isinstance(result, IncrementalResult)
        assert result.changed_files_count == 2
        assert result.new_issues_count >= 0
        assert result.fixed_issues_count >= 0
        assert -1 <= result.net_quality_impact <= 1
        assert len(result.focus_areas) > 0
        assert len(result.recommendations) > 0

    def test_determine_focus_areas(self):
        """Test determining focus areas based on issues."""
        # Test with issues
        focused_results = {
            "issues": [
                {"category": "syntax", "severity": "error"},
                {"category": "syntax", "severity": "error"},
                {"category": "style", "severity": "warning"},
                {"category": "performance", "severity": "info"},
            ]
        }

        focus_areas = self.analyzer._determine_focus_areas(focused_results)

        assert len(focus_areas) > 0
        assert "syntax: 2 issues" in focus_areas
        assert "style: 1 issues" in focus_areas
        assert "performance: 1 issues" in focus_areas

        # Test with no issues
        focused_results = {"issues": []}
        focus_areas = self.analyzer._determine_focus_areas(focused_results)
        assert focus_areas == ["No issues found in changed files"]

    def test_generate_incremental_recommendations(self):
        """Test generating incremental recommendations."""
        focused_results = {
            "issues": [
                {"category": "syntax", "severity": "error"},
                {"category": "style", "severity": "warning"},
            ]
        }

        # Set up changes
        self.analyzer.changes = [
            FileChange("main.py", ChangeType.MODIFIED, 150, 50, is_new_file=False),
            FileChange("new_module.py", ChangeType.ADDED, 100, 0, is_new_file=True),
        ]

        recommendations = self.analyzer._generate_incremental_recommendations(
            focused_results, -0.5, 2  # Quality regression, 2 issues
        )

        assert len(recommendations) > 0
        assert any("Quality regression detected" in rec for rec in recommendations)
        assert any("2 issues found" in rec for rec in recommendations)
        assert any("1 new files added" in rec for rec in recommendations)
        assert any("1 files with large changes" in rec for rec in recommendations)

    def test_identify_quick_fixes(self):
        """Test identifying quick fixes."""
        focused_results = {
            "issues": [
                {"category": "formatting", "auto_fixable": True},
                {"category": "imports", "auto_fixable": True},
                {"category": "syntax", "auto_fixable": False},
            ]
        }

        quick_fixes = self.analyzer._identify_quick_fixes(focused_results)

        assert len(quick_fixes) > 0
        assert any("2 issues can be auto-fixed" in fix for fix in quick_fixes)
        assert any("Run 'black .' to fix" in fix for fix in quick_fixes)
        assert any("Run 'isort .' to fix" in fix for fix in quick_fixes)

    def test_analyze_pull_request_no_changes(self):
        """Test analyzing pull request with no changes."""
        with patch.object(self.analyzer, "_get_file_changes") as mock_changes:
            mock_changes.return_value = []

            result = self.analyzer.analyze_pull_request("main")

            assert isinstance(result, IncrementalResult)
            assert result.changed_files_count == 0
            assert result.new_issues_count == 0
            assert result.fixed_issues_count == 0
            assert result.net_quality_impact == 0.0
            assert result.recommendations == ["No changes to analyze"]

    def test_analyze_pull_request_with_changes(self):
        """Test analyzing pull request with changes."""
        with patch.object(self.analyzer, "_get_file_changes") as mock_changes:
            mock_changes.return_value = [
                FileChange("main.py", ChangeType.MODIFIED, 10, 5, is_new_file=False),
                FileChange("new_module.py", ChangeType.ADDED, 20, 0, is_new_file=True),
            ]

            # Patch the UnifiedValidator class since the method creates new instances
            with patch(
                "src.infrastructure.tools.validation.core.incremental_analyzer.Validator"
            ) as mock_validator_class:
                mock_validator_instance = Mock()
                mock_validator_instance.run_validation.return_value = {
                    "detailed_issues": [{"category": "style", "severity": "warning"}],
                    "summary": {"total_issues": 1},
                }
                mock_validator_class.return_value = mock_validator_instance

                with patch.object(
                    self.analyzer, "_get_baseline_report"
                ) as mock_baseline:
                    mock_baseline.return_value = {"summary": {"total_issues": 2}}

                    result = self.analyzer.analyze_pull_request("main")

                    assert isinstance(result, IncrementalResult)
                    assert result.changed_files_count == 2
                    assert result.fixed_issues_count == 1  # 2 baseline - 1 current
                    assert len(result.focus_areas) > 0
                    assert len(result.recommendations) > 0

    def test_generate_pr_comment(self):
        """Test generating PR comment."""
        # Set up test changes
        self.analyzer.changes = [
            FileChange("main.py", ChangeType.MODIFIED, 10, 5, is_new_file=False),
            FileChange("new_module.py", ChangeType.ADDED, 20, 0, is_new_file=True),
        ]

        result = IncrementalResult(
            changed_files_count=2,
            new_issues_count=1,
            fixed_issues_count=2,
            net_quality_impact=0.3,
            focus_areas=["style: 1 issues"],
            recommendations=["Good work!", "Consider adding tests"],
        )

        comment = self.analyzer.generate_pr_comment(result)

        assert "## ✅ Code Quality Analysis" in comment
        assert "Files Changed**: 2" in comment
        assert "New Issues**: 1" in comment
        assert "Fixed Issues**: 2" in comment
        assert "focus areas" in comment.lower()
        assert "recommendations" in comment.lower()
        assert "main.py" in comment
        assert "new_module.py" in comment

    def test_should_request_review(self):
        """Test determining if manual review should be requested."""
        # Set up changes
        self.analyzer.changes = [
            FileChange("main.py", ChangeType.MODIFIED, 100, 50, is_new_file=False),
            FileChange("new_module.py", ChangeType.ADDED, 200, 0, is_new_file=True),
        ]

        # Test case 1: Quality regression
        result1 = IncrementalResult(
            changed_files_count=2,
            new_issues_count=3,
            fixed_issues_count=0,
            net_quality_impact=-0.3,  # Quality regression
            focus_areas=[],
            recommendations=[],
        )

        assert self.analyzer.should_request_review(result1) is True

        # Test case 2: Many new issues
        result2 = IncrementalResult(
            changed_files_count=2,
            new_issues_count=8,  # Many new issues
            fixed_issues_count=0,
            net_quality_impact=0.1,
            focus_areas=[],
            recommendations=[],
        )

        assert self.analyzer.should_request_review(result2) is True

        # Test case 3: Good quality
        result3 = IncrementalResult(
            changed_files_count=2,
            new_issues_count=1,
            fixed_issues_count=2,
            net_quality_impact=0.2,
            focus_areas=[],
            recommendations=[],
        )

        assert self.analyzer.should_request_review(result3) is False

    def test_get_merge_recommendation(self):
        """Test getting merge recommendation."""
        # Set up changes
        self.analyzer.changes = [
            FileChange("main.py", ChangeType.MODIFIED, 10, 5, is_new_file=False)
        ]

        # Test case 1: Should allow merge
        result1 = IncrementalResult(
            changed_files_count=1,
            new_issues_count=2,
            fixed_issues_count=3,
            net_quality_impact=0.2,
            focus_areas=[],
            recommendations=[],
        )

        recommendation1 = self.analyzer.get_merge_recommendation(result1)

        assert recommendation1["can_merge"] is True
        assert recommendation1["requires_review"] is False
        assert "recommendation" in recommendation1
        assert "quality_score" in recommendation1
        assert 0 <= recommendation1["quality_score"] <= 100

        # Test case 2: Should block merge
        result2 = IncrementalResult(
            changed_files_count=1,
            new_issues_count=15,  # Too many new issues
            fixed_issues_count=0,
            net_quality_impact=-0.6,  # Significant regression
            focus_areas=[],
            recommendations=[],
        )

        recommendation2 = self.analyzer.get_merge_recommendation(result2)

        assert recommendation2["can_merge"] is False
        assert recommendation2["requires_review"] is True

    def test_assess_impact(self):
        """Test impact assessment."""
        assert self.analyzer._assess_impact(0.4) == "Significant quality improvement"
        assert self.analyzer._assess_impact(0.2) == "Minor quality improvement"
        assert self.analyzer._assess_impact(0.0) == "Neutral impact"
        assert self.analyzer._assess_impact(-0.2) == "Minor quality regression"
        assert self.analyzer._assess_impact(-0.4) == "Significant quality regression"

    def test_summarize_changes_by_type(self):
        """Test summarizing changes by type."""
        self.analyzer.changes = [
            FileChange("main.py", ChangeType.MODIFIED, 10, 5, is_new_file=False),
            FileChange("new_module.py", ChangeType.ADDED, 20, 0, is_new_file=True),
            FileChange("another.py", ChangeType.MODIFIED, 5, 2, is_new_file=False),
            FileChange("deleted.py", ChangeType.DELETED, 0, 15, is_new_file=False),
        ]

        summary = self.analyzer._summarize_changes_by_type()

        assert summary["modified"] == 2
        assert summary["added"] == 1
        assert summary["deleted"] == 1

    def test_generate_incremental_report(self):
        """Test generating incremental report."""
        # Set up changes
        self.analyzer.changes = [
            FileChange("main.py", ChangeType.MODIFIED, 10, 5, is_new_file=False),
            FileChange("new_module.py", ChangeType.ADDED, 20, 0, is_new_file=True),
        ]

        result = IncrementalResult(
            changed_files_count=2,
            new_issues_count=1,
            fixed_issues_count=2,
            net_quality_impact=0.3,
            focus_areas=["style: 1 issues"],
            recommendations=["Good work!"],
        )

        with patch("time.strftime") as mock_time:
            mock_time.return_value = "2023-01-01 12:00:00"

            # This should create a report file
            self.analyzer._generate_incremental_report(result)

            # Check that report file was created
            report_path = self.root_path / "reports" / "incremental_analysis.json"
            assert report_path.exists()

            # Check report content
            with open(report_path) as f:
                report_data = json.load(f)

            assert report_data["timestamp"] == "2023-01-01 12:00:00"
            assert report_data["analysis_type"] == "incremental"
            assert report_data["base_branch"] == "main"
            assert report_data["changes_summary"]["total_files_changed"] == 2
            assert report_data["quality_impact"]["net_quality_impact"] == 0.3
            assert len(report_data["file_changes"]) == 2


class TestIncrementalAnalyzerIntegration:
    """Integration tests for incremental analyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)

        # Create comprehensive test project
        self.create_comprehensive_test_project()

        self.analyzer = IncrementalAnalyzer(self.root_path)

    def create_comprehensive_test_project(self):
        """Create a comprehensive test project with git history."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=self.root_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=self.root_path
        )
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.root_path)

        # Create initial application
        app_file = self.root_path / "app.py"
        app_file.write_text(
            """
'''Main application.'''

class Calculator:
    '''Simple calculator.'''
    
    def add(self, a, b):
        '''Add two numbers.'''
        return a + b
    
    def subtract(self, a, b):
        '''Subtract two numbers.'''
        return a - b
"""
        )

        test_file = self.root_path / "test_app.py"
        test_file.write_text(
            """
'''Tests for application.'''

import pytest
from app import Calculator

def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_subtract():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2
"""
        )

        # Commit initial version
        subprocess.run(["git", "add", "."], cwd=self.root_path)
        subprocess.run(["git", "commit", "-m", "Initial version"], cwd=self.root_path)

        # Create main branch
        subprocess.run(["git", "branch", "main"], cwd=self.root_path)
        subprocess.run(["git", "checkout", "main"], cwd=self.root_path)

        # Create feature branch
        subprocess.run(["git", "checkout", "-b", "feature"], cwd=self.root_path)

        # Make improvements
        app_file.write_text(
            """
'''Main application with improvements.'''

import logging

logger = logging.getLogger(__name__)


class Calculator:
    '''Enhanced calculator with validation and logging.'''
    
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        '''Add two numbers with validation.'''
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Arguments must be numbers")
        
        result = a + b
        self.history.append(f"add({a}, {b}) = {result}")
        logger.info(f"Addition: {a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        '''Subtract two numbers with validation.'''
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Arguments must be numbers")
        
        result = a - b
        self.history.append(f"subtract({a}, {b}) = {result}")
        logger.info(f"Subtraction: {a} - {b} = {result}")
        return result
    
    def multiply(self, a, b):
        '''Multiply two numbers.'''
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Arguments must be numbers")
        
        result = a * b
        self.history.append(f"multiply({a}, {b}) = {result}")
        logger.info(f"Multiplication: {a} * {b} = {result}")
        return result
    
    def get_history(self):
        '''Get calculation history.'''
        return self.history.copy()
"""
        )

        # Add new utility module
        utils_file = self.root_path / "utils.py"
        utils_file.write_text(
            """
'''Utility functions.'''

def validate_number(value):
    '''Validate that a value is a number.'''
    if not isinstance(value, (int, float)):
        raise TypeError(f"Expected number, got {type(value).__name__}")
    return True

def format_result(result, precision=2):
    '''Format calculation result.'''
    if isinstance(result, float):
        return round(result, precision)
    return result
"""
        )

        # Update tests
        test_file.write_text(
            """
'''Tests for enhanced application.'''

import pytest
from app import Calculator
from utils import validate_number, format_result


class TestCalculator:
    def setup_method(self):
        self.calc = Calculator()
    
    def test_add_valid(self):
        assert self.calc.add(2, 3) == 5
        assert self.calc.add(-1, 1) == 0
        assert self.calc.add(2.5, 1.5) == 4.0
    
    def test_add_invalid(self):
        with pytest.raises(TypeError):
            self.calc.add("2", 3)
        with pytest.raises(TypeError):
            self.calc.add(2, "3")
    
    def test_subtract_valid(self):
        assert self.calc.subtract(5, 3) == 2
        assert self.calc.subtract(-1, 1) == -2
    
    def test_subtract_invalid(self):
        with pytest.raises(TypeError):
            self.calc.subtract("5", 3)
    
    def test_multiply(self):
        assert self.calc.multiply(2, 3) == 6
        assert self.calc.multiply(-2, 3) == -6
    
    def test_history(self):
        self.calc.add(1, 2)
        self.calc.subtract(5, 3)
        history = self.calc.get_history()
        assert len(history) == 2
        assert "add(1, 2) = 3" in history
        assert "subtract(5, 3) = 2" in history


class TestUtils:
    def test_validate_number(self):
        assert validate_number(5) is True
        assert validate_number(3.14) is True
        
        with pytest.raises(TypeError):
            validate_number("5")
        with pytest.raises(TypeError):
            validate_number(None)
    
    def test_format_result(self):
        assert format_result(3.14159, 2) == 3.14
        assert format_result(5) == 5
        assert format_result(2.0, 1) == 2.0
"""
        )

        # Commit changes
        subprocess.run(["git", "add", "."], cwd=self.root_path)
        subprocess.run(
            ["git", "commit", "-m", "Add enhancements and new features"],
            cwd=self.root_path,
        )

    @pytest.mark.slow
    def test_full_incremental_analysis(self):
        """Test full incremental analysis workflow."""
        with patch.object(
            self.analyzer.unified_validator, "run_validation"
        ) as mock_validate:
            # Mock current validation
            mock_validate.return_value = {
                "detailed_issues": [
                    {
                        "category": "style",
                        "severity": "warning",
                        "file": "app.py",
                        "auto_fixable": True,
                    },
                    {
                        "category": "complexity",
                        "severity": "info",
                        "file": "app.py",
                        "auto_fixable": False,
                    },
                ],
                "summary": {"total_issues": 2, "critical_issues": 0, "warnings": 1},
            }

            # Run analysis
            result = self.analyzer.analyze_pull_request("main")

            # Should complete successfully
            assert isinstance(result, IncrementalResult)
            assert result.changed_files_count > 0
            assert len(result.focus_areas) > 0
            assert len(result.recommendations) > 0

    @pytest.mark.slow
    def test_pr_comment_generation(self):
        """Test PR comment generation with real data."""
        with patch.object(self.analyzer, "_get_file_changes") as mock_changes:
            mock_changes.return_value = [
                FileChange("app.py", ChangeType.MODIFIED, 30, 10, is_new_file=False),
                FileChange("utils.py", ChangeType.ADDED, 25, 0, is_new_file=True),
            ]

            with patch.object(
                self.analyzer.unified_validator, "run_validation"
            ) as mock_validate:
                mock_validate.return_value = {
                    "detailed_issues": [
                        {
                            "category": "style",
                            "severity": "warning",
                            "auto_fixable": True,
                        },
                        {
                            "category": "documentation",
                            "severity": "info",
                            "auto_fixable": False,
                        },
                    ],
                    "summary": {"total_issues": 2},
                }

                result = self.analyzer.analyze_pull_request("main")
                comment = self.analyzer.generate_pr_comment(result)

                # Should generate comprehensive comment
                assert "Code Quality Analysis" in comment
                assert "Files Changed" in comment
                assert "Focus Areas" in comment
                assert "Recommendations" in comment
                assert "File Changes" in comment
                assert "app.py" in comment
                assert "utils.py" in comment

    def test_merge_recommendation_logic(self):
        """Test merge recommendation logic with different scenarios."""
        # Scenario 1: High quality changes
        with patch.object(self.analyzer, "_get_file_changes") as mock_changes:
            mock_changes.return_value = [
                FileChange("app.py", ChangeType.MODIFIED, 10, 5, is_new_file=False)
            ]

            # Mock both the main validator and any new validators created
            with patch.object(
                self.analyzer.unified_validator, "run_validation"
            ) as mock_validate, patch(
                "src.infrastructure.tools.validation.core.incremental_analyzer.Validator"
            ) as mock_validator_class:

                # Configure main validator mock
                mock_validate.return_value = {
                    "detailed_issues": [],
                    "summary": {"total_issues": 0},
                }

                # Configure the focused validator that gets created in _analyze_changed_files
                mock_focused_validator = Mock()
                mock_focused_validator.run_validation.return_value = {
                    "detailed_issues": [],
                    "summary": {"total_issues": 0},
                }
                mock_validator_class.return_value = mock_focused_validator

                result = self.analyzer.analyze_pull_request("main")
                recommendation = self.analyzer.get_merge_recommendation(result)

                assert recommendation["can_merge"] is True
                assert recommendation["requires_review"] is False
                assert recommendation["quality_score"] > 50

        # Scenario 2: Poor quality changes
        with patch.object(
            self.analyzer, "_get_file_changes"
        ) as mock_changes, patch.object(
            self.analyzer.unified_validator, "run_validation"
        ) as mock_validate, patch(
            "src.infrastructure.tools.validation.core.incremental_analyzer.Validator"
        ) as mock_validator_class, patch.object(
            self.analyzer, "_analyze_changed_files"
        ) as mock_analyze, patch.object(
            self.analyzer, "_get_baseline_report"
        ) as mock_baseline:

            mock_changes.return_value = [
                FileChange(
                    "app.py", ChangeType.MODIFIED, 200, 100, is_new_file=False
                )  # Large change
            ]

            # Configure main validator mock
            mock_validate.return_value = {
                "detailed_issues": [
                    {"category": "security", "severity": "error"},
                    {"category": "bugs", "severity": "error"},
                    {"category": "style", "severity": "warning"},
                ]
                * 5,  # 15 issues total
                "summary": {"total_issues": 15},
            }

            # Configure the focused validator that gets created in _analyze_changed_files
            mock_focused_validator = Mock()
            mock_focused_validator.run_validation.return_value = {
                "detailed_issues": [
                    {"category": "security", "severity": "error"},
                    {"category": "bugs", "severity": "error"},
                    {"category": "style", "severity": "warning"},
                ]
                * 5,  # 15 issues total
                "summary": {"total_issues": 15},
            }
            mock_validator_class.return_value = mock_focused_validator

            # Mock _analyze_changed_files to return our expected results
            mock_analyze.return_value = {
                "issues": [
                    {"category": "security", "severity": "error"},
                    {"category": "bugs", "severity": "error"},
                    {"category": "style", "severity": "warning"},
                ]
                * 5,  # 15 issues total
                "files_analyzed": 1,
                "summary": {"total_issues": 15},
            }

            # Mock baseline to have 0 issues (clean baseline)
            mock_baseline.return_value = {
                "detailed_issues": [],
                "summary": {"total_issues": 0},
            }

            result = self.analyzer.analyze_pull_request("main")
            recommendation = self.analyzer.get_merge_recommendation(result)

            assert recommendation["can_merge"] is False
            assert recommendation["requires_review"] is True
            assert recommendation["quality_score"] < 50


if __name__ == "__main__":
    pytest.main([__file__])
