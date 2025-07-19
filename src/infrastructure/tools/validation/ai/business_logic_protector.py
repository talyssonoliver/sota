"""
Business Logic Protector
Protects critical business logic from harmful modifications and ensures compliance.
"""

import ast
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..core.base_validator import BaseValidator


class RiskLevel(Enum):
    """Risk levels for business logic modifications."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BusinessLogicRule:
    """Represents a business logic protection rule."""

    name: str
    pattern: str
    risk_level: RiskLevel
    description: str
    allowed_modifications: List[str]
    requires_approval: bool = False
    auto_block: bool = False


class BusinessLogicProtector(BaseValidator):
    """Protects critical business logic from harmful modifications."""

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize business logic protector."""
        super().__init__(root_path)
        self._load_business_config()
        self.protected_modules = self._identify_protected_modules()
        self.business_rules = self._load_business_rules()
        self.violations: List[Dict] = []
        self.risk_assessments: Dict[str, RiskLevel] = {}

    def _load_business_config(self) -> None:
        """Load business logic protection configuration and merge with base config."""
        config_path = (
            self.root_path
            / "src"
            / "infrastructure"
            / "tools"
            / "validation"
            / "config"
            / "ai_validation_config.json"
        )

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    business_config = config.get("business_logic_protection", {})
                    # Merge business-specific config with base config
                    self.config.update(business_config)
            except Exception:
                pass

        # Set business logic protection defaults if not loaded from config
        business_defaults = {
            "enabled": True,
            "core_modules": [
                "src/core",
                "src/business",
                "src/domain",
                "src/services",
                "src/infrastructure/orchestration",
                "src/infrastructure/memory",
            ],
            "security_modules": [
                "auth",
                "security",
                "permissions",
                "login",
                "token",
                "oauth",
                "jwt",
                "session",
            ],
            "config_files": [
                "config.py",
                "settings.py",
                "constants.py",
                "validation_config.json",
                "pyproject.toml",
                "requirements.txt",
            ],
            "risk_threshold": "MEDIUM",
            "circuit_breaker_threshold": 50,
            "auto_block_critical": True,
            "require_approval_high": True,
            "monitoring_enabled": True,
        }

        # Add business defaults if not already present
        for key, value in business_defaults.items():
            if key not in self.config:
                self.config[key] = value

    def _identify_protected_modules(self) -> Set[str]:
        """Identify modules that contain critical business logic."""
        protected = set()

        # Add core modules from config
        for module in self.config.get("core_modules", []):
            module_path = self.root_path / module
            if module_path.exists():
                protected.add(str(module_path))

        # Add security-related modules
        for file_path in self.python_files:
            file_name = file_path.name.lower()
            if any(
                sec_module in file_name
                for sec_module in self.config.get("security_modules", [])
            ):
                protected.add(str(file_path))

        # Add configuration files
        for config_file in self.config.get("config_files", []):
            config_path = self.root_path / config_file
            if config_path.exists():
                protected.add(str(config_path))

        return protected

    def _load_business_rules(self) -> List[BusinessLogicRule]:
        """Load business logic protection rules."""
        return [
            BusinessLogicRule(
                name="Authentication Bypass",
                pattern=r"(skip_auth|bypass_auth|no_auth|auth.*=.*False)",
                risk_level=RiskLevel.CRITICAL,
                description="Potential authentication bypass detected",
                allowed_modifications=[],
                requires_approval=True,
                auto_block=True,
            ),
            BusinessLogicRule(
                name="Permission Check Removal",
                pattern=r"#.*permission|#.*auth|#.*check",
                risk_level=RiskLevel.HIGH,
                description="Commented out permission or authentication check",
                allowed_modifications=[],
                requires_approval=True,
                auto_block=False,
            ),
            BusinessLogicRule(
                name="Database Direct Access",
                pattern=r"(DELETE|DROP|TRUNCATE|ALTER).*FROM|execute\s*\(.*DELETE",
                risk_level=RiskLevel.HIGH,
                description="Direct database modification detected",
                allowed_modifications=["migration", "setup", "admin"],
                requires_approval=True,
                auto_block=False,
            ),
            BusinessLogicRule(
                name="Security Header Removal",
                pattern=r"#.*(CORS|CSP|X-Frame|X-XSS|Strict-Transport)",
                risk_level=RiskLevel.HIGH,
                description="Security header configuration commented out",
                allowed_modifications=[],
                requires_approval=True,
                auto_block=False,
            ),
            BusinessLogicRule(
                name="Debug Mode Enable",
                pattern=r"(DEBUG|debug)\s*=\s*True",
                risk_level=RiskLevel.MEDIUM,
                description="Debug mode enabled in production code",
                allowed_modifications=["development", "testing"],
                requires_approval=False,
                auto_block=False,
            ),
            BusinessLogicRule(
                name="Hardcoded Credentials",
                pattern=r"(password|secret|key|token)\s*=\s*['\"][^'\"]+['\"]",
                risk_level=RiskLevel.CRITICAL,
                description="Hardcoded credentials detected",
                allowed_modifications=[],
                requires_approval=True,
                auto_block=True,
            ),
            BusinessLogicRule(
                name="Input Validation Bypass",
                pattern=r"#.*validate|#.*sanitize|#.*clean",
                risk_level=RiskLevel.HIGH,
                description="Input validation commented out",
                allowed_modifications=[],
                requires_approval=True,
                auto_block=False,
            ),
            BusinessLogicRule(
                name="Error Handling Removal",
                pattern=r"#.*try|#.*except|#.*error",
                risk_level=RiskLevel.MEDIUM,
                description="Error handling commented out",
                allowed_modifications=["refactoring"],
                requires_approval=False,
                auto_block=False,
            ),
            BusinessLogicRule(
                name="Rate Limiting Bypass",
                pattern=r"#.*rate_limit|#.*throttle|rate.*=.*0",
                risk_level=RiskLevel.HIGH,
                description="Rate limiting bypassed or disabled",
                allowed_modifications=["testing"],
                requires_approval=True,
                auto_block=False,
            ),
            BusinessLogicRule(
                name="Logging Suppression",
                pattern=r"#.*log|#.*audit|log.*=.*False",
                risk_level=RiskLevel.MEDIUM,
                description="Logging or auditing disabled",
                allowed_modifications=["performance"],
                requires_approval=False,
                auto_block=False,
            ),
        ]

    def protect_business_logic(self) -> bool:
        """Run business logic protection analysis."""
        if not self.config.get("enabled", True):
            return True

        if not self.python_files:
            self._collect_files()

        print("🛡️  Business Logic Protection Analysis...")

        # Analyze protected modules
        self._analyze_protected_modules()

        # Check for risky patterns
        self._check_business_rules()

        # Assess overall risk
        self._assess_risk_levels()

        # Check circuit breaker
        self._check_circuit_breaker()

        return not self.has_errors()

    def _analyze_protected_modules(self):
        """Analyze protected modules for potential issues."""
        for file_path in self.python_files:
            if str(file_path) in self.protected_modules:
                self._analyze_protected_file(file_path)

    def _analyze_protected_file(self, file_path: Path):
        """Analyze a protected file for business logic violations."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST for structural analysis
            tree = ast.parse(content)

            # Check for dangerous patterns
            self._check_dangerous_ast_patterns(file_path, tree)

            # Check for security-related modifications
            self._check_security_modifications(file_path, content)

            # Check for configuration changes
            self._check_configuration_changes(file_path, content)

        except Exception as e:
            self.add_issue(
                category="business_logic",
                issue_type="ANALYSIS_ERROR",
                file_path=str(file_path),
                message=f"Could not analyze protected file: {str(e)}",
                severity="error",
            )

    def _check_dangerous_ast_patterns(self, file_path: Path, tree: ast.AST):
        """Check for dangerous AST patterns."""
        dangerous_patterns = [
            # Functions that bypass security
            (ast.FunctionDef, lambda node: "bypass" in node.name.lower()),
            (ast.FunctionDef, lambda node: "skip" in node.name.lower()),
            (ast.FunctionDef, lambda node: "disable" in node.name.lower()),
            # Dangerous function calls
            (
                ast.Call,
                lambda node: isinstance(node.func, ast.Name)
                and node.func.id in ["eval", "exec"],
            ),
            (
                ast.Call,
                lambda node: isinstance(node.func, ast.Attribute)
                and node.func.attr in ["system", "popen"],
            ),
            # Security-related assignments
            (
                ast.Assign,
                lambda node: any(
                    isinstance(target, ast.Name)
                    and any(
                        sec_word in target.id.lower()
                        for sec_word in ["auth", "security", "permission"]
                    )
                    for target in node.targets
                ),
            ),
        ]

        for node in ast.walk(tree):
            for pattern_type, pattern_check in dangerous_patterns:
                if isinstance(node, pattern_type) and pattern_check(node):
                    self.add_issue(
                        category="business_logic",
                        issue_type="SECURITY_ISSUE",
                        file_path=str(file_path),
                        message="Dangerous pattern detected in protected module",
                        line=getattr(node, "lineno", 1),
                        severity="error",
                        fix_suggestion="Review and validate this modification in protected business logic",
                        auto_fixable=False,
                    )

    def _check_security_modifications(self, file_path: Path, content: str):
        """Check for security-related modifications."""
        security_keywords = [
            "authentication",
            "authorization",
            "permission",
            "access_control",
            "security",
            "validate",
            "sanitize",
            "csrf",
            "xss",
            "sql_injection",
        ]

        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for commented out security code
            if line.strip().startswith("#"):
                comment_content = line.strip()[1:].strip().lower()
                if any(keyword in comment_content for keyword in security_keywords):
                    self.add_issue(
                        category="business_logic",
                        issue_type="SECURITY_ISSUE",
                        file_path=str(file_path),
                        message=f"Security-related code commented out: {line.strip()}",
                        line=i,
                        severity="error",
                        fix_suggestion="Verify if this security code should be uncommented",
                        auto_fixable=False,
                    )

    def _check_configuration_changes(self, file_path: Path, content: str):
        """Check for dangerous configuration changes."""
        config_patterns = [
            (r"DEBUG\s*=\s*True", "Debug mode enabled"),
            (r"SECURE_SSL_REDIRECT\s*=\s*False", "SSL redirect disabled"),
            (
                r"SESSION_COOKIE_SECURE\s*=\s*False",
                "Secure cookie setting disabled",
            ),
            (r"ALLOWED_HOSTS\s*=\s*\[.*\*.*\]", "Wildcard allowed hosts"),
            (r"CORS_ORIGIN_ALLOW_ALL\s*=\s*True", "CORS allows all origins"),
        ]

        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            for pattern, message in config_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.add_issue(
                        category="business_logic",
                        issue_type="SECURITY_ISSUE",
                        file_path=str(file_path),
                        message=f"Dangerous configuration: {message}",
                        line=i,
                        severity="error",
                        fix_suggestion=f"Review configuration change: {message}",
                        auto_fixable=False,
                    )

    def _check_business_rules(self):
        """Check all business rules against the codebase."""
        for file_path in self.python_files:
            if str(file_path) in self.protected_modules:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    for rule in self.business_rules:
                        self._check_rule_against_file(rule, file_path, content)

                except Exception:
                    continue

    def _check_rule_against_file(
        self, rule: BusinessLogicRule, file_path: Path, content: str
    ):
        """Check a specific business rule against a file."""
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            if re.search(rule.pattern, line, re.IGNORECASE):
                # Check if this is an allowed modification
                is_allowed = any(
                    allowed in file_path.name.lower() or allowed in content.lower()
                    for allowed in rule.allowed_modifications
                )

                if not is_allowed:
                    severity = self._map_risk_to_severity(rule.risk_level)

                    self.add_issue(
                        category="business_logic",
                        issue_type="ARCHITECTURE_VIOLATION",
                        file_path=str(file_path),
                        message=f"Business rule violation: {rule.description}",
                        line=i,
                        severity=severity,
                        fix_suggestion=f"Review: {rule.description}. Approval required: {rule.requires_approval}",
                        auto_fixable=False,
                    )

                    # Track violation
                    self.violations.append(
                        {
                            "rule": rule.name,
                            "file": str(file_path),
                            "line": i,
                            "risk_level": rule.risk_level.value,
                            "requires_approval": rule.requires_approval,
                            "auto_block": rule.auto_block,
                        }
                    )

    def _map_risk_to_severity(self, risk_level: RiskLevel) -> str:
        """Map risk level to severity level."""
        mapping = {
            RiskLevel.LOW: "info",
            RiskLevel.MEDIUM: "warning",
            RiskLevel.HIGH: "error",
            RiskLevel.CRITICAL: "error",
        }
        return mapping.get(risk_level, "warning")

    def _assess_risk_levels(self):
        """Assess overall risk levels for each file."""
        for file_path in self.python_files:
            if str(file_path) in self.protected_modules:
                file_violations = [
                    v for v in self.violations if v["file"] == str(file_path)
                ]

                if not file_violations:
                    self.risk_assessments[str(file_path)] = RiskLevel.LOW
                else:
                    # Calculate risk based on highest severity violation
                    risk_levels = [
                        RiskLevel[v["risk_level"].upper()] for v in file_violations
                    ]
                    max_risk = max(
                        risk_levels,
                        key=lambda x: [
                            "low",
                            "medium",
                            "high",
                            "critical",
                        ].index(x.value),
                    )
                    self.risk_assessments[str(file_path)] = max_risk

    def _check_circuit_breaker(self):
        """Check if circuit breaker threshold is exceeded."""
        threshold = self.config.get("circuit_breaker_threshold", 50)
        high_risk_violations = [
            v for v in self.violations if v["risk_level"] in ["high", "critical"]
        ]

        if len(high_risk_violations) >= threshold:
            self.add_issue(
                category="business_logic",
                issue_type="ARCHITECTURE_VIOLATION",
                file_path="multiple_files",
                message=f"Circuit breaker triggered: {len(high_risk_violations)} high-risk violations",
                severity="error",
                fix_suggestion="Review and address high-risk business logic violations",
                auto_fixable=False,
            )

    def should_block_modification(self, file_path: str) -> bool:
        """Check if a modification should be blocked."""
        file_violations = [v for v in self.violations if v["file"] == file_path]

        return any(
            v["auto_block"] and v["risk_level"] == "critical" for v in file_violations
        )

    def requires_approval(self, file_path: str) -> bool:
        """Check if modifications require approval."""
        file_violations = [v for v in self.violations if v["file"] == file_path]

        return any(
            v["requires_approval"] and v["risk_level"] in ["high", "critical"]
            for v in file_violations
        )

    def generate_protection_report(self) -> Dict[str, Any]:
        """Generate business logic protection report."""
        return {
            "protected_modules": len(self.protected_modules),
            "total_violations": len(self.violations),
            "risk_distribution": {
                "low": len([v for v in self.violations if v["risk_level"] == "low"]),
                "medium": len(
                    [v for v in self.violations if v["risk_level"] == "medium"]
                ),
                "high": len([v for v in self.violations if v["risk_level"] == "high"]),
                "critical": len(
                    [v for v in self.violations if v["risk_level"] == "critical"]
                ),
            },
            "approval_required": len(
                [v for v in self.violations if v["requires_approval"]]
            ),
            "auto_blocked": len([v for v in self.violations if v["auto_block"]]),
            "violations_by_rule": self._group_violations_by_rule(),
            "risk_assessments": {k: v.value for k, v in self.risk_assessments.items()},
            "recommendations": self._generate_protection_recommendations(),
        }

    def _group_violations_by_rule(self) -> Dict[str, int]:
        """Group violations by rule name."""
        rule_counts = {}
        for violation in self.violations:
            rule_name = violation["rule"]
            rule_counts[rule_name] = rule_counts.get(rule_name, 0) + 1
        return rule_counts

    def _generate_protection_recommendations(self) -> List[str]:
        """Generate protection recommendations."""
        recommendations = []

        critical_violations = [
            v for v in self.violations if v["risk_level"] == "critical"
        ]
        if critical_violations:
            recommendations.append(
                "Immediate review required for critical business logic violations"
            )

        high_violations = [v for v in self.violations if v["risk_level"] == "high"]
        if high_violations:
            recommendations.append("Review and approve high-risk modifications")

        if len(self.violations) > 10:
            recommendations.append("Consider implementing stricter protection rules")

        return recommendations
