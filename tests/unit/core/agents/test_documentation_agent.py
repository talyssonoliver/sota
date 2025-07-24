"""
Comprehensive tests for DocumentationWriter agent.
Tests the actual functionality of the documentation agent including
initialization, task execution, and integration with memory engine.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.core.agents.doc import DocumentationWriter


class TestDocumentationWriter:
    """Test DocumentationWriter agent functionality."""

    def test_initialization_without_tools_or_memory(self):
        """Test DocumentationWriter can be initialized without tools or memory engine."""
        mock_agent = Mock()
        mock_agent.role = "Documentation Writer"
        mock_agent_class = Mock(return_value=mock_agent)

        with patch(
            "src.core.agents.doc._get_agent_class", return_value=mock_agent_class
        ):
            doc_writer = DocumentationWriter()

            assert doc_writer.tools == []
            assert doc_writer.memory_engine is None
            assert doc_writer.agent is not None
            assert doc_writer.agent.role == "Documentation Writer"

            # Verify agent was created with correct parameters
            mock_agent_class.assert_called_once_with(
                role="Documentation Writer",
                goal="Documentation Writer Agent for creating technical documentation",
                backstory="Expert documentation writer with deep knowledge and expertise",
                verbose=True,
                allow_delegation=False,
                tools=[],
            )

    def test_initialization_with_tools(self):
        """Test DocumentationWriter initialization with tools."""
        mock_tools = [Mock(name="tool1"), Mock(name="tool2")]
        doc_writer = DocumentationWriter(tools=mock_tools)

        assert doc_writer.tools == mock_tools
        assert len(doc_writer.tools) == 2

    def test_initialization_with_memory_engine(self):
        """Test DocumentationWriter initialization with memory engine."""
        mock_memory = Mock()
        doc_writer = DocumentationWriter(memory_engine=mock_memory)

        assert doc_writer.memory_engine == mock_memory

    def test_initialization_with_tools_and_memory(self):
        """Test DocumentationWriter initialization with both tools and memory."""
        mock_tools = [Mock(name="markdown_tool")]
        mock_memory = Mock()

        doc_writer = DocumentationWriter(tools=mock_tools, memory_engine=mock_memory)

        assert doc_writer.tools == mock_tools
        assert doc_writer.memory_engine == mock_memory

    def test_agent_configuration(self):
        """Test that the CrewAI agent is properly configured."""
        mock_agent = Mock()
        mock_agent.role = "Documentation Writer"
        mock_agent_class = Mock(return_value=mock_agent)

        with patch(
            "src.core.agents.doc._get_agent_class", return_value=mock_agent_class
        ):
            doc_writer = DocumentationWriter()

            assert doc_writer.agent.role == "Documentation Writer"
            # Note: Other properties may not be accessible due to mock implementation

    def test_execute_task_basic(self):
        """Test basic task execution."""
        doc_writer = DocumentationWriter()
        task = {"id": "DOC-01", "description": "Create API documentation"}

        result = doc_writer.execute_task(task)

        assert result["task_id"] == "DOC-01"
        assert result["status"] == "completed"
        assert result["agent"] == "DocumentationWriter"
        assert "output" in result

    def test_execute_task_without_id(self):
        """Test task execution when task has no ID."""
        doc_writer = DocumentationWriter()
        task = {"description": "Create user guide"}

        result = doc_writer.execute_task(task)

        assert result["task_id"] == "unknown"
        assert result["status"] == "completed"
        assert result["agent"] == "DocumentationWriter"

    def test_execute_task_empty_task(self):
        """Test task execution with empty task dictionary."""
        doc_writer = DocumentationWriter()
        task = {}

        result = doc_writer.execute_task(task)

        assert result["task_id"] == "unknown"
        assert result["status"] == "completed"
        assert result["agent"] == "DocumentationWriter"

    @patch("src.core.agents.doc.logger")
    def test_execute_task_logging(self, mock_logger):
        """Test that task execution is properly logged."""
        doc_writer = DocumentationWriter()
        task = {"id": "DOC-02", "description": "Create technical specification"}

        doc_writer.execute_task(task)

        mock_logger.info.assert_called_once_with("Executing task: DOC-02")

    def test_execute_task_with_tools_integration(self):
        """Test task execution when tools are available."""
        mock_tool = Mock()
        mock_tool.name = "markdown_generator"
        doc_writer = DocumentationWriter(tools=[mock_tool])

        task = {"id": "DOC-03", "type": "markdown", "content": "# API Documentation"}
        result = doc_writer.execute_task(task)

        assert result["task_id"] == "DOC-03"
        assert result["status"] == "completed"
        # Verify tools are accessible (though not used in current implementation)
        assert len(doc_writer.tools) == 1

    def test_execute_task_with_memory_integration(self):
        """Test task execution when memory engine is available."""
        mock_memory = Mock()
        mock_memory.get_relevant_context.return_value = {
            "context": "Previous documentation patterns"
        }

        doc_writer = DocumentationWriter(memory_engine=mock_memory)
        task = {"id": "DOC-04", "description": "Create consistent documentation"}

        result = doc_writer.execute_task(task)

        assert result["task_id"] == "DOC-04"
        assert result["status"] == "completed"
        # Verify memory engine is accessible
        assert doc_writer.memory_engine == mock_memory

    def test_multiple_task_execution(self):
        """Test executing multiple tasks in sequence."""
        doc_writer = DocumentationWriter()

        tasks = [
            {"id": "DOC-05", "description": "Create README"},
            {"id": "DOC-06", "description": "Create API docs"},
            {"id": "DOC-07", "description": "Create user guide"},
        ]

        results = []
        for task in tasks:
            result = doc_writer.execute_task(task)
            results.append(result)

        assert len(results) == 3
        assert all(result["status"] == "completed" for result in results)
        assert [result["task_id"] for result in results] == [
            "DOC-05",
            "DOC-06",
            "DOC-07",
        ]

    def test_agent_attributes_access(self):
        """Test accessing agent attributes."""
        mock_agent = Mock()
        mock_agent.role = "Documentation Writer"
        mock_agent_class = Mock(return_value=mock_agent)

        with patch(
            "src.core.agents.doc._get_agent_class", return_value=mock_agent_class
        ):
            doc_writer = DocumentationWriter()

            # Test that we can access the agent and its basic properties
            assert hasattr(doc_writer, "agent")
            assert hasattr(doc_writer.agent, "role")
            assert doc_writer.agent.role == "Documentation Writer"


class TestDocumentationWriterErrorHandling:
    """Test error handling scenarios for DocumentationWriter."""

    def test_task_execution_with_none_task(self):
        """Test task execution with None task."""
        doc_writer = DocumentationWriter()

        # This should handle gracefully
        with pytest.raises(AttributeError):
            doc_writer.execute_task(None)

    @patch("src.core.agents.doc.logger")
    def test_logging_with_complex_task_id(self, mock_logger):
        """Test logging with various task ID formats."""
        doc_writer = DocumentationWriter()

        test_cases = [
            {"id": "DOC-123", "expected": "DOC-123"},
            {"id": "", "expected": ""},
            {"id": "COMPLEX-DOC-456-SUBPART", "expected": "COMPLEX-DOC-456-SUBPART"},
        ]

        for test_case in test_cases:
            mock_logger.reset_mock()
            task = {"id": test_case["id"]}
            doc_writer.execute_task(task)
            mock_logger.info.assert_called_once_with(
                f"Executing task: {test_case['expected']}"
            )


class TestDocumentationWriterIntegration:
    """Integration tests for DocumentationWriter with other components."""

    def test_end_to_end_documentation_workflow(self):
        """Test complete documentation generation workflow."""
        # Mock tools that might be used for documentation
        mock_markdown_tool = Mock()
        mock_markdown_tool.name = "markdown_generator"

        mock_file_tool = Mock()
        mock_file_tool.name = "file_writer"

        # Mock memory engine with documentation context
        mock_memory = Mock()
        mock_memory.get_relevant_context.return_value = {
            "documentation_style": "technical",
            "previous_docs": ["API reference", "User guide"],
        }

        # Create documentation writer with full setup
        doc_writer = DocumentationWriter(
            tools=[mock_markdown_tool, mock_file_tool], memory_engine=mock_memory
        )

        # Execute documentation task
        task = {
            "id": "DOC-INTEGRATION-01",
            "type": "api_documentation",
            "target": "REST API endpoints",
            "format": "markdown",
        }

        result = doc_writer.execute_task(task)

        # Verify result structure
        assert result["task_id"] == "DOC-INTEGRATION-01"
        assert result["status"] == "completed"
        assert result["agent"] == "DocumentationWriter"
        assert "output" in result

        # Verify tools and memory are properly integrated
        assert len(doc_writer.tools) == 2
        assert doc_writer.memory_engine == mock_memory

    def test_documentation_writer_factory_compatibility(self):
        """Test that DocumentationWriter works with factory pattern."""
        # This tests compatibility with the agent factory system
        from src.core.agents.factory import Agent, create_documentation_agent

        # Test that factory can create documentation agent
        doc_agent = create_documentation_agent()

        # Factory creates CrewAI Agent, not DocumentationWriter
        assert isinstance(doc_agent, Agent)

        # Test that our DocumentationWriter can coexist with factory system
        doc_writer = DocumentationWriter()

        # Test that both types of agents have the expected interfaces
        assert hasattr(doc_writer, "execute_task")
        assert doc_agent is not None  # Factory agent exists

        # Test task execution with our DocumentationWriter
        task = {
            "id": "FACTORY-DOC-01",
            "description": "Factory-created documentation task",
        }
        result = doc_writer.execute_task(task)

        assert result["task_id"] == "FACTORY-DOC-01"
        assert result["status"] == "completed"
