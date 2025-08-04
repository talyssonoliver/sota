"""
Tests for Error Boundary System

Tests the error boundary implementation for cascade failure prevention
and proper error isolation.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.core.error_handling import (
    ErrorBoundary, BoundaryConfig, BoundaryMode,
    ErrorBoundaryManager, with_error_boundary,
    SystemError, ErrorSeverity, ErrorCategory
)


class TestErrorBoundary:
    """Test suite for ErrorBoundary"""
    
    def setup_method(self):
        """Setup test environment"""
        # Reset global manager
        import src.core.error_handling.error_boundary as eb_module
        eb_module._global_boundary_manager = None
    
    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """Test successful operation execution"""
        boundary = ErrorBoundary("test")
        
        async def success_operation():
            return "success"
        
        result = await boundary.execute_async(success_operation)
        assert result == "success"
        
        stats = boundary.get_stats()
        assert stats["state"]["success_count"] == 1
        assert stats["state"]["failure_count"] == 0
    
    @pytest.mark.asyncio
    async def test_fail_fast_mode(self):
        """Test fail fast mode behavior"""
        config = BoundaryConfig(mode=BoundaryMode.FAIL_FAST)
        boundary = ErrorBoundary("test", config)
        
        async def failing_operation():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await boundary.execute_async(failing_operation)
        
        stats = boundary.get_stats()
        assert stats["state"]["failure_count"] == 1
    
    @pytest.mark.asyncio
    async def test_fail_safe_mode_with_fallback(self):
        """Test fail safe mode with fallback handler"""
        config = BoundaryConfig(mode=BoundaryMode.FAIL_SAFE)
        
        def fallback_handler(error):
            return "fallback_result"
        
        boundary = ErrorBoundary("test", config, fallback_handler)
        
        async def failing_operation():
            raise ValueError("Test error")
        
        result = await boundary.execute_async(failing_operation)
        assert result == "fallback_result"
    
    @pytest.mark.asyncio
    async def test_fail_safe_mode_without_fallback(self):
        """Test fail safe mode without fallback handler"""
        config = BoundaryConfig(mode=BoundaryMode.FAIL_SAFE)
        boundary = ErrorBoundary("test", config)
        
        async def failing_operation():
            raise ValueError("Test error")
        
        result = await boundary.execute_async(failing_operation)
        assert result is None  # Default fail safe behavior
    
    @pytest.mark.asyncio
    async def test_retry_mode_success_after_retry(self):
        """Test retry mode with eventual success"""
        config = BoundaryConfig(mode=BoundaryMode.RETRY, max_retries=2)
        boundary = ErrorBoundary("test", config)
        
        call_count = 0
        
        async def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = await boundary.execute_async(failing_then_success)
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_mode_max_retries_exceeded(self):
        """Test retry mode when max retries exceeded"""
        config = BoundaryConfig(mode=BoundaryMode.RETRY, max_retries=1)
        boundary = ErrorBoundary("test", config)
        
        async def always_failing():
            raise ConnectionError("Persistent failure")
        
        with pytest.raises(ConnectionError):
            await boundary.execute_async(always_failing)
        
        stats = boundary.get_stats()
        assert stats["state"]["failure_count"] == 1
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_mode(self):
        """Test circuit breaker mode"""
        config = BoundaryConfig(
            mode=BoundaryMode.CIRCUIT_BREAKER,
            circuit_breaker_threshold=2
        )
        boundary = ErrorBoundary("test", config)
        
        async def failing_operation():
            raise ConnectionError("Service down")
        
        # First failure
        with pytest.raises(ConnectionError):
            await boundary.execute_async(failing_operation)
        
        # Second failure - should open circuit
        with pytest.raises(ConnectionError):
            await boundary.execute_async(failing_operation)
        
        # Third attempt - circuit should be open
        with pytest.raises(Exception) as exc_info:
            await boundary.execute_async(failing_operation)
        
        assert "Circuit breaker is open" in str(exc_info.value)
        assert not await boundary.can_execute()
    
    @pytest.mark.asyncio
    async def test_custom_error_classifier(self):
        """Test custom error classifier"""
        def error_classifier(error):
            # Only handle ConnectionError as boundary error
            return isinstance(error, ConnectionError)
        
        boundary = ErrorBoundary("test", error_classifier=error_classifier)
        
        # ValueError should not be handled by boundary
        async def value_error_operation():
            raise ValueError("Not a boundary error")
        
        with pytest.raises(ValueError):
            await boundary.execute_async(value_error_operation)
        
        # ConnectionError should be handled
        async def connection_error_operation():
            raise ConnectionError("Boundary error")
        
        result = await boundary.execute_async(connection_error_operation)
        assert result is None  # Fail safe default
    
    @pytest.mark.asyncio
    async def test_boundary_reset(self):
        """Test boundary state reset"""
        boundary = ErrorBoundary("test")
        
        # Generate some failures
        async def failing_operation():
            raise ValueError("Test error")
        
        try:
            await boundary.execute_async(failing_operation)
        except:
            pass
        
        assert boundary.get_stats()["state"]["failure_count"] == 1
        
        # Reset boundary
        await boundary.reset()
        assert boundary.get_stats()["state"]["failure_count"] == 0
    
    def test_sync_operation(self):
        """Test boundary with synchronous operation"""
        boundary = ErrorBoundary("test")
        
        def sync_operation():
            return "sync_result"
        
        # This should work directly for sync operations
        result = boundary.execute(sync_operation)
        assert result == "sync_result"


class TestErrorBoundaryManager:
    """Test suite for ErrorBoundaryManager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.manager = ErrorBoundaryManager()
    
    def test_create_boundary(self):
        """Test boundary creation"""
        config = BoundaryConfig(mode=BoundaryMode.RETRY)
        boundary = self.manager.create_boundary("test_boundary", config)
        
        assert boundary.name == "test_boundary"
        assert "test_boundary" in self.manager.list_boundaries()
    
    def test_duplicate_boundary_creation(self):
        """Test error on duplicate boundary creation"""
        self.manager.create_boundary("test_boundary")
        
        with pytest.raises(ValueError):
            self.manager.create_boundary("test_boundary")
    
    def test_get_boundary(self):
        """Test boundary retrieval"""
        boundary = self.manager.create_boundary("test_boundary")
        retrieved = self.manager.get_boundary("test_boundary")
        
        assert retrieved is boundary
        assert self.manager.get_boundary("nonexistent") is None
    
    def test_remove_boundary(self):
        """Test boundary removal"""
        self.manager.create_boundary("test_boundary")
        assert "test_boundary" in self.manager.list_boundaries()
        
        result = self.manager.remove_boundary("test_boundary")
        assert result is True
        assert "test_boundary" not in self.manager.list_boundaries()
        
        # Try to remove nonexistent boundary
        result = self.manager.remove_boundary("nonexistent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_reset_all_boundaries(self):
        """Test resetting all boundaries"""
        # Create multiple boundaries with some failures
        boundary1 = self.manager.create_boundary("boundary1")
        boundary2 = self.manager.create_boundary("boundary2")
        
        # Generate failures
        async def failing_op():
            raise ValueError("Test")
        
        try:
            await boundary1.execute_async(failing_op)
        except:
            pass
        try:
            await boundary2.execute_async(failing_op)
        except:
            pass
        
        # Reset all
        count = await self.manager.reset_all_boundaries()
        assert count == 2
        
        # Verify reset
        assert boundary1.get_stats()["state"]["failure_count"] == 0
        assert boundary2.get_stats()["state"]["failure_count"] == 0
    
    def test_get_all_stats(self):
        """Test getting all boundary statistics"""
        self.manager.create_boundary("boundary1")
        self.manager.create_boundary("boundary2")
        
        all_stats = self.manager.get_all_stats()
        assert "boundary1" in all_stats
        assert "boundary2" in all_stats
        assert len(all_stats) == 2
    
    @pytest.mark.asyncio
    async def test_get_unhealthy_boundaries(self):
        """Test identifying unhealthy boundaries"""
        # Create healthy boundary
        healthy = self.manager.create_boundary("healthy")
        
        # Create unhealthy boundary (circuit breaker)
        config = BoundaryConfig(mode=BoundaryMode.CIRCUIT_BREAKER, circuit_breaker_threshold=1)
        unhealthy = self.manager.create_boundary("unhealthy", config)
        
        # Make unhealthy boundary fail and open circuit
        async def failing_op():
            raise ConnectionError("Fail")
        
        try:
            await unhealthy.execute_async(failing_op)
        except:
            pass
        
        unhealthy_list = self.manager.get_unhealthy_boundaries()
        assert "unhealthy" in unhealthy_list
        assert "healthy" not in unhealthy_list


class TestErrorBoundaryDecorator:
    """Test suite for error boundary decorator"""
    
    @pytest.mark.asyncio
    async def test_async_function_decorator(self):
        """Test decorator with async function"""
        @with_error_boundary("test_async")
        async def test_function():
            return "success"
        
        result = await test_function()
        assert result == "success"
    
    def test_sync_function_decorator(self):
        """Test decorator with sync function"""
        @with_error_boundary("test_sync")
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_decorator_with_config(self):
        """Test decorator with custom config"""
        config = BoundaryConfig(mode=BoundaryMode.FAIL_SAFE)
        
        @with_error_boundary("test_config", config=config)
        async def failing_function():
            raise ValueError("Test error")
        
        result = await failing_function()
        assert result is None  # Fail safe default
    
    @pytest.mark.asyncio
    async def test_decorator_with_fallback(self):
        """Test decorator with fallback handler"""
        def fallback(error):
            return "fallback"
        
        @with_error_boundary("test_fallback", fallback_handler=fallback)
        async def failing_function():
            raise ValueError("Test error")
        
        result = await failing_function()
        assert result == "fallback"


class TestErrorBoundaryIntegration:
    """Integration tests for error boundary system"""
    
    @pytest.mark.asyncio
    async def test_nested_boundaries(self):
        """Test nested error boundaries"""
        outer_boundary = ErrorBoundary("outer")
        inner_boundary = ErrorBoundary("inner")
        
        async def inner_operation():
            raise ValueError("Inner error")
        
        async def outer_operation():
            return await inner_boundary.execute_async(inner_operation)
        
        result = await outer_boundary.execute_async(outer_operation)
        assert result is None  # Inner boundary should handle error
    
    @pytest.mark.asyncio
    async def test_boundary_with_real_system_error(self):
        """Test boundary with SystemError"""
        boundary = ErrorBoundary("system_test")
        
        async def system_error_operation():
            raise SystemError(
                "System failure",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.OPERATION,
                recoverable=True
            )
        
        result = await boundary.execute_async(system_error_operation)
        assert result is None  # Should be handled as boundary error
    
    @pytest.mark.asyncio
    async def test_boundary_metrics_collection(self):
        """Test boundary metrics collection"""
        config = BoundaryConfig(metrics_enabled=True)
        boundary = ErrorBoundary("metrics_test", config)
        
        # Execute successful operation
        await boundary.execute_async(lambda: "success")
        
        # Execute failing operation
        try:
            await boundary.execute_async(lambda: (_ for _ in ()).throw(ValueError("fail")))
        except ValueError:
            pass
        
        stats = boundary.get_stats()
        assert stats["state"]["total_executions"] == 2
        assert stats["state"]["success_count"] == 1
        assert stats["state"]["failure_count"] == 1
        assert stats["state"]["error_rate"] == 0.5