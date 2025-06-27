"""Register output workflow."""

def register_output(task_id, output):
    """Register task output.""" 
    return {"task_id": task_id, "output": output, "status": "registered"}

__all__ = ["register_output"]
