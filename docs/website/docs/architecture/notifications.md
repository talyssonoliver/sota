# graph/notifications.py

## Classes
- **NotificationLevel** (line 34)
- **SlackNotifier** (line 44)
  - Methods: __init__, should_notify, format_message, send_notification, node_start_handler, node_end_handler, error_handler, state_change_handler

## Functions
- **attach_notifications_to_workflow(workflow, notifier, notification_level)** (line 285)
