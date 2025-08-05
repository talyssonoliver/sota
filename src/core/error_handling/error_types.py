
from src.infrastructure.utils.common_imports import (
    Enum,
    dataclass,
    datetime,
    field,
    re,
    traceback,
    uuid
)
"""
Error Types and Classifications

Defines a comprehensive hierarchy of error types with proper
classification and metadata for consistent error handling.
"""

# import traceback  # Consolidated to common_imports
from typing import Dict, Any, Optional, List
# from dataclasses import dataclass, field  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports
# import uuid  # Consolidated to common_imports


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification"""
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    SECURITY = "security"
    OPERATION = "operation"
    NETWORK = "network"
    DATABASE = "database"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"
    RESOURCE = "resource"


class ErrorSource(Enum):
    """Error source locations"""
    CORE = "core"
    INFRASTRUCTURE = "infrastructure"
    INTERFACE = "interface"
    EXTERNAL = "external"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Error context information"""
    error_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SystemError(Exception):
    """Base system error with enhanced metadata"""
    
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        source: ErrorSource = ErrorSource.UNKNOWN,
        recoverable: bool = True,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.category = category
        self.source = source
        self.recoverable = recoverable
        self.context = context or ErrorContext()
        self.cause = cause
        self.metadata = metadata or {}
        self.stack_trace = traceback.format_exc()
        
        # Set additional context if cause is provided
        if cause:
            self.context.metadata["caused_by"] = {
                "type": type(cause).__name__,
                "message": str(cause)
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation"""
        return {
            "error_id": self.context.error_id,
            "timestamp": self.context.timestamp.isoformat(),
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "source": self.source.value,
            "recoverable": self.recoverable,
            "context": {
                "correlation_id": self.context.correlation_id,
                "user_id": self.context.user_id,
                "session_id": self.context.session_id,
                "request_id": self.context.request_id,
                "component": self.context.component,
                "operation": self.context.operation,
                "metadata": self.context.metadata
            },
            "metadata": self.metadata,
            "caused_by": str(self.cause) if self.cause else None,
            "stack_trace": self.stack_trace
        }
    
    def add_context(self, key: str, value: Any) -> 'SystemError':
        """Add context information to error"""
        self.context.metadata[key] = value
        return self
    
    def set_component(self, component: str) -> 'SystemError':
        """Set the component where error occurred"""
        self.context.component = component
        return self
    
    def set_operation(self, operation: str) -> 'SystemError':
        """Set the operation that failed"""
        self.context.operation = operation
        return self
    
    def set_correlation_id(self, correlation_id: str) -> 'SystemError':
        """Set correlation ID for tracking"""
        self.context.correlation_id = correlation_id
        return self


class ValidationError(SystemError):
    """Error for validation failures"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        validation_rule: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            **kwargs
        )
        self.field = field
        self.value = value
        self.validation_rule = validation_rule
        
        if field:
            self.add_context("field", field)
        if value is not None:
            self.add_context("value", str(value))
        if validation_rule:
            self.add_context("validation_rule", validation_rule)


class ConfigurationError(SystemError):
    """Error for configuration issues"""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        expected_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            **kwargs
        )
        self.config_key = config_key
        self.config_file = config_file
        self.expected_type = expected_type
        
        if config_key:
            self.add_context("config_key", config_key)
        if config_file:
            self.add_context("config_file", config_file)
        if expected_type:
            self.add_context("expected_type", expected_type)


class DependencyError(SystemError):
    """Error for dependency resolution issues"""
    
    def __init__(
        self,
        message: str,
        dependency_name: Optional[str] = None,
        dependency_type: Optional[str] = None,
        resolution_path: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DEPENDENCY,
            **kwargs
        )
        self.dependency_name = dependency_name
        self.dependency_type = dependency_type
        self.resolution_path = resolution_path or []
        
        if dependency_name:
            self.add_context("dependency_name", dependency_name)
        if dependency_type:
            self.add_context("dependency_type", dependency_type)
        if resolution_path:
            self.add_context("resolution_path", resolution_path)


class SecurityError(SystemError):
    """Error for security violations"""
    
    def __init__(
        self,
        message: str,
        security_rule: Optional[str] = None,
        risk_level: Optional[str] = None,
        attempted_action: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SECURITY,
            recoverable=False,
            **kwargs
        )
        self.security_rule = security_rule
        self.risk_level = risk_level
        self.attempted_action = attempted_action
        
        if security_rule:
            self.add_context("security_rule", security_rule)
        if risk_level:
            self.add_context("risk_level", risk_level)
        if attempted_action:
            self.add_context("attempted_action", attempted_action)


class OperationError(SystemError):
    """Error for operation failures"""
    
    def __init__(
        self,
        message: str,
        operation_name: Optional[str] = None,
        step: Optional[str] = None,
        retry_count: int = 0,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.OPERATION,
            **kwargs
        )
        self.operation_name = operation_name
        self.step = step
        self.retry_count = retry_count
        
        if operation_name:
            self.add_context("operation_name", operation_name)
        if step:
            self.add_context("step", step)
        self.add_context("retry_count", retry_count)


