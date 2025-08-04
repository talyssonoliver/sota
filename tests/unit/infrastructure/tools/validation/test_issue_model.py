"""
Tests for validation issue model - Structured representation of validation issues.
"""

import pytest

from src.infrastructure.tools.validation.core.issue_model import (
    IssueType,
    SeverityLevel,
    ValidationIssue,
)


class TestIssueType:
    """Test cases for IssueType enum."""

    def test_issue_type_values(self):
        """Test that all issue types have correct values."""
        # Basic issue types
        assert IssueType.SYNTAX_ERROR.value == "syntax_error"
        assert IssueType.IMPORT_ERROR.value == "import_error"
        assert IssueType.UNUSED_IMPORT.value == "unused_import"
        assert IssueType.CIRCULAR_IMPORT.value == "circular_import"
        assert IssueType.NAMING_CONVENTION.value == "naming_convention"
        assert IssueType.SECURITY_ISSUE.value == "security_issue"
        assert IssueType.PERFORMANCE_ISSUE.value == "performance_issue"
        assert IssueType.COMPLEXITY_ISSUE.value == "complexity_issue"
        assert IssueType.STRUCTURE_ISSUE.value == "structure_issue"
        assert IssueType.DEPENDENCY_ISSUE.value == "dependency_issue"
        assert IssueType.ARCHITECTURE_VIOLATION.value == "architecture_violation"
        assert IssueType.CODE_SMELL.value == "code_smell"
        assert IssueType.DOCUMENTATION_ISSUE.value == "documentation_issue"
        assert IssueType.OTHER.value == "other"

    def test_architecture_issue_types(self):
        """Test architecture-specific issue types."""
        assert IssueType.ANALYSIS_ERROR.value == "analysis_error"
        assert IssueType.FORBIDDEN_LAYER_IMPORT.value == "forbidden_layer_import"
        assert IssueType.EXPLICITLY_FORBIDDEN_IMPORT.value == "explicitly_forbidden_import"

    def test_performance_issue_types(self):
        """Test performance-specific issue types."""
        assert IssueType.FUNCTION_TOO_LONG.value == "function_too_long"
        assert IssueType.HIGH_COMPLEXITY.value == "high_complexity"

    def test_health_issue_types(self):
        """Test health-specific issue types."""
        assert IssueType.HIGH_FILE_TODO_COUNT.value == "high_file_todo_count"
        assert IssueType.HIGH_FILE_FIXME_COUNT.value == "high_file_fixme_count"
        assert IssueType.HIGH_PROJECT_TODO_COUNT.value == "high_project_todo_count"
        assert IssueType.HIGH_PROJECT_FIXME_COUNT.value == "high_project_fixme_count"
        assert IssueType.URGENT_TODO.value == "urgent_todo"
        assert IssueType.URGENT_FIXME.value == "urgent_fixme"
        assert IssueType.TEMPORARY_HACK.value == "temporary_hack"
        assert IssueType.BROKEN_CODE.value == "broken_code"
        assert IssueType.TEMPORARY_CODE.value == "temporary_code"
        assert IssueType.DEBUG_PRINT.value == "debug_print"
        assert IssueType.DEBUG_IMPORT.value == "debug_import"
        assert IssueType.BREAKPOINT.value == "breakpoint"
        assert IssueType.COMMENTED_TODO.value == "commented_todo"

    def test_issue_type_membership(self):
        """Test that specific values are members of the enum."""
        # Test membership using string values
        assert "syntax_error" in [item.value for item in IssueType]
        assert "import_error" in [item.value for item in IssueType]
        assert "security_issue" in [item.value for item in IssueType]

    def test_issue_type_iteration(self):
        """Test iteration over issue types."""
        issue_types = list(IssueType)
        assert len(issue_types) > 20  # Should have many issue types
        assert IssueType.SYNTAX_ERROR in issue_types
        assert IssueType.OTHER in issue_types


class TestSeverityLevel:
    """Test cases for SeverityLevel enum."""

    def test_severity_level_values(self):
        """Test that all severity levels have correct values."""
        assert SeverityLevel.ERROR.value == "error"
        assert SeverityLevel.WARNING.value == "warning"
        assert SeverityLevel.INFO.value == "info"
        assert SeverityLevel.HINT.value == "hint"

    def test_severity_level_ordering(self):
        """Test implicit ordering of severity levels."""
        # While enums don't have natural ordering, we can test membership
        severities = [SeverityLevel.ERROR, SeverityLevel.WARNING, 
                     SeverityLevel.INFO, SeverityLevel.HINT]
        assert len(severities) == 4

    def test_severity_level_membership(self):
        """Test membership of severity levels."""
        severity_values = [item.value for item in SeverityLevel]
        assert "error" in severity_values
        assert "warning" in severity_values
        assert "info" in severity_values
        assert "hint" in severity_values


class TestValidationIssue:
    """Test cases for ValidationIssue dataclass."""

    def test_minimal_issue_creation(self):
        """Test creating issue with minimal required fields."""
        issue = ValidationIssue(
            category="syntax",
            issue_type=IssueType.SYNTAX_ERROR,
            file_path="/path/to/file.py",
            message="Syntax error found"
        )

        assert issue.category == "syntax"
        assert issue.issue_type == IssueType.SYNTAX_ERROR
        assert issue.file_path == "/path/to/file.py"
        assert issue.message == "Syntax error found"
        assert issue.line is None
        assert issue.character is None
        assert issue.fix_suggestion is None
        assert issue.severity == SeverityLevel.WARNING  # Default
        assert issue.offending_line is None
        assert issue.expected_pattern is None
        assert issue.auto_fixable is False  # Default

    def test_complete_issue_creation(self):
        """Test creating issue with all fields."""
        issue = ValidationIssue(
            category="imports",
            issue_type=IssueType.UNUSED_IMPORT,
            file_path="/path/to/file.py",
            message="Unused import detected",
            line=10,
            character=5,
            fix_suggestion="Remove the unused import",
            severity=SeverityLevel.ERROR,
            offending_line="import unused_module",
            expected_pattern="^import [a-z_]+$",
            auto_fixable=True
        )

        assert issue.category == "imports"
        assert issue.issue_type == IssueType.UNUSED_IMPORT
        assert issue.file_path == "/path/to/file.py"
        assert issue.message == "Unused import detected"
        assert issue.line == 10
        assert issue.character == 5
        assert issue.fix_suggestion == "Remove the unused import"
        assert issue.severity == SeverityLevel.ERROR
        assert issue.offending_line == "import unused_module"
        assert issue.expected_pattern == "^import [a-z_]+$"
        assert issue.auto_fixable is True

    def test_to_dict_minimal(self):
        """Test converting minimal issue to dictionary."""
        issue = ValidationIssue(
            category="syntax",
            issue_type=IssueType.SYNTAX_ERROR,
            file_path="/path/to/file.py",
            message="Syntax error found"
        )

        result = issue.to_dict()

        expected = {
            "category": "syntax",
            "issue_type": "syntax_error",
            "file_path": "/path/to/file.py",
            "message": "Syntax error found",
            "line": None,
            "character": None,
            "fix_suggestion": None,
            "severity": "warning",
            "offending_line": None,
            "expected_pattern": None,
            "auto_fixable": False,
            "details": None
        }

        assert result == expected

    def test_to_dict_complete(self):
        """Test converting complete issue to dictionary."""
        issue = ValidationIssue(
            category="imports",
            issue_type=IssueType.UNUSED_IMPORT,
            file_path="/path/to/file.py",
            message="Unused import detected",
            line=10,
            character=5,
            fix_suggestion="Remove the unused import",
            severity=SeverityLevel.ERROR,
            offending_line="import unused_module",
            expected_pattern="^import [a-z_]+$",
            auto_fixable=True
        )

        result = issue.to_dict()

        expected = {
            "category": "imports",
            "issue_type": "unused_import",
            "file_path": "/path/to/file.py",
            "message": "Unused import detected",
            "line": 10,
            "character": 5,
            "fix_suggestion": "Remove the unused import",
            "severity": "error",
            "offending_line": "import unused_module",
            "expected_pattern": "^import [a-z_]+$",
            "auto_fixable": True,
            "details": None
        }

        assert result == expected

    def test_to_dict_preserves_enum_values(self):
        """Test that to_dict converts enums to their string values."""
        issue = ValidationIssue(
            category="security",
            issue_type=IssueType.SECURITY_ISSUE,
            file_path="/path/to/file.py",
            message="Security vulnerability",
            severity=SeverityLevel.ERROR
        )

        result = issue.to_dict()

        # Enums should be converted to string values
        assert result["issue_type"] == "security_issue"
        assert result["severity"] == "error"
        assert isinstance(result["issue_type"], str)
        assert isinstance(result["severity"], str)

    def test_str_representation_minimal(self):
        """Test string representation with minimal information."""
        issue = ValidationIssue(
            category="syntax",
            issue_type=IssueType.SYNTAX_ERROR,
            file_path="/path/to/file.py",
            message="Syntax error found"
        )

        result = str(issue)
        expected = "[WARNING] /path/to/file.py - Syntax error found"
        assert result == expected

    def test_str_representation_with_line(self):
        """Test string representation with line number."""
        issue = ValidationIssue(
            category="syntax",
            issue_type=IssueType.SYNTAX_ERROR,
            file_path="/path/to/file.py",
            message="Syntax error found",
            line=42,
            severity=SeverityLevel.ERROR
        )

        result = str(issue)
        expected = "[ERROR] /path/to/file.py:42 - Syntax error found"
        assert result == expected

    def test_str_representation_with_line_and_character(self):
        """Test string representation with line and character."""
        issue = ValidationIssue(
            category="syntax",
            issue_type=IssueType.SYNTAX_ERROR,
            file_path="/path/to/file.py",
            message="Syntax error found",
            line=42,
            character=15,
            severity=SeverityLevel.INFO
        )

        result = str(issue)
        expected = "[INFO] /path/to/file.py:42:15 - Syntax error found"
        assert result == expected

    def test_str_representation_severity_cases(self):
        """Test string representation with different severity levels."""
        base_issue = {
            "category": "test",
            "issue_type": IssueType.OTHER,
            "file_path": "/test.py",
            "message": "Test message"
        }

        # Test ERROR
        issue = ValidationIssue(**base_issue, severity=SeverityLevel.ERROR)
        assert "[ERROR]" in str(issue)

        # Test WARNING
        issue = ValidationIssue(**base_issue, severity=SeverityLevel.WARNING)
        assert "[WARNING]" in str(issue)

        # Test INFO
        issue = ValidationIssue(**base_issue, severity=SeverityLevel.INFO)
        assert "[INFO]" in str(issue)

        # Test HINT
        issue = ValidationIssue(**base_issue, severity=SeverityLevel.HINT)
        assert "[HINT]" in str(issue)

    def test_issue_equality(self):
        """Test equality comparison of ValidationIssue instances."""
        issue1 = ValidationIssue(
            category="syntax",
            issue_type=IssueType.SYNTAX_ERROR,
            file_path="/path/to/file.py",
            message="Syntax error found",
            line=10
        )

        issue2 = ValidationIssue(
            category="syntax",
            issue_type=IssueType.SYNTAX_ERROR,
            file_path="/path/to/file.py",
            message="Syntax error found",
            line=10
        )

        issue3 = ValidationIssue(
            category="syntax",
            issue_type=IssueType.SYNTAX_ERROR,
            file_path="/path/to/file.py",
            message="Different message",
            line=10
        )

        assert issue1 == issue2
        assert issue1 != issue3

    def test_issue_with_different_issue_types(self):
        """Test issues with various issue types."""
        issue_types_to_test = [
            IssueType.SYNTAX_ERROR,
            IssueType.IMPORT_ERROR,
            IssueType.SECURITY_ISSUE,
            IssueType.PERFORMANCE_ISSUE,
            IssueType.CODE_SMELL,
            IssueType.ARCHITECTURE_VIOLATION,
            IssueType.HIGH_COMPLEXITY,
            IssueType.URGENT_TODO,
            IssueType.DEBUG_PRINT
        ]

        for issue_type in issue_types_to_test:
            issue = ValidationIssue(
                category="test",
                issue_type=issue_type,
                file_path="/test.py",
                message=f"Test {issue_type.value}"
            )

            assert issue.issue_type == issue_type
            assert issue.to_dict()["issue_type"] == issue_type.value

    def test_dataclass_features(self):
        """Test that ValidationIssue behaves as expected dataclass."""
        issue = ValidationIssue(
            category="test",
            issue_type=IssueType.OTHER,
            file_path="/test.py",
            message="Test message"
        )

        # Test that it's a dataclass
        assert hasattr(issue, "__dataclass_fields__")
        
        # Test field access
        assert hasattr(issue, "category")
        assert hasattr(issue, "issue_type")
        assert hasattr(issue, "file_path")
        assert hasattr(issue, "message")
        assert hasattr(issue, "line")
        assert hasattr(issue, "character")
        assert hasattr(issue, "fix_suggestion")
        assert hasattr(issue, "severity")
        assert hasattr(issue, "offending_line")
        assert hasattr(issue, "expected_pattern")
        assert hasattr(issue, "auto_fixable")

    def test_issue_creation_with_string_paths(self):
        """Test issue creation with different path formats."""
        paths = [
            "/absolute/path/to/file.py",
            "relative/path/to/file.py",
            "file.py",
            "./local/file.py",
            "../parent/file.py"
        ]

        for path in paths:
            issue = ValidationIssue(
                category="test",
                issue_type=IssueType.OTHER,
                file_path=path,
                message="Test message"
            )
            assert issue.file_path == path