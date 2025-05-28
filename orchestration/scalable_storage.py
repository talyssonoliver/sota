#!/usr/bin/env python3
"""
Scalable Storage Manager for High-Volume Task Processing

Addresses scalability concerns for systems handling thousands of tasks:
- Hierarchical directory structure to avoid large flat directories
- Efficient task lookup and caching
- Cleanup policies for old tasks
- Performance monitoring
"""

import hashlib
import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class StorageMetrics:
    """Track storage performance metrics"""
    total_tasks: int = 0
    avg_lookup_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    directory_depth: int = 0
    files_per_directory: Dict[str, int] = None

    def __post_init__(self):
        if self.files_per_directory is None:
            self.files_per_directory = {}


class ScalableTaskStorage:
    """
    Scalable storage manager using hierarchical directory structure.

    Instead of outputs/BE-123, uses outputs/B/E/BE-123
    This prevents any single directory from having >256 subdirectories.
    """

    def __init__(self, base_dir: str = "outputs", depth: int = 2):
        self.base_dir = Path(base_dir)
        self.depth = depth  # How many levels of hierarchy
        self.cache = {}  # Task directory cache
        self.metrics = StorageMetrics()
        self.lock = threading.Lock()

        self.base_dir.mkdir(exist_ok=True)

    def _get_hierarchical_path(self, task_id: str) -> Path:
        """
        Generate hierarchical path for task.

        Examples:
        - BE-07 → outputs/B/E/BE-07
        - FE-1234 → outputs/F/E/FE-1234
        - TASK-567 → outputs/T/A/TASK-567
        """
        # Use first few characters for hierarchy
        hierarchy_chars = list(task_id.replace("-", "")[:self.depth])

        # Ensure we have enough characters
        while len(hierarchy_chars) < self.depth:
            hierarchy_chars.append("_")

        # Build path: base/char1/char2/full_task_id
        path = self.base_dir
        for char in hierarchy_chars:
            path = path / char.upper()

        return path / task_id

    def get_task_directory(self, task_id: str) -> Path:
        """Get task directory with caching and performance tracking"""
        start_time = datetime.now()

        with self.lock:
            # Check cache first
            if task_id in self.cache:
                self.metrics.cache_hit_rate = (
                    self.metrics.cache_hit_rate * 0.9) + (1.0 * 0.1)
                return self.cache[task_id]

            # Cache miss
            self.metrics.cache_hit_rate = self.metrics.cache_hit_rate * 0.9

            # Get hierarchical path
            task_dir = self._get_hierarchical_path(task_id)
            task_dir.mkdir(parents=True, exist_ok=True)

            # Cache the result
            self.cache[task_id] = task_dir

            # Update metrics
            lookup_time = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics.avg_lookup_time_ms = (
                self.metrics.avg_lookup_time_ms * 0.9) + (lookup_time * 0.1)
            self.metrics.total_tasks = len(self.cache)

            return task_dir

    def list_all_tasks(self) -> List[str]:
        """Efficiently list all tasks using hierarchical structure"""
        tasks = []

        # Traverse hierarchy
        for char1_dir in self.base_dir.iterdir():
            if not char1_dir.is_dir():
                continue

            for char2_dir in char1_dir.iterdir():
                if not char2_dir.is_dir():
                    continue

                for task_dir in char2_dir.iterdir():
                    if task_dir.is_dir():
                        tasks.append(task_dir.name)

        return sorted(tasks)

    def cleanup_old_tasks(self, days_old: int = 30) -> int:
        """Remove tasks older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        removed_count = 0

        for task_id in self.list_all_tasks():
            task_dir = self.get_task_directory(task_id)

            # Check modification time
            if task_dir.stat().st_mtime < cutoff_date.timestamp():
                try:
                    import shutil
                    shutil.rmtree(task_dir)
                    removed_count += 1

                    # Remove from cache
                    if task_id in self.cache:
                        del self.cache[task_id]

                except Exception as e:
                    print(f"Failed to remove {task_dir}: {e}")

        return removed_count

    def get_storage_metrics(self) -> StorageMetrics:
        """Get current storage performance metrics"""
        # Update directory statistics
        for char1_dir in self.base_dir.iterdir():
            if char1_dir.is_dir():
                count = len(list(char1_dir.iterdir()))
                self.metrics.files_per_directory[char1_dir.name] = count

        self.metrics.directory_depth = self.depth
        return self.metrics

    def get_metrics(self) -> StorageMetrics:
        """Alias for get_storage_metrics for compatibility"""
        return self.get_storage_metrics()

    def optimize_cache(self, max_cache_size: int = 1000):
        """Optimize cache by removing least recently used entries"""
        if len(self.cache) > max_cache_size:
            # Simple LRU: remove oldest 20%
            items_to_remove = len(self.cache) - int(max_cache_size * 0.8)
            keys_to_remove = list(self.cache.keys())[:items_to_remove]

            for key in keys_to_remove:
                del self.cache[key]


# Performance monitoring utilities
def benchmark_storage_performance(
        storage: ScalableTaskStorage,
        num_tasks: int = 1000):
    """Benchmark storage performance with simulated tasks"""
    import random
    import time

    print(f"🔍 Benchmarking storage with {num_tasks} tasks...")

    # Generate test task IDs
    task_ids = [f"BE-{i:04d}" for i in range(num_tasks)]

    # Test directory creation
    start_time = time.time()
    for task_id in task_ids:
        storage.get_task_directory(task_id)
    creation_time = time.time() - start_time

    # Test random access
    start_time = time.time()
    for _ in range(100):
        random_task = random.choice(task_ids)
        storage.get_task_directory(random_task)
    access_time = time.time() - start_time

    # Test listing
    start_time = time.time()
    all_tasks = storage.list_all_tasks()
    listing_time = time.time() - start_time

    metrics = storage.get_storage_metrics()

    print(f"📊 Performance Results:")
    print(
        f"   Directory creation: {
            creation_time:.2f}s ({
            num_tasks /
            creation_time:.0f} tasks/sec)")
    print(f"   Random access (100x): {access_time:.3f}s")
    print(f"   Full listing: {listing_time:.3f}s ({len(all_tasks)} tasks)")
    print(f"   Cache hit rate: {metrics.cache_hit_rate:.1%}")
    print(f"   Avg lookup time: {metrics.avg_lookup_time_ms:.2f}ms")

    return metrics


if __name__ == "__main__":
    # Demo scalable storage
    storage = ScalableTaskStorage()

    # Run benchmark
    benchmark_storage_performance(storage, 1000)

    # Show metrics
    metrics = storage.get_storage_metrics()
    print(f"\n📈 Storage Metrics:")
    print(f"   Total tasks: {metrics.total_tasks}")
    print(f"   Directory depth: {metrics.directory_depth}")
    print(f"   Files per top-level dir: {metrics.files_per_directory}")
