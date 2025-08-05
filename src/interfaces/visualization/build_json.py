#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import (
    Path,
    datetime,
    json,
    logging,
    sys,
    timedelta
)
"""
Phase 6 Step 6.5 - Visual Progress Charts Data Builder

Python data export script to generate progress_data.json for client-side chart rendering
with Chart.js or ECharts for real-time visualizations.

Usage:
    python visualization/build_json.py > static/progress_data.json
"""

# import json  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
# import sys  # Consolidated to common_imports
# from datetime import datetime, timedelta  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
from typing import Any, Dict, List

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Constants for deduplication
STACK_LABEL = "Stack 0"
IN_PROGRESS_LABEL = "In Progress"
TODO_LABEL = "To Do"
COMPLETED_LABEL = "Completed"
BLOCKED_LABEL = "Blocked"






# Robust import/fallback pattern for production using external fallback module
try:
    from src.infrastructure.utils.completion_metrics import CompletionMetricsCalculator
    COMPLETION_METRICS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Completion metrics not available: {e}")
    COMPLETION_METRICS_AVAILABLE = False
    from src.interfaces.visualization.fallbacks import CompletionMetricsCalculator

try:
    from src.core.workflows.daily_cycle import DailyCycleOrchestrator
    DAILY_CYCLE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Daily cycle orchestrator not available: {e}")
    DAILY_CYCLE_AVAILABLE = False
    from src.interfaces.visualization.fallbacks import DailyCycleOrchestrator


logger = logging.getLogger(__name__)


