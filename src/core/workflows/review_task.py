"""Review task workflow."""

def review_task(task):
    """Review a task."""
    return {"task": task, "review": "approved", "status": "completed"}

__all__ = ["review_task"]
