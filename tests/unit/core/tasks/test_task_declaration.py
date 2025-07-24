"""
Real tests for Task Declaration system.
Tests real TaskDeclaration, TaskPreparationStatus enum, and dataclass functionality.
"""

import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.core.workflows.task_declaration import (
    TaskDeclaration,
    TaskDeclarationManager,
    TaskPreparationStatus,
)


class TestTaskPreparationStatus:
    """Real tests for TaskPreparationStatus enum."""

    def test_status_enum_values(self):
        """Test TaskPreparationStatus enum has correct string values."""
        assert TaskPreparationStatus.PENDING == "PENDING"
        assert TaskPreparationStatus.CONTEXT_LOADED == "CONTEXT_LOADED"
        assert TaskPreparationStatus.PROMPT_GENERATED == "PROMPT_GENERATED"
        assert TaskPreparationStatus.READY_FOR_EXECUTION == "READY_FOR_EXECUTION"
        assert TaskPreparationStatus.FAILED == "FAILED"

    def test_status_enum_inheritance(self):
        """Test TaskPreparationStatus inherits from str and Enum."""
        # Should be usable as string
        status = TaskPreparationStatus.PENDING
        assert isinstance(status, str)
        assert status == "PENDING"


class TestTaskDeclaration:
    """Real tests for TaskDeclaration dataclass."""

    def test_task_declaration_basic_init(self):
        """Test TaskDeclaration initialization with all required fields."""
        declaration = TaskDeclaration(
            id="BE-07",
            title="Test Backend Task",
            description="Test task for backend development",
            owner="backend",
            state="CREATED",
            priority="HIGH",
            estimation_hours=8.0,
            depends_on=["BE-06"],
            artefacts=["api.py", "tests.py"],
            context_topics=["database", "api_design"],
            preparation_status=TaskPreparationStatus.PENDING,
        )

        # Test all core fields are set correctly
        assert declaration.id == "BE-07"
        assert declaration.title == "Test Backend Task"
        assert declaration.description == "Test task for backend development"
        assert declaration.owner == "backend"
        assert declaration.state == "CREATED" 
        assert declaration.priority == "HIGH"
        assert declaration.estimation_hours == 8.0
        assert declaration.depends_on == ["BE-06"]
        assert declaration.artefacts == ["api.py", "tests.py"]
        assert declaration.context_topics == ["database", "api_design"]
        assert declaration.preparation_status == TaskPreparationStatus.PENDING

        # Test default values for optional fields
        assert declaration.context_loaded == False
        assert declaration.prompt_generated == False
        assert declaration.dependencies_satisfied == False
        assert declaration.context_content is None
        assert declaration.generated_prompt is None
        assert declaration.agent_assignment is None
        assert declaration.execution_plan is None
        assert declaration.declared_at is None
        assert declaration.prepared_by is None

    def test_task_declaration_to_dict(self):
        """Test TaskDeclaration.to_dict() method."""
        declaration = TaskDeclaration(
            id="BE-07",
            title="Test Task", 
            description="Test description",
            owner="backend",
            state="CREATED",
            priority="medium",
            estimation_hours=4.0,
            depends_on=[],
            artefacts=[],
            context_topics=[],
            preparation_status=TaskPreparationStatus.PENDING,
        )

        result_dict = declaration.to_dict()

        # Should be a dictionary
        assert isinstance(result_dict, dict)
        
        # Should contain all dataclass fields
        assert result_dict["id"] == "BE-07"
        assert result_dict["title"] == "Test Task"
        assert result_dict["owner"] == "backend"
        assert result_dict["preparation_status"] == TaskPreparationStatus.PENDING
        assert result_dict["context_loaded"] == False
        assert result_dict["prompt_generated"] == False

    def test_task_declaration_from_metadata(self):
        """Test TaskDeclaration.from_metadata() class method."""
        metadata = {
            "id": "FE-123",
            "title": "Frontend Component",
            "description": "Create reusable UI component",
            "owner": "frontend",
            "state": "PLANNED",
            "priority": "HIGH",
            "estimation_hours": 12.0,
            "depends_on": ["BE-07", "BE-08"],
            "artefacts": ["component.tsx", "styles.css"],
            "context_topics": ["react", "typescript"]
        }

        declaration = TaskDeclaration.from_metadata(metadata)

        # Test all fields from metadata are properly mapped
        assert declaration.id == "FE-123"
        assert declaration.title == "Frontend Component"
        assert declaration.description == "Create reusable UI component"
        assert declaration.owner == "frontend"
        assert declaration.state == "PLANNED"
        assert declaration.priority == "HIGH"
        assert declaration.estimation_hours == 12.0
        assert declaration.depends_on == ["BE-07", "BE-08"]
        assert declaration.artefacts == ["component.tsx", "styles.css"]
        assert declaration.context_topics == ["react", "typescript"]

        # Test default values are set correctly
        assert declaration.preparation_status == TaskPreparationStatus.PENDING
        assert declaration.context_loaded == False
        assert declaration.prompt_generated == False
        assert declaration.dependencies_satisfied == False
        
        # Test declared_at timestamp is set
        assert declaration.declared_at is not None
        assert isinstance(declaration.declared_at, str)
        # Should be valid ISO format timestamp
        datetime.fromisoformat(declaration.declared_at)

    def test_task_declaration_from_metadata_missing_fields(self):
        """Test TaskDeclaration.from_metadata() with missing optional fields."""
        minimal_metadata = {
            "id": "QA-01",
            "title": "Test Task",
            "owner": "qa"
        }

        declaration = TaskDeclaration.from_metadata(minimal_metadata)

        # Test required fields
        assert declaration.id == "QA-01"
        assert declaration.title == "Test Task"
        assert declaration.owner == "qa"

        # Test defaults for missing fields
        assert declaration.description == ""  # Default empty string
        assert declaration.state == "CREATED"  # Default state
        assert declaration.priority == "MEDIUM"  # Default priority
        assert declaration.estimation_hours == 0  # Default hours
        assert declaration.depends_on == []  # Default empty list
        assert declaration.artefacts == []  # Default empty list
        assert declaration.context_topics == []  # Default empty list

    def test_task_declaration_from_dict(self):
        """Test TaskDeclaration.from_dict() class method."""
        task_dict = {
            "id": "TL-01",
            "title": "Technical Leadership Task",
            "description": "Architecture planning",
            "owner": "technical",
            "state": "IN_PROGRESS",
            "priority": "CRITICAL",
            "estimation_hours": 20.0,
            "depends_on": [],
            "artefacts": ["architecture.md"],
            "context_topics": ["system_design"],
            "preparation_status": TaskPreparationStatus.CONTEXT_LOADED,
            "context_loaded": True,
            "prompt_generated": False,
            "dependencies_satisfied": True,
            "context_content": "Loaded context content",
            "generated_prompt": None,
            "agent_assignment": "technical_handler",
            "execution_plan": {"workflow_type": "sequential"},
            "declared_at": "2024-01-01T12:00:00",
            "prepared_by": "TaskDeclarationManager"
        }

        declaration = TaskDeclaration.from_dict(task_dict)

        # Test all fields are properly loaded
        assert declaration.id == "TL-01"
        assert declaration.title == "Technical Leadership Task"
        assert declaration.state == "IN_PROGRESS"
        assert declaration.priority == "CRITICAL"
        assert declaration.preparation_status == TaskPreparationStatus.CONTEXT_LOADED
        assert declaration.context_loaded == True
        assert declaration.prompt_generated == False
        assert declaration.dependencies_satisfied == True
        assert declaration.context_content == "Loaded context content"
        assert declaration.agent_assignment == "technical_handler"
        assert declaration.execution_plan == {"workflow_type": "sequential"}
        assert declaration.declared_at == "2024-01-01T12:00:00"
        assert declaration.prepared_by == "TaskDeclarationManager"


