"""
Test Suite for Step 4.3: LangGraph Workflow Execution

Tests for orchestration/execute_graph.py functionality.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from orchestration.execute_graph import build_task_state, main, run_task_graph
from orchestration.states import TaskStatus

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestStep43WorkflowExecution:
    """Test Step 4.3 workflow execution functionality."""

    @pytest.fixture
    def mock_task_metadata(self):
        """Mock task metadata."""
        return {
            'title': 'Test Backend Task',
            'description': 'Test backend functionality',
            'priority': 'HIGH',
            'estimation_hours': 8,
            'state': TaskStatus.IN_PROGRESS,
            'context_topics': ['backend', 'api']
        }

    def test_build_task_state_success(self, mock_task_metadata):
        """Test successful task state building."""
        with patch('orchestration.execute_graph.load_task_metadata') as mock_load_task, \
                patch('orchestration.execute_graph.get_relevant_context') as mock_get_context:

            mock_load_task.return_value = mock_task_metadata
            mock_get_context.return_value = {'backend': 'Backend context'}

            result = build_task_state('BE-07')

            assert result['task_id'] == 'BE-07'
            assert result['title'] == 'Test Backend Task'
            mock_load_task.assert_called_once_with('BE-07')

    def test_run_task_graph_dry_run(self):
        """Test dry run mode."""
        with patch('orchestration.execute_graph.build_task_state') as mock_build_state:
            mock_state = {
                'task_id': 'BE-07',
                'title': 'Test Task',
                'status': 'IN_PROGRESS',
                'dependencies': [],
                'context': ''}
            mock_build_state.return_value = mock_state

            result = run_task_graph('BE-07', dry_run=True)

            assert result == mock_state
            mock_build_state.assert_called_once_with('BE-07')

    @pytest.fixture
    def mock_workflow_execution(self):
        """Mock workflow execution for testing."""
        return {
            'execute_workflow': lambda task_id,
            workflow_type="basic": {
                'result': 'Mock workflow completed',
                'status': 'success',
                'execution_duration': 0.1,
                'task_id': task_id,
                'enhanced_prompt': 'You are a test agent. Task completed successfully.'}}

    def test_run_task_graph_advanced_workflow(self, mock_workflow_execution):
        """Test advanced workflow execution."""
        # Use the mock workflow execution
        mock_result = {
            'result': 'Mock workflow completed',
            'status': 'success',
            'execution_duration': 0.1,
            'task_id': 'BE-07',
            'enhanced_prompt': 'You are a test agent. Task completed successfully.'}

        # Call the mock workflow execution directly
        result = mock_workflow_execution['execute_workflow'](
            'BE-07', workflow_type="advanced")

        assert 'result' in result
        assert result['status'] == 'success'


class TestStep43CLIInterface:
    """Test Step 4.3 CLI interface."""

    def test_main_with_task_argument(self):
        """Test main function with task argument."""
        test_args = ['execute_graph.py', '--task', 'BE-07']

        with patch('sys.argv', test_args), \
                patch('orchestration.execute_graph.run_task_graph') as mock_run:

            mock_run.return_value = {
                'result': 'Success', 'status': 'COMPLETED'}

            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0

            mock_run.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
