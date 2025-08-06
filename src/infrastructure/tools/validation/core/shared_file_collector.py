
"""
Shared File Collector - Performance Optimization
Eliminates redundant directory traversals in validation pipeline.
"""

from src.infrastructure.utils.common_imports import Path, os, time
from threading import Lock
from typing import Dict, List, Optional, Any


class SharedFileCollector:
    """
    Singleton file collector that caches directory traversal results
    to eliminate redundant file system operations.
    """

    _instance = None
    _lock = Lock()
    _file_cache: Dict[str, Dict[str, List[Path]]] = {}
    _cache_timestamps: Dict[str, float] = {}
    _cache_ttl = 300  # 5 minutes cache TTL

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    # Assign _instance before recursion to prevent UnboundLocalError
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.excluded_dirs = {
                "__pycache__",
                ".git",
                ".pytest_cache",
                "htmlcov",
                "build",
                "dist",
                ".mypy_cache",
                ".tox",
                "venv",
                ".venv",  # Added missing .venv exclusion
                "env",
                ".env",   # Added .env exclusion for consistency
                "node_modules",
                ".next",
                ".nuxt",
                "backup",
                "archives",  # Added archives directory
                "test_outputs",  # Added test outputs
                ".coverage",  # Added coverage directory
            }
            # Clear any existing cache since exclusions changed
            self._file_cache.clear()
            self._cache_timestamps.clear()
            self._initialized = True

    def get_files(
        self, root_path: Path, force_refresh: bool = False
    ) -> Dict[str, List[Path]]:
        """
        Get cached file collections for a root path.

        Args:
            root_path: Root directory to scan
            force_refresh: Force cache refresh

        Returns:
            Dict with 'all_files' and 'python_files' keys
        """
        root_str = str(root_path.resolve())

        # Check cache validity
        if not force_refresh and self._is_cache_valid(root_str):
            return self._file_cache[root_str]

        # Perform file collection
        with self._lock:
            # Double-check after acquiring lock
            if not force_refresh and self._is_cache_valid(root_str):
                return self._file_cache[root_str]

            files = self._collect_files(root_path)
            self._file_cache[root_str] = files
            self._cache_timestamps[root_str] = time.time()

            return files

    def _is_cache_valid(self, root_str: str) -> bool:
        """Check if cache is valid for the given root path."""
        if root_str not in self._file_cache:
            return False

        if root_str not in self._cache_timestamps:
            return False

        # Check TTL
        elapsed = time.time() - self._cache_timestamps[root_str]
        return elapsed < self._cache_ttl

    def _collect_files(self, root_path: Path) -> Dict[str, List[Path]]:
        """
        Perform the actual file collection.

        Args:
            root_path: Root directory to scan

        Returns:
            Dict containing all_files and python_files lists
        """
        all_files = []
        python_files = []

        print(f"SharedFileCollector: Scanning {root_path}...")
        start_time = time.time()

        for root, dirs, files in os.walk(root_path):
            # Remove excluded directories in-place
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]

            for file in files:
                file_path = Path(root) / file
                all_files.append(file_path)

                if file.endswith(".py"):
                    python_files.append(file_path)

        elapsed = time.time() - start_time
        print(
            f"SharedFileCollector: Found {len(all_files)} files "
            f"({len(python_files)} Python) in {elapsed:.2f}s"
        )

        return {"all_files": all_files, "python_files": python_files}

    def clear_cache(self, root_path: Optional[Path] = None):
        """
        Clear cache for specific path or all paths.

        Args:
            root_path: Specific path to clear, or None for all
        """
        with self._lock:
            if root_path:
                root_str = str(root_path.resolve())
                self._file_cache.pop(root_str, None)
                self._cache_timestamps.pop(root_str, None)
            else:
                self._file_cache.clear()
                self._cache_timestamps.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            stats = {
                "cached_paths": len(self._file_cache),
                "total_files": sum(
                    len(files["all_files"]) for files in self._file_cache.values()
                ),
                "total_python_files": sum(
                    len(files["python_files"]) for files in self._file_cache.values()
                ),
                "cache_entries": [],
            }

            current_time = time.time()
            for root_str, files in self._file_cache.items():
                timestamp = self._cache_timestamps.get(root_str, 0)
                age = current_time - timestamp

                stats["cache_entries"].append(
                    {
                        "path": root_str,
                        "all_files": len(files["all_files"]),
                        "python_files": len(files["python_files"]),
                        "age_seconds": age,
                        "valid": age < self._cache_ttl,
                    }
                )

            return stats


# Global instance for easy access
shared_file_collector = SharedFileCollector()
