"""Agent implementations for the AI system."""

# Lazy loading implemented in individual agent modules to avoid heavy dependencies
# Import specific agents directly when needed:
# from src.core.agents.backend import BackendEngineer
# from src.core.agents.frontend import FrontendEngineer
# etc.

# Import agents that have proper lazy loading implemented
try:
    from .backend import BackendEngineer
except ImportError:
    pass

try:
    from .coordinator import Coordinator
except ImportError:
    pass

try:
    from .doc import DocumentationWriter
except ImportError:
    pass

try:
    from .frontend import FrontendEngineer
except ImportError:
    pass

try:
    from .human_agents import HumanProductManager, HumanUXDesigner
except ImportError:
    pass

try:
    from .technical import TechnicalLead
except ImportError:
    pass

try:
    from .qa import QAEngineer
except ImportError:
    pass

# Skip factory for now as it's still slow
# try:
#     from .factory import create_agent, agent_builder
# except ImportError:
#     pass

__all__ = [
    "BackendEngineer",
    "Coordinator",
    "DocumentationWriter",
    "FrontendEngineer",
    "HumanProductManager",
    "HumanUXDesigner",
    "TechnicalLead",
    "QAEngineer",
]
