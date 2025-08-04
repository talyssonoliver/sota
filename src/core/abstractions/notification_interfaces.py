
from src.infrastructure.utils.common_imports import Enum, dataclass
"""
Notification Service Interfaces

Abstract interfaces for notification services, breaking
dependency on specific email or messaging implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
# from dataclasses import dataclass  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports


class NotificationType(Enum):
    """Types of notifications"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    RETRY = "retry"


@dataclass
class NotificationRecipient:
    """Notification recipient information"""
    address: str  # Email, phone, webhook URL, etc.
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class NotificationTemplate:
    """Notification template"""
    id: str
    name: str
    subject: Optional[str] = None
    content: str
    content_type: str = "text/plain"  # text/plain, text/html, markdown
    variables: Optional[List[str]] = None


@dataclass
class NotificationMessage:
    """Notification message specification"""
    id: Optional[str] = None
    notification_type: NotificationType = NotificationType.EMAIL
    recipients: List[NotificationRecipient] = None
    subject: Optional[str] = None
    content: str = ""
    content_type: str = "text/plain"
    priority: NotificationPriority = NotificationPriority.NORMAL
    metadata: Optional[Dict[str, Any]] = None
    template_id: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None
    schedule_time: Optional[str] = None  # ISO format
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.recipients is None:
            self.recipients = []


@dataclass
class NotificationResult:
    """Notification delivery result"""
    message_id: str
    status: NotificationStatus
    recipient: NotificationRecipient
    sent_at: Optional[str] = None
    delivered_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0


