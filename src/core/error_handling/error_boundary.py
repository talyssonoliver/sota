
from src.infrastructure.utils.common_imports import (
    Enum,
    asyncio,
    dataclass,
    logging,
    time
)
"""
Error Boundary Implementation

Provides error boundaries to prevent cascade failures and contain
errors within specific components or operations.
"""


from typing import Dict, Any, Optional, Callable, List, TypeVar, Generic, Union
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from .error_types import SystemError, ErrorSeverity, ErrorCategory
from .error_handler import get_error_handler

T = TypeVar('T')


class ErrorContext:
    """Error context for tracking error information in tests"""
    _current_context = None
    
    def __init__(self, metadata: Dict[str, Any]):
        self.metadata = metadata.copy()
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to the context"""
        self.metadata[key] = value
    
    def __enter__(self):
        """Enter context manager"""
        self._previous_context = ErrorContext._current_context
        ErrorContext._current_context = self
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        ErrorContext._current_context = self._previous_context
        return False
    
    @classmethod
    def get_current(cls):
        """Get the current error context"""
        return cls._current_context


class BoundaryMode(Enum):
    """Error boundary isolation modes"""
    FAIL_FAST = "fail_fast"          # Fail immediately on first error
    FAIL_SAFE = "fail_safe"          # Continue with default/fallback values
    CIRCUIT_BREAKER = "circuit_breaker"  # Open circuit after threshold
    RETRY = "retry"                  # Retry operation with backoff


@dataclass
class BoundaryConfig:
    """Error boundary configuration"""
    mode: BoundaryMode = BoundaryMode.FAIL_SAFE
    max_retries: int = 3
    retry_delay_ms: int = 1000
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout_ms: int = 60000
    fallback_enabled: bool = True
    isolation_enabled: bool = True
    metrics_enabled: bool = True


class IErrorBoundary(ABC):
    """Interface for error boundaries"""
    
    @abstractmethod
    async def execute(self, operation: Callable[[], T]) -> T:
        """Execute operation within error boundary"""
        pass
    
    @abstractmethod
    async def can_execute(self) -> bool:
        """Check if boundary can execute operations"""
        pass
    
    @abstractmethod
    async def reset(self) -> bool:
        """Reset boundary state"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get boundary statistics"""
        pass


class ErrorBoundaryState:
    """Manages error boundary state"""
    
    def __init__(self, config: BoundaryConfig):
        self.config = config
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.is_circuit_open = False
        self.total_executions = 0
        self.total_errors = 0
        
    def can_execute(self) -> bool:
        """Check if operations can be executed"""
        if self.config.mode == BoundaryMode.CIRCUIT_BREAKER and self.is_circuit_open:
            current_time = time.time() * 1000
            if current_time - self.last_failure_time > self.config.circuit_breaker_timeout_ms:
                # Try to close circuit
                self.is_circuit_open = False
                return True
            return False
        return True
    
    def record_success(self):
        """Record successful execution"""
        self.success_count += 1
        self.total_executions += 1
        self.failure_count = 0
        
        if self.config.mode == BoundaryMode.CIRCUIT_BREAKER:
            self.is_circuit_open = False
    
    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.total_errors += 1
        self.total_executions += 1
        self.last_failure_time = time.time() * 1000
        
        if (self.config.mode == BoundaryMode.CIRCUIT_BREAKER and 
            self.failure_count >= self.config.circuit_breaker_threshold):
            self.is_circuit_open = True
    
    def reset(self):
        """Reset state"""
        self.failure_count = 0
        self.success_count = 0
        self.is_circuit_open = False
        self.last_failure_time = 0


