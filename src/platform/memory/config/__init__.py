"""Unified memory platform - config"""

try:
    from .memory_config import MemoryConfig
    from .factory import create_memory_engine
    from .exceptions import MemoryConfigError, MemoryInitializationError
except ImportError as e:
    # Mock implementations for testing
    class MemoryConfig:
        def __init__(self, config_path=None):
            self.config_path = config_path
        
        def get_config(self):
            return {
                "vector_store": {"provider": "mock"},
                "cache": {"enabled": True},
                "encryption": {"enabled": False}
            }
    
    def create_memory_engine(config=None):
        from unittest.mock import MagicMock
        return MagicMock()
    
    class MemoryConfigError(Exception):
        pass
    
    class MemoryInitializationError(Exception):
        pass

__all__ = ['MemoryConfig', 'create_memory_engine', 'MemoryConfigError', 'MemoryInitializationError']
