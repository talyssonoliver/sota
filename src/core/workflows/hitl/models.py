"""
HITL Engine Models

Data classes and model definitions for the HITL system.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .types import CheckpointStatus, RiskLevel


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
    risk_factors: List[str] = field(default_factory=list)
    required_approvals: int = 1
    assigned_reviewers: List[str] = field(default_factory=list)
    approvals: List[Dict[str, Any]] = field(default_factory=list)
    rejections: List[Dict[str, Any]] = field(default_factory=list)
    escalation_level: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_checkpoint_id: Optional[str] = None
    description: str = ""
    mitigation_suggestions: List[str] = field(default_factory=list)
    timeout_action: Optional[str] = None

    def __post_init__(self):
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
        context_info.update(
            {
                "task_type": self.task_type,
                "description": self.description,
                "risk_factors": self.risk_factors,
                "checkpoint_type": self.checkpoint_type,
            }
        )
        return context_info

    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary"""
        return {
            "checkpoint_id": self.checkpoint_id,
            "task_id": self.task_id,
            "checkpoint_type": self.checkpoint_type,
            "task_type": self.task_type,
            "content": self.content,
            "risk_level": self.risk_level.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "timeout_at": self.timeout_at.isoformat() if self.timeout_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "risk_factors": self.risk_factors,
            "required_approvals": self.required_approvals,
            "assigned_reviewers": self.assigned_reviewers,
            "approvals": self.approvals,
            "rejections": self.rejections,
            "escalation_level": self.escalation_level,
            "metadata": self.metadata,
            "parent_checkpoint_id": self.parent_checkpoint_id,
            "description": self.description,
            "mitigation_suggestions": self.mitigation_suggestions,
            "deadline": self.timeout_at.isoformat() if self.timeout_at else None,
            "reviewers": self.assigned_reviewers or [],
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
        data["risk_level"] = self.risk_level.value
        return data


@dataclass
class HITLReviewDecision:
    """Represents a review decision for a checkpoint"""

    checkpoint_id: str
    decision: str  # "approve", "reject", "escalate"
    reviewer_id: str
    comments: str
    reviewed_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["reviewed_at"] = self.reviewed_at.isoformat()
        return data


@dataclass
class HITLAuditEntry:
    """Represents an audit log entry"""

    timestamp: datetime
    checkpoint_id: str
    action: str
    user_id: str
    details: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
