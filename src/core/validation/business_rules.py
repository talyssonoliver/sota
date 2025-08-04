
from src.infrastructure.utils.common_imports import (
    Enum,
    dataclass,
    field,
    logging,
    re
)
"""
Business Rules Validation

Centralizes business rule validation that was previously scattered
across 53 files, providing consistent business logic enforcement.
"""

# import asyncio  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
from typing import Dict, Any, Optional, List, TypeVar
from abc import ABC, abstractmethod
# from dataclasses import dataclass, field  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
from .validation_middleware import ValidationResult, IValidationMiddleware

T = TypeVar('T')


class RuleSeverity(Enum):
    """Business rule severity levels"""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"


class RuleCategory(Enum):
    """Business rule categories"""
    DATA_INTEGRITY = "data_integrity"
    BUSINESS_LOGIC = "business_logic"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    WORKFLOW = "workflow"
    AUTHORIZATION = "authorization"


@dataclass
class RuleContext:
    """Context for business rule execution"""
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    operation: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuleViolation:
    """Business rule violation"""
    rule_id: str
    rule_name: str
    severity: RuleSeverity
    category: RuleCategory
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None
    context: Optional[RuleContext] = None
    suggested_fix: Optional[str] = None


class IBusinessRule(ABC):
    """Interface for business rules"""
    
    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique rule identifier"""
        pass
    
    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Human-readable rule name"""
        pass
    
    @property
    @abstractmethod
    def category(self) -> RuleCategory:
        """Rule category"""
        pass
    
    @property
    @abstractmethod
    def severity(self) -> RuleSeverity:
        """Rule severity"""
        pass
    
    @abstractmethod
    async def validate(self, data: Any, context: RuleContext) -> List[RuleViolation]:
        """Validate data against business rule"""
        pass
    
    @abstractmethod
    async def can_validate(self, data_type: str, operation: str) -> bool:
        """Check if rule applies to this data type and operation"""
        pass


class BusinessRuleEngine:
    """Engine for executing business rules"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._rules: Dict[str, IBusinessRule] = {}
        self._rule_chains: Dict[str, List[str]] = {}  # data_type -> rule_ids
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default business rules"""
        # Register common business rules
        self.register_rule(RequiredFieldsRule())
        self.register_rule(DataIntegrityRule())
        self.register_rule(WorkflowStateRule())
        self.register_rule(AuthorizationRule())
        self.register_rule(TaskAssignmentRule())
        self.register_rule(ConfigurationRule())
    
    def register_rule(self, rule: IBusinessRule):
        """Register a business rule"""
        self._rules[rule.rule_id] = rule
        self.logger.debug(f"Registered business rule: {rule.rule_id}")
    
    def unregister_rule(self, rule_id: str) -> bool:
        """Unregister a business rule"""
        if rule_id in self._rules:
            del self._rules[rule_id]
            # Remove from rule chains
            for chain in self._rule_chains.values():
                if rule_id in chain:
                    chain.remove(rule_id)
            self.logger.debug(f"Unregistered business rule: {rule_id}")
            return True
        return False
    
    def add_rule_to_chain(self, data_type: str, rule_id: str):
        """Add rule to data type validation chain"""
        if data_type not in self._rule_chains:
            self._rule_chains[data_type] = []
        if rule_id not in self._rule_chains[data_type]:
            self._rule_chains[data_type].append(rule_id)
    
    async def validate(self, data: Any, data_type: str, 
                      context: Optional[RuleContext] = None) -> List[RuleViolation]:
        """Validate data against all applicable business rules"""
        violations = []
        rule_context = context or RuleContext()
        
        # Get applicable rules
        applicable_rules = await self._get_applicable_rules(data, data_type, rule_context)
        
        # Execute rules
        for rule in applicable_rules:
            try:
                rule_violations = await rule.validate(data, rule_context)
                violations.extend(rule_violations)
            except Exception as e:
                self.logger.error(f"Business rule {rule.rule_id} failed: {e}")
                violations.append(RuleViolation(
                    rule_id=rule.rule_id,
                    rule_name=rule.rule_name,
                    severity=RuleSeverity.ERROR,
                    category=RuleCategory.BUSINESS_LOGIC,
                    message=f"Rule execution failed: {str(e)}",
                    context=rule_context
                ))
        
        return violations
    
    async def _get_applicable_rules(self, data: Any, data_type: str, 
                                   context: RuleContext) -> List[IBusinessRule]:
        """Get rules applicable to the data type and operation"""
        applicable_rules = []
        operation = context.operation or "unknown"
        
        # Check rules in the chain for this data type
        rule_chain = self._rule_chains.get(data_type, [])
        for rule_id in rule_chain:
            rule = self._rules.get(rule_id)
            if rule and await rule.can_validate(data_type, operation):
                applicable_rules.append(rule)
        
        # Check all rules if no specific chain exists
        if not rule_chain:
            for rule in self._rules.values():
                if await rule.can_validate(data_type, operation):
                    applicable_rules.append(rule)
        
        return applicable_rules
    
    def get_rules_by_category(self, category: RuleCategory) -> List[IBusinessRule]:
        """Get rules by category"""
        return [rule for rule in self._rules.values() if rule.category == category]
    
    def get_rule_stats(self) -> Dict[str, Any]:
        """Get business rule statistics"""
        stats = {
            "total_rules": len(self._rules),
            "by_category": {},
            "by_severity": {},
            "rule_chains": {k: len(v) for k, v in self._rule_chains.items()}
        }
        
        for rule in self._rules.values():
            category = rule.category.value
            severity = rule.severity.value
            
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
        
        return stats


