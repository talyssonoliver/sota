"""
Test suite for QA Agent decisions and workflow integration.
"""

import os
import shutil
import unittest

try:
    from unittest.mock import MagicMock, patch  # noqa: F401
except ImportError:
    pass
try:
    from src.core.workflows.states import TaskStatus
except ImportError:
    pass


class TestQAAgentDecisions(unittest.TestCase):

    def test_qa_agent_default_behavior(self):
        from src.infrastructure.tools.handlers.qa_handler import qa_agent

        state = {
            "task_id": "BE-07",
            "status": TaskStatus.QA_PENDING,
            "output": "Implementation output for BE-07",
        }
        result = qa_agent(state)
        self.assertEqual(result["status"], TaskStatus.HUMAN_REVIEW)
        self.assertTrue(result["review_required"])
        self.assertIn("review_file", result)
        self.assertEqual(result["agent"], "qa")
        self.assertIn("QA Report", result["output"])

    def test_qa_agent_preserves_input_state(self):
        from src.infrastructure.tools.handlers.qa_handler import qa_agent

        state = {
            "task_id": "BE-08",
            "status": TaskStatus.QA_PENDING,
            "output": "Some output",
            "custom_field": "custom_value",
        }
        result = qa_agent(state)
        self.assertEqual(result["custom_field"], "custom_value")
        self.assertEqual(result["status"], TaskStatus.HUMAN_REVIEW)


class TestQAAgentMockIntegration(unittest.TestCase):

    @patch("src.infrastructure.tools.handlers.qa_handler.save_to_review")
    def test_qa_agent_in_workflow(self, mock_save_to_review):
        from src.infrastructure.tools.handlers.qa_handler import qa_agent

        state = {
            "task_id": "BE-09",
            "status": TaskStatus.QA_PENDING,
            "output": "Output for BE-09",
        }
        result = qa_agent(state)
        mock_save_to_review.assert_called_once()
        self.assertEqual(result["status"], TaskStatus.HUMAN_REVIEW)
        self.assertTrue(result["review_required"])
        self.assertIn("review_file", result)
        self.assertEqual(result["agent"], "qa")


def teardown_module(module):
    """Cleanup test_outputs directory after tests finish."""
    test_output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "test_outputs"
    )
    if os.path.exists(test_output_dir):
        try:
            for child in os.listdir(test_output_dir):
                child_path = os.path.join(test_output_dir, child)
                try:
                    if os.path.isdir(child_path):
                        shutil.rmtree(child_path)
                    else:
                        os.remove(child_path)
                except PermissionError:
                    # Retry immediately without sleep - file should be available
                    try:
                        if os.path.isdir(child_path):
                            shutil.rmtree(child_path, ignore_errors=True)
                        else:
                            os.remove(child_path)
                    except PermissionError:
                        pass  # Ignore if still locked
            os.rmdir(test_output_dir)
        except Exception as e:
            print(f"Failed to cleanup test_outputs directory: {e}")


if __name__ == "__main__":
    unittest.main()
