
from src.infrastructure.utils.common_imports import (
    Enum,
    asyncio,
    dataclass,
    logging
)
"""
Validation Middleware

Provides validation boundaries at system entry points to prevent
bad data from propagating through the system.
"""

# import asyncio  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
from typing import Dict, Any, Optional, Callable, List, TypeVar, Generic
from abc import ABC, abstractmethod
# from dataclasses import dataclass  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
from ..error_handling import ValidationError, ErrorSeverity
from ..configuration import get_configuration_factory

T = TypeVar('T')


class ValidationLevel(Enum):
    """Validation strictness levels"""
    STRICT = "strict"        # Fail on any validation error
    LENIENT = "lenient"      # Log warnings but continue
    PERMISSIVE = "permissive"  # Only validate critical fields


@dataclass
class ValidationResult:
    """Result of validation operation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_data: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None


class IValidationMiddleware(ABC):
    """Interface for validation middleware"""
    
    @abstractmethod
    async def validate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate data and return result"""
        pass
    
    @abstractmethod
    async def can_validate(self, data_type: str) -> bool:
        """Check if middleware can validate this data type"""
        pass
    
    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """Get list of supported data types"""
        pass


class ValidationChain:
    """Chain of validation middleware components"""
    
    def __init__(self):
        self._middleware: List[IValidationMiddleware] = []
        self.logger = logging.getLogger(__name__)
    
    def add_middleware(self, middleware: IValidationMiddleware) -> 'ValidationChain':
        """Add validation middleware to chain"""
        self._middleware.append(middleware)
        return self
    
    def remove_middleware(self, middleware: IValidationMiddleware) -> bool:
        """Remove validation middleware from chain"""
        try:
            self._middleware.remove(middleware)
            return True
        except ValueError:
            return False
    
    async def validate(self, data: Any, data_type: str, 
                      context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate data through middleware chain"""
        all_errors = []
        all_warnings = []
        sanitized_data = data
        metadata = {}
        
        for middleware in self._middleware:
            if await middleware.can_validate(data_type):
                try:
                    result = await middleware.validate(sanitized_data, context)
                    
                    # Accumulate results
                    all_errors.extend(result.errors)
                    all_warnings.extend(result.warnings)
                    
                    # Use sanitized data for next middleware
                    if result.sanitized_data is not None:
                        sanitized_data = result.sanitized_data
                    
                    # Merge metadata
                    if result.metadata:
                        metadata.update(result.metadata)
                    
                    # Stop on first validation failure in strict mode
                    if not result.is_valid and self._is_strict_mode(context):
                        break
                        
                except Exception as e:
                    self.logger.error(f"Validation middleware error: {e}")
                    all_errors.append(f"Validation middleware failed: {str(e)}")
        
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            sanitized_data=sanitized_data,
            metadata=metadata
        )
    
    def _is_strict_mode(self, context: Optional[Dict[str, Any]]) -> bool:
        """Check if strict validation mode is enabled"""
        if context and "validation_level" in context:
            return context["validation_level"] == ValidationLevel.STRICT
        return True  # Default to strict mode


class ValidationMiddleware:
    """Main validation middleware coordinator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._validation_chain = ValidationChain()
        self._validation_config = self._load_validation_config()
        self._setup_default_middleware()
    
    def _load_validation_config(self) -> Dict[str, Any]:
        """Load validation configuration"""
        try:
            config_factory = get_configuration_factory()
            env_provider = config_factory.get_environment_provider()
            return env_provider.get_section("validation") or {
                "strict_mode": True,
                "sanitization_enabled": True,
                "max_validation_time_ms": 5000,
                "cache_validation_results": True
            }
        except Exception as e:
            self.logger.warning(f"Could not load validation config: {e}")
            return {"strict_mode": True}
    
    def _setup_default_middleware(self):
        """Setup default validation middleware"""
        try:
            from .input_validator import InputValidator
            self._validation_chain.add_middleware(InputValidator())
        except ImportError as e:
            self.logger.warning(f"Could not load InputValidator: {e}")
        
        try:
            from .schema_validator import SchemaValidator
            self._validation_chain.add_middleware(SchemaValidator())
        except ImportError as e:
            self.logger.warning(f"Could not load SchemaValidator: {e}")
        
        try:
            from .business_rules import BusinessRuleValidator
            self._validation_chain.add_middleware(BusinessRuleValidator())
        except ImportError as e:
            self.logger.warning(f"Could not load BusinessRuleValidator: {e}")
    
    async def validate_request(self, data: Any, endpoint: str, 
                              context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate incoming request data"""
        validation_context = self._build_validation_context(endpoint, context)
        
        try:
            result = await self._validation_chain.validate(
                data, 
                "request",
                validation_context
            )
            
            # Log validation results
            self._log_validation_result(result, endpoint, "request")
            
            # Raise error if validation failed and in strict mode
            if not result.is_valid and self._is_strict_mode(validation_context):
                raise ValidationError(
                    f"Request validation failed for {endpoint}: {'; '.join(result.errors)}",
                    field="request_data",
                    value=data
                ).set_component("ValidationMiddleware").set_operation("validate_request")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Request validation error: {e}")
            raise ValidationError(
                f"Request validation system error: {str(e)}",
                severity=ErrorSeverity.HIGH
            ).set_component("ValidationMiddleware")
    
    async def validate_response(self, data: Any, endpoint: str,
                               context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate outgoing response data"""
        validation_context = self._build_validation_context(endpoint, context)
        
        try:
            result = await self._validation_chain.validate(
                data,
                "response", 
                validation_context
            )
            
            # Log validation results
            self._log_validation_result(result, endpoint, "response")
            
            # Response validation failures are usually warnings in production
            if not result.is_valid:
                self.logger.warning(
                    f"Response validation failed for {endpoint}: {'; '.join(result.errors)}"
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Response validation error: {e}")
            # Don't fail the response for validation errors
            return ValidationResult(
                is_valid=False,
                errors=[f"Response validation system error: {str(e)}"],
                warnings=[]
            )
    
    async def validate_data(self, data: Any, data_type: str,
                           context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate arbitrary data"""
        validation_context = context or {}
        
        try:
            result = await self._validation_chain.validate(data, data_type, validation_context)
            self._log_validation_result(result, data_type, "data")
            return result
            
        except Exception as e:
            self.logger.error(f"Data validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Data validation system error: {str(e)}"],
                warnings=[]
            )
    
    def _build_validation_context(self, endpoint: str, 
                                 context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build validation context with configuration"""
        validation_context = context or {}
        validation_context.update({
            "endpoint": endpoint,
            "validation_level": (
                ValidationLevel.STRICT if self._validation_config.get("strict_mode", True)
                else ValidationLevel.LENIENT
            ),
            "sanitization_enabled": self._validation_config.get("sanitization_enabled", True),
            "max_validation_time_ms": self._validation_config.get("max_validation_time_ms", 5000)
        })
        return validation_context
    
    def _is_strict_mode(self, context: Dict[str, Any]) -> bool:
        """Check if strict validation mode is enabled"""
        return context.get("validation_level") == ValidationLevel.STRICT
    
    def _log_validation_result(self, result: ValidationResult, endpoint: str, data_type: str):
        """Log validation results"""
        if not result.is_valid:
            self.logger.warning(
                f"Validation failed for {endpoint} ({data_type}): "
                f"Errors: {result.errors}, Warnings: {result.warnings}"
            )
        elif result.warnings:
            self.logger.info(
                f"Validation warnings for {endpoint} ({data_type}): {result.warnings}"
            )
        else:
            self.logger.debug(f"Validation passed for {endpoint} ({data_type})")
    
    def add_custom_middleware(self, middleware: IValidationMiddleware):
        """Add custom validation middleware"""
        self._validation_chain.add_middleware(middleware)
    
    def remove_custom_middleware(self, middleware: IValidationMiddleware):
        """Remove custom validation middleware"""
        self._validation_chain.remove_middleware(middleware)
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        # This would typically be implemented with metrics collection
        return {
            "middleware_count": len(self._validation_chain._middleware),
            "strict_mode": self._validation_config.get("strict_mode", True),
            "sanitization_enabled": self._validation_config.get("sanitization_enabled", True)
        }


# Request/Response validation decorators
def validate_request(data_type: str = "request", strict: bool = True):
    """Decorator to validate request data"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # Extract request data (assume first argument after self)
            request_data = args[1] if len(args) > 1 else kwargs.get('data')
            
            if request_data is not None:
                middleware = get_validation_middleware()
                context = {"validation_level": ValidationLevel.STRICT if strict else ValidationLevel.LENIENT}
                
                result = await middleware.validate_data(request_data, data_type, context)
                
                if not result.is_valid and strict:
                    raise ValidationError(
                        f"Request validation failed: {'; '.join(result.errors)}"
                    )
                
                # Use sanitized data if available
                if result.sanitized_data is not None:
                    if len(args) > 1:
                        args = list(args)
                        args[1] = result.sanitized_data
                        args = tuple(args)
                    else:
                        kwargs['data'] = result.sanitized_data
            
            return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_response(data_type: str = "response", strict: bool = False):
    """Decorator to validate response data"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            if result is not None:
                middleware = get_validation_middleware()
                context = {"validation_level": ValidationLevel.STRICT if strict else ValidationLevel.LENIENT}
                
                validation_result = await middleware.validate_data(result, data_type, context)
                
                if not validation_result.is_valid and strict:
                    raise ValidationError(
                        f"Response validation failed: {'; '.join(validation_result.errors)}"
                    )
                
                # Use sanitized data if available
                if validation_result.sanitized_data is not None:
                    result = validation_result.sanitized_data
            
            return result
        
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global validation middleware instance
_global_validation_middleware: Optional[ValidationMiddleware] = None


def get_validation_middleware() -> ValidationMiddleware:
    """Get global validation middleware instance"""
    global _global_validation_middleware
    if _global_validation_middleware is None:
        _global_validation_middleware = ValidationMiddleware()
    return _global_validation_middleware