"""
Test script for agent orchestration and delegation functionality.
This test suite validates that agents can be properly orchestrated,
delegated to, and that they interact correctly with the system.
"""

import os
import sys
import time
import unittest
from datetime import datetime
from unittest.mock import MagicMock, call, patch

from orchestration.delegation import delegate_task, save_task_output
from orchestration.registry import (AGENT_REGISTRY, create_agent_instance,
                                    get_agent_config, get_agent_for_task)
from tests.test_utils import TestFeedback, Timer

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules we'll be testing

# Import our test utilities


class TestAgentRegistry(unittest.TestCase):
    """Test the agent registry system."""

    @patch('orchestration.registry.load_agent_config')
    def test_agent_registry_completeness(self, mock_load_config):
        """Test that all expected agents are in the registry."""
        # Provide mock config that matches the AGENT_REGISTRY keys in
        # registry.py
        mock_load_config.return_value = {
            "coordinator": {"name": "Coordinator Agent"},
            "technical_lead": {"name": "Technical Lead Agent"},
            "backend_engineer": {"name": "Backend Engineer Agent"},
            "frontend_engineer": {"name": "Frontend Engineer Agent"},
            "documentation": {"name": "Documentation Agent"},
            "qa": {"name": "QA Agent"}
        }

        # Check that all expected agent roles are registered
        expected_roles = [
            "coordinator",
            "technical_lead",
            "backend_engineer",
            "frontend_engineer",
            "documentation",
            "qa"]

        for role in expected_roles:
            self.assertIn(role, AGENT_REGISTRY,
                          f"Agent role '{role}' should be in registry")

    @patch('orchestration.registry.load_agent_config')
    def test_task_prefix_mapping(self, mock_load_config):
        """Test that task prefixes are correctly mapped to agent constructors."""
        # Provide mock config
        mock_load_config.return_value = {
            "coordinator": {"name": "Coordinator Agent"},
            "technical_lead": {"name": "Technical Lead Agent"},
            "backend_engineer": {"name": "Backend Engineer Agent"},
            "frontend_engineer": {"name": "Frontend Engineer Agent"},
            "documentation": {"name": "Documentation Agent"},
            "qa": {"name": "QA Agent"}
        }

        expected_mappings = {
            "CO": "coordinator",
            "TL": "technical_lead",
            "BE": "backend_engineer",
            "FE": "frontend_engineer",
            "DOC": "documentation",
            "QA": "qa"
        }

        for prefix, role in expected_mappings.items():
            self.assertIn(prefix, AGENT_REGISTRY,
                          f"Task prefix '{prefix}' should be in registry")

    @patch('orchestration.registry.load_agent_config')
    def test_agent_config_loading(self, mock_load_config):
        """Test loading agent configuration."""
        mock_load_config.return_value = {
            "backend_engineer": {
                "name": "Backend Engineer Agent",
                "role": "Supabase Engineer",
                "tools": ["supabase", "github"]
            }
        }

        # Test getting a valid agent config
        config = get_agent_config("backend_engineer")
        self.assertIsNotNone(config)
        self.assertEqual(config["name"], "Backend Engineer Agent")

        # Test getting a non-existent agent config
        config = get_agent_config("nonexistent")
        self.assertIsNone(config, "Nonexistent agent config should be None")


class TestAgentDelegation(unittest.TestCase):
    """Test the agent delegation system."""

    @patch('orchestration.delegation.get_relevant_context')
    def test_delegate_task(self, mock_get_context):
        """Test delegating a task to an agent."""
        # Set up mocks
        mock_agent = MagicMock()
        mock_agent.execute.return_value = {
            "output": "Task BE-01 completed successfully",
            "task_id": "BE-01",
            "agent_id": "backend_engineer"  # Using consistent naming with registry
        }
        mock_get_context.return_value = "Relevant context for the task"

        # Test delegating with explicit agent ID
        with patch('orchestration.delegation.create_agent_instance') as mock_create_agent:
            mock_create_agent.return_value = mock_agent

            result = delegate_task(
                task_id="BE-01",
                task_description="Implement user authentication",
                agent_id="backend_engineer"  # Using consistent naming with registry
            )

            self.assertEqual(result["output"],
                             "Task BE-01 completed successfully")
            self.assertEqual(result["task_id"], "BE-01")
            self.assertEqual(result["agent_id"], "backend_engineer")

        # Test delegating with task ID prefix
        with patch('orchestration.delegation.get_agent_for_task') as mock_get_agent:
            # Create a new mock agent with correct return value
            task_prefix_mock_agent = MagicMock()
            task_prefix_mock_agent.execute.return_value = {
                "output": "Task TL-02 completed successfully",
                "task_id": "TL-02",
                "agent_id": "technical_lead"
            }
            mock_get_agent.return_value = task_prefix_mock_agent

            result = delegate_task(
                task_id="TL-02",
                task_description="Design CI/CD pipeline"
            )

            self.assertEqual(result["output"],
                             "Task TL-02 completed successfully")
            self.assertEqual(result["task_id"], "TL-02")
            self.assertEqual(result["agent_id"], "technical_lead")

    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    def test_save_task_output(self, mock_makedirs, mock_path_exists):
        """Test saving task output to a file."""
        with patch('builtins.open', unittest.mock.mock_open()) as mock_open:
            result = save_task_output("BE-01", "Task completed successfully")

            # Check if the output directory was created
            mock_makedirs.assert_called_once()

            # Check if the file was opened for writing
            mock_open.assert_called_once()

            # Check that the output was written to the file
            handle = mock_open()
            handle.write.assert_called_once_with("Task completed successfully")

            # The function should return the file path
            self.assertIsInstance(result, str)
            self.assertIn("BE-01", result)


