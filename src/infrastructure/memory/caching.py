
from src.infrastructure.utils.common_imports import (
    dataclass,
    datetime,
    logging,
    timedelta
)
"""
Memory Engine Caching Module

Provides caching functionality for the memory engine.
"""

# import logging  # Consolidated to common_imports
# from dataclasses import dataclass  # Consolidated to common_imports
# from datetime import datetime, timedelta  # Consolidated to common_imports
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached entry"""

    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0


class CacheManager:
    """Manages in-memory caching for the memory engine"""

    def __init__(self, max_size_mb: int = 100, default_ttl_seconds: int = 3600):
        """Initialize cache manager

        Args:
            max_size_mb: Maximum cache size in megabytes
            default_ttl_seconds: Default time-to-live in seconds
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size_bytes = 0
        self.default_ttl_seconds = default_ttl_seconds
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            self.miss_count += 1
            return None

        entry = self.cache[key]

        # Check expiration
        if entry.expires_at and datetime.now() > entry.expires_at:
            self.evict(key)
            self.miss_count += 1
            return None

        # Update access statistics
        entry.access_count += 1
        entry.last_accessed = datetime.now()
        self.hit_count += 1

        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds (None for default)

        Returns:
            True if cached successfully
        """
        # Calculate size (simplified)
        size_bytes = len(str(value).encode("utf-8"))

        # Check if we need to evict entries
        if self.current_size_bytes + size_bytes > self.max_size_bytes:
            self._evict_lru()

        # Create cache entry
        ttl = ttl_seconds or self.default_ttl_seconds
        expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at,
            size_bytes=size_bytes,
        )

        # Remove old entry if exists
        if key in self.cache:
            self.current_size_bytes -= self.cache[key].size_bytes

        # Add new entry
        self.cache[key] = entry
        self.current_size_bytes += size_bytes

        return True

    def evict(self, key: str) -> bool:
        """Evict entry from cache

        Args:
            key: Cache key

        Returns:
            True if evicted successfully
        """
        if key in self.cache:
            self.current_size_bytes -= self.cache[key].size_bytes
            del self.cache[key]
            return True
        return False

    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
        self.current_size_bytes = 0
        self.hit_count = 0
        self.miss_count = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0

        return {
            "entries": len(self.cache),
            "size_bytes": self.current_size_bytes,
            "size_mb": self.current_size_bytes / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }

    def _evict_lru(self):
        """Evict least recently used entries to make space"""
        if not self.cache:
            return

        # Sort by last access time (oldest first)
        sorted_entries = sorted(
            self.cache.items(), key=lambda x: x[1].last_accessed or x[1].created_at
        )

        # Evict until we have enough space
        target_size = int(self.max_size_bytes * 0.8)  # Free up to 80% capacity

        for key, entry in sorted_entries:
            if self.current_size_bytes <= target_size:
                break
            self.evict(key)
            logger.debug(f"Evicted cache entry: {key}")


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
