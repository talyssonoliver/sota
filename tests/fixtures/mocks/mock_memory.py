"""
from unittest.mock import Mock, MagicMock
Mock Memory System for Tests

Provides lightweight mocks for memory system components.
"""

try:
    pass
except ImportError:
    pass
from typing import Any, Dict, List

try:
    pass
except ImportError:
    pass


class MockMemoryEngine:
    """Mock memory engine for unit tests."""

    def __init__(self):
        self.stored_data = {}
        self.search_results = []

    def store(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        key = metadata.get("id", hash(content)) if metadata else hash(content)
        self.stored_data[key] = {"content": content, "metadata": metadata or {}}
        return True

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.search_results[:limit]

    def set_search_results(self, results: List[Dict[str, Any]]):
        """Set mock search results."""
        self.search_results = results


class MockUnifiedMemorySystem:
    """Mock unified memory system."""

    def __init__(self):
        self.engine = MockMemoryEngine()
        self.contexts = {}

    def store_knowledge(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        return self.engine.store(content, metadata)

    def retrieve_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.engine.search(query, limit)

    def get_context(self, context_type: str = "active") -> Dict[str, Any]:
        return self.contexts.get(context_type, {})

    def health_check(self) -> Dict[str, Any]:
        return {"status": "mock", "components": {"engine": "mock"}}


def get_mock_memory_system():
    """Get mock memory system instance."""
    return MockUnifiedMemorySystem()
