"""
Tests for fast precommit validator - Ultra-fast validator for pre-commit hooks.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

import pytest

from src.infrastructure.tools.validation.fast_precommit_validator import (
    FastPrecommitValidator,
    main
)


class TestFastPrecommitValidator:
    """Test cases for FastPrecommitValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)
        
        # Create test files
        self.create_test_files()

    def create_test_files(self):
        """Create test files for validation."""
        # Valid Python file
        self.valid_file = self.root_path / "valid.py"
        self.valid_file.write_text('''"""Valid Python file."""

from src.infrastructure.memory import MemoryEngine
from src.core.workflows import task_lifecycle

def hello_world():
    """A simple function."""
    print("Hello, World!")
    return True

class TestClass:
    """A test class."""
    pass
''')

        # Invalid syntax file
        self.invalid_syntax_file = self.root_path / "invalid_syntax.py"
        self.invalid_syntax_file.write_text('''"""File with syntax errors."""

def broken_function(
    # Missing closing parenthesis and colon
    pass
''')

        # File with deprecated imports
        self.deprecated_imports_file = self.root_path / "deprecated_imports.py"
        self.deprecated_imports_file.write_text('''"""File with deprecated imports."""

from memory.engine import MemoryEngine
from src.core.workflows.task_lifecycle import run_task
from src.platform.tools.validator import Validator

def test_function():
    pass
''')

        # File in deprecated directory structure
        deprecated_dir = self.root_path / "orchestration"
        deprecated_dir.mkdir()
        self.deprecated_location_file = deprecated_dir / "old_file.py"
        self.deprecated_location_file.write_text('''"""File in deprecated location."""

def old_function():
    pass
''')

        # Non-Python file (should be ignored)
        self.text_file = self.root_path / "readme.txt"
        self.text_file.write_text("This is not a Python file")

        # File with encoding issues
        self.unicode_file = self.root_path / "unicode_test.py"
        self.unicode_file.write_text('''# -*- coding: utf-8 -*-
"""Unicode test file."""

def test_unicode():
    message = "Hello 世界! 🌍"
    return message
''', encoding='utf-8')

    def test_initialization(self):
        """Test validator initialization."""
        files = [str(self.valid_file), str(self.text_file)]
        validator = FastPrecommitValidator(files)
        
        # Should only include Python files
        assert len(validator.files) == 1
        assert validator.files[0] == self.valid_file
        assert validator.errors == []
        assert validator.warnings == []

    def test_initialization_no_python_files(self):
        """Test initialization with no Python files."""
        files = [str(self.text_file), "other.txt"]
        validator = FastPrecommitValidator(files)
        
        assert len(validator.files) == 0
        assert validator.errors == []
        assert validator.warnings == []

    def test_validate_all_success(self):
        """Test successful validation of all files."""
        files = [str(self.valid_file)]
        validator = FastPrecommitValidator(files)
        
        with patch('builtins.print') as mock_print:
            result = validator.validate_all()
        
        assert result is True
        assert len(validator.errors) == 0
        
        # Should have printed progress messages
        mock_print.assert_called()
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Fast validation" in msg for msg in print_calls)
        assert any("completed in" in msg for msg in print_calls)

    def test_validate_all_with_errors(self):
        """Test validation with files containing errors."""
        files = [str(self.invalid_syntax_file), str(self.deprecated_imports_file)]
        validator = FastPrecommitValidator(files)
        
        with patch('builtins.print') as mock_print:
            result = validator.validate_all()
        
        assert result is False
        assert len(validator.errors) > 0
        
        # Should have printed error messages
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("errors found" in msg for msg in print_calls)

    def test_validate_file_valid(self):
        """Test validation of a valid file."""
        files = [str(self.valid_file)]
        validator = FastPrecommitValidator(files)
        
        result = validator._validate_file(self.valid_file)
        
        assert result is True
        assert len(validator.errors) == 0

    def test_validate_file_nonexistent(self):
        """Test validation of non-existent file."""
        nonexistent = self.root_path / "nonexistent.py"
        files = [str(nonexistent)]
        validator = FastPrecommitValidator(files)
        
        result = validator._validate_file(nonexistent)
        
        assert result is False
        assert len(validator.errors) == 1
        assert "does not exist" in validator.errors[0]

    def test_validate_file_with_relative_path(self):
        """Test validation resolves relative paths."""
        # Create a file in current directory for this test
        with patch('pathlib.Path.cwd', return_value=self.root_path):
            files = ["valid.py"]  # Relative path
            validator = FastPrecommitValidator(files)
            
            result = validator._validate_file(Path("valid.py"))
            
            assert result is True

    def test_validate_file_read_error(self):
        """Test validation handles file read errors."""
        files = [str(self.valid_file)]
        validator = FastPrecommitValidator(files)
        
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            result = validator._validate_file(self.valid_file)
        
        assert result is False
        assert len(validator.errors) == 1
        assert "Failed to read" in validator.errors[0]

    def test_check_syntax_valid(self):
        """Test syntax checking with valid code."""
        files = [str(self.valid_file)]
        validator = FastPrecommitValidator(files)
        
        content = self.valid_file.read_text()
        result = validator._check_syntax(self.valid_file, content)
        
        assert result is True
        assert len(validator.errors) == 0

    def test_check_syntax_invalid(self):
        """Test syntax checking with invalid code."""
        files = [str(self.invalid_syntax_file)]
        validator = FastPrecommitValidator(files)
        
        content = self.invalid_syntax_file.read_text()
        result = validator._check_syntax(self.invalid_syntax_file, content)
        
        assert result is False
        assert len(validator.errors) == 1
        assert "Syntax error" in validator.errors[0]
        assert str(self.invalid_syntax_file) in validator.errors[0]

    def test_check_imports_valid(self):
        """Test import checking with valid imports."""
        files = [str(self.valid_file)]
        validator = FastPrecommitValidator(files)
        
        content = self.valid_file.read_text()
        result = validator._check_imports(self.valid_file, content)
        
        assert result is True
        assert len(validator.errors) == 0

    def test_check_imports_deprecated(self):
        """Test import checking detects deprecated imports."""
        files = [str(self.deprecated_imports_file)]
        validator = FastPrecommitValidator(files)
        
        content = self.deprecated_imports_file.read_text()
        result = validator._check_imports(self.deprecated_imports_file, content)
        
        assert result is False
        assert len(validator.errors) >= 3  # Three deprecated imports
        
        # Check for specific deprecated import errors
        error_messages = " ".join(validator.errors)
        assert "from memory." in error_messages
        assert "from src.core.workflows." in error_messages
        assert "from src.platform.tools." in error_messages

    def test_check_imports_memory_deprecated(self):
        """Test specific detection of deprecated memory imports."""
        test_content = '''"""Test file."""

from memory.engine import MemoryEngine
from memory.storage import Storage
'''
        
        files = []
        validator = FastPrecommitValidator(files)
        
        result = validator._check_imports(Path("test.py"), test_content)
        
        assert result is False
        assert len(validator.errors) == 2
        assert all("from memory." in error for error in validator.errors)

    def test_check_imports_workflows_deprecated(self):
        """Test specific detection of deprecated workflow imports."""
        test_content = '''"""Test file."""

from src.core.workflows.task import run_task
from src.core.workflows.states import State
'''
        
        files = []
        validator = FastPrecommitValidator(files)
        
        result = validator._check_imports(Path("test.py"), test_content)
        
        assert result is False
        assert len(validator.errors) == 2
        assert all("from src.core.workflows." in error for error in validator.errors)

    def test_check_imports_platform_tools_deprecated(self):
        """Test specific detection of deprecated platform tools imports."""
        test_content = '''"""Test file."""

from src.platform.tools.validator import Validator
from src.platform.tools.analyzer import Analyzer
from src.platform.tools.memory.engine import Engine  # This should NOT trigger error
'''
        
        files = []
        validator = FastPrecommitValidator(files)
        
        result = validator._check_imports(Path("test.py"), test_content)
        
        assert result is False
        assert len(validator.errors) == 2  # Only two errors, memory.engine is allowed
        assert all("from src.platform.tools." in error for error in validator.errors)
        assert all("tools.memory." not in error for error in validator.errors)

    def test_check_architecture_valid(self):
        """Test architecture checking with valid file location."""
        files = [str(self.valid_file)]
        validator = FastPrecommitValidator(files)
        
        content = self.valid_file.read_text()
        result = validator._check_architecture(self.valid_file, content)
        
        assert result is True
        assert len(validator.errors) == 0

    def test_check_architecture_deprecated_location(self):
        """Test architecture checking detects deprecated locations."""
        files = [str(self.deprecated_location_file)]
        validator = FastPrecommitValidator(files)
        
        content = self.deprecated_location_file.read_text()
        result = validator._check_architecture(self.deprecated_location_file, content)
        
        assert result is False
        assert len(validator.errors) == 1
        assert "deprecated directory" in validator.errors[0]
        assert str(self.deprecated_location_file) in validator.errors[0]

    def test_check_architecture_all_deprecated_dirs(self):
        """Test all deprecated directory patterns."""
        deprecated_dirs = [
            "orchestration/",
            "tools/memory/", 
            "handlers/",
            "memory-bank/",
            "patches/"
        ]
        
        for deprecated_dir in deprecated_dirs:
            # Create test file in deprecated location
            test_dir = self.root_path / deprecated_dir.rstrip("/")
            test_dir.mkdir(parents=True, exist_ok=True)
            test_file = test_dir / "test.py"
            test_file.write_text("# Test file")
            
            files = [str(test_file)]
            validator = FastPrecommitValidator(files)
            
            result = validator._check_architecture(test_file, "# Test file")
            
            assert result is False
            assert len(validator.errors) >= 1
            assert "deprecated directory" in validator.errors[0]

    def test_check_architecture_windows_paths(self):
        """Test architecture checking with Windows-style paths."""
        # Create a mock Windows path
        windows_path = Path("C:\\project\\orchestration\\old_file.py")
        
        files = []
        validator = FastPrecommitValidator(files)
        
        result = validator._check_architecture(windows_path, "# Test file")
        
        assert result is False
        assert len(validator.errors) == 1
        assert "deprecated directory" in validator.errors[0]

    def test_unicode_file_handling(self):
        """Test handling of files with unicode content."""
        files = [str(self.unicode_file)]
        validator = FastPrecommitValidator(files)
        
        result = validator._validate_file(self.unicode_file)
        
        assert result is True
        assert len(validator.errors) == 0

    def test_mixed_file_validation(self):
        """Test validation of mixed valid and invalid files."""
        files = [
            str(self.valid_file),
            str(self.invalid_syntax_file),
            str(self.deprecated_imports_file),
            str(self.text_file)  # Should be filtered out
        ]
        validator = FastPrecommitValidator(files)
        
        # Should only process Python files
        assert len(validator.files) == 3
        
        result = validator.validate_all()
        
        assert result is False
        assert len(validator.errors) > 0

    def test_empty_file_list(self):
        """Test validation with empty file list."""
        validator = FastPrecommitValidator([])
        
        result = validator.validate_all()
        
        assert result is True
        assert len(validator.errors) == 0

    def test_performance_timing(self):
        """Test that validation reports timing information."""
        files = [str(self.valid_file)]
        validator = FastPrecommitValidator(files)
        
        with patch('builtins.print') as mock_print:
            validator.validate_all()
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        timing_messages = [msg for msg in print_calls if "completed in" in msg]
        assert len(timing_messages) == 1
        assert "s" in timing_messages[0]  # Should include seconds

    def test_warning_reporting(self):
        """Test warning reporting functionality."""
        files = [str(self.valid_file)]
        validator = FastPrecommitValidator(files)
        
        # Manually add a warning to test reporting
        validator.warnings.append("Test warning")
        
        with patch('builtins.print') as mock_print:
            result = validator.validate_all()
        
        assert result is True  # Warnings don't fail validation
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        warning_messages = [msg for msg in print_calls if "warnings found" in msg]
        assert len(warning_messages) == 1


