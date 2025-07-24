"""
Real tests for workflow states module.
Tests TaskStatus enum, WorkflowState class, and state transition functions.
"""

import pytest
from src.core.workflows.states import (
    TaskStatus,
    WorkflowState,
    get_next_status,
    get_valid_transitions,
)


class TestTaskStatus:
    """Real tests for TaskStatus enum."""

    def test_task_status_enum_values(self):
        """Test TaskStatus enum has correct string values."""
        assert TaskStatus.CREATED.value == "created"
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.BLOCKED.value == "blocked"
        assert TaskStatus.CANCELLED.value == "cancelled"
        assert TaskStatus.DONE.value == "done"
        assert TaskStatus.QA_PENDING.value == "qa_pending"
        assert TaskStatus.DOCUMENTATION.value == "documentation"
        assert TaskStatus.HUMAN_REVIEW.value == "human_review"
        assert TaskStatus.PLANNED.value == "planned"

    def test_task_status_enum_inheritance(self):
        """Test TaskStatus inherits from Enum and has proper representation."""
        status = TaskStatus.CREATED
        assert isinstance(status, TaskStatus)
        assert status.value == "created"
        assert str(status) == "TaskStatus.CREATED"

    def test_task_status_enum_comparison(self):
        """Test TaskStatus enum comparison."""
        assert TaskStatus.CREATED == TaskStatus.CREATED
        assert TaskStatus.CREATED != TaskStatus.PENDING
        assert TaskStatus.CREATED.value == "created"
        assert TaskStatus.CREATED.value != "pending"

    def test_all_task_statuses_exist(self):
        """Test all expected task statuses are defined."""
        expected_statuses = {
            "CREATED", "PENDING", "IN_PROGRESS", "COMPLETED", "FAILED",
            "BLOCKED", "CANCELLED", "DONE", "QA_PENDING", "DOCUMENTATION",
            "HUMAN_REVIEW", "PLANNED"
        }
        actual_statuses = {status.name for status in TaskStatus}
        assert actual_statuses == expected_statuses


class TestWorkflowState:
    """Real tests for WorkflowState class."""

    def test_workflow_state_initialization(self):
        """Test WorkflowState initialization with default values."""
        state = WorkflowState()
        
        assert state.status == TaskStatus.CREATED
        assert state.data == {}
        assert isinstance(state.data, dict)

    def test_workflow_state_update(self):
        """Test WorkflowState update method."""
        state = WorkflowState()
        
        # Update with single key-value pair
        state.update(task_id="BE-07")
        assert state.data["task_id"] == "BE-07"
        
        # Update with multiple key-value pairs
        state.update(owner="backend", priority="HIGH")
        assert state.data["task_id"] == "BE-07"  # Should preserve existing
        assert state.data["owner"] == "backend"
        assert state.data["priority"] == "HIGH"
        
        # Update existing key
        state.update(priority="MEDIUM")
        assert state.data["priority"] == "MEDIUM"

    def test_workflow_state_get(self):
        """Test WorkflowState get method."""
        state = WorkflowState()
        
        # Test getting non-existent key with default None
        result = state.get("nonexistent")
        assert result is None
        
        # Test getting non-existent key with custom default
        result = state.get("nonexistent", "default_value")
        assert result == "default_value"
        
        # Test getting existing key
        state.update(task_id="FE-123")
        result = state.get("task_id")
        assert result == "FE-123"
        
        # Test getting existing key ignores default
        result = state.get("task_id", "ignored_default")
        assert result == "FE-123"

    def test_workflow_state_status_change(self):
        """Test WorkflowState status can be changed."""
        state = WorkflowState()
        
        # Initial status
        assert state.status == TaskStatus.CREATED
        
        # Change status
        state.status = TaskStatus.IN_PROGRESS
        assert state.status == TaskStatus.IN_PROGRESS
        
        # Change to another status
        state.status = TaskStatus.COMPLETED
        assert state.status == TaskStatus.COMPLETED


