

"""
Base Validator Class
Foundation for all validation implementations.
"""

from src.infrastructure.utils.common_imports import (
    Path,
    datetime,
    json,
    os,
    time
)
from collections import defaultdict
from typing import Dict, List, Optional, Union

from .issue_model import IssueType, SeverityLevel, ValidationIssue

# Integration: Enhanced validation errors
from src.infrastructure.utils.validation_errors import (
    ValidationError as Week2ValidationError,
    SecurityValidationError,
    ErrorCollector
)

class BaseValidator:
    """Base class for all validators with common functionality."""

    def __init__(
        self, root_path: Optional[Union[str, Path]] = None, shared_collector=None
    ):
        """Initialize base validator."""
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.issues: List[ValidationIssue] = []
        self.fixes_applied: List[str] = []
        self.start_time = time.time()

        # Load configuration
        self.config = self._load_config()

        # Initialize results structure
        self.results = {
            category: {"status": "pass", "errors": [], "warnings": []}
            for category in [
                "syntax",
                "imports",
                "dependencies",
                "structure",
                "architecture",
                "coverage",
                "security",
                "performance",
                "health",
                "configuration",
                "build",
                "documentation",
                "ai_analysis",
                "system",
                "nfr",  # Add NFR category
                "coding_standards",  # Add coding standards category
                "type_checking",  # Add type checking category
                "formatting",  # Add formatting category
                "code_quality",  # Add code quality category
                "quality_gates",  # Add quality gates category
                "quality",  # Add quality category
            ]
        }

        # File collections - use shared collector if provided
        self.shared_collector = shared_collector
        self.all_files: List[Path] = []
        self.python_files: List[Path] = []

    def _load_config(self) -> Dict:
        """Load validation configuration with defaults."""
        default_config = {
            "coverage_threshold": 85,
            "complexity_threshold": 10,
            "max_function_lines": 50,
            "max_file_lines": 500,
            "naming_conventions": {
                "files": r"^[a-z][a-z0-9_]*\.py$",
                "classes": r"^[A-Z][a-zA-Z0-9]*$",
                "functions": r"^(__[a-z][a-z0-9_]*__|_[a-z][a-z0-9_]*|[a-z][a-z0-9_]*)$",
                "constants": r"^[A-Z][A-Z0-9_]*$",
            },
            "forbidden_patterns": [
                r"TODO.*URGENT",
                r"FIXME.*ASAP",
                r"HACK.*REMOVE",
                r"XXX.*BROKEN",
            ],
            "secret_patterns": [
                r'(?i)api[_-]?key[_-]?[=:]\s*["\']?[a-z0-9]{20,}["\']?',
                r'(?i)secret[_-]?key[_-]?[=:]\s*["\']?[a-z0-9]{20,}["\']?',
                r'(?i)password[_-]?[=:]\s*["\']?[a-z0-9]{8,}["\']?',
                r'(?i)token[_-]?[=:]\s*["\']?[a-z0-9]{20,}["\']?',
            ],
            "excluded_dirs": {
                "__pycache__",
                ".git",
                ".pytest_cache",
                "htmlcov",
                "build",
                "dist",
                ".mypy_cache",
                ".tox",
                "venv",
                "env",
                "node_modules",
                ".next",
                ".nuxt",
                "backup",
            },
            "performance_thresholds": {
                "max_import_time": 1.0,
                "max_function_time": 0.1,
            },
        }

        # Try to load from config files
        config_paths = [
            self.root_path
            / "src"
            / "infrastructure"
            / "tools"
            / "validation"
            / "config"
            / "validation_config.json",
            self.root_path / "validation_config.json",
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        loaded_config = json.load(f)
                        default_config.update(loaded_config)
                        break
                except Exception as e:
                    print(f"Warning: Could not load config from {config_path}: {e}")

        return default_config

    def add_issue(
        self,
        category: str,
        issue_type: str,
        file_path: Union[str, Path],
        message: str,
        line: Optional[int] = None,
        character: Optional[int] = None,
        fix_suggestion: Optional[str] = None,
        severity: str = "warning",
        offending_line: Optional[str] = None,
        expected_pattern: Optional[str] = None,
        auto_fixable: bool = False,
    ):
        """Add a structured issue to the validation results."""

        # Convert string issue_type to enum if needed
        if isinstance(issue_type, str):
            try:
                issue_type_enum = IssueType(issue_type)
            except ValueError:
                issue_type_enum = IssueType.OTHER
        else:
            issue_type_enum = issue_type

        # Convert string severity to enum if needed
        if isinstance(severity, str):
            try:
                severity_enum = SeverityLevel(severity)
            except ValueError:
                severity_enum = SeverityLevel.WARNING
        else:
            severity_enum = severity

        issue = ValidationIssue(
            category=category,
            issue_type=issue_type_enum,
            file_path=str(file_path),
            message=message,
            line=line,
            character=character,
            fix_suggestion=fix_suggestion,
            severity=severity_enum,
            offending_line=offending_line,
            expected_pattern=expected_pattern,
            auto_fixable=auto_fixable,
        )

        self.issues.append(issue)

        # Update legacy results for backward compatibility
        if severity_enum == SeverityLevel.ERROR:
            self.results[category]["errors"].append(message)
            self.results[category]["status"] = "error"
        else:
            self.results[category]["warnings"].append(message)
            if self.results[category]["status"] == "pass":
                self.results[category]["status"] = "warning"

    def _collect_files(self):
        """Collect all files for validation using shared collector if available."""
        if self.shared_collector:
            # Use shared collector for performance
            files = self.shared_collector.get_files(self.root_path)
            self.all_files = files["all_files"]
            self.python_files = files["python_files"]
            print(
                f"Using shared collector: {len(self.all_files)} total files, {len(self.python_files)} Python files"
            )
        else:
            # Fallback to original collection method
            print("Collecting files...")

            for root, dirs, files in os.walk(self.root_path):
                # Remove excluded directories
                dirs[:] = [d for d in dirs if d not in self.config["excluded_dirs"]]

                for file in files:
                    file_path = Path(root) / file
                    self.all_files.append(file_path)

                    if file.endswith(".py"):
                        self.python_files.append(file_path)

            print(
                f"Found {len(self.all_files)} total files, {len(self.python_files)} Python files"
            )

    def get_python_files(self) -> List[Path]:
        """Get all Python files in the project."""
        if not self.python_files:
            self._collect_files()
        return self.python_files

    def has_errors(self) -> bool:
        """Check if any error-level issues were found."""
        from .issue_model import SeverityLevel
        return any(issue.severity == SeverityLevel.ERROR for issue in self.issues)

    def has_warnings(self) -> bool:
        """Check if any warning-level issues were found."""
        from .issue_model import SeverityLevel
        return any(issue.severity == SeverityLevel.WARNING for issue in self.issues)

    def get_issues_by_category(self, category: str) -> List[ValidationIssue]:
        """Get all issues for a specific category."""
        return [issue for issue in self.issues if issue.category == category]

    def get_issues_by_severity(self, severity: str) -> List[ValidationIssue]:
        """Get all issues with a specific severity level."""
        from .issue_model import SeverityLevel
        if isinstance(severity, str):
            severity_enum = SeverityLevel(severity)
        else:
            severity_enum = severity
        return [issue for issue in self.issues if issue.severity == severity_enum]

    def generate_json_report(self) -> Dict:
        """Generate machine-readable JSON report."""
        from .issue_model import SeverityLevel

        total_errors = len(
            [issue for issue in self.issues if issue.severity == SeverityLevel.ERROR]
        )
        total_warnings = len(
            [issue for issue in self.issues if issue.severity == SeverityLevel.WARNING]
        )

        if total_errors > 0:
            overall_status = "FAIL"
        elif total_warnings > 0:
            overall_status = "WARN"
        else:
            overall_status = "PASS"

        return {
            "meta": {
                "timestamp": datetime.now().isoformat(),
                "validator_version": "3.0.0",
                "validation_time": time.time() - self.start_time,
                "validator_type": self.__class__.__name__,
            },
            "summary": {
                "overall_status": overall_status,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "files_analyzed": len(self.all_files),
                "python_files_analyzed": len(self.python_files),
                "fixes_applied": len(self.fixes_applied),
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "fixes_applied": self.fixes_applied,
            "categories": {
                category: {
                    "status": self.results[category]["status"],
                    "error_count": len(
                        [
                            issue
                            for issue in self.issues
                            if issue.category == category
                            and issue.severity == SeverityLevel.ERROR
                        ]
                    ),
                    "warning_count": len(
                        [
                            issue
                            for issue in self.issues
                            if issue.category == category
                            and issue.severity == SeverityLevel.WARNING
                        ]
                    ),
                }
                for category in self.results.keys()
            },
        }


    def add_validation_error(self, error: Week2ValidationError, category: str = "validation"):
        """Add a Week 2 validation error to the issues list"""
        severity = "error" if isinstance(error, SecurityValidationError) else "warning"
        
        self.add_issue(
            category=category,
            issue_type="VALIDATION_ERROR",
            file_path=getattr(error, 'field', 'unknown'),
            message=error.message,
            severity=severity,
            fix_suggestion=getattr(error, 'details', {}).get('fix_suggestion'),
            auto_fixable=False
        )
    
    def validate_with_collector(self) -> ErrorCollector:
        """Create an error collector for batch validation"""
        return ErrorCollector()
    
    def enhance_issue_with_week2_context(self, issue: ValidationIssue, context: Dict):
        """Enhance existing issue with Week 2 validation context"""
        if issue.details is not None:
            issue.details.update(context)
        else:
            issue.details = context

    def print_summary(self):
        """Print a human-readable summary of validation results."""
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)

        from .issue_model import SeverityLevel
        total_errors = len(
            [issue for issue in self.issues if issue.severity == SeverityLevel.ERROR]
        )
        total_warnings = len(
            [issue for issue in self.issues if issue.severity == SeverityLevel.WARNING]
        )

        if total_errors == 0 and total_warnings == 0:
            print("✅ All validations passed! No issues found.")
            return

        print(f"Total Issues Found: {total_errors + total_warnings}")
        print(f"  Errors: {total_errors}")
        print(f"  Warnings: {total_warnings}")

        if total_errors > 0:
            print("  Status: FAIL (Critical errors found)")
        elif total_warnings > 0:
            print("  Status: WARN (Warnings found)")
        else:
            print("  Status: PASS")

        # Group issues by category
        categories = defaultdict(list)
        for issue in self.issues:
            categories[issue.category].append(issue)

        print("\nIssues by Category:")
        for category, issues in sorted(categories.items()):
            errors = [i for i in issues if i.severity == SeverityLevel.ERROR]
            warnings = [i for i in issues if i.severity == SeverityLevel.WARNING]
            print(
                f"  {category.title()}: {len(errors)} errors, {len(warnings)} warnings"
            )

        print("\n" + "=" * 80)
