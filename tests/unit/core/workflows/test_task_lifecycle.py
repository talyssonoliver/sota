"""
Tests for Task Lifecycle Manager

Comprehensive test suite for the task lifecycle management system
to validate task archival, cleanup, and storage optimization.
"""

import gzip
import json
import os
import shutil
import tarfile
import tempfile
import threading
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, call
import pytest

from src.core.workflows.task_lifecycle import (
    TaskLifecycleManager, 
    TaskLifecyclePolicy, 
    TaskArchiveMetadata
)


class TestTaskLifecyclePolicy:
    """Test TaskLifecyclePolicy dataclass."""
    
    def test_default_policy_creation(self):
        """Test creation of default lifecycle policy."""
        policy = TaskLifecyclePolicy()
        
        assert policy.hot_storage_days == 7
        assert policy.warm_storage_days == 30
        assert policy.cold_storage_days == 365
        assert policy.auto_cleanup_enabled is True
        assert policy.compression_level == 6
        assert policy.max_hot_tasks == 1000
    
    def test_custom_policy_creation(self):
        """Test creation of custom lifecycle policy."""
        policy = TaskLifecyclePolicy(
            hot_storage_days=14,
            warm_storage_days=60,
            cold_storage_days=730,
            auto_cleanup_enabled=False,
            compression_level=9,
            max_hot_tasks=500
        )
        
        assert policy.hot_storage_days == 14
        assert policy.warm_storage_days == 60
        assert policy.cold_storage_days == 730
        assert policy.auto_cleanup_enabled is False
        assert policy.compression_level == 9
        assert policy.max_hot_tasks == 500


class TestTaskArchiveMetadata:
    """Test TaskArchiveMetadata dataclass."""
    
    def test_metadata_creation(self):
        """Test creation of archive metadata."""
        metadata = TaskArchiveMetadata(
            task_id="BE-07",
            archived_at="2024-01-01T12:00:00",
            original_size_bytes=1024,
            compressed_size_bytes=512,
            archive_location="archives/warm/BE-07.tar.gz",
            retention_until="2025-01-01T12:00:00",
            qa_status="passed",
            completion_status="completed"
        )
        
        assert metadata.task_id == "BE-07"
        assert metadata.archived_at == "2024-01-01T12:00:00"
        assert metadata.original_size_bytes == 1024
        assert metadata.compressed_size_bytes == 512
        assert metadata.qa_status == "passed"
        assert metadata.completion_status == "completed"


