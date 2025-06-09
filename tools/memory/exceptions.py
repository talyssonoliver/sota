"""
Memory Engine Exception Hierarchy
Defines all custom exceptions used throughout the memory system
"""

class MemoryEngineError(Exception):
    """Base exception for MemoryEngine errors"""
    pass


class SecurityError(MemoryEngineError):
    """Security-related errors"""
    pass


class AccessDeniedError(SecurityError):
    """Access control violations"""
    pass


class StorageError(MemoryEngineError):
    """Storage-related errors"""
    pass


class CacheError(MemoryEngineError):
    """Cache-related errors"""
    pass


class EncryptionError(SecurityError):
    """Encryption/decryption errors"""
    pass


class ValidationError(MemoryEngineError):
    """Input validation errors"""
    pass