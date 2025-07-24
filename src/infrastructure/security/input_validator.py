#!/usr/bin/env python3
"""
Input Validation Security Module
"""

import re
import uuid
from typing import Any, Dict, List, Union

from flask import jsonify, request


class ValidationError(Exception):
    """Input validation errors."""

    pass


class InputValidator:
    """Comprehensive input validation for API endpoints."""

    # Security patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bupdate\b.*\bset\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(--|#|/\*|\*/)",
        r"(\bor\b.*=.*)",
        r"(\band\b.*=.*)",
        r"(xp_|sp_)",
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"on\w+\s*=",
        r"expression\s*\(",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]

    def __init__(self):
        """Initialize input validator."""
        self.compiled_sql_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.SQL_INJECTION_PATTERNS
        ]
        self.compiled_xss_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.XSS_PATTERNS
        ]

    def sanitize_string(self, value: str, max_length: int = 1000) -> str:
        """Sanitize string input for security."""
        if not isinstance(value, str):
            raise ValidationError(f"Expected string, got {type(value)}")

        # Length check
        if len(value) > max_length:
            raise ValidationError(f"String too long: {len(value)} > {max_length}")

        # Check for SQL injection patterns
        for pattern in self.compiled_sql_patterns:
            if pattern.search(value):
                raise ValidationError("Potential SQL injection detected")

        # Check for XSS patterns
        for pattern in self.compiled_xss_patterns:
            if pattern.search(value):
                raise ValidationError("Potential XSS detected")

        # Basic sanitization
        sanitized = value.strip()

        # Remove null bytes and control characters
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized)

        return sanitized

    def validate_uuid(self, value: str) -> str:
        """Validate UUID format."""
        try:
            uuid_obj = uuid.UUID(value)
            return str(uuid_obj)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid UUID format: {value}")

    def validate_integer(
        self, value: Union[str, int], min_val: int = None, max_val: int = None
    ) -> int:
        """Validate integer input."""
        try:
            int_val = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid integer: {value}")

        if min_val is not None and int_val < min_val:
            raise ValidationError(f"Integer too small: {int_val} < {min_val}")

        if max_val is not None and int_val > max_val:
            raise ValidationError(f"Integer too large: {int_val} > {max_val}")

        return int_val

    def validate_enum(self, value: str, allowed_values: List[str]) -> str:
        """Validate enum/choice input."""
        if value not in allowed_values:
            raise ValidationError(f"Invalid value '{value}'. Allowed: {allowed_values}")
        return value

    def validate_json_schema(
        self, data: Dict[str, Any], schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Basic JSON schema validation."""
        if not isinstance(data, dict):
            raise ValidationError("Expected JSON object")

        validated = {}

        for field, field_schema in schema.items():
            field_type = field_schema.get("type")
            required = field_schema.get("required", False)
            max_length = field_schema.get("max_length", 1000)

            if field not in data:
                if required:
                    raise ValidationError(f"Required field missing: {field}")
                continue

            value = data[field]

            if field_type == "string":
                validated[field] = self.sanitize_string(value, max_length)
            elif field_type == "integer":
                validated[field] = self.validate_integer(
                    value, field_schema.get("min"), field_schema.get("max")
                )
            elif field_type == "uuid":
                validated[field] = self.validate_uuid(value)
            elif field_type == "enum":
                validated[field] = self.validate_enum(value, field_schema["values"])
            else:
                # Basic sanitization for unknown types
                if isinstance(value, str):
                    validated[field] = self.sanitize_string(value, max_length)
                else:
                    validated[field] = value

        return validated

    def validate_request_args(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Flask request arguments."""
        try:
            args_data = {}
            for key, value in request.args.items():
                args_data[key] = value

            return self.validate_json_schema(args_data, schema)
        except ValidationError as e:
            raise ValidationError(f"Request argument validation failed: {str(e)}")

    def validate_request_json(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Flask request JSON body."""
        try:
            json_data = request.get_json() or {}
            return self.validate_json_schema(json_data, schema)
        except ValidationError as e:
            raise ValidationError(f"Request JSON validation failed: {str(e)}")


def validate_input(schema: Dict[str, Any], json_schema: Dict[str, Any] = None):
    """Decorator for automatic input validation."""

    def decorator(f):
        def wrapper(*args, **kwargs):
            validator = InputValidator()

            try:
                # Validate query parameters
                if schema:
                    validated_args = validator.validate_request_args(schema)
                    request.validated_args = validated_args

                # Validate JSON body
                if json_schema:
                    validated_json = validator.validate_request_json(json_schema)
                    request.validated_json = validated_json

            except ValidationError as e:
                return (
                    jsonify(
                        {
                            "error": "Input validation failed",
                            "details": str(e),
                            "code": "VALIDATION_ERROR",
                        }
                    ),
                    400,
                )

            return f(*args, **kwargs)

        wrapper.__name__ = f.__name__
        wrapper.__doc__ = f.__doc__
        return wrapper

    return decorator


# Global validator instance
validator = InputValidator()
