"""
Structure Validator
Validates project structure, naming conventions, and documentation standards.
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Optional

from .base_validator import BaseValidator


class StructureValidator(BaseValidator):
    """Validates project structure and naming conventions."""

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize structure validator."""
        super().__init__(root_path)
        self.python_files: List[Path] = []

    def _is_valid_python_filename(self, filename: str) -> bool:
        """Check if filename follows Python naming conventions."""
        if not filename.endswith(".py"):
            return False

        # Remove .py extension for name validation
        name = filename[:-3]

        # Check for valid Python identifier pattern (lowercase with underscores)
        # Allow __init__.py and other dunder files
        if name.startswith("__") and name.endswith("__"):
            return True

        # Regular Python module names should be lowercase with underscores
        return re.match(r"^[a-z][a-z0-9_]*$", name) is not None

    def validate_structure(self) -> bool:
        """Validate file and folder structure."""
        self.python_files = self.get_python_files()

        # Check for empty directories
        self._validate_empty_directories()

        # Check naming conventions
        self._validate_naming_conventions()

        # Check documentation
        self._validate_documentation()

        # Check test coverage indicators
        self._validate_test_coverage()

        return not self.has_errors()

    def _validate_empty_directories(self):
        """Check for empty directories."""
        for root, dirs, files in os.walk(self.root_path):
            if not dirs and not files:
                rel_path = str(Path(root).relative_to(self.root_path))
                if rel_path not in self.config.get("excluded_dirs", []):
                    self.add_issue(
                        category="structure",
                        issue_type="EMPTY_DIRECTORY",
                        file_path=root,
                        message=f"Empty directory: {rel_path}",
                        severity="warning",
                        fix_suggestion="Remove empty directory or add placeholder file",
                        auto_fixable=True,
                    )

    def _validate_naming_conventions(self):
        """Check naming conventions for files, classes, and functions."""
        naming_config = self.config.get("naming_conventions", {})

        for file_path in self.python_files:
            file_name = file_path.name

            # Check file naming
            if "files" in naming_config:
                if not re.match(naming_config["files"], file_name):
                    self.add_issue(
                        category="structure",
                        issue_type="FILE_NAMING_CONVENTION",
                        file_path=str(file_path),
                        message=f"File name doesn't follow convention: {file_name}",
                        severity="warning",
                        fix_suggestion=f"Rename to follow pattern: {naming_config['files']}",
                        auto_fixable=True,
                        expected_pattern=naming_config["files"],
                    )

            # Check class and function naming
            self._validate_code_naming(file_path, naming_config)

    def _validate_code_naming(self, file_path: Path, naming_config: dict):
        """Validate naming conventions for classes and functions in a file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if "classes" in naming_config:
                        if not re.match(naming_config["classes"], node.name):
                            self.add_issue(
                                category="structure",
                                issue_type="CLASS_NAMING_CONVENTION",
                                file_path=str(file_path),
                                message=f"Class '{node.name}' doesn't follow naming convention",
                                line=getattr(node, "lineno", None),
                                severity="warning",
                                fix_suggestion=f"Rename class to follow pattern: {naming_config['classes']}",
                                auto_fixable=True,
                                expected_pattern=naming_config["classes"],
                                offending_line=f"class {node.name}",
                            )

                elif isinstance(node, ast.FunctionDef):
                    if "functions" in naming_config:
                        if not re.match(naming_config["functions"], node.name):
                            self.add_issue(
                                category="structure",
                                issue_type="FUNCTION_NAMING_CONVENTION",
                                file_path=str(file_path),
                                message=f"Function '{node.name}' doesn't follow naming convention",
                                line=getattr(node, "lineno", None),
                                severity="warning",
                                fix_suggestion=f"Rename function to follow pattern: {naming_config['functions']}",
                                auto_fixable=True,
                                expected_pattern=naming_config["functions"],
                                offending_line=f"def {node.name}",
                            )

        except Exception as e:
            self.add_issue(
                category="structure",
                issue_type="NAMING_VALIDATION_ERROR",
                file_path=str(file_path),
                message=f"Error validating naming conventions: {e}",
                severity="warning",
            )

    def _validate_documentation(self):
        """Check for missing documentation."""
        undocumented_items = []

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if not ast.get_docstring(node) and not node.name.startswith(
                            "_"
                        ):
                            undocumented_items.append(
                                (file_path, node.name, node.lineno)
                            )

            except Exception:
                continue

        # Report undocumented items (limit to avoid spam)
        for file_path, name, line_no in undocumented_items[:20]:
            self.add_issue(
                category="documentation",
                issue_type="MISSING_DOCSTRING",
                file_path=str(file_path),
                message=f"Missing docstring for '{name}'",
                line=line_no,
                severity="warning",
                fix_suggestion=f"Add docstring to document the purpose of '{name}'",
            )

        if len(undocumented_items) > 20:
            self.add_issue(
                category="documentation",
                issue_type="DOCUMENTATION_COVERAGE",
                file_path=str(self.root_path),
                message=f"Found {len(undocumented_items)} undocumented items in total",
                severity="info",
            )

    def _validate_test_coverage(self):
        """Check for test coverage indicators."""
        test_files = [f for f in self.python_files if "test" in str(f).lower()]
        src_files = [
            f
            for f in self.python_files
            if str(f).startswith(str(self.root_path / "src"))
        ]

        if src_files:
            coverage_ratio = len(test_files) / len(src_files) * 100
            coverage_threshold = self.config.get("coverage_threshold", 50)

            if coverage_ratio < coverage_threshold:
                self.add_issue(
                    category="coverage",
                    issue_type="LOW_TEST_COVERAGE",
                    file_path=str(self.root_path),
                    message=f"Test coverage appears low: {coverage_ratio:.1f}% (threshold: {coverage_threshold}%)",
                    severity="warning",
                    fix_suggestion="Add more test files to improve coverage",
                )

    def validate_security_patterns(self):
        """Validate security patterns and detect potential issues."""
        security_patterns = self.config.get("security_patterns", {})

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for potential security issues
                self._check_security_patterns(file_path, content, security_patterns)

            except Exception as e:
                self.add_issue(
                    category="security",
                    issue_type="SECURITY_SCAN_ERROR",
                    file_path=str(file_path),
                    message=f"Error scanning for security issues: {e}",
                    severity="warning",
                )

    def _check_security_patterns(
        self, file_path: Path, content: str, security_patterns: dict
    ):
        """Check for security anti-patterns in code."""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()

            # Check for hardcoded secrets
            if any(
                pattern in line_lower
                for pattern in ["password", "secret", "key", "token"]
            ):
                if "=" in line and not line.strip().startswith("#"):
                    self.add_issue(
                        category="security",
                        issue_type="POTENTIAL_HARDCODED_SECRET",
                        file_path=str(file_path),
                        message="Potential hardcoded secret detected",
                        line=line_num,
                        severity="warning",
                        fix_suggestion="Move secrets to environment variables or config files",
                        offending_line=line.strip(),
                    )

            # Check for eval/exec usage
            if "eval(" in line or "exec(" in line:
                self.add_issue(
                    category="security",
                    issue_type="DANGEROUS_FUNCTION_USAGE",
                    file_path=str(file_path),
                    message="Potentially dangerous function usage (eval/exec)",
                    line=line_num,
                    severity="error",
                    fix_suggestion="Avoid using eval() or exec() - use safer alternatives",
                    offending_line=line.strip(),
                )

            # Check for shell injection risks
            if "subprocess" in line and "shell=True" in line:
                self.add_issue(
                    category="security",
                    issue_type="SHELL_INJECTION_RISK",
                    file_path=str(file_path),
                    message="Potential shell injection risk",
                    line=line_num,
                    severity="warning",
                    fix_suggestion="Avoid shell=True in subprocess calls",
                    offending_line=line.strip(),
                )

    def get_structure_summary(self) -> dict:
        """Get a summary of structure validation results."""
        return {
            "total_files": len(self.python_files),
            "total_issues": len(self.issues),
            "error_count": len([i for i in self.issues if i.severity == "error"]),
            "warning_count": len([i for i in self.issues if i.severity == "warning"]),
            "auto_fixable_count": len([i for i in self.issues if i.auto_fixable]),
        }

    def validate_file(self, file_path: Path) -> List:
        """Validate a single file for structure issues."""
        if not file_path.exists() or file_path.suffix != ".py":
            return []

        old_issues_count = len(self.issues)

        # Validate naming conventions for this file
        self._validate_file_naming(file_path)

        # Validate documentation for this file
        self._validate_file_documentation(file_path)

        # Validate security patterns for this file
        self._validate_file_security(file_path)

        # Return new issues for this file
        new_issues = self.issues[old_issues_count:]
        return new_issues

    def _validate_file_naming(self, file_path: Path):
        """Validate naming conventions for a single file."""
        if not self._is_valid_python_filename(file_path.name):
            self.add_issue(
                category="structure",
                issue_type="NAMING_CONVENTION",
                file_path=str(file_path),
                message=f"File name '{file_path.name}' doesn't follow Python naming conventions",
                severity="warning",
                fix_suggestion="Use lowercase with underscores (e.g., my_module.py)",
            )

    def _validate_file_documentation(self, file_path: Path):
        """Validate documentation for a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for module docstring
            tree = ast.parse(content)
            if not (
                tree.body
                and isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)
            ):
                self.add_issue(
                    category="structure",
                    issue_type="MISSING_DOCSTRING",
                    file_path=str(file_path),
                    message="Module missing docstring",
                    severity="warning",
                    fix_suggestion="Add module docstring at the top of the file",
                )
        except Exception:
            pass  # Skip files that can't be parsed

    def _validate_file_security(self, file_path: Path):
        """Validate security patterns for a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Check for potential security issues
                if "subprocess.call" in line and "shell=True" in line:
                    self.add_issue(
                        category="security",
                        issue_type="SECURITY_ISSUE",
                        file_path=str(file_path),
                        message="Potential security risk: subprocess with shell=True",
                        line=line_num,
                        severity="warning",
                        fix_suggestion="Avoid shell=True in subprocess calls",
                        offending_line=line.strip(),
                    )
        except Exception:
            pass  # Skip files that can't be read

    def validate(self, files: List[Path]) -> List:
        """Validate structure for the given files."""
        issues = []
        for file_path in files:
            file_issues = self.validate_file(file_path)
            issues.extend(file_issues)
        return issues