class TestGetNextStatus:
    """Real tests for get_next_status function."""

    def test_get_next_status_success_flow(self):
        """Test get_next_status with successful progression."""
        # CREATED -> IN_PROGRESS
        next_status = get_next_status(TaskStatus.CREATED, "backend", is_success=True)
        assert next_status == TaskStatus.IN_PROGRESS
        
        # IN_PROGRESS -> QA_PENDING (for QA agent)
        next_status = get_next_status(TaskStatus.IN_PROGRESS, "qa", is_success=True)
        assert next_status == TaskStatus.QA_PENDING
        
        # IN_PROGRESS -> QA_PENDING (for non-QA agent)
        next_status = get_next_status(TaskStatus.IN_PROGRESS, "backend", is_success=True)
        assert next_status == TaskStatus.QA_PENDING
        
        # QA_PENDING -> DOCUMENTATION
        next_status = get_next_status(TaskStatus.QA_PENDING, "qa", is_success=True)
        assert next_status == TaskStatus.DOCUMENTATION
        
        # DOCUMENTATION -> COMPLETED
        next_status = get_next_status(TaskStatus.DOCUMENTATION, "doc", is_success=True)
        assert next_status == TaskStatus.COMPLETED

    def test_get_next_status_failure_flow(self):
        """Test get_next_status with failure scenarios."""
        # Any status with failure -> BLOCKED
        next_status = get_next_status(TaskStatus.CREATED, "backend", is_success=False)
        assert next_status == TaskStatus.BLOCKED
        
        next_status = get_next_status(TaskStatus.IN_PROGRESS, "qa", is_success=False)
        assert next_status == TaskStatus.BLOCKED
        
        next_status = get_next_status(TaskStatus.QA_PENDING, "doc", is_success=False)
        assert next_status == TaskStatus.BLOCKED

    def test_get_next_status_edge_cases(self):
        """Test get_next_status edge cases."""
        # Unknown status stays the same
        next_status = get_next_status(TaskStatus.DONE, "backend", is_success=True)
        assert next_status == TaskStatus.DONE
        
        next_status = get_next_status(TaskStatus.CANCELLED, "qa", is_success=True)
        assert next_status == TaskStatus.CANCELLED
        
        # QA agent role variations
        next_status = get_next_status(TaskStatus.IN_PROGRESS, "QA", is_success=True)
        assert next_status == TaskStatus.QA_PENDING

    def test_get_next_status_different_agent_roles(self):
        """Test get_next_status with different agent roles."""
        agent_roles = ["backend", "frontend", "technical", "doc", "coordinator"]
        
        for role in agent_roles:
            # All roles follow same progression for most statuses
            next_status = get_next_status(TaskStatus.CREATED, role, is_success=True)
            assert next_status == TaskStatus.IN_PROGRESS
            
            next_status = get_next_status(TaskStatus.IN_PROGRESS, role, is_success=True)
            assert next_status == TaskStatus.QA_PENDING


