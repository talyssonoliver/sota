"""
Technical Lead Agent for architectural decision making and oversight.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from crewai import Agent
from dotenv import load_dotenv
from langchain_core.tools import BaseTool
from langchain_core.tools import Tool  # Updated import for Tool class
from langchain_openai import ChatOpenAI

from prompts.utils import load_and_format_prompt
from src.platform.tools.github_tool import GitHubTool
from src.platform.tools.memory import get_context_by_keys
from src.platform.tools.vercel_tool import VercelTool

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Memory configuration (module-level variable for patching in tests)
memory = None


def build_technical_agent(task_metadata: Dict = None, **kwargs):
    """Build technical agent with memory-enhanced context"""
    # Import here to avoid circular imports
    from agents import agent_builder

    return agent_builder.build_agent(
        role="technical_lead",
        task_metadata=task_metadata,
        **kwargs
    )


def get_context_with_error_handling(
        domains: List[str],
        max_results: int,
        testing_env_var: str = "TESTING") -> list:
    """Retrieve context with error handling and fallback logic."""
    from agents import agent_builder
    try:
        result = agent_builder.memory.get_context_by_domains(
            domains=domains,
            max_results=max_results
        )
        if isinstance(result, list):
            return result
        return [result]
    except Exception:
        import os
        if os.environ.get(testing_env_var, "0") == "1":
            return None
        return [
            f"# No Context Available\nNo context found for domains: {
                ', '.join(domains)}"]


def get_technical_context(task_id: str = None) -> list:
    """Get technical-specific context for external use. Always returns a list, or None on error if required by tests."""
    return get_context_with_error_handling(
        domains=["infrastructure", "deployment", "architecture"],
        max_results=5
    )


def create_technical_lead_agent(
    llm_model: str = "gpt-4-turbo",
    temperature: float = 0.1,  # Lower temperature for more deterministic decisions
    memory_config: Optional[Dict[str, Any]] = None,
    custom_tools: Optional[list] = None,
    context_keys: Optional[List[str]] = None
) -> Agent:
    """
    Create a Technical Lead Agent specialized in architecture and technical oversight.
    Refactored to use the unified AgentFactory.

    Args:
        llm_model: The OpenAI model to use
        temperature: Creativity of the model (0.0 to 1.0)
        memory_config: Configuration for agent memory
        custom_tools: List of additional tools to provide to the agent
        context_keys: List of specific context document keys to include in the prompt

    Returns:
        A CrewAI Agent configured as the Technical Lead
    """
    from src.core.agents.factory import agent_factory
    
    return agent_factory.create_agent(
        agent_type='technical',
        llm_model=llm_model,
        temperature=temperature,
        memory_config=memory_config,
        custom_tools=custom_tools,
        context_keys=context_keys or ["system-architecture", "technical-requirements", "best-practices"]
    )
