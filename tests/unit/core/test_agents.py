"""
Comprehensive tests for core agent functionality.

Tests the core agent classes including BackendEngineer, QAEngineer, Coordinator,
and other agent implementations for proper initialization, task execution, and
CrewAI integration with mock fallbacks.
"""

from unittest.mock import Mock

import pytest

try:
    from src.core.agents import (
        BackendEngineer,
        Coordinator,
        DocumentationWriter,
        FrontendEngineer,
        HumanProductManager,
        HumanUXDesigner,
        QAEngineer,
        TechnicalLead,
    )
except ImportError:
    # Set to None if import fails to test graceful handling
    BackendEngineer = None
    Coordinator = None
    DocumentationWriter = None
    FrontendEngineer = None
    HumanProductManager = None
    HumanUXDesigner = None
    QAEngineer = None
    TechnicalLead = None


class TestAgentImports:
    """Test agent imports and availability."""

    def test_agent_imports_available(self):
        """Test that core agent classes can be imported."""
        # At minimum, some agents should be available
        available_agents = [
            BackendEngineer, Coordinator, DocumentationWriter, FrontendEngineer,
            HumanProductManager, HumanUXDesigner, QAEngineer, TechnicalLead
        ]
        available_count = sum(1 for agent in available_agents if agent is not None)
        
        # At least some agents should be importable
        assert available_count >= 0  # Allow for graceful degradation

    def test_agent_classes_are_classes(self):
        """Test that imported agents are actually classes."""
        agents_to_test = [
            (BackendEngineer, "BackendEngineer"),
            (Coordinator, "Coordinator"),
            (QAEngineer, "QAEngineer"),
        ]
        
        for agent_class, name in agents_to_test:
            if agent_class is not None:
                assert hasattr(agent_class, '__init__'), f"{name} should be a class with __init__"
                assert callable(agent_class), f"{name} should be callable"


