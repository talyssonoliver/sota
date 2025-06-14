#!/usr/bin/env python3
"""
Mock Agents for Tests

Provides lightweight mocks for agent system components.
"""

from typing import Dict, Any, List
from unittest.mock import Mock

class MockAgent:
    """Base mock agent."""
    
    def __init__(self, agent_type: str = "mock"):
        self.agent_type = agent_type
        self.responses = []
        self.call_count = 0
    
    def invoke(self, prompt: str, **kwargs) -> Dict[str, Any]:
        self.call_count += 1
        if self.responses:
            return self.responses.pop(0)
        return {"response": f"Mock response for: {prompt[:50]}...", "agent": self.agent_type}
    
    def set_responses(self, responses: List[Dict[str, Any]]):
        """Set mock responses."""
        self.responses = responses.copy()

class MockBackendAgent(MockAgent):
    """Mock backend agent."""
    
    def __init__(self):
        super().__init__("backend")

class MockQAAgent(MockAgent):
    """Mock QA agent."""
    
    def __init__(self):
        super().__init__("qa")

class MockCoordinator(MockAgent):
    """Mock coordinator."""
    
    def __init__(self):
        super().__init__("coordinator")

def create_mock_agent(agent_type: str) -> MockAgent:
    """Factory function for creating mock agents."""
    agent_classes = {
        "backend": MockBackendAgent,
        "qa": MockQAAgent,
        "coordinator": MockCoordinator
    }
    
    agent_class = agent_classes.get(agent_type, MockAgent)
    return agent_class()