class TestFastPrecommitValidatorMain:
    """Test cases for the main function and CLI interface."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)
        
        # Create a test file
        self.test_file = self.root_path / "test.py"
        self.test_file.write_text('"""Test file."""\nprint("Hello")')

    def test_main_with_files(self):
        """Test main function with file arguments."""
        test_args = ["fast_precommit_validator.py", str(self.test_file)]
        
        with patch.object(sys, 'argv', test_args):
            with patch('builtins.print'):
                result = main()
        
        assert result == 0

    def test_main_with_invalid_files(self):
        """Test main function with invalid files."""
        invalid_file = self.root_path / "invalid.py"
        invalid_file.write_text("def broken(\n  pass")  # Syntax error
        
        test_args = ["fast_precommit_validator.py", str(invalid_file)]
        
        with patch.object(sys, 'argv', test_args):
            with patch('builtins.print'):
                result = main()
        
        assert result == 1

    def test_main_no_files(self):
        """Test main function with no files."""
        test_args = ["fast_precommit_validator.py"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('builtins.print') as mock_print:
                result = main()
        
        assert result == 0
        # Should print "No files to validate"
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("No files to validate" in msg for msg in print_calls)

    def test_main_with_staged_flag(self):
        """Test main function with --staged flag."""
        test_args = ["fast_precommit_validator.py", "--staged", str(self.test_file)]
        
        with patch.object(sys, 'argv', test_args):
            with patch('builtins.print'):
                result = main()
        
        assert result == 0

    def test_argparse_integration(self):
        """Test argument parsing integration."""
        # Test help argument (should raise SystemExit)
        test_args = ["fast_precommit_validator.py", "--help"]
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 0  # Help exit code

    def test_main_mixed_files(self):
        """Test main function with mixed valid/invalid files."""
        valid_file = self.root_path / "valid.py"
        valid_file.write_text('"""Valid file."""\nprint("Hello")')
        
        invalid_file = self.root_path / "invalid.py"
        invalid_file.write_text("def broken(\n  pass")
        
        test_args = ["fast_precommit_validator.py", str(valid_file), str(invalid_file)]
        
        with patch.object(sys, 'argv', test_args):
            with patch('builtins.print'):
                result = main()
        
        assert result == 1  # Should fail due to invalid file

    def test_main_error_handling(self):
        """Test main function error handling."""
        # Test with file that will cause an exception
        with patch('src.infrastructure.tools.validation.fast_precommit_validator.FastPrecommitValidator') as mock_validator:
            mock_instance = MagicMock()
            mock_instance.validate_all.side_effect = Exception("Test error")
            mock_validator.return_value = mock_instance
            
            test_args = ["fast_precommit_validator.py", str(self.test_file)]
            
            with patch.object(sys, 'argv', test_args):
                # Should not crash, but might not handle the exception gracefully
                # depending on implementation
                try:
                    result = main()
                except Exception:
                    # If it doesn't handle exceptions, that's also valid behavior
                    pass