class ErrorBoundary(IErrorBoundary):
    """Comprehensive error boundary implementation"""
    
    def __init__(
        self,
        name: Optional[str] = None,
        config: Optional[BoundaryConfig] = None,
        fallback_handler: Optional[Callable[[Exception], T]] = None,
        error_classifier: Optional[Callable[[Exception], bool]] = None,
        mode: Optional[BoundaryMode] = None,
        # Additional parameters for backward compatibility with tests
        fallback_value: Any = None,
        fallback_function: Optional[Callable] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        failure_threshold: Optional[int] = None,
        reset_timeout: Optional[float] = None
    ):
        self.name = name or "default_boundary"
        
        # Build config from parameters
        if config is None:
            config = BoundaryConfig()
        
        # Handle mode parameter for backward compatibility
        if mode is not None:
            config.mode = mode
            
        # Handle config parameters from test compatibility
        if max_retries is not None:
            config.max_retries = max_retries
        if retry_delay is not None:
            config.retry_delay_ms = int(retry_delay * 1000)  # Convert seconds to ms
        if failure_threshold is not None:
            config.circuit_breaker_threshold = failure_threshold
        if reset_timeout is not None:
            config.circuit_breaker_timeout_ms = int(reset_timeout * 1000)  # Convert seconds to ms
                
        self.config = config
        
        # Handle fallback configurations
        self.fallback_handler = fallback_handler
        self.fallback_value = fallback_value
        self.fallback_function = fallback_function
        
        # If we have a fallback_value or fallback_function, create a handler
        if fallback_value is not None:
            self.fallback_handler = lambda error: fallback_value
        elif fallback_function is not None:
            self.fallback_handler = lambda error: fallback_function(error, None)
        
        self.error_classifier = error_classifier or self._default_error_classifier
        self.state = ErrorBoundaryState(self.config)
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self._metrics: Dict[str, Any] = {}
    
    def execute(self, operation: Callable[[], T]) -> T:
        """Execute operation within error boundary (supports both sync and async)"""
        # For backward compatibility, support synchronous execution
        if asyncio.iscoroutinefunction(operation):
            # If operation is async, we need to use async execution
            try:
                # Try to get current event loop to see if we're already in one
                loop = asyncio.get_running_loop()
                # If we're in an event loop, we can't use asyncio.run()
                # The caller should use execute_async instead
                raise RuntimeError(
                    "Cannot use execute() with async operation in a running event loop. "
                    "Use execute_async() instead."
                )
            except RuntimeError:
                # No event loop running, safe to use asyncio.run()
                return asyncio.run(self._async_execute(operation))
        else:
            # For sync operations, use sync execution
            return self._sync_execute(operation)
    
    async def execute_async(self, operation: Callable[[], T]) -> T:
        """Execute async operation within error boundary"""
        return await self._async_execute(operation)
    
    async def _async_execute(self, operation: Callable[[], T]) -> T:
        """Execute async operation within error boundary"""
        if not await self.can_execute():
            if self.config.mode == BoundaryMode.CIRCUIT_BREAKER:
                raise Exception("Circuit breaker is open")
        
        if self.config.mode == BoundaryMode.RETRY:
            return await self._execute_with_retry(operation)
        else:
            return await self._execute_once(operation)
    
    def _sync_execute(self, operation: Callable[[], T]) -> T:
        """Execute sync operation within error boundary"""
        if not self._sync_can_execute():
            if self.config.mode == BoundaryMode.CIRCUIT_BREAKER:
                raise Exception("Circuit breaker is open")
        
        if self.config.mode == BoundaryMode.RETRY:
            return self._sync_execute_with_retry(operation)
        else:
            return self._sync_execute_once(operation)
    
    def _sync_execute_once(self, operation: Callable[[], T]) -> T:
        """Execute operation once with synchronous error handling"""
        try:
            result = operation()
            self.state.record_success()
            self._update_metrics("success")
            return result
            
        except Exception as error:
            self.state.record_failure()
            self._update_metrics("failure")
            
            # Classify error
            is_boundary_error = self.error_classifier(error)
            
            if is_boundary_error:
                # Handle through error handler (sync version)
                error_handler = get_error_handler()
                # For sync execution, we can't await, so skip the async error handling
                # Just log the error directly
                self.logger.error(f"Error in boundary '{self.name}': {error}")
                
                # Try fallback if configured
                if self.config.fallback_enabled and self.fallback_handler:
                    try:
                        return self.fallback_handler(error)
                    except Exception as fallback_error:
                        self.logger.error(f"Fallback handler failed: {fallback_error}")
                
                # Fail fast or fail safe
                if self.config.mode == BoundaryMode.FAIL_FAST:
                    raise
                elif self.config.mode == BoundaryMode.FAIL_SAFE:
                    return None  # or default value
            
            # Re-raise non-boundary errors
            raise
    
    def _sync_execute_with_retry(self, operation: Callable[[], T]) -> T:
        """Execute operation with synchronous retry logic"""
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                result = operation()
                self.state.record_success()
                self._update_metrics("success")
                return result
                
            except Exception as error:
                last_error = error
                is_retryable = self._is_retryable_error(error)
                
                if attempt < self.config.max_retries and is_retryable:
                    delay = self._calculate_retry_delay(attempt)
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay}ms: {error}"
                    )
