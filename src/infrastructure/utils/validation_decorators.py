"""
Validation Decorators and Middleware
Provides decorators and middleware for consistent input validation
"""

import functools
import inspect
from typing import Any, Dict, List, Callable

from .validation_errors import ValidationError, InputValidationError, MultipleValidationError
from .validation_utils import (
    validate_email, validate_url, validate_path
)


def validate_input(**validators: Callable[[Any], bool]) -> Callable:
    """
    Decorator to validate function inputs using custom validators
    
    Usage:
        @validate_input(
            email=validate_email,
            age=lambda x: validate_range(x, 0, 120)
        )
        def create_user(email: str, age: int):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Validate each parameter
            errors = []
            for param_name, validator in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    try:
                        if not validator(value):
                            errors.append(
                                InputValidationError(
                                    f"Invalid value for {param_name}",
                                    field=param_name,
                                    value=value
                                )
                            )
                    except Exception as e:
                        errors.append(
                            InputValidationError(
                                f"Validation failed for {param_name}: {str(e)}",
                                field=param_name,
                                value=value
                            )
                        )
            
            if errors:
                if len(errors) == 1:
                    raise errors[0]
                else:
                    raise MultipleValidationError(errors)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_json(schema: Dict[str, Any]) -> Callable:
    """
    Decorator to validate JSON input against schema
    
    Usage:
        @validate_json({
            'name': {'type': 'string', 'required': True},
            'age': {'type': 'integer', 'min': 0}
        })
        def process_data(data: dict):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Find the data argument (usually first dict argument)
            data = None
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            for param_name, value in bound.arguments.items():
                if isinstance(value, dict):
                    data = value
                    break
            
            if data is None:
                raise InputValidationError("No dictionary data found to validate")
            
            # Validate against schema
            errors = []
            for field, rules in schema.items():
                if rules.get('required', False) and field not in data:
                    errors.append(
                        InputValidationError(
                            f"Required field '{field}' is missing",
                            field=field
                        )
                    )
                    continue
                
                if field in data:
                    value = data[field]
                    
                    # Type validation
                    if 'type' in rules:
                        expected_type = rules['type']
                        type_map = {
                            'string': str,
                            'integer': int,
                            'number': (int, float),
                            'boolean': bool,
                            'array': list,
                            'object': dict
                        }
                        
                        if expected_type in type_map:
                            if not isinstance(value, type_map[expected_type]):
                                errors.append(
                                    InputValidationError(
                                        f"Field '{field}' expected {expected_type}, got {type(value).__name__}",
                                        field=field,
                                        value=value
                                    )
                                )
                                continue
                    
                    # Range validation for numbers
                    if isinstance(value, (int, float)):
                        if 'min' in rules and value < rules['min']:
                            errors.append(
                                InputValidationError(
                                    f"Field '{field}' value {value} is below minimum {rules['min']}",
                                    field=field,
                                    value=value
                                )
                            )
                        if 'max' in rules and value > rules['max']:
                            errors.append(
                                InputValidationError(
                                    f"Field '{field}' value {value} is above maximum {rules['max']}",
                                    field=field,
                                    value=value
                                )
                            )
                    
                    # Length validation for strings/arrays
                    if isinstance(value, (str, list)):
                        if 'min_length' in rules and len(value) < rules['min_length']:
                            errors.append(
                                InputValidationError(
                                    f"Field '{field}' length {len(value)} is below minimum {rules['min_length']}",
                                    field=field,
                                    value=value
                                )
                            )
                        if 'max_length' in rules and len(value) > rules['max_length']:
                            errors.append(
                                InputValidationError(
                                    f"Field '{field}' length {len(value)} is above maximum {rules['max_length']}",
                                    field=field,
                                    value=value
                                )
                            )
            
            if errors:
                if len(errors) == 1:
                    raise errors[0]
                else:
                    raise MultipleValidationError(errors)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_args(*arg_validators: Callable[[Any], bool]) -> Callable:
    """
    Decorator to validate positional arguments
    
    Usage:
        @validate_args(
            lambda x: isinstance(x, str),
            lambda x: isinstance(x, int) and x > 0
        )
        def process(name: str, count: int):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            errors = []
            
            for i, (arg, validator) in enumerate(zip(args, arg_validators)):
                try:
                    if not validator(arg):
                        errors.append(
                            InputValidationError(
                                f"Invalid argument at position {i}",
                                field=f"arg_{i}",
                                value=arg
                            )
                        )
                except Exception as e:
                    errors.append(
                        InputValidationError(
                            f"Validation failed for argument at position {i}: {str(e)}",
                            field=f"arg_{i}",
                            value=arg
                        )
                    )
            
            if errors:
                if len(errors) == 1:
                    raise errors[0]
                else:
                    raise MultipleValidationError(errors)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_fields(*required_fields: str) -> Callable:
    """
    Decorator to ensure required fields are present in kwargs
    
    Usage:
        @require_fields('name', 'email')
        def create_user(**kwargs):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            errors = []
            
            for field in required_fields:
                if field not in kwargs:
                    errors.append(
                        InputValidationError(
                            f"Required field '{field}' is missing",
                            field=field
                        )
                    )
            
            if errors:
                if len(errors) == 1:
                    raise errors[0]
                else:
                    raise MultipleValidationError(errors)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class ValidationMiddleware:
    """Base class for validation middleware"""
    
    def __init__(self):
        self.validators: List[Callable] = []
    
    def add_validator(self, validator: Callable) -> None:
        """Add a validator function"""
        self.validators.append(validator)
    
    def validate(self, data: Any) -> None:
        """Run all validators on data"""
        errors = []
        
        for validator in self.validators:
            try:
                result = validator(data)
                if result is False:
                    errors.append(
                        ValidationError(f"Validator {validator.__name__} failed")
                    )
                elif isinstance(result, ValidationError):
                    errors.append(result)
                elif isinstance(result, list) and result:
                    errors.extend(result)
            except ValidationError as e:
                errors.append(e)
            except Exception as e:
                errors.append(
                    ValidationError(f"Validator {validator.__name__} threw exception: {str(e)}")
                )
        
        if errors:
            if len(errors) == 1:
                raise errors[0]
            else:
                raise MultipleValidationError(errors)


