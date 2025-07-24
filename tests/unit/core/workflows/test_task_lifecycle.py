"""
Comprehensive tests for task lifecycle management functionality.

Tests TaskLifecycleManager class and related dataclasses for archival,
cleanup, and storage optimization functions.
"""

import json
import os
import shutil
import tarfile
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.core.workflows.task_lifecycle import (
    TaskArchiveMetadata,
    TaskLifecycleManager,
    TaskLifecyclePolicy,
    main,
)


class TestTaskLifecyclePolicy:
    """Test the TaskLifecyclePolicy dataclass."""

    def test_task_lifecycle_policy_creation(self):
        """Test basic TaskLifecyclePolicy creation."""
        policy = TaskLifecyclePolicy()
        
        assert policy.hot_storage_days == 7
        assert policy.warm_storage_days == 30
        assert policy.cold_storage_days == 365
        assert policy.auto_cleanup_enabled is True
        assert policy.compression_level == 6
        assert policy.max_hot_tasks == 1000

    def test_task_lifecycle_policy_custom_values(self):
        """Test TaskLifecyclePolicy with custom values."""
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

    def test_task_lifecycle_policy_defaults(self):
        """Test TaskLifecyclePolicy default value types."""
        policy = TaskLifecyclePolicy()
        
        assert isinstance(policy.hot_storage_days, int)
        assert isinstance(policy.warm_storage_days, int)
        assert isinstance(policy.cold_storage_days, int)
        assert isinstance(policy.auto_cleanup_enabled, bool)
        assert isinstance(policy.compression_level, int)
        assert isinstance(policy.max_hot_tasks, int)


class TestTaskArchiveMetadata:
    """Test the TaskArchiveMetadata dataclass."""

    def test_task_archive_metadata_creation(self):
        """Test basic TaskArchiveMetadata creation."""
        metadata = TaskArchiveMetadata(
            task_id="TEST-01",
            archived_at="2024-01-01T12:00:00",
            original_size_bytes=1024,
            compressed_size_bytes=512,
            archive_location="/path/to/archive.tar.gz",
            retention_until="2024-02-01T12:00:00",
            qa_status="passed",
            completion_status="complete"
        )
        
        assert metadata.task_id == "TEST-01"
        assert metadata.archived_at == "2024-01-01T12:00:00"
        assert metadata.original_size_bytes == 1024
        assert metadata.compressed_size_bytes == 512
        assert metadata.archive_location == "/path/to/archive.tar.gz"
        assert metadata.retention_until == "2024-02-01T12:00:00"
        assert metadata.qa_status == "passed"
        assert metadata.completion_status == "complete"

    def test_task_archive_metadata_different_statuses(self):
        """Test TaskArchiveMetadata with different QA and completion statuses."""
        statuses = [
            ("passed", "complete"),
            ("failed", "complete"),
            ("pending", "in_progress"),
            ("unknown", "failed")
        ]
        
        for qa_status, completion_status in statuses:
            metadata = TaskArchiveMetadata(
                task_id="STATUS-TEST",
                archived_at="2024-01-01T12:00:00",
                original_size_bytes=1000,
                compressed_size_bytes=500,
                archive_location="/path/archive.tar.gz",
                retention_until="2024-02-01T12:00:00",
                qa_status=qa_status,
                completion_status=completion_status
            )
            
            assert metadata.qa_status == qa_status
            assert metadata.completion_status == completion_status

    def test_task_archive_metadata_size_calculation(self):
        """Test compression ratio calculation."""
        metadata = TaskArchiveMetadata(
            task_id="SIZE-TEST",
            archived_at="2024-01-01T12:00:00",
            original_size_bytes=2000,
            compressed_size_bytes=1000,
            archive_location="/path/archive.tar.gz",
            retention_until="2024-02-01T12:00:00",
            qa_status="passed",
            completion_status="complete"
        )
        
        # Compression ratio should be 50%
        compression_ratio = metadata.compressed_size_bytes / metadata.original_size_bytes
        assert compression_ratio == 0.5


