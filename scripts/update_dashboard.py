#!/usr/bin/env python3
"""
Dashboard Update Script for Phase 5

Updates dashboard with task completion data, QA results, and progress metrics.
Integrates with completion metrics and real-time monitoring systems.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.completion_metrics import CompletionMetricsCalculator
from utils.execution_monitor import DashboardLogger


class DashboardUpdater:
    """Updates dashboard with latest completion data"""

    def __init__(self, dashboard_dir: str = "dashboard"):
        self.dashboard_dir = Path(dashboard_dir)
        self.dashboard_dir.mkdir(exist_ok=True)
        self.metrics_calculator = CompletionMetricsCalculator(dashboard_dir=str(self.dashboard_dir))
        self.dashboard_logger = DashboardLogger(str(self.dashboard_dir))

    def update_completion_dashboard(self, task_id: Optional[str] = None) -> bool:
        """Update dashboard with completion data"""
        try:
            print(f"🔄 Updating completion dashboard...")

            # Calculate latest metrics
            metrics = self.metrics_calculator.calculate_all_metrics()

            # Save metrics to dashboard
            self.metrics_calculator.save_metrics_to_dashboard(metrics)

            # Update completion status if specific task provided
            if task_id:
                self._update_task_completion_status(task_id, metrics)

            # Update dashboard summary
            self._update_dashboard_summary(metrics)

            # Generate completion charts data
            self._generate_charts_data(metrics)

            print(f"✅ Dashboard updated successfully")
            return True

        except Exception as e:
            print(f"❌ Dashboard update failed: {e}")
            return False

    def _update_task_completion_status(self, task_id: str, metrics: Dict[str, Any]) -> None:
        """Update specific task completion status"""
        task_metrics = metrics.get("task_metrics", [])
        task_data = next((t for t in task_metrics if t["task_id"] == task_id), None)

        if task_data:
            # Update live execution status
            self.dashboard_logger.update_live_dashboard(
                task_id=task_id,
                agent="completion",
                status=task_data["status"],
                duration=task_data.get("duration_minutes", 0) * 60
            )

            print(f"   📊 Updated status for {task_id}: {task_data['status']}")

    def _update_dashboard_summary(self, metrics: Dict[str, Any]) -> None:
        """Update dashboard summary file"""
        team_metrics = metrics.get("team_metrics", {})
        progress_metrics = metrics.get("progress_metrics", {})

        summary = {
            "last_updated": datetime.now().isoformat(),
            "overview": {
                "total_tasks": team_metrics.get("total_tasks", 0),
                "completed_tasks": team_metrics.get("completed_tasks", 0),
                "completion_rate": team_metrics.get("completion_rate", 0.0),
                "qa_pass_rate": team_metrics.get("qa_pass_rate", 0.0),
                "average_coverage": team_metrics.get("average_coverage", 0.0)
            },
            "recent_activity": {
                "daily_completions": progress_metrics.get("daily_completions", {}),
                "completion_trend": progress_metrics.get("completion_trend", [])[-7:],  # Last 7 days
                "coverage_trend": progress_metrics.get("coverage_trend", [])[-7:]
            },
            "status_breakdown": self._calculate_status_breakdown(metrics["task_metrics"])
        }

        summary_file = self.dashboard_dir / "dashboard_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"   📈 Dashboard summary updated")

    def _calculate_status_breakdown(self, task_metrics: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate task status breakdown"""
        breakdown = {}
        for task in task_metrics:
            status = task.get("status", "UNKNOWN")
            breakdown[status] = breakdown.get(status, 0) + 1
        return breakdown

    def _generate_charts_data(self, metrics: Dict[str, Any]) -> None:
        """Generate data for dashboard charts"""
        charts_data = {
            "completion_chart": self._create_completion_chart_data(metrics),
            "qa_chart": self._create_qa_chart_data(metrics),
            "coverage_chart": self._create_coverage_chart_data(metrics),
            "progress_chart": self._create_progress_chart_data(metrics),
            "generated_at": datetime.now().isoformat()
        }

        charts_file = self.dashboard_dir / "charts_data.json"
        with open(charts_file, 'w') as f:
            json.dump(charts_data, f, indent=2)

        print(f"   📊 Charts data generated")

    def _create_completion_chart_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create completion status chart data"""
        team_metrics = metrics.get("team_metrics", {})
        return {
            "type": "doughnut",
            "title": "Task Completion Status",
            "data": {
                "labels": ["Completed", "In Progress", "Failed", "Not Started"],
                "datasets": [{
                    "data": [
                        team_metrics.get("completed_tasks", 0),
                        team_metrics.get("in_progress_tasks", 0),
                        team_metrics.get("failed_tasks", 0),
                        max(0, team_metrics.get("total_tasks", 0) - 
                            team_metrics.get("completed_tasks", 0) - 
                            team_metrics.get("in_progress_tasks", 0) - 
                            team_metrics.get("failed_tasks", 0))
                    ],
                    "backgroundColor": ["#28a745", "#ffc107", "#dc3545", "#6c757d"],
                    "borderColor": ["#155724", "#856404", "#721c24", "#383d41"],
                    "borderWidth": 2
                }]
            }
        }

    def _create_qa_chart_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create QA results chart data"""
        task_metrics = metrics.get("task_metrics", [])
        qa_passed = len([t for t in task_metrics if t.get("qa_status") == "PASSED"])
        qa_failed = len([t for t in task_metrics if t.get("qa_status") == "FAILED"])
        qa_not_run = len([t for t in task_metrics if t.get("qa_status") in [None, "NOT_RUN"]])

        return {
            "type": "bar",
            "title": "QA Results Overview",
            "data": {
                "labels": ["Passed", "Failed", "Not Run"],
                "datasets": [{
                    "label": "QA Results",
                    "data": [qa_passed, qa_failed, qa_not_run],
                    "backgroundColor": ["#28a745", "#dc3545", "#6c757d"],
                    "borderColor": ["#155724", "#721c24", "#383d41"],
                    "borderWidth": 1
                }]
            }
        }

    def _create_coverage_chart_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create coverage trend chart data"""
        progress_metrics = metrics.get("progress_metrics", {})
        coverage_trend = progress_metrics.get("coverage_trend", [])

        return {
            "type": "line",
            "title": "Test Coverage Trend",
            "data": {
                "labels": [item[0] for item in coverage_trend[-30:]],  # Last 30 days
                "datasets": [{
                    "label": "Coverage %",
                    "data": [item[1] for item in coverage_trend[-30:]],
                    "borderColor": "#007bff",
                    "backgroundColor": "rgba(0, 123, 255, 0.1)",
                    "fill": True,
                    "tension": 0.3
                }]
            }
        }

    def _create_progress_chart_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create progress completion chart data"""
        progress_metrics = metrics.get("progress_metrics", {})
        completion_trend = progress_metrics.get("completion_trend", [])

        return {
            "type": "bar",
            "title": "Daily Completion Progress",
            "data": {
                "labels": [item[0] for item in completion_trend[-14:]],  # Last 14 days
                "datasets": [{
                    "label": "Tasks Completed",
                    "data": [item[1] for item in completion_trend[-14:]],
                    "backgroundColor": "#28a745",
                    "borderColor": "#155724",
                    "borderWidth": 1
                }]
            },
            "summary": {
                "completion_rate": metrics.get("team_metrics", {}).get("completion_rate", 0),
                "total_tasks": metrics.get("team_metrics", {}).get("total_tasks", 0),
                "qa_pass_rate": metrics.get("team_metrics", {}).get("qa_pass_rate", 0),
                "average_coverage": metrics.get("team_metrics", {}).get("average_coverage", 0)
            }
        }

    def update_real_time_status(self, task_id: str, status: str, agent: str = "system") -> None:
        """Update real-time task status in dashboard"""
        self.dashboard_logger.update_live_dashboard(task_id, agent, status)
        print(f"   🔄 Real-time status updated: {task_id} -> {status}")

    def generate_progress_summary(self) -> str:
        """Generate progress summary for display"""
        metrics = self.metrics_calculator.calculate_all_metrics()
        team_metrics = metrics.get("team_metrics", {})

        summary = f"""
# Dashboard Update Summary

**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current Status
- **Total Tasks:** {team_metrics.get('total_tasks', 0)}
- **Completed:** {team_metrics.get('completed_tasks', 0)} ({team_metrics.get('completion_rate', 0.0):.1f}%)
- **In Progress:** {team_metrics.get('in_progress_tasks', 0)}
- **Failed:** {team_metrics.get('failed_tasks', 0)}

## Quality Metrics
- **QA Pass Rate:** {team_metrics.get('qa_pass_rate', 0.0):.1f}%
- **Average Coverage:** {team_metrics.get('average_coverage', 0.0):.1f}%
- **Average Completion Time:** {team_metrics.get('average_completion_time', 0.0):.1f} minutes

## Files Updated
- dashboard/completion_metrics.json
- dashboard/dashboard_summary.json
- dashboard/charts_data.json
- dashboard/live_execution.json
- dashboard/agent_status.json
"""
        return summary


