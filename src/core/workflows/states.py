"""Workflow states module."""

from enum import Enum

class TaskStatus(Enum):
    """Task status enumeration."""

    CREATED = "CREATED"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"
    DONE = "DONE"
    QA_PENDING = "QA_PENDING"
    DOCUMENTATION = "DOCUMENTATION"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    PLANNED = "PLANNED"
    
    def __str__(self):
        """Return just the value string."""
        return self.value
    
    @classmethod
    def from_string(cls, status_str):
        """Convert string to TaskStatus, defaulting to IN_PROGRESS for invalid values."""
        try:
            return cls(status_str)
        except ValueError:
            return cls.IN_PROGRESS


class WorkflowState:
    """Workflow state class."""

    def __init__(self):
        self.status = TaskStatus.CREATED
        self.data = {}

    def update(self, **kwargs):
        """Update state."""
        self.data.update(kwargs)

    def get(self, key, default=None):
        """Get value from state."""
        return self.data.get(key, default)


def get_next_status(current_status, agent_role, is_success=True):
    """
    Get the next status based on current status and agent role.

    Args:
        current_status: Current TaskStatus
        agent_role: Role of the agent that processed the task
        is_success: Whether the processing was successful

    Returns:
        Next TaskStatus
    """
    if not is_success:
        return TaskStatus.BLOCKED

    # Agent-specific transitions
    if current_status == TaskStatus.CREATED:
        if agent_role == "coordinator":
            return TaskStatus.PLANNED
        else:
            return TaskStatus.IN_PROGRESS
    elif current_status == TaskStatus.BLOCKED:
        if agent_role == "coordinator":
            return TaskStatus.PLANNED
        else:
            return TaskStatus.IN_PROGRESS
    elif current_status == TaskStatus.PLANNED:
        if agent_role == "technical":
            return TaskStatus.IN_PROGRESS
        elif agent_role in ["backend", "frontend"]:
            return TaskStatus.QA_PENDING
        else:
            return TaskStatus.IN_PROGRESS
    elif current_status == TaskStatus.IN_PROGRESS:
        if agent_role in ["backend", "frontend"]:
            return TaskStatus.QA_PENDING
        elif agent_role == "qa":
            return TaskStatus.QA_PENDING
        else:
            return TaskStatus.QA_PENDING
    elif current_status == TaskStatus.QA_PENDING:
        if agent_role == "qa":
            return TaskStatus.DOCUMENTATION
        else:
            return TaskStatus.DOCUMENTATION
    elif current_status == TaskStatus.DOCUMENTATION:
        if agent_role == "documentation":
            return TaskStatus.DONE
        else:
            return TaskStatus.COMPLETED
    elif current_status == TaskStatus.COMPLETED:
        return TaskStatus.DONE
    else:
        return current_status


def get_valid_transitions(current_status):
    """
    Get valid status transitions from current status.

    Args:
        current_status: Current TaskStatus

    Returns:
        Dict mapping agent roles to their target status transitions
    """
    transitions = {
        TaskStatus.CREATED: {"coordinator": TaskStatus.PLANNED},
        TaskStatus.PLANNED: {"coordinator": TaskStatus.IN_PROGRESS},
        TaskStatus.IN_PROGRESS: {"qa": TaskStatus.QA_PENDING},
        TaskStatus.QA_PENDING: {"qa": TaskStatus.DOCUMENTATION},
        TaskStatus.DOCUMENTATION: {"documentation": TaskStatus.COMPLETED},
        TaskStatus.COMPLETED: {"coordinator": TaskStatus.DONE},
        TaskStatus.BLOCKED: {"coordinator": TaskStatus.IN_PROGRESS},
        TaskStatus.FAILED: {"coordinator": TaskStatus.IN_PROGRESS},
        TaskStatus.CANCELLED: {},
        TaskStatus.DONE: {},
        TaskStatus.HUMAN_REVIEW: {"coordinator": TaskStatus.IN_PROGRESS},
    }
    return transitions.get(current_status, {})


def is_terminal_status(status):
    """
    Check if a status is terminal (no further transitions possible).
    
    Args:
        status: TaskStatus to check
    
    Returns:
        bool: True if status is terminal
    """
    terminal_statuses = {
        TaskStatus.DONE,
        TaskStatus.BLOCKED, 
        TaskStatus.HUMAN_REVIEW,
        TaskStatus.CANCELLED,
        TaskStatus.FAILED
    }
    return status in terminal_statuses


__all__ = [
    "TaskStatus",
    "WorkflowState",
    "get_next_status",
    "get_valid_transitions",
    "is_terminal_status",
]
