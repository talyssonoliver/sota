"""
Task Metadata Loader Utility

This module provides functions to load and manage task metadata from YAML files.
"""

import yaml
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def load_task_metadata(task_id: str) -> Dict[str, Any]:
    """
    Load task metadata from a YAML file.
    
    Args:
        task_id: The task identifier (e.g. BE-07)
        
    Returns:
        A dictionary containing the task metadata
        
    Raises:
        FileNotFoundError: If the task file doesn't exist
        yaml.YAMLError: If there's an error parsing the YAML
    """
    path = os.path.join("tasks", f"{task_id}.yaml")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Task metadata file not found: {path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing task metadata YAML: {e}")
        raise

def get_all_tasks() -> List[str]:
    """
    Get a list of all available task IDs.
    
    Returns:
        A list of task IDs
    """
    tasks_dir = "tasks"
    task_files = [f for f in os.listdir(tasks_dir) if f.endswith('.yaml')]
    return [f[:-5] for f in task_files]  # Remove .yaml extension

def save_task_metadata(task_id: str, metadata: Dict[str, Any]) -> None:
    """
    Save task metadata to a YAML file.
    
    Args:
        task_id: The task identifier (e.g. BE-07)
        metadata: The task metadata to save
        
    Raises:
        yaml.YAMLError: If there's an error dumping the YAML
    """
    path = os.path.join("tasks", f"{task_id}.yaml")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(metadata, f, default_flow_style=False, sort_keys=False)
    except yaml.YAMLError as e:
        logger.error(f"Error saving task metadata YAML: {e}")
        raise

def update_task_state(task_id: str, state: str) -> None:
    """
    Update the state of a task.
    
    Args:
        task_id: The task identifier (e.g. BE-07)
        state: The new state (e.g. PLANNED, IN_PROGRESS, QA_PENDING, DONE, BLOCKED)
    """
    try:
        metadata = load_task_metadata(task_id)
        metadata['state'] = state
        save_task_metadata(task_id, metadata)
    except Exception as e:
        logger.error(f"Error updating task state: {e}")
        raise

def get_tasks_by_state(state: str) -> List[str]:
    """
    Get a list of tasks in a specific state.
    
    Args:
        state: The state to filter by
        
    Returns:
        A list of task IDs
    """
    tasks = []
    for task_id in get_all_tasks():
        try:
            metadata = load_task_metadata(task_id)
            if metadata.get('state') == state:
                tasks.append(task_id)
        except Exception:
            continue
    return tasks

def get_dependent_tasks(task_id: str) -> List[str]:
    """
    Get tasks that depend on the given task.
    
    Args:
        task_id: The task identifier (e.g. BE-07)
        
    Returns:
        A list of task IDs that depend on the given task
    """
    dependent_tasks = []
    for other_id in get_all_tasks():
        try:
            metadata = load_task_metadata(other_id)
            if 'depends_on' in metadata and task_id in metadata['depends_on']:
                dependent_tasks.append(other_id)
        except Exception:
            continue
    return dependent_tasks