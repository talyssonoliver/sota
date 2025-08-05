
from src.infrastructure.utils.common_imports import (
    Enum,
    dataclass,
    datetime,
    logging
)
"""
Business Rules Engine

Centralizes all business rules and policies that were previously
scattered across infrastructure and interface layers.

Extracted from src/infrastructure/tools/validation/ai/business_logic_protector.py
"""

# import logging  # Consolidated to common_imports
from abc import ABC, abstractmethod
# from dataclasses import dataclass  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of business rules"""

    VALIDATION = "validation"
    EXECUTION_POLICY = "execution_policy"
    SECURITY_POLICY = "security_policy"
    QUALITY_GATE = "quality_gate"
    BUSINESS_CONSTRAINT = "business_constraint"


class RuleSeverity(Enum):
    """Severity levels for rule violations"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class RuleViolation:
    """Represents a business rule violation"""

    rule_id: str
    rule_name: str
    severity: RuleSeverity
    message: str
    context: Dict[str, Any]
    timestamp: datetime
    suggested_actions: List[str]


@dataclass
class RuleExecutionResult:
    """Result of business rule execution"""

    success: bool
    violations: List[RuleViolation]
    warnings: List[str]
    execution_time: float
    metadata: Dict[str, Any]


class BusinessRule(ABC):
    """Abstract base class for business rules"""

    def __init__(
        self, rule_id: str, name: str, rule_type: RuleType, severity: RuleSeverity
    ):
        self.rule_id = rule_id
        self.name = name
        self.rule_type = rule_type
        self.severity = severity
        self.enabled = True

    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> RuleExecutionResult:
        """Evaluate the business rule against the given context"""
        pass

    def is_applicable(self, context: Dict[str, Any]) -> bool:
        """Check if this rule is applicable to the given context"""
        return self.enabled


class ValidationRule(BusinessRule):
    """Business validation rule implementation"""

    def __init__(
        self,
        rule_id: str,
        name: str,
        validator: Callable[[Dict[str, Any]], bool],
        error_message: str,
        severity: RuleSeverity = RuleSeverity.ERROR,
    ):
        super().__init__(rule_id, name, RuleType.VALIDATION, severity)
        self.validator = validator
        self.error_message = error_message

    def evaluate(self, context: Dict[str, Any]) -> RuleExecutionResult:
        """Evaluate validation rule"""
        start_time = datetime.now()
        violations = []
        warnings = []

        try:
            if not self.validator(context):
                violation = RuleViolation(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    severity=self.severity,
                    message=self.error_message,
                    context=context,
                    timestamp=datetime.now(),
                    suggested_actions=self._get_suggested_actions(context),
                )
                violations.append(violation)

            execution_time = (datetime.now() - start_time).total_seconds()

            return RuleExecutionResult(
                success=len(violations) == 0,
                violations=violations,
                warnings=warnings,
                execution_time=execution_time,
                metadata={"rule_type": "validation"},
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error evaluating rule {self.rule_id}: {e}")

            violation = RuleViolation(
                rule_id=self.rule_id,
                rule_name=self.name,
                severity=RuleSeverity.CRITICAL,
                message=f"Rule evaluation failed: {str(e)}",
                context=context,
                timestamp=datetime.now(),
                suggested_actions=["Check rule implementation", "Review input data"],
            )

            return RuleExecutionResult(
                success=False,
                violations=[violation],
                warnings=[],
                execution_time=execution_time,
                metadata={"error": str(e)},
            )

    def _get_suggested_actions(self, context: Dict[str, Any]) -> List[str]:
        """Get suggested actions for rule violation"""
        return ["Review input data", "Check business requirements"]


class ExecutionPolicy(BusinessRule):
    """Business execution policy implementation"""

    def __init__(
        self,
        rule_id: str,
        name: str,
        policy_check: Callable[[Dict[str, Any]], bool],
        policy_message: str,
        severity: RuleSeverity = RuleSeverity.WARNING,
    ):
        super().__init__(rule_id, name, RuleType.EXECUTION_POLICY, severity)
        self.policy_check = policy_check
        self.policy_message = policy_message

    def evaluate(self, context: Dict[str, Any]) -> RuleExecutionResult:
        """Evaluate execution policy"""
        start_time = datetime.now()
        violations = []
        warnings = []

        try:
            if not self.policy_check(context):
                violation = RuleViolation(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    severity=self.severity,
                    message=self.policy_message,
                    context=context,
                    timestamp=datetime.now(),
                    suggested_actions=self._get_policy_actions(context),
                )
                violations.append(violation)

            execution_time = (datetime.now() - start_time).total_seconds()

            return RuleExecutionResult(
                success=len(violations) == 0,
                violations=violations,
                warnings=warnings,
                execution_time=execution_time,
                metadata={"rule_type": "execution_policy"},
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error evaluating policy {self.rule_id}: {e}")

            return RuleExecutionResult(
                success=False,
                violations=[],
                warnings=[f"Policy evaluation failed: {str(e)}"],
                execution_time=execution_time,
                metadata={"error": str(e)},
            )

    def _get_policy_actions(self, context: Dict[str, Any]) -> List[str]:
        """Get suggested actions for policy violation"""
        return ["Review execution parameters", "Check resource availability"]


class BusinessRuleEngine:
    """
    Central business rule engine.

    Consolidates business logic that was previously scattered across
    infrastructure validation tools and interface layers.
    """

    def __init__(self):
        """Initialize business rule engine"""
        self.rules: Dict[str, BusinessRule] = {}
        self.rule_groups: Dict[str, List[str]] = {}
        self._register_default_rules()

    def register_rule(self, rule: BusinessRule):
        """Register a business rule"""
        self.rules[rule.rule_id] = rule
        logger.info(f"Registered business rule: {rule.rule_id}")

    def register_rule_group(self, group_name: str, rule_ids: List[str]):
        """Register a group of related rules"""
        self.rule_groups[group_name] = rule_ids
        logger.info(f"Registered rule group: {group_name} with {len(rule_ids)} rules")

    def evaluate_rules(
        self,
        context: Dict[str, Any],
        rule_ids: Optional[List[str]] = None,
        rule_group: Optional[str] = None,
    ) -> Dict[str, RuleExecutionResult]:
        """
        Evaluate business rules against context

        Args:
            context: Business context to evaluate
            rule_ids: Specific rules to evaluate (if None, evaluates all applicable)
            rule_group: Rule group to evaluate

        Returns:
            Dictionary of rule results keyed by rule_id
        """
        if rule_group and rule_group in self.rule_groups:
            rule_ids = self.rule_groups[rule_group]
        elif rule_ids is None:
            rule_ids = list(self.rules.keys())

        results = {}
        for rule_id in rule_ids:
            if rule_id in self.rules:
                rule = self.rules[rule_id]
                if rule.is_applicable(context):
                    results[rule_id] = rule.evaluate(context)
                else:
                    logger.debug(f"Rule {rule_id} not applicable to context")
            else:
                logger.warning(f"Rule {rule_id} not found")

        return results

    def validate_checkpoint_approval(
        self, context: Dict[str, Any]
    ) -> RuleExecutionResult:
        """Validate checkpoint approval against business rules"""
        return self._evaluate_rule_group("checkpoint_approval", context)

    def validate_task_execution(self, context: Dict[str, Any]) -> RuleExecutionResult:
        """Validate task execution against business rules"""
        return self._evaluate_rule_group("task_execution", context)

    def validate_agent_assignment(self, context: Dict[str, Any]) -> RuleExecutionResult:
        """Validate agent assignment against business rules"""
        return self._evaluate_rule_group("agent_assignment", context)

    def check_security_policies(self, context: Dict[str, Any]) -> RuleExecutionResult:
        """Check security policies"""
        return self._evaluate_rule_group("security_policies", context)

    def validate_quality_gates(self, context: Dict[str, Any]) -> RuleExecutionResult:
        """Validate quality gates"""
        return self._evaluate_rule_group("quality_gates", context)

    def _evaluate_rule_group(
        self, group_name: str, context: Dict[str, Any]
    ) -> RuleExecutionResult:
        """Evaluate a group of rules and consolidate results"""
        results = self.evaluate_rules(context, rule_group=group_name)

        all_violations = []
        all_warnings = []
        total_execution_time = 0.0
        overall_success = True

        for result in results.values():
            all_violations.extend(result.violations)
            all_warnings.extend(result.warnings)
            total_execution_time += result.execution_time
            if not result.success:
                overall_success = False

        return RuleExecutionResult(
            success=overall_success,
            violations=all_violations,
            warnings=all_warnings,
            execution_time=total_execution_time,
            metadata={"group": group_name, "rules_evaluated": len(results)},
        )

    def _register_default_rules(self):
        """Register default business rules"""

        # Checkpoint approval rules
        self.register_rule(
            ValidationRule(
                rule_id="checkpoint_requires_reviewer",
                name="Checkpoint Requires Reviewer",
                validator=lambda ctx: ctx.get("reviewer_id") is not None,
                error_message="Checkpoint approval requires a reviewer ID",
            )
        )

        self.register_rule(
            ValidationRule(
                rule_id="checkpoint_must_be_pending",
                name="Checkpoint Must Be Pending",
                validator=lambda ctx: ctx.get("checkpoint_status") == "pending",
                error_message="Only pending checkpoints can be approved",
            )
        )

        # Task execution rules
        self.register_rule(
            ValidationRule(
                rule_id="task_requires_id",
                name="Task Requires ID",
                validator=lambda ctx: ctx.get("task_id") is not None,
                error_message="Task execution requires a task ID",
            )
        )

        self.register_rule(
            ExecutionPolicy(
                rule_id="max_concurrent_tasks",
                name="Maximum Concurrent Tasks",
                policy_check=lambda ctx: ctx.get("concurrent_tasks", 0) < 10,
                policy_message="Maximum concurrent tasks limit exceeded",
            )
        )

        # Agent assignment rules
        self.register_rule(
            ValidationRule(
                rule_id="agent_type_valid",
                name="Agent Type Valid",
                validator=lambda ctx: ctx.get("agent_type")
                in [
                    "backend",
                    "frontend",
                    "qa",
                    "coordinator",
                    "technical",
                    "documentation",
                ],
                error_message="Invalid agent type specified",
            )
        )

        # Security policies
        self.register_rule(
            ExecutionPolicy(
                rule_id="secure_task_execution",
                name="Secure Task Execution",
                policy_check=lambda ctx: not self._contains_sensitive_data(ctx),
                policy_message="Task contains sensitive data requiring additional security measures",
                severity=RuleSeverity.CRITICAL,
            )
        )

        # Quality gates
        self.register_rule(
            ValidationRule(
                rule_id="minimum_test_coverage",
                name="Minimum Test Coverage",
                validator=lambda ctx: ctx.get("test_coverage", 0) >= 80,
                error_message="Test coverage below minimum threshold (80%)",
                severity=RuleSeverity.WARNING,
            )
        )

        # Register rule groups
        self.register_rule_group(
            "checkpoint_approval",
            ["checkpoint_requires_reviewer", "checkpoint_must_be_pending"],
        )

        self.register_rule_group(
            "task_execution",
            ["task_requires_id", "max_concurrent_tasks", "secure_task_execution"],
        )

        self.register_rule_group("agent_assignment", ["agent_type_valid"])

        self.register_rule_group("quality_gates", ["minimum_test_coverage"])

        self.register_rule_group("security_policies", ["secure_task_execution"])

    def _contains_sensitive_data(self, context: Dict[str, Any]) -> bool:
        """Check if context contains sensitive data"""
        sensitive_patterns = ["password", "token", "secret", "key", "credential"]
        content = str(context).lower()
        return any(pattern in content for pattern in sensitive_patterns)

    def get_rule_summary(self) -> Dict[str, Any]:
        """Get summary of registered rules"""
        return {
            "total_rules": len(self.rules),
            "rule_groups": len(self.rule_groups),
            "rules_by_type": {
                rule_type.value: len(
                    [r for r in self.rules.values() if r.rule_type == rule_type]
                )
                for rule_type in RuleType
            },
            "rules_by_severity": {
                severity.value: len(
                    [r for r in self.rules.values() if r.severity == severity]
                )
                for severity in RuleSeverity
            },
        }


# Global business rule engine instance
_rule_engine = None


def get_business_rule_engine() -> BusinessRuleEngine:
    """Get the global business rule engine instance"""
    global _rule_engine
    if _rule_engine is None:
        _rule_engine = BusinessRuleEngine()
    return _rule_engine
