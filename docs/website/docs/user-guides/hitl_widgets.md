# dashboard/hitl_widgets.py

## Classes
- **HITLWidget** (line 25)
  - Methods: __init__, get_data, get_widget_config
- **HITLPendingReviewsWidget** (line 44)
  - Methods: get_data, get_widget_config, _calculate_time_remaining, _calculate_priority, _get_assigned_reviewer
- **HITLApprovalActionsWidget** (line 218)
  - Methods: get_data, get_widget_config, process_action
- **HITLMetricsWidget** (line 256)
  - Methods: get_data, get_widget_config, _get_daily_trend, _get_review_time_trend
- **HITLWorkflowStatusWidget** (line 335)
  - Methods: get_data, get_widget_config, _get_active_workflows, _get_workflow_hitl_status
- **HITLDashboardManager** (line 404)
  - Methods: __init__, get_dashboard_data, get_widget_data, process_widget_action, export_dashboard_state

## Functions
- **get_hitl_kanban_data()** (line 467)
- **get_hitl_dashboard_data()** (line 473)
- **process_hitl_action(checkpoint_id, action, reviewer, comments)** (line 479)
