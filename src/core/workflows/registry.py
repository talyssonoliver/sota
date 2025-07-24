"""Workflow registry module."""

import logging

logger = logging.getLogger(__name__)

# Agent registry mapping task prefixes to agent types
AGENT_REGISTRY = {
    "CO": "coordinator",
    "TL": "technical_lead", 
    "BE": "backend_engineer",
    "FE": "frontend_engineer",
    "DOC": "documentation",
    "QA": "qa",
    "coordinator": "coordinator",
    "technical_lead": "technical_lead",
    "backend_engineer": "backend_engineer", 
    "frontend_engineer": "frontend_engineer",
    "documentation": "documentation",
    "qa": "qa"
}


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
    config = load_agent_config()
    return config.get(agent_name)


def load_agent_config():
    """Load agent configuration."""
    return {
        "coordinator": {"name": "Coordinator Agent"},
        "technical_lead": {"name": "Technical Lead Agent"},
        "backend_engineer": {"name": "Backend Engineer Agent"},
        "frontend_engineer": {"name": "Frontend Engineer Agent"},
        "documentation": {"name": "Documentation Agent"},
        "qa": {"name": "QA Agent"}
    }


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
    from src.core.agents.coordinator import Coordinator
    return Coordinator(*args, **kwargs)


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
    "AGENT_REGISTRY",
    "get_agent_constructor",
    "create_agent_instance",
    "get_agent_config",
    "load_agent_config",
    "get_agent_for_task",
    "get_agent",
    "create_technical_lead_agent",
    "create_backend_engineer_agent",
    "create_coordinator_agent",
    "create_qa_agent",
    "create_documentation_agent",
    "create_frontend_engineer_agent",
]
