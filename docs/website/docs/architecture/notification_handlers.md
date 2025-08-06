# orchestration/notification_handlers.py

## Classes
- **NotificationHandler** (line 23)
  - Methods: send_notification
- **DashboardNotificationHandler** (line 32)
  - Methods: __init__, send_notification, _get_notification_title, _get_notification_message, _get_notification_severity, _update_dashboard_data, _save_to_local_storage
- **EmailNotificationHandler** (line 161)
  - Methods: __init__, _load_email_templates, send_notification, _is_email_configured, _get_email_recipients, _prepare_email_data, _format_review_items, _calculate_overdue_duration, _format_review_history, _send_email
- **SlackNotificationHandler** (line 413)
  - Methods: __init__, send_notification, _prepare_slack_message
