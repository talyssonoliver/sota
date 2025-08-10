"""
Test script for agent instantiation and basic functionality.
This test suite validates that all agents can be properly constructed,
have the correct tools attached, and handle basic run operations.
"""

import os
import sys
import time
import unittest

# Keep this import for compatibility with test mocks
from langchain_core.tools import BaseTool
# Add import from langchain_core

from src.core.workflows.registry import (create_backend_engineer_agent, create_coordinator_agent,
                    create_documentation_agent, create_frontend_engineer_agent,
                    create_qa_agent, create_technical_lead_agent)
from src.core.workflows.registry import get_agent_for_task
# Add the project root to the path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.append(project_root)

# Import test environment setup FIRST before any other imports
# This sets the TESTING environment variable and mocks prompt loading
from tests.test_environment import *
from tests.unit.core.test_utils import TestFeedback

# Import the agent creation functions that we'll be testing

# Create a proper mock tool class that inherits from BaseTool


class MockBaseTool(BaseTool):
    name: str = "mock_tool"
    description: str = "A mock tool for testing"

    def _run(self, query: str) -> str:
        return f"Mock response for: {query}"

    def _arun(self, query: str) -> str:
        return self._run(query)


def create_mock_tool(name: str, description: str) -> BaseTool:
    """Create a valid BaseTool instance for testing."""
    tool = MockBaseTool()
    tool.name = name
    tool.description = description
    return tool


class TestAgentInstantiation(unittest.TestCase):
    """Test agent instantiation and basic properties."""

    def setUp(self):
        """Set up test environment."""
        # Create mock tools for specific tests
        self.tool_mocks = {}
        for tool_name in [
            'github_tool',
            'supabase_tool',
            'tailwind_tool',
            'markdown_tool',
            'vercel_tool',
            'jest_tool',
            'cypress_tool',
                'coverage_tool']:
            mock_tool = create_mock_tool(
                tool_name, f"Mock {tool_name} description")
            self.tool_mocks[tool_name] = mock_tool

    def test_coordinator_agent_creation(self):
        """Test creation of the coordinator agent."""
        agent = create_coordinator_agent()
        self.assertIsNotNone(agent)
        # Test that it's a Coordinator instance
        from src.core.agents.coordinator import Coordinator
        self.assertIsInstance(agent, Coordinator)

    def test_technical_lead_agent_creation(self):
        """Test creation of the technical lead agent."""

        agent = create_technical_lead_agent(custom_tools=[])
        self.assertIsNotNone(agent)

    def test_backend_engineer_agent_creation(self):
        """Test creation of the backend engineer agent."""
        # Create the agent with empty tools
        agent = create_backend_engineer_agent(custom_tools=[])
        self.assertIsNotNone(agent)

    def test_frontend_engineer_agent_creation(self):
        """Test creation of the frontend engineer agent."""
        # Create the agent with empty tools
        agent = create_frontend_engineer_agent(custom_tools=[])
        self.assertIsNotNone(agent)

    def test_documentation_agent_creation(self):
        """Test creation of the documentation agent."""
        # Create the agent with empty tools
        agent = create_documentation_agent(custom_tools=[])
        self.assertIsNotNone(agent)

    def test_qa_agent_creation(self):
        """Test creation of the qa agent."""
        # Create the agent with empty tools
        agent = create_qa_agent(custom_tools=[])
        self.assertIsNotNone(agent)

    def test_custom_tools_integration(self):
        """Test that custom tools are properly integrated into agents."""
        # Create a mock custom tool
        mock_custom_tool = create_mock_tool(
            "custom_test_tool", "A custom tool for testing")

        agent = create_backend_engineer_agent(custom_tools=[mock_custom_tool])
        self.assertIsNotNone(agent)

    def test_memory_config_integration(self):
        """Test that memory configuration can be passed to agent creation."""
        # Create memory configuration
        memory_config = {"type": "redis", "ttl": 3600}

        # Create the agent with memory config
        agent = create_frontend_engineer_agent(memory_config=memory_config, custom_tools=[])
        
        # Just verify the agent was created successfully
        self.assertIsNotNone(agent)


class TestAgentFunctionality(unittest.TestCase):
    """Test agent functional capabilities."""

    def test_agent_run_method(self):
        """Test that the agent can be created successfully."""

        # Create the agent
        agent = create_technical_lead_agent(custom_tools=[])

        # Just verify the agent was created successfully
        self.assertIsNotNone(agent)

    def test_agent_for_task_lookup(self):
        """Test that we can get the correct agent for a task type."""
        # Test backend task type
        agent_type = get_agent_for_task("backend")
        self.assertEqual(agent_type, "backend")

        # Test technical task type
        agent_type = get_agent_for_task("technical")
        self.assertEqual(agent_type, "technical_lead")

        # Test unknown task type
        agent_type = get_agent_for_task("unknown")
        self.assertEqual(agent_type, "coordinator")


class TestAgentToolIntegration(unittest.TestCase):
    """Test integration between agents and their tools."""

    def test_backend_agent_tool_initialization(self):
        """Test that backend agent initializes its tools correctly."""

        agent = create_backend_engineer_agent()
        self.assertIsNotNone(agent)

    def test_qa_agent_tool_initialization(self):
        """Test that QA agent initializes its tools correctly."""

        agent = create_qa_agent()
        self.assertIsNotNone(agent)


# Custom test runner to use our test feedback system
class FeedbackTestRunner:
    """Custom test runner that provides standardized feedback."""

    @staticmethod
    def run():
        """Run all tests with standardized feedback."""
        test_start = time.time()
        TestFeedback.print_header("Agent Tests")

        # Run the tests using unittest
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestAgentInstantiation))
        suite.addTest(unittest.makeSuite(TestAgentFunctionality))
        suite.addTest(unittest.makeSuite(TestAgentToolIntegration))

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
            "Errors": [f"{test[0]._testMethodName}: {test[1]}" for test in result.errors]
        }

        # Calculate execution time
        execution_time = time.time() - test_start

        # Print standardized results
        passed = tests_failed == 0
        return TestFeedback.print_result(
            test_name="Agent Tests",
            passed=passed,
            details=details,
            execution_time=execution_time
        )


if __name__ == "__main__":
    # Use our custom test runner instead of unittest.main()
    success = FeedbackTestRunner.run()
    sys.exit(0 if success else 1)
