
from src.infrastructure.utils.common_imports import (
    Enum,
    dataclass,
    logging,
    re
)
"""
Input Validation

Provides comprehensive input validation and sanitization to prevent
malicious or malformed data from entering the system.
"""

# import re  # Consolidated to common_imports
import html
# import logging  # Consolidated to common_imports
from typing import Dict, Any, Optional, List, Union, Callable
from abc import ABC, abstractmethod
# from dataclasses import dataclass  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports

from .validation_middleware import IValidationMiddleware, ValidationResult


class SanitizationMode(Enum):
    """Input sanitization modes"""
    NONE = "none"
    BASIC = "basic"           # Basic HTML/script sanitization
    AGGRESSIVE = "aggressive"  # Strict sanitization with whitelist
    CUSTOM = "custom"         # Custom sanitization rules


class InputType(Enum):
    """Types of input data"""
    TEXT = "text"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    JSON = "json"
    XML = "xml"
    HTML = "html"
    SQL = "sql"
    COMMAND = "command"
    PATH = "path"
    FILENAME = "filename"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    UUID = "uuid"
    BASE64 = "base64"
    HEX = "hex"


@dataclass
class InputConstraints:
    """Constraints for input validation"""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    forbidden_values: Optional[List[Any]] = None
    required: bool = True
    allow_empty: bool = False
    sanitization_mode: SanitizationMode = SanitizationMode.BASIC


class IInputSanitizer(ABC):
    """Interface for input sanitizers"""
    
    @abstractmethod
    def sanitize(self, value: Any, input_type: InputType, 
                constraints: Optional[InputConstraints] = None) -> Any:
        """Sanitize input value"""
        pass
    
    @abstractmethod
    def can_sanitize(self, input_type: InputType) -> bool:
        """Check if can sanitize this input type"""
        pass


