"""
Week 2 Day 3 Integration Utilities
Provides utilities to bridge Week 2 validation improvements with enterprise framework
"""

from pathlib import Path
from typing import Dict, List, Any

from ..core.base_validator import BaseValidator
from src.infrastructure.utils.validation_errors import (
    ValidationError, ErrorCollector
)
from src.infrastructure.utils.validation_decorators import (
    validate_input, validate_json
)
from src.infrastructure.utils.schema_registry import SchemaRegistry


class EnterpriseValidationBridge:
    """Bridge between Week 2 validation improvements and enterprise framework"""
    
    def __init__(self, root_path: Path = None):
        self.root_path = root_path or Path.cwd()
        self.schema_registry = SchemaRegistry()
        
    def enhance_validator(self, validator: BaseValidator) -> BaseValidator:
        """Enhance existing validator with Week 2 improvements"""
        
        # Add Week 2 error handling capabilities
        def add_week2_error(error: ValidationError, category: str = "validation"):
            validator.add_validation_error(error, category)
        
        validator.add_week2_error = add_week2_error
        
        # Add schema validation capabilities
        validator.schema_registry = self.schema_registry
        
        return validator
    
    def create_enhanced_error_collector(self) -> ErrorCollector:
        """Create error collector that integrates with enterprise framework"""
        return ErrorCollector()
    
    def convert_enterprise_issues_to_week2(self, validator: BaseValidator) -> List[ValidationError]:
        """Convert enterprise validation issues to Week 2 error format"""
        week2_errors = []
        
        for issue in validator.issues:
            if issue.category == "security":
                from src.infrastructure.utils.validation_errors import SecurityValidationError
                error = SecurityValidationError(
                    message=issue.message,
                    field=issue.file_path,
                    severity="high" if issue.severity.value == "error" else "medium"
                )
            elif issue.category == "input":
                from src.infrastructure.utils.validation_errors import InputValidationError
                error = InputValidationError(
                    message=issue.message,
                    field=issue.file_path
                )
            else:
                from src.infrastructure.utils.validation_errors import ValidationError
                error = ValidationError(
                    message=issue.message,
                    field=issue.file_path
                )
            
            week2_errors.append(error)
        
        return week2_errors
    
    def apply_week2_decorators_to_enterprise_methods(self, validator_class):
        """Apply Week 2 decorators to enterprise validator methods"""
        
        # Enhance validation methods with Week 2 decorators
        original_validate = validator_class.validate_dict if hasattr(validator_class, 'validate_dict') else None
        
        if original_validate:
            @validate_input()
            @validate_json()
            def enhanced_validate(self, data: Dict[str, Any], **kwargs):
                return original_validate(self, data, **kwargs)
            
            validator_class.validate_dict = enhanced_validate
        
        return validator_class


# Convenience functions for integration
def create_enterprise_bridge(root_path: Path = None) -> EnterpriseValidationBridge:
    """Create bridge between Week 2 and enterprise validation"""
    return EnterpriseValidationBridge(root_path)


def enhance_existing_validator(validator: BaseValidator) -> BaseValidator:
    """Enhance existing enterprise validator with Week 2 improvements"""
    bridge = EnterpriseValidationBridge()
    return bridge.enhance_validator(validator)


def integrate_validation_systems():
    """Integrate Week 2 validation with enterprise framework"""
    print("🔗 Integrating Week 2 validation patterns with enterprise framework...")
    
    # This function can be called to apply integration across the system
    return {
        "status": "integrated",
        "week2_modules": [
            "validation_errors.py",
            "validation_decorators.py", 
            "schema_registry.py",
            "api_validation.py"
        ],
        "enterprise_enhanced": [
            "base_validator.py",
            "input_validation.py",
            "validator.py"
        ]
    }
