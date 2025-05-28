#!/usr/bin/env python3
"""
Progress Report Generator for Phase 5

Generates daily, weekly, and task-specific progress reports for team visibility
and project tracking. Integrates with completion metrics and QA results.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.completion_metrics import CompletionMetricsCalculator


class ProgressReportGenerator:
    """Generates comprehensive progress reports"""

    def __init__(self, outputs_dir: str = "outputs", reports_dir: str = "progress_reports"):
        self.outputs_dir = Path(outputs_dir)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        self.metrics_calculator = CompletionMetricsCalculator(str(self.outputs_dir))

    def generate_daily_report(self, date: Optional[str] = None) -> str:
        """Generate daily progress report"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            report_date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid date format: {date}. Use YYYY-MM-DD")

        metrics = self.metrics_calculator.calculate_all_metrics()
        daily_tasks = self._get_tasks_for_date(metrics, date)
        
        report = self._create_daily_report(report_date, daily_tasks, metrics)
          # Save report
        filename = f"daily_report_{date}.md"
        report_path = self.reports_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Daily report saved to {report_path}")
        return report

    def generate_weekly_report(self, week_start: Optional[str] = None) -> str:
        """Generate weekly progress report"""
        if week_start is None:
            # Get Monday of current week
            today = datetime.now()
            monday = today - timedelta(days=today.weekday())
            week_start = monday.strftime('%Y-%m-%d')
        
        try:
            start_date = datetime.strptime(week_start, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid date format: {week_start}. Use YYYY-MM-DD")

        end_date = start_date + timedelta(days=6)
        
        metrics = self.metrics_calculator.calculate_all_metrics()
        weekly_tasks = self._get_tasks_for_week(metrics, start_date, end_date)
        report = self._create_weekly_report(start_date, end_date, weekly_tasks, metrics)
        
        # Save report
        filename = f"weekly_report_{week_start}.md"
        report_path = self.reports_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Weekly report saved to {report_path}")
        return report

    def generate_task_report(self, task_id: str) -> str:
        """Generate detailed report for specific task"""
        metrics = self.metrics_calculator.calculate_all_metrics()
        task_data = next((t for t in metrics["task_metrics"] if t["task_id"] == task_id), None)
        
        if not task_data:
            raise ValueError(f"Task {task_id} not found")
        
        report = self._create_task_report(task_id, task_data)
          # Save report
        filename = f"task_report_{task_id}.md"
        report_path = self.reports_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Task report saved to {report_path}")
        return report

    def generate_summary_report(self) -> str:
        """Generate overall project summary report"""
        metrics = self.metrics_calculator.calculate_all_metrics()
        report = self._create_summary_report(metrics)
          # Save report
        filename = f"summary_report_{datetime.now().strftime('%Y-%m-%d')}.md"
        report_path = self.reports_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ Summary report saved to {report_path}")
        return report

    def _get_tasks_for_date(self, metrics: Dict[str, Any], date: str) -> List[Dict[str, Any]]:
        """Get tasks completed on specific date"""
        tasks = []
        # Handle case where task_metrics might not be present (e.g., in tests)
        if "task_metrics" not in metrics:
            return tasks
            
        for task in metrics["task_metrics"]:
            if task.get("completion_time"):
                try:
                    completion_time = datetime.fromisoformat(task["completion_time"].replace('Z', '+00:00'))
                    completion_date = completion_time.strftime('%Y-%m-%d')
                    if completion_date == date:
                        tasks.append(task)
                except Exception:
                    continue
        return tasks    
    
    def _get_tasks_for_week(self, metrics: Dict[str, Any], start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get tasks completed during specific week"""
        tasks = []
        # Handle case where task_metrics might not be present (e.g., in tests)
        if "task_metrics" not in metrics:
            return tasks
            
        for task in metrics["task_metrics"]:
            if task.get("completion_time"):
                try:
                    completion_time = datetime.fromisoformat(task["completion_time"].replace('Z', '+00:00'))
                    if start_date <= completion_time <= end_date:
                        tasks.append(task)
                except Exception:
                    continue
        return tasks

    def _create_daily_report(self, report_date: datetime, daily_tasks: List[Dict[str, Any]], metrics: Dict[str, Any]) -> str:
        """Create daily progress report"""
        date_str = report_date.strftime('%Y-%m-%d')
        day_name = report_date.strftime('%A')
        
        report = f"""# Daily Progress Report - {day_name}, {date_str}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Tasks Completed Today:** {len(daily_tasks)}
- **Overall Progress:** {metrics['team_metrics']['completion_rate']:.1f}% ({metrics['team_metrics']['completed_tasks']}/{metrics['team_metrics']['total_tasks']} tasks)

## Tasks Completed Today
"""
        
        if daily_tasks:
            for task in daily_tasks:
                status_emoji = "✅" if task["status"] == "COMPLETED" else "⚠️"
                qa_status = task.get("qa_status", "NOT_RUN")
                qa_emoji = "✅" if qa_status == "PASSED" else "❌" if qa_status == "FAILED" else "⏳"
                
                report += f"""
### {status_emoji} {task['task_id']} ({task['agent_type']})
- **Status:** {task['status']}
- **QA Status:** {qa_emoji} {qa_status}
- **Coverage:** {task.get('coverage', 'N/A')}%
- **Tests:** {task.get('tests_passed', 0)} passed, {task.get('tests_failed', 0)} failed
- **Duration:** {task.get('duration_minutes', 'N/A')} minutes
"""
        else:
            report += "\nNo tasks completed today.\n"

        # Add QA insights
        report += self._add_qa_insights(daily_tasks)
        
        # Add next steps
        report += self._add_next_steps(metrics)
        
        return report

    def _create_weekly_report(self, start_date: datetime, end_date: datetime, weekly_tasks: List[Dict[str, Any]], metrics: Dict[str, Any]) -> str:
        """Create weekly progress report"""
        week_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        report = f"""# Weekly Progress Report - {week_str}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Weekly Summary
- **Tasks Completed This Week:** {len(weekly_tasks)}
- **Overall Project Progress:** {metrics['team_metrics']['completion_rate']:.1f}%
- **QA Pass Rate:** {metrics['team_metrics']['qa_pass_rate']:.1f}%
- **Average Coverage:** {metrics['team_metrics']['average_coverage']:.1f}%

## Daily Breakdown
"""
        
        # Group tasks by day
        daily_breakdown = {}
        for task in weekly_tasks:
            if task.get("completion_time"):
                try:
                    completion_time = datetime.fromisoformat(task["completion_time"].replace('Z', '+00:00'))
                    day = completion_time.strftime('%Y-%m-%d (%A)')
                    if day not in daily_breakdown:
                        daily_breakdown[day] = []
                    daily_breakdown[day].append(task)
                except Exception:
                    continue
        
        for day, tasks in sorted(daily_breakdown.items()):
            report += f"\n### {day} - {len(tasks)} tasks completed\n"
            for task in tasks:
                qa_status = task.get("qa_status", "NOT_RUN")
                qa_emoji = "✅" if qa_status == "PASSED" else "❌" if qa_status == "FAILED" else "⏳"
                report += f"- {qa_emoji} **{task['task_id']}** ({task['agent_type']}) - {qa_status}\n"

        # Add weekly insights
        report += self._add_weekly_insights(weekly_tasks, metrics)
        
        return report

    def _create_task_report(self, task_id: str, task_data: Dict[str, Any]) -> str:
        """Create detailed task report"""
        report = f"""# Task Report - {task_id}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Task Overview
- **Task ID:** {task_id}
- **Agent Type:** {task_data['agent_type']}
- **Status:** {task_data['status']}
- **Completion Time:** {task_data.get('completion_time', 'Not completed')}
- **Duration:** {task_data.get('duration_minutes', 'N/A')} minutes

## Quality Assurance
- **QA Status:** {task_data.get('qa_status', 'NOT_RUN')}
- **Test Coverage:** {task_data.get('coverage', 'N/A')}%
- **Tests Passed:** {task_data.get('tests_passed', 0)}
- **Tests Failed:** {task_data.get('tests_failed', 0)}

## Documentation & Archival
- **Documentation Generated:** {'✅' if task_data.get('documentation_generated') else '❌'}
- **Archived:** {'✅' if task_data.get('archived') else '❌'}

## Files & Artifacts
"""
        
        # Check for task files
        task_dir = self.outputs_dir / task_id
        if task_dir.exists():
            files = list(task_dir.rglob("*"))
            for file in sorted(files):
                if file.is_file():
                    rel_path = file.relative_to(task_dir)
                    file_size = file.stat().st_size
                    report += f"- `{rel_path}` ({file_size} bytes)\n"
        
        # Add recommendations
        report += self._add_task_recommendations(task_data)
        
        return report

    def _create_summary_report(self, metrics: Dict[str, Any]) -> str:
        """Create overall project summary report"""
        team_metrics = metrics["team_metrics"]
        progress_metrics = metrics["progress_metrics"]
        
        report = f"""# Project Summary Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Tasks Analyzed:** {metrics['total_tasks_analyzed']}

## Overall Progress
- **Completion Rate:** {team_metrics['completion_rate']:.1f}%
- **Tasks Completed:** {team_metrics['completed_tasks']}
- **Tasks In Progress:** {team_metrics['in_progress_tasks']}
- **Failed Tasks:** {team_metrics['failed_tasks']}

## Quality Metrics
- **QA Pass Rate:** {team_metrics['qa_pass_rate']:.1f}%
- **Average Test Coverage:** {team_metrics['average_coverage']:.1f}%
- **Average Completion Time:** {team_metrics['average_completion_time']:.1f} minutes

## Progress Trends
"""
        
        # Add completion trend
        completion_trend = progress_metrics.get("completion_trend", [])
        if completion_trend:
            report += "\n### Recent Completion Activity\n"
            for date, count in completion_trend[-10:]:
                report += f"- **{date}:** {count} tasks completed\n"
        
        # Add coverage trend
        coverage_trend = progress_metrics.get("coverage_trend", [])
        if coverage_trend:
            report += "\n### Coverage Trend\n"
            for date, coverage in coverage_trend[-5:]:
                report += f"- **{date}:** {coverage:.1f}% average coverage\n"

        # Add task breakdown by agent type
        report += self._add_agent_breakdown(metrics["task_metrics"])
        
        # Add recommendations
        report += self._add_project_recommendations(metrics)
        
        return report

    def _add_qa_insights(self, tasks: List[Dict[str, Any]]) -> str:
        """Add QA insights section"""
        if not tasks:
            return ""
        
        qa_passed = len([t for t in tasks if t.get("qa_status") == "PASSED"])
        qa_failed = len([t for t in tasks if t.get("qa_status") == "FAILED"])
        
        insights = f"""
## QA Insights
- **QA Pass Rate Today:** {(qa_passed / len(tasks) * 100) if tasks else 0:.1f}%
- **Tasks Needing Attention:** {qa_failed}
"""
        
        if qa_failed > 0:
            insights += "\n### Failed QA Tasks\n"
            for task in tasks:
                if task.get("qa_status") == "FAILED":
                    insights += f"- **{task['task_id']}** - Review required\n"
        
        return insights    
    
    def _add_next_steps(self, metrics: Dict[str, Any]) -> str:
        """Add next steps section"""
        team_metrics = metrics.get("team_metrics", {})
        next_steps = "\n## Next Steps\n"
        
        # Based on current progress
        completion_rate = team_metrics.get("completion_rate", 0)
        in_progress = team_metrics.get("in_progress_tasks", 0)
        failed_tasks = team_metrics.get("failed_tasks", 0)
        
        if completion_rate < 25:
            next_steps += "- 🚀 **Focus on task initiation** - Get more tasks into active development\n"
        elif completion_rate < 50:
            next_steps += "- 🎯 **Maintain momentum** - Continue current development pace\n"
        elif completion_rate < 75:
            next_steps += "- 🔍 **Quality focus** - Emphasize QA and testing as project nears completion\n"
        else:
            next_steps += "- 🏁 **Final push** - Complete remaining tasks and prepare for deployment\n"
        
        if failed_tasks > 0:
            next_steps += f"- ⚠️ **Address failures** - Review and resolve {failed_tasks} failed tasks\n"
        if in_progress > 0:
            next_steps += f"- 📋 **Monitor progress** - Track {in_progress} tasks currently in development\n"
        
        # QA-specific recommendations
        qa_pass_rate = team_metrics.get("qa_pass_rate", 0)
        if qa_pass_rate < 90:
            next_steps += "- 🔧 **Improve QA process** - Review testing standards and coverage requirements\n"
        
        # Coverage recommendations
        avg_coverage = team_metrics.get("average_coverage", 0)
        if avg_coverage < 85:
            next_steps += "- 📊 **Increase test coverage** - Focus on comprehensive testing\n"
        
        next_steps += "- 📈 **Continue monitoring** - Regular progress reviews and metric tracking\n"
        
        return next_steps

    def _add_weekly_insights(self, weekly_tasks: List[Dict[str, Any]], metrics: Dict[str, Any]) -> str:
        """Add weekly insights section"""
        insights = "\n## Weekly Insights\n"
        
        if weekly_tasks:
            # Calculate weekly statistics
            qa_passed = len([t for t in weekly_tasks if t.get("qa_status") == "PASSED"])
            avg_coverage = sum(t.get("coverage", 0) for t in weekly_tasks if t.get("coverage")) / len(weekly_tasks)
            
            insights += f"- **Weekly QA Pass Rate:** {(qa_passed / len(weekly_tasks) * 100):.1f}%\n"
            insights += f"- **Weekly Average Coverage:** {avg_coverage:.1f}%\n"
          # Add productivity metrics
        team_metrics = metrics.get("team_metrics", {})
        completion_rate = team_metrics.get("completion_rate", 0)
        insights += f"- **Project Velocity:** {completion_rate:.1f}% complete\n"
        
        return insights

    def _add_task_recommendations(self, task_data: Dict[str, Any]) -> str:
        """Add task-specific recommendations"""
        recommendations = "\n## Recommendations\n"
        
        qa_status = task_data.get("qa_status")
        coverage = task_data.get("coverage", 0)
        
        if qa_status == "FAILED":
            recommendations += "- ⚠️ Review and fix QA failures before proceeding\n"
        
        if coverage and coverage < 85:
            recommendations += f"- 📈 Improve test coverage from {coverage}% to at least 85%\n"
        
        if not task_data.get("documentation_generated"):
            recommendations += "- 📝 Generate task documentation\n"
        
        if not task_data.get("archived"):
            recommendations += "- 📦 Archive task artifacts for compliance\n"
        
        if task_data["status"] == "COMPLETED":
            recommendations += "- ✅ Task completed successfully - ready for next phase\n"
        
        return recommendations

    def _add_agent_breakdown(self, task_metrics: List[Dict[str, Any]]) -> str:
        """Add agent type breakdown"""
        breakdown = "\n## Task Breakdown by Agent Type\n"
        agent_counts = {}
        for task in task_metrics:
            agent_type = task.get("agent_type", "unknown")
            if agent_type not in agent_counts:
                agent_counts[agent_type] = {"total": 0, "completed": 0, "qa_passed": 0}
            agent_counts[agent_type]["total"] += 1
            if task.get("status") == "COMPLETED":
                agent_counts[agent_type]["completed"] += 1
            if task.get("qa_status") == "PASSED":
                agent_counts[agent_type]["qa_passed"] += 1
        
        for agent_type, counts in sorted(agent_counts.items()):
            completion_rate = (counts["completed"] / counts["total"] * 100) if counts["total"] > 0 else 0
            qa_rate = (counts["qa_passed"] / counts["total"] * 100) if counts["total"] > 0 else 0
            
            breakdown += f"""### {agent_type.title()} Agent ({agent_type})
- **Total Tasks:** {counts['total']}
- **Completed:** {counts['completed']} ({completion_rate:.1f}%)
- **QA Passed:** {counts['qa_passed']} ({qa_rate:.1f}%)

"""
        
        return breakdown    
    
    def _add_project_recommendations(self, metrics: Dict[str, Any]) -> str:
        """Add project-level recommendations"""
        team_metrics = metrics.get("team_metrics", {})
        recommendations = "\n## Project Recommendations\n"
        
        completion_rate = team_metrics.get("completion_rate", 0)
        qa_pass_rate = team_metrics.get("qa_pass_rate", 0)
        avg_coverage = team_metrics.get("average_coverage", 0)
        
        if completion_rate < 50:
            recommendations += "- 🚀 Focus on task completion velocity\n"
        elif completion_rate > 80:
            recommendations += "- 🎯 Project nearing completion - focus on quality and documentation\n"
        
        if qa_pass_rate < 90:
            recommendations += "- 🔍 Improve QA processes and testing standards\n"
        
        if avg_coverage < 85:
            recommendations += "- 📊 Implement stricter test coverage requirements\n"
        
        failed_tasks = team_metrics.get("failed_tasks", 0)
        if failed_tasks > 0:
            recommendations += "- ⚠️ Review and address failed tasks as priority\n"
        
        recommendations += "- 📈 Continue monitoring progress and quality metrics\n"
        
        return recommendations
        
        return recommendations


def main():
    """CLI interface for progress report generation"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate progress reports")
    parser.add_argument("--type", choices=["daily", "weekly", "task", "summary"], 
                        default="daily", help="Report type")
    parser.add_argument("--date", help="Date for daily report (YYYY-MM-DD)")
    parser.add_argument("--week-start", help="Week start date for weekly report (YYYY-MM-DD)")
    parser.add_argument("--task-id", help="Task ID for task-specific report")
    parser.add_argument("--outputs-dir", default="outputs", help="Outputs directory")
    parser.add_argument("--reports-dir", default="progress_reports", help="Reports directory")
    parser.add_argument("--print", action="store_true", help="Print report to console")

    args = parser.parse_args()

    generator = ProgressReportGenerator(args.outputs_dir, args.reports_dir)

    try:
        if args.type == "daily":
            report = generator.generate_daily_report(args.date)
        elif args.type == "weekly":
            report = generator.generate_weekly_report(args.week_start)
        elif args.type == "task":
            if not args.task_id:
                print("❌ --task-id required for task reports")
                sys.exit(1)
            report = generator.generate_task_report(args.task_id)
        elif args.type == "summary":
            report = generator.generate_summary_report()
        
        if args.print:
            print("\n" + "="*60)
            print(report)

    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
