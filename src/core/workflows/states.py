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
    DONE = "done"
    QA_PENDING = "qa_pending"
    DOCUMENTATION = "documentation"
    HUMAN_REVIEW = "human_review"
    PLANNED = "planned"

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
        
    # Simple status progression logic
    if current_status == TaskStatus.CREATED:
        return TaskStatus.IN_PROGRESS
    elif current_status == TaskStatus.IN_PROGRESS:
        if agent_role in ["qa", "QA"]:
            return TaskStatus.QA_PENDING
        else:
            return TaskStatus.QA_PENDING
    elif current_status == TaskStatus.QA_PENDING:
        return TaskStatus.DOCUMENTATION
    elif current_status == TaskStatus.DOCUMENTATION:
        return TaskStatus.COMPLETED
    else:
        return current_status

def get_valid_transitions(current_status):
    """
    Get valid status transitions from current status.
    
    Args:
        current_status: Current TaskStatus
        
    Returns:
        List of valid TaskStatus transitions
    """
    transitions = {
        TaskStatus.CREATED: [TaskStatus.IN_PROGRESS, TaskStatus.PLANNED],
        TaskStatus.PLANNED: [TaskStatus.IN_PROGRESS],
        TaskStatus.IN_PROGRESS: [TaskStatus.QA_PENDING, TaskStatus.COMPLETED, TaskStatus.BLOCKED],
        TaskStatus.QA_PENDING: [TaskStatus.DOCUMENTATION, TaskStatus.IN_PROGRESS, TaskStatus.HUMAN_REVIEW],
        TaskStatus.DOCUMENTATION: [TaskStatus.COMPLETED, TaskStatus.DONE],
        TaskStatus.HUMAN_REVIEW: [TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED],
        TaskStatus.COMPLETED: [TaskStatus.DONE],
        TaskStatus.BLOCKED: [TaskStatus.IN_PROGRESS, TaskStatus.HUMAN_REVIEW],
        TaskStatus.FAILED: [TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED],
        TaskStatus.CANCELLED: [],
        TaskStatus.DONE: []
    }
    return transitions.get(current_status, [])

__all__ = ["TaskStatus", "WorkflowState", "get_next_status", "get_valid_transitions"]