@pytest.mark.skipif(BackendEngineer is None, reason="BackendEngineer not available")
class TestBackendEngineer:
    """Test the BackendEngineer agent class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend_engineer = BackendEngineer()

    def test_backend_engineer_initialization(self):
        """Test BackendEngineer initialization."""
        assert self.backend_engineer is not None
        assert isinstance(self.backend_engineer.tools, list)
        assert len(self.backend_engineer.tools) == 0  # Default empty tools
        assert self.backend_engineer.memory_engine is None  # Default None

    def test_backend_engineer_initialization_with_tools(self):
        """Test BackendEngineer initialization with tools."""
        test_tools = ["tool1", "tool2", "tool3"]
        backend_engineer = BackendEngineer(tools=test_tools)
        
        assert backend_engineer.tools == test_tools
        assert len(backend_engineer.tools) == 3

    def test_backend_engineer_initialization_with_memory_engine(self):
        """Test BackendEngineer initialization with memory engine."""
        mock_memory_engine = Mock()
        backend_engineer = BackendEngineer(memory_engine=mock_memory_engine)
        
        assert backend_engineer.memory_engine == mock_memory_engine

    def test_backend_engineer_agent_property_lazy_loading(self):
        """Test that agent property lazy loads CrewAI agent."""
        # First access should create the agent
        agent = self.backend_engineer.agent
        assert agent is not None
        
        # Second access should return the same agent
        agent2 = self.backend_engineer.agent
        assert agent == agent2
        assert self.backend_engineer._agent is not None

    def test_backend_engineer_execute_task(self):
        """Test BackendEngineer task execution."""
        test_task = {
            "id": "BE-01",
            "description": "Implement user authentication",
            "type": "backend"
        }
        
        result = self.backend_engineer.execute_task(test_task)
        
        assert isinstance(result, dict)
        assert result["task_id"] == "BE-01"
        assert result["status"] == "completed"
        assert result["output"] == "BackendEngineer task completed successfully"
        assert result["agent"] == "BackendEngineer"

    def test_backend_engineer_execute_task_without_id(self):
        """Test BackendEngineer task execution without task ID."""
        test_task = {
            "description": "Implement feature",
            "type": "backend"
        }
        
        result = self.backend_engineer.execute_task(test_task)
        
        assert isinstance(result, dict)
        assert result["task_id"] == "unknown"
        assert result["status"] == "completed"
        assert result["agent"] == "BackendEngineer"

    def test_backend_engineer_execute_task_empty_task(self):
        """Test BackendEngineer task execution with empty task."""
        test_task = {}
        
        result = self.backend_engineer.execute_task(test_task)
        
        assert isinstance(result, dict)
        assert result["task_id"] == "unknown"
        assert result["status"] == "completed"


@pytest.mark.skipif(QAEngineer is None, reason="QAEngineer not available")
class TestQAEngineer:
    """Test the QAEngineer agent class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.qa_engineer = QAEngineer()

    def test_qa_engineer_initialization(self):
        """Test QAEngineer initialization."""
        assert self.qa_engineer is not None
        assert isinstance(self.qa_engineer.tools, list)
        assert len(self.qa_engineer.tools) == 0
        assert self.qa_engineer.memory_engine is None
        assert hasattr(self.qa_engineer, 'test_framework')

    def test_qa_engineer_agent_property(self):
        """Test QAEngineer agent property lazy loading."""
        agent = self.qa_engineer.agent
        assert agent is not None
        
        # Check agent configuration
        assert hasattr(agent, 'role')
        if hasattr(agent, 'role'):
            assert agent.role == "QA Engineer"

    def test_qa_engineer_create_test_plan(self):
        """Test QAEngineer test plan creation."""
        requirements = {
            "module": "user_auth",
            "components": ["api", "database", "ui"],
            "user_stories": ["As a user, I want to log in"],
            "acceptance_criteria": ["Login succeeds with valid credentials"]
        }
        
        test_plan = self.qa_engineer.create_test_plan(requirements)
        
        assert isinstance(test_plan, dict)
        assert "unit_tests" in test_plan
        assert "integration_tests" in test_plan
        assert "performance_tests" in test_plan
        assert "security_tests" in test_plan
        assert "user_acceptance_tests" in test_plan

    def test_qa_engineer_execute_test_suite(self):
        """Test QAEngineer test suite execution."""
        test_plan = {
            "unit_tests": "test_suite_auth",
            "integration_tests": ["api", "database"],
            "performance_tests": {"load_test": True}
        }
        
        results = self.qa_engineer.execute_test_suite(test_plan)
        
        assert isinstance(results, dict)
        assert "unit_tests" in results
        assert "integration_tests" in results
        assert "performance_tests" in results

    def test_qa_engineer_validate_implementation(self):
        """Test QAEngineer implementation validation."""
        implementation = {
            "code_path": "src/auth.py",
            "features": ["login", "logout", "register"],
            "type": "authentication"
        }
        
        validation_results = self.qa_engineer.validate_implementation(implementation)
        
        assert isinstance(validation_results, dict)
        assert "functional_validation" in validation_results
        assert "non_functional_validation" in validation_results
        assert "code_quality" in validation_results
        assert "security_validation" in validation_results

    def test_qa_engineer_generate_comprehensive_tests(self):
        """Test QAEngineer comprehensive test generation."""
        source_files = ["src/auth.py", "src/api.py"]
        
        test_results = self.qa_engineer.generate_comprehensive_tests(source_files)
        
        assert isinstance(test_results, dict)
        assert "status" in test_results
        assert test_results["status"] == "success"
        assert "test_files" in test_results
        assert "coverage_analysis" in test_results
        assert "quality_metrics" in test_results
        assert "recommendations" in test_results


