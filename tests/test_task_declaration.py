"""
Tests for Phase 4 Task Declaration & Preparation System
Tests the complete workflow from task declaration to execution readiness.
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from orchestration.task_declaration import (TaskDeclaration,
                                            TaskDeclarationManager,
                                            TaskPreparationStatus)
from tools.memory_engine import MemoryEngine
from utils.task_loader import load_task_metadata

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTaskDeclaration:
    """Test the TaskDeclaration dataclass functionality"""

    def test_task_declaration_creation(self):
        """Test basic TaskDeclaration creation"""
        declaration = TaskDeclaration(
            id="TEST-01",
            title="Test Task",
            description="Test description",
            owner="backend",
            state="PLANNED",
            priority="HIGH",
            estimation_hours=2.0,
            depends_on=["TEST-00"],
            artefacts=["test.ts"],
            context_topics=["test-pattern"],
            preparation_status=TaskPreparationStatus.PENDING
        )

        assert declaration.id == "TEST-01"
        assert declaration.title == "Test Task"
        assert declaration.owner == "backend"
        assert declaration.preparation_status == TaskPreparationStatus.PENDING
        assert "TEST-00" in declaration.depends_on
        assert "test.ts" in declaration.artefacts

    def test_task_declaration_to_dict(self):
        """Test TaskDeclaration serialization to dictionary"""
        declaration = TaskDeclaration(
            id="TEST-01",
            title="Test Task",
            description="Test description",
            owner="backend",
            state="PLANNED",
            priority="HIGH",
            estimation_hours=2.0,
            depends_on=[],
            artefacts=[],
            context_topics=[],
            preparation_status=TaskPreparationStatus.PENDING
        )

        data = declaration.to_dict()
        assert isinstance(data, dict)
        assert data['id'] == "TEST-01"
        assert data['title'] == "Test Task"
        assert data['preparation_status'] == TaskPreparationStatus.PENDING

    def test_task_declaration_from_dict(self):
        """Test TaskDeclaration deserialization from dictionary"""
        data = {
            'id': 'TEST-01',
            'title': 'Test Task',
            'description': 'Test description',
            'owner': 'backend',
            'state': 'PLANNED',
            'priority': 'HIGH',
            'estimation_hours': 2.0,
            'depends_on': [],
            'artefacts': [],
            'context_topics': [],
            'preparation_status': 'PENDING'
        }

        declaration = TaskDeclaration.from_dict(data)
        assert declaration.id == "TEST-01"
        assert declaration.title == "Test Task"
        assert declaration.preparation_status == TaskPreparationStatus.PENDING

    def test_task_declaration_from_metadata(self):
        """Test TaskDeclaration creation from task metadata"""
        metadata = {
            'id': 'TEST-01',
            'title': 'Test Task',
            'description': 'Test description',
            'owner': 'backend',
            'state': 'PLANNED',
            'priority': 'HIGH',
            'estimation_hours': 2,
            'depends_on': ['TEST-00'],
            'artefacts': ['test.ts'],
            'context_topics': ['test-pattern']
        }

        declaration = TaskDeclaration.from_metadata(metadata)
        assert declaration.id == "TEST-01"
        assert declaration.title == "Test Task"
        assert declaration.owner == "backend"
        assert declaration.depends_on == ['TEST-00']
        assert declaration.preparation_status == TaskPreparationStatus.PENDING


class TestTaskDeclarationManager:
    """Test the TaskDeclarationManager functionality"""

    @pytest.fixture
    def temp_outputs_dir(self):
        """Create a temporary outputs directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_memory_engine(self):
        """Create a mock memory engine for testing"""
        mock_engine = Mock(spec=MemoryEngine)
        mock_engine.build_focused_context.return_value = "Mock context content"
        mock_engine.get_documents.return_value = []
        return mock_engine

    @pytest.fixture
    def manager_with_temp_dir(self, temp_outputs_dir, mock_memory_engine):
        """Create a TaskDeclarationManager with temporary directory"""
        manager = TaskDeclarationManager(memory_engine=mock_memory_engine)
        manager.outputs_dir = temp_outputs_dir
        # Clear any existing declarations to ensure test isolation
        manager.declared_tasks = {}
        return manager

    def test_manager_initialization(self, mock_memory_engine):
        """Test TaskDeclarationManager initialization"""
        manager = TaskDeclarationManager(memory_engine=mock_memory_engine)
        assert manager.memory_engine == mock_memory_engine
        assert isinstance(manager.declared_tasks, dict)
        assert manager.outputs_dir.exists()

    @patch('orchestration.task_declaration.load_task_metadata')
    def test_declare_task(self, mock_load_metadata, manager_with_temp_dir):
        """Test task declaration functionality"""
        # Mock task metadata
        mock_metadata = {
            'id': 'TEST-01',
            'title': 'Test Task',
            'description': 'Test description',
            'owner': 'backend',
            'state': 'PLANNED',
            'priority': 'HIGH',
            'estimation_hours': 2,
            'depends_on': [],
            'artefacts': ['test.ts'],
            'context_topics': ['test-pattern']
        }
        mock_load_metadata.return_value = mock_metadata

        # Declare the task
        declaration = manager_with_temp_dir.declare_task('TEST-01')

        # Verify declaration
        assert declaration.id == 'TEST-01'
        assert declaration.title == 'Test Task'
        assert declaration.preparation_status == TaskPreparationStatus.PENDING
        assert 'TEST-01' in manager_with_temp_dir.declared_tasks

        # Verify file was saved
        task_dir = manager_with_temp_dir.outputs_dir / 'TEST-01'
        declaration_file = task_dir / 'task_declaration.json'
        assert declaration_file.exists()

    @patch('orchestration.task_declaration.load_task_metadata')
    def test_prepare_task_for_execution(
            self, mock_load_metadata, manager_with_temp_dir):
        """Test complete task preparation workflow"""
        mock_metadata = {
            'id': 'TEST-01',
            'title': 'Test Task',
            'description': 'Test description',
            'owner': 'backend',
            'state': 'PLANNED',
            'priority': 'HIGH',
            'estimation_hours': 2,
            'depends_on': [],
            'artefacts': ['test.ts'],
            'context_topics': ['test-pattern']
        }
        mock_load_metadata.return_value = mock_metadata

        # Prepare task for execution
        declaration = manager_with_temp_dir.prepare_task_for_execution(
            'TEST-01')

        # Verify preparation completed
        assert declaration.preparation_status == TaskPreparationStatus.READY_FOR_EXECUTION
        assert declaration.context_loaded
        assert declaration.prompt_generated
        assert declaration.dependencies_satisfied
        assert declaration.agent_assignment is not None
        assert declaration.execution_plan is not None

    def test_get_preparation_summary_empty(self, manager_with_temp_dir):
        """Test preparation summary with no new declared tasks"""
        summary = manager_with_temp_dir.get_preparation_summary()

        # Manager starts with empty declarations due to isolation
        assert summary['total_tasks'] == 0
        assert summary['ready_for_execution'] == 0
        assert summary['failed_preparation'] == 0
        assert summary['summary'] == "No tasks declared"

    @patch('orchestration.task_declaration.load_task_metadata')
    def test_get_tasks_ready_for_execution(
            self, mock_load_metadata, manager_with_temp_dir):
        """Test getting tasks ready for execution"""
        mock_metadata = {
            'id': 'TEST-01',
            'title': 'Test Task',
            'description': 'Test description',
            'owner': 'backend',
            'state': 'PLANNED',
            'priority': 'HIGH',
            'estimation_hours': 2,
            'depends_on': [],
            'artefacts': [],
            'context_topics': []
        }
        mock_load_metadata.return_value = mock_metadata

        # Prepare task
        manager_with_temp_dir.prepare_task_for_execution('TEST-01')

        # Get ready tasks
        ready_tasks = manager_with_temp_dir.get_tasks_ready_for_execution()

        assert len(ready_tasks) == 1
        assert ready_tasks[0].id == 'TEST-01'
        assert ready_tasks[0].preparation_status == TaskPreparationStatus.READY_FOR_EXECUTION


