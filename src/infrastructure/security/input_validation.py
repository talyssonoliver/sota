#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import (
    datetime,
    json,
    logging,
    re
)
"""
Comprehensive Input Validation Framework

Provides secure input validation for all API endpoints and data processing.
Addresses the 9.55% input validation coverage gap, targeting 95% coverage.
"""

# import re  # Consolidated to common_imports
import html
# import logging  # Consolidated to common_imports
from typing import Any, Dict, List, Optional, Union, Callable
# from datetime import datetime  # Consolidated to common_imports
from urllib.parse import urlparse
# import json  # Consolidated to common_imports
from functools import wraps

# Week 2 Day 3 Integration: Enhanced validation decorators
from src.infrastructure.utils.validation_decorators import (
    validate_input as week2_validate_input,
    validate_json,
    validate_args,
    require_fields
)
from src.infrastructure.utils.validation_utils import validate_schema



logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(message)


class ValidationRule:
    """Base class for validation rules."""
    
    def __init__(self, error_message: str = "Validation failed"):
        self.error_message = error_message
    
    def validate(self, value: Any, field_name: str = None) -> bool:
        """Validate the value. Return True if valid."""
        raise NotImplementedError
    
    def sanitize(self, value: Any) -> Any:
        """Sanitize the value. Default implementation returns unchanged."""
        return value


class StringLengthRule(ValidationRule):
    """Validates string length constraints."""
    
    def __init__(self, min_length: int = 0, max_length: int = None, 
                 error_message: str = None):
        self.min_length = min_length
        self.max_length = max_length
        
        if error_message is None:
            if max_length:
                error_message = f"String must be between {min_length} and {max_length} characters"
            else:
                error_message = f"String must be at least {min_length} characters"
        
        super().__init__(error_message)
    
    def validate(self, value: Any, field_name: str = None) -> bool:
        if not isinstance(value, str):
            return False
        
        length = len(value)
        
        if length < self.min_length:
            return False
        
        if self.max_length and length > self.max_length:
            return False
        
        return True


class RegexRule(ValidationRule):
    """Validates string against regex pattern."""
    
    def __init__(self, pattern: str, error_message: str = "Invalid format"):
        self.pattern = re.compile(pattern)
        super().__init__(error_message)
    
    def validate(self, value: Any, field_name: str = None) -> bool:
        if not isinstance(value, str):
            return False
        
        return bool(self.pattern.match(value))


class EmailRule(ValidationRule):
    """Validates email addresses."""
    
    def __init__(self):
        super().__init__("Invalid email address format")
    
    def validate(self, value: Any, field_name: str = None) -> bool:
        if not isinstance(value, str):
            return False
        
        if not value or '@' not in value:
            return False
        
        # Basic structure check
        if value.count('@') != 1:
            return False
        
        local, domain = value.split('@', 1)
        
        # Check local part
        if not local or local.startswith('.') or local.endswith('.') or '..' in local:
            return False
        
        # Check domain part
        if not domain or '.' not in domain or domain.startswith('.') or domain.endswith('.'):
            return False
        
        # Basic character validation
        import re
        local_pattern = r'^[a-zA-Z0-9._%+-]+$'
        domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        return bool(re.match(local_pattern, local)) and bool(re.match(domain_pattern, domain))


class URLRule(ValidationRule):
    """Validates URLs."""
    
    def __init__(self, allowed_schemes: List[str] = None):
        self.allowed_schemes = allowed_schemes or ['http', 'https']
        super().__init__("Invalid URL format")
    
    def validate(self, value: Any, field_name: str = None) -> bool:
        if not isinstance(value, str):
            return False
        
        try:
            parsed = urlparse(value)
            return (parsed.scheme in self.allowed_schemes and 
                   bool(parsed.netloc))
        except Exception:
            return False


class NumericRangeRule(ValidationRule):
    """Validates numeric values within range."""
    
    def __init__(self, min_value: Union[int, float] = None, 
                 max_value: Union[int, float] = None):
        self.min_value = min_value
        self.max_value = max_value
        
        msg_parts = []
        if min_value is not None:
            msg_parts.append(f"minimum {min_value}")
        if max_value is not None:
            msg_parts.append(f"maximum {max_value}")
        
        error_message = f"Value must be within range: {', '.join(msg_parts)}"
        super().__init__(error_message)
    
    def validate(self, value: Any, field_name: str = None) -> bool:
        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (ValueError, TypeError):
                return False
        
        if self.min_value is not None and value < self.min_value:
            return False
        
        if self.max_value is not None and value > self.max_value:
            return False
        
        return True


