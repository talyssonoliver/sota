# orchestration/hitl_task_metadata.py

## Classes
- **HITLStatus** (line 20)
- **HITLRiskLevel** (line 30)
- **HITLCheckpointMetadata** (line 39)
  - Methods: to_dict, from_dict
- **HITLTaskMetadata** (line 81)
  - Methods: add_hitl_checkpoint, get_active_checkpoints, get_checkpoint_by_id, update_checkpoint_status, update_phase, calculate_risk_score, is_blocked_on_hitl, to_dict, from_dict
- **HITLTaskMetadataManager** (line 272)
  - Methods: __init__, save_task_metadata, load_task_metadata, get_all_tasks, get_tasks_with_active_hitl, get_tasks_by_status, get_tasks_by_hitl_status, get_tasks_by_risk_level, update_task_status, add_checkpoint_to_task, update_checkpoint_status, create_task_from_legacy, get_statistics
