"""Completion metrics utilities."""

class CompletionMetrics:
    """Track and calculate completion metrics."""
    
    def __init__(self):
        """Initialize completion metrics."""
        self.metrics = {}
    
    def calculate_completion_rate(self, tasks):
        """Calculate completion rate for tasks."""
        if not tasks:
            return 0.0
        completed = sum(1 for task in tasks if task.get('status') == 'completed')
        return completed / len(tasks) * 100
    
    def get_metrics_summary(self):
        """Get metrics summary."""
        return self.metrics

class CompletionMetricsCalculator:
    """Calculate completion metrics for tasks and workflows."""
    
    def __init__(self):
        """Initialize completion metrics calculator."""
        self.metrics = {}
        self.calculations = CompletionMetrics()
    
    def calculate_task_completion_rate(self, tasks):
        """Calculate completion rate for a list of tasks."""
        return self.calculations.calculate_completion_rate(tasks)
    
    def calculate_daily_metrics(self, day_data):
        """Calculate daily completion metrics."""
        if not day_data:
            return {
                'completion_rate': 0.0,
                'total_tasks': 0,
                'completed_tasks': 0,
                'pending_tasks': 0,
                'failed_tasks': 0
            }
        
        tasks = day_data.get('tasks', [])
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.get('status') == 'completed')
        pending_tasks = sum(1 for task in tasks if task.get('status') == 'pending')
        failed_tasks = sum(1 for task in tasks if task.get('status') == 'failed')
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        
        return {
            'completion_rate': completion_rate,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'failed_tasks': failed_tasks
        }
    
    def get_progress_summary(self, data):
        """Get progress summary with metrics."""
        return {
            'daily_metrics': self.calculate_daily_metrics(data),
            'overall_progress': self.calculations.get_metrics_summary()
        }

__all__ = ["CompletionMetrics", "CompletionMetricsCalculator"]
