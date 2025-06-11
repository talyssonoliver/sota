"""
Memory Engine Module
Modular, production-ready memory management system for MCP (Model Context Protocol)

This module provides a refactored version of the monolithic memory engine,
breaking it into focused, maintainable components while preserving all functionality.

Main Components:
- engine.py: Main MemoryEngine orchestration
- storage.py: Tiered storage management  
- caching.py: Multi-level caching system
- security.py: Encryption, PII detection, access control
- chunking.py: Semantic and adaptive chunking
- retrieval.py: Context retrieval and search
- config.py: Configuration management
- exceptions.py: Custom exception hierarchy

Usage:
    from tools.memory import MemoryEngine, initialize_memory
    
    memory = MemoryEngine()
    context = memory.get_context("query", k=5)
"""

# Import main classes for backward compatibility
from .engine import MemoryEngine
from .config import MemoryEngineConfig
from .exceptions import MemoryEngineError, SecurityError, StorageError

# Import factory functions
from .factory import initialize_memory, get_relevant_context, get_context_by_keys, get_answer

# Backward compatibility - create singleton instance
memory = None

def get_memory_instance():
    """Get or create singleton memory instance"""
    global memory
    if memory is None:
        memory = MemoryEngine()
    return memory

# Export main interface
__all__ = [
    'MemoryEngine',
    'MemoryEngineConfig', 
    'MemoryEngineError',
    'SecurityError',
    'StorageError',
    'initialize_memory',
    'get_relevant_context',
    'get_context_by_keys',
    'get_answer',
    'get_memory_instance'
]