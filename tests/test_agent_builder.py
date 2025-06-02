import os
import unittest
from unittest.mock import patch, MagicMock

from crewai import Agent
from langchain_core.tools import Tool

# Ensure agents.agent_builder can be imported
from agents.agent_builder import create_generic_agent

class TestCreateGenericAgent(unittest.TestCase):

    @patch.dict(os.environ, {"TESTING": "0", "OPENAI_API_KEY": "test_key"})
    @patch("agents.agent_builder.ChatOpenAI")
    @patch("agents.agent_builder.get_context_by_keys")
    @patch("agents.agent_builder.load_and_format_prompt")
    def test_create_generic_agent_basic_creation(
        self, mock_load_prompt, mock_get_context, mock_chat_openai
    ):
        """Test basic agent creation with minimal valid parameters."""
        mock_load_prompt.return_value = "Formatted system prompt"
        # mock_get_context is not called if context_keys is None
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance

        agent = create_generic_agent(
            role="Test Role",
            goal="Test Goal",
            backstory="Test Backstory",
            prompt_file="prompts/test-prompt.md",
            context_keys=None # Explicitly None, which is the default
        )

        self.assertIsInstance(agent, Agent)
        self.assertEqual(agent.role, "Test Role")
        self.assertEqual(agent.goal, "Test Goal")
        self.assertEqual(agent.backstory, "Test Backstory")
        self.assertEqual(agent.llm, mock_llm_instance)
        mock_chat_openai.assert_called_once_with(model="gpt-4-turbo", temperature=0.2)
        mock_load_prompt.assert_called_once_with("prompts/test-prompt.md", variables={"context": ""})
        mock_get_context.assert_not_called()

    @patch.dict(os.environ, {"TESTING": "0", "OPENAI_API_KEY": "test_key"})
    @patch("agents.agent_builder.ChatOpenAI")
    @patch("agents.agent_builder.get_context_by_keys")
    @patch("agents.agent_builder.load_and_format_prompt")
    def test_create_generic_agent_with_all_params(
        self, mock_load_prompt, mock_get_context, mock_chat_openai
    ):
        """Test agent creation with all parameters specified."""
        mock_load_prompt.return_value = "Formatted system prompt with context"
        mock_get_context.return_value = {"ctx_key": "ctx_value"}
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance

        mock_tool_run = MagicMock(return_value="Tool output")
        custom_tool_instance = MagicMock()
        custom_tool_instance.name = "custom_test_tool"
        custom_tool_instance.description = "A custom tool for testing"
        custom_tool_instance._run = mock_tool_run


        agent = create_generic_agent(
            role="Advanced Role",
            goal="Advanced Goal",
            backstory="Advanced Backstory",
            prompt_file="prompts/advanced-prompt.md",
            llm_model="gpt-3.5-turbo",
            temperature=0.7,
            memory_config={"type": "custom_memory"}, # Passed to Agent constructor
            custom_tools=[custom_tool_instance],
            context_keys=["ctx_key"],
            allow_delegation=True,
            max_iter=5,
            max_rpm=10,
            verbose=False,
        )

        self.assertIsInstance(agent, Agent)
        self.assertEqual(agent.role, "Advanced Role")
        self.assertEqual(agent.llm, mock_llm_instance)
        self.assertEqual(agent.allow_delegation, True)
        self.assertEqual(agent.max_iter, 5)
        self.assertEqual(agent.verbose, False)

        self.assertIsNotNone(agent.memory)

        mock_chat_openai.assert_called_once_with(model="gpt-3.5-turbo", temperature=0.7)
        mock_get_context.assert_called_once_with(["ctx_key"])
        mock_load_prompt.assert_called_once_with(
            "prompts/advanced-prompt.md", variables={"context": "ctx_key: ctx_value"}
        )

        self.assertEqual(len(agent.tools), 1)
        self.assertIsInstance(agent.tools[0], Tool) # Builder wraps it
        self.assertEqual(agent.tools[0].name, custom_tool_instance.name)
        agent.tools[0].func("test")
        custom_tool_instance._run.assert_called_with("test")


    @patch.dict(os.environ, {"TESTING": "1", "OPENAI_API_KEY": "test_key"})
    @patch("agents.agent_builder.ChatOpenAI")
    @patch("agents.agent_builder.get_context_by_keys")
    @patch("agents.agent_builder.load_and_format_prompt")
    def test_create_generic_agent_testing_mode(
        self, mock_load_prompt, mock_get_context, mock_chat_openai
    ):
        """Test agent creation in TESTING mode (tools list should be empty)."""
        mock_load_prompt.return_value = "Test prompt"
        mock_get_context.return_value = {}
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance

        unwrapped_tool = MagicMock()
        unwrapped_tool.name = "unwrapped_tool"
        unwrapped_tool.description = "An unwrapped tool"
        unwrapped_tool._run = MagicMock(return_value="unwrapped output")

        agent = create_generic_agent(
            role="Test Role Testing",
            goal="Test Goal Testing",
            backstory="Test Backstory Testing",
            prompt_file="prompts/testing-prompt.md",
            custom_tools=[unwrapped_tool],
            context_keys=[]
        )

        self.assertIsInstance(agent, Agent)
        self.assertEqual(len(agent.tools), 0)

        self.assertTrue(hasattr(agent, "_memory_config"))
        self.assertEqual(agent._memory_config, {"type": "chroma"})
        self.assertTrue(hasattr(agent, "memory"))
        self.assertIsNotNone(agent.memory)
        if agent.memory is not None and hasattr(agent.memory, 'embedder'):
            self.assertIsNotNone(agent.memory.embedder)


    @patch.dict(os.environ, {"TESTING": "0", "OPENAI_API_KEY": "test_key"})
    @patch("agents.agent_builder.ChatOpenAI")
    @patch("agents.agent_builder.get_context_by_keys")
    @patch("agents.agent_builder.load_and_format_prompt")
    def test_tool_wrapping_for_non_basetool_objects(
        self, mock_load_prompt, mock_get_context, mock_chat_openai
    ):
        """Test that non-BaseTool objects with correct structure are wrapped into Tool."""
        mock_load_prompt.return_value = "Prompt for tool wrapping test"
        mock_get_context.return_value = {}
        mock_chat_openai.return_value = MagicMock()

        custom_callable_tool = MagicMock()
        custom_callable_tool.name = "callable_tool"
        custom_callable_tool.description = "A callable tool object"
        custom_callable_tool._run = MagicMock(return_value="callable output")

        agent = create_generic_agent(
            role="Tool Wrapper Test",
            goal="Test tool wrapping",
            backstory="Testing if tool-like objects are correctly wrapped.",
            prompt_file="prompts/toolwrap-prompt.md",
            custom_tools=[custom_callable_tool]
        )

        self.assertEqual(len(agent.tools), 1)
        self.assertIsInstance(agent.tools[0], Tool)
        self.assertEqual(agent.tools[0].name, "callable_tool")
        self.assertEqual(agent.tools[0].description, "A callable tool object")

        agent.tools[0].func("test input")
        custom_callable_tool._run.assert_called_once_with("test input")

    @patch.dict(os.environ, {"TESTING": "0", "OPENAI_API_KEY": "test_key"})
    @patch("agents.agent_builder.ChatOpenAI")
    @patch("agents.agent_builder.get_context_by_keys")
    @patch("agents.agent_builder.load_and_format_prompt")
    def test_context_keys_handling(
        self, mock_load_prompt, mock_get_context, mock_chat_openai
    ):
        """Test how context_keys are used to fetch and format context for the prompt."""
        mock_load_prompt.return_value = "Formatted system prompt with context"
        mock_get_context.return_value = {"name": "Jules", "ability": "coding"}
        mock_chat_openai.return_value = MagicMock()

        create_generic_agent(
            role="Context Test Role",
            goal="Test context handling",
            backstory="Testing context fetching and formatting.",
            prompt_file="prompts/context-test.md",
            context_keys=["name", "ability"]
        )

        mock_get_context.assert_called_once_with(["name", "ability"])
        expected_context_str = "name: Jules\nability: coding"
        mock_load_prompt.assert_called_once_with(
            "prompts/context-test.md", variables={"context": expected_context_str}
        )

    @patch.dict(os.environ, {"TESTING": "0", "OPENAI_API_KEY": "test_key"})
    @patch("agents.agent_builder.ChatOpenAI")
    @patch("agents.agent_builder.get_context_by_keys")
    @patch("agents.agent_builder.load_and_format_prompt")
    def test_create_generic_agent_no_context_keys(
        self, mock_load_prompt, mock_get_context, mock_chat_openai
    ):
        """Test agent creation when context_keys is None or empty."""
        mock_load_prompt.return_value = "Formatted system prompt without specific context"
        mock_chat_openai.return_value = MagicMock()

        agent_none_keys = create_generic_agent(
            role="No Context Role",
            goal="Test no context keys",
            backstory="Backstory",
            prompt_file="prompts/no-context.md",
            context_keys=None
        )
        mock_get_context.assert_not_called()
        mock_load_prompt.assert_called_with("prompts/no-context.md", variables={"context": ""})

        mock_load_prompt.reset_mock()
        mock_get_context.reset_mock()


        mock_get_context.return_value = {}
        agent_empty_keys = create_generic_agent(
            role="Empty Context Role",
            goal="Test empty context keys",
            backstory="Backstory",
            prompt_file="prompts/empty-context.md",
            context_keys=[]
        )
        mock_get_context.assert_called_once_with([])
        mock_load_prompt.assert_called_with("prompts/empty-context.md", variables={"context": ""})


if __name__ == "__main__":
    unittest.main()
