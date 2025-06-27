"""
Workflow Test Helpers

Utilities for testing workflow components including agent orchestration,
task execution, and state management.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import Mock
try:
    from tests.utils.test_utils import create_temporary_directory, create_temporary_file
except ImportError as e:
    logging.warning(f'Failed to import test utilities: {e}')

    def create_temporary_directory():
        """Fallback temporary directory creation."""
        import tempfile
        return tempfile.mkdtemp()

    def create_temporary_file():
        """Fallback temporary file creation."""
        import tempfile
        return tempfile.mktemp()

class WorkflowTestHelper:
    """Helper class for testing workflow components."""

    def __init__(self):
        self.mock_agents = {}
        self.mock_tasks = {}
        self.mock_states = {}
        self.temp_files = []

    def create_mock_agent(self, agent_type: str, **kwargs) -> Mock:
        """Create a mock agent with standard interface."""
        mock_agent = Mock()
        mock_agent.name = kwargs.get('name', f'mock_{agent_type}')
        mock_agent.role = agent_type
        mock_agent.backstory = kwargs.get('backstory', f'Mock {agent_type} for testing')
        mock_agent.goal = kwargs.get('goal', f'Execute {agent_type} tasks')
        mock_agent.verbose = kwargs.get('verbose', True)
        mock_agent.allow_delegation = kwargs.get('allow_delegation', False)
        mock_agent.execute_task = Mock(return_value={'success': True, 'result': f'Mock result from {agent_type}', 'metadata': {'agent': agent_type, 'timestamp': datetime.now().isoformat()}})
        mock_agent.get_tools = Mock(return_value=[])
        mock_agent.get_context = Mock(return_value={})
        mock_agent.validate_input = Mock(return_value=True)
        self.mock_agents[agent_type] = mock_agent
        return mock_agent

    def create_mock_task(self, task_id: str, **kwargs) -> Dict[str, Any]:
        """Create a mock task definition."""
        task = {'id': task_id, 'title': kwargs.get('title', f'Test Task {task_id}'), 'description': kwargs.get('description', f'Mock task {task_id} for testing'), 'agent_type': kwargs.get('agent_type', 'test_agent'), 'dependencies': kwargs.get('dependencies', []), 'expected_output': kwargs.get('expected_output', 'Mock output'), 'context': kwargs.get('context', {}), 'tools': kwargs.get('tools', []), 'priority': kwargs.get('priority', 'medium'), 'estimated_duration': kwargs.get('estimated_duration', 300), 'created_at': datetime.now().isoformat(), 'status': kwargs.get('status', 'pending')}
        self.mock_tasks[task_id] = task
        return task

    def create_mock_workflow_state(self, workflow_id: str=None, **kwargs) -> Dict[str, Any]:
        """Create a mock workflow state."""
        if not workflow_id:
            workflow_id = f'test_workflow_{len(self.mock_states) + 1}'
        state = {'workflow_id': workflow_id, 'status': kwargs.get('status', 'running'), 'current_step': kwargs.get('current_step', 'init'), 'steps_completed': kwargs.get('steps_completed', 0), 'total_steps': kwargs.get('total_steps', 5), 'start_time': kwargs.get('start_time', datetime.now().isoformat()), 'end_time': kwargs.get('end_time'), 'progress': kwargs.get('progress', 0.0), 'agents': kwargs.get('agents', {}), 'tasks': kwargs.get('tasks', {}), 'results': kwargs.get('results', {}), 'errors': kwargs.get('errors', []), 'warnings': kwargs.get('warnings', []), 'metadata': kwargs.get('metadata', {'test_workflow': True, 'created_by': 'WorkflowTestHelper'})}
        self.mock_states[workflow_id] = state
        return state

    def simulate_workflow_execution(self, workflow_id: str, steps: List[str], step_duration: float=0.1) -> Dict[str, Any]:
        """Simulate workflow execution through multiple steps."""
        import time
        state = self.mock_states.get(workflow_id) or self.create_mock_workflow_state(workflow_id)
        for i, step in enumerate(steps):
            state['current_step'] = step
            state['steps_completed'] = i
            state['progress'] = i / len(steps)
            time.sleep(step_duration)
            state['results'][step] = {'success': True, 'output': f'Mock output for step {step}', 'timestamp': datetime.now().isoformat()}
        state['status'] = 'completed'
        state['steps_completed'] = len(steps)
        state['progress'] = 1.0
        state['end_time'] = datetime.now().isoformat()
        return state

    def create_test_workflow_config(self, **kwargs) -> Dict[str, Any]:
        """Create a test workflow configuration."""
        return {'name': kwargs.get('name', 'test_workflow'), 'description': kwargs.get('description', 'Test workflow for unit testing'), 'version': kwargs.get('version', '1.0.0'), 'agents': kwargs.get('agents', [{'type': 'test_agent', 'name': 'test_agent_1'}, {'type': 'qa_agent', 'name': 'qa_agent_1'}]), 'tasks': kwargs.get('tasks', [{'id': 'task_1', 'agent_type': 'test_agent'}, {'id': 'task_2', 'agent_type': 'qa_agent', 'dependencies': ['task_1']}]), 'max_iterations': kwargs.get('max_iterations', 10), 'timeout': kwargs.get('timeout', 3600), 'retry_attempts': kwargs.get('retry_attempts', 3), 'parallel_execution': kwargs.get('parallel_execution', False), 'memory_enabled': kwargs.get('memory_enabled', True), 'logging_enabled': kwargs.get('logging_enabled', True)}

    def validate_workflow_output(self, output: Dict[str, Any], expected_keys: List[str]=None) -> bool:
        """Validate workflow output structure and content."""
        if expected_keys is None:
            expected_keys = ['workflow_id', 'status', 'results']
        for key in expected_keys:
            if key not in output:
                raise AssertionError(f"Missing required key '{key}' in workflow output")
        valid_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
        if output.get('status') not in valid_statuses:
            raise AssertionError(f"Invalid status '{output.get('status')}'. Must be one of {valid_statuses}")
        if 'progress' in output:
            progress = output['progress']
            if not 0.0 <= progress <= 1.0:
                raise AssertionError(f'Progress must be between 0.0 and 1.0, got {progress}')
        return True

    def create_test_memory_context(self, context_type: str='test') -> Dict[str, Any]:
        """Create test memory context for workflow testing."""
        return {'context_id': f'test_context_{context_type}', 'type': context_type, 'content': f'Test {context_type} context for workflow testing', 'tags': ['test', 'workflow', context_type], 'created_at': datetime.now().isoformat(), 'metadata': {'test_data': True, 'workflow_test': True}}

    def create_test_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """Create test agent configuration for workflow testing."""
        agent_configs = {'backend': {'role': 'Backend Engineer', 'goal': 'Implement backend services and APIs', 'backstory': 'Experienced backend developer specializing in API development', 'tools': ['github_tool', 'supabase_tool'], 'context_domains': ['backend', 'api', 'database']}, 'frontend': {'role': 'Frontend Engineer', 'goal': 'Create user interfaces and frontend components', 'backstory': 'Expert frontend developer with React and modern web technologies', 'tools': ['github_tool', 'vercel_tool'], 'context_domains': ['frontend', 'ui', 'react']}, 'qa': {'role': 'Quality Assurance Engineer', 'goal': 'Ensure code quality and test coverage', 'backstory': 'Meticulous QA engineer focused on automated testing and quality', 'tools': ['testing_tool', 'coverage_tool'], 'context_domains': ['testing', 'qa', 'quality']}, 'technical_lead': {'role': 'Technical Lead', 'goal': 'Coordinate technical decisions and architecture', 'backstory': 'Senior technical leader with expertise in system architecture', 'tools': ['architecture_tool', 'planning_tool'], 'context_domains': ['architecture', 'leadership', 'planning']}}
        config = agent_configs.get(agent_type, {'role': f'{agent_type.title()} Agent', 'goal': f'Execute {agent_type} related tasks', 'backstory': f'Mock {agent_type} agent for testing', 'tools': [], 'context_domains': [agent_type]})
        config.update({'name': f'test_{agent_type}_agent', 'verbose': True, 'allow_delegation': False, 'max_iter': 10, 'memory_enabled': True, 'test_mode': True})
        return config

    def cleanup(self):
        """Clean up test resources."""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception:
                pass
        self.mock_agents.clear()
        self.mock_tasks.clear()
        self.mock_states.clear()
        self.temp_files.clear()

def setup_workflow_test(workflow_name: str='test_workflow') -> WorkflowTestHelper:
    """Set up a workflow test environment."""
    return WorkflowTestHelper()

def create_mock_workflow_state(**kwargs) -> Dict[str, Any]:
    """Create a mock workflow state."""
    helper = WorkflowTestHelper()
    return helper.create_mock_workflow_state(**kwargs)

def validate_workflow_output(output: Dict[str, Any], expected_keys: List[str]=None) -> bool:
    """Validate workflow output structure and content."""
    helper = WorkflowTestHelper()
    return helper.validate_workflow_output(output, expected_keys)

def simulate_workflow_execution(workflow_id: str, steps: List[str], step_duration: float=0.1) -> Dict[str, Any]:
    """Simulate workflow execution through multiple steps."""
    helper = WorkflowTestHelper()
    return helper.simulate_workflow_execution(workflow_id, steps, step_duration)

def create_test_task(**kwargs) -> Dict[str, Any]:
    """Create a test task."""
    helper = WorkflowTestHelper()
    task_id = kwargs.pop('task_id', 'test_task_1')
    return helper.create_mock_task(task_id, **kwargs)

def create_test_agent_config(agent_type: str) -> Dict[str, Any]:
    """Create test agent configuration."""
    helper = WorkflowTestHelper()
    return helper.create_test_agent_config(agent_type)
__all__ = ['WorkflowTestHelper', 'setup_workflow_test', 'create_mock_workflow_state', 'validate_workflow_output', 'simulate_workflow_execution', 'create_test_task', 'create_test_agent_config']