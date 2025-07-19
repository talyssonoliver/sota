"""
Coordinator Agent for managing and coordinating tasks.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

if TYPE_CHECKING:
    from src.infrastructure.memory import MemoryEngine

logger = logging.getLogger(__name__)

# Lazy import globals - will be set to actual classes or mocks
_agent_class = None
_crewai_available = None


def _get_agent_class() -> Type[Any]:
    """Lazy import of CrewAI Agent class to avoid loading heavy dependencies on module import."""
    global _agent_class, _crewai_available

    if _crewai_available is None:
        try:
            from crewai import Agent

            _agent_class = Agent
            _crewai_available = True
            logger.debug("CrewAI successfully imported")
        except ImportError:
            logger.warning("CrewAI not available, using mock class")

            # Mock class for testing
            class MockAgent:
                def __init__(self, *args, **kwargs):
                    self.role = kwargs.get("role", "Coordinator")
                    self.goal = kwargs.get("goal", "")
                    self.backstory = kwargs.get("backstory", "")
                    self.verbose = kwargs.get("verbose", True)
                    self.allow_delegation = kwargs.get("allow_delegation", False)
                    self.tools = kwargs.get("tools", [])

            _agent_class = MockAgent
            _crewai_available = False

    return _agent_class  # type: ignore


class Coordinator:
    """Coordinator Agent agent."""

    def __init__(
        self,
        tools: Optional[List[Any]] = None,
        memory_engine: Optional["MemoryEngine"] = None,
    ):
        """Initialize Coordinator."""
        self.tools = tools or []
        self.memory_engine = memory_engine
        self._agent: Optional[Any] = None  # Lazy-loaded agent instance

    @property
    def agent(self) -> Any:
        """Get the agent instance, loading CrewAI only when needed."""
        if self._agent is None:
            agent_class = _get_agent_class()

            # Agent configuration
            self._agent = agent_class(
                role="Coordinator",
                goal="Coordinator Agent for managing and coordinating tasks",
                backstory="Expert coordinator with deep knowledge and expertise",
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
            "output": "Coordinator task completed successfully",
            "agent": "Coordinator",
        }

        return result


# Export the class
__all__ = ["Coordinator"]
