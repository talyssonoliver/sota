"""
Agent Registry for the AI Agent System
Maps agent names to their constructor functions for dynamic instantiation.
"""

import os
from typing import Any, Callable, Dict, List, Optional

import yaml

from agents import (create_backend_engineer_agent, create_coordinator_agent,
                    create_documentation_agent, create_frontend_engineer_agent,
                    create_qa_agent, create_technical_lead_agent)
from tools.tool_loader import get_tools_for_agent, load_all_tools

# Registry mapping agent roles to their constructor functions
AGENT_REGISTRY: Dict[str, Callable] = {
    # Agent roles by type
    "coordinator": create_coordinator_agent,
    # Changed from "technical" to "technical_lead"
    "technical_lead": create_technical_lead_agent,
    "backend": create_backend_engineer_agent,
    "backend_engineer": create_backend_engineer_agent,  # Added for consistency
    "frontend": create_frontend_engineer_agent,
    "frontend_engineer": create_frontend_engineer_agent,  # Added for consistency
    "documentation": create_documentation_agent,
    "qa": create_qa_agent,

    # Task prefix mappings
    "CO": create_coordinator_agent,
    "TL": create_technical_lead_agent,
    "BE": create_backend_engineer_agent,
    "FE": create_frontend_engineer_agent,
    "DOC": create_documentation_agent,
    "QA": create_qa_agent,
}


def load_agent_config() -> Dict[str, Any]:
    """
    Load the agent configuration from YAML.

    Returns:
        Dict[str, Any]: The parsed agent configuration.
    """
    config_path = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'config', 'agents.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def get_agent_config(agent_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the configuration for a specific agent.

    Args:
        agent_id: The agent identifier

    Returns:
        Dict[str, Any]: The agent configuration or None if not found
    """
    agent_config = load_agent_config()

    # Try direct match
    if agent_id.lower() in agent_config:
        return agent_config[agent_id.lower()]

    # Try to match task prefix with agent role
    for role, config in agent_config.items():
        if role.upper().startswith(agent_id.upper()):
            return config

    # Return None for nonexistent agents
    return None


def get_agent_constructor(agent_id: str) -> Optional[Callable]:
    """
    Get agent constructor function by agent identifier.

    Args:
        agent_id: The agent identifier (can be role name or task prefix)

    Returns:
        The constructor function for the specified agent or None if not found
    """
    # First, check if the agent_id matches a role name (lowercase)
    constructor = AGENT_REGISTRY.get(agent_id.lower())
    if constructor is not None:
        return constructor

    # If not found, check if it matches a task prefix (uppercase)
    constructor = AGENT_REGISTRY.get(agent_id.upper())
    return constructor


def create_agent_instance(agent_id: str, **kwargs) -> Any:
    """
    Create an agent instance by agent identifier.

    Args:
        agent_id: The agent identifier (can be role name or task prefix)
        **kwargs: Configuration parameters to pass to the agent constructor

    Returns:
        An instance of the specified agent with appropriate tools

    Raises:
        ValueError: If the agent identifier is not found in the registry
    """
    constructor = get_agent_constructor(agent_id)

    if constructor is None:
        raise ValueError(f"Unknown agent identifier: {agent_id}")

    # Get agent configuration
    agent_config = get_agent_config(agent_id)

    # Load tools if configuration exists
    if agent_config:
        if "custom_tools" not in kwargs:
            # Add tools from configuration
            custom_tools = get_tools_for_agent(
                agent_id, agent_config, **kwargs)

            if custom_tools:
                kwargs["custom_tools"] = custom_tools

    return constructor(**kwargs)


def get_agent_for_task(task_id: str, **kwargs) -> Any:
    """
    Create an agent instance based on a task identifier.

    Args:
        task_id: The task identifier (e.g., BE-07, TL-03)
        **kwargs: Configuration parameters to pass to the agent constructor

    Returns:
        An instance of the appropriate agent for the task

    Raises:
        ValueError: If the task prefix is not recognized
    """
    parts = task_id.split("-", 1)

    if len(parts) < 2 or not parts[0]:
        raise ValueError(f"Invalid task ID format: {task_id}")

    task_prefix = parts[0].upper()
    return create_agent_instance(task_prefix, **kwargs)


def get_agent(agent_name: str, **kwargs) -> Any:
    """
    Get an instantiated agent by name.

    Args:
        agent_name: The agent name or role
        **kwargs: Additional parameters to pass to the agent constructor

    Returns:
        An instantiated agent

    Raises:
        ValueError: If the agent name is not found in the registry
    """
    return create_agent_instance(agent_name, **kwargs)
