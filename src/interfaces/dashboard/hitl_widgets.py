"""HITL widgets for dashboard."""

class HITLWidget:
    """Human-in-the-loop widget."""
    
    def __init__(self, widget_id):
        self.widget_id = widget_id
    
    def render(self):
        """Render widget."""
        return {"id": self.widget_id, "type": "hitl_widget"}

class TaskReviewWidget(HITLWidget):
    """Task review widget."""
    
    def __init__(self):
        super().__init__("task_review")
    
    def get_pending_tasks(self):
        """Get pending tasks."""
        return []

__all__ = ["HITLWidget", "TaskReviewWidget"]
