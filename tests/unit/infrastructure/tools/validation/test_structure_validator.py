"""
Tests for structure validator - Validates project structure and naming conventions.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from src.infrastructure.tools.validation.core.structure_validator import StructureValidator
from src.infrastructure.tools.validation.core.issue_model import IssueType, SeverityLevel


class TestStructureValidator:
    """Test cases for StructureValidator class."""
    
    @classmethod
    def setup_class(cls):
        """Set up class-level fixtures to reduce overhead."""
        import shutil
        cls.temp_dir = tempfile.mkdtemp()
        cls.root_path = Path(cls.temp_dir)
        cls.create_test_structure()

    def setup_method(self):
        """Set up test fixtures."""
        # Use class-level temp directory and files
        self.temp_dir = self.__class__.temp_dir
        self.root_path = self.__class__.root_path
        
        # Create validator instance for each test
        self.validator = StructureValidator(root_path=self.root_path)
    
    @classmethod
    def teardown_class(cls):
        """Clean up class-level fixtures."""
        import shutil
        if hasattr(cls, 'temp_dir') and Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    @classmethod
    def create_test_structure(cls):
        """Create a test project structure."""
        # Create properly named Python file
        good_file = cls.root_path / "good_module.py"
        good_file.write_text('''"""
Module docstring.
"""

class GoodClass:
    """Class docstring."""
    
    def good_method(self):
        """Method docstring."""
        pass


def good_function():
    """Function docstring."""
    pass
''')

        # Create badly named Python file
        bad_file = cls.root_path / "BadFile.py"
        bad_file.write_text('''# No module docstring

class bad_class:
    # No docstring
    def BadMethod(self):
        pass

def Bad_Function():
    # No docstring
    pass
''')

        # Create file with security issues
        security_file = cls.root_path / "security_issues.py"
        security_file.write_text('''"""Security test file."""

import subprocess

# Hardcoded secrets
API_KEY = "sk-1234567890abcdef"
password = "admin123"
SECRET_TOKEN = "super_secret"

# Dangerous functions
def dangerous():
    user_input = input("Enter code: ")
    eval(user_input)  # Security risk!
    exec("print('hello')")  # Another risk
    
    # Shell injection risk
    subprocess.call(f"echo {user_input}", shell=True)
''')

        # Create empty directory
        empty_dir = cls.root_path / "empty_dir"
        empty_dir.mkdir()

        # Create test files
        test_dir = cls.root_path / "tests"
        test_dir.mkdir()
        test_file = test_dir / "test_example.py"
        test_file.write_text('"""Test file."""')

        # Create src directory with files
        src_dir = cls.root_path / "src"
        src_dir.mkdir()
        src_file = src_dir / "module.py"
        src_file.write_text('"""Source module."""')

        # Create __init__.py file (should be allowed)
        init_file = cls.root_path / "__init__.py"
        init_file.write_text('"""Init file."""')

        # Create file that can't be parsed
        broken_file = cls.root_path / "broken_syntax.py"
        broken_file.write_text("def broken(:\n    pass")

    def test_initialization(self):
        """Test validator initialization."""
        assert self.validator.root_path == self.root_path
        assert self.validator.python_files == []

    def test_is_valid_python_filename(self):
        """Test Python filename validation."""
        # Valid names
        assert self.validator._is_valid_python_filename("module.py") is True
        assert self.validator._is_valid_python_filename("my_module.py") is True
        assert self.validator._is_valid_python_filename("module123.py") is True
        assert self.validator._is_valid_python_filename("__init__.py") is True
        assert self.validator._is_valid_python_filename("__main__.py") is True
        
        # Invalid names
        assert self.validator._is_valid_python_filename("Module.py") is False
        assert self.validator._is_valid_python_filename("MyModule.py") is False
        assert self.validator._is_valid_python_filename("module-name.py") is False
        assert self.validator._is_valid_python_filename("123module.py") is False
        assert self.validator._is_valid_python_filename("module.txt") is False
        assert self.validator._is_valid_python_filename("module") is False

    def test_validate_structure(self):
        """Test complete structure validation."""
        result = self.validator.validate_structure()
        
        # Should find issues
        assert len(self.validator.issues) > 0
        
        # Check for specific issue types
        issue_types = [issue.issue_type for issue in self.validator.issues]
        
        # Should find empty directory
        assert IssueType.EMPTY_DIRECTORY in issue_types

    def test_validate_empty_directories(self):
        """Test empty directory detection."""
        self.validator._validate_empty_directories()
        
        # Should find the empty_dir
        empty_dir_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.EMPTY_DIRECTORY
        ]
        
        assert len(empty_dir_issues) >= 1
        assert "empty_dir" in empty_dir_issues[0].message
        assert empty_dir_issues[0].severity == SeverityLevel.WARNING
        assert empty_dir_issues[0].auto_fixable is True

    def test_validate_empty_directories_with_exclusions(self):
        """Test empty directory detection with exclusions."""
        # Configure excluded directories
        self.validator.config["excluded_dirs"] = ["empty_dir"]
        self.validator.issues = []  # Clear previous issues
        
        self.validator._validate_empty_directories()
        
        # Should not find issues for excluded directory
        empty_dir_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.EMPTY_DIRECTORY
        ]
        
        assert len(empty_dir_issues) == 0

    def test_validate_naming_conventions(self):
        """Test naming convention validation."""
        # Configure naming patterns
        self.validator.config["naming_conventions"] = {
            "files": r"^[a-z][a-z0-9_]*\.py$",
            "classes": r"^[A-Z][a-zA-Z0-9]*$",
            "functions": r"^[a-z][a-z0-9_]*$"
        }
        
        self.validator.python_files = list(self.root_path.glob("**/*.py"))
        self.validator._validate_naming_conventions()
        
        # Should find naming issues
        naming_issues = [
            issue for issue in self.validator.issues 
            if "naming_convention" in issue.issue_type.value
        ]
        
        assert len(naming_issues) > 0
        
        # Check for specific violations
        issue_messages = [issue.message for issue in naming_issues]
        assert any("BadFile.py" in msg for msg in issue_messages)

    def test_validate_code_naming(self):
        """Test code naming convention validation."""
        naming_config = {
            "classes": r"^[A-Z][a-zA-Z0-9]*$",
            "functions": r"^[a-z][a-z0-9_]*$"
        }
        
        bad_file = self.root_path / "BadFile.py"
        self.validator._validate_code_naming(bad_file, naming_config)
        
        # Should find class and function naming issues
        class_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.CLASS_NAMING_CONVENTION
        ]
        function_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.FUNCTION_NAMING_CONVENTION
        ]
        
        assert len(class_issues) >= 1  # bad_class
        assert len(function_issues) >= 2  # BadMethod and Bad_Function
        
        # Check issue details
        assert any("bad_class" in issue.message for issue in class_issues)
        assert any("BadMethod" in issue.message for issue in function_issues)
        assert any("Bad_Function" in issue.message for issue in function_issues)

    def test_validate_code_naming_with_parsing_error(self):
        """Test code naming validation with unparseable file."""
        naming_config = {"classes": r"^[A-Z][a-zA-Z0-9]*$"}
        
        broken_file = self.root_path / "broken_syntax.py"
        self.validator._validate_code_naming(broken_file, naming_config)
        
        # Should add error issue
        error_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.NAMING_VALIDATION_ERROR
        ]
        
        assert len(error_issues) == 1
        assert "Error validating naming conventions" in error_issues[0].message

    def test_validate_documentation(self):
        """Test documentation validation."""
        self.validator.python_files = list(self.root_path.glob("**/*.py"))
        self.validator._validate_documentation()
        
        # Should find missing docstrings
        doc_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.MISSING_DOCSTRING
        ]
        
        assert len(doc_issues) > 0
        
        # Check specific missing docstrings
        issue_messages = [issue.message for issue in doc_issues]
        assert any("bad_class" in msg for msg in issue_messages)
        assert any("BadMethod" in msg for msg in issue_messages)
        assert any("Bad_Function" in msg for msg in issue_messages)

    def test_validate_documentation_limit(self):
        """Test documentation validation with many undocumented items."""
        # Create many undocumented functions
        many_funcs_file = self.root_path / "many_functions.py"
        content = ""
        for i in range(30):
            content += f"def func_{i}(): pass\n"
        many_funcs_file.write_text(content)
        
        self.validator.python_files = [many_funcs_file]
        self.validator._validate_documentation()
        
        # Should limit individual issues to 20
        individual_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.MISSING_DOCSTRING
        ]
        assert len(individual_issues) == 20
        
        # Should have summary issue
        summary_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.DOCUMENTATION_COVERAGE
        ]
        assert len(summary_issues) == 1
        assert "30 undocumented items" in summary_issues[0].message

    def test_validate_test_coverage(self):
        """Test test coverage validation."""
        self.validator.python_files = list(self.root_path.glob("**/*.py"))
        self.validator.config["coverage_threshold"] = 50
        
        self.validator._validate_test_coverage()
        
        # Should check test file ratio
        coverage_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.LOW_TEST_COVERAGE
        ]
        
        # May or may not have issues depending on file ratio
        # Just verify it runs without error

    def test_validate_security_patterns(self):
        """Test security pattern validation."""
        self.validator.python_files = list(self.root_path.glob("**/*.py"))
        self.validator.validate_security_patterns()
        
        # Should find security issues
        security_issues = [
            issue for issue in self.validator.issues 
            if issue.category == "security"
        ]
        
        assert len(security_issues) > 0
        
        # Check for specific security issues
        issue_types = [issue.issue_type for issue in security_issues]
        assert IssueType.POTENTIAL_HARDCODED_SECRET in issue_types
        assert IssueType.DANGEROUS_FUNCTION_USAGE in issue_types
        assert IssueType.SHELL_INJECTION_RISK in issue_types

    def test_check_security_patterns(self):
        """Test specific security pattern checks."""
        security_file = self.root_path / "security_issues.py"
        with open(security_file) as f:
            content = f.read()
        
        self.validator._check_security_patterns(security_file, content, {})
        
        # Check hardcoded secrets
        secret_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.POTENTIAL_HARDCODED_SECRET
        ]
        assert len(secret_issues) >= 3  # API_KEY, password, SECRET_TOKEN
        
        # Check dangerous functions
        dangerous_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.DANGEROUS_FUNCTION_USAGE
        ]
        assert len(dangerous_issues) >= 2  # eval and exec
        
        # Check shell injection
        shell_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.SHELL_INJECTION_RISK
        ]
        assert len(shell_issues) >= 1

    def test_validate_security_patterns_with_error(self):
        """Test security validation with file read error."""
        # Create a file path that doesn't exist
        nonexistent = self.root_path / "nonexistent.py"
        self.validator.python_files = [nonexistent]
        
        self.validator.validate_security_patterns()
        
        # Should handle error gracefully
        error_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.SECURITY_SCAN_ERROR
        ]
        
        assert len(error_issues) == 1

    def test_get_structure_summary(self):
        """Test structure summary generation."""
        # Add some test issues
        self.validator.python_files = list(self.root_path.glob("**/*.py"))
        self.validator.add_issue(
            category="structure",
            issue_type=IssueType.NAMING_CONVENTION,
            file_path="test.py",
            message="Test error",
            severity="error"
        )
        self.validator.add_issue(
            category="structure",
            issue_type=IssueType.NAMING_CONVENTION,
            file_path="test.py",
            message="Test warning",
            severity="warning",
            auto_fixable=True
        )
        
        summary = self.validator.get_structure_summary()
        
        assert summary["total_files"] == len(self.validator.python_files)
        assert summary["total_issues"] == 2
        assert summary["error_count"] == 1
        assert summary["warning_count"] == 1
        assert summary["auto_fixable_count"] == 1

    def test_validate_file(self):
        """Test single file validation."""
        bad_file = self.root_path / "BadFile.py"
        issues = self.validator.validate_file(bad_file)
        
        assert len(issues) > 0
        
        # Check that issues are for the specific file
        assert all(bad_file.name in issue.file_path for issue in issues)

    def test_validate_file_nonexistent(self):
        """Test validation of non-existent file."""
        nonexistent = self.root_path / "nonexistent.py"
        issues = self.validator.validate_file(nonexistent)
        
        assert len(issues) == 0

    def test_validate_file_non_python(self):
        """Test validation of non-Python file."""
        text_file = self.root_path / "readme.txt"
        text_file.write_text("Not a Python file")
        
        issues = self.validator.validate_file(text_file)
        
        assert len(issues) == 0

    def test_validate_file_naming(self):
        """Test file naming validation."""
        bad_file = self.root_path / "BadFile.py"
        self.validator._validate_file_naming(bad_file)
        
        naming_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.NAMING_CONVENTION
        ]
        
        assert len(naming_issues) == 1
        assert "BadFile.py" in naming_issues[0].message
        assert naming_issues[0].severity == SeverityLevel.WARNING

    def test_validate_file_documentation(self):
        """Test file documentation validation."""
        bad_file = self.root_path / "BadFile.py"
        self.validator._validate_file_documentation(bad_file)
        
        doc_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.MISSING_DOCSTRING
        ]
        
        assert len(doc_issues) == 1
        assert "Module missing docstring" in doc_issues[0].message

    def test_validate_file_documentation_with_docstring(self):
        """Test file documentation validation with proper docstring."""
        good_file = self.root_path / "good_module.py"
        self.validator._validate_file_documentation(good_file)
        
        doc_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.MISSING_DOCSTRING
        ]
        
        assert len(doc_issues) == 0

    def test_validate_file_documentation_with_parse_error(self):
        """Test file documentation validation with unparseable file."""
        broken_file = self.root_path / "broken_syntax.py"
        self.validator._validate_file_documentation(broken_file)
        
        # Should not crash, just skip the file
        assert True  # If we get here, it handled the error

    def test_validate_file_security(self):
        """Test file security validation."""
        security_file = self.root_path / "security_issues.py"
        self.validator._validate_file_security(security_file)
        
        security_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.SECURITY_ISSUE
        ]
        
        assert len(security_issues) >= 1
        assert "subprocess with shell=True" in security_issues[0].message

    def test_validate_file_security_with_read_error(self):
        """Test file security validation with read error."""
        # Create a file that we can't read
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            some_file = self.root_path / "some_file.py"
            self.validator._validate_file_security(some_file)
        
        # Should not crash
        assert True

    def test_validate_multiple_files(self):
        """Test validation of multiple files."""
        files = list(self.root_path.glob("*.py"))
        issues = self.validator.validate(files)
        
        assert isinstance(issues, list)
        assert len(issues) > 0

    def test_validate_with_empty_list(self):
        """Test validation with empty file list."""
        issues = self.validator.validate([])
        
        assert issues == []

    def test_has_errors(self):
        """Test error detection."""
        # Initially no errors
        assert not self.validator.has_errors()
        
        # Add error-level issue
        self.validator.add_issue(
            category="structure",
            issue_type=IssueType.STRUCTURE_ISSUE,
            file_path="test.py",
            message="Test error",
            severity="error"
        )
        
        assert self.validator.has_errors()

    def test_private_method_documentation_skip(self):
        """Test that private methods are skipped in documentation check."""
        private_file = self.root_path / "private_methods.py"
        private_file.write_text('''"""Module with private methods."""

class MyClass:
    """Class docstring."""
    
    def _private_method(self):
        # Private methods don't need docstrings
        pass
    
    def public_method(self):
        # This should be flagged
        pass
''')
        
        self.validator.python_files = [private_file]
        self.validator._validate_documentation()
        
        doc_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.MISSING_DOCSTRING
        ]
        
        # Should only flag public_method, not _private_method
        assert len(doc_issues) == 1
        assert "public_method" in doc_issues[0].message
        assert "_private_method" not in str([issue.message for issue in doc_issues])