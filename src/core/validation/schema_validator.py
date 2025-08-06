
from src.infrastructure.utils.common_imports import (
    Enum,
    dataclass,
    field,
    logging,
    re
)
"""
Schema Validation

Provides JSON schema and structural validation to ensure data
conforms to expected formats and types.
"""

# import json  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
# from dataclasses import dataclass, field  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports

from .validation_middleware import IValidationMiddleware, ValidationResult


class SchemaType(Enum):
    """Types of validation schemas"""
    JSON_SCHEMA = "json_schema"
    PYDANTIC = "pydantic"
    CUSTOM = "custom"
    DATACLASS = "dataclass"


@dataclass
class ValidationSchema:
    """Schema definition for validation"""
    name: str
    schema_type: SchemaType
    schema_definition: Dict[str, Any]
    strict_mode: bool = True
    allow_additional_properties: bool = False
    coerce_types: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class ISchemaValidator(ABC):
    """Interface for schema validators"""
    
    @abstractmethod
    def validate_schema(self, data: Any, schema: ValidationSchema) -> ValidationResult:
        """Validate data against schema"""
        pass
    
    @abstractmethod
    def can_validate_schema(self, schema_type: SchemaType) -> bool:
        """Check if can validate this schema type"""
        pass


class JSONSchemaValidator(ISchemaValidator):
    """JSON Schema validator implementation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Try to import jsonschema library (optional)
        try:
            import jsonschema
            self.jsonschema = jsonschema
            self.has_jsonschema = True
        except ImportError:
            self.jsonschema = None
            self.has_jsonschema = False
            self.logger.warning("jsonschema library not available, using basic validation")
    
    def validate_schema(self, data: Any, schema: ValidationSchema) -> ValidationResult:
        """Validate data against JSON schema"""
        errors = []
        warnings = []
        
        if not self.has_jsonschema:
            # Fallback to basic validation
            return self._basic_json_validation(data, schema)
        
        try:
            # Use jsonschema library for full validation
            self.jsonschema.validate(
                instance=data,
                schema=schema.schema_definition
            )
            
            return ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                sanitized_data=data,
                metadata={"validator": "JSONSchemaValidator", "schema": schema.name}
            )
            
        except self.jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
            if hasattr(e, 'path') and e.path:
                errors.append(f"Error path: {'.'.join(str(p) for p in e.path)}")
            
        except self.jsonschema.SchemaError as e:
            errors.append(f"Invalid schema definition: {e.message}")
            
        except Exception as e:
            errors.append(f"Schema validation error: {str(e)}")
        
        return ValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            sanitized_data=data,
            metadata={"validator": "JSONSchemaValidator", "schema": schema.name}
        )
    
    def can_validate_schema(self, schema_type: SchemaType) -> bool:
        """Check if can validate this schema type"""
        return schema_type == SchemaType.JSON_SCHEMA
    
    def _basic_json_validation(self, data: Any, schema: ValidationSchema) -> ValidationResult:
        """Basic JSON validation without jsonschema library"""
        errors = []
        warnings = []
        
        try:
            schema_def = schema.schema_definition
            
            # Basic type validation
            if "type" in schema_def:
                expected_type = schema_def["type"]
                if not self._check_basic_type(data, expected_type):
                    errors.append(f"Expected type '{expected_type}', got '{type(data).__name__}'")
            
            # Basic property validation for objects
            if isinstance(data, dict) and "properties" in schema_def:
                errors.extend(self._validate_object_properties(data, schema_def))
            
            # Basic array validation
            if isinstance(data, list) and "items" in schema_def:
                errors.extend(self._validate_array_items(data, schema_def))
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings + ["Using basic JSON validation (jsonschema library not available)"],
                sanitized_data=data,
                metadata={"validator": "BasicJSONValidator", "schema": schema.name}
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Basic JSON validation failed: {str(e)}"],
                warnings=warnings,
                sanitized_data=data
            )
    
    def _check_basic_type(self, data: Any, expected_type: str) -> bool:
        """Check basic JSON type"""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return False
        
        return isinstance(data, expected_python_type)
    
    def _validate_object_properties(self, data: Dict[str, Any], schema_def: Dict[str, Any]) -> List[str]:
        """Validate object properties"""
        errors = []
        properties = schema_def.get("properties", {})
        required = schema_def.get("required", [])
        
        # Check required properties
        for prop in required:
            if prop not in data:
                errors.append(f"Missing required property: {prop}")
        
        # Check property types
        for prop, value in data.items():
            if prop in properties:
                prop_schema = properties[prop]
                if "type" in prop_schema:
                    if not self._check_basic_type(value, prop_schema["type"]):
                        errors.append(f"Property '{prop}' has wrong type")
        
        return errors
    
    def _validate_array_items(self, data: List[Any], schema_def: Dict[str, Any]) -> List[str]:
        """Validate array items"""
        errors = []
        items_schema = schema_def.get("items", {})
        
        if "type" in items_schema:
            expected_type = items_schema["type"]
            for i, item in enumerate(data):
                if not self._check_basic_type(item, expected_type):
                    errors.append(f"Array item {i} has wrong type")
        
        return errors


class CustomSchemaValidator(ISchemaValidator):
    """Custom schema validator with simple rules"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_schema(self, data: Any, schema: ValidationSchema) -> ValidationResult:
        """Validate data against custom schema"""
        errors = []
        warnings = []
        
        try:
            schema_def = schema.schema_definition
            
            # Apply custom validation rules
            for rule_name, rule_config in schema_def.items():
                rule_errors = self._apply_custom_rule(data, rule_name, rule_config)
                errors.extend(rule_errors)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                sanitized_data=data,
                metadata={"validator": "CustomSchemaValidator", "schema": schema.name}
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Custom schema validation failed: {str(e)}"],
                warnings=warnings,
                sanitized_data=data
            )
    
    def can_validate_schema(self, schema_type: SchemaType) -> bool:
        """Check if can validate this schema type"""
        return schema_type == SchemaType.CUSTOM
    
    def _apply_custom_rule(self, data: Any, rule_name: str, rule_config: Any) -> List[str]:
        """Apply custom validation rule"""
        errors = []
        
        try:
            if rule_name == "min_length" and isinstance(data, (str, list, dict)):
                if len(data) < rule_config:
                    errors.append(f"Data too short: {len(data)} < {rule_config}")
            
            elif rule_name == "max_length" and isinstance(data, (str, list, dict)):
                if len(data) > rule_config:
                    errors.append(f"Data too long: {len(data)} > {rule_config}")
            
            elif rule_name == "allowed_values" and isinstance(rule_config, list):
                if data not in rule_config:
                    errors.append(f"Value not allowed: {data}")
            
            elif rule_name == "forbidden_values" and isinstance(rule_config, list):
                if data in rule_config:
                    errors.append(f"Value forbidden: {data}")
            
            elif rule_name == "pattern" and isinstance(data, str):
