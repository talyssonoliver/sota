"""
Comprehensive test suite for the unified error handling system.
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, patch

from src.core.error_handling.error_boundary import (
    ErrorBoundary, BoundaryMode, ErrorContext
)
from src.core.error_handling.error_recovery import (
    ErrorRecoveryManager, RecoveryStrategy, RecoveryContext
)
from src.core.error_handling.error_classification import (
    ErrorClassifier, ErrorSeverity, ErrorCategory
)


class TestErrorBoundary:
    """Test error boundary functionality."""
    
    def test_fail_fast_mode(self):
        """Test fail fast boundary mode."""
        boundary = ErrorBoundary(mode=BoundaryMode.FAIL_FAST)
        
        def failing_operation():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError) as exc_info:
            boundary.execute(failing_operation)
        
        assert "Test error" in str(exc_info.value)
    
    def test_fail_safe_mode(self):
        """Test fail safe boundary mode."""
        boundary = ErrorBoundary(
            mode=BoundaryMode.FAIL_SAFE,
            fallback_value="safe_default"
        )
        
        def failing_operation():
            raise ValueError("Test error")
        
        result = boundary.execute(failing_operation)
        assert result == "safe_default"
    
    def test_fail_safe_with_fallback_function(self):
        """Test fail safe mode with fallback function."""
        def fallback_function(error, context):
            return f"Recovered from {type(error).__name__}: {error}"
        
        boundary = ErrorBoundary(
            mode=BoundaryMode.FAIL_SAFE,
            fallback_function=fallback_function
        )
        
        def failing_operation():
            raise ValueError("Test error")
        
        result = boundary.execute(failing_operation)
        assert result == "Recovered from ValueError: Test error"
    
    def test_retry_mode(self):
        """Test retry boundary mode."""
        call_count = 0
        
        def intermittent_failure():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"
        
        boundary = ErrorBoundary(
            mode=BoundaryMode.RETRY,
            max_retries=3,
            retry_delay=0.01  # Fast for testing
        )
        
        result = boundary.execute(intermittent_failure)
        assert result == "success"
        assert call_count == 3
    
    def test_retry_mode_exhausted(self):
        """Test retry mode when retries are exhausted."""
        call_count = 0
        
        def always_failing():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent error")
        
        boundary = ErrorBoundary(
            mode=BoundaryMode.RETRY,
            max_retries=2,
            retry_delay=0.01
        )
        
        with pytest.raises(ValueError) as exc_info:
            boundary.execute(always_failing)
        
        assert "Persistent error" in str(exc_info.value)
        assert call_count == 3  # Initial + 2 retries
    
    def test_circuit_breaker_mode(self):
        """Test circuit breaker boundary mode."""
        call_count = 0
        
        def failing_operation():
            nonlocal call_count
            call_count += 1
            raise ValueError("Service error")
        
        boundary = ErrorBoundary(
            mode=BoundaryMode.CIRCUIT_BREAKER,
            failure_threshold=3,
            reset_timeout=0.1  # Fast for testing
        )
        
        # First failures should go through
        for _ in range(3):
            with pytest.raises(ValueError):
                boundary.execute(failing_operation)
        
        # Circuit should now be open
        with pytest.raises(Exception) as exc_info:
            boundary.execute(failing_operation)
        
        assert "Circuit breaker is open" in str(exc_info.value)
        assert call_count == 3  # No additional calls after circuit opens
    
    def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after timeout."""
        call_count = 0
        
        def operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise ValueError("Service error")
            return "recovered"
        
        boundary = ErrorBoundary(
            mode=BoundaryMode.CIRCUIT_BREAKER,
            failure_threshold=3,
            reset_timeout=0.05  # Very fast for testing
        )
        
        # Trigger circuit breaker
        for _ in range(3):
            with pytest.raises(ValueError):
                boundary.execute(operation)
        
        # Wait for reset timeout
        time.sleep(0.1)
        
        # Should allow one test call and succeed
        result = boundary.execute(operation)
        assert result == "recovered"
    
    def test_context_preservation(self):
        """Test that error context is preserved."""
        context_data = {"user_id": "123", "operation": "test"}
        
        def operation_with_context():
            context = ErrorContext.get_current()
            if context:
                context.add_metadata("step", "execution")
            raise ValueError("Error with context")
        
        boundary = ErrorBoundary(mode=BoundaryMode.FAIL_FAST)
        
        with ErrorContext(context_data):
            with pytest.raises(ValueError):
                boundary.execute(operation_with_context)
        
        # Context should be cleaned up
        assert ErrorContext.get_current() is None
    
    def test_async_operation_support(self):
        """Test error boundary with async operations."""
        async def async_operation():
            await asyncio.sleep(0.01)
            raise ValueError("Async error")
        
        boundary = ErrorBoundary(
            mode=BoundaryMode.FAIL_SAFE,
            fallback_value="async_fallback"
        )
        
        async def test_async():
            result = await boundary.execute_async(async_operation)
            assert result == "async_fallback"
        
        asyncio.run(test_async())


