"""
Tests for auto fixer - Automatic code fixing capabilities.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.infrastructure.tools.validation.core.auto_fixer import AutoFixer
from src.infrastructure.tools.validation.core.issue_model import (
    IssueType,
    SeverityLevel,
    ValidationIssue,
)


class TestAutoFixer:
    """Test cases for AutoFixer class."""
    
    @classmethod
    def setup_class(cls):
        """Set up class-level fixtures to reduce overhead."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.root_path = Path(cls.temp_dir)
        cls.create_test_files()

    def setup_method(self):
        """Set up test fixtures."""
        # Use class-level temp directory and files
        self.temp_dir = self.__class__.temp_dir
        self.root_path = self.__class__.root_path
        self.test_file = self.__class__.test_file
        self.test_file2 = self.__class__.test_file2
        
        # Create a unique empty directory for each test to avoid race conditions
        import uuid
        unique_name = f"empty_directory_{uuid.uuid4().hex[:8]}"
        self.empty_dir = self.root_path / unique_name
        self.empty_dir.mkdir(exist_ok=True)
        
        # Store original file content to restore after tests that modify it
        self._original_test_file_content = self.test_file.read_text()
        
        # Mock tool detection to speed up initialization
        with patch.object(AutoFixer, '_detect_available_tools', return_value={
            "black": True, "ruff": True, "isort": True, "autopep8": True
        }):
            self.auto_fixer = AutoFixer(root_path=self.root_path, create_backup=True)
    
    def teardown_method(self):
        """Clean up after each test."""
        # Restore original file content
        self.test_file.write_text(self._original_test_file_content)
        
        # Clean up the unique empty directory for this test
        if self.empty_dir.exists():
            import shutil
            shutil.rmtree(self.empty_dir, ignore_errors=True)
    
    @classmethod
    def teardown_class(cls):
        """Clean up class-level fixtures."""
        if hasattr(cls, 'temp_dir') and Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    @classmethod
    def create_test_files(cls):
        """Create test files for fixing."""
        # Python file with formatting issues
        cls.test_file = cls.root_path / "test_file.py"
        cls.test_file.write_text(
            """
import os
import sys
import unused_module  # This will be marked as unused

def badly_formatted_function( x,y ):
    return x+y

class   BadlyFormattedClass:
    def method(self):
        pass

# TODO: URGENT - Fix this
print("Hello World")
"""
        )

        # Another test file
        cls.test_file2 = cls.root_path / "another_file.py"
        cls.test_file2.write_text(
            """
# File with import sorting issues
import sys
import os
import ast
from pathlib import Path
from collections import defaultdict
"""
        )

        # Empty directory will be created per-test to avoid race conditions

    def test_initialization(self):
        """Test auto fixer initialization."""
        assert self.auto_fixer.root_path == self.root_path
        assert self.auto_fixer.create_backup is True
        assert self.auto_fixer.fixes_applied == []
        assert isinstance(self.auto_fixer.available_tools, dict)

    def test_initialization_without_backup(self):
        """Test auto fixer initialization without backup."""
        # Mock tool detection to speed up initialization
        with patch.object(AutoFixer, '_detect_available_tools', return_value={
            "black": True, "ruff": True, "isort": True, "autopep8": True
        }):
            fixer = AutoFixer(root_path=self.root_path, create_backup=False)
            assert fixer.create_backup is False

    @patch('subprocess.run')
    def test_detect_available_tools_success(self, mock_run):
        """Test detection of available tools when they exist."""
        # Mock successful tool detection
        mock_run.return_value.returncode = 0

        fixer = AutoFixer(root_path=self.root_path)
        
        # All tools should be detected as available
        assert fixer.available_tools["black"] is True
        assert fixer.available_tools["ruff"] is True
        assert fixer.available_tools["isort"] is True
        assert fixer.available_tools["autopep8"] is True

    @patch('subprocess.run')
    def test_detect_available_tools_failure(self, mock_run):
        """Test detection when tools are not available."""
        # Mock failed tool detection
        mock_run.side_effect = FileNotFoundError()

        fixer = AutoFixer(root_path=self.root_path)
        
        # All tools should be detected as unavailable
        assert fixer.available_tools["black"] is False
        assert fixer.available_tools["ruff"] is False
        assert fixer.available_tools["isort"] is False
        assert fixer.available_tools["autopep8"] is False

    @patch('subprocess.run')
    def test_detect_available_tools_timeout(self, mock_run):
        """Test detection when tools timeout."""
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired("black", 5)

        fixer = AutoFixer(root_path=self.root_path)
        
        # Tools should be detected as unavailable due to timeout
        assert fixer.available_tools["black"] is False

    def test_can_fix_auto_fixable_true(self):
        """Test can_fix with auto_fixable issues."""
        # Code formatting issue
        issue = ValidationIssue(
            category="formatting",
            issue_type=IssueType.CODE_FORMATTING,
            file_path=str(self.test_file),
            message="Code needs formatting",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        # Mock black as available
        self.auto_fixer.available_tools["black"] = True
        assert self.auto_fixer.can_fix(issue) is True

        # Import sorting issue
        issue.issue_type = IssueType.IMPORT_SORTING
        self.auto_fixer.available_tools["isort"] = True
        assert self.auto_fixer.can_fix(issue) is True

        # Unused import (doesn't require external tools)
        issue.issue_type = IssueType.UNUSED_IMPORT
        assert self.auto_fixer.can_fix(issue) is True

    def test_can_fix_auto_fixable_false(self):
        """Test can_fix with non-auto_fixable issues."""
        issue = ValidationIssue(
            category="syntax",
            issue_type=IssueType.SYNTAX_ERROR,
            file_path=str(self.test_file),
            message="Syntax error",
            severity=SeverityLevel.ERROR,
            auto_fixable=False,
        )

        assert self.auto_fixer.can_fix(issue) is False

    def test_can_fix_missing_tools(self):
        """Test can_fix when required tools are missing."""
        issue = ValidationIssue(
            category="formatting",
            issue_type=IssueType.CODE_FORMATTING,
            file_path=str(self.test_file),
            message="Code needs formatting",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        # No formatting tools available
        self.auto_fixer.available_tools["black"] = False
        self.auto_fixer.available_tools["ruff"] = False
        assert self.auto_fixer.can_fix(issue) is False

    def test_can_fix_naming_convention(self):
        """Test can_fix for naming convention issues."""
        issue = ValidationIssue(
            category="naming",
            issue_type=IssueType.FUNCTION_NAMING_CONVENTION,
            file_path=str(self.test_file),
            message="Function name violates convention",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        assert self.auto_fixer.can_fix(issue) is True

    def test_create_backup(self):
        """Test backup creation."""
        backup_path = self.auto_fixer._create_backup(self.test_file)
        
        assert backup_path.exists()
        assert backup_path.name.startswith(f"{self.test_file.name}.backup")
        assert backup_path.read_text() == self.test_file.read_text()

    def test_create_backup_directory_creation(self):
        """Test backup creation with directory creation."""
        # Ensure backup directory doesn't exist initially
        backup_dir = self.root_path / "backup" / "validation_fixes"
        if backup_dir.exists():
            import shutil
            shutil.rmtree(backup_dir.parent)

        backup_path = self.auto_fixer._create_backup(self.test_file)
        
        # Backup directory should be created
        assert backup_dir.exists()
        assert backup_path.exists()

    @patch('subprocess.run')
    def test_apply_code_formatting_with_black(self, mock_run):
        """Test applying code formatting with black."""
        # Mock successful black execution
        mock_run.return_value.returncode = 0
        
        self.auto_fixer.available_tools["black"] = True
        
        issue = ValidationIssue(
            category="formatting",
            issue_type=IssueType.CODE_FORMATTING,
            file_path=str(self.test_file),
            message="Code needs formatting",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        result = self.auto_fixer._apply_code_formatting(issue)
        
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "black" in args

    @patch('subprocess.run')
    def test_apply_code_formatting_with_ruff(self, mock_run):
        """Test applying code formatting with ruff when black unavailable."""
        # Mock successful ruff execution
        mock_run.return_value.returncode = 0
        
        self.auto_fixer.available_tools["black"] = False
        self.auto_fixer.available_tools["ruff"] = True
        
        issue = ValidationIssue(
            category="formatting",
            issue_type=IssueType.CODE_FORMATTING,
            file_path=str(self.test_file),
            message="Code needs formatting",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        result = self.auto_fixer._apply_code_formatting(issue)
        
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "ruff" in args

    @patch('subprocess.run')
    def test_apply_import_sorting(self, mock_run):
        """Test applying import sorting."""
        # Mock successful isort execution
        mock_run.return_value.returncode = 0
        
        self.auto_fixer.available_tools["isort"] = True
        
        issue = ValidationIssue(
            category="imports",
            issue_type=IssueType.IMPORT_SORTING,
            file_path=str(self.test_file2),
            message="Imports need sorting",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        result = self.auto_fixer._apply_import_sorting(issue)
        
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "isort" in args

    def test_remove_unused_import(self):
        """Test removing unused imports."""
        issue = ValidationIssue(
            category="imports",
            issue_type=IssueType.UNUSED_IMPORT,
            file_path=str(self.test_file),
            message="Unused import: unused_module",
            line=4,
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
            offending_line="import unused_module  # This will be marked as unused",
        )

        original_content = self.test_file.read_text()
        result = self.auto_fixer._remove_unused_import(issue)
        new_content = self.test_file.read_text()
        
        assert result is True
        assert "import unused_module" not in new_content
        assert len(new_content.splitlines()) == len(original_content.splitlines()) - 1

    def test_remove_unused_import_no_line_info(self):
        """Test removing unused imports without line information."""
        issue = ValidationIssue(
            category="imports",
            issue_type=IssueType.UNUSED_IMPORT,
            file_path=str(self.test_file),
            message="Unused import: unused_module",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        result = self.auto_fixer._remove_unused_import(issue)
        
        # Should fail without line information
        assert result is False

    def test_remove_empty_directory(self):
        """Test removing empty directories."""
        issue = ValidationIssue(
            category="structure",
            issue_type=IssueType.EMPTY_DIRECTORY,
            file_path=str(self.empty_dir),
            message="Empty directory should be removed",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        assert self.empty_dir.exists()
        result = self.auto_fixer._remove_empty_directory(issue)
        
        assert result is True
        assert not self.empty_dir.exists()

    def test_remove_empty_directory_not_empty(self):
        """Test removing directory that's not empty."""
        # Add a file to the directory
        (self.empty_dir / "not_empty.txt").write_text("content")
        
        issue = ValidationIssue(
            category="structure",
            issue_type=IssueType.EMPTY_DIRECTORY,
            file_path=str(self.empty_dir),
            message="Directory should be removed",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        result = self.auto_fixer._remove_empty_directory(issue)
        
        # Should fail for non-empty directory
        assert result is False
        assert self.empty_dir.exists()

    def test_remove_forbidden_pattern(self):
        """Test removing forbidden patterns."""
        issue = ValidationIssue(
            category="quality",
            issue_type=IssueType.FORBIDDEN_PATTERN,
            file_path=str(self.test_file),
            message="Forbidden pattern: TODO: URGENT",
            line=13,
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
            offending_line="# TODO: URGENT - Fix this",
        )

        original_content = self.test_file.read_text()
        result = self.auto_fixer._remove_forbidden_pattern(issue)
        new_content = self.test_file.read_text()
        
        assert result is True
        assert "TODO: URGENT" not in new_content
        assert len(new_content.splitlines()) == len(original_content.splitlines()) - 1

    def test_fix_naming_convention(self):
        """Test fixing naming convention issues."""
        # Create a file with naming issues
        naming_file = self.root_path / "BadNaming.py"
        naming_file.write_text(
            """
class badClass:
    def BadMethod(self):
        pass

def BadFunction():
    pass
"""
        )

        issue = ValidationIssue(
            category="naming",
            issue_type=IssueType.FUNCTION_NAMING_CONVENTION,
            file_path=str(naming_file),
            message="Function name should be snake_case",
            line=6,
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
            offending_line="def BadFunction():",
            expected_pattern="bad_function",
        )

        result = self.auto_fixer._fix_naming_convention(issue)
        new_content = naming_file.read_text()
        
        assert result is True
        assert "def bad_function():" in new_content
        assert "def BadFunction():" not in new_content

    def test_apply_fix_success(self):
        """Test successful fix application."""
        issue = ValidationIssue(
            category="structure",
            issue_type=IssueType.EMPTY_DIRECTORY,
            file_path=str(self.empty_dir),
            message="Empty directory should be removed",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        result = self.auto_fixer.apply_fix(issue)
        
        assert result is True
        assert len(self.auto_fixer.fixes_applied) == 1
        assert not self.empty_dir.exists()

        # Check fix record
        fix_record = self.auto_fixer.fixes_applied[0]
        assert "issue" in fix_record
        assert "timestamp" in fix_record
        assert "backup_path" in fix_record

    def test_apply_fix_with_backup(self):
        """Test fix application with backup creation."""
        issue = ValidationIssue(
            category="imports",
            issue_type=IssueType.UNUSED_IMPORT,
            file_path=str(self.test_file),
            message="Unused import: unused_module",
            line=4,
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
            offending_line="import unused_module  # This will be marked as unused",
        )

        original_content = self.test_file.read_text()
        result = self.auto_fixer.apply_fix(issue)
        
        assert result is True
        assert len(self.auto_fixer.fixes_applied) == 1

        # Check backup was created
        fix_record = self.auto_fixer.fixes_applied[0]
        backup_path = Path(fix_record["backup_path"])
        assert backup_path.exists()
        assert backup_path.read_text() == original_content

    def test_apply_fix_without_backup(self):
        """Test fix application without backup."""
        # Mock tool detection to speed up initialization
        with patch.object(AutoFixer, '_detect_available_tools', return_value={
            "black": True, "ruff": True, "isort": True, "autopep8": True
        }):
            fixer = AutoFixer(root_path=self.root_path, create_backup=False)
        
        issue = ValidationIssue(
            category="structure",
            issue_type=IssueType.EMPTY_DIRECTORY,
            file_path=str(self.empty_dir),
            message="Empty directory should be removed",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        result = fixer.apply_fix(issue)
        
        assert result is True
        assert len(fixer.fixes_applied) == 1

        # No backup should be created
        fix_record = fixer.fixes_applied[0]
        assert fix_record["backup_path"] is None

    def test_apply_fix_failure(self):
        """Test fix application failure."""
        issue = ValidationIssue(
            category="syntax",
            issue_type=IssueType.SYNTAX_ERROR,
            file_path=str(self.test_file),
            message="Syntax error",
            severity=SeverityLevel.ERROR,
            auto_fixable=False,  # Not auto-fixable
        )

        result = self.auto_fixer.apply_fix(issue)
        
        assert result is False
        assert len(self.auto_fixer.fixes_applied) == 0

    def test_apply_fix_exception_handling(self):
        """Test fix application with exception handling."""
        # Create an issue for a non-existent file
        issue = ValidationIssue(
            category="imports",
            issue_type=IssueType.UNUSED_IMPORT,
            file_path="/non/existent/file.py",
            message="Unused import",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        result = self.auto_fixer.apply_fix(issue)
        
        # Should handle exception gracefully
        assert result is False
        assert len(self.auto_fixer.fixes_applied) == 0

    def test_apply_multiple_fixes(self):
        """Test applying multiple fixes."""
        # Create multiple fixable issues
        issues = [
            ValidationIssue(
                category="structure",
                issue_type=IssueType.EMPTY_DIRECTORY,
                file_path=str(self.empty_dir),
                message="Empty directory",
                severity=SeverityLevel.WARNING,
                auto_fixable=True,
            ),
            ValidationIssue(
                category="imports",
                issue_type=IssueType.UNUSED_IMPORT,
                file_path=str(self.test_file),
                message="Unused import: unused_module",
                line=4,
                severity=SeverityLevel.WARNING,
                auto_fixable=True,
                offending_line="import unused_module  # This will be marked as unused",
            ),
        ]

        success_count = 0
        for issue in issues:
            if self.auto_fixer.apply_fix(issue):
                success_count += 1

        assert success_count == 2
        assert len(self.auto_fixer.fixes_applied) == 2

    def test_get_fixes_summary(self):
        """Test getting summary of applied fixes."""
        # Apply a fix first
        issue = ValidationIssue(
            category="structure",
            issue_type=IssueType.EMPTY_DIRECTORY,
            file_path=str(self.empty_dir),
            message="Empty directory should be removed",
            severity=SeverityLevel.WARNING,
            auto_fixable=True,
        )

        self.auto_fixer.apply_fix(issue)
        
        assert len(self.auto_fixer.fixes_applied) == 1
        fix_record = self.auto_fixer.fixes_applied[0]
        
        # Verify fix record structure
        assert "issue" in fix_record
        assert "timestamp" in fix_record
        assert "backup_path" in fix_record
        assert isinstance(fix_record["issue"], dict)
        assert isinstance(fix_record["timestamp"], str)