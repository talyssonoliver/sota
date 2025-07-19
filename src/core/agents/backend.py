"""
Backend Engineer Agent for implementing Supabase services and API routes.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from src.infrastructure.memory import MemoryEngine

# Defer CrewAI import until actually needed to avoid 1.6s import cascade
Agent = None
Task = None
_CREWAI_AVAILABLE = None


def _import_crewai():
    """Lazy import of CrewAI dependencies."""
    global Agent, Task, _CREWAI_AVAILABLE

    if _CREWAI_AVAILABLE is None:
        try:
            from crewai import Agent as _Agent
            from crewai import Task as _Task

            Agent = _Agent
            Task = _Task
            _CREWAI_AVAILABLE = True
            logger.info("CrewAI dependencies loaded successfully")
        except ImportError:
            # Mock classes for testing
            class MockAgent:
                def __init__(self, *args, **kwargs):
                    self.role = kwargs.get("role", "BackendEngineer")

            class MockTask:
                def __init__(self, *args, **kwargs):
                    pass

            Agent = MockAgent
            Task = MockTask
            _CREWAI_AVAILABLE = False
            logger.warning("CrewAI not available, using mock classes")

    return _CREWAI_AVAILABLE


logger = logging.getLogger(__name__)


class BackendEngineer:
    """Backend Engineer Agent agent."""

    def __init__(
        self,
        tools: Optional[List] = None,
        memory_engine: Optional["MemoryEngine"] = None,
    ):
        """Initialize BackendEngineer."""
        self.tools = tools or []
        self.memory_engine = memory_engine
        self._agent = None  # Lazy load the agent

    @property
    def agent(self):
        """Lazy-loaded CrewAI agent."""
        if self._agent is None:
            _import_crewai()  # Load CrewAI dependencies only when needed
            self._agent = Agent(
                role="Backend Engineer",
                goal=(
                    "Backend Engineer Agent for implementing Supabase services "
                    "and API routes"
                ),
                backstory="Expert backend engineer with deep knowledge and expertise",
                verbose=True,
                allow_delegation=False,
                tools=self.tools,
            )
        return self._agent

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task."""
        logger.info(f"Executing task: {task.get('id', 'unknown')}")

        result = {
            "task_id": task.get("id", "unknown"),
            "status": "completed",
            "output": "BackendEngineer task completed successfully",
            "agent": "BackendEngineer",
        }

        return result


# Export the class
__all__ = ["BackendEngineer"]
