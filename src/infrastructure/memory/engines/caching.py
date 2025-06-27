"""Caching module."""

class CacheManager:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        self.cache[key] = value
    
    def put(self, key, value):
        """Alias for set method."""
        return self.set(key, value)

__all__ = ["CacheManager"]
