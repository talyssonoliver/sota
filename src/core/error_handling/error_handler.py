
from src.infrastructure.utils.common_imports import asyncio, logging
"""
Error Handler Implementation

Provides centralized error handling with proper logging, metrics,
and escalation to replace inconsistent error patterns.
"""

# import logging  # Consolidated to common_imports
# import asyncio  # Consolidated to common_imports
from typing import Dict, Any, Optional, Callable, List, Type
from abc import ABC, abstractmethod
from .error_types import SystemError, ErrorSeverity, ErrorCategory, ErrorSource, create_error_from_exception


class IErrorHandler(ABC):
    """Interface for error handlers"""
    
    @abstractmethod
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """Handle an error and return True if handled successfully"""
        pass
    
    @abstractmethod
    async def can_handle(self, error: Exception) -> bool:
        """Check if this handler can handle the error"""
        pass
    
    @abstractmethod
    async def get_recovery_suggestion(self, error: Exception) -> Optional[str]:
        """Get recovery suggestion for the error"""
        pass


class ErrorHandlerChain:
    """Chain of responsibility pattern for error handlers"""
    
    def __init__(self):
        self._handlers: List[IErrorHandler] = []
    
    def add_handler(self, handler: IErrorHandler) -> 'ErrorHandlerChain':
        """Add error handler to chain"""
        self._handlers.append(handler)
        return self
    
    def remove_handler(self, handler: IErrorHandler) -> bool:
        """Remove error handler from chain"""
        try:
            self._handlers.remove(handler)
            return True
        except ValueError:
            return False
    
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """Handle error through chain of handlers"""
        for handler in self._handlers:
            if await handler.can_handle(error):
                try:
                    if await handler.handle_error(error, context):
                        return True
                except Exception as handler_error:
                    # Handler failed - log and continue to next handler
                    logging.error(f"Error handler {type(handler).__name__} failed: {handler_error}")
        
        return False


