
from src.infrastructure.utils.common_imports import (
    Any,
    Dict,
    Enum,
    List,
    Optional,
    Path,
    dataclass,
    json,
    time
)
"""
Validation Pipeline
Integrates SonarQube, MyPy, Black, Ruff, and all custom validators into a single,
comprehensive validation system based on software engineering principles.
"""

# import json  # Consolidated to common_imports
# import time  # Consolidated to common_imports
from concurrent.futures import ThreadPoolExecutor, as_completed
# from dataclasses import dataclass  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
# from typing import Any, Dict, List, Optional  # Consolidated to common_imports

from ..sonarqube_integrator import SonarQubeIntegrator
from .base_validator import BaseValidator
from .dependency_validator import DependencyValidator
from .nfr_validator import NFRValidator
from .performance_validator import PerformanceValidator
from .quality_gates import QualityGatesEngine
from .shared_file_collector import shared_file_collector
from .structure_validator import StructureValidator
from .syntax_validator import SyntaxValidator
from .vv_validator import VVValidator

# Lazy import to avoid circular imports
# from ..ai.business_logic_protector import BusinessLogicProtector
# from ..ai.pattern_detector import AIPatternDetector


class ValidationPhase(Enum):
    """Validation phases for the pipeline."""

    PREPARATION = "preparation"
    STATIC_ANALYSIS = "static_analysis"
    QUALITY_GATES = "quality_gates"
    SECURITY_SCAN = "security_scan"
    NFR_VALIDATION = "nfr_validation"
    INTEGRATION = "integration"
    REPORTING = "reporting"


@dataclass
class ValidationResult:
    """Result of a validation phase."""

    phase: ValidationPhase
    success: bool
    duration: float
    issues_found: int
    critical_issues: int
    warnings: int
    info: int
    details: Dict[str, Any]


