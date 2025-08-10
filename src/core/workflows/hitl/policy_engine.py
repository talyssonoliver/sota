
from src.infrastructure.utils.common_imports import (
    Any,
    Dict,
    List,
    Optional,
    datetime,
    logging,
    yaml
)
"""
HITL Policy Engine

Core policy engine for managing checkpoints and approvals.
"""

# import logging  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports
# from typing import Any, Dict, List, Optional  # Consolidated to common_imports

try:
#     import yaml  # Consolidated to common_imports

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from .models import HITLCheckpoint, HITLReviewDecision, HITLAuditEntry
from .types import CheckpointStatus, RiskLevel

logger = logging.getLogger(__name__)


class HITLPolicyEngine:
    """Core HITL policy engine for managing checkpoints and approvals"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize HITL policy engine"""
        self.config_path = config_path or "config/hitl_policies.yaml"
        self.policies = self._load_policies()
        self.checkpoints: Dict[str, HITLCheckpoint] = {}
        self.audit_log: List[Dict[str, Any]] = []

        # Initialize storage directories
        from config.build_paths import HITL_STORAGE_DIR

        self.storage_dir = HITL_STORAGE_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Initialize notification system
        self.notification_handlers = []
        self._init_notification_handlers()

        logger.info(
            f"HITL Policy Engine initialized with {len(self.policies)} policy groups"
        )

    def _load_policies(self) -> Dict[str, Any]:
        """Load HITL policies from configuration file"""
        if not YAML_AVAILABLE:
            logger.warning("YAML not available, using default policies")
            return self._get_default_policies()

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"HITL policies file not found: {self.config_path}")
            return self._get_default_policies()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing HITL policies: {e}")
            return self._get_default_policies()
        except Exception as e:
            logger.error(f"Unexpected error loading policies: {e}")
            return self._get_default_policies()

    def _get_default_policies(self) -> Dict[str, Any]:
        """Get default HITL policies as fallback"""
        return {
            "hitl_policies": {
                "global_settings": {
                    "enabled": True,
                    "default_timeout_hours": 24,
                    "auto_escalation_enabled": True,
                    "notification_channels": ["dashboard"],
                },
                "checkpoint_triggers": {
                    "output_evaluation": {
                        "enabled": True,
                        "conditions": ["critical_service_changes"],
                        "required_approvals": 1,
                        "reviewers": ["Technical Lead"],
                    }
                },
            }
        }

    def _init_notification_handlers(self):
        """Initialize notification handlers"""
        # Dashboard notification handler
        try:
            from src.core.workflows.notification_handlers import \
                DashboardNotificationHandler

            self.notification_handlers.append(DashboardNotificationHandler())
        except ImportError:
            logger.warning("Dashboard notification handler not available")

        # Email notification handler (if configured)
        if (
            self.policies.get("hitl_policies", {})
            .get("integrations", {})
            .get("notifications", {})
            .get("email", {})
            .get("enabled")
        ):
            try:
                from src.core.workflows.notification_handlers import \
                    EmailNotificationHandler

                self.notification_handlers.append(EmailNotificationHandler())
            except ImportError:
                logger.warning("Email notification handler not available")

        # Slack notification handler (if configured)
        if (
            self.policies.get("hitl_policies", {})
            .get("integrations", {})
            .get("notifications", {})
            .get("slack", {})
            .get("enabled")
        ):
            try:
                from src.core.workflows.notification_handlers import \
                    SlackNotificationHandler

                self.notification_handlers.append(SlackNotificationHandler())
            except ImportError:
                logger.warning("Slack notification handler not available")

    def _normalize_policy_access(self, *keys):
        """Helper method to access policies with fallback for both config formats"""
        # First try with hitl_policies wrapper (production format)
        result = self.policies
        try:
            for key in ["hitl_policies"] + list(keys):
                result = result[key]
            return result
        except (KeyError, TypeError):
            pass

        # Fallback to direct access (test format)
        result = self.policies
        try:
            for key in keys:
                result = result[key]
            return result
        except (KeyError, TypeError):
            return {}

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status for health checks"""
        return {
            "status": "healthy",
            "checkpoints_count": len(self.checkpoints),
            "policies_loaded": len(self.policies),
            "notification_handlers": len(self.notification_handlers),
            "audit_log_entries": len(self.audit_log),
        }

    def get_pending_checkpoints(
        self, task_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get pending checkpoints"""
        pending = []
        for checkpoint_id, checkpoint in self.checkpoints.items():
            if checkpoint.status == CheckpointStatus.PENDING:
                if task_id is None or checkpoint.task_id == task_id:
                    pending.append(
                        {
                            "id": checkpoint_id,
                            "task_id": checkpoint.task_id,
                            "status": checkpoint.status,
                            "created_at": checkpoint.created_at,
                            "metadata": checkpoint.metadata,
                        }
                    )
        return pending
    
    def _assess_risk(self, task_type: str, risk_factors: List[str]) -> RiskLevel:
        """Assess risk level based on task type and risk factors"""
        # High risk factors
        high_risk_indicators = [
            "complex_logic", "external_dependency", "security_sensitive",
            "data_modification", "system_critical", "user_facing"
        ]
        
        # Medium risk factors  
        medium_risk_indicators = [
            "configuration_change", "moderate_complexity", "internal_api"
        ]
        
        # Count high and medium risk factors
        high_risk_count = sum(1 for factor in risk_factors if factor in high_risk_indicators)
        medium_risk_count = sum(1 for factor in risk_factors if factor in medium_risk_indicators)
        
        # Determine risk level
        if high_risk_count >= 2 or (high_risk_count >= 1 and medium_risk_count >= 2):
            return RiskLevel.HIGH
        elif high_risk_count >= 1 or medium_risk_count >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def create_checkpoint(
        self,
        task_id: str,
        checkpoint_type: str,
        task_type: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        risk_factors: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HITLCheckpoint:
        """Create a new checkpoint"""
        checkpoint_id = f"checkpoint_{task_id}_{len(self.checkpoints)}"

        if metadata is None:
            metadata = {}
        
        # Use provided parameters with fallbacks
        actual_task_type = task_type or "generic"
        actual_content = content or {}
        actual_risk_factors = risk_factors or []
        
        # Assess risk level based on risk factors
        risk_level = self._assess_risk(actual_task_type, actual_risk_factors)
        
        # Store risk factors in metadata if provided
        if risk_factors:
            metadata['risk_factors'] = risk_factors

        checkpoint = HITLCheckpoint(
            checkpoint_id=checkpoint_id,
            task_id=task_id,
            checkpoint_type=checkpoint_type,
            task_type=actual_task_type,
            content=actual_content,
            risk_level=risk_level,
            status=CheckpointStatus.PENDING,
            created_at=datetime.now(),
            risk_factors=actual_risk_factors,
            metadata=metadata or {},
        )

        self.checkpoints[checkpoint_id] = checkpoint

        # Add to audit log
        audit_entry = HITLAuditEntry(
            timestamp=checkpoint.created_at,
            checkpoint_id=checkpoint_id,
            action="created",
            user_id="system",
            details={
                "task_id": task_id,
                "checkpoint_type": checkpoint_type,
                "task_type": actual_task_type
            },
            metadata=metadata
        )
        self.audit_log.append(audit_entry)

        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Optional[HITLCheckpoint]:
        """Get checkpoint details"""
        return self.checkpoints.get(checkpoint_id)

    def get_checkpoint_audit_log(self, checkpoint_id: str) -> List[HITLAuditEntry]:
        """Get audit log for a checkpoint"""
        return [
            entry
            for entry in self.audit_log
            if entry.checkpoint_id == checkpoint_id
        ]

    def process_decision(
        self,
        checkpoint_id: str,
        decision: str,
        user_id: Optional[str] = None,
        comments: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a decision for a checkpoint"""
        checkpoint = self.checkpoints.get(checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")

        checkpoint.status = (
            CheckpointStatus.APPROVED
            if decision == "approve"
            else CheckpointStatus.REJECTED
        )

        # Add to audit log
        self.audit_log.append(
            {
                "action": "decision_processed",
                "checkpoint_id": checkpoint_id,
                "decision": decision,
                "user_id": user_id,
                "comments": comments,
                "timestamp": (
                    datetime.now().isoformat()
                    if "datetime" in globals()
                    else str(len(self.audit_log))
                ),
            }
        )

        return {
            "checkpoint_id": checkpoint_id,
            "decision": decision,
            "status": checkpoint.status,
        }

    def escalate_checkpoint(
        self, checkpoint_id: str, escalation_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Escalate a checkpoint"""
        checkpoint = self.checkpoints.get(checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")

        checkpoint.status = CheckpointStatus.ESCALATED

        # Add to audit log
        self.audit_log.append(
            {
                "action": "checkpoint_escalated",
                "checkpoint_id": checkpoint_id,
                "reason": escalation_reason,
                "timestamp": (
                    datetime.now().isoformat()
                    if "datetime" in globals()
                    else str(len(self.audit_log))
                ),
            }
        )

        return {
            "checkpoint_id": checkpoint_id,
            "status": "escalated",
            "escalation_reason": escalation_reason,
        }

    def get_checkpoints_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all checkpoints for a specific task"""
        task_checkpoints = []
        for checkpoint_id, checkpoint in self.checkpoints.items():
            if checkpoint.task_id == task_id:
                task_checkpoints.append(
                    {
                        "id": checkpoint_id,
                        "task_id": checkpoint.task_id,
                        "status": checkpoint.status,
                        "created_at": checkpoint.created_at,
                        "metadata": checkpoint.metadata,
                    }
                )
        return task_checkpoints

    def get_audit_trail(
        self, task_id: Optional[str] = None, checkpoint_id: Optional[str] = None
    ) -> List[HITLAuditEntry]:
        """Get audit trail"""
        if checkpoint_id:
            return self.get_checkpoint_audit_log(checkpoint_id)
        elif task_id:
            return [
                entry for entry in self.audit_log if entry.details.get("task_id") == task_id
            ]
        else:
            return self.audit_log.copy()

    def approve_checkpoint(
        self,
        checkpoint_id: str,
        user_id: Optional[str] = None,
        comments: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Approve a checkpoint"""
        return self.process_decision(checkpoint_id, "approve", user_id, comments)

    def reject_checkpoint(
        self,
        checkpoint_id: str,
        user_id: Optional[str] = None,
        comments: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Reject a checkpoint"""
        return self.process_decision(checkpoint_id, "reject", user_id, comments)

    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        total_checkpoints = len(self.checkpoints)
        pending_count = sum(
            1
            for cp in self.checkpoints.values()
            if cp.status == CheckpointStatus.PENDING
        )
        approved_count = sum(
            1
            for cp in self.checkpoints.values()
            if cp.status == CheckpointStatus.APPROVED
        )
        rejected_count = sum(
            1
            for cp in self.checkpoints.values()
            if cp.status == CheckpointStatus.REJECTED
        )

        return {
            "total_checkpoints": total_checkpoints,
            "pending": pending_count,
            "approved": approved_count,
            "rejected": rejected_count,
            "approval_rate": (
                (approved_count / total_checkpoints * 100)
                if total_checkpoints > 0
                else 0
            ),
        }

    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get active workflows"""
        # Mock implementation - return active tasks based on pending checkpoints
        active_tasks = set()
        for checkpoint in self.checkpoints.values():
            if checkpoint.status == CheckpointStatus.PENDING:
                active_tasks.add(checkpoint.task_id)

        return [
            {
                "task_id": task_id,
                "status": "active",
                "pending_checkpoints": len(
                    [
                        cp
                        for cp in self.checkpoints.values()
                        if cp.task_id == task_id
                        and cp.status == CheckpointStatus.PENDING
                    ]
                ),
            }
            for task_id in active_tasks
        ]

    def get_policies_config(self) -> Dict[str, Any]:
        """Get policies configuration"""
        return self.policies.copy()

    def get_recent_notifications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent notifications"""
        # Mock implementation based on recent audit log entries
        recent_entries = self.audit_log[-limit:] if self.audit_log else []

        notifications = []
        for entry in recent_entries:
            notifications.append(
                {
                    "id": f"notif_{len(notifications)}",
                    "type": "checkpoint_action",
                    "message": f"Checkpoint {entry.get('action', 'action')} for {entry.get('checkpoint_id', 'unknown')}",
                    "timestamp": entry.get("timestamp", "unknown"),
                    "metadata": entry,
                }
            )

        return notifications

    async def process_decision(self, decision: 'HITLReviewDecision') -> bool:
        """Process a review decision for a checkpoint"""
        checkpoint = self.checkpoints.get(decision.checkpoint_id)
        if not checkpoint:
            return False

        # Update checkpoint status based on decision
        if decision.decision == "approve":
            checkpoint.status = CheckpointStatus.APPROVED
            checkpoint.resolved_at = decision.reviewed_at
            checkpoint.approvals.append({
                "reviewer_id": decision.reviewer_id,
                "comments": decision.comments,
                "reviewed_at": decision.reviewed_at.isoformat(),
                "metadata": decision.metadata
            })
        elif decision.decision == "reject":
            checkpoint.status = CheckpointStatus.REJECTED
            checkpoint.resolved_at = decision.reviewed_at
            checkpoint.rejections.append({
                "reviewer_id": decision.reviewer_id,
                "comments": decision.comments,
                "reviewed_at": decision.reviewed_at.isoformat(),
                "metadata": decision.metadata
            })
        elif decision.decision == "escalate":
            checkpoint.status = CheckpointStatus.ESCALATED
            checkpoint.escalation_level += 1

        # Add to audit log - convert decision to past tense for audit action
        action_mapping = {
            "approve": "approved",
            "reject": "rejected", 
            "escalate": "escalated"
        }
        audit_action = action_mapping.get(decision.decision, decision.decision)
        
        audit_entry = HITLAuditEntry(
            timestamp=decision.reviewed_at,
            checkpoint_id=decision.checkpoint_id,
            action=audit_action,
            user_id=decision.reviewer_id,
            details={
                "decision": decision.decision,
                "comments": decision.comments
            },
            metadata=decision.metadata
        )
        self.audit_log.append(audit_entry)

        return True

    def process_timeouts(self) -> List[HITLCheckpoint]:
        """Process checkpoints that have timed out"""
        timed_out_checkpoints = []
        current_time = datetime.now()

        for checkpoint in self.checkpoints.values():
            if (checkpoint.status == CheckpointStatus.PENDING and 
                checkpoint.timeout_at and 
                current_time > checkpoint.timeout_at):
                
                # Escalate timed out checkpoint
                checkpoint.status = CheckpointStatus.ESCALATED
                checkpoint.escalation_level += 1
                
                # Add to audit log
                audit_entry = HITLAuditEntry(
                    timestamp=current_time,
                    checkpoint_id=checkpoint.checkpoint_id,
                    action="checkpoint_timeout",
                    user_id="system",
                    details={
                        "timeout_at": checkpoint.timeout_at.isoformat(),
                        "escalation_level": checkpoint.escalation_level
                    }
                )
                self.audit_log.append(audit_entry)
                
                timed_out_checkpoints.append(checkpoint)

        return timed_out_checkpoints
