"""
Tests for base validator class - Foundation for all validation implementations.
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.infrastructure.tools.validation.core.base_validator import BaseValidator
from src.infrastructure.tools.validation.core.issue_model import (
    IssueType,
    SeverityLevel,
    ValidationIssue,
)


class TestBaseValidator:
    """Test cases for BaseValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)
        
        # Create test files
        self.create_test_files()
        
        self.validator = BaseValidator(root_path=self.root_path)

    def create_test_files(self):
        """Create test files for validation."""
        # Python files
        (self.root_path / "main.py").write_text("print('Hello World')")
        (self.root_path / "utils.py").write_text("def helper(): pass")
        
        # Sub-directory with Python files
        sub_dir = self.root_path / "package"
        sub_dir.mkdir()
        (sub_dir / "__init__.py").write_text("")
        (sub_dir / "module.py").write_text("class TestClass: pass")
        
        # Non-Python files
        (self.root_path / "README.md").write_text("# Test Project")
        (self.root_path / "config.json").write_text('{"test": true}')
        
        # Excluded directory
        cache_dir = self.root_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "test.pyc").write_text("compiled")

    def test_initialization(self):
        """Test validator initialization."""
        assert self.validator.root_path == self.root_path
        assert self.validator.issues == []
        assert self.validator.fixes_applied == []
        assert isinstance(self.validator.start_time, float)
        assert isinstance(self.validator.config, dict)
        assert isinstance(self.validator.results, dict)

    def test_initialization_with_defaults(self):
        """Test validator initialization with default root path."""
        validator = BaseValidator()
        assert validator.root_path == Path.cwd()
        assert len(validator.results) > 0

    def test_initialization_with_shared_collector(self):
        """Test validator initialization with shared collector."""
        mock_collector = Mock()
        validator = BaseValidator(shared_collector=mock_collector)
        assert validator.shared_collector == mock_collector

    def test_config_loading_defaults(self):
        """Test default configuration loading."""
        config = self.validator.config
        assert "coverage_threshold" in config
        assert config["coverage_threshold"] == 85
        assert "complexity_threshold" in config
        assert config["complexity_threshold"] == 10
        assert "excluded_dirs" in config
        assert "__pycache__" in config["excluded_dirs"]

    def test_config_loading_from_file(self):
        """Test configuration loading from file."""
        # Create config file
        config_data = {"coverage_threshold": 90, "custom_setting": "test"}
        config_path = self.root_path / "validation_config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)
        
        validator = BaseValidator(root_path=self.root_path)
        assert validator.config["coverage_threshold"] == 90
        assert validator.config["custom_setting"] == "test"

    def test_config_loading_invalid_file(self):
        """Test configuration loading with invalid JSON file."""
        config_path = self.root_path / "validation_config.json"
        config_path.write_text("invalid json content")
        
        # Should still work with defaults
        validator = BaseValidator(root_path=self.root_path)
        assert validator.config["coverage_threshold"] == 85

    def test_add_issue_with_string_values(self):
        """Test adding issue with string parameters."""
        self.validator.add_issue(
            category="syntax",
            issue_type="syntax_error",
            file_path="test.py",
            message="Test message",
            line=10,
            character=5,
            severity="error",
            auto_fixable=True
        )
        
        assert len(self.validator.issues) == 1
        issue = self.validator.issues[0]
        assert issue.category == "syntax"
        assert issue.issue_type == IssueType.SYNTAX_ERROR
        assert issue.file_path == "test.py"
        assert issue.message == "Test message"
        assert issue.line == 10
        assert issue.character == 5
        assert issue.severity == SeverityLevel.ERROR
        assert issue.auto_fixable is True

    def test_add_issue_with_enum_values(self):
        """Test adding issue with enum parameters."""
        self.validator.add_issue(
            category="security",
            issue_type=IssueType.SECURITY_ISSUE,
            file_path=Path("secure.py"),
            message="Security issue",
            severity=SeverityLevel.WARNING
        )
        
        assert len(self.validator.issues) == 1
        issue = self.validator.issues[0]
        assert issue.issue_type == IssueType.SECURITY_ISSUE
        assert issue.severity == SeverityLevel.WARNING

    def test_add_issue_invalid_enum_values(self):
        """Test adding issue with invalid enum values."""
        self.validator.add_issue(
            category="syntax",  # Use valid category
            issue_type="INVALID_TYPE",
            file_path="test.py",
            message="Test message",
            severity="invalid_severity"
        )
        
        issue = self.validator.issues[0]
        assert issue.issue_type == IssueType.OTHER
        assert issue.severity == SeverityLevel.WARNING

    def test_add_issue_updates_results(self):
        """Test that adding issues updates legacy results structure."""
        # Add error
        self.validator.add_issue(
            category="syntax",
            issue_type="syntax_error",
            file_path="test.py",
            message="Error message",
            severity="error"
        )
        
        assert self.validator.results["syntax"]["status"] == "error"
        assert "Error message" in self.validator.results["syntax"]["errors"]
        
        # Add warning to different category
        self.validator.add_issue(
            category="imports",
            issue_type="import_error",
            file_path="test.py",
            message="Warning message",
            severity="warning"
        )
        
        assert self.validator.results["imports"]["status"] == "warning"
        assert "Warning message" in self.validator.results["imports"]["warnings"]

    def test_collect_files_without_shared_collector(self):
        """Test file collection without shared collector."""
        self.validator._collect_files()
        
        # Should find Python files but exclude cache directory
        python_files = [f.name for f in self.validator.python_files]
        assert "main.py" in python_files
        assert "utils.py" in python_files
        assert "__init__.py" in python_files
        assert "module.py" in python_files
        
        # Should not include files from excluded directories
        all_file_paths = [str(f) for f in self.validator.all_files]
        assert not any("__pycache__" in path for path in all_file_paths)

    def test_collect_files_with_shared_collector(self):
        """Test file collection with shared collector."""
        mock_collector = Mock()
        mock_collector.get_files.return_value = {
            "all_files": [Path("file1.py"), Path("file2.txt")],
            "python_files": [Path("file1.py")]
        }
        
        validator = BaseValidator(shared_collector=mock_collector)
        validator._collect_files()
        
        mock_collector.get_files.assert_called_once()
        assert len(validator.all_files) == 2
        assert len(validator.python_files) == 1

    def test_get_python_files(self):
        """Test getting Python files."""
        python_files = self.validator.get_python_files()
        
        # Should trigger file collection
        assert len(python_files) > 0
        assert all(f.suffix == ".py" for f in python_files)

    def test_has_errors(self):
        """Test error detection."""
        assert not self.validator.has_errors()
        
        self.validator.add_issue(
            category="syntax",
            issue_type="syntax_error",
            file_path="test.py",
            message="Test error",
            severity="error"
        )
        
        assert self.validator.has_errors()

    def test_has_warnings(self):
        """Test warning detection."""
        assert not self.validator.has_warnings()
        
        self.validator.add_issue(
            category="syntax",
            issue_type="syntax_error",
            file_path="test.py",
            message="Test warning",
            severity="warning"
        )
        
        assert self.validator.has_warnings()

    def test_get_issues_by_category(self):
        """Test getting issues by category."""
        self.validator.add_issue(
            category="syntax",
            issue_type="syntax_error",
            file_path="test.py",
            message="Syntax issue"
        )
        
        self.validator.add_issue(
            category="imports",
            issue_type="import_error",
            file_path="test.py",
            message="Import issue"
        )
        
        syntax_issues = self.validator.get_issues_by_category("syntax")
        assert len(syntax_issues) == 1
        assert syntax_issues[0].category == "syntax"
        
        import_issues = self.validator.get_issues_by_category("imports")
        assert len(import_issues) == 1
        assert import_issues[0].category == "imports"

    def test_get_issues_by_severity(self):
        """Test getting issues by severity."""
        self.validator.add_issue(
            category="syntax",
            issue_type="syntax_error",
            file_path="test.py",
            message="Error message",
            severity="error"
        )
        
        self.validator.add_issue(
            category="syntax",
            issue_type="syntax_error",
            file_path="test.py",
            message="Warning message",
            severity="warning"
        )
        
        errors = self.validator.get_issues_by_severity("error")
        assert len(errors) == 1
        assert errors[0].severity == SeverityLevel.ERROR
        
        warnings = self.validator.get_issues_by_severity("warning")
        assert len(warnings) == 1
        assert warnings[0].severity == SeverityLevel.WARNING

    def test_generate_json_report(self):
        """Test JSON report generation."""
        # Add some issues
        self.validator.add_issue(
            category="syntax",
            issue_type="SYNTAX_ERROR",
            file_path="test.py",
            message="Test error",
            severity="error"
        )
        
        self.validator.add_issue(
            category="imports",
            issue_type="IMPORT_ERROR",
            file_path="test.py",
            message="Test warning",
            severity="warning"
        )
        
        self.validator.fixes_applied.append("Fixed import issue")
        
        report = self.validator.generate_json_report()
        
        # Check report structure
        assert "meta" in report
        assert "summary" in report
        assert "issues" in report
        assert "fixes_applied" in report
        assert "categories" in report
        
        # Check meta information
        meta = report["meta"]
        assert "timestamp" in meta
        assert meta["validator_version"] == "3.0.0"
        assert "validation_time" in meta
        assert meta["validator_type"] == "BaseValidator"
        
        # Check summary
        summary = report["summary"]
        assert summary["overall_status"] == "FAIL"  # Has errors
        assert summary["total_errors"] == 1
        assert summary["total_warnings"] == 1
        assert summary["fixes_applied"] == 1
        
        # Check issues
        assert len(report["issues"]) == 2
        
        # Check categories
        assert "syntax" in report["categories"]
        assert report["categories"]["syntax"]["error_count"] == 1
        assert report["categories"]["imports"]["warning_count"] == 1

    def test_generate_json_report_no_issues(self):
        """Test JSON report generation with no issues."""
        report = self.validator.generate_json_report()
        
        summary = report["summary"]
        assert summary["overall_status"] == "PASS"
        assert summary["total_errors"] == 0
        assert summary["total_warnings"] == 0

    def test_generate_json_report_warnings_only(self):
        """Test JSON report generation with warnings only."""
        self.validator.add_issue(
            category="imports",
            issue_type="import_error",
            file_path="test.py",
            message="Style warning",
            severity="warning"
        )
        
        report = self.validator.generate_json_report()
        assert report["summary"]["overall_status"] == "WARN"

    @patch('builtins.print')
    def test_print_summary_no_issues(self, mock_print):
        """Test printing summary with no issues."""
        self.validator.print_summary()
        
        # Check that success message was printed
        call_args = [call[0][0] for call in mock_print.call_args_list]
        assert any("✅ All validations passed!" in arg for arg in call_args)

    @patch('builtins.print')
    def test_print_summary_with_issues(self, mock_print):
        """Test printing summary with issues."""
        # Add test issues
        self.validator.add_issue(
            category="syntax",
            issue_type="syntax_error",
            file_path="test.py",
            message="Syntax error",
            severity="error"
        )
        
        self.validator.add_issue(
            category="imports",
            issue_type="import_error",
            file_path="test.py",
            message="Style warning",
            severity="warning"
        )
        
        self.validator.print_summary()
        
        # Check that summary was printed correctly
        call_args = [call[0][0] for call in mock_print.call_args_list]
        summary_text = "\n".join(call_args)
        
        assert "VALIDATION SUMMARY" in summary_text
        assert "Total Issues Found: 2" in summary_text
        assert "Errors: 1" in summary_text
        assert "Warnings: 1" in summary_text
        assert "Status: FAIL" in summary_text
        assert "Syntax: 1 errors, 0 warnings" in summary_text
        assert "Imports: 0 errors, 1 warnings" in summary_text

    def test_results_categories_initialization(self):
        """Test that all expected categories are initialized in results."""
        expected_categories = [
            "syntax", "imports", "dependencies", "structure", "architecture",
            "coverage", "security", "performance", "health", "configuration",
            "build", "documentation", "ai_analysis", "system", "nfr",
            "coding_standards", "type_checking", "formatting", "code_quality",
            "quality_gates", "quality"
        ]
        
        for category in expected_categories:
            assert category in self.validator.results
            assert self.validator.results[category]["status"] == "pass"
            assert self.validator.results[category]["errors"] == []
            assert self.validator.results[category]["warnings"] == []

    def test_timing_measurement(self):
        """Test that validation timing is measured."""
        start_time = self.validator.start_time
        time.sleep(0.01)  # Small delay
        
        report = self.validator.generate_json_report()
        validation_time = report["meta"]["validation_time"]
        
        assert validation_time > 0
        assert validation_time >= 0.01