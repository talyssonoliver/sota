"""
Test suite for QA Agent decisions and workflow integration.
"""

import unittest
from unittest.mock import patch, MagicMock
from orchestration.states import TaskStatus
import shutil
import os

# Test the QA agent's default behavior in the workflow
class TestQAAgentDecisions(unittest.TestCase):
    def test_qa_agent_default_behavior(self):
        from handlers.qa_handler import qa_agent
        # Simulate a state as would be passed in the workflow
        state = {
            "task_id": "BE-07",
            "status": TaskStatus.QA_PENDING,
            "output": "Implementation output for BE-07"
        }
        # Run the QA agent
        result = qa_agent(state)
        # Should move to HUMAN_REVIEW and include review_required
        self.assertEqual(result["status"], TaskStatus.HUMAN_REVIEW)
        self.assertTrue(result["review_required"])
        self.assertIn("review_file", result)
        self.assertEqual(result["agent"], "qa")
        self.assertIn("QA Report", result["output"])

    def test_qa_agent_preserves_input_state(self):
        from handlers.qa_handler import qa_agent
        # Simulate a state with extra fields
        state = {
            "task_id": "BE-08",
            "status": TaskStatus.QA_PENDING,
            "output": "Some output",
            "custom_field": "custom_value"
        }
        result = qa_agent(state)
        # Custom fields should be preserved in the result
        self.assertEqual(result["custom_field"], "custom_value")
        self.assertEqual(result["status"], TaskStatus.HUMAN_REVIEW)

# Test the QA agent in a workflow context with mocks
class TestQAAgentMockIntegration(unittest.TestCase):
    @patch("handlers.qa_handler.save_to_review")
    def test_qa_agent_in_workflow(self, mock_save_to_review):
        from handlers.qa_handler import qa_agent
        state = {
            "task_id": "BE-09",
            "status": TaskStatus.QA_PENDING,
            "output": "Output for BE-09"
        }
        result = qa_agent(state)
        # Ensure the review file is saved
        mock_save_to_review.assert_called_once()
        self.assertEqual(result["status"], TaskStatus.HUMAN_REVIEW)
        self.assertTrue(result["review_required"])
        self.assertIn("review_file", result)
        self.assertEqual(result["agent"], "qa")

def teardown_module(module):
    """Cleanup test_outputs directory after tests finish."""
    test_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_outputs")
    if os.path.exists(test_output_dir):
        for child in os.listdir(test_output_dir):
            child_path = os.path.join(test_output_dir, child)
            if os.path.isdir(child_path):
                shutil.rmtree(child_path)
            else:
                os.remove(child_path)

if __name__ == "__main__":
    unittest.main()
