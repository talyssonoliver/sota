"""Module initialization."""

import logging

logger = logging.getLogger(__name__)

# Core engine imports - these are required
try:
    from .engine import MemoryEngine
    # Provide backward compatibility aliases
    Engine = MemoryEngine
    engine = MemoryEngine  # For cases where it's used as a class reference
    
    __all__ = ["MemoryEngine", "Engine", "engine"]
except ImportError as e:
    logger.error(f"Failed to import MemoryEngine: {e}")
    # Re-raise the error instead of silently failing
    raise ImportError(f"Required memory engine components are not available: {e}") from e

# Optional storage module
try:
    from .storage import TieredStorageManager
    __all__.append("TieredStorageManager")
except ImportError as e:
    logger.warning(f"TieredStorageManager not available: {e}")
    # Don't add to __all__ if import fails

# Optional security module  
try:
    from .security import SecurityManager
    __all__.append("SecurityManager")
except ImportError as e:
    logger.warning(f"SecurityManager not available: {e}")
    # Don't add to __all__ if import fails