class TestTaskLifecycleManager:
    """Test TaskLifecycleManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.outputs_dir = self.temp_dir / "outputs"
        self.archive_dir = self.temp_dir / "archives"
        
        # Create test directories
        self.outputs_dir.mkdir(parents=True)
        
        # Create test policy
        self.test_policy = TaskLifecyclePolicy(
            hot_storage_days=1,
            warm_storage_days=7,
            cold_storage_days=30,
            auto_cleanup_enabled=True,
            compression_level=1,  # Fast compression for tests
            max_hot_tasks=5
        )
        
        self.manager = TaskLifecycleManager(
            outputs_dir=str(self.outputs_dir),
            archive_dir=str(self.archive_dir),
            policy=self.test_policy
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_task(self, task_id: str, days_old: int = 0) -> Path:
        """Create a test task directory with files."""
        task_dir = self.outputs_dir / task_id
        task_dir.mkdir(exist_ok=True)
        
        # Create test files
        (task_dir / "output.txt").write_text(f"Task {task_id} output")
        (task_dir / "metadata.json").write_text(json.dumps({
            "task_id": task_id,
            "status": "completed",
            "created_at": datetime.now().isoformat()
        }))
        
        # Set file modification time to simulate age
        if days_old > 0:
            old_time = datetime.now() - timedelta(days=days_old)
            timestamp = old_time.timestamp()
            for file_path in task_dir.rglob("*"):
                if file_path.is_file():
                    os.utime(file_path, (timestamp, timestamp))
        
        return task_dir
    
    def test_manager_initialization(self):
        """Test lifecycle manager initialization."""
        assert self.manager.outputs_dir == self.outputs_dir
        assert self.manager.archive_dir == self.archive_dir
        assert self.manager.policy == self.test_policy
        
        # Check directory structure was created
        assert self.manager.warm_dir.exists()
        assert self.manager.cold_dir.exists()
        assert isinstance(self.manager.metadata, dict)
        assert isinstance(self.manager.lock, threading.Lock)
    
    def test_manager_initialization_default_policy(self):
        """Test manager initialization with default policy."""
        manager = TaskLifecycleManager(
            outputs_dir=str(self.outputs_dir),
            archive_dir=str(self.archive_dir)
        )
        
        assert isinstance(manager.policy, TaskLifecyclePolicy)
        assert manager.policy.hot_storage_days == 7
    
    def test_load_metadata_new_install(self):
        """Test loading metadata when no metadata file exists."""
        # metadata should be empty dict for new installation
        assert self.manager.metadata == {}
    
    def test_load_metadata_existing_file(self):
        """Test loading metadata from existing file."""
        # Create test metadata file
        test_metadata = {
            "BE-07": {
                "task_id": "BE-07",
                "archived_at": "2024-01-01T12:00:00",
                "original_size_bytes": 1024,
                "compressed_size_bytes": 512,
                "archive_location": "archives/warm/BE-07.tar.gz",
                "retention_until": "2025-01-01T12:00:00",
                "qa_status": "passed",
                "completion_status": "completed"
            }
        }
        
        with open(self.manager.metadata_file, 'w') as f:
            json.dump(test_metadata, f)
        
        # Reload metadata
        metadata = self.manager._load_metadata()
        
        assert "BE-07" in metadata
        assert isinstance(metadata["BE-07"], TaskArchiveMetadata)
        assert metadata["BE-07"].task_id == "BE-07"
    
    def test_load_metadata_corrupted_file(self):
        """Test loading metadata when file is corrupted."""
        # Create corrupted metadata file
        self.manager.metadata_file.write_text("{ invalid json }")
        
        # Should return empty dict and not crash
        metadata = self.manager._load_metadata()
        assert metadata == {}
    
    def test_save_metadata(self):
        """Test saving metadata to file."""
        # Add test metadata
        test_metadata = TaskArchiveMetadata(
            task_id="BE-07",
            archived_at="2024-01-01T12:00:00",
            original_size_bytes=1024,
            compressed_size_bytes=512,
            archive_location="archives/warm/BE-07.tar.gz",
            retention_until="2025-01-01T12:00:00",
            qa_status="passed",
            completion_status="completed"
        )
        
        self.manager.metadata["BE-07"] = test_metadata
        self.manager._save_metadata()
        
        # Verify file was created and contains correct data
        assert self.manager.metadata_file.exists()
        
        with open(self.manager.metadata_file, 'r') as f:
            saved_data = json.load(f)
        
        assert "BE-07" in saved_data
        assert saved_data["BE-07"]["task_id"] == "BE-07"
    
    def test_get_task_age_days(self):
        """Test getting task age in days."""
        # Create test task with known age
        task_dir = self.create_test_task("BE-07", days_old=5)
        
        age = self.manager.get_task_age_days("BE-07")
        
        # Should be approximately 5 days (allowing for small time differences)
        assert age is not None
        assert 4 <= age <= 6
    
    def test_get_task_age_days_nonexistent(self):
        """Test getting age of non-existent task."""
        age = self.manager.get_task_age_days("NONEXISTENT")
        assert age is None
    
    def test_identify_tasks_for_lifecycle(self):
        """Test identifying tasks for lifecycle management."""
        # Create tasks of different ages
        self.create_test_task("HOT-01", days_old=0)      # Hot
        self.create_test_task("WARM-01", days_old=2)     # Should move to warm
        self.create_test_task("COLD-01", days_old=10)    # Should move to cold
        
        hot_tasks, warm_tasks, cold_tasks = self.manager.identify_tasks_for_lifecycle()
        
        # Verify tasks are categorized correctly
        assert "HOT-01" in hot_tasks
        assert "WARM-01" in warm_tasks
        assert "COLD-01" in cold_tasks
    
    def test_archive_task_to_warm(self):
        """Test archiving task to warm storage."""
        # Create test task
        task_dir = self.create_test_task("BE-07")
        original_size = sum(f.stat().st_size for f in task_dir.rglob("*") if f.is_file())
        
        # Archive to warm storage
        result = self.manager.archive_task_to_warm("BE-07")
        
        assert result is True
        
        # Verify task was archived
        assert not task_dir.exists()  # Original should be removed
        
        # Check warm storage
        warm_archive = self.manager.warm_dir / "BE-07.tar.gz"
        assert warm_archive.exists()
        
        # Check metadata was created
        assert "BE-07" in self.manager.metadata
        metadata = self.manager.metadata["BE-07"]
        assert metadata.task_id == "BE-07"
        assert metadata.original_size_bytes == original_size
        assert metadata.compressed_size_bytes > 0
    
    def test_archive_task_to_warm_nonexistent(self):
        """Test archiving non-existent task to warm storage."""
        result = self.manager.archive_task_to_warm("NONEXISTENT")
        assert result is False
    
    def test_archive_task_to_cold(self):
        """Test archiving task to cold storage."""
        # First create a warm archive
        task_dir = self.create_test_task("BE-07")
        self.manager.archive_task_to_warm("BE-07")
        
        # Now move to cold storage
        result = self.manager.archive_task_to_cold("BE-07")
        
        assert result is True
        
        # Verify warm archive was removed
        warm_archive = self.manager.warm_dir / "BE-07.tar.gz"
        assert not warm_archive.exists()
        
        # Verify cold archive exists
        cold_archive = self.manager.cold_dir / "BE-07.tar.gz"
        assert cold_archive.exists()
        
        # Check metadata was updated
        assert "BE-07" in self.manager.metadata
        metadata = self.manager.metadata["BE-07"]
        assert "cold" in metadata.archive_location
    
    def test_archive_task_to_cold_no_warm(self):
        """Test archiving task to cold when no warm archive exists."""
        result = self.manager.archive_task_to_cold("NONEXISTENT")
        assert result is False
    
    def test_restore_task_from_warm(self):
        """Test restoring task from warm storage."""
        # Create and archive task
        task_dir = self.create_test_task("BE-07")
        original_files = list(task_dir.rglob("*"))
        self.manager.archive_task_to_warm("BE-07")
        
        # Restore task
        result = self.manager.restore_task_from_warm("BE-07")
        
        assert result is True
        assert task_dir.exists()
        
        # Verify files were restored
        restored_files = list(task_dir.rglob("*"))
        assert len(restored_files) >= len(original_files)
    
    def test_restore_task_from_warm_no_archive(self):
        """Test restoring task when no warm archive exists."""
        result = self.manager.restore_task_from_warm("NONEXISTENT")
        assert result is False
    
    def test_restore_task_from_cold(self):
        """Test restoring task from cold storage."""
        # Create, archive to warm, then cold
        task_dir = self.create_test_task("BE-07")
        self.manager.archive_task_to_warm("BE-07")
        self.manager.archive_task_to_cold("BE-07")
        
        # Restore from cold
        result = self.manager.restore_task_from_cold("BE-07")
        
        assert result is True
        
        # Should be restored to warm storage
        warm_archive = self.manager.warm_dir / "BE-07.tar.gz"
        assert warm_archive.exists()
    
    def test_delete_archived_task(self):
        """Test deleting archived task."""
        # Create and archive task
        task_dir = self.create_test_task("BE-07")
        self.manager.archive_task_to_warm("BE-07")
        
        # Delete archived task
        result = self.manager.delete_archived_task("BE-07")
        
        assert result is True
        
        # Verify archive and metadata were removed
        warm_archive = self.manager.warm_dir / "BE-07.tar.gz"
        assert not warm_archive.exists()
        assert "BE-07" not in self.manager.metadata
    
    def test_delete_archived_task_nonexistent(self):
        """Test deleting non-existent archived task."""
        result = self.manager.delete_archived_task("NONEXISTENT")
        assert result is False
    
    def test_get_storage_stats(self):
        """Test getting storage statistics."""
        # Create tasks in different storage tiers
        self.create_test_task("HOT-01")
        
        task_dir = self.create_test_task("WARM-01")
        self.manager.archive_task_to_warm("WARM-01")
        
        task_dir = self.create_test_task("COLD-01")
        self.manager.archive_task_to_warm("COLD-01")
        self.manager.archive_task_to_cold("COLD-01")
        
        # Get storage stats
        stats = self.manager.get_storage_stats()
        
        assert "hot_storage" in stats
        assert "warm_storage" in stats
        assert "cold_storage" in stats
        assert stats["hot_storage"]["task_count"] >= 1
        assert stats["warm_storage"]["task_count"] >= 0
        assert stats["cold_storage"]["task_count"] >= 1
    
    def test_cleanup_expired_tasks(self):
        """Test cleanup of expired tasks."""
        # Create old task and archive it
        task_dir = self.create_test_task("OLD-01")
        self.manager.archive_task_to_warm("OLD-01")
        
        # Manually set retention date to past
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        self.manager.metadata["OLD-01"].retention_until = past_date
        
        # Run cleanup
        deleted_count = self.manager.cleanup_expired_tasks()
        
        assert deleted_count >= 1
        assert "OLD-01" not in self.manager.metadata
    
    def test_run_lifecycle_management(self):
        """Test complete lifecycle management run."""
        # Create tasks of different ages
        self.create_test_task("NEW-01", days_old=0)
        self.create_test_task("OLD-01", days_old=2)
        self.create_test_task("ANCIENT-01", days_old=10)
        
        # Run lifecycle management
        result = self.manager.run_lifecycle_management()
        
        assert "processed" in result
        assert "archived_to_warm" in result
        assert "archived_to_cold" in result
        assert "errors" in result
    
    def test_validate_archive_integrity(self):
        """Test archive integrity validation."""
        # Create and archive task
        task_dir = self.create_test_task("BE-07")
        self.manager.archive_task_to_warm("BE-07")
        
        # Validate integrity
        is_valid = self.manager.validate_archive_integrity("BE-07")
        
        assert is_valid is True
    
    def test_validate_archive_integrity_corrupted(self):
        """Test integrity validation of corrupted archive."""
        # Create and archive task
        task_dir = self.create_test_task("BE-07")
        self.manager.archive_task_to_warm("BE-07")
        
        # Corrupt the archive
        warm_archive = self.manager.warm_dir / "BE-07.tar.gz"
        warm_archive.write_bytes(b"corrupted data")
        
        # Validate integrity
        is_valid = self.manager.validate_archive_integrity("BE-07")
        
        assert is_valid is False
    
    def test_get_task_history(self):
        """Test getting task history."""
        # Create task and perform lifecycle operations
        task_dir = self.create_test_task("BE-07")
        self.manager.archive_task_to_warm("BE-07")
        
        # Get history
        history = self.manager.get_task_history("BE-07")
        
        assert history is not None
        assert "task_id" in history
        assert "lifecycle_events" in history
        assert len(history["lifecycle_events"]) >= 1
    
    def test_get_task_history_nonexistent(self):
        """Test getting history of non-existent task."""
        history = self.manager.get_task_history("NONEXISTENT")
        assert history is None


class TestTaskLifecycleManagerIntegration:
    """Test integration scenarios for task lifecycle management."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.outputs_dir = self.temp_dir / "outputs"
        self.archive_dir = self.temp_dir / "archives"
        
        self.outputs_dir.mkdir(parents=True)
        
        self.manager = TaskLifecycleManager(
            outputs_dir=str(self.outputs_dir),
            archive_dir=str(self.archive_dir),
            policy=TaskLifecyclePolicy(
                hot_storage_days=1,
                warm_storage_days=3,
                cold_storage_days=7,
                max_hot_tasks=3
            )
        )
    
    def teardown_method(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_task(self, task_id: str, days_old: int = 0) -> Path:
        """Create a test task directory with files."""
        task_dir = self.outputs_dir / task_id
        task_dir.mkdir(exist_ok=True)
        
        # Create test files
        (task_dir / "output.txt").write_text(f"Task {task_id} output" * 100)
        (task_dir / "data.json").write_text(json.dumps({
            "task_id": task_id,
            "results": list(range(50)),
            "status": "completed"
        }))
        
        # Set file age
        if days_old > 0:
            old_time = datetime.now() - timedelta(days=days_old)
            timestamp = old_time.timestamp()
            for file_path in task_dir.rglob("*"):
                if file_path.is_file():
                    os.utime(file_path, (timestamp, timestamp))
        
        return task_dir
    
    def test_complete_lifecycle_workflow(self):
        """Test complete task lifecycle from creation to deletion."""
        # Create tasks at different lifecycle stages
        new_task = self.create_test_task("NEW-01", days_old=0)      # Hot
        warm_task = self.create_test_task("WARM-01", days_old=2)    # Warm
        cold_task = self.create_test_task("COLD-01", days_old=5)    # Cold
        old_task = self.create_test_task("OLD-01", days_old=10)     # Should be deleted
        
        # Run complete lifecycle management
        initial_stats = self.manager.get_storage_stats()
        result = self.manager.run_lifecycle_management()
        final_stats = self.manager.get_storage_stats()
        
        # Verify lifecycle operations occurred
        assert result["processed"] >= 4
        assert new_task.exists()  # Should still be in hot storage
        
        # Check that tasks were moved appropriately
        assert final_stats["warm_storage"]["task_count"] >= 1
        assert final_stats["cold_storage"]["task_count"] >= 1
    
    def test_storage_optimization_workflow(self):
        """Test storage optimization under capacity pressure."""
        # Create more tasks than max_hot_tasks limit
        tasks = []
        for i in range(5):  # More than max_hot_tasks (3)
            task = self.create_test_task(f"TASK-{i:02d}", days_old=0)
            tasks.append(task)
        
        # Run lifecycle management
        result = self.manager.run_lifecycle_management()
        
        # Should handle capacity optimization
        remaining_hot = len([t for t in tasks if t.exists()])
        assert remaining_hot <= self.manager.policy.max_hot_tasks
    
    def test_disaster_recovery_workflow(self):
        """Test disaster recovery and archive validation."""
        # Create and archive multiple tasks
        tasks = ["TASK-01", "TASK-02", "TASK-03"]
        for task_id in tasks:
            self.create_test_task(task_id, days_old=2)
        
        # Archive tasks
        for task_id in tasks:
            self.manager.archive_task_to_warm(task_id)
        
        # Simulate partial corruption by corrupting one archive
        corrupt_archive = self.manager.warm_dir / "TASK-02.tar.gz"
        corrupt_archive.write_bytes(b"corrupted")
        
        # Validate all archives
        validation_results = {}
        for task_id in tasks:
            validation_results[task_id] = self.manager.validate_archive_integrity(task_id)
        
        # Should detect corruption
        assert validation_results["TASK-01"] is True
        assert validation_results["TASK-02"] is False
        assert validation_results["TASK-03"] is True
    
    def test_concurrent_lifecycle_operations(self):
        """Test thread safety of concurrent lifecycle operations."""
        import threading
        import time
        
        # Create multiple tasks
        for i in range(10):
            self.create_test_task(f"CONCURRENT-{i:02d}", days_old=1)
        
        # Define concurrent operations
        def archive_operations():
            for i in range(0, 5):
                self.manager.archive_task_to_warm(f"CONCURRENT-{i:02d}")
                time.sleep(0.01)  # Small delay to encourage race conditions
        
        def lifecycle_operations():
            time.sleep(0.05)  # Start slightly later
            self.manager.run_lifecycle_management()
        
        # Run operations concurrently
        thread1 = threading.Thread(target=archive_operations)
        thread2 = threading.Thread(target=lifecycle_operations)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Should complete without errors
        stats = self.manager.get_storage_stats()
        assert stats["total_tasks"] >= 5


if __name__ == '__main__':
    pytest.main([__file__])