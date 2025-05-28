"""
Test for Step 4.7 — Update Task Status
Validates that the update_task_state function sets the correct state in the YAML file.
"""
import os

import pytest
import yaml

from utils.task_loader import load_task_metadata, update_task_state


def test_update_task_status_sets_done(tmp_path):
    # Setup: create a temporary tasks directory and task YAML
    task_id = "TEST-07"
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(exist_ok=True)  # Allow directory to exist
    task_file = tasks_dir / f"{task_id}.yaml"
    initial_data = {
        "id": task_id,
        "title": "Test Task",
        "state": "IN_PROGRESS"
    }
    with open(task_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(initial_data, f)

    # Patch the loader to use the temp directory
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        update_task_state(task_id, "DONE")
        updated = load_task_metadata(task_id)
        assert updated["state"] == "DONE"
    finally:
        os.chdir(orig_cwd)
