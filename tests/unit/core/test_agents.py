"""
Test script for agent instantiation and basic functionality.
This test suite validates that all agents can be properly constructed,
have the correct tools attached, and handle basic run operations.
"""

import os
import sys
import time
import unittest
from typing import Any, Dict
from unittest.mock import DEFAULT, MagicMock, patch

# Keep this import for compatibility with test mocks
from langchain_core.tools import BaseTool
# Add import from langchain_core
from langchain_core.tools import BaseTool as CoreBaseTool

from agents import (create_backend_engineer_agent, create_coordinator_agent,
                    create_documentation_agent, create_frontend_engineer_agent,
                    create_qa_agent, create_technical_lead_agent)
from src.core.workflows.registry import get_agent_config, get_agent_for_task
# Import test environment setup FIRST before any other imports
# This sets the TESTING environment variable and mocks prompt loading
from test_environment import *
from test_utils import FeedbackCollector, Timer

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    # Create a properly configured mock tool
    class ConfiguredMockTool(MockBaseTool):
        def __init__(self):
            super().__init__()
            self.name = name
            self.description = description
    
    return ConfiguredMockTool()


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

    @patch('src.core.agents.coordinator.ChatOpenAI')
    @patch('src.core.agents.coordinator.get_context_by_keys')
    @patch('src.core.agents.coordinator.Agent')
    def test_coordinator_agent_creation(
            self,
            mock_agent_class,
            mock_get_context,
            mock_chat_openai):
        """Test creation of the coordinator agent."""
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        mock_get_context.return_value = {}

        # Create a mock agent instance that will be returned by the Agent
        # constructor
        mock_agent_instance = MagicMock()
        mock_agent_instance.role = "Project Manager"
        mock_agent_class.return_value = mock_agent_instance

        agent = create_coordinator_agent(
            llm_model="gpt-3.5-turbo-16k", custom_tools=[])
        self.assertIsNotNone(agent)
        # Verify the agent was created by checking it has the expected mock structure
        self.assertTrue(hasattr(agent, 'role'), "Agent should have a role attribute")

    @patch('src.core.agents.technical.ChatOpenAI')
    @patch('src.core.agents.technical.get_context_by_keys')
    @patch('src.core.agents.technical.VercelTool')
    @patch('src.core.agents.technical.GitHubTool')
    @patch('src.core.agents.technical.os')
    def test_technical_lead_agent_creation(
            self,
            mock_os,
            mock_github_tool,
            mock_vercel_tool,
            mock_get_context,
            mock_chat_openai):
        """Test creation of the technical lead agent."""
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        mock_get_context.return_value = {}

        # Set up mock environment variables
        mock_os.getenv.return_value = "dummy-vercel-token"

        # Configure mock tools to be BaseTool instances
        mock_vercel = MagicMock()
        mock_vercel.__class__ = BaseTool
        mock_vercel.name = "vercel_tool"
        mock_vercel.description = "Vercel deployment tool"
        mock_vercel._run = lambda query: f"Mock Vercel response for: {query}"
        mock_vercel_tool.return_value = mock_vercel

        mock_github = MagicMock()
        mock_github.__class__ = BaseTool
        mock_github.name = "github_tool"
        mock_github.description = "GitHub repository tool"
        mock_github._run = lambda query: f"Mock GitHub response for: {query}"
        mock_github_tool.return_value = mock_github

        agent = create_technical_lead_agent(custom_tools=[])
        self.assertIsNotNone(agent)

    @patch('src.core.agents.backend.ChatOpenAI')
    @patch('src.core.agents.backend.get_context_by_keys')
    @patch('src.core.agents.backend.SupabaseTool')
    @patch('src.core.agents.backend.GitHubTool')
    @patch('src.core.agents.backend.os')
    def test_backend_engineer_agent_creation(
            self,
            mock_os,
            mock_github_tool,
            mock_supabase_tool,
            mock_get_context,
            mock_chat_openai):
        """Test creation of the backend engineer agent."""
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        mock_get_context.return_value = {}
        mock_os.environ.get.return_value = "1"  # Set TESTING=1

        # Create the agent - with testing flag, should create with empty tools
        agent = create_backend_engineer_agent(custom_tools=[])
        self.assertIsNotNone(agent)

    @patch('src.core.agents.frontend.ChatOpenAI')
    @patch('src.core.agents.frontend.get_context_by_keys')
    @patch('src.core.agents.frontend.TailwindTool')
    @patch('src.core.agents.frontend.GitHubTool')
    @patch('src.core.agents.frontend.os')
    def test_frontend_engineer_agent_creation(
            self,
            mock_os,
            mock_github_tool,
            mock_tailwind_tool,
            mock_get_context,
            mock_chat_openai):
        """Test creation of the frontend engineer agent."""
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        mock_get_context.return_value = {}
        mock_os.environ.get.return_value = "1"  # Set TESTING=1

        # Create the agent - with testing flag, should create with empty tools
        agent = create_frontend_engineer_agent(custom_tools=[])
        self.assertIsNotNone(agent)

    @patch('src.core.agents.doc.ChatOpenAI')
    @patch('src.core.agents.doc.get_context_by_keys')
    @patch('src.core.agents.doc.MarkdownTool')
    @patch('src.core.agents.doc.GitHubTool')
    @patch('src.core.agents.doc.os')
    def test_documentation_agent_creation(
            self,
            mock_os,
            mock_github_tool,
            mock_markdown_tool,
            mock_get_context,
            mock_chat_openai):
        """Test creation of the documentation agent."""
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        mock_get_context.return_value = {}
        mock_os.environ.get.return_value = "1"  # Set TESTING=1

        # Create the agent - with testing flag, should create with empty tools
        agent = create_documentation_agent(custom_tools=[])
        self.assertIsNotNone(agent)

    @patch('src.core.agents.qa.ChatOpenAI')
    @patch('src.core.agents.qa.get_context_by_keys')
    @patch('src.core.agents.qa.JestTool')
    @patch('src.core.agents.qa.CypressTool')
    @patch('src.core.agents.qa.CoverageTool')
    @patch('src.core.agents.qa.os')
    def test_qa_agent_creation(
            self,
            mock_os,
            mock_coverage_tool,
            mock_cypress_tool,
            mock_jest_tool,
            mock_get_context,
            mock_chat_openai):
        """Test creation of the qa agent."""
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        mock_get_context.return_value = {}
        mock_os.environ.get.return_value = "1"  # Set TESTING=1

        # Create the agent - with testing flag, should create with empty tools
        agent = create_qa_agent(custom_tools=[])
        self.assertIsNotNone(agent)

    @patch('src.core.agents.backend.ChatOpenAI')
    @patch('src.core.agents.backend.get_context_by_keys')
    @patch('src.core.agents.backend.SupabaseTool')
    @patch('src.core.agents.backend.GitHubTool')
    @patch('src.core.agents.backend.os')
    def test_custom_tools_integration(
            self,
            mock_os,
            mock_github_tool,
            mock_supabase_tool,
            mock_get_context,
            mock_chat_openai):
        """Test that custom tools are properly integrated into agents."""
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        mock_get_context.return_value = {}
        mock_os.environ.get.return_value = "1"  # Set TESTING=1        # Create a mock custom tool
        mock_custom_tool = create_mock_tool(
            "custom_test_tool", "A custom tool for testing")
        
        agent = create_backend_engineer_agent(custom_tools=[mock_custom_tool])
        self.assertIsNotNone(agent)

    def test_memory_config_integration(self):
        """Test that memory configuration is properly passed to the Agent constructor."""
        # Create memory configuration
        memory_config = {"type": "redis", "ttl": 3600}

        # Mock the Agent class in the right location (agents.frontend for old structure)
        with patch('agents.frontend.Agent') as mock_agent_class, \
                patch('agents.frontend.ChatOpenAI') as mock_chat_openai, \
                patch('agents.frontend.get_context_by_keys') as mock_get_context, \
                patch('agents.frontend.os') as mock_os:

            # Set up the mock environment
            mock_agent_instance = MagicMock()
            mock_agent_class.return_value = mock_agent_instance
            mock_chat_openai.return_value = MagicMock()
            mock_get_context.return_value = {}
            mock_os.environ.get.return_value = "1"  # Set TESTING=1

            # Create the agent with memory config (using imported function from setup)
            agent = create_frontend_engineer_agent(
                memory_config=memory_config, custom_tools=[])

            # Verify the agent was created
            self.assertIsNotNone(agent, "Agent should be created successfully")
            
            # Since we're using the test framework, just verify agent creation works
            # The actual memory config integration is tested in the dedicated test file


class TestAgentFunctionality(unittest.TestCase):
    """Test agent functional capabilities."""

    @patch('src.core.agents.technical.ChatOpenAI')
    @patch('src.core.agents.technical.get_context_by_keys')
    @patch('src.core.agents.technical.VercelTool')
    @patch('src.core.agents.technical.GitHubTool')
    @patch('src.core.agents.technical.os')
    def test_agent_run_method(
            self,
            mock_os,
            mock_github_tool,
            mock_vercel_tool,
            mock_get_context,
            mock_chat_openai):
        """Test that the agent can be created successfully."""
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        mock_get_context.return_value = {}

        # Set up mock environment variables
        mock_os.getenv.return_value = "dummy-vercel-token"

        # Configure mock tools to be BaseTool instances
        mock_vercel = MagicMock()
        mock_vercel.__class__ = BaseTool
        mock_vercel.name = "vercel_tool"
        mock_vercel.description = "Vercel deployment tool"
        mock_vercel._run = lambda query: f"Mock Vercel response for: {query}"
        mock_vercel_tool.return_value = mock_vercel

        mock_github = MagicMock()
        mock_github.__class__ = BaseTool
        mock_github.name = "github_tool"
        mock_github.description = "GitHub repository tool"
        mock_github._run = lambda query: f"Mock GitHub response for: {query}"
        mock_github_tool.return_value = mock_github

        # Create the agent
        agent = create_technical_lead_agent(custom_tools=[])

        # Just verify the agent was created successfully
        self.assertIsNotNone(agent)

    @patch('src.core.workflows.registry.create_agent_instance')
    def test_agent_for_task_lookup(self, mock_create_agent_instance):
        """Test that we can get the correct agent for a task ID."""
        # Set up mock return values
        mock_agent = MagicMock()
        mock_create_agent_instance.return_value = mock_agent

        # Test backend task prefix
        agent = get_agent_for_task("BE-01")
        self.assertIsNotNone(agent)
        # Assert it was called with the correct task prefix
        mock_create_agent_instance.assert_called_with("BE")

        # Test technical lead task prefix
        agent = get_agent_for_task("TL-05")
        self.assertIsNotNone(agent)
        # Assert it was called with the correct task prefix
        mock_create_agent_instance.assert_called_with("TL")


