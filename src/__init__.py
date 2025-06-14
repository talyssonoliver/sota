"""
AI Agent System - Source Code Root

This module provides the main entry points for the AI Agent System
with proper import paths for the new src/ architecture.
"""

# Re-export main modules for convenience
try:
    from . import core
    from . import interfaces
    from . import platform
    from . import integrations
except ImportError:
    # Graceful fallback if dependencies are missing
    pass

__version__ = "1.0.0"
__all__ = ["core", "interfaces", "platform", "integrations"]