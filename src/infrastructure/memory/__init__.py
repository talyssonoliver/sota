"""Infrastructure memory module.

Provides memory management functionality including:
- Memory engines for context storage and retrieval
- Caching mechanisms for performance optimization  
- Chunking for large data processing
- Security and encryption support

Usage:
    from src.infrastructure.memory import MemoryEngine, get_memory_instance
    
    # Initialize memory engine
    memory = MemoryEngine()
    context = memory.get_context("query", k=5)
    
    # Or use convenience function
    memory = get_memory_instance()
"""

try:
    from .caching import CacheManager, get_cache_manager  # noqa: F401 - Public API re-export
    from .chunking import ChunkingManager, get_chunking_manager  # noqa: F401 - Public API re-export
    from .config import MemoryEngineConfig  # noqa: F401 - Public API re-export
    from .engines.memory_engine import MemoryEngine  # noqa: F401 - Public API re-export
    from .exceptions import *  # noqa: F401,F403 - Public API re-export
    from .security import SecurityManager  # noqa: F401 - Public API re-export
except ImportError:
    pass

try:
    from .engines.caching import CacheManager  # noqa: F401 - Fallback import
    from .engines.chunking import ChunkProcessor  # noqa: F401 - Fallback import
    from .engines.storage import StorageManager  # noqa: F401 - Fallback import
except ImportError:
    # Fallback implementations for when core modules are not available
    class MemoryEngine:
        def __init__(self, config=None):
            self.config = config or {}

        def store_context(self, key, context):
            return True

        def retrieve_context(self, key):
            return {}

        def get_relevant_context(self, query, domains=None):
            return {"query": query, "domains": domains or [], "context": []}

    class CacheManager:
        def __init__(self):
            pass

        def get(self, key):
            return None

        def set(self, key, value):
            return True

    class ChunkProcessor:
        def __init__(self, chunk_size=1000):
            self.chunk_size = chunk_size

        def chunk_text(self, text):
            return [text]

    class StorageManager:
        def __init__(self):
            pass

        def store(self, key, data):
            return True

        def retrieve(self, key):
            return None


def get_context_by_keys(keys, **kwargs):
    """Get context by keys."""
    return f"Context for keys: {keys}"


def get_memory_instance():
    """Get memory instance."""
    return initialize_memory()


def get_memory_system():
    """Get memory system."""
    return initialize_memory()


def initialize_memory(config=None):
    """Initialize memory engine."""
    try:
        if config is None:
            # Import here to avoid circular imports
            try:
                from .config.memory_config import MemoryEngineConfig

                config = MemoryEngineConfig()
            except ImportError:
                # Fallback to basic config
                config = {}
        return MemoryEngine(config)
    except Exception:
        # Return fallback memory engine if initialization fails
        return MemoryEngine({})


def get_relevant_context(query, k=5, user="system"):
    """Get relevant context for a query."""
    try:
        memory_engine = get_memory_instance()
        if memory_engine is None:
            return "Context unavailable: Memory engine not initialized"
        
        if not hasattr(memory_engine, 'get_context'):
            return "Context unavailable: Memory engine does not support get_context"
            
        return memory_engine.get_context(query, k=k, user=user)
    except Exception as e:
        return f"Context unavailable: {str(e)}"


__all__ = [
    "MemoryEngine",
    "CacheManager",
    "ChunkProcessor",
    "StorageManager",
    "get_context_by_keys",
    "get_memory_instance",
    "get_memory_system",
    "initialize_memory",
    "get_relevant_context",
]
