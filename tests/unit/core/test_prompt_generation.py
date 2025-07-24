"""
Comprehensive tests for prompt generation workflow.

Tests prompt generation functions and context formatting.
"""

import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.workflows.generate_prompt import (
    format_prompt_with_context,
    generate_prompt,
    get_task_context,
    load_prompt_template,
    load_task_metadata,
    main,
)


class TestGeneratePrompt:
    """Test the generate_prompt function."""

    def test_generate_prompt_basic(self):
        """Test basic prompt generation."""
        result = generate_prompt("TEST-01", "qa_agent")
        
        assert result["task_id"] == "TEST-01"
        assert result["agent_type"] == "qa_agent"
        assert result["output_path"] is None

    def test_generate_prompt_with_output_path(self):
        """Test prompt generation with output path."""
        output_path = "/tmp/output.txt"
        result = generate_prompt("TEST-02", "documentation_agent", output_path)
        
        assert result["task_id"] == "TEST-02"
        assert result["agent_type"] == "documentation_agent"
        assert result["output_path"] == output_path

    def test_generate_prompt_different_agent_types(self):
        """Test prompt generation with different agent types."""
        agent_types = ["qa_agent", "documentation_agent", "test_generator", "custom_agent"]
        
        for agent_type in agent_types:
            result = generate_prompt("MULTI-01", agent_type)
            assert result["agent_type"] == agent_type
            assert result["task_id"] == "MULTI-01"

    def test_generate_prompt_return_structure(self):
        """Test that generate_prompt returns expected structure."""
        result = generate_prompt("STRUCT-01", "test_agent")
        
        # Check all expected keys are present
        expected_keys = ["task_id", "agent_type", "output_path"]
        for key in expected_keys:
            assert key in result

    def test_generate_prompt_with_special_characters(self):
        """Test prompt generation with special characters in inputs."""
        special_task_id = "TEST-01_special!@#"
        special_agent = "agent/with/path"
        special_path = "/path/with spaces/file.txt"
        
        result = generate_prompt(special_task_id, special_agent, special_path)
        
        assert result["task_id"] == special_task_id
        assert result["agent_type"] == special_agent
        assert result["output_path"] == special_path


class TestLoadPromptTemplate:
    """Test the load_prompt_template function."""

    def test_load_prompt_template_basic(self):
        """Test basic template loading."""
        template_path = "templates/qa_agent.txt"
        result = load_prompt_template(template_path)
        
        assert "template" in result
        assert result["template"] == "default template"

    def test_load_prompt_template_different_paths(self):
        """Test template loading with different paths."""
        paths = [
            "templates/qa.txt",
            "/absolute/path/template.txt",
            "relative/path/template.md",
            "template_with_underscores.jinja2"
        ]
        
        for path in paths:
            result = load_prompt_template(path)
            assert result["template"] == "default template"

    def test_load_prompt_template_return_type(self):
        """Test that load_prompt_template returns dict."""
        result = load_prompt_template("any_path.txt")
        assert isinstance(result, dict)
        assert len(result) == 1


class TestLoadTaskMetadata:
    """Test the load_task_metadata function."""

    def test_load_task_metadata_basic(self):
        """Test basic metadata loading."""
        result = load_task_metadata("TASK-01")
        
        assert "task_id" in result
        assert "title" in result
        assert result["task_id"] == "TASK-01"
        assert result["title"] == "Default Task"

    def test_load_task_metadata_different_task_ids(self):
        """Test metadata loading with different task IDs."""
        task_ids = ["BE-01", "FE-02", "TEST-03", "DOC-04", "QA-05"]
        
        for task_id in task_ids:
            result = load_task_metadata(task_id)
            assert result["task_id"] == task_id
            assert result["title"] == "Default Task"

    def test_load_task_metadata_structure(self):
        """Test metadata structure consistency."""
        result = load_task_metadata("STRUCT-01")
        
        # Check expected keys
        expected_keys = ["task_id", "title"]
        for key in expected_keys:
            assert key in result
            assert isinstance(result[key], str)

    def test_load_task_metadata_with_special_task_ids(self):
        """Test metadata loading with special task IDs."""
        special_ids = ["TASK_01", "task-with-dashes", "LONG_TASK_ID_123", "T1"]
        
        for task_id in special_ids:
            result = load_task_metadata(task_id)
            assert result["task_id"] == task_id


class TestGetTaskContext:
    """Test the get_task_context function."""

    def test_get_task_context_basic(self):
        """Test basic context retrieval."""
        result = get_task_context("CONTEXT-01")
        
        assert isinstance(result, str)
        assert "CONTEXT-01" in result
        assert "Context for" in result

    def test_get_task_context_different_task_ids(self):
        """Test context retrieval with different task IDs."""
        task_ids = ["BE-01", "FE-02", "TEST-03"]
        
        for task_id in task_ids:
            result = get_task_context(task_id)
            assert task_id in result
            assert isinstance(result, str)

    def test_get_task_context_format(self):
        """Test context format consistency."""
        result = get_task_context("FORMAT-01")
        expected_format = "Context for FORMAT-01"
        assert result == expected_format

    def test_get_task_context_with_empty_string(self):
        """Test context retrieval with empty string."""
        result = get_task_context("")
        assert "Context for " in result
        assert isinstance(result, str)


