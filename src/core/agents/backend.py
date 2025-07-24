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
    """Lazy import of CrewAI dependencies.
    
    This function implements lazy loading to prevent the 1.6s import cascade
    from CrewAI. It loads dependencies only when actually needed and provides
    mock classes for testing environments.
    
    Returns:
        bool: True if CrewAI is available, False if using mock classes
    """
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
                """Mock Agent class for testing when CrewAI is not available."""
                
                def __init__(self, *args, **kwargs):
                    """Initialize mock agent with basic properties."""
                    self.role = kwargs.get("role", "BackendEngineer")

            class MockTask:
                """Mock Task class for testing when CrewAI is not available."""
                
                def __init__(self, *args, **kwargs):
                    """Initialize mock task."""
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
        """Initialize BackendEngineer.
        
        Args:
            tools: Optional list of tools for the agent to use
            memory_engine: Optional memory engine for context integration
        """
        self.tools = tools or []
        self.memory_engine = memory_engine
        self._agent = None  # Lazy load the agent

    @property
    def agent(self):
        """Lazy-loaded CrewAI agent.
        
        This property implements lazy loading to defer CrewAI import until
        the agent is actually needed, preventing unnecessary startup delays.
        
        Returns:
            Agent: CrewAI Agent instance or mock agent for testing
        """
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
        """Execute a backend engineering task.
        
        This is a placeholder implementation that returns a successful result.
        In production, this would contain actual backend task execution logic.
        
        Args:
            task: Dictionary containing task details with 'id' and other parameters
            
        Returns:
            Dict[str, Any]: Result dictionary with task_id, status, output, and agent fields
        """
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