# Default business rules implementations

class RequiredFieldsRule(IBusinessRule):
    """Validates required fields are present"""
    
    @property
    def rule_id(self) -> str:
        return "required_fields"
    
    @property
    def rule_name(self) -> str:
        return "Required Fields Validation"
    
    @property
    def category(self) -> RuleCategory:
        return RuleCategory.DATA_INTEGRITY
    
    @property
    def severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR
    
    async def validate(self, data: Any, context: RuleContext) -> List[RuleViolation]:
        violations = []
        
        if not isinstance(data, dict):
            return violations
        
        # Define required fields by entity type
        required_fields = self._get_required_fields(context.entity_type)
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                violations.append(RuleViolation(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    severity=self.severity,
                    category=self.category,
                    message=f"Required field '{field}' is missing or empty",
                    field=field,
                    value=data.get(field),
                    context=context,
                    suggested_fix=f"Please provide a value for '{field}'"
                ))
        
        return violations
    
    async def can_validate(self, data_type: str, operation: str) -> bool:
        return data_type in ["task", "user", "agent", "workflow", "configuration"]
    
    def _get_required_fields(self, entity_type: Optional[str]) -> List[str]:
        """Get required fields for entity type"""
        field_map = {
            "task": ["title", "status", "priority"],
            "user": ["username", "email"],
            "agent": ["name", "type", "capabilities"],
            "workflow": ["name", "definition"],
            "configuration": ["key", "value"]
        }
        return field_map.get(entity_type or "", [])


class DataIntegrityRule(IBusinessRule):
    """Validates data integrity constraints"""
    
    @property
    def rule_id(self) -> str:
        return "data_integrity"
    
    @property
    def rule_name(self) -> str:
        return "Data Integrity Validation"
    
    @property
    def category(self) -> RuleCategory:
        return RuleCategory.DATA_INTEGRITY
    
    @property
    def severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR
    
    async def validate(self, data: Any, context: RuleContext) -> List[RuleViolation]:
        violations = []
        
        if not isinstance(data, dict):
            return violations
        
        # Email format validation
        if "email" in data:
            email = data["email"]
            if email and not self._is_valid_email(email):
                violations.append(RuleViolation(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    severity=self.severity,
                    category=self.category,
                    message=f"Invalid email format: {email}",
                    field="email",
                    value=email,
                    context=context,
                    suggested_fix="Please provide a valid email address"
                ))
        
        # Status validation for tasks
        if context.entity_type == "task" and "status" in data:
            status = data["status"]
            valid_statuses = ["pending", "in_progress", "completed", "failed", "cancelled"]
            if status not in valid_statuses:
                violations.append(RuleViolation(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    severity=self.severity,
                    category=self.category,
                    message=f"Invalid task status: {status}",
                    field="status",
                    value=status,
                    context=context,
                    suggested_fix=f"Status must be one of: {', '.join(valid_statuses)}"
                ))
        
        return violations
    
    async def can_validate(self, data_type: str, operation: str) -> bool:
        return True  # Applies to all data types
    
    def _is_valid_email(self, email: str) -> bool:
        """Simple email validation"""