def create_validator(validation_rules: Dict[str, Any]) -> Callable:
    """
    Factory function to create validators from rules
    
    Usage:
        validator = create_validator({
            'email': validate_email,
            'age': lambda x: validate_range(x, 0, 120)
        })
    """
    def validator(data: Dict[str, Any]) -> List[ValidationError]:
        errors = []
        
        for field, rule in validation_rules.items():
            if field in data:
                value = data[field]
                try:
                    if callable(rule):
                        if not rule(value):
                            errors.append(
                                InputValidationError(
                                    f"Validation failed for field '{field}'",
                                    field=field,
                                    value=value
                                )
                            )
                    elif isinstance(rule, dict):
                        # Handle complex validation rules
                        if 'validator' in rule:
                            if not rule['validator'](value):
                                message = rule.get('message', f"Validation failed for field '{field}'")
                                errors.append(
                                    InputValidationError(message, field=field, value=value)
                                )
                except Exception as e:
                    errors.append(
                        InputValidationError(
                            f"Validation error for field '{field}': {str(e)}",
                            field=field,
                            value=value
                        )
                    )
        
        return errors
    
    return validator


# Common validation patterns as decorators
def validate_email_field(field_name: str = 'email') -> Callable:
    """Decorator to validate email field"""
    return validate_input(**{field_name: validate_email})


def validate_url_field(field_name: str = 'url') -> Callable:
    """Decorator to validate URL field"""
    return validate_input(**{field_name: validate_url})


def validate_path_field(field_name: str = 'path') -> Callable:
    """Decorator to validate path field"""
    return validate_input(**{field_name: validate_path})
