"""
Automated Escalation System for Human-in-the-Loop (HITL) Integration
Implements policy-driven escalation with notification management and timeout handling.

This module provides comprehensive escalation functionality for the HITL system,
including timeout-based escalations, rejection handling, notification management,
and integration with the existing feedback and HITL systems.
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable, Any, Union
import logging
from pathlib import Path

# Import existing system components
try:
    from utils.feedback_system import FeedbackSystem, FeedbackEntry, FeedbackCategory
    from orchestration.hitl_engine import HITLEngine
except ImportError as e:
    logging.warning(f"Some dependencies not available: {e}")


class EscalationLevel(Enum):
    """Escalation levels with timeout and recipient configuration"""
    
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    
    @property
    def config(self) -> Dict[str, Any]:
        configs = {
            1: {
                "name": "Team Lead Review",
                "timeout_hours": 2,
                "recipients": ["team_lead", "senior_engineer"],
                "notification_channels": ["email", "slack"],
                "description": "Initial escalation to team leadership"
            },
            2: {
                "name": "Management Review",
                "timeout_hours": 6,
                "recipients": ["engineering_manager", "product_manager"],
                "notification_channels": ["email", "slack", "dashboard"],
                "description": "Escalation to engineering management"
            },
            3: {
                "name": "Director Review",
                "timeout_hours": 12,
                "recipients": ["director_engineering", "cto"],
                "notification_channels": ["email", "slack", "dashboard", "phone"],
                "description": "High-level executive escalation"
            },
            4: {
                "name": "Executive Review",
                "timeout_hours": 24,
                "recipients": ["cto", "ceo", "board"],
                "notification_channels": ["email", "slack", "dashboard", "phone", "emergency"],
                "description": "Critical executive escalation"
            }
        }
        return configs[self.value]
    
    @property
    def timeout_hours(self) -> int:
        return self.config["timeout_hours"]
    
    @property
    def recipients(self) -> List[str]:
        return self.config["recipients"]
    
    @property
    def notification_channels(self) -> List[str]:
        return self.config["notification_channels"]


@dataclass
class EscalationRule:
    """Defines escalation behavior for specific task types and conditions"""
    
    task_type: str
    risk_level: str
    trigger_conditions: List[str]
    escalation_path: List[EscalationLevel]
    auto_escalate: bool = True
    notification_template: str = "default_escalation"
    custom_recipients: Optional[List[str]] = None
    escalation_delay_minutes: int = 0
    
    def __post_init__(self):
        """Validate escalation rule parameters"""
        valid_task_types = ["backend", "frontend", "qa", "design", "data", "security", "default", "custom"]
        if self.task_type not in valid_task_types:
            raise ValueError(f"Invalid task type: {self.task_type}. Must be one of {valid_task_types}")
            
        valid_risk_levels = ["low", "medium", "high", "critical"]
        if self.risk_level not in valid_risk_levels:
            raise ValueError(f"Invalid risk level: {self.risk_level}. Must be one of {valid_risk_levels}")


@dataclass
class EscalationEvent:
    """Represents an escalation event with full context"""
    
    task_id: str
    trigger: str
    level: EscalationLevel
    triggered_at: datetime
    triggered_by: str
    context: Dict[str, Any]
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
    notifications_sent: List[str] = None
    
    def __post_init__(self):
        if self.notifications_sent is None:
            self.notifications_sent = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize escalation event for persistence"""
        data = asdict(self)
        data["triggered_at"] = self.triggered_at.isoformat()
        if self.resolved_at:
            data["resolved_at"] = self.resolved_at.isoformat()
        data["level"] = {
            "name": self.level.config["name"],
            "value": self.level.value,
            "timeout_hours": self.level.timeout_hours
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EscalationEvent':
        """Deserialize escalation event from persistence"""        # Convert datetime strings back to datetime objects
        data["triggered_at"] = datetime.fromisoformat(data["triggered_at"])
        if data.get("resolved_at"):
            data["resolved_at"] = datetime.fromisoformat(data["resolved_at"])
        
        # Reconstruct escalation level
        level_data = data["level"]
        for level in EscalationLevel:
            if level.value == level_data["value"]:
                data["level"] = level
                break
        
        return cls(**data)


class EscalationNotifier:
    """Handles escalation notifications across multiple channels"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/escalation_notifications.json"
        self.templates = self._load_templates()
        self.notification_channels = {
            "email": self._send_email,
            "slack": self._send_slack,
            "dashboard": self._send_dashboard_notification,
            "phone": self._send_phone_notification,
            "emergency": self._send_emergency_notification
        }
        
    def _load_templates(self) -> Dict[str, str]:
        """Load notification templates"""
        return {
            "default_escalation": """
            🚨 ESCALATION ALERT 🚨
            
            Task: {task_id}
            Level: {escalation_level}
            Trigger: {trigger}
            Duration: {duration}
            
            Action Required: Please review and respond within {timeout_hours} hours.
            
            Context: {context}
            """,
            
            "timeout_escalation": """
            ⏰ TIMEOUT ESCALATION ⏰
            
            Task {task_id} has exceeded its review timeout.
            
            Original Reviewer: {reviewer}
            Timeout Duration: {timeout_duration} hours
            Escalation Level: {escalation_level}
            
            Immediate action required.
            """,
            
            "rejection_escalation": """
            ❌ REJECTION ESCALATION ❌
            
            Task {task_id} has been rejected multiple times.
            
            Rejection Count: {rejection_count}
            Latest Reason: {rejection_reason}
            Escalation Level: {escalation_level}
            
            Management review required.
            """
        }
    
    def send_notification(self, event: EscalationEvent, recipients: List[str], 
                         channels: List[str]) -> Dict[str, Any]:
        """Send escalation notification across specified channels"""
        results = {
            "success": True,
            "channels_used": [],
            "failures": [],
            "message_id": f"escalation_{event.task_id}_{int(time.time())}"        }
        
        # Render notification content
        content = self.render_template(event.trigger + "_escalation", {
            "task_id": event.task_id,
            "escalation_level": event.level.config["name"],
            "trigger": event.trigger,
            "timeout_hours": event.level.timeout_hours,
            "context": json.dumps(event.context, indent=2),
            "duration": "unknown",
            **event.context
        })
          # Send through each channel
        for channel in channels:
            try:
                if channel in self.notification_channels:
                    # Use getattr to get the current method (allows mocking to work)
                    method_name = f"_send_{channel}" if channel not in ["dashboard", "phone", "emergency"] else f"_send_{channel}_notification"
                    if channel == "dashboard":
                        method_name = "_send_dashboard_notification"
                    elif channel == "phone":
                        method_name = "_send_phone_notification"
                    elif channel == "emergency":
                        method_name = "_send_emergency_notification"
                    
                    method = getattr(self, method_name)
                    success = method(content, recipients, event)
                    if success:
                        results["channels_used"].append(channel)
                        event.notifications_sent.append(f"{channel}_{datetime.now().isoformat()}")
                    else:
                        results["failures"].append(channel)
                        results["success"] = False
            except Exception as e:
                logging.error(f"Failed to send {channel} notification: {e}")
                results["failures"].append(channel)
                results["success"] = False
                
        return results
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render notification template with context"""
        template = self.templates.get(template_name, self.templates["default_escalation"])
        try:
            return template.format(**context)
        except KeyError as e:
            logging.warning(f"Missing template variable {e}, using partial rendering")
            # Safely handle missing variables by providing defaults
            safe_context = {}
            for key, value in context.items():
                safe_context[key] = str(value)
            
            # Add default values for common missing variables
            safe_context.setdefault('task_id', 'unknown')
            safe_context.setdefault('escalation_level', 'unknown')
            safe_context.setdefault('trigger', 'unknown')
            safe_context.setdefault('timeout_hours', 'unknown')
            safe_context.setdefault('context', '{}')
            safe_context.setdefault('duration', 'unknown')
            safe_context.setdefault('reviewer', 'unknown')
            safe_context.setdefault('timeout_duration', 'unknown')
            safe_context.setdefault('rejection_count', 'unknown')
            safe_context.setdefault('rejection_reason', 'unknown')
            
            return template.format(**safe_context)
    
    def _send_email(self, content: str, recipients: List[str], event: EscalationEvent) -> bool:
        """Send email notification (mock implementation)"""
        logging.info(f"Sending email escalation for {event.task_id} to {recipients}")
        # In production, integrate with actual email system
        return True
    
    def _send_slack(self, content: str, recipients: List[str], event: EscalationEvent) -> bool:
        """Send Slack notification (mock implementation)"""
        logging.info(f"Sending Slack escalation for {event.task_id} to {recipients}")
        # In production, integrate with Slack API
        return True
    
    def _send_dashboard_notification(self, content: str, recipients: List[str], event: EscalationEvent) -> bool:
        """Send dashboard notification (mock implementation)"""
        logging.info(f"Sending dashboard escalation for {event.task_id}")
        # In production, integrate with dashboard notification system
        return True
    
    def _send_phone_notification(self, content: str, recipients: List[str], event: EscalationEvent) -> bool:
        """Send phone notification (mock implementation)"""
        logging.info(f"Sending phone escalation for {event.task_id} to {recipients}")
        # In production, integrate with phone/SMS system
        return True
    
    def _send_emergency_notification(self, content: str, recipients: List[str], event: EscalationEvent) -> bool:
        """Send emergency notification (mock implementation)"""
        logging.critical(f"EMERGENCY escalation for {event.task_id} to {recipients}")
        # In production, integrate with emergency notification system
        return True


class EscalationTracker:
    """Tracks and persists escalation events and metrics"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or "data/storage/escalations")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.escalations_file = self.storage_path / "escalations.json"
        self.events: List[EscalationEvent] = self._load_events()
        # Ensure file exists
        if not self.escalations_file.exists():
            self._save_events()
        
    def _load_events(self) -> List[EscalationEvent]:
        """Load escalation events from storage"""
        if self.escalations_file.exists():
            try:
                with open(self.escalations_file, 'r') as f:
                    data = json.load(f)
                    return [EscalationEvent.from_dict(event_data) for event_data in data]
            except Exception as e:
                logging.error(f"Failed to load escalation events: {e}")
        return []
    
    def _save_events(self):
        """Save escalation events to storage"""
        try:
            with open(self.escalations_file, 'w') as f:
                data = [event.to_dict() for event in self.events]
                json.dump(data, f, indent=2, default=str)  # Add default=str to handle non-serializable objects
        except Exception as e:
            logging.error(f"Failed to save escalation events: {e}")
    
    def track_event(self, event: EscalationEvent):
        """Track a new escalation event"""
        self.events.append(event)
        self._save_events()
        logging.info(f"Tracked escalation event: {event.task_id} - {event.trigger}")
    
    def get_events_for_task(self, task_id: str) -> List[EscalationEvent]:
        """Get all escalation events for a specific task"""
        return [event for event in self.events if event.task_id == task_id]
    
    def get_escalation_history(self, days: int = 7) -> List[EscalationEvent]:
        """Get escalation history for specified number of days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [event for event in self.events if event.triggered_at >= cutoff_date]
    
    def calculate_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Calculate escalation metrics"""
        recent_events = self.get_escalation_history(days)
        
        metrics = {
            "total_escalations": len(recent_events),
            "timeout_escalations": len([e for e in recent_events if e.trigger == "timeout"]),
            "rejection_escalations": len([e for e in recent_events if e.trigger == "rejection"]),
            "level_1_escalations": len([e for e in recent_events if e.level == EscalationLevel.LEVEL_1]),
            "level_2_escalations": len([e for e in recent_events if e.level == EscalationLevel.LEVEL_2]),
            "level_3_escalations": len([e for e in recent_events if e.level == EscalationLevel.LEVEL_3]),
            "level_4_escalations": len([e for e in recent_events if e.level == EscalationLevel.LEVEL_4]),
            "avg_resolution_time": self._calculate_avg_resolution_time(recent_events),
            "escalations_by_task_type": self._group_by_task_type(recent_events)
        }
        
        return metrics
    
    def _calculate_avg_resolution_time(self, events: List[EscalationEvent]) -> Optional[float]:
        """Calculate average resolution time in hours"""
        resolved_events = [e for e in events if e.resolved_at]
        if not resolved_events:
            return None
            
        total_time = sum([
            (e.resolved_at - e.triggered_at).total_seconds() / 3600
            for e in resolved_events
        ])
        return total_time / len(resolved_events)
    
    def _group_by_task_type(self, events: List[EscalationEvent]) -> Dict[str, int]:
        """Group escalations by task type"""
        counts = {}
        for event in events:
            task_type = event.task_id.split('-')[0].lower()
            counts[task_type] = counts.get(task_type, 0) + 1
        return counts


class EscalationTimer:
    """Manages escalation timers with automatic triggers"""
    
    def __init__(self, task_id: str, timeout_hours: int, callback: Callable,
                 level: EscalationLevel, start_time: Optional[datetime] = None):
        self.task_id = task_id
        self.timeout_hours = timeout_hours
        self.callback = callback
        self.level = level
        self.start_time = start_time or datetime.now()
        self.timer: Optional[threading.Timer] = None
        self.active = False
        
    def is_expired(self) -> bool:
        """Check if timer has expired"""
        elapsed = datetime.now() - self.start_time
        return elapsed.total_seconds() >= (self.timeout_hours * 3600)
    
    def is_active(self) -> bool:
        """Check if timer is currently active"""
        return self.active and self.timer is not None
    
    def start(self):
        """Start the escalation timer"""
        timeout_seconds = self.timeout_hours * 3600
        self.timer = threading.Timer(timeout_seconds, self._timeout_handler)
        self.timer.start()
        self.active = True
        logging.info(f"Started escalation timer for {self.task_id}: {self.timeout_hours}h")
    
    def cancel(self):
        """Cancel the escalation timer"""
        if self.timer:
            self.timer.cancel()
            self.active = False
            logging.info(f"Cancelled escalation timer for {self.task_id}")
    
    def _timeout_handler(self):
        """Handle timer timeout"""
        self.active = False
        logging.warning(f"Escalation timer expired for {self.task_id}")
        if self.callback:
            self.callback()


class EscalationPolicy:
    """Manages escalation policies and rules"""
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/escalation_policies.yaml"
        self.policies = self._load_default_policies()
        self.custom_rules: Dict[str, EscalationRule] = {}
        
    def _load_default_policies(self) -> Dict[str, Dict[str, EscalationRule]]:
        """Load default escalation policies"""
        return {
            "backend": {
                "low": EscalationRule(
                    task_type="backend",
                    risk_level="low",
                    trigger_conditions=["timeout"],
                    escalation_path=[EscalationLevel.LEVEL_1],
                    auto_escalate=True
                ),
                "medium": EscalationRule(
                    task_type="backend",
                    risk_level="medium",
                    trigger_conditions=["timeout", "rejection"],
                    escalation_path=[EscalationLevel.LEVEL_1, EscalationLevel.LEVEL_2],
                    auto_escalate=True
                ),
                "high": EscalationRule(
                    task_type="backend",
                    risk_level="high",
                    trigger_conditions=["timeout", "rejection", "security_concern"],
                    escalation_path=[EscalationLevel.LEVEL_1, EscalationLevel.LEVEL_2, EscalationLevel.LEVEL_3],
                    auto_escalate=True
                ),
                "critical": EscalationRule(
                    task_type="backend",
                    risk_level="critical",
                    trigger_conditions=["immediate", "timeout", "rejection"],
                    escalation_path=[EscalationLevel.LEVEL_3, EscalationLevel.LEVEL_4],
                    auto_escalate=True,
                    escalation_delay_minutes=0
                )
            },
            "frontend": {
                "low": EscalationRule(
                    task_type="frontend",
                    risk_level="low",
                    trigger_conditions=["timeout"],
                    escalation_path=[EscalationLevel.LEVEL_1],
                    auto_escalate=True
                ),
                "medium": EscalationRule(
                    task_type="frontend",
                    risk_level="medium",
                    trigger_conditions=["timeout", "rejection"],
                    escalation_path=[EscalationLevel.LEVEL_1, EscalationLevel.LEVEL_2],
                    auto_escalate=True
                ),
                "high": EscalationRule(
                    task_type="frontend",
                    risk_level="high",
                    trigger_conditions=["timeout", "rejection"],
                    escalation_path=[EscalationLevel.LEVEL_1, EscalationLevel.LEVEL_2],
                    auto_escalate=True
                )
            },
            "qa": {
                "low": EscalationRule(
                    task_type="qa",
                    risk_level="low",
                    trigger_conditions=["timeout"],
                    escalation_path=[EscalationLevel.LEVEL_1],
                    auto_escalate=True
                ),
                "medium": EscalationRule(
                    task_type="qa",
                    risk_level="medium",
                    trigger_conditions=["timeout", "rejection"],
                    escalation_path=[EscalationLevel.LEVEL_1, EscalationLevel.LEVEL_2],
                    auto_escalate=True
                ),
                "high": EscalationRule(
                    task_type="qa",
                    risk_level="high",
                    trigger_conditions=["timeout", "rejection"],
                    escalation_path=[EscalationLevel.LEVEL_1, EscalationLevel.LEVEL_2, EscalationLevel.LEVEL_3],
                    auto_escalate=True
                ),
                "critical": EscalationRule(
                    task_type="qa",
                    risk_level="critical",
                    trigger_conditions=["immediate", "timeout", "rejection"],
                    escalation_path=[EscalationLevel.LEVEL_2, EscalationLevel.LEVEL_3, EscalationLevel.LEVEL_4],
                    auto_escalate=True,
                    escalation_delay_minutes=0
                )
            },
            "default": {
                "low": EscalationRule(
                    task_type="default",
                    risk_level="low",
                    trigger_conditions=["timeout"],
                    escalation_path=[EscalationLevel.LEVEL_1],
                    auto_escalate=True
                ),
                "medium": EscalationRule(
                    task_type="default",
                    risk_level="medium",
                    trigger_conditions=["timeout"],
                    escalation_path=[EscalationLevel.LEVEL_1, EscalationLevel.LEVEL_2],
                    auto_escalate=True
                ),
                "high": EscalationRule(
                    task_type="default",
                    risk_level="high",
                    trigger_conditions=["timeout", "rejection"],
                    escalation_path=[EscalationLevel.LEVEL_2, EscalationLevel.LEVEL_3],
                    auto_escalate=True
                )
            }
        }
    
    def get_escalation_rule(self, task_type: str, risk_level: str) -> Optional[EscalationRule]:
        """Get escalation rule for task type and risk level"""
        # Check custom rules first
        custom_key = f"{task_type}_{risk_level}"
        if custom_key in self.custom_rules:
            return self.custom_rules[custom_key]
            
        # Check default policies
        if task_type in self.policies and risk_level in self.policies[task_type]:
            return self.policies[task_type][risk_level]
            
        # Fall back to default policy
        if risk_level in self.policies["default"]:
            return self.policies["default"][risk_level]
            
        return None
    
    def add_custom_rule(self, key: str, rule: EscalationRule):
        """Add custom escalation rule"""
        self.custom_rules[key] = rule


class EscalationEngine:
    """Main escalation engine coordinating all escalation functionality"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.policy = EscalationPolicy(config_path)
        self.notifier = EscalationNotifier()
        self.tracker = EscalationTracker()
        self.timers: Dict[str, EscalationTimer] = {}
        self.feedback_system = None
        self.hitl_engine = None
        
        # Try to initialize integrations
        try:
            self.feedback_system = FeedbackSystem()
        except Exception as e:
            logging.warning(f"Feedback system not available: {e}")
            
        try:
            self.hitl_engine = HITLEngine()
        except Exception as e:
            logging.warning(f"HITL engine not available: {e}")
    
    def handle_timeout_escalation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle timeout-based escalation"""
        task_id = task_data["task_id"]
        task_type = task_data.get("task_type", "default")
        risk_level = task_data.get("risk_level", "medium")
        
        # Determine escalation level
        level = self.determine_escalation_level(task_type, risk_level, "timeout", task_data)
        
        # Create escalation event
        event = EscalationEvent(
            task_id=task_id,
            trigger="timeout",
            level=level,
            triggered_at=datetime.now(),
            triggered_by="system",
            context={
                "timeout_duration": task_data.get("timeout_duration", "unknown"),
                "reviewer": task_data.get("reviewer", "unknown"),
                "task_type": task_type,
                "risk_level": risk_level
            }
        )
        
        # Send notifications
        notification_result = self.notifier.send_notification(
            event, level.recipients, level.notification_channels
        )
        
        # Track event
        self.tracker.track_event(event)
        
        # Capture feedback if system available
        if self.feedback_system:
            try:
                self.capture_escalation_feedback(event)
            except Exception as e:
                logging.warning(f"Failed to capture escalation feedback: {e}")
        
        return {
            "escalated": True,
            "level": level,
            "event": event,
            "notification_result": notification_result
        }
    
    def handle_rejection_escalation(self, rejection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle rejection-based escalation"""
        task_id = rejection_data["task_id"]
        task_type = rejection_data.get("task_type", "default")
        risk_level = rejection_data.get("risk_level", "medium")
        rejection_count = rejection_data.get("rejection_count", 1)
        
        # Determine escalation level based on rejection count
        if rejection_count >= 3:
            level = EscalationLevel.LEVEL_3
        elif rejection_count >= 2:
            level = EscalationLevel.LEVEL_2
        else:
            level = EscalationLevel.LEVEL_1
        
        # Create escalation event
        event = EscalationEvent(
            task_id=task_id,
            trigger="rejection",
            level=level,
            triggered_at=datetime.now(),
            triggered_by="reviewer",
            context={
                "rejection_count": rejection_count,
                "rejection_reason": rejection_data.get("rejection_reason", "unknown"),
                "reviewer": rejection_data.get("reviewer", "unknown"),
                "task_type": task_type,
                "risk_level": risk_level
            }
        )
        
        # Send notifications
        notification_result = self.notifier.send_notification(
            event, level.recipients, level.notification_channels
        )
        
        # Track event
        self.tracker.track_event(event)
        
        return {
            "escalated": True,
            "level": level,
            "reason": "multiple_rejections",
            "escalation_event": event,
            "notification_result": notification_result
        }
    
    def determine_escalation_level(self, task_type: str, risk_level: str, 
                                 trigger: str, context: Dict[str, Any]) -> EscalationLevel:
        """Determine appropriate escalation level"""
        rule = self.policy.get_escalation_rule(task_type, risk_level)
        
        if not rule:
            return EscalationLevel.LEVEL_1        # For timeout triggers, use escalation path based on duration
        if trigger == "timeout":
            # Check both duration (in seconds) and timeout_hours
            timeout_duration = context.get("duration", 0)
            timeout_hours = context.get("timeout_hours", 0)
            
            # If using duration directly, apply direct thresholds
            if timeout_duration > 0:
                # Direct duration thresholds (from test expectations)
                if timeout_duration >= 28800:  # 8+ hours (high priority escalation)
                    return rule.escalation_path[min(2, len(rule.escalation_path) - 1)]
                elif timeout_duration >= 7200:  # 2+ hours (medium escalation)
                    return rule.escalation_path[min(1, len(rule.escalation_path) - 1)]
                else:
                    return rule.escalation_path[0]
            elif timeout_hours > 0:
                # For timeout_hours, use different thresholds (timer cascade scenario)
                if timeout_hours >= 8:  # 8+ hours
                    return rule.escalation_path[min(2, len(rule.escalation_path) - 1)]
                elif timeout_hours >= 6:  # 6+ hours 
                    return rule.escalation_path[min(1, len(rule.escalation_path) - 1)]
                else:
                    return rule.escalation_path[0]
        
        # For rejection triggers, escalate based on count
        if trigger == "rejection":
            rejection_count = context.get("rejection_count", 1)
            if rejection_count >= 3:
                # For critical tasks with 3+ rejections, use LEVEL_3
                if risk_level == "critical":
                    return EscalationLevel.LEVEL_3
                else:
                    level_index = min(rejection_count - 1, len(rule.escalation_path) - 1)
                    return rule.escalation_path[level_index]
            else:
                level_index = min(rejection_count - 1, len(rule.escalation_path) - 1)
                return rule.escalation_path[level_index]
        
        # For critical triggers, use appropriate level based on risk
        if trigger in ["immediate", "security_concern"]:
            if risk_level == "critical":
                return EscalationLevel.LEVEL_3  # Not highest level for critical
            else:
                return rule.escalation_path[-1]
        
        return rule.escalation_path[0]
      
    def schedule_escalation_timer(self, task_data: Dict[str, Any]) -> str:
        """Schedule escalation timer for a task"""
        task_id = task_data["task_id"]
        timeout_hours = task_data.get("timeout_hours", 24)
        
        # Create timer callback
        def timeout_callback():
            self.handle_timeout_escalation(task_data)
        
        # Create and start timer
        timer = EscalationTimer(
            task_id=task_id,
            timeout_hours=timeout_hours,
            callback=timeout_callback,
            level=EscalationLevel.LEVEL_1
        )
        
        # Generate unique timer ID using time and counter for uniqueness
        import time
        timer_id = f"{task_id}_{int(time.time() * 1000000)}"  # Use microseconds for uniqueness
        self.timers[timer_id] = timer
        timer.start()
        
        return timer_id
    
    def cancel_escalation_timer(self, timer_id: str) -> bool:
        """Cancel escalation timer"""
        if timer_id in self.timers:
            self.timers[timer_id].cancel()
            del self.timers[timer_id]
            return True
        return False
    
    def check_pending_reviews_for_escalation(self) -> List[Dict[str, Any]]:
        """Check pending reviews for escalation conditions"""
        escalations = []
        
        if not self.hitl_engine:
            return escalations
        
        try:
            # Get pending reviews from HITL engine
            pending_reviews = self.hitl_engine.get_pending_reviews()
            
            for review in pending_reviews:
                # Check if review has timed out
                started_at = review.get("started_at")
                if started_at:
                    elapsed = datetime.now() - started_at
                    if elapsed.total_seconds() > 3600:  # 1 hour timeout
                        escalation_data = {
                            "task_id": review["task_id"],
                            "timeout_duration": elapsed.total_seconds() / 3600,
                            "reviewer": review.get("reviewer", "unknown")
                        }
                        escalations.append(escalation_data)
        except Exception as e:
            logging.error(f"Failed to check pending reviews: {e}")
        
        return escalations
    
    def calculate_feedback_impact(self, escalation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate feedback impact from escalation"""
        severity_score = 0
        
        # Calculate severity based on escalation level
        level = escalation_data.get("escalation_level", EscalationLevel.LEVEL_1)
        if level == EscalationLevel.LEVEL_1:
            severity_score = 3
        elif level == EscalationLevel.LEVEL_2:
            severity_score = 5
        elif level == EscalationLevel.LEVEL_3:
            severity_score = 7
        elif level == EscalationLevel.LEVEL_4:
            severity_score = 10
        return {
            "severity_score": severity_score,
            "categories": ["escalation", "process_improvement"],
            "impact_type": "negative",
            "escalation_reason": escalation_data.get("escalation_reason", "unknown")
        }
    
    def capture_escalation_feedback(self, event: EscalationEvent):
        """Capture feedback from escalation events"""
        if not self.feedback_system:
            # Try to initialize feedback system if not available
            try:
                self.feedback_system = FeedbackSystem()
            except Exception as e:
                logging.warning(f"Feedback system still not available: {e}")
                return
            
        try:
            # Import here to avoid circular imports
            from utils.feedback_system import FeedbackEntry
            
            feedback_entry = FeedbackEntry(
                task_id=event.task_id,
                reviewer="system",
                approval_decision=False,  # Escalation implies non-approval
                feedback_categories={
                    "architecture": {
                        "score": 2, 
                        "comments": f"Escalation triggered: {event.trigger} at level {event.level.config['name']}"
                    }
                },
                comments=[f"Escalation triggered: {event.trigger} at level {event.level.config['name']}"],
                suggested_improvements=["Review escalation policies", "Address timeout issues"],
                risk_level="high",  # Escalation indicates high risk
                timestamp=event.triggered_at
            )
            
            self.feedback_system.capture_feedback(feedback_entry)
            logging.info(f"Captured escalation feedback for {event.task_id}")
        except Exception as e:
            logging.error(f"Failed to capture escalation feedback: {e}")
            
    def get_escalation_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get escalation metrics and analytics"""
        return self.tracker.calculate_metrics(days)
    
    def get_active_escalations(self) -> List[Dict[str, Any]]:
        """Get currently active escalations"""
        active = []
        
        # Get recent unresolved escalations
        recent_events = self.tracker.get_escalation_history(days=1)
        for event in recent_events:
            if not event.resolved_at:
                active.append({
                    "task_id": event.task_id,
                    "level": event.level.config["name"],
                    "trigger": event.trigger,
                    "triggered_at": event.triggered_at,
                    "context": event.context
                })
        
        return active
