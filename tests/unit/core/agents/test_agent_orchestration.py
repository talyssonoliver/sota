"""Tests for agent orchestration functionality."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.core.agents.coordinator import Coordinator
from src.core.agents.factory import (
    AGENT_CONFIGS,
    AgentFactory,
    create_agent,
    create_coordinator_agent,
)
from src.core.workflows.delegation import delegate_task, save_task_output
from src.core.workflows.registry import (
    create_agent_instance,
    get_agent_config,
    get_agent_for_task,
)


class TestAgentFactory:
    """Test the AgentFactory for creating and orchestrating agents."""

    def test_create_agent_valid_type(self):
        """Test creating an agent with a valid type."""
        with patch("src.core.agents.factory.Agent") as mock_agent_class:
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            _ = create_agent("backend", tools=[])

            mock_agent_class.assert_called_once()
            assert mock_agent_class.call_args[1]["role"] == "Backend Engineer"
            assert (
                mock_agent_class.call_args[1]["goal"]
                == "Develop robust backend services and APIs"
            )

    def test_create_agent_invalid_type(self):
        """Test creating an agent with an invalid type."""
        with pytest.raises(ValueError, match="Unknown agent type: invalid_type"):
            create_agent("invalid_type")

    def test_agent_factory_with_memory_engine(self):
        """Test AgentFactory with memory engine integration."""
        mock_memory_engine = Mock()
        mock_memory_engine.get_relevant_context.return_value = "Test context"

        factory = AgentFactory(memory_engine=mock_memory_engine)

        with patch("src.core.agents.factory.Agent") as mock_agent_class:
            _ = factory.create_agent(
                "qa", context_domains=["testing", "quality"], tools=[]
            )

            mock_memory_engine.get_relevant_context.assert_called_once_with(
                query="agent context", domains=["testing", "quality"]
            )

            # Verify context was passed to agent
            assert mock_agent_class.call_args[1].get("context") == "Test context"

    def test_agent_factory_memory_engine_failure(self):
        """Test AgentFactory when memory engine fails."""
        mock_memory_engine = Mock()
        mock_memory_engine.get_relevant_context.side_effect = Exception("Memory error")

        factory = AgentFactory(memory_engine=mock_memory_engine)

        with patch("src.core.agents.factory.Agent") as mock_agent_class:
            # Should still create agent despite memory failure
            _ = factory.create_agent("frontend", context_domains=["ui"])
            mock_agent_class.assert_called_once()

    def test_all_agent_types_configured(self):
        """Test that all agent types have proper configuration."""
        expected_agents = [
            "technical_lead",
            "backend",
            "frontend",
            "qa",
            "documentation",
            "coordinator",
        ]

        for agent_type in expected_agents:
            assert agent_type in AGENT_CONFIGS
            config = AGENT_CONFIGS[agent_type]
            assert "role" in config
            assert "goal" in config
            assert "backstory" in config


class TestCoordinator:
    """Test the Coordinator agent class."""

    def test_coordinator_initialization(self):
        """Test Coordinator initialization."""
        tools = [Mock(), Mock()]
        memory_engine = Mock()
        mock_agent_class = Mock()

        with patch(
            "src.core.agents.coordinator._get_agent_class",
            return_value=mock_agent_class,
        ):
            coordinator = Coordinator(tools=tools, memory_engine=memory_engine)

            assert coordinator.tools == tools
            assert coordinator.memory_engine == memory_engine

            # Access the agent property to trigger lazy loading
            _ = coordinator.agent

            mock_agent_class.assert_called_once_with(
                role="Coordinator",
                goal="Coordinator Agent for managing and coordinating tasks",
                backstory="Expert coordinator with deep knowledge and expertise",
                verbose=True,
                allow_delegation=False,
                tools=tools,
            )

    def test_coordinator_execute_task(self):
        """Test Coordinator execute_task method."""
        coordinator = Coordinator()

        task = {"id": "TEST-01", "description": "Test task", "type": "test"}

        result = coordinator.execute_task(task)

        assert result["task_id"] == "TEST-01"
        assert result["status"] == "completed"
        assert result["agent"] == "Coordinator"
        assert "output" in result


class TestTaskDelegation:
    """Test task delegation functionality."""

    @patch("src.core.workflows.delegation.get_agent_for_task")
    @patch("src.core.workflows.delegation.get_context_by_keys")
    @patch("src.core.workflows.delegation.save_task_output")
    def test_delegate_task_auto_agent_selection(
        self, mock_save_output, mock_get_context, mock_get_agent
    ):
        """Test delegating a task with automatic agent selection."""
        mock_agent = Mock()
        mock_agent.execute.return_value = {
            "status": "completed",
            "output": "Task completed",
        }
        mock_get_agent.return_value = mock_agent
        mock_get_context.return_value = "Test context"

        result = delegate_task(task_id="BE-01", task_description="Backend task")

        mock_get_agent.assert_called_once_with("BE-01", memory_config=None)
        mock_agent.execute.assert_called_once()

        # Verify agent_id was added to result
        assert result["agent_id"] == "BE"
        assert result["status"] == "completed"

        mock_save_output.assert_called_once_with("BE-01", result)

    @patch("src.core.workflows.delegation.create_agent_instance")
    @patch("src.core.workflows.delegation.save_task_output")
    def test_delegate_task_specific_agent(self, mock_save_output, mock_create_agent):
        """Test delegating a task to a specific agent."""
        mock_agent = Mock()
        mock_agent.execute.return_value = {"status": "completed"}
        mock_create_agent.return_value = mock_agent

        _ = delegate_task(
            task_id="CUSTOM-01",
            task_description="Custom task",
            agent_id="backend",
            context="Custom context",
            relevant_files=["file1.py", "file2.py"],
        )

        mock_create_agent.assert_called_once_with("backend", memory_config=None)

        # Verify execute was called with proper arguments
        execute_args = mock_agent.execute.call_args[0][0]
        assert execute_args["task_id"] == "CUSTOM-01"
        assert execute_args["context"] == "Custom context"
        assert "file1.py" in execute_args["file_references"]
        assert "file2.py" in execute_args["file_references"]

    @patch("src.core.workflows.delegation.get_agent_for_task")
    def test_delegate_task_exception_handling(self, mock_get_agent):
        """Test exception handling in task delegation."""
        mock_agent = Mock()
        mock_agent.execute.side_effect = Exception("Execution failed")
        mock_get_agent.return_value = mock_agent

        with pytest.raises(Exception, match="Execution failed"):
            delegate_task("BE-01", "Backend task")

    @patch("os.makedirs")
    @patch("builtins.open", create=True)
    def test_save_task_output(self, mock_open, mock_makedirs):
        """Test saving task output to file."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        output = {"status": "completed", "data": "test"}
        path = save_task_output("TEST-01", output)

        mock_makedirs.assert_called_once()
        mock_open.assert_called_once()
        mock_file.write.assert_called_once_with(str(output))

        assert "TEST-01" in path
        assert path.endswith(".txt")


