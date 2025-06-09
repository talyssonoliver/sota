"""
Human-in-the-Loop (HITL) Engine for Phase 7 Implementation

This module provides comprehensive HITL checkpoint management, risk assessment,
and approval workflows for AI agent task execution.

Key Features:
- Dynamic checkpoint creation based on risk assessment
- Multi-level approval workflows
- Escalation policies with timeout handling
- Real-time notification system
- Dashboard integration
- Audit trail and compliance reporting
"""

import os
import yaml
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import uuid
import hashlib
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CheckpointType(Enum):
    """Types of HITL checkpoints"""
    AGENT_PROMPT = "agent_prompt"
    OUTPUT_EVALUATION = "output_evaluation"
    QA_VALIDATION = "qa_validation"
    DOCUMENTATION = "documentation"
    TASK_TRANSITIONS = "task_transitions"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CheckpointStatus(Enum):
    """Checkpoint status values"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class TimeoutAction(Enum):
    """Actions to take when checkpoint times out"""
    AUTO_APPROVE = "auto_approve"
    ESCALATE = "escalate"
    BLOCK = "block"
    NOTIFY_ONLY = "notify_only"


@dataclass
class HITLCheckpoint:
    """Represents a Human-in-the-Loop checkpoint"""
    checkpoint_id: str
    task_id: str
    checkpoint_type: str
    task_type: str
    content: Dict[str, Any]
    risk_level: RiskLevel
    status: CheckpointStatus
    created_at: datetime
    timeout_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    risk_factors: List[str] = None
    required_approvals: int = 1
    assigned_reviewers: List[str] = None
    approvals: List[Dict[str, Any]] = None
    rejections: List[Dict[str, Any]] = None
    escalation_level: int = 0
    metadata: Dict[str, Any] = None
    parent_checkpoint_id: Optional[str] = None
    description: str = ""
    mitigation_suggestions: List[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.risk_factors is None:
            self.risk_factors = []
        if self.assigned_reviewers is None:
            self.assigned_reviewers = []
        if self.approvals is None:
            self.approvals = []
        if self.rejections is None:
            self.rejections = []
        if self.mitigation_suggestions is None:
            self.mitigation_suggestions = []
        if self.timeout_at is None:
            self.timeout_at = self.created_at + timedelta(hours=24)
    
    @property
    def id(self) -> str:
        """Get checkpoint ID (alias for checkpoint_id)"""
        return self.checkpoint_id
    
    @property
    def is_overdue(self) -> bool:
        """Check if checkpoint is overdue"""
        return datetime.now() > self.timeout_at if self.timeout_at else False
    
    @property
    def is_approved(self) -> bool:
        """Check if checkpoint has sufficient approvals"""
        return len(self.approvals) >= self.required_approvals
    
    @property
    def approval_progress(self) -> float:
        """Get approval progress as percentage"""
        return (len(self.approvals) / self.required_approvals) * 100
    
    @property
    def deadline(self) -> Optional[datetime]:
        """Get checkpoint deadline (alias for timeout_at)"""
        return self.timeout_at
    
    @property
    def reviewers(self) -> List[str]:
        """Get reviewers (alias for assigned_reviewers)"""
        return self.assigned_reviewers or []
    
    @property
    def context(self) -> Dict[str, Any]:
        """Get context information for the checkpoint"""
        context_info = self.content.copy()
        context_info.update({
            "task_type": self.task_type,
            "description": self.description,
            "risk_factors": self.risk_factors,
            "checkpoint_type": self.checkpoint_type
        })
        return context_info
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary"""
        return {
            'checkpoint_id': self.checkpoint_id,
            'task_id': self.task_id,
            'checkpoint_type': self.checkpoint_type,
            'task_type': self.task_type,
            'content': self.content,
            'risk_level': self.risk_level.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'timeout_at': self.timeout_at.isoformat() if self.timeout_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'risk_factors': self.risk_factors,
            'required_approvals': self.required_approvals,
            'assigned_reviewers': self.assigned_reviewers,
            'approvals': self.approvals,
            'rejections': self.rejections,
            'escalation_level': self.escalation_level,
            'metadata': self.metadata,
            'parent_checkpoint_id': self.parent_checkpoint_id,
            'description': self.description,
            'mitigation_suggestions': self.mitigation_suggestions,
            'deadline': self.timeout_at.isoformat() if self.timeout_at else None,
            'reviewers': self.assigned_reviewers or []
        }


@dataclass
class RiskAssessment:
    """Risk assessment result"""
    risk_level: RiskLevel
    confidence_score: float
    risk_factors: List[str]
    mitigation_suggestions: List[str]
    auto_approve_eligible: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['risk_level'] = self.risk_level.value
        return data


@dataclass
class HITLReviewDecision:
    """Represents a review decision for a checkpoint"""
    checkpoint_id: str
    decision: str  # "approve", "reject", "escalate"
    reviewer_id: str
    comments: str
    reviewed_at: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['reviewed_at'] = self.reviewed_at.isoformat()
        return data


