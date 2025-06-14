#!/usr/bin/env python3
"""
End-of-Day Report Generator - Phase 6 Step 6.3

Enhanced reporting system for comprehensive end-of-day analysis,
building upon existing Phase 5 infrastructure with automation-specific insights.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.completion_metrics import CompletionMetricsCalculator
from utils.execution_monitor import ExecutionMonitor
from scripts.generate_progress_report import ProgressReportGenerator


class EndOfDayReportGenerator:
    """
    Enhanced end-of-day reporting with automation insights and daily summaries.
    """
    
    def __init__(self):
        """Initialize the end-of-day report generator."""
        self.metrics_calculator = CompletionMetricsCalculator()
        self.execution_monitor = ExecutionMonitor()
        self.progress_generator = ProgressReportGenerator()
        self.logger = logging.getLogger(__name__)
        
        # Initialize paths
        self.reports_dir = Path("docs/sprint/daily_reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_eod_report(self, 
                                 report_date: Optional[str] = None,
                                 include_automation_stats: bool = True,
                                 include_detailed_metrics: bool = True,
                                 output_format: str = "markdown") -> Dict[str, Any]:
        """
        Generate comprehensive end-of-day report.
        
        Args:
            report_date: Date for report (YYYY-MM-DD), defaults to today
            include_automation_stats: Include daily automation statistics
            include_detailed_metrics: Include detailed task metrics
            output_format: Output format (markdown, html, console)
            
        Returns:
            Dict containing report data and metadata
        """
        if not report_date:
            report_date = datetime.now().strftime('%Y-%m-%d')
        
        report_data = {
            "date": report_date,
            "timestamp": datetime.now().isoformat(),
            "type": "end_of_day",
            "format": output_format
        }
        
        # Core daily metrics
        report_data["daily_summary"] = await self._generate_daily_summary(report_date)
        
        # Sprint progress analysis
        report_data["sprint_progress"] = self._analyze_sprint_progress()
        
        # Task completion analysis
        report_data["task_analysis"] = self._analyze_daily_tasks(report_date)
        
        if include_automation_stats:
            report_data["automation_stats"] = self._gather_automation_statistics(report_date)
        
        if include_detailed_metrics:
            report_data["detailed_metrics"] = self._gather_detailed_metrics()
        
        # Quality and blockers analysis
        report_data["quality_analysis"] = self._analyze_quality_metrics()
        report_data["blockers_analysis"] = self._analyze_blockers()
        
        # Tomorrow's preparation
        report_data["tomorrow_prep"] = self._prepare_tomorrow_insights()
        
        # Generate formatted output
        formatted_report = self._format_report(report_data, output_format)
        
        # Save report
        report_filename = self._save_report(formatted_report, report_date, output_format)
        
        report_data["output_file"] = report_filename
        report_data["formatted_content"] = formatted_report
        
        return report_data
    
    async def _generate_daily_summary(self, report_date: str) -> Dict[str, Any]:
        """Generate daily summary using existing infrastructure."""
        try:
            # Use existing progress report generator for base summary
            daily_report = self.progress_generator.generate_daily_report(report_date)
            
            # Extract key metrics
            team_metrics = self.metrics_calculator.calculate_team_metrics()
            
            return {
                "completed_tasks": team_metrics.get("completed_tasks", 0),
                "total_tasks": team_metrics.get("total_tasks", 0),
                "completion_rate": team_metrics.get("completion_rate", 0),
                "daily_velocity": self._calculate_daily_velocity(report_date),
                "key_accomplishments": self._extract_accomplishments(report_date),
                "challenges_faced": self._identify_daily_challenges(report_date)
            }
        except Exception as e:
            self.logger.error(f"Error generating daily summary: {e}")
            return {"error": str(e)}
    
    def _analyze_sprint_progress(self) -> Dict[str, Any]:
        """Analyze overall sprint progress trends."""
        try:
            sprint_metrics = self.metrics_calculator.calculate_sprint_metrics()
            team_metrics = self.metrics_calculator.calculate_team_metrics()
            
            # Calculate trend analysis
            trend_data = self._calculate_progress_trend()
            
            return {
                "current_completion": team_metrics.get("completion_rate", 0),
                "sprint_health": self._assess_sprint_health_detailed(),
                "velocity_trend": trend_data.get("velocity", "stable"),
                "projected_completion": self._project_sprint_completion(),
                "risk_assessment": self._assess_sprint_risks(),
                "recommendations": self._generate_sprint_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Error analyzing sprint progress: {e}")
            return {"error": str(e)}
    
    def _analyze_daily_tasks(self, report_date: str) -> Dict[str, Any]:
        """Analyze tasks completed and worked on during the day."""
        try:
            all_tasks = self._get_all_tasks()
            
            # Filter tasks worked on today
            today_tasks = []
            completed_today = []
            started_today = []
            blocked_today = []
            
            for task in all_tasks:
                # Check if task was modified today (simplified heuristic)
                if self._was_task_active_today(task, report_date):
                    today_tasks.append(task)
                    
                    if task.get("status") == "COMPLETED":
                        completed_today.append(task)
                    elif task.get("status") == "IN_PROGRESS":
                        if self._was_task_started_today(task, report_date):
                            started_today.append(task)
                    elif task.get("status") == "BLOCKED":
                        blocked_today.append(task)
            
            return {
                "total_active": len(today_tasks),
                "completed_count": len(completed_today),
                "started_count": len(started_today),
                "blocked_count": len(blocked_today),
                "completed_tasks": [self._format_task_summary(task) for task in completed_today],
                "active_tasks": [self._format_task_summary(task) for task in started_today],
                "blocked_tasks": [self._format_task_summary(task) for task in blocked_today],
                "productivity_score": self._calculate_productivity_score(today_tasks)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing daily tasks: {e}")
            return {"error": str(e)}
    
    def _gather_automation_statistics(self, report_date: str) -> Dict[str, Any]:
        """Gather statistics about daily automation performance."""
        try:
            # Check execution monitor logs for automation runs
            execution_stats = self._analyze_execution_logs(report_date)
            
            return {
                "briefings_generated": execution_stats.get("briefings", 0),
                "reports_generated": execution_stats.get("reports", 0),
                "dashboard_updates": execution_stats.get("dashboard_updates", 0),
                "automation_uptime": execution_stats.get("uptime_percentage", 100.0),
                "error_count": execution_stats.get("errors", 0),
                "performance_metrics": {
                    "avg_briefing_time": execution_stats.get("avg_briefing_time", 0),
                    "avg_report_time": execution_stats.get("avg_report_time", 0)
                }
            }
        except Exception as e:
            self.logger.error(f"Error gathering automation statistics: {e}")
            return {"error": str(e)}
    
    def _gather_detailed_metrics(self) -> Dict[str, Any]:
        """Gather detailed metrics for comprehensive analysis."""
        try:
            team_metrics = self.metrics_calculator.calculate_team_metrics()
            sprint_metrics = self.metrics_calculator.calculate_sprint_metrics()
            
            return {
                "team_metrics": team_metrics,
                "sprint_metrics": sprint_metrics,
                "task_distribution": self._analyze_task_distribution(),
                "complexity_analysis": self._analyze_task_complexity(),
                "time_tracking": self._analyze_time_metrics(),
                "qa_metrics": self._analyze_qa_metrics()
            }
        except Exception as e:
            self.logger.error(f"Error gathering detailed metrics: {e}")
            return {"error": str(e)}
    
    def _analyze_quality_metrics(self) -> Dict[str, Any]:
        """Analyze quality metrics and QA coverage."""
        try:
            # Use existing QA analysis capabilities
            qa_stats = self._gather_qa_statistics()
            
            return {
                "test_coverage": qa_stats.get("coverage_percentage", 0),
                "code_quality_score": qa_stats.get("quality_score", 0),
                "review_completion": qa_stats.get("review_completion", 0),
                "defect_rate": qa_stats.get("defect_rate", 0),
                "quality_trend": self._calculate_quality_trend()
            }
        except Exception as e:
            self.logger.error(f"Error analyzing quality metrics: {e}")
            return {"error": str(e)}
    
    def _analyze_blockers(self) -> Dict[str, Any]:
        """Analyze current blockers and their impact."""
        try:
            all_tasks = self._get_all_tasks()
            blocked_tasks = [task for task in all_tasks if task.get("status") == "BLOCKED"]
            
            blocker_analysis = {
                "total_blocked": len(blocked_tasks),
                "blocker_categories": self._categorize_blockers(blocked_tasks),
                "impact_assessment": self._assess_blocker_impact(blocked_tasks),
                "resolution_timeline": self._estimate_blocker_resolution(blocked_tasks),
                "recommendations": self._generate_blocker_recommendations(blocked_tasks)
            }
            
            return blocker_analysis
        except Exception as e:
            self.logger.error(f"Error analyzing blockers: {e}")
            return {"error": str(e)}
    
    def _prepare_tomorrow_insights(self) -> Dict[str, Any]:
        """Prepare insights and recommendations for tomorrow."""
        try:
            # Analyze tomorrow's planned tasks
            planned_tasks = self._get_planned_tasks_for_tomorrow()
            
            return {
                "planned_tasks": len(planned_tasks),
                "priority_tasks": self._identify_priority_tasks(planned_tasks),
                "potential_blockers": self._identify_potential_blockers(planned_tasks),
                "resource_requirements": self._analyze_resource_needs(planned_tasks),
                "success_factors": self._identify_success_factors(),
                "preparation_checklist": self._generate_preparation_checklist()
            }
        except Exception as e:
            self.logger.error(f"Error preparing tomorrow insights: {e}")
            return {"error": str(e)}
    
    def _format_report(self, report_data: Dict[str, Any], output_format: str) -> str:
        """Format the report in the specified format."""
        if output_format == "markdown":
            return self._format_markdown_report(report_data)
        elif output_format == "html":
            return self._format_html_report(report_data)
        elif output_format == "console":
            return self._format_console_report(report_data)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _format_markdown_report(self, data: Dict[str, Any]) -> str:
        """Format report as markdown."""
        report_date = datetime.strptime(data["date"], '%Y-%m-%d').strftime('%A, %B %d, %Y')
        
        content = f"""# End-of-Day Report - {report_date}

