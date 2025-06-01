#!/usr/bin/env python3
"""
Completion Metrics Calculator for Phase 5

Calculates task completion metrics, QA statistics, and progress tracking
for dashboard integration and reporting systems.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


@dataclass
class TaskMetrics:
    """Metrics for a single task"""
    task_id: str
    status: str
    completion_time: Optional[str]
    qa_status: Optional[str]
    coverage: Optional[float]
    tests_passed: Optional[int]
    tests_failed: Optional[int]
    agent_type: str
    duration_minutes: Optional[float] = None
    documentation_generated: bool = False
    archived: bool = False


@dataclass
class TeamMetrics:
    """Team-level completion metrics"""
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    failed_tasks: int
    completion_rate: float
    average_coverage: float
    average_completion_time: float
    qa_pass_rate: float


@dataclass
class ProgressMetrics:
    """Progress tracking metrics"""
    daily_completions: Dict[str, int]
    weekly_completions: Dict[str, int]
    completion_trend: List[Tuple[str, int]]
    coverage_trend: List[Tuple[str, float]]
    qa_trend: List[Tuple[str, float]]


class CompletionMetricsCalculator:
    """Calculates comprehensive completion metrics for reporting"""

    def __init__(self, outputs_dir: str = "outputs", dashboard_dir: str = "dashboard"):
        self.outputs_dir = Path(outputs_dir)
        self.dashboard_dir = Path(dashboard_dir)
        self.dashboard_dir.mkdir(exist_ok=True)

    def calculate_all_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive metrics for all tasks"""
        task_metrics = self._collect_task_metrics()
        team_metrics = self._calculate_team_metrics(task_metrics)
        progress_metrics = self._calculate_progress_metrics(task_metrics)

        return {
            "task_metrics": [metric.__dict__ for metric in task_metrics],
            "team_metrics": team_metrics.__dict__,
            "progress_metrics": {
                "daily_completions": progress_metrics.daily_completions,
                "weekly_completions": progress_metrics.weekly_completions,
                "completion_trend": progress_metrics.completion_trend,
                "coverage_trend": progress_metrics.coverage_trend,
                "qa_trend": progress_metrics.qa_trend
            },
            "last_updated": datetime.now().isoformat(),
            "total_tasks_analyzed": len(task_metrics)
        }

    def _collect_task_metrics(self) -> List[TaskMetrics]:
        """Collect metrics from all task directories"""
        task_metrics = []

        for task_dir in self.outputs_dir.iterdir():
            if not task_dir.is_dir():
                continue

            task_id = task_dir.name
            try:
                metrics = self._extract_task_metrics(task_dir, task_id)
                if metrics:
                    task_metrics.append(metrics)
            except Exception as e:
                print(f"Warning: Failed to extract metrics for {task_id}: {e}")
                continue

        return task_metrics

    def _extract_task_metrics(self, task_dir: Path, task_id: str) -> Optional[TaskMetrics]:
        """Extract metrics from a single task directory"""
        status_file = task_dir / "status.json"
        qa_report_file = task_dir / "qa_report.json"
        task_declaration_file = task_dir / "task_declaration.json"

        # Get basic task info
        status = "UNKNOWN"
        completion_time = None
        agent_type = "unknown"
        duration_minutes = None

        if status_file.exists():
            try:
                with open(status_file) as f:
                    status_data = json.load(f)                    
                    status = status_data.get("status", "UNKNOWN")
                    completion_time = status_data.get("completion_time")
                    duration_minutes = status_data.get("duration_minutes")
            except Exception:
                pass

        if task_declaration_file.exists():
            try:
                with open(task_declaration_file) as f:
                    task_data = json.load(f)
                    agent_type = task_data.get("owner", task_data.get("agent", "unknown"))
                    
                    # If no status.json, try to get status from task_declaration.json
                    if not status_file.exists():
                        state = task_data.get("state", "UNKNOWN")
                        # Map task_declaration states to standard status values
                        status_mapping = {
                            "DONE": "COMPLETED",
                            "IN_PROGRESS": "IN_PROGRESS", 
                            "TODO": "PENDING",
                            "BLOCKED": "FAILED",
                            "CANCELLED": "FAILED"
                        }
                        status = status_mapping.get(state, state)
                        
                        # Use current time as completion time for DONE tasks
                        if state == "DONE":
                            completion_time = datetime.now().isoformat()
            except Exception:
                pass

        # Get QA metrics
        qa_status = None
        coverage = None
        tests_passed = None
        tests_failed = None

        if qa_report_file.exists():
            try:
                with open(qa_report_file) as f:
                    qa_data = json.load(f)
                    qa_status = qa_data.get("status", "NOT_RUN")
                    coverage = qa_data.get("coverage")
                    tests_passed = qa_data.get("tests_passed")
                    tests_failed = qa_data.get("tests_failed")
            except Exception:
                pass

        # Check for documentation and archival
        documentation_generated = (task_dir / "completion_report.md").exists()
        archived = False  # Will be updated when archival system is implemented

        return TaskMetrics(
            task_id=task_id,
            status=status,
            completion_time=completion_time,
            qa_status=qa_status,
            coverage=coverage,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            agent_type=agent_type,
            duration_minutes=duration_minutes,
            documentation_generated=documentation_generated,
            archived=archived
        )

    def _calculate_team_metrics(self, task_metrics: List[TaskMetrics]) -> TeamMetrics:
        """Calculate team-level metrics"""
        if not task_metrics:
            return TeamMetrics(0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0)

        total_tasks = len(task_metrics)
        completed_tasks = len([t for t in task_metrics if t.status == "COMPLETED"])
        in_progress_tasks = len([t for t in task_metrics if t.status in ["IN_PROGRESS", "QA_PENDING"]])
        failed_tasks = len([t for t in task_metrics if t.status == "FAILED"])

        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

        # Calculate coverage metrics
        coverage_values = [t.coverage for t in task_metrics if t.coverage is not None]
        average_coverage = sum(coverage_values) / len(coverage_values) if coverage_values else 0.0

        # Calculate completion time metrics
        duration_values = [t.duration_minutes for t in task_metrics if t.duration_minutes is not None]
        average_completion_time = sum(duration_values) / len(duration_values) if duration_values else 0.0

        # Calculate QA pass rate
        qa_tasks = [t for t in task_metrics if t.qa_status is not None]
        qa_passed = len([t for t in qa_tasks if t.qa_status == "PASSED"])
        qa_pass_rate = (qa_passed / len(qa_tasks) * 100) if qa_tasks else 0.0

        return TeamMetrics(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            failed_tasks=failed_tasks,
            completion_rate=completion_rate,
            average_coverage=average_coverage,
            average_completion_time=average_completion_time,
            qa_pass_rate=qa_pass_rate
        )

    def _calculate_progress_metrics(self, task_metrics: List[TaskMetrics]) -> ProgressMetrics:
        """Calculate progress tracking metrics"""
        # Group by completion date
        daily_completions = {}
        coverage_by_date = {}
        qa_by_date = {}

        for task in task_metrics:
            if task.completion_time and task.status == "COMPLETED":
                try:
                    # Parse completion time
                    completion_date = datetime.fromisoformat(task.completion_time.replace('Z', '+00:00'))
                    date_str = completion_date.strftime('%Y-%m-%d')

                    # Count completions
                    daily_completions[date_str] = daily_completions.get(date_str, 0) + 1

                    # Track coverage
                    if task.coverage is not None:
                        if date_str not in coverage_by_date:
                            coverage_by_date[date_str] = []
                        coverage_by_date[date_str].append(task.coverage)

                    # Track QA status
                    if task.qa_status == "PASSED":
                        qa_by_date[date_str] = qa_by_date.get(date_str, 0) + 1

                except Exception:
                    continue

        # Calculate weekly completions
        weekly_completions = self._aggregate_weekly(daily_completions)

        # Calculate trends
        completion_trend = [(date, count) for date, count in sorted(daily_completions.items())]

        coverage_trend = []
        for date, coverages in sorted(coverage_by_date.items()):
            avg_coverage = sum(coverages) / len(coverages)
            coverage_trend.append((date, avg_coverage))

        qa_trend = []
        for date, qa_count in sorted(qa_by_date.items()):
            total_for_date = daily_completions.get(date, 1)
            qa_rate = (qa_count / total_for_date * 100)
            qa_trend.append((date, qa_rate))

        return ProgressMetrics(
            daily_completions=daily_completions,
            weekly_completions=weekly_completions,
            completion_trend=completion_trend,
            coverage_trend=coverage_trend,
            qa_trend=qa_trend
        )

    def _aggregate_weekly(self, daily_data: Dict[str, int]) -> Dict[str, int]:
        """Aggregate daily data into weekly totals"""
        weekly_data = {}

        for date_str, count in daily_data.items():
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                # Get Monday of the week
                monday = date - timedelta(days=date.weekday())
                week_str = monday.strftime('%Y-W%U')
                weekly_data[week_str] = weekly_data.get(week_str, 0) + count
            except Exception:
                continue

        return weekly_data

    def save_metrics_to_dashboard(self, metrics: Dict[str, Any]) -> None:
        """Save metrics to dashboard files"""
        # Save as JSON for API consumption
        metrics_file = self.dashboard_dir / "completion_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Save summary for quick access
        summary_file = self.dashboard_dir / "completion_summary.json"
        summary = {
            "last_updated": metrics.get("last_updated", datetime.now().isoformat()),
            "total_tasks": metrics.get("total_tasks_analyzed", 0),
            "completion_rate": metrics.get("team_metrics", {}).get("completion_rate", 0.0),
            "qa_pass_rate": metrics.get("team_metrics", {}).get("qa_pass_rate", 0.0),
            "average_coverage": metrics.get("team_metrics", {}).get("average_coverage", 0.0)
        }
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"✅ Metrics saved to {metrics_file}")
        print(f"✅ Summary saved to {summary_file}")

    def generate_metrics_report(self) -> str:
        """Generate human-readable metrics report"""
        metrics = self.calculate_all_metrics()
        team = metrics["team_metrics"]
        progress = metrics["progress_metrics"]

        report = f"""# Completion Metrics Report

**Generated:** {metrics.get("last_updated", "Unknown")}
**Total Tasks Analyzed:** {metrics.get("total_tasks_analyzed", 0)}

## Team Performance
- **Completion Rate:** {team["completion_rate"]:.1f}%
- **Tasks Completed:** {team["completed_tasks"]} / {team["total_tasks"]}
- **Tasks In Progress:** {team["in_progress_tasks"]}
- **Failed Tasks:** {team["failed_tasks"]}

## Quality Metrics
- **QA Pass Rate:** {team["qa_pass_rate"]:.1f}%
- **Average Coverage:** {team["average_coverage"]:.1f}%
- **Average Completion Time:** {team["average_completion_time"]:.1f} minutes

## Progress Trends
- **Daily Completions:** {len(progress["daily_completions"])} active days
- **Recent Activity:** {list(progress["daily_completions"].items())[-5:] if progress["daily_completions"] else "No recent activity"}

## Task Breakdown by Status
"""
        # Add task breakdown
        task_metrics = metrics["task_metrics"]
        status_counts = {}        
        for task in task_metrics:
            status = task["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        for status, count in sorted(status_counts.items()):
            report += f"- **{status}:** {count} tasks\n"

        return report

    # Public interface methods for daily cycle integration
    def calculate_team_metrics(self) -> Dict[str, Any]:
        """Public interface for team metrics calculation"""
        all_metrics = self.calculate_all_metrics()
        return all_metrics["team_metrics"]
    
    def calculate_sprint_metrics(self) -> Dict[str, Any]:
        """Public interface for sprint metrics calculation"""
        all_metrics = self.calculate_all_metrics()
        
        # Calculate sprint-specific metrics
        task_metrics = all_metrics["task_metrics"]
        team_metrics = all_metrics["team_metrics"]
        progress_metrics = all_metrics["progress_metrics"]
        
        # Sprint health assessment
        completion_rate = team_metrics["completion_rate"]
        qa_pass_rate = team_metrics["qa_pass_rate"]
        
        sprint_health = "excellent" if completion_rate >= 90 and qa_pass_rate >= 95 else \
                       "good" if completion_rate >= 75 and qa_pass_rate >= 85 else \
                       "needs_attention" if completion_rate >= 50 else "critical"
        
        # Identify blockers and priorities
        blockers = []
        high_priority_tasks = []
        
        for task in task_metrics:
            if task["status"] == "FAILED":
                blockers.append({
                    "task_id": task["task_id"],
                    "agent_type": task["agent_type"],
                    "reason": "Task failed"
                })
            elif task["status"] == "IN_PROGRESS" and task.get("duration_minutes", 0) > 480:  # > 8 hours
                blockers.append({
                    "task_id": task["task_id"],
                    "agent_type": task["agent_type"],
                    "reason": "Long-running task"
                })
            elif task["qa_status"] == "FAILED":
                high_priority_tasks.append({
                    "task_id": task["task_id"],
                    "agent_type": task["agent_type"],
                    "reason": "QA failed, needs rework"
                })
        
        return {
            "sprint_health": sprint_health,
            "completion_rate": completion_rate,
            "qa_pass_rate": qa_pass_rate,
            "total_tasks": team_metrics["total_tasks"],
            "completed_tasks": team_metrics["completed_tasks"],
            "in_progress_tasks": team_metrics["in_progress_tasks"],
            "failed_tasks": team_metrics["failed_tasks"],
            "blockers": blockers,
            "high_priority_tasks": high_priority_tasks,
            "daily_trend": progress_metrics["completion_trend"][-7:],  # Last 7 days
            "coverage_trend": progress_metrics["coverage_trend"][-7:],
            "average_coverage": team_metrics["average_coverage"],
            "average_completion_time": team_metrics["average_completion_time"]
        }


def main():
    """CLI interface for completion metrics calculation"""
    import argparse

    parser = argparse.ArgumentParser(description="Calculate completion metrics")
    parser.add_argument("--outputs-dir", default="outputs", help="Outputs directory")
    parser.add_argument("--dashboard-dir", default="dashboard", help="Dashboard directory")
    parser.add_argument("--format", choices=["json", "report", "both"], default="both",
                        help="Output format")
    parser.add_argument("--save", action="store_true", help="Save to dashboard files")

    args = parser.parse_args()

    calculator = CompletionMetricsCalculator(args.outputs_dir, args.dashboard_dir)

    if args.format in ["json", "both"]:
        metrics = calculator.calculate_all_metrics()
        print(json.dumps(metrics, indent=2))

        if args.save:
            calculator.save_metrics_to_dashboard(metrics)

    if args.format in ["report", "both"]:
        report = calculator.generate_metrics_report()
        print("\n" + "="*60)
        print(report)


if __name__ == "__main__":
    main()
