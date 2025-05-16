"""
Specialized test runner for memory config integration.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our mock environment
from tests.mock_environment import setup_mock_environment

class TestMemoryConfig(unittest.TestCase):
    """Test the memory configuration integration specifically."""
    
    def setUp(self):
        """Set up the test environment."""
        # Set the environment variable to indicate we're in a testing environment
        os.environ["TESTING"] = "1"
        # Set up the mock environment
        self.mock_env = setup_mock_environment()
    
    def test_memory_config_integration(self):
        """Test that memory config is properly passed to the Agent constructor."""
        # Create a special recorder class for the Agent constructor
        class MemoryAwareAgentMock:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                # Explicitly save memory field
                self.memory = kwargs.get('memory')
                
            def __getattr__(self, name):
                if name in self.kwargs:
                    return self.kwargs[name]
                return MagicMock()
        
        # Create a memory config to test with
        memory_config = {"type": "redis", "ttl": 3600}
        
        # Patch the Agent constructor to use our mock
        with patch('crewai.Agent', side_effect=MemoryAwareAgentMock):
            # Import after patching so import uses our patched version
            from agents.frontend import create_frontend_engineer_agent
            
            # Create the agent with memory config
            agent = create_frontend_engineer_agent(
                memory_config=memory_config,
                custom_tools=[]
            )
            
            # Verify memory config was passed correctly
            self.assertEqual(
                agent.memory,
                memory_config,
                f"Memory config was not correctly passed to Agent constructor. Got: {agent.memory}"
            )


if __name__ == "__main__":
    unittest.main()