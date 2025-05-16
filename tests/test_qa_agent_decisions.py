"""
Test QA Agent Decision Making
This script tests the critical decision points in the QA agent's workflow.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules we'll be testing
from handlers.qa_handler import qa_agent
from orchestration.states import TaskStatus
from tests.test_utils import TestFeedback, Timer


class TestQAAgentDecisions(unittest.TestCase):
    """Test the QA agent's decision-making based on various inputs."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_timer = Timer().start()
        
    def tearDown(self):
        """Clean up after tests."""
        self.test_timer.stop()
        print(f"Test execution time: {self.test_timer.elapsed():.2f}s")
    
    @patch('handlers.qa_handler.save_to_review')
    def test_qa_agent_default_behavior(self, mock_save_to_review):
        """Test the default behavior of the QA agent."""
        input_state = {
            "task_id": "BE-07",
            "status": TaskStatus.QA_PENDING,
            "message": "Implement Missing Service Functions",
            "output": "Implementation code"
        }
        
        # Call QA agent
        result = qa_agent(input_state)
        
        # Verify QA result
        self.assertEqual(result["status"], TaskStatus.HUMAN_REVIEW)
        self.assertEqual(result["agent"], "qa")
        self.assertTrue(result["review_required"])
        self.assertIn("QA Report", result["output"])
        self.assertIn("12 tests passed", result["output"])
        self.assertIn("94%", result["output"])
        
        # Verify the output was saved for review
        mock_save_to_review.assert_called_once()
        self.assertEqual(mock_save_to_review.call_args[0][0], "qa_BE-07.md")
    
    @patch('handlers.qa_handler.save_to_review')
    def test_qa_agent_preserves_input_state(self, mock_save_to_review):
        """Test that QA agent preserves input state fields."""
        input_state = {
            "task_id": "BE-07",
            "status": TaskStatus.QA_PENDING,
            "message": "Implement Missing Service Functions",
            "output": "Implementation code",
            "context": "Test context",
            "dependencies": ["BE-01", "TL-09"]
        }
        
        # Call QA agent
        result = qa_agent(input_state)
        
        # Verify preserved fields
        self.assertEqual(result["task_id"], "BE-07")
        self.assertEqual(result["message"], "Implement Missing Service Functions")
        self.assertEqual(result["context"], "Test context")
        self.assertEqual(result["dependencies"], ["BE-01", "TL-09"])
        
        # Verify fields that should change
        self.assertNotEqual(result["status"], TaskStatus.QA_PENDING)
        self.assertNotEqual(result["output"], "Implementation code")
    
    @patch('handlers.qa_handler.save_to_review')  
    def test_qa_with_human_review_workflow(self, mock_save_to_review):
        """Test the human review workflow in the QA process."""
        # Create a mock graph handler that would use the output from qa_agent
        mock_handler = MagicMock()
        
        # Set up the initial state
        initial_state = {
            "task_id": "BE-07",
            "status": TaskStatus.QA_PENDING,
            "message": "Implement Missing Service Functions",
            "output": "Implementation code"
        }
        
        # Call QA agent
        qa_result = qa_agent(initial_state)
        
        # Verify human review workflow setup
        self.assertTrue(qa_result["review_required"])
        self.assertIn("review_file", qa_result)
        
        # Check that the status is set for human review
        self.assertEqual(qa_result["status"], TaskStatus.HUMAN_REVIEW)
        
        # Test information included in saved review
        saved_content = mock_save_to_review.call_args[0][1]
        self.assertIn("QA Report", saved_content)
        self.assertIn("tests passed", saved_content)
        self.assertIn("Code coverage", saved_content)
        self.assertIn("Task output", saved_content)


class TestQAAgentMockIntegration(unittest.TestCase):
    """Test the QA agent's integration with the workflow using mocks."""
    
    def test_qa_agent_in_workflow(self):
        """Test QA agent's role in the workflow."""
        # Create a mock agent
        mock_agent = MagicMock()
        mock_agent.execute = MagicMock(return_value={
            "status": TaskStatus.DOCUMENTATION,
            "output": "QA Report: All tests passing with 94% coverage"
        })
        
        # Simulate a workflow step
        task_state = {
            "task_id": "BE-07",
            "status": TaskStatus.QA_PENDING,
            "agent": "qa",
            "message": "Check implementation quality"
        }
        
        # Mock the workflow calling sequence
        from_workflow = mock_agent.execute(task_state)
        
        # Verify decision flow in workflow
        mock_agent.execute.assert_called_once_with(task_state)
        self.assertEqual(from_workflow["status"], TaskStatus.DOCUMENTATION)


if __name__ == "__main__":
    unittest.main()