class SQLInjectionRule(ValidationRule):
    """Detects potential SQL injection attempts."""
    
    def __init__(self):
        # Common SQL injection patterns
        self.dangerous_patterns = [
            r"('|(\\')|(;|(%3B))|((\*|(%2A))\s*(.|\n)*(\*|(%2A))))",
            r"(union\s+select|union\s+all\s+select)",
            r"(insert\s+into|delete\s+from|update\s+.+\s+set)",
            r"(drop\s+table|alter\s+table|create\s+table)",
            r"(exec\s*\(|exec\s+[a-z])",
            r"(script\s*>|<\s*script)",
            r"(javascript\s*:|vbscript\s*:)",
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) 
                                for pattern in self.dangerous_patterns]
        
        super().__init__("Potentially dangerous input detected")
    
    def validate(self, value: Any, field_name: str = None) -> bool:
        if not isinstance(value, str):
            return True  # Non-strings are safe from SQL injection
        
        # Check against known dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                logger.warning(f"Potential SQL injection attempt detected in field {field_name}: {value[:50]}...")
                return False
        
        return True


class XSSRule(ValidationRule):
    """Detects potential XSS attempts."""
    
    def __init__(self):
        # XSS patterns to detect
        self.xss_patterns = [
            r"<\s*script[^>]*>.*?<\s*/\s*script\s*>",
            r"javascript\s*:",
            r"vbscript\s*:",
            r"on\w+\s*=",
            r"<\s*iframe[^>]*>",
            r"<\s*object[^>]*>",
            r"<\s*embed[^>]*>",
            r"<\s*link[^>]*>",
            r"<\s*meta[^>]*>",
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) 
                                for pattern in self.xss_patterns]
        
        super().__init__("Potentially dangerous HTML/JavaScript detected")
    
    def validate(self, value: Any, field_name: str = None) -> bool:
        if not isinstance(value, str):
            return True
        
        # Check for XSS patterns
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                logger.warning(f"Potential XSS attempt detected in field {field_name}: {value[:50]}...")
                return False
        
        return True
    
    def sanitize(self, value: Any) -> Any:
        """Sanitize HTML content."""
        if isinstance(value, str):
            return html.escape(value)
        return value


class FilePathRule(ValidationRule):
    """Validates file paths to prevent directory traversal."""
    
    def __init__(self, allowed_extensions: List[str] = None):
        self.allowed_extensions = allowed_extensions or []
        super().__init__("Invalid or dangerous file path")
    
    def validate(self, value: Any, field_name: str = None) -> bool:
        if not isinstance(value, str):
            return False
        
        # Check for directory traversal attempts
        if '..' in value or value.startswith('/') or ':' in value:
            logger.warning(f"Directory traversal attempt detected: {value}")
            return False
        
        # Check file extension if restrictions apply
        if self.allowed_extensions:
            extension = value.split('.')[-1].lower()
            if extension not in self.allowed_extensions:
                return False
        
        return True


class JSONRule(ValidationRule):
    """Validates JSON format."""
    
    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
        super().__init__("Invalid JSON format")
    
    def validate(self, value: Any, field_name: str = None) -> bool:
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return self._check_depth(parsed, 0)
            except (json.JSONDecodeError, ValueError):
                return False
        return True
    
    def _check_depth(self, obj: Any, current_depth: int) -> bool:
        """Check JSON nesting depth to prevent DoS attacks."""
        if current_depth > self.max_depth:
            return False
        
        if isinstance(obj, dict):
            for value in obj.values():
                if not self._check_depth(value, current_depth + 1):
                    return False
        elif isinstance(obj, list):
            for item in obj:
                if not self._check_depth(item, current_depth + 1):
                    return False
        
        return True


class InputValidator:
    """Main input validation class."""
    
    def __init__(self):
        self.rules: Dict[str, List[ValidationRule]] = {}
        self.global_rules: List[ValidationRule] = [
            SQLInjectionRule(),
            XSSRule()
        ]
    
    def add_rule(self, field_name: str, rule: ValidationRule):
        """Add a validation rule for a specific field."""
        if field_name not in self.rules:
            self.rules[field_name] = []
        self.rules[field_name].append(rule)
    
    def add_global_rule(self, rule: ValidationRule):
        """Add a global validation rule applied to all fields."""
        self.global_rules.append(rule)
    
    def validate_field(self, field_name: str, value: Any, 
                      sanitize: bool = True) -> tuple[bool, Any, List[str]]:
        """
        Validate a single field.
        
        Returns:
            tuple: (is_valid, sanitized_value, error_messages)
        """
        errors = []
        sanitized_value = value
        
        # Apply global rules first
        for rule in self.global_rules:
            if not rule.validate(value, field_name):
                errors.append(f"{field_name}: {rule.error_message}")
            if sanitize:
                sanitized_value = rule.sanitize(sanitized_value)
        
        # Apply field-specific rules
        field_rules = self.rules.get(field_name, [])
        for rule in field_rules:
            if not rule.validate(value, field_name):
                errors.append(f"{field_name}: {rule.error_message}")
            if sanitize:
                sanitized_value = rule.sanitize(sanitized_value)
        
        return len(errors) == 0, sanitized_value, errors
    
    def validate_dict(self, data: Dict[str, Any], 
                     sanitize: bool = True) -> tuple[bool, Dict[str, Any], List[str]]:
        """
        Validate a dictionary of data.
        
        Returns:
            tuple: (is_valid, sanitized_data, error_messages)
        """
        all_errors = []
        sanitized_data = {}
        
        for field_name, value in data.items():
            is_valid, sanitized_value, errors = self.validate_field(
                field_name, value, sanitize
            )
            
            sanitized_data[field_name] = sanitized_value
            all_errors.extend(errors)
        
        return len(all_errors) == 0, sanitized_data, all_errors


