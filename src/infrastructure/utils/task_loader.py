"""Task loading utilities."""

import json
import os

try:
    import yaml
except ImportError:
    pass
from typing import Any, Dict, List, Optional


class TaskLoader:
    """Load and manage tasks."""

    def __init__(self):
        """Initialize task loader."""
        self.tasks = []

    def load_task(self, task_path):
        """Load a task from file."""
        return {"path": task_path, "status": "loaded", "content": {}}

    def load_all_tasks(self, directory):
        """Load all tasks from directory."""
        tasks = []
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith(".yaml") or file.endswith(".json"):
                    tasks.append(self.load_task(os.path.join(directory, file)))
        return tasks


def load_task_metadata(task_id: str) -> Dict[str, Any]:
    """Load task metadata from task files.

    Args:
        task_id: Task identifier (e.g., 'BE-01', 'FE-02')

    Returns:
        Dict containing task metadata
    """
    # Search for task file in various locations
    search_paths = [
        f"tasks/{task_id}.yaml",
        f"tasks/{task_id}.json",
        f"src/core/tasks/{task_id}.yaml",
        f"src/core/tasks/{task_id}.json",
        f"src/core/tasks/backend/{task_id}.yaml",
        f"src/core/tasks/backend/{task_id}.json",
        f"src/core/tasks/frontend/{task_id}.yaml",
        f"src/core/tasks/frontend/{task_id}.json",
        f"src/core/tasks/general/{task_id}.yaml",
        f"src/core/tasks/general/{task_id}.json",
    ]

    for path in search_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    if path.endswith(".yaml"):
                        return yaml.safe_load(f) or {}
                    else:
                        return json.load(f) or {}
            except Exception:
                continue

    # Return default metadata if file not found
    return {
        "id": task_id,
        "state": "pending",
        "status": "pending",
        "depends_on": [],
        "metadata": {},
    }


def update_task_state(
    task_id: str, new_state: str, metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Update task state and metadata.

    Args:
        task_id: Task identifier
        new_state: New state to set (e.g., 'completed', 'failed', 'in_progress')
        metadata: Optional metadata to update

    Returns:
        bool: True if update was successful
    """
    try:
        # Load current task data
        task_data = load_task_metadata(task_id)

        # Update state
        task_data["state"] = new_state
        task_data["status"] = new_state

        # Update metadata if provided
        if metadata:
            if "metadata" not in task_data:
                task_data["metadata"] = {}
            task_data["metadata"].update(metadata)

        # Add timestamp
        try:
            import datetime

            task_data["updated"] = datetime.datetime.now().isoformat()
        except ImportError:
            pass

        # Try to save back to original location
        search_paths = [
            f"tasks/{task_id}.yaml",
            f"tasks/{task_id}.json",
            f"src/core/tasks/{task_id}.yaml",
            f"src/core/tasks/{task_id}.json",
            f"src/core/tasks/backend/{task_id}.yaml",
            f"src/core/tasks/backend/{task_id}.json",
            f"src/core/tasks/frontend/{task_id}.yaml",
            f"src/core/tasks/frontend/{task_id}.json",
            f"src/core/tasks/general/{task_id}.yaml",
            f"src/core/tasks/general/{task_id}.json",
        ]

        for path in search_paths:
            if os.path.exists(path):
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        if path.endswith(".yaml"):
                            yaml.dump(task_data, f, default_flow_style=False)
                        else:
                            json.dump(task_data, f, indent=2)
                    return True
                except Exception:
                    continue

        # If no existing file found, create new one in tasks directory
        os.makedirs("tasks", exist_ok=True)
        output_path = f"tasks/{task_id}.yaml"

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(task_data, f, default_flow_style=False)

        return True

    except Exception:
        return False


def get_all_tasks() -> List[str]:
    """Get all available task IDs from the tasks directory.

    Returns:
        List of task IDs (e.g., ['BE-01', 'FE-02', 'TL-01'])
    """
    task_ids = []
    search_directories = [
        "tasks",
        "src/core/tasks",
        "src/core/tasks/backend",
        "src/core/tasks/frontend",
        "src/core/tasks/general",
    ]

    for directory in search_directories:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith(".yaml") or file.endswith(".json"):
                    # Extract task ID from filename (e.g., 'BE-01.yaml' -> 'BE-01')
                    task_id = os.path.splitext(file)[0]
                    if task_id not in task_ids:
                        task_ids.append(task_id)

    return sorted(task_ids)


__all__ = [
    "TaskLoader",
    "load_task_metadata",
    "update_task_state",
    "get_all_tasks",
]
