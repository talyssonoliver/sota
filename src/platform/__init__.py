"""
Platform Module - Infrastructure Services

Contains platform-level services including memory, tools, and utilities.
"""

try:
    from . import memory
    from . import tools
    from . import utils
    
    __all__ = ["memory", "tools", "utils"]
except ImportError:
    # Graceful fallback if dependencies are missing
    __all__ = []