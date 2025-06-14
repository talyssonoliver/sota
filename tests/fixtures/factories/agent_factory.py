#!/usr/bin/env python3
"""
Agent Factory for Tests
"""

from tests.fixtures.mocks.mock_agents import create_mock_agent

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
