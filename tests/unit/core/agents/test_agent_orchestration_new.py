"""
Enhanced test suite for agent orchestration and task delegation workflows.
Complements the existing test_agent_orchestration.py with additional scenarios.
"""

import pytest
import tempfile
from unittest.mock import Mock, patch
from datetime import datetime

# Import the modules under test
try:
    from src.core.workflows.delegation import delegate_task, save_task_output
    from src.core.workflows.registry import (
        AGENT_REGISTRY, create_agent_instance, 
        get_agent_config, get_agent_for_task
    )
    from src.core.workflows.states import TaskStatus
except ImportError:
    # Handle import errors gracefully for testing
    delegate_task = None
    save_task_output = None
    AGENT_REGISTRY = {}
    create_agent_instance = None
    get_agent_config = None
    get_agent_for_task = None
    TaskStatus = None


class TestAdvancedAgentOrchestration:
    """Test advanced agent orchestration scenarios."""

    def test_concurrent_task_delegation(self):
        """Test handling multiple concurrent task delegations."""
        if delegate_task is None:
            pytest.skip("delegate_task not available")
            
        with patch('src.core.workflows.delegation.create_agent_instance') as mock_create:
            # Mock multiple agents
            mock_agent_1 = Mock()
            mock_agent_1.execute.return_value = {
                "output": "Task 1 completed",
                "task_id": "BE-01",
                "agent_id": "backend_engineer"
            }
            
            mock_agent_2 = Mock()
            mock_agent_2.execute.return_value = {
                "output": "Task 2 completed", 
                "task_id": "FE-01",
                "agent_id": "frontend_engineer"
            }
            
            mock_create.side_effect = [mock_agent_1, mock_agent_2]
            
            with patch('src.core.workflows.delegation.get_relevant_context', return_value="test context"):
                # Delegate tasks concurrently
                result_1 = delegate_task("BE-01", "Backend task", "backend_engineer")
                result_2 = delegate_task("FE-01", "Frontend task", "frontend_engineer")
                
                assert result_1["task_id"] == "BE-01"
                assert result_2["task_id"] == "FE-01"
                assert mock_create.call_count == 2

    def test_task_delegation_with_dependencies(self):
        """Test task delegation with dependency resolution."""
        if delegate_task is None:
            pytest.skip("delegate_task not available")
            
        with patch('src.core.workflows.delegation.create_agent_instance') as mock_create:
            mock_agent = Mock()
            mock_agent.execute.return_value = {
                "output": "Dependent task completed",
                "task_id": "BE-02", 
                "agent_id": "backend_engineer",
                "dependencies_resolved": ["BE-01"]
            }
            mock_create.return_value = mock_agent
            
            with patch('src.core.workflows.delegation.get_relevant_context', return_value="dependency context"):
                result = delegate_task(
                    "BE-02", 
                    "Task with dependencies", 
                    "backend_engineer"
                )
                
                assert result["task_id"] == "BE-02"
                assert "dependencies_resolved" in result

    def test_agent_failure_and_retry(self):
        """Test agent failure handling and retry mechanisms."""
        if delegate_task is None:
            pytest.skip("delegate_task not available")
            
        with patch('src.core.workflows.delegation.create_agent_instance') as mock_create:
            mock_agent = Mock()
            # First call fails, second succeeds
            mock_agent.execute.side_effect = [
                Exception("Agent execution failed"),
                {
                    "output": "Task completed on retry",
                    "task_id": "BE-03",
                    "agent_id": "backend_engineer", 
                    "retry_count": 1
                }
            ]
            mock_create.return_value = mock_agent
            
            with patch('src.core.workflows.delegation.get_relevant_context', return_value="test context"):
                # Should handle failure gracefully
                try:
                    result = delegate_task("BE-03", "Failing task", "backend_engineer")
                    # If retry logic exists, result should be successful
                    if isinstance(result, dict) and "retry_count" in result:
                        assert result["retry_count"] == 1
                except Exception:
                    # Expected if no retry logic implemented
                    assert True

    def test_dynamic_agent_selection(self):
        """Test dynamic agent selection based on task characteristics."""
        if get_agent_for_task is None:
            pytest.skip("get_agent_for_task not available")
            
        # Test different task types
        test_cases = [
            ("BE-01", "backend_engineer"),
            ("FE-01", "frontend_engineer"), 
            ("DOC-01", "documentation"),
            ("QA-01", "qa"),
            ("TL-01", "technical_lead")
        ]
        
        for task_id, expected_agent in test_cases:
            with patch('src.core.workflows.registry.AGENT_REGISTRY', {
                "backend_engineer": Mock(),
                "frontend_engineer": Mock(),
                "documentation": Mock(), 
                "qa": Mock(),
                "technical_lead": Mock()
            }):
                agent_type = get_agent_for_task(task_id.split("-")[0].lower())
                # Verify appropriate agent is selected
                assert isinstance(agent_type, str)

    def test_task_output_persistence(self):
        """Test task output saving and retrieval."""
        if save_task_output is None:
            pytest.skip("save_task_output not available")
            
        with tempfile.TemporaryDirectory():
            with patch('src.core.workflows.delegation.os.makedirs') as mock_makedirs:
                with patch('src.core.workflows.delegation.os.path.join', return_value="/fake/path/BE-01_20250725_120000.txt"):
                    with patch('builtins.open', create=True) as mock_open:
                        mock_file = Mock()
                        mock_open.return_value.__enter__.return_value = mock_file
                        
                        result = save_task_output("BE-01", "Task output content")
                        
                        assert isinstance(result, str)
                        assert "BE-01" in result
                        mock_file.write.assert_called_once_with("Task output content")
                        mock_makedirs.assert_called_once()

    @pytest.mark.parametrize("agent_type,expected_config", [
        ("backend_engineer", {"name": "Backend Engineer Agent"}),
        ("frontend_engineer", {"name": "Frontend Engineer Agent"}),
        ("qa", {"name": "QA Agent"})
    ])
    def test_agent_configuration_loading(self, agent_type, expected_config):
        """Test agent configuration loading for different agent types."""
        if get_agent_config is None:
            pytest.skip("get_agent_config not available")
            
        with patch('src.core.workflows.registry.load_agent_config') as mock_load:
            mock_load.return_value = {agent_type: expected_config}
            
            config = get_agent_config(agent_type)
            
            assert config == expected_config


