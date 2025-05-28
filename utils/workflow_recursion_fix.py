"""
Workflow Recursion Fix for BE-07 and similar tasks.
This module provides patches to prevent infinite recursion in workflow execution.
"""

import logging
import types
from typing import Any, Optional

logger = logging.getLogger(__name__)


class WorkflowRecursionLimiter:
    """Helper class to manage workflow recursion limits safely."""

    def __init__(self, max_iterations: int = 5):
        self.max_iterations = max_iterations
        self.iteration_counts = {}

    def check_limit(self, task_id: str, current_iteration: int) -> bool:
        """Check if task has exceeded iteration limit."""
        if task_id not in self.iteration_counts:
            self.iteration_counts[task_id] = 0

        self.iteration_counts[task_id] = current_iteration

        if current_iteration >= self.max_iterations:
            logger.warning(
                f"Task {task_id} reached iteration limit ({
                    self.max_iterations})")
            return False

        return True

    def reset_count(self, task_id: str):
        """Reset iteration count for a task."""
        if task_id in self.iteration_counts:
            del self.iteration_counts[task_id]


def patch_workflow_executor(executor_instance, max_iterations: int = 5):
    """
    Patch the _check_recursion_limit method on an EnhancedWorkflowExecutor instance
    to avoid infinite recursion with BE-07 and similar tasks.

    Args:
        executor_instance: An instance of EnhancedWorkflowExecutor
        max_iterations: Maximum iterations before stopping (default: 5)

    Returns:
        The patched executor instance
    """
    limiter = WorkflowRecursionLimiter(max_iterations)

    def patched_check_recursion_limit(self, iteration: int, limit: int):
        """Fixed recursion limit check that prevents infinite loops."""
        task_id = getattr(self, 'current_task_id', 'UNKNOWN')

        # Use the limiter to check safely
        if not limiter.check_limit(task_id, iteration):
            logger.warning(
                f"Stopping execution for task {task_id} at iteration {iteration}")
            return False

        return True

    # Apply the patch
    executor_instance._check_recursion_limit = types.MethodType(
        patched_check_recursion_limit, executor_instance
    )

    # Add method to reset counts if needed
    def reset_recursion_count(self, task_id: str):
        limiter.reset_count(task_id)

    executor_instance.reset_recursion_count = types.MethodType(
        reset_recursion_count, executor_instance
    )

    logger.info(
        f"Applied recursion patch to executor with limit: {max_iterations}")
    return executor_instance


def create_safe_workflow_executor(*args, **kwargs):
    """
    Factory function to create a workflow executor with recursion protection.
    """
    from orchestration.enhanced_workflow import EnhancedWorkflowExecutor

    # Get max_iterations from kwargs or use default
    max_iterations = kwargs.pop('max_iterations', 5)

    # Create the executor
    executor = EnhancedWorkflowExecutor(*args, **kwargs)

    # Apply the recursion patch
    return patch_workflow_executor(executor, max_iterations)


def ensure_recursion_protection(executor_instance, max_iterations: int = 5):
    """
    Ensure that an executor instance has recursion protection.
    Safe to call multiple times.
    """
    if not hasattr(executor_instance, '_recursion_patched'):
        patch_workflow_executor(executor_instance, max_iterations)
        executor_instance._recursion_patched = True

    return executor_instance
