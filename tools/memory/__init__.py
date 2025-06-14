"""
Memory Module - Legacy Compatibility Layer

⚠️  DEPRECATED: Use 'from src.platform.memory import ...' instead

This module provides compatibility for legacy imports while redirecting
to the new consolidated memory system location.
"""

import warnings
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

warnings.warn(
    "Importing from 'tools.memory' is deprecated. Use 'from src.platform.memory import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

try:
    # Import from new consolidated location
    from src.platform.memory.engines.memory_engine import MemoryEngine
    from src.platform.memory.config.memory_config import MemoryEngineConfig
    from src.platform.memory.config.exceptions import MemoryEngineError, SecurityError, StorageError
    from src.platform.memory.security.thread_safety import (
        ThreadSafeMemoryEngine,
        get_thread_safe_memory_instance,
        reset_memory_instance,
        with_thread_safe_memory,
        get_context_by_keys,
        get_relevant_context
    )
    from src.platform.memory.config.factory import initialize_memory, get_answer
    
except ImportError as e:
    print(f"Warning: Could not import from new memory location: {e}")
    
    # Provide fallback implementations
    class MemoryEngine:
        def __init__(self, *args, **kwargs):
            pass
        def get_context(self, *args, **kwargs):
            return ""
    
    MemoryEngineConfig = type('MemoryEngineConfig', (), {})
    MemoryEngineError = Exception
    SecurityError = Exception
    StorageError = Exception
    ThreadSafeMemoryEngine = MemoryEngine
    
    def get_thread_safe_memory_instance(*args, **kwargs):
        return MemoryEngine()
    
    def reset_memory_instance(*args, **kwargs):
        pass
    
    def with_thread_safe_memory(*args, **kwargs):
        pass
    
    def get_context_by_keys(keys: List[str], **kwargs) -> str:
        return ""
    
    def get_relevant_context(query: str, **kwargs) -> str:
        return ""
    
    def initialize_memory(*args, **kwargs):
        return MemoryEngine()
    
    def get_answer(*args, **kwargs):
        return ""

# Backward compatibility - thread-safe singleton instance
memory = None

def get_memory_instance():
    """Get or create thread-safe singleton memory instance (legacy compatibility)"""
    global memory
    if memory is None:
        memory = get_thread_safe_memory_instance()
    return memory

# Export main interface
__all__ = [
    'MemoryEngine',
    'ThreadSafeMemoryEngine',
    'MemoryEngineConfig', 
    'MemoryEngineError',
    'SecurityError',
    'StorageError',
    'initialize_memory',
    'get_relevant_context',
    'get_context_by_keys',
    'get_answer',
    'get_memory_instance',
    'get_thread_safe_memory_instance',
    'reset_memory_instance',
    'with_thread_safe_memory'
]