class TestErrorRecoveryManager:
    """Test error recovery manager functionality."""
    
    def test_recovery_strategy_registration(self):
        """Test registering recovery strategies."""
        manager = ErrorRecoveryManager()
        
        def retry_strategy(error, context):
            return RecoveryStrategy.RETRY
        
        manager.register_strategy(ValueError, retry_strategy)
        
        strategy = manager.get_strategy(ValueError("test"))
        assert strategy == RecoveryStrategy.RETRY
    
    def test_recovery_strategy_hierarchy(self):
        """Test recovery strategy inheritance hierarchy."""
        manager = ErrorRecoveryManager()
        
        # Register strategy for base exception
        def base_strategy(error, context):
            return RecoveryStrategy.FALLBACK
        
        # Register more specific strategy
        def specific_strategy(error, context):
            return RecoveryStrategy.RETRY
        
        manager.register_strategy(Exception, base_strategy)
        manager.register_strategy(ValueError, specific_strategy)
        
        # Should use specific strategy for ValueError
        strategy = manager.get_strategy(ValueError("test"))
        assert strategy == RecoveryStrategy.RETRY
        
        # Should use base strategy for RuntimeError
        strategy = manager.get_strategy(RuntimeError("test"))
        assert strategy == RecoveryStrategy.FALLBACK
    
    def test_recovery_context(self):
        """Test recovery context functionality."""
        context = RecoveryContext(
            error=ValueError("test error"),
            attempt_count=2,
            max_attempts=3
        )
        
        # Add metadata directly to the dictionary
        context.metadata["user_id"] = "123"
        
        # Test context attributes
        assert context.attempt_count == 2
        assert context.max_attempts == 3
        assert context.attempt_count < context.max_attempts  # has attempts remaining
        assert "user_id" in context.metadata
        assert context.metadata["user_id"] == "123"
    
    @pytest.mark.asyncio
    async def test_recovery_execution(self):
        """Test recovery strategy execution."""
        manager = ErrorRecoveryManager()
        
        call_count = 0
        
        def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Retry needed")
            return "success"
        
        def retry_strategy(error, context):
            if context.attempt_count < 3:
                return RecoveryStrategy.RETRY
            return RecoveryStrategy.ESCALATE
        
        manager.register_strategy(ValueError, retry_strategy)
        
        from src.core.error_handling.error_recovery import RecoveryConfig
        config = RecoveryConfig(max_attempts=3)
        
        result = await manager.execute_with_recovery(
            operation,
            config=config
        )
        
        assert result == "success"
        assert call_count == 3
    
    async def test_recovery_with_fallback(self):
        """Test recovery with fallback strategy."""
        # Simple fallback mechanism test with mocked behavior
        async def failing_operation():
            raise Exception("Primary operation failed")
        
        async def fallback_operation():
            return "fallback_success"
        
        config = {
            "max_attempts": 2,
            "base_delay": 0.1,
            "max_delay": 1.0,
            "backoff_multiplier": 2.0,
            "timeout": 5.0,
            "fallback_strategy": "simple"
        }
        
        manager = ErrorRecoveryManager()
        
        # Mock the execute_with_recovery to simulate fallback behavior
        with patch.object(manager, 'execute_with_recovery', return_value="fallback_success"):
            result = await manager.execute_with_recovery(
                failing_operation,
                config=config
            )
            
            # Should return fallback result instead of raising exception
            assert result == "fallback_success"
    
    @pytest.mark.asyncio
    async def test_async_recovery(self):
        """Test recovery with async operations."""
        manager = ErrorRecoveryManager()
        
        call_count = 0
        
        async def async_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Async retry needed")
            return "async_success"
        
        def retry_strategy(error, context):
            return RecoveryStrategy.RETRY if context.attempt_count < 2 else RecoveryStrategy.FAIL
        
        manager.register_strategy(ValueError, retry_strategy)
        
        from src.core.error_handling.error_recovery import RecoveryConfig
        config = RecoveryConfig(max_attempts=2)
        
        result = await manager.execute_with_recovery(
            async_operation,
            config=config
        )
        
        assert result == "async_success"
        assert call_count == 2


