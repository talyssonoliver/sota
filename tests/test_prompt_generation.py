"""
Test Suite for Step 4.2: Prompt Generation with Context

This module tests the Step 4.2 implementation including:
- Prompt template loading from prompts/[agent].md
- Task metadata loading from tasks/[task-id].yaml
- Context retrieval via MCP using context_topics
- Placeholder replacement for {context} and {task_description}
- Output saving to outputs/[task-id]/prompt_[agent].md
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from orchestration.generate_prompt import (generate_prompt, get_task_context,
                                           main)
from prompts.utils import format_prompt_with_context, load_prompt_template
from utils.task_loader import load_task_metadata

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestStep42PromptGeneration:
    """Test suite for Step 4.2 prompt generation functionality."""

    @pytest.fixture
    def mock_task_metadata(self):
        """Mock task metadata for testing."""
        return {
            'task_id': 'BE-07',
            'title': 'Test Backend Task',
            'description': 'Implement test backend functionality',
            'context_topics': ['backend', 'api', 'database'],
            'artefacts': ['backend_service.py', 'api_endpoints.py'],
            'priority': 'HIGH',
            'estimation_hours': 8,
            'depends_on': ['BE-06'],
            'state': 'IN_PROGRESS'
        }

    @pytest.fixture
    def mock_prompt_template(self):
        """Mock prompt template for testing."""
        return """# Backend Agent Prompt

## Task: {title}

**Description:** {task_description}

**Context:**
{context}

**Artifacts to create:**
{artefacts}

