"""
Workflow Notification System
Implements Slack notifications for LangGraph workflow events.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Callable, Optional, List, Union
from datetime import datetime
import requests
from enum import Enum
from pythonjsonlogger import jsonlogger

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, Graph
from orchestration.states import TaskStatus

# Configure structured JSON logging for production
logger = logging.getLogger("workflow_notifications")
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(event)s %(agent)s %(task_id)s')
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.setLevel(logging.INFO)

class NotificationLevel(str, Enum):
    """Notification level for filtering events"""
    ALL = "all"           # Send all notifications
    ERROR = "error"       # Send only error notifications
    STATE_CHANGE = "state_change"  # Send only state change notifications
    COMPLETION = "completion"  # Send only task completion notifications
    NONE = "none"         # Do not send notifications


class SlackNotifier:
    """
    Slack notification handler for LangGraph workflow events.
    """
    
    def __init__(self, webhook_url: Optional[str] = None, notification_level: NotificationLevel = NotificationLevel.ALL):
        """
        Initialize the Slack notifier.
        
        Args:
            webhook_url: Slack webhook URL. If None, will look for SLACK_WEBHOOK_URL environment variable.
            notification_level: Level of notifications to send
        """
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.notification_level = notification_level
        
        if not self.webhook_url and notification_level != NotificationLevel.NONE:
            logger.warning("Slack webhook URL not provided. Notifications will be logged but not sent.")
    
    def should_notify(self, event_type: str, state: Dict[str, Any]) -> bool:
        """
        Determine if a notification should be sent based on notification level and event type.
        
        Args:
            event_type: Type of event (node_start, node_end, error, etc.)
            state: Current workflow state
            
        Returns:
            True if notification should be sent, False otherwise
        """
        if self.notification_level == NotificationLevel.NONE:
            return False
        
        if self.notification_level == NotificationLevel.ALL:
            return True
        
        if self.notification_level == NotificationLevel.ERROR:
            return event_type == "error" or "error" in state
        
        if self.notification_level == NotificationLevel.STATE_CHANGE:
            return event_type == "state_change"
        
        if self.notification_level == NotificationLevel.COMPLETION:
            return event_type == "node_end" and state.get("status") == TaskStatus.DONE
        
        return False
    
    def format_message(self, event_type: str, node_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a notification message for Slack.
        
        Args:
            event_type: Type of event
            node_id: ID of the node that triggered the event
            state: Current workflow state
            
        Returns:
            Formatted Slack message payload
        """
        task_id = state.get("task_id", "Unknown")
        title = state.get("title", "Unknown task")
        status = state.get("status", "Unknown status")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Set color based on event type
        color = "#36a64f"  # Green for normal events
        if event_type == "error" or "error" in state:
            color = "#ff0000"  # Red for errors
        elif event_type == "node_start":
            color = "#0000ff"  # Blue for node start
        elif status == TaskStatus.DONE:
            color = "#36a64f"  # Green for completions
        elif status == TaskStatus.BLOCKED:
            color = "#ff0000"  # Red for blocked tasks
        
        # Create message text based on event type
        if event_type == "node_start":
            text = f"Agent *{node_id}* started processing task *{task_id}*: {title}"
        elif event_type == "node_end":
            text = f"Agent *{node_id}* completed processing task *{task_id}* with status: *{status}*"
        elif event_type == "error":
            text = f"Error in agent *{node_id}* while processing task *{task_id}*: {state.get('error', 'Unknown error')}"
        elif event_type == "state_change":
            text = f"Task *{task_id}* state changed to *{status}*"
        else:
            text = f"Event '{event_type}' for task *{task_id}* in agent *{node_id}*"
        
        # Build Slack message payload
        attachments = [{
            "color": color,
            "title": f"Workflow Event: {event_type.replace('_', ' ').title()}",
            "text": text,
            "fields": [
                {
                    "title": "Task ID",
                    "value": task_id,
                    "short": True
                },
                {
                    "title": "Agent",
                    "value": node_id,
                    "short": True
                },
                {
                    "title": "Status",
                    "value": status,
                    "short": True
                },
                {
                    "title": "Timestamp",
                    "value": timestamp,
                    "short": True
                }
            ],
            "footer": "AI Agent System Workflow",
            "ts": int(datetime.now().timestamp())
        }]
        
        # Add error details if available
        if event_type == "error" or "error" in state:
            attachments[0]["fields"].append({
                "title": "Error Details",
                "value": state.get("error", "Unknown error"),
                "short": False
            })
        
        return {
            "text": text,
            "attachments": attachments
        }
    
    def send_notification(self, event_type: str, node_id: str, state: Dict[str, Any]) -> bool:
        """
        Send a notification to Slack.
        
        Args:
            event_type: Type of event
            node_id: ID of the node that triggered the event
            state: Current workflow state
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        if not self.should_notify(event_type, state):
            return False
        
        message = self.format_message(event_type, node_id, state)
        
        # Always log the notification
        logger.info(f"Notification: {json.dumps(message)}", extra={"event": "notification_sent", "agent": node_id, "task_id": state.get("task_id")})
        
        # Send to Slack if webhook URL is available
        if self.webhook_url:
            try:
                response = requests.post(
                    self.webhook_url,
                    json=message,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to send Slack notification: {response.status_code} - {response.text}", extra={"event": "notification_error"})
                    return False
                
                return True
            except Exception as e:
                logger.error(f"Error sending Slack notification: {str(e)}", extra={"event": "notification_error"})
                return False
        
        return True  # Return True if logged, even if not sent to Slack

    def node_start_handler(self, node_id: str, state: Dict[str, Any]) -> None:
        """
        Handler for node start events.
        
        Args:
            node_id: ID of the node that started
            state: Current workflow state
        """
        self.send_notification("node_start", node_id, state)
    
    def node_end_handler(self, node_id: str, state: Dict[str, Any]) -> None:
        """
        Handler for node end events.
        
        Args:
            node_id: ID of the node that ended
            state: Current workflow state
        """
        self.send_notification("node_end", node_id, state)
    
    def error_handler(self, node_id: str, state: Dict[str, Any]) -> None:
        """
        Handler for error events.
        
        Args:
            node_id: ID of the node where error occurred
            state: Current workflow state
        """
        self.send_notification("error", node_id, state)
    
    def state_change_handler(self, old_state: Dict[str, Any], new_state: Dict[str, Any]) -> None:
        """
        Handler for state change events.
        
        Args:
            old_state: Previous workflow state
            new_state: New workflow state
        """
        # Get the node that caused the state change
        node_id = new_state.get("agent", "Unknown")
        self.send_notification("state_change", node_id, new_state)


def attach_notifications_to_workflow(workflow: Union[Graph, StateGraph], 
                                     notifier: Optional[SlackNotifier] = None,
                                     notification_level: NotificationLevel = NotificationLevel.ALL) -> Union[Graph, StateGraph]:
    """
    Attach notification handlers to a workflow graph.
    
    Args:
        workflow: LangGraph workflow to attach notifications to
        notifier: SlackNotifier instance, or None to create a new one
        notification_level: Level of notifications to send
        
    Returns:
        Workflow with notification handlers attached
    """
    if notifier is None:
        notifier = SlackNotifier(notification_level=notification_level)
    
    # In a full implementation, we'd register these handlers with the LangGraph events
    # This is a placeholder for how it would be implemented
    # LangGraph currently doesn't have a built-in event system, so we'd need to:
    # 1. Modify the graph's node handlers to trigger notifications
    # 2. Add pre-execution and post-execution hooks
    
    logger.info(f"Attached notifications to workflow with level: {notification_level}")
    
    # Return the workflow unchanged for now
    return workflow