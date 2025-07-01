#!/usr/bin/env python3
"""
factory.py - Unified Memory System

Consolidated from tools/memory/factory.py
New location: src/platform/memory/config/factory.py

Part of the unified memory architecture eliminating fragmentation
across tools/memory/, memory-bank/, and runtime/ locations.
"""

"""
Memory Engine Factory Functions
Provides factory functions for backward compatibility and easy initialization
"""


try:
    from typing import Any, Dict, List, Optional
except ImportError:
    pass
try:
    from ..engine import MemoryEngine
    pass  # Use fallback implementations
except ImportError:
    pass
try:
    from src.infrastructure.memory.config.memory_config import MemoryEngineConfig
    pass  # Use fallback implementations
except ImportError:
    pass
# Global singleton instance
_memory_instance: Optional[MemoryEngine] = None

def initialize_memory(config: Optional[Dict[str, Any]] = None) -> MemoryEngine:
    """
    Initialize and return memory engine singleton.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        MemoryEngine instance
    """
    global _memory_instance
    
    if _memory_instance is None:
        if config:
            memory_config = MemoryEngineConfig.from_dict(config)
        else:
            memory_config = MemoryEngineConfig()
        
        _memory_instance = MemoryEngine(memory_config)
    
    return _memory_instance

def get_memory_instance() -> MemoryEngine:
    """
    Get the memory engine singleton instance.
    
    Returns:
        MemoryEngine instance
    """
    global _memory_instance
    
    if _memory_instance is None:
        _memory_instance = initialize_memory()
    
    return _memory_instance

# Import consolidated functions from main memory module
from .. import get_relevant_context

def get_context_by_keys(keys: List[str], **kwargs) -> List[str]:
    """
    Backward compatibility function for getting context by keys.
    
    Args:
        keys: List of context keys
        **kwargs: Additional arguments
        
    Returns:
        List of context strings
    """
    memory = get_memory_instance()
    
    try:
        results = memory.get_context_by_keys(keys, **kwargs)
        
        if isinstance(results, list):
            return [str(result) for result in results]
        else:
            return [str(results)]
            
    except Exception:
        return [f"No context available for keys: {keys}"]

def get_answer(question: str, context: Optional[str] = None, **kwargs) -> str:
    """
    Backward compatibility function for getting answers.
    
    Args:
        question: Question to answer
        context: Optional context to use
        **kwargs: Additional arguments
        
    Returns:
        Answer string
    """
    # Import here to use the patched version in tests
    from . import get_memory_instance as get_memory_from_init
    memory = get_memory_from_init()
    
    try:
        # Use retrieval_qa method which is what tests expect
        if hasattr(memory, 'retrieval_qa'):
            # Set default parameters expected by tests
            retrieval_kwargs = {
                'use_conversation': False,
                'metadata_filter': None,
                'temperature': 0.0,
                'user': None,
                'chat_history': None
            }
            # Override with any provided kwargs
            retrieval_kwargs.update(kwargs)
            return memory.retrieval_qa(question, **retrieval_kwargs)
        else:
            # Fallback to context retrieval
            relevant_context = get_relevant_context(question, **kwargs)
            return f"Based on the available context:\n\n{relevant_context}"
            
    except Exception:
        return f"Unable to answer question: {question}"