# Pre-configured validators for common use cases

def create_api_validator() -> InputValidator:
    """Create validator for API endpoints."""
    validator = InputValidator()
    
    # Common API field validations
    validator.add_rule('email', EmailRule())
    validator.add_rule('url', URLRule())
    validator.add_rule('name', StringLengthRule(1, 100))
    validator.add_rule('description', StringLengthRule(0, 1000))
    validator.add_rule('id', RegexRule(r'^[a-zA-Z0-9_-]+$', "Invalid ID format"))
    validator.add_rule('task_id', RegexRule(r'^[a-zA-Z0-9_-]+$', "Invalid task ID format"))
    
    return validator


def create_hitl_validator() -> InputValidator:
    """Create validator for HITL endpoints."""
    validator = create_api_validator()
    
    # HITL-specific validations
    validator.add_rule('checkpoint_type', RegexRule(r'^[a-z_]+$', "Invalid checkpoint type"))
    validator.add_rule('risk_score', NumericRangeRule(0.0, 1.0))
    validator.add_rule('action', RegexRule(r'^(approve|reject|escalate)$', "Invalid action"))
    validator.add_rule('reason', StringLengthRule(0, 500))
    validator.add_rule('data', JSONRule(max_depth=5))
    
    return validator


def create_file_upload_validator() -> InputValidator:
    """Create validator for file uploads."""
    validator = InputValidator()
    
    # File-specific validations
    validator.add_rule('filename', FilePathRule(['txt', 'json', 'yaml', 'py']))
    validator.add_rule('path', FilePathRule())
    validator.add_rule('content', StringLengthRule(0, 1000000))  # 1MB limit
    
    return validator


# Decorator for automatic validation
def validate_request(validator: InputValidator = None, 
                    sanitize: bool = True):
    """
    Decorator to automatically validate Flask request data.
    
    Args:
        validator: InputValidator instance to use
        sanitize: Whether to sanitize input data
    """
    if validator is None:
        validator = create_api_validator()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            
            # Get request data
            if request.is_json:
                data = request.get_json() or {}
            else:
                data = request.form.to_dict()
            
            # Validate data
            is_valid, sanitized_data, errors = validator.validate_dict(data, sanitize)
            
            if not is_valid:
                logger.warning(f"Validation failed for {func.__name__}: {errors}")
                return jsonify({
                    'status': 'error',
                    'message': 'Input validation failed',
                    'errors': errors
                }), 400
            
            # Replace request data with sanitized version
            if sanitize and request.is_json:
                request._cached_json = (sanitized_data, True)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Global validator instances
api_validator = create_api_validator()
hitl_validator = create_hitl_validator()
file_validator = create_file_upload_validator()


# Convenience functions
def validate_email(email: str) -> bool:
    """Validate email address."""
    rule = EmailRule()
    return rule.validate(email)


def validate_url(url: str) -> bool:
    """Validate URL."""
    rule = URLRule()
    return rule.validate(url)


def sanitize_html(html_content: str) -> str:
    """Sanitize HTML content."""
    rule = XSSRule()
    return rule.sanitize(html_content)


def is_safe_path(path: str) -> bool:
    """Check if file path is safe."""
    rule = FilePathRule()
    return rule.validate(path)

# Week 2 Day 3 Integration Functions
def integrate_week2_validation(validator_class=None):
    """
    Integrate Week 2 validation patterns with existing validation.
    This bridges the Week 2 standardized patterns with the enterprise framework.
    """
    if validator_class is None:
        validator_class = InputValidator
    
    # Create enhanced validator with Week 2 patterns
    enhanced_validator = validator_class()
    
    # Add Week 2 validation rules
    enhanced_validator.add_global_rule(SQLInjectionRule())
    enhanced_validator.add_global_rule(XSSRule())
    
    return enhanced_validator


def create_enterprise_validator():
    """Create validator that combines enterprise framework with Week 2 improvements"""
    return integrate_week2_validation()


# Enhanced validation functions using Week 2 patterns
def validate_with_week2_decorators(schema_name: str = None):
    """Decorator that combines enterprise validation with Week 2 patterns"""
    def decorator(func):
        # Apply Week 2 validation decorators
        if schema_name:
            func = week2_validate_schema(schema_name)(func)
        func = week2_validate_input()(func)
        
        # Apply existing enterprise validation
        func = validate_request()(func)
        
        return func
    return decorator
