"""
AI Agent System - Source Code Root

This module provides the main entry points for the AI Agent System
with proper import paths for the new src/ architecture.
"""

try:
    from . import core
except ImportError:
    pass

try:
    from . import interfaces
except ImportError:
    pass

try:
    from . import infrastructure
except ImportError:
    pass

try:
    from . import integrations
except ImportError:
    pass

__version__ = "1.0.0"
__all__ = ["core", "interfaces", "infrastructure", "integrations"]
