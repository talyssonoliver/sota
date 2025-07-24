"""
Real tests for register output workflow.
Tests the AgentOutputRegistry and RegistrationResult classes to achieve proper code coverage.
"""

import tempfile
import pytest
from pathlib import Path
from src.core.workflows.register_output import AgentOutputRegistry, RegistrationResult


class TestRegistrationResult:
    """Real tests for RegistrationResult class."""

    def test_registration_result_init(self):
        """Test RegistrationResult initialization with keyword arguments."""
        result = RegistrationResult(
            task_id="BE-07",
            agent_id="backend_agent", 
            status="success",
            file_count=3
        )
        
        assert result.task_id == "BE-07"
        assert result.agent_id == "backend_agent"
        assert result.status == "success"
        assert result.file_count == 3

    def test_registration_result_empty_init(self):
        """Test RegistrationResult with no arguments."""
        result = RegistrationResult()
        # Should create empty object without errors
        assert result is not None

    def test_registration_result_dynamic_attributes(self):
        """Test that RegistrationResult accepts arbitrary attributes."""
        result = RegistrationResult(
            custom_field="custom_value",
            another_field=42,
            complex_data={"nested": "value"}
        )
        
        assert result.custom_field == "custom_value"
        assert result.another_field == 42
        assert result.complex_data == {"nested": "value"}


class TestAgentOutputRegistry:
    """Real tests for AgentOutputRegistry class."""

    def setup_method(self):
        """Set up test fixture."""
        self.registry = AgentOutputRegistry()

    def test_registry_initialization_default(self):
        """Test AgentOutputRegistry initialization with defaults."""
        registry = AgentOutputRegistry()
        assert registry.outputs == {}
        assert registry.base_outputs_dir == "outputs"

    def test_registry_initialization_custom_dir(self):
        """Test AgentOutputRegistry initialization with custom directory."""
        custom_dir = "/tmp/custom_outputs"
        registry = AgentOutputRegistry(base_outputs_dir=custom_dir)
        assert registry.base_outputs_dir == custom_dir
        assert registry.outputs == {}

    def test_register_basic(self):
        """Test basic output registration."""
        task_id = "BE-07"
        output_data = {"status": "completed", "files": ["file1.py", "file2.py"]}
        
        result = self.registry.register(task_id, output_data)
        
        assert result["task_id"] == task_id
        assert result["output"] == output_data
        assert result["status"] == "registered"
        
        # Verify it's stored in registry
        assert self.registry.outputs[task_id] == output_data

    def test_register_multiple_tasks(self):
        """Test registering multiple tasks."""
        tasks = [
            ("BE-07", {"status": "completed"}),
            ("FE-123", {"status": "in_progress"}),
            ("QA-001", {"status": "failed"})
        ]
        
        for task_id, output in tasks:
            result = self.registry.register(task_id, output)
            assert result["status"] == "registered"
        
        # Verify all are stored
        assert len(self.registry.outputs) == 3
        assert self.registry.outputs["BE-07"]["status"] == "completed"
        assert self.registry.outputs["FE-123"]["status"] == "in_progress"
        assert self.registry.outputs["QA-001"]["status"] == "failed"

    def test_get_output_existing(self):
        """Test getting existing output."""
        task_id = "BE-07"
        output_data = {"status": "completed"}
        
        # Register first
        self.registry.register(task_id, output_data)
        
        # Then retrieve
        retrieved = self.registry.get_output(task_id)
        assert retrieved == output_data

    def test_get_output_nonexistent(self):
        """Test getting non-existent output."""
        result = self.registry.get_output("NON-EXISTENT")
        assert result is None

    def test_register_output_with_temp_file(self):
        """Test register_output method with temporary file."""
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_file.write('{"test": "data"}')
            tmp_path = tmp_file.name
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            registry = AgentOutputRegistry(base_outputs_dir=temp_dir)
            
            try:
                result = registry.register_output(
                    task_id="BE-07",
                    agent_id="test_agent", 
                    source_path=tmp_path,
                    output_type="json",
                    metadata={"version": "1.0"}
                )
                
                # Verify result has expected attributes
                assert result.task_id == "BE-07"
                assert result.agent_id == "test_agent"
                assert result.output_type == "json"
                assert result.metadata == {"version": "1.0"}
                
                # Verify file was copied to target directory
                target_dir = Path(temp_dir) / "BE-07"
                assert target_dir.exists()
                
                source_filename = Path(tmp_path).name
                target_file = target_dir / source_filename
                assert target_file.exists()
                
            finally:
                # Clean up temporary file
                Path(tmp_path).unlink(missing_ok=True)

    def test_register_output_nonexistent_file(self):
        """Test register_output with non-existent source file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            registry = AgentOutputRegistry(base_outputs_dir=temp_dir)
            
            result = registry.register_output(
                task_id="BE-07",
                agent_id="test_agent",
                source_path="/nonexistent/path/file.json",
                output_type="json"
            )
            
            # Should still create result object
            assert result.task_id == "BE-07"
            assert result.agent_id == "test_agent"
            assert result.file_size == 0  # File doesn't exist

    def test_register_output_creates_directory(self):
        """Test that register_output creates target directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            registry = AgentOutputRegistry(base_outputs_dir=temp_dir)
            
            # Create a temporary source file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write("test content")
                tmp_path = tmp_file.name
            
            try:
                registry.register_output(
                    task_id="NEW-TASK",
                    agent_id="test_agent",
                    source_path=tmp_path
                )
                
                # Verify target directory was created
                target_dir = Path(temp_dir) / "NEW-TASK"
                assert target_dir.exists()
                assert target_dir.is_dir()
                
            finally:
                Path(tmp_path).unlink(missing_ok=True)

    def test_registry_overwrite_existing(self):
        """Test overwriting existing registry entry."""
        task_id = "BE-07"
        
        # Register initial output
        initial_output = {"status": "in_progress"}
        self.registry.register(task_id, initial_output)
        
        # Register new output with same task_id
        final_output = {"status": "completed", "files": ["output.json"]}
        result = self.registry.register(task_id, final_output)
        
        # Should overwrite and return new data
        assert result["output"] == final_output
        assert self.registry.get_output(task_id) == final_output
        assert self.registry.get_output(task_id) != initial_output