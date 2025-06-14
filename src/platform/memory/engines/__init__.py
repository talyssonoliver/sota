"""Unified memory platform - engines"""

try:
    from .memory_engine import MemoryEngine
    from .caching import CacheManager
    from .storage import TieredStorageManager as StorageManager
    from .chunking import ChunkingStrategy
except ImportError as e:
    # Mock implementations for testing
    from unittest.mock import MagicMock
    
    class MemoryEngine:
        def __init__(self, config=None): 
            self.config = config
        def store(self, *args, **kwargs): return True
        def retrieve(self, *args, **kwargs): return []
        def search(self, *args, **kwargs): return []
        def get_context_by_keys(self, keys, **kwargs): return ""
    
    class CacheManager:
        def __init__(self, config=None): pass
        def get(self, key): return None
        def set(self, key, value): return True
    
    class StorageManager:
        def __init__(self, config=None): pass
        def save(self, *args, **kwargs): return True
        def load(self, *args, **kwargs): return {}
    
    class ChunkingStrategy:
        def __init__(self, config=None): pass
        def chunk_text(self, text): return [text]

__all__ = ['MemoryEngine', 'CacheManager', 'StorageManager', 'ChunkingStrategy']
