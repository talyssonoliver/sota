"""
Memory Engine Caching System
Multi-tiered caching implementation with LRU in-memory and disk persistence
"""

import json
import logging
import os
import threading
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .config import CacheConfig
from .exceptions import CacheError

logger = logging.getLogger(__name__)


class LRUCache:
    """Thread-safe LRU Cache with TTL support"""
    
    def __init__(self, maxsize: int = 1000, ttl_hours: int = 24):
        self.maxsize = maxsize
        self.ttl_hours = ttl_hours
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, datetime] = {}
        self.lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key in self.cache:
                # Check TTL
                if self._is_expired(key):
                    self._remove(key)
                    return None
                
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache"""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.maxsize:
                    # Remove least recently used
                    oldest_key = next(iter(self.cache))
                    self._remove(oldest_key)
            
            self.cache[key] = value
            self.timestamps[key] = datetime.now()
    
    def _remove(self, key: str) -> None:
        """Remove item from cache"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.timestamps:
            return True
        
        age = datetime.now() - self.timestamps[key]
        return age > timedelta(hours=self.ttl_hours)
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)


class DiskCache:
    """Persistent disk cache with automatic cleanup"""
    
    def __init__(self, cache_dir: str = "cache/memory_disk_cache", 
                 maxsize: int = 5000, ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.maxsize = maxsize
        self.ttl_hours = ttl_hours
        self.lock = threading.RLock()
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metadata
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from disk cache"""
        try:
            cache_file = self._get_cache_file(key)
            
            if not cache_file.exists():
                return None
            
            # Check TTL
            if self._is_expired(key):
                self._remove(key)
                return None
            
            # Read from disk
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update access time
            self._update_access_time(key)
            
            return data['value']
            
        except Exception as e:
            logger.warning(f"Error reading from disk cache: {e}")
            return None
    
    def put(self, key: str, value: Any) -> None:
        """Put item in disk cache"""
        try:
            with self.lock:
                # Check size limit
                if len(self.metadata) >= self.maxsize:
                    self._evict_oldest()
                
                # Write to disk
                cache_file = self._get_cache_file(key)
                data = {
                    'value': value,
                    'timestamp': datetime.now().isoformat(),
                    'access_time': datetime.now().isoformat()
                }
                
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
                
                # Update metadata
                self.metadata[key] = {
                    'timestamp': datetime.now().isoformat(),
                    'access_time': datetime.now().isoformat(),
                    'size': cache_file.stat().st_size
                }
                
                self._save_metadata()
                
        except Exception as e:
            logger.error(f"Error writing to disk cache: {e}")
            raise CacheError(f"Failed to write to disk cache: {e}")
    
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key"""
        # Use hash to avoid filesystem issues with special characters
        import hashlib
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load cache metadata"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading cache metadata: {e}")
        
        return {}
    
    def _save_metadata(self) -> None:
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache metadata: {e}")
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.metadata:
            return True
        
        timestamp_str = self.metadata[key]['timestamp']
        timestamp = datetime.fromisoformat(timestamp_str)
        age = datetime.now() - timestamp
        
        return age > timedelta(hours=self.ttl_hours)
    
    def _update_access_time(self, key: str) -> None:
        """Update access time for cache entry"""
        if key in self.metadata:
            self.metadata[key]['access_time'] = datetime.now().isoformat()
            self._save_metadata()
    
    def _evict_oldest(self) -> None:
        """Evict oldest cache entries"""
        if not self.metadata:
            return
        
        # Sort by access time
        sorted_entries = sorted(
            self.metadata.items(),
            key=lambda x: x[1]['access_time']
        )
        
        # Remove oldest 10% of entries
        num_to_remove = max(1, len(sorted_entries) // 10)
        
        for key, _ in sorted_entries[:num_to_remove]:
            self._remove(key)
    
    def _remove(self, key: str) -> None:
        """Remove cache entry"""
        try:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink()
            
            self.metadata.pop(key, None)
            self._save_metadata()
            
        except Exception as e:
            logger.warning(f"Error removing cache entry: {e}")
    
    def _start_cleanup_thread(self) -> None:
        """Start background cleanup thread"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(3600)  # Run every hour
                    self._cleanup_expired()
                except Exception as e:
                    logger.error(f"Error in cache cleanup: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_expired(self) -> None:
        """Clean up expired cache entries"""
        with self.lock:
            expired_keys = []
            
            for key in list(self.metadata.keys()):
                if self._is_expired(key):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove(key)
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            # Remove all cache files
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file != self.metadata_file:
                    cache_file.unlink()
            
            # Clear metadata
            self.metadata.clear()
            self._save_metadata()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.metadata)


class CacheManager:
    """Manages both LRU and disk caches"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.lru_cache = LRUCache(
            maxsize=config.lru_maxsize,
            ttl_hours=config.ttl_hours
        )
        self.disk_cache = DiskCache(
            cache_dir=config.disk_cache_dir,
            maxsize=config.disk_maxsize,
            ttl_hours=config.ttl_hours
        )
        
        self.hits = 0
        self.misses = 0
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache (LRU first, then disk)"""
        with self.lock:
            # Try LRU cache first
            value = self.lru_cache.get(key)
            if value is not None:
                self.hits += 1
                return value
            
            # Try disk cache
            value = self.disk_cache.get(key)
            if value is not None:
                # Promote to LRU cache
                self.lru_cache.put(key, value)
                self.hits += 1
                return value
            
            self.misses += 1
            return None
    
    def put(self, key: str, value: Any) -> None:
        """Put item in both caches"""
        with self.lock:
            self.lru_cache.put(key, value)
            self.disk_cache.put(key, value)
    
    def clear(self) -> None:
        """Clear both caches"""
        with self.lock:
            self.lru_cache.clear()
            self.disk_cache.clear()
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            
            return {
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'l1': {
                    'size': self.lru_cache.size(),
                    'hits': self.hits,
                    'misses': self.misses
                },
                'l2': {
                    'size': self.disk_cache.size(),
                    'hits': 0,  # Could track separately if needed
                    'misses': 0
                },
                'lru_size': self.lru_cache.size(),
                'disk_size': self.disk_cache.size()
            }