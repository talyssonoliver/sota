#!/usr/bin/env python3
"""
thread_safe.py - Unified Memory System

Consolidated from tools/memory/thread_safe.py
New location: src/platform/memory/security/thread_safety.py

Part of the unified memory architecture eliminating fragmentation
across tools/memory/, memory-bank/, and runtime/ locations.

Thread-Safe Memory Engine Access Patterns
Provides thread-safe wrappers and access patterns for memory engine operations.
"""

import logging
import threading
import time

try:
    from typing import Any, Dict, List, Optional, Union
except ImportError:
    pass
try:
    from ..config.memory_config import MemoryEngineConfig
except ImportError:
    MemoryEngineConfig = None

try:
    from ..engines.memory_engine import MemoryEngine
except ImportError:
    # Create placeholder if not available
    class MemoryEngine:
        def __init__(self, config=None):
            self.config = config


logger = logging.getLogger(__name__)


class ThreadSafeMemoryEngine:
    """
    Thread-safe wrapper for MemoryEngine with proper locking mechanisms.
    Ensures safe concurrent access to memory operations across multiple agents.
    """

    def __init__(self, config: Optional[MemoryEngineConfig] = None):
        """Initialize thread-safe memory engine wrapper"""
        self._engine = MemoryEngine(config)
        self._read_write_lock = threading.RLock()
        self._document_lock = threading.RLock()
        self._cache_lock = threading.RLock()
        self._stats_lock = threading.RLock()

        # Thread-safe statistics tracking
        self._operation_stats = {
            "reads": 0,
            "writes": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
        }

        logger.info("ThreadSafeMemoryEngine initialized")

    def add_document(
        self,
        file_path: str,
        user: str = "system",
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Thread-safe document addition"""
        with self._document_lock:
            try:
                with self._stats_lock:
                    self._operation_stats["writes"] += 1

                result = self._engine.add_document(
                    file_path, user, content_type, metadata
                )
                logger.debug(f"Document added thread-safely: {file_path}")
                return result

            except Exception as e:
                with self._stats_lock:
                    self._operation_stats["errors"] += 1
                logger.error(f"Thread-safe document addition failed: {e}")
                raise

    def get_context(
        self,
        query: str,
        k: int = 5,
        user: str = "system",
        similarity_threshold: Optional[float] = None,
        context_domains: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> Union[str, List[str]]:
        """Thread-safe context retrieval"""
        with self._read_write_lock:
            try:
                with self._stats_lock:
                    self._operation_stats["reads"] += 1

                result = self._engine.get_context(
                    query,
                    k,
                    user,
                    similarity_threshold,
                    context_domains,
                    metadata_filter,
                )

                logger.debug(f"Context retrieved thread-safely for query: {query}")
                return result

            except Exception as e:
                with self._stats_lock:
                    self._operation_stats["errors"] += 1
                logger.error(f"Thread-safe context retrieval failed: {e}")
                raise

    def get_context_by_keys(self, keys: List[str], user: str = "system") -> List[str]:
        """Thread-safe context retrieval by keys"""
        with self._read_write_lock:
            try:
                with self._stats_lock:
                    self._operation_stats["reads"] += 1

                result = self._engine.get_context_by_keys(keys, user)
                logger.debug(
                    f"Context retrieved by keys thread-safely: {len(keys)} keys"
                )
                return result

            except Exception as e:
                with self._stats_lock:
                    self._operation_stats["errors"] += 1
                logger.error(f"Thread-safe context by keys retrieval failed: {e}")
                raise

    def build_focused_context(
        self,
        context_topics: List[str],
        max_tokens: int = 1000,
        max_per_topic: int = 2,
        user: str = "system",
        task_id: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Thread-safe focused context building"""
        with self._read_write_lock:
            try:
                with self._stats_lock:
                    self._operation_stats["reads"] += 1

                result = self._engine.build_focused_context(
                    context_topics,
                    max_tokens,
                    max_per_topic,
                    user,
                    task_id,
                    **kwargs,
                )

                logger.debug(
                    f"Focused context built thread-safely for {len(context_topics)} topics"
                )
                return result

            except Exception as e:
                with self._stats_lock:
                    self._operation_stats["errors"] += 1
                logger.error(f"Thread-safe focused context building failed: {e}")
                raise

    def secure_delete(self, file_path: str, user: str = "system") -> bool:
        """Thread-safe document deletion"""
        with self._document_lock:
            try:
                with self._stats_lock:
                    self._operation_stats["writes"] += 1

                result = self._engine.secure_delete(file_path, user)
                logger.debug(f"Document deleted thread-safely: {file_path}")
                return result

            except Exception as e:
                with self._stats_lock:
                    self._operation_stats["errors"] += 1
                logger.error(f"Thread-safe document deletion failed: {e}")
                raise

    def clear(self, user: str = "system") -> bool:
        """Thread-safe memory system clear"""
        with self._document_lock:
            with self._cache_lock:
                try:
                    with self._stats_lock:
                        self._operation_stats["writes"] += 1

                    result = self._engine.clear(user)
                    logger.info("Memory system cleared thread-safely")
                    return result

                except Exception as e:
                    with self._stats_lock:
                        self._operation_stats["errors"] += 1
                    logger.error(f"Thread-safe memory clear failed: {e}")
                    raise

    def get_stats(self) -> Dict[str, Any]:
        """Thread-safe statistics retrieval"""
        with self._stats_lock:
            with self._read_write_lock:
                try:
                    engine_stats = self._engine.get_stats()
                    thread_stats = {
                        "thread_safety": {
                            "enabled": True,
                            "operation_counts": self._operation_stats.copy(),
                            "locks": {
                                "read_write_lock": "active",
                                "document_lock": "active",
                                "cache_lock": "active",
                                "stats_lock": "active",
                            },
                        }
                    }

                    # Merge engine stats with thread safety stats
                    combined_stats = {**engine_stats, **thread_stats}
                    return combined_stats

                except Exception as e:
                    logger.error(f"Thread-safe stats retrieval failed: {e}")
                    return {
                        "error": str(e),
                        "thread_safety": {"enabled": True, "error": True},
                    }

    def get_documents(self, user: str = "system") -> List[Dict[str, Any]]:
        """Thread-safe document listing"""
        with self._read_write_lock:
            try:
                with self._stats_lock:
                    self._operation_stats["reads"] += 1

                result = self._engine.get_documents(user)
                logger.debug(f"Documents listed thread-safely: {len(result)} documents")
                return result

            except Exception as e:
                with self._stats_lock:
                    self._operation_stats["errors"] += 1
                logger.error(f"Thread-safe document listing failed: {e}")
                raise

    def index_health(self) -> Dict[str, Any]:
        """Thread-safe index health check"""
        with self._read_write_lock:
            try:
                health = self._engine.index_health()
                # Add thread safety status
                health["thread_safety"] = {
                    "enabled": True,
                    "locks_active": True,
                    "concurrent_operations_supported": True,
                }
                return health

            except Exception as e:
                logger.error(f"Thread-safe index health check failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "thread_safety": {"enabled": True, "error": True},
                }

    def shutdown(self):
        """Thread-safe shutdown"""
        with self._document_lock:
            with self._cache_lock:
                with self._read_write_lock:
                    try:
                        self._engine.shutdown()
                        logger.info("ThreadSafeMemoryEngine shut down successfully")
                    except Exception as e:
                        logger.error(f"Thread-safe shutdown failed: {e}")
                        raise


# Global thread-safe memory engine singleton
_memory_instance: Optional[ThreadSafeMemoryEngine] = None
_memory_lock = threading.RLock()


def get_thread_safe_memory_instance(
    config: Optional[MemoryEngineConfig] = None,
) -> ThreadSafeMemoryEngine:
    """
    Get the global thread-safe memory engine instance.
    Uses double-checked locking pattern for safe singleton initialization.

    Args:
        config: Optional memory engine configuration

    Returns:
        Thread-safe memory engine instance
    """
    global _memory_instance

    if _memory_instance is None:
        with _memory_lock:
            if _memory_instance is None:  # Double-check locking
                _memory_instance = ThreadSafeMemoryEngine(config)
                logger.info("Global thread-safe memory engine instance created")

    return _memory_instance


def reset_memory_instance():
    """Reset the global memory instance (primarily for testing)"""
    global _memory_instance
    with _memory_lock:
        if _memory_instance:
            try:
                _memory_instance.shutdown()
            except Exception as e:
                logger.warning(f"Error shutting down memory instance during reset: {e}")
        _memory_instance = None
        logger.info("Global memory instance reset")


class ThreadSafeContextManager:
    """
    Context manager for thread-safe memory operations with automatic cleanup.
    Provides transactional-like behavior for memory operations.
    """

    def __init__(
        self,
        memory_engine: ThreadSafeMemoryEngine,
        operation_type: str = "read",
    ):
        self.memory_engine = memory_engine
        self.operation_type = operation_type
        self.start_time = None
        self.success = False

    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting thread-safe {self.operation_type} operation")
        return self.memory_engine

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time if self.start_time else 0

        if exc_type is None:
            self.success = True
            logger.debug(
                f"Thread-safe {self.operation_type} operation completed successfully in {duration:.3f}s"
            )
        else:
            logger.error(
                f"Thread-safe {self.operation_type} operation failed after {duration:.3f}s: {exc_val}"
            )

        return False  # Don't suppress exceptions


def with_thread_safe_memory(operation_type: str = "read"):
    """
    Decorator for functions that need thread-safe memory access.

    Args:
        operation_type: Type of operation ('read', 'write', 'admin')
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            memory_engine = get_thread_safe_memory_instance()
            with ThreadSafeContextManager(memory_engine, operation_type):
                return func(memory_engine, *args, **kwargs)

        return wrapper

    return decorator


# Convenience functions for backward compatibility
def get_context_by_keys(keys: List[str], user: str = "system") -> List[str]:
    """Thread-safe convenience function for context retrieval by keys"""
    memory_engine = get_thread_safe_memory_instance()
    return memory_engine.get_context_by_keys(keys, user)


def get_relevant_context(query: str, k: int = 5, user: str = "system", **kwargs) -> str:
    """Thread-safe convenience function for context retrieval"""
    memory_engine = get_thread_safe_memory_instance()
    return memory_engine.get_context(query, k, user, **kwargs)
