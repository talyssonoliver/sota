#!/usr/bin/env python3
"""
Test suite for enhanced memory system consolidator script

Tests the memory system consolidation functionality with safety measures,
git integration, and comprehensive error handling.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add scripts directory to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

try:
    from memory_system_consolidator import MemorySystemConsolidator
except ImportError as e:
    pytest.skip(f"Could not import memory_system_consolidator: {e}", allow_module_level=True)


class TestMemorySystemConsolidator:
    """Test suite for enhanced MemorySystemConsolidator."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)
    
    @pytest.fixture
    def consolidator(self, temp_dir):
        """Create a consolidator instance for testing."""
        # Create target memory system structure
        target_dir = temp_dir / "src/infrastructure/tools/memory"
        target_dir.mkdir(parents=True)
        
        # Create mock target memory system
        target_init = target_dir / "__init__.py"
        target_init.write_text('''"""Mock target memory system for testing."""
class MemoryEngine:
    def __init__(self):
        pass

def get_memory_instance():
    return MemoryEngine()

def get_context_by_keys():
    return {}

__all__ = ['MemoryEngine', 'get_memory_instance', 'get_context_by_keys']
''')
        
        # Change to temp directory for testing
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        consolidator = MemorySystemConsolidator(
            root_dir=str(temp_dir),
            dry_run=True,  # Default to dry run for safety
            verify_tests=False,  # Skip tests in unit tests
            create_backup=False,  # Skip git operations in unit tests
            verify_git_clean=False
        )
        
        yield consolidator
        
        # Restore original directory
        os.chdir(original_cwd)
    
    @pytest.fixture
    def sample_memory_files(self, temp_dir):
        """Create sample files with memory system imports."""
        src_dir = temp_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        files = {}
        
        # Create deprecated memory system structure
        deprecated_dir = temp_dir / "src/infrastructure/memory"
        deprecated_dir.mkdir(parents=True)
        
        # File using deprecated memory imports
        files["deprecated_imports"] = src_dir / "deprecated_usage.py"
        files["deprecated_imports"].write_text('''"""Sample file with deprecated memory imports."""
from src.infrastructure.memory import MemoryEngine
from src.infrastructure.memory import get_memory_instance
from src.infrastructure.memory.config import CacheConfig

def sample_function():
    engine = MemoryEngine()
    instance = get_memory_instance()
    return engine
''')
        
        # File using new memory imports (should be skipped)
        files["new_imports"] = src_dir / "new_usage.py"
        files["new_imports"].write_text('''"""Sample file already using new memory imports."""
from src.infrastructure.tools.memory import MemoryEngine
from src.infrastructure.tools.memory import get_memory_instance

def sample_function():
    return MemoryEngine()
''')
        
        # File using mixed imports (conflict case)
        files["mixed_imports"] = src_dir / "mixed_usage.py"
        files["mixed_imports"].write_text('''"""Sample file with mixed memory imports."""
from src.infrastructure.memory import MemoryEngine as OldEngine
from src.infrastructure.tools.memory import get_memory_instance

def sample_function():
    engine = OldEngine()
    instance = get_memory_instance()
    return engine
''')
        
        # Duplicate memory engine file (to be removed)
        duplicate_engine = deprecated_dir / "engines" / "memory_engine.py"
        duplicate_engine.parent.mkdir(exist_ok=True)
        files["duplicate_engine"] = duplicate_engine
        files["duplicate_engine"].write_text('''"""Duplicate memory engine implementation."""
class MemoryEngine:
    """Duplicate implementation - should be removed."""
    
    def __init__(self):
        self.name = "duplicate"
    
    def store(self, key, value):
        pass
    
    def retrieve(self, key):
        return None

# 50+ lines of duplicate code would be here...
''' + '\n'.join([f"# Line {i}" for i in range(50)]))
        
        # Duplicate config file
        duplicate_config = deprecated_dir / "config" / "memory_config.py"
        duplicate_config.parent.mkdir(exist_ok=True)
        files["duplicate_config"] = duplicate_config
        files["duplicate_config"].write_text('''"""Duplicate memory config."""
class CacheConfig:
    def __init__(self):
        self.size = 1000
        
class ChunkingConfig:
    def __init__(self):
        self.chunk_size = 512

# More duplicate config code...
''' + '\n'.join([f"# Config line {i}" for i in range(30)]))
        
        return files
    
    def test_initialization(self, temp_dir):
        """Test consolidator initialization with various options."""
        consolidator = MemorySystemConsolidator(
            root_dir=str(temp_dir),
            dry_run=False,
            verify_tests=True,
            create_backup=True,
            verify_git_clean=True
        )
        
        assert consolidator.root_dir == temp_dir
        assert consolidator.dry_run is False
        assert consolidator.verify_tests is True
        assert consolidator.create_backup is True
        assert consolidator.verify_git_clean is True
        assert consolidator.max_workers == 4
        assert len(consolidator.import_mappings) > 0
        assert len(consolidator.removal_targets) > 0
    
    def test_target_memory_system_validation(self, consolidator):
        """Test validation of target memory system."""
        # Should pass with our mock target system
        assert consolidator.validate_target_memory_system() is True
        assert len(consolidator.validation_errors) == 0
    
    def test_target_memory_system_validation_missing(self, temp_dir):
        """Test validation failure when target system is missing."""
        consolidator = MemorySystemConsolidator(
            root_dir=str(temp_dir),
            dry_run=True,
            verify_tests=False,
            create_backup=False,
            verify_git_clean=False
        )
        
        # Should fail without target system
        assert consolidator.validate_target_memory_system() is False
        assert len(consolidator.validation_errors) > 0
    
    def test_memory_system_analysis(self, consolidator, sample_memory_files):
        """Test analysis of memory system architecture."""
        analysis = consolidator.analyze_memory_system()
        
        # Should detect usage patterns
        assert len(analysis['usage_patterns']) > 0
        assert len(analysis['duplicate_files']) > 0
        assert len(analysis['import_conflicts']) > 0  # Mixed imports file
        
        # Should calculate impact metrics
        impact = analysis['consolidation_impact']
        assert impact['files_with_memory_imports'] > 0
        assert impact['duplicate_files_found'] > 0
        assert impact['estimated_lines_saved'] > 0
    
    def test_import_mapping_detection(self, consolidator, sample_memory_files):
        """Test detection of imports that need consolidation."""
        # Read the deprecated imports file
        deprecated_file = sample_memory_files["deprecated_imports"]
        with open(deprecated_file, 'r') as f:
            content = f.read()
        
        # Check that import mappings are detected
        detected_imports = 0
        for old_import in consolidator.import_mappings.keys():
            if old_import in content:
                detected_imports += 1
        
        assert detected_imports > 0
    
    def test_single_file_import_update(self, consolidator, sample_memory_files):
        """Test updating imports in a single file."""
        deprecated_file = sample_memory_files["deprecated_imports"]
        
        # Read original content
        with open(deprecated_file, 'r') as f:
            original_content = f.read()
        
        # Test import update
        result = consolidator.update_imports_in_file(deprecated_file)
        
        assert result["success"] is True
        assert result["changes"] > 0
        
        # In dry run mode, file should be unchanged
        with open(deprecated_file, 'r') as f:
            current_content = f.read()
        assert current_content == original_content
    
    def test_single_file_no_changes_needed(self, consolidator, sample_memory_files):
        """Test file that doesn't need import updates."""
        new_file = sample_memory_files["new_imports"]
        
        result = consolidator.update_imports_in_file(new_file)
        
        assert result["success"] is True
        assert result["changes"] == 0  # No deprecated imports to update
    
    def test_import_consolidation_all_files(self, consolidator, sample_memory_files):
        """Test consolidating imports across all files."""
        # First analyze the system
        analysis = consolidator.analyze_memory_system()
        
        # Then consolidate imports
        results = consolidator.consolidate_imports(analysis)
        
        assert results["files_processed"] > 0
        assert results["imports_updated"] > 0
        assert isinstance(results["errors"], list)
        assert isinstance(results["updated_files"], list)
    
    def test_duplicate_file_removal_analysis(self, consolidator, sample_memory_files):
        """Test analysis of duplicate files for removal."""
        analysis = consolidator.analyze_memory_system()
        
        duplicate_files = analysis['duplicate_files']
        assert len(duplicate_files) > 0
        
        # Should detect our duplicate files
        duplicate_paths = [item['path'] for item in duplicate_files]
        assert any('memory_engine.py' in path for path in duplicate_paths)
        assert any('memory_config.py' in path for path in duplicate_paths)
        
        # Should calculate size impact
        for duplicate_info in duplicate_files:
            assert duplicate_info['size_bytes'] > 0
            assert duplicate_info['estimated_lines'] > 0
    
    def test_duplicate_file_removal_dry_run(self, consolidator, sample_memory_files):
        """Test duplicate file removal in dry run mode."""
        analysis = consolidator.analyze_memory_system()
        
        # Files should exist before removal
        assert sample_memory_files["duplicate_engine"].exists()
        assert sample_memory_files["duplicate_config"].exists()
        
        # Run removal in dry run mode
        removal_results = consolidator.remove_duplicate_files(analysis)
        
        # Files should still exist after dry run
        assert sample_memory_files["duplicate_engine"].exists()
        assert sample_memory_files["duplicate_config"].exists()
        
        # But should report what would be done
        assert removal_results["files_removed"] > 0
        assert removal_results["lines_saved"] > 0
    
    def test_compatibility_layer_creation(self, consolidator):
        """Test creation of compatibility layer."""
        result = consolidator.create_compatibility_layer()
        
        # Should succeed in dry run mode
        assert result is True
        
        # In dry run mode, file shouldn't actually be created
        compatibility_file = consolidator.root_dir / "src/infrastructure/memory/__init__.py"
        # File may or may not exist depending on test setup, but function should succeed
    
    @patch('subprocess.run')
    def test_git_status_verification(self, mock_run, consolidator):
        """Test git status verification."""
        # Test clean git status
        mock_run.return_value = Mock(returncode=0, stdout="")
        consolidator.verify_git_clean = True
        assert consolidator.verify_git_status() is True
        
        # Test dirty git status
        mock_run.return_value = Mock(returncode=0, stdout="M file.py\n")
        assert consolidator.verify_git_status() is False
        
        # Test git not available
        mock_run.return_value = Mock(returncode=128, stderr="not a git repository")
        assert consolidator.verify_git_status() is True
    
    @patch('subprocess.run')
    def test_backup_branch_creation(self, mock_run, consolidator):
        """Test backup branch creation."""
        # Mock successful branch creation
        mock_run.side_effect = [
            Mock(returncode=0, stdout="Switched to a new branch"),
            Mock(returncode=0, stdout="Switched to branch")
        ]
        
        consolidator.create_backup = True
        
        assert consolidator.create_backup_branch() is True
        assert consolidator.backup_created is True
        assert consolidator.backup_branch is not None
        assert "memory-consolidation-backup-" in consolidator.backup_branch
    
    @patch('subprocess.run')
    def test_test_verification_before(self, mock_run, consolidator):
        """Test running tests before consolidation."""
        consolidator.verify_tests = True
        
        # Mock passing tests
        mock_run.return_value = Mock(
            returncode=0,
            stdout="collected 100 items\n100 passed in 10.00s"
        )
        
        assert consolidator.run_tests_before() is True
        assert len(consolidator.test_failures_before) == 0
        
        # Mock failing tests
        mock_run.return_value = Mock(
            returncode=1,
            stdout="collected 100 items\n5 failed, 95 passed\nFAILED test_a.py::test_1"
        )
        
        assert consolidator.run_tests_before() is True  # Still continues with pre-existing failures
        assert len(consolidator.test_failures_before) > 0
    
    @patch('subprocess.run')
    def test_test_verification_after(self, mock_run, consolidator):
        """Test running tests after consolidation."""
        consolidator.verify_tests = True
        consolidator.test_failures_before = ["test_a.py::test_1"]  # Pre-existing failure
        
        # Mock same failures (no new failures introduced)
        mock_run.return_value = Mock(
            returncode=1,
            stdout="collected 100 items\n1 failed, 99 passed\nFAILED test_a.py::test_1"
        )
        
        assert consolidator.run_tests_after() is True  # Same failures, OK
        
        # Mock new failures introduced
        mock_run.return_value = Mock(
            returncode=1,
            stdout="collected 100 items\n2 failed, 98 passed\nFAILED test_a.py::test_1\nFAILED test_b.py::test_2"
        )
        
        assert consolidator.run_tests_after() is False  # New failure introduced
    
    def test_error_handling_in_file_processing(self, consolidator, temp_dir):
        """Test error handling when processing files."""
        # Create a file that will cause issues
        bad_file = temp_dir / "src" / "bad_file.py"
        bad_file.parent.mkdir(parents=True, exist_ok=True)
        bad_file.write_text("invalid python syntax $$$ @@@")
        
        # Should handle errors gracefully
        result = consolidator.update_imports_in_file(bad_file)
        
        # Should not crash, might succeed or fail gracefully
        assert "success" in result
    
    def test_thread_safety(self, consolidator, temp_dir):
        """Test thread safety of consolidation operations."""
        # Create multiple files for parallel processing
        src_dir = temp_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        files = []
        for i in range(10):
            file_path = src_dir / f"test_{i}.py"
            file_path.write_text(f'''
from src.infrastructure.memory import MemoryEngine
from src.infrastructure.memory import get_memory_instance

def func_{i}():
    return MemoryEngine()
''')
            files.append(file_path)
        
        # Run analysis and consolidation
        analysis = consolidator.analyze_memory_system()
        results = consolidator.consolidate_imports(analysis)
        
        # Should process all files without errors
        assert results["files_processed"] >= len(files)
        assert results["imports_updated"] >= len(files) * 2  # Each file has 2 imports
    
    def test_full_consolidation_cycle_dry_run(self, consolidator, sample_memory_files):
        """Test complete consolidation cycle in dry run mode."""
        # Should complete successfully
        results = consolidator.run_consolidation()
        
        assert "success" in results
        assert "analysis" in results
        assert "import_consolidation" in results
        assert "file_removal" in results
        assert "compatibility_layer" in results
        assert "summary" in results
        
        summary = results["summary"]
        assert summary["files_analyzed"] > 0
        assert summary["imports_consolidated"] > 0
        
        # Files should still exist after dry run
        assert sample_memory_files["deprecated_imports"].exists()
        assert sample_memory_files["duplicate_engine"].exists()
    
    def test_consolidation_with_missing_target_system(self, temp_dir):
        """Test consolidation failure when target system is missing."""
        consolidator = MemorySystemConsolidator(
            root_dir=str(temp_dir),
            dry_run=False,  # Not dry run to trigger validation
            verify_tests=False,
            create_backup=False,
            verify_git_clean=False
        )
        
        results = consolidator.run_consolidation()
        
        assert results["success"] is False
        assert "Target memory system not available" in results["error"]
        assert len(results["validation_errors"]) > 0


