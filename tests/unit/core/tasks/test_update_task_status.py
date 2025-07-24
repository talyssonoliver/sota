"""
Comprehensive tests for task_loader module.

Tests TaskLoader class and utility functions for loading and managing task metadata.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from src.infrastructure.utils.task_loader import (
    TaskLoader,
    get_all_tasks,
    load_task_metadata,
    update_task_state,
)


class TestTaskLoader:
    """Test the TaskLoader class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.loader = TaskLoader()

    def test_init(self):
        """Test TaskLoader initialization."""
        assert self.loader.tasks == []

    def test_load_task(self):
        """Test loading a single task."""
        task_path = "/test/path/task.yaml"
        result = self.loader.load_task(task_path)
        
        expected = {"path": task_path, "status": "loaded", "content": {}}
        assert result == expected

    def test_load_all_tasks_empty_directory(self):
        """Test loading tasks from empty directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = self.loader.load_all_tasks(tmp_dir)
            assert result == []

    def test_load_all_tasks_nonexistent_directory(self):
        """Test loading tasks from non-existent directory."""
        result = self.loader.load_all_tasks("/nonexistent/directory")
        assert result == []

    def test_load_all_tasks_with_files(self):
        """Test loading tasks from directory with task files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create test files
            yaml_file = Path(tmp_dir) / "task1.yaml"
            json_file = Path(tmp_dir) / "task2.json"
            other_file = Path(tmp_dir) / "readme.txt"
            
            yaml_file.write_text("test: data")
            json_file.write_text('{"test": "data"}')
            other_file.write_text("ignored")
            
            result = self.loader.load_all_tasks(tmp_dir)
            
            # Should load 2 files (yaml and json, not txt)
            assert len(result) == 2
            paths = {task["path"] for task in result}
            assert str(yaml_file) in paths
            assert str(json_file) in paths


class TestLoadTaskMetadata:
    """Test the load_task_metadata function."""

    def test_load_nonexistent_task(self):
        """Test loading metadata for non-existent task."""
        result = load_task_metadata("NONEXISTENT-01")
        
        expected = {
            "id": "NONEXISTENT-01",
            "state": "pending",
            "status": "pending",
            "depends_on": [],
            "metadata": {},
        }
        assert result == expected

    def test_load_yaml_task(self):
        """Test loading metadata from YAML file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            task_file = Path(tmp_dir) / "tasks" / "TEST-01.yaml"
            task_file.parent.mkdir(exist_ok=True)
            
            task_data = {
                "id": "TEST-01",
                "title": "Test Task",
                "state": "completed",
                "metadata": {"priority": "high"}
            }
            
            with open(task_file, "w", encoding="utf-8") as f:
                yaml.safe_dump(task_data, f)
            
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = load_task_metadata("TEST-01")
                assert result["id"] == "TEST-01"
                assert result["title"] == "Test Task"
                assert result["state"] == "completed"
                assert result["metadata"]["priority"] == "high"
            finally:
                os.chdir(orig_cwd)

    def test_load_json_task(self):
        """Test loading metadata from JSON file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            task_file = Path(tmp_dir) / "tasks" / "TEST-02.json"
            task_file.parent.mkdir(exist_ok=True)
            
            task_data = {
                "id": "TEST-02",
                "title": "JSON Test Task",
                "state": "in_progress",
                "metadata": {"assignee": "test_user"}
            }
            
            with open(task_file, "w", encoding="utf-8") as f:
                json.dump(task_data, f)
            
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = load_task_metadata("TEST-02")
                assert result["id"] == "TEST-02"
                assert result["title"] == "JSON Test Task"
                assert result["state"] == "in_progress"
                assert result["metadata"]["assignee"] == "test_user"
            finally:
                os.chdir(orig_cwd)

    def test_load_corrupted_file(self):
        """Test loading metadata from corrupted file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            task_file = Path(tmp_dir) / "tasks" / "CORRUPTED-01.yaml"
            task_file.parent.mkdir(exist_ok=True)
            
            # Write invalid YAML
            with open(task_file, "w", encoding="utf-8") as f:
                f.write("invalid: yaml: content: [")
            
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = load_task_metadata("CORRUPTED-01")
                # Should return default metadata on parsing error
                assert result["id"] == "CORRUPTED-01"
                assert result["state"] == "pending"
            finally:
                os.chdir(orig_cwd)

    @patch("yaml.safe_load")
    def test_yaml_import_error_fallback(self, mock_yaml_load):
        """Test fallback when YAML operations fail."""
        mock_yaml_load.side_effect = Exception("YAML error")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            task_file = Path(tmp_dir) / "tasks" / "TEST-03.yaml"
            task_file.parent.mkdir(exist_ok=True)
            
            with open(task_file, "w", encoding="utf-8") as f:
                f.write("test: data")
            
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = load_task_metadata("TEST-03")
                # Should return default metadata on error
                assert result["id"] == "TEST-03"
                assert result["state"] == "pending"
            finally:
                os.chdir(orig_cwd)


class TestUpdateTaskState:
    """Test the update_task_state function."""

    def test_update_existing_yaml_task(self):
        """Test updating state of existing YAML task."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            task_file = Path(tmp_dir) / "tasks" / "UPDATE-01.yaml"
            task_file.parent.mkdir(exist_ok=True)
            
            initial_data = {
                "id": "UPDATE-01",
                "title": "Update Test",
                "state": "pending"
            }
            
            with open(task_file, "w", encoding="utf-8") as f:
                yaml.safe_dump(initial_data, f)
            
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = update_task_state("UPDATE-01", "completed")
                assert result is True
                
                # Verify the update
                updated_data = load_task_metadata("UPDATE-01")
                assert updated_data["state"] == "completed"
                assert updated_data["status"] == "completed"
                assert "updated" in updated_data
            finally:
                os.chdir(orig_cwd)

    def test_update_with_metadata(self):
        """Test updating task state with additional metadata."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            task_file = Path(tmp_dir) / "tasks" / "META-01.yaml"
            task_file.parent.mkdir(exist_ok=True)
            
            initial_data = {"id": "META-01", "state": "pending"}
            
            with open(task_file, "w", encoding="utf-8") as f:
                yaml.safe_dump(initial_data, f)
            
            metadata = {"completion_time": "2024-01-01", "notes": "Test completion"}
            
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = update_task_state("META-01", "completed", metadata)
                assert result is True
                
                updated_data = load_task_metadata("META-01")
                assert updated_data["metadata"]["completion_time"] == "2024-01-01"
                assert updated_data["metadata"]["notes"] == "Test completion"
            finally:
                os.chdir(orig_cwd)

    def test_create_new_task_file(self):
        """Test creating new task file when none exists."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = update_task_state("NEW-01", "created")
                assert result is True
                
                # Check that file was created
                task_file = Path("tasks/NEW-01.yaml")
                assert task_file.exists()
                
                # Verify content
                task_data = load_task_metadata("NEW-01")
                assert task_data["id"] == "NEW-01"
                assert task_data["state"] == "created"
                assert task_data["status"] == "created"
            finally:
                os.chdir(orig_cwd)

    def test_update_existing_json_task(self):
        """Test updating existing JSON task."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            task_file = Path(tmp_dir) / "tasks" / "JSON-01.json"
            task_file.parent.mkdir(exist_ok=True)
            
            initial_data = {"id": "JSON-01", "state": "pending"}
            
            with open(task_file, "w", encoding="utf-8") as f:
                json.dump(initial_data, f)
            
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = update_task_state("JSON-01", "completed")
                assert result is True
                
                updated_data = load_task_metadata("JSON-01")
                assert updated_data["state"] == "completed"
            finally:
                os.chdir(orig_cwd)

    @patch("datetime.datetime")
    def test_timestamp_handling(self, mock_datetime):
        """Test timestamp addition when datetime is available."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                update_task_state("TIME-01", "completed")
                task_data = load_task_metadata("TIME-01")
                assert task_data["updated"] == "2024-01-01T12:00:00"
            finally:
                os.chdir(orig_cwd)

    def test_update_failure_scenarios(self):
        """Test update failure handling."""
        # Test with invalid directory permissions scenario
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a read-only directory scenario by mocking os.makedirs to fail
            with patch("os.makedirs", side_effect=PermissionError("Permission denied")):
                orig_cwd = os.getcwd()
                os.chdir(tmp_dir)
                try:
                    result = update_task_state("FAIL-01", "completed")
                    # Should handle the error gracefully
                    assert result is False
                finally:
                    os.chdir(orig_cwd)