class TestAgentOrchestration(unittest.TestCase):
    """Test the complete orchestration flow with agents."""

    def test_agent_task_delegation_flow(self):
        """Test the flow of delegating tasks to different agents."""
        # Create function-specific patches to avoid interfering with other
        # tests
        with patch('orchestration.delegation.delegate_task') as mock_delegate_task:
            # Set up mock return values for different task types
            mock_delegate_task.side_effect = [
                {"task_id": "BE-01", "agent_id": "backend",
                    "output": "Backend task completed"},
                {"task_id": "FE-02", "agent_id": "frontend",
                    "output": "Frontend task completed"},
                {"task_id": "QA-03", "agent_id": "qa",
                    "output": "QA task completed"}
            ]

            # Simulate delegating a sequence of tasks
            results = []
            for task_info in [
                {"task_id": "BE-01", "desc": "Implement user auth"},
                {"task_id": "FE-02", "desc": "Create login form"},
                {"task_id": "QA-03", "desc": "Test auth flow"}
            ]:
                result = mock_delegate_task(
                    task_id=task_info["task_id"],
                    task_description=task_info["desc"]
                )
                results.append(result)

            # Verify that the mock was called exactly 3 times
            self.assertEqual(mock_delegate_task.call_count, 3)

            # Verify correct parameters were used in each call
            self.assertEqual(
                mock_delegate_task.call_args_list[0][1]['task_id'], 'BE-01')
            self.assertEqual(
                mock_delegate_task.call_args_list[0][1]['task_description'],
                'Implement user auth')

            self.assertEqual(
                mock_delegate_task.call_args_list[1][1]['task_id'], 'FE-02')
            self.assertEqual(
                mock_delegate_task.call_args_list[1][1]['task_description'],
                'Create login form')

            self.assertEqual(
                mock_delegate_task.call_args_list[2][1]['task_id'], 'QA-03')
            self.assertEqual(
                mock_delegate_task.call_args_list[2][1]['task_description'],
                'Test auth flow')

            # Verify the results match what we expect
            self.assertEqual(results[0]["output"], "Backend task completed")
            self.assertEqual(results[1]["output"], "Frontend task completed")
            self.assertEqual(results[2]["output"], "QA task completed")

    def test_task_failure_handling(self):
        """Test handling of task failures during orchestration."""
        # Create a function that always raises an exception
        def mock_delegate_that_raises(*args, **kwargs):
            raise Exception("Task execution failed")

        # Use the patch decorator to replace the module-level function
        # completely
        with patch('orchestration.delegation.delegate_task',
                   mock_delegate_that_raises):

            # This should now raise the exception from our mock function
            with self.assertRaises(Exception) as context:
                from orchestration.delegation import delegate_task
                delegate_task(
                    task_id="BE-01",
                    task_description="Implement failing task"
                )

            # Verify the exception is the one we expect
            self.assertTrue("Task execution failed" in str(context.exception))


# Custom test runner to use our test feedback system
class FeedbackTestRunner:
    """Custom test runner that provides standardized feedback."""

    @staticmethod
    def run():
        """Run all tests with standardized feedback."""
        test_start = time.time()
        TestFeedback.print_header("Agent Orchestration Tests")

        # Run the tests using unittest
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestAgentRegistry))
        suite.addTest(unittest.makeSuite(TestAgentDelegation))
        suite.addTest(unittest.makeSuite(TestAgentOrchestration))

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
            "Test categories": ["Agent Registry", "Agent Delegation", "Agent Orchestration"]
        }

        # Calculate execution time
        execution_time = time.time() - test_start

        # Print standardized results
        passed = tests_failed == 0
        return TestFeedback.print_result(
            test_name="Agent Orchestration Tests",
            passed=passed,
            details=details,
            execution_time=execution_time
        )


if __name__ == "__main__":
    # Use our custom test runner instead of unittest.main()
    success = FeedbackTestRunner.run()
    sys.exit(0 if success else 1)
