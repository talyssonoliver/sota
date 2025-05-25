"""
Task Lifecycle States
Defines the standard states that a task can be in throughout its lifecycle.
"""

from enum import Enum
from typing import Dict, Optional, Set, Union

class TaskStatus(str, Enum):
    """
    Enum for tracking task status through the workflow
    Using string enum allows for serialization in state dictionaries
    """
    CREATED = "CREATED"      # Task is created but not yet started
    PLANNED = "PLANNED"      # Task is planned and ready to be worked on
    IN_PROGRESS = "IN_PROGRESS"  # Task is currently being worked on
    QA_PENDING = "QA_PENDING"    # Task is completed and waiting for QA
    DOCUMENTATION = "DOCUMENTATION"  # Task has passed QA and needs documentation
    HUMAN_REVIEW = "HUMAN_REVIEW"    # Task requires human review before proceeding
    DONE = "DONE"            # Task is completed and passed QA (legacy)
    BLOCKED = "BLOCKED"      # Task is blocked by an issue
    COMPLETED = "COMPLETED"  # Task is fully completed/completed (for compatibility)
    FAILED = "FAILED"        # Task failed
    QA_FAILED = "QA_FAILED"  # Task failed QA
    REVIEW = "REVIEW"        # Task is under review

    def __str__(self):
        return self.value
        
    @classmethod
    def from_string(cls, value: str):
        """Convert a string to the corresponding TaskStatus enum value."""
        try:
            return cls(value)
        except ValueError:
            # Default to IN_PROGRESS if invalid status
            return cls.IN_PROGRESS


def get_next_status(current_status: Union[str, TaskStatus], agent_role: str, success: bool = True) -> TaskStatus:
    """
    Determine the next status for a task based on the current status, 
    the agent role that just executed, and whether execution was successful.
    
    Args:
        current_status: The current status of the task
        agent_role: The role of the agent that executed the task
        success: Whether the agent execution was successful
        
    Returns:
        The next status for the task
    """
    # Convert string to enum if needed
    if isinstance(current_status, str):
        current_status = TaskStatus.from_string(current_status)
        
    if not success:
        return TaskStatus.BLOCKED
    
    # Define allowed transitions per role
    transitions = {
        "coordinator": {
            TaskStatus.CREATED: TaskStatus.PLANNED,
            TaskStatus.BLOCKED: TaskStatus.PLANNED,
            # Default to PLANNED for coordinator
            None: TaskStatus.PLANNED
        },
        "technical": {
            TaskStatus.PLANNED: TaskStatus.IN_PROGRESS,
            # Default to IN_PROGRESS for technical architect
            None: TaskStatus.IN_PROGRESS
        },
        "backend": {
            TaskStatus.IN_PROGRESS: TaskStatus.QA_PENDING,
            TaskStatus.PLANNED: TaskStatus.QA_PENDING,
            # Default to QA_PENDING for backend
            None: TaskStatus.QA_PENDING
        },
        "frontend": {
            TaskStatus.IN_PROGRESS: TaskStatus.QA_PENDING,
            TaskStatus.PLANNED: TaskStatus.QA_PENDING,
            # Default to QA_PENDING for frontend
            None: TaskStatus.QA_PENDING
        },
        "qa": {
            TaskStatus.QA_PENDING: TaskStatus.DOCUMENTATION,
            # Default to DOCUMENTATION for successful QA
            None: TaskStatus.DOCUMENTATION
        },
        "documentation": {
            TaskStatus.DOCUMENTATION: TaskStatus.DONE,
            # Default to DONE for documentation
            None: TaskStatus.DONE
        }
    }
    
    # Get the transitions for this agent role
    role_transitions = transitions.get(agent_role, {})
    
    # Try to get the specific transition, fall back to default for this role,
    # or return the current status if no transition defined
    return role_transitions.get(current_status, role_transitions.get(None, current_status))


def is_terminal_status(status: Union[str, TaskStatus]) -> bool:
    """
    Check if a status is terminal (no further processing needed).
    
    Args:
        status: The status to check
        
    Returns:
        True if the status is terminal, False otherwise
    """
    # Convert string to enum if needed
    if isinstance(status, str):
        status = TaskStatus.from_string(status)
        
    terminal_statuses = {
        TaskStatus.DONE,
        TaskStatus.BLOCKED,
        TaskStatus.HUMAN_REVIEW
    }
    
    return status in terminal_statuses


def get_valid_transitions(current_status: Union[str, TaskStatus]) -> Dict[str, TaskStatus]:
    """
    Get all valid transitions from the current status.
    
    Args:
        current_status: The current status
    
    Returns:
        Dictionary mapping agent roles to possible next statuses
    """
    # Convert string to enum if needed
    if isinstance(current_status, str):
        current_status = TaskStatus.from_string(current_status)
    
    # Define valid transitions for each state
    transitions = {
        TaskStatus.CREATED: {
            "coordinator": TaskStatus.PLANNED
        },
        TaskStatus.PLANNED: {
            "technical": TaskStatus.IN_PROGRESS,
            "backend": TaskStatus.QA_PENDING,
            "frontend": TaskStatus.QA_PENDING
        },
        TaskStatus.IN_PROGRESS: {
            "backend": TaskStatus.QA_PENDING,
            "frontend": TaskStatus.QA_PENDING
        },
        TaskStatus.QA_PENDING: {
            "qa": TaskStatus.DOCUMENTATION
        },
        TaskStatus.DOCUMENTATION: {
            "documentation": TaskStatus.DONE
        },
        TaskStatus.BLOCKED: {
            "coordinator": TaskStatus.PLANNED,
            "human": TaskStatus.HUMAN_REVIEW
        },
        TaskStatus.HUMAN_REVIEW: {
            "human": TaskStatus.PLANNED
        }
    }
    
    return transitions.get(current_status, {})