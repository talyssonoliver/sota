"""Task declaration workflow."""

def declare_task(task_config):
    """Declare a new task."""
    return {"config": task_config, "status": "declared"}

__all__ = ["declare_task"]
