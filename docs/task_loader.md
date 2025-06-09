# Task Loader Documentation

**File:** `utils/task_loader.py`
**Type:** configuration loader
**Purpose:** Handles reading and writing task metadata stored as YAML files under the `tasks/` directory.

## Functions
### `load_task_metadata(task_id)`
Loads a task's YAML file and returns a dictionary. Falls back to `context-store/agent_task_assignments.json` if the file is missing.

### `save_task_metadata(task_id, metadata)`
Writes the given metadata dictionary back to the YAML file, converting enum values to strings for compatibility.

### `get_all_tasks()`
Iterates over all YAML files in `tasks/` and returns a list of their metadata.

### `update_task_state(task_id, new_state)`
Convenience wrapper that loads the task, sets its `state` field and saves it back to disk.

### Retrieval Helpers
- `get_tasks_by_state(state)` – filter tasks by lifecycle state
- `get_dependent_tasks(task_id)` – list tasks that depend on a given task
- `get_tasks_by_owner(owner)` – filter by agent role
- `get_tasks_by_priority(priority)` – filter by priority
- `validate_task_dependencies(task_id=None)` – verify missing or circular dependencies

## Example
```python
meta = load_task_metadata("BE-07")
meta['state'] = 'IN_PROGRESS'
save_task_metadata("BE-07", meta)
```