class TestAgentRegistry:
    """Test agent registry functionality."""

    def test_get_agent_for_task(self):
        """Test getting appropriate agent for task type."""
        assert get_agent_for_task("backend") == "backend"
        assert get_agent_for_task("frontend") == "frontend"
        assert get_agent_for_task("qa") == "qa"
        assert get_agent_for_task("documentation") == "documentation"
        assert get_agent_for_task("technical") == "technical_lead"
        assert get_agent_for_task("unknown") == "coordinator"  # default

    def test_create_agent_instance(self):
        """Test creating agent instance."""
        config = {"tools": ["tool1", "tool2"]}
        agent = create_agent_instance("backend", config)

        assert agent["type"] == "backend"
        assert agent["config"] == config

    def test_get_agent_config(self):
        """Test getting agent configuration."""
        config = get_agent_config("qa")
        assert config["name"] == "qa"
        assert "config" in config


class TestAgentOrchestration:
    """Test end-to-end agent orchestration scenarios."""

    @patch("src.core.workflows.delegation.get_agent_for_task")
    @patch("src.core.workflows.delegation.save_task_output")
    @patch("src.core.workflows.delegation.get_context_by_keys")
    def test_multi_agent_task_execution(
        self, mock_get_context, mock_save_output, mock_get_agent
    ):
        """Test orchestrating multiple agents for different tasks."""
        # Setup different agents
        backend_agent = Mock()
        backend_agent.execute.return_value = {
            "status": "completed",
            "output": "API created",
        }

        frontend_agent = Mock()
        frontend_agent.execute.return_value = {
            "status": "completed",
            "output": "UI created",
        }

        qa_agent = Mock()
        qa_agent.execute.return_value = {
            "status": "completed",
            "output": "Tests passed",
        }

        # Configure mock to return different agents based on task
        def get_agent_side_effect(task_id, **kwargs):
            if task_id.startswith("BE"):
                return backend_agent
            elif task_id.startswith("FE"):
                return frontend_agent
            elif task_id.startswith("QA"):
                return qa_agent

        mock_get_agent.side_effect = get_agent_side_effect
        mock_get_context.return_value = "Task context"

        # Execute tasks
        tasks = [
            ("BE-01", "Create API endpoint"),
            ("FE-01", "Create UI component"),
            ("QA-01", "Test integration"),
        ]

        results = []
        for task_id, description in tasks:
            result = delegate_task(task_id, description)
            results.append(result)

        # Verify all agents were called
        assert backend_agent.execute.call_count == 1
        assert frontend_agent.execute.call_count == 1
        assert qa_agent.execute.call_count == 1

        # Verify results
        assert all(r["status"] == "completed" for r in results)
        assert results[0]["output"] == "API created"
        assert results[1]["output"] == "UI created"
        assert results[2]["output"] == "Tests passed"

    def test_coordinator_agent_creation(self):
        """Test creating a coordinator agent through factory."""
        with patch("src.core.agents.factory.Agent") as mock_agent_class:
            _ = create_coordinator_agent(tools=["tool1"])

            mock_agent_class.assert_called_once()
            call_kwargs = mock_agent_class.call_args[1]
            assert call_kwargs["role"] == "Project Coordinator"
            assert call_kwargs["allow_delegation"] is True
            assert "tool1" in call_kwargs["tools"]
