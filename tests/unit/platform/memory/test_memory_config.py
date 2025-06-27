"""
Specialized test runner for memory config integration.
"""
import logging
import os
import sys
import unittest
from unittest.mock import MagicMock, patch
try:
    from tests.mock_environment import setup_mock_environment
except ImportError as e:
    logging.warning(f'Failed to import mock environment: {e}')

    def setup_mock_environment():
        """Fallback mock environment setup."""
        return {}
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMemoryConfig(unittest.TestCase):
    """Test the memory configuration integration specifically."""

    def setUp(self):
        """Set up the test environment."""
        os.environ['TESTING'] = '1'
        self.mock_env = setup_mock_environment()

    def test_memory_config_integration(self):
        """Test that memory config is properly passed to the Agent constructor."""

        class MemoryAwareAgentMock:

            def __init__(self, **kwargs):
                self.kwargs = kwargs
                self.memory = kwargs.get('memory') or kwargs.get('memory_config')

            def __getattr__(self, name):
                if name in self.kwargs:
                    return self.kwargs[name]
                return MagicMock()
        memory_config = {'type': 'redis', 'ttl': 3600}
        with patch('src.core.agents.factory.Agent', side_effect=MemoryAwareAgentMock):
            from src.core.agents.factory import create_frontend_engineer_agent
            agent = create_frontend_engineer_agent(memory_config=memory_config, custom_tools=[])
            self.assertEqual(agent.memory, memory_config, f'Memory config was not correctly passed to Agent constructor. Got: {agent.memory}')
if __name__ == '__main__':
    unittest.main()