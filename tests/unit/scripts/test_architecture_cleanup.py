#!/usr/bin/env python3
"""
Test suite for architecture cleanup script

Tests the enhanced architecture cleanup functionality with safety measures,
git integration, and proper error handling.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add scripts directory to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

try:
    from architecture_cleanup import ArchitectureStorageCleaner
except ImportError as e:
    pytest.skip(f"Could not import architecture_cleanup: {e}", allow_module_level=True)


class TestArchitectureStorageCleaner:
    """Test suite for ArchitectureStorageCleaner with enhanced safety features."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)
    
    @pytest.fixture
    def cleaner(self, temp_dir):
        """Create a cleaner instance for testing."""
        return ArchitectureStorageCleaner(
            root_dir=str(temp_dir),
            dry_run=True,
            extended_mode=True,
            verify_git_clean=False  # Skip git checks in tests
        )
    
    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample files and directories for testing."""
        # Create directory structure
        outputs_dir = temp_dir / "outputs"
        outputs_dir.mkdir()
        
        logs_dir = temp_dir / "logs"
        logs_dir.mkdir()
        
        hitl_dir = temp_dir / "build" / "storage" / "hitl"
        hitl_dir.mkdir(parents=True)
        
        # Create sample files with different ages
        now = datetime.now()
        
        # Old PERF directory (should be cleaned)
        old_perf = outputs_dir / "PERF-01"
        old_perf.mkdir()
        (old_perf / "results.json").write_text('{"test": "data"}')
        
        # Set modification time to 5 days ago
        old_time = (now - timedelta(days=5)).timestamp()
        os.utime(old_perf / "results.json", (old_time, old_time))
        os.utime(old_perf, (old_time, old_time))
        
        # Recent PERF directory (should be kept)
        new_perf = outputs_dir / "PERF-02"
        new_perf.mkdir()
        (new_perf / "results.json").write_text('{"test": "data"}')
        
        # Old log file
        old_log = logs_dir / "old_execution.log"
        old_log.write_text("Log content")
        os.utime(old_log, (old_time, old_time))
        
        # Audit log (should be preserved longer)
        audit_log = hitl_dir / "audit.jsonl"
        audit_log.write_text('{"event": "test"}')
        os.utime(audit_log, (old_time, old_time))
        
        return {
            "old_perf": old_perf,
            "new_perf": new_perf,
            "old_log": old_log,
            "audit_log": audit_log
        }
    
    def test_initialization(self, temp_dir):
        """Test cleaner initialization with various options."""
        cleaner = ArchitectureStorageCleaner(
            root_dir=str(temp_dir),
            dry_run=True,
            extended_mode=True,
            create_backup=False,
            verify_git_clean=False
        )
        
        assert cleaner.root_dir == temp_dir
        assert cleaner.dry_run is True
        assert cleaner.extended_mode is True
        assert cleaner.create_backup is False
        assert cleaner.verify_git_clean is False
        assert cleaner.max_workers == 4
        assert len(cleaner.retention_policies) > 0
    
    def test_configuration_validation(self, cleaner):
        """Test configuration validation."""
        # Valid configuration should pass
        assert cleaner.validate_configuration() is True
        
        # Invalid retention policy should fail
        cleaner.retention_policies['test'] = -1
        assert cleaner.validate_configuration() is False
        
        # Restore valid configuration
        del cleaner.retention_policies['test']
        assert cleaner.validate_configuration() is True
        
        # Invalid worker count should fail
        cleaner.max_workers = 20
        assert cleaner.validate_configuration() is False
    
    def test_file_classification(self, cleaner, sample_files):
        """Test file type classification."""
        # Test PERF output classification
        assert cleaner.classify_file(sample_files["old_perf"]) == 'perf_outputs'
        
        # Test log file classification  
        assert cleaner.classify_file(sample_files["old_log"]) == 'logs'
        
        # Test audit log classification
        assert cleaner.classify_file(sample_files["audit_log"]) == 'audit_logs'
    
    def test_item_age_calculation(self, cleaner, sample_files):
        """Test age calculation for files and directories."""
        # Old files should have age > 0
        old_file_age = cleaner.get_item_age_days(sample_files["old_log"])
        assert old_file_age >= 4  # Should be around 5 days old
        
        # Recent files should have age close to 0
        new_file_age = cleaner.get_item_age_days(sample_files["new_perf"])
        assert new_file_age <= 1  # Should be very recent
    
    def test_expiration_check(self, cleaner, sample_files):
        """Test expiration logic based on retention policies."""
        # Old PERF output should be expired (retention: 3 days, age: 5 days)
        assert cleaner.is_item_expired(
            sample_files["old_perf"], 'perf_outputs', 'directory'
        ) is True
        
        # Recent PERF output should not be expired
        assert cleaner.is_item_expired(
            sample_files["new_perf"], 'perf_outputs', 'directory'
        ) is False
        
        # Old audit log should not be expired (retention: 90 days)
        assert cleaner.is_item_expired(
            sample_files["audit_log"], 'audit_logs', 'file'
        ) is False
    
    def test_discovery_process(self, cleaner, sample_files):
        """Test cleanup target discovery."""
        targets = cleaner.discover_cleanup_targets()
        
        # Should find files in outputs and logs directories
        assert len(targets) > 0
        
        # Check that both files and directories are discovered
        file_targets = [t for t in targets if t[1] == 'file']
        dir_targets = [t for t in targets if t[1] == 'directory']
        
        assert len(file_targets) > 0
        assert len(dir_targets) > 0
    
    def test_size_calculation(self, cleaner, sample_files):
        """Test size calculation for files and directories."""
        # File size should be > 0
        file_size = cleaner.get_item_size(sample_files["old_log"], 'file')
        assert file_size > 0
        
        # Directory size should include all contents
        dir_size = cleaner.get_item_size(sample_files["old_perf"], 'directory')
        assert dir_size > 0
    
    @patch('subprocess.run')
    def test_git_status_verification(self, mock_run, cleaner):
        """Test git status verification."""
        # Test clean git status
        mock_run.return_value = Mock(returncode=0, stdout="")
        cleaner.verify_git_clean = True
        assert cleaner.verify_git_status() is True
        
        # Test dirty git status
        mock_run.return_value = Mock(returncode=0, stdout="M file.py\n")
        assert cleaner.verify_git_status() is False
        
        # Test git not available
        mock_run.return_value = Mock(returncode=128, stderr="not a git repository")
        assert cleaner.verify_git_status() is True  # Should not fail if not in git repo
    
    @patch('subprocess.run')
    def test_backup_branch_creation(self, mock_run, cleaner):
        """Test backup branch creation."""
        # Mock successful branch creation
        mock_run.side_effect = [
            Mock(returncode=0, stdout="Switched to a new branch"),  # checkout -b
            Mock(returncode=0, stdout="Switched to branch")         # checkout -
        ]
        
        cleaner.create_backup = True
        cleaner.dry_run = False
        
        assert cleaner.create_backup_branch() is True
        assert cleaner.backup_created is True
        
        # Should call git twice (create branch, switch back)
        assert mock_run.call_count == 2
    
    def test_critical_file_identification(self, cleaner, sample_files):
        """Test identification of critical files that need backup."""
        # Audit logs should be considered critical
        assert cleaner._is_critical_file(sample_files["audit_log"], 'audit_logs') is True
        
        # Regular PERF outputs should not be critical
        assert cleaner._is_critical_file(sample_files["old_perf"], 'perf_outputs') is False
    
    def test_dry_run_mode(self, cleaner, sample_files):
        """Test that dry run mode doesn't actually delete files."""
        # Run cleanup in dry run mode
        result = cleaner.run_cleanup()
        
        # Files should still exist after dry run
        assert sample_files["old_perf"].exists()
        assert sample_files["old_log"].exists()
        assert sample_files["audit_log"].exists()
        
        # But counters should be updated
        assert result["files_processed"] >= 0
    
    def test_error_handling(self, cleaner, temp_dir):
        """Test error handling for various failure scenarios."""
        # Create a file we can't delete (simulate permission error)
        protected_dir = temp_dir / "outputs" / "protected"
        protected_dir.mkdir(parents=True)
        protected_file = protected_dir / "file.txt"
        protected_file.write_text("content")
        
        # Mock permission error
        with patch('pathlib.Path.unlink', side_effect=PermissionError("Permission denied")):
            cleaner.dry_run = False  # Need to actually try to delete
            
            # Should handle error gracefully
            targets = [(protected_file, 'file')]
            cleaner._clean_file_type_extended(targets, 'logs')
            
            # Should have recorded the error
            assert len(cleaner.errors) > 0
            assert "Permission denied" in str(cleaner.errors[0])
    
    def test_thread_safety(self, cleaner, temp_dir):
        """Test thread safety of counter updates."""
        # Create multiple files for parallel processing
        outputs_dir = temp_dir / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        files = []
        for i in range(10):
            file_path = outputs_dir / f"test_{i}.txt"
            file_path.write_text("content")
            files.append((file_path, 'file'))
        
        # Process files in parallel (dry run)
        with patch.object(cleaner, 'is_item_expired', return_value=True):
            cleaner._clean_file_type_extended(files, 'test_outputs')
        
        # Counters should be updated correctly
        assert cleaner.removed_count >= 0
        assert cleaner.freed_space >= 0
    
    def test_main_function_validation_only(self, temp_dir):
        """Test main function with validation-only flag."""
        # Mock sys.argv for argument parsing
        test_args = [
            'architecture_cleanup.py',
            '--storage-dir', str(temp_dir),
            '--validate-only',
            '--no-git-check'
        ]
        
        with patch('sys.argv', test_args):
            # Import and run main function
            from architecture_cleanup import main
            
            # Should succeed with validation only
            result = main()
            assert result == 0  # Success exit code
    
    @pytest.mark.parametrize("extended_mode,dry_run", [
        (True, True),
        (True, False),
        (False, True),
        (False, False)
    ])
    def test_different_modes(self, temp_dir, extended_mode, dry_run):
        """Test cleanup with different mode combinations."""
        cleaner = ArchitectureStorageCleaner(
            root_dir=str(temp_dir),
            dry_run=dry_run,
            extended_mode=extended_mode,
            verify_git_clean=False
        )
        
        # Should be able to initialize and validate
        assert cleaner.validate_configuration() is True
        
        # Should be able to discover targets (even if none exist)
        targets = cleaner.discover_cleanup_targets()
        assert isinstance(targets, list)