class INotificationService(ABC):
    """High-level interface for notification services"""
    
    @abstractmethod
    async def send_notification(self, message: NotificationMessage) -> List[NotificationResult]:
        """Send notification message"""
        pass
    
    @abstractmethod
    async def send_bulk_notifications(self, messages: List[NotificationMessage]) -> List[NotificationResult]:
        """Send multiple notification messages"""
        pass
    
    @abstractmethod
    async def schedule_notification(self, message: NotificationMessage, send_at: str) -> str:
        """Schedule notification for future delivery"""
        pass
    
    @abstractmethod
    async def cancel_scheduled_notification(self, message_id: str) -> bool:
        """Cancel scheduled notification"""
        pass
    
    @abstractmethod
    async def get_notification_status(self, message_id: str) -> Optional[NotificationResult]:
        """Get notification delivery status"""
        pass
    
    @abstractmethod
    async def retry_failed_notification(self, message_id: str) -> NotificationResult:
        """Retry failed notification"""
        pass
    
    @abstractmethod
    async def get_delivery_history(self, recipient: str, limit: int = 100) -> List[NotificationResult]:
        """Get delivery history for recipient"""
        pass
    
    @abstractmethod
    async def register_template(self, template: NotificationTemplate) -> bool:
        """Register notification template"""
        pass
    
    @abstractmethod
    async def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Get notification template"""
        pass
    
    @abstractmethod
    async def render_template(self, template_id: str, variables: Dict[str, Any]) -> str:
        """Render template with variables"""
        pass
    
    @abstractmethod
    async def validate_recipient(self, recipient: NotificationRecipient, notification_type: NotificationType) -> bool:
        """Validate recipient for notification type"""
        pass
    
    @abstractmethod
    async def get_supported_types(self) -> List[NotificationType]:
        """Get supported notification types"""
        pass
    
    @abstractmethod
    async def get_service_health(self) -> Dict[str, Any]:
        """Get notification service health status"""
        pass


class IEmailService(ABC):
    """Interface for email-specific functionality"""
    
    @abstractmethod
    async def send_email(self, to: List[str], subject: str, body: str, 
                        cc: Optional[List[str]] = None, bcc: Optional[List[str]] = None,
                        attachments: Optional[List[Dict[str, Any]]] = None) -> NotificationResult:
        """Send email message"""
        pass
    
    @abstractmethod
    async def send_html_email(self, to: List[str], subject: str, html_body: str,
                             text_body: Optional[str] = None,
                             cc: Optional[List[str]] = None, bcc: Optional[List[str]] = None,
                             attachments: Optional[List[Dict[str, Any]]] = None) -> NotificationResult:
        """Send HTML email message"""
        pass
    
    @abstractmethod
    async def validate_email_address(self, email: str) -> bool:
        """Validate email address format"""
        pass
    
    @abstractmethod
    async def check_email_deliverability(self, email: str) -> Dict[str, Any]:
        """Check if email address is deliverable"""
        pass
    
    @abstractmethod
    async def add_to_suppression_list(self, email: str, reason: str) -> bool:
        """Add email to suppression list"""
        pass
    
    @abstractmethod
    async def remove_from_suppression_list(self, email: str) -> bool:
        """Remove email from suppression list"""
        pass
    
    @abstractmethod
    async def is_suppressed(self, email: str) -> bool:
        """Check if email is in suppression list"""
        pass
    
    @abstractmethod
    async def get_bounce_rate(self) -> float:
        """Get current bounce rate"""
        pass
    
    @abstractmethod
    async def get_email_stats(self) -> Dict[str, Any]:
        """Get email service statistics"""
        pass


class IWebhookNotificationService(ABC):
    """Interface for webhook notifications"""
    
    @abstractmethod
    async def send_webhook(self, url: str, payload: Dict[str, Any], 
                          headers: Optional[Dict[str, str]] = None,
                          method: str = "POST") -> NotificationResult:
        """Send webhook notification"""
        pass
    
    @abstractmethod
    async def validate_webhook_url(self, url: str) -> bool:
        """Validate webhook URL"""
        pass
    
    @abstractmethod
    async def test_webhook_connectivity(self, url: str) -> Dict[str, Any]:
        """Test webhook connectivity"""
        pass
    
    @abstractmethod
    async def register_webhook_signature(self, url: str, secret: str) -> bool:
        """Register webhook signature for security"""
        pass
    
    @abstractmethod
    async def get_webhook_delivery_attempts(self, url: str) -> List[Dict[str, Any]]:
        """Get webhook delivery attempt history"""
        pass


class INotificationChannelManager(ABC):
    """Interface for managing notification channels"""
    
    @abstractmethod
    async def register_channel(self, channel_type: NotificationType, config: Dict[str, Any]) -> bool:
        """Register notification channel"""
        pass
    
    @abstractmethod
    async def update_channel_config(self, channel_type: NotificationType, config: Dict[str, Any]) -> bool:
        """Update channel configuration"""
        pass
    
    @abstractmethod
    async def disable_channel(self, channel_type: NotificationType) -> bool:
        """Disable notification channel"""
        pass
    
    @abstractmethod
    async def enable_channel(self, channel_type: NotificationType) -> bool:
        """Enable notification channel"""
        pass
    
    @abstractmethod
    async def get_channel_status(self, channel_type: NotificationType) -> Dict[str, Any]:
        """Get channel status and health"""
        pass
    
    @abstractmethod
    async def test_channel(self, channel_type: NotificationType) -> Dict[str, Any]:
        """Test notification channel"""
        pass
    
    @abstractmethod
    async def get_channel_metrics(self, channel_type: NotificationType) -> Dict[str, Any]:
        """Get channel delivery metrics"""
        pass


class INotificationQueue(ABC):
    """Interface for notification queue management"""
    
    @abstractmethod
    async def enqueue_notification(self, message: NotificationMessage) -> str:
        """Add notification to queue"""
        pass
    
    @abstractmethod
    async def dequeue_notification(self) -> Optional[NotificationMessage]:
        """Get next notification from queue"""
        pass
    
    @abstractmethod
    async def peek_queue(self, limit: int = 10) -> List[NotificationMessage]:
        """Peek at queue without removing items"""
        pass
    
    @abstractmethod
    async def get_queue_size(self) -> int:
        """Get current queue size"""
        pass
    
    @abstractmethod
    async def clear_queue(self) -> bool:
        """Clear notification queue"""
        pass
    
    @abstractmethod
    async def requeue_failed_notifications(self) -> int:
        """Requeue failed notifications and return count"""
        pass
    
    @abstractmethod
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        pass


class INotificationRateLimiter(ABC):
    """Interface for notification rate limiting"""
    
    @abstractmethod
    async def can_send(self, recipient: str, notification_type: NotificationType) -> bool:
        """Check if notification can be sent based on rate limits"""
        pass
    
    @abstractmethod
    async def record_send(self, recipient: str, notification_type: NotificationType) -> None:
        """Record notification send for rate limiting"""
        pass
    
    @abstractmethod
    async def get_rate_limit_status(self, recipient: str, notification_type: NotificationType) -> Dict[str, Any]:
        """Get rate limit status for recipient"""
        pass
    
    @abstractmethod
    async def reset_rate_limit(self, recipient: str, notification_type: NotificationType) -> bool:
        """Reset rate limit for recipient"""
        pass
    
    @abstractmethod
    async def configure_rate_limit(self, notification_type: NotificationType, 
                                  max_per_minute: int, max_per_hour: int, max_per_day: int) -> bool:
        """Configure rate limits for notification type"""
        pass