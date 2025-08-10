
from src.infrastructure.utils.common_imports import (
    Any,
    Dict,
    Enum,
    List,
    Optional,
    Path,
    dataclass,
    json,
    re,
    time
)
"""
Non-Functional Requirements (NFR) Validator
Implements NFR validation for security, performance, maintainability, reliability,
usability, and portability based on ISO/IEC 25010.
"""

import ast
# import json  # Consolidated to common_imports
# import re  # Consolidated to common_imports
# import time  # Consolidated to common_imports
# from dataclasses import dataclass  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
# from typing import Any, Dict, List, Optional  # Consolidated to common_imports

import psutil

from .base_validator import BaseValidator


class NFRCategory(Enum):
    """Non-functional requirement categories based on ISO/IEC 25010."""

    SECURITY = "security"
    PERFORMANCE_EFFICIENCY = "performance_efficiency"
    MAINTAINABILITY = "maintainability"
    RELIABILITY = "reliability"
    USABILITY = "usability"
    COMPATIBILITY = "compatibility"
    PORTABILITY = "portability"


@dataclass
class NFRMetric:
    """Non-functional requirement metric."""

    name: str
    category: NFRCategory
    measurement_unit: str
    threshold_value: float
    operator: str  # ">=", "<=", "==", "!=", ">", "<"
    severity: str
    description: str


@dataclass
class PerformanceProfile:
    """Performance profiling result."""

    function_name: str
    file_path: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    calls_count: int
    complexity_score: float


@dataclass
class NFRViolation:
    """Non-functional requirement violation."""

    category: str
    severity: str
    description: str
    file_path: str
    line_number: int
    metric_name: str
    actual_value: float
    expected_value: float
    remediation_suggestion: str


@dataclass
class SecurityMetric:
    """Security metric definition."""

    name: str
    value: float
    unit: str
    category: str
    threshold: float
    status: str


@dataclass
class MaintainabilityMetric:
    """Maintainability metric definition."""

    name: str
    value: float
    unit: str
    category: str
    threshold: float
    status: str


