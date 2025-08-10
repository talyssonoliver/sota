# graph/interrupt_nodes.py

## Classes
- **InterruptCheckpoint** (line 29)
  - Methods: __post_init__, is_expired, approval_file_path, pending_file_path, to_dict, from_dict
- **InterruptNodeManager** (line 75)
  - Methods: __init__, _load_existing_checkpoints, create_checkpoint, _save_checkpoint, check_approval_status, approve_task, reject_task, _cleanup_checkpoint, get_pending_reviews, get_expired_checkpoints, cleanup_expired_checkpoints

## Functions
- **get_interrupt_manager()** (line 244)
- **human_checkpoint_node(state)** (line 253)
- **conditional_human_checkpoint(state)** (line 326)
- **create_qa_checkpoint_node(qa_threshold)** (line 351)
- **create_code_review_checkpoint_node()** (line 369)
- **create_documentation_checkpoint_node()** (line 382)
- **list_pending_reviews()** (line 396)
- **approve_task_cli(task_id, approver, comments)** (line 415)
- **reject_task_cli(task_id, reviewer, reason)** (line 421)