#                 import re  # Consolidated to common_imports
                if not re.match(rule_config, data):
                    errors.append(f"Data doesn't match pattern: {rule_config}")
            
            elif rule_name == "custom_function" and callable(rule_config):
                try:
                    result = rule_config(data)
                    if result is not True:
                        errors.append(f"Custom validation failed: {result}")
                except Exception as e:
                    errors.append(f"Custom validation error: {str(e)}")
            
        except Exception as e:
            errors.append(f"Rule '{rule_name}' validation error: {str(e)}")
        
        return errors


class SchemaValidator(IValidationMiddleware):
    """Schema validation middleware"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validators: Dict[SchemaType, ISchemaValidator] = {}
        self.schemas: Dict[str, ValidationSchema] = {}
        
        # Register default validators
        self.validators[SchemaType.JSON_SCHEMA] = JSONSchemaValidator()
        self.validators[SchemaType.CUSTOM] = CustomSchemaValidator()
        
        # Load default schemas
        self._load_default_schemas()
    
    def _load_default_schemas(self):
        """Load default validation schemas"""
        # Request schema
        self.schemas["request"] = ValidationSchema(
            name="request",
            schema_type=SchemaType.CUSTOM,
            schema_definition={
                "max_length": 1000000,  # 1MB max request size
                "forbidden_values": ["<script>", "javascript:"],
            }
        )
        
        # Task schema
        self.schemas["task"] = ValidationSchema(
            name="task",
            schema_type=SchemaType.JSON_SCHEMA,
            schema_definition={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "minLength": 1, "maxLength": 200},
                    "description": {"type": "string", "maxLength": 2000},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "failed", "cancelled"]
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "normal", "high", "critical"]
                    },
                    "assigned_to": {"type": ["string", "null"]},
                    "due_date": {"type": ["string", "null"], "format": "date"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 10
                    }
                },
                "required": ["title", "status"],
                "additionalProperties": False
            }
        )
        
        # User schema
        self.schemas["user"] = ValidationSchema(
            name="user",
            schema_type=SchemaType.JSON_SCHEMA,
            schema_definition={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "minLength": 3, "maxLength": 50},
                    "email": {"type": "string", "format": "email"},
                    "role": {
                        "type": "string",
                        "enum": ["admin", "user", "viewer"]
                    },
                    "active": {"type": "boolean"},
                    "metadata": {"type": "object"}
                },
                "required": ["username", "email"],
                "additionalProperties": False
            }
        )
        
        # Configuration schema
        self.schemas["configuration"] = ValidationSchema(
            name="configuration",
            schema_type=SchemaType.JSON_SCHEMA,
            schema_definition={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "minLength": 1, "maxLength": 100},
                    "value": {"type": ["string", "number", "boolean", "object"]},
                    "description": {"type": "string", "maxLength": 500},
                    "category": {"type": "string", "maxLength": 50},
                    "sensitive": {"type": "boolean"},
                    "environment": {
                        "type": "string",
                        "enum": ["development", "testing", "staging", "production"]
                    }
                },
                "required": ["key", "value"],
                "additionalProperties": False
            }
        )
    
    async def validate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate data against appropriate schema"""
        errors = []
        warnings = []
        
        try:
            # Determine schema to use
            schema_name = self._determine_schema(data, context)
            
            if schema_name not in self.schemas:
                # No specific schema, do basic validation
                return await self._basic_validation(data, context)
            
            schema = self.schemas[schema_name]
            
            # Get appropriate validator
            validator = self.validators.get(schema.schema_type)
            if not validator:
                errors.append(f"No validator available for schema type: {schema.schema_type}")
                return ValidationResult(
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    sanitized_data=data
                )
            
            # Validate against schema
            result = validator.validate_schema(data, schema)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Schema validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Schema validation failed: {str(e)}"],
                warnings=warnings,
                sanitized_data=data
            )
    
    async def can_validate(self, data_type: str) -> bool:
        """Check if can validate this data type"""
        return data_type in ["request", "response", "task", "user", "configuration", "json", "schema"]
    
    def get_supported_types(self) -> List[str]:
        """Get supported data types"""
        return ["request", "response", "task", "user", "configuration", "json", "schema"]
    
    def register_schema(self, schema: ValidationSchema):
        """Register a new validation schema"""
        self.schemas[schema.name] = schema
        self.logger.debug(f"Registered schema: {schema.name}")
    
    def register_validator(self, schema_type: SchemaType, validator: ISchemaValidator):
        """Register a new schema validator"""
        self.validators[schema_type] = validator
        self.logger.debug(f"Registered validator for: {schema_type}")
    
    def _determine_schema(self, data: Any, context: Optional[Dict[str, Any]]) -> Optional[str]:
        """Determine which schema to use for validation"""
        if context:
            # Explicit schema specified
            if "schema" in context:
                return context["schema"]
            
            # Determine by data type
            if "data_type" in context:
                return context["data_type"]
            
            # Determine by entity type
            if "entity_type" in context:
                return context["entity_type"]
            
            # Determine by endpoint
            if "endpoint" in context:
                endpoint = context["endpoint"]
                if "/tasks" in endpoint:
                    return "task"
                elif "/users" in endpoint:
                    return "user"
                elif "/config" in endpoint:
                    return "configuration"
        
        # Try to infer from data structure
        if isinstance(data, dict):
            # Check for common field patterns
            if "title" in data and "status" in data:
                return "task"
            elif "username" in data and "email" in data:
                return "user"
            elif "key" in data and "value" in data:
                return "configuration"
        
        return None
    
    async def _basic_validation(self, data: Any, context: Optional[Dict[str, Any]]) -> ValidationResult:
        """Basic validation when no specific schema is available"""
        errors = []
        warnings = []
        
        try:
            # Basic JSON structure validation
            if isinstance(data, dict):
                # Check for reasonable size
                if len(str(data)) > 1000000:  # 1MB
                    errors.append("Data too large")
                
                # Check for nested depth
                if self._get_dict_depth(data) > 10:
                    warnings.append("Data deeply nested (>10 levels)")
            
            elif isinstance(data, list):
                # Check for reasonable list size
                if len(data) > 10000:
                    errors.append("List too large")
            
            elif isinstance(data, str):
                # Check for reasonable string size
                if len(data) > 100000:  # 100KB
                    errors.append("String too large")
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                sanitized_data=data,
                metadata={"validator": "BasicSchemaValidator"}
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Basic validation failed: {str(e)}"],
                warnings=warnings,
                sanitized_data=data
            )
    
    def _get_dict_depth(self, data: Dict[str, Any], depth: int = 0) -> int:
        """Get maximum depth of nested dictionary"""
        if not isinstance(data, dict):
            return depth
        
        max_depth = depth
        for value in data.values():
            if isinstance(value, dict):
                max_depth = max(max_depth, self._get_dict_depth(value, depth + 1))
        
        return max_depth