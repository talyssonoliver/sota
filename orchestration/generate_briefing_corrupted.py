#!/usr/bin/env python3
"""
Morning Briefing Generator - Phase 6 Step 6.2

Generates comprehensive morning briefings with sprint status, priorities,
and actionable insights using existing Phase 5 infrastructure.
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


class BriefingGenerator:
    """
    Generates comprehensive morning briefings using Phase 5 data and infrastructure.
    """
    
    def __init__(self):
        """Initialize the briefing generator."""
        self.metrics_calculator = CompletionMetricsCalculator()
        self.execution_monitor = ExecutionMonitor()
        self.logger = logging.getLogger(__name__)
        
        # Initialize paths
        self.briefings_dir = Path("docs/sprint/briefings")
        self.briefings_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_briefing(self, 
                               briefing_type: str = "morning",
                               include_metrics: bool = True,
                               include_priorities: bool = True,
                               output_format: str = "markdown") -> Dict[str, Any]:
        """
        Generate a comprehensive briefing.
        
        Args:
            briefing_type: Type of briefing (morning, midday, eod)
            include_metrics: Include sprint metrics
            include_priorities: Include task priorities
            output_format: Output format (markdown, html, console)
            
        Returns:
            Dictionary with briefing data and status
        """
        self.logger.info(f"Generating {briefing_type} briefing")
        
        try:
            # Gather briefing data
            briefing_data = await self._gather_briefing_data(
                briefing_type, include_metrics, include_priorities
            )
            
            # Generate output based on format
            if output_format == "markdown":
                output = self._generate_markdown_briefing(briefing_data, briefing_type)
            elif output_format == "html":
                output = self._generate_html_briefing(briefing_data, briefing_type)
            else:
                output = self._generate_console_briefing(briefing_data, briefing_type)
            
            # Save briefing to file
            file_path = self._save_briefing(output, briefing_type, output_format)
            
            return {
                "status": "success",
                "briefing_type": briefing_type,
                "file_path": str(file_path),
                "data": briefing_data,
                "output": output
            }
            
        except Exception as e:
            self.logger.error(f"Error generating briefing: {e}")
            return {
                "status": "error",
                "message": str(e),
                "briefing_type": briefing_type
            }
    
    async def _gather_briefing_data(self, 
                                   briefing_type: str,
                                   include_metrics: bool,
                                   include_priorities: bool) -> Dict[str, Any]:
        """Gather data for briefing generation."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "briefing_type": briefing_type,
            "date": datetime.now().strftime("%A, %B %d, %Y")
        }
        
        if include_metrics:
            # Get sprint metrics using existing Phase 5 infrastructure
            try:                
                team_metrics = self.metrics_calculator.calculate_team_metrics()
                sprint_metrics = self.metrics_calculator.calculate_sprint_metrics()
                
                data["metrics"] = {
                    "team": team_metrics,
                    "sprint": sprint_metrics,
                    "completion_rate": team_metrics.get("completion_rate", 0.0) * 100,  # Convert to percentage
                    "velocity": self._calculate_velocity()
                }
            except Exception as e:
                self.logger.warning(f"Could not gather metrics: {e}")
                data["metrics"] = {"error": str(e)}
        
        if include_priorities:
            data["priorities"] = self._get_today_priorities()
            data["yesterday_summary"] = self._get_yesterday_summary()
            data["blockers"] = self._identify_blockers()
        
        # Add sprint health information
        data["sprint_health"] = self._assess_sprint_health()
        data["recommendations"] = self._generate_recommendations(data)
        
        return data
    
    def _calculate_completion_rate(self) -> float:
        """Calculate current sprint completion rate."""
        try:
            # Use existing metrics infrastructure
            all_tasks = self._get_all_tasks()
            completed_tasks = [t for t in all_tasks if t.get("status") == "DONE"]
            
            if not all_tasks:
                return 0.0
            
            return round((len(completed_tasks) / len(all_tasks)) * 100, 1)
        except Exception:
            return 0.0
    
    def _calculate_velocity(self) -> Dict[str, Any]:
        """Calculate sprint velocity metrics."""
        try:
            # Calculate daily and weekly velocity
            tasks_per_day = self._get_daily_task_completion()
            avg_daily = sum(tasks_per_day.values()) / max(len(tasks_per_day), 1)
            
            return {
                "daily_average": round(avg_daily, 1),
                "weekly_projection": round(avg_daily * 7, 1),
                "trend": "stable"  # Could be enhanced with trend analysis
            }
        except Exception:
            return {"daily_average": 0, "weekly_projection": 0, "trend": "unknown"}
    
    def _get_today_priorities(self) -> List[Dict[str, Any]]:
        """Get today's priority tasks."""
        try:
            all_tasks = self._get_all_tasks()
            today_tasks = []
            
            for task in all_tasks:
                if (task.get("status") in ["PLANNED", "IN_PROGRESS"] and 
                    task.get("priority", "").upper() in ["HIGH", "CRITICAL"]):
                    today_tasks.append({
                        "id": task.get("id", ""),
                        "title": task.get("title", ""),
                        "priority": task.get("priority", ""),
                        "owner": task.get("owner", ""),
                        "status": task.get("status", "")
                    })
            
            return sorted(today_tasks, key=lambda x: x.get("priority") == "CRITICAL", reverse=True)[:5]
        except Exception:
            return []
    
    def _get_yesterday_summary(self) -> Dict[str, Any]:
        """Get summary of yesterday's accomplishments."""
        try:
            # This would ideally track completed tasks from yesterday
            # For now, return recent completions
            all_tasks = self._get_all_tasks()
            recent_completed = [t for t in all_tasks if t.get("status") == "DONE"][-5:]
            
            return {
                "completed_tasks": len(recent_completed),
                "tasks": [{"id": t.get("id"), "title": t.get("title")} for t in recent_completed]
            }
        except Exception:
            return {"completed_tasks": 0, "tasks": []}
    
    def _identify_blockers(self) -> List[Dict[str, Any]]:
        """Identify current blockers and issues."""
        try:
            all_tasks = self._get_all_tasks()
            blockers = []
            
            for task in all_tasks:
                if task.get("status") == "BLOCKED":
                    blockers.append({
                        "id": task.get("id"),
                        "title": task.get("title"),
                        "owner": task.get("owner"),
                        "blocker_reason": task.get("blocker_reason", "Unknown")
                    })
            
            return blockers
        except Exception:
            return []
    
    def _assess_sprint_health(self) -> Dict[str, Any]:
        """Assess overall sprint health."""
        try:
            # Use the already calculated team metrics
            team_metrics = self.metrics_calculator.calculate_team_metrics()
            completion_rate = team_metrics.get("completion_rate", 0.0) * 100  # Convert to percentage
            velocity = self._calculate_velocity()
            blockers = len(self._identify_blockers())
            
            # Simple health assessment
            if completion_rate >= 80:
                health_status = "excellent"
            elif completion_rate >= 60:
                health_status = "good"
            elif completion_rate >= 40:
                health_status = "fair"
            else:
                health_status = "needs_attention"
            
            return {
                "status": health_status,
                "completion_rate": completion_rate,
                "daily_velocity": velocity.get("daily_average", 0),
                "active_blockers": blockers,
                "assessment": f"Sprint is {health_status.replace('_', ' ')}"
            }
        except Exception:
            return {"status": "unknown", "assessment": "Unable to assess sprint health"}
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on briefing data."""
        recommendations = []
        
        try:
            sprint_health = data.get("sprint_health", {})
            blockers = data.get("blockers", [])
            priorities = data.get("priorities", [])
            
            # Health-based recommendations
            if sprint_health.get("status") == "needs_attention":
                recommendations.append("⚠️  Sprint completion rate is low - consider reprioritizing tasks")
            
            # Blocker recommendations
            if blockers:
                recommendations.append(f"🚫 {len(blockers)} blocker(s) identified - immediate attention needed")
            
            # Priority recommendations
            if priorities:
                high_priority_count = len([p for p in priorities if p.get("priority") == "HIGH"])
                if high_priority_count > 3:
                    recommendations.append(f"📋 {high_priority_count} high-priority tasks - consider task distribution")
            
            # Default recommendation
            if not recommendations:
                recommendations.append("✅ Sprint is progressing well - maintain current momentum")
                
        except Exception as e:
            recommendations.append(f"⚠️  Unable to generate recommendations: {e}")
        
        return recommendations
    
    def _get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks from the system."""
        try:
            # Try to load from tasks directory or other sources
            tasks_file = Path("tasks.json")
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Fallback to outputs directory scanning
            outputs_dir = Path("outputs")
            if outputs_dir.exists():
                tasks = []
                for task_dir in outputs_dir.iterdir():
                    if task_dir.is_dir():
                        status_file = task_dir / "status.json"
                        if status_file.exists():
                            try:
                                with open(status_file, 'r', encoding='utf-8') as f:
                                    task_data = json.load(f)
                                    task_data["id"] = task_dir.name
                                    tasks.append(task_data)
                            except Exception:
                                continue
                return tasks
            
            return []
        except Exception:
            return []
    
    def _get_daily_task_completion(self) -> Dict[str, int]:
        """Get task completion counts by day."""
        # Simplified implementation - could be enhanced with actual date tracking
        return {"today": 2, "yesterday": 3, "two_days_ago": 1}
    
    def _generate_markdown_briefing(self, data: Dict[str, Any], briefing_type: str) -> str:
        """Generate markdown format briefing."""
        template = f"""# {briefing_type.title()} Briefing - {data['date']}

## Sprint Health Overview
**Status:** {data.get('sprint_health', {}).get('status', 'unknown').replace('_', ' ').title()}
**Completion Rate:** {data.get('sprint_health', {}).get('completion_rate', 0)}%
**Daily Velocity:** {data.get('sprint_health', {}).get('daily_velocity', 0)} tasks/day

## Yesterday's Accomplishments
{self._format_yesterday_summary(data.get('yesterday_summary', {}))}

## Today's Priorities
{self._format_priorities(data.get('priorities', []))}

## Active Blockers
{self._format_blockers(data.get('blockers', []))}

## Recommendations
{self._format_recommendations(data.get('recommendations', []))}

---
*Generated at {data['timestamp']} by Daily Automation System*
"""
        return template
    
    def _generate_html_briefing(self, data: Dict[str, Any], briefing_type: str) -> str:
        """Generate HTML format briefing."""
        # Simplified HTML template
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{briefing_type.title()} Briefing - {data['date']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; }}
        .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #ecf0f1; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{briefing_type.title()} Briefing</h1>
        <p>{data['date']}</p>
    </div>
    
    <div class="section">
        <h2>Sprint Health</h2>
        <div class="metric">Status: {data.get('sprint_health', {}).get('status', 'unknown')}</div>
        <div class="metric">Completion: {data.get('sprint_health', {}).get('completion_rate', 0)}%</div>
    </div>
    
    <!-- Additional sections would be added here -->
    
    <p><em>Generated at {data['timestamp']}</em></p>