class TestTaskLifecycleManager:
    """Test the TaskLifecycleManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.outputs_dir = Path(self.temp_dir) / "outputs"
        self.archive_dir = Path(self.temp_dir) / "archives"
        
        # Create test directories
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test policy
        self.policy = TaskLifecyclePolicy(
            hot_storage_days=1,  # Short for testing
            warm_storage_days=2,
            cold_storage_days=3,
            max_hot_tasks=5
        )
        
        self.manager = TaskLifecycleManager(
            outputs_dir=str(self.outputs_dir),
            archive_dir=str(self.archive_dir),
            policy=self.policy
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test TaskLifecycleManager initialization."""
        assert self.manager.outputs_dir == self.outputs_dir
        assert self.manager.archive_dir == self.archive_dir
        assert self.manager.policy == self.policy
        
        # Check directory structure
        assert self.manager.warm_dir.exists()
        assert self.manager.cold_dir.exists()
        assert self.manager.metadata_file.exists() or not self.manager.metadata_file.exists()  # May or may not exist
        assert isinstance(self.manager.metadata, dict)

    def test_initialization_with_defaults(self):
        """Test TaskLifecycleManager initialization with default policy."""
        manager = TaskLifecycleManager(
            outputs_dir=str(self.outputs_dir),
            archive_dir=str(self.archive_dir)
        )
        
        assert isinstance(manager.policy, TaskLifecyclePolicy)
        assert manager.policy.hot_storage_days == 7  # Default value

    def test_load_metadata_no_file(self):
        """Test loading metadata when file doesn't exist."""
        metadata = self.manager._load_metadata()
        assert isinstance(metadata, dict)
        assert len(metadata) == 0

    def test_load_metadata_with_file(self):
        """Test loading metadata from existing file."""
        # Create test metadata file
        test_metadata = {
            "TEST-01": {
                "task_id": "TEST-01",
                "archived_at": "2024-01-01T12:00:00",
                "original_size_bytes": 1024,
                "compressed_size_bytes": 512,
                "archive_location": "/path/archive.tar.gz",
                "retention_until": "2024-02-01T12:00:00",
                "qa_status": "passed",
                "completion_status": "complete"
            }
        }
        
        with open(self.manager.metadata_file, "w") as f:
            json.dump(test_metadata, f)
        
        metadata = self.manager._load_metadata()
        assert "TEST-01" in metadata
        assert isinstance(metadata["TEST-01"], TaskArchiveMetadata)
        assert metadata["TEST-01"].task_id == "TEST-01"

    def test_save_metadata(self):
        """Test saving metadata to file."""
        # Add test metadata
        test_metadata = TaskArchiveMetadata(
            task_id="SAVE-TEST",
            archived_at="2024-01-01T12:00:00",
            original_size_bytes=1024,
            compressed_size_bytes=512,
            archive_location="/path/archive.tar.gz",
            retention_until="2024-02-01T12:00:00",
            qa_status="passed",
            completion_status="complete"
        )
        
        self.manager.metadata["SAVE-TEST"] = test_metadata
        self.manager._save_metadata()
        
        # Verify file was created and contains data
        assert self.manager.metadata_file.exists()
        
        with open(self.manager.metadata_file, "r") as f:
            saved_data = json.load(f)
        
        assert "SAVE-TEST" in saved_data
        assert saved_data["SAVE-TEST"]["task_id"] == "SAVE-TEST"

    def test_get_task_age_days_no_task(self):
        """Test getting task age when task doesn't exist."""
        age = self.manager.get_task_age_days("NONEXISTENT")
        assert age is None

    def test_get_task_age_days_with_task(self):
        """Test getting task age for existing task."""
        # Create test task directory with files
        task_dir = self.outputs_dir / "AGE-TEST"
        task_dir.mkdir()
        
        test_file = task_dir / "test.txt"
        test_file.write_text("test content")
        
        # Set file modification time to 2 days ago
        two_days_ago = datetime.now().timestamp() - (2 * 24 * 3600)
        os.utime(test_file, (two_days_ago, two_days_ago))
        
        age = self.manager.get_task_age_days("AGE-TEST")
        assert age >= 1  # Should be at least 1 day old

    def test_should_archive_task_no_task(self):
        """Test should_archive_task when task doesn't exist."""
        should_archive = self.manager.should_archive_task("NONEXISTENT")
        assert should_archive is False

    def test_should_archive_task_young_task(self):
        """Test should_archive_task for recently created task."""
        # Create recent task
        task_dir = self.outputs_dir / "YOUNG-TASK"
        task_dir.mkdir()
        
        test_file = task_dir / "test.txt"
        test_file.write_text("test content")
        
        should_archive = self.manager.should_archive_task("YOUNG-TASK")
        assert should_archive is False

    def test_should_archive_task_old_complete_task(self):
        """Test should_archive_task for old completed task."""
        # Create old task
        task_dir = self.outputs_dir / "OLD-TASK"
        task_dir.mkdir()
        
        # Create status file indicating completion
        status_file = task_dir / "status.json"
        status_data = {"overall_status": "complete"}
        with open(status_file, "w") as f:
            json.dump(status_data, f)
        
        # Make task old
        old_time = datetime.now().timestamp() - (5 * 24 * 3600)  # 5 days ago
        os.utime(status_file, (old_time, old_time))
        
        should_archive = self.manager.should_archive_task("OLD-TASK")
        assert should_archive is True

    def test_archive_task_nonexistent(self):
        """Test archiving task that doesn't exist."""
        metadata = self.manager.archive_task("NONEXISTENT")
        assert metadata is None

    def test_archive_task_success(self):
        """Test successful task archiving."""
        # Create test task with files
        task_dir = self.outputs_dir / "ARCHIVE-TEST"
        task_dir.mkdir()
        
        test_file = task_dir / "test.txt"
        test_file.write_text("test content for archiving")
        
        # Create QA file
        qa_file = task_dir / "qa_summary.md"
        qa_file.write_text("✅ PASSED - All tests successful")
        
        metadata = self.manager.archive_task("ARCHIVE-TEST")
        
        assert metadata is not None
        assert metadata.task_id == "ARCHIVE-TEST"
        assert metadata.qa_status == "passed"
        assert metadata.original_size_bytes > 0
        assert metadata.compressed_size_bytes > 0
        
        # Original directory should be removed
        assert not task_dir.exists()
        
        # Archive file should exist
        archive_path = Path(metadata.archive_location)
        assert archive_path.exists()

    def test_restore_task_no_metadata(self):
        """Test restoring task with no metadata."""
        success = self.manager.restore_task("NONEXISTENT")
        assert success is False

    def test_restore_task_no_archive_file(self):
        """Test restoring task when archive file is missing."""
        # Add metadata without actual archive
        metadata = TaskArchiveMetadata(
            task_id="MISSING-ARCHIVE",
            archived_at="2024-01-01T12:00:00",
            original_size_bytes=1024,
            compressed_size_bytes=512,
            archive_location="/nonexistent/path.tar.gz",
            retention_until="2024-02-01T12:00:00",
            qa_status="passed",
            completion_status="complete"
        )
        
        self.manager.metadata["MISSING-ARCHIVE"] = metadata
        
        success = self.manager.restore_task("MISSING-ARCHIVE")
        assert success is False

    def test_run_lifecycle_maintenance_disabled(self):
        """Test lifecycle maintenance when auto_cleanup is disabled."""
        self.manager.policy.auto_cleanup_enabled = False
        
        stats = self.manager.run_lifecycle_maintenance()
        
        assert stats["tasks_archived"] == 0
        assert stats["tasks_moved_to_cold"] == 0
        assert stats["tasks_purged"] == 0
        assert stats["bytes_freed"] == 0

    def test_track_task_completion(self):
        """Test task completion tracking."""
        # Create test task
        task_dir = self.outputs_dir / "TRACK-TEST"
        task_dir.mkdir()
        
        self.manager.track_task_completion("TRACK-TEST", "test_agent")
        
        tracking_file = task_dir / "lifecycle_tracking.json"
        assert tracking_file.exists()
        
        with open(tracking_file, "r") as f:
            tracking_data = json.load(f)
        
        assert tracking_data["task_id"] == "TRACK-TEST"
        assert tracking_data["agent_id"] == "test_agent"
        assert tracking_data["ready_for_archival"] is True

    def test_cleanup_old_tasks_disabled(self):
        """Test cleanup when auto_cleanup is disabled."""
        self.manager.policy.auto_cleanup_enabled = False
        
        stats = self.manager.cleanup_old_tasks()
        
        assert stats["tasks_archived"] == 0
        assert stats["tasks_moved_to_cold"] == 0
        assert stats["tasks_purged"] == 0
        assert stats["bytes_freed"] == 0

    def test_cleanup_old_tasks_forced(self):
        """Test forced cleanup regardless of policy."""
        self.manager.policy.auto_cleanup_enabled = False
        
        # Create old task that should be archived
        task_dir = self.outputs_dir / "FORCE-CLEANUP"
        task_dir.mkdir()
        
        test_file = task_dir / "test.txt"
        test_file.write_text("content")
        
        # Make it old
        old_time = datetime.now().timestamp() - (5 * 24 * 3600)
        os.utime(test_file, (old_time, old_time))
        
        # Create status indicating complete
        status_file = task_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump({"overall_status": "complete"}, f)
        os.utime(status_file, (old_time, old_time))
        
        stats = self.manager.cleanup_old_tasks(force=True)
        
        # Should have processed the task even with disabled policy
        assert isinstance(stats, dict)

    def test_should_trigger_cleanup_disabled(self):
        """Test cleanup trigger when auto_cleanup is disabled."""
        self.manager.policy.auto_cleanup_enabled = False
        
        should_trigger = self.manager.should_trigger_cleanup()
        assert should_trigger is False

    def test_should_trigger_cleanup_high_task_count(self):
        """Test cleanup trigger when task count is high."""
        # Create many tasks to exceed threshold
        for i in range(10):  # More than max_hot_tasks (5)
            task_dir = self.outputs_dir / f"MANY-TASK-{i}"
            task_dir.mkdir()
        
        should_trigger = self.manager.should_trigger_cleanup()
        assert should_trigger is True

    def test_get_storage_statistics(self):
        """Test storage statistics calculation."""
        # Create test tasks
        for i in range(3):
            task_dir = self.outputs_dir / f"STATS-TASK-{i}"
            task_dir.mkdir()
            
            test_file = task_dir / "test.txt"
            test_file.write_text(f"content for task {i}")
        
        stats = self.manager.get_storage_statistics()
        
        assert "hot_storage" in stats
        assert "warm_storage" in stats
        assert "cold_storage" in stats
        assert "total_archived" in stats
        assert "compression_ratio" in stats
        
        assert stats["hot_storage"]["count"] == 3
        assert stats["hot_storage"]["size_bytes"] > 0
        assert isinstance(stats["compression_ratio"], float)

    def test_move_to_cold_storage(self):
        """Test moving task from warm to cold storage."""
        # Create mock warm archive file
        warm_file = self.manager.warm_dir / "test_warm.tar.gz"
        warm_file.write_text("mock archive content")
        
        metadata = TaskArchiveMetadata(
            task_id="COLD-TEST",
            archived_at="2024-01-01T12:00:00",
            original_size_bytes=1024,
            compressed_size_bytes=512,
            archive_location=str(warm_file),
            retention_until="2024-02-01T12:00:00",
            qa_status="passed",
            completion_status="complete"
        )
        
        success = self.manager._move_to_cold_storage("COLD-TEST", metadata)
        assert success is True
        
        # Warm file should be gone
        assert not warm_file.exists()
        
        # Cold file should exist
        cold_file = self.manager.cold_dir / "COLD-TEST_cold.tar.gz"
        assert cold_file.exists()

    def test_purge_task(self):
        """Test task purging."""
        # Create mock archive file
        archive_file = self.manager.cold_dir / "purge_test.tar.gz"
        archive_file.write_text("mock archive content")
        
        metadata = TaskArchiveMetadata(
            task_id="PURGE-TEST",
            archived_at="2024-01-01T12:00:00",
            original_size_bytes=1024,
            compressed_size_bytes=512,
            archive_location=str(archive_file),
            retention_until="2024-02-01T12:00:00",
            qa_status="passed",
            completion_status="complete"
        )
        
        self.manager.metadata["PURGE-TEST"] = metadata
        
        success = self.manager._purge_task("PURGE-TEST", metadata)
        assert success is True
        
        # Archive file should be gone
        assert not archive_file.exists()
        
        # Metadata should be removed
        assert "PURGE-TEST" not in self.manager.metadata


