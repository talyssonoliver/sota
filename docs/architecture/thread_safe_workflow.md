# orchestration/thread_safe_workflow.py

## Classes
- **WorkflowPriority** (line 23)
- **TaskExecution** (line 32)
- **ThreadSafeWorkflowOrchestrator** (line 55)
  - Methods: __init__, add_task, execute_workflow, _validate_dependencies, _queue_ready_tasks, _is_task_ready, _get_priority_value, _execute_tasks_parallel, _execute_task, _queue_dependent_tasks, _wait_for_completion, _collect_results, _cleanup_execution, get_statistics, get_task_status, cancel_workflow, reset

## Functions
- **create_thread_safe_workflow(max_workers, enable_error_propagation)** (line 533)
- **execute_tasks_parallel(tasks, max_workers, timeout)** (line 548)
