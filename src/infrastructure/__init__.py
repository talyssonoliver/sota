"""Infrastructure module for AI Agent System."""

# Import lightweight modules immediately
try:
    from . import tools, utils
except ImportError:
    pass

# Memory module is imported lazily to avoid ChromaDB dependency at import time
memory = None


def get_memory():
    """Get memory module with lazy import."""
    global memory
    if memory is None:
        try:
            from . import memory as _memory

            memory = _memory
        except ImportError:
            pass
    return memory


__all__ = ["get_memory", "tools", "utils"]
