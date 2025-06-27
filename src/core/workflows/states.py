"""Workflow states module."""

from enum import Enum

class TaskStatus(Enum):
    """Task status enumeration."""
    CREATED = "created"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

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

__all__ = ["TaskStatus", "WorkflowState"]
