"""
Memory Engine Exceptions

Custom exceptions for memory engine operations.
"""


class MemoryEngineError(Exception):
    """Base exception for memory engine errors"""

    pass


class MemoryEngineConfigError(MemoryEngineError):
    """Configuration related errors"""

    pass


class MemoryEngineStorageError(MemoryEngineError):
    """Storage operation errors"""

    pass


class MemoryEngineSecurityError(MemoryEngineError):
    """Security related errors"""

    pass


class MemoryEngineChunkingError(MemoryEngineError):
    """Chunking operation errors"""

    pass


class MemoryEngineCacheError(MemoryEngineError):
    """Caching operation errors"""

    pass


class MemoryEngineEncryptionError(MemoryEngineSecurityError):
    """Encryption/decryption errors"""

    pass


class MemoryEnginePIIError(MemoryEngineSecurityError):
    """PII detection/handling errors"""

    pass


# Alias for backward compatibility with validation system
StorageError = MemoryEngineStorageError
