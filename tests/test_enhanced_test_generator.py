"""
Test coverage for Enhanced Test Generator components.
This file tests the test generator's advanced capabilities including edge cases,
integration tests, error handling, performance tests, and security tests.
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from utils.test_generator import (CodeLanguage, QATestCase, QATestFramework,
                                   QATestGenerator, QATestSuite)

# Add the project root to the path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class TestEnhancedQATestGenerator:
    """Test suite for enhanced test generator features."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)

        # Create sample source files
        (project_path / "src").mkdir()

        # Python file with complex class
        (project_path / "src" / "complex_module.py").write_text("""
class DatabaseManager:
    def __init__(self, connection_string):
        self.connection = connection_string
        self.connected = False

    def connect(self):
        if not self.connection:
            raise ValueError("No connection string provided")
        self.connected = True
        return True

    def execute_query(self, query, params=None):
        if not self.connected:
            raise RuntimeError("Not connected to database")
        return {"result": "success", "rows": 10}

    def disconnect(self):
        self.connected = False

class UserService:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_user(self, username, email):
        if not username or not email:
            raise ValueError("Username and email required")
        query = "INSERT INTO users (username, email) VALUES (?, ?)"
        return self.db.execute_query(query, (username, email))

    def get_user(self, user_id):
        query = "SELECT * FROM users WHERE id = ?"
        return self.db.execute_query(query, (user_id,))

def process_user_input(input_data):
    \"\"\"Process user input with validation.\"\"\"
    if not input_data:
        return None
    return {"processed": True, "data": input_data}

def handle_file_upload(file_path):
    \"\"\"Handle file upload operation.\"\"\"
    if not file_path or not Path(file_path).exists():
        raise FileNotFoundError("File not found")
    return {"uploaded": True, "path": file_path}
""")

        yield project_path
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def test_generator(self, temp_project):
        """Create a QATestGenerator instance for testing."""
        return QATestGenerator(str(temp_project))

    def test_generate_edge_case_tests(self, test_generator):
        """Test edge case test generation."""
        analysis = {
            "functions": [
                {"name": "process_data", "args": [
                    "data", "options"], "line": 10},
                {"name": "calculate", "args": ["x", "y"], "line": 20}
            ]
        }

        edge_tests = test_generator._generate_edge_case_tests(
            analysis, QATestFramework.PYTEST)

        assert len(edge_tests) == 2
        assert all(isinstance(test, QATestCase) for test in edge_tests)
        assert edge_tests[0].name == "test_process_data_edge_cases"
        assert edge_tests[0].test_type == "unit"
        assert "None" in edge_tests[0].code

    def test_generate_integration_tests(self, test_generator):
        """Test integration test generation."""
        analysis = {
            "classes": [
                {"name": "DatabaseManager", "methods": [
                    "connect", "execute_query"]},
                {"name": "UserService", "methods": ["create_user", "get_user"]}
            ]
        }

        integration_tests = test_generator._generate_integration_tests(
            analysis, QATestFramework.PYTEST)

        assert len(integration_tests) == 1
        assert integration_tests[0].name == "test_component_integration"
        assert integration_tests[0].test_type == "integration"
        assert "DatabaseManager" in integration_tests[0].code
        assert "UserService" in integration_tests[0].code

    def test_generate_integration_tests_insufficient_classes(
            self, test_generator):
        """Test integration test generation with insufficient classes."""
        analysis = {
            "classes": [
                {"name": "SingleClass", "methods": ["method1"]}
            ]
        }

        integration_tests = test_generator._generate_integration_tests(
            analysis, QATestFramework.PYTEST)

        # No integration tests for single class
        assert len(integration_tests) == 0

    def test_generate_error_handling_tests(self, test_generator):
        """Test error handling test generation."""
        analysis = {
            "functions": [
                {"name": "divide_numbers", "args": ["a", "b"], "line": 10},
                {"name": "parse_json", "args": ["data"], "line": 20}
            ]
        }

        error_tests = test_generator._generate_error_handling_tests(
            analysis, QATestFramework.PYTEST)

        assert len(error_tests) == 2
        assert error_tests[0].name == "test_divide_numbers_error_handling"
        assert error_tests[0].test_type == "unit"
        assert "pytest.raises" in error_tests[0].code
        assert "ValueError" in error_tests[0].code or "TypeError" in error_tests[0].code

    def test_generate_integration_test_code_jest(self, test_generator):
        """Test integration test code generation for Jest."""
        classes = [
            {"name": "APIClient", "methods": ["get", "post"]},
            {"name": "DataProcessor", "methods": ["process", "validate"]}
        ]

        code = test_generator._generate_integration_test_code(
            classes, QATestFramework.JEST)

        assert "test(" in code
        assert "APIClient" in code
        assert "DataProcessor" in code
        assert "expect(" in code
        assert ".toBeDefined()" in code

    def test_generate_integration_test_code_pytest(self, test_generator):
        """Test integration test code generation for pytest."""
        classes = [
            {"name": "DatabaseManager", "methods": ["connect"]},
            {"name": "UserService", "methods": ["create_user"]}
        ]

        code = test_generator._generate_integration_test_code(
            classes, QATestFramework.PYTEST)

        assert "def test_component_integration" in code
        assert "DatabaseManager" in code
        assert "UserService" in code
        assert "assert" in code
        assert "is not None" in code

    def test_generate_error_test_code_jest(self, test_generator):
        """Test error handling test code generation for Jest."""
        code = test_generator._generate_error_test_code(
            "validateInput", QATestFramework.JEST)

        assert "test(" in code
        assert "validateInput" in code
        assert "expect(" in code
        assert "null" in code
        assert "undefined" in code
        assert "catch" in code

    def test_generate_error_test_code_pytest(self, test_generator):
        """Test error handling test code generation for pytest."""
        code = test_generator._generate_error_test_code(
            "validate_input", QATestFramework.PYTEST)

        assert "def test_validate_input_error_handling" in code
        assert "validate_input" in code
        assert "pytest.raises" in code
        assert "ValueError" in code or "TypeError" in code
        assert "None" in code

    def test_generate_performance_tests(self, test_generator):
        """Test performance test generation."""
        analysis = {
            "functions": [
                {"name": "compute_heavy", "args": ["data"], "line": 10},
                {"name": "process_batch", "args": ["items"], "line": 20}
            ]
        }

        perf_tests = test_generator.generate_performance_tests(
            analysis, QATestFramework.PYTEST)

        assert len(perf_tests) == 2
        assert perf_tests[0].name == "test_compute_heavy_performance"
        assert perf_tests[0].test_type == "performance"
        assert "time" in perf_tests[0].code
        assert "execution_time" in perf_tests[0].code

    def test_generate_performance_test_code_jest(self, test_generator):
        """Test performance test code generation for Jest."""
        code = test_generator._generate_performance_test_code(
            "heavyComputation", QATestFramework.JEST)

        assert "test(" in code
        assert "heavyComputation" in code
        assert "Date.now()" in code
        assert "executionTime" in code
        assert "toBeLessThan(1000)" in code

    def test_generate_performance_test_code_pytest(self, test_generator):
        """Test performance test code generation for pytest."""
        code = test_generator._generate_performance_test_code(
            "heavy_computation", QATestFramework.PYTEST)

        assert "def test_heavy_computation_performance" in code
        assert "import time" in code
        assert "time.time()" in code
        assert "execution_time" in code
        assert "assert execution_time < 1.0" in code

    def test_generate_security_tests(self, test_generator):
        """Test security test generation."""
        analysis = {
            "functions": [
                {"name": "process_user_input", "args": ["data"], "line": 10},
                {"name": "parse_xml", "args": ["xml_data"], "line": 20},
                {"name": "handle_upload", "args": ["file"], "line": 30},
                # Should not generate security test
                {"name": "calculate", "args": ["x", "y"], "line": 40}
            ]
        }

        security_tests = test_generator.generate_security_tests(
            analysis, QATestFramework.PYTEST)

        # Should generate tests for functions with security-relevant names
        # process_user_input, parse_xml, handle_upload
        assert len(security_tests) >= 2

        security_test_names = [test.name for test in security_tests]
        assert any(
            "process_user_input" in name for name in security_test_names)
        assert any("parse_xml" in name for name in security_test_names)
        assert any("handle_upload" in name for name in security_test_names)

        # Should not generate security test for regular calculation function
        assert not any("calculate" in name for name in security_test_names)

    def test_generate_security_test_code_jest(self, test_generator):
        """Test security test code generation for Jest."""
        code = test_generator._generate_security_test_code(
            "processInput", QATestFramework.JEST)

        assert "test(" in code
        assert "processInput" in code
        assert "maliciousInputs" in code
        assert "script" in code
        assert "etc/passwd" in code
        assert "DROP TABLE" in code
        assert "forEach" in code

    def test_generate_security_test_code_pytest(self, test_generator):
        """Test security test code generation for pytest."""
        code = test_generator._generate_security_test_code(
            "process_input", QATestFramework.PYTEST)

        assert "def test_process_input_security" in code
        assert "malicious_inputs" in code
        assert "script" in code
        assert "etc/passwd" in code
        assert "DROP TABLE" in code
        assert "__class__.__bases__" in code  # Python-specific injection
        assert "for malicious_input in malicious_inputs" in code

    def test_enhanced_test_suite_generation(self, test_generator):
        """Test enhanced test suite generation with all new features."""
        # Create a complex analysis that should trigger all test types
        analysis = {
            "filename": "complex_module",
            "classes": [
                {"name": "DatabaseManager", "methods": [
                    "connect", "execute_query"], "line": 1},
                {"name": "UserService", "methods": [
                    "create_user", "get_user"], "line": 20}
            ],
            "functions": [
                {"name": "process_user_input", "args": [
                    "input_data"], "line": 50, "is_async": False},
                {"name": "handle_file_upload", "args": [
                    "file_path"], "line": 60, "is_async": False}
            ],
            "imports": ["pathlib", "json"],
            "complexity": "high"
        }

        test_suite = test_generator._generate_test_suite(
            analysis, QATestFramework.PYTEST, CodeLanguage.PYTHON
        )

        assert isinstance(test_suite, QATestSuite)
        assert test_suite.framework == QATestFramework.PYTEST
        assert test_suite.language == CodeLanguage.PYTHON

        # Should have various types of tests
        test_types = [test.test_type for test in test_suite.test_cases]
        assert "unit" in test_types
        # Should have integration tests due to multiple classes
        assert "integration" in test_types
        # Should have tests for both classes
        # Check that we have tests for the classes (either by name or class
        # reference)
        test_names = [test.name for test in test_suite.test_cases]
        class_tests_found = any(any(cls_name.lower() in name.lower() for cls_name in [
                                "database", "user", "service", "manager"]) for name in test_names)
        assert class_tests_found
        # Should have security tests for input/upload functions
        assert any(
            "security" in test.test_type.lower() for test in test_suite.test_cases) or any(
            "security" in test.name.lower() for test in test_suite.test_cases)

        # Should have error handling tests
        assert any("error_handling" in name for name in test_names)

    def test_comprehensive_file_generation_with_real_analysis(
            self, test_generator, temp_project):
        """Test comprehensive test file generation with real code analysis."""
        source_file = temp_project / "src" / "complex_module.py"

        # Generate test file for the complex module
        test_content = test_generator.generate_test_file(
            str(source_file),
            framework=QATestFramework.PYTEST
        )

        assert test_content is not None
        assert len(test_content) > 0

        # Check that the test content includes various test types
        assert "import pytest" in test_content
        assert "class Test" in test_content
        assert "def test_" in test_content
        # Should include tests for the classes we defined
        assert "DatabaseManager" in test_content
        assert "UserService" in test_content

        # Should include security tests for input handling functions (might be
        # in error handling)
        assert ("security" in test_content.lower() or "malicious" in test_content.lower(
        ) or "error" in test_content.lower() or "exception" in test_content.lower())

        # Should include error handling
        assert "error" in test_content.lower() or "exception" in test_content.lower()


