"""Inject context workflow."""


def inject_context(task, context):
    """Inject context into task."""
    return {"task": task, "context": context, "status": "injected"}


class ContextInjector:
    """Context injection utility class."""

    def prepare_agent_with_context(self, task_id, agent_role):
        """Prepare agent with injected context."""
        # Mock implementation for now
        return {
            "task_id": task_id,
            "agent_role": agent_role,
            "context": "injected_context",
            "status": "prepared",
        }


# Create a module-level instance for backward compatibility
context_injector = ContextInjector()

__all__ = ["inject_context", "context_injector", "ContextInjector"]