class TestArchitectureCleanupIntegration:
    """Integration tests for architecture cleanup script."""
    
    @pytest.fixture
    def integration_temp_dir(self):
        """Create a more comprehensive test environment."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_dir = Path(tmp_dir)
            
            # Create realistic directory structure
            directories = [
                "outputs/PERF-001",
                "outputs/PERF-002", 
                "outputs/BE-001",
                "outputs/FE-001",
                "logs",
                "build/storage/hitl",
                "build/storage/hot",
                "build/storage/warm"
            ]
            
            for dir_path in directories:
                (test_dir / dir_path).mkdir(parents=True)
                
                # Add some files
                (test_dir / dir_path / "data.json").write_text('{"test": "data"}')
                (test_dir / dir_path / "log.txt").write_text("log content")
            
            yield test_dir
    
    def test_full_cleanup_cycle(self, integration_temp_dir):
        """Test a complete cleanup cycle with realistic data."""
        cleaner = ArchitectureStorageCleaner(
            root_dir=str(integration_temp_dir),
            dry_run=True,
            extended_mode=True,
            verify_git_clean=False,
            create_backup=False
        )
        
        # Validate configuration
        assert cleaner.validate_configuration() is True
        
        # Discover targets
        targets = cleaner.discover_cleanup_targets()
        assert len(targets) > 0
        
        # Run cleanup
        result = cleaner.run_cleanup()
        assert result["success"] is True
        assert result["files_processed"] >= 0
        assert result["space_freed"] >= 0.0
        assert isinstance(result["errors"], list)
    
    def test_performance_with_many_files(self, integration_temp_dir):
        """Test cleanup performance with many files."""
        # Create many files
        outputs_dir = integration_temp_dir / "outputs"
        for i in range(100):
            perf_dir = outputs_dir / f"PERF-{i:03d}"
            perf_dir.mkdir(exist_ok=True)
            for j in range(5):
                (perf_dir / f"file_{j}.txt").write_text(f"content {j}")
        
        cleaner = ArchitectureStorageCleaner(
            root_dir=str(integration_temp_dir),
            dry_run=True,
            extended_mode=True,
            verify_git_clean=False,
            max_workers=4
        )
        
        # Should complete in reasonable time
        import time
        start_time = time.time()
        
        result = cleaner.run_cleanup()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 30 seconds for 500 files
        assert execution_time < 30
        assert result["success"] is True
    
    def test_cleanup_with_existing_git_repo(self, integration_temp_dir):
        """Test cleanup behavior in a git repository."""
        # Initialize git repo
        import subprocess
        try:
            subprocess.run(['git', 'init'], cwd=integration_temp_dir, check=True, 
                         capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'], 
                         cwd=integration_temp_dir, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'], 
                         cwd=integration_temp_dir, check=True, capture_output=True)
            
            # Add a file and commit
            test_file = integration_temp_dir / "test.txt"
            test_file.write_text("test")
            subprocess.run(['git', 'add', 'test.txt'], cwd=integration_temp_dir, 
                         check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], 
                         cwd=integration_temp_dir, check=True, capture_output=True)
            
            # Test cleaner with git verification
            cleaner = ArchitectureStorageCleaner(
                root_dir=str(integration_temp_dir),
                dry_run=True,
                extended_mode=True,
                verify_git_clean=True,
                create_backup=True
            )
            
            # Should work with clean git repo
            result = cleaner.run_cleanup()
            assert result["success"] is True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Git not available, skip test
            pytest.skip("Git not available for testing")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])