</body>
</html>
"""
        return html_template
    
    def _generate_console_briefing(self, data: Dict[str, Any], briefing_type: str) -> str:
        """Generate console-friendly briefing."""
        output = f"""
{'='*60}
{briefing_type.upper()} BRIEFING - {data['date']}
{'='*60}

SPRINT HEALTH: {data.get('sprint_health', {}).get('status', 'unknown').upper()}
Completion Rate: {data.get('sprint_health', {}).get('completion_rate', 0)}%

TODAY'S PRIORITIES:
{self._format_priorities_console(data.get('priorities', []))}

BLOCKERS:
{self._format_blockers_console(data.get('blockers', []))}

RECOMMENDATIONS:
{self._format_recommendations_console(data.get('recommendations', []))}

{'='*60}
"""
        return output
    
    def _format_yesterday_summary(self, summary: Dict[str, Any]) -> str:
        """Format yesterday's summary for markdown."""
        if not summary.get("tasks"):
            return "- No completed tasks recorded"
        
        formatted = [f"**Completed:** {summary.get('completed_tasks', 0)} tasks"]
        for task in summary.get("tasks", [])[:3]:
            formatted.append(f"- {task.get('id', '')}: {task.get('title', '')}")
        
        return "\n".join(formatted)
    
    def _format_priorities(self, priorities: List[Dict[str, Any]]) -> str:
        """Format priorities for markdown."""
        if not priorities:
            return "- No high-priority tasks identified"
        
        formatted = []
        for priority in priorities:
            status_emoji = "🔴" if priority.get("priority") == "CRITICAL" else "🟡"
            formatted.append(f"- {status_emoji} **{priority.get('id')}**: {priority.get('title')} ({priority.get('owner')})")
        
        return "\n".join(formatted)
    
    def _format_blockers(self, blockers: List[Dict[str, Any]]) -> str:
        """Format blockers for markdown."""
        if not blockers:
            return "- No active blockers ✅"
        
        formatted = []
        for blocker in blockers:
            formatted.append(f"- 🚫 **{blocker.get('id')}**: {blocker.get('title')} ({blocker.get('owner')})")
        
        return "\n".join(formatted)
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations for markdown."""
        if not recommendations:
            return "- No specific recommendations"
        
        return "\n".join([f"- {rec}" for rec in recommendations])
    
    def _format_priorities_console(self, priorities: List[Dict[str, Any]]) -> str:
        """Format priorities for console output."""
        if not priorities:
            return "  No high-priority tasks"
        return "\n".join([f"  - {p.get('id')}: {p.get('title')}" for p in priorities[:5]])
    
    def _format_blockers_console(self, blockers: List[Dict[str, Any]]) -> str:
        """Format blockers for console output."""
        if not blockers:
            return "  No active blockers"
        return "\n".join([f"  - {b.get('id')}: {b.get('title')}" for b in blockers])
    
    def _format_recommendations_console(self, recommendations: List[str]) -> str:
        """Format recommendations for console output."""
        if not recommendations:
            return "  No specific recommendations"
        return "\n".join([f"  - {rec}" for rec in recommendations])
    
    def _save_briefing(self, content: str, briefing_type: str, output_format: str) -> Path:
        """Save briefing to file."""
        timestamp = datetime.now().strftime("%Y%m%d")
        
        if output_format == "html":
            filename = f"{timestamp}_{briefing_type}_briefing.html"
        else:
            filename = f"{timestamp}_{briefing_type}_briefing.md"
        
        file_path = self.briefings_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Briefing saved to {file_path}")
        return file_path


def main():
    """CLI interface for briefing generation."""
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(description="Generate morning briefings")
    parser.add_argument("--type", choices=["morning", "midday", "eod"], default="morning",
                       help="Type of briefing to generate")
    parser.add_argument("--format", choices=["markdown", "html", "console"], default="markdown",
                       help="Output format")
    parser.add_argument("--no-metrics", action="store_true", help="Exclude metrics")
    parser.add_argument("--no-priorities", action="store_true", help="Exclude priorities")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = BriefingGenerator()
    
    # Generate briefing
    result = asyncio.run(generator.generate_briefing(
        briefing_type=args.type,
        include_metrics=not args.no_metrics,
        include_priorities=not args.no_priorities,
        output_format=args.format
    ))
    
    if result["status"] == "success":
        print(f"✅ Briefing generated successfully: {result['file_path']}")
        if args.format == "console":
            print(result["output"])
    else:
        print(f"❌ Error generating briefing: {result['message']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