class TestQATestGeneratorPatterns:
    """Test test generation patterns and templates."""

    @pytest.fixture
    def test_generator(self):
        return QATestGenerator()

    def test_jest_patterns(self, test_generator):
        """Test Jest test patterns."""
        patterns = test_generator.patterns["jest"]

        assert "imports" in patterns
        assert "setup" in patterns
        assert "test_wrapper" in patterns

        # Check Jest-specific imports
        imports = patterns["imports"]
        assert any("@testing-library/react" in imp for imp in imports)
        assert any("jest" in imp for imp in imports)

    def test_pytest_patterns(self, test_generator):
        """Test pytest patterns."""
        patterns = test_generator.patterns["pytest"]

        assert "imports" in patterns
        assert "setup" in patterns
        assert "test_wrapper" in patterns

        # Check pytest-specific imports
        imports = patterns["imports"]
        assert any("pytest" in imp for imp in imports)
        assert any("unittest.mock" in imp for imp in imports)

    def test_unittest_patterns(self, test_generator):
        """Test unittest patterns."""
        patterns = test_generator.patterns["unittest"]

        assert "imports" in patterns
        assert "setup" in patterns
        assert "test_wrapper" in patterns

        # Check unittest-specific imports
        imports = patterns["imports"]
        assert any("unittest" in imp for imp in imports)
        assert any("unittest.mock" in imp for imp in imports)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
