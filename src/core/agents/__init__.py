"""Agent implementations for the AI system."""

try:
    from .backend import BackendEngineer
except ImportError:
    pass

    from .coordinator import Coordinator
    from .doc import DocumentationWriter
    from .factory import create_agent, agent_builder
    from .frontend import FrontendEngineer
    from .human_agents import HumanProductManager, HumanUXDesigner
    from .qa import QAEngineer
    from .technical import TechnicalLead
    # Fallback for missing dependencies
    pass

# Export factory functions for backward compatibility
try:
    from .factory import (
        create_technical_lead_agent,
        create_backend_agent,
        create_frontend_agent,
        create_qa_agent,
        create_documentation_agent,
        create_coordinator_agent
    )
except ImportError:
    pass
__all__ = [
    "BackendEngineer",
    "Coordinator",
    "DocumentationWriter",
    "create_agent",
    "agent_builder",
    "FrontendEngineer",
    "HumanProductManager",
    "HumanUXDesigner",
    "QAEngineer",
    "TechnicalLead",
    "create_technical_lead_agent",
    "create_backend_agent",
    "create_frontend_agent",
    "create_qa_agent",
    "create_documentation_agent",
    "create_coordinator_agent"
]