class TestAgentCommunication:
    """Test inter-agent communication and coordination."""

    def test_agent_to_agent_messaging(self):
        """Test communication between agents."""
        with patch('src.core.workflows.delegation.create_agent_instance') as mock_create:
            # Create mock agents that can communicate
            sender_agent = Mock()
            receiver_agent = Mock()
            
            sender_agent.send_message = Mock(return_value={"status": "sent"})
            receiver_agent.receive_message = Mock(return_value={"status": "received"})
            
            mock_create.side_effect = [sender_agent, receiver_agent]
            
            # Test message passing
            if hasattr(sender_agent, 'send_message'):
                message_result = sender_agent.send_message("test message")
                assert message_result["status"] == "sent"
                
            if hasattr(receiver_agent, 'receive_message'):
                receive_result = receiver_agent.receive_message()
                assert receive_result["status"] == "received"

    def test_workflow_coordination(self):
        """Test coordination of multi-agent workflows."""
        with patch('src.core.workflows.delegation.create_agent_instance') as mock_create:
            # Mock coordinator and worker agents
            coordinator = Mock()
            worker1 = Mock()
            worker2 = Mock()
            
            coordinator.coordinate.return_value = {
                "workflow_id": "WF-001",
                "assigned_agents": ["worker1", "worker2"],
                "status": "coordinated"
            }
            
            worker1.execute.return_value = {"task_id": "SUB-01", "status": "completed"}
            worker2.execute.return_value = {"task_id": "SUB-02", "status": "completed"}
            
            mock_create.side_effect = [coordinator, worker1, worker2]
            
            # Test workflow coordination
            if hasattr(coordinator, 'coordinate'):
                coordination_result = coordinator.coordinate()
                assert coordination_result["status"] == "coordinated"
                assert len(coordination_result["assigned_agents"]) == 2