@dataclass
class HITLAuditEntry:
    """Represents an audit log entry"""
    timestamp: datetime
    checkpoint_id: str
    action: str
    user_id: str
    details: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class HITLPolicyEngine:
    """Core HITL policy engine for managing checkpoints and approvals"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize HITL policy engine"""
        self.config_path = config_path or "config/hitl_policies.yaml"
        self.policies = self._load_policies()
        self.checkpoints: Dict[str, HITLCheckpoint] = {}
        self.audit_log: List[Dict[str, Any]] = []
        
        # Initialize storage directories
        self.storage_dir = Path("storage/hitl")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize notification system
        self.notification_handlers = []
        self._init_notification_handlers()
        
        logger.info(f"HITL Policy Engine initialized with {len(self.policies)} policy groups")
    
    def _load_policies(self) -> Dict[str, Any]:
        """Load HITL policies from configuration file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"HITL policies file not found: {self.config_path}")
            return self._get_default_policies()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing HITL policies: {e}")
            return self._get_default_policies()
    
    def _get_default_policies(self) -> Dict[str, Any]:
        """Get default HITL policies as fallback"""
        return {
            'hitl_policies': {
                'global_settings': {
                    'enabled': True,
                    'default_timeout_hours': 24,
                    'auto_escalation_enabled': True,
                    'notification_channels': ['dashboard']
                },
                'checkpoint_triggers': {
                    'output_evaluation': {
                        'enabled': True,
                        'conditions': ['critical_service_changes'],
                        'required_approvals': 1,
                        'reviewers': ['Technical Lead']
                    }
                }
            }
        }
    
    def _init_notification_handlers(self):
        """Initialize notification handlers"""
        # Dashboard notification handler
        from .notification_handlers import DashboardNotificationHandler
        self.notification_handlers.append(DashboardNotificationHandler())
        
        # Email notification handler (if configured)
        if self.policies.get('hitl_policies', {}).get('integrations', {}).get('notifications', {}).get('email', {}).get('enabled'):
            from .notification_handlers import EmailNotificationHandler
            self.notification_handlers.append(EmailNotificationHandler())
        
        # Slack notification handler (if configured)
        if self.policies.get('hitl_policies', {}).get('integrations', {}).get('notifications', {}).get('slack', {}).get('enabled'):
            from .notification_handlers import SlackNotificationHandler
            self.notification_handlers.append(SlackNotificationHandler())
    
    async def assess_risk(self, task_id: str, task_data: Dict[str, Any], 
                         checkpoint_type: CheckpointType) -> RiskAssessment:
        """Assess risk level for a task and checkpoint type"""
        risk_factors = []
        confidence_score = 0.5  # Base confidence
        risk_level = RiskLevel.LOW
        
        # Get task type from task_id prefix
        task_type = self._get_task_type(task_id)
        task_policies = self.policies.get('hitl_policies', {}).get('task_type_policies', {}).get(task_type, {})
        
        # Check for high-risk patterns in task content
        if 'content' in task_data:
            content = str(task_data['content']).lower()
            
            # Check high-risk patterns
            high_risk_patterns = task_policies.get('risk_assessment', {}).get('high_risk_patterns', [])
            for pattern in high_risk_patterns:
                if pattern.lower() in content:
                    risk_factors.append(f"High-risk pattern detected: {pattern}")
                    risk_level = RiskLevel.HIGH
                    confidence_score += 0.2
            
            # Check medium-risk patterns
            medium_risk_patterns = task_policies.get('risk_assessment', {}).get('medium_risk_patterns', [])
            for pattern in medium_risk_patterns:
                if pattern.lower() in content:
                    risk_factors.append(f"Medium-risk pattern detected: {pattern}")
                    if risk_level == RiskLevel.LOW:
                        risk_level = RiskLevel.MEDIUM
                    confidence_score += 0.1
        
        # Check for critical checkpoint conditions
        checkpoint_config = self.policies.get('hitl_policies', {}).get('checkpoint_triggers', {}).get(checkpoint_type.value, {})
        conditions = checkpoint_config.get('conditions', [])
        
        for condition in conditions:
            if self._check_condition(condition, task_data):
                risk_factors.append(f"Checkpoint condition met: {condition}")
                if 'critical' in condition or 'security' in condition:
                    risk_level = RiskLevel.CRITICAL
                    confidence_score += 0.3
                elif 'high' in condition:
                    risk_level = RiskLevel.HIGH
                    confidence_score += 0.2
        
        # Determine auto-approve eligibility
        auto_approve_threshold = checkpoint_config.get('auto_approve_threshold', 0.9)
        auto_approve_eligible = (
            confidence_score >= auto_approve_threshold and 
            risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM] and
            task_policies.get('auto_approve_enabled', False)
        )
        
        # Generate mitigation suggestions
        mitigation_suggestions = self._generate_mitigation_suggestions(risk_factors, risk_level)
        
        return RiskAssessment(
            risk_level=risk_level,
            confidence_score=min(confidence_score, 1.0),
            risk_factors=risk_factors,
            mitigation_suggestions=mitigation_suggestions,
            auto_approve_eligible=auto_approve_eligible
        )
    
    def _get_task_type(self, task_id: str) -> str:
        """Determine task type from task ID prefix"""
        if task_id.startswith('BE-'):
            return 'backend_tasks'
        elif task_id.startswith('FE-'):
            return 'frontend_tasks'
        elif task_id.startswith('UX-'):
            return 'design_tasks'
        elif task_id.startswith('INFRA-'):
            return 'infrastructure_tasks'
        elif task_id.startswith('QA-'):
            return 'qa_tasks'
        else:
            return 'backend_tasks'  # Default fallback
    
    def _check_condition(self, condition: str, task_data: Dict[str, Any]) -> bool:
        """Check if a specific condition is met"""
        # Implementation for checking various conditions
        condition_checks = {
            'critical_service_changes': self._check_critical_service_changes,
            'schema_modifications': self._check_schema_modifications,
            'security_implications': self._check_security_implications,
            'coverage_below_threshold': self._check_coverage_threshold,
            'performance_regression': self._check_performance_regression,
            'breaking_changes': self._check_breaking_changes,
        }
        
        check_func = condition_checks.get(condition)
        if check_func:
            return check_func(task_data)
        
        # Default: check if condition keyword exists in task data
        task_content = str(task_data).lower()
        return condition.lower().replace('_', ' ') in task_content
    
    def _check_critical_service_changes(self, task_data: Dict[str, Any]) -> bool:
        """Check for critical service changes"""
        critical_patterns = ['api/', 'service/', 'core/', 'database/', 'auth/']
        content = str(task_data.get('content', '')).lower()
        return any(pattern in content for pattern in critical_patterns)
    
    def _check_schema_modifications(self, task_data: Dict[str, Any]) -> bool:
        """Check for database schema modifications"""
        schema_patterns = ['alter table', 'create table', 'drop table', 'add column', 'drop column']
        content = str(task_data.get('content', '')).lower()
        return any(pattern in content for pattern in schema_patterns)
    
    def _check_security_implications(self, task_data: Dict[str, Any]) -> bool:
        """Check for security implications"""
        security_patterns = ['auth', 'password', 'token', 'security', 'permission', 'access control']
        content = str(task_data.get('content', '')).lower()
        return any(pattern in content for pattern in security_patterns)
    
    def _check_coverage_threshold(self, task_data: Dict[str, Any]) -> bool:
        """Check if test coverage is below threshold"""
        coverage = task_data.get('test_coverage', 100)
        threshold = self.policies.get('hitl_policies', {}).get('checkpoint_triggers', {}).get('qa_validation', {}).get('thresholds', {}).get('coverage_minimum', 90)
        return coverage < threshold
    
    def _check_performance_regression(self, task_data: Dict[str, Any]) -> bool:
        """Check for performance regression"""
        regression = task_data.get('performance_regression', 0)        
        threshold = self.policies.get('hitl_policies', {}).get('checkpoint_triggers', {}).get('qa_validation', {}).get('thresholds', {}).get('performance_regression_max', 5)
        return regression > threshold
    
    def _check_breaking_changes(self, task_data: Dict[str, Any]) -> bool:
        """Check for breaking changes"""
        breaking_patterns = ['breaking', 'deprecat', 'remov', 'delet', 'incompatible']
        content = str(task_data.get('content', '')).lower()
        return any(pattern in content for pattern in breaking_patterns)
    
    def _generate_mitigation_suggestions(self, risk_factors: List[str], risk_level: RiskLevel) -> List[str]:
        """Generate mitigation suggestions based on risk factors"""
        suggestions = []
        
        if risk_level == RiskLevel.CRITICAL:
            suggestions.append("Require security team review")
            suggestions.append("Implement staged rollout")
            suggestions.append("Prepare rollback plan")
        
        if any('schema' in factor.lower() for factor in risk_factors):
            suggestions.append("Create database backup before deployment")
            suggestions.append("Test migration on staging environment")
        
        if any('performance' in factor.lower() for factor in risk_factors):
            suggestions.append("Run load testing before deployment")
            suggestions.append("Monitor key performance metrics")
        
        if any('security' in factor.lower() for factor in risk_factors):
            suggestions.append("Conduct security review")
            suggestions.append("Run vulnerability scan")
        
        return suggestions
    
    def create_checkpoint(self, task_id: str, checkpoint_type: str, task_type: str,
                         content: Dict[str, Any], risk_factors: List[str] = None,
                         parent_checkpoint_id: Optional[str] = None) -> HITLCheckpoint:
        """Create a new HITL checkpoint"""
        # Generate unique checkpoint ID
        checkpoint_id = f"hitl_{task_id}_{checkpoint_type}_{uuid.uuid4().hex[:8]}"
        
        # Assess risk level
        if risk_factors is None:
            risk_factors = []
        
        risk_level = self._assess_risk(task_type, risk_factors)        # Check if checkpoint type is enabled
        checkpoint_config = self._normalize_policy_access('checkpoint_triggers', checkpoint_type)
        if not checkpoint_config.get('enabled', True):
            # Auto-approve disabled checkpoint types
            status = CheckpointStatus.APPROVED        
        else:
            # Check for auto-approval conditions
            task_policy = self._normalize_policy_access('task_type_policies', task_type)
            
            # If no policy found with full task type, try simplified version
            if not task_policy:
                simplified_task_type = task_type.replace('_tasks', '')
                task_policy = self._normalize_policy_access('task_type_policies', simplified_task_type)
            
            if (risk_level == RiskLevel.LOW and 
                task_policy.get('auto_approve_low_risk', False)):
                status = CheckpointStatus.APPROVED
            else:
                status = CheckpointStatus.PENDING# Get timeout configuration
        global_settings = self._normalize_policy_access('global_settings')
        timeout_hours = checkpoint_config.get('timeout_hours', 
                                             global_settings.get('default_timeout_hours', 24))
        timeout_at = datetime.now() + timedelta(hours=timeout_hours)
        
        # Get required approvals
        required_approvals = checkpoint_config.get('required_approvers', 1)
        
        # Create checkpoint
        checkpoint = HITLCheckpoint(
            checkpoint_id=checkpoint_id,
            task_id=task_id,
            checkpoint_type=checkpoint_type,
            task_type=task_type,
            content=content,
            risk_level=risk_level,
            status=status,
            created_at=datetime.now(),
            timeout_at=timeout_at,
            risk_factors=risk_factors,
            required_approvals=required_approvals,
            parent_checkpoint_id=parent_checkpoint_id
        )        # Store checkpoint
        self.checkpoints[checkpoint_id] = checkpoint
        self._save_checkpoint(checkpoint)
        
        # Create audit entry
        self._create_audit_entry(checkpoint_id, "created", "system", {
            "checkpoint_type": checkpoint_type,
            "risk_level": risk_level.value,
            "auto_approved": status == CheckpointStatus.APPROVED
        })
        
        # Send notifications if not auto-approved
        if status == CheckpointStatus.PENDING:
            self._send_notification(checkpoint, "checkpoint_created")
        
        logger.info(f"Created checkpoint {checkpoint_id} for task {task_id} with status {status.value}")
        return checkpoint
    
    def _send_notification(self, checkpoint: HITLCheckpoint, notification_type: str):
        """Send notifications for checkpoint events"""
        try:
            # Use existing notification method if available
            self._send_checkpoint_notifications(checkpoint, notification_type)
        except Exception as e:
            # If notification fails, just log and continue
            logger.warning(f"Failed to send notification for checkpoint {checkpoint.id}: {e}")
    
    def _create_review_items(self, task_data: Dict[str, Any], risk_assessment: RiskAssessment, 
                           checkpoint_type: CheckpointType) -> List[Dict[str, Any]]:
        """Create review items for the checkpoint"""
        items = []
        
        # Add risk factors as review items
        for factor in risk_assessment.risk_factors:
            items.append({
                'type': 'risk_factor',
                'description': factor,
                'severity': risk_assessment.risk_level.value,
                'requires_review': True
            })
        
        # Add mitigation suggestions
        for suggestion in risk_assessment.mitigation_suggestions:
            items.append({
                'type': 'mitigation',
                'description': suggestion,
                'severity': 'suggestion',
                'requires_review': False
            })
        
        # Add checkpoint-specific items
        if checkpoint_type == CheckpointType.OUTPUT_EVALUATION:
            if 'code_changes' in task_data:
                items.append({
                    'type': 'code_review',
                    'description': 'Review code changes for quality and security',
                    'severity': 'high',
                    'requires_review': True,
                    'content': task_data['code_changes']
                })
        
        elif checkpoint_type == CheckpointType.QA_VALIDATION:
            if 'test_results' in task_data:
                items.append({
                    'type': 'test_review',
                    'description': 'Review test results and coverage',
                    'severity': 'medium',
                    'requires_review': True,
                    'content': task_data['test_results']
                })
        
        return items
    
    async def approve_checkpoint(self, checkpoint_id: str, reviewer: str, 
                               comments: str = None) -> bool:
        """Approve a checkpoint"""
        checkpoint = self.checkpoints.get(checkpoint_id)
        if not checkpoint:
            logger.error(f"Checkpoint {checkpoint_id} not found")
            return False
        
        if checkpoint.status != CheckpointStatus.PENDING:
            logger.error(f"Checkpoint {checkpoint_id} is not in pending status")
            return False
        
        if reviewer not in checkpoint.assigned_reviewers:
            logger.warning(f"Reviewer {reviewer} not assigned to checkpoint {checkpoint_id}")
        
        # Add approval
        approval = {
            'reviewer': reviewer,
            'timestamp': datetime.now().isoformat(),
            'comments': comments or '',
            'approval_id': uuid.uuid4().hex[:8]
        }
        checkpoint.approvals.append(approval)        # Check if checkpoint is fully approved
        if checkpoint.is_approved:
            checkpoint.status = CheckpointStatus.APPROVED
            checkpoint.resolved_at = datetime.now()
            self._send_checkpoint_notifications(checkpoint, 'approval_granted')
            
            # Update task metadata to mark as human-reviewed
            self._update_task_metadata(checkpoint.task_id, {
                'human_reviewed': True,
                'approved_by': [a['reviewer'] for a in checkpoint.approvals],
                'approval_timestamp': datetime.now().isoformat()        })
        
        # Save checkpoint
        self._save_checkpoint(checkpoint)
        
        # Log audit event
        self._log_audit_event('approval_granted', {
            'checkpoint_id': checkpoint_id,
            'reviewer': reviewer,
            'comments': comments,
            'fully_approved': checkpoint.is_approved
        })
        
        logger.info(f"Checkpoint {checkpoint_id} approved by {reviewer}")
        return True
    
    async def reject_checkpoint(self, checkpoint_id: str, reviewer: str, 
                              reason: str, comments: str = None) -> bool:
        """Reject a checkpoint"""
        checkpoint = self.checkpoints.get(checkpoint_id)
        if not checkpoint:
            logger.error(f"Checkpoint {checkpoint_id} not found")
            return False
        
        if checkpoint.status != CheckpointStatus.PENDING:
            logger.error(f"Checkpoint {checkpoint_id} is not in pending status")
            return False
        
        # Add rejection
        rejection = {
            'reviewer': reviewer,
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'comments': comments or '',
            'rejection_id': uuid.uuid4().hex[:8]
        }
        checkpoint.rejections.append(rejection)
        checkpoint.status = CheckpointStatus.REJECTED
        checkpoint.resolved_at = datetime.now()
        
        # Save checkpoint
        self._save_checkpoint(checkpoint)
        
        # Send notifications
        self._send_checkpoint_notifications(checkpoint, 'approval_rejected')
        
        # Update task metadata
        self._update_task_metadata(checkpoint.task_id, {
            'human_reviewed': True,
            'rejected_by': reviewer,
            'rejection_reason': reason,
            'rejection_timestamp': datetime.now().isoformat(),
            'requires_rework': True
        })
        
        # Log audit event
        self._log_audit_event('approval_rejected', {
            'checkpoint_id': checkpoint_id,
            'reviewer': reviewer,
            'reason': reason,
            'comments': comments
        })
        
        logger.info(f"Checkpoint {checkpoint_id} rejected by {reviewer}: {reason}")
        return True
    
    async def check_timeouts(self) -> List[HITLCheckpoint]:
        """Check for overdue checkpoints and handle timeouts"""
        overdue_checkpoints = []
        
        for checkpoint in self.checkpoints.values():
            if checkpoint.status == CheckpointStatus.PENDING and checkpoint.is_overdue:
                overdue_checkpoints.append(checkpoint)
                
                # Handle timeout based on policy
                if checkpoint.timeout_action == TimeoutAction.AUTO_APPROVE:
                    self._auto_approve_checkpoint(checkpoint)
                elif checkpoint.timeout_action == TimeoutAction.ESCALATE:
                    self._escalate_checkpoint(checkpoint)
                elif checkpoint.timeout_action == TimeoutAction.BLOCK:
                    self._block_checkpoint(checkpoint)
                elif checkpoint.timeout_action == TimeoutAction.NOTIFY_ONLY:
                    self._notify_timeout(checkpoint)
        
        return overdue_checkpoints
    
    def _auto_approve_checkpoint(self, checkpoint: HITLCheckpoint):
        """Auto-approve an overdue checkpoint"""
        checkpoint.status = CheckpointStatus.APPROVED
        checkpoint.approvals.append({
            'reviewer': 'system',
            'timestamp': datetime.now().isoformat(),
            'comments': 'Auto-approved due to timeout',
            'approval_id': 'auto_' + uuid.uuid4().hex[:8]
        })
        
        self._save_checkpoint(checkpoint)
        self._log_audit_event('auto_approved', {
            'checkpoint_id': checkpoint.id,
            'reason': 'timeout'
        })
        
        logger.info(f"Auto-approved checkpoint {checkpoint.id} due to timeout")
    
    def _escalate_checkpoint(self, checkpoint: HITLCheckpoint):
        """Escalate an overdue checkpoint"""
        checkpoint.escalation_level += 1
        checkpoint.status = CheckpointStatus.ESCALATED
        
        # Extend deadline
        extension_hours = 24  # Default extension
        checkpoint.deadline = datetime.now() + timedelta(hours=extension_hours)
        
        # Add escalation reviewers
        escalation_policies = self.policies.get('hitl_policies', {}).get('escalation_policies', {})
        risk_policy = escalation_policies.get(checkpoint.risk_level.value, {})
        
        escalation_levels = risk_policy.get('escalation_levels', [])
        if checkpoint.escalation_level <= len(escalation_levels):
            level_config = escalation_levels[checkpoint.escalation_level - 1]
            additional_reviewers = level_config.get('notify', [])
            checkpoint.assigned_reviewers.extend(additional_reviewers)
        
        self._save_checkpoint(checkpoint)
        self._send_checkpoint_notifications(checkpoint, 'escalation_alert')
        self._log_audit_event('escalated', {
            'checkpoint_id': checkpoint.id,
            'escalation_level': checkpoint.escalation_level
        })
        
        logger.info(f"Escalated checkpoint {checkpoint.id} to level {checkpoint.escalation_level}")
    
    def _block_checkpoint(self, checkpoint: HITLCheckpoint):
        """Block a checkpoint that has timed out"""
        checkpoint.status = CheckpointStatus.TIMEOUT
        
        self._save_checkpoint(checkpoint)
        self._update_task_metadata(checkpoint.task_id, {
            'blocked_by_hitl': True,
            'block_reason': 'Checkpoint timeout without approval',
            'block_timestamp': datetime.now().isoformat()
        })
        
        self._log_audit_event('blocked', {
            'checkpoint_id': checkpoint.id,
            'reason': 'timeout'
        })
        
        logger.info(f"Blocked checkpoint {checkpoint.id} due to timeout")
    
    def _notify_timeout(self, checkpoint: HITLCheckpoint):
        """Send timeout notification without taking action"""
        self._send_checkpoint_notifications(checkpoint, 'timeout_warning')
        self._log_audit_event('timeout_notified', {
            'checkpoint_id': checkpoint.id
        })
        
        logger.info(f"Sent timeout notification for checkpoint {checkpoint.id}")
    
    def _save_checkpoint(self, checkpoint: HITLCheckpoint):
        """Save checkpoint to persistent storage"""
        filepath = self.storage_dir / f"{checkpoint.id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(checkpoint.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _send_checkpoint_notifications(self, checkpoint: HITLCheckpoint, 
                                           notification_type: str):
        """Send notifications for checkpoint events"""
        for handler in self.notification_handlers:
            try:
                handler.send_notification(checkpoint, notification_type)
            except Exception as e:
                logger.error(f"Error sending notification via {handler.__class__.__name__}: {e}")
    
    def _update_task_metadata(self, task_id: str, metadata: Dict[str, Any]):
        """Update task metadata with HITL information"""
        # Implementation depends on task metadata storage system
        metadata_file = Path(f"tasks/{task_id}/metadata.json")
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                existing_metadata = json.load(f)
            
            existing_metadata.update(metadata)
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(existing_metadata, f, indent=2, ensure_ascii=False)
    
    def _log_audit_event(self, event_type: str, data: Dict[str, Any]):
        """Log audit event"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data,
            'event_id': uuid.uuid4().hex
        }
        
        self.audit_log.append(audit_entry)
          # Save to persistent audit log
        audit_file = self.storage_dir / "audit_log.jsonl"
        with open(audit_file, 'a', encoding='utf-8') as f:
            json.dump(audit_entry, f, ensure_ascii=False)
            f.write('\n')
    
    def _create_audit_entry(self, checkpoint_id: str, action: str, 
                                actor: str, metadata: Dict[str, Any]):
        """Create an audit entry for checkpoint actions"""
        audit_entry = {
            'checkpoint_id': checkpoint_id,
            'action': action,
            'user_id': actor,  # Changed from 'actor' to 'user_id' to match HITLAuditEntry
            'timestamp': datetime.now().isoformat(),
            'details': metadata  # Changed from 'metadata' to 'details' to match HITLAuditEntry
        }
        
        # Add to in-memory audit log
        self.audit_log.append(audit_entry)
        
        # Save to audit log file
        audit_file = self.storage_dir / "audit.jsonl"
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry) + '\n')
        
        logger.info(f"Audit entry created: {checkpoint_id} - {action} by {actor}")
    
    def _assess_risk(self, task_type: str, risk_factors: List[str]) -> RiskLevel:
        """Assess risk level based on task type and risk factors"""        
        # Get task type policies - try both formats
        task_policy = self._normalize_policy_access('task_type_policies', task_type)
        
        # If no policy found with full task type, try simplified version
        if not task_policy:
            simplified_task_type = task_type.replace('_tasks', '')
            task_policy = self._normalize_policy_access('task_type_policies', simplified_task_type)
        
        # Check both risk assessment formats
        risk_assessment = task_policy.get('risk_assessment', {})
        risk_patterns = task_policy.get('risk_patterns', {})
        
        # Check for high risk patterns (both formats)
        high_risk_patterns = risk_assessment.get('high_risk_patterns', [])
        high_risk_patterns.extend(risk_patterns.get('high', []))
        for factor in risk_factors:
            if factor in high_risk_patterns:
                return RiskLevel.HIGH
        
        # Check for medium risk patterns (both formats)
        medium_risk_patterns = risk_assessment.get('medium_risk_patterns', [])
        medium_risk_patterns.extend(risk_patterns.get('medium', []))
        for factor in risk_factors:
            if factor in medium_risk_patterns:
                return RiskLevel.MEDIUM
        
        # Check for low risk patterns (both formats)
        low_risk_patterns = risk_assessment.get('low_risk_patterns', [])
        low_risk_patterns.extend(risk_patterns.get('low', []))
        for factor in risk_factors:
            if factor in low_risk_patterns:
                return RiskLevel.LOW
        
        # Default to task type default risk level
        default_risk = task_policy.get('default_risk_level', 'medium')
        return RiskLevel(default_risk)
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[HITLCheckpoint]:
        """Get a checkpoint by ID"""
        return self.checkpoints.get(checkpoint_id)
    
    def get_pending_checkpoints(self, task_id: str = None) -> List[HITLCheckpoint]:
        """Get all pending checkpoints, optionally filtered by task_id"""
        pending = [cp for cp in self.checkpoints.values() if cp.status == CheckpointStatus.PENDING]
        if task_id:
            return [cp for cp in pending if cp.task_id == task_id]
        return pending
    
    def get_pending_checkpoints_for_task(self, task_id: str) -> List[HITLCheckpoint]:
        """Get pending checkpoints for a specific task"""
        return [cp for cp in self.checkpoints.values() 
                if cp.task_id == task_id and cp.status == CheckpointStatus.PENDING]
    
    def get_checkpoints_for_task(self, task_id: str) -> List[HITLCheckpoint]:
        """Get all checkpoints for a specific task"""
        return [cp for cp in self.checkpoints.values() if cp.task_id == task_id]
    
    async def process_decision(self, decision_or_checkpoint_id, decision_data=None) -> bool:
        """Process a review decision
        
        Args:
            decision_or_checkpoint_id: Either HITLReviewDecision object or checkpoint_id string
            decision_data: If first arg is checkpoint_id, this should be the decision dict
        
        Returns:
            bool: True if decision processed successfully
        """
        try:
            # Support both calling patterns
            if isinstance(decision_or_checkpoint_id, HITLReviewDecision):
                # Original pattern: process_decision(HITLReviewDecision)
                decision = decision_or_checkpoint_id
            elif decision_data is not None:
                # CLI pattern: process_decision(checkpoint_id, decision_dict)
                checkpoint_id = decision_or_checkpoint_id
                decision = HITLReviewDecision(
                    checkpoint_id=checkpoint_id,
                    decision=decision_data.get('decision'),
                    reviewer_id=decision_data.get('reviewer'),
                    comments=decision_data.get('comments', ''),
                    reviewed_at=datetime.fromisoformat(decision_data.get('timestamp', datetime.now().isoformat()))
                )
            else:
                logger.error("Invalid arguments to process_decision")
                return False
            
            checkpoint = self.checkpoints.get(decision.checkpoint_id)
            if not checkpoint:
                logger.error(f"Checkpoint not found: {decision.checkpoint_id}")
                return False
            
            if decision.decision == "approve" or decision.decision == "approved":
                checkpoint.approvals.append(decision.to_dict())
                if len(checkpoint.approvals) >= checkpoint.required_approvals:
                    checkpoint.status = CheckpointStatus.APPROVED
                    self._create_audit_entry(checkpoint.checkpoint_id, "approved", 
                                           decision.reviewer_id, {"comments": decision.comments})
            
            elif decision.decision == "reject" or decision.decision == "rejected":
                checkpoint.rejections.append(decision.to_dict())
                checkpoint.status = CheckpointStatus.REJECTED
                self._create_audit_entry(checkpoint.checkpoint_id, "rejected", 
                                       decision.reviewer_id, {"comments": decision.comments})
            
            elif decision.decision == "escalate" or decision.decision == "escalated":
                checkpoint.status = CheckpointStatus.ESCALATED
                checkpoint.escalation_level += 1
                self._create_audit_entry(checkpoint.checkpoint_id, "escalated", 
                                       decision.reviewer_id, {"comments": decision.comments})
            
            # Save updated checkpoint
            self._save_checkpoint(checkpoint)
              # Send notifications (if method exists)
            self._send_notification(checkpoint, f"checkpoint_{decision.decision}d")
            
            return True
            
        except Exception as e:
            return False
    
    async def escalate_checkpoint(self, checkpoint_id: str, escalated_by_or_data) -> bool:
        """Escalate a checkpoint
        
        Args:
            checkpoint_id: Checkpoint ID to escalate
            escalated_by_or_data: Either string (escalated_by) or dict (escalation_data)
            
        Returns:
            bool: True if escalation successful
        """
        try:
            checkpoint = self.checkpoints.get(checkpoint_id)
            if not checkpoint:
                return False
            
            # Support both calling patterns
            if isinstance(escalated_by_or_data, str):
                # Original pattern: escalate_checkpoint(checkpoint_id, escalated_by)
                escalated_by = escalated_by_or_data
                reason = "Manual escalation"
                escalation_level_add = 1
            else:
                # CLI pattern: escalate_checkpoint(checkpoint_id, escalation_data)
                escalation_data = escalated_by_or_data
                escalated_by = escalation_data.get('escalated_by', 'system')
                reason = escalation_data.get('reason', 'Manual escalation')
                escalation_level_add = escalation_data.get('escalation_level', 1)
            
            checkpoint.status = CheckpointStatus.ESCALATED
            checkpoint.escalation_level += escalation_level_add
            
            self._create_audit_entry(checkpoint_id, "escalated", escalated_by, {
                "escalation_level": checkpoint.escalation_level,
                "reason": reason
            })
            self._save_checkpoint(checkpoint)
            self._send_notification(checkpoint, "checkpoint_escalated")
            
            return True
        except Exception as e:
            logger.error(f"Error escalating checkpoint: {e}")
            return False
    
    def process_timeouts(self) -> List[HITLCheckpoint]:
        """Process checkpoints that have timed out"""
        timed_out = []
        current_time = datetime.now()
        
        for checkpoint in self.checkpoints.values():
            if (checkpoint.status == CheckpointStatus.PENDING and 
                checkpoint.timeout_at and 
                current_time > checkpoint.timeout_at):
                checkpoint.status = CheckpointStatus.ESCALATED
                checkpoint.escalation_level += 1

                # Create audit entry (non-async version for process_timeouts)
                audit_entry = {
                    'checkpoint_id': checkpoint.checkpoint_id,
                    'action': "timeout_escalated",
                    'actor': "system",
                    'timestamp': datetime.now().isoformat(),
                    'metadata': {"timeout_at": checkpoint.timeout_at.isoformat()}
                }
                
                # Save to audit log file
                audit_file = self.storage_dir / "audit.jsonl"
                with open(audit_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(audit_entry) + '\n')
                
                # Save checkpoint (non-async version)
                filepath = self.storage_dir / f"{checkpoint.checkpoint_id}.json"
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(checkpoint.to_dict(), f, indent=2, ensure_ascii=False)
        return timed_out
    
    def get_audit_trail(self, checkpoint_id: str = None, task_id: str = None) -> List[HITLAuditEntry]:
        """Get audit trail for a checkpoint or task
        
        Args:
            checkpoint_id: Specific checkpoint ID to get audit trail for
            task_id: Task ID to get audit trail for (gets all checkpoints for task)
            
        Returns:
            List of HITLAuditEntry objects
        """
        def _convert_entry(entry):
            """Convert audit log entry to HITLAuditEntry"""
            entry_copy = entry.copy()
            # Convert timestamp string to datetime if needed
            if isinstance(entry_copy.get('timestamp'), str):
                entry_copy['timestamp'] = datetime.fromisoformat(entry_copy['timestamp'])
            return HITLAuditEntry(**entry_copy)
        
        if checkpoint_id:
            # Get audit trail for specific checkpoint
            filtered_entries = [entry for entry in self.audit_log 
                              if entry.get('checkpoint_id') == checkpoint_id]
            entries = [_convert_entry(entry) for entry in filtered_entries]
        elif task_id:
            # Get audit trail for all checkpoints of a task
            task_checkpoint_ids = [cp.checkpoint_id for cp in self.checkpoints.values() 
                                 if cp.task_id == task_id]
            filtered_entries = [entry for entry in self.audit_log 
                              if entry.get('checkpoint_id') in task_checkpoint_ids]
            entries = [_convert_entry(entry) for entry in filtered_entries]
        else:
            # Get all audit entries
            entries = [_convert_entry(entry) for entry in self.audit_log]
        
        return entries
    def get_metrics(self, period_days: int = 30, days: int = None) -> Dict[str, Any]:
        """Get HITL metrics for specified period
        
        Args:
            period_days: Number of days to get metrics for (original parameter)
            days: Number of days to get metrics for (CLI parameter)
            
        Returns:
            Dictionary with metrics data
        """
        # Support both parameter names for compatibility
        if days is not None:
            period = days
        else:
            period = period_days
            
        return self.get_checkpoint_statistics(days=period)
    
    def get_checkpoint_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get checkpoint statistics for the specified number of days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filter checkpoints within the time period
            recent_checkpoints = [
                cp for cp in self.checkpoints.values()
                if cp.created_at >= cutoff_date
            ]
            
            # Calculate statistics
            total_created = len(recent_checkpoints)
            total_resolved = len([cp for cp in recent_checkpoints 
                                if cp.status in [CheckpointStatus.APPROVED, CheckpointStatus.REJECTED]])
            
            approved = [cp for cp in recent_checkpoints if cp.status == CheckpointStatus.APPROVED]
            rejected = [cp for cp in recent_checkpoints if cp.status == CheckpointStatus.REJECTED]
            
            approval_rate = len(approved) / total_resolved if total_resolved > 0 else 0
            
            # Calculate average review time for resolved checkpoints
            resolved_checkpoints = [cp for cp in recent_checkpoints if cp.resolved_at]
            avg_review_time_hours = 0
            if resolved_checkpoints:
                total_hours = sum(
                    (cp.resolved_at - cp.created_at).total_seconds() / 3600
                    for cp in resolved_checkpoints
                )
                avg_review_time_hours = total_hours / len(resolved_checkpoints)
            
            return {
                "total_created": total_created,
                "total_resolved": total_resolved,
                "approval_rate": approval_rate,
                "avg_review_time_hours": avg_review_time_hours,
                "approved_count": len(approved),
                "rejected_count": len(rejected),
                "escalated_count": len([cp for cp in recent_checkpoints if cp.status == CheckpointStatus.ESCALATED]),
                "pending_count": len([cp for cp in recent_checkpoints if cp.status == CheckpointStatus.PENDING])
            }
            
        except Exception as e:
            logger.error(f"Error getting checkpoint statistics: {e}")
            return {
                "total_created": 0,
                "total_resolved": 0,
                "approval_rate": 0,
                "avg_review_time_hours": 0,
                "approved_count": 0,
                "rejected_count": 0,
                "escalated_count": 0,
                "pending_count": 0
            }
    
    def get_daily_trends(self, days: int = 30) -> Dict[str, List]:
        """Get daily trends for checkpoints over the specified period."""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Generate date range
            dates = []
            created_counts = []
            resolved_counts = []
            approval_rates = []
            
            for i in range(days):
                day = start_date + timedelta(days=i)
                day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                
                # Count checkpoints created on this day
                created_on_day = [
                    cp for cp in self.checkpoints.values()
                    if day_start <= cp.created_at < day_end
                ]
                
                # Count checkpoints resolved on this day
                resolved_on_day = [
                    cp for cp in self.checkpoints.values()
                    if (cp.resolved_at and day_start <= cp.resolved_at < day_end)
                ]
                
                # Calculate approval rate for the day
                if resolved_on_day:
                    approved_on_day = [cp for cp in resolved_on_day if cp.status == CheckpointStatus.APPROVED]
                    approval_rate = len(approved_on_day) / len(resolved_on_day)
                else:
                    approval_rate = 0
                
                dates.append(day.strftime("%Y-%m-%d"))
                created_counts.append(len(created_on_day))
                resolved_counts.append(len(resolved_on_day))
                approval_rates.append(approval_rate)
            
            # Also include overall counts for pie charts
            all_checkpoints = list(self.checkpoints.values())
            approved_total = len([cp for cp in all_checkpoints if cp.status == CheckpointStatus.APPROVED])
            rejected_total = len([cp for cp in all_checkpoints if cp.status == CheckpointStatus.REJECTED])
            escalated_total = len([cp for cp in all_checkpoints if cp.status == CheckpointStatus.ESCALATED])
            
            return {
                "dates": dates,
                "created_counts": created_counts,
                "resolved_counts": resolved_counts,
                "approval_rates": approval_rates,
                "approved_count": approved_total,
                "rejected_count": rejected_total,
                "escalated_count": escalated_total
            }
            
        except Exception as e:
            logger.error(f"Error getting daily trends: {e}")
            return {
                "dates": [],
                "created_counts": [],
                "resolved_counts": [],
                "approval_rates": [],
                "approved_count": 0,
                "rejected_count": 0,
                "escalated_count": 0
            }
    
    def get_checkpoint_distribution(self) -> Dict[str, int]:
        """Get distribution of checkpoints by type and risk level."""
        try:
            distribution = {}
            
            for checkpoint in self.checkpoints.values():
                # By checkpoint type
                type_key = f"type_{checkpoint.checkpoint_type}"
                distribution[type_key] = distribution.get(type_key, 0) + 1
                
                # By risk level
                risk_key = f"risk_{checkpoint.risk_level}"
                distribution[risk_key] = distribution.get(risk_key, 0) + 1
                
                # By status
                status_key = f"status_{checkpoint.status}"
                distribution[status_key] = distribution.get(status_key, 0) + 1
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error getting checkpoint distribution: {e}")
            return {}
    
    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get active workflows with HITL checkpoints."""
        try:
            # Group checkpoints by task_id to simulate workflows
            workflows = {}
            
            for checkpoint in self.checkpoints.values():
                task_id = checkpoint.task_id
                if task_id not in workflows:
                    workflows[task_id] = {
                        "workflow_id": f"workflow_{task_id}",
                        "task_id": task_id,
                        "current_phase": "implementation",  # Default phase
                        "task_type": checkpoint.task_type,
                        "hitl_checkpoints": [],
                        "blocked_on_review": False,
                        "progress_percentage": 50,  # Default progress
                        "estimated_completion": (datetime.now() + timedelta(days=2)).isoformat(),
                        "risk_level": "medium"  # Default risk
                    }
                
                workflows[task_id]["hitl_checkpoints"].append(checkpoint.checkpoint_id)
                
                # Update workflow status based on checkpoints
                if checkpoint.status == CheckpointStatus.PENDING:
                    workflows[task_id]["blocked_on_review"] = True
                
                # Use highest risk level from checkpoints
                if checkpoint.risk_level == "high":
                    workflows[task_id]["risk_level"] = "high"
                elif checkpoint.risk_level == "medium" and workflows[task_id]["risk_level"] != "high":
                    workflows[task_id]["risk_level"] = "medium"
            
            return list(workflows.values())
            
        except Exception as e:
            logger.error(f"Error getting active workflows: {e}")
            return []
      
    def _get_escalation_policy(self, risk_level: RiskLevel) -> Dict[str, Any]:
        """Get escalation policy for a given risk level"""
        try:
            escalation_policies = self._normalize_policy_access('escalation_policies')
            
            # Convert risk_level to string if it's an enum
            risk_key = risk_level.value if hasattr(risk_level, 'value') else str(risk_level)
            
            # Try different key formats: 'high', 'high_risk'
            policy = escalation_policies.get(risk_key, {})
            if not policy:
                policy = escalation_policies.get(f"{risk_key}_risk", {})
            
            # Provide default escalation policy if not configured
            if not policy:
                default_policies = {
                    'high': {
                        'escalation_levels': [
                            {'level': 1, 'notify': ['team_lead'], 'timeout_hours': 2},
                            {'level': 2, 'notify': ['technical_director'], 'timeout_hours': 4},
                            {'level': 3, 'notify': ['cto'], 'timeout_hours': 8}
                        ],
                        'notification_channels': ['email', 'slack'],
                        'auto_escalate': True
                    },
                    'medium': {
                        'escalation_levels': [
                            {'level': 1, 'notify': ['team_lead'], 'timeout_hours': 4},
                            {'level': 2, 'notify': ['technical_director'], 'timeout_hours': 8}
                        ],
                        'notification_channels': ['email', 'slack'],
                        'auto_escalate': True
                    },
                    'low': {
                        'escalation_levels': [
                            {'level': 1, 'notify': ['team_lead'], 'timeout_hours': 8}
                        ],
                        'notification_channels': ['email'],
                        'auto_escalate': False
                    }
                }
                policy = default_policies.get(risk_key, default_policies['medium'])
            
            return policy
            
        except Exception as e:
            logger.error(f"Error getting escalation policy for risk level {risk_level}: {e}")
            return {
                'escalation_levels': [{'level': 1, 'notify': ['team_lead'], 'timeout_hours': 4}],
                'notification_channels': ['email'],
                'auto_escalate': False
            }
    
    def _normalize_policy_access(self, *keys):
        """Helper method to access policies with fallback for both config formats"""
        # First try with hitl_policies wrapper (production format)
        result = self.policies
        try:
            for key in ['hitl_policies'] + list(keys):
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

# Factory function for creating HITL engine
def create_hitl_engine(config_path: Optional[str] = None) -> HITLPolicyEngine:
    """Create and return HITL policy engine instance"""
    return HITLPolicyEngine(config_path)


# Integration helper functions
async def create_hitl_checkpoint_for_task(task_id: str, checkpoint_type: str, 
                                        task_data: Dict[str, Any], 
                                        trigger_conditions: List[str] = None) -> Optional[HITLCheckpoint]:
    """Helper function to create HITL checkpoint for a task"""
    engine = create_hitl_engine()
    
    try:
        checkpoint_type_enum = CheckpointType(checkpoint_type)
        return engine.create_checkpoint(task_id, checkpoint_type_enum, task_data, trigger_conditions)
    except ValueError:
        logger.error(f"Invalid checkpoint type: {checkpoint_type}")
        return None
    except Exception as e:
        logger.error(f"Error creating HITL checkpoint: {e}")
        return None


async def check_hitl_approval_required(task_id: str, task_data: Dict[str, Any]) -> bool:
    """Check if HITL approval is required for a task"""
    engine = create_hitl_engine()
    
    # Check all checkpoint types
    for checkpoint_type in CheckpointType:
        risk_assessment = engine.assess_risk(task_id, task_data, checkpoint_type)
        
        if (risk_assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] or 
            not risk_assessment.auto_approve_eligible):
            return True
    
    return False


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        engine = create_hitl_engine()
        
        # Example task data
        task_data = {
            'content': 'ALTER TABLE users ADD COLUMN sensitive_data VARCHAR(255)',
            'test_coverage': 85,
            'performance_regression': 3
        }
        
        # Create checkpoint
        checkpoint = engine.create_checkpoint(
            'BE-123',
            CheckpointType.OUTPUT_EVALUATION,
            task_data,
            ['schema_modifications']
        )
        
        print(f"Created checkpoint: {checkpoint.id}")
        print(f"Risk level: {checkpoint.risk_level}")
        print(f"Deadline: {checkpoint.deadline}")
        
        # Get metrics
        metrics = engine.get_checkpoint_metrics()
        print(f"Metrics: {metrics}")
    
    asyncio.run(main())
