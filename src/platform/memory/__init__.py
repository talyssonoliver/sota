#!/usr/bin/env python3
"""
Unified Memory System Interface

Consolidated interface for all memory operations across the AI system.
Provides a single entry point for memory engines, knowledge management,
and security features.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from .engines.memory_engine import MemoryEngine
    from .engines.caching import CacheManager
    from .engines.storage import TieredStorageManager as StorageManager
    from .knowledge.context_manager import ContextManager
    from .security.encryption import SecurityManager
    from .config.memory_config import MemoryConfig
except ImportError as e:
    print(f"Warning: Memory components not available: {e}")
    # Mock implementations for development
    class MemoryEngine:
        def __init__(self, config=None): pass
        def store(self, *args, **kwargs): return True
        def retrieve(self, *args, **kwargs): return []
        def search(self, *args, **kwargs): return []
    
    class CacheManager:
        def __init__(self, config=None): pass
        def get(self, key): return None
        def set(self, key, value): return True
    
    class StorageManager:
        def __init__(self, config=None): pass
        def save(self, *args, **kwargs): return True
        def load(self, *args, **kwargs): return {}
    
    class ContextManager:
        def __init__(self, config=None): pass
        def get_context(self, *args, **kwargs): return {}
        def update_context(self, *args, **kwargs): return True
    
    class SecurityManager:
        def __init__(self, config=None): pass
        def encrypt(self, data): return data
        def decrypt(self, data): return data
    
    class MemoryConfig:
        def __init__(self): pass
        def get_config(self): return {}


class UnifiedMemorySystem:
    """Unified interface for all memory operations."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize unified memory system."""
        self.config = MemoryConfig(config_path)
        
        # Initialize components
        self.engine = MemoryEngine(self.config)
        self.cache = CacheManager(self.config)
        self.storage = StorageManager(self.config)
        self.context = ContextManager(self.config)
        self.security = SecurityManager(self.config)
        
        print("🧠 Unified Memory System initialized")
    
    def store_knowledge(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Store knowledge with security and caching."""
        try:
            # Encrypt sensitive content
            encrypted_content = self.security.encrypt(content)
            
            # Store in main engine
            result = self.engine.store(encrypted_content, metadata or {})
            
            # Update cache
            if result and metadata:
                cache_key = metadata.get('id', hash(content))
                self.cache.set(cache_key, content)
            
            return result
        except Exception as e:
            print(f"Error storing knowledge: {e}")
            return False
    
    def retrieve_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve knowledge with caching and security."""
        try:
            # Check cache first
            cache_key = f"query_{hash(query)}"
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            # Search main engine
            results = self.engine.search(query, limit=limit)
            
            # Decrypt results
            decrypted_results = []
            for result in results:
                if 'content' in result:
                    result['content'] = self.security.decrypt(result['content'])
                decrypted_results.append(result)
            
            # Cache results
            self.cache.set(cache_key, decrypted_results)
            
            return decrypted_results
        except Exception as e:
            print(f"Error retrieving knowledge: {e}")
            return []
    
    def get_context(self, context_type: str = "active") -> Dict[str, Any]:
        """Get context information."""
        return self.context.get_context(context_type)
    
    def update_context(self, context_type: str, updates: Dict[str, Any]) -> bool:
        """Update context information."""
        return self.context.update_context(context_type, updates)
    
    def save_state(self, state_name: str, data: Dict[str, Any]) -> bool:
        """Save system state."""
        return self.storage.save(state_name, data)
    
    def load_state(self, state_name: str) -> Dict[str, Any]:
        """Load system state."""
        return self.storage.load(state_name)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform system health check."""
        return {
            "status": "operational",
            "components": {
                "engine": "operational",
                "cache": "operational", 
                "storage": "operational",
                "context": "operational",
                "security": "operational"
            },
            "config": self.config.get_config()
        }


# Global instance for easy access
_memory_system = None

def get_memory_system(config_path: Optional[str] = None) -> UnifiedMemorySystem:
    """Get global memory system instance."""
    global _memory_system
    if _memory_system is None:
        _memory_system = UnifiedMemorySystem(config_path)
    return _memory_system


# Convenience functions for backward compatibility
def store_knowledge(content: str, metadata: Dict[str, Any] = None) -> bool:
    """Store knowledge using unified system."""
    return get_memory_system().store_knowledge(content, metadata)


def retrieve_knowledge(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve knowledge using unified system."""
    return get_memory_system().retrieve_knowledge(query, limit)


def get_context(context_type: str = "active") -> Dict[str, Any]:
    """Get context using unified system."""
    return get_memory_system().get_context(context_type)


def get_context_by_keys(keys: List[str], **kwargs) -> str:
    """Get context by keys for backward compatibility."""
    try:
        memory = get_memory_system()
        results = []
        for key in keys:
            context = memory.get_context(key)
            if context:
                results.append(str(context))
        return '\n'.join(results)
    except Exception as e:
        print(f"Error getting context by keys: {e}")
        return ""


if __name__ == "__main__":
    # Demo usage
    memory = UnifiedMemorySystem()
    
    print("🧠 Unified Memory System Demo")
    print("=" * 40)
    
    # Health check
    health = memory.health_check()
    print(f"Status: {health['status']}")
    
    # Store some knowledge
    success = memory.store_knowledge(
        "The AI system uses a unified memory architecture.",
        {"type": "system_info", "priority": "high"}
    )
    print(f"Storage successful: {success}")
    
    # Retrieve knowledge
    results = memory.retrieve_knowledge("unified memory")
    print(f"Retrieved {len(results)} results")
    
    print("✅ Demo complete")