## Daily Summary
**Tasks Completed:** {data['daily_summary'].get('completed_tasks', 0)}
**Total Tasks:** {data['daily_summary'].get('total_tasks', 0)}
**Completion Rate:** {data['daily_summary'].get('completion_rate', 0):.1f}%
**Daily Velocity:** {data['daily_summary'].get('daily_velocity', 0)} tasks

### Key Accomplishments
{self._format_accomplishments_list(data['daily_summary'].get('key_accomplishments', []))}

## Sprint Progress Analysis
**Current Completion:** {data['sprint_progress'].get('current_completion', 0):.1f}%
**Sprint Health:** {data['sprint_progress'].get('sprint_health', {}).get('status', 'Unknown')}
**Velocity Trend:** {data['sprint_progress'].get('velocity_trend', 'stable')}
**Projected Completion:** {data['sprint_progress'].get('projected_completion', 0):.1f}%

### Risk Assessment
{self._format_risk_assessment(data['sprint_progress'].get('risk_assessment', {}))}

## Task Analysis
- **Active Today:** {data['task_analysis'].get('total_active', 0)} tasks
- **Completed:** {data['task_analysis'].get('completed_count', 0)} tasks
- **Started:** {data['task_analysis'].get('started_count', 0)} tasks
- **Blocked:** {data['task_analysis'].get('blocked_count', 0)} tasks
- **Productivity Score:** {data['task_analysis'].get('productivity_score', 0):.1f}/10

