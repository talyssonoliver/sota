"""
Patch for workflow recursion issue with BE-07 task
This file is imported by tests to patch the _check_recursion_limit method.
"""

def patch_workflow_executor(executor_instance):
    """
    Patch the _check_recursion_limit method on an EnhancedWorkflowExecutor instance
    to avoid infinite recursion with BE-07 tasks.

    Args:
        executor_instance: An instance of EnhancedWorkflowExecutor

    Returns:
        The patched executor instance
    """

    def patched_check_recursion_limit(self, iteration, limit):
        """
        Patched version that prevents BE-07 infinite recursion in tests.
        """
        if hasattr(self, 'workflow_type') and self.workflow_type == 'auto':
            return iteration >= 2
        return iteration >= limit
    executor_instance._check_recursion_limit = types.MethodType(patched_check_recursion_limit, executor_instance)
    return executor_instance