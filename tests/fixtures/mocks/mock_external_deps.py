"""
Mock External Dependencies

Provides mock implementations for external libraries that may not be
available in the test environment.
"""

from unittest.mock import MagicMock, Mock
import sys

# Mock CrewAI
class MockAgent:
    def __init__(self, *args, **kwargs):
        self.role = kwargs.get('role', 'mock_agent')
        self.goal = kwargs.get('goal', 'mock_goal')
        self.backstory = kwargs.get('backstory', 'mock_backstory')
        self.tools = kwargs.get('tools', [])
        
class MockCrew:
    def __init__(self, *args, **kwargs):
        self.agents = kwargs.get('agents', [])
        self.tasks = kwargs.get('tasks', [])
        
    def kickoff(self):
        return {'result': 'mock_output'}

# Mock LangChain components
class MockChatOpenAI:
    def __init__(self, *args, **kwargs):
        pass
    
    def invoke(self, messages):
        return Mock(content="Mock response")

class MockBaseTool:
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', 'mock_tool')
        self.description = kwargs.get('description', 'Mock tool description')

class MockTool:
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', 'mock_tool')
        self.description = kwargs.get('description', 'Mock tool description')

# Mock ChromaDB
class MockChromaClient:
    def __init__(self, *args, **kwargs):
        pass
    
    def get_or_create_collection(self, name):
        return MockCollection(name)
        
class MockCollection:
    def __init__(self, name):
        self.name = name
        
    def add(self, *args, **kwargs):
        pass
        
    def query(self, *args, **kwargs):
        return {'documents': [['Mock document']], 'ids': [['mock_id']]}

# Install mocks in sys.modules if the real modules aren't available
mock_modules = {
    'crewai': Mock(Agent=MockAgent, Crew=MockCrew),
    'langchain_openai': Mock(ChatOpenAI=MockChatOpenAI),
    'langchain_core.tools': Mock(BaseTool=MockBaseTool, Tool=MockTool),
    'chromadb': Mock(Client=MockChromaClient),
    'dotenv': Mock(load_dotenv=Mock()),
    'schedule': Mock(),
}

def install_mocks():
    """Install mock modules for missing dependencies."""
    for module_name, mock_module in mock_modules.items():
        if module_name not in sys.modules:
            sys.modules[module_name] = mock_module

# Auto-install mocks when this module is imported
install_mocks()