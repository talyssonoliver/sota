"""
HITL Engine Types

Enumerations and type definitions for the HITL system.
"""

from enum import Enum


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