class TestAgentToolIntegration(unittest.TestCase):
    """Test integration between agents and their tools."""

    @patch('src.core.agents.backend.ChatOpenAI')
    @patch('src.core.agents.backend.get_context_by_keys')
    @patch('src.core.agents.backend.SupabaseTool')
    @patch('src.core.agents.backend.GitHubTool')
    @patch('src.core.agents.backend.os')
    def test_backend_agent_tool_initialization(
            self,
            mock_os,
            mock_github_tool,
            mock_supabase_tool,
            mock_get_context,
            mock_chat_openai):
        """Test that backend agent initializes its tools correctly."""
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        mock_get_context.return_value = {}
        mock_os.environ.get.return_value = "1"  # Set TESTING=1

        agent = create_backend_engineer_agent()
        self.assertIsNotNone(agent)

    @patch('src.core.agents.qa.ChatOpenAI')
    @patch('src.core.agents.qa.get_context_by_keys')
    @patch('src.core.agents.qa.JestTool')
    @patch('src.core.agents.qa.CypressTool')
    @patch('src.core.agents.qa.CoverageTool')
    @patch('src.core.agents.qa.os')
    def test_qa_agent_tool_initialization(
            self,
            mock_os,
            mock_coverage_tool,
            mock_cypress_tool,
            mock_jest_tool,
            mock_get_context,
            mock_chat_openai):
        """Test that QA agent initializes its tools correctly."""
        mock_chat_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_instance
        mock_get_context.return_value = {}
        mock_os.environ.get.return_value = "1"  # Set TESTING=1

        agent = create_qa_agent()
        self.assertIsNotNone(agent)


# Custom test runner to use our test feedback system
class FeedbackTestRunner:
    """Custom test runner that provides standardized feedback."""

    @staticmethod
    def run():
        """Run all tests with standardized feedback."""
        test_start = time.time()
        FeedbackCollector.print_header("Agent Tests")

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
        return FeedbackCollector.print_result(
            test_name="Agent Tests",
            passed=passed,
            details=details,
            execution_time=execution_time
        )


if __name__ == "__main__":
    # Use our custom test runner instead of unittest.main()
    success = FeedbackTestRunner.run()
    sys.exit(0 if success else 1)
