
from src.infrastructure.utils.common_imports import logging
"""
Documentation Writer Agent for creating technical documentation.
"""

# import logging  # Consolidated to common_imports
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

if TYPE_CHECKING:
    from src.infrastructure.memory import MemoryEngine

logger = logging.getLogger(__name__)

# Lazy import globals - will be set to actual class or mock
_agent_class = None
_crewai_available = None


def _get_agent_class() -> Type[Any]:
    """Lazy import of CrewAI Agent class to avoid loading heavy dependencies on module import.
    
    This function implements lazy loading to prevent the 1.6s import cascade
    from CrewAI. It loads the Agent class only when actually needed and provides
    a mock class for testing environments.
    
    Returns:
        Type[Any]: CrewAI Agent class or MockAgent class for testing
    """
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
                """Mock Agent class for testing when CrewAI is not available."""
                
                def __init__(self, *args, **kwargs):
                    """Initialize mock agent with basic properties.
                    
                    Args:
                        *args: Positional arguments (ignored)
                        **kwargs: Keyword arguments to configure the mock agent
                    """
                    self.role = kwargs.get("role", "DocumentationWriter")
                    self.goal = kwargs.get("goal", "")
                    self.backstory = kwargs.get("backstory", "")
                    self.verbose = kwargs.get("verbose", True)
                    self.allow_delegation = kwargs.get("allow_delegation", False)
                    self.tools = kwargs.get("tools", [])

            _agent_class = MockAgent
            _crewai_available = False

    return _agent_class  # type: ignore


class DocumentationWriter:
    """Documentation Writer Agent agent."""

    def __init__(
        self,
        tools: Optional[List] = None,
        memory_engine: Optional["MemoryEngine"] = None,
    ):
        """Initialize DocumentationWriter.
        
        Args:
            tools: Optional list of tools for the agent to use
            memory_engine: Optional memory engine for context integration
        """
        self.tools = tools or []
        self.memory_engine = memory_engine
        self._agent = None  # Lazy-loaded

    @property
    def agent(self) -> Any:
        """Get the agent instance, loading CrewAI only when needed.
        
        This property implements lazy loading to defer CrewAI import until
        the agent is actually needed, preventing unnecessary startup delays.
        
        Returns:
            Any: CrewAI Agent instance or mock agent for testing
        """
        if self._agent is None:
            agent_class = _get_agent_class()

            # Agent configuration
            self._agent = agent_class(
                role="Documentation Writer",
                goal="Documentation Writer Agent for creating technical documentation",
                backstory="Expert documentation writer with deep knowledge and expertise",
                verbose=True,
                allow_delegation=False,
                tools=self.tools,
            )
        return self._agent

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a documentation writing task.
        
        This is a placeholder implementation that returns a successful result.
        In production, this would contain actual documentation generation logic.
        
        Args:
            task: Dictionary containing task details with 'id' and other parameters
            
        Returns:
            Dict[str, Any]: Result dictionary with task_id, status, output, and agent fields
        """
        logger.info(f"Executing task: {task.get('id', 'unknown')}")

        result = {
            "task_id": task.get("id", "unknown"),
            "status": "completed",
            "output": "DocumentationWriter task completed successfully",
            "agent": "DocumentationWriter",
        }

        return result


# Export the class
__all__ = ["DocumentationWriter"]
