#!/usr/bin/env python3
"""
Tests for Dashboard Integration & Reporting Components

Tests for Step 5.5 implementation including:
- Dashboard updater functionality
- Progress report generation
- Chart data generation
- Integration with completion metrics
"""

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.update_dashboard import DashboardUpdater
from scripts.generate_progress_report import ProgressReportGenerator
from utils.completion_metrics import CompletionMetricsCalculator


class TestDashboardUpdater(unittest.TestCase):
    """Test cases for DashboardUpdater"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.dashboard_dir = Path(self.temp_dir) / "dashboard"
        self.dashboard_dir.mkdir(exist_ok=True)
        self.updater = DashboardUpdater(str(self.dashboard_dir))

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_dashboard_updater_initialization(self):
        """Test dashboard updater initialization"""
        self.assertTrue(self.dashboard_dir.exists())
        self.assertIsInstance(self.updater.metrics_calculator, CompletionMetricsCalculator)

    def test_status_breakdown_calculation(self):
        """Test task status breakdown calculation"""
        task_metrics = [
            {"task_id": "T1", "status": "COMPLETED"},
            {"task_id": "T2", "status": "COMPLETED"},
            {"task_id": "T3", "status": "IN_PROGRESS"},
            {"task_id": "T4", "status": "FAILED"},
            {"task_id": "T5", "status": "CREATED"}
        ]
        
        breakdown = self.updater._calculate_status_breakdown(task_metrics)
        
        self.assertEqual(breakdown["COMPLETED"], 2)
        self.assertEqual(breakdown["IN_PROGRESS"], 1)
        self.assertEqual(breakdown["FAILED"], 1)
        self.assertEqual(breakdown["CREATED"], 1)

    def test_completion_chart_data_generation(self):
        """Test completion chart data generation"""
        metrics = {
            "team_metrics": {
                "total_tasks": 10,
                "completed_tasks": 6,
                "in_progress_tasks": 2,
                "failed_tasks": 1
            }
        }
        
        chart_data = self.updater._create_completion_chart_data(metrics)
        
        self.assertEqual(chart_data["type"], "doughnut")
        self.assertEqual(chart_data["title"], "Task Completion Status")
        self.assertEqual(chart_data["data"]["datasets"][0]["data"], [6, 2, 1, 1])  # Not started = 1

    def test_qa_chart_data_generation(self):
        """Test QA chart data generation"""
        metrics = {
            "task_metrics": [
                {"task_id": "T1", "qa_status": "PASSED"},
                {"task_id": "T2", "qa_status": "PASSED"},
                {"task_id": "T3", "qa_status": "FAILED"},
                {"task_id": "T4", "qa_status": "NOT_RUN"},
                {"task_id": "T5", "qa_status": None}
            ]
        }
        
        chart_data = self.updater._create_qa_chart_data(metrics)
        
        self.assertEqual(chart_data["type"], "bar")
        self.assertEqual(chart_data["data"]["datasets"][0]["data"], [2, 1, 2])  # Passed, Failed, Not Run

    def test_coverage_chart_data_generation(self):
        """Test coverage chart data generation"""
        metrics = {
            "progress_metrics": {
                "coverage_trend": [
                    ["2025-05-25", 85.5],
                    ["2025-05-26", 87.2],
                    ["2025-05-27", 89.1]
                ]
            }
        }
        
        chart_data = self.updater._create_coverage_chart_data(metrics)
        
        self.assertEqual(chart_data["type"], "line")
        self.assertEqual(chart_data["data"]["labels"], ["2025-05-25", "2025-05-26", "2025-05-27"])
        self.assertEqual(chart_data["data"]["datasets"][0]["data"], [85.5, 87.2, 89.1])

    def test_progress_chart_data_generation(self):
        """Test progress chart data generation"""
        metrics = {
            "progress_metrics": {
                "completion_trend": [
                    ["2025-05-25", 3],
                    ["2025-05-26", 2],
                    ["2025-05-27", 4]
                ]
            },
            "team_metrics": {
                "completion_rate": 75.0,
                "total_tasks": 20,
                "qa_pass_rate": 90.0,
                "average_coverage": 85.5
            }
        }
        
        chart_data = self.updater._create_progress_chart_data(metrics)
        
        self.assertEqual(chart_data["type"], "bar")
        self.assertEqual(chart_data["data"]["labels"], ["2025-05-25", "2025-05-26", "2025-05-27"])
        self.assertEqual(chart_data["data"]["datasets"][0]["data"], [3, 2, 4])
        self.assertEqual(chart_data["summary"]["completion_rate"], 75.0)

    @patch('scripts.update_dashboard.DashboardLogger')
    @patch('scripts.update_dashboard.CompletionMetricsCalculator')
    def test_charts_data_generation(self, mock_calculator, mock_logger):
        """Test complete charts data generation"""
        # Mock metrics data
        mock_metrics = {
            "team_metrics": {
                "total_tasks": 15,
                "completed_tasks": 10,
                "in_progress_tasks": 3,
                "failed_tasks": 2,
                "completion_rate": 66.7,
                "qa_pass_rate": 85.0,
                "average_coverage": 78.5
            },
            "progress_metrics": {
                "completion_trend": [["2025-05-27", 5]],
                "coverage_trend": [["2025-05-27", 78.5]]
            },
            "task_metrics": [
                {"task_id": "T1", "qa_status": "PASSED"},
                {"task_id": "T2", "qa_status": "FAILED"}
            ]
        }
        
        mock_calculator.return_value.calculate_all_metrics.return_value = mock_metrics
        
        updater = DashboardUpdater(str(self.dashboard_dir))
        updater._generate_charts_data(mock_metrics)
        
        # Check that charts_data.json was created
        charts_file = self.dashboard_dir / "charts_data.json"
        self.assertTrue(charts_file.exists())
        
        with open(charts_file, 'r') as f:
            charts_data = json.load(f)
        
        self.assertIn("completion_chart", charts_data)
        self.assertIn("qa_chart", charts_data)
        self.assertIn("coverage_chart", charts_data)
        self.assertIn("progress_chart", charts_data)
        self.assertIn("generated_at", charts_data)

    @patch('scripts.update_dashboard.CompletionMetricsCalculator')
    def test_dashboard_summary_update(self, mock_calculator):
        """Test dashboard summary update functionality"""
        mock_metrics = {
            "team_metrics": {
                "total_tasks": 20,
                "completed_tasks": 15,
                "completion_rate": 75.0,
                "qa_pass_rate": 90.0,
                "average_coverage": 85.0
            },
            "progress_metrics": {
                "daily_completions": {"2025-05-27": 3},
                "completion_trend": [["2025-05-27", 3]],
                "coverage_trend": [["2025-05-27", 85.0]]
            },
            "task_metrics": [
                {"task_id": "T1", "status": "COMPLETED"},
                {"task_id": "T2", "status": "IN_PROGRESS"}
            ]
        }
        
        updater = DashboardUpdater(str(self.dashboard_dir))
        updater._update_dashboard_summary(mock_metrics)
        
        # Check that dashboard_summary.json was created
        summary_file = self.dashboard_dir / "dashboard_summary.json"
        self.assertTrue(summary_file.exists())
        
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        self.assertIn("last_updated", summary)
        self.assertIn("overview", summary)
        self.assertIn("recent_activity", summary)
        self.assertIn("status_breakdown", summary)
        
        self.assertEqual(summary["overview"]["total_tasks"], 20)
        self.assertEqual(summary["overview"]["completion_rate"], 75.0)


class TestProgressReportGenerator(unittest.TestCase):
    """Test cases for ProgressReportGenerator"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.outputs_dir = Path(self.temp_dir) / "outputs"
        self.reports_dir = Path(self.temp_dir) / "reports"
        self.outputs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Create sample task output
        task_dir = self.outputs_dir / "TEST-01"
        task_dir.mkdir(exist_ok=True)
        (task_dir / "status.json").write_text(json.dumps({
            "task_id": "TEST-01",
            "agent_type": "backend",
            "status": "COMPLETED",
            "completion_time": "2025-05-28T10:00:00Z",
            "qa_status": "PASSED",
            "coverage": 85,
            "tests_passed": 10,
            "tests_failed": 0,
            "duration_minutes": 45
        }))
        
        self.generator = ProgressReportGenerator(str(self.outputs_dir), str(self.reports_dir))

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_generator_initialization(self):
        """Test progress report generator initialization"""
        self.assertTrue(self.outputs_dir.exists())
        self.assertTrue(self.reports_dir.exists())

    def test_qa_insights_generation(self):
        """Test QA insights section generation"""
        tasks = [
            {"task_id": "T1", "qa_status": "PASSED"},
            {"task_id": "T2", "qa_status": "PASSED"},
            {"task_id": "T3", "qa_status": "FAILED"}
        ]
        
        insights = self.generator._add_qa_insights(tasks)
        
        self.assertIn("QA Insights", insights)
        self.assertIn("66.7%", insights)  # Pass rate
        self.assertIn("Failed QA Tasks", insights)
        self.assertIn("T3", insights)

    def test_next_steps_generation(self):
        """Test next steps generation"""
        metrics = {
            "team_metrics": {
                "completion_rate": 45.0,
                "in_progress_tasks": 3,
                "failed_tasks": 1,
                "qa_pass_rate": 85.0,
                "average_coverage": 75.0
            }
        }
        
        next_steps = self.generator._add_next_steps(metrics)
        
        self.assertIn("Next Steps", next_steps)
        self.assertIn("Maintain momentum", next_steps)  # < 50% completion
        self.assertIn("Address failures", next_steps)  # Has failed tasks
        self.assertIn("Monitor progress", next_steps)  # Has in progress
        self.assertIn("Increase test coverage", next_steps)  # < 85% coverage

    def test_task_recommendations_generation(self):
        """Test task recommendations generation"""
        task_data = {
            "qa_status": "FAILED",
            "coverage": 60,
            "documentation_generated": False,
            "archived": False,
            "status": "COMPLETED"
        }
        
        recommendations = self.generator._add_task_recommendations(task_data)
        
        self.assertIn("Recommendations", recommendations)
        self.assertIn("Review and fix QA failures", recommendations)
        self.assertIn("Improve test coverage from 60%", recommendations)
        self.assertIn("Generate task documentation", recommendations)
        self.assertIn("Archive task artifacts", recommendations)

    def test_agent_breakdown_generation(self):
        """Test agent breakdown generation"""
        task_metrics = [
            {"agent_type": "backend", "status": "COMPLETED", "qa_status": "PASSED"},
            {"agent_type": "backend", "status": "COMPLETED", "qa_status": "FAILED"},
            {"agent_type": "frontend", "status": "COMPLETED", "qa_status": "PASSED"},
            {"agent_type": "frontend", "status": "IN_PROGRESS", "qa_status": "NOT_RUN"}
        ]
        
        breakdown = self.generator._add_agent_breakdown(task_metrics)
        
        self.assertIn("Task Breakdown by Agent Type", breakdown)
        self.assertIn("backend", breakdown)
        self.assertIn("frontend", breakdown)
        self.assertIn("100.0%", breakdown)  # Backend completion rate
        self.assertIn("50.0%", breakdown)   # Frontend completion rate

    def test_project_recommendations_generation(self):
        """Test project recommendations generation"""
        metrics = {
            "team_metrics": {
                "completion_rate": 30.0,
                "qa_pass_rate": 85.0,
                "average_coverage": 70.0,
                "failed_tasks": 2
            }
        }
        
        recommendations = self.generator._add_project_recommendations(metrics)
        
        self.assertIn("Project Recommendations", recommendations)
        self.assertIn("Focus on task completion velocity", recommendations)  # < 50%
        self.assertIn("Implement stricter test coverage", recommendations)  # < 85%
        self.assertIn("Review and address failed tasks", recommendations)  # Has failures

    def test_weekly_insights_generation(self):
        """Test weekly insights generation"""
        weekly_tasks = [
            {"qa_status": "PASSED", "coverage": 80},
            {"qa_status": "PASSED", "coverage": 90},
            {"qa_status": "FAILED", "coverage": 60}
        ]
        
        metrics = {
            "team_metrics": {
                "completion_rate": 75.0
            }
        }
        
        insights = self.generator._add_weekly_insights(weekly_tasks, metrics)
        
        self.assertIn("Weekly Insights", insights)
        self.assertIn("66.7%", insights)  # Weekly QA pass rate
        self.assertIn("76.7%", insights)  # Weekly average coverage
        self.assertIn("75.0%", insights)  # Project velocity

    @patch('scripts.generate_progress_report.CompletionMetricsCalculator')
    def test_daily_report_generation(self, mock_calculator):
        """Test daily report generation"""
        mock_metrics = {
            "team_metrics": {
                "completion_rate": 75.0,
                "completed_tasks": 15,
                "total_tasks": 20,
                "qa_pass_rate": 90.0,
                "average_coverage": 85.0
            }
        }
        mock_calculator.return_value.calculate_all_metrics.return_value = mock_metrics
        
        # Create generator with mocked calculator
        generator = ProgressReportGenerator(str(self.outputs_dir), str(self.reports_dir))
        report = generator.generate_daily_report()
        
        self.assertIn("Daily Progress Report", report)
        self.assertIn("Generated:", report)
        self.assertIn("75.0%", report)
        self.assertIn("15/20 tasks", report)

    @patch('scripts.generate_progress_report.CompletionMetricsCalculator')
    def test_summary_report_generation(self, mock_calculator):
        """Test summary report generation"""
        mock_metrics = {
            "total_tasks_analyzed": 25,
            "team_metrics": {
                "completion_rate": 80.0,
                "completed_tasks": 20,
                "in_progress_tasks": 3,
                "failed_tasks": 2,
                "qa_pass_rate": 85.0,
                "average_coverage": 78.5,
                "average_completion_time": 65.0
            },
            "progress_metrics": {
                "completion_trend": [["2025-05-27", 5]],
                "coverage_trend": [["2025-05-27", 78.5]]
            },
            "task_metrics": []
        }
        mock_calculator.return_value.calculate_all_metrics.return_value = mock_metrics
        
        generator = ProgressReportGenerator(str(self.outputs_dir), str(self.reports_dir))
        report = generator.generate_summary_report()
        
        self.assertIn("Project Summary Report", report)
        self.assertIn("25", report)  # Total tasks analyzed
        self.assertIn("80.0%", report)  # Completion rate
        self.assertIn("85.0%", report)  # QA pass rate
        self.assertIn("Recent Completion Activity", report)
        self.assertIn("Project Recommendations", report)


