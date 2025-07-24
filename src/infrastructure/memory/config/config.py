"""
Memory Configuration Module

Re-exports configuration classes from the config package for backward compatibility.
"""

from .config.exceptions import (
    AccessDeniedError,
    CacheError,
    ConfigurationError,
    EncryptionError,
    InitializationError,
    MemoryEngineError,
    SecurityError,
    StorageError,
    ValidationError,
)
from .config.factory import (
    get_answer,
    get_context_by_keys,
    get_memory_instance,
    get_relevant_context,
    initialize_memory,
    reset_memory_instance,
)

# Import all configuration classes and functions from the config package
from .config.memory_config import (
    CacheConfig,
    ChunkingConfig,
    MemoryConfig,
    MemoryEngineConfig,
    ResourceConfig,
    RetrievalConfig,
    StorageConfig,
)

# Re-export everything for backward compatibility
__all__ = [
    # Configuration classes
    "CacheConfig",
    "ChunkingConfig",
    "RetrievalConfig",
    "ResourceConfig",
    "StorageConfig",
    "MemoryEngineConfig",
    "MemoryConfig",
    # Factory functions
    "initialize_memory",
    "get_memory_instance",
    "reset_memory_instance",
    "get_relevant_context",
    "get_context_by_keys",
    "get_answer",
    # Exceptions
    "MemoryEngineError",
    "SecurityError",
    "AccessDeniedError",
    "StorageError",
    "CacheError",
    "EncryptionError",
    "ValidationError",
    "ConfigurationError",
    "InitializationError",
]