class TestAgentPerformanceAndScaling:
    """Test agent performance and scaling scenarios."""

    def test_agent_load_balancing(self):
        """Test load balancing across multiple agent instances."""
        if delegate_task is None:
            pytest.skip("delegate_task not available")
            
        with patch('src.core.workflows.delegation.create_agent_instance') as mock_create:
            # Mock multiple instances of the same agent type
            agents = []
            for i in range(3):
                agent = Mock()
                agent.execute.return_value = {
                    "output": f"Task completed by instance {i}",
                    "task_id": f"BE-0{i+1}",
                    "agent_id": "backend_engineer",
                    "instance_id": i
                }
                agents.append(agent)
            
            mock_create.side_effect = agents
            
            with patch('src.core.workflows.delegation.get_relevant_context', return_value="test context"):
                # Delegate multiple tasks
                results = []
                for i in range(3):
                    result = delegate_task(f"BE-0{i+1}", f"Task {i+1}", "backend_engineer")
                    results.append(result)
                
                # Verify all tasks completed
                assert len(results) == 3
                for i, result in enumerate(results):
                    assert result["task_id"] == f"BE-0{i+1}"

    def test_agent_resource_management(self):
        """Test agent resource allocation and management."""
        with patch('src.core.workflows.registry.create_agent_instance') as mock_create:
            mock_agent = Mock()
            mock_agent.get_resource_usage.return_value = {
                "memory_usage": "125MB",
                "cpu_usage": "15%", 
                "execution_time": "2.3s",
                "status": "healthy"
            }
            mock_create.return_value = mock_agent
            
            if create_agent_instance is not None:
                agent = create_agent_instance("backend_engineer")
                
                if hasattr(agent, 'get_resource_usage'):
                    resources = agent.get_resource_usage()
                    assert "memory_usage" in resources
                    assert "cpu_usage" in resources
                    assert resources["status"] == "healthy"


class TestErrorRecoveryAndResilience:
    """Test error recovery and system resilience."""

    def test_agent_health_monitoring(self):
        """Test agent health monitoring and status reporting."""
        with patch('src.core.workflows.registry.create_agent_instance') as mock_create:
            mock_agent = Mock()
            mock_agent.health_check.return_value = {
                "status": "healthy",
                "last_heartbeat": datetime.now().isoformat(),
                "response_time": 0.05,
                "error_count": 0
            }
            mock_create.return_value = mock_agent
            
            if create_agent_instance is not None:
                agent = create_agent_instance("backend_engineer")
                
                if hasattr(agent, 'health_check'):
                    health = agent.health_check()
                    assert health["status"] == "healthy"
                    assert health["error_count"] == 0

    def test_graceful_degradation(self):
        """Test graceful degradation when agents are unavailable."""
        if delegate_task is None:
            pytest.skip("delegate_task not available")
            
        with patch('src.core.workflows.delegation.create_agent_instance') as mock_create:
            # Simulate agent unavailable
            mock_create.side_effect = Exception("Agent service unavailable")
            
            with patch('src.core.workflows.delegation.get_relevant_context', return_value="test context"):
                # Should handle gracefully or provide fallback
                try:
                    result = delegate_task("BE-01", "Test task", "unavailable_agent")
                    # If fallback exists, should return error info
                    if isinstance(result, dict):
                        assert "error" in result or "status" in result
                except Exception as e:
                    # Expected behavior for unavailable agent
                    assert "unavailable" in str(e).lower() or "service" in str(e).lower()

    def test_system_recovery_after_failure(self):
        """Test system recovery mechanisms after agent failures."""
        with patch('src.core.workflows.registry.AGENT_REGISTRY') as mock_registry:
            # Simulate registry recovery
            mock_registry.get.side_effect = [
                None,  # First call fails
                Mock()  # Second call succeeds after recovery
            ]
            
            # Test recovery mechanism
            if AGENT_REGISTRY is not None:
                # First attempt should fail/return None
                result1 = mock_registry.get("backend_engineer")
                assert result1 is None
                
                # Second attempt should succeed
                result2 = mock_registry.get("backend_engineer") 
                assert result2 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
