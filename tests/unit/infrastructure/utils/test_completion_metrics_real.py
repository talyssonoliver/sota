"""
Real test for completion metrics that actually executes source code.
This test demonstrates how to achieve proper test coverage.
"""

from pathlib import Path
from src.infrastructure.utils.completion_metrics import CompletionMetrics, CompletionMetricsCalculator


class TestCompletionMetricsReal:
    """Real tests that execute source code and generate coverage."""

    def test_completion_metrics_init(self):
        """Test CompletionMetrics initialization."""
        metrics = CompletionMetrics()
        assert metrics.metrics == {}

    def test_calculate_completion_rate_empty_tasks(self):
        """Test completion rate calculation with empty tasks."""
        metrics = CompletionMetrics()
        result = metrics.calculate_completion_rate([])
        assert result == 0.0

    def test_calculate_completion_rate_no_completed_tasks(self):
        """Test completion rate with no completed tasks."""
        metrics = CompletionMetrics()
        tasks = [
            {"status": "pending"},
            {"status": "in_progress"},
            {"status": "failed"}
        ]
        result = metrics.calculate_completion_rate(tasks)
        assert result == 0.0

    def test_calculate_completion_rate_all_completed(self):
        """Test completion rate with all completed tasks."""
        metrics = CompletionMetrics()
        tasks = [
            {"status": "completed"},
            {"status": "completed"},
            {"status": "completed"}
        ]
        result = metrics.calculate_completion_rate(tasks)
        assert result == 100.0

    def test_calculate_completion_rate_mixed_tasks(self):
        """Test completion rate with mixed task statuses."""
        metrics = CompletionMetrics()
        tasks = [
            {"status": "completed"},
            {"status": "pending"},
            {"status": "completed"},
            {"status": "in_progress"}
        ]
        result = metrics.calculate_completion_rate(tasks)
        assert result == 50.0  # 2 out of 4 completed

    def test_get_metrics_summary(self):
        """Test getting metrics summary."""
        metrics = CompletionMetrics()
        summary = metrics.get_metrics_summary()
        assert summary == {}
        
        # Test after adding metrics
        metrics.metrics = {"completion_rate": 75.0}
        summary = metrics.get_metrics_summary()
        assert summary == {"completion_rate": 75.0}

    def test_completion_metrics_calculator_init(self):
        """Test CompletionMetricsCalculator initialization."""
        calculator = CompletionMetricsCalculator()
        assert calculator is not None
        
        # Test with dashboard_dir parameter using temporary directory
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "test_dashboard"
            calculator_with_dir = CompletionMetricsCalculator(dashboard_dir=str(test_path))
            assert calculator_with_dir is not None
            assert test_path.exists()

    def test_calculate_completion_rate_edge_cases(self):
        """Test edge cases for completion rate calculation."""
        metrics = CompletionMetrics()
        
        # Test with None tasks
        result = metrics.calculate_completion_rate(None)
        assert result == 0.0
        
        # Test with tasks missing status
        tasks_missing_status = [{"name": "task1"}, {"name": "task2"}]
        result = metrics.calculate_completion_rate(tasks_missing_status)
        assert result == 0.0
        
        # Test with mixed status formats
        mixed_tasks = [
            {"status": "completed"},
            {"status": "COMPLETED"},  # Different case
            {"status": "done"},       # Different value
            {"status": "completed"}
        ]
        result = metrics.calculate_completion_rate(mixed_tasks)
        assert result == 50.0  # Only exact "completed" matches count