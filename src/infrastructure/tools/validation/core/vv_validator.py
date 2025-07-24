"""
Validation and Verification (V&V) Validator
Implements comprehensive V&V based on software engineering principles, coding standards,
vulnerabilities, and OWASP rules.
"""

import ast
import json
import re
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_validator import BaseValidator
from .issue_model import ValidationIssue


class OWASPCategory(Enum):
    """OWASP Top 10 categories."""

    BROKEN_ACCESS_CONTROL = "A01:2021-Broken Access Control"
    CRYPTOGRAPHIC_FAILURES = "A02:2021-Cryptographic Failures"
    INJECTION = "A03:2021-Injection"
    INSECURE_DESIGN = "A04:2021-Insecure Design"
    SECURITY_MISCONFIGURATION = "A05:2021-Security Misconfiguration"
    VULNERABLE_COMPONENTS = "A06:2021-Vulnerable and Outdated Components"
    IDENTIFICATION_FAILURES = "A07:2021-Identification and Authentication Failures"
    SOFTWARE_INTEGRITY = "A08:2021-Software and Data Integrity Failures"
    LOGGING_MONITORING = "A09:2021-Security Logging and Monitoring Failures"
    SSRF = "A10:2021-Server-Side Request Forgery"


@dataclass
class CodingStandard:
    """Coding standard definition."""

    name: str
    category: str
    pattern: str
    message: str
    severity: str
    auto_fixable: bool
    owasp_mapping: Optional[OWASPCategory] = None


@dataclass
class VulnerabilityRule:
    """Security vulnerability rule."""

    rule_id: str
    name: str
    description: str
    pattern: str
    severity: str
    owasp_category: OWASPCategory
    cwe_id: Optional[str] = None
    remediation: str = ""


