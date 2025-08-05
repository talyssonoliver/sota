
from src.infrastructure.utils.common_imports import Path, re, time
"""
Performance Validator
Analyzes code performance patterns and suggests optimizations.
"""

import ast
# import re  # Consolidated to common_imports
# import time  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
from typing import Dict, List, Optional, Set

from .base_validator import BaseValidator
from .issue_model import IssueType, ValidationIssue


class PerformanceValidator(BaseValidator):
    """Validates code performance patterns and suggests optimizations."""

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize performance validator."""
        super().__init__(root_path)
        self.performance_issues: List[ValidationIssue] = []
        self.import_times: Dict[str, float] = {}
        self.complexity_scores: Dict[str, int] = {}

    def validate_performance(self) -> bool:
        """Run all performance validations."""
        if not self.python_files:
            self._collect_files()

        print("⚡ Analyzing performance patterns...")

        # Check function complexity
        self._check_function_complexity()

        # Check import performance
        self._check_import_performance()

        # Check for performance anti-patterns
        self._check_performance_antipatterns()

        # Check file sizes
        self._check_file_sizes()

        # Check for inefficient patterns
        self._check_inefficient_patterns()

        return not self.has_errors()

    def _check_function_complexity(self):
        """Check for overly complex functions."""
        max_complexity = self.config.get("complexity_threshold", 10)
        max_lines = self.config.get("max_function_lines", 50)

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Calculate cyclomatic complexity
                        complexity = self._calculate_complexity(node)
                        lines = (
                            (node.end_lineno - node.lineno)
                            if hasattr(node, "end_lineno") and node.end_lineno
                            else 0
                        )

                        if complexity > max_complexity:
                            self.add_issue(
                                category="performance",
                                issue_type=IssueType.HIGH_COMPLEXITY,
                                file_path=str(file_path),
                                message=f"Function '{node.name}' has high complexity ({complexity})",
                                line=node.lineno,
                                severity="warning",
                                fix_suggestion=f"Consider breaking down function into smaller pieces (current: {complexity}, max: {max_complexity})",
                                auto_fixable=False,
                            )

                        if lines > max_lines:
                            self.add_issue(
                                category="performance",
                                issue_type=IssueType.FUNCTION_TOO_LONG,
                                file_path=str(file_path),
                                message=f"Function '{node.name}' is too long ({lines} lines)",
                                line=node.lineno,
                                severity="warning",
                                fix_suggestion=f"Consider splitting function (current: {lines}, max: {max_lines})",
                                auto_fixable=False,
                            )

            except Exception as e:
                self.add_issue(
                    category="performance",
                    issue_type=IssueType.ANALYSIS_ERROR,
                    file_path=str(file_path),
                    message=f"Could not analyze complexity: {str(e)}",
                    severity="error",
                )

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ListComp):
                complexity += 1
            elif isinstance(child, ast.DictComp):
                complexity += 1
            elif isinstance(child, ast.SetComp):
                complexity += 1
            elif isinstance(child, ast.GeneratorExp):
                complexity += 1

        return complexity

    def _check_import_performance(self):
        """Check for slow imports."""
        max_import_time = self.config.get("performance_thresholds", {}).get(
            "max_import_time", 1.0
        )

        for file_path in self.python_files:
            try:
                imports = self._extract_imports(file_path)

                for import_name in imports:
                    import_time = self._measure_import_time(import_name)

                    if import_time > max_import_time:
                        self.add_issue(
                            category="performance",
                            issue_type=IssueType.PERFORMANCE_ISSUE,
                            file_path=str(file_path),
                            message=f"Slow import: {import_name} ({import_time:.3f}s)",
                            severity="warning",
                            fix_suggestion=f"Consider lazy loading or optimizing import of {import_name}",
                            auto_fixable=False,
                        )

            except Exception:
                continue  # Skip files with import errors

    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract import statements from file."""
        imports = set()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])
        except Exception:
            pass

        return imports

    def _measure_import_time(self, module_name: str) -> float:
        """Measure time taken to import a module."""
        if module_name in self.import_times:
            return self.import_times[module_name]

        try:
            start_time = time.time()
            __import__(module_name)
            import_time = time.time() - start_time
            self.import_times[module_name] = import_time
            return import_time
        except (Exception, SystemExit):
            # Module import failed or called sys.exit() - return 0 time
            return 0.0

    def _check_performance_antipatterns(self):
        """Check for common performance anti-patterns."""
        antipatterns = [
            (
                r"\.append\(.*\)\s*for\s+.*\s+in\s+.*",
                "Use list comprehension instead of append in loop",
            ),
            (
                r"len\([^)]+\)\s*>\s*0",
                'Use "if collection:" instead of "if len(collection) > 0"',
            ),
            (
                r"len\([^)]+\)\s*==\s*0",
                'Use "if not collection:" instead of "if len(collection) == 0"',
            ),
            (
                r"\.keys\(\)\s*in\s+for",
                "Iterate over dict directly instead of .keys()",
            ),
            (
                r"range\(len\([^)]+\)\)",
                "Use enumerate() instead of range(len())",
            ),
            (
                r"\.format\(.*\)",
                "Consider using f-strings for better performance",
            ),
            (r"import\s+\*", "Avoid wildcard imports for better performance"),
        ]

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    for pattern, suggestion in antipatterns:
                        if re.search(pattern, line):
                            self.add_issue(
                                category="performance",
                                issue_type=IssueType.PERFORMANCE_ISSUE,
                                file_path=str(file_path),
                                message=f"Performance anti-pattern detected: {line.strip()}",
                                line=i,
                                severity="info",
                                fix_suggestion=suggestion,
                                auto_fixable=False,
                            )

            except Exception:
                continue

    def _check_file_sizes(self):
        """Check for overly large files."""
        max_file_lines = self.config.get("max_file_lines", 500)

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    line_count = sum(1 for _ in f)

                if line_count > max_file_lines:
                    self.add_issue(
                        category="performance",
                        issue_type=IssueType.STRUCTURE_ISSUE,
                        file_path=str(file_path),
                        message=f"File too large ({line_count} lines)",
                        severity="warning",
                        fix_suggestion=f"Consider splitting large file (current: {line_count}, max: {max_file_lines})",
                        auto_fixable=False,
                    )

            except Exception:
                continue

    def _check_inefficient_patterns(self):
        """Check for inefficient coding patterns."""
        inefficient_patterns = [
            # String concatenation in loops
            (
                r"for\s+.*:\s*.*\+\=\s*.*",
                "Use join() for string concatenation in loops",
            ),
            # Nested loops with O(n²) complexity
            (r"for\s+.*:\s*.*for\s+.*:", "Consider optimizing nested loops"),
            # Global variable usage
            (r"global\s+\w+", "Avoid global variables for better performance"),
            # Inefficient dictionary access
            (
                r"if\s+\w+\s+in\s+.*\.keys\(\)",
                'Use "if key in dict" instead of "if key in dict.keys()"',
            ),
        ]

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    for pattern, suggestion in inefficient_patterns:
                        if re.search(pattern, line.strip()):
                            self.add_issue(
                                category="performance",
                                issue_type=IssueType.PERFORMANCE_ISSUE,
                                file_path=str(file_path),
                                message=f"Inefficient pattern: {line.strip()}",
                                line=i,
                                severity="info",
                                fix_suggestion=suggestion,
                                auto_fixable=False,
                            )

            except Exception:
                continue

    def get_performance_report(self) -> Dict:
        """Generate performance analysis report."""
        return {
            "total_files_analyzed": len(self.python_files),
            "performance_issues": len(
                [i for i in self.issues if i.category == "performance"]
            ),
            "complexity_issues": len(
                [i for i in self.issues if i.issue_type == IssueType.HIGH_COMPLEXITY]
            ),
            "import_performance": self.import_times,
            "complexity_scores": self.complexity_scores,
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        # Check for common improvement areas
        if len([i for i in self.issues if "complexity" in i.message.lower()]) > 0:
            recommendations.append(
                "Consider refactoring complex functions into smaller, more focused functions"
            )

        if len([i for i in self.issues if "import" in i.message.lower()]) > 0:
            recommendations.append("Consider lazy loading or optimizing slow imports")

        if len([i for i in self.issues if "too long" in i.message.lower()]) > 0:
            recommendations.append(
                "Break down large functions to improve readability and performance"
            )

        return recommendations
