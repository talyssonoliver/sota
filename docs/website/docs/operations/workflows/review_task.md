# orchestration/review_task.py

## Classes
- **AdvancedReviewPortal** (line 54)
  - Methods: __init__, load_policies, review_task, batch_review, review_checkpoint, dashboard_view, _load_task_data, _display_task_overview, _load_agent_outputs, _display_agent_outputs, _display_code_diffs, _show_sample_diff, _load_qa_results, _display_qa_metrics, _load_hitl_checkpoints, _display_checkpoints, _interactive_review, _approve_task, _reject_task, _request_changes, _escalate_task, _show_detailed_output, _export_review_data, _quick_review_checkpoint, _process_checkpoint_approval, _process_checkpoint_rejection, _interactive_checkpoint_review, _display_checkpoint_details, _display_task_context, _display_review_metrics, _display_recent_activity, _checkpoint_to_dict, _apply_filters, _is_overdue, _get_task_status, _get_creation_time, _get_last_modified, _escalate_checkpoint, _export_checkpoint_data, _generate_session_summary

## Functions
- **setup_logging(verbose)** (line 41)
- **cmd_review_task(args)** (line 891)
- **cmd_batch_review(args)** (line 908)
- **cmd_review_checkpoint(args)** (line 933)
- **cmd_dashboard(args)** (line 949)
- **main()** (line 956)