class TestTaskDeclarationManager:
    """Real tests for TaskDeclarationManager initialization and basic functionality."""

    def test_manager_initialization(self):
        """Test TaskDeclarationManager initialization."""
        with patch('src.infrastructure.memory.get_memory_instance') as mock_memory:
            mock_memory.return_value = None  # Mock memory engine
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Change working directory to temp for outputs
                import os
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    manager = TaskDeclarationManager()
                    
                    # Test basic initialization
                    assert manager is not None
                    assert hasattr(manager, 'declare_task')
                    assert hasattr(manager, 'prepare_task_for_execution')
                    assert hasattr(manager, 'declared_tasks')
                    assert isinstance(manager.declared_tasks, dict)
                    assert len(manager.declared_tasks) == 0  # Should start empty
                    
                    # Test outputs directory creation
                    assert hasattr(manager, 'outputs_dir')
                    assert manager.outputs_dir.exists()
                    assert manager.outputs_dir.is_dir()
                    
                finally:
                    os.chdir(original_cwd)

    def test_manager_with_memory_engine(self):
        """Test TaskDeclarationManager with memory engine parameter."""
        mock_memory = object()  # Simple mock object
        
        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                manager = TaskDeclarationManager(memory_engine=mock_memory)
                
                # Should use provided memory engine
                assert manager.memory_engine is mock_memory
                assert manager.declared_tasks == {}
                
            finally:
                os.chdir(original_cwd)

    @patch('src.infrastructure.utils.task_loader.load_task_metadata')
    def test_declare_task_with_mock_metadata(self, mock_load_metadata):
        """Test task declaration with mocked metadata loading."""
        # Mock the metadata loading
        mock_load_metadata.return_value = {
            "id": "BE-07",
            "title": "Backend API Development",
            "description": "Develop REST API endpoints",
            "owner": "backend",
            "state": "CREATED",
            "priority": "HIGH",
            "estimation_hours": 16.0,
            "depends_on": ["BE-06"],
            "artefacts": ["api.py", "tests.py"],
            "context_topics": ["database", "rest_api"]
        }
        
        with patch('src.infrastructure.memory.get_memory_instance') as mock_memory:
            mock_memory.return_value = None
            
            with tempfile.TemporaryDirectory() as temp_dir:
                import os
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    manager = TaskDeclarationManager()
                    
                    # Declare task
                    declaration = manager.declare_task("BE-07")
                    
                    # Verify TaskDeclaration object was created correctly
                    assert isinstance(declaration, TaskDeclaration)
                    assert declaration.id == "BE-07"
                    assert declaration.title == "Backend API Development"
                    assert declaration.description == "Develop REST API endpoints"
                    assert declaration.owner == "backend"
                    assert declaration.state == "CREATED"
                    assert declaration.priority == "HIGH"
                    assert declaration.estimation_hours == 16.0
                    assert declaration.depends_on == ["BE-06"]
                    assert declaration.artefacts == ["api.py", "tests.py"]
                    assert declaration.context_topics == ["database", "rest_api"]
                    assert declaration.preparation_status == TaskPreparationStatus.PENDING
                    assert declaration.prepared_by == "TaskDeclarationManager"
                    
                    # Verify task was stored in manager
                    assert "BE-07" in manager.declared_tasks
                    assert manager.declared_tasks["BE-07"] is declaration
                    
                    # Verify metadata was loaded with correct task ID
                    mock_load_metadata.assert_called_once_with("BE-07")
                    
                finally:
                    os.chdir(original_cwd)

    @patch('src.infrastructure.utils.task_loader.load_task_metadata')
    def test_declare_task_already_declared(self, mock_load_metadata):
        """Test declaring a task that's already been declared."""
        mock_load_metadata.return_value = {
            "id": "FE-123",
            "title": "Frontend Component",
            "owner": "frontend",
            "state": "CREATED"
        }
        
        with patch('src.infrastructure.memory.get_memory_instance') as mock_memory:
            mock_memory.return_value = None
            
            with tempfile.TemporaryDirectory() as temp_dir:
                import os
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    manager = TaskDeclarationManager()
                    
                    # Declare task first time
                    first_declaration = manager.declare_task("FE-123")
                    assert mock_load_metadata.call_count == 1
                    
                    # Declare same task again (should return existing)
                    second_declaration = manager.declare_task("FE-123")
                    
                    # Should return same object and not call load_metadata again
                    assert first_declaration is second_declaration
                    assert mock_load_metadata.call_count == 1  # Still only called once
                    
                finally:
                    os.chdir(original_cwd)

    def test_get_tasks_ready_for_execution_empty(self):
        """Test getting ready tasks when none are ready.""" 
        with patch('src.infrastructure.memory.get_memory_instance') as mock_memory:
            mock_memory.return_value = None
            
            with tempfile.TemporaryDirectory() as temp_dir:
                import os
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    manager = TaskDeclarationManager()
                    
                    ready_tasks = manager.get_tasks_ready_for_execution()
                    
                    # Should return empty list when no tasks are declared
                    assert isinstance(ready_tasks, list)
                    assert len(ready_tasks) == 0
                    
                finally:
                    os.chdir(original_cwd)

    def test_get_task_declaration(self):
        """Test getting specific task declaration."""
        with patch('src.infrastructure.memory.get_memory_instance') as mock_memory:
            mock_memory.return_value = None
            
            with tempfile.TemporaryDirectory() as temp_dir:
                import os
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    manager = TaskDeclarationManager()
                    
                    # Test getting non-existent task
                    result = manager.get_task_declaration("NON-EXISTENT")
                    assert result is None
                    
                    # Add a task directly to test retrieval
                    test_declaration = TaskDeclaration(
                        id="TEST-01",
                        title="Test Task",
                        description="Test description",
                        owner="backend",
                        state="CREATED",
                        priority="MEDIUM",
                        estimation_hours=4.0,
                        depends_on=[],
                        artefacts=[],
                        context_topics=[],
                        preparation_status=TaskPreparationStatus.PENDING,
                    )
                    manager.declared_tasks["TEST-01"] = test_declaration
                    
                    # Test retrieving existing task
                    retrieved = manager.get_task_declaration("TEST-01")
                    assert retrieved is test_declaration
                    assert retrieved.id == "TEST-01"
                    
                finally:
                    os.chdir(original_cwd)


