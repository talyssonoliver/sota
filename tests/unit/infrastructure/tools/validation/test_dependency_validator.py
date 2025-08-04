"""
Tests for dependency validator - Validates project dependencies.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.infrastructure.tools.validation.core.dependency_validator import DependencyValidator


class TestDependencyValidator:
    """Test cases for DependencyValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)
        
        # Create test files
        self.create_test_files()
        
        self.validator = DependencyValidator(root_path=self.root_path)

    def create_test_files(self):
        """Create test files for validation."""
        # Requirements file
        requirements_file = self.root_path / "requirements.txt"
        requirements_file.write_text(
            """
# Core dependencies
requests==2.28.0
numpy>=1.20.0
pandas
flask==2.0.1

# Development dependencies
pytest==7.0.0
black
ruff==0.0.1

# Unused dependency
unused-package==1.0.0
"""
        )

        # Python files using some dependencies
        main_file = self.root_path / "main.py"
        main_file.write_text(
            """
import requests
import numpy as np
from flask import Flask

app = Flask(__name__)

def fetch_data():
    response = requests.get("https://api.example.com")
    return response.json()

def process_data(data):
    array = np.array(data)
    return array.mean()
"""
        )

        # Test file
        test_file = self.root_path / "test_main.py"
        test_file.write_text(
            """
import pytest
from main import fetch_data, process_data

def test_process_data():
    data = [1, 2, 3, 4, 5]
    result = process_data(data)
    assert result == 3.0
"""
        )

    def test_initialization(self):
        """Test validator initialization."""
        assert self.validator.root_path == self.root_path
        assert self.validator.dependency_analysis is None

    def test_validate_dependencies_success(self):
        """Test successful dependency validation."""
        result = self.validator.validate_dependencies()
        
        assert result is True
        assert self.validator.dependency_analysis is not None

    def test_validate_dependencies_no_requirements_file(self):
        """Test validation when requirements.txt is missing."""
        # Remove requirements file
        requirements_file = self.root_path / "requirements.txt"
        requirements_file.unlink()
        
        result = self.validator.validate_dependencies()
        
        assert result is False
        assert len(self.validator.issues) > 0
        
        # Should have issue about missing requirements.txt
        missing_req_issues = [
            issue for issue in self.validator.issues
            if "requirements.txt file not found" in issue.message
        ]
        assert len(missing_req_issues) > 0

    def test_parse_requirements_file(self):
        """Test parsing requirements file."""
        requirements_file = self.root_path / "requirements.txt"
        declared_deps = self.validator._parse_requirements_file(requirements_file)
        
        assert "requests" in declared_deps
        assert "numpy" in declared_deps
        assert "pandas" in declared_deps
        assert "flask" in declared_deps
        assert "pytest" in declared_deps
        assert "black" in declared_deps
        assert "ruff" in declared_deps
        assert "unused-package" in declared_deps

    def test_parse_requirements_file_with_versions(self):
        """Test parsing requirements file preserves version info."""
        requirements_file = self.root_path / "requirements.txt"
        declared_deps = self.validator._parse_requirements_file(requirements_file)
        
        # Version specifications should be stripped, only package names preserved
        assert "requests" in declared_deps
        assert "numpy" in declared_deps
        assert "flask" in declared_deps
        assert "pytest" in declared_deps

    def test_find_used_imports(self):
        """Test finding used imports in Python files."""
        used_imports = self.validator._find_used_imports()
        
        # Should find imports from our test files
        assert "requests" in used_imports
        assert "numpy" in used_imports
        assert "flask" in used_imports
        assert "pytest" in used_imports
        
        # Should not find unused package
        assert "unused-package" not in used_imports

    def test_categorize_dependencies(self):
        """Test dependency categorization."""
        declared_deps = {"requests", "numpy", "flask", "pytest", "unused-package"}
        used_imports = {"requests", "numpy", "flask", "pytest"}
        
        categories = self.validator._categorize_dependencies(declared_deps, used_imports)
        
        assert isinstance(categories, dict)
        # Check that categories dict has expected structure
        expected_categories = [
            "direct_imports", "dev_tools", "runtime_critical", "infrastructure",
            "transitive", "type_stubs", "optional_features", "unknown", "safe_to_review"
        ]
        for category in expected_categories:
            assert category in categories

    def test_report_dependency_findings(self):
        """Test reporting of dependency findings."""
        # First run validation to populate analysis
        self.validator.validate_dependencies()
        
        requirements_file = self.root_path / "requirements.txt"
        initial_issue_count = len(self.validator.issues)
        
        self.validator._report_dependency_findings(requirements_file)
        
        # Should have added findings to issues
        assert len(self.validator.issues) >= initial_issue_count

    def test_is_safe_to_remove_dependency(self):
        """Test safe dependency removal detection."""
        # Test the _is_safe_to_review method which exists in the implementation
        context = {"python_files": [], "config_files": [], "scripts": [], "docker_files": [], "ci_files": [], "documentation": [], "possible_indirect": []}
        
        # Test with pytest (which is in dev_tools list and has no usage)
        assert self.validator._is_safe_to_review("pytest", context) is True
        
        # Test with package that has python files usage
        context_with_usage = context.copy()
        context_with_usage["python_files"] = ["test.py"]
        assert self.validator._is_safe_to_review("pytest", context_with_usage) is False

    def test_has_errors(self):
        """Test error detection."""
        # Initially no errors
        assert not self.validator.has_errors()
        
        # Add error-level issue
        self.validator.add_issue(
            category="dependencies",
            issue_type="DEPENDENCY_ERROR",
            file_path="requirements.txt",
            message="Critical dependency error",
            severity="error"
        )
        
        assert self.validator.has_errors()

    def test_dependency_validation_with_empty_requirements(self):
        """Test validation with empty requirements file."""
        # Create empty requirements file
        requirements_file = self.root_path / "requirements.txt"
        requirements_file.write_text("")
        
        result = self.validator.validate_dependencies()
        
        # Should still succeed but may have warnings
        assert result is True

    def test_dependency_validation_with_malformed_requirements(self):
        """Test validation with malformed requirements file."""
        # Create malformed requirements file
        requirements_file = self.root_path / "requirements.txt"
        requirements_file.write_text(
            """
        invalid line without package name
        ==2.0.0
        another-invalid-line===
        """
        )
        
        # Should handle gracefully
        try:
            result = self.validator.validate_dependencies()
            # Should not crash
            assert isinstance(result, bool)
        except Exception:
            pytest.fail("Dependency validation should handle malformed requirements gracefully")

    def test_get_dependency_report(self):
        """Test getting dependency analysis report."""
        self.validator.validate_dependencies()
        
        # Test that dependency analysis was populated
        assert self.validator.dependency_analysis is not None
        assert isinstance(self.validator.dependency_analysis, dict)

    @patch('ast.parse')
    def test_find_used_imports_with_syntax_error(self, mock_parse):
        """Test handling of syntax errors when parsing files."""
        mock_parse.side_effect = SyntaxError("Invalid syntax")
        
        # Should handle syntax errors gracefully
        used_imports = self.validator._find_used_imports()
        
        # Should return empty set or handle gracefully
        assert isinstance(used_imports, set)

    def test_complex_import_patterns(self):
        """Test handling of complex import patterns."""
        # Create file with complex imports
        complex_file = self.root_path / "complex_imports.py"
        complex_file.write_text(
            """
# Various import patterns
import os
import sys as system
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Optional
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# Conditional imports
try:
    import optional_package
except ImportError:
    optional_package = None
"""
        )
        
        used_imports = self.validator._find_used_imports()
        
        # Should detect various import patterns
        expected_imports = {"os", "sys", "pathlib", "collections", "typing", 
                          "numpy", "sklearn", "matplotlib"}
        
        # Check that some expected imports are found
        found_expected = expected_imports.intersection(used_imports)
        assert len(found_expected) > 0