#                     import time  # Consolidated to common_imports
                    time.sleep(delay / 1000)  # Convert ms to seconds
                    continue
                else:
                    self.state.record_failure()
                    self._update_metrics("failure")
                    
                    # Handle through error handler (sync version)
                    self.logger.error(f"Retry exhausted in boundary '{self.name}': {error}")
                    
                    # Try fallback if available
                    if self.config.fallback_enabled and self.fallback_handler:
                        try:
                            return self.fallback_handler(error)
                        except Exception as fallback_error:
                            self.logger.error(f"Fallback handler failed: {fallback_error}")
                    
                    raise
        
        # Should never reach here, but just in case
        if last_error:
            raise last_error
    
    async def _execute_once(self, operation: Callable[[], T]) -> T:
        """Execute operation once with error handling"""
        try:
            if asyncio.iscoroutinefunction(operation):
                result = await operation()
            else:
                result = operation()
            
            self.state.record_success()
            self._update_metrics("success")
            return result
            
        except Exception as error:
            self.state.record_failure()
            self._update_metrics("failure")
            
            # Classify error
            is_boundary_error = self.error_classifier(error)
            
            if is_boundary_error:
                # Handle through error handler
                error_handler = get_error_handler()
                await error_handler.handle_error(
                    error,
                    context={"boundary": self.name},
                    component=self.name
                )
                
                # Try fallback if configured
                if self.config.fallback_enabled and self.fallback_handler:
                    try:
                        return self.fallback_handler(error)
                    except Exception as fallback_error:
                        self.logger.error(f"Fallback handler failed: {fallback_error}")
                
                # Fail fast or fail safe
                if self.config.mode == BoundaryMode.FAIL_FAST:
                    raise
                elif self.config.mode == BoundaryMode.FAIL_SAFE:
                    return None  # or default value
            
            # Re-raise non-boundary errors
            raise
    
    async def _execute_with_retry(self, operation: Callable[[], T]) -> T:
        """Execute operation with retry logic"""
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(operation):
                    result = await operation()
                else:
                    result = operation()
                
                self.state.record_success()
                self._update_metrics("success")
                return result
                
            except Exception as error:
                last_error = error
                is_retryable = self._is_retryable_error(error)
                
                if attempt < self.config.max_retries and is_retryable:
                    delay = self._calculate_retry_delay(attempt)
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay}ms: {error}"
                    )
                    await asyncio.sleep(delay / 1000)
                    continue
                else:
                    self.state.record_failure()
                    self._update_metrics("failure")
                    
                    # Handle through error handler
                    error_handler = get_error_handler()
                    await error_handler.handle_error(
                        error,
                        context={
                            "boundary": self.name,
                            "attempt": attempt + 1,
                            "max_retries": self.config.max_retries
                        },
                        component=self.name
                    )
                    
                    # Try fallback if available
                    if self.config.fallback_enabled and self.fallback_handler:
                        try:
                            return self.fallback_handler(error)
                        except Exception as fallback_error:
                            self.logger.error(f"Fallback handler failed: {fallback_error}")
                    
                    raise
        
        # Should never reach here, but just in case
        if last_error:
            raise last_error
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Check if error is retryable"""
        if isinstance(error, SystemError):
            return error.recoverable and error.category in [
                ErrorCategory.NETWORK,
                ErrorCategory.EXTERNAL_SERVICE,
                ErrorCategory.DATABASE
            ]
        
        # For RETRY mode, be more permissive - retry most errors except critical ones
        if self.config.mode == BoundaryMode.RETRY:
            non_retryable_types = (
                ImportError,
                SyntaxError,
                SystemExit,
                KeyboardInterrupt,
                MemoryError
            )
            return not isinstance(error, non_retryable_types)
        
        # Default retryable error types for other modes
        retryable_types = (
            ConnectionError,
            TimeoutError,
            OSError
        )
        
        return isinstance(error, retryable_types)
    
    def _calculate_retry_delay(self, attempt: int) -> int:
        """Calculate retry delay with exponential backoff"""
        base_delay = self.config.retry_delay_ms
        return int(base_delay * (2 ** attempt))
    
    def _default_error_classifier(self, error: Exception) -> bool:
        """Default error classification logic"""
        if isinstance(error, SystemError):
            return error.severity != ErrorSeverity.CRITICAL
        
        # Consider most errors as boundary errors except critical system errors
        critical_types = (ImportError, SyntaxError, SystemExit, KeyboardInterrupt)
        return not isinstance(error, critical_types)
    
    def _update_metrics(self, result_type: str):
        """Update boundary metrics"""
        if not self.config.metrics_enabled:
            return
        
        self._metrics[f"{result_type}_count"] = self._metrics.get(f"{result_type}_count", 0) + 1
        # Use time.time() for sync operations, asyncio loop time for async operations
        try:
            # Try to get asyncio loop time if we're in an async context
            loop = asyncio.get_running_loop()
            self._metrics["last_execution"] = loop.time()
        except RuntimeError:
            # No running event loop, use standard time
            import time
            self._metrics["last_execution"] = time.time()
    
    async def can_execute(self) -> bool:
        """Check if boundary can execute operations"""
        return self.state.can_execute()
    
    def _sync_can_execute(self) -> bool:
        """Synchronous version of can_execute"""
        return self.state.can_execute()
    
    async def reset(self) -> bool:
        """Reset boundary state"""
        self.state.reset()
        self._metrics.clear()
        self.logger.info(f"Error boundary '{self.name}' reset")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get boundary statistics"""
        return {
            "name": self.name,
            "config": {
                "mode": self.config.mode.value,
                "max_retries": self.config.max_retries,
                "circuit_breaker_threshold": self.config.circuit_breaker_threshold
            },
            "state": {
                "failure_count": self.state.failure_count,
                "success_count": self.state.success_count,
                "is_circuit_open": self.state.is_circuit_open,
                "total_executions": self.state.total_executions,
                "total_errors": self.state.total_errors,
                "error_rate": (
                    self.state.total_errors / self.state.total_executions 
                    if self.state.total_executions > 0 else 0
                )
            },
            "metrics": self._metrics.copy()
        }