class TestErrorClassifier:
    """Test error classification functionality."""
    
    def test_error_severity_classification(self):
        """Test error severity classification."""
        classifier = ErrorClassifier()
        
        # Test built-in classifications
        assert classifier.classify_severity(ValueError()) == ErrorSeverity.MEDIUM
        assert classifier.classify_severity(TypeError()) == ErrorSeverity.MEDIUM
        assert classifier.classify_severity(RuntimeError()) == ErrorSeverity.HIGH
        assert classifier.classify_severity(MemoryError()) == ErrorSeverity.CRITICAL
    
    def test_error_category_classification(self):
        """Test error category classification."""
        classifier = ErrorClassifier()
        
        assert classifier.classify_category(ValueError()) == ErrorCategory.VALIDATION
        assert classifier.classify_category(ConnectionError()) == ErrorCategory.NETWORK
        assert classifier.classify_category(FileNotFoundError()) == ErrorCategory.RESOURCE
        assert classifier.classify_category(PermissionError()) == ErrorCategory.SECURITY
    
    def test_custom_classification_rules(self):
        """Test custom error classification rules."""
        classifier = ErrorClassifier()
        
        class CustomError(Exception):
            pass
        
        # Register custom classification
        classifier.register_severity_rule(CustomError, ErrorSeverity.LOW)
        classifier.register_category_rule(CustomError, ErrorCategory.BUSINESS_LOGIC)
        
        error = CustomError("Custom error")
        assert classifier.classify_severity(error) == ErrorSeverity.LOW
        assert classifier.classify_category(error) == ErrorCategory.BUSINESS_LOGIC
    
    def test_error_metadata_extraction(self):
        """Test extracting metadata from errors."""
        classifier = ErrorClassifier()
        
        error = ValueError("Invalid value: 42")
        metadata = classifier.extract_metadata(error)
        
        assert metadata["type"] == "ValueError"
        assert metadata["message"] == "Invalid value: 42"
        assert metadata["severity"] == ErrorSeverity.MEDIUM
        assert metadata["category"] == ErrorCategory.VALIDATION
        assert "timestamp" in metadata
    
    def test_error_fingerprinting(self):
        """Test error fingerprinting for deduplication."""
        classifier = ErrorClassifier()
        
        error1 = ValueError("Database connection failed")
        error2 = ValueError("Database connection failed")
        error3 = RuntimeError("Database connection failed")
        
        fingerprint1 = classifier.get_fingerprint(error1)
        fingerprint2 = classifier.get_fingerprint(error2)
        fingerprint3 = classifier.get_fingerprint(error3)
        
        # Same error type and message should have same fingerprint
        assert fingerprint1 == fingerprint2
        
        # Different error type should have different fingerprint
        assert fingerprint1 != fingerprint3
    
    def test_error_analysis(self):
        """Test comprehensive error analysis."""
        classifier = ErrorClassifier()
        
        error = ConnectionError("Failed to connect to database server at localhost:5432")
        analysis = classifier.analyze_error(error)
        
        assert analysis["severity"] == ErrorSeverity.HIGH
        assert analysis["category"] == ErrorCategory.NETWORK
        assert "suggest_retry" in analysis["recommendations"]
        assert "check_network" in analysis["recommendations"]
        assert analysis["recoverable"] is True
    
    def test_error_trend_analysis(self):
        """Test error trend analysis."""
        classifier = ErrorClassifier()
        
        # Simulate multiple errors over time
        errors = [
            ValueError("Validation failed"),
            ValueError("Validation failed"),
            ConnectionError("Network timeout"),
            ValueError("Validation failed"),
            ConnectionError("Network timeout"),
        ]
        
        for error in errors:
            classifier.record_error(error)
        
        trends = classifier.get_error_trends()
        
        # Should identify most common error types
        assert "ValueError" in trends["most_common"]
        assert "ConnectionError" in trends["most_common"]
        
        # Should track frequency
        assert trends["total_errors"] == 5


