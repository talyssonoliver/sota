"""
Technical Lead Agent for architecture and technical oversight.
"""

import logging
from typing import Dict, Any, List, Optional

from tools import memory

try:
    from crewai import Agent, Task
except ImportError:
    # Mock classes for testing
    class Agent:
        def __init__(self, *args, **kwargs):
            self.role = kwargs.get('role', 'TechnicalLead')
            
    class Task:
        def __init__(self, *args, **kwargs):
            pass

try:
    from src.infrastructure.memory import MemoryEngine
except ImportError:
    MemoryEngine = None

logger = logging.getLogger(__name__)

class TechnicalLead:
    """Technical Lead Agent agent."""
    
    def __init__(self, tools: Optional[List] = None, memory_engine: Optional[memory.engine] = None):
        """Initialize TechnicalLead."""
        self.tools = tools or []
        self.memory_engine = memory_engine
        
        # Agent configuration
        self.agent = Agent(
            role="Technical Lead",
            goal="Technical Lead Agent for architecture and technical oversight",
            backstory="Expert technicallead with deep knowledge and expertise",
            verbose=True,
            allow_delegation=False,
            tools=self.tools
        )
        
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task."""
        logger.info(f"Executing task: {task.get('id', 'unknown')}")
        
        result = {
            "task_id": task.get("id", "unknown"),
            "status": "completed",
            "output": "TechnicalLead task completed successfully",
            "agent": "TechnicalLead"
        }
        
        return result

# Export the class
__all__ = ["TechnicalLead"]
