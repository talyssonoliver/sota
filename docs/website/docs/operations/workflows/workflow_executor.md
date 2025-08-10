# Workflow Executor Documentation

**File:** `orchestration/execute_graph.py`
**Type:** workflow executor
**Purpose:** Runs LangGraph agent workflows with monitoring, notifications and command-line options.

## Overview
`execute_graph.py` provides a command-line interface to run various workflow graphs built with LangGraph. It loads task metadata, builds the initial execution state including context from the memory engine and handles progress updates. The script supports Slack notifications, execution monitoring and dry-run planning.

## Key Functions
### `build_task_state(task_id)`
Loads task metadata from `tasks/` and constructs the starting state dictionary with description, dependencies, priority and retrieved context. Falls back to `context-store/agent_task_assignments.json` when the YAML file is missing.

### `run_task_graph(task_id, workflow_type='advanced', dry_run=False, output_dir=None, enable_notifications=True, enable_monitoring=True)`
Selects a workflow builder based on the type (`advanced`, `dynamic`, `state`, `resilient`) and executes it. The function attaches Slack notifications, sets up real-time monitoring hooks and updates the task state file upon completion. Returns the workflow result dictionary.

### `main()`
Parses command-line arguments and calls `run_task_graph` with the chosen options. Supports dry runs, verbose output and enabling/disabling monitoring and notifications.

## Example Usage
```bash
python orchestration/execute_graph.py --task BE-07 --workflow advanced --monitor --notify
```
This command executes the advanced workflow for task `BE-07` with monitoring and Slack notifications enabled.
