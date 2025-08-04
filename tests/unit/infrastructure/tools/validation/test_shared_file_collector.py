"""
Tests for shared file collector - Performance optimization utility.
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from src.infrastructure.tools.validation.core.shared_file_collector import (
    SharedFileCollector
)


class TestSharedFileCollector:
    """Test cases for SharedFileCollector class."""

    @classmethod
    def setup_class(cls):
        """Set up class-level fixtures for performance."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.root_path = Path(cls.temp_dir)
        # Create test directory structure once for all tests
        cls.create_test_structure()

    def setup_method(self):
        """Set up test fixtures."""
        # Use class-level temp directory
        self.temp_dir = self.__class__.temp_dir
        self.root_path = self.__class__.root_path
        
        # Clear any existing cache before each test
        SharedFileCollector._file_cache.clear()
        SharedFileCollector._cache_timestamps.clear()
        
        # Create fresh instance for testing
        SharedFileCollector._instance = None
        self.collector = SharedFileCollector()

    @classmethod
    def create_test_structure(cls):
        """Create a test directory structure."""
        # Create Python files
        (cls.root_path / "module1.py").write_text("# Module 1")
        (cls.root_path / "module2.py").write_text("# Module 2")
        
        # Create subdirectory with Python files
        subdir = cls.root_path / "subpackage"
        subdir.mkdir()
        (subdir / "__init__.py").write_text("# Init file")
        (subdir / "submodule.py").write_text("# Submodule")
        
        # Create non-Python files
        (cls.root_path / "readme.txt").write_text("README")
        (cls.root_path / "config.json").write_text('{"test": true}')
        
        # Create excluded directories
        excluded_dir = cls.root_path / "__pycache__"
        excluded_dir.mkdir()
        (excluded_dir / "module1.pyc").write_text("Compiled Python")
        
        git_dir = cls.root_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("Git config")
        
        # Create another excluded directory with Python files (should be ignored)
        venv_dir = cls.root_path / "venv"
        venv_dir.mkdir()
        venv_lib = venv_dir / "lib"
        venv_lib.mkdir()
        (venv_lib / "external.py").write_text("# External library")

    def test_singleton_pattern(self):
        """Test that SharedFileCollector implements singleton pattern."""
        collector1 = SharedFileCollector()
        collector2 = SharedFileCollector()
        
        assert collector1 is collector2
        assert id(collector1) == id(collector2)

    def test_singleton_with_global_instance(self):
        """Test that global instance follows singleton pattern."""
        # Reset singleton for this test
        SharedFileCollector._instance = None
        
        collector1 = SharedFileCollector()
        
        # Create a new global instance after reset  
        global_collector = SharedFileCollector()
        
        # They should be the same instance
        assert global_collector is collector1

    def test_initialization(self):
        """Test collector initialization."""
        assert hasattr(self.collector, 'excluded_dirs')
        assert isinstance(self.collector.excluded_dirs, set)
        assert '__pycache__' in self.collector.excluded_dirs
        assert '.git' in self.collector.excluded_dirs
        assert 'venv' in self.collector.excluded_dirs

    def test_get_files_first_time(self):
        """Test file collection on first call."""
        with patch('builtins.print') as mock_print:
            files = self.collector.get_files(self.root_path)
        
        # Should return dict with expected keys
        assert isinstance(files, dict)
        assert 'all_files' in files
        assert 'python_files' in files
        
        # Check file lists
        all_files = files['all_files']
        python_files = files['python_files']
        
        assert isinstance(all_files, list)
        assert isinstance(python_files, list)
        assert len(python_files) > 0
        assert len(all_files) >= len(python_files)
        
        # Check that Python files are actually Python files
        for py_file in python_files:
            assert str(py_file).endswith('.py')
        
        # Check that excluded directories are not included
        file_paths_str = [str(f) for f in all_files]
        assert not any('__pycache__' in path for path in file_paths_str)
        assert not any('.git' in path for path in file_paths_str)
        assert not any('venv' in path for path in file_paths_str)
        
        # Should have printed scanning message
        mock_print.assert_called()
        print_args = [call[0][0] for call in mock_print.call_args_list]
        assert any('Scanning' in arg for arg in print_args)
        assert any('Found' in arg for arg in print_args)

    def test_get_files_cached(self):
        """Test file collection returns cached results."""
        # First call
        files1 = self.collector.get_files(self.root_path)
        
        # Mock the _collect_files method to ensure it's not called again
        with patch.object(self.collector, '_collect_files') as mock_collect:
            # Second call should use cache
            files2 = self.collector.get_files(self.root_path)
            
            # Should not have called _collect_files
            mock_collect.assert_not_called()
            
            # Should return same results
            assert files1 == files2

    def test_get_files_force_refresh(self):
        """Test force refresh bypasses cache."""
        # First call
        files1 = self.collector.get_files(self.root_path)
        
        # Mock _collect_files to return different results
        with patch.object(self.collector, '_collect_files') as mock_collect:
            mock_collect.return_value = {
                'all_files': [Path('fake.py')],
                'python_files': [Path('fake.py')]
            }
            
            # Force refresh should call _collect_files
            files2 = self.collector.get_files(self.root_path, force_refresh=True)
            
            mock_collect.assert_called_once()
            assert files2 != files1

    def test_cache_validity(self):
        """Test cache validity checking."""
        root_str = str(self.root_path.resolve())
        
        # Initially cache should be invalid
        assert not self.collector._is_cache_valid(root_str)
        
        # Add to cache
        test_files = {'all_files': [], 'python_files': []}
        self.collector._file_cache[root_str] = test_files
        self.collector._cache_timestamps[root_str] = time.time()
        
        # Now should be valid
        assert self.collector._is_cache_valid(root_str)
        
        # Test expired cache
        old_time = time.time() - (self.collector._cache_ttl + 10)
        self.collector._cache_timestamps[root_str] = old_time
        
        # Should be invalid now
        assert not self.collector._is_cache_valid(root_str)

    def test_cache_validity_missing_timestamp(self):
        """Test cache validity with missing timestamp."""
        root_str = str(self.root_path.resolve())
        
        # Add to cache but no timestamp
        test_files = {'all_files': [], 'python_files': []}
        self.collector._file_cache[root_str] = test_files
        
        # Should be invalid without timestamp
        assert not self.collector._is_cache_valid(root_str)

    def test_collect_files_method(self):
        """Test the _collect_files method directly."""
        with patch('builtins.print') as mock_print:
            files = self.collector._collect_files(self.root_path)
        
        assert isinstance(files, dict)
        assert 'all_files' in files
        assert 'python_files' in files
        
        # Check specific files we created
        all_file_names = [f.name for f in files['all_files']]
        python_file_names = [f.name for f in files['python_files']]
        
        assert 'module1.py' in python_file_names
        assert 'module2.py' in python_file_names
        assert '__init__.py' in python_file_names
        assert 'submodule.py' in python_file_names
        
        assert 'readme.txt' in all_file_names
        assert 'config.json' in all_file_names
        
        # Should not include files from excluded directories
        assert 'module1.pyc' not in all_file_names
        assert 'external.py' not in python_file_names

    def test_excluded_directories_filtering(self):
        """Test that excluded directories are properly filtered."""
        files = self.collector.get_files(self.root_path)
        
        # Convert to strings for easier checking
        all_paths = [str(f) for f in files['all_files']]
        python_paths = [str(f) for f in files['python_files']]
        
        # None of the paths should contain excluded directories
        for excluded in self.collector.excluded_dirs:
            assert not any(excluded in path for path in all_paths)
            assert not any(excluded in path for path in python_paths)

    def test_clear_cache_specific_path(self):
        """Test clearing cache for specific path."""
        # Populate cache
        files = self.collector.get_files(self.root_path)
        root_str = str(self.root_path.resolve())
        
        assert root_str in self.collector._file_cache
        assert root_str in self.collector._cache_timestamps
        
        # Clear cache for specific path
        self.collector.clear_cache(self.root_path)
        
        assert root_str not in self.collector._file_cache
        assert root_str not in self.collector._cache_timestamps

    def test_clear_cache_all(self):
        """Test clearing all cache."""
        # Populate cache
        files = self.collector.get_files(self.root_path)
        
        # Add another entry
        other_path = Path(tempfile.mkdtemp())
        other_files = self.collector.get_files(other_path)
        
        assert len(self.collector._file_cache) >= 2
        assert len(self.collector._cache_timestamps) >= 2
        
        # Clear all cache
        self.collector.clear_cache()
        
        assert len(self.collector._file_cache) == 0
        assert len(self.collector._cache_timestamps) == 0

    def test_get_cache_stats(self):
        """Test cache statistics."""
        # Initially empty
        stats = self.collector.get_cache_stats()
        assert stats['cached_paths'] == 0
        assert stats['total_files'] == 0
        assert stats['total_python_files'] == 0
        assert stats['cache_entries'] == []
        
        # Populate cache
        files = self.collector.get_files(self.root_path)
        
        stats = self.collector.get_cache_stats()
        assert stats['cached_paths'] == 1
        assert stats['total_files'] > 0
        assert stats['total_python_files'] > 0
        assert len(stats['cache_entries']) == 1
        
        # Check cache entry details
        entry = stats['cache_entries'][0]
        assert 'path' in entry
        assert 'all_files' in entry
        assert 'python_files' in entry
        assert 'age_seconds' in entry
        assert 'valid' in entry
        assert entry['valid'] is True  # Should be valid initially

    def test_cache_stats_with_expired_entry(self):
        """Test cache statistics with expired entries."""
        # Populate cache
        files = self.collector.get_files(self.root_path)
        
        # Manually set old timestamp
        root_str = str(self.root_path.resolve())
        old_time = time.time() - (self.collector._cache_ttl + 10)
        self.collector._cache_timestamps[root_str] = old_time
        
        stats = self.collector.get_cache_stats()
        entry = stats['cache_entries'][0]
        assert entry['valid'] is False

    def test_threading_safety(self):
        """Test basic threading safety of singleton creation."""
        import threading
        
        instances = []
        
        def create_instance():
            instances.append(SharedFileCollector())
        
        # Create multiple instances in parallel
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_instance)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All instances should be the same
        first_instance = instances[0]
        for instance in instances[1:]:
            assert instance is first_instance

    def test_concurrent_file_access(self):
        """Test concurrent access to file collection."""
        import threading
        
        results = []
        
        def collect_files():
            files = self.collector.get_files(self.root_path)
            results.append(files)
        
        # Access files concurrently
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=collect_files)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All results should be identical (cached)
        first_result = results[0]
        for result in results[1:]:
            assert result == first_result

    def test_large_directory_structure(self):
        """Test performance with larger directory structure."""
        # Create larger test structure
        large_dir = self.root_path / "large_test"
        large_dir.mkdir()
        
        # Create many files
        for i in range(50):
            (large_dir / f"module_{i}.py").write_text(f"# Module {i}")
            (large_dir / f"data_{i}.txt").write_text(f"Data {i}")
        
        # Create subdirectories
        for i in range(10):
            sub = large_dir / f"sub_{i}"
            sub.mkdir()
            for j in range(5):
                (sub / f"file_{j}.py").write_text(f"# File {j}")
        
        start_time = time.time()
        files = self.collector.get_files(large_dir)
        duration = time.time() - start_time
        
        # Should complete reasonably quickly
        assert duration < 5.0  # Adjust threshold as needed
        assert len(files['python_files']) > 50

    def test_empty_directory(self):
        """Test file collection on empty directory."""
        empty_dir = Path(tempfile.mkdtemp())
        
        files = self.collector.get_files(empty_dir)
        
        assert files['all_files'] == []
        assert files['python_files'] == []

    def test_nonexistent_directory(self):
        """Test file collection on non-existent directory."""
        nonexistent = self.root_path / "nonexistent"
        
        # Should handle gracefully (os.walk handles this)
        files = self.collector.get_files(nonexistent)
        
        # Should return empty results
        assert files['all_files'] == []
        assert files['python_files'] == []

    def test_symlinks_handling(self):
        """Test handling of symbolic links."""
        # Create a symlink if the OS supports it
        try:
            link_target = self.root_path / "module1.py"
            link_path = self.root_path / "link_to_module.py"
            link_path.symlink_to(link_target)
            
            files = self.collector.get_files(self.root_path)
            
            # Should include both original and symlink
            file_names = [f.name for f in files['python_files']]
            assert 'module1.py' in file_names
            assert 'link_to_module.py' in file_names
            
        except (OSError, NotImplementedError):
            # Skip test if symlinks not supported
            pytest.skip("Symlinks not supported on this system")

    def test_cache_ttl_configuration(self):
        """Test cache TTL configuration."""
        original_ttl = SharedFileCollector._cache_ttl
        
        try:
            # Set very short TTL
            SharedFileCollector._cache_ttl = 0.1
            
            # Get files
            files1 = self.collector.get_files(self.root_path)
            
            # Wait for cache to expire
            time.sleep(0.2)
            
            # Mock _collect_files to verify it's called again
            with patch.object(self.collector, '_collect_files') as mock_collect:
                mock_collect.return_value = {
                    'all_files': [],
                    'python_files': []
                }
                
                files2 = self.collector.get_files(self.root_path)
                
                # Should have called _collect_files due to expired cache
                mock_collect.assert_called_once()
                
        finally:
            # Restore original TTL
            SharedFileCollector._cache_ttl = original_ttl

    def test_path_resolution(self):
        """Test that paths are properly resolved for caching."""
        # Test with relative path
        rel_path = Path(".")
        abs_path = rel_path.resolve()
        
        # Mock the expensive file collection operation
        mock_files = ['file1.py', 'file2.py']
        with patch.object(self.collector, '_collect_files', return_value=mock_files) as mock_collect1:
            # Both should use the same cache entry
            files1 = self.collector.get_files(rel_path)
            assert files1 == mock_files
            
            with patch.object(self.collector, '_collect_files') as mock_collect2:
                files2 = self.collector.get_files(abs_path)
                
                # Should not call _collect_files (cache hit)
                mock_collect2.assert_not_called()
                assert files2 == files1

    def test_file_extension_filtering(self):
        """Test that only .py files are included in python_files."""
        # Create files with various Python-related extensions
        (self.root_path / "script.py").write_text("# Python script")
        (self.root_path / "compiled.pyc").write_text("Compiled")
        (self.root_path / "optimized.pyo").write_text("Optimized")
        (self.root_path / "template.pyt").write_text("Template")
        (self.root_path / "notebook.ipynb").write_text('{"cells": []}')
        
        files = self.collector.get_files(self.root_path)
        
        python_names = [f.name for f in files['python_files']]
        all_names = [f.name for f in files['all_files']]
        
        # Only .py files should be in python_files
        assert 'script.py' in python_names
        assert 'compiled.pyc' not in python_names
        assert 'optimized.pyo' not in python_names
        assert 'template.pyt' not in python_names
        assert 'notebook.ipynb' not in python_names
        
        # But all files should be in all_files
        assert 'script.py' in all_names
        assert 'compiled.pyc' in all_names
        assert 'optimized.pyo' in all_names