class ErrorBoundaryManager:
    """Manages multiple error boundaries"""
    
    def __init__(self):
        self._boundaries: Dict[str, ErrorBoundary] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_boundary(
        self,
        name: str,
        config: Optional[BoundaryConfig] = None,
        fallback_handler: Optional[Callable] = None
    ) -> ErrorBoundary:
        """Create new error boundary"""
        if name in self._boundaries:
            raise ValueError(f"Boundary '{name}' already exists")
        
        boundary = ErrorBoundary(name, config, fallback_handler)
        self._boundaries[name] = boundary
        self.logger.info(f"Created error boundary: {name}")
        return boundary
    
    def get_boundary(self, name: str) -> Optional[ErrorBoundary]:
        """Get error boundary by name"""
        return self._boundaries.get(name)
    
    def remove_boundary(self, name: str) -> bool:
        """Remove error boundary"""
        if name in self._boundaries:
            del self._boundaries[name]
            self.logger.info(f"Removed error boundary: {name}")
            return True
        return False
    
    def list_boundaries(self) -> List[str]:
        """List all boundary names"""
        return list(self._boundaries.keys())
    
    async def reset_all_boundaries(self) -> int:
        """Reset all boundaries"""
        count = 0
        for boundary in self._boundaries.values():
            await boundary.reset()
            count += 1
        return count
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all boundaries"""
        return {name: boundary.get_stats() for name, boundary in self._boundaries.items()}
    
    def get_unhealthy_boundaries(self) -> List[str]:
        """Get boundaries that are in unhealthy state"""
        unhealthy = []
        for name, boundary in self._boundaries.items():
            stats = boundary.get_stats()
            if stats["state"]["is_circuit_open"] or stats["state"]["error_rate"] > 0.5:
                unhealthy.append(name)
        return unhealthy


# Context manager for error boundaries
@asynccontextmanager
async def error_boundary(
    name: str,
    config: Optional[BoundaryConfig] = None,
    fallback_handler: Optional[Callable] = None
):
    """Context manager for temporary error boundary"""
    manager = _get_boundary_manager()
    
    # Create temporary boundary
    boundary = manager.create_boundary(name, config, fallback_handler)
    
    try:
        yield boundary
    finally:
        # Cleanup temporary boundary
        manager.remove_boundary(name)


# Decorator for error boundaries
def with_error_boundary(
    name: Optional[str] = None,
    config: Optional[BoundaryConfig] = None,
    fallback_handler: Optional[Callable] = None
):
    """Decorator to wrap function with error boundary"""
    def decorator(func):
        boundary_name = name or f"{func.__module__}.{func.__name__}"
        
        async def async_wrapper(*args, **kwargs):
            manager = _get_boundary_manager()
            boundary = manager.get_boundary(boundary_name)
            
            if not boundary:
                boundary = manager.create_boundary(boundary_name, config, fallback_handler)
            
            async def async_operation():
                return await func(*args, **kwargs)
            
            return await boundary.execute_async(async_operation)
        
        def sync_wrapper(*args, **kwargs):
            manager = _get_boundary_manager()
            boundary = manager.get_boundary(boundary_name)
            
            if not boundary:
                boundary = manager.create_boundary(boundary_name, config, fallback_handler)
            
            def sync_operation():
                return func(*args, **kwargs)
            
            # For sync operations, we can safely use execute since it's not async
            return boundary.execute(sync_operation)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global boundary manager
_global_boundary_manager: Optional[ErrorBoundaryManager] = None


def _get_boundary_manager() -> ErrorBoundaryManager:
    """Get global boundary manager"""
    global _global_boundary_manager
    if _global_boundary_manager is None:
        _global_boundary_manager = ErrorBoundaryManager()
    return _global_boundary_manager


def get_boundary_manager() -> ErrorBoundaryManager:
    """Public interface to get boundary manager"""
    return _get_boundary_manager()