class TestGetAllTasks:
    """Test the get_all_tasks function."""

    def test_empty_directories(self):
        """Test getting tasks from empty directories."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = get_all_tasks()
                assert result == []
            finally:
                os.chdir(orig_cwd)

    def test_mixed_task_files(self):
        """Test getting all tasks from multiple directories."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create various task files
            tasks_dir = Path(tmp_dir) / "tasks"
            backend_dir = Path(tmp_dir) / "src/core/tasks/backend"
            frontend_dir = Path(tmp_dir) / "src/core/tasks/frontend"
            
            tasks_dir.mkdir(parents=True, exist_ok=True)
            backend_dir.mkdir(parents=True, exist_ok=True)
            frontend_dir.mkdir(parents=True, exist_ok=True)
            
            # Create task files
            (tasks_dir / "TASK-01.yaml").write_text("id: TASK-01")
            (tasks_dir / "TASK-02.json").write_text('{"id": "TASK-02"}')
            (backend_dir / "BE-01.yaml").write_text("id: BE-01")
            (frontend_dir / "FE-01.json").write_text('{"id": "FE-01"}')
            (tasks_dir / "readme.txt").write_text("Not a task file")
            
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = get_all_tasks()
                # Should be sorted and deduplicated
                expected = ["BE-01", "FE-01", "TASK-01", "TASK-02"]
                assert result == expected
            finally:
                os.chdir(orig_cwd)

    def test_duplicate_task_ids(self):
        """Test handling of duplicate task IDs in different directories."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tasks_dir = Path(tmp_dir) / "tasks"
            core_dir = Path(tmp_dir) / "src/core/tasks"
            
            tasks_dir.mkdir(parents=True, exist_ok=True)
            core_dir.mkdir(parents=True, exist_ok=True)
            
            # Create duplicate task IDs
            (tasks_dir / "DUP-01.yaml").write_text("id: DUP-01")
            (core_dir / "DUP-01.json").write_text('{"id": "DUP-01"}')
            
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = get_all_tasks()
                # Should appear only once
                assert result == ["DUP-01"]
            finally:
                os.chdir(orig_cwd)

    def test_nonexistent_directories(self):
        """Test behavior when search directories don't exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Only create one of the search directories
            tasks_dir = Path(tmp_dir) / "tasks"
            tasks_dir.mkdir(exist_ok=True)
            (tasks_dir / "EXIST-01.yaml").write_text("id: EXIST-01")
            
            orig_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = get_all_tasks()
                assert result == ["EXIST-01"]
            finally:
                os.chdir(orig_cwd)