class NetworkError(SystemError):
    """Error for network-related issues"""
    
    def __init__(
        self,
        message: str,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        timeout: Optional[float] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.NETWORK,
            **kwargs
        )
        self.endpoint = endpoint
        self.status_code = status_code
        self.timeout = timeout
        
        if endpoint:
            self.add_context("endpoint", endpoint)
        if status_code:
            self.add_context("status_code", status_code)
        if timeout:
            self.add_context("timeout", timeout)


class DatabaseError(SystemError):
    """Error for database-related issues"""
    
    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        table: Optional[str] = None,
        connection_string: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DATABASE,
            **kwargs
        )
        self.query = query
        self.table = table
        self.connection_string = connection_string
        
        if query:
            # Sanitize query for logging (remove sensitive data)
            sanitized_query = self._sanitize_query(query)
            self.add_context("query", sanitized_query)
        if table:
            self.add_context("table", table)
        if connection_string:
            # Sanitize connection string
            sanitized_conn = self._sanitize_connection_string(connection_string)
            self.add_context("connection", sanitized_conn)
    
    def _sanitize_query(self, query: str) -> str:
        """Sanitize query for logging"""
        # Remove potential sensitive data patterns
#         import re  # Consolidated to common_imports
        # This is a basic sanitization - in production, use more sophisticated methods
        sanitized = re.sub(r"'[^']*'", "'***'", query)
        sanitized = re.sub(r'"[^"]*"', '"***"', sanitized)
        return sanitized
    
    def _sanitize_connection_string(self, conn_str: str) -> str:
        """Sanitize connection string for logging"""
#         import re  # Consolidated to common_imports
        # Remove passwords and sensitive info
        sanitized = re.sub(r'password=[^;]*', 'password=***', conn_str, flags=re.IGNORECASE)
        sanitized = re.sub(r'pwd=[^;]*', 'pwd=***', sanitized, flags=re.IGNORECASE)
        return sanitized


class BusinessLogicError(SystemError):
    """Error for business logic violations"""
    
    def __init__(
        self,
        message: str,
        business_rule: Optional[str] = None,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            **kwargs
        )
        self.business_rule = business_rule
        self.entity_id = entity_id
        self.entity_type = entity_type
        
        if business_rule:
            self.add_context("business_rule", business_rule)
        if entity_id:
            self.add_context("entity_id", entity_id)
        if entity_type:
            self.add_context("entity_type", entity_type)


class ExternalServiceError(SystemError):
    """Error for external service failures"""
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        service_endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.EXTERNAL_SERVICE,
            **kwargs
        )
        self.service_name = service_name
        self.service_endpoint = service_endpoint
        self.status_code = status_code
        self.response_body = response_body
        
        if service_name:
            self.add_context("service_name", service_name)
        if service_endpoint:
            self.add_context("service_endpoint", service_endpoint)
        if status_code:
            self.add_context("status_code", status_code)
        if response_body:
            # Truncate response body for logging
            truncated_body = response_body[:500] + "..." if len(response_body) > 500 else response_body
            self.add_context("response_body", truncated_body)


def create_error_from_exception(
    exception: Exception,
    message: Optional[str] = None,
    category: Optional[ErrorCategory] = None,
    severity: Optional[ErrorSeverity] = None,
    **kwargs
) -> SystemError:
    """Create a SystemError from a generic exception"""
    error_message = message or str(exception)
    error_category = category or ErrorCategory.SYSTEM
    error_severity = severity or ErrorSeverity.MEDIUM
    
    return SystemError(
        message=error_message,
        severity=error_severity,
        category=error_category,
        cause=exception,
        **kwargs
    )


def is_recoverable_error(error: Exception) -> bool:
    """Check if an error is recoverable"""
    if isinstance(error, SystemError):
        return error.recoverable
    
    # Default recovery rules for common exceptions
    recoverable_types = (
        ConnectionError,
        TimeoutError,
        OSError
    )
    
    non_recoverable_types = (
        ValueError,
        TypeError,
        AttributeError,
        ImportError,
        SyntaxError
    )
    
    if isinstance(error, recoverable_types):
        return True
    elif isinstance(error, non_recoverable_types):
        return False
    else:
        # Default to recoverable for unknown errors
        return True


def get_error_severity(error: Exception) -> ErrorSeverity:
    """Get error severity from exception"""
    if isinstance(error, SystemError):
        return error.severity
    
    # Default severity mapping
    if isinstance(error, (SecurityError, ImportError, SyntaxError)):
        return ErrorSeverity.CRITICAL
    elif isinstance(error, (ConnectionError, TimeoutError, OSError)):
        return ErrorSeverity.HIGH
    elif isinstance(error, (ValueError, TypeError)):
        return ErrorSeverity.MEDIUM
    else:
        return ErrorSeverity.LOW