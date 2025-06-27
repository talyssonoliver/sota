"""
from typing import Dict, Any
Task Factory for Tests
"""
try:
    pass
except ImportError:
    pass

class TestTaskFactory:
    """Factory for creating test tasks."""

    @staticmethod
    def create_task(task_id: str='TEST-01', **kwargs) -> Dict[str, Any]:
        """Create mock task."""
        return {'task_id': task_id, 'title': kwargs.get('title', f'Test Task {task_id}'), 'description': kwargs.get('description', 'Test task description'), 'status': kwargs.get('status', 'pending'), 'agent_type': kwargs.get('agent_type', 'backend'), 'priority': kwargs.get('priority', 'medium'), **kwargs}

    @staticmethod
    def create_task_batch(count: int=5) -> List[Dict[str, Any]]:
        """Create batch of test tasks."""
        return [TestTaskFactory.create_task(f'TEST-{i:02d}') for i in range(1, count + 1)]