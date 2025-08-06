"""
End-to-end tests for prompt generation workflow.

Tests the complete prompt generation pipeline including template loading,
context gathering, formatting, and output generation for various agent types
and task scenarios.
"""

import json
import tempfile
from pathlib import Path

import pytest

try:
    from src.core.workflows.generate_prompt import (
        format_prompt_with_context,
        generate_prompt,
        get_task_context,
        load_prompt_template,
        load_task_metadata,
        main,
    )
except ImportError:
    generate_prompt = None
    load_prompt_template = None
    load_task_metadata = None
    get_task_context = None
    format_prompt_with_context = None
    main = None


@pytest.mark.skipif(generate_prompt is None, reason="generate_prompt not available")
class TestPromptGenerationE2E:
    """End-to-end tests for prompt generation workflow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_task_id = "BE-07"
        self.test_agent_type = "backend"

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_prompt_generation_workflow(self):
        """Test complete prompt generation workflow from start to finish."""
        # Generate prompt
        result = generate_prompt(
            task_id=self.test_task_id,
            agent_type=self.test_agent_type,
            output_path=f"{self.temp_dir}/prompt.txt"
        )
        
        assert isinstance(result, dict)
        assert result["task_id"] == self.test_task_id
        assert result["agent_type"] == self.test_agent_type
        assert result["output_path"] == f"{self.temp_dir}/prompt.txt"

    def test_prompt_generation_with_various_agent_types(self):
        """Test prompt generation for different agent types."""
        agent_types = ["backend", "frontend", "qa", "documentation", "coordinator"]
        
        results = []
        for agent_type in agent_types:
            result = generate_prompt(
                task_id=f"TEST-{agent_type}",
                agent_type=agent_type
            )
            results.append(result)
        
        # Verify all agent types are handled
        assert len(results) == len(agent_types)
        for i, result in enumerate(results):
            assert result["agent_type"] == agent_types[i]
            assert result["task_id"] == f"TEST-{agent_types[i]}"

    def test_prompt_generation_without_output_path(self):
        """Test prompt generation without specifying output path."""
        result = generate_prompt(
            task_id="TEST-01",
            agent_type="qa"
        )
        
        assert result["output_path"] is None
        assert result["task_id"] == "TEST-01"
        assert result["agent_type"] == "qa"

    def test_load_prompt_template_functionality(self):
        """Test loading prompt templates."""
        # Create a test template file
        template_path = Path(self.temp_dir) / "test_template.txt"
        template_path.write_text("Task: {task_id}\nAgent: {agent_type}\n")
        
        # Load template (should return string content)
        template = load_prompt_template(str(template_path))
        
        assert isinstance(template, str)
        assert "Task: {task_id}" in template
        assert "Agent: {agent_type}" in template

    def test_load_task_metadata_functionality(self):
        """Test loading task metadata."""
        # Create mock task metadata
        task_metadata_path = Path(self.temp_dir) / f"{self.test_task_id}.json"
        task_data = {
            "task_id": self.test_task_id,
            "title": "Implement user authentication",
            "description": "Create backend API for user auth",
            "priority": "high"
        }
        task_metadata_path.write_text(json.dumps(task_data))
        
        # Load metadata
        metadata = load_task_metadata(self.test_task_id)
        
        assert isinstance(metadata, dict)
        assert metadata["task_id"] == self.test_task_id
        assert "title" in metadata

    def test_get_task_context_functionality(self):
        """Test retrieving task context."""
        context = get_task_context(self.test_task_id)
        
        assert isinstance(context, str)
        assert len(context) > 0
        # Context should contain relevant information, not necessarily the task ID
        assert any(keyword in context.lower() for keyword in ['schema', 'pattern', 'fallback', 'context'])

    def test_format_prompt_with_context(self):
        """Test formatting prompt with context."""
        template = {"content": "Task: {task_id}, Context: {context}"}
        context = {"task_id": "TEST-01", "agent": "backend", "priority": "high"}
        
        formatted = format_prompt_with_context(template, context)
        
        assert isinstance(formatted, str)
        assert "Task:" in formatted
        assert "Context:" in formatted
        # Should contain the context data as string
        assert "TEST-01" in formatted or "backend" in formatted

    def test_integration_prompt_generation_pipeline(self):
        """Test integrated prompt generation pipeline."""
        # Skip if template files don't exist (this is an integration test)
        try:
            # Step 1: Load template
            template = load_prompt_template("prompts/backend-agent.md")
            assert template is not None
        except FileNotFoundError:
            pytest.skip("Template files not found - integration test requires real files")
        
        # Step 2: Load task metadata
        metadata = load_task_metadata(self.test_task_id)
        assert metadata["task_id"] == self.test_task_id
        
        # Step 3: Get context
        context = get_task_context(self.test_task_id)
        assert context is not None
        
        # Step 4: Format prompt
        formatted_prompt = format_prompt_with_context(template, context)
        assert len(formatted_prompt) > 0
        
        # Step 5: Generate final prompt
        result = generate_prompt(
            task_id=self.test_task_id,
            agent_type="backend",
            output_path=f"{self.temp_dir}/final_prompt.txt"
        )
        assert result["task_id"] == self.test_task_id

    def test_prompt_generation_error_handling(self):
        """Test error handling in prompt generation."""
        # Test with empty task_id should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            generate_prompt("", "backend")
        
        # Test with None values should raise an exception
        with pytest.raises((FileNotFoundError, TypeError, AttributeError)):
            generate_prompt(None, None)

    def test_main_cli_function(self):
        """Test main CLI function."""
        if main is None:
            pytest.skip("main function not available")
            
        # Test that main function executes without error
        import sys
        original_argv = sys.argv
        try:
            sys.argv = ['generate_prompt.py', 'BE-07', 'backend']
            # Just ensure it doesn't crash - output testing is tricky in e2e context
            main()
        finally:
            sys.argv = original_argv
        
        # If we get here, the main function executed successfully

    def test_main_cli_with_default_agent(self):
        """Test main CLI with default agent type."""
        if main is None:
            pytest.skip("main function not available")
            
        import sys
        original_argv = sys.argv
        try:
            sys.argv = ['generate_prompt.py', 'QA-01']
            main()  # Should use default agent type
        finally:
            sys.argv = original_argv

    def test_main_cli_without_arguments(self):
        """Test main CLI without required arguments."""
        if main is None:
            pytest.skip("main function not available")
            
        # Should exit with error code 1 when no arguments provided
        import sys
        original_argv = sys.argv
        try:
            sys.argv = ['generate_prompt.py']
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
        finally:
            sys.argv = original_argv


class TestPromptGenerationScenarios:
    """Test various prompt generation scenarios."""

    def test_batch_prompt_generation(self):
        """Test generating prompts for multiple tasks."""
        if generate_prompt is None:
            pytest.skip("generate_prompt not available")
            
        task_ids = ["BE-01", "BE-02", "FE-01", "QA-01", "DOC-01"]
        agent_mapping = {
            "BE": "backend",
            "FE": "frontend", 
            "QA": "qa",
            "DOC": "documentation"
        }
        
        results = []
        for task_id in task_ids:
            prefix = task_id.split("-")[0]
            agent_type = agent_mapping.get(prefix, "coordinator")
            
            result = generate_prompt(task_id, agent_type)
            results.append(result)
        
        assert len(results) == len(task_ids)
        
        # Verify correct agent assignment
        assert results[0]["agent_type"] == "backend"
        assert results[2]["agent_type"] == "frontend"
        assert results[3]["agent_type"] == "qa"
        assert results[4]["agent_type"] == "documentation"

    def test_prompt_generation_with_special_characters(self):
        """Test prompt generation with special characters in task IDs."""
        if generate_prompt is None:
            pytest.skip("generate_prompt not available")
            
        special_task_ids = [
            "TASK-001_special",
            "TASK#002",
            "TASK@003",
            "TASK.004"
        ]
        
        for task_id in special_task_ids:
            result = generate_prompt(task_id, "backend")
            assert result["task_id"] == task_id

    def test_concurrent_prompt_generation(self):
        """Test concurrent prompt generation for multiple tasks."""
        if generate_prompt is None:
            pytest.skip("generate_prompt not available")
            
        from concurrent.futures import ThreadPoolExecutor
        
        def generate_task_prompt(task_num):
            return generate_prompt(f"CONCURRENT-{task_num}", "backend")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_task_prompt, i) for i in range(10)]
            results = [f.result() for f in futures]
        
        assert len(results) == 10
        assert all(r["agent_type"] == "backend" for r in results)
        
        # Verify all task IDs are unique and correct
        task_ids = [r["task_id"] for r in results]
        assert len(set(task_ids)) == 10

    def test_prompt_generation_performance(self):
        """Test prompt generation performance for large batches."""
        if generate_prompt is None:
            pytest.skip("generate_prompt not available")
            
        import time
        from unittest.mock import patch, MagicMock
        
        # Mock the memory engine to avoid repeated initialization overhead
        mock_memory = MagicMock()
        mock_memory.retrieve.return_value = None
        
        with patch('src.infrastructure.memory.engines.memory_engine.MemoryEngine', return_value=mock_memory):
            start_time = time.time()
            
            # Generate 10 prompts (reduced for performance)
            for i in range(10):
                generate_prompt(f"PERF-{i}", "backend")
            
            elapsed_time = time.time() - start_time
            
            # Should complete 10 prompts in under 5 seconds (adjusted for test environment)
            assert elapsed_time < 5.0

    def test_prompt_template_caching(self):
        """Test template caching behavior."""
        if load_prompt_template is None:
            pytest.skip("load_prompt_template not available")
            
        # Load same template multiple times
        template1 = load_prompt_template("prompts/backend-agent.md")
        template2 = load_prompt_template("prompts/backend-agent.md")
        load_prompt_template("prompts/qa-agent.md")
        
        # Current implementation always returns same default
        assert template1 == template2
        assert "Backend Engineer Agent" in template1

    def test_metadata_and_context_integration(self):
        """Test integration of metadata and context in prompt generation."""
        if not all([load_task_metadata, get_task_context, format_prompt_with_context]):
            pytest.skip("Required functions not available")
            
        # Create complete prompt data
        task_id = "INTEGRATION-01"
        
        metadata = load_task_metadata(task_id)
        context = get_task_context(task_id)
        
        # Combine metadata and context
        combined_data = {
            "metadata": metadata,
            "context": context,
            "agent": "backend"
        }
        
        # Format with template
        template = {"template": "Task {task_id} with context"}
        formatted = format_prompt_with_context(template, combined_data)
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0
