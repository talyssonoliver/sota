"""
Test Workflow State Transitions
This script tests the critical state transitions in the task workflow.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules we'll be testing
from orchestration.states import (
    TaskStatus,
    get_next_status,
    is_terminal_status,
    get_valid_transitions
)
from graph.handlers import (
    coordinator_handler,
    technical_handler,
    backend_handler,
    frontend_handler,
    qa_handler,
    documentation_handler
)
# Import the qa_agent from the correct module
from handlers.qa_handler import qa_agent

# Import our test utilities
from tests.test_utils import TestFeedback, Timer


class TestTaskStatusTransitions(unittest.TestCase):
    """Test the task status transitions logic."""
    
    def test_task_status_enum_values(self):
        """Test that TaskStatus enum has the expected values."""
        self.assertEqual(TaskStatus.CREATED.value, "CREATED")
        self.assertEqual(TaskStatus.PLANNED.value, "PLANNED")
        self.assertEqual(TaskStatus.IN_PROGRESS.value, "IN_PROGRESS")
        self.assertEqual(TaskStatus.QA_PENDING.value, "QA_PENDING")
        self.assertEqual(TaskStatus.DOCUMENTATION.value, "DOCUMENTATION")
        self.assertEqual(TaskStatus.HUMAN_REVIEW.value, "HUMAN_REVIEW")
        self.assertEqual(TaskStatus.DONE.value, "DONE")
        self.assertEqual(TaskStatus.BLOCKED.value, "BLOCKED")
    
    def test_task_status_string_conversion(self):
        """Test that TaskStatus can be converted to and from strings."""
        self.assertEqual(str(TaskStatus.PLANNED), "PLANNED")
        self.assertEqual(TaskStatus.from_string("QA_PENDING"), TaskStatus.QA_PENDING)
        
        # Test invalid status conversion defaults to IN_PROGRESS
        self.assertEqual(TaskStatus.from_string("INVALID_STATUS"), TaskStatus.IN_PROGRESS)
    
    def test_get_next_status_coordinator(self):
        """Test the next status determination for coordinator agent."""
        self.assertEqual(get_next_status(TaskStatus.CREATED, "coordinator"), TaskStatus.PLANNED)
        self.assertEqual(get_next_status(TaskStatus.BLOCKED, "coordinator"), TaskStatus.PLANNED)
        
        # Test failure case for any status should result in BLOCKED
        self.assertEqual(get_next_status(TaskStatus.CREATED, "coordinator", False), TaskStatus.BLOCKED)
    
    def test_get_next_status_technical(self):
        """Test the next status determination for technical architect agent."""
        self.assertEqual(get_next_status(TaskStatus.PLANNED, "technical"), TaskStatus.IN_PROGRESS)
    
    def test_get_next_status_backend(self):
        """Test the next status determination for backend agent."""
        self.assertEqual(get_next_status(TaskStatus.IN_PROGRESS, "backend"), TaskStatus.QA_PENDING)
        self.assertEqual(get_next_status(TaskStatus.PLANNED, "backend"), TaskStatus.QA_PENDING)
    
    def test_get_next_status_frontend(self):
        """Test the next status determination for frontend agent."""
        self.assertEqual(get_next_status(TaskStatus.IN_PROGRESS, "frontend"), TaskStatus.QA_PENDING)
        self.assertEqual(get_next_status(TaskStatus.PLANNED, "frontend"), TaskStatus.QA_PENDING)
    
    def test_get_next_status_qa(self):
        """Test the next status determination for QA agent."""
        self.assertEqual(get_next_status(TaskStatus.QA_PENDING, "qa"), TaskStatus.DOCUMENTATION)
        
        # Test failure case should result in BLOCKED
        self.assertEqual(get_next_status(TaskStatus.QA_PENDING, "qa", False), TaskStatus.BLOCKED)
    
    def test_get_next_status_documentation(self):
        """Test the next status determination for documentation agent."""
        self.assertEqual(get_next_status(TaskStatus.DOCUMENTATION, "documentation"), TaskStatus.DONE)
    
    def test_is_terminal_status(self):
        """Test identification of terminal statuses."""
        self.assertTrue(is_terminal_status(TaskStatus.DONE))
        self.assertTrue(is_terminal_status(TaskStatus.BLOCKED))
        self.assertTrue(is_terminal_status(TaskStatus.HUMAN_REVIEW))
        
        self.assertFalse(is_terminal_status(TaskStatus.CREATED))
        self.assertFalse(is_terminal_status(TaskStatus.PLANNED))
        self.assertFalse(is_terminal_status(TaskStatus.IN_PROGRESS))
        self.assertFalse(is_terminal_status(TaskStatus.QA_PENDING))
        self.assertFalse(is_terminal_status(TaskStatus.DOCUMENTATION))
    
    def test_get_valid_transitions(self):
        """Test getting valid transitions from a status."""
        # Test transitions from CREATED
        created_transitions = get_valid_transitions(TaskStatus.CREATED)
        self.assertEqual(len(created_transitions), 1)
        self.assertEqual(created_transitions.get("coordinator"), TaskStatus.PLANNED)
        
        # Test transitions from QA_PENDING
        qa_pending_transitions = get_valid_transitions(TaskStatus.QA_PENDING)
        self.assertEqual(len(qa_pending_transitions), 1)
        self.assertEqual(qa_pending_transitions.get("qa"), TaskStatus.DOCUMENTATION)


class TestHandlerStateTransitions(unittest.TestCase):
    """Test the transitions between different handlers in the workflow."""
    
    def test_coordinator_handler_state_transition(self):
        """Test that coordinator handler properly transitions task state."""
        input_state = {
            "task_id": "TL-01",
            "status": TaskStatus.CREATED,
            "message": "Test task"
        }
        
        # Mock the agent instance since we're not testing execution
        with patch('graph.handlers.create_agent_instance') as mock_create_agent:
            mock_agent = MagicMock()
            mock_agent.execute.return_value = {
                "output": "Task planned successfully",
                "task_id": "TL-01"
            }
            mock_create_agent.return_value = mock_agent
            
            # Call the handler
            result = coordinator_handler(input_state)
            
            # Verify state transition
            self.assertEqual(result.get("status"), TaskStatus.PLANNED)
            self.assertEqual(result.get("agent"), "coordinator")
    
    def test_technical_handler_state_transition(self):
        """Test that technical handler properly transitions task state."""
        input_state = {
            "task_id": "TL-01",
            "status": TaskStatus.PLANNED,
            "message": "Test task"
        }
        
        # Mock the agent instance
        with patch('graph.handlers.create_agent_instance') as mock_create_agent:
            mock_agent = MagicMock()
            mock_agent.execute.return_value = {
                "output": "Task implementation started",
                "task_id": "TL-01"
            }
            mock_create_agent.return_value = mock_agent
            
            # Call the handler
            result = technical_handler(input_state)
            
            # Verify state transition
            self.assertEqual(result.get("status"), TaskStatus.IN_PROGRESS)
            self.assertEqual(result.get("agent"), "technical")
    
    def test_backend_handler_state_transition(self):
        """Test that backend handler properly transitions task state."""
        input_state = {
            "task_id": "BE-01",
            "status": TaskStatus.IN_PROGRESS,
            "message": "Test task"
        }
        
        # Mock the agent instance
        with patch('graph.handlers.create_agent_instance') as mock_create_agent:
            mock_agent = MagicMock()
            mock_agent.execute.return_value = {
                "output": "Task implementation completed",
                "task_id": "BE-01"
            }
            mock_create_agent.return_value = mock_agent
            
            # Call the handler
            result = backend_handler(input_state)
            
            # Verify state transition
            self.assertEqual(result.get("status"), TaskStatus.QA_PENDING)
            self.assertEqual(result.get("agent"), "backend")
    
    def test_qa_handler_state_transition_success(self):
        """Test that QA handler properly transitions task state on successful QA."""
        input_state = {
            "task_id": "BE-01",
            "status": TaskStatus.QA_PENDING,
            "message": "Test task",
            "output": "Implementation code"
        }
        
        # Mock the QA agent implementation - Fixed the import path
        with patch('handlers.qa_handler.qa_agent') as mock_qa_agent:
            mock_qa_agent.return_value = {
                "status": TaskStatus.DOCUMENTATION,
                "output": "QA passed with 100% test coverage",
                "task_id": "BE-01",
                "agent": "qa"
            }
            
            # Call the handler
            result = qa_handler(input_state)
            
            # Verify state transition to DOCUMENTATION on success
            self.assertEqual(result.get("status"), TaskStatus.DOCUMENTATION)
            self.assertEqual(result.get("agent"), "qa")
    
    def test_qa_handler_state_transition_failure(self):
        """Test that QA handler properly transitions task state on QA failure."""
        input_state = {
            "task_id": "BE-01",
            "status": TaskStatus.QA_PENDING,
            "message": "Test task",
            "output": "Implementation code with bugs"
        }
        
        # Mock the QA agent implementation to return BLOCKED status - Fixed the import path
        with patch('handlers.qa_handler.qa_agent') as mock_qa_agent:
            mock_qa_agent.return_value = {
                "status": TaskStatus.BLOCKED,
                "output": "QA failed: Found critical bugs",
                "task_id": "BE-01",
                "agent": "qa",
                "error": "Test failures"
            }
            
            # Call the handler
            result = qa_handler(input_state)
            
            # Verify state transition to BLOCKED on failure
            self.assertEqual(result.get("status"), TaskStatus.BLOCKED)
            self.assertEqual(result.get("agent"), "qa")
    
    def test_qa_handler_exception_handling(self):
        """Test that QA handler properly handles exceptions."""
        input_state = {
            "task_id": "BE-01",
            "status": TaskStatus.QA_PENDING,
            "message": "Test task"
        }
        
        # Mock the QA agent implementation to raise an exception - Fixed the import path
        with patch('handlers.qa_handler.qa_agent') as mock_qa_agent:
            mock_qa_agent.side_effect = Exception("QA process failed")
            
            # Call the handler
            result = qa_handler(input_state)
            
            # Verify state transition to BLOCKED on exception
            self.assertEqual(result.get("status"), TaskStatus.BLOCKED)
            self.assertEqual(result.get("agent"), "qa")
            self.assertIn("error", result)
    
    def test_documentation_handler_state_transition(self):
        """Test that documentation handler properly transitions task state."""
        input_state = {
            "task_id": "BE-01",
            "status": TaskStatus.DOCUMENTATION,
            "message": "Test task",
            "output": "Implementation code"
        }
        
        # Mock the agent instance
        with patch('graph.handlers.create_agent_instance') as mock_create_agent:
            mock_agent = MagicMock()
            mock_agent.execute.return_value = {
                "output": "Documentation created successfully",
                "task_id": "BE-01"
            }
            mock_create_agent.return_value = mock_agent
            
            # Call the handler
            result = documentation_handler(input_state)
            
            # Verify state transition
            self.assertEqual(result.get("status"), TaskStatus.DONE)
            self.assertEqual(result.get("agent"), "documentation")


class TestFullWorkflowStateSequence(unittest.TestCase):
    """Test the complete workflow state sequence from CREATED to DONE."""
    
    def test_happy_path_workflow_sequence(self):
        """Test a complete happy path workflow sequence with all state transitions."""
        # Start with a task in CREATED state
        state = {
            "task_id": "BE-07",
            "status": TaskStatus.CREATED,
            "message": "Implement Missing Service Functions"
        }
        
        # Mock agent responses for each handler
        agent_responses = {
            "coordinator": {
                "output": "Task BE-07 has been planned with high priority",
                "task_id": "BE-07"
            },
            "technical": {
                "output": "Technical architecture has been prepared for implementation",
                "task_id": "BE-07"
            },
            "backend": {
                "output": "Service functions implemented with proper error handling",
                "task_id": "BE-07"
            },
            "qa": {
                "status": TaskStatus.DOCUMENTATION,
                "output": "All tests passing with 94% coverage",
                "task_id": "BE-07",
                "agent": "qa"
            },
            "documentation": {
                "output": "API documentation created with examples",
                "task_id": "BE-07"
            }
        }
        
        # Patch all handler dependencies - Fixed the import path
        with patch('graph.handlers.create_agent_instance') as mock_create_agent, \
             patch('handlers.qa_handler.qa_agent') as mock_qa_agent:
            
            # Configure mocks
            mock_agent = MagicMock()
            mock_agent.execute.side_effect = lambda state: agent_responses.get(state.get("agent", ""))
            mock_create_agent.return_value = mock_agent
            mock_qa_agent.return_value = agent_responses["qa"]
            
            # 1. CREATED → PLANNED (via Coordinator)
            state = coordinator_handler(state)
            self.assertEqual(state.get("status"), TaskStatus.PLANNED)
            
            # 2. PLANNED → IN_PROGRESS (via Technical)
            state = technical_handler(state)
            self.assertEqual(state.get("status"), TaskStatus.IN_PROGRESS)
            
            # 3. IN_PROGRESS → QA_PENDING (via Backend)
            state = backend_handler(state)
            self.assertEqual(state.get("status"), TaskStatus.QA_PENDING)
            
            # 4. QA_PENDING → DOCUMENTATION (via QA)
            state = qa_handler(state)
            self.assertEqual(state.get("status"), TaskStatus.DOCUMENTATION)
            
            # 5. DOCUMENTATION → DONE (via Documentation)
            state = documentation_handler(state)
            self.assertEqual(state.get("status"), TaskStatus.DONE)
            
            # Verify final state is marked as DONE
            self.assertEqual(state.get("status"), TaskStatus.DONE)
            self.assertTrue(is_terminal_status(state.get("status")))
    
    def test_qa_failure_workflow_sequence(self):
        """Test a workflow sequence where QA fails and the task becomes blocked."""
        # Start with a task already at QA_PENDING state
        state = {
            "task_id": "BE-07",
            "status": TaskStatus.QA_PENDING,
            "message": "Implement Missing Service Functions",
            "output": "Implementation with bugs"
        }
        
        # Mock QA agent to return BLOCKED status - Fixed the import path
        with patch('handlers.qa_handler.qa_agent') as mock_qa_agent:
            mock_qa_agent.return_value = {
                "status": TaskStatus.BLOCKED,
                "output": "QA failed: Critical bugs in error handling",
                "task_id": "BE-07",
                "agent": "qa",
                "error": "Test failures in error handling scenarios"
            }
            
            # QA_PENDING → BLOCKED (via QA failure)
            state = qa_handler(state)
            self.assertEqual(state.get("status"), TaskStatus.BLOCKED)
            self.assertTrue(is_terminal_status(state.get("status")))
            self.assertIn("error", state)


if __name__ == "__main__":
    unittest.main()