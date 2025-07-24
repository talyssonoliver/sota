"""
Thread-safe, size-limited cache for agent instances.
"""

import threading
from typing import Any, Dict, Optional


class AgentCache:
    """Thread-safe, size-limited cache for agent instances."""

    def __init__(self, max_size: int = 10):
        self.cache: Dict[str, Any] = {}
        self.lock = threading.Lock()
        self.max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """Get an agent from the cache."""
        with self.lock:
            return self.cache.get(key)

    def set(self, key: str, value: Any):
        """Set an agent in the cache."""
        with self.lock:
            if len(self.cache) >= self.max_size:
                # Simple FIFO eviction strategy
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self.cache[key] = value


# Global cache instance
_agent_cache = AgentCache()


def get_agent_from_cache(key: str) -> Optional[Any]:
    """Get an agent from the global cache."""
    return _agent_cache.get(key)


def set_agent_in_cache(key: str, agent: Any):
    """Set an agent in the global cache."""
    _agent_cache.set(key, agent)