def main():
    """CLI interface for dashboard updates"""
    import argparse

    parser = argparse.ArgumentParser(description="Update dashboard with completion data")
    parser.add_argument("--task-id", help="Specific task ID to update")
    parser.add_argument("--dashboard-dir", default="dashboard", help="Dashboard directory")
    parser.add_argument("--completion", help="Mark task as completed (use with --task-id)")
    parser.add_argument("--status", help="Set task status (use with --task-id)")
    parser.add_argument("--summary", action="store_true", help="Show progress summary")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    updater = DashboardUpdater(args.dashboard_dir)

    try:
        if args.completion and args.task_id:
            # Handle task completion
            updater.update_real_time_status(args.task_id, "COMPLETED")
            success = updater.update_completion_dashboard(args.task_id)
            if success and args.verbose:
                print(f"\n✅ Task {args.task_id} marked as completed")
        
        elif args.status and args.task_id:
            # Handle status update
            updater.update_real_time_status(args.task_id, args.status)
            success = updater.update_completion_dashboard(args.task_id)
            if success and args.verbose:
                print(f"\n✅ Task {args.task_id} status updated to {args.status}")
        
        else:
            # General dashboard update
            success = updater.update_completion_dashboard()

        if args.summary:
            summary = updater.generate_progress_summary()
            print(summary)

        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"❌ Dashboard update failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