#         import re  # Consolidated to common_imports
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


class WorkflowStateRule(IBusinessRule):
    """Validates workflow state transitions"""
    
    @property
    def rule_id(self) -> str:
        return "workflow_state"
    
    @property
    def rule_name(self) -> str:
        return "Workflow State Validation"
    
    @property
    def category(self) -> RuleCategory:
        return RuleCategory.WORKFLOW
    
    @property
    def severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR
    
    async def validate(self, data: Any, context: RuleContext) -> List[RuleViolation]:
        violations = []
        
        if not isinstance(data, dict) or "status" not in data:
            return violations
        
        current_status = data.get("current_status")
        new_status = data["status"]
        
        # Define valid transitions
        valid_transitions = {
            "pending": ["in_progress", "cancelled"],
            "in_progress": ["completed", "failed", "cancelled"],
            "completed": [],  # No transitions from completed
            "failed": ["pending", "cancelled"],  # Can retry
            "cancelled": []  # No transitions from cancelled
        }
        
        if current_status and current_status in valid_transitions:
            allowed_statuses = valid_transitions[current_status]
            if new_status not in allowed_statuses:
                violations.append(RuleViolation(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    severity=self.severity,
                    category=self.category,
                    message=f"Invalid status transition from '{current_status}' to '{new_status}'",
                    field="status",
                    value=new_status,
                    context=context,
                    suggested_fix=f"Valid transitions from '{current_status}': {', '.join(allowed_statuses)}"
                ))
        
        return violations
    
    async def can_validate(self, data_type: str, operation: str) -> bool:
        return data_type in ["task", "workflow"] and operation in ["update", "transition"]


class AuthorizationRule(IBusinessRule):
    """Validates user authorization for operations"""
    
    @property
    def rule_id(self) -> str:
        return "authorization"
    
    @property
    def rule_name(self) -> str:
        return "Authorization Validation"
    
    @property
    def category(self) -> RuleCategory:
        return RuleCategory.AUTHORIZATION
    
    @property
    def severity(self) -> RuleSeverity:
        return RuleSeverity.CRITICAL
    
    async def validate(self, data: Any, context: RuleContext) -> List[RuleViolation]:
        violations = []
        
        # Check if user has permission for operation
        if context.user_id and context.operation:
            has_permission = await self._check_permission(
                context.user_id, context.operation, context.entity_type
            )
            
            if not has_permission:
                violations.append(RuleViolation(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    severity=self.severity,
                    category=self.category,
                    message=f"User {context.user_id} not authorized for operation '{context.operation}'",
                    context=context,
                    suggested_fix="Contact administrator for required permissions"
                ))
        
        return violations
    
    async def can_validate(self, data_type: str, operation: str) -> bool:
        # Apply to operations that modify data
        return operation in ["create", "update", "delete", "execute"]
    
    async def _check_permission(self, user_id: str, operation: str, 
                               entity_type: Optional[str]) -> bool:
        """Check user permission (simplified implementation)"""
        # In a real system, this would check against a permission service
        # For now, we'll implement basic rules
        
        # Admin users can do everything
        if user_id == "admin":
            return True
        
        # Basic permission mapping
        allowed_operations = {
            "read": True,  # Everyone can read
            "create": entity_type not in ["configuration", "user"],  # Limited creation
            "update": entity_type in ["task", "workflow"],  # Limited updates
            "delete": False,  # Very limited deletion
            "execute": entity_type == "workflow"  # Limited execution
        }
        
        return allowed_operations.get(operation, False)


class TaskAssignmentRule(IBusinessRule):
    """Validates task assignment logic"""
    
    @property
    def rule_id(self) -> str:
        return "task_assignment"
    
    @property
    def rule_name(self) -> str:
        return "Task Assignment Validation"
    
    @property
    def category(self) -> RuleCategory:
        return RuleCategory.BUSINESS_LOGIC
    
    @property
    def severity(self) -> RuleSeverity:
        return RuleSeverity.WARNING
    
    async def validate(self, data: Any, context: RuleContext) -> List[RuleViolation]:
        violations = []
        
        if not isinstance(data, dict):
            return violations
        
        assigned_to = data.get("assigned_to")
        priority = data.get("priority")
        status = data.get("status")
        
        # High priority tasks should be assigned
        if priority == "high" and not assigned_to:
            violations.append(RuleViolation(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                severity=self.severity,
                category=self.category,
                message="High priority tasks should be assigned to someone",
                field="assigned_to",
                value=assigned_to,
                context=context,
                suggested_fix="Assign high priority task to appropriate team member"
            ))
        
        # In-progress tasks must be assigned
        if status == "in_progress" and not assigned_to:
            violations.append(RuleViolation(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                severity=RuleSeverity.ERROR,
                category=self.category,
                message="In-progress tasks must be assigned",
                field="assigned_to",
                value=assigned_to,
                context=context,
                suggested_fix="Assign task before marking as in-progress"
            ))
        
        return violations
    
    async def can_validate(self, data_type: str, operation: str) -> bool:
        return data_type == "task"


