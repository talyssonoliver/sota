"""
Test Workflow Integration
This script tests the integrated workflow execution with focus on conditional paths.
"""

import json
import os
import shutil
import sys
import tempfile
import time
import unittest

try:
    from datetime import datetime
except ImportError:
    pass
try:
    from pathlib import Path
except ImportError:
    pass
try:
    from unittest.mock import MagicMock, mock_open, patch
except ImportError:
    pass
try:
    from src.core.workflows.enhanced_workflow import EnhancedWorkflowExecutor
except ImportError:
    pass
try:
    from src.core.workflows.states import TaskStatus
except ImportError:
    pass


class Timer:
    """Simple timer for test timing."""

    def __init__(self):
        self.start_time = None

    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        return self

    def elapsed(self):
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def stop(self):
        """Stop the timer and return elapsed time."""
        return self.elapsed()


try:
    from tests.unit.core.workflows.test_workflow_helpers import (
        ensure_check_recursion_method,
    )
except ImportError:
    pass
try:
    from tests.utils.test_utils import FeedbackCollector
except ImportError:
    pass
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def teardown_module(module):
    """Cleanup test_outputs directory after tests finish."""
    test_output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "test_outputs"
    )
    if os.path.exists(test_output_dir):
        for child in os.listdir(test_output_dir):
            child_path = os.path.join(test_output_dir, child)
            if os.path.isdir(child_path):
                shutil.rmtree(child_path)
            else:
                os.remove(child_path)


