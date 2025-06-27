"""Test integration for execution monitor."""
try:
    import pytest
except ImportError:
    pass
from src.infrastructure.utils.execution_monitor import ExecutionMonitor, DashboardLogger, CrewAIExecutionHook, LangGraphHook

class TestExecutionMonitorIntegration:
    """Integration tests for execution monitor."""

    def test_execution_monitor_creation(self):
        """Test execution monitor can be created."""
        monitor = ExecutionMonitor()
        assert monitor is not None
        assert hasattr(monitor, 'executions')

    def test_dashboard_logger_creation(self):
        """Test dashboard logger can be created."""
        logger = DashboardLogger()
        assert logger is not None
        assert hasattr(logger, 'dashboard_dir')

    def test_crewai_execution_hook_creation(self):
        """Test CrewAI execution hook can be created."""
        hook = CrewAIExecutionHook('test-task')
        assert hook is not None
        assert hook.task_id == 'test-task'

    def test_langgraph_hook_creation(self):
        """Test LangGraph hook can be created."""
        hook = LangGraphHook('test-task')
        assert hook is not None
        assert hook.task_id == 'test-task'
CrewAIExecutionHook = CrewAIExecutionHook
__all__ = ['TestExecutionMonitorIntegration', 'CrewAIExecutionHook']