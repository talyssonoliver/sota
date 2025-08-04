#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import logging, traceback
"""
Secure Error Handling Patterns

Provides secure alternatives to try/except/pass anti-patterns.
Fixes Bandit B110 vulnerabilities (6,545 occurrences).
"""

# import logging  # Consolidated to common_imports
import functools
# import traceback  # Consolidated to common_imports
from typing import Any, Callable, Optional, TypeVar, Union
from contextlib import contextmanager


# Configure logging
logger = logging.getLogger(__name__)

# Type variable for generic functions
T = TypeVar('T')


class ErrorHandlingStrategy:
    """Base class for error handling strategies."""
    
    def handle(self, error: Exception, context: dict) -> None:
        """Handle the error with specific strategy."""
        raise NotImplementedError


class LoggingStrategy(ErrorHandlingStrategy):
    """Log errors with appropriate severity."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def handle(self, error: Exception, context: dict) -> None:
        """Log the error with context."""
        self.logger.error(
            f"Error in {context.get('function', 'unknown')}: {error}",
            exc_info=True,
            extra=context
        )


class MetricsStrategy(ErrorHandlingStrategy):
    """Track error metrics for monitoring."""
    
    def handle(self, error: Exception, context: dict) -> None:
        """Record error metrics."""
        # In production, this would send to monitoring service
        error_type = type(error).__name__
        function_name = context.get('function', 'unknown')
        logger.info(f"Metric: error.{function_name}.{error_type}")


def safe_execute(
    func: Callable[..., T],
    *args,
    default: Optional[T] = None,
    error_handler: Optional[ErrorHandlingStrategy] = None,
    log_errors: bool = True,
    reraise: bool = False,
    **kwargs
) -> Optional[T]:
    """
    Safely execute a function with proper error handling.
    
    This is a replacement for try/except/pass patterns.
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        default: Default value to return on error
        error_handler: Custom error handling strategy
        log_errors: Whether to log errors
        reraise: Whether to re-raise the exception after handling
        **kwargs: Keyword arguments for the function
        
    Returns:
        Function result or default value on error
        
    Example:
        # Instead of:
        try:
            result = risky_operation()
        except:
            pass
            
        # Use:
        result = safe_execute(risky_operation, default=None)
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        context = {
            'function': func.__name__,
            'args': args,
            'kwargs': kwargs,
            'error_type': type(e).__name__
        }
        
        if error_handler:
            error_handler.handle(e, context)
        elif log_errors:
            logger.error(
                f"Error in {func.__name__}: {e}",
                exc_info=True,
                extra=context
            )
        
        if reraise:
            raise
            
        return default


def handle_errors(
    default: Any = None,
    exceptions: tuple = (Exception,),
    log_errors: bool = True,
    error_handler: Optional[ErrorHandlingStrategy] = None,
    reraise: bool = False
):
    """
    Decorator for handling errors in functions.
    
    Replaces try/except/pass patterns at function level.
    
    Args:
        default: Default return value on error
        exceptions: Tuple of exceptions to catch
        log_errors: Whether to log errors
        error_handler: Custom error handling strategy
        reraise: Whether to re-raise after handling
        
    Example:
        @handle_errors(default=[], exceptions=(ValueError, KeyError))
        def get_items():
            return risky_operation()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                context = {
                    'function': func.__name__,
                    'error_type': type(e).__name__,
                    'module': func.__module__
                }
                
                if error_handler:
                    error_handler.handle(e, context)
                elif log_errors:
                    logger.error(
                        f"Error in {func.__name__}: {e}",
                        exc_info=True,
                        extra=context
                    )
                
                if reraise:
                    raise
                    
                return default
        return wrapper
    return decorator


@contextmanager
def suppress_and_log(*exceptions, context: str = ""):
    """
    Context manager that suppresses and logs exceptions.
    
    Replacement for contextlib.suppress when you need logging.
    
    Args:
        *exceptions: Exception types to suppress
        context: Additional context for logging
        
    Example:
        # Instead of:
        try:
            cleanup_operation()
        except:
            pass
            
        # Use:
        with suppress_and_log(Exception, context="cleanup"):
            cleanup_operation()
    """
    try:
        yield
    except exceptions as e:
        logger.warning(
            f"Suppressed error{' in ' + context if context else ''}: {e}",
            exc_info=True
        )


def resilient_import(module_name: str, attribute: Optional[str] = None) -> Any:
    """
    Safely import a module or attribute with fallback.
    
    Replaces try/except/pass for import statements.
    
    Args:
        module_name: Name of the module to import
        attribute: Optional attribute to import from module
        
    Returns:
        Module or attribute, or None if import fails
        
    Example:
        # Instead of:
        try:
            import optional_module
        except:
            pass
            
        # Use:
        optional_module = resilient_import('optional_module')
    """
    try:
        module = __import__(module_name)
        
        if attribute:
            return getattr(module, attribute, None)
        
        return module
        
    except ImportError as e:
        logger.debug(f"Optional import failed for {module_name}: {e}")
        return None


class ErrorContext:
    """
    Context manager for grouping error handling logic.
    
    Provides structured error handling for code blocks.
    """
    
    def __init__(
        self,
        operation: str,
        critical: bool = False,
        default: Any = None,
        error_handler: Optional[ErrorHandlingStrategy] = None
    ):
        self.operation = operation
        self.critical = critical
        self.default = default
        self.error_handler = error_handler or LoggingStrategy()
        self.error = None
        self.success = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            
            context = {
                'operation': self.operation,
                'critical': self.critical,
                'traceback': traceback.format_exc()
            }
            
            self.error_handler.handle(exc_val, context)
            
            if self.critical:
                # Critical errors should propagate
                return False
            
            # Non-critical errors are suppressed
            return True
        
        self.success = True
        return False
    
    @property
    def result(self):
        """Get the result or default value."""
        return self.default if self.error else None


# Example replacements for common try/except/pass patterns

def fix_silent_exception_pattern():
    """
    Example of fixing silent exception patterns.
    
    BEFORE (Vulnerable - B110):
        try:
            risky_operation()
        except:
            pass
    
    AFTER (Secure):
        with suppress_and_log(Exception, context="risky_operation"):
            risky_operation()
    """
    pass


def fix_import_pattern():
    """
    Example of fixing import patterns.
    
    BEFORE (Vulnerable - B110):
        try:
            import optional_lib
        except:
            pass
    
    AFTER (Secure):
        optional_lib = resilient_import('optional_lib')
    """
    pass


def fix_cleanup_pattern():
    """
    Example of fixing cleanup patterns.
    
    BEFORE (Vulnerable - B110):
        try:
            file.close()
        except:
            pass
    
    AFTER (Secure):
        safe_execute(file.close, log_errors=True)
    """
    pass


def fix_fallback_pattern():
    """
    Example of fixing fallback patterns.
    
    BEFORE (Vulnerable - B110):
        try:
            value = get_config_value()
        except:
            pass
        
    AFTER (Secure):
        value = safe_execute(get_config_value, default=None)
    """
    pass