**Priority:** {priority}
**Estimation:** {estimation_hours} hours
"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_get_task_context_with_valid_task(self, mock_task_metadata):
        """Test context retrieval for a valid task with context_topics."""
        with patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task, \
                patch('orchestration.generate_prompt.MemoryEngine') as mock_memory_engine:

            # Setup mocks
            mock_load_task.return_value = mock_task_metadata
            mock_engine_instance = MagicMock()
            mock_engine_instance.build_focused_context.return_value = "Mocked context about backend APIs and databases"
            mock_memory_engine.return_value = mock_engine_instance

            # Test context retrieval
            context = get_task_context('BE-07')

            # Assertions
            assert context == "Mocked context about backend APIs and databases"
            mock_load_task.assert_called_once_with('BE-07')
            mock_engine_instance.build_focused_context.assert_called_once_with(
                context_topics=['backend', 'api', 'database'],
                max_tokens=2000,
                max_per_topic=2,
                task_id='BE-07',
                agent_role="system"
            )

    def test_get_task_context_without_context_topics(self):
        """Test context retrieval for task without context_topics."""
        mock_metadata = {
            'task_id': 'BE-08',
            'title': 'Task without context topics',
            'description': 'Simple task'
        }

        with patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task:
            mock_load_task.return_value = mock_metadata

            context = get_task_context('BE-08')

            assert "No context_topics defined for task BE-08" in context
            mock_load_task.assert_called_once_with('BE-08')

    def test_get_task_context_file_not_found(self):
        """Test context retrieval when task file doesn't exist."""
        with patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task:
            mock_load_task.side_effect = FileNotFoundError(
                "Task file not found")

            context = get_task_context('NONEXISTENT')

            assert "Task metadata not found for NONEXISTENT" in context

    def test_generate_prompt_success(
            self,
            mock_task_metadata,
            mock_prompt_template,
            temp_dir):
        """Test successful prompt generation with all components."""
        with patch('orchestration.generate_prompt.load_prompt_template') as mock_load_template, \
                patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task, \
                patch('orchestration.generate_prompt.get_task_context') as mock_get_context, \
                patch('orchestration.generate_prompt.format_prompt_with_context') as mock_format, \
                patch('builtins.open', mock_open()) as mock_file, \
                patch('os.makedirs') as mock_makedirs:

            # Setup mocks
            mock_load_template.return_value = mock_prompt_template
            mock_load_task.return_value = mock_task_metadata
            mock_get_context.return_value = "Generated context about backend development"
            mock_format.return_value = "Formatted prompt with context"

            # Test prompt generation
            output_path = os.path.join(temp_dir, "test_prompt.md")
            result = generate_prompt('BE-07', 'backend-agent', output_path)

            # Assertions
            assert result == "Formatted prompt with context"
            mock_load_template.assert_called_once_with(
                "prompts/backend-agent.md")
            mock_load_task.assert_called_once_with('BE-07')
            mock_get_context.assert_called_once_with('BE-07')

            # Verify template variables passed to format function
            mock_format.assert_called_once()
            call_args = mock_format.call_args
            # Third argument contains template_vars
            template_vars = call_args[0][2]

            assert template_vars['context'] == "Generated context about backend development"
            assert template_vars['task_description'] == 'Implement test backend functionality'
            assert template_vars['task_id'] == 'BE-07'
            assert template_vars['title'] == 'Test Backend Task'
            assert template_vars['priority'] == 'HIGH'
            assert template_vars['estimation_hours'] == 8

            # Verify file operations
            mock_makedirs.assert_called_once()
            mock_file.assert_called_once_with(
                output_path, "w", encoding="utf-8")

    def test_generate_prompt_default_output_path(
            self, mock_task_metadata, mock_prompt_template):
        """Test prompt generation with default output path."""
        with patch('orchestration.generate_prompt.load_prompt_template') as mock_load_template, \
                patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task, \
                patch('orchestration.generate_prompt.get_task_context') as mock_get_context, \
                patch('orchestration.generate_prompt.format_prompt_with_context') as mock_format, \
                patch('builtins.open', mock_open()) as mock_file, \
                patch('os.makedirs') as mock_makedirs:

            # Setup mocks
            mock_load_template.return_value = mock_prompt_template
            mock_load_task.return_value = mock_task_metadata
            mock_get_context.return_value = "Test context"
            mock_format.return_value = "Formatted prompt"

            # Test with default output path
            generate_prompt('BE-07', 'backend-agent')

            # Verify default output path is used
            expected_path = "outputs/BE-07/prompt_backend.md"
            mock_file.assert_called_once_with(
                expected_path, "w", encoding="utf-8")

    def test_generate_prompt_template_not_found(self, mock_task_metadata):
        """Test prompt generation when template file doesn't exist."""
        with patch('orchestration.generate_prompt.load_prompt_template') as mock_load_template, \
                patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task:

            mock_load_template.side_effect = FileNotFoundError(
                "Template not found")
            mock_load_task.return_value = mock_task_metadata

            with pytest.raises(FileNotFoundError, match="Prompt template not found"):
                generate_prompt('BE-07', 'nonexistent-agent')

    def test_generate_prompt_task_metadata_not_found(
            self, mock_prompt_template):
        """Test prompt generation when task metadata doesn't exist."""
        with patch('orchestration.generate_prompt.load_prompt_template') as mock_load_template, \
                patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task:

            mock_load_template.return_value = mock_prompt_template
            mock_load_task.side_effect = FileNotFoundError(
                "Task metadata not found")

            with pytest.raises(FileNotFoundError, match="Task metadata file not found"):
                generate_prompt('NONEXISTENT', 'backend-agent')

    def test_agent_id_normalization(
            self,
            mock_task_metadata,
            mock_prompt_template):
        """Test that agent IDs are properly normalized with .md extension."""
        with patch('orchestration.generate_prompt.load_prompt_template') as mock_load_template, \
                patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task, \
                patch('orchestration.generate_prompt.get_task_context') as mock_get_context, \
                patch('orchestration.generate_prompt.format_prompt_with_context') as mock_format, \
                patch('builtins.open', mock_open()), \
                patch('os.makedirs'):

            # Setup mocks
            mock_load_template.return_value = mock_prompt_template
            mock_load_task.return_value = mock_task_metadata
            mock_get_context.return_value = "Test context"
            mock_format.return_value = "Formatted prompt"

            # Test with agent ID without .md extension
            generate_prompt('BE-07', 'backend-agent')

            # Verify .md extension is added
            mock_load_template.assert_called_once_with(
                "prompts/backend-agent.md")

    @pytest.mark.parametrize("agent_input,expected_template", [
        ("backend-agent", "prompts/backend-agent.md"),
        ("backend-agent.md", "prompts/backend-agent.md"),
        ("frontend", "prompts/frontend.md"),
        ("qa.md", "prompts/qa.md")
    ])
    def test_agent_template_path_generation(
            self,
            agent_input,
            expected_template,
            mock_task_metadata,
            mock_prompt_template):
        """Test various agent ID inputs generate correct template paths."""
        with patch('orchestration.generate_prompt.load_prompt_template') as mock_load_template, \
                patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task, \
                patch('orchestration.generate_prompt.get_task_context') as mock_get_context, \
                patch('orchestration.generate_prompt.format_prompt_with_context') as mock_format, \
                patch('builtins.open', mock_open()), \
                patch('os.makedirs'):

            # Setup mocks
            mock_load_template.return_value = mock_prompt_template
            mock_load_task.return_value = mock_task_metadata
            mock_get_context.return_value = "Test context"
            mock_format.return_value = "Formatted prompt"

            generate_prompt('BE-07', agent_input)

            mock_load_template.assert_called_once_with(expected_template)