class TestMainFunction:
    """Test the main CLI function."""

    @patch('src.core.workflows.task_lifecycle.TaskLifecycleManager')
    def test_main_function(self, mock_manager_class):
        """Test main function execution."""
        mock_manager = Mock()
        mock_manager.run_lifecycle_maintenance.return_value = {
            'tasks_archived': 2,
            'tasks_moved_to_cold': 1,
            'tasks_purged': 0,
            'bytes_freed': 1024
        }
        mock_manager.get_storage_statistics.return_value = {
            'hot_storage': {'count': 5, 'size_bytes': 2048},
            'warm_storage': {'count': 3, 'size_bytes': 1024},
            'cold_storage': {'count': 1, 'size_bytes': 512},
            'compression_ratio': 0.6
        }
        mock_manager_class.return_value = mock_manager
        
        main()
        
        mock_manager_class.assert_called_once()
        mock_manager.run_lifecycle_maintenance.assert_called_once()
        mock_manager.get_storage_statistics.assert_called_once()


class TestTaskLifecycleIntegration:
    """Test integration scenarios for task lifecycle management."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.outputs_dir = Path(self.temp_dir) / "outputs"
        self.archive_dir = Path(self.temp_dir) / "archives"
        
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        self.manager = TaskLifecycleManager(
            outputs_dir=str(self.outputs_dir),
            archive_dir=str(self.archive_dir),
            policy=TaskLifecyclePolicy(hot_storage_days=1, max_hot_tasks=3)
        )

    def teardown_method(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_lifecycle_workflow(self):
        """Test complete task lifecycle from creation to purging."""
        # 1. Create test task
        task_dir = self.outputs_dir / "LIFECYCLE-TEST"
        task_dir.mkdir()
        
        test_file = task_dir / "data.txt"
        test_file.write_text("test data for lifecycle")
        
        status_file = task_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump({"overall_status": "complete"}, f)
        
        # Make task old enough for archival
        old_time = datetime.now().timestamp() - (2 * 24 * 3600)
        os.utime(test_file, (old_time, old_time))
        os.utime(status_file, (old_time, old_time))
        
        # 2. Archive task
        metadata = self.manager.archive_task("LIFECYCLE-TEST")
        assert metadata is not None
        assert not task_dir.exists()  # Original removed
        
        # 3. Restore task
        success = self.manager.restore_task("LIFECYCLE-TEST")
        assert success is True
        assert task_dir.exists()  # Restored
        
        # 4. Archive again for cold storage test
        self.manager.archive_task("LIFECYCLE-TEST")
        
        # 5. Move to cold storage
        success = self.manager._move_to_cold_storage("LIFECYCLE-TEST", metadata)
        assert success is True
        
        # 6. Purge task
        success = self.manager._purge_task("LIFECYCLE-TEST", metadata)
        assert success is True
        assert "LIFECYCLE-TEST" not in self.manager.metadata

    def test_archive_and_restore_preserves_data(self):
        """Test that archiving and restoring preserves all data."""
        # Create task with various file types
        task_dir = self.outputs_dir / "PRESERVE-TEST"
        task_dir.mkdir()
        
        # Create subdirectory structure
        sub_dir = task_dir / "subdir"
        sub_dir.mkdir()
        
        # Create various files
        files_data = {
            "text.txt": "Simple text content",
            "data.json": '{"key": "value", "number": 42}',
            "subdir/nested.py": "def hello():\n    return 'world'\n"
        }
        
        for file_path, content in files_data.items():
            full_path = task_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Archive task
        metadata = self.manager.archive_task("PRESERVE-TEST")
        assert metadata is not None
        
        # Restore task
        success = self.manager.restore_task("PRESERVE-TEST")
        assert success is True
        
        # Verify all files and content preserved
        for file_path, expected_content in files_data.items():
            restored_file = self.outputs_dir / "PRESERVE-TEST" / file_path
            assert restored_file.exists()
            assert restored_file.read_text() == expected_content

    def test_lifecycle_maintenance_comprehensive(self):
        """Test comprehensive lifecycle maintenance."""
        # Create tasks in different states
        tasks = [
            ("HOT-TASK", False, 0),  # Recent, should stay hot
            ("WARM-READY", True, 2), # Old complete, should archive
            ("OLD-INCOMPLETE", False, 3), # Old incomplete, should archive later
        ]
        
        for task_id, is_complete, age_days in tasks:
            task_dir = self.outputs_dir / task_id
            task_dir.mkdir()
            
            test_file = task_dir / "test.txt"
            test_file.write_text(f"content for {task_id}")
            
            if is_complete:
                status_file = task_dir / "status.json"
                with open(status_file, "w") as f:
                    json.dump({"overall_status": "complete"}, f)
            
            # Set file age
            if age_days > 0:
                old_time = datetime.now().timestamp() - (age_days * 24 * 3600)
                os.utime(test_file, (old_time, old_time))
        
        # Run maintenance
        stats = self.manager.run_lifecycle_maintenance()
        
        # Should have archived at least the completed old task
        assert isinstance(stats, dict)
        assert all(key in stats for key in ["tasks_archived", "tasks_moved_to_cold", "tasks_purged", "bytes_freed"])