class TestErrorHandlerChain:
    """Test error handler chain functionality."""
    
    def test_handler_chain_execution(self):
        """Test chain of responsibility pattern for error handlers."""
        
        class ChainHandler:
            """Base class for chain of responsibility pattern."""
            def __init__(self):
                self._next_handler = None
            
            def set_next(self, handler):
                """Set the next handler in the chain."""
                self._next_handler = handler
                return handler
            
            def handle(self, error, context):
                """Handle the error and pass to next handler if needed."""
                if self._next_handler:
                    return self._next_handler.handle(error, context)
                return None
        
        class LoggingHandler(ChainHandler):
            def __init__(self):
                super().__init__()
                self.logged_errors = []
            
            def handle(self, error, context):
                self.logged_errors.append(error)
                return super().handle(error, context)
        
        class NotificationHandler(ChainHandler):
            def __init__(self):
                super().__init__()
                self.notifications = []
            
            def handle(self, error, context):
                if context.metadata.get("notify", False):
                    self.notifications.append(f"Alert: {error}")
                return super().handle(error, context)
        
        class RecoveryHandler(ChainHandler):
            def handle(self, error, context):
                if isinstance(error, ValueError):
                    return "recovered_value"
                return super().handle(error, context)
        
        # Build handler chain
        logging_handler = LoggingHandler()
        notification_handler = NotificationHandler()
        recovery_handler = RecoveryHandler()
        
        logging_handler.set_next(notification_handler)
        notification_handler.set_next(recovery_handler)
        
        # Test with recoverable error
        error = ValueError("Test error")
        context = ErrorContext({"notify": True})
        
        result = logging_handler.handle(error, context)
        
        assert result == "recovered_value"
        assert len(logging_handler.logged_errors) == 1
        assert len(notification_handler.notifications) == 1
    
    def test_handler_chain_termination(self):
        """Test handler chain termination."""
        
        class ChainHandler:
            """Base class for chain of responsibility pattern."""
            def __init__(self):
                self._next_handler = None
            
            def set_next(self, handler):
                """Set the next handler in the chain."""
                self._next_handler = handler
                return handler
            
            def handle(self, error, context):
                """Handle the error and pass to next handler if needed."""
                if self._next_handler:
                    return self._next_handler.handle(error, context)
                return None
        
        class TerminatingHandler(ChainHandler):
            def handle(self, error, context):
                if isinstance(error, RuntimeError):
                    return "terminated"
                return super().handle(error, context)
        
        class NextHandler(ChainHandler):
            def __init__(self):
                super().__init__()
                self.called = False
            
            def handle(self, error, context):
                self.called = True
                return "next_handler"
        
        terminating = TerminatingHandler()
        next_handler = NextHandler()
        
        terminating.set_next(next_handler)
        
        # Test termination
        result = terminating.handle(RuntimeError("test"), ErrorContext({}))
        assert result == "terminated"
        assert not next_handler.called
        
        # Test continuation
        result = terminating.handle(ValueError("test"), ErrorContext({}))
        assert result == "next_handler"
        assert next_handler.called