class VVValidator(BaseValidator):
    """Validation and Verification validator implementing software engineering principles."""

    def __init__(self, root_path: Optional[Path] = None):
        super().__init__(root_path)
        self.coding_standards = self._load_coding_standards()
        self.vulnerability_rules = self._load_vulnerability_rules()
        self.owasp_findings: Dict[OWASPCategory, List[ValidationIssue]] = {}
        self.tool_results: Dict[str, Any] = {}

    def _load_coding_standards(self) -> List[CodingStandard]:
        """Load coding standards based on PEP 8, PEP 257, and industry best practices."""
        return [
            # PEP 8 Standards
            CodingStandard(
                name="line_length",
                category="formatting",
                pattern=r".{89,}",  # Lines longer than 88 characters
                message="Line exceeds maximum length (88 characters)",
                severity="warning",
                auto_fixable=True,
            ),
            CodingStandard(
                name="trailing_whitespace",
                category="formatting",
                pattern=r"[ \t]+$",
                message="Trailing whitespace detected",
                severity="info",
                auto_fixable=True,
            ),
            CodingStandard(
                name="import_order",
                category="imports",
                pattern=r"^from\s+\w+\s+import.*\nimport\s+\w+",
                message="Import order violation (from imports before regular imports)",
                severity="warning",
                auto_fixable=True,
            ),
            # Security Standards
            CodingStandard(
                name="hardcoded_password",
                category="security",
                pattern=r"(password|passwd|pwd)\s*=\s*['\"][^'\"]+['\"]",
                message="Hardcoded password detected",
                severity="error",
                auto_fixable=False,
                owasp_mapping=OWASPCategory.CRYPTOGRAPHIC_FAILURES,
            ),
            CodingStandard(
                name="sql_injection_risk",
                category="security",
                pattern=r"(execute|query)\s*\(\s*['\"].*%.*['\"]",
                message="Potential SQL injection vulnerability",
                severity="error",
                auto_fixable=False,
                owasp_mapping=OWASPCategory.INJECTION,
            ),
            CodingStandard(
                name="debug_mode",
                category="security",
                pattern=r"DEBUG\s*=\s*True",
                message="Debug mode enabled in production code",
                severity="error",
                auto_fixable=False,
                owasp_mapping=OWASPCategory.SECURITY_MISCONFIGURATION,
            ),
            # Code Quality Standards
            CodingStandard(
                name="function_length",
                category="complexity",
                pattern=r"",  # Handled by AST analysis
                message="Function too long (>50 lines)",
                severity="warning",
                auto_fixable=False,
            ),
            CodingStandard(
                name="class_length",
                category="complexity",
                pattern=r"",  # Handled by AST analysis
                message="Class too long (>300 lines)",
                severity="warning",
                auto_fixable=False,
            ),
            CodingStandard(
                name="todo_comments",
                category="maintenance",
                pattern=r"#.*TODO",
                message="TODO comment found - should be tracked in issue tracker",
                severity="info",
                auto_fixable=False,
            ),
            CodingStandard(
                name="fixme_comments",
                category="maintenance",
                pattern=r"#.*FIXME",
                message="FIXME comment found - indicates technical debt",
                severity="warning",
                auto_fixable=False,
            ),
            # Documentation Standards
            CodingStandard(
                name="missing_docstring",
                category="documentation",
                pattern=r"",  # Handled by AST analysis
                message="Missing docstring for public function/class",
                severity="warning",
                auto_fixable=False,
            ),
            CodingStandard(
                name="docstring_format",
                category="documentation",
                pattern=r'"""[^"].*"""',
                message="Docstring should use triple double quotes",
                severity="info",
                auto_fixable=True,
            ),
        ]

    def _load_vulnerability_rules(self) -> List[VulnerabilityRule]:
        """Load OWASP-based vulnerability detection rules."""
        return [
            # A01: Broken Access Control
            VulnerabilityRule(
                rule_id="SEC001",
                name="Missing Authorization Check",
                description="Function appears to perform privileged operations without authorization check",
                pattern=r"(delete|remove|admin|sudo|root)",
                severity="high",
                owasp_category=OWASPCategory.BROKEN_ACCESS_CONTROL,
                cwe_id="CWE-862",
                remediation="Add proper authorization checks before privileged operations",
            ),
            # A02: Cryptographic Failures
            VulnerabilityRule(
                rule_id="SEC002",
                name="Weak Cryptographic Algorithm",
                description="Use of weak or deprecated cryptographic algorithms",
                pattern=r"(md5|sha1|des|rc4)",
                severity="high",
                owasp_category=OWASPCategory.CRYPTOGRAPHIC_FAILURES,
                cwe_id="CWE-327",
                remediation="Use strong cryptographic algorithms like SHA-256 or AES",
            ),
            VulnerabilityRule(
                rule_id="SEC003",
                name="Hardcoded Cryptographic Key",
                description="Cryptographic keys should not be hardcoded",
                pattern=r"(key|secret|token)\s*=\s*['\"][a-zA-Z0-9+/=]{16,}['\"]",
                severity="critical",
                owasp_category=OWASPCategory.CRYPTOGRAPHIC_FAILURES,
                cwe_id="CWE-798",
                remediation="Store cryptographic keys in secure configuration or key management system",
            ),
            # A03: Injection
            VulnerabilityRule(
                rule_id="SEC004",
                name="SQL Injection",
                description="Potential SQL injection vulnerability",
                pattern=r"(execute|query|cursor)\s*\(\s*['\"].*%.*['\"]",
                severity="critical",
                owasp_category=OWASPCategory.INJECTION,
                cwe_id="CWE-89",
                remediation="Use parameterized queries or prepared statements",
            ),
            VulnerabilityRule(
                rule_id="SEC005",
                name="Command Injection",
                description="Potential command injection vulnerability",
                pattern=r"(os\.system|subprocess\.call|subprocess\.run)\s*\([^)]*\+",
                severity="critical",
                owasp_category=OWASPCategory.INJECTION,
                cwe_id="CWE-78",
                remediation="Validate and sanitize input before executing system commands",
            ),
            # A04: Insecure Design
            VulnerabilityRule(
                rule_id="SEC006",
                name="Insufficient Logging",
                description="Security-sensitive operations should be logged",
                pattern=r"(login|authenticate|authorize)",
                severity="medium",
                owasp_category=OWASPCategory.LOGGING_MONITORING,
                cwe_id="CWE-778",
                remediation="Add comprehensive logging for security events",
            ),
            # A05: Security Misconfiguration
            VulnerabilityRule(
                rule_id="SEC007",
                name="Debug Mode in Production",
                description="Debug mode should not be enabled in production",
                pattern=r"DEBUG\s*=\s*True",
                severity="high",
                owasp_category=OWASPCategory.SECURITY_MISCONFIGURATION,
                cwe_id="CWE-489",
                remediation="Disable debug mode in production environments",
            ),
            VulnerabilityRule(
                rule_id="SEC008",
                name="Insecure Random Number Generation",
                description="Use cryptographically secure random number generation",
                pattern=r"random\.(random|randint|choice)",
                severity="medium",
                owasp_category=OWASPCategory.CRYPTOGRAPHIC_FAILURES,
                cwe_id="CWE-338",
                remediation="Use secrets module for cryptographically secure random numbers",
            ),
            # A08: Software and Data Integrity Failures
            VulnerabilityRule(
                rule_id="SEC009",
                name="Unsafe Deserialization",
                description="Unsafe deserialization can lead to remote code execution",
                pattern=r"(pickle\.loads|yaml\.load|eval|exec)",
                severity="critical",
                owasp_category=OWASPCategory.SOFTWARE_INTEGRITY,
                cwe_id="CWE-502",
                remediation="Use safe deserialization methods or validate input data",
            ),
            # A10: Server-Side Request Forgery
            VulnerabilityRule(
                rule_id="SEC010",
                name="Potential SSRF",
                description="Server-side request forgery vulnerability",
                pattern=r"requests\.(get|post|put|delete)\s*\(\s*[^)]*input",
                severity="high",
                owasp_category=OWASPCategory.SSRF,
                cwe_id="CWE-918",
                remediation="Validate and whitelist allowed URLs and domains",
            ),
        ]

    def run_validation_verification(self) -> bool:
        """Run comprehensive V&V analysis."""
        print("🔍 Running Validation & Verification Analysis...")

        if not self.python_files:
            self._collect_files()

        # 1. Run external tool validations
        self._run_external_tools()

        # 2. Check coding standards
        self._validate_coding_standards()

        # 3. Detect security vulnerabilities
        self._detect_vulnerabilities()

        # 4. Perform AST-based analysis
        self._perform_ast_analysis()

        # 5. Generate OWASP compliance report
        self._generate_owasp_report()

        return not self.has_errors()

    def _run_external_tools(self):
        """Run external validation tools (MyPy, Black, Ruff, Bandit)."""
        print("  🛠️ Running external validation tools...")

        results = {}

        # Run MyPy
        results["mypy"] = self._run_mypy()

        # Run Black
        results["black"] = self._run_black()

        # Run Ruff
        results["ruff"] = self._run_ruff()

        # Run Bandit
        results["bandit"] = self._run_bandit()

        return results

    def _run_mypy(self):
        """Run MyPy type checking."""
        try:
            result = subprocess.run(
                ["python", "-m", "mypy", "src/", "--json-report", "mypy-report.json"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=120,
            )

            # Parse MyPy output
            if result.stdout:
                for line in result.stdout.split("\n"):
                    if line.strip() and ":" in line:
                        parts = line.split(":")
                        if len(parts) >= 4:
                            file_path = parts[0]
                            line_no = parts[1]
                            message = ":".join(parts[3:]).strip()

                            self.add_issue(
                                category="type_checking",
                                issue_type="TYPE_ERROR",
                                file_path=file_path,
                                message=f"MyPy: {message}",
                                line=int(line_no) if line_no.isdigit() else 1,
                                severity="error",
                                fix_suggestion="Fix type annotations and type-related issues",
                                auto_fixable=False,
                            )

            self.tool_results["mypy"] = {
                "returncode": result.returncode,
                "issues_found": len([i for i in self.issues if "MyPy" in i.message]),
            }

            return {
                "success": True,
                "issues_found": len([i for i in self.issues if "MyPy" in i.message]),
                "output": result.stdout,
                "returncode": result.returncode,
            }

        except Exception as e:
            print(f"    ⚠️ MyPy execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "issues_found": 0,
                "output": "",
                "returncode": -1,
            }

    def _run_black(self):
        """Run Black code formatting."""
        try:
            # Check formatting
            result = subprocess.run(
                ["python", "-m", "black", "--check", "--diff", "src/"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60,
            )

            if result.returncode != 0 and result.stdout:
                # Parse Black output for files that need formatting
                lines = result.stdout.split("\n")
                for line in lines:
                    if line.startswith("would reformat"):
                        file_path = line.split()[-1]
                        self.add_issue(
                            category="formatting",
                            issue_type="FORMATTING_ERROR",
                            file_path=file_path,
                            message="Black: Code formatting required",
                            severity="warning",
                            fix_suggestion="Run 'black .' to auto-format code",
                            auto_fixable=True,
                        )

            self.tool_results["black"] = {
                "returncode": result.returncode,
                "issues_found": len([i for i in self.issues if "Black" in i.message]),
            }

            return {
                "success": True,
                "issues_found": len([i for i in self.issues if "Black" in i.message]),
                "output": result.stdout,
                "returncode": result.returncode,
            }

        except Exception as e:
            print(f"    ⚠️ Black execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "issues_found": 0,
                "output": "",
                "returncode": -1,
            }

    def _run_ruff(self):
        """Run Ruff linting."""
        try:
            result = subprocess.run(
                ["python", "-m", "ruff", "check", "src/", "--output-format=json"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=120,
            )

            if result.stdout:
                try:
                    ruff_issues = json.loads(result.stdout)
                    for issue in ruff_issues:
                        self.add_issue(
                            category="code_quality",
                            issue_type="LINT_ERROR",
                            file_path=issue.get("filename", "unknown"),
                            message=f"Ruff: {issue.get('message', 'Unknown issue')}",
                            line=issue.get("location", {}).get("row", 1),
                            severity="warning",
                            fix_suggestion=f"Fix {issue.get('code', 'unknown')} violation",
                            auto_fixable=True,
                        )
                except json.JSONDecodeError:
                    pass

            self.tool_results["ruff"] = {
                "returncode": result.returncode,
                "issues_found": len([i for i in self.issues if "Ruff" in i.message]),
            }

            return {
                "success": True,
                "issues_found": len([i for i in self.issues if "Ruff" in i.message]),
                "output": result.stdout,
                "returncode": result.returncode,
            }

        except Exception as e:
            print(f"    ⚠️ Ruff execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "issues_found": 0,
                "output": "",
                "returncode": -1,
            }

    def _run_bandit(self):
        """Run Bandit security analysis."""
        try:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "bandit",
                    "-r",
                    "src/",
                    "-f",
                    "json",
                    "-o",
                    "bandit-report.json",
                ],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=120,
            )

            bandit_report = self.root_path / "bandit-report.json"
            if bandit_report.exists():
                with open(bandit_report) as f:
                    bandit_data = json.load(f)

                for issue in bandit_data.get("results", []):
                    severity_mapping = {
                        "HIGH": "error",
                        "MEDIUM": "warning",
                        "LOW": "info",
                    }

                    severity = severity_mapping.get(
                        issue.get("issue_severity", "LOW"), "info"
                    )

                    self.add_issue(
                        category="security",
                        issue_type="SECURITY_VULNERABILITY",
                        file_path=issue.get("filename", "unknown"),
                        message=f"Bandit: {issue.get('issue_text', 'Security issue')}",
                        line=issue.get("line_number", 1),
                        severity=severity,
                        fix_suggestion=f"Address {issue.get('test_id', 'security')} vulnerability",
                        auto_fixable=False,
                    )

            self.tool_results["bandit"] = {
                "returncode": result.returncode,
                "issues_found": len([i for i in self.issues if "Bandit" in i.message]),
            }

            return {
                "success": True,
                "issues_found": len([i for i in self.issues if "Bandit" in i.message]),
                "output": result.stdout,
                "returncode": result.returncode,
            }

        except Exception as e:
            print(f"    ⚠️ Bandit execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "issues_found": 0,
                "output": "",
                "returncode": -1,
            }

    def _validate_coding_standards(self):
        """Validate coding standards compliance."""
        print("  📋 Validating coding standards...")

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    for standard in self.coding_standards:
                        if standard.pattern and re.search(standard.pattern, line):
                            self.add_issue(
                                category="coding_standards",
                                issue_type="STANDARD_VIOLATION",
                                file_path=str(file_path),
                                message=f"Coding Standard: {standard.message}",
                                line=i,
                                severity=standard.severity,
                                fix_suggestion=f"Follow {standard.name} coding standard",
                                auto_fixable=standard.auto_fixable,
                            )

            except Exception:
                continue

    def _detect_vulnerabilities(self):
        """Detect security vulnerabilities using OWASP rules."""
        print("  🔒 Detecting security vulnerabilities...")

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    for rule in self.vulnerability_rules:
                        if re.search(rule.pattern, line, re.IGNORECASE):
                            issue = self.add_issue(
                                category="security",
                                issue_type="VULNERABILITY",
                                file_path=str(file_path),
                                message=f"{rule.name}: {rule.description}",
                                line=i,
                                severity=rule.severity,
                                fix_suggestion=rule.remediation,
                                auto_fixable=False,
                            )

                            # Track OWASP mapping
                            if rule.owasp_category not in self.owasp_findings:
                                self.owasp_findings[rule.owasp_category] = []
                            self.owasp_findings[rule.owasp_category].append(issue)

            except Exception:
                continue

    def _perform_ast_analysis(self):
        """Perform AST-based code analysis."""
        print("  🌳 Performing AST analysis...")

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                # Check function and class lengths
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_length = self._get_node_length(node, content)
                        if func_length > 50:
                            self.add_issue(
                                category="complexity",
                                issue_type="FUNCTION_TOO_LONG",
                                file_path=str(file_path),
                                message=f"Function '{node.name}' is too long ({func_length} lines)",
                                line=node.lineno,
                                severity="warning",
                                fix_suggestion="Break down function into smaller, more manageable pieces",
                                auto_fixable=False,
                            )

                        # Check for missing docstrings
                        if not ast.get_docstring(node) and not node.name.startswith(
                            "_"
                        ):
                            self.add_issue(
                                category="documentation",
                                issue_type="MISSING_DOCSTRING",
                                file_path=str(file_path),
                                message=f"Public function '{node.name}' missing docstring",
                                line=node.lineno,
                                severity="warning",
                                fix_suggestion="Add docstring describing function purpose and parameters",
                                auto_fixable=False,
                            )

                    elif isinstance(node, ast.ClassDef):
                        class_length = self._get_node_length(node, content)
                        if class_length > 300:
                            self.add_issue(
                                category="complexity",
                                issue_type="CLASS_TOO_LONG",
                                file_path=str(file_path),
                                message=f"Class '{node.name}' is too long ({class_length} lines)",
                                line=node.lineno,
                                severity="warning",
                                fix_suggestion="Consider breaking class into smaller, more focused classes",
                                auto_fixable=False,
                            )

                        # Check for missing docstrings
                        if not ast.get_docstring(node) and not node.name.startswith(
                            "_"
                        ):
                            self.add_issue(
                                category="documentation",
                                issue_type="MISSING_DOCSTRING",
                                file_path=str(file_path),
                                message=f"Public class '{node.name}' missing docstring",
                                line=node.lineno,
                                severity="warning",
                                fix_suggestion="Add docstring describing class purpose",
                                auto_fixable=False,
                            )

            except Exception:
                continue

    def _get_node_length(self, node: ast.AST, content: str) -> int:
        """Calculate the length of an AST node in lines."""
        start_line = node.lineno
        end_line = getattr(node, "end_lineno", start_line)
        return end_line - start_line + 1 if end_line else 1

    def _generate_owasp_report(self):
        """Generate OWASP Top 10 compliance report."""
        print("  📊 Generating OWASP compliance report...")

        owasp_report = {
            "timestamp": time.time(),
            "total_vulnerabilities": sum(
                len(issues) for issues in self.owasp_findings.values()
            ),
            "categories": {},
        }

        for category in OWASPCategory:
            issues = self.owasp_findings.get(category, [])
            owasp_report["categories"][category.value] = {
                "issues_count": len(issues),
                "status": "COMPLIANT" if len(issues) == 0 else "NON_COMPLIANT",
                "severity_breakdown": self._get_severity_breakdown(issues),
            }

        # Save OWASP report
        report_path = self.root_path / "reports" / "owasp_compliance_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(owasp_report, f, indent=2, default=str)
            print(f"    📄 OWASP report saved to: {report_path}")
        except Exception as e:
            print(f"    ⚠️ Failed to save OWASP report: {e}")

    def _get_severity_breakdown(self, issues: List[ValidationIssue]) -> Dict[str, int]:
        """Get severity breakdown for a list of issues."""
        breakdown = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "error": 0,
            "warning": 0,
            "info": 0,
        }

        for issue in issues:
            if issue is None:
                continue
            severity = getattr(issue, "severity", "unknown")
            if severity in breakdown:
                breakdown[severity] += 1

        return breakdown

    def generate_vv_report(self) -> Dict[str, Any]:
        """Generate comprehensive V&V report."""
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "validation_verification": {
                "summary": {
                    "total_issues": len(self.issues),
                    "critical_issues": len(
                        [i for i in self.issues if i.severity == "error"]
                    ),
                    "warnings": len(
                        [i for i in self.issues if i.severity == "warning"]
                    ),
                    "info": len([i for i in self.issues if i.severity == "info"]),
                    "files_analyzed": len(self.python_files),
                    "validation_passed": not self.has_errors(),
                },
                "coding_standards": {
                    "total_violations": len(
                        [i for i in self.issues if i.category == "coding_standards"]
                    ),
                    "auto_fixable": len(
                        [
                            i
                            for i in self.issues
                            if i.category == "coding_standards" and i.auto_fixable
                        ]
                    ),
                },
                "security_vulnerabilities": {
                    "total_vulnerabilities": len(
                        [i for i in self.issues if i.category == "security"]
                    ),
                    "by_owasp_category": {
                        cat.value: len(issues)
                        for cat, issues in self.owasp_findings.items()
                    },
                },
                "external_tools": self.tool_results,
                "compliance": {
                    "owasp_top_10": self._assess_owasp_compliance(),
                    "pep8_compliance": self._assess_pep8_compliance(),
                },
            },
            "recommendations": self._generate_vv_recommendations(),
        }

    def _assess_owasp_compliance(self) -> Dict[str, Any]:
        """Assess OWASP Top 10 compliance."""
        compliant_categories = 0
        total_categories = len(OWASPCategory)

        for category in OWASPCategory:
            if len(self.owasp_findings.get(category, [])) == 0:
                compliant_categories += 1

        compliance_percentage = (compliant_categories / total_categories) * 100

        return {
            "compliance_percentage": compliance_percentage,
            "compliant_categories": compliant_categories,
            "total_categories": total_categories,
            "status": "COMPLIANT" if compliance_percentage == 100 else "NON_COMPLIANT",
        }

    def _assess_pep8_compliance(self) -> Dict[str, Any]:
        """Assess PEP 8 compliance."""
        pep8_issues = [
            i for i in self.issues if i.category in ["formatting", "coding_standards"]
        ]
        total_files = len(self.python_files)
        files_with_issues = len(set(issue.file_path for issue in pep8_issues))

        compliance_percentage = (
            ((total_files - files_with_issues) / total_files) * 100
            if total_files > 0
            else 100
        )

        return {
            "compliance_percentage": compliance_percentage,
            "files_compliant": total_files - files_with_issues,
            "total_files": total_files,
            "total_violations": len(pep8_issues),
            "status": "COMPLIANT" if compliance_percentage >= 95 else "NON_COMPLIANT",
        }

    def _validate_vulnerabilities(self) -> Dict[str, Any]:
        """Validate vulnerabilities and return summary."""
        vulnerabilities = {
            "total_vulnerabilities": 0,
            "vulnerabilities_by_type": {},
            "high_severity_count": 0,
            "medium_severity_count": 0,
            "low_severity_count": 0,
        }

        # Initialize vulnerability types based on OWASP categories
        for category in OWASPCategory:
            vulnerabilities["vulnerabilities_by_type"][
                category.value.lower()
                .replace(" ", "_")
                .replace(":", "")
                .replace("-", "_")
            ] = 0

        # Count vulnerabilities from detection
        security_issues = [i for i in self.issues if i.category == "security"]
        vulnerabilities["total_vulnerabilities"] = len(security_issues)

        for issue in security_issues:
            if issue.severity in ["critical", "high"]:
                vulnerabilities["high_severity_count"] += 1
            elif issue.severity == "medium":
                vulnerabilities["medium_severity_count"] += 1
            else:
                vulnerabilities["low_severity_count"] += 1

        # Count by OWASP category
        for category, issues in self.owasp_findings.items():
            key = (
                category.value.lower()
                .replace(" ", "_")
                .replace(":", "")
                .replace("-", "_")
            )
            if key in vulnerabilities["vulnerabilities_by_type"]:
                vulnerabilities["vulnerabilities_by_type"][key] = len(issues)

        return vulnerabilities

    def _validate_coding_standards(self) -> Dict[str, Any]:
        """Validate coding standards and return compliance metrics."""
        compliance = {
            "pep8_compliance": {"compliance_percentage": 0, "violations": 0},
            "docstring_coverage": {"compliance_percentage": 0, "violations": 0},
            "function_naming": {"compliance_percentage": 0, "violations": 0},
            "overall_compliance": {"compliance_percentage": 0, "violations": 0},
        }

        # Count standards violations
        standards_issues = [i for i in self.issues if i.category == "coding_standards"]
        total_files = len(self.python_files)

        if total_files == 0:
            return compliance

        # PEP8 compliance
        pep8_issues = [
            i
            for i in standards_issues
            if "pep8" in i.message.lower() or "formatting" in i.message.lower()
        ]
        pep8_compliance = max(0, 100 - (len(pep8_issues) / total_files * 100))
        compliance["pep8_compliance"] = {
            "compliance_percentage": pep8_compliance,
            "violations": len(pep8_issues),
        }

        # Docstring coverage
        docstring_issues = [i for i in self.issues if "docstring" in i.message.lower()]
        docstring_compliance = max(0, 100 - (len(docstring_issues) / total_files * 100))
        compliance["docstring_coverage"] = {
            "compliance_percentage": docstring_compliance,
            "violations": len(docstring_issues),
        }

        # Function naming compliance
        naming_issues = [i for i in standards_issues if "naming" in i.message.lower()]
        naming_compliance = max(0, 100 - (len(naming_issues) / total_files * 100))
        compliance["function_naming"] = {
            "compliance_percentage": naming_compliance,
            "violations": len(naming_issues),
        }

        # Overall compliance
        overall_compliance = (
            pep8_compliance + docstring_compliance + naming_compliance
        ) / 3
        compliance["overall_compliance"] = {
            "compliance_percentage": overall_compliance,
            "violations": len(standards_issues),
        }

        return compliance

    def _calculate_owasp_compliance(
        self, vulnerabilities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate OWASP Top 10 compliance."""
        total_categories = len(OWASPCategory)
        compliant_categories = 0

        vulnerabilities_by_category = vulnerabilities.get("vulnerabilities_by_type", {})

        for category in OWASPCategory:
            key = (
                category.value.lower()
                .replace(" ", "_")
                .replace(":", "")
                .replace("-", "_")
            )
            if vulnerabilities_by_category.get(key, 0) == 0:
                compliant_categories += 1

        compliance_percentage = (compliant_categories / total_categories) * 100

        return {
            "compliance_percentage": compliance_percentage,
            "categories_compliant": compliant_categories,
            "categories_total": total_categories,
            "vulnerabilities_by_category": vulnerabilities_by_category,
            "status": "COMPLIANT" if compliance_percentage == 100 else "NON_COMPLIANT",
        }

    def _generate_vv_recommendations(self) -> List[str]:
        """Generate V&V recommendations."""
        recommendations = []

        # Security recommendations
        security_issues = [i for i in self.issues if i.category == "security"]
        if security_issues:
            recommendations.append(
                f"🔒 Address {len(security_issues)} security vulnerabilities immediately"
            )

            # OWASP-specific recommendations
            for category, issues in self.owasp_findings.items():
                if issues:
                    recommendations.append(
                        f"  - {category.value}: {len(issues)} issues"
                    )

        # Code quality recommendations
        quality_issues = [
            i for i in self.issues if i.category in ["code_quality", "complexity"]
        ]
        if quality_issues:
            recommendations.append(
                f"📊 Improve code quality: {len(quality_issues)} issues found"
            )

        # Tool-specific recommendations
        for tool, results in self.tool_results.items():
            if results.get("issues_found", 0) > 0:
                recommendations.append(
                    f"🛠️ Run {tool} to fix {results['issues_found']} issues"
                )

        if not recommendations:
            recommendations.append(
                "✅ All V&V checks passed! Excellent code quality and security posture."
            )

        return recommendations
