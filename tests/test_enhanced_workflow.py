"""
Test Enhanced Workflow Features
This script tests all PHASE 2 enhancements working together.
"""

import json
import os
import shutil
import sys
import threading
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from graph.notifications import NotificationLevel
from orchestration.enhanced_workflow import EnhancedWorkflowExecutor
from orchestration.states import TaskStatus
from tests.test_utils import TestFeedback, Timer

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Import our test utilities


class TestEnhancedWorkflow(unittest.TestCase):
    """Test cases for enhanced workflow features."""

    def setUp(self):
        """Set up test environment."""
        # Create a test output directory
        from config.build_paths import TEST_OUTPUTS_DIR
        self.test_output_dir = TEST_OUTPUTS_DIR
        os.makedirs(self.test_output_dir, exist_ok=True)

        # Set up a timer for performance tracking
        self.timer = Timer().start()

        # Record test statistics
        self.test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "execution_times": {}
        }

    def tearDown(self):
        """Clean up after tests."""
        # Record test timing
        self.timer.stop()
        print(f"Test execution time: {self.timer.elapsed():.2f}s")
        # Clean up test output directory
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

        # Check file existence
        self.assertTrue(status_path.exists(),
                        f"Status file for {task_id} does not exist")

        # Attempt to read and parse the file
        try:
            with open(status_path, "r") as f:
                status_data = json.load(f)

            # Verify required fields
            self.assertIn("task_id", status_data,
                          "Status file missing task_id field")
            self.assertEqual(
                status_data["task_id"],
                task_id,
                "Task ID in status file doesn't match expected value")
            self.assertIn("timestamp", status_data,
                          "Status file missing timestamp field")

            return status_data
        except json.JSONDecodeError:
            self.fail(f"Status file for {task_id} contains invalid JSON")
            return None

    def test_basic_workflow(self):
        """Test the basic workflow execution."""
        test_timer = Timer().start()
        TestFeedback.print_section("Basic Workflow Test")

        executor = EnhancedWorkflowExecutor(
            workflow_type="basic",
            notification_level=NotificationLevel.NONE,
            output_dir=str(self.test_output_dir)
        )

        # Test with a simple task
        task_id = "TL-01"
        result = executor.execute_task(task_id)

        # Verify the task was executed and files were created
        self.assertEqual(result["task_id"], task_id)
        self.assertTrue(
            (self.test_output_dir / task_id / "status.json").exists())

        # Verify the status file contains valid data
        status_data = self.verify_status_file(task_id)

        # Update test statistics
        test_timer.stop()
        self.test_results["tests_run"] += 1
        self.test_results["tests_passed"] += 1
        self.test_results["execution_times"]["test_basic_workflow"] = test_timer.elapsed(
        )

        print(f"✅ Basic workflow test passed in {test_timer.elapsed():.2f}s")

    def test_auto_generated_workflow(self):
        """Test the auto-generated workflow."""
        test_timer = Timer().start()
        TestFeedback.print_section("Auto-Generated Workflow Test")

        executor = EnhancedWorkflowExecutor(
            workflow_type="auto",
            notification_level=NotificationLevel.NONE,
            output_dir=str(self.test_output_dir)
        )

        # Test with a task
        task_id = "BE-07"
        result = executor.execute_task(task_id)

        # Verify the task was executed
        self.assertEqual(result["task_id"], task_id)
        self.assertTrue(
            (self.test_output_dir / task_id / "status.json").exists())

        # Verify the status file contains valid data
        status_data = self.verify_status_file(task_id)

        # Update test statistics
        test_timer.stop()
        self.test_results["tests_run"] += 1
        self.test_results["tests_passed"] += 1
        self.test_results["execution_times"]["test_auto_generated_workflow"] = test_timer.elapsed()

        print(
            f"✅ Auto-generated workflow test passed in {test_timer.elapsed():.2f}s")

    def test_resilient_workflow(self):
        """Test the resilient workflow with retry logic."""
        test_timer = Timer().start()
        TestFeedback.print_section("Resilient Workflow Test")

        # Customize resilience settings for quicker testing
        resilience_config = {
            "max_retries": 2,
            "retry_delay": 1,
            "timeout_seconds": 10
        }

        executor = EnhancedWorkflowExecutor(
            workflow_type="dynamic",
            resilience_config=resilience_config,
            notification_level=NotificationLevel.NONE,
            output_dir=str(self.test_output_dir)
        )

        # Test execution
        task_id = "QA-01"
        result = executor.execute_task(task_id)

        # Verify the task was executed
        self.assertEqual(result["task_id"], task_id)

        # Verify the status file contains valid data
        status_data = self.verify_status_file(task_id)

        # Update test statistics
        test_timer.stop()
        self.test_results["tests_run"] += 1
        self.test_results["tests_passed"] += 1
        self.test_results["execution_times"]["test_resilient_workflow"] = test_timer.elapsed(
        )

        print(
            f"✅ Resilient workflow test passed in {test_timer.elapsed():.2f}s")

    def test_notification_integration(self):
        """Test notification system integration."""
        test_timer = Timer().start()
        TestFeedback.print_section("Notification Integration Test")
        # PHASE 2 OPTIMIZATION: Use fast notification config
        with patch('time.sleep'), \
                patch('requests.post') as mock_post, \
                patch('graph.notifications.SlackNotifier.send_notification') as mock_notify:

            mock_post.return_value.status_code = 200
            mock_notify.return_value = {"success": True}

            # Set to error-only notifications to reduce noise
            executor = EnhancedWorkflowExecutor(
                workflow_type="dynamic",
                notification_level=NotificationLevel.ERROR,
                output_dir=str(self.test_output_dir)
            )

            # Test with a task that should succeed
            task_id = "FE-01"
            result = executor.execute_task(task_id)

            # Verify the task was executed
            self.assertEqual(result["task_id"], task_id)

            # Verify the status file contains valid data
            status_data = self.verify_status_file(task_id)

        # Update test statistics
        test_timer.stop()
        self.test_results["tests_run"] += 1
        self.test_results["tests_passed"] += 1
        self.test_results["execution_times"]["test_notification_integration"] = test_timer.elapsed()

        print(
            f"✅ Notification integration test passed in {
                test_timer.elapsed():.2f}s")

    def test_all_components_together(self):
        """Test all components working together."""
        test_timer = Timer().start()
        TestFeedback.print_section("All Components Test")

        # Create a custom executor with all features enabled
        executor = EnhancedWorkflowExecutor(
            workflow_type="auto",
            resilience_config={
                "max_retries": 2,
                "retry_delay": 1,
                "timeout_seconds": 15
            },
            notification_level=NotificationLevel.ALL,
            output_dir=str(self.test_output_dir)
        )

        # Start a monitoring process in a separate thread
        def run_monitor():
            os.system(
                f"python scripts/monitor_workflow.py --task BE-07 --output {
                    self.test_output_dir} --simple")

        monitor_thread = threading.Thread(target=run_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()

        # Give the monitor a moment to start
        time.sleep(1)

        # Execute the task
        task_id = "BE-07"
        result = executor.execute_task(task_id)

        # Verify the task was executed
        self.assertEqual(result["task_id"], task_id)

        # Verify output files were created
        self.assertTrue(
            (self.test_output_dir / task_id / "status.json").exists())

        # Verify the status file contains valid data
        status_data = self.verify_status_file(task_id)

        # Give the monitor a moment to detect the completion
        time.sleep(2)

        # Update test statistics
        test_timer.stop()
        self.test_results["tests_run"] += 1
        self.test_results["tests_passed"] += 1
        self.test_results["execution_times"]["test_all_components_together"] = test_timer.elapsed()

        print(f"✅ All components test passed in {test_timer.elapsed():.2f}s")


# Custom test runner to use our test feedback system
class FeedbackTestRunner:
    """Custom test runner that provides standardized feedback."""

    @staticmethod
    def run():
        """Run all tests with standardized feedback."""
        test_start = time.time()
        TestFeedback.print_header("Enhanced Workflow Tests")

        # Run the tests using unittest
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestEnhancedWorkflow))

        # Create a test result object that will collect the results
        result = unittest.TextTestResult(sys.stdout, True, 1)

        # Run the tests
        print("\nRunning tests...")
        suite.run(result)

        # Calculate test metrics
        tests_run = result.testsRun
        tests_failed = len(result.failures) + len(result.errors)
        tests_passed = tests_run - tests_failed

        # Gather details for feedback
        details = {
            "Tests run": tests_run,
            "Tests passed": tests_passed,
            "Tests failed": tests_failed,
            "Failures": [f"{test[0]._testMethodName}: {test[1]}" for test in result.failures],
            "Errors": [f"{test[0]._testMethodName}: {test[1]}" for test in result.errors],
            "Test categories": ["Basic workflow", "Auto-generated workflow", "Resilient workflow",
                                "Notification integration", "Combined components"]
        }

        # Calculate execution time
        execution_time = time.time() - test_start

        # Print standardized results
        passed = tests_failed == 0
        return TestFeedback.print_result(
            test_name="Enhanced Workflow Tests",
            passed=passed,
            details=details,
            execution_time=execution_time
        )


def teardown_module(module):
    """Cleanup test_outputs directory after tests finish."""
    from config.build_paths import TEST_OUTPUTS_DIR
    test_output_dir = str(TEST_OUTPUTS_DIR)
    if os.path.exists(test_output_dir):
        for child in os.listdir(test_output_dir):
            child_path = os.path.join(test_output_dir, child)
            if os.path.isdir(child_path):
                shutil.rmtree(child_path)
            else:
                os.remove(child_path)


if __name__ == "__main__":
    # Use our custom test runner instead of unittest.main()
    success = FeedbackTestRunner.run()
    sys.exit(0 if success else 1)
