
from src.infrastructure.utils.common_imports import asyncio, logging
"""
Validation Decorators

Provides convenient decorators for applying validation to functions,
methods, and API endpoints automatically.
"""

# import asyncio  # Consolidated to common_imports
import functools
# import logging  # Consolidated to common_imports
from typing import Any, Callable, Dict, Optional, TypeVar, Union, List
from ..error_handling import ValidationError, ErrorSeverity

T = TypeVar('T')


def validate_input(schema: Optional[str] = None, 
                  strict: bool = True,
                  sanitize: bool = True,
                  field_constraints: Optional[Dict[str, Dict[str, Any]]] = None):
    """
    Decorator to validate function input parameters
    
    Args:
        schema: Schema name to validate against
        strict: Whether to raise errors on validation failure
        sanitize: Whether to sanitize input data
        field_constraints: Field-specific validation constraints
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            from .validation_middleware import get_validation_middleware
            
            middleware = get_validation_middleware()
            
            # Build validation context
            context = {
                "schema": schema,
                "strict_mode": strict,
                "sanitization_enabled": sanitize,
                "function_name": func.__name__,
                "field_constraints": field_constraints or {}
            }
            
            # Validate positional arguments (skip 'self' if present)
            start_idx = 1 if args and hasattr(args[0], func.__name__) else 0
            
            for i, arg in enumerate(args[start_idx:], start_idx):
                if arg is not None:
                    try:
                        result = await middleware.validate_data(arg, "input", context)
                        
                        if not result.is_valid and strict:
                            raise ValidationError(
                                f"Input validation failed for argument {i}: {'; '.join(result.errors)}",
                                field=f"arg_{i}",
                                value=arg
                            ).set_component("ValidationDecorator").set_operation(func.__name__)
                        
                        # Use sanitized data if available
                        if result.sanitized_data is not None and sanitize:
                            args = list(args)
                            args[i] = result.sanitized_data
                            args = tuple(args)
                            
                    except ValidationError:
                        raise
                    except Exception as e:
                        logger = logging.getLogger(__name__)
                        logger.error(f"Input validation error in {func.__name__}: {e}")
                        if strict:
                            raise ValidationError(
                                f"Input validation system error: {str(e)}",
                                severity=ErrorSeverity.HIGH
                            ).set_component("ValidationDecorator")
            
            # Validate keyword arguments
            for key, value in kwargs.items():
                if value is not None:
                    try:
                        result = await middleware.validate_data(value, "input", context)
                        
                        if not result.is_valid and strict:
                            raise ValidationError(
                                f"Input validation failed for parameter '{key}': {'; '.join(result.errors)}",
                                field=key,
                                value=value
                            ).set_component("ValidationDecorator").set_operation(func.__name__)
                        
                        # Use sanitized data if available
                        if result.sanitized_data is not None and sanitize:
                            kwargs[key] = result.sanitized_data
                            
                    except ValidationError:
                        raise
                    except Exception as e:
                        logger = logging.getLogger(__name__)
                        logger.error(f"Input validation error for '{key}' in {func.__name__}: {e}")
                        if strict:
                            raise ValidationError(
                                f"Input validation system error: {str(e)}",
                                severity=ErrorSeverity.HIGH
                            ).set_component("ValidationDecorator")
            
            # Call the original function
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_output(schema: Optional[str] = None,
                   strict: bool = False,
                   sanitize: bool = False):
    """
    Decorator to validate function output
    
    Args:
        schema: Schema name to validate against
        strict: Whether to raise errors on validation failure
        sanitize: Whether to sanitize output data
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            from .validation_middleware import get_validation_middleware
            
            # Call the original function
            result = await func(*args, **kwargs)
            
            if result is not None:
                middleware = get_validation_middleware()
                
                # Build validation context
                context = {
                    "schema": schema,
                    "strict_mode": strict,
                    "sanitization_enabled": sanitize,
                    "function_name": func.__name__
                }
                
                try:
                    validation_result = await middleware.validate_data(result, "output", context)
                    
                    if not validation_result.is_valid:
                        logger = logging.getLogger(__name__)
                        logger.warning(
                            f"Output validation failed for {func.__name__}: {'; '.join(validation_result.errors)}"
                        )
                        
                        if strict:
                            raise ValidationError(
                                f"Output validation failed: {'; '.join(validation_result.errors)}",
                                field="return_value",
                                value=result
                            ).set_component("ValidationDecorator").set_operation(func.__name__)
                    
                    # Use sanitized data if available
                    if validation_result.sanitized_data is not None and sanitize:
                        result = validation_result.sanitized_data
                        
                except ValidationError:
                    raise
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.error(f"Output validation error in {func.__name__}: {e}")
                    if strict:
                        raise ValidationError(
                            f"Output validation system error: {str(e)}",
                            severity=ErrorSeverity.HIGH
                        ).set_component("ValidationDecorator")
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_business_rules(entity_type: str,
                           operation: str = "unknown",
                           strict: bool = True):
    """
    Decorator to validate business rules for entity operations
    
    Args:
        entity_type: Type of entity being processed
        operation: Operation being performed (create, update, delete, etc.)
        strict: Whether to raise errors on validation failure
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            from .business_rules import get_business_rule_engine, RuleContext
            
            # Get the data to validate (assume first non-self argument)
            data = None
            start_idx = 1 if args and hasattr(args[0], func.__name__) else 0
            
            if len(args) > start_idx:
                data = args[start_idx]
            elif kwargs:
                # Try common parameter names
                for param_name in ['data', 'entity', 'obj', 'item']:
                    if param_name in kwargs:
                        data = kwargs[param_name]
                        break
            
            if data is not None:
                engine = get_business_rule_engine()
                
                # Build rule context
                context = RuleContext(
                    entity_type=entity_type,
                    operation=operation,
                    metadata={
                        "function_name": func.__name__,
                        "strict_mode": strict
                    }
                )
                
                try:
                    violations = await engine.validate(data, entity_type, context)
                    
                    if violations:
                        logger = logging.getLogger(__name__)
                        
                        # Separate errors and warnings
                        critical_violations = [v for v in violations 
                                             if v.severity.value in ['error', 'critical']]
                        warning_violations = [v for v in violations 
                                            if v.severity.value in ['info', 'warning']]
                        
                        # Log warnings
                        for violation in warning_violations:
                            logger.warning(f"Business rule warning in {func.__name__}: {violation.message}")
                        
                        # Handle critical violations
                        if critical_violations and strict:
                            error_messages = [v.message for v in critical_violations]
                            raise ValidationError(
                                f"Business rule validation failed: {'; '.join(error_messages)}",
                                field="entity_data",
                                value=data
                            ).set_component("BusinessRuleDecorator").set_operation(func.__name__)
                        
                except ValidationError:
                    raise
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.error(f"Business rule validation error in {func.__name__}: {e}")
                    if strict:
                        raise ValidationError(
                            f"Business rule validation system error: {str(e)}",
                            severity=ErrorSeverity.HIGH
                        ).set_component("BusinessRuleDecorator")
            
            # Call the original function
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_api_request(endpoint: str,
                        method: str = "POST",
                        schema: Optional[str] = None,
                        strict: bool = True):
    """
    Decorator to validate API request data
    
    Args:
        endpoint: API endpoint being called
        method: HTTP method
        schema: Schema name to validate against
        strict: Whether to raise errors on validation failure
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            from .validation_middleware import get_validation_middleware
            
            # Extract request data (common parameter names)
            request_data = None
            for param_name in ['request', 'data', 'payload', 'body']:
                if param_name in kwargs:
                    request_data = kwargs[param_name]
                    break
            
            if request_data is not None:
                middleware = get_validation_middleware()
                
                # Build validation context
                context = {
                    "endpoint": endpoint,
                    "method": method,
                    "schema": schema,
                    "data_type": "request",
                    "strict_mode": strict
                }
                
                try:
                    result = await middleware.validate_request(request_data, endpoint, context)
                    
                    if not result.is_valid and strict:
                        raise ValidationError(
                            f"API request validation failed for {endpoint}: {'; '.join(result.errors)}",
                            field="request_data",
                            value=request_data
                        ).set_component("APIValidationDecorator").set_operation(func.__name__)
                    
                    # Use sanitized data if available
                    if result.sanitized_data is not None:
                        # Update the request data parameter
                        for param_name in ['request', 'data', 'payload', 'body']:
                            if param_name in kwargs:
                                kwargs[param_name] = result.sanitized_data
                                break
                        
                except ValidationError:
                    raise
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.error(f"API request validation error in {func.__name__}: {e}")
                    if strict:
                        raise ValidationError(
                            f"API request validation system error: {str(e)}",
                            severity=ErrorSeverity.HIGH
                        ).set_component("APIValidationDecorator")
            
            # Call the original function
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_api_response(endpoint: str,
                         schema: Optional[str] = None,
                         strict: bool = False):
    """
    Decorator to validate API response data
    
    Args:
        endpoint: API endpoint being called
        schema: Schema name to validate against
        strict: Whether to raise errors on validation failure
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            from .validation_middleware import get_validation_middleware
            
            # Call the original function
            response = await func(*args, **kwargs)
            
            if response is not None:
                middleware = get_validation_middleware()
                
                # Build validation context
                context = {
                    "endpoint": endpoint,
                    "schema": schema,
                    "data_type": "response",
                    "strict_mode": strict
                }
                
                try:
                    result = await middleware.validate_response(response, endpoint, context)
                    
                    if not result.is_valid:
                        logger = logging.getLogger(__name__)
                        logger.warning(
                            f"API response validation failed for {endpoint}: {'; '.join(result.errors)}"
                        )
                        
                        if strict:
                            raise ValidationError(
                                f"API response validation failed: {'; '.join(result.errors)}",
                                field="response_data",
                                value=response
                            ).set_component("APIValidationDecorator").set_operation(func.__name__)
                    
                    # Use sanitized data if available
                    if result.sanitized_data is not None:
                        response = result.sanitized_data
                        
                except ValidationError:
                    raise
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.error(f"API response validation error in {func.__name__}: {e}")
                    if strict:
                        raise ValidationError(
                            f"API response validation system error: {str(e)}",
                            severity=ErrorSeverity.HIGH
                        ).set_component("APIValidationDecorator")
            
            return response
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Convenience decorators for common patterns
def validate_task_data(operation: str = "unknown", strict: bool = True):
    """Validate task entity data"""
    return validate_business_rules("task", operation, strict)


def validate_user_data(operation: str = "unknown", strict: bool = True):
    """Validate user entity data"""
    return validate_business_rules("user", operation, strict)


def validate_config_data(operation: str = "unknown", strict: bool = True):
    """Validate configuration data"""
    return validate_business_rules("configuration", operation, strict)


def validate_json_input(max_size: int = 100000, strict: bool = True):
    """Validate JSON input data"""
    constraints = {
        "data": {
            "max_length": max_size,
            "required": True
        }
    }
    return validate_input(schema="json", strict=strict, field_constraints=constraints)


def validate_safe_string(max_length: int = 1000, strict: bool = True):
    """Validate string input for safety"""
    constraints = {
        "data": {
            "max_length": max_length,
            "sanitization_mode": "aggressive",
            "required": True
        }
    }
    return validate_input(strict=strict, sanitize=True, field_constraints=constraints)