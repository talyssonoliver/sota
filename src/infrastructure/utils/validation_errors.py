"""
Standardized Validation Error Hierarchy
Provides consistent error types for all validation scenarios
"""

from typing import Any, Dict, List, Optional, Union


class ValidationError(Exception):
    """Base class for all validation errors"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.field = field
        self.value = value
        self.code = code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses"""
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'field': self.field,
            'code': self.code,
            'details': self.details
        }
    
    def __str__(self) -> str:
        if self.field:
            return f"{self.field}: {self.message}"
        return self.message


class InputValidationError(ValidationError):
    """Raised when input data fails validation"""
    pass


class SchemaValidationError(ValidationError):
    """Raised when data doesn't match expected schema"""
    
    def __init__(
        self,
        message: str,
        schema_path: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.schema_path = schema_path


class APIValidationError(ValidationError):
    """Raised when API request/response validation fails"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code


class SecurityValidationError(ValidationError):
    """Raised when security validation fails"""
    
    def __init__(
        self,
        message: str,
        severity: str = "medium",
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.severity = severity


class BusinessValidationError(ValidationError):
    """Raised when business rule validation fails"""
    
    def __init__(
        self,
        message: str,
        rule: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.rule = rule


class TypeValidationError(ValidationError):
    """Raised when type validation fails"""
    
    def __init__(
        self,
        message: str,
        expected_type: Optional[type] = None,
        actual_type: Optional[type] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.expected_type = expected_type
        self.actual_type = actual_type


class MultipleValidationError(ValidationError):
    """Container for multiple validation errors"""
    
    def __init__(
        self,
        errors: List[ValidationError],
        message: Optional[str] = None
    ):
        if not message:
            message = f"Multiple validation errors ({len(errors)} errors)"
        super().__init__(message)
        self.errors = errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all errors to dictionary"""
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'errors': [error.to_dict() for error in self.errors]
        }
    
    def add_error(self, error: ValidationError) -> None:
        """Add another validation error"""
        self.errors.append(error)
    
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0


# Convenience functions for common error scenarios
def input_error(message: str, field: Optional[str] = None, **kwargs) -> InputValidationError:
    """Create input validation error"""
    return InputValidationError(message, field=field, **kwargs)


def schema_error(message: str, schema_path: Optional[str] = None, **kwargs) -> SchemaValidationError:
    """Create schema validation error"""
    return SchemaValidationError(message, schema_path=schema_path, **kwargs)


def api_error(message: str, status_code: int = 400, **kwargs) -> APIValidationError:
    """Create API validation error"""
    return APIValidationError(message, status_code=status_code, **kwargs)


def security_error(message: str, severity: str = "medium", **kwargs) -> SecurityValidationError:
    """Create security validation error"""
    return SecurityValidationError(message, severity=severity, **kwargs)


def business_error(message: str, rule: Optional[str] = None, **kwargs) -> BusinessValidationError:
    """Create business validation error"""
    return BusinessValidationError(message, rule=rule, **kwargs)


def type_error(message: str, expected: Optional[type] = None, actual: Optional[type] = None, **kwargs) -> TypeValidationError:
    """Create type validation error"""
    return TypeValidationError(message, expected_type=expected, actual_type=actual, **kwargs)


# Error collection context manager
class ErrorCollector:
    """Context manager for collecting multiple validation errors"""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.errors:
            raise MultipleValidationError(self.errors)
        return False
    
    def add(self, error: ValidationError) -> None:
        """Add an error to the collection"""
        self.errors.append(error)
    
    def add_if(self, condition: bool, error: ValidationError) -> None:
        """Add error only if condition is true"""
        if condition:
            self.errors.append(error)
    
    def validate(self, condition: bool, error: ValidationError) -> None:
        """Add error if condition is false"""
        if not condition:
            self.errors.append(error)
    
    def has_errors(self) -> bool:
        """Check if any errors were collected"""
        return len(self.errors) > 0
