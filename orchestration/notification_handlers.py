"""
Notification Handlers for HITL Engine

This module provides various notification handlers for sending alerts
and updates about Human-in-the-Loop checkpoints.
"""

import json
import logging
import smtplib
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class NotificationHandler(ABC):
    """Abstract base class for notification handlers"""
    
    @abstractmethod
    def send_notification(self, checkpoint, notification_type: str, recipients=None, metadata=None):
        """Send notification for checkpoint event"""
        pass


class DashboardNotificationHandler(NotificationHandler):
    """Handler for dashboard notifications"""
    def __init__(self, config=None):
        from config.build_paths import DASHBOARD_NOTIFICATIONS_DIR
        self.storage_dir = DASHBOARD_NOTIFICATIONS_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def send_notification(self, checkpoint, notification_type: str, recipients=None, metadata=None):
        """Send dashboard notification"""        
        notification = {
            'id': f"notif_{checkpoint.id}_{notification_type}",
            'type': notification_type,
            'checkpoint_id': checkpoint.id,
            'task_id': checkpoint.task_id,
            'title': self._get_notification_title(checkpoint, notification_type),
            'message': self._get_notification_message(checkpoint, notification_type),
            'severity': self._get_notification_severity(checkpoint, notification_type),
            'timestamp': datetime.now().isoformat(),
            'read': False,
            'action_url': f"/hitl/checkpoint/{checkpoint.id}",
            'metadata': {
                'checkpoint_type': getattr(checkpoint.checkpoint_type, 'value', checkpoint.checkpoint_type),
                'risk_level': getattr(checkpoint.risk_level, 'value', checkpoint.risk_level),
                'assigned_reviewers': checkpoint.assigned_reviewers,
                'deadline': checkpoint.timeout_at.isoformat() if checkpoint.timeout_at else None
            }
        }# Save notification to dashboard storage
        notification_file = self.storage_dir / f"{notification['id']}.json"
        with open(notification_file, 'w', encoding='utf-8') as f:
            json.dump(notification, f, indent=2, ensure_ascii=False)
        
        # Update dashboard data
        dashboard_url = metadata.get('url') if metadata else None
        self._update_dashboard_data(notification, dashboard_url)
        
        logger.info(f"Dashboard notification sent: {notification['title']}")
        return True
    
    def _get_notification_title(self, checkpoint, notification_type: str) -> str:
        """Get notification title based on type"""
        titles = {
            'checkpoint_created': f"🔍 Review Required: {checkpoint.task_id}",
            'escalation_alert': f"⚠️ Escalated Review: {checkpoint.task_id}",
            'approval_granted': f"✅ Approved: {checkpoint.task_id}",
            'approval_rejected': f"❌ Rejected: {checkpoint.task_id}",
            'timeout_warning': f"⏰ Review Timeout Warning: {checkpoint.task_id}"
        }
        return titles.get(notification_type, f"HITL Update: {checkpoint.task_id}")
    
    def _get_notification_message(self, checkpoint, notification_type: str) -> str:
        """Get notification message based on type"""        
        messages = {
            'checkpoint_created': f"A {getattr(checkpoint.checkpoint_type, 'value', checkpoint.checkpoint_type)} checkpoint requires your review. Risk level: {getattr(checkpoint.risk_level, 'value', checkpoint.risk_level)}",
            'escalation_alert': f"Checkpoint has been escalated (Level {checkpoint.escalation_level}). Immediate attention required.",
            'approval_granted': f"Checkpoint has been approved. Task can proceed.",
            'approval_rejected': f"Checkpoint has been rejected. Task requires rework.",
            'timeout_warning': f"Checkpoint is approaching deadline: {checkpoint.timeout_at.strftime('%Y-%m-%d %H:%M')}" if checkpoint.timeout_at else "Checkpoint is approaching deadline."
        }
        return messages.get(notification_type, "HITL checkpoint update")
    
    def _get_notification_severity(self, checkpoint, notification_type: str) -> str:
        """Get notification severity"""
        if notification_type in ['escalation_alert', 'approval_rejected']:
            return 'error'
        elif notification_type in ['checkpoint_created', 'timeout_warning']:
            return 'warning'
        elif notification_type == 'approval_granted':
            return 'success'
        else:
            return 'info'
      
    def _update_dashboard_data(self, notification: Dict[str, Any], dashboard_url: str = None):
        """Update dashboard data with new notification"""
        # If dashboard URL is provided, send HTTP POST request
        if dashboard_url:
            try:
                response = requests.post(
                    f"{dashboard_url}/api/notifications",
                    json=notification,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                if response.status_code == 200:
                    logger.info(f"Successfully sent notification to dashboard: {dashboard_url}")
                else:
                    logger.warning(f"Dashboard API returned status {response.status_code}")
            except Exception as e:
                logger.error(f"Failed to send notification to dashboard API: {e}")
                # Fall back to local storage
                self._save_to_local_storage(notification)
        else:
            # Save to local storage
            self._save_to_local_storage(notification)
    
    def _save_to_local_storage(self, notification: Dict[str, Any]):
        """Save notification to local dashboard storage"""
        dashboard_data_file = Path("dashboard/hitl_data.json")
        
        # Load existing data
        if dashboard_data_file.exists():
            with open(dashboard_data_file, 'r', encoding='utf-8') as f:
                dashboard_data = json.load(f)
        else:
            dashboard_data = {
                'notifications': [],
                'pending_count': 0,
                'overdue_count': 0,
                'last_updated': None
            }
        
        # Add new notification
        dashboard_data['notifications'].insert(0, notification)
        
        # Keep only last 100 notifications
        dashboard_data['notifications'] = dashboard_data['notifications'][:100]
        
        # Update counts
        if notification['type'] == 'checkpoint_created':
            dashboard_data['pending_count'] += 1
        elif notification['type'] in ['approval_granted', 'approval_rejected']:
            dashboard_data['pending_count'] = max(0, dashboard_data['pending_count'] - 1)
        
        dashboard_data['last_updated'] = datetime.now().isoformat()
        
        # Save updated data
        with open(dashboard_data_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)


class EmailNotificationHandler(NotificationHandler):
    """Handler for email notifications"""
    def __init__(self, config=None):
        if config:
            self.smtp_server = config.get('smtp_server', os.getenv('SMTP_SERVER', 'localhost'))
            self.smtp_port = int(config.get('smtp_port', os.getenv('SMTP_PORT', '587')))
            self.smtp_username = config.get('smtp_username', os.getenv('SMTP_USERNAME', ''))
            self.smtp_password = config.get('smtp_password', os.getenv('SMTP_PASSWORD', ''))
            self.from_address = config.get('from_address', os.getenv('HITL_FROM_EMAIL', 'hitl-system@company.com'))
            self.use_tls = config.get('use_tls', os.getenv('SMTP_USE_TLS', 'true').lower() == 'true')
        else:
            self.smtp_server = os.getenv('SMTP_SERVER', 'localhost')
            self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
            self.smtp_username = os.getenv('SMTP_USERNAME', '')
            self.smtp_password = os.getenv('SMTP_PASSWORD', '')
            self.from_address = os.getenv('HITL_FROM_EMAIL', 'hitl-system@company.com')
            self.use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        
        # Load email templates
        self.templates = self._load_email_templates()
    
    def _load_email_templates(self) -> Dict[str, Dict[str, str]]:
        """Load email templates from configuration"""
        # In a real implementation, these would come from the HITL policies file
        return {
            'checkpoint_created': {
                'subject': '🔍 HITL Review Required: {task_id} - {checkpoint_type}',
                'body': '''
A Human-in-the-Loop checkpoint has been created for your review:

**Task:** {task_id} - {task_title}
**Checkpoint Type:** {checkpoint_type}
**Risk Level:** {risk_level}
**Reason:** {trigger_reason}
**Deadline:** {deadline}

**Review Items:**
{review_items}

**Action Required:**
Please review and approve/reject this checkpoint at: {review_url}

**Timeout Action:** {timeout_action}

Best regards,
HITL System
                '''
            },
            'escalation_alert': {
                'subject': '⚠️ HITL Escalation: {task_id} - Requires Immediate Attention',
                'body': '''
A Human-in-the-Loop checkpoint has been escalated:

**Task:** {task_id} - {task_title}
**Escalation Level:** {escalation_level}
**Original Deadline:** {original_deadline}
**Time Overdue:** {overdue_duration}

**Previous Reviewers:** {previous_reviewers}
**Review History:** {review_history}

**Immediate Action Required:** {review_url}

Best regards,
HITL System
                '''
            },
            'approval_granted': {
                'subject': '✅ HITL Approved: {task_id} - {checkpoint_type}',
                'body': '''
Checkpoint approved by {approver_name}:

**Task:** {task_id} - {task_title}
**Approved At:** {approval_timestamp}
**Comments:** {approval_comments}

**Next Steps:** {next_steps}

Best regards,
HITL System
                '''
            },
            'approval_rejected': {
                'subject': '❌ HITL Rejected: {task_id} - {checkpoint_type}',
                'body': '''
Checkpoint rejected by {reviewer_name}:

**Task:** {task_id} - {task_title}
**Rejected At:** {rejection_timestamp}
**Reason:** {rejection_reason}
**Comments:** {rejection_comments}

**Required Actions:** {required_actions}

Best regards,
HITL System
                '''
            }
        }
    
    def send_notification(self, checkpoint, notification_type: str, recipients=None, metadata=None):
        """Send email notification"""
        if not self._is_email_configured():
            logger.warning("Email not configured, skipping email notification")
            return False
        
        template = self.templates.get(notification_type)
        if not template:
            logger.warning(f"No email template found for notification type: {notification_type}")
            return False
        
        # Get email recipients - use provided recipients or get from checkpoint
        if recipients is None:
            recipients = self._get_email_recipients(checkpoint, notification_type)
        if not recipients:
            logger.warning(f"No email recipients found for checkpoint {checkpoint.id}")
            return False
        
        # Prepare email data
        email_data = self._prepare_email_data(checkpoint, notification_type)
        
        # Format email content
        subject = template['subject'].format(**email_data)
        body = template['body'].format(**email_data)
          # Send email
        try:
            self._send_email(recipients, subject, body)
            logger.info(f"Email notification sent to {recipients} for checkpoint {checkpoint.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _is_email_configured(self) -> bool:
        """Check if email is properly configured"""
        return bool(self.smtp_server and self.from_address)
    
    def _get_email_recipients(self, checkpoint, notification_type: str) -> List[str]:
        """Get email recipients for notification"""
        # In a real implementation, this would map reviewers to email addresses
        # For now, we'll use environment variables or default addresses
        recipients = []
        
        for reviewer in checkpoint.assigned_reviewers:
            # Map reviewer role to email address
            email_mapping = {
                'Technical Lead': os.getenv('TECH_LEAD_EMAIL', 'tech-lead@company.com'),
                'Backend Engineer': os.getenv('BACKEND_EMAIL', 'backend@company.com'),
                'Frontend Engineer': os.getenv('FRONTEND_EMAIL', 'frontend@company.com'),
                'QA Engineer': os.getenv('QA_EMAIL', 'qa@company.com'),
                'Security Lead': os.getenv('SECURITY_EMAIL', 'security@company.com'),
                'Product Manager': os.getenv('PM_EMAIL', 'pm@company.com')
            }
            
            email = email_mapping.get(reviewer)
            if email:
                recipients.append(email)
        
        return recipients
    
    def _prepare_email_data(self, checkpoint, notification_type: str) -> Dict[str, str]:
        """Prepare data for email template"""        
        return {
            'task_id': checkpoint.task_id,
            'task_title': checkpoint.metadata.get('task_data', {}).get('title', 'N/A'),
            'checkpoint_type': getattr(checkpoint.checkpoint_type, 'value', checkpoint.checkpoint_type).replace('_', ' ').title(),
            'risk_level': getattr(checkpoint.risk_level, 'value', checkpoint.risk_level).title(),
            'trigger_reason': ', '.join(checkpoint.risk_factors) if checkpoint.risk_factors else 'N/A',
            'deadline': checkpoint.timeout_at.strftime('%Y-%m-%d %H:%M UTC') if checkpoint.timeout_at else 'N/A',
            'review_items': self._format_review_items(checkpoint.mitigation_suggestions or ['Review required']),
            'review_url': f"http://localhost:8000/hitl/checkpoint/{checkpoint.id}",
            'timeout_action': 'Escalate',  # Default timeout action
            'escalation_level': str(checkpoint.escalation_level),
            'original_deadline': checkpoint.timeout_at.strftime('%Y-%m-%d %H:%M UTC') if checkpoint.timeout_at else 'N/A',
            'overdue_duration': self._calculate_overdue_duration(checkpoint),
            'previous_reviewers': ', '.join(checkpoint.assigned_reviewers) if checkpoint.assigned_reviewers else 'N/A',
            'review_history': self._format_review_history(checkpoint),
            'approver_name': checkpoint.approvals[-1]['reviewer'] if checkpoint.approvals else 'N/A',
            'approval_timestamp': checkpoint.approvals[-1]['timestamp'] if checkpoint.approvals else 'N/A',
            'approval_comments': checkpoint.approvals[-1]['comments'] if checkpoint.approvals else 'N/A',
            'reviewer_name': checkpoint.rejections[-1]['reviewer'] if checkpoint.rejections else 'N/A',
            'rejection_timestamp': checkpoint.rejections[-1]['timestamp'] if checkpoint.rejections else 'N/A',
            'rejection_reason': checkpoint.rejections[-1]['reason'] if checkpoint.rejections else 'N/A',
            'rejection_comments': checkpoint.rejections[-1]['comments'] if checkpoint.rejections else 'N/A',
            'next_steps': 'Task can proceed with execution',
            'required_actions': 'Please address the rejection feedback and resubmit'
        }
    
    def _format_review_items(self, review_items: list) -> str:
        """Format review items for email"""
        if not review_items:
            return "No specific review items"
        
        formatted = []
        for item in review_items:
            # Handle both dict items and string items
            if isinstance(item, dict):
                if item.get('requires_review', False):
                    severity = item.get('severity', 'medium').upper()
                    formatted.append(f"• [{severity}] {item['description']}")
            else:
                # Handle simple string items (e.g., mitigation_suggestions)
                formatted.append(f"• {item}")
        
        return '\n'.join(formatted) if formatted else "No specific review items"
    
    def _calculate_overdue_duration(self, checkpoint) -> str:
        """Calculate how long checkpoint has been overdue"""
        if not checkpoint.is_overdue:
            return "Not overdue"
        
        overdue_delta = datetime.now() - checkpoint.timeout_at
        hours = int(overdue_delta.total_seconds() / 3600)
        
        if hours < 24:
            return f"{hours} hours"
        else:
            days = hours // 24
            remaining_hours = hours % 24
            return f"{days} days, {remaining_hours} hours"
    
    def _format_review_history(self, checkpoint) -> str:
        """Format review history for email"""
        history = []
        
        for approval in checkpoint.approvals:
            history.append(f"✅ {approval['reviewer']} approved at {approval['timestamp']}")
        
        for rejection in checkpoint.rejections:
            history.append(f"❌ {rejection['reviewer']} rejected at {rejection['timestamp']}: {rejection['reason']}")
        
        return '\n'.join(history) if history else "No review history"
    
    def _send_email(self, recipients: list, subject: str, body: str):
        """Send email using SMTP"""
        msg = MIMEMultipart()
        msg['From'] = self.from_address
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            server.send_message(msg)


class SlackNotificationHandler(NotificationHandler):
    """Handler for Slack notifications"""   
    def __init__(self, config=None):
        if config:
            self.webhook_url = config.get('webhook_url', os.getenv('SLACK_WEBHOOK_URL'))
        else:
            self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        self.enabled = bool(self.webhook_url)
        
        # Channel mapping based on risk level
        self.channel_mapping = {
            'critical': os.getenv('SLACK_CRITICAL_CHANNEL', '#critical-reviews'),
            'high': os.getenv('SLACK_HIGH_RISK_CHANNEL', '#engineering-reviews'),
            'medium': os.getenv('SLACK_MEDIUM_RISK_CHANNEL', '#engineering-reviews'),            
            'low': os.getenv('SLACK_LOW_RISK_CHANNEL', '#general-reviews')
        }
    
    def send_notification(self, checkpoint, notification_type: str, recipients=None, metadata=None):
        """Send Slack notification"""
        if not self.enabled:
            logger.warning("Slack not configured, skipping Slack notification")
            return False
        
        # Prepare Slack message
        message = self._prepare_slack_message(checkpoint, notification_type)
        
        # Send to Slack
        try:
            response = requests.post(self.webhook_url, json=message, timeout=10)
            response.raise_for_status()
            logger.info(f"Slack notification sent for checkpoint {checkpoint.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def _prepare_slack_message(self, checkpoint, notification_type: str) -> Dict[str, Any]:
        """Prepare Slack message payload"""
        color_mapping = {
            'checkpoint_created': '#ffaa00',  # Orange
            'escalation_alert': '#ff0000',    # Red
            'approval_granted': '#00ff00',    # Green
            'approval_rejected': '#ff0000',   # Red
            'timeout_warning': '#ffaa00'      # Orange
        }
        
        icon_mapping = {
            'checkpoint_created': '🔍',
            'escalation_alert': '⚠️',
            'approval_granted': '✅',
            'approval_rejected': '❌',
            'timeout_warning': '⏰'
        }
        
        # Get appropriate channel
        channel = self.channel_mapping.get(checkpoint.risk_level.value, '#general-reviews')
        
        # Create message blocks
        blocks = []
        
        # Header block
        header_text = f"{icon_mapping.get(notification_type, '📋')} *HITL {notification_type.replace('_', ' ').title()}*"
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": header_text
            }
        })
        
        # Main info block
        fields = [
            {
                "type": "mrkdwn",
                "text": f"*Task:* {checkpoint.task_id}"
            },            {
                "type": "mrkdwn",
                "text": f"*Type:* {getattr(checkpoint.checkpoint_type, 'value', checkpoint.checkpoint_type).replace('_', ' ').title()}"
            },
            {
                "type": "mrkdwn",
                "text": f"*Risk Level:* {getattr(checkpoint.risk_level, 'value', checkpoint.risk_level).title()}"
            },
            {
                "type": "mrkdwn",
                "text": f"*Deadline:* {checkpoint.deadline.strftime('%Y-%m-%d %H:%M')}"
            }
        ]
        
        if checkpoint.assigned_reviewers:
            fields.append({
                "type": "mrkdwn",
                "text": f"*Reviewers:* {', '.join(checkpoint.assigned_reviewers)}"
            })
        
        blocks.append({
            "type": "section",
            "fields": fields
        })
        
        # Action buttons (if applicable)
        if notification_type == 'checkpoint_created':
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Review Checkpoint"
                        },
                        "url": f"http://localhost:8000/hitl/checkpoint/{checkpoint.id}",
                        "style": "primary"
                    }
                ]
            })
        
        return {
            "channel": channel,
            "blocks": blocks,
            "attachments": [{
                "color": color_mapping.get(notification_type, '#cccccc'),
                "fallback": f"HITL {notification_type} for {checkpoint.task_id}"
            }]
        }


# Export notification handlers
__all__ = [
    'NotificationHandler',
    'DashboardNotificationHandler', 
    'EmailNotificationHandler',
    'SlackNotificationHandler'
]
