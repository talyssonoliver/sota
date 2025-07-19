# orchestration/hitl_engine.py

## Classes
- **CheckpointType** (line 35)
- **RiskLevel** (line 44)
- **CheckpointStatus** (line 52)
- **TimeoutAction** (line 62)
- **HITLCheckpoint** (line 71)
  - Methods: __post_init__, id, is_overdue, is_approved, approval_progress, deadline, reviewers, context, to_dict
- **RiskAssessment** (line 181)
  - Methods: to_dict
- **HITLReviewDecision** (line 197)
  - Methods: __post_init__, to_dict
- **HITLAuditEntry** (line 218)
  - Methods: __post_init__, to_dict
- **HITLPolicyEngine** (line 238)
  - Methods: __init__, _load_policies, _get_default_policies, _init_notification_handlers, _get_task_type, _check_condition, _check_critical_service_changes, _check_schema_modifications, _check_security_implications, _check_coverage_threshold, _check_performance_regression, _check_breaking_changes, _generate_mitigation_suggestions, create_checkpoint, _send_notification, _create_review_items, _auto_approve_checkpoint, _escalate_checkpoint, _block_checkpoint, _notify_timeout, _save_checkpoint, _send_checkpoint_notifications, _update_task_metadata, _log_audit_event, _create_audit_entry, _assess_risk, get_checkpoint, get_pending_checkpoints, get_pending_checkpoints_for_task, get_checkpoints_for_task, process_timeouts, get_audit_trail, get_metrics, get_checkpoint_statistics, get_daily_trends, get_checkpoint_distribution, get_active_workflows, _get_escalation_policy, _normalize_policy_access

## Functions
- **create_hitl_engine(config_path)** (line 1358)
