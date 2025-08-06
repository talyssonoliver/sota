"""
Tests for syntax validator - Validates Python syntax and import statements.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import concurrent.futures
import time


from src.infrastructure.tools.validation.core.syntax_validator import SyntaxValidator
from src.infrastructure.tools.validation.core.issue_model import IssueType, SeverityLevel


class TestSyntaxValidator:
    """Test cases for SyntaxValidator class."""
    
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
        
        # Create validator instance for each test
        self.validator = SyntaxValidator(root_path=self.root_path)
    
    @classmethod
    def teardown_class(cls):
        """Clean up class-level fixtures."""
        import shutil
        if hasattr(cls, 'temp_dir') and Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    @classmethod
    def create_test_files(cls):
        """Create test files for syntax validation."""
        # Valid Python file
        valid_file = cls.root_path / "valid_syntax.py"
        valid_file.write_text('''"""Valid Python file."""

import os
import sys
from pathlib import Path
from collections import defaultdict

def hello_world():
    """A simple function."""
    print("Hello, World!")
    return True

class TestClass:
    """A test class."""
    
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
''')

        # Invalid syntax file
        invalid_file = cls.root_path / "invalid_syntax.py"
        invalid_file.write_text('''"""File with syntax errors."""

def broken_function(
    # Missing closing parenthesis and colon
    pass

# Missing colon
if True
    print("This will fail")

# Indentation error
def another_function():
print("Broken indentation")
''')

        # File with import errors
        import_file = cls.root_path / "import_test.py"
        import_file.write_text('''"""File with various imports."""

import os
import sys
from pathlib import Path
from nonexistent_module import something
import /invalid/import
from . import relative_import
from ..parent import parent_import

# Import in try/except block
try:
    import optional_package
    from optional_package import optional_function
except ImportError:
    optional_package = None
    optional_function = None

def test_function():
    return True
''')

        # File with problematic import names
        bad_imports_file = cls.root_path / "bad_imports.py"
        bad_imports_file.write_text('''"""File with invalid import names."""

# These should be caught as invalid
# import ""  # Empty import (commented out due to syntax error)
# import "quoted string"  # Invalid import (commented out)

def dummy():
    pass
''')

        # Unicode/encoding test file
        unicode_file = cls.root_path / "unicode_test.py"
        unicode_file.write_text('''# -*- coding: utf-8 -*-
"""Unicode test file."""

def test_unicode():
    message = "Hello 世界! 🌍"
    return message

# Some unicode identifiers (if allowed by Python version)
def test_함수():
    return "Korean function name"
''', encoding='utf-8')

        # Large file for performance testing
        large_file = cls.root_path / "large_file.py"
        content = '"""Large file for performance testing."""\n\n'
        for i in range(1000):
            content += f'def function_{i}():\n    """Function {i}."""\n    return {i}\n\n'
        large_file.write_text(content)

        # File that causes parse errors (but not syntax errors)
        parse_error_file = cls.root_path / "parse_error.py"
        # Create a file that might cause AST parsing issues
        parse_error_file.write_text('''"""File that might cause parse errors."""

# This is syntactically valid but might cause issues during processing
import sys
sys.setrecursionlimit(1)  # Very low recursion limit

# Some complex nested structures
deeply_nested = [[[[[[[[[[[[[[[["deep"]]]]]]]]]]]]]]]

def complex_function():
    """Function with complex structure."""
    try:
        with open("test") as f:
            for line in f:
                if line.strip():
                    for char in line:
                        if char.isalpha():
                            for i in range(ord(char)):
                                yield i
    except Exception as e:
        raise RuntimeError("Complex error") from e

    return True
''')

    def test_initialization(self):
        """Test validator initialization."""
        assert self.validator.root_path == self.root_path
        assert self.validator.syntax_errors == []
        assert self.validator.handled_imports == set()

    def test_validate_syntax_valid_file(self):
        """Test syntax validation with valid file."""
        valid_file = self.root_path / "valid_syntax.py"
        result = self.validator.validate_syntax(valid_file)
        
        assert result is True
        assert len(self.validator.syntax_errors) == 0

    def test_validate_syntax_invalid_file(self):
        """Test syntax validation with invalid file."""
        invalid_file = self.root_path / "invalid_syntax.py"
        result = self.validator.validate_syntax(invalid_file)
        
        assert result is False
        assert len(self.validator.syntax_errors) > 0
        
        # Check that syntax error issues were added
        syntax_error_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.SYNTAX_ERROR
        ]
        assert len(syntax_error_issues) > 0
        assert syntax_error_issues[0].severity == SeverityLevel.ERROR

    def test_validate_syntax_nonexistent_file(self):
        """Test syntax validation with non-existent file."""
        nonexistent = self.root_path / "nonexistent.py"
        result = self.validator.validate_syntax(nonexistent)
        
        assert result is False
        assert len(self.validator.syntax_errors) > 0

    def test_validate_syntax_unicode_file(self):
        """Test syntax validation with unicode content."""
        unicode_file = self.root_path / "unicode_test.py"
        result = self.validator.validate_syntax(unicode_file)
        
        assert result is True

    def test_extract_imports_valid_file(self):
        """Test import extraction from valid file."""
        import_file = self.root_path / "import_test.py"
        imports = self.validator.extract_imports(import_file)
        
        assert isinstance(imports, list)
        assert len(imports) > 0
        
        # Check for expected imports
        assert "os" in imports
        assert "sys" in imports
        assert "pathlib" in imports
        assert "nonexistent_module" in imports
        
        # Check for relative imports (should have dot prefix)
        relative_imports = [imp for imp in imports if imp.startswith(".")]
        assert len(relative_imports) >= 2  # relative_import and parent_import

    def test_extract_imports_with_try_except(self):
        """Test import extraction identifies try/except wrapped imports."""
        import_file = self.root_path / "import_test.py"
        imports = self.validator.extract_imports(import_file)
        
        # Should identify optional_package as handled import
        assert "optional_package" in self.validator.handled_imports

    def test_extract_imports_with_error(self):
        """Test import extraction with file that causes parsing errors."""
        invalid_file = self.root_path / "invalid_syntax.py"
        imports = self.validator.extract_imports(invalid_file)
        
        # Should return empty list and add error issue
        assert imports == []
        
        extraction_errors = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.IMPORT_EXTRACTION_ERROR
        ]
        assert len(extraction_errors) > 0

    def test_validate_import_valid_names(self):
        """Test import validation with valid import names."""
        test_file = self.root_path / "test.py"
        
        # Valid imports
        assert self.validator.validate_import("os", test_file) is True
        assert self.validator.validate_import("sys", test_file) is True
        assert self.validator.validate_import("collections.defaultdict", test_file) is True
        assert self.validator.validate_import("my_module", test_file) is True

    def test_validate_import_relative_imports(self):
        """Test import validation with relative imports."""
        test_file = self.root_path / "test.py"
        
        # Relative imports should be valid
        assert self.validator.validate_import(".relative", test_file) is True
        assert self.validator.validate_import("..parent", test_file) is True

    def test_validate_import_invalid_names(self):
        """Test import validation with invalid import names."""
        test_file = self.root_path / "test.py"
        
        # Empty or whitespace-only names
        assert self.validator.validate_import("", test_file) is False
        assert self.validator.validate_import("   ", test_file) is False
        
        # Invalid characters
        assert self.validator.validate_import("module/with/slashes", test_file) is False
        assert self.validator.validate_import("module\\with\\backslashes", test_file) is False
        assert self.validator.validate_import("module:with:colons", test_file) is False
        assert self.validator.validate_import('module"with"quotes', test_file) is False

    def test_validate_import_optional_dependency(self):
        """Test import validation identifies optional dependencies."""
        test_file = self.root_path / "test.py"
        
        # Mark an import as handled (optional)
        self.validator.handled_imports.add("optional_package")
        
        result = self.validator.validate_import("optional_package", test_file)
        assert result is True
        
        # Should add info issue about optional dependency
        optional_issues = [
            issue for issue in self.validator.issues 
            if issue.issue_type == IssueType.OPTIONAL_DEPENDENCY
        ]
        assert len(optional_issues) == 1
        assert optional_issues[0].severity == SeverityLevel.INFO

    def test_validate_import_with_exception(self):
        """Test import validation handles exceptions gracefully."""
        test_file = self.root_path / "test.py"
        
        # Mock an exception during validation
        with patch.object(self.validator, 'add_issue') as mock_add_issue:
            # This should trigger the exception handler
            with patch('builtins.any', side_effect=Exception("Test exception")):
                result = self.validator.validate_import("test_module", test_file)
                
                assert result is False
                # Should have called add_issue with validation error
                mock_add_issue.assert_called()
                args = mock_add_issue.call_args[1]
                assert args['issue_type'] == IssueType.IMPORT_VALIDATION_ERROR

    def test_validate_files_list(self):
        """Test validation of file list."""
        files = [
            self.root_path / "valid_syntax.py",
            self.root_path / "invalid_syntax.py"
        ]
        
        issues = self.validator.validate(files)
        
        assert isinstance(issues, list)
        assert len(issues) > 0
        
        # Should find syntax error in invalid file
        syntax_issues = [
            issue for issue in issues 
            if issue.issue_type == IssueType.SYNTAX_ERROR
        ]
        assert len(syntax_issues) > 0

    def test_validate_all_imports_small_set(self):
        """Test parallel import validation with small file set."""
        files = [
            self.root_path / "valid_syntax.py",
            self.root_path / "import_test.py"
        ]
        
        result = self.validator.validate_all_imports(files)
        
        # Should complete validation
        assert isinstance(result, bool)

    def test_validate_all_imports_large_set(self):
        """Test parallel import validation with larger file set."""
        files = list(self.root_path.glob("*.py"))
        
        result = self.validator.validate_all_imports(files)
        
        # Should complete validation
        assert isinstance(result, bool)

    def test_validate_all_imports_with_timeout(self):
        """Test import validation with timeout."""
        files = [self.root_path / "large_file.py"]
        
        # Mock time.time to simulate timeout
        with patch('time.time') as mock_time:
            mock_time.side_effect = [0, 1000]  # Start time, then timeout
            
            result = self.validator.validate_all_imports(files)
            
            # Should handle timeout gracefully
            assert isinstance(result, bool)

    def test_validate_all_imports_sequential_fallback(self):
        """Test fallback to sequential processing."""
        files = [self.root_path / "valid_syntax.py"]
        
        # Mock ThreadPoolExecutor to raise exception
        with patch('concurrent.futures.ThreadPoolExecutor', side_effect=Exception("Pool error")):
            result = self.validator.validate_all_imports(files)
            
            # Should fallback to sequential and still work
            assert isinstance(result, bool)

    def test_validate_all_imports_sequential_with_timeout(self):
        """Test sequential validation with timeout."""
        files = [self.root_path / "valid_syntax.py"]
        
        # Clear any existing issues
        self.validator.issues.clear()
        
        # Test the sequential fallback method directly
        start_time = 0.0
        timeout = 1  # Very short timeout
        
        # Create a mock that always returns timeout exceeded
        with patch('src.infrastructure.tools.validation.core.syntax_validator.time.time') as mock_time:
            # Mock to always return a time that ensures timeout condition is met
            def time_side_effect():
                return start_time + timeout + 1
            mock_time.side_effect = time_side_effect
            
            result = self.validator._validate_all_imports_sequential(files, timeout, start_time)
            
            assert result is False  # Should timeout
            
            # Should add timeout error issue
            timeout_issues = [
                issue for issue in self.validator.issues 
                if "timed out" in issue.message.lower()
            ]
            assert len(timeout_issues) > 0, f"Expected timeout issues, but got: {[issue.message for issue in self.validator.issues]}"

    def test_get_syntax_errors(self):
        """Test syntax error retrieval."""
        # Validate an invalid file to generate errors
        invalid_file = self.root_path / "invalid_syntax.py"
        self.validator.validate_syntax(invalid_file)
        
        errors = self.validator.get_syntax_errors()
        
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert all(isinstance(error, tuple) for error in errors)
        assert all(len(error) == 2 for error in errors)  # (file_path, error_message)

    def test_has_syntax_errors(self):
        """Test syntax error detection."""
        # Initially no errors
        assert self.validator.has_syntax_errors() is False
        
        # Validate invalid file
        invalid_file = self.root_path / "invalid_syntax.py"
        self.validator.validate_syntax(invalid_file)
        
        # Now should have errors
        assert self.validator.has_syntax_errors() is True

    def test_validate_file_valid(self):
        """Test single file validation with valid file."""
        valid_file = self.root_path / "valid_syntax.py"
        errors = self.validator.validate_file(valid_file)
        
        assert errors == []

    def test_validate_file_invalid(self):
        """Test single file validation with invalid file."""
        invalid_file = self.root_path / "invalid_syntax.py"
        errors = self.validator.validate_file(invalid_file)
        
        assert len(errors) > 0
        assert all(error[0] == invalid_file for error in errors)

    def test_validate_file_nonexistent(self):
        """Test single file validation with non-existent file."""
        nonexistent = self.root_path / "nonexistent.py"
        errors = self.validator.validate_file(nonexistent)
        
        assert errors == []

    def test_validate_file_non_python(self):
        """Test single file validation with non-Python file."""
        text_file = self.root_path / "readme.txt"
        text_file.write_text("Not a Python file")
        
        errors = self.validator.validate_file(text_file)
        
        assert errors == []

    def test_extract_imports_complex_cases(self):
        """Test import extraction with complex cases."""
        complex_file = self.root_path / "complex_imports.py"
        complex_file.write_text('''"""Complex import cases."""

# Standard imports
import os
import sys as system
from pathlib import Path
from collections import defaultdict, Counter

# Nested try/except with imports
try:
    import optional1
    try:
        from optional1 import submodule
    except ImportError:
        submodule = None
except ImportError:
    optional1 = None

# Import with multiple exception handlers
try:
    import tricky_package
except ImportError:
    pass
except ModuleNotFoundError:
    pass

# Relative imports with different levels
from . import sibling
from .. import parent
from ... import grandparent

def dummy():
    pass
''')
        
        imports = self.validator.extract_imports(complex_file)
        
        # Should extract all imports
        assert "os" in imports
        assert "sys" in imports
        assert "pathlib" in imports
        assert "collections" in imports
        assert "optional1" in imports
        assert "tricky_package" in imports
        
        # Should handle relative imports
        relative_imports = [imp for imp in imports if imp.startswith(".")]
        assert ".sibling" in imports
        assert "..parent" in imports
        assert "...grandparent" in imports
        
        # Should identify handled imports
        assert "optional1" in self.validator.handled_imports
        assert "tricky_package" in self.validator.handled_imports

    def test_performance_large_file(self):
        """Test performance with large file."""
        large_file = self.root_path / "large_file.py"
        
        start_time = time.time()
        result = self.validator.validate_syntax(large_file)
        duration = time.time() - start_time
        
        assert result is True
        # Should complete within reasonable time (adjust threshold as needed)
        assert duration < 10.0

    def test_concurrent_futures_exception_handling(self):
        """Test handling of concurrent.futures exceptions."""
        files = [self.root_path / "valid_syntax.py"]
        
        # Mock ThreadPoolExecutor to raise TimeoutError
        with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
            mock_context = MagicMock()
            mock_executor.return_value.__enter__.return_value = mock_context
            mock_context.submit.side_effect = concurrent.futures.TimeoutError("Test timeout")
            
            result = self.validator.validate_all_imports(files)
            
            # Should handle exception and fallback
            assert isinstance(result, bool)

    def test_progress_reporting(self):
        """Test progress reporting during validation."""
        files = list(self.root_path.glob("*.py"))
        
        # Capture printed output
        with patch('builtins.print') as mock_print:
            self.validator.validate_all_imports(files)
            
            # Should have printed progress messages
            assert mock_print.called
            
            # Check for progress-related prints
            print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
            progress_messages = [msg for msg in print_calls if "Progress:" in msg or "files/sec" in msg]
            assert len(progress_messages) > 0

    def test_encoding_handling(self):
        """Test proper handling of different file encodings."""
        # Test file with explicit UTF-8 content
        unicode_file = self.root_path / "unicode_test.py"
        result = self.validator.validate_syntax(unicode_file)
        
        assert result is True

    def test_ast_parse_error_vs_syntax_error(self):
        """Test distinction between syntax errors and parse errors."""
        # Create file that causes parse error (not syntax error)
        parse_error_file = self.root_path / "parse_error_test.py"
        # This is syntactically valid but might cause issues
        parse_error_file.write_text("# This file is syntactically correct\nimport sys\n")
        
        # Mock ast.parse to raise different types of exceptions
        with patch('ast.parse', side_effect=ValueError("Parse error")):
            result = self.validator.validate_syntax(parse_error_file)
            
            assert result is False
            
            # Should add parse error, not syntax error
            parse_errors = [
                issue for issue in self.validator.issues 
                if issue.issue_type == IssueType.PARSE_ERROR
            ]
            assert len(parse_errors) > 0

    def test_module_parts_extraction(self):
        """Test extraction of module parts for nested imports."""
        test_file = self.root_path / "nested_imports.py"
        test_file.write_text('''"""Nested import test."""

try:
    from very.deeply.nested.package import something
except ImportError:
    pass

def dummy():
    pass
''')
        
        imports = self.validator.extract_imports(test_file)
        
        # Should handle nested module properly
        assert "very.deeply.nested.package" in imports
        
        # Should track all parts of the module in handled_imports
        assert "very" in self.validator.handled_imports
        assert "very.deeply" in self.validator.handled_imports
        assert "very.deeply.nested" in self.validator.handled_imports
        assert "very.deeply.nested.package" in self.validator.handled_imports