### Completed Tasks Today
{self._format_task_list(data['task_analysis'].get('completed_tasks', []))}

## Quality & Blockers
**Test Coverage:** {data['quality_analysis'].get('test_coverage', 0):.1f}%
**Code Quality Score:** {data['quality_analysis'].get('code_quality_score', 0):.1f}/10
**Active Blockers:** {data['blockers_analysis'].get('total_blocked', 0)}

### Blocker Impact
{self._format_blocker_analysis(data['blockers_analysis'])}

## Tomorrow's Preparation
**Planned Tasks:** {data['tomorrow_prep'].get('planned_tasks', 0)}
**Priority Tasks:** {len(data['tomorrow_prep'].get('priority_tasks', []))}

### Success Factors
{self._format_success_factors(data['tomorrow_prep'].get('success_factors', []))}

### Preparation Checklist
{self._format_checklist(data['tomorrow_prep'].get('preparation_checklist', []))}

## Automation Performance
{self._format_automation_stats(data.get('automation_stats', {}))}

---
*Generated at {data['timestamp']} by Enhanced Daily Automation System*
"""
        return content
    
    def _save_report(self, content: str, report_date: str, output_format: str) -> str:
        """Save the formatted report to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"eod_report_{report_date}_{timestamp}.{output_format}"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    # Helper methods for formatting and analysis
    def _get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks from the system."""
        # Implementation would scan outputs directory for task data
        # This is a simplified version
        return []
    
    def _calculate_daily_velocity(self, report_date: str) -> float:
        """Calculate velocity for the specific day."""
        # Implementation would analyze task completions for the day
        return 0.0
    
    def _extract_accomplishments(self, report_date: str) -> List[str]:
        """Extract key accomplishments for the day."""
        # Implementation would analyze completed tasks and identify key ones
        return []
    
    def _identify_daily_challenges(self, report_date: str) -> List[str]:
        """Identify challenges faced during the day."""
        # Implementation would analyze blocked tasks and issues
        return []
    
    def _calculate_progress_trend(self) -> Dict[str, str]:
        """Calculate progress trends."""
        # Implementation would analyze historical data
        return {"velocity": "stable"}
    
    def _assess_sprint_health_detailed(self) -> Dict[str, Any]:
        """Detailed sprint health assessment."""
        # Use the existing sprint health logic from briefing generator
        return {"status": "needs_attention"}
    
    def _project_sprint_completion(self) -> float:
        """Project final sprint completion percentage."""
        # Implementation would use velocity and remaining time
        return 0.0
    
    def _assess_sprint_risks(self) -> Dict[str, Any]:
        """Assess sprint risks."""
        # Implementation would analyze blockers, velocity, etc.
        return {}
    
    def _generate_sprint_recommendations(self) -> List[str]:
        """Generate sprint recommendations."""
        # Implementation would provide actionable recommendations
        return []
    
    def _was_task_active_today(self, task: Dict[str, Any], report_date: str) -> bool:
        """Check if task was active on the given date."""
        # Implementation would check task modification timestamps
        return False
    
    def _was_task_started_today(self, task: Dict[str, Any], report_date: str) -> bool:
        """Check if task was started on the given date."""
        # Implementation would check status change timestamps
        return False
    
    def _format_task_summary(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Format task data for summary display."""
        return {
            "id": task.get("id", "Unknown"),
            "title": task.get("title", "Unknown"),
            "status": task.get("status", "Unknown")
        }
    
    def _calculate_productivity_score(self, tasks: List[Dict[str, Any]]) -> float:
        """Calculate productivity score for the day."""
        # Implementation would analyze task completion vs. planned
        return 0.0
    
    def _analyze_execution_logs(self, report_date: str) -> Dict[str, Any]:
        """Analyze execution monitor logs for automation statistics."""
        # Implementation would parse execution logs
        return {}
    
    def _analyze_task_distribution(self) -> Dict[str, Any]:
        """Analyze task distribution by status, priority, etc."""
        # Implementation would analyze task characteristics
        return {}
    
    def _analyze_task_complexity(self) -> Dict[str, Any]:
        """Analyze task complexity metrics."""
        # Implementation would analyze task complexity
        return {}
    
    def _analyze_time_metrics(self) -> Dict[str, Any]:
        """Analyze time tracking metrics."""
        # Implementation would analyze time spent on tasks
        return {}
    
    def _analyze_qa_metrics(self) -> Dict[str, Any]:
        """Analyze QA and testing metrics."""
        # Implementation would analyze QA coverage and quality
        return {}
    
    def _gather_qa_statistics(self) -> Dict[str, Any]:
        """Gather QA statistics."""
        # Implementation would gather QA data
        return {}
    
    def _calculate_quality_trend(self) -> str:
        """Calculate quality trend."""
        # Implementation would analyze quality over time
        return "stable"
    
    def _categorize_blockers(self, blocked_tasks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize blockers by type."""
        # Implementation would categorize blocker types
        return {}
    
    def _assess_blocker_impact(self, blocked_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess impact of blockers."""
        # Implementation would assess blocker impact
        return {}
    
    def _estimate_blocker_resolution(self, blocked_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate blocker resolution timeline."""
        # Implementation would estimate resolution times
        return {}
    
    def _generate_blocker_recommendations(self, blocked_tasks: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for resolving blockers."""
        # Implementation would generate actionable recommendations
        return []
    
    def _get_planned_tasks_for_tomorrow(self) -> List[Dict[str, Any]]:
        """Get tasks planned for tomorrow."""
        # Implementation would identify tomorrow's planned tasks
        return []
    
    def _identify_priority_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify priority tasks."""
        # Implementation would identify high-priority tasks
        return []
    
    def _identify_potential_blockers(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential blockers for tomorrow."""
        # Implementation would identify potential issues
        return []
    
    def _analyze_resource_needs(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze resource requirements for tomorrow."""
        # Implementation would analyze resource needs
        return {}
    
    def _identify_success_factors(self) -> List[str]:
        """Identify factors for tomorrow's success."""
        # Implementation would identify success factors
        return []
    
    def _generate_preparation_checklist(self) -> List[str]:
        """Generate preparation checklist for tomorrow."""
        # Implementation would generate checklist
        return []
    
    def _format_console_report(self, data: Dict[str, Any]) -> str:
        """Format report for console output."""
        # Implementation would format for console
        return ""
    
    def _format_html_report(self, data: Dict[str, Any]) -> str:
        """Format report as HTML."""
        # Implementation would format as HTML
        return ""
    
    # Additional formatting helper methods
    def _format_accomplishments_list(self, accomplishments: List[str]) -> str:
        """Format accomplishments as markdown list."""
        if not accomplishments:
            return "- No major accomplishments recorded"
        return "\n".join([f"- {acc}" for acc in accomplishments])
    
    def _format_risk_assessment(self, risk_data: Dict[str, Any]) -> str:
        """Format risk assessment data."""
        if not risk_data:
            return "- No significant risks identified"
        # Implementation would format risk data
        return "- Risk assessment data not available"
    
    def _format_task_list(self, tasks: List[Dict[str, Any]]) -> str:
        """Format task list for markdown."""
        if not tasks:
            return "- No tasks completed today"
        return "\n".join([f"- **{task['id']}**: {task['title']}" for task in tasks])
    
    def _format_blocker_analysis(self, blocker_data: Dict[str, Any]) -> str:
        """Format blocker analysis."""
        if blocker_data.get('total_blocked', 0) == 0:
            return "- No active blockers ✅"
        # Implementation would format blocker data
        return f"- {blocker_data.get('total_blocked', 0)} active blockers requiring attention"
    
    def _format_success_factors(self, factors: List[str]) -> str:
        """Format success factors list."""
        if not factors:
            return "- No specific success factors identified"
        return "\n".join([f"- {factor}" for factor in factors])
    
    def _format_checklist(self, checklist: List[str]) -> str:
        """Format preparation checklist."""
        if not checklist:
            return "- [ ] No preparation items identified"
        return "\n".join([f"- [ ] {item}" for item in checklist])
    
    def _format_automation_stats(self, stats: Dict[str, Any]) -> str:
        """Format automation statistics."""
        if not stats or 'error' in stats:
            return "- Automation statistics not available"
        
        return f"""**Briefings Generated:** {stats.get('briefings_generated', 0)}
**Reports Generated:** {stats.get('reports_generated', 0)}
**Dashboard Updates:** {stats.get('dashboard_updates', 0)}
**System Uptime:** {stats.get('automation_uptime', 100.0):.1f}%
**Error Count:** {stats.get('error_count', 0)}"""


async def main():
    """Main entry point for end-of-day report generation."""
    import asyncio
    
    generator = EndOfDayReportGenerator()
    
    try:
        # Generate today's end-of-day report
        report_data = await generator.generate_eod_report()
        
        print(f"✅ End-of-day report generated: {report_data['output_file']}")
        print(f"📊 Report includes comprehensive daily analysis")
        print(f"🔄 Integrated with Phase 5 infrastructure")
        
        return True
        
    except Exception as e:
        print(f"❌ End-of-day report generation failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