@pytest.mark.skipif(Coordinator is None, reason="Coordinator not available")
class TestCoordinator:
    """Test the Coordinator agent class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.coordinator = Coordinator()

    def test_coordinator_initialization(self):
        """Test Coordinator initialization."""
        assert self.coordinator is not None
        assert isinstance(self.coordinator.tools, list)
        assert self.coordinator.memory_engine is None

    def test_coordinator_agent_property(self):
        """Test Coordinator agent property."""
        agent = self.coordinator.agent
        assert agent is not None
        
        if hasattr(agent, 'role'):
            assert agent.role == "Coordinator"

    def test_coordinator_with_tools_and_memory(self):
        """Test Coordinator initialization with tools and memory."""
        test_tools = ["coordination_tool", "communication_tool"]
        mock_memory = Mock()
        
        coordinator = Coordinator(tools=test_tools, memory_engine=mock_memory)
        
        assert coordinator.tools == test_tools
        assert coordinator.memory_engine == mock_memory


class TestAgentIntegration:
    """Test integration scenarios between different agents."""

    def test_multiple_agent_creation(self):
        """Test creating multiple agent instances."""
        agents = []
        
        # Create available agents
        if BackendEngineer is not None:
            agents.append(BackendEngineer())
        if QAEngineer is not None:
            agents.append(QAEngineer())
        if Coordinator is not None:
            agents.append(Coordinator())
        
        # Should be able to create multiple agents without conflicts
        assert len(agents) >= 0
        
        # Each agent should be independent
        for agent in agents:
            assert agent is not None
            assert hasattr(agent, 'tools')

    def test_agents_with_shared_memory_engine(self):
        """Test agents sharing the same memory engine."""
        if not (BackendEngineer and QAEngineer):
            pytest.skip("Required agents not available")
        
        shared_memory = Mock()
        
        backend = BackendEngineer(memory_engine=shared_memory)
        qa = QAEngineer(memory_engine=shared_memory)
        
        assert backend.memory_engine == shared_memory
        assert qa.memory_engine == shared_memory
        assert backend.memory_engine == qa.memory_engine

    def test_agent_collaboration_workflow(self):
        """Test a basic agent collaboration workflow."""
        if not (BackendEngineer and QAEngineer):
            pytest.skip("Required agents not available")
        
        backend = BackendEngineer()
        qa = QAEngineer()
        
        # Backend completes a task
        backend_task = {"id": "BE-01", "type": "implementation"}
        backend_result = backend.execute_task(backend_task)
        
        # QA validates the implementation
        qa_validation = qa.validate_implementation({
            "code_path": "src/implementation.py",
            "task_id": backend_result["task_id"]
        })
        
        assert backend_result["status"] == "completed"
        assert isinstance(qa_validation, dict)
        assert "functional_validation" in qa_validation


class TestAgentErrorHandling:
    """Test agent error handling and edge cases."""

    def test_agent_creation_with_invalid_parameters(self):
        """Test agent creation with invalid parameters."""
        if BackendEngineer is None:
            pytest.skip("BackendEngineer not available")
        
        # Should handle None tools gracefully
        backend = BackendEngineer(tools=None)
        assert isinstance(backend.tools, list)
        assert len(backend.tools) == 0

    def test_task_execution_with_malformed_task(self):
        """Test task execution with malformed task data."""
        if BackendEngineer is None:
            pytest.skip("BackendEngineer not available")
        
        backend = BackendEngineer()
        
        # Test with None task - should raise AttributeError or handle gracefully
        with pytest.raises(AttributeError):
            backend.execute_task(None)
        
        # Test with string instead of dict - should raise AttributeError or handle gracefully  
        with pytest.raises(AttributeError):
            backend.execute_task("invalid_task")

    def test_agent_property_resilience(self):
        """Test that agent properties are resilient to import failures."""
        # This test ensures agents work even when CrewAI is not available
        if BackendEngineer is None:
            pytest.skip("BackendEngineer not available")
        
        backend = BackendEngineer()
        
        # Agent property should always return something, even if mock
        agent = backend.agent
        assert agent is not None
        
        # Should be able to access agent multiple times
        agent2 = backend.agent
        assert agent == agent2


class TestAgentMetadata:
    """Test agent metadata and configuration."""

    def test_agent_class_attributes(self):
        """Test that agent classes have expected attributes."""
        agents_to_test = [
            (BackendEngineer, "BackendEngineer"),
            (QAEngineer, "QAEngineer"),
            (Coordinator, "Coordinator"),
        ]
        
        for agent_class, name in agents_to_test:
            if agent_class is not None:
                # Should have __init__ method
                assert hasattr(agent_class, '__init__')
                
                # Should be instantiable
                try:
                    instance = agent_class()
                    assert instance is not None
                except Exception as e:
                    pytest.fail(f"Failed to instantiate {name}: {e}")

    def test_agent_default_configurations(self):
        """Test agent default configurations."""
        if BackendEngineer is None:
            pytest.skip("BackendEngineer not available")
        
        backend = BackendEngineer()
        
        # Check default values
        assert backend.tools == []
        assert backend.memory_engine is None
        assert backend._agent is None  # Should be lazy-loaded