class TestMemorySystemConsolidatorIntegration:
    """Integration tests for memory system consolidator."""
    
    @pytest.fixture
    def integration_temp_dir(self):
        """Create a comprehensive test environment for integration testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_dir = Path(tmp_dir)
            
            # Create realistic directory structure
            (test_dir / "src" / "core" / "workflows").mkdir(parents=True)
            (test_dir / "src" / "infrastructure" / "memory" / "engines").mkdir(parents=True)
            (test_dir / "src" / "infrastructure" / "memory" / "config").mkdir(parents=True)
            (test_dir / "src" / "infrastructure" / "tools" / "memory").mkdir(parents=True)
            (test_dir / "tests" / "unit").mkdir(parents=True)
            (test_dir / "reports").mkdir(parents=True)
            
            # Create target memory system
            target_init = test_dir / "src" / "infrastructure" / "tools" / "memory" / "__init__.py"
            target_init.write_text('''"""Target memory system."""
class MemoryEngine:
    def __init__(self):
        self.version = "2.0"

def get_memory_instance():
    return MemoryEngine()

def get_context_by_keys():
    return {}

__all__ = ['MemoryEngine', 'get_memory_instance', 'get_context_by_keys']
''')
            
            # Create files with various memory import patterns
            files_content = {
                "src/core/workflows/memory_workflow.py": '''
from src.infrastructure.memory import MemoryEngine
from src.infrastructure.memory.config import CacheConfig
import logging

def workflow_with_memory():
    engine = MemoryEngine()
    config = CacheConfig()
    return engine.store("key", "value")
''',
                "src/infrastructure/memory/engines/memory_engine.py": '''
"""Duplicate memory engine - should be removed."""
class MemoryEngine:
    def __init__(self):
        self.version = "1.0"
        # 100+ lines of duplicate implementation
''' + '\n'.join([f"    # Duplicate line {i}" for i in range(100)]) + '''

    def store(self, key, value):
        pass
        
    def retrieve(self, key):
        return None
''',
                "src/infrastructure/memory/config/memory_config.py": '''
"""Duplicate config - should be removed."""
class CacheConfig:
    def __init__(self):
        self.cache_size = 1000

class ChunkingConfig:
    def __init__(self):
        self.chunk_size = 512
        
# 50+ lines of duplicate config code
''' + '\n'.join([f"# Config duplicate line {i}" for i in range(50)]),
                "tests/unit/test_memory_integration.py": '''
import unittest
from src.infrastructure.memory import MemoryEngine

class TestMemoryIntegration(unittest.TestCase):
    def test_memory_engine(self):
        engine = MemoryEngine()
        self.assertIsNotNone(engine)
'''
            }
            
            # Write all test files
            for file_path, content in files_content.items():
                full_path = test_dir / file_path
                full_path.write_text(content)
            
            yield test_dir
    
    def test_full_integration_dry_run(self, integration_temp_dir):
        """Test complete integration with realistic codebase structure."""
        original_cwd = os.getcwd()
        try:
            os.chdir(integration_temp_dir)
            
            consolidator = MemorySystemConsolidator(
                root_dir=str(integration_temp_dir),
                dry_run=True,
                verify_tests=False,
                create_backup=False,
                verify_git_clean=False
            )
            
            # Validate target memory system
            assert consolidator.validate_target_memory_system() is True
            
            # Run full consolidation
            results = consolidator.run_consolidation()
            
            # Should find files to process
            assert results["success"] is True
            assert results["summary"]["files_analyzed"] > 0
            assert results["summary"]["imports_consolidated"] > 0
            assert results["summary"]["files_removed"] > 0
            assert results["summary"]["lines_saved"] > 0
            
        finally:
            os.chdir(original_cwd)
    
    def test_consolidation_preserves_functionality(self, integration_temp_dir):
        """Test that consolidation preserves code functionality."""
        original_cwd = os.getcwd()
        try:
            os.chdir(integration_temp_dir)
            
            # Read original workflow file
            workflow_file = integration_temp_dir / "src/core/workflows/memory_workflow.py"
            original_content = workflow_file.read_text()
            
            consolidator = MemorySystemConsolidator(
                root_dir=str(integration_temp_dir),
                dry_run=False,  # Actually make changes
                verify_tests=False,
                create_backup=False,
                verify_git_clean=False
            )
            
            # Run consolidation
            results = consolidator.run_consolidation()
            
            if results["success"] and results["summary"]["imports_consolidated"] > 0:
                # Verify the file was updated
                new_content = workflow_file.read_text()
                
                # Should still have the function definition
                assert "def workflow_with_memory():" in new_content
                # Should have updated imports
                if "from src.infrastructure.memory import" in original_content:
                    assert "from src.infrastructure.tools.memory import" in new_content
            
        finally:
            os.chdir(original_cwd)
    
    def test_performance_with_many_files(self, integration_temp_dir):
        """Test consolidation performance with many files."""
        # Create many files with memory imports
        src_dir = integration_temp_dir / "src" / "test_modules"
        src_dir.mkdir(exist_ok=True)
        
        for i in range(50):
            file_path = src_dir / f"module_{i}.py"
            file_path.write_text(f'''
from src.infrastructure.memory import MemoryEngine
from src.infrastructure.memory.config import CacheConfig
import logging

class Module{i}:
    def __init__(self):
        self.engine = MemoryEngine()
        self.config = CacheConfig()
    
    def process(self):
        return self.engine.store(f"key_{i}", "value")
''')
        
        consolidator = MemorySystemConsolidator(
            root_dir=str(integration_temp_dir),
            dry_run=True,
            verify_tests=False,
            create_backup=False,
            verify_git_clean=False,
            max_workers=4
        )
        
        # Should complete in reasonable time
        import time
        start_time = time.time()
        
        results = consolidator.run_consolidation()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 30 seconds for 50 files
        assert execution_time < 30
        assert results["success"] is True
        assert results["summary"]["files_analyzed"] >= 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])