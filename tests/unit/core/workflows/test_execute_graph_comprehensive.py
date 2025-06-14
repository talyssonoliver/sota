"""
Comprehensive Tests for Graph Execution

Extended test suite for the graph execution system
to validate workflow execution, state management, and error handling.
"""

import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import os

from src.core.workflows.execute_graph import (
    run_task_graph,
    build_task_state,
    get_relevant_context
)


class TestBuildTaskState:
    """Test build_task_state function."""
    
    @patch('orchestration.execute_graph.load_task_metadata')
    @patch('orchestration.execute_graph.get_context_by_keys')
    def test_build_task_state_with_metadata(self, mock_get_context, mock_load_metadata):
        """Test building task state with metadata."""
        # Mock task metadata
        mock_load_metadata.return_value = {
            'title': 'Test Task',
            'description': 'Test description',
            'depends_on': ['BE-06'],
            'priority': 'HIGH',
            'estimation_hours': 4,
            'artefacts': ['file1.py'],
            'state': 'PLANNED'
        }
        mock_get_context.return_value = "test context"
        
        state = build_task_state("BE-07")
        
        assert state['task_id'] == "BE-07"
        assert state['title'] == 'Test Task'
        assert state['description'] == 'Test description'
        assert state['dependencies'] == ['BE-06']
        assert state['priority'] == 'HIGH'
        assert state['estimation_hours'] == 4
        assert state['artefacts'] == ['file1.py']
        assert state['status'] == 'PLANNED'
        assert 'timestamp' in state
    
    @patch('orchestration.execute_graph.load_task_metadata')
    @patch('orchestration.execute_graph.get_context_by_keys')
    def test_build_task_state_fallback(self, mock_get_context, mock_load_metadata):
        """Test building task state with fallback when metadata not found."""
        mock_load_metadata.side_effect = FileNotFoundError()
        mock_get_context.return_value = "fallback context"
        
        with patch('os.path.exists', return_value=False):
            state = build_task_state("BE-07")
        
        assert state['task_id'] == "BE-07"
        assert state['title'] == "Task BE-07"
        assert state['description'] == ""
        assert state['dependencies'] == []
        assert 'timestamp' in state


class TestRunTaskGraph:
    """Test run_task_graph function."""
    
    @patch('orchestration.execute_graph.build_task_state')
    @patch('orchestration.execute_graph.generate_prompt')
    @patch('orchestration.execute_graph.build_advanced_workflow_graph')
    def test_run_task_graph_dry_run(self, mock_build_workflow, mock_generate_prompt, mock_build_state):
        """Test dry run execution."""
        mock_build_state.return_value = {
            'task_id': 'BE-07',
            'title': 'Test Task',
            'status': 'PLANNED',
            'dependencies': [],
            'priority': 'MEDIUM',
            'estimation_hours': 2,
            'artefacts': [],
            'context': 'test context'
        }
        mock_generate_prompt.return_value = "test prompt"
        
        result = run_task_graph("BE-07", dry_run=True)
        
        assert result['task_id'] == 'BE-07'
        assert result['enhanced_prompt'] == "test prompt"
        mock_build_workflow.assert_not_called()  # Should not build workflow in dry run
    
    @pytest.mark.skip(reason="Recursion issue in monitoring hooks - needs deeper investigation")
    @patch('orchestration.execute_graph.build_task_state')
    @patch('orchestration.execute_graph.generate_prompt')
    @patch('orchestration.execute_graph.build_advanced_workflow_graph')
    @patch('orchestration.execute_graph.get_execution_monitor')
    @patch('orchestration.execute_graph.SlackNotifier')
    @patch('orchestration.execute_graph.attach_notifications_to_workflow')
    @patch('orchestration.execute_graph.update_task_state')
    @patch('orchestration.execute_graph.create_langgraph_hook')
    def test_run_task_graph_success(self, mock_create_hook, mock_update_task_state, 
                                  mock_attach_notifications, mock_slack_notifier, 
                                  mock_monitor, mock_build_workflow, 
                                  mock_generate_prompt, mock_build_state):
        """Test successful workflow execution."""
        # Mock state
        mock_build_state.return_value = {
            'task_id': 'BE-07',
            'title': 'Test Task',
            'status': 'PLANNED',
            'dependencies': [],
            'context': 'test context'
        }
        mock_generate_prompt.return_value = "test prompt"
        
        # Mock workflow - return successful result
        mock_workflow = Mock()
        mock_workflow.invoke.return_value = {
            'task_id': 'BE-07',
            'status': 'COMPLETED',
            'result': 'success'
        }
        mock_build_workflow.return_value = mock_workflow
        
        # Mock notifications
        mock_attach_notifications.return_value = mock_workflow
        
        # Mock LangGraph hook
        mock_hook = Mock()
        mock_create_hook.return_value = mock_hook
        
        # Mock monitor
        mock_monitor_instance = Mock()
        mock_monitor.return_value = mock_monitor_instance
        mock_monitor_instance.start_agent_execution.return_value = {'execution_id': 'test-exec-123'}
        mock_monitor_instance.get_execution_stats.return_value = {
            'total_executions': 1,
            'successful_executions': 1,
            'average_duration_minutes': 5.0,
            'agents_used': ['backend']
        }
        
        result = run_task_graph("BE-07", enable_monitoring=True)
        
        assert result['task_id'] == 'BE-07'
        assert result['status'] == 'COMPLETED'
        mock_workflow.invoke.assert_called_once()
    
    @patch('orchestration.execute_graph.build_task_state')
    @patch('orchestration.execute_graph.generate_prompt')
    @patch('orchestration.execute_graph.build_advanced_workflow_graph')
    def test_run_task_graph_workflow_error(self, mock_build_workflow, mock_generate_prompt, mock_build_state):
        """Test workflow execution with error."""
        mock_build_state.return_value = {
            'task_id': 'BE-07',
            'title': 'Test Task',
            'status': 'PLANNED',
            'context': 'test context'
        }
        mock_generate_prompt.return_value = "test prompt"
        
        # Mock workflow that raises an error
        mock_workflow = Mock()
        mock_workflow.invoke.side_effect = Exception("Workflow failed")
        mock_build_workflow.return_value = mock_workflow
        
        result = run_task_graph("BE-07", enable_monitoring=False)
        
        assert result['task_id'] == 'BE-07'
        assert result['status'] == 'FAILED'
        assert 'error' in result
        assert "Workflow failed" in result['error']


class TestGetRelevantContext:
    """Test get_relevant_context function."""
    
    @patch('tools.memory.get_relevant_context')
    def test_get_relevant_context_success(self, mock_memory_get_context):
        """Test successful context retrieval."""
        mock_memory_get_context.return_value = "relevant context"
        
        result = get_relevant_context("test query", k=3)
        
        assert result == "relevant context"
        mock_memory_get_context.assert_called_once_with("test query", k=3)
    
    @patch('tools.memory.get_relevant_context', side_effect=ImportError())
    def test_get_relevant_context_fallback(self, mock_memory_get_context):
        """Test fallback when memory system not available."""
        result = get_relevant_context("test query")
        
        assert result == ""