class ErrorHandler:
    """Main error handler with comprehensive error processing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._error_counts: Dict[str, int] = {}
        self._error_callbacks: Dict[ErrorCategory, List[Callable]] = {}
        self._severity_thresholds: Dict[ErrorSeverity, int] = {
            ErrorSeverity.LOW: 10,
            ErrorSeverity.MEDIUM: 5,
            ErrorSeverity.HIGH: 2,
            ErrorSeverity.CRITICAL: 1
        }
        self._handler_chain = ErrorHandlerChain()
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default error handlers"""
        self._handler_chain.add_handler(SecurityErrorHandler())
        self._handler_chain.add_handler(ValidationErrorHandler())
        self._handler_chain.add_handler(ConfigurationErrorHandler())
        self._handler_chain.add_handler(DependencyErrorHandler())
        self._handler_chain.add_handler(NetworkErrorHandler())
        self._handler_chain.add_handler(DatabaseErrorHandler())
        self._handler_chain.add_handler(GenericErrorHandler())
    
    async def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        component: Optional[str] = None,
        operation: Optional[str] = None
    ) -> bool:
        """Handle error with comprehensive processing"""
        
        # Convert to SystemError if needed
        if not isinstance(error, SystemError):
            system_error = create_error_from_exception(error)
        else:
            system_error = error
        
        # Add context information
        if component:
            system_error.set_component(component)
        if operation:
            system_error.set_operation(operation)
        if context:
            for key, value in context.items():
                system_error.add_context(key, value)
        
        # Log the error
        await self._log_error(system_error)
        
        # Update error metrics
        await self._update_error_metrics(system_error)
        
        # Check for error escalation
        await self._check_escalation(system_error)
        
        # Execute error callbacks
        await self._execute_callbacks(system_error)
        
        # Try to handle through handler chain
        handled = await self._handler_chain.handle_error(system_error, context)
        
        # If not handled and critical, escalate
        if not handled and system_error.severity == ErrorSeverity.CRITICAL:
            await self._escalate_critical_error(system_error)
        
        return handled
    
    async def _log_error(self, error: SystemError):
        """Log error with appropriate level"""
        error_dict = error.to_dict()
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(
                f"CRITICAL ERROR: {error.message}",
                extra={"error_data": error_dict}
            )
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(
                f"HIGH SEVERITY ERROR: {error.message}",
                extra={"error_data": error_dict}
            )
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(
                f"MEDIUM SEVERITY ERROR: {error.message}",
                extra={"error_data": error_dict}
            )
        else:
            self.logger.info(
                f"LOW SEVERITY ERROR: {error.message}",
                extra={"error_data": error_dict}
            )
    
    async def _update_error_metrics(self, error: SystemError):
        """Update error metrics and counters"""
        error_key = f"{error.category.value}:{error.severity.value}"
        self._error_counts[error_key] = self._error_counts.get(error_key, 0) + 1
        
        # Component-specific metrics
        if error.context.component:
            component_key = f"{error.context.component}:{error.category.value}"
            self._error_counts[component_key] = self._error_counts.get(component_key, 0) + 1
    
    async def _check_escalation(self, error: SystemError):
        """Check if error should be escalated based on frequency"""
        error_key = f"{error.category.value}:{error.severity.value}"
        threshold = self._severity_thresholds.get(error.severity, 1)
        
        if self._error_counts.get(error_key, 0) >= threshold:
            await self._escalate_error(error, "frequency_threshold_exceeded")
    
    async def _execute_callbacks(self, error: SystemError):
        """Execute registered error callbacks"""
        callbacks = self._error_callbacks.get(error.category, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(error)
                else:
                    callback(error)
            except Exception as callback_error:
                self.logger.error(f"Error callback failed: {callback_error}")
    
    async def _escalate_error(self, error: SystemError, reason: str):
        """Escalate error to appropriate channels"""
        self.logger.critical(
            f"ERROR ESCALATION: {reason} - {error.message}",
            extra={
                "error_id": error.context.error_id,
                "escalation_reason": reason,
                "error_data": error.to_dict()
            }
        )
        
        # Here you would integrate with alerting systems, notifications, etc.
        # For now, we'll just log the escalation
    
    async def _escalate_critical_error(self, error: SystemError):
        """Handle critical error escalation"""
        await self._escalate_error(error, "critical_error_unhandled")
    
    def register_callback(self, category: ErrorCategory, callback: Callable):
        """Register error callback for specific category"""
        if category not in self._error_callbacks:
            self._error_callbacks[category] = []
        self._error_callbacks[category].append(callback)
    
    def unregister_callback(self, category: ErrorCategory, callback: Callable):
        """Unregister error callback"""
        if category in self._error_callbacks:
            try:
                self._error_callbacks[category].remove(callback)
            except ValueError:
                pass
    
    def add_handler(self, handler: IErrorHandler):
        """Add custom error handler"""
        self._handler_chain.add_handler(handler)
    
    def remove_handler(self, handler: IErrorHandler):
        """Remove error handler"""
        self._handler_chain.remove_handler(handler)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "error_counts": self._error_counts.copy(),
            "total_errors": sum(self._error_counts.values()),
            "severity_thresholds": self._severity_thresholds.copy()
        }
    
    def reset_error_counts(self):
        """Reset error counters"""
        self._error_counts.clear()


# Specific error handlers for different categories

class SecurityErrorHandler(IErrorHandler):
    """Handler for security-related errors"""
    
    async def can_handle(self, error: Exception) -> bool:
        return isinstance(error, SystemError) and error.category == ErrorCategory.SECURITY
    
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        # Security errors should not be auto-recovered
        # Log security incident and potentially lock down system
        logging.critical(f"SECURITY INCIDENT: {error}")
        return False  # Never auto-handle security errors
    
    async def get_recovery_suggestion(self, error: Exception) -> Optional[str]:
        return "Security error detected. Manual review required. Check logs and security policies."


