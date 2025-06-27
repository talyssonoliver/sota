"""
Mock Environment Module - provides mocking utilities for tests.
"""
import sys
from unittest.mock import MagicMock
from typing import Any

class MockModule:
    """A generic mock module that can be used for any missing dependency."""

    def __init__(self, name: str):
        self.name = name

    def __getattr__(self, item: str) -> Any:
        return MagicMock()

    def __call__(self, *args, **kwargs) -> Any:
        return MagicMock()

def mock_external_dependencies():
    """Mock all external dependencies that may not be available in test environment."""
    external_modules = ['crewai', 'crewai.api', 'crewai.models', 'crewai.config', 'crewai.tools', 'langchain', 'langchain.chains', 'langchain.agents', 'langchain.tools', 'langchain_core', 'langchain_core.runnables', 'langchain_core.tools', 'langchain_community', 'langchain_community.chat_models', 'langchain_openai', 'langsmith', 'chromadb', 'chromadb.api', 'chromadb.models', 'matplotlib', 'matplotlib.pyplot', 'matplotlib.colors', 'plotly', 'plotly.graph_objects', 'plotly.express', 'selenium', 'selenium.webdriver', 'selenium.webdriver.chrome.options', 'langgraph', 'langgraph.checkpoint', 'langgraph.graph']
    for module_name in external_modules:
        sys.modules[module_name] = MockModule(module_name)

def setup_test_mocks():
    """Set up all necessary mocks for testing."""
    mock_external_dependencies()
    return True
MockAgent = MagicMock
MockTask = MagicMock
MockWorkflow = MagicMock
MockMemoryEngine = MagicMock
setup_test_mocks()