class TestIntegration(unittest.TestCase):
    """Integration tests for dashboard components"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.dashboard_dir = Path(self.temp_dir) / "dashboard"
        self.outputs_dir = Path(self.temp_dir) / "outputs"
        self.dashboard_dir.mkdir(exist_ok=True)
        self.outputs_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('utils.completion_metrics.CompletionMetricsCalculator.calculate_all_metrics')
    def test_dashboard_update_integration(self, mock_calculate):
        """Test complete dashboard update workflow"""
        mock_calculate.return_value = {
            "team_metrics": {
                "total_tasks": 10,
                "completed_tasks": 7,
                "in_progress_tasks": 2,
                "failed_tasks": 1,
                "completion_rate": 70.0,
                "qa_pass_rate": 85.7,
                "average_coverage": 82.3
            },
            "progress_metrics": {
                "completion_trend": [["2025-05-27", 3]],
                "coverage_trend": [["2025-05-27", 82.3]]
            },
            "task_metrics": [
                {"task_id": "T1", "qa_status": "PASSED"},
                {"task_id": "T2", "qa_status": "FAILED"}
            ]
        }
        
        updater = DashboardUpdater(str(self.dashboard_dir))
        result = updater.update_completion_dashboard()
        
        self.assertTrue(result)
        
        # Verify files were created
        self.assertTrue((self.dashboard_dir / "dashboard_summary.json").exists())
        self.assertTrue((self.dashboard_dir / "charts_data.json").exists())
        
        # Verify content
        with open(self.dashboard_dir / "charts_data.json", 'r') as f:
            charts_data = json.load(f)
        
        self.assertIn("completion_chart", charts_data)
        self.assertIn("generated_at", charts_data)


if __name__ == '__main__':
    unittest.main()
