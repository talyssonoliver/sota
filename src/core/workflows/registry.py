"""Workflow registry module."""

import logging

logger = logging.getLogger(__name__)


def get_agent_constructor(agent_name):
    """Get agent constructor."""
    constructors = {
        "technical_lead": lambda: {"type": "technical_lead"},
        "backend": lambda: {"type": "backend"},
        "coordinator": lambda: {"type": "coordinator"},
        "qa": lambda: {"type": "qa"},
        "frontend": lambda: {"type": "frontend"},
        "documentation": lambda: {"type": "documentation"},
    }
    return constructors.get(agent_name)


def create_agent_instance(agent_type, config=None):
    """Create agent instance."""
    return {"type": agent_type, "config": config or {}}


def get_agent_config(agent_name):
    """Get agent configuration."""
    return {"name": agent_name, "config": {}}


def get_agent_for_task(task_type):
    """Get agent for task type."""
    task_agent_map = {
        "backend": "backend",
        "frontend": "frontend",
        "qa": "qa",
        "documentation": "documentation",
        "technical": "technical_lead",
    }
    return task_agent_map.get(task_type, "coordinator")


def get_agent(agent_name):
    """Get agent by name."""
    return {"name": agent_name, "type": "agent"}


def create_technical_lead_agent(*args, **kwargs):
    """Create technical lead agent."""
    return {"type": "technical_lead", "args": args, "kwargs": kwargs}


def create_backend_engineer_agent(*args, **kwargs):
    """Create backend engineer agent."""
    return {"type": "backend", "args": args, "kwargs": kwargs}


def create_coordinator_agent(*args, **kwargs):
    """Create coordinator agent."""
    return {"type": "coordinator", "args": args, "kwargs": kwargs}


def create_qa_agent(*args, **kwargs):
    """Create QA agent."""
    return {"type": "qa", "args": args, "kwargs": kwargs}


def create_documentation_agent(*args, **kwargs):
    """Create documentation agent."""
    return {"type": "documentation", "args": args, "kwargs": kwargs}


def create_frontend_engineer_agent(*args, **kwargs):
    """Create frontend engineer agent."""
    return {"type": "frontend", "args": args, "kwargs": kwargs}


__all__ = [
    "get_agent_constructor",
    "create_agent_instance",
    "get_agent_config",
    "get_agent_for_task",
    "get_agent",
    "create_technical_lead_agent",
    "create_backend_engineer_agent",
    "create_coordinator_agent",
    "create_qa_agent",
    "create_documentation_agent",
    "create_frontend_engineer_agent",
]
