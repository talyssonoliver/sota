#!/usr/bin/env python3
"""
Webhook Manager - Step 7.7: API Integration & Webhooks

Comprehensive webhook system for external system integration and review workflows.
Supports outgoing webhooks for review events and incoming webhooks for external approvals.
"""

import json
import logging
import hashlib
import hmac
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

import requests
from flask import Blueprint, request, jsonify


class WebhookEventType(Enum):
    """Types of webhook events."""
    REVIEW_CREATED = "review.created"
    REVIEW_APPROVED = "review.approved"
    REVIEW_REJECTED = "review.rejected"
    REVIEW_ESCALATED = "review.escalated"
    REVIEW_TIMEOUT = "review.timeout"
    TASK_STATUS_CHANGED = "task.status_changed"
    CHECKPOINT_CREATED = "checkpoint.created"
    CHECKPOINT_COMPLETED = "checkpoint.completed"
    ESCALATION_TRIGGERED = "escalation.triggered"
    FEEDBACK_RECEIVED = "feedback.received"


class WebhookStatus(Enum):
    """Webhook delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"


@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration."""
    id: str
    name: str
    url: str
    secret: str
    events: List[WebhookEventType]
    active: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    headers: Dict[str, str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class WebhookDelivery:
    """Webhook delivery record."""
    id: str
    endpoint_id: str
    event_type: WebhookEventType
    payload: Dict[str, Any]
    status: WebhookStatus
    created_at: datetime
    delivered_at: Optional[datetime] = None
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    next_retry_at: Optional[datetime] = None


class WebhookEventData:
    """Base class for webhook event data."""
    
    @staticmethod
    def review_created(task_id: str, checkpoint_id: str, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create review.created event data."""
        return {
            "event": WebhookEventType.REVIEW_CREATED.value,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "task_id": task_id,
                "checkpoint_id": checkpoint_id,
                "review_type": review_data.get("checkpoint_type", "unknown"),
                "risk_level": review_data.get("risk_level", "medium"),
                "timeout_at": review_data.get("timeout_at"),
                "reviewer_assigned": review_data.get("reviewer"),
                "metadata": review_data.get("metadata", {})
            }
        }
    
    @staticmethod
    def review_approved(task_id: str, checkpoint_id: str, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create review.approved event data."""
        return {
            "event": WebhookEventType.REVIEW_APPROVED.value,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "task_id": task_id,
                "checkpoint_id": checkpoint_id,
                "reviewer": approval_data.get("reviewer", "unknown"),
                "decision": "approved",
                "feedback": approval_data.get("feedback"),
                "completed_at": approval_data.get("approved_at", datetime.now().isoformat()),
                "metadata": approval_data.get("metadata", {})
            }
        }
    
    @staticmethod
    def review_rejected(task_id: str, checkpoint_id: str, rejection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create review.rejected event data."""
        return {
            "event": WebhookEventType.REVIEW_REJECTED.value,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "task_id": task_id,
                "checkpoint_id": checkpoint_id,
                "reviewer": rejection_data.get("reviewer", "unknown"),
                "decision": "rejected",
                "reason": rejection_data.get("reason", "No reason provided"),
                "feedback": rejection_data.get("feedback"),
                "rejected_at": rejection_data.get("rejected_at", datetime.now().isoformat()),
                "metadata": rejection_data.get("metadata", {})
            }
        }
    
    @staticmethod
    def escalation_triggered(task_id: str, escalation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create escalation.triggered event data."""
        return {
            "event": WebhookEventType.ESCALATION_TRIGGERED.value,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "task_id": task_id,
                "escalation_level": escalation_data.get("level", 1),
                "reason": escalation_data.get("reason", "timeout"),
                "original_reviewer": escalation_data.get("original_reviewer"),
                "escalated_to": escalation_data.get("escalated_to", []),
                "timeout_occurred_at": escalation_data.get("timeout_at"),
                "metadata": escalation_data.get("metadata", {})
            }
        }


class WebhookManager:
    """Manages webhook endpoints and deliveries."""
    
    def __init__(self, config_path: str = "config/webhooks.json"):
        """Initialize webhook manager."""
        self.config_path = Path(config_path)
        self.logger = logging.getLogger("webhook.manager")
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.deliveries: Dict[str, WebhookDelivery] = {}
        self.event_handlers: Dict[WebhookEventType, List[Callable]] = {}
        
        # Load configuration
        self._load_config()
        
        # Initialize Flask blueprint for incoming webhooks
        self.webhook_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')
        self._setup_routes()
    
    def _load_config(self):
        """Load webhook configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    
                for endpoint_data in config.get("endpoints", []):
                    endpoint = WebhookEndpoint(
                        id=endpoint_data["id"],
                        name=endpoint_data["name"],
                        url=endpoint_data["url"],
                        secret=endpoint_data["secret"],
                        events=[WebhookEventType(event) for event in endpoint_data["events"]],
                        active=endpoint_data.get("active", True),
                        max_retries=endpoint_data.get("max_retries", 3),
                        timeout_seconds=endpoint_data.get("timeout_seconds", 30),
                        headers=endpoint_data.get("headers", {}),
                        created_at=datetime.fromisoformat(endpoint_data.get("created_at", datetime.now().isoformat()))
                    )
                    self.endpoints[endpoint.id] = endpoint
                    
        except Exception as e:
            self.logger.error(f"Failed to load webhook config: {e}")
    
    def _save_config(self):
        """Save webhook configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                "endpoints": [
                    {
                        "id": endpoint.id,
                        "name": endpoint.name,
                        "url": endpoint.url,
                        "secret": endpoint.secret,
                        "events": [event.value for event in endpoint.events],
                        "active": endpoint.active,
                        "max_retries": endpoint.max_retries,
                        "timeout_seconds": endpoint.timeout_seconds,
                        "headers": endpoint.headers,
                        "created_at": endpoint.created_at.isoformat()
                    }
                    for endpoint in self.endpoints.values()
                ]
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save webhook config: {e}")
    
    def _setup_routes(self):
        """Setup Flask routes for incoming webhooks."""
        
        @self.webhook_bp.route('/incoming/<endpoint_id>', methods=['POST'])
        def handle_incoming_webhook(endpoint_id: str):
            """Handle incoming webhook."""
            try:
                # Verify endpoint exists
                if endpoint_id not in self.endpoints:
                    return jsonify({"error": "Unknown endpoint"}), 404
                
                endpoint = self.endpoints[endpoint_id]
                
                # Verify signature if secret is provided
                if endpoint.secret:
                    signature = request.headers.get('X-Webhook-Signature')
                    if not signature or not self._verify_signature(request.data, endpoint.secret, signature):
                        return jsonify({"error": "Invalid signature"}), 401
                
                # Process webhook data
                webhook_data = request.get_json()
                result = self._process_incoming_webhook(endpoint_id, webhook_data)
                
                return jsonify(result), 200
                
            except Exception as e:
                self.logger.error(f"Error handling incoming webhook: {e}")
                return jsonify({"error": "Internal server error"}), 500
        
        @self.webhook_bp.route('/endpoints', methods=['GET'])
        def list_endpoints():
            """List webhook endpoints."""
            return jsonify({
                "endpoints": [
                    {
                        "id": endpoint.id,
                        "name": endpoint.name,
                        "url": endpoint.url,
                        "events": [event.value for event in endpoint.events],
                        "active": endpoint.active
                    }
                    for endpoint in self.endpoints.values()
                ]
            })
        
        @self.webhook_bp.route('/endpoints', methods=['POST'])
        def create_endpoint():
            """Create new webhook endpoint."""
            try:
                data = request.get_json()
                endpoint = WebhookEndpoint(
                    id=data["id"],
                    name=data["name"],
                    url=data["url"],
                    secret=data["secret"],
                    events=[WebhookEventType(event) for event in data["events"]],
                    active=data.get("active", True),
                    max_retries=data.get("max_retries", 3),
                    timeout_seconds=data.get("timeout_seconds", 30),
                    headers=data.get("headers", {})
                )
                
                self.endpoints[endpoint.id] = endpoint
                self._save_config()
                
                return jsonify({"status": "created", "endpoint_id": endpoint.id}), 201
                
            except Exception as e:
                self.logger.error(f"Error creating endpoint: {e}")
                return jsonify({"error": str(e)}), 400
        
        @self.webhook_bp.route('/deliveries', methods=['GET'])
        def list_deliveries():
            """List webhook deliveries."""
            deliveries = []
            for delivery in self.deliveries.values():
                deliveries.append({
                    "id": delivery.id,
                    "endpoint_id": delivery.endpoint_id,
                    "event_type": delivery.event_type.value,
                    "status": delivery.status.value,
                    "created_at": delivery.created_at.isoformat(),
                    "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else None,
                    "retry_count": delivery.retry_count,
                    "response_status": delivery.response_status
                })
            
            return jsonify({"deliveries": deliveries})
    
    def _verify_signature(self, payload: bytes, secret: str, signature: str) -> bool:
        """Verify webhook signature."""
        try:
            expected_signature = hmac.new(
                secret.encode(), 
                payload, 
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(f"sha256={expected_signature}", signature)
        except Exception:
            return False
    
    def _process_incoming_webhook(self, endpoint_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook data."""
        self.logger.info(f"Processing incoming webhook from {endpoint_id}: {data.get('event', 'unknown')}")
        
        # Handle different incoming webhook types
        event_type = data.get("event")
        
        if event_type == "external_approval":
            return self._handle_external_approval(data)
        elif event_type == "external_rejection":
            return self._handle_external_rejection(data)
        elif event_type == "external_escalation":
            return self._handle_external_escalation(data)
        else:
            self.logger.warning(f"Unknown incoming webhook event type: {event_type}")
            return {"status": "ignored", "reason": "unknown_event_type"}
    
    def _handle_external_approval(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle external approval webhook."""
        task_id = data.get("task_id")
        checkpoint_id = data.get("checkpoint_id")
        reviewer = data.get("reviewer", "external_system")
        
        # Import here to avoid circular imports
        from orchestration.hitl_engine import HITLPolicyEngine
        
        try:
            hitl_engine = HITLPolicyEngine()
            result = hitl_engine.approve_checkpoint(
                checkpoint_id=checkpoint_id,
                reviewer=reviewer,
                feedback=data.get("feedback", {}),
                metadata={"source": "external_webhook", "external_data": data}
            )
            
            return {"status": "approved", "checkpoint_id": checkpoint_id, "result": result}
            
        except Exception as e:
            self.logger.error(f"Failed to process external approval: {e}")
            return {"status": "error", "error": str(e)}
    
    def _handle_external_rejection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle external rejection webhook."""
        task_id = data.get("task_id")
        checkpoint_id = data.get("checkpoint_id")
        reviewer = data.get("reviewer", "external_system")
        reason = data.get("reason", "External system rejection")
        
        from orchestration.hitl_engine import HITLPolicyEngine
        
        try:
            hitl_engine = HITLPolicyEngine()
            result = hitl_engine.reject_checkpoint(
                checkpoint_id=checkpoint_id,
                reviewer=reviewer,
                reason=reason,
                feedback=data.get("feedback", {}),
                metadata={"source": "external_webhook", "external_data": data}
            )
            
            return {"status": "rejected", "checkpoint_id": checkpoint_id, "result": result}
            
        except Exception as e:
            self.logger.error(f"Failed to process external rejection: {e}")
            return {"status": "error", "error": str(e)}
    
    def _handle_external_escalation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle external escalation webhook."""
        task_id = data.get("task_id")
        escalation_level = data.get("level", 1)
        reason = data.get("reason", "External escalation request")
        
        from utils.escalation_system import EscalationEngine
        
        try:
            escalation_engine = EscalationEngine()
            result = escalation_engine.escalate_task(
                task_id=task_id,
                level=escalation_level,
                reason=reason,
                metadata={"source": "external_webhook", "external_data": data}
            )
            
            return {"status": "escalated", "task_id": task_id, "result": result}
            
        except Exception as e:
            self.logger.error(f"Failed to process external escalation: {e}")
            return {"status": "error", "error": str(e)}
    
    def register_endpoint(self, endpoint: WebhookEndpoint) -> bool:
        """Register a new webhook endpoint."""
        try:
            self.endpoints[endpoint.id] = endpoint
            self._save_config()
            self.logger.info(f"Registered webhook endpoint: {endpoint.name} ({endpoint.id})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register endpoint: {e}")
            return False
    
    def remove_endpoint(self, endpoint_id: str) -> bool:
        """Remove a webhook endpoint."""
        try:
            if endpoint_id in self.endpoints:
                del self.endpoints[endpoint_id]
                self._save_config()
                self.logger.info(f"Removed webhook endpoint: {endpoint_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove endpoint: {e}")
            return False
    
    def send_webhook(self, event_type: WebhookEventType, event_data: Dict[str, Any], task_id: str = None) -> List[str]:
        """Send webhook to all registered endpoints for the event type."""
        delivery_ids = []
        
        for endpoint in self.endpoints.values():
            if endpoint.active and event_type in endpoint.events:
                delivery_id = self._create_delivery(endpoint, event_type, event_data)
                delivery_ids.append(delivery_id)
                
                # Send webhook asynchronously
                asyncio.create_task(self._deliver_webhook(delivery_id))
        
        return delivery_ids
    
    def _create_delivery(self, endpoint: WebhookEndpoint, event_type: WebhookEventType, payload: Dict[str, Any]) -> str:
        """Create a webhook delivery record."""
        delivery_id = f"del_{int(time.time())}_{hash(endpoint.id)}_{len(self.deliveries)}"
        
        delivery = WebhookDelivery(
            id=delivery_id,
            endpoint_id=endpoint.id,
            event_type=event_type,
            payload=payload,
            status=WebhookStatus.PENDING,
            created_at=datetime.now()
        )
        
        self.deliveries[delivery_id] = delivery
        return delivery_id
    
    async def _deliver_webhook(self, delivery_id: str):
        """Deliver a webhook with retry logic."""
        if delivery_id not in self.deliveries:
            return
        
        delivery = self.deliveries[delivery_id]
        endpoint = self.endpoints.get(delivery.endpoint_id)
        
        if not endpoint:
            delivery.status = WebhookStatus.FAILED
            delivery.error_message = "Endpoint not found"
            return
        
        for attempt in range(endpoint.max_retries + 1):
            try:
                # Prepare payload
                payload_json = json.dumps(delivery.payload)
                
                # Generate signature
                signature = hmac.new(
                    endpoint.secret.encode(),
                    payload_json.encode(),
                    hashlib.sha256
                ).hexdigest()
                
                # Prepare headers
                headers = {
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": f"sha256={signature}",
                    "X-Webhook-Event": delivery.event_type.value,
                    "X-Webhook-Delivery": delivery.id,
                    **endpoint.headers
                }
                
                # Send request
                response = requests.post(
                    endpoint.url,
                    data=payload_json,
                    headers=headers,
                    timeout=endpoint.timeout_seconds
                )
                
                # Update delivery record
                delivery.response_status = response.status_code
                delivery.response_body = response.text[:1000]  # Limit response body size
                
                if response.status_code < 400:
                    delivery.status = WebhookStatus.DELIVERED
                    delivery.delivered_at = datetime.now()
                    self.logger.info(f"Webhook delivered successfully: {delivery_id}")
                    return
                else:
                    raise requests.HTTPError(f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                delivery.retry_count = attempt + 1
                delivery.error_message = str(e)
                
                if attempt < endpoint.max_retries:
                    # Calculate next retry time (exponential backoff)
                    delay_seconds = 2 ** attempt * 60  # 1min, 2min, 4min, etc.
                    delivery.next_retry_at = datetime.now() + timedelta(seconds=delay_seconds)
                    delivery.status = WebhookStatus.RETRYING
                    
                    self.logger.warning(f"Webhook delivery failed, retrying in {delay_seconds}s: {e}")
                    await asyncio.sleep(delay_seconds)
                else:
                    delivery.status = WebhookStatus.FAILED
                    self.logger.error(f"Webhook delivery failed permanently: {e}")
                    return
    
    def get_delivery_status(self, delivery_id: str) -> Optional[WebhookDelivery]:
        """Get webhook delivery status."""
        return self.deliveries.get(delivery_id)
    
    def get_endpoint_stats(self, endpoint_id: str) -> Dict[str, Any]:
        """Get statistics for a webhook endpoint."""
        if endpoint_id not in self.endpoints:
            return {}
        
        endpoint_deliveries = [d for d in self.deliveries.values() if d.endpoint_id == endpoint_id]
        
        total = len(endpoint_deliveries)
        delivered = len([d for d in endpoint_deliveries if d.status == WebhookStatus.DELIVERED])
        failed = len([d for d in endpoint_deliveries if d.status == WebhookStatus.FAILED])
        pending = len([d for d in endpoint_deliveries if d.status in [WebhookStatus.PENDING, WebhookStatus.RETRYING]])
        
        return {
            "endpoint_id": endpoint_id,
            "total_deliveries": total,
            "successful_deliveries": delivered,
            "failed_deliveries": failed,
            "pending_deliveries": pending,
            "success_rate": (delivered / total * 100) if total > 0 else 0
        }


# Global webhook manager instance
_webhook_manager = None

def get_webhook_manager() -> WebhookManager:
    """Get global webhook manager instance."""
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager


# Convenience functions for sending webhooks
def send_review_created_webhook(task_id: str, checkpoint_id: str, review_data: Dict[str, Any]):
    """Send review.created webhook."""
    event_data = WebhookEventData.review_created(task_id, checkpoint_id, review_data)
    return get_webhook_manager().send_webhook(WebhookEventType.REVIEW_CREATED, event_data, task_id)


def send_review_approved_webhook(task_id: str, checkpoint_id: str, approval_data: Dict[str, Any]):
    """Send review.approved webhook."""
    event_data = WebhookEventData.review_approved(task_id, checkpoint_id, approval_data)
    return get_webhook_manager().send_webhook(WebhookEventType.REVIEW_APPROVED, event_data, task_id)


def send_review_rejected_webhook(task_id: str, checkpoint_id: str, rejection_data: Dict[str, Any]):
    """Send review.rejected webhook."""
    event_data = WebhookEventData.review_rejected(task_id, checkpoint_id, rejection_data)
    return get_webhook_manager().send_webhook(WebhookEventType.REVIEW_REJECTED, event_data, task_id)


def send_escalation_webhook(task_id: str, escalation_data: Dict[str, Any]):
    """Send escalation.triggered webhook."""
    event_data = WebhookEventData.escalation_triggered(task_id, escalation_data)
    return get_webhook_manager().send_webhook(WebhookEventType.ESCALATION_TRIGGERED, event_data, task_id)


# Module-level exports for integration
webhook_manager = get_webhook_manager()
webhook_bp = webhook_manager.webhook_bp
