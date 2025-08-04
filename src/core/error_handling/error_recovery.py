
from src.infrastructure.utils.common_imports import (
    Enum,
    asyncio,
    dataclass,
    datetime,
    field,
    logging,
    timedelta
)
"""
Error Recovery System

Provides intelligent error recovery strategies and mechanisms
to handle different types of system failures gracefully.
"""

# import asyncio  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
from typing import Dict, Any, Optional, List, Callable, TypeVar, Protocol
from abc import ABC, abstractmethod
# from dataclasses import dataclass, field  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
# from datetime import datetime, timedelta  # Consolidated to common_imports

from .error_types import SystemError, ErrorSeverity, ErrorCategory

T = TypeVar('T')


class RecoveryStrategy(Enum):
    """Error recovery strategies"""
    RETRY = "retry"
    FAILOVER = "failover" 
    CIRCUIT_BREAKER = "circuit_breaker"
    FALLBACK = "fallback"
    IGNORE = "ignore"
    ESCALATE = "escalate"


class RecoveryResult(Enum):
    """Recovery attempt results"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    RETRY_NEEDED = "retry_needed"
    ESCALATION_NEEDED = "escalation_needed"


@dataclass
class RecoveryContext:
    """Context for error recovery operations"""
    error: Exception
    attempt_count: int = 0
    max_attempts: int = 3
    last_attempt_time: Optional[datetime] = None
    recovery_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class RecoveryConfig:
    """Configuration for error recovery"""
    strategy: RecoveryStrategy = RecoveryStrategy.RETRY
    max_attempts: int = 3
    backoff_multiplier: float = 2.0
    max_backoff_seconds: float = 60.0
    timeout_seconds: float = 30.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    fallback_enabled: bool = True
    escalation_threshold: int = 10


class IErrorRecoveryStrategy(Protocol):
    """Interface for error recovery strategies"""
    
    async def can_recover(self, error: Exception, context: RecoveryContext) -> bool:
        """Check if this strategy can recover from the error"""
        ...
    
    async def recover(self, error: Exception, context: RecoveryContext) -> RecoveryResult:
        """Attempt to recover from the error"""
        ...
    
    async def get_backoff_delay(self, attempt_count: int, config: RecoveryConfig) -> float:
        """Calculate backoff delay for retry attempts"""
        ...


class RetryRecoveryStrategy:
    """Retry-based error recovery strategy"""
    
    def __init__(self, config: Optional[RecoveryConfig] = None):
        self.config = config or RecoveryConfig()
        self.logger = logging.getLogger(__name__)
    
    async def can_recover(self, error: Exception, context: RecoveryContext) -> bool:
        """Check if error is retryable"""
        # Retryable error types
        retryable_types = (
            ConnectionError,
            TimeoutError,
            OSError,
        )
        
        # Check if it's a retryable SystemError
        if isinstance(error, SystemError):
            return error.recoverable and error.category in [
                ErrorCategory.NETWORK,
                ErrorCategory.EXTERNAL_SERVICE,
                ErrorCategory.RESOURCE
            ]
        
        return isinstance(error, retryable_types)
    
    async def recover(self, error: Exception, context: RecoveryContext) -> RecoveryResult:
        """Attempt recovery through retry"""
        if context.attempt_count >= self.config.max_attempts:
            self.logger.warning(f"Max retry attempts ({self.config.max_attempts}) exceeded for {type(error).__name__}")
            return RecoveryResult.ESCALATION_NEEDED
        
        # Calculate backoff delay
        delay = await self.get_backoff_delay(context.attempt_count, self.config)
        
        self.logger.info(f"Retrying operation in {delay:.2f}s (attempt {context.attempt_count + 1}/{self.config.max_attempts})")
        
        if delay > 0:
            await asyncio.sleep(delay)
        
        return RecoveryResult.RETRY_NEEDED
    
    async def get_backoff_delay(self, attempt_count: int, config: RecoveryConfig) -> float:
        """Calculate exponential backoff delay"""
        if attempt_count == 0:
            return 0
        
        delay = min(
            config.backoff_multiplier ** (attempt_count - 1),
            config.max_backoff_seconds
        )
        return delay


class FallbackRecoveryStrategy:
    """Fallback-based error recovery strategy"""
    
    def __init__(self, fallback_handler: Optional[Callable] = None):
        self.fallback_handler = fallback_handler
        self.logger = logging.getLogger(__name__)
    
    async def can_recover(self, error: Exception, context: RecoveryContext) -> bool:
        """Check if fallback is available"""
        return self.fallback_handler is not None
    
    async def recover(self, error: Exception, context: RecoveryContext) -> RecoveryResult:
        """Attempt recovery using fallback"""
        if not self.fallback_handler:
            return RecoveryResult.FAILURE
        
        try:
            self.logger.info(f"Executing fallback handler for {type(error).__name__}")
            
            # Execute fallback handler
            if asyncio.iscoroutinefunction(self.fallback_handler):
                result = await self.fallback_handler(error, context)
            else:
                result = self.fallback_handler(error, context)
            
            # Store fallback result in context
            context.recovery_data["fallback_result"] = result
            
            return RecoveryResult.PARTIAL_SUCCESS
            
        except Exception as fallback_error:
            self.logger.error(f"Fallback handler failed: {fallback_error}")
            return RecoveryResult.FAILURE


class CircuitBreakerRecoveryStrategy:
    """Circuit breaker error recovery strategy"""
    
    def __init__(self, config: Optional[RecoveryConfig] = None):
        self.config = config or RecoveryConfig()
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.circuit_open = False
        self.logger = logging.getLogger(__name__)
    
    async def can_recover(self, error: Exception, context: RecoveryContext) -> bool:
        """Check if circuit breaker should handle this error"""
        return not self.circuit_open
    
    async def recover(self, error: Exception, context: RecoveryContext) -> RecoveryResult:
        """Manage circuit breaker state"""
        current_time = datetime.now()
        
        # Check if circuit should be reset
        if (self.circuit_open and 
            self.last_failure_time and 
            current_time - self.last_failure_time > timedelta(seconds=self.config.circuit_breaker_timeout)):
            
            self.logger.info("Circuit breaker timeout elapsed, attempting reset")
            self.circuit_open = False
            self.failure_count = 0
        
        # If circuit is open, reject immediately
        if self.circuit_open:
            self.logger.warning("Circuit breaker is open, rejecting request")
            return RecoveryResult.FAILURE
        
        # Record failure
        self.failure_count += 1
        self.last_failure_time = current_time
        
        # Check if circuit should open
        if self.failure_count >= self.config.circuit_breaker_threshold:
            self.circuit_open = True
            self.logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
            return RecoveryResult.FAILURE
        
        return RecoveryResult.RETRY_NEEDED


class ErrorRecoveryManager:
    """Manages error recovery strategies and execution"""
    
    def __init__(self):
        self.strategies: Dict[RecoveryStrategy, IErrorRecoveryStrategy] = {}
        self.exception_strategies: Dict[type, Callable] = {}  # For exception-specific strategies
        self.exception_fallbacks: Dict[type, Callable] = {}  # For exception-specific fallback handlers
        self.recovery_stats: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        self._setup_default_strategies()
    
    def _setup_default_strategies(self):
        """Setup default recovery strategies"""
        self.strategies[RecoveryStrategy.RETRY] = RetryRecoveryStrategy()
        self.strategies[RecoveryStrategy.FALLBACK] = FallbackRecoveryStrategy()
        self.strategies[RecoveryStrategy.CIRCUIT_BREAKER] = CircuitBreakerRecoveryStrategy()
    
    def register_strategy(self, strategy_type, strategy):
        """Register a custom recovery strategy"""
        if isinstance(strategy_type, type) and issubclass(strategy_type, Exception):
            # Register strategy for specific exception type
            self.exception_strategies[strategy_type] = strategy
            self.logger.debug(f"Registered recovery strategy for exception: {strategy_type.__name__}")
        elif isinstance(strategy_type, RecoveryStrategy):
            # Register strategy for recovery strategy enum
            self.strategies[strategy_type] = strategy
            self.logger.debug(f"Registered recovery strategy: {strategy_type.value}")
        else:
            raise ValueError(f"Invalid strategy type: {strategy_type}. Must be RecoveryStrategy enum or Exception type.")
    
    def set_fallback_handler(self, handler: Callable):
        """Set fallback handler for fallback strategy"""
        if RecoveryStrategy.FALLBACK in self.strategies:
            fallback_strategy = self.strategies[RecoveryStrategy.FALLBACK]
            if hasattr(fallback_strategy, 'fallback_handler'):
                fallback_strategy.fallback_handler = handler
    
    def register_fallback(self, exception_type: type, fallback_handler: Callable):
        """Register a fallback handler for a specific exception type"""
        # Store the exception-specific fallback handler
        self.exception_fallbacks[exception_type] = fallback_handler
        
        # Create a strategy function that returns FALLBACK
        def fallback_strategy(error, context):
            return RecoveryStrategy.FALLBACK
        
        # Register the strategy
        self.register_strategy(exception_type, fallback_strategy)
    
    def register_async_fallback(self, exception_type: type, async_fallback_handler: Callable):
        """Register an async fallback handler for a specific exception type"""
        # Store the exception-specific fallback handler
        self.exception_fallbacks[exception_type] = async_fallback_handler
        
        # Create a strategy function that returns FALLBACK
        def async_fallback_strategy(error, context):
            return RecoveryStrategy.FALLBACK
        
        # Register the strategy
        self.register_strategy(exception_type, async_fallback_strategy)
    
    async def attempt_recovery(self, error: Exception, 
                              config: Optional[RecoveryConfig] = None) -> RecoveryResult:
        """Attempt to recover from an error using configured strategies"""
        recovery_config = config or RecoveryConfig()
        context = RecoveryContext(error=error, max_attempts=recovery_config.max_attempts)
        
        # Track recovery attempt
        error_type = type(error).__name__
        if error_type not in self.recovery_stats:
            self.recovery_stats[error_type] = {
                "attempts": 0,
                "successes": 0,
                "failures": 0,
                "last_attempt": None
            }
        
        stats = self.recovery_stats[error_type]
        stats["attempts"] += 1
        stats["last_attempt"] = datetime.now().isoformat()
        
        # Get strategy for this recovery type
        strategy = self.strategies.get(recovery_config.strategy)
        if not strategy:
            self.logger.error(f"No strategy found for {recovery_config.strategy}")
            stats["failures"] += 1
            return RecoveryResult.FAILURE
        
        try:
            # Check if strategy can handle this error
            if not await strategy.can_recover(error, context):
                self.logger.debug(f"Strategy {recovery_config.strategy} cannot recover from {error_type}")
                stats["failures"] += 1
                return RecoveryResult.FAILURE
            
            # Attempt recovery
            result = await strategy.recover(error, context)
            
            if result == RecoveryResult.SUCCESS:
                stats["successes"] += 1
            elif result in [RecoveryResult.FAILURE, RecoveryResult.ESCALATION_NEEDED]:
                stats["failures"] += 1
            
            return result
            
        except Exception as recovery_error:
            self.logger.error(f"Recovery strategy failed: {recovery_error}")
            stats["failures"] += 1
            return RecoveryResult.FAILURE
    
    async def execute_with_recovery(self, operation: Callable[[], T], 
                                   config: Optional[RecoveryConfig] = None) -> T:
        """Execute an operation with automatic error recovery"""
        recovery_config = config or RecoveryConfig()
        context = RecoveryContext(error=None, max_attempts=recovery_config.max_attempts)
        
        for attempt in range(recovery_config.max_attempts):
            context.attempt_count = attempt
            context.last_attempt_time = datetime.now()
            
            try:
                # Execute the operation
                if asyncio.iscoroutinefunction(operation):
                    result = await operation()
                else:
                    result = operation()
                
                return result
                
            except Exception as error:
                context.error = error
                self.logger.warning(f"Operation failed (attempt {attempt + 1}/{recovery_config.max_attempts}): {error}")
                
                # Check for exception-specific strategy first
                exception_type = type(error)
                if exception_type in self.exception_strategies:
                    strategy_func = self.exception_strategies[exception_type]
                    try:
                        strategy_result = strategy_func(error, context)
                        if strategy_result == RecoveryStrategy.RETRY and context.attempt_count + 1 < recovery_config.max_attempts:
                            continue
                        elif strategy_result == RecoveryStrategy.FALLBACK:
                            # Check for exception-specific fallback handler
                            if exception_type in self.exception_fallbacks:
                                fallback_handler = self.exception_fallbacks[exception_type]
                                try:
                                    if asyncio.iscoroutinefunction(fallback_handler):
                                        fallback_result = await fallback_handler(error, context)
                                    else:
                                        fallback_result = fallback_handler(error, context)
                                    return fallback_result
                                except Exception as fallback_error:
                                    self.logger.error(f"Exception-specific fallback failed: {fallback_error}")
                        elif strategy_result == RecoveryStrategy.ESCALATE:
                            raise error
                    except Exception as strategy_error:
                        self.logger.error(f"Exception-specific strategy failed: {strategy_error}")
                
                # Fall back to default recovery mechanism
                recovery_result = await self.attempt_recovery(error, recovery_config)
                
                if recovery_result == RecoveryResult.SUCCESS:
                    # Retry the operation
                    continue
                elif recovery_result == RecoveryResult.PARTIAL_SUCCESS:
                    # Return fallback result if available
                    if "fallback_result" in context.recovery_data:
                        return context.recovery_data["fallback_result"]
                elif recovery_result == RecoveryResult.RETRY_NEEDED:
                    # Continue to next attempt
                    continue
                elif recovery_result in [RecoveryResult.FAILURE, RecoveryResult.ESCALATION_NEEDED]:
                    # Re-raise the original error
                    raise error
        
        # If we've exhausted all attempts, raise the last error
        if context.error:
            raise context.error
        else:
            raise RuntimeError("Operation failed without error context")
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        return {
            "strategies": list(self.strategies.keys()),
            "error_stats": self.recovery_stats.copy(),
            "total_attempts": sum(stats["attempts"] for stats in self.recovery_stats.values()),
            "total_successes": sum(stats["successes"] for stats in self.recovery_stats.values()),
            "total_failures": sum(stats["failures"] for stats in self.recovery_stats.values())
        }
    
    def reset_stats(self):
        """Reset recovery statistics"""
        self.recovery_stats.clear()
    
    def get_strategy(self, error: Exception) -> RecoveryStrategy:
        """Get the appropriate recovery strategy for an error.
        
        Args:
            error: The exception to get strategy for
            
        Returns:
            RecoveryStrategy: The strategy to use for this error type
        """
        error_type = type(error)
        
        # Check for exact match first
        if error_type in self.exception_strategies:
            strategy_func = self.exception_strategies[error_type]
            context = RecoveryContext(error=error)
            return strategy_func(error, context)
        
        # Check inheritance hierarchy
        for exc_type, strategy_func in self.exception_strategies.items():
            if isinstance(error, exc_type):
                context = RecoveryContext(error=error)
                return strategy_func(error, context)
        
        # Return default strategy if no specific strategy found
        return RecoveryStrategy.RETRY


# Global error recovery manager
_global_recovery_manager: Optional[ErrorRecoveryManager] = None


def get_error_recovery_manager() -> ErrorRecoveryManager:
    """Get global error recovery manager"""
    global _global_recovery_manager
    if _global_recovery_manager is None:
        _global_recovery_manager = ErrorRecoveryManager()
    return _global_recovery_manager


# Convenience decorator for automatic recovery
def with_error_recovery(config: Optional[RecoveryConfig] = None):
    """Decorator to add automatic error recovery to functions"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        async def async_wrapper(*args, **kwargs) -> T:
            manager = get_error_recovery_manager()
            return await manager.execute_with_recovery(
                lambda: func(*args, **kwargs),
                config
            )
        
        def sync_wrapper(*args, **kwargs) -> T:
            manager = get_error_recovery_manager()
            return asyncio.run(manager.execute_with_recovery(
                lambda: func(*args, **kwargs),
                config
            ))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator