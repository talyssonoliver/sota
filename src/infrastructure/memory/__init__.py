"""Infrastructure memory module."""

try:
    from .caching import CacheManager, get_cache_manager
    from .chunking import ChunkingManager, get_chunking_manager
    from .config import MemoryEngineConfig
    from .engines.memory_engine import MemoryEngine
    from .exceptions import *
    from .security import SecurityManager
except ImportError:
    pass

try:
    from .engines.caching import CacheManager
    from .engines.chunking import ChunkProcessor
    from .engines.storage import StorageManager
except ImportError:

    # Fallback implementations
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
    if config is None:
        # Import here to avoid circular imports
        try:
            from .config.memory_config import MemoryEngineConfig

            config = MemoryEngineConfig()
        except ImportError:
            # Fallback to basic config
            config = {}
    return MemoryEngine(config)


def get_relevant_context(query, k=5, user="system"):
    """Get relevant context for a query."""
    memory_engine = get_memory_instance()
    return memory_engine.get_context(query, k=k, user=user)


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
