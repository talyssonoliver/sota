"""
Unified Error Handling Module

Provides comprehensive error handling, classification, and recovery
framework to replace inconsistent error patterns throughout the system.
"""

from .error_types import (
    SystemError, ValidationError, ConfigurationError, 
    DependencyError, SecurityError, OperationError,
    BusinessLogicError, ErrorSeverity, ErrorCategory
)
from .error_handler import ErrorHandler, IErrorHandler
from .error_boundary import (
    ErrorBoundary, IErrorBoundary, BoundaryConfig, BoundaryMode, 
    ErrorBoundaryManager, with_error_boundary
)
from .error_recovery import ErrorRecoveryManager, IErrorRecoveryStrategy
from .error_reporter import ErrorReporter, IErrorReporter

__all__ = [
    # Error types
    "SystemError",
    "ValidationError", 
    "ConfigurationError",
    "DependencyError",
    "SecurityError",
    "OperationError",
    "BusinessLogicError",
    "ErrorSeverity",
    "ErrorCategory",
    
    # Error handling
    "ErrorHandler",
    "IErrorHandler",
    
    # Error boundaries
    "ErrorBoundary",
    "IErrorBoundary",
    "BoundaryConfig",
    "BoundaryMode",
    "ErrorBoundaryManager",
    "with_error_boundary",
    
    # Error recovery
    "ErrorRecoveryManager",
    "IErrorRecoveryStrategy",
    
    # Error reporting
    "ErrorReporter", 
    "IErrorReporter"
]