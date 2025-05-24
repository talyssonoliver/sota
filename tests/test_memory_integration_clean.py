"""
Test memory integration with comprehensive CrewAI mocking.
This version uses a simpler approach to avoid Pydantic conflicts.
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mock CrewAI components before any imports
def create_mock_agent():
    """Create a mock agent with required attributes"""
    mock_agent = Mock()
    mock_agent.role = "test_role"
    mock_agent.goal = "test_goal"
    mock_agent.backstory = "test_backstory"
    mock_agent.verbose = True
    mock_agent.allow_delegation = False
    mock_agent.tools = []
    # Add any additional attributes needed for CrewAI/agent tests
    mock_agent._context = ["mock context"]
    mock_agent._memory_retriever = Mock()
    mock_agent._enhanced_prompt = "mock prompt"
    return mock_agent

def create_mock_task():
    """Create a mock task with required attributes"""
    mock_task = Mock()
    mock_task.description = "test_description"
    mock_task.expected_output = "test_output"
    mock_task.agent = create_mock_agent()
    return mock_task

# Mock CrewAI classes
mock_agent_class = Mock(return_value=create_mock_agent())
mock_task_class = Mock(return_value=create_mock_task())
mock_crew_class = Mock()

# Mock the entire crewai module
crewai_mock = MagicMock()
crewai_mock.Agent = mock_agent_class
crewai_mock.Task = mock_task_class
crewai_mock.Crew = mock_crew_class

# Mock utilities
crewai_mock.utilities = MagicMock()
crewai_mock.utilities.I18N = Mock()
crewai_mock.utilities.Prompts = Mock()

# Apply the mocks
sys.modules['crewai'] = crewai_mock
sys.modules['crewai.utilities'] = crewai_mock.utilities
sys.modules['crewai.utilities.i18n'] = crewai_mock.utilities
sys.modules['crewai.utilities.prompts'] = crewai_mock.utilities

# Now import our modules
from tools.memory_engine import memory


class TestMemoryIntegration:
    """Test suite for memory integration with agents"""
    
    @pytest.fixture(autouse=True)
    def setup_memory(self):
        """Setup memory engine for tests"""
        self.memory_engine = memory
        
        # Mock the memory engine methods if needed
        if not hasattr(self.memory_engine, 'search'):
            self.memory_engine.search = Mock(return_value=[
                {"content": "Test context 1", "metadata": {"type": "test"}},
                {"content": "Test context 2", "metadata": {"type": "test"}}
            ])
        
        if not hasattr(self.memory_engine, 'store'):
            self.memory_engine.store = Mock(return_value=True)
    
    def test_memory_engine_available(self):
        """Test that memory engine is available"""
        assert self.memory_engine is not None
    
    def test_memory_search_functionality(self):
        """Test basic memory search functionality"""
        results = self.memory_engine.search("test query", limit=5)
        assert isinstance(results, list)
    
    @patch('agents.memory', new_callable=lambda: memory)
    def test_agent_builder_import(self, mock_memory):
        """Test that agent builder can be imported successfully"""
        try:
            from agents import MemoryEnabledAgentBuilder
            assert MemoryEnabledAgentBuilder is not None
            return True
        except Exception as e:
            pytest.fail(f"Failed to import agent builder: {e}")
    
    @patch('agents.backend.Agent', new_callable=lambda: mock_agent_class)
    @patch('agents.backend.memory', new_callable=lambda: memory)
    def test_backend_agent_creation(self, mock_memory, mock_agent):
        """Test backend agent creation with memory"""
        try:
            from agents.backend import build_backend_agent, get_backend_context
            
            # Test context retrieval
            context = get_backend_context("test query")
            assert isinstance(context, list)
            
            # Test agent building
            agent = build_backend_agent(context="test context")
            assert agent is not None
            
        except Exception as e:
            pytest.fail(f"Backend agent creation failed: {e}")
    
    @patch('agents.frontend.Agent', new_callable=lambda: mock_agent_class)
    @patch('agents.frontend.memory', new_callable=lambda: memory)
    def test_frontend_agent_creation(self, mock_memory, mock_agent):
        """Test frontend agent creation with memory"""
        try:
            from agents.frontend import build_frontend_agent, get_frontend_context
            
            # Test context retrieval
            context = get_frontend_context("test query")
            assert isinstance(context, list)
            
            # Test agent building
            agent = build_frontend_agent(context="test context")
            assert agent is not None
            
        except Exception as e:
            pytest.fail(f"Frontend agent creation failed: {e}")
    
    @patch('agents.technical.Agent', new_callable=lambda: mock_agent_class)
    @patch('agents.technical.memory', new_callable=lambda: memory)
    def test_technical_agent_creation(self, mock_memory, mock_agent):
        """Test technical agent creation with memory"""
        try:
            from agents.technical import build_technical_agent, get_technical_context
            
            # Test context retrieval
            context = get_technical_context("test query")
            assert isinstance(context, list)
            
            # Test agent building
            agent = build_technical_agent(context="test context")
            assert agent is not None
            
        except Exception as e:
            pytest.fail(f"Technical agent creation failed: {e}")
    
    @patch('agents.qa.Agent', new_callable=lambda: mock_agent_class)
    @patch('agents.qa.memory', new_callable=lambda: memory)
    def test_qa_agent_creation(self, mock_memory, mock_agent):
        """Test QA agent creation with memory"""
        try:
            from agents.qa import build_qa_agent, get_qa_context
            
            # Test context retrieval
            context = get_qa_context("test query")
            assert isinstance(context, list)
            
            # Test agent building
            agent = build_qa_agent(context="test context")
            assert agent is not None
            
        except Exception as e:
            pytest.fail(f"QA agent creation failed: {e}")
    
    @patch('agents.doc.Agent', new_callable=lambda: mock_agent_class)
    @patch('agents.doc.memory', new_callable=lambda: memory)
    def test_doc_agent_creation(self, mock_memory, mock_agent):
        """Test documentation agent creation with memory"""
        try:
            from agents.doc import build_doc_agent, get_doc_context
            
            # Test context retrieval
            context = get_doc_context("test query")
            assert isinstance(context, list)
            
            # Test agent building
            agent = build_doc_agent(context="test context")
            assert agent is not None
            
        except Exception as e:
            pytest.fail(f"Doc agent creation failed: {e}")
    
    @patch('agents.coordinator.Agent', new_callable=lambda: mock_agent_class)
    @patch('agents.coordinator.memory', new_callable=lambda: memory)
    def test_coordinator_agent_creation(self, mock_memory, mock_agent):
        """Test coordinator agent creation with memory"""
        try:
            from agents.coordinator import build_coordinator_agent, get_coordinator_context
            
            # Test context retrieval
            context = get_coordinator_context("test query")
            assert isinstance(context, list)
            
            # Test agent building
            agent = build_coordinator_agent(context="test context")
            assert agent is not None
            
        except Exception as e:
            pytest.fail(f"Coordinator agent creation failed: {e}")
    
    def test_context_injection_import(self):
        """Test context injection module import"""
        try:
            from orchestration.inject_context import context_injector
            assert context_injector is not None
        except Exception as e:
            pytest.fail(f"Context injection import failed: {e}")
    
    @patch('orchestration.inject_context.memory', new_callable=lambda: memory)
    def test_context_injector_functionality(self, mock_memory):
        """Test context injector functionality"""
        try:
            from orchestration.inject_context import ContextInjector
            
            injector = ContextInjector()
            assert injector is not None
            
            # Test context preparation
            mock_agent = create_mock_agent()
            task_metadata = {"role": "backend", "query": "test"}
            
            enhanced_agent = injector.prepare_agent_with_context(mock_agent, task_metadata)
            assert enhanced_agent is not None
            
        except Exception as e:
            pytest.fail(f"Context injector test failed: {e}")
    
    def test_prompt_utils_import(self):
        """Test prompt utilities import"""
        try:
            from prompts.utils import load_prompt, format_prompt_with_context
            assert load_prompt is not None
            assert format_prompt_with_context is not None
        except Exception as e:
            pytest.fail(f"Prompt utils import failed: {e}")
    
    def test_prompt_formatting_with_context(self):
        """Test prompt formatting with context"""
        try:
            from prompts.utils import format_prompt_with_context
            
            base_prompt = "This is a test prompt: {query}"
            context = ["Context item 1", "Context item 2"]
            
            formatted = format_prompt_with_context(base_prompt, context, query="test query")
            assert "test query" in formatted
            assert "Context item 1" in formatted
            
        except Exception as e:
            pytest.fail(f"Prompt formatting test failed: {e}")
    
    def test_execute_task_import(self):
        """Test task execution module import"""
        try:
            from orchestration.execute_task import execute_task_with_context
            assert execute_task_with_context is not None
        except Exception as e:
            pytest.fail(f"Execute task import failed: {e}")
    
    @patch('orchestration.execute_task.memory', new_callable=lambda: memory)
    def test_task_execution_with_context(self, mock_memory):
        """Test task execution with context"""
        try:
            from orchestration.execute_task import execute_task_with_context
            
            mock_task = create_mock_task()
            task_metadata = {"role": "backend", "query": "test"}
            
            # This should not raise an exception
            result = execute_task_with_context(mock_task, task_metadata)
            # We don't need to assert specific behavior, just that it doesn't crash
            
        except Exception as e:
            pytest.fail(f"Task execution test failed: {e}")


class TestMemoryEnabledAgentBuilder:
    """Test the MemoryEnabledAgentBuilder class specifically"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for agent builder tests"""
        self.memory_engine = memory
    
    @patch('agents.memory', new_callable=lambda: memory)
    def test_agent_builder_creation(self, mock_memory):
        """Test MemoryEnabledAgentBuilder creation"""
        try:
            from agents import MemoryEnabledAgentBuilder
            
            builder = MemoryEnabledAgentBuilder()
            assert builder is not None
            assert hasattr(builder, 'memory_engine')
            
        except Exception as e:
            pytest.fail(f"Agent builder creation failed: {e}")
    
    @patch('agents.memory', new_callable=lambda: memory)
    @patch('agents.Agent', new_callable=lambda: mock_agent_class)
    def test_agent_builder_build_method(self, mock_agent, mock_memory):
        """Test agent builder build method"""
        try:
            from agents import MemoryEnabledAgentBuilder
            
            builder = MemoryEnabledAgentBuilder()
            
            agent = builder.build(
                role="test_role",
                goal="test_goal",
                backstory="test_backstory"
            )
            
            assert agent is not None
            
        except Exception as e:
            pytest.fail(f"Agent builder build method failed: {e}")
    
    @patch('agents.memory', new_callable=lambda: memory)
    def test_context_retrieval_methods(self, mock_memory):
        """Test context retrieval methods"""
        try:
            from agents import MemoryEnabledAgentBuilder
            
            builder = MemoryEnabledAgentBuilder()
            
            # Test different role contexts
            roles = ["backend", "frontend", "technical", "qa", "doc", "coordinator"]
            
            for role in roles:
                context = builder._get_context_for_agent(role, "test query")
                assert isinstance(context, list)
            
        except Exception as e:
            pytest.fail(f"Context retrieval methods failed: {e}")


# Mock I18N and Prompts for CrewAI compatibility
class MockI18N:
    def __init__(self):
        self.slices = {
            'no_tools': 'No tools available.'
        }
    def get(self, key, default=None):
        return self.slices.get(key, default)

class MockPrompts:
    def __init__(self):
        self.slices = {
            'no_tools': 'No tools available.'
        }
    def get(self, key, default=None):
        return self.slices.get(key, default)

# Replace original mocks with extended mocks
crewai_mock.utilities.I18N = MockI18N
crewai_mock.utilities.Prompts = MockPrompts


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