class Validator(BaseValidator):
    """Main validation pipeline integrating all validation tools and techniques."""

    def __init__(
        self,
        root_path: Optional[Path] = None,
        enable_sonarqube: bool = False,
        enable_parallel: bool = True,
        enable_quality_gates: bool = True,
        sonar_host_url: str = "http://localhost:9000",
        sonar_token: Optional[str] = None,
        quality_gate_config: Optional[Dict] = None,
    ):
        super().__init__(root_path, shared_collector=shared_file_collector)

        # Configuration
        self.enable_sonarqube = enable_sonarqube
        self.enable_parallel = enable_parallel
        self.enable_quality_gates = enable_quality_gates
        self.quality_gate_config = quality_gate_config or {}

        # Initialize validators with shared file collector for performance
        self._syntax_validator = None
        self._dependency_validator = None
        self._structure_validator = None
        self._performance_validator = None
        self._pattern_detector = None
        self._business_logic_protector = None
        self._quality_gates_engine = None
        self._vv_validator = None
        self._nfr_validator = None

        if enable_sonarqube:
            self.sonarqube_integrator = SonarQubeIntegrator(
                root_path=root_path,
                sonar_host_url=sonar_host_url,
                sonar_token=sonar_token,
            )
        else:
            self.sonarqube_integrator = None

        # Results tracking
        self.validation_results: List[ValidationResult] = []
        self.overall_start_time = 0
        self.phases_completed = 0
        self.build_decision: Dict[str, Any] = {}

    @property
    def syntax_validator(self):
        """Lazy-loaded syntax validator."""
        if self._syntax_validator is None:
            self._syntax_validator = SyntaxValidator(self.root_path)
            self._syntax_validator.shared_collector = shared_file_collector
        return self._syntax_validator

    @property
    def dependency_validator(self):
        """Lazy-loaded dependency validator."""
        if self._dependency_validator is None:
            self._dependency_validator = DependencyValidator(self.root_path)
            self._dependency_validator.shared_collector = shared_file_collector
        return self._dependency_validator

    @property
    def structure_validator(self):
        """Lazy-loaded structure validator."""
        if self._structure_validator is None:
            self._structure_validator = StructureValidator(self.root_path)
            self._structure_validator.shared_collector = shared_file_collector
        return self._structure_validator

    @property
    def performance_validator(self):
        """Lazy-loaded performance validator."""
        if self._performance_validator is None:
            self._performance_validator = PerformanceValidator(self.root_path)
            self._performance_validator.shared_collector = shared_file_collector
        return self._performance_validator

    @property
    def pattern_detector(self):
        """Lazy-loaded AI pattern detector."""
        if self._pattern_detector is None:
            from ..ai.pattern_detector import AIPatternDetector

            self._pattern_detector = AIPatternDetector(self.root_path)
            self._pattern_detector.shared_collector = shared_file_collector
        return self._pattern_detector

    @property
    def business_logic_protector(self):
        """Lazy-loaded business logic protector."""
        if self._business_logic_protector is None:
            from ..ai.business_logic_protector import BusinessLogicProtector

            self._business_logic_protector = BusinessLogicProtector(self.root_path)
            self._business_logic_protector.shared_collector = shared_file_collector
        return self._business_logic_protector

    @property
    def quality_gates_engine(self):
        """Lazy-loaded quality gates engine."""
        if self._quality_gates_engine is None:
            self._quality_gates_engine = QualityGatesEngine(self.root_path)
            if hasattr(self._quality_gates_engine, "shared_collector"):
                self._quality_gates_engine.shared_collector = shared_file_collector
        return self._quality_gates_engine

    @property
    def vv_validator(self):
        """Lazy-loaded V&V validator."""
        if self._vv_validator is None:
            self._vv_validator = VVValidator(self.root_path)
            if hasattr(self._vv_validator, "shared_collector"):
                self._vv_validator.shared_collector = shared_file_collector
        return self._vv_validator

    @property
    def nfr_validator(self):
        """Lazy-loaded NFR validator."""
        if self._nfr_validator is None:
            self._nfr_validator = NFRValidator(self.root_path)
            if hasattr(self._nfr_validator, "shared_collector"):
                self._nfr_validator.shared_collector = shared_file_collector
        return self._nfr_validator

    def run_validation(self) -> Dict[str, Any]:
        """Run the complete validation pipeline."""
        self.overall_start_time = time.time()

        print("🚀 Starting Validation Pipeline")
        print("=" * 60)

        # Phase 1: Preparation
        self._run_phase(ValidationPhase.PREPARATION, self._preparation_phase)

        # Phase 2: Static Analysis (can run in parallel)
        if self.enable_parallel:
            self._run_parallel_static_analysis()
        else:
            self._run_phase(
                ValidationPhase.STATIC_ANALYSIS, self._static_analysis_phase
            )

        # Phase 3: Quality Gates
        if self.enable_quality_gates:
            self._run_phase(ValidationPhase.QUALITY_GATES, self._quality_gates_phase)

        # Phase 4: Security Scan
        self._run_phase(ValidationPhase.SECURITY_SCAN, self._security_scan_phase)

        # Phase 5: NFR Validation
        self._run_phase(ValidationPhase.NFR_VALIDATION, self._nfr_validation_phase)

        # Phase 6: Integration (SonarQube)
        if self.enable_sonarqube:
            self._run_phase(ValidationPhase.INTEGRATION, self._integration_phase)

        # Phase 7: Reporting
        self._run_phase(ValidationPhase.REPORTING, self._reporting_phase)

        # Generate final report
        return self._generate_final_report()

    def _run_phase(self, phase: ValidationPhase, phase_func) -> ValidationResult:
        """Run a single validation phase."""
        print(
            f"\n📍 Phase {self.phases_completed + 1}: {phase.value.replace('_', ' ').title()}"
        )

        start_time = time.time()
        success = True
        details = {}

        try:
            details = phase_func()
            if details.get("success", True) is False:
                success = False
        except Exception as e:
            success = False
            details = {"error": str(e)}
            print(f"❌ Phase {phase.value} failed: {e}")

        duration = time.time() - start_time

        # Count issues
        issues_found = len(self.issues)
        critical_issues = len([i for i in self.issues if i.severity == "error"])
        warnings = len([i for i in self.issues if i.severity == "warning"])
        info = len([i for i in self.issues if i.severity == "info"])

        result = ValidationResult(
            phase=phase,
            success=success,
            duration=duration,
            issues_found=issues_found,
            critical_issues=critical_issues,
            warnings=warnings,
            info=info,
            details=details,
        )

        self.validation_results.append(result)
        self.phases_completed += 1

        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status} ({duration:.2f}s) - {issues_found} issues found")

        return result

    def _preparation_phase(self) -> Dict[str, Any]:
        """Preparation phase - setup and file collection."""
        if not self.python_files:
            self._collect_files()

        # Create reports directory
        reports_dir = self.root_path / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Validate environment
        environment_checks = {
            "python_files": len(self.python_files),
            "test_files": len(
                [f for f in self.python_files if "test" in str(f).lower()]
            ),
            "has_requirements": (self.root_path / "requirements.txt").exists(),
            "has_pyproject": (self.root_path / "pyproject.toml").exists(),
            "has_tests_dir": (self.root_path / "tests").exists(),
        }

        if self.enable_sonarqube:
            environment_checks["sonarqube_available"] = (
                self.sonarqube_integrator.is_sonarqube_available()
            )

        print(f"  📁 Found {environment_checks['python_files']} Python files")
        print(f"  🧪 Found {environment_checks['test_files']} test files")

        return {
            "success": True,
            "environment": environment_checks,
            "files_collected": len(self.python_files),
        }

    def _get_validator_configurations(self) -> List[tuple]:
        """Get validator configurations with their execution methods.
        
        Returns:
            List of (name, validator, method_name, args) tuples
        """
        return [
            ("syntax", self.syntax_validator, "validate_all_imports", (self.python_files,)),
            ("dependencies", self.dependency_validator, "validate_dependencies", ()),
            ("structure", self.structure_validator, "validate_structure", ()),
            ("performance", self.performance_validator, "validate_performance", ()),
            ("ai_patterns", self.pattern_detector, "analyze_patterns", ()),
            ("business_logic", self.business_logic_protector, "protect_business_logic", ()),
        ]

    def _execute_validator(self, name: str, validator: Any, method_name: str, args: tuple) -> bool:
        """Execute a single validator and handle its result.
        
        Args:
            name: Name of the validator
            validator: Validator instance
            method_name: Method to call on the validator
            args: Arguments to pass to the method
            
        Returns:
            Success status of the validation
        """
        try:
            if not validator:
                print(f"  ⚠️  {name} validator not available")
                return True
                
            method = getattr(validator, method_name)
            success = method(*args) if args else method()
            
            # Merge issues from validator
            for issue in validator.issues:
                if issue not in self.issues:
                    self.issues.append(issue)
            
            return bool(success) if success is not None else False
            
        except Exception as e:
            print(f"  ❌ {name} validation failed: {e}")
            return False

    def _generate_issues_by_category(self) -> Dict[str, int]:
        """Generate count of issues by category.
        
        Returns:
            Dictionary mapping category names to issue counts
        """
        categories = [
            "syntax", "dependencies", "structure", "performance", 
            "ai_analysis", "business_logic"
        ]
        
        return {
            category: len([i for i in self.issues if i.category == category])
            for category in categories
        }

    def _static_analysis_phase(self) -> Dict[str, Any]:
        """Static analysis phase - comprehensive validation."""
        validator_configs = self._get_validator_configurations()
        
        results = {}
        overall_success = True

        # Execute each validator
        for name, validator, method_name, args in validator_configs:
            success = self._execute_validator(name, validator, method_name, args)
            results[name] = success
            overall_success &= success

        return {
            "success": overall_success,
            "validators_run": list(results.keys()),
            "results": results,
            "issues_by_category": self._generate_issues_by_category(),
        }

    def _run_parallel_static_analysis(self):
        """Run static analysis components in parallel."""
        print(f"\n📍 Phase {self.phases_completed + 1}: Static Analysis (Parallel)")

        start_time = time.time()

        # Define parallel tasks
        tasks = [
            (
                "syntax_validation",
                self.syntax_validator.validate_all_imports,
                (self.python_files,),
            ),
            (
                "dependency_validation",
                self.dependency_validator.validate_dependencies,
                (),
            ),
            (
                "structure_validation",
                self.structure_validator.validate_structure,
                (),
            ),
            (
                "performance_validation",
                self.performance_validator.validate_performance,
                (),
            ),
            (
                "ai_pattern_detection",
                self.pattern_detector.analyze_patterns,
                (),
            ),
            (
                "business_logic_protection",
                self.business_logic_protector.protect_business_logic,
                (),
            ),
        ]

        results = {}

        with ThreadPoolExecutor(max_workers=min(len(tasks), 4)) as executor:
            # Submit tasks
            future_to_task = {
                executor.submit(task_func, *args): task_name
                for task_name, task_func, args in tasks
            }

            # Collect results
            for future in as_completed(future_to_task):
                task_name = future_to_task[future]
                try:
                    result = future.result()
                    results[task_name] = {"success": result, "error": None}
                    print(f"  ✅ {task_name} completed")
                except Exception as e:
                    results[task_name] = {"success": False, "error": str(e)}
                    print(f"  ❌ {task_name} failed: {e}")

        # Merge all issues
        for validator in [
            self.syntax_validator,
            self.dependency_validator,
            self.structure_validator,
            self.performance_validator,
            self.pattern_detector,
            self.business_logic_protector,
        ]:
            for issue in validator.issues:
                if issue not in self.issues:
                    self.issues.append(issue)

        duration = time.time() - start_time
        success = all(result["success"] for result in results.values())

        issues_found = len(self.issues)
        critical_issues = len([i for i in self.issues if i.severity == "error"])
        warnings = len([i for i in self.issues if i.severity == "warning"])
        info = len([i for i in self.issues if i.severity == "info"])

        result = ValidationResult(
            phase=ValidationPhase.STATIC_ANALYSIS,
            success=success,
            duration=duration,
            issues_found=issues_found,
            critical_issues=critical_issues,
            warnings=warnings,
            info=info,
            details={"parallel_results": results},
        )

        self.validation_results.append(result)
        self.phases_completed += 1

        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status} ({duration:.2f}s) - {issues_found} issues found")

    def _quality_gates_phase(self) -> Dict[str, Any]:
        """Quality gates phase - enforce quality standards."""
        gate_report = self.quality_gates_engine.evaluate_quality_gates()

        # Convert quality gate failures to issues
        for gate_result in gate_report.get("gate_results", []):
            if gate_result["status"] == "FAILED":
                self.add_issue(
                    category="quality_gates",
                    issue_type="QUALITY_GATE_FAILURE",
                    file_path="system",
                    message=f"Quality Gate Failed: {gate_result['message']}",
                    severity=gate_result["severity"],
                    fix_suggestion=f"Fix {gate_result['name']} to meet threshold",
                    auto_fixable=False,
                )

        # Make build decision
        self.build_decision = gate_report.get("build_decision", {})

        return {
            "success": gate_report["overall_status"] != "FAILED",
            "quality_gates_passed": gate_report["quality_gates_passed"],
            "quality_gates_failed": gate_report["quality_gates_failed"],
            "quality_gates_warning": gate_report["quality_gates_warning"],
            "build_decision": self.build_decision,
            "technical_debt": gate_report.get("technical_debt", {}),
            "iso_25010_compliance": gate_report.get("iso_25010_compliance", {}),
        }

    def _security_scan_phase(self) -> Dict[str, Any]:
        """Security scan phase - V&V with OWASP compliance."""
        success = self.vv_validator.run_validation_verification()

        # Merge issues from V&V validator
        for issue in self.vv_validator.issues:
            if issue not in self.issues:
                self.issues.append(issue)

        vv_report = self.vv_validator.generate_vv_report()

        return {
            "success": success,
            "owasp_compliance": vv_report["validation_verification"]["compliance"][
                "owasp_top_10"
            ],
            "pep8_compliance": vv_report["validation_verification"]["compliance"][
                "pep8_compliance"
            ],
            "security_vulnerabilities": vv_report["validation_verification"][
                "security_vulnerabilities"
            ],
            "external_tools": vv_report["validation_verification"]["external_tools"],
        }

    def _nfr_validation_phase(self) -> Dict[str, Any]:
        """NFR validation phase - non-functional requirements."""
        success = self.nfr_validator.run_nfr_validation()

        # Merge issues from NFR validator
        for issue in self.nfr_validator.issues:
            if issue not in self.issues:
                self.issues.append(issue)

        nfr_report = self.nfr_validator.generate_nfr_report()

        return {
            "success": success,
            "iso_25010_compliance": nfr_report["iso_25010_compliance"],
            "security_metrics": nfr_report["security_metrics"],
            "maintainability_metrics": nfr_report["maintainability_metrics"],
            "performance_profiles": nfr_report["performance_profiles"],
            "nfr_violations": nfr_report["nfr_violations"],
        }

    def _integration_phase(self) -> Dict[str, Any]:
        """Integration phase - SonarQube integration."""
        if not self.sonarqube_integrator:
            return {"success": True, "message": "SonarQube integration disabled"}

        success = self.sonarqube_integrator.run_sonarqube_analysis()

        # Merge issues from SonarQube
        for issue in self.sonarqube_integrator.issues:
            if issue not in self.issues:
                self.issues.append(issue)

        integration_report = self.sonarqube_integrator.generate_integrated_report()

        return {
            "success": success,
            "sonarqube_enabled": self.sonarqube_integrator.is_sonarqube_available(),
            "sonarqube_issues": len(self.sonarqube_integrator.sonar_issues),
            "integration_report": integration_report,
        }

    def _reporting_phase(self) -> Dict[str, Any]:
        """Reporting phase - generate comprehensive reports."""
        # Generate individual reports
        reports_generated = []

        # Quality Gates report
        quality_report_path = self.root_path / "reports" / "quality_gates_report.json"
        if self.quality_gates_engine.generate_quality_report(quality_report_path):
            reports_generated.append(str(quality_report_path))

        # V&V report
        vv_report = self.vv_validator.generate_vv_report()
        vv_report_path = self.root_path / "reports" / "vv_report.json"
        try:
            with open(vv_report_path, "w", encoding="utf-8") as f:
                json.dump(vv_report, f, indent=2, default=str)
            reports_generated.append(str(vv_report_path))
        except Exception:
            pass

        # NFR report
        nfr_report = self.nfr_validator.generate_nfr_report()
        nfr_report_path = self.root_path / "reports" / "nfr_report.json"
        try:
            with open(nfr_report_path, "w", encoding="utf-8") as f:
                json.dump(nfr_report, f, indent=2, default=str)
            reports_generated.append(str(nfr_report_path))
        except Exception:
            pass

        # Generate validation report
        validation_report = self._generate_final_report()
        validation_report_path = self.root_path / "reports" / "validation_report.json"
        try:
            # Ensure reports directory exists
            validation_report_path.parent.mkdir(parents=True, exist_ok=True)

            with open(validation_report_path, "w", encoding="utf-8") as f:
                json.dump(validation_report, f, indent=2, default=str)
            reports_generated.append(str(validation_report_path))
            print(f"  ✅ Validation report saved: {validation_report_path}")
        except Exception as e:
            print(f"  ❌ Failed to save validation report: {e}")
            # Try to save a minimal report without detailed issues
            try:
                minimal_report = validation_report.copy()
                minimal_report.pop("detailed_issues", None)
                with open(validation_report_path, "w", encoding="utf-8") as f:
                    json.dump(minimal_report, f, indent=2, default=str)
                print("  ⚠️  Saved minimal report without detailed issues")
            except Exception as e2:
                print(f"  ❌ Failed to save even minimal report: {e2}")

        return {
            "success": True,
            "reports_generated": reports_generated,
            "total_reports": len(reports_generated),
        }

    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate the final validation report."""
        total_duration = time.time() - self.overall_start_time

        # Categorize and group issues efficiently
        issues_by_category = {}
        issues_by_severity = {}
        issues_by_type = {}  # Group by issue type to avoid repetition

        for issue in self.issues:
            # By category
            if issue.category not in issues_by_category:
                issues_by_category[issue.category] = []
            issues_by_category[issue.category].append(issue)

            # By severity (convert enum to string for JSON serialization)
            severity_key = (
                str(issue.severity.value)
                if hasattr(issue.severity, "value")
                else str(issue.severity)
            )
            if severity_key not in issues_by_severity:
                issues_by_severity[severity_key] = []
            issues_by_severity[severity_key].append(issue)

            # Group by type to identify patterns
            issue_type_str = (
                str(issue.issue_type.value)
                if hasattr(issue.issue_type, "value")
                else str(issue.issue_type)
            )
            type_key = f"{issue.category}:{issue_type_str}"
            if type_key not in issues_by_type:
                issues_by_type[type_key] = {
                    "category": issue.category,
                    "type": issue_type_str,
                    "severity": (
                        str(issue.severity.value)
                        if hasattr(issue.severity, "value")
                        else str(issue.severity)
                    ),
                    "message_pattern": issue.message,
                    "fix_suggestion": issue.fix_suggestion,
                    "auto_fixable": issue.auto_fixable,
                    "occurrences": [],
                    "count": 0,
                }
            issues_by_type[type_key]["count"] += 1
            # Only store file and line info for occurrences
            issues_by_type[type_key]["occurrences"].append(
                {
                    "file": str(issue.file_path),
                    "line": issue.line if issue.line is not None else 0,
                }
            )

        # Calculate overall success
        overall_success = all(result.success for result in self.validation_results)
        can_merge = self.build_decision.get("allow_merge", True)

        # Generate summary
        summary = {
            "overall_success": overall_success,
            "can_merge": can_merge,
            "total_duration": total_duration,
            "phases_completed": self.phases_completed,
            "total_issues": len(self.issues),
            "critical_issues": len(issues_by_severity.get("error", [])),
            "warnings": len(issues_by_severity.get("warning", [])),
            "info_issues": len(issues_by_severity.get("info", [])),
            "build_decision": self.build_decision,
        }

        # Phase results
        phase_results = {
            result.phase.value: {
                "success": result.success,
                "duration": result.duration,
                "issues_found": result.issues_found,
                "critical_issues": result.critical_issues,
                "warnings": result.warnings,
                "info": result.info,
                "details": result.details,
            }
            for result in self.validation_results
        }

        # Software engineering principles compliance
        compliance_assessment = self._assess_software_engineering_compliance()

        # Generate recommendations
        recommendations = self._generate_recommendations()

        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "validation_system": "Validation Pipeline v3.0",
            "summary": summary,
            "phase_results": phase_results,
            "issues_by_category": {k: len(v) for k, v in issues_by_category.items()},
            "issues_by_severity": {k: len(v) for k, v in issues_by_severity.items()},
            "compliance_assessment": compliance_assessment,
            "recommendations": recommendations,
            "total_issues": len(self.issues),
            # Add top issues summary for quick insights
            "top_issues_summary": self._generate_top_issues_summary(issues_by_type),
            # Group issues by type to avoid repetition and reduce size
            "issues_grouped": [
                {
                    "category": str(group["category"]),
                    "type": str(group["type"]),
                    "severity": str(group["severity"]),
                    "message_pattern": str(group["message_pattern"]),
                    "fix_suggestion": (
                        str(group["fix_suggestion"]) if group["fix_suggestion"] else ""
                    ),
                    "auto_fixable": bool(group["auto_fixable"]),
                    "count": group["count"],
                    # Limit occurrences to prevent huge reports
                    "sample_occurrences": group["occurrences"][:10],
                    "total_occurrences": len(group["occurrences"]),
                }
                for group in sorted(
                    issues_by_type.values(), key=lambda x: x["count"], reverse=True
                )
            ],
        }

    def _assess_software_engineering_compliance(self) -> Dict[str, Any]:
        """Assess compliance with software engineering principles."""
        principles = {
            "Quality Engineering": {
                "metrics_evaluated": ["duplication", "complexity", "coverage"],
                "compliance": len(
                    [i for i in self.issues if i.category == "quality_gates"]
                )
                == 0,
            },
            "Validation and Verification": {
                "standards_checked": ["PEP8", "OWASP", "coding_standards"],
                "compliance": len(
                    [
                        i
                        for i in self.issues
                        if i.category in ["coding_standards", "security"]
                    ]
                )
                == 0,
            },
            "Non-Functional Requirements": {
                "categories_assessed": [
                    "security",
                    "performance",
                    "maintainability",
                    "reliability",
                ],
                "compliance": len([i for i in self.issues if i.category == "nfr"]) == 0,
            },
            "Maintainability": {
                "code_smells_detected": len(
                    [i for i in self.issues if "smell" in i.message.lower()]
                ),
                "compliance": len(
                    [i for i in self.issues if i.category == "maintainability"]
                )
                == 0,
            },
            "Process Automation": {
                "ci_cd_ready": self.build_decision.get("allow_merge", False),
                "quality_gates_enabled": self.enable_quality_gates,
            },
        }

        overall_compliance = sum(
            1 for p in principles.values() if p.get("compliance", False)
        )
        compliance_percentage = (overall_compliance / len(principles)) * 100

        return {
            "overall_compliance_percentage": compliance_percentage,
            "principles": principles,
            "iso_25010_compliant": compliance_percentage >= 80,
            "ready_for_production": compliance_percentage >= 90
            and self.build_decision.get("allow_merge", False),
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations across all validators."""
        recommendations = []

        # Critical issues first
        critical_issues = [i for i in self.issues if i.severity == "error"]
        if critical_issues:
            recommendations.append(
                f"🚨 CRITICAL: Fix {len(critical_issues)} critical issues before deployment"
            )

            # Group by category
            critical_by_category = {}
            for issue in critical_issues:
                if issue.category not in critical_by_category:
                    critical_by_category[issue.category] = 0
                critical_by_category[issue.category] += 1

            for category, count in critical_by_category.items():
                recommendations.append(f"  - {category}: {count} critical issues")

        # Build decision
        if not self.build_decision.get("allow_merge", True):
            blocking_issues = self.build_decision.get("blocking_issues", [])
            recommendations.append(
                f"🚫 BUILD BLOCKED: {len(blocking_issues)} quality gates failed"
            )
            for issue in blocking_issues:
                recommendations.append(f"  - {issue}")

        # Quality improvements
        warnings = [i for i in self.issues if i.severity == "warning"]
        if warnings:
            recommendations.append(
                f"⚠️ QUALITY: Address {len(warnings)} warnings to improve code quality"
            )

        # Tool-specific recommendations
        if self.enable_sonarqube and self.sonarqube_integrator:
            sonar_issues = len(self.sonarqube_integrator.sonar_issues)
            if sonar_issues > 0:
                recommendations.append(
                    f"🔍 SONARQUBE: Review {sonar_issues} issues in SonarQube dashboard"
                )

        # Software engineering principles
        compliance = self._assess_software_engineering_compliance()
        if compliance["overall_compliance_percentage"] < 90:
            recommendations.append(
                f"📐 COMPLIANCE: {compliance['overall_compliance_percentage']:.1f}% compliance with software engineering principles"
            )

        if not recommendations:
            recommendations.append(
                "✅ EXCELLENT: All validations passed! Code is production-ready."
            )

        return recommendations

    def _generate_top_issues_summary(
        self, issues_by_type: Dict[str, Dict]
    ) -> List[Dict[str, Any]]:
        """Generate summary of top issues for quick insights."""
        # Sort by count and take top 10
        sorted_issues = sorted(
            issues_by_type.values(), key=lambda x: x["count"], reverse=True
        )[:10]

        return [
            {
                "issue": f"{issue['category']}:{issue['type']}",
                "count": issue["count"],
                "severity": str(issue["severity"]),
                "message": (
                    str(issue["message_pattern"])[:100] + "..."
                    if len(str(issue["message_pattern"])) > 100
                    else str(issue["message_pattern"])
                ),
            }
            for issue in sorted_issues
        ]

    def should_block_build(self) -> bool:
        """Determine if the build should be blocked."""
        return not self.build_decision.get("allow_merge", True)

    def get_build_summary(self) -> str:
        """Get a build summary for CI/CD systems."""
        if not self.validation_results:
            return "❓ Validation not run"

        failed_phases = [r for r in self.validation_results if not r.success]
        critical_issues = len([i for i in self.issues if i.severity == "error"])

        if failed_phases:
            return f"❌ FAILED: {len(failed_phases)} phases failed, {critical_issues} critical issues"
        elif critical_issues > 0:
            return f"⚠️ WARNING: {critical_issues} critical issues found"
        else:
            return f"✅ SUCCESS: All {len(self.validation_results)} phases passed"