class ConfigurationRule(IBusinessRule):
    """Validates configuration changes"""
    
    @property
    def rule_id(self) -> str:
        return "configuration"
    
    @property
    def rule_name(self) -> str:
        return "Configuration Validation"
    
    @property
    def category(self) -> RuleCategory:
        return RuleCategory.SECURITY
    
    @property
    def severity(self) -> RuleSeverity:
        return RuleSeverity.CRITICAL
    
    async def validate(self, data: Any, context: RuleContext) -> List[RuleViolation]:
        violations = []
        
        if not isinstance(data, dict):
            return violations
        
        key = data.get("key", "")
        value = data.get("value")
        
        # Validate sensitive configuration keys
        sensitive_keys = ["password", "secret", "key", "token", "api_key"]
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            if isinstance(value, str) and len(value) < 8:
                violations.append(RuleViolation(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    severity=self.severity,
                    category=self.category,
                    message=f"Sensitive configuration '{key}' value too short",
                    field="value",
                    value="***",  # Don't log actual value
                    context=context,
                    suggested_fix="Use a stronger value (at least 8 characters)"
                ))
        
        # Validate URL configurations
        if "url" in key.lower() and value:
            if not (str(value).startswith("http://") or str(value).startswith("https://")):
                violations.append(RuleViolation(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    severity=RuleSeverity.ERROR,
                    category=self.category,
                    message=f"URL configuration '{key}' must start with http:// or https://",
                    field="value",
                    value=value,
                    context=context,
                    suggested_fix="Provide a valid URL format"
                ))
        
        return violations
    
    async def can_validate(self, data_type: str, operation: str) -> bool:
        return data_type == "configuration"


class BusinessRuleValidator(IValidationMiddleware):
    """Middleware integration for business rules"""
    
    def __init__(self):
        self.engine = BusinessRuleEngine()
        self.logger = logging.getLogger(__name__)
    
    async def validate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate data using business rules"""
        try:
            # Build rule context
            rule_context = RuleContext()
            if context:
                rule_context.entity_type = context.get("entity_type")
                rule_context.entity_id = context.get("entity_id")
                rule_context.operation = context.get("operation")
                rule_context.user_id = context.get("user_id")
                rule_context.metadata = context.get("metadata", {})
            
            # Get data type
            data_type = context.get("data_type", "unknown") if context else "unknown"
            
            # Execute business rules
            violations = await self.engine.validate(data, data_type, rule_context)
            
            # Convert violations to validation result
            errors = []
            warnings = []
            
            for violation in violations:
                message = f"[{violation.rule_name}] {violation.message}"
                if violation.severity in [RuleSeverity.ERROR, RuleSeverity.CRITICAL]:
                    errors.append(message)
                else:
                    warnings.append(message)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                metadata={"violations": [violation.__dict__ for violation in violations]}
            )
            
        except Exception as e:
            self.logger.error(f"Business rule validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Business rule validation failed: {str(e)}"],
                warnings=[]
            )
    
    async def can_validate(self, data_type: str) -> bool:
        """Check if can validate this data type"""
        return True  # Business rules can apply to any data type
    
    def get_supported_types(self) -> List[str]:
        """Get supported data types"""
        return ["task", "user", "agent", "workflow", "configuration", "request", "response"]


# Global business rule engine
_global_rule_engine: Optional[BusinessRuleEngine] = None


def get_business_rule_engine() -> BusinessRuleEngine:
    """Get global business rule engine"""
    global _global_rule_engine
    if _global_rule_engine is None:
        _global_rule_engine = BusinessRuleEngine()
    return _global_rule_engine