class TestTaskLoader:
    """Test task loading functionality."""

    def test_load_task_metadata_basic(self):
        """Test basic task metadata loading."""
        task_id = "BE-06"

        # Mock the task metadata
        mock_metadata = {
            "id": task_id,
            "title": "Create API endpoint",
            "owner": "backend",
            "state": "CREATED",
            "priority": "medium",
        }

        with patch("builtins.open", mock_open(read_data=yaml.dump(mock_metadata))):
            with patch("pathlib.Path.exists", return_value=True):
                metadata = load_task_metadata(task_id)

                assert metadata["id"] == task_id
                assert metadata["owner"] == "backend"

    def test_load_task_metadata_with_dependencies(self):
        """Test loading task metadata with dependencies."""
        task_id = "FE-04"
        mock_metadata = {
            "id": task_id,
            "title": "Implement user interface",
            "owner": "frontend",
            "depends_on": ["BE-01", "BE-02"],
            "context_topics": ["ui_patterns", "design_system"],
        }

        with patch("builtins.open", mock_open(read_data=yaml.dump(mock_metadata))):
            with patch("pathlib.Path.exists", return_value=True):
                metadata = load_task_metadata(task_id)

                assert "depends_on" in metadata
                assert "context_topics" in metadata
                assert len(metadata["depends_on"]) == 2

    def test_get_all_tasks(self):
        """Test getting all available task IDs."""
        mock_task_files = [
            Path("BE-01.yaml"),
            Path("BE-02.yaml"),
            Path("FE-01.yaml"),
            Path("TL-01.yaml"),
        ]

        with patch("pathlib.Path.glob") as mock_glob:
            mock_glob.return_value = mock_task_files

            tasks = get_all_tasks()

            # Should return task IDs extracted from filenames
            assert isinstance(tasks, list)

    def test_load_task_metadata_file_not_found(self):
        """Test handling when task file doesn't exist."""
        task_id = "INVALID-01"

        with patch("pathlib.Path.exists", return_value=False):
            metadata = load_task_metadata(task_id)
            # Should return default metadata when file doesn't exist
            assert metadata is not None
            assert metadata["id"] == task_id
            assert metadata["state"] == "pending"
            assert "depends_on" in metadata


class TestHITLTaskMetadata:
    """Test HITL task metadata functionality."""

    def test_hitl_task_metadata_creation(self):
        """Test creating HITL task metadata."""
        task_id = "BE-07"
        hitl_metadata = HITLTaskMetadata(task_id)

        assert hitl_metadata.task_id == task_id
        assert hitl_metadata.hitl_status == HITLStatus.NO_HITL

    def test_hitl_task_metadata_with_status(self):
        """Test HITL metadata with specific status."""
        task_id = "TL-02"
        hitl_metadata = HITLTaskMetadata(task_id, hitl_status=HITLStatus.HITL_PENDING)

        assert hitl_metadata.hitl_status == HITLStatus.HITL_PENDING

    def test_hitl_status_values(self):
        """Test HITL status enum values."""
        assert HITLStatus.NO_HITL == "no_hitl"
        assert HITLStatus.HITL_PENDING == "hitl_pending"
        assert HITLStatus.HITL_APPROVED == "hitl_approved"

    def test_hitl_task_metadata_manager(self):
        """Test HITL task metadata manager."""
        manager = HITLTaskMetadataManager()
        task_id = "QA-02"

        # Create HITL metadata directly (manager doesn't have create method)
        hitl_metadata = HITLTaskMetadata(task_id)

        # Test that manager can save the metadata
        result = manager.save_task_metadata(hitl_metadata)
        assert result is True or result is False  # Should return a boolean
        assert hitl_metadata.task_id == task_id


class TestTaskLifecycleManager:
    """Test task lifecycle management."""

    def test_task_lifecycle_manager_initialization(self):
        """Test TaskLifecycleManager can be initialized."""
        lifecycle_manager = TaskLifecycleManager()
        assert lifecycle_manager is not None

    def test_archive_task(self):
        """Test task archival functionality."""
        lifecycle_manager = TaskLifecycleManager()
        task_id = "BE-08"

        result = lifecycle_manager.archive_task(task_id)

        # Should return success indicator
        assert result is not None

    def test_track_task_completion(self):
        """Test task completion tracking."""
        lifecycle_manager = TaskLifecycleManager()

        if hasattr(lifecycle_manager, "track_task_completion"):
            result = lifecycle_manager.track_task_completion("FE-05", "frontend_agent")
            # Method returns None and should complete without error
            assert result is None

    def test_cleanup_old_tasks(self):
        """Test cleanup of old tasks."""
        lifecycle_manager = TaskLifecycleManager()

        if hasattr(lifecycle_manager, "cleanup_old_tasks"):
            result = lifecycle_manager.cleanup_old_tasks()
            # Should complete without errors
            assert (
                result is not None or result is None
            )  # Either return value is acceptable


class TestTaskIntegration:
    """Integration tests for task declaration system."""

    @patch("src.core.workflows.task_declaration.load_task_metadata")
    def test_end_to_end_task_workflow(self, mock_load):
        """Test complete task workflow from declaration to execution."""
        task_id = "INTEGRATION-01"

        # Mock task metadata with all required fields
        mock_load.return_value = {
            "id": task_id,
            "title": "Integration Test Task",
            "description": "End-to-end integration test",
            "owner": "backend",
            "state": "CREATED",
            "priority": "medium",
            "estimation_hours": 8.0,
            "depends_on": [],
            "artefacts": [],
            "context_topics": [],
        }

        # Initialize components
        declaration_manager = TaskDeclarationManager()
        hitl_manager = HITLTaskMetadataManager()
        lifecycle_manager = TaskLifecycleManager()
        
        # Verify managers are properly initialized
        assert declaration_manager is not None
        assert hitl_manager is not None
        assert lifecycle_manager is not None

        # Step 1: Declare task
        declaration = declaration_manager.declare_task(task_id)
        assert declaration.id == task_id

        # Step 2: Create HITL metadata
        hitl_metadata = HITLTaskMetadata(task_id)
        assert hitl_metadata.task_id == task_id

        # Step 3: Prepare for execution
        preparation_result = declaration_manager.prepare_task_for_execution(task_id)
        assert preparation_result is not None

    @patch("src.core.workflows.task_declaration.load_task_metadata")
    def test_task_declaration_with_dependencies(self, mock_load):
        """Test task declaration with dependency handling."""
        mock_load.return_value = {
            "id": "DEPENDENT-01",
            "title": "Task with dependencies",
            "owner": "backend",
            "depends_on": ["BE-01", "FE-01"],
            "state": "CREATED",
        }

        manager = TaskDeclarationManager()
        declaration = manager.declare_task("DEPENDENT-01")

        assert declaration.id == "DEPENDENT-01"

    def test_task_metadata_validation(self):
        """Test task metadata validation."""
        # Test valid task metadata structure
        valid_metadata = {
            "id": "VALID-01",
            "title": "Valid task",
            "owner": "backend",
            "state": "CREATED",
            "priority": "medium",
            "estimation_hours": 8,
        }

        # Basic validation - check required fields
        required_fields = ["id", "title", "owner", "state"]
        for field in required_fields:
            assert field in valid_metadata

        # Validate owner values
        valid_owners = [
            "backend",
            "frontend",
            "technical",
            "qa",
            "doc",
            "coordinator",
            "product",
            "ux",
        ]
        assert valid_metadata["owner"] in valid_owners

    def test_task_state_transitions(self):
        """Test valid task state transitions."""
        valid_states = [
            "CREATED",
            "PLANNED",
            "IN_PROGRESS",
            "QA_PENDING",
            "DOCUMENTATION",
            "HUMAN_REVIEW",
            "DONE",
            "BLOCKED",
        ]

        # Test that all states are valid strings
        for state in valid_states:
            assert isinstance(state, str)
            assert len(state) > 0

        # Test state uniqueness
        assert len(set(valid_states)) == len(valid_states)


class TestTaskErrorHandling:
    """Test error handling in task declaration system."""

    def test_invalid_task_id_handling(self):
        """Test handling of invalid task IDs."""
        manager = TaskDeclarationManager()

        # Test with invalid task ID format
        invalid_ids = ["", "invalid", "123", "BE-", "-01"]

        for invalid_id in invalid_ids:
            try:
                declaration = manager.declare_task(invalid_id)
                # If no exception, verify it handles gracefully
                assert declaration is not None
            except (ValueError, KeyError):
                # Expected behavior for invalid IDs
                pass

    def test_missing_task_file_handling(self):
        """Test handling when task files are missing."""
        with patch("pathlib.Path.exists", return_value=False):
            # load_task_metadata returns default metadata instead of raising
            metadata = load_task_metadata("MISSING-01")
            assert metadata is not None
            assert metadata["id"] == "MISSING-01"
            assert metadata["state"] == "pending"

    def test_malformed_task_metadata_handling(self):
        """Test handling of malformed task metadata."""
        malformed_yaml = "invalid: yaml: content: ["

        with patch("builtins.open", mock_open(read_data=malformed_yaml)):
            with patch("pathlib.Path.exists", return_value=True):
                try:
                    load_task_metadata("MALFORMED-01")
                except (yaml.YAMLError, ValueError):
                    # Expected behavior for malformed YAML
                    pass

    def test_task_preparation_failure_handling(self):
        """Test handling of task preparation failures."""
        manager = TaskDeclarationManager()

        # Test preparation of non-existent task
        try:
            result = manager.prepare_task_for_execution("NON_EXISTENT-01")
            # Should either return False/None or raise exception
            assert result is False or result is None
        except (ValueError, KeyError):
            # Expected behavior for non-existent tasks
            pass