class NFRValidator(BaseValidator):
    """Non-Functional Requirements validator implementing ISO/IEC 25010 standards."""

    def __init__(self, root_path: Optional[Path] = None):
        super().__init__(root_path)
        self.nfr_metrics = self._load_nfr_metrics()
        self.nfr_categories = self._load_nfr_categories()
        self.performance_profiles: List[PerformanceProfile] = []
        self.security_metrics: Dict[str, Any] = {}
        self.maintainability_metrics: Dict[str, Any] = {}
        self.nfr_violations: List[NFRViolation] = []

    def _load_nfr_metrics(self) -> List[NFRMetric]:
        """Load NFR metrics based on ISO/IEC 25010."""
        return [
            # Security NFRs
            NFRMetric(
                name="authentication_coverage",
                category=NFRCategory.SECURITY,
                measurement_unit="percentage",
                threshold_value=100.0,
                operator="==",
                severity="error",
                description="All protected endpoints must have authentication",
            ),
            NFRMetric(
                name="input_validation_coverage",
                category=NFRCategory.SECURITY,
                measurement_unit="percentage",
                threshold_value=95.0,
                operator=">=",
                severity="error",
                description="Input validation coverage must be at least 95%",
            ),
            NFRMetric(
                name="encryption_usage",
                category=NFRCategory.SECURITY,
                measurement_unit="percentage",
                threshold_value=100.0,
                operator="==",
                severity="error",
                description="All sensitive data must be encrypted",
            ),
            # Performance Efficiency NFRs
            NFRMetric(
                name="response_time",
                category=NFRCategory.PERFORMANCE_EFFICIENCY,
                measurement_unit="milliseconds",
                threshold_value=200.0,
                operator="<=",
                severity="warning",
                description="Average response time should be under 200ms",
            ),
            NFRMetric(
                name="memory_usage",
                category=NFRCategory.PERFORMANCE_EFFICIENCY,
                measurement_unit="megabytes",
                threshold_value=512.0,
                operator="<=",
                severity="warning",
                description="Memory usage should be under 512MB",
            ),
            NFRMetric(
                name="cpu_usage",
                category=NFRCategory.PERFORMANCE_EFFICIENCY,
                measurement_unit="percentage",
                threshold_value=80.0,
                operator="<=",
                severity="warning",
                description="CPU usage should be under 80%",
            ),
            # Maintainability NFRs
            NFRMetric(
                name="cyclomatic_complexity",
                category=NFRCategory.MAINTAINABILITY,
                measurement_unit="score",
                threshold_value=10.0,
                operator="<=",
                severity="warning",
                description="Cyclomatic complexity should be under 10",
            ),
            NFRMetric(
                name="code_duplication",
                category=NFRCategory.MAINTAINABILITY,
                measurement_unit="percentage",
                threshold_value=5.0,
                operator="<=",
                severity="warning",
                description="Code duplication should be under 5%",
            ),
            NFRMetric(
                name="documentation_coverage",
                category=NFRCategory.MAINTAINABILITY,
                measurement_unit="percentage",
                threshold_value=80.0,
                operator=">=",
                severity="warning",
                description="Documentation coverage should be at least 80%",
            ),
            # Reliability NFRs
            NFRMetric(
                name="error_handling_coverage",
                category=NFRCategory.RELIABILITY,
                measurement_unit="percentage",
                threshold_value=90.0,
                operator=">=",
                severity="error",
                description="Error handling coverage should be at least 90%",
            ),
            NFRMetric(
                name="test_coverage",
                category=NFRCategory.RELIABILITY,
                measurement_unit="percentage",
                threshold_value=80.0,
                operator=">=",
                severity="error",
                description="Test coverage should be at least 80%",
            ),
            # Usability NFRs
            NFRMetric(
                name="api_consistency",
                category=NFRCategory.USABILITY,
                measurement_unit="score",
                threshold_value=95.0,
                operator=">=",
                severity="warning",
                description="API design consistency should be at least 95%",
            ),
            NFRMetric(
                name="error_message_clarity",
                category=NFRCategory.USABILITY,
                measurement_unit="score",
                threshold_value=90.0,
                operator=">=",
                severity="warning",
                description="Error messages should be clear and actionable",
            ),
            # Portability NFRs
            NFRMetric(
                name="platform_compatibility",
                category=NFRCategory.PORTABILITY,
                measurement_unit="percentage",
                threshold_value=95.0,
                operator=">=",
                severity="warning",
                description="Platform compatibility should be at least 95%",
            ),
            NFRMetric(
                name="dependency_portability",
                category=NFRCategory.PORTABILITY,
                measurement_unit="score",
                threshold_value=90.0,
                operator=">=",
                severity="warning",
                description="Dependencies should be portable across platforms",
            ),
        ]

    def run_nfr_validation(self) -> bool:
        """Run comprehensive NFR validation."""
        print("🏗️ Running Non-Functional Requirements Validation...")

        if not self.python_files:
            self._collect_files()

        # 1. Security NFR validation
        self._validate_security_nfrs()

        # 2. Performance efficiency validation
        self._validate_performance_nfrs()

        # 3. Maintainability validation
        self._validate_maintainability_nfrs()

        # 4. Reliability validation
        self._validate_reliability_nfrs()

        # 5. Usability validation
        self._validate_usability_nfrs()

        # 6. Portability validation
        self._validate_portability_nfrs()

        return not self.has_errors()

    def _validate_security_nfrs(self):
        """Validate security non-functional requirements."""
        print("  🔒 Validating Security NFRs...")

        # Check authentication coverage
        auth_coverage = self._calculate_authentication_coverage()
        self._check_nfr_metric("authentication_coverage", auth_coverage)

        # Check input validation coverage
        validation_coverage = self._calculate_input_validation_coverage()
        self._check_nfr_metric("input_validation_coverage", validation_coverage)

        # Check encryption usage
        encryption_usage = self._calculate_encryption_usage()
        self._check_nfr_metric("encryption_usage", encryption_usage)

        self.security_metrics = {
            "authentication_coverage": auth_coverage,
            "input_validation_coverage": validation_coverage,
            "encryption_usage": encryption_usage,
        }

    def _calculate_authentication_coverage(self) -> float:
        """Calculate authentication coverage percentage."""
        protected_endpoints = 0
        authenticated_endpoints = 0

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for API endpoints/routes
                endpoint_patterns = [
                    r"@app\.route\(",
                    r"@api\.route\(",
                    r"def\s+\w+.*\(.*request",
                    r"class.*View.*:",
                    r"@require_auth",
                    r"@login_required",
                ]

                auth_patterns = [
                    r"@require_auth",
                    r"@login_required",
                    r"authenticate\(",
                    r"check_auth\(",
                    r"verify_token\(",
                ]

                lines = content.split("\n")
                for i, line in enumerate(lines):
                    # Check if line defines an endpoint
                    if any(re.search(pattern, line) for pattern in endpoint_patterns):
                        protected_endpoints += 1

                        # Check if this endpoint or nearby lines have authentication
                        auth_context = lines[max(0, i - 3) : min(len(lines), i + 3)]
                        if any(
                            any(
                                re.search(auth_pattern, context_line)
                                for auth_pattern in auth_patterns
                            )
                            for context_line in auth_context
                        ):
                            authenticated_endpoints += 1

            except Exception:
                continue

        return (
            (authenticated_endpoints / protected_endpoints * 100)
            if protected_endpoints > 0
            else 100.0
        )

    def _calculate_input_validation_coverage(self) -> float:
        """Calculate input validation coverage percentage."""
        input_points = 0
        validated_inputs = 0

        validation_patterns = [
            r"validate\(",
            r"clean\(",
            r"sanitize\(",
            r"isinstance\(",
            r"type\s*==",
            r"\.is_valid\(\)",
            r"schema\.validate\(",
        ]

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    # Look for function parameters (input points)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if len(node.args.args) > 1:  # Exclude 'self'
                            input_points += len(node.args.args) - 1

                            # Check function body for validation
                            func_source = ast.get_source_segment(content, node)
                            if func_source and any(
                                re.search(pattern, func_source)
                                for pattern in validation_patterns
                            ):
                                validated_inputs += len(node.args.args) - 1

            except Exception:
                continue

        return (validated_inputs / input_points * 100) if input_points > 0 else 100.0

    def _calculate_encryption_usage(self) -> float:
        """Calculate encryption usage for sensitive data."""
        sensitive_data_points = 0
        encrypted_data_points = 0

        sensitive_patterns = [
            r"password",
            r"secret",
            r"key",
            r"token",
            r"credential",
            r"private",
            r"confidential",
        ]

        encryption_patterns = [
            r"encrypt\(",
            r"hash\(",
            r"bcrypt",
            r"scrypt",
            r"pbkdf2",
            r"AES\.",
            r"RSA\.",
            r"cryptography\.",
        ]

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")
                for line in lines:
                    # Check for sensitive data
                    if any(
                        re.search(pattern, line, re.IGNORECASE)
                        for pattern in sensitive_patterns
                    ):
                        sensitive_data_points += 1

                        # Check if encryption is used
                        if any(
                            re.search(pattern, line) for pattern in encryption_patterns
                        ):
                            encrypted_data_points += 1

            except Exception:
                continue

        return (
            (encrypted_data_points / sensitive_data_points * 100)
            if sensitive_data_points > 0
            else 100.0
        )

    def _validate_performance_nfrs(self):
        """Validate performance efficiency NFRs."""
        print("  ⚡ Validating Performance Efficiency NFRs...")

        # Profile performance
        self._profile_performance()

        if self.performance_profiles:
            avg_response_time = sum(
                p.execution_time for p in self.performance_profiles
            ) / len(self.performance_profiles)
            avg_memory_usage = sum(
                p.memory_usage for p in self.performance_profiles
            ) / len(self.performance_profiles)
            avg_cpu_usage = sum(p.cpu_usage for p in self.performance_profiles) / len(
                self.performance_profiles
            )

            self._check_nfr_metric(
                "response_time", avg_response_time * 1000
            )  # Convert to ms
            self._check_nfr_metric("memory_usage", avg_memory_usage)
            self._check_nfr_metric("cpu_usage", avg_cpu_usage)

    def _profile_performance(self):
        """Profile performance of key functions."""
        try:
            # Simple performance profiling using basic metrics
            process = psutil.Process()
            
            # Get actual system metrics using the process instance
            try:
                system_cpu_percent = process.cpu_percent(interval=0.1)
                memory_info = process.memory_info()
                system_memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
            except Exception:
                # Fallback to estimated values if system monitoring fails
                system_cpu_percent = 0.0
                system_memory_mb = 0.0

            for file_path in self.python_files[:5]:  # Limit to first 5 files for demo
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            # Calculate basic complexity score
                            complexity = self._calculate_function_complexity(node)

                            # Use real system metrics when available, otherwise estimate based on complexity
                            if system_cpu_percent > 0 or system_memory_mb > 0:
                                # Scale system metrics by function complexity
                                estimated_time = (complexity * 0.001) + (system_cpu_percent * 0.0001)
                                estimated_memory = max(complexity * 0.5, system_memory_mb / 100)
                                estimated_cpu = min(system_cpu_percent + (complexity * 2), 100)
                            else:
                                # Fallback to complexity-based estimation
                                estimated_time = (complexity * 0.001)  # 1ms per complexity point
                                estimated_memory = (complexity * 0.5)  # 0.5MB per complexity point
                                estimated_cpu = min(complexity * 2, 100)  # Max 100% CPU

                            profile = PerformanceProfile(
                                function_name=node.name,
                                file_path=str(file_path),
                                execution_time=estimated_time,
                                memory_usage=estimated_memory,
                                cpu_usage=estimated_cpu,
                                calls_count=1,
                                complexity_score=complexity,
                            )

                            self.performance_profiles.append(profile)

                except Exception:
                    continue

        except Exception:
            pass

    def _calculate_function_complexity(self, node: ast.AST) -> float:
        """Calculate function complexity score."""
        complexity = 1.0

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 0.5
            elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp)):
                complexity += 0.5

        return complexity

    def _validate_maintainability_nfrs(self):
        """Validate maintainability NFRs."""
        print("  🛠️ Validating Maintainability NFRs...")

        # Calculate cyclomatic complexity
        avg_complexity = self._calculate_average_complexity()
        self._check_nfr_metric("cyclomatic_complexity", avg_complexity)

        # Calculate code duplication
        duplication_percentage = self._calculate_code_duplication()
        self._check_nfr_metric("code_duplication", duplication_percentage)

        # Calculate documentation coverage
        doc_coverage = self._calculate_documentation_coverage()
        self._check_nfr_metric("documentation_coverage", doc_coverage)

        self.maintainability_metrics = {
            "average_complexity": avg_complexity,
            "duplication_percentage": duplication_percentage,
            "documentation_coverage": doc_coverage,
        }

    def _calculate_average_complexity(self) -> float:
        """Calculate average cyclomatic complexity."""
        complexities = []

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        complexity = self._calculate_function_complexity(node)
                        complexities.append(complexity)

            except Exception:
                continue

        return sum(complexities) / len(complexities) if complexities else 0.0

    def _calculate_code_duplication(self) -> float:
        """Calculate code duplication percentage."""
        line_hashes = {}
        total_lines = 0
        duplicated_lines = 0

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                for line in lines:
                    normalized = line.strip()
                    if normalized and not normalized.startswith("#"):
                        total_lines += 1
                        line_hash = hash(normalized)

                        if line_hash in line_hashes:
                            line_hashes[line_hash] += 1
                            if line_hashes[line_hash] == 2:
                                duplicated_lines += 2
                            else:
                                duplicated_lines += 1
                        else:
                            line_hashes[line_hash] = 1

            except Exception:
                continue

        return (duplicated_lines / total_lines * 100) if total_lines > 0 else 0.0

    def _calculate_documentation_coverage(self) -> float:
        """Calculate documentation coverage percentage."""
        total_functions = 0
        documented_functions = 0

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(
                        node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                    ):
                        if not node.name.startswith(
                            "_"
                        ):  # Only public functions/classes
                            total_functions += 1
                            if ast.get_docstring(node):
                                documented_functions += 1

            except Exception:
                continue

        return (
            (documented_functions / total_functions * 100)
            if total_functions > 0
            else 100.0
        )

    def _validate_reliability_nfrs(self):
        """Validate reliability NFRs."""
        print("  🔧 Validating Reliability NFRs...")

        # Calculate error handling coverage
        error_coverage = self._calculate_error_handling_coverage()
        self._check_nfr_metric("error_handling_coverage", error_coverage)

        # Calculate test coverage (if available)
        test_coverage = self._get_test_coverage()
        if test_coverage is not None:
            self._check_nfr_metric("test_coverage", test_coverage)

    def _calculate_error_handling_coverage(self) -> float:
        """Calculate error handling coverage percentage."""
        total_functions = 0
        functions_with_error_handling = 0

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        total_functions += 1

                        # Check for error handling constructs
                        has_try_except = any(
                            isinstance(child, ast.Try) for child in ast.walk(node)
                        )
                        has_raises = any(
                            isinstance(child, ast.Raise) for child in ast.walk(node)
                        )

                        if has_try_except or has_raises:
                            functions_with_error_handling += 1

            except Exception:
                continue

        return (
            (functions_with_error_handling / total_functions * 100)
            if total_functions > 0
            else 0.0
        )

    def _get_test_coverage(self) -> Optional[float]:
        """Get test coverage from coverage report."""
        coverage_file = self.root_path / "coverage.json"
        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                return coverage_data.get("totals", {}).get("percent_covered", 0.0)
            except Exception:
                pass
        return None

    def _validate_usability_nfrs(self):
        """Validate usability NFRs."""
        print("  👤 Validating Usability NFRs...")

        # Calculate API consistency
        api_consistency = self._calculate_api_consistency()
        self._check_nfr_metric("api_consistency", api_consistency)

        # Calculate error message clarity
        error_clarity = self._calculate_error_message_clarity()
        self._check_nfr_metric("error_message_clarity", error_clarity)

    def _calculate_api_consistency(self) -> float:
        """Calculate API design consistency score."""
        # Simple heuristic based on naming conventions and patterns
        consistent_patterns = 0
        total_patterns = 0

        naming_patterns = {"functions": [], "classes": [], "variables": []}

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        naming_patterns["functions"].append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        naming_patterns["classes"].append(node.name)

            except Exception:
                continue

        # Check consistency of naming conventions
        for pattern_type, names in naming_patterns.items():
            if names:
                total_patterns += len(names)

                if pattern_type == "functions":
                    # Check snake_case consistency
                    snake_case_count = sum(
                        1 for name in names if re.match(r"^[a-z][a-z0-9_]*$", name)
                    )
                    consistent_patterns += snake_case_count
                elif pattern_type == "classes":
                    # Check PascalCase consistency
                    pascal_case_count = sum(
                        1 for name in names if re.match(r"^[A-Z][a-zA-Z0-9]*$", name)
                    )
                    consistent_patterns += pascal_case_count

        return (
            (consistent_patterns / total_patterns * 100)
            if total_patterns > 0
            else 100.0
        )

    def _calculate_error_message_clarity(self) -> float:
        """Calculate error message clarity score."""
        clear_messages = 0
        total_messages = 0

        clarity_indicators = [
            r"Invalid",
            r"Expected",
            r"Please",
            r"Error:",
            r"Failed to",
            r"Cannot",
            r"Unable to",
        ]

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for exception messages and error strings
                error_patterns = [
                    r'raise\s+\w+Exception\s*\(\s*["\']([^"\']+)["\']',
                    r'ValueError\s*\(\s*["\']([^"\']+)["\']',
                    r'RuntimeError\s*\(\s*["\']([^"\']+)["\']',
                    r'TypeError\s*\(\s*["\']([^"\']+)["\']',
                ]

                for pattern in error_patterns:
                    matches = re.findall(pattern, content)
                    for message in matches:
                        total_messages += 1
                        if any(
                            re.search(indicator, message, re.IGNORECASE)
                            for indicator in clarity_indicators
                        ):
                            clear_messages += 1

            except Exception:
                continue

        return (clear_messages / total_messages * 100) if total_messages > 0 else 100.0

    def _validate_portability_nfrs(self):
        """Validate portability NFRs."""
        print("  🌐 Validating Portability NFRs...")

        # Calculate platform compatibility
        platform_compatibility = self._calculate_platform_compatibility()
        self._check_nfr_metric("platform_compatibility", platform_compatibility)

        # Calculate dependency portability
        dependency_portability = self._calculate_dependency_portability()
        self._check_nfr_metric("dependency_portability", dependency_portability)

    def _calculate_platform_compatibility(self) -> float:
        """Calculate platform compatibility score."""
        platform_specific_code = 0
        total_platform_checks = 0
        portable_implementations = 0

        platform_patterns = [
            r"sys\.platform",
            r"os\.name",
            r"platform\.",
            r"windows",
            r"linux",
            r"darwin",
            r"win32",
        ]

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")
                for line in lines:
                    if any(
                        re.search(pattern, line, re.IGNORECASE)
                        for pattern in platform_patterns
                    ):
                        total_platform_checks += 1

                        # Check if there's proper abstraction/fallback
                        if any(
                            keyword in line.lower()
                            for keyword in ["if", "else", "elif", "try", "except"]
                        ):
                            portable_implementations += 1

            except Exception:
                continue

        # If no platform-specific code, assume high portability
        if total_platform_checks == 0:
            return 95.0
        
        # Include platform_specific_code in the calculation
        compatibility_score = (portable_implementations / total_platform_checks * 100)
        
        # Adjust score based on amount of platform-specific code found
        if platform_specific_code > 0:
            # Reduce score if there's unhandled platform-specific code
            unhandled_platform_code = max(0, platform_specific_code - portable_implementations)
            penalty = (unhandled_platform_code / total_platform_checks) * 20  # Up to 20% penalty
            compatibility_score = max(0, compatibility_score - penalty)

        return compatibility_score

    def _calculate_dependency_portability(self) -> float:
        """Calculate dependency portability score."""
        requirements_file = self.root_path / "requirements.txt"
        if not requirements_file.exists():
            return 90.0  # Assume good if no requirements file

        try:
            with open(requirements_file, "r") as f:
                dependencies = f.readlines()

            total_deps = 0
            portable_deps = 0

            # Known problematic dependencies for portability
            non_portable_patterns = [
                r"win.*",
                r".*-win32",
                r".*-linux",
                r".*-darwin",
                r"windows-curses",
            ]

            for dep in dependencies:
                dep = dep.strip()
                if dep and not dep.startswith("#"):
                    total_deps += 1

                    # Check if dependency is platform-specific
                    is_portable = not any(
                        re.match(pattern, dep, re.IGNORECASE)
                        for pattern in non_portable_patterns
                    )

                    if is_portable:
                        portable_deps += 1

            return (portable_deps / total_deps * 100) if total_deps > 0 else 90.0

        except Exception:
            return 90.0

    def _check_nfr_metric(self, metric_name: str, actual_value: float):
        """Check NFR metric against threshold."""
        metric = next((m for m in self.nfr_metrics if m.name == metric_name), None)
        if not metric:
            return

        passed = self._evaluate_condition(
            actual_value, metric.operator, metric.threshold_value
        )

        if not passed:
            self.add_issue(
                category="nfr",
                issue_type="NFR_VIOLATION",
                file_path="system",
                message=f"NFR violation: {metric.description} (Actual: {actual_value:.2f} {metric.measurement_unit})",
                severity=metric.severity,
                fix_suggestion=f"Improve {metric.name} to meet threshold of {metric.threshold_value} {metric.measurement_unit}",
                auto_fixable=False,
            )

    def _evaluate_condition(
        self, actual: float, operator: str, expected: float
    ) -> bool:
        """Evaluate NFR condition."""
        if operator == ">=":
            return actual >= expected
        elif operator == "<=":
            return actual <= expected
        elif operator == "==":
            return abs(actual - expected) < 0.01  # Float comparison
        elif operator == "!=":
            return abs(actual - expected) >= 0.01
        elif operator == ">":
            return actual > expected
        elif operator == "<":
            return actual < expected
        else:
            return False

    def generate_nfr_report(self) -> Dict[str, Any]:
        """Generate comprehensive NFR report."""
        # Get category compliance data
        category_compliance = {
            category.value: self._assess_category_compliance(category)
            for category in NFRCategory
        }

        # Calculate overall compliance using the _calculate_iso_25010_compliance method
        # Convert to format expected by that method
        category_scores = {
            category: data["compliance_percentage"]
            for category, data in category_compliance.items()
        }
        iso_compliance = self._calculate_iso_25010_compliance(category_scores)

        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "iso_25010_compliance": iso_compliance,
            "security_metrics": self.security_metrics,
            "maintainability_metrics": self.maintainability_metrics,
            "performance_profiles": [
                {
                    "function": p.function_name,
                    "file": p.file_path,
                    "execution_time_ms": p.execution_time * 1000,
                    "memory_mb": p.memory_usage,
                    "cpu_percent": p.cpu_usage,
                    "complexity": p.complexity_score,
                }
                for p in self.performance_profiles
            ],
            "nfr_violations": [
                {
                    "metric": (
                        issue.message.split(":")[1].strip()
                        if ":" in issue.message
                        else issue.message
                    ),
                    "severity": (
                        str(issue.severity.value)
                        if hasattr(issue.severity, "value")
                        else str(issue.severity)
                    ),
                    "category": issue.category,
                }
                for issue in self.issues
                if issue.category == "nfr"
            ],
            "recommendations": self._generate_nfr_recommendations(),
        }

    def _assess_category_compliance(self, category: NFRCategory) -> Dict[str, Any]:
        """Assess compliance for a specific NFR category."""
        category_metrics = [m for m in self.nfr_metrics if m.category == category]
        category_violations = [
            i
            for i in self.issues
            if i.category == "nfr" and category.value in i.message.lower()
        ]

        compliant_metrics = len(category_metrics) - len(category_violations)
        compliance_percentage = (
            (compliant_metrics / len(category_metrics) * 100)
            if category_metrics
            else 100
        )

        return {
            "compliance_percentage": compliance_percentage,
            "total_metrics": len(category_metrics),
            "violations": len(category_violations),
            "status": "COMPLIANT" if compliance_percentage >= 90 else "NON_COMPLIANT",
        }

    def _load_nfr_categories(self) -> List[NFRCategory]:
        """Load NFR categories for testing."""
        return list(NFRCategory)

    def _analyze_performance(self) -> List[PerformanceProfile]:
        """Analyze performance and return profiles."""
        # If no profiles exist yet, create them
        if not self.performance_profiles:
            self._profile_performance()
        return self.performance_profiles

    def _analyze_security_metrics(self) -> List[SecurityMetric]:
        """Analyze security metrics."""
        # If security metrics haven't been calculated yet, calculate them
        if not self.security_metrics:
            auth_coverage = self._calculate_authentication_coverage()
            validation_coverage = self._calculate_input_validation_coverage()
            encryption_usage = self._calculate_encryption_usage()

            self.security_metrics = {
                "authentication_coverage": auth_coverage,
                "input_validation_coverage": validation_coverage,
                "encryption_usage": encryption_usage,
            }

        security_metrics = []
        # Convert security_metrics dict to SecurityMetric objects
        for metric_name, value in self.security_metrics.items():
            threshold = 100.0 if metric_name == "encryption_usage" else 95.0
            status = "PASS" if value >= threshold else "FAIL"

            security_metrics.append(
                SecurityMetric(
                    name=metric_name,
                    value=value,
                    unit="percentage",
                    category="security",
                    threshold=threshold,
                    status=status,
                )
            )

        return security_metrics

    def _analyze_maintainability(self) -> List[MaintainabilityMetric]:
        """Analyze maintainability metrics."""
        # If maintainability metrics haven't been calculated yet, calculate them
        if not self.maintainability_metrics:
            avg_complexity = self._calculate_average_complexity()
            duplication_percentage = self._calculate_code_duplication()
            doc_coverage = self._calculate_documentation_coverage()

            self.maintainability_metrics = {
                "average_complexity": avg_complexity,
                "duplication_percentage": duplication_percentage,
                "documentation_coverage": doc_coverage,
            }

        maintainability_metrics = []

        # Convert maintainability_metrics dict to MaintainabilityMetric objects
        for metric_name, value in self.maintainability_metrics.items():
            if metric_name == "average_complexity":
                threshold = 10.0
                status = "PASS" if value <= threshold else "FAIL"
            elif metric_name == "duplication_percentage":
                threshold = 5.0
                status = "PASS" if value <= threshold else "FAIL"
            elif metric_name == "documentation_coverage":
                threshold = 80.0
                status = "PASS" if value >= threshold else "FAIL"
            else:
                threshold = 0.0
                status = "PASS"

            maintainability_metrics.append(
                MaintainabilityMetric(
                    name=metric_name,
                    value=value,
                    unit=(
                        "percentage"
                        if "percentage" in metric_name or "coverage" in metric_name
                        else "score"
                    ),
                    category="maintainability",
                    threshold=threshold,
                    status=status,
                )
            )

        return maintainability_metrics

    def _analyze_reliability(self) -> Dict[str, Any]:
        """Analyze reliability metrics."""
        return {
            "error_handling_coverage": self._calculate_error_handling_coverage(),
            "test_coverage": self._get_test_coverage() or 0.0,
            "fault_tolerance": 85.0,  # Mock value
        }

    def _analyze_usability(self) -> Dict[str, Any]:
        """Analyze usability metrics."""
        return {
            "api_consistency": self._calculate_api_consistency(),
            "error_message_clarity": self._calculate_error_message_clarity(),
            "user_interface_simplicity": 90.0,  # Mock value
        }

    def _calculate_iso_25010_compliance(
        self, category_scores: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calculate ISO/IEC 25010 compliance score."""
        if category_scores is None:
            category_scores = {}

            # Calculate compliance for each category
            for category in NFRCategory:
                category_metrics = [
                    m for m in self.nfr_metrics if m.category == category
                ]
                category_violations = [
                    v
                    for v in self.nfr_violations
                    if category.value in v.category.lower()
                ]

                if category_metrics:
                    compliance_score = max(
                        0,
                        100 - (len(category_violations) / len(category_metrics) * 100),
                    )
                else:
                    compliance_score = 100

                category_scores[category.value] = {
                    "score": compliance_score,
                    "violations": len(category_violations),
                    "total_metrics": len(category_metrics),
                    "status": (
                        "COMPLIANT" if compliance_score >= 90 else "NON_COMPLIANT"
                    ),
                }

        # Calculate overall compliance
        # Handle both dictionary format (internal) and float format (test input)
        scores = []
        for cat in category_scores.values():
            if isinstance(cat, dict) and "score" in cat:
                scores.append(cat["score"])
            elif isinstance(cat, (int, float)):
                scores.append(float(cat))
            else:
                scores.append(0.0)  # fallback

        overall_score = sum(scores) / len(scores) if scores else 0.0

        # Count compliant and non-compliant categories (score >= 90)
        compliant_categories = sum(1 for score in scores if score >= 90.0)
        non_compliant_categories = len(scores) - compliant_categories

        return {
            "overall": overall_score,
            "by_category": category_scores,
            "compliant_categories": compliant_categories,
            "non_compliant_categories": non_compliant_categories,
            "total_categories": len(category_scores),
            "status": "COMPLIANT" if overall_score >= 90 else "NON_COMPLIANT",
        }

    def _validate_nfr_requirements(self) -> Dict[str, Any]:
        """Validate all NFR requirements."""
        validation_results = {}

        # Validate security requirements
        security_metrics = self._analyze_security_metrics()
        validation_results["security"] = {
            "metrics": len(security_metrics),
            "passed": len([m for m in security_metrics if m.status == "PASS"]),
            "compliance": (
                len([m for m in security_metrics if m.status == "PASS"])
                / len(security_metrics)
                * 100
                if security_metrics
                else 100
            ),
        }

        # Validate maintainability requirements
        maintainability_metrics = self._analyze_maintainability()
        validation_results["maintainability"] = {
            "metrics": len(maintainability_metrics),
            "passed": len([m for m in maintainability_metrics if m.status == "PASS"]),
            "compliance": (
                len([m for m in maintainability_metrics if m.status == "PASS"])
                / len(maintainability_metrics)
                * 100
                if maintainability_metrics
                else 100
            ),
        }

        # Validate performance requirements
        performance_profiles = self._analyze_performance()
        fast_functions = len(
            [p for p in performance_profiles if p.execution_time <= 0.1]
        )
        validation_results["performance"] = {
            "functions": len(performance_profiles),
            "fast_functions": fast_functions,
            "compliance": (
                fast_functions / len(performance_profiles) * 100
                if performance_profiles
                else 100
            ),
        }

        # Validate reliability requirements
        reliability_metrics = self._analyze_reliability()
        validation_results["reliability"] = {
            "error_handling_coverage": reliability_metrics["error_handling_coverage"],
            "test_coverage": reliability_metrics["test_coverage"],
            "compliance": (
                reliability_metrics["error_handling_coverage"]
                + reliability_metrics["test_coverage"]
            )
            / 2,
        }

        # Validate usability requirements
        usability_metrics = self._analyze_usability()
        validation_results["usability"] = {
            "api_consistency": usability_metrics["api_consistency"],
            "error_message_clarity": usability_metrics["error_message_clarity"],
            "compliance": (
                usability_metrics["api_consistency"]
                + usability_metrics["error_message_clarity"]
            )
            / 2,
        }

        return validation_results

    def _generate_nfr_recommendations(self) -> List[str]:
        """Generate NFR improvement recommendations."""
        recommendations = []

        nfr_violations = [i for i in self.issues if i.category == "nfr"]

        if nfr_violations:
            recommendations.append(f"📋 {len(nfr_violations)} NFR violations found:")

            # Group by category
            violations_by_category = {}
            for violation in nfr_violations:
                for category in NFRCategory:
                    if category.value in violation.message.lower():
                        if category not in violations_by_category:
                            violations_by_category[category] = []
                        violations_by_category[category].append(violation)
                        break

            for category, violations in violations_by_category.items():
                recommendations.append(f"  {category.value}: {len(violations)} issues")

        # Specific recommendations based on performance profiles
        if self.performance_profiles:
            slow_functions = [
                p for p in self.performance_profiles if p.execution_time > 0.1
            ]
            if slow_functions:
                recommendations.append(
                    f"⚡ Optimize {len(slow_functions)} slow functions"
                )

        if not recommendations:
            recommendations.append(
                "✅ All NFR requirements met! Excellent system quality."
            )

        return recommendations