class TestGetValidTransitions:
    """Real tests for get_valid_transitions function."""

    def test_get_valid_transitions_created(self):
        """Test valid transitions from CREATED status."""
        transitions = get_valid_transitions(TaskStatus.CREATED)
        expected = [TaskStatus.IN_PROGRESS, TaskStatus.PLANNED]
        assert transitions == expected

    def test_get_valid_transitions_planned(self):
        """Test valid transitions from PLANNED status."""
        transitions = get_valid_transitions(TaskStatus.PLANNED)
        expected = [TaskStatus.IN_PROGRESS]
        assert transitions == expected

    def test_get_valid_transitions_in_progress(self):
        """Test valid transitions from IN_PROGRESS status."""
        transitions = get_valid_transitions(TaskStatus.IN_PROGRESS)
        expected = [TaskStatus.QA_PENDING, TaskStatus.COMPLETED, TaskStatus.BLOCKED]
        assert transitions == expected

    def test_get_valid_transitions_qa_pending(self):
        """Test valid transitions from QA_PENDING status."""
        transitions = get_valid_transitions(TaskStatus.QA_PENDING)
        expected = [TaskStatus.DOCUMENTATION, TaskStatus.IN_PROGRESS, TaskStatus.HUMAN_REVIEW]
        assert transitions == expected

    def test_get_valid_transitions_documentation(self):
        """Test valid transitions from DOCUMENTATION status."""
        transitions = get_valid_transitions(TaskStatus.DOCUMENTATION)
        expected = [TaskStatus.COMPLETED, TaskStatus.DONE]
        assert transitions == expected

    def test_get_valid_transitions_human_review(self):
        """Test valid transitions from HUMAN_REVIEW status."""
        transitions = get_valid_transitions(TaskStatus.HUMAN_REVIEW)
        expected = [TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED]
        assert transitions == expected

    def test_get_valid_transitions_completed(self):
        """Test valid transitions from COMPLETED status."""
        transitions = get_valid_transitions(TaskStatus.COMPLETED)
        expected = [TaskStatus.DONE]
        assert transitions == expected

    def test_get_valid_transitions_blocked(self):
        """Test valid transitions from BLOCKED status."""
        transitions = get_valid_transitions(TaskStatus.BLOCKED)
        expected = [TaskStatus.IN_PROGRESS, TaskStatus.HUMAN_REVIEW]
        assert transitions == expected

    def test_get_valid_transitions_failed(self):
        """Test valid transitions from FAILED status."""
        transitions = get_valid_transitions(TaskStatus.FAILED)
        expected = [TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED]
        assert transitions == expected

    def test_get_valid_transitions_terminal_states(self):
        """Test valid transitions from terminal states."""
        # CANCELLED has no valid transitions
        transitions = get_valid_transitions(TaskStatus.CANCELLED)
        assert transitions == []
        
        # DONE has no valid transitions
        transitions = get_valid_transitions(TaskStatus.DONE)
        assert transitions == []

    def test_get_valid_transitions_all_statuses(self):
        """Test get_valid_transitions handles all TaskStatus values."""
        for status in TaskStatus:
            transitions = get_valid_transitions(status)
            # Should always return a list
            assert isinstance(transitions, list)
            # All transition statuses should be valid TaskStatus values
            for transition in transitions:
                assert isinstance(transition, TaskStatus)


class TestWorkflowStateIntegration:
    """Integration tests for workflow state functionality."""

    def test_complete_workflow_progression(self):
        """Test a complete workflow progression using all components."""
        state = WorkflowState()
        
        # Start with CREATED status
        assert state.status == TaskStatus.CREATED
        
        # Add initial task data
        state.update(task_id="BE-07", owner="backend", priority="HIGH")
        
        # Progress through workflow
        state.status = get_next_status(state.status, state.get("owner"), is_success=True)
        assert state.status == TaskStatus.IN_PROGRESS
        
        # Add progress data
        state.update(started_at="2024-01-01T10:00:00")
        
        # Continue progression
        state.status = get_next_status(state.status, "qa", is_success=True)
        assert state.status == TaskStatus.QA_PENDING
        
        state.status = get_next_status(state.status, "qa", is_success=True)
        assert state.status == TaskStatus.DOCUMENTATION
        
        state.status = get_next_status(state.status, "doc", is_success=True)
        assert state.status == TaskStatus.COMPLETED
        
        # Verify final state
        assert state.get("task_id") == "BE-07"
        assert state.get("owner") == "backend"
        assert state.get("priority") == "HIGH"
        assert state.get("started_at") == "2024-01-01T10:00:00"

    def test_workflow_with_failure_recovery(self):
        """Test workflow handling failure and recovery."""
        state = WorkflowState()
        state.update(task_id="FE-123", owner="frontend")
        
        # Normal progression
        state.status = get_next_status(state.status, "frontend", is_success=True)
        assert state.status == TaskStatus.IN_PROGRESS
        
        # Failure occurs
        state.status = get_next_status(state.status, "qa", is_success=False)
        assert state.status == TaskStatus.BLOCKED
        
        # Check valid recovery options
        valid_transitions = get_valid_transitions(state.status)
        assert TaskStatus.IN_PROGRESS in valid_transitions
        assert TaskStatus.HUMAN_REVIEW in valid_transitions
        
        # Recover to IN_PROGRESS
        state.status = TaskStatus.IN_PROGRESS
        state.update(recovery_note="Issue resolved")
        
        # Continue normal flow
        state.status = get_next_status(state.status, "qa", is_success=True)
        assert state.status == TaskStatus.QA_PENDING