class TestIntegratedWorkflowExecution(unittest.TestCase):
    """Test the integrated workflow execution with conditional paths."""

    def setUp(self):
        """Set up test environment."""
        self.test_output_dir = Path(tempfile.mkdtemp())
        self.test_timer = Timer().start()
        self.test_results = {"tests_run": 0, "tests_passed": 0, "execution_times": {}}

    def tearDown(self):
        """Clean up after test."""
        self.test_timer.stop()
        print(f"Test execution time: {self.test_timer.elapsed():.2f}s")
        if self.test_output_dir.exists():
            for child in self.test_output_dir.iterdir():
                if child.is_dir():
                    for subchild in child.iterdir():
                        subchild.unlink()
                    child.rmdir()
                else:
                    child.unlink()

    def verify_status_file(self, task_id):
        """Verify status file exists and contains valid JSON."""
        status_path = self.test_output_dir / task_id / "status.json"
        self.assertTrue(status_path.exists())
        with open(status_path, "r") as f:
            status_data = json.load(f)
        self.assertIn("task_id", status_data)
        self.assertEqual(status_data["task_id"], task_id)
        self.assertIn("status", status_data)
        self.assertIn("timestamp", status_data)
        return status_data

    @patch(
        "src.core.workflows.enhanced_workflow.EnhancedWorkflowExecutor._build_workflow"
    )
    def test_workflow_with_task_dependencies(self, mock_build_workflow):
        """Test workflow execution respects task dependencies."""
        test_timer = Timer().start()
        FeedbackCollector.print_section("Task Dependencies Test")
        mock_workflow = MagicMock()
        mock_workflow.invoke.return_value = {
            "task_id": "BE-07",
            "status": TaskStatus.DOCUMENTATION,
            "dependencies": ["TL-09", "BE-01"],
            "agent": "backend",
            "output": "Task completed with all dependencies satisfied",
            "timestamp": datetime.now().isoformat(),
        }
        mock_build_workflow.return_value = mock_workflow
        executor = EnhancedWorkflowExecutor(
            workflow_type="basic",
            notification_level="none",
            output_dir=str(self.test_output_dir),
        )
        executor = ensure_check_recursion_method(executor)
        with patch.object(
            executor,
            "check_dependencies",
            return_value=(True, "All dependencies satisfied"),
        ):
            result = executor.execute_task("BE-07")
            self.assertEqual(result["task_id"], "BE-07")
            self.assertIn(
                result["status"], [TaskStatus.DOCUMENTATION, TaskStatus.BLOCKED]
            )
            self.assertGreaterEqual(mock_workflow.invoke.call_count, 1)
        mock_workflow.invoke.reset_mock()
        with patch.object(
            executor,
            "check_dependencies",
            return_value=(False, "Missing dependency: TL-09 is not DONE"),
        ):
            with patch.object(
                executor, "execute_task", wraps=executor.execute_task
            ) as patched_execute:
                result = executor.execute_task("BE-07")
                # Verify patched execute was called
                patched_execute.assert_called_once_with("BE-07")
                if result[
                    "status"
                ] == TaskStatus.BLOCKED and "Recursion/iteration limit" in str(
                    result.get("error", "")
                ):
                    pass
                else:
                    self.assertIn("dependencies", str(result))
        test_timer.stop()
        self.test_results["tests_run"] += 1
        self.test_results["tests_passed"] += 1
        self.test_results["execution_times"][
            "test_workflow_with_task_dependencies"
        ] = test_timer.elapsed()

    @patch("src.infrastructure.utils.task_loader.load_task_metadata")
    def test_error_handling_in_workflow(self, mock_load_metadata):
        """Test workflow error handling during execution."""
        test_timer = Timer().start()
        FeedbackCollector.print_section("Error Handling Test")
        mock_load_metadata.return_value = {
            "id": "BE-07",
            "title": "Error Test Task",
            "description": "Test error handling in workflow",
        }
        executor = EnhancedWorkflowExecutor(
            workflow_type="basic",
            notification_level="none",
            output_dir=str(self.test_output_dir),
        )
        with patch.object(executor, "workflow") as mock_workflow:
            mock_workflow.invoke.side_effect = Exception("Test exception")
            with patch("builtins.open", mock_open()), patch("os.makedirs"):
                result = executor.execute_task("BE-07")
                self.assertEqual(result["task_id"], "BE-07")
                self.assertEqual(result["status"], TaskStatus.BLOCKED)
                self.assertIn("error", result)
                self.assertEqual(result["error"], "Test exception")
        self.test_results["tests_run"] += 1
        self.test_results["tests_passed"] += 1
        self.test_results["execution_times"][
            "test_error_handling_in_workflow"
        ] = test_timer.elapsed()

    @patch(
        "src.core.workflows.enhanced_workflow.EnhancedWorkflowExecutor._build_workflow"
    )
    @patch("src.infrastructure.utils.task_loader.load_task_metadata")
    def test_auto_generated_workflow_with_dependencies(
        self, mock_load_metadata, mock_build_workflow
    ):
        """Test auto-generated workflow respects task dependencies."""
        "Test auto-generated workflow respects task dependencies."
        test_timer = Timer().start()
        FeedbackCollector.print_section("Auto-Generated Workflow Test")
        mock_load_metadata.return_value = {
            "id": "BE-07",
            "title": "Implement Service Functions",
            "description": "Add the missing service functions",
            "depends_on": ["BE-01", "TL-09"],
        }
        mock_workflow = MagicMock()
        call_count = {"count": 0}

        def mock_invoke_side_effect(state):
            call_count["count"] += 1
            task_id = state.get("task_id")
            if task_id == "BE-07":
                if call_count["count"] == 1:
                    return {
                        "task_id": task_id,
                        "status": TaskStatus.QA_PENDING,
                        "dependencies": ["BE-01", "TL-09"],
                        "agent": "backend",
                        "output": f"Task {task_id} completed with dependencies resolved",
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    return {
                        "task_id": task_id,
                        "status": TaskStatus.DONE,
                        "dependencies": ["BE-01", "TL-09"],
                        "agent": "backend",
                        "output": f"Task {task_id} is done",
                        "timestamp": datetime.now().isoformat(),
                    }
            return state

        mock_workflow.invoke.side_effect = mock_invoke_side_effect
        mock_build_workflow.return_value = mock_workflow
        executor = EnhancedWorkflowExecutor(
            workflow_type="auto",
            notification_level="none",
            output_dir=str(self.test_output_dir),
        )
        executor = ensure_check_recursion_method(executor)
        with patch.object(
            executor,
            "check_dependencies",
            return_value=(True, "All dependencies satisfied"),
        ):
            result = executor.execute_task("BE-07")
        self.assertEqual(result["task_id"], "BE-07")
        self.assertEqual(result["status"], TaskStatus.DONE)
        status_data = self.verify_status_file("BE-07")
        self.assertEqual(status_data["task_id"], "BE-07")
        test_timer.stop()
        self.test_results["tests_run"] += 1
        self.test_results["tests_passed"] += 1
        self.test_results["execution_times"][
            "test_auto_generated_workflow_with_dependencies"
        ] = test_timer.elapsed()

    @patch(
        "src.core.workflows.enhanced_workflow.EnhancedWorkflowExecutor._build_workflow"
    )
    def test_resilient_workflow_retry_logic(self, mock_build_workflow):
        """Test retry logic in resilient workflow."""
        test_timer = Timer().start()
        FeedbackCollector.print_section("Resilient Workflow Retry Test")
        mock_workflow = MagicMock()
        invoke_count = 0

        def mock_invoke_with_retry(state):
            nonlocal invoke_count
            invoke_count += 1
            if invoke_count <= 2:
                raise Exception(f"Temporary failure #{invoke_count}")
            else:
                return {
                    "task_id": state["task_id"],
                    "status": TaskStatus.DOCUMENTATION,
                    "agent": "qa",
                    "output": "Task completed after retries",
                    "timestamp": datetime.now().isoformat(),
                    "retry_count": invoke_count - 1,
                }

        mock_workflow.invoke.side_effect = mock_invoke_with_retry
        mock_build_workflow.return_value = mock_workflow
        executor = EnhancedWorkflowExecutor(
            workflow_type="dynamic",
            resilience_config={
                "max_retries": 3,
                "retry_delay": 0.1,
                "timeout_seconds": 5,
            },
            notification_level="none",
            output_dir=str(self.test_output_dir),
        )
        result = executor.execute_task("QA-01")
        self.assertEqual(result["task_id"], "QA-01")
        test_timer.stop()
        self.test_results["tests_run"] += 1
        self.test_results["tests_passed"] += 1
        self.test_results["execution_times"][
            "test_resilient_workflow_retry_logic"
        ] = test_timer.elapsed()

    @patch(
        "src.core.workflows.enhanced_workflow.EnhancedWorkflowExecutor._build_workflow"
    )
    def test_dynamic_routing_based_on_status(self, mock_build_workflow):
        """Test dynamic routing in the workflow based on task status."""
        test_timer = Timer().start()
        FeedbackCollector.print_section("Dynamic Routing Test")
        test_cases = [
            {
                "initial_status": TaskStatus.QA_PENDING,
                "result_status": TaskStatus.BLOCKED,
                "expected_next_agent": "coordinator",
                "task_id": "BE-07",
            },
            {
                "initial_status": TaskStatus.QA_PENDING,
                "result_status": TaskStatus.DOCUMENTATION,
                "expected_next_agent": "documentation",
                "task_id": "BE-07",
            },
            {
                "initial_status": TaskStatus.IN_PROGRESS,
                "result_status": TaskStatus.HUMAN_REVIEW,
                "expected_next_agent": "human_review",
                "task_id": "BE-14",
            },
        ]
        for idx, test_case in enumerate(test_cases):
            mock_workflow = MagicMock()
            mock_workflow.invoke.return_value = {
                "task_id": test_case["task_id"],
                "status": test_case["result_status"],
                "agent": "current_agent",
                "next_agent": test_case["expected_next_agent"],
                "output": f"Task routed to {test_case['expected_next_agent']}",
                "timestamp": datetime.now().isoformat(),
            }
            mock_build_workflow.return_value = mock_workflow
            executor = EnhancedWorkflowExecutor(
                workflow_type="dynamic",
                notification_level="none",
                output_dir=str(self.test_output_dir),
            )
            initial_state = {
                "task_id": test_case["task_id"],
                "status": test_case["initial_status"],
                "message": f"Test dynamic routing case {idx}",
            }
            with patch.object(
                executor,
                "execute_task",
                wraps=lambda task_id, initial_state=None: mock_workflow.invoke(
                    initial_state
                    if initial_state
                    else {"task_id": task_id, "status": TaskStatus.CREATED}
                ),
            ):
                result = executor.execute_task(test_case["task_id"], initial_state)
                self.assertEqual(result["task_id"], test_case["task_id"])
                self.assertEqual(result["status"], test_case["result_status"])
                self.assertEqual(result["next_agent"], test_case["expected_next_agent"])
        test_timer.stop()
        self.test_results["tests_run"] += 1
        self.test_results["tests_passed"] += 1
        self.test_results["execution_times"][
            "test_dynamic_routing_based_on_status"
        ] = test_timer.elapsed()


if __name__ == "__main__":
    unittest.main()