class BasicInputSanitizer(IInputSanitizer):
    """Basic input sanitizer for common security threats"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Dangerous patterns to remove/escape
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'<form[^>]*>.*?</form>',
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(\bOR\b\s+\d+\s*=\s*\d+)',
            r'(\bAND\b\s+\d+\s*=\s*\d+)',
            r'(--|#|/\*|\*/)',
            r"('|\"|`)",  # Quote characters
        ]
        
        # Command injection patterns
        self.command_patterns = [
            r'(\||&|;|\$\(|\`)',
            r'(\.\./|\.\.\\)',
            r'(rm\s|del\s|format\s)',
        ]
    
    def sanitize(self, value: Any, input_type: InputType, 
                constraints: Optional[InputConstraints] = None) -> Any:
        """Sanitize input value based on type and constraints"""
        if value is None:
            return value
        
        constraints = constraints or InputConstraints()
        
        # Convert to string for processing
        str_value = str(value)
        
        # Apply sanitization based on mode
        if constraints.sanitization_mode == SanitizationMode.NONE:
            return value
        elif constraints.sanitization_mode == SanitizationMode.BASIC:
            return self._basic_sanitize(str_value, input_type)
        elif constraints.sanitization_mode == SanitizationMode.AGGRESSIVE:
            return self._aggressive_sanitize(str_value, input_type)
        else:
            return self._basic_sanitize(str_value, input_type)
    
    def can_sanitize(self, input_type: InputType) -> bool:
        """Check if can sanitize this input type"""
        return True  # Basic sanitizer handles all types
    
    def _basic_sanitize(self, value: str, input_type: InputType) -> str:
        """Basic sanitization to prevent common attacks"""
        sanitized = value
        
        # HTML entity encoding for web-safe content
        if input_type in [InputType.TEXT, InputType.HTML]:
            sanitized = html.escape(sanitized, quote=True)
        
        # Remove dangerous XSS patterns
        for pattern in self.xss_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Remove SQL injection patterns for text input
        if input_type in [InputType.TEXT, InputType.EMAIL, InputType.SQL]:
            for pattern in self.sql_patterns:
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Remove command injection patterns
        if input_type in [InputType.TEXT, InputType.COMMAND, InputType.PATH]:
            for pattern in self.command_patterns:
                sanitized = re.sub(pattern, '', sanitized)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized
    
    def _aggressive_sanitize(self, value: str, input_type: InputType) -> str:
        """Aggressive sanitization with whitelist approach"""
        if input_type == InputType.TEXT:
            # Only allow alphanumeric, basic punctuation, and spaces
            sanitized = re.sub(r'[^a-zA-Z0-9\s\.,!?\-_]', '', value)
        elif input_type == InputType.EMAIL:
            # Only allow valid email characters
            sanitized = re.sub(r'[^a-zA-Z0-9@\.\-_\+]', '', value)
        elif input_type == InputType.URL:
            # Only allow valid URL characters
            sanitized = re.sub(r'[^a-zA-Z0-9:/?#\[\]@!$&\'()*+,;=\.\-_~%]', '', value)
        elif input_type == InputType.FILENAME:
            # Only allow safe filename characters
            sanitized = re.sub(r'[^a-zA-Z0-9\.\-_\s]', '', value)
        elif input_type == InputType.PATH:
            # Only allow safe path characters (no traversal)
            sanitized = re.sub(r'[^a-zA-Z0-9/\\\.\-_\s]', '', value)
            sanitized = re.sub(r'\.\./', '', sanitized)  # Remove path traversal
        else:
            sanitized = self._basic_sanitize(value, input_type)
        
        return sanitized.strip()


class InputValidator(IValidationMiddleware):
    """Input validation middleware"""
    
    def __init__(self, sanitizer: Optional[IInputSanitizer] = None):
        self.sanitizer = sanitizer or BasicInputSanitizer()
        self.logger = logging.getLogger(__name__)
        
        # Validation patterns
        self.patterns = {
            InputType.EMAIL: r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            InputType.URL: r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.]*))?(?:#(?:[\w.]*))?)?$',
            InputType.PHONE: r'^\+?[\d\s\-\(\)]{10,}$',
            InputType.UUID: r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$',
            InputType.HEX: r'^[0-9a-fA-F]+$',
            InputType.BASE64: r'^[A-Za-z0-9+/]*={0,2}$',
            InputType.DATE: r'^\d{4}-\d{2}-\d{2}$',
            InputType.DATETIME: r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?(?:Z|[+-]\d{2}:\d{2})$',
        }
    
    async def validate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate input data"""
        errors = []
        warnings = []
        sanitized_data = data
        
        try:
            if isinstance(data, dict):
                sanitized_data = await self._validate_dict(data, context, errors, warnings)
            elif isinstance(data, list):
                sanitized_data = await self._validate_list(data, context, errors, warnings)
            else:
                sanitized_data = await self._validate_value(data, context, errors, warnings)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                sanitized_data=sanitized_data,
                metadata={"validator": "InputValidator"}
            )
            
        except Exception as e:
            self.logger.error(f"Input validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Input validation failed: {str(e)}"],
                warnings=warnings,
                sanitized_data=data
            )
    
    async def can_validate(self, data_type: str) -> bool:
        """Check if can validate this data type"""
        return data_type in ["request", "input", "form", "json", "text"]
    
    def get_supported_types(self) -> List[str]:
        """Get supported data types"""
        return ["request", "input", "form", "json", "text"]
    
    async def _validate_dict(self, data: Dict[str, Any], context: Optional[Dict[str, Any]], 
                           errors: List[str], warnings: List[str]) -> Dict[str, Any]:
        """Validate dictionary data"""
        sanitized = {}
        field_constraints = self._get_field_constraints(context)
        
        for key, value in data.items():
            # Validate field name
            if not self._is_valid_field_name(key):
                errors.append(f"Invalid field name: {key}")
                continue
            
            # Get constraints for this field
            constraints = field_constraints.get(key, InputConstraints())
            
            # Validate and sanitize value
            try:
                sanitized_value = await self._validate_field_value(
                    key, value, constraints, errors, warnings
                )
                sanitized[key] = sanitized_value
            except Exception as e:
                errors.append(f"Field '{key}' validation failed: {str(e)}")
        
        return sanitized
    
    async def _validate_list(self, data: List[Any], context: Optional[Dict[str, Any]], 
                           errors: List[str], warnings: List[str]) -> List[Any]:
        """Validate list data"""
        sanitized = []
        max_items = context.get('max_items', 1000) if context else 1000
        
        if len(data) > max_items:
            errors.append(f"Too many items in list: {len(data)} > {max_items}")
            return data
        
        for i, item in enumerate(data):
            try:
                if isinstance(item, (dict, list)):
                    sanitized_item = await self._validate_dict(item, context, errors, warnings) if isinstance(item, dict) else await self._validate_list(item, context, errors, warnings)
                else:
                    sanitized_item = await self._validate_value(item, context, errors, warnings)
                sanitized.append(sanitized_item)
            except Exception as e:
                errors.append(f"List item {i} validation failed: {str(e)}")
                sanitized.append(item)
        
        return sanitized
    
    async def _validate_value(self, data: Any, context: Optional[Dict[str, Any]], 
                            errors: List[str], warnings: List[str]) -> Any:
        """Validate single value"""
        if data is None:
            return data
        
        # Basic type validation
        if isinstance(data, str):
            return self._validate_string(data, context, errors, warnings)
        elif isinstance(data, (int, float)):
            return self._validate_number(data, context, errors, warnings)
        elif isinstance(data, bool):
            return data
        else:
            # Try to sanitize as string
            return self._validate_string(str(data), context, errors, warnings)
    
    async def _validate_field_value(self, field_name: str, value: Any, 
                                   constraints: InputConstraints,
                                   errors: List[str], warnings: List[str]) -> Any:
        """Validate individual field value"""
        # Check if required
        if constraints.required and (value is None or value == ""):
            errors.append(f"Required field '{field_name}' is missing or empty")
            return value
        
        # Check if empty is allowed
        if not constraints.allow_empty and value == "":
            errors.append(f"Field '{field_name}' cannot be empty")
            return value
        
        if value is None or value == "":
            return value
        
        # Determine input type based on field name
        input_type = self._determine_input_type(field_name, value)
        
        # Apply constraints
        sanitized_value = self._apply_constraints(value, constraints, input_type, field_name, errors, warnings)
        
        # Sanitize the value
        if self.sanitizer.can_sanitize(input_type):
            sanitized_value = self.sanitizer.sanitize(sanitized_value, input_type, constraints)
        
        return sanitized_value
    
    def _is_valid_field_name(self, field_name: str) -> bool:
        """Check if field name is valid"""
        # Basic field name validation
        if not isinstance(field_name, str):
            return False
        
        # Should not contain dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '$', '`', '|', ';']
        if any(char in field_name for char in dangerous_chars):
            return False
        
        # Should not be too long
        if len(field_name) > 100:
            return False
        
        return True
    
    def _determine_input_type(self, field_name: str, value: Any) -> InputType:
        """Determine input type based on field name and value"""
        field_lower = field_name.lower()
        
        if 'email' in field_lower:
            return InputType.EMAIL
        elif 'url' in field_lower or 'link' in field_lower:
            return InputType.URL
        elif 'phone' in field_lower or 'tel' in field_lower:
            return InputType.PHONE
        elif 'path' in field_lower or 'file' in field_lower:
            return InputType.PATH
        elif 'date' in field_lower and 'time' in field_lower:
            return InputType.DATETIME
        elif 'date' in field_lower:
            return InputType.DATE
        elif isinstance(value, int):
            return InputType.INTEGER
        elif isinstance(value, float):
            return InputType.FLOAT
        elif isinstance(value, bool):
            return InputType.BOOLEAN
        else:
            return InputType.TEXT
    
    def _apply_constraints(self, value: Any, constraints: InputConstraints, 
                          input_type: InputType, field_name: str,
                          errors: List[str], warnings: List[str]) -> Any:
        """Apply validation constraints"""
        # Length constraints
        if isinstance(value, str):
            if constraints.min_length and len(value) < constraints.min_length:
                errors.append(f"Field '{field_name}' too short: {len(value)} < {constraints.min_length}")
            if constraints.max_length and len(value) > constraints.max_length:
                errors.append(f"Field '{field_name}' too long: {len(value)} > {constraints.max_length}")
                value = value[:constraints.max_length]  # Truncate
        
        # Value constraints
        if isinstance(value, (int, float)):
            if constraints.min_value and value < constraints.min_value:
                errors.append(f"Field '{field_name}' too small: {value} < {constraints.min_value}")
            if constraints.max_value and value > constraints.max_value:
                errors.append(f"Field '{field_name}' too large: {value} > {constraints.max_value}")
        
        # Pattern validation
        if constraints.pattern and isinstance(value, str):
            if not re.match(constraints.pattern, value):
                errors.append(f"Field '{field_name}' doesn't match required pattern")
        
        # Type-specific pattern validation
        if input_type in self.patterns and isinstance(value, str):
            if not re.match(self.patterns[input_type], value):
                errors.append(f"Field '{field_name}' has invalid {input_type.value} format")
        
        # Allowed/forbidden values
        if constraints.allowed_values and value not in constraints.allowed_values:
            errors.append(f"Field '{field_name}' has invalid value: {value}")
        
        if constraints.forbidden_values and value in constraints.forbidden_values:
            errors.append(f"Field '{field_name}' has forbidden value: {value}")
        
        return value
    
    def _validate_string(self, value: str, context: Optional[Dict[str, Any]], 
                        errors: List[str], warnings: List[str]) -> str:
        """Validate string value"""
        # Basic string length check
        max_length = context.get('max_string_length', 10000) if context else 10000
        if len(value) > max_length:
            errors.append(f"String too long: {len(value)} > {max_length}")
            value = value[:max_length]
        
        # Check for suspicious patterns
        suspicious_patterns = [
            (r'<script', 'Potential XSS script tag'),
            (r'javascript:', 'JavaScript protocol'),
            (r'data:.*base64', 'Base64 data URL'),
            (r'\\x[0-9a-fA-F]{2}', 'Hex encoded characters'),
        ]
        
        for pattern, description in suspicious_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                warnings.append(f"Suspicious pattern detected: {description}")
        
        return value
    
    def _validate_number(self, value: Union[int, float], context: Optional[Dict[str, Any]], 
                        errors: List[str], warnings: List[str]) -> Union[int, float]:
        """Validate numeric value"""
        # Basic range checks
        if isinstance(value, int):
            if value < -2**31 or value > 2**31 - 1:
                errors.append(f"Integer out of safe range: {value}")
        elif isinstance(value, float):
            if not (-1e308 < value < 1e308):
                errors.append(f"Float out of safe range: {value}")
        
        return value
    
    def _get_field_constraints(self, context: Optional[Dict[str, Any]]) -> Dict[str, InputConstraints]:
        """Get field constraints from context"""
        if not context or 'field_constraints' not in context:
            return {}
        
        constraints = {}
        for field, config in context['field_constraints'].items():
            constraints[field] = InputConstraints(**config)
        
        return constraints


class ValidationPipeline:
    """Pipeline for complex input validation workflows"""
    
    def __init__(self):
        self.validators: List[IValidationMiddleware] = []
        self.logger = logging.getLogger(__name__)
    
    def add_validator(self, validator: IValidationMiddleware) -> 'ValidationPipeline':
        """Add validator to pipeline"""
        self.validators.append(validator)
        return self
    
    async def validate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Run data through validation pipeline"""
        all_errors = []
        all_warnings = []
        sanitized_data = data
        metadata = {}
        
        for validator in self.validators:
            try:
                result = await validator.validate(sanitized_data, context)
                
                all_errors.extend(result.errors)
                all_warnings.extend(result.warnings)
                
                if result.sanitized_data is not None:
                    sanitized_data = result.sanitized_data
                
                if result.metadata:
                    metadata.update(result.metadata)
                
                # Stop on first failure if strict mode
                if not result.is_valid and context and context.get('strict_mode', True):
                    break
                    
            except Exception as e:
                self.logger.error(f"Validator {type(validator).__name__} failed: {e}")
                all_errors.append(f"Validator {type(validator).__name__} failed: {str(e)}")
        
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            sanitized_data=sanitized_data,
            metadata=metadata
        )