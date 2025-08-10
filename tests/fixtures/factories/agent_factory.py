"""
Agent Factory for Tests
"""

try:
    from tests.fixtures.mocks.mock_agents import create_mock_agent
except ImportError:

    def create_mock_agent(agent_type):
        """Fallback mock agent function."""
        from unittest.mock import Mock

        return Mock(agent_type=agent_type)


class TestAgentFactory:
    """Factory for creating test agents."""

    @staticmethod
    def create_backend_agent(**kwargs):
        """Create mock backend agent."""
        return create_mock_agent("backend")

    @staticmethod
    def create_qa_agent(**kwargs):
        """Create mock QA agent."""
        return create_mock_agent("qa")

    @staticmethod
    def create_coordinator(**kwargs):
        """Create mock coordinator."""
        return create_mock_agent("coordinator")
