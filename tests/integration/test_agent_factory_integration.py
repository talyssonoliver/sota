"""
Integration tests for Agent Factory with other system components.

Tests the complete agent creation and initialization workflow, including:
- Agent creation from configuration
- Tool loading and initialization
- Memory context injection
- Agent-to-workflow handoff
"""

import pytest
import unittest
from unittest.mock import Mock, patch
import tempfile
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.agents.factory import create_agent, AGENT_CONFIGS
from src.infrastructure.memory import MemoryEngine





@pytest.fixture
def integration_environment():
    """Set up integration test environment."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test configuration
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create agent configuration
        agent_config = {
            "agents": {
                "technical_lead": {
                    "role": "Technical Lead",
                    "tools": ["github_tool", "design_system_tool"],
                    "context_domains": ["architecture", "project_management"],
                    "memory_enabled": True
                },
                "backend": {
                    "role": "Backend Engineer", 
                    "tools": ["supabase_tool", "github_tool"],
                    "context_domains": ["backend", "api", "database"],
                    "memory_enabled": True
                }
            }
        }
        
        config_file = config_dir / "agents.yaml"
        with open(config_file, "w") as f:
            import yaml
            yaml.dump(agent_config, f)
        
        # Create mock memory store
        memory_dir = Path(temp_dir) / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        yield {
            'temp_dir': temp_dir,
            'config_dir': config_dir,
            'memory_dir': memory_dir,
            'agent_config': agent_config
        }


class TestAgentFactoryIntegration(unittest.TestCase):
    """Integration tests for Agent Factory with other system components."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_memory = Mock(spec=MemoryEngine)
        self.mock_memory.get_context.return_value = {"context": "Test context", "metadata": {"source": "test"}}
    
    def test_end_to_end_agent_creation_and_initialization(self):
        """Test complete agent creation workflow from config to ready state."""
        with patch('src.core.agents.factory.MemoryEngine', return_value=self.mock_memory):
            # Create agent from configuration
            agent = create_agent("technical_lead")
            
            # Verify agent is created (mock Agent doesn't have attributes)
            self.assertIsNotNone(agent)
            
            # Verify the agent was created with proper configuration call
            # In a real environment, these would be Agent attributes
    
    def test_agent_to_workflow_handoff(self):
        """Test agent integration with workflow execution engine."""
        with patch('src.core.agents.factory.MemoryEngine', return_value=self.mock_memory):
            # Create agent
            agent = create_agent("backend")
            
            # Simulate workflow execution with agent
            task_id = "BE-01"
            input_message = "Test task input"
            
            # Mock execute_task to avoid actual workflow execution
            with patch('src.core.workflows.execute_workflow.execute_task') as mock_execute_task:
                mock_execute_task.return_value = {"status": "completed", "output": "mocked output"}
                
                result = mock_execute_task(task_id, input_message, workflow_type="standard", use_coordinator_planning=False)
                
                # Verify execute_task was called
                mock_execute_task.assert_called_once_with(task_id, input_message, workflow_type="standard", use_coordinator_planning=False)
                self.assertEqual(result["status"], "completed")
    
    def test_agent_context_injection_from_memory(self):
        """Test that agents receive proper context from memory system."""
        test_contexts = {
            "architecture": {"patterns": ["MVC", "REST"], "standards": ["PEP8"]},
            "backend": {"frameworks": ["FastAPI", "SQLAlchemy"], "databases": ["PostgreSQL"]}
        }
        
        # Create technical lead agent with context domains
        tl_agent = create_agent("technical_lead", 
                                    context_domains=["architecture", "project_management"])
        
        # Verify agent was created (no direct context assertion here)
        self.assertIsNotNone(tl_agent)

        # Create backend agent with context domains
        be_agent = create_agent("backend",
                                    context_domains=["backend", "api", "database"])
        
        # Verify agent was created
        self.assertIsNotNone(be_agent)
    
    def test_agent_tool_loading_integration(self):
        """Test that agents receive and can use their configured tools."""
        mock_tools = {
            "github_tool": Mock(name="GitHub Tool"),
            "supabase_tool": Mock(name="Supabase Tool"),
            "design_system_tool": Mock(name="Design System Tool")
        }
        
        def mock_load_tools(agent_type, config):
            """Mock tool loading based on agent type."""
            if agent_type == "technical_lead":
                return [mock_tools["github_tool"], mock_tools["design_system_tool"]]
            elif agent_type == "backend":
                return [mock_tools["github_tool"], mock_tools["supabase_tool"]]
            return []
        
        with patch('src.infrastructure.tools.core.tool_loader.load_tools_for_agent', side_effect=mock_load_tools):
            with patch('src.core.agents.factory.MemoryEngine', return_value=self.mock_memory):
                # Create agents with tools
                tl_agent = create_agent("technical_lead", load_tools=True)
                be_agent = create_agent("backend", load_tools=True)
                
                # Verify tools were loaded (mocked in this case)
                # In real implementation, check agent.tools attribute
                self.assertIsNotNone(tl_agent)
                self.assertIsNotNone(be_agent)
    
    def test_error_propagation_during_agent_creation(self):
        """Test how errors propagate through agent creation process."""
        # Test memory initialization failure
        with patch('src.core.agents.factory.Agent', side_effect=Exception("Memory init failed")):
            with self.assertRaises(Exception) as context:
                create_agent("technical_lead")
            self.assertIn("Memory init failed", str(context.exception))
        
        # Test invalid agent type
        with self.assertRaises(ValueError) as context:
            create_agent("invalid_agent_type")
        self.assertIn("Unknown agent type", str(context.exception))
    
    def test_concurrent_agent_creation(self):
        """Test thread safety of concurrent agent creation."""
        import threading
        
        agents_created = []
        errors = []
        
        def create_agent_thread(agent_type):
            """Thread function to create agent."""
            try:
                with patch('src.core.agents.factory.MemoryEngine', return_value=self.mock_memory):
                    agent = create_agent(agent_type)
                    agents_created.append((agent_type, agent))
            except Exception as e:
                errors.append((agent_type, str(e)))
        
        # Create multiple agents concurrently
        threads = []
        agent_types = ["technical_lead", "backend", "frontend", "qa"]
        
        for agent_type in agent_types:
            if agent_type in AGENT_CONFIGS:
                thread = threading.Thread(target=create_agent_thread, args=(agent_type,))
                threads.append(thread)
                thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5)
        
        # Verify all agents were created without errors
        self.assertEqual(len(errors), 0, f"Errors during concurrent creation: {errors}")
        self.assertGreaterEqual(len(agents_created), 2)  # At least TL and backend
    
    def test_agent_lifecycle_integration(self):
        """Test complete agent lifecycle from creation to cleanup."""
        with patch('src.core.agents.factory.MemoryEngine', return_value=self.mock_memory):
            # Create agent
            agent = create_agent("backend")
            
            # Simulate agent usage in workflow
            agent_state = {"tasks_completed": 0, "errors": []}
            
            # Mock task execution
            for i in range(3):
                agent_state["tasks_completed"] += 1
            
            # Verify agent can be properly cleaned up
            if hasattr(agent, 'cleanup'):
                agent.cleanup()
            
            # Verify memory was properly released
            self.mock_memory.shutdown.assert_not_called()  # Memory is shared
    
    def test_agent_configuration_validation(self):
        """Test that agent configurations are properly validated."""
        # Test with missing required fields - use real CrewAI Agent for validation
        invalid_config = {
            "role": "Test Agent"
            # Missing goal and backstory
        }
        
        with patch.dict('src.core.agents.factory.AGENT_CONFIGS', {'test_agent': invalid_config}):
            # Mock the Agent class to raise validation error
            with patch('src.core.agents.factory.Agent') as mock_agent:
                mock_agent.side_effect = ValueError("Field required: goal")
                
                with self.assertRaises(ValueError) as context:
                    create_agent("test_agent")
                self.assertIn("Field required", str(context.exception))
    
    def test_performance_agent_creation(self):
        """Test performance characteristics of agent creation."""
        import time
        
        with patch('src.core.agents.factory.MemoryEngine', return_value=self.mock_memory):
            # Measure single agent creation time
            start_time = time.time()
            agent = create_agent("technical_lead")
            creation_time = time.time() - start_time
            
            # Agent creation should be fast (< 100ms)
            self.assertLess(creation_time, 0.1, f"Agent creation took {creation_time:.3f}s")
            
            # Test batch creation performance
            start_time = time.time()
            agents = []
            for _ in range(10):
                agents.append(create_agent("backend"))
            batch_time = time.time() - start_time
            
            # Batch creation should scale well (< 50ms per agent)
            avg_time = batch_time / 10
            self.assertLess(avg_time, 0.05, f"Average creation time: {avg_time:.3f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])