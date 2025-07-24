"""
Test Utilities Module

Provides common utilities and helpers for the AI system test suite.
This module consolidates test utilities that were previously scattered
across multiple files and locations.

Usage:
    from tests.utils import create_test_context, setup_test_environment
    
    # Set up test environment
    setup_test_environment()
    
    # Create test context for workflows
    context = create_test_context()
"""

from tests.utils import workflow_helpers
from tests.utils import test_utils

# Re-export specific functions for convenience
try:
    from tests.utils.workflow_helpers import (
        setup_workflow_test,
        create_mock_workflow_state,
        validate_workflow_output,
        simulate_workflow_execution,
        create_test_task,
        create_test_agent_config,
        WorkflowTestHelper,
    )
except ImportError:
    pass

try:
    from tests.utils.test_utils import (
        create_test_context,
        setup_test_environment,
        cleanup_test_environment,
        create_temporary_file,
        create_temporary_directory,
        wait_for_condition,
        assert_eventually,
        mock_environment_variables,
        capture_logs,
        TestContextManager,
        TemporaryEnvironment,
    )
except ImportError:
    pass
__all__ = [
    "create_test_context",
    "setup_test_environment",
    "cleanup_test_environment",
    "create_temporary_file",
    "create_temporary_directory",
    "wait_for_condition",
    "assert_eventually",
    "mock_environment_variables",
    "capture_logs",
    "TestContextManager",
    "TemporaryEnvironment",
    "setup_workflow_test",
    "create_mock_workflow_state",
    "validate_workflow_output",
    "simulate_workflow_execution",
    "create_test_task",
    "create_test_agent_config",
    "WorkflowTestHelper",
    "workflow_helpers",
    "test_utils",
]