class ValidationErrorHandler(IErrorHandler):
    """Handler for validation errors"""
    
    async def can_handle(self, error: Exception) -> bool:
        return isinstance(error, SystemError) and error.category == ErrorCategory.VALIDATION
    
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        # Validation errors usually require user input correction
        logging.warning(f"Validation error: {error}")
        return True  # Mark as handled (user needs to fix input)
    
    async def get_recovery_suggestion(self, error: Exception) -> Optional[str]:
        if hasattr(error, 'field') and error.field:
            return f"Please correct the value for field '{error.field}'"
        return "Please check your input data and try again"


class ConfigurationErrorHandler(IErrorHandler):
    """Handler for configuration errors"""
    
    async def can_handle(self, error: Exception) -> bool:
        return isinstance(error, SystemError) and error.category == ErrorCategory.CONFIGURATION
    
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        # Configuration errors usually require admin intervention
        logging.error(f"Configuration error: {error}")
        return False  # Cannot auto-handle config errors
    
    async def get_recovery_suggestion(self, error: Exception) -> Optional[str]:
        if hasattr(error, 'config_key') and error.config_key:
            return f"Please check configuration for key '{error.config_key}'"
        return "Please review system configuration and restart if necessary"


class DependencyErrorHandler(IErrorHandler):
    """Handler for dependency resolution errors"""
    
    async def can_handle(self, error: Exception) -> bool:
        return isinstance(error, SystemError) and error.category == ErrorCategory.DEPENDENCY
    
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        # Dependency errors usually require system restart or reconfiguration
        logging.error(f"Dependency error: {error}")
        return False  # Cannot auto-handle dependency errors
    
    async def get_recovery_suggestion(self, error: Exception) -> Optional[str]:
        if hasattr(error, 'dependency_name') and error.dependency_name:
            return f"Please check dependency '{error.dependency_name}' registration and configuration"
        return "Please check system dependencies and restart services"


class NetworkErrorHandler(IErrorHandler):
    """Handler for network-related errors"""
    
    async def can_handle(self, error: Exception) -> bool:
        return isinstance(error, SystemError) and error.category == ErrorCategory.NETWORK
    
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        # Network errors might be retryable
        logging.warning(f"Network error: {error}")
        return True  # Mark as handled (might retry automatically)
    
    async def get_recovery_suggestion(self, error: Exception) -> Optional[str]:
        if hasattr(error, 'endpoint') and error.endpoint:
            return f"Check network connectivity to '{error.endpoint}' and try again"
        return "Check network connectivity and try again"


class DatabaseErrorHandler(IErrorHandler):
    """Handler for database-related errors"""
    
    async def can_handle(self, error: Exception) -> bool:
        return isinstance(error, SystemError) and error.category == ErrorCategory.DATABASE
    
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        # Database errors might be retryable depending on type
        logging.error(f"Database error: {error}")
        return True  # Mark as handled (might retry automatically)
    
    async def get_recovery_suggestion(self, error: Exception) -> Optional[str]:
        return "Check database connectivity and try again. If problem persists, contact administrator."


class GenericErrorHandler(IErrorHandler):
    """Fallback handler for unspecified errors"""
    
    async def can_handle(self, error: Exception) -> bool:
        return True  # Handles everything as fallback
    
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        # Generic handling - log and potentially retry
        logging.error(f"Unhandled error: {error}")
        return isinstance(error, SystemError) and error.recoverable
    
    async def get_recovery_suggestion(self, error: Exception) -> Optional[str]:
        return "An unexpected error occurred. Please try again or contact support."


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


async def handle_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    component: Optional[str] = None,
    operation: Optional[str] = None
) -> bool:
    """Convenience function to handle errors"""
    handler = get_error_handler()
    return await handler.handle_error(error, context, component, operation)