# Workflow Monitoring and Notification System

This document describes the monitoring, notification, and resilience features for the AI Agent System workflow.

## Overview

The system includes several components for monitoring workflow execution, sending notifications, and ensuring resilience:

1. **Real-time Workflow Monitoring CLI**: Monitor LangGraph workflow executions in real-time
2. **Slack Notification System**: Send notifications about node execution events
3. **Resilient Workflow Components**: Add retry and timeout capabilities to workflow nodes

## Real-time Monitoring CLI

The Workflow Monitoring CLI provides a real-time view of LangGraph workflow execution progress, making it easy to track the status of agent tasks as they execute.

### Features

- Interactive terminal UI with color-coding for different status types
- Live event log with real-time updates
- File watching to detect changes in output directory
- Support for monitoring specific tasks or all tasks
- Option for simple console mode (non-terminal UI)

### Usage

```bash
# Monitor all tasks with interactive UI
python scripts/monitor_workflow.py

# Monitor a specific task
python scripts/monitor_workflow.py --task BE-07

# Use custom output directory
python scripts/monitor_workflow.py --output custom/output/dir

# Use simple output mode (no curses UI)
python scripts/monitor_workflow.py --simple
```

### UI Components

The interactive UI includes:
- Task status display showing all tasks and their current status
- Agent status display showing all nodes and their execution status
- Event log showing real-time events and status changes
- Runtime display showing how long monitoring has been active

### Controls

- **q**: Quit the monitoring interface
- **r**: Force refresh data from the file system

## Slack Notification System

The Slack notification system integrates with your workflow to provide real-time notifications about important events.

### Features

- Configurable notification levels (all events, errors only, state changes, completion events)
- Formatted Slack messages with task details and status information
- Color-coded notifications based on event type and status
- Fallback to local logging when Slack webhook is unavailable

### Configuration

To enable Slack notifications, set the `SLACK_WEBHOOK_URL` environment variable with your Slack webhook URL.

```bash
# On Windows
set SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url

# On Linux/macOS
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
```

### Integrating with Workflows

```python
from graph.notifications import SlackNotifier, attach_notifications_to_workflow, NotificationLevel

# Create a workflow
workflow = build_workflow_graph()

# Add notifications with default settings (all notifications)
workflow_with_notifications = attach_notifications_to_workflow(workflow)

# Or customize notification level
notifier = SlackNotifier(notification_level=NotificationLevel.ERROR)
workflow_with_notifications = attach_notifications_to_workflow(workflow, notifier)
```

### Notification Levels

- `NotificationLevel.ALL`: Send all notifications
- `NotificationLevel.ERROR`: Send only error notifications
- `NotificationLevel.STATE_CHANGE`: Send only state change notifications
- `NotificationLevel.COMPLETION`: Send only task completion notifications
- `NotificationLevel.NONE`: Do not send notifications (only log locally)

## Resilient Workflow Components

The resilient workflow components add retry logic and timeout handling to ensure robustness in your agent workflows.

### Features

- Retry decorator for automatic retry of failed operations
- Timeout decorator to prevent indefinite hanging on long operations
- Error handling with automatic status updates
- In-memory tracking of retry attempts
- Integration with task state management

### Usage

```python
from graph.resilient_workflow import with_retry, with_timeout, create_resilient_workflow
from graph.graph_builder import build_workflow_graph

# Create a resilient version of an existing workflow
resilient_workflow = create_resilient_workflow(
    build_workflow_graph,
    config={
        "max_retries": 3,
        "retry_delay": 5,
        "timeout_seconds": 300
    }
)

# Or apply decorators directly to handlers
@with_retry(max_retries=3, retry_delay=5)
@with_timeout(timeout_seconds=300)
def agent_handler(state):
    # Your handler logic here
    return state
```

### Configuration Options

- `max_retries`: Maximum number of retry attempts (default: 3)
- `retry_delay`: Time to wait between retries in seconds (default: 5)
- `timeout_seconds`: Maximum execution time in seconds (default: 300)

## Integration Example

Here's how to use all components together for a fully monitored, resilient workflow:

```python
from graph.graph_builder import build_workflow_graph
from graph.resilient_workflow import create_resilient_workflow
from graph.notifications import attach_notifications_to_workflow, NotificationLevel

# 1. Create base workflow
base_workflow = build_workflow_graph()

# 2. Add resilience features
resilient_workflow = create_resilient_workflow(
    lambda: base_workflow,
    config={
        "max_retries": 3,
        "timeout_seconds": 300
    }
)

# 3. Add notifications
monitored_workflow = attach_notifications_to_workflow(
    resilient_workflow,
    notification_level=NotificationLevel.STATE_CHANGE
)

# 4. Run the workflow
result = monitored_workflow.invoke({
    "task_id": "BE-07",
    "status": "CREATED"
})

# 5. Monitor the execution in real-time using the CLI
# In separate terminal: python scripts/monitor_workflow.py --task BE-07
```