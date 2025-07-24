# orchestration/task_lifecycle.py

## Classes
- **TaskLifecyclePolicy** (line 25)
- **TaskArchiveMetadata** (line 36)
- **TaskLifecycleManager** (line 48)
  - Methods: __init__, _load_metadata, _save_metadata, get_task_age_days, should_archive_task, archive_task, restore_task, run_lifecycle_maintenance, _move_to_cold_storage, _purge_task, get_storage_statistics, track_task_completion, cleanup_old_tasks, should_trigger_cleanup

## Functions
- **main()** (line 499)
