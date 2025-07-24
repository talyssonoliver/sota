"""
SonarQube Integrator
Integrates SonarQube analysis with the existing validation system.
"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .core.base_validator import BaseValidator


class SonarQubeIntegrator(BaseValidator):
    """Integrates SonarQube analysis with existing validation system."""

    def __init__(
        self,
        root_path: Optional[Path] = None,
        sonar_host_url: str = "http://localhost:9000",
        sonar_token: Optional[str] = None,
        project_key: Optional[str] = None,
    ):
        """Initialize SonarQube integrator."""
        super().__init__(root_path)
        self.sonar_host_url = sonar_host_url
        self.sonar_token = sonar_token or os.getenv("SONAR_TOKEN")
        self.project_key = project_key or "sota-ai"
        self.sonar_scanner_path = self._find_sonar_scanner()
        self.analysis_results: Optional[Dict] = None
        self.sonar_issues: List[Dict] = []

    def _find_sonar_scanner(self) -> Optional[str]:
        """Find SonarQube scanner in system PATH."""
        import platform

        scanner_names = ["sonar-scanner", "sonar-scanner.bat"]

        for scanner in scanner_names:
            try:
                # Use appropriate command based on platform
                if platform.system() == "Windows":
                    cmd = ["where", scanner]
                else:
                    cmd = ["which", scanner]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return scanner
            except (
                subprocess.TimeoutExpired,
                subprocess.SubprocessError,
                FileNotFoundError,
            ):
                continue

        return None

    def is_sonarqube_available(self) -> bool:
        """Check if SonarQube scanner and server are available."""
        if not self.sonar_scanner_path:
            return False

        if not self.sonar_token:
            return False

        # Check if SonarQube server is accessible
        try:
            import requests

            response = requests.get(
                f"{self.sonar_host_url}/api/system/status", timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def run_sonarqube_analysis(self) -> bool:
        """Run SonarQube analysis and integrate with existing validation."""
        if not self.is_sonarqube_available():
            self.add_issue(
                category="sonarqube",
                issue_type="INTEGRATION_ERROR",
                file_path="sonar_integration",
                message="SonarQube not available - scanner or server not accessible",
                severity="warning",
                fix_suggestion="Install SonarQube scanner and ensure server is running",
                auto_fixable=False,
            )
            return False

        print("🔍 Running SonarQube analysis...")

        # Generate coverage report for SonarQube
        self._generate_coverage_report()

        # Run SonarQube scanner
        success = self._execute_sonar_scanner()

        if success:
            # Retrieve and process analysis results
            self._retrieve_analysis_results()
            self._process_sonar_issues()

        return success

    def _generate_coverage_report(self):
        """Generate coverage report in XML format for SonarQube."""
        try:
            coverage_cmd = [
                "python",
                "-m",
                "pytest",
                "--cov=src",
                "--cov-report=xml:coverage.xml",
                "--cov-report=term-missing",
                "tests/",
                "-q",  # Quiet mode
            ]

            result = subprocess.run(
                coverage_cmd,
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode == 0:
                print("✅ Coverage report generated successfully")
            else:
                print(f"⚠️ Coverage generation failed: {result.stderr}")

        except Exception as e:
            print(f"⚠️ Could not generate coverage report: {e}")

    def _execute_sonar_scanner(self) -> bool:
        """Execute SonarQube scanner."""
        scanner_args = [
            self.sonar_scanner_path,
            f"-Dsonar.projectKey={self.project_key}",
            "-Dsonar.sources=src",
            "-Dsonar.tests=tests",
            f"-Dsonar.host.url={self.sonar_host_url}",
            f"-Dsonar.token={self.sonar_token}",
            "-Dsonar.sourceEncoding=UTF-8",
            "-Dsonar.python.version=3.12",
        ]

        # Add coverage report if available
        coverage_file = self.root_path / "coverage.xml"
        if coverage_file.exists():
            scanner_args.append("-Dsonar.python.coverage.reportPaths=coverage.xml")

        try:
            result = subprocess.run(
                scanner_args,
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes timeout
            )

            if result.returncode == 0:
                print("✅ SonarQube analysis completed successfully")
                return True
            else:
                self.add_issue(
                    category="sonarqube",
                    issue_type="ANALYSIS_ERROR",
                    file_path="sonar_scanner",
                    message=f"SonarQube analysis failed: {result.stderr}",
                    severity="error",
                    fix_suggestion="Check SonarQube configuration and server connectivity",
                    auto_fixable=False,
                )
                return False

        except subprocess.TimeoutExpired:
            self.add_issue(
                category="sonarqube",
                issue_type="ANALYSIS_ERROR",
                file_path="sonar_scanner",
                message="SonarQube analysis timed out after 10 minutes",
                severity="error",
                fix_suggestion="Optimize project size or increase timeout",
                auto_fixable=False,
            )
            return False
        except Exception as e:
            self.add_issue(
                category="sonarqube",
                issue_type="ANALYSIS_ERROR",
                file_path="sonar_scanner",
                message=f"SonarQube analysis failed: {str(e)}",
                severity="error",
                fix_suggestion="Check SonarQube installation and configuration",
                auto_fixable=False,
            )
            return False

    def _retrieve_analysis_results(self):
        """Retrieve analysis results from SonarQube API."""
        if not self.sonar_token:
            return

        try:
            import requests

            # Get project issues
            issues_url = f"{self.sonar_host_url}/api/issues/search"
            params = {
                "componentKeys": self.project_key,
                "resolved": "false",
                "ps": 500,  # Page size
            }

            headers = {"Authorization": f"Bearer {self.sonar_token}"}

            response = requests.get(
                issues_url, params=params, headers=headers, timeout=30
            )

            if response.status_code == 200:
                self.analysis_results = response.json()
                issues_count = (
                    len(self.analysis_results.get("issues", []))
                    if self.analysis_results
                    else 0
                )
                print(f"✅ Retrieved {issues_count} SonarQube issues")
            else:
                print(f"⚠️ Could not retrieve SonarQube results: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Error retrieving SonarQube results: {e}")

    def _process_sonar_issues(self):
        """Process SonarQube issues and convert to validation issues."""
        if not self.analysis_results:
            return

        issues = self.analysis_results.get("issues", [])

        for sonar_issue in issues:
            # Map SonarQube severity to validation severity
            severity_mapping = {
                "BLOCKER": "error",
                "CRITICAL": "error",
                "MAJOR": "warning",
                "MINOR": "info",
                "INFO": "info",
            }

            severity = severity_mapping.get(sonar_issue.get("severity", "INFO"), "info")

            # Map SonarQube type to validation category
            type_mapping = {
                "BUG": "bugs",
                "VULNERABILITY": "security",
                "CODE_SMELL": "maintainability",
                "SECURITY_HOTSPOT": "security",
            }

            category = type_mapping.get(
                sonar_issue.get("type", "CODE_SMELL"), "sonarqube"
            )

            # Extract file path and line number
            component = sonar_issue.get("component", "")
            file_path = component.replace(f"{self.project_key}:", "")
            line = sonar_issue.get("line", 1)

            # Create validation issue
            self.add_issue(
                category=category,
                issue_type="SONARQUBE_ISSUE",
                file_path=file_path,
                message=f"SonarQube: {sonar_issue.get('message', 'Issue detected')}",
                line=line,
                severity=severity,
                fix_suggestion=f"Rule: {sonar_issue.get('rule', 'N/A')}",
                auto_fixable=False,
            )

            # Store original SonarQube issue data
            self.sonar_issues.append(sonar_issue)

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary from the base validator."""
        try:
            # Since SonarQubeIntegrator inherits from BaseValidator, use self directly
            return {
                "total_issues": len(getattr(self, "issues", [])),
                "error_count": len(
                    [
                        i
                        for i in getattr(self, "issues", [])
                        if getattr(i, "severity", "") == "error"
                    ]
                ),
                "warning_count": len(
                    [
                        i
                        for i in getattr(self, "issues", [])
                        if getattr(i, "severity", "") == "warning"
                    ]
                ),
                "files_processed": len(getattr(self, "python_files", [])),
                "validation_status": (
                    "completed" if hasattr(self, "issues") else "pending"
                ),
            }
        except Exception as e:
            return {
                "error": f"Could not generate validation summary: {str(e)}",
                "validation_status": "error",
            }

    def generate_integrated_report(self) -> Dict[str, Any]:
        """Generate integrated report combining validation and SonarQube results."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sonarqube_integration": {
                "enabled": self.is_sonarqube_available(),
                "issues_count": len(self.sonar_issues),
                "analysis_success": self.analysis_results is not None,
            },
            "validation_summary": self.get_validation_summary(),
            "sonarqube_summary": self._get_sonarqube_summary(),
            "combined_metrics": self._calculate_combined_metrics(),
            "recommendations": self._generate_integration_recommendations(),
        }

        return report

    def _get_sonarqube_summary(self) -> Dict[str, Any]:
        """Get summary of SonarQube analysis results."""
        if not self.analysis_results:
            return {"status": "not_available"}

        issues = self.analysis_results.get("issues", [])

        summary = {
            "total_issues": len(issues),
            "by_severity": {},
            "by_type": {},
            "by_status": {},
        }

        for issue in issues:
            # Count by severity
            severity = issue.get("severity", "INFO")
            summary["by_severity"][severity] = (
                summary["by_severity"].get(severity, 0) + 1
            )

            # Count by type
            issue_type = issue.get("type", "CODE_SMELL")
            summary["by_type"][issue_type] = summary["by_type"].get(issue_type, 0) + 1

            # Count by status
            status = issue.get("status", "OPEN")
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

        return summary

    def _calculate_combined_metrics(self) -> Dict[str, Any]:
        """Calculate combined metrics from both validation systems."""
        validation_errors = len(self.get_issues_by_severity("error"))
        validation_warnings = len(self.get_issues_by_severity("warning"))

        sonar_errors = 0
        sonar_warnings = 0

        if self.analysis_results:
            issues = self.analysis_results.get("issues", [])
            for issue in issues:
                severity = issue.get("severity", "INFO")
                if severity in ["BLOCKER", "CRITICAL"]:
                    sonar_errors += 1
                elif severity == "MAJOR":
                    sonar_warnings += 1

        return {
            "total_errors": validation_errors + sonar_errors,
            "total_warnings": validation_warnings + sonar_warnings,
            "validation_only_errors": validation_errors,
            "validation_only_warnings": validation_warnings,
            "sonarqube_only_errors": sonar_errors,
            "sonarqube_only_warnings": sonar_warnings,
            "coverage_overlap": self._analyze_coverage_overlap(),
        }

    def _analyze_coverage_overlap(self) -> Dict[str, Any]:
        """Analyze overlap between validation and SonarQube findings."""
        overlap_analysis = {
            "security_coverage": {
                "validation_rules": "BusinessLogicProtector + Security patterns",
                "sonarqube_rules": "SAST + Vulnerability detection",
                "complementary": True,
            },
            "code_quality": {
                "validation_rules": "AIPatternDetector + Structure validation",
                "sonarqube_rules": "Code smells + Complexity + Duplication",
                "complementary": True,
            },
            "dependency_analysis": {
                "validation_rules": "Enhanced dependency categorization",
                "sonarqube_rules": "SCA + License compliance",
                "complementary": True,
            },
        }

        return overlap_analysis

    def _generate_integration_recommendations(self) -> List[str]:
        """Generate recommendations for the integrated validation system."""
        recommendations = []

        if not self.is_sonarqube_available():
            recommendations.append(
                "Set up SonarQube for enterprise-grade security scanning"
            )
            recommendations.append(
                "Install SonarQube scanner and configure authentication"
            )

        if self.analysis_results:
            sonar_summary = self._get_sonarqube_summary()
            critical_issues = sonar_summary.get("by_severity", {}).get("CRITICAL", 0)

            if critical_issues > 0:
                recommendations.append(
                    f"Address {critical_issues} critical SonarQube security issues"
                )

        recommendations.extend(
            [
                "Your validation system provides excellent domain-specific analysis",
                "SonarQube adds industry-standard security and compliance checking",
                "Use both systems together for comprehensive code quality assurance",
                "Consider setting up quality gates in CI/CD with both validators",
            ]
        )

        return recommendations

    def export_sonarqube_config(self) -> bool:
        """Export configuration for SonarQube integration."""
        try:
            config = {
                "sonarqube_integration": {
                    "project_key": self.project_key,
                    "host_url": self.sonar_host_url,
                    "scanner_path": self.sonar_scanner_path,
                    "coverage_enabled": True,
                    "quality_gate_enabled": True,
                },
                "integration_settings": {
                    "combine_reports": True,
                    "severity_mapping": {
                        "BLOCKER": "error",
                        "CRITICAL": "error",
                        "MAJOR": "warning",
                        "MINOR": "info",
                        "INFO": "info",
                    },
                    "exclude_patterns": [
                        "**/tests/**",
                        "**/__pycache__/**",
                        "**/venv/**",
                    ],
                },
            }

            config_path = self.root_path / "sonarqube_integration_config.json"
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            print(f"✅ SonarQube integration config exported to {config_path}")
            return True

        except Exception as e:
            print(f"⚠️ Could not export SonarQube config: {e}")
            return False