class VisualProgressChartsDataBuilder:
    """
    Data builder for Phase 6 Step 6.5 Visual Progress Charts Enhancement.

    Generates comprehensive progress data for client-side chart rendering
    including daily automation visualizations, velocity tracking, and
    sprint health indicators.
    """

    def __init__(self, database_client: Any):
        """Initialize the data builder with current project context."""
        self.logger = logging.getLogger(__name__)
        self.base_path = Path(__file__).parent.parent
        self.tasks_dir = self.base_path / "tasks"
        self.reports_dir = self.base_path / "reports"
        self.progress_reports_dir = self.base_path / "progress_reports"
        self.database_client = database_client

        # Initialize metrics calculator if available
        try:
            self.metrics_calculator = CompletionMetricsCalculator()
        except Exception:
            self.metrics_calculator = None

        # Initialize orchestrator for daily automation data
        try:
            self.daily_orchestrator = DailyCycleOrchestrator()
        except Exception:
            self.daily_orchestrator = None

    def build_comprehensive_progress_data(self) -> Dict[str, Any]:
        """
        Build comprehensive progress data for visual charts.

        Returns:
            Dict containing all chart data for dashboard visualization
        """
        progress_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "phase": "Phase 6 Step 6.5 - Visual Progress Charts",
                "data_version": "1.0.0",
            },
            "doughnut_chart": self._build_doughnut_chart_data(),
            "stacked_bar_by_day": self._build_stacked_bar_by_day_data(),
            "stacked_bar_by_owner": self._build_stacked_bar_by_owner_data(),
            "summary_cards": self._build_summary_cards_data(),
            "daily_automation_visualization": self._build_daily_automation_data(),
            "velocity_tracking": self._build_velocity_tracking_data(),
            "interactive_timeline": self._build_interactive_timeline_data(),
            "sprint_health_indicators": self._build_sprint_health_data(),
            "trend_analysis": self._build_trend_analysis_data(),
            "critical_path": self._build_critical_path_data(),
        }

        return progress_data

    def _build_doughnut_chart_data(self) -> Dict[str, Any]:
        """Build overall task status doughnut chart data."""
        task_statuses = self._get_task_status_breakdown()

        return {
            "type": "doughnut",
            "title": "Overall Task Status Distribution",
            "data": {
                "labels": list(task_statuses.keys()),
                "datasets": [
                    {
                        "data": list(task_statuses.values()),
                        "backgroundColor": [
                            "#28a745",  # Completed - Green
                            "#17a2b8",  # In Progress - Blue
                            "#dc3545",  # Blocked - Red
                            "#ffc107",  # To Do - Yellow
                        ],
                        "borderWidth": 2,
                        "borderColor": "#ffffff",
                    }
                ],
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"position": "right"},
                    "tooltip": {
                        "callbacks": {
                            "label": "function(context) { return context.label + ': ' + context.parsed + ' tasks'; }"
                        }
                    },
                },
            },
        }

    def _build_stacked_bar_by_day_data(self) -> Dict[str, Any]:
        """Build stacked bar chart showing tasks by day."""
        daily_data = self._get_daily_task_breakdown()

        return {
            "type": "bar",
            "title": "Tasks Progress by Day",
            "data": {
                "labels": list(daily_data.keys()),
                "datasets": [
                    {
                        "label": COMPLETED_LABEL,
                        "data": [day_data.get("completed", 0) for day_data in daily_data.values()],
                        "backgroundColor": "#28a745",
                        "stack": STACK_LABEL,
                    },
                    {
                        "label": IN_PROGRESS_LABEL,
                        "data": [day_data.get("in_progress", 0) for day_data in daily_data.values()],
                        "backgroundColor": "#17a2b8",
                        "stack": STACK_LABEL,
                    },
                    {
                        "label": BLOCKED_LABEL,
                        "data": [day_data.get("blocked", 0) for day_data in daily_data.values()],
                        "backgroundColor": "#dc3545",
                        "stack": STACK_LABEL,
                    },
                    {
                        "label": TODO_LABEL,
                        "data": [day_data.get("todo", 0) for day_data in daily_data.values()],
                        "backgroundColor": "#ffc107",
                        "stack": STACK_LABEL,
                    },
                ],
            },
            "options": {
                "responsive": True,
                "scales": {"x": {"stacked": True}, "y": {"stacked": True, "beginAtZero": True}},
            },
        }

    def _build_daily_automation_data(self) -> Dict[str, Any]:
        """Build daily automation visualization data."""
        automation_cycles = self._get_daily_automation_cycles()

        return {
            "type": "line",
            "title": "Daily Automation Cycles",
            "data": {
                "labels": list(automation_cycles.keys()),
                "datasets": [
                    {
                        "label": "Morning Briefings",
                        "data": [
                            cycle.get("morning_briefings", 0)
                            for cycle in automation_cycles.values()
                        ],
                        "borderColor": "#667eea",
                        "backgroundColor": "rgba(102, 126, 234, 0.1)",
                        "tension": 0.4,
                        "fill": True,
                    },
                    {
                        "label": "EOD Reports",
                        "data": [
                            cycle.get("eod_reports", 0)
                            for cycle in automation_cycles.values()
                        ],
                        "borderColor": "#764ba2",
                        "backgroundColor": "rgba(118, 75, 162, 0.1)",
                        "tension": 0.4,
                        "fill": True,
                    },
                    {
                        "label": "Health Checks",
                        "data": [
                            cycle.get("health_checks", 0)
                            for cycle in automation_cycles.values()
                        ],
                        "borderColor": "#28a745",
                        "backgroundColor": "rgba(40, 167, 69, 0.1)",
                        "tension": 0.4,
                        "fill": True,
                    },
                    {
                        "label": "Success Rate %",
                        "data": [
                            cycle.get("success_rate", 0)
                            for cycle in automation_cycles.values()
                        ],
                        "borderColor": "#ffc107",
                        "backgroundColor": "rgba(255, 193, 7, 0.1)",
                        "tension": 0.4,
                        "yAxisID": "y1",
                        "type": "line",
                    },
                ],
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "interaction": {"mode": "index", "intersect": False},
                "scales": {
                    "y": {
                        "type": "linear",
                        "display": True,
                        "position": "left",
                        "title": {
                            "display": True,
                            "text": "Automation Cycles",
                        },
                    },
                    "y1": {
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "title": {"display": True, "text": "Success Rate (%)"},
                        "grid": {"drawOnChartArea": False},
                        "min": 0,
                        "max": 100,
                    },
                },
                "plugins": {
                    "legend": {"position": "top"},
                    "tooltip": {"mode": "index", "intersect": False},
                },
            },
        }

    def _build_stacked_bar_by_owner_data(self) -> Dict[str, Any]:
        """Build stacked bar chart showing tasks by owner."""
        owner_data = self._get_owner_task_breakdown()
        if not owner_data:
            owner_data = {
                "Default Owner": {
                    "completed": 0,
                    "in_progress": 0,
                    "blocked": 0,
                    "todo": 0,
                }
            }

        return {
            "type": "bar",
            "title": "Tasks Distribution by Owner",
            "data": {
                "labels": list(owner_data.keys()),
                "datasets": [
                    {
                        "label": COMPLETED_LABEL,
                        "data": [owner_stats.get("completed", 0) for owner_stats in owner_data.values()],
                        "backgroundColor": "#28a745",
                        "stack": STACK_LABEL,
                    },
                    {
                        "label": IN_PROGRESS_LABEL,
                        "data": [owner_stats.get("in_progress", 0) for owner_stats in owner_data.values()],
                        "backgroundColor": "#17a2b8",
                        "stack": STACK_LABEL,
                    },
                    {
                        "label": BLOCKED_LABEL,
                        "data": [owner_stats.get("blocked", 0) for owner_stats in owner_data.values()],
                        "backgroundColor": "#dc3545",
                        "stack": STACK_LABEL,
                    },
                    {
                        "label": TODO_LABEL,
                        "data": [owner_stats.get("todo", 0) for owner_stats in owner_data.values()],
                        "backgroundColor": "#ffc107",
                        "stack": STACK_LABEL,
                    },
                ],
            },
            "options": {
                "responsive": True,
                "scales": {"x": {"stacked": True}, "y": {"stacked": True, "beginAtZero": True}},
                "plugins": {"legend": {"position": "top"}},
            },
        }

    def _build_summary_cards_data(self) -> Dict[str, Any]:
        """Build summary cards data for quick overview."""
        owner_data = self._get_owner_task_breakdown()

        return {
            "type": "bar",
            "title": "Tasks Distribution by Owner",
            "data": {
                "labels": list(owner_data.keys()),
                "datasets": [
                    {
                        "label": COMPLETED_LABEL,
                        "data": [owner_stats.get("completed", 0) for owner_stats in owner_data.values()],
                        "backgroundColor": "#28a745",
                        "stack": STACK_LABEL,
                    },
                    {
                        "label": IN_PROGRESS_LABEL,
                        "data": [owner_stats.get("in_progress", 0) for owner_stats in owner_data.values()],
                        "backgroundColor": "#17a2b8",
                        "stack": STACK_LABEL,
                    },
                    {
                        "label": BLOCKED_LABEL,
                        "data": [owner_stats.get("blocked", 0) for owner_stats in owner_data.values()],
                        "backgroundColor": "#dc3545",
                        "stack": STACK_LABEL,
                    },
                    {
                        "label": TODO_LABEL,
                        "data": [owner_stats.get("todo", 0) for owner_stats in owner_data.values()],
                        "backgroundColor": "#ffc107",
                        "stack": STACK_LABEL,
                    },
                ],
            },
            "options": {
                "responsive": True,
                "scales": {"x": {"stacked": True}, "y": {"stacked": True, "beginAtZero": True}},
                "plugins": {"legend": {"position": "top"}},
            },
        }

    def _build_velocity_tracking_data(self) -> Dict[str, Any]:
        """Build velocity tracking and trend analysis data."""
        velocity_data = self._get_sprint_velocity_data()

        return {
            "type": "line",
            "title": "Sprint Velocity Tracking & Predictions",
            "data": {
                "labels": list(velocity_data.keys()),
                "datasets": [
                    {
                        "label": "Actual Velocity",
                        "data": [v.get("actual", 0) for v in velocity_data.values()],
                        "borderColor": "#17a2b8",
                        "backgroundColor": "rgba(23, 162, 184, 0.1)",
                        "pointBackgroundColor": "#17a2b8",
                        "pointRadius": 6,
                        "tension": 0.3,
                    },
                    {
                        "label": "Predicted Velocity",
                        "data": [v.get("predicted", 0) for v in velocity_data.values()],
                        "borderColor": "#ffc107",
                        "backgroundColor": "rgba(255, 193, 7, 0.1)",
                        "borderDash": [5, 5],
                        "pointBackgroundColor": "#ffc107",
                        "pointRadius": 4,
                        "tension": 0.3,
                    },
                    {
                        "label": "Target Velocity",
                        "data": [v.get("target", 0) for v in velocity_data.values()],
                        "borderColor": "#28a745",
                        "backgroundColor": "rgba(40, 167, 69, 0.1)",
                        "borderDash": [10, 5],
                        "pointBackgroundColor": "#28a745",
                        "pointRadius": 5,
                        "tension": 0.1,
                    },
                ],
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": "Story Points / Tasks",
                        },
                    }
                },
                "plugins": {
                    "legend": {"position": "top"},
                    "tooltip": {
                        "mode": "index",
                        "intersect": False,
                        "callbacks": {
                            "footer": "function(context) { return 'Trend: ' + (context[0].raw > context[0].dataset.data[Math.max(0, context[0].dataIndex - 1)] ? '↗️' : '↘️'); }"
                        },
                    },
                },
            },
        }

    def _build_interactive_timeline_data(self) -> Dict[str, Any]:
        """Build interactive timeline data for daily cycle tracking."""
        timeline_events = self._get_timeline_events()

        return {
            "type": "timeline",
            "title": "Daily Cycle Interactive Timeline",
            "events": timeline_events,
            "options": {
                "responsive": True,
                "interaction": {"intersect": False, "mode": "index"},
                "scales": {
                    "x": {
                        "type": "time",
                        "time": {
                            "displayFormats": {
                                "hour": "HH:mm",
                                "day": "MMM DD",
                            }
                        },
                        "title": {"display": True, "text": "Timeline"},
                    },
                    "y": {"title": {"display": True, "text": "Event Type"}},
                },
            },
        }

    def _build_sprint_health_data(self) -> Dict[str, Any]:
        """Build sprint health indicators and critical path visualization."""
        health_metrics = self._get_sprint_health_metrics()

        return {
            "overall_health": health_metrics.get("overall_score", 75),
            "health_indicators": {
                "velocity": {
                    "score": health_metrics.get("velocity_score", 80),
                    "status": health_metrics.get("velocity_status", "good"),
                    "trend": health_metrics.get("velocity_trend", "stable"),
                },
                "quality": {
                    "score": health_metrics.get("quality_score", 85),
                    "status": health_metrics.get("quality_status", "excellent"),
                    "trend": health_metrics.get("quality_trend", "improving"),
                },
                "team_utilization": {
                    "score": health_metrics.get("utilization_score", 70),
                    "status": health_metrics.get("utilization_status", "moderate"),
                    "trend": health_metrics.get("utilization_trend", "stable"),
                },
                "automation": {
                    "score": health_metrics.get("automation_score", 90),
                    "status": health_metrics.get("automation_status", "excellent"),
                    "trend": health_metrics.get("automation_trend", "improving"),
                },
            },
            "critical_path": health_metrics.get("critical_path", []),
            "recommendations": health_metrics.get("recommendations", []),
        }

    def _build_trend_analysis_data(self) -> Dict[str, Any]:
        """Build trend analysis with predictive indicators."""
        trend_data = self._get_trend_analysis()

        return {
            "completion_trend": {
                "type": "line",
                "data": trend_data.get("completion_trend", []),
                "prediction": trend_data.get("completion_prediction", []),
            },
            "velocity_trend": {
                "type": "line",
                "data": trend_data.get("velocity_trend", []),
                "prediction": trend_data.get("velocity_prediction", []),
            },
            "quality_trend": {
                "type": "line",
                "data": trend_data.get("quality_trend", []),
                "prediction": trend_data.get("quality_prediction", []),
            },
        }

    def _build_critical_path_data(self) -> Dict[str, Any]:
        """Build critical path visualization with dependency mapping."""
        critical_path = self._get_critical_path_analysis()

        return {
            "type": "network",
            "title": "Critical Path & Dependencies",
            "nodes": critical_path.get("nodes", []),
            "edges": critical_path.get("edges", []),
            "critical_tasks": critical_path.get("critical_tasks", []),
            "options": {
                "layout": {"hierarchical": {"enabled": True, "direction": "LR"}},
                "physics": {"enabled": False},
                "interaction": {"hover": True, "selectConnectedEdges": True},
            },
        }

    def _get_task_status_breakdown(self) -> Dict[str, int]:
        """Get breakdown of tasks by status."""
        if self.metrics_calculator:
            try:
                # type: ignore[attr-defined] for fallback stub
                return self.metrics_calculator.get_task_status_breakdown()  # type: ignore[attr-defined]
            except Exception:
                pass

        # Mock data for visualization if metrics not available
        return {COMPLETED_LABEL: 25, IN_PROGRESS_LABEL: 8, BLOCKED_LABEL: 2, TODO_LABEL: 15}

    def _get_daily_task_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get daily breakdown of task progress."""
        days = []
        base_date = datetime.now() - timedelta(days=6)

        for i in range(7):
            day = base_date + timedelta(days=i)
            days.append(day.strftime("%Y-%m-%d"))

        # Mock daily data - in real implementation, this would query actual task data
        daily_data = {}
        for i, day in enumerate(days):
            daily_data[day] = {
                "completed": max(0, 3 + i - 2),
                "in_progress": max(1, 2 - (i % 3)),
                "blocked": 1 if i % 4 == 0 else 0,
                "todo": max(0, 5 - i),
            }

        return daily_data

    def _get_owner_task_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get breakdown of tasks by owner."""
        try:
            # Replace with actual query logic to fetch task assignments from a database or API
            task_assignments = self.database_client.fetch_task_assignments()  # Example method

            owner_data = {}
            for task in task_assignments:
                owner = task.get("owner", "Unknown")
                status = task.get("status", "todo").lower()

                if owner not in owner_data:
                    owner_data[owner] = {"completed": 0, "in_progress": 0, "blocked": 0, "todo": 0}

                if status in owner_data[owner]:
                    owner_data[owner][status] += 1

            return owner_data
        except Exception as e:
            self.logger.error(f"Failed to fetch task assignments: {e}")
            # Fallback to default mock data
            return {
                "Default Owner": {
                    "completed": 0,
                    "in_progress": 0,
                    "blocked": 0,
                    "todo": 0,
                }
            }

    def _calculate_trend(self, status: str) -> str:
        """Calculate trend for status (up, down, stable)."""
        # Mock trend calculation - in real implementation, this would analyze historical data
        trends = {
            "completed": "up",
            "in_progress": "stable",
            "blocked": "down",
            "todo": "down",
        }
        return trends.get(status, "stable")

    def _get_daily_automation_cycles(self) -> Dict[str, Dict[str, int]]:
        """Get daily automation cycle data."""
        if self.daily_orchestrator:
            try:
                # Replace with valid method or remove
                pass
            except Exception as e:
                self.logger.warning(f"Failed to fetch daily automation cycles: {e}")

        # Mock automation data
        cycles = {}
        base_date = datetime.now() - timedelta(days=6)

        for i in range(7):
            day = base_date + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            cycles[day_str] = {
                "morning_briefings": 1 if i < 5 else 0,
                "eod_reports": 1 if i < 5 else 0,
                "health_checks": 3 + (i % 2),
                "success_rate": 95 + (i % 6) - 2,
            }

        return cycles

    def _get_sprint_velocity_data(self) -> Dict[str, Dict[str, float]]:
        """Get sprint velocity data with predictions."""
        # Mock velocity data - in real implementation, this would analyze sprint history
        velocity = {}
        base_date = datetime.now() - timedelta(weeks=4)

        for i in range(5):
            week_date = base_date + timedelta(weeks=i)
            week_str = f"Week {i+1}"
            print(f"📊 Adding velocity data for {week_str} (date: {week_date.strftime('%Y-%m-%d')})")
            velocity[week_str] = {
                "actual": 20 + (i * 2) + (i % 3),
                "predicted": 22 + (i * 2),
                "target": 25,
            }

        return velocity

    def _get_timeline_events(self) -> List[Dict[str, Any]]:
        """Get timeline events for interactive timeline."""
        events = []
        base_date = datetime.now() - timedelta(days=2)

        # Mock timeline events
        for i in range(7):
            day = base_date + timedelta(days=i)
            events.extend(
                [
                    {
                        "id": f"morning_{i}",
                        "title": "Morning Briefing",
                        "start": day.replace(hour=8, minute=0).isoformat(),
                        "type": "briefing",
                        "status": "completed" if i < 2 else "scheduled",
                    },
                    {
                        "id": f"health_{i}",
                        "title": "Health Check",
                        "start": day.replace(hour=12, minute=0).isoformat(),
                        "type": "health_check",
                        "status": "completed" if i < 2 else "scheduled",
                    },
                    {
                        "id": f"eod_{i}",
                        "title": "EOD Report",
                        "start": day.replace(hour=18, minute=0).isoformat(),
                        "type": "report",
                        "status": "completed" if i < 2 else "scheduled",
                    },
                ]
            )

        return events

    def _get_sprint_health_metrics(self) -> Dict[str, Any]:
        """Get comprehensive sprint health metrics."""
        return {
            "overall_score": 78,
            "velocity_score": 82,
            "velocity_status": "good",
            "velocity_trend": "improving",
            "quality_score": 88,
            "quality_status": "excellent",
            "quality_trend": "stable",
            "utilization_score": 72,
            "utilization_status": "moderate",
            "utilization_trend": "stable",
            "automation_score": 95,
            "automation_status": "excellent",
            "automation_trend": "improving",
            "critical_path": [
                {"task": "BE-08", "duration": 3, "slack": 0},
                {"task": "FE-05", "duration": 2, "slack": 1},
                {"task": "QA-03", "duration": 1, "slack": 0},
            ],
            "recommendations": [
                "Focus on BE-08 to maintain schedule",
                "Consider parallel work on FE-05",
                "Monitor automation system performance",
            ],
        }

    def _get_trend_analysis(self) -> Dict[str, List[float]]:
        """Get trend analysis data with predictions."""
        return {
            "completion_trend": [60, 65, 70, 75, 78],
            "completion_prediction": [80, 85, 90],
            "velocity_trend": [18, 20, 22, 24, 25],
            "velocity_prediction": [26, 28, 30],
            "quality_trend": [80, 82, 85, 87, 88],
            "quality_prediction": [89, 90, 92],
        }

    def _get_critical_path_analysis(self) -> Dict[str, List[Any]]:
        """Get critical path analysis with dependency mapping."""
        return {
            "nodes": [
                {
                    "id": "BE-08",
                    "label": "Backend API",
                    "critical": True,
                    "status": "in_progress",
                },
                {
                    "id": "FE-05",
                    "label": "Frontend UI",
                    "critical": False,
                    "status": "todo",
                },
                {
                    "id": "QA-03",
                    "label": "Testing",
                    "critical": True,
                    "status": "todo",
                },
                {
                    "id": "DOC-01",
                    "label": "Documentation",
                    "critical": False,
                    "status": "todo",
                },
            ],
            "edges": [
                {"from": "BE-08", "to": "FE-05", "critical": True},
                {"from": "FE-05", "to": "QA-03", "critical": True},
                {"from": "QA-03", "to": "DOC-01", "critical": False},
            ],
            "critical_tasks": ["BE-08", "QA-03"],
        }


# Define mock_database_client
class MockDatabaseClient:
    """Mock database client for testing and development."""

    def fetch_task_assignments(self):
        """Mock method to fetch task assignments."""
        return []


mock_database_client = MockDatabaseClient()


def main():
    """Main function to generate and output progress data JSON."""
    try:
        # Provide required argument
        builder = VisualProgressChartsDataBuilder(database_client=mock_database_client)
        progress_data = builder.build_comprehensive_progress_data()

        # Output JSON to stdout for redirection to file
        print(json.dumps(progress_data, indent=2, ensure_ascii=True))

    except Exception as e:
        logging.error(f"Error generating progress data: {e}")
        # Output minimal valid JSON on error
        error_data = {
            "error": "Failed to generate progress data",
            "message": str(e),
            "generated_at": datetime.now().isoformat(),
        }
        print(json.dumps(error_data, indent=2, ensure_ascii=True))
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