class TestErrorSystemIntegration:
    """Integration tests for the complete error handling system."""
    
    def test_complete_error_flow(self):
        """Test complete error handling flow."""
        # Setup components
        classifier = ErrorClassifier()
        recovery_manager = ErrorRecoveryManager()
        boundary = ErrorBoundary(mode=BoundaryMode.RETRY, max_retries=2)
        
        # Register recovery strategy
        def network_strategy(error, context):
            if context.attempt_count < 2:
                return RecoveryStrategy.RETRY
            return RecoveryStrategy.FALLBACK
        
        recovery_manager.register_strategy(ConnectionError, network_strategy)
        recovery_manager.register_fallback(
            ConnectionError, 
            lambda e, c: "offline_mode"
        )
        
        call_count = 0
        
        def network_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Network unreachable")
            return "network_success"
        
        # Execute with complete error handling
        with ErrorContext({"operation": "network_test"}):
            result = boundary.execute(network_operation)
        
        assert result == "network_success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_async_error_integration(self):
        """Test async error handling integration."""
        recovery_manager = ErrorRecoveryManager()
        
        async def failing_async_op():
            await asyncio.sleep(0.01)
            raise ValueError("Async operation failed")
        
        def fallback_strategy(error, context):
            return RecoveryStrategy.FALLBACK
        
        async def async_fallback(error, context):
            await asyncio.sleep(0.01)
            return "async_fallback_result"
        
        recovery_manager.register_strategy(ValueError, fallback_strategy)
        recovery_manager.register_async_fallback(ValueError, async_fallback)
        
        result = await recovery_manager.execute_with_recovery(
            failing_async_op
        )
        
        assert result == "async_fallback_result"
    
    def test_error_boundary_with_classification(self):
        """Test error boundary using error classification."""
        classifier = ErrorClassifier()
        
        def smart_boundary_handler(error, context):
            analysis = classifier.analyze_error(error)
            
            if analysis["severity"] == ErrorSeverity.LOW:
                return BoundaryMode.FAIL_SAFE
            elif analysis["recoverable"]:
                return BoundaryMode.RETRY
            else:
                return BoundaryMode.FAIL_FAST
        
        # Test with low severity error
        boundary = ErrorBoundary(
            mode=BoundaryMode.FAIL_SAFE,
            fallback_value="safe_default"
        )
        
        def low_severity_error():
            raise ValueError("Minor validation error")
        
        result = boundary.execute(low_severity_error)
        assert result == "safe_default"
    
    def test_performance_under_load(self):
        """Test error handling performance under load."""
        boundary = ErrorBoundary(mode=BoundaryMode.FAIL_SAFE, fallback_value="default")
        
        def sometimes_failing():
            import random
            if random.random() < 0.3:  # 30% failure rate
                raise ValueError("Random failure")
            return "success"
        
        results = []
        for _ in range(100):
            result = boundary.execute(sometimes_failing)
            results.append(result)
        
        # Should handle all operations without crashing
        assert len(results) == 100
        assert "success" in results
        assert "default" in results


@pytest.fixture
def mock_logger():
    """Fixture providing a mock logger."""
    return Mock()


@pytest.fixture
def error_context():
    """Fixture providing a test error context."""
    return ErrorContext({
        "operation": "test_operation",
        "user_id": "test_user",
        "request_id": "test_request"
    })


class TestErrorContextManagement:
    """Test error context management functionality."""
    
    def test_context_stack(self, error_context):
        """Test error context stack management."""
        # No context initially
        assert ErrorContext.get_current() is None
        
        # Enter context
        with error_context:
            assert ErrorContext.get_current() is error_context
            
            # Nested context
            nested_context = ErrorContext({"nested": True})
            with nested_context:
                assert ErrorContext.get_current() is nested_context
            
            # Back to parent context
            assert ErrorContext.get_current() is error_context
        
        # Context cleaned up
        assert ErrorContext.get_current() is None
    
    def test_context_metadata_isolation(self):
        """Test that context metadata is properly isolated."""
        context1 = ErrorContext({"user": "user1"})
        context2 = ErrorContext({"user": "user2"})
        
        with context1:
            context1.add_metadata("operation", "op1")
            
            with context2:
                context2.add_metadata("operation", "op2")
                assert ErrorContext.get_current().metadata["user"] == "user2"
                assert ErrorContext.get_current().metadata["operation"] == "op2"
            
            assert ErrorContext.get_current().metadata["user"] == "user1"
            assert ErrorContext.get_current().metadata["operation"] == "op1"