class TestFormatPromptWithContext:
    """Test the format_prompt_with_context function."""

    def test_format_prompt_with_context_basic(self):
        """Test basic prompt formatting."""
        template = "You are a {role}"
        context = "qa_agent"
        
        result = format_prompt_with_context(template, context)
        
        assert isinstance(result, str)
        assert template in result
        assert context in result
        assert "Template:" in result
        assert "Context:" in result

    def test_format_prompt_with_context_different_inputs(self):
        """Test formatting with different template and context combinations."""
        test_cases = [
            ("Simple template", "Simple context"),
            ("Complex template with {variables}", "Context with data"),
            ("", "Empty template context"),
            ("Non-empty template", ""),
        ]
        
        for template, context in test_cases:
            result = format_prompt_with_context(template, context)
            assert isinstance(result, str)
            assert str(template) in result
            assert str(context) in result

    def test_format_prompt_with_context_format(self):
        """Test consistent formatting structure."""
        template = "Test template"
        context = "Test context"
        
        result = format_prompt_with_context(template, context)
        expected = f"Template: {template}, Context: {context}"
        assert result == expected

    def test_format_prompt_with_context_special_characters(self):
        """Test formatting with special characters."""
        template = "Template with !@#$%^&*()_+"
        context = "Context with émojis 🚀 and unicode"
        
        result = format_prompt_with_context(template, context)
        assert template in result
        assert context in result


class TestMainFunction:
    """Test the main CLI function."""

    def test_main_with_no_arguments(self):
        """Test main function with no command line arguments."""
        with patch.object(sys, 'argv', ['generate_prompt.py']):
            # Should run without error and not print anything
            main()

    def test_main_with_task_id_only(self):
        """Test main function with only task ID."""
        with patch.object(sys, 'argv', ['generate_prompt.py', 'TEST-01']):
            with patch('builtins.print') as mock_print:
                main()
                
                mock_print.assert_called_once()
                call_args = mock_print.call_args[0][0]
                assert "Generated prompt:" in call_args
                assert "TEST-01" in call_args
                assert "default" in call_args

    def test_main_with_task_id_and_agent_type(self):
        """Test main function with task ID and agent type."""
        with patch.object(sys, 'argv', ['generate_prompt.py', 'TEST-02', 'qa_agent']):
            with patch('builtins.print') as mock_print:
                main()
                
                mock_print.assert_called_once()
                call_args = mock_print.call_args[0][0]
                assert "Generated prompt:" in call_args
                assert "TEST-02" in call_args
                assert "qa_agent" in call_args

    def test_main_with_multiple_arguments(self):
        """Test main function with multiple arguments."""
        args = ['generate_prompt.py', 'MULTI-01', 'test_agent', 'extra_arg']
        with patch.object(sys, 'argv', args):
            with patch('builtins.print') as mock_print:
                main()
                
                mock_print.assert_called_once()
                call_args = mock_print.call_args[0][0]
                assert "MULTI-01" in call_args
                assert "test_agent" in call_args

    def test_main_output_format(self):
        """Test main function output format."""
        with patch.object(sys, 'argv', ['generate_prompt.py', 'FORMAT-01', 'format_agent']):
            with patch('builtins.print') as mock_print:
                main()
                
                # Verify the output contains expected structure
                output = mock_print.call_args[0][0]
                assert output.startswith("Generated prompt: ")
                assert "task_id" in output
                assert "agent_type" in output
                assert "output_path" in output


class TestModuleIntegration:
    """Test integration between different module functions."""

    def test_full_workflow_integration(self):
        """Test a complete workflow using multiple functions."""
        # Generate basic prompt
        prompt_data = generate_prompt("WORKFLOW-01", "qa_agent", "/tmp/output.txt")
        
        # Load template and metadata
        template = load_prompt_template("templates/qa.txt")
        metadata = load_task_metadata(prompt_data["task_id"])
        
        # Get context and format
        context = get_task_context(prompt_data["task_id"])
        formatted = format_prompt_with_context(template["template"], context)
        
        # Verify all pieces work together
        assert prompt_data["task_id"] == "WORKFLOW-01"
        assert metadata["task_id"] == "WORKFLOW-01"
        assert "WORKFLOW-01" in context
        assert template["template"] in formatted

    def test_template_and_context_integration(self):
        """Test template loading and context formatting integration."""
        template_data = load_prompt_template("test_template.txt")
        context = get_task_context("INTEGRATION-01")
        
        result = format_prompt_with_context(template_data["template"], context)
        
        assert "default template" in result
        assert "Context for INTEGRATION-01" in result

    def test_metadata_and_prompt_generation_consistency(self):
        """Test consistency between metadata loading and prompt generation."""
        task_id = "CONSISTENCY-01"
        
        prompt_data = generate_prompt(task_id, "test_agent")
        metadata = load_task_metadata(task_id)
        
        # Both should reference the same task
        assert prompt_data["task_id"] == metadata["task_id"]
        assert prompt_data["task_id"] == task_id