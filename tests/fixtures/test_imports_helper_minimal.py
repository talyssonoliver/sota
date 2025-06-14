"""
Minimal Test Import Helper for debugging terminal crashes
"""

import sys
from unittest.mock import MagicMock
import importlib


def setup_minimal_test_imports():
    """Setup only essential imports for testing."""
    
    # Preserve built-in platform module
    builtin_platform_module = importlib.import_module('platform')
    sys.modules['platform'] = builtin_platform_module
    
    # Mock only essential external dependencies
    essential_mocks = {
        'crewai': MagicMock(),
        'langchain_openai': MagicMock(),
        'langchain_core': MagicMock(),
        'chromadb': MagicMock(),
        'dotenv': MagicMock(),
        'pydantic': MagicMock(),
        'flask': MagicMock(),
        'flask_cors': MagicMock(),
        'numpy': MagicMock(),
        'psutil': MagicMock(),
    }
    
    for module_name, mock_obj in essential_mocks.items():
        if module_name not in sys.modules:
            sys.modules[module_name] = mock_obj
    
    # Mock memory modules with simple returns
    memory_mock = MagicMock()
    memory_mock.get_memory_instance.return_value.build_focused_context.return_value = "Mocked context about backend APIs and databases"
    sys.modules['src.platform.tools.memory'] = memory_mock
    
    print("Minimal test imports setup complete")
