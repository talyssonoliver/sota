"""
Task Metadata Loader Utilities
Provides functions for loading and managing task metadata from YAML files.
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

def load_task_metadata(task_id: str) -> Dict[str, Any]:
    """
    Load task metadata from YAML file.
    
    Args:
        task_id: Unique task identifier
        
    Returns:
        Dictionary containing task metadata
        
    Raises:
        FileNotFoundError: If task file doesn't exist
        ValueError: If task metadata is invalid
    """
    task_file = Path("tasks") / f"{task_id}.yaml"
    
    if not task_file.exists():
        # Fallback to agent_task_assignments.json
        assignments_file = Path("context-store") / "agent_task_assignments.json"
        if assignments_file.exists():
            try:
                with open(assignments_file, 'r', encoding='utf-8') as f:
                    assignments = json.load(f)
                
                # Find task in assignments
                for task in assignments.get('tasks', []):
                    if task.get('id') == task_id:
                        logger.warning(f"Using fallback data from agent_task_assignments.json for task {task_id}")
                        return task
                        
            except Exception as e:
                logger.error(f"Error reading fallback assignments file: {e}")
        
        raise FileNotFoundError(f"Task file not found: {task_file}")
    
    try:
        with open(task_file, 'r', encoding='utf-8') as f:
            metadata = yaml.safe_load(f)
        
        if not metadata or 'id' not in metadata:
            raise ValueError(f"Invalid task metadata in {task_file}")
            
        return metadata
        
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format in {task_file}: {e}")
    except Exception as e:
        raise ValueError(f"Error loading task metadata from {task_file}: {e}")


def save_task_metadata(task_id: str, metadata: Dict[str, Any]) -> None:
    """
    Save task metadata to YAML file.
    
    Args:
        task_id: Unique task identifier
        metadata: Task metadata dictionary
    """
    task_file = Path("tasks") / f"{task_id}.yaml"
    task_file.parent.mkdir(exist_ok=True)
    
    # Convert TaskStatus enums to strings before saving
    cleaned_metadata = {}
    for key, value in metadata.items():
        if hasattr(value, 'value') and hasattr(value, 'name'):  # Likely an enum
            cleaned_metadata[key] = str(value)  # Convert enum to string
        else:
            cleaned_metadata[key] = value
    
    try:
        with open(task_file, 'w', encoding='utf-8') as f:
            yaml.dump(cleaned_metadata, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"Task metadata saved for {task_id}")
        
    except Exception as e:
        logger.error(f"Error saving task metadata for {task_id}: {e}")
        raise


def get_all_tasks() -> List[Dict[str, Any]]:
    """
    Get all available tasks from YAML files.
    
    Returns:
        List of task metadata dictionaries
    """
    tasks = []
    tasks_dir = Path("tasks")
    
    if not tasks_dir.exists():
        logger.warning("Tasks directory not found")
        return tasks
    
    for task_file in tasks_dir.glob("*.yaml"):
        try:
            task_id = task_file.stem
            metadata = load_task_metadata(task_id)
            tasks.append(metadata)
        except Exception as e:
            logger.warning(f"Failed to load task from {task_file}: {e}")
            continue
    
    return tasks


def update_task_state(task_id: str, new_state: str) -> None:
    """
    Update task state in YAML file.
    
    Args:
        task_id: Unique task identifier
        new_state: New task state
    """
    try:
        metadata = load_task_metadata(task_id)
        metadata['state'] = new_state
        save_task_metadata(task_id, metadata)
        
        logger.info(f"Task {task_id} state updated to {new_state}")
        
    except Exception as e:
        logger.error(f"Error updating task state for {task_id}: {e}")
        raise


def get_tasks_by_state(state: str) -> List[Dict[str, Any]]:
    """
    Get tasks in a specific state.
    
    Args:
        state: Task state to filter by
        
    Returns:
        List of task metadata dictionaries
    """
    all_tasks = get_all_tasks()
    return [task for task in all_tasks if task.get('state') == state]


def get_dependent_tasks(task_id: str) -> List[Dict[str, Any]]:
    """
    Get tasks that depend on a given task.
    
    Args:
        task_id: Task ID to find dependents for
        
    Returns:
        List of task metadata dictionaries
    """
    all_tasks = get_all_tasks()
    dependent_tasks = []
    
    for task in all_tasks:
        dependencies = task.get('depends_on', [])
        if task_id in dependencies:
            dependent_tasks.append(task)
    
    return dependent_tasks


def get_tasks_by_owner(owner: str) -> List[Dict[str, Any]]:
    """
    Get tasks assigned to a specific owner.
    
    Args:
        owner: Owner/agent role to filter by
        
    Returns:
        List of task metadata dictionaries
    """
    all_tasks = get_all_tasks()
    return [task for task in all_tasks if task.get('owner') == owner]


def get_tasks_by_priority(priority: str) -> List[Dict[str, Any]]:
    """
    Get tasks with a specific priority.
    
    Args:
        priority: Priority level to filter by
        
    Returns:
        List of task metadata dictionaries
    """
    all_tasks = get_all_tasks()
    return [task for task in all_tasks if task.get('priority') == priority]


def validate_task_dependencies(task_id: str = None) -> Dict[str, Any]:
    """
    Validate task dependencies for circular references and missing dependencies.
    
    Args:
        task_id: Optional specific task to validate (validates all if None)
        
    Returns:
        Validation result dictionary
    """
    all_tasks = get_all_tasks()
    task_map = {task['id']: task for task in all_tasks}
    
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    tasks_to_check = [task_id] if task_id else [task['id'] for task in all_tasks]
    
    for tid in tasks_to_check:
        if tid not in task_map:
            validation_result['errors'].append(f"Task {tid} not found")
            validation_result['valid'] = False
            continue
            
        task = task_map[tid]
        dependencies = task.get('depends_on', [])
        
        # Check for missing dependencies
        for dep in dependencies:
            if dep not in task_map:
                validation_result['errors'].append(f"Task {tid} depends on missing task {dep}")
                validation_result['valid'] = False
        
        # Check for circular dependencies (simplified)
        visited = set()
        def check_circular(current_task_id):
            if current_task_id in visited:
                return True
            visited.add(current_task_id)
            
            current_task = task_map.get(current_task_id)
            if not current_task:
                return False
                
            for dep in current_task.get('depends_on', []):
                if check_circular(dep):
                    return True
            
            visited.remove(current_task_id)
            return False
        
        if check_circular(tid):
            validation_result['errors'].append(f"Circular dependency detected for task {tid}")
            validation_result['valid'] = False
    
    return validation_result