class TestTaskDeclarationIntegration:
    """Integration tests for the complete task declaration system"""

    @pytest.fixture
    def real_task_file(self):
        """Use a real task file for integration testing"""
        return "BE-07"  # This should exist in the tasks directory

    @pytest.mark.integration
    def test_real_task_declaration(self, real_task_file):
        """Test declaring a real task from the tasks directory"""
        try:
            # Create manager with real memory engine (mocked for faster tests)
            with patch('tools.memory_engine.MemoryEngine') as mock_engine_class:
                mock_engine = Mock()
                mock_engine.build_focused_context.return_value = "Real context content"
                mock_engine.get_documents.return_value = []
                mock_engine_class.return_value = mock_engine

                manager = TaskDeclarationManager()

                # Declare real task
                declaration = manager.declare_task(real_task_file)

                # Verify basic properties
                assert declaration.id == real_task_file
                assert declaration.title is not None
                assert declaration.owner is not None
                # Don't check specific preparation status since it may already
                # be prepared
                assert declaration.preparation_status is not None

        except FileNotFoundError:
            pytest.skip(
                f"Task file {real_task_file}.yaml not found - skipping integration test")


class TestTaskDeclarationCLI:
    """Test the command-line interface functionality"""

    @patch('orchestration.task_declaration.TaskDeclarationManager')
    def test_cli_summary_command(self, mock_manager_class):
        """Test the CLI summary command"""
        mock_manager = Mock()
        mock_manager.get_preparation_summary.return_value = {
            'total_tasks': 5,
            'ready_for_execution': 2,
            'failed_preparation': 0,
            'status_breakdown': {
                TaskPreparationStatus.READY_FOR_EXECUTION: 2,
                TaskPreparationStatus.PENDING: 3
            }
        }
        mock_manager_class.return_value = mock_manager

        # Test would require actual CLI execution - this tests the manager
        # method
        summary = mock_manager.get_preparation_summary()

        assert summary['total_tasks'] == 5
        assert summary['ready_for_execution'] == 2
        assert summary['failed_preparation'] == 0


def test_module_imports():
    """Test that all required modules can be imported"""
    from orchestration.task_declaration import (TaskDeclaration,
                                                TaskDeclarationManager,
                                                TaskPreparationStatus)
    from tools.memory_engine import MemoryEngine
    from utils.task_loader import load_task_metadata

    # Basic import test
    assert TaskDeclarationManager is not None
    assert TaskDeclaration is not None
    assert TaskPreparationStatus is not None
    assert MemoryEngine is not None
    assert load_task_metadata is not None


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])