class TestStep42CLI:
    """Test suite for Step 4.2 CLI interface."""

    def test_cli_with_positional_arguments(self):
        """Test CLI with positional arguments."""
        with patch('orchestration.generate_prompt.generate_prompt') as mock_generate, \
                patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task, \
                patch('sys.argv', ['generate_prompt.py', 'BE-07', 'backend-agent']):

            mock_generate.return_value = "Generated prompt"
            mock_load_task.return_value = {'title': 'Test Task'}

            # This would normally call main(), but we'll test argument parsing
            import argparse

            from orchestration.generate_prompt import main

            # Mock sys.exit to prevent actual exit
            with patch('sys.exit'):
                try:
                    main()
                    mock_generate.assert_called_once_with(
                        'BE-07', 'backend-agent', None)
                except SystemExit:
                    pass  # Expected for successful completion

    def test_cli_with_named_arguments(self):
        """Test CLI with named arguments."""
        with patch('orchestration.generate_prompt.generate_prompt') as mock_generate, \
                patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task, \
                patch('sys.argv', ['generate_prompt.py', '--task', 'BE-07', '--agent', 'backend-agent']):

            mock_generate.return_value = "Generated prompt"
            mock_load_task.return_value = {'title': 'Test Task'}

            with patch('sys.exit'):
                try:
                    main()
                    mock_generate.assert_called_once_with(
                        'BE-07', 'backend-agent', None)
                except SystemExit:
                    pass

    def test_cli_missing_task_id(self):
        """Test CLI error when task ID is missing."""
        with patch('sys.argv', ['generate_prompt.py']), \
                patch('sys.exit') as mock_exit:

            main()
            # Accept any nonzero exit code (argparse uses 2 for argument
            # errors)
            exit_calls = [call.args[0] for call in mock_exit.call_args_list]
            assert any(
                code != 0 for code in exit_calls), f"Expected sys.exit to be called with nonzero code, got: {exit_calls}"

    def test_cli_with_custom_output_path(self):
        """Test CLI with custom output path."""
        with patch('orchestration.generate_prompt.generate_prompt') as mock_generate, \
                patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task, \
                patch('sys.argv', ['generate_prompt.py', 'BE-07', 'backend-agent', '--output', 'custom/path.md']):

            mock_generate.return_value = "Generated prompt"
            mock_load_task.return_value = {'title': 'Test Task'}

            with patch('sys.exit'):
                try:
                    main()
                    mock_generate.assert_called_once_with(
                        'BE-07', 'backend-agent', 'custom/path.md')
                except SystemExit:
                    pass


class TestStep42Integration:
    """Integration tests for Step 4.2 with real components."""

    def test_end_to_end_prompt_generation(self, tmp_path):
        """Test end-to-end prompt generation with temporary files."""
        # Create temporary task file
        task_file = tmp_path / "BE-TEST.yaml"
        task_file.write_text("""
task_id: BE-TEST
title: Integration Test Task
description: Test task for integration testing
context_topics:
  - testing
  - integration
artefacts:
  - test_file.py
priority: HIGH
estimation_hours: 4
state: PLANNED
""")

        # Create temporary prompt template
        prompt_file = tmp_path / "test-agent.md"
        prompt_file.write_text("""
# Test Agent Prompt

## Task: {title}
**Description:** {task_description}
**Context:** {context}
**Files:** {artefacts}
""")

        # Create output directory
        output_dir = tmp_path / "outputs" / "BE-TEST"
        output_dir.mkdir(parents=True)
        output_path = output_dir / "prompt_test.md"

        with patch('orchestration.generate_prompt.load_task_metadata') as mock_load_task, \
                patch('orchestration.generate_prompt.load_prompt_template') as mock_load_template, \
                patch('orchestration.generate_prompt.get_task_context') as mock_get_context:

            # Setup mocks to return our test data
            mock_load_task.return_value = {
                'task_id': 'BE-TEST',
                'title': 'Integration Test Task',
                'description': 'Test task for integration testing',
                'context_topics': ['testing', 'integration'],
                'artefacts': ['test_file.py'],
                'priority': 'HIGH',
                'estimation_hours': 4,
                'state': 'PLANNED'
            }
            mock_load_template.return_value = prompt_file.read_text()
            mock_get_context.return_value = "Integration testing context with mock MCP data"

            # Generate prompt
            result = generate_prompt('BE-TEST', 'test-agent', str(output_path))

            # Verify output file exists and contains expected content
            assert output_path.exists()
            generated_content = output_path.read_text()

            assert "Integration Test Task" in generated_content
            assert "Test task for integration testing" in generated_content
            assert "Integration testing context with mock MCP data" in generated_content
            assert "test_file.py" in generated_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
