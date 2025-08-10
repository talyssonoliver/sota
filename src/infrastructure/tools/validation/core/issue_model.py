
"""
Validation Issue Model
Structured representation of code validation issues.
"""
from src.infrastructure.utils.common_imports import Enum, dataclass
from typing import Dict, Optional


class IssueType(Enum):
    """Types of validation issues."""

    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"
    UNUSED_IMPORT = "unused_import"
    CIRCULAR_IMPORT = "circular_import"
    NAMING_CONVENTION = "naming_convention"
    FUNCTION_NAMING_CONVENTION = "function_naming_convention"
    IMPORT_SORTING = "import_sorting"
    SECURITY_ISSUE = "security_issue"
    PERFORMANCE_ISSUE = "performance_issue"
    COMPLEXITY_ISSUE = "complexity_issue"
    STRUCTURE_ISSUE = "structure_issue"
    DEPENDENCY_ISSUE = "dependency_issue"
    ARCHITECTURE_VIOLATION = "architecture_violation"
    CODE_SMELL = "code_smell"
    DOCUMENTATION_ISSUE = "documentation_issue"
    OTHER = "other"

    # Architecture validation issues
    ANALYSIS_ERROR = "analysis_error"
    FORBIDDEN_LAYER_IMPORT = "forbidden_layer_import"
    EXPLICITLY_FORBIDDEN_IMPORT = "explicitly_forbidden_import"

    # Performance validation issues
    FUNCTION_TOO_LONG = "function_too_long"
    HIGH_COMPLEXITY = "high_complexity"

    # Health validation issues
    HIGH_FILE_TODO_COUNT = "high_file_todo_count"
    HIGH_FILE_FIXME_COUNT = "high_file_fixme_count"
    HIGH_PROJECT_TODO_COUNT = "high_project_todo_count"
    HIGH_PROJECT_FIXME_COUNT = "high_project_fixme_count"
    URGENT_TODO = "urgent_todo"
    URGENT_FIXME = "urgent_fixme"
    TEMPORARY_HACK = "temporary_hack"
    BROKEN_CODE = "broken_code"
    TEMPORARY_CODE = "temporary_code"
    DEBUG_PRINT = "debug_print"
    DEBUG_IMPORT = "debug_import"
    BREAKPOINT = "breakpoint"
    COMMENTED_TODO = "commented_todo"
    
    # Auto-fixer specific issue types
    EMPTY_DIRECTORY = "empty_directory"
    FORBIDDEN_PATTERN = "forbidden_pattern"
    CODE_FORMATTING = "code_formatting"
    
    # Syntax validator specific issue types
    PARSE_ERROR = "parse_error"
    IMPORT_EXTRACTION_ERROR = "import_extraction_error"
    INVALID_IMPORT_NAME = "invalid_import_name"
    INVALID_IMPORT_SYNTAX = "invalid_import_syntax"
    OPTIONAL_DEPENDENCY = "optional_dependency"
    IMPORT_VALIDATION_ERROR = "import_validation_error"
    
    # Structure validator specific issue types
    FILE_NAMING_CONVENTION = "file_naming_convention"
    CLASS_NAMING_CONVENTION = "class_naming_convention"
    NAMING_VALIDATION_ERROR = "naming_validation_error"
    MISSING_DOCSTRING = "missing_docstring"
    DOCUMENTATION_COVERAGE = "documentation_coverage"
    LOW_TEST_COVERAGE = "low_test_coverage"
    SECURITY_SCAN_ERROR = "security_scan_error"
    POTENTIAL_HARDCODED_SECRET = "potential_hardcoded_secret"
    DANGEROUS_FUNCTION_USAGE = "dangerous_function_usage"
    SHELL_INJECTION_RISK = "shell_injection_risk"


class SeverityLevel(Enum):
    """Severity levels for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass
class ValidationIssue:
    """Structured representation of a validation issue."""

    category: str
    issue_type: IssueType
    file_path: str
    message: str
    line: Optional[int] = None
    character: Optional[int] = None
    fix_suggestion: Optional[str] = None
    severity: SeverityLevel = SeverityLevel.WARNING
    offending_line: Optional[str] = None
    expected_pattern: Optional[str] = None
    auto_fixable: bool = False
    details: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert issue to dictionary format."""
        return {
            "category": self.category,
            "issue_type": self.issue_type.value,
            "file_path": self.file_path,
            "message": self.message,
            "line": self.line,
            "character": self.character,
            "fix_suggestion": self.fix_suggestion,
            "severity": self.severity.value,
            "offending_line": self.offending_line,
            "expected_pattern": self.expected_pattern,
            "auto_fixable": self.auto_fixable,
            "details": self.details,
        }

    def __str__(self) -> str:
        """String representation of the issue."""
        location = f"{self.file_path}"
        if self.line:
            location += f":{self.line}"
        if self.character:
            location += f":{self.character}"

        return f"[{self.severity.value.upper()}] {location} - {self.message}"
