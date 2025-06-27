#!/usr/bin/env python3
"""
exceptions.py - Unified Memory System

Consolidated from tools/memory/exceptions.py
New location: src/platform/memory/config/exceptions.py

Part of the unified memory architecture eliminating fragmentation
across tools/memory/, memory-bank/, and runtime/ locations.
"""

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