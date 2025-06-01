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
from collections import Counter
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
    async def generate_day_briefing(self, day: int, output_format: str = "markdown") -> Dict[str, Any]:
        """
        Generate day-specific morning briefing as required by Step 6.2.
        
        Args:
            day: Day number for the briefing (must be positive)
            output_format: Output format (markdown, console)
            
        Returns:
            Dictionary with briefing data and status
        """
        if day <= 0:
            raise ValueError("Day must be a positive integer")
        
        self.logger.info(f"Generating Day {day} morning briefing")
        
        try:
            # Gather day-specific briefing data
            briefing_data = await self._gather_day_briefing_data(day)
            
            # Generate output based on format
            if output_format == "console":
                output = self._generate_day_console_briefing(briefing_data, day)
            else:
                output = self._generate_day_markdown_briefing(briefing_data, day)
            
            # Save briefing to day-specific file (always save as markdown)
            file_path = self._save_day_briefing(
                self._generate_day_markdown_briefing(briefing_data, day), day
            )
            
            return {
                "status": "success",
                "day": day,
                "file_path": str(file_path),
                "data": briefing_data,
                "output": output,
                "format": output_format
            }
            
        except Exception as e:
            self.logger.error(f"Error generating day {day} briefing: {e}")
            return {
                "status": "error",
                "message": str(e),
                "day": day
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
                    "completion_rate": team_metrics.get("completion_rate", 0.0),  # Already in percentage format
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

    async def _gather_day_briefing_data(self, day: int) -> Dict[str, Any]:
        """Gather data for day-specific briefing generation."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "day": day,
            "date": datetime.now().strftime("%A, %B %d, %Y")
        }
        
        try:
            # Get backend and frontend tasks
            data["backend_tasks"] = self._get_backend_tasks()
            data["frontend_tasks"] = self._get_frontend_tasks()
            
            # Generate key focus areas
            data["key_focus"] = self._generate_key_focus()
            
            # Generate coordination points
            data["coordination_points"] = self._generate_coordination_points(day)
            
            # Include metrics if available
            try:
                team_metrics = self.metrics_calculator.calculate_team_metrics()
                data["metrics"] = team_metrics
                data["metrics_error"] = None
            except Exception as e:
                self.logger.warning(f"Could not gather metrics: {e}")
                data["metrics"] = None
                data["metrics_error"] = str(e)
            
        except Exception as e:
            self.logger.error(f"Error gathering day briefing data: {e}")
            data["error"] = str(e)
        
        return data
    
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
            completion_rate = team_metrics.get("completion_rate", 0.0)  # Already in percentage format
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
                        # Try to load from task_declaration.json first (more complete data)
                        task_declaration_file = task_dir / "task_declaration.json"
                        status_file = task_dir / "status.json"
                        
                        task_data = {"id": task_dir.name}
                        
                        # Load task declaration for title, description, priority
                        if task_declaration_file.exists():
                            try:
                                with open(task_declaration_file, 'r', encoding='utf-8') as f:
                                    declaration_data = json.load(f)
                                    task_data.update({
                                        "title": declaration_data.get("title", ""),
                                        "priority": declaration_data.get("priority", "MEDIUM"),
                                        "owner": declaration_data.get("owner", ""),
                                        "description": declaration_data.get("description", "")
                                    })
                            except Exception:
                                pass
                        
                        # Load status for current state
                        if status_file.exists():
                            try:
                                with open(status_file, 'r', encoding='utf-8') as f:
                                    status_data = json.load(f)
                                    task_data.update({
                                        "status": status_data.get("status", "UNKNOWN"),
                                        "state": status_data.get("state", "UNKNOWN")
                                    })
                            except Exception:
                                pass
                        
                        # Determine task type from ID or other hints
                        task_id = task_dir.name
                        if task_id.startswith("BE-"):
                            task_data["type"] = "backend"
                        elif task_id.startswith("FE-"):
                            task_data["type"] = "frontend"
                        elif task_id.startswith("UX-"):
                            task_data["type"] = "frontend"
                        elif task_id.startswith("QA-"):
                            task_data["type"] = "qa"
                        else:
                            task_data["type"] = "other"
                        
                        tasks.append(task_data)
                
                return tasks
            
            return []
        except Exception:
            return []
        
    def _get_daily_task_completion(self) -> Dict[str, int]:
        """Get task completion counts by day (last 7 days)."""

        all_tasks = self._get_all_tasks()
        completion_counts = Counter()

        for task in all_tasks:
            if task.get("status") == "DONE":
                # Try to get completion date from task, fallback to today if missing
                completed_at = task.get("completed_at")
                if completed_at:
                    try:
                        # Support both ISO and date-only formats
                        dt = datetime.fromisoformat(completed_at[:19])
                        day_str = dt.strftime("%Y-%m-%d")
                    except Exception:
                        day_str = datetime.now().strftime("%Y-%m-%d")
                else:
                    day_str = datetime.now().strftime("%Y-%m-%d")
                completion_counts[day_str] += 1

        # Prepare last 7 days (including today)
        result = {}
        for i in range(7):
            day = datetime.now() - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            result[day_str] = completion_counts.get(day_str, 0)

        return result

    def _get_backend_tasks(self) -> List[Dict[str, Any]]:
        """Get backend-specific tasks for day briefing."""
        try:
            all_tasks = self._get_all_tasks()
            backend_tasks = []
            
            for task in all_tasks:
                task_id = task.get("id", "")
                task_type = task.get("type", "")
                
                # Identify backend tasks by ID prefix or type
                if (task_id.startswith("BE-") or 
                    task_type.lower() == "backend" or
                    "backend" in task.get("title", "").lower()):
                    backend_tasks.append({
                        "id": task_id,
                        "title": task.get("title", ""),
                        "status": task.get("status", ""),
                        "priority": task.get("priority", ""),
                        "owner": task.get("owner", "")
                    })
            
            return backend_tasks
        except Exception as e:
            self.logger.warning(f"Could not get backend tasks: {e}")
            return []

    def _get_frontend_tasks(self) -> List[Dict[str, Any]]:
        """Get frontend-specific tasks for day briefing."""
        try:
            all_tasks = self._get_all_tasks()
            frontend_tasks = []
            
            for task in all_tasks:
                task_id = task.get("id", "")
                task_type = task.get("type", "")
                
                # Identify frontend tasks by ID prefix or type
                if (task_id.startswith("FE-") or 
                    task_type.lower() == "frontend" or
                    "frontend" in task.get("title", "").lower() or
                    "ui" in task.get("title", "").lower()):
                    frontend_tasks.append({
                        "id": task_id,
                        "title": task.get("title", ""),
                        "status": task.get("status", ""),
                        "priority": task.get("priority", ""),
                        "owner": task.get("owner", "")
                    })
            
            return frontend_tasks
        except Exception as e:
            self.logger.warning(f"Could not get frontend tasks: {e}")
            return []

    def _generate_key_focus(self) -> List[str]:
        """Generate key focus areas for the day."""
        focus_areas = []
        
        try:
            backend_tasks = self._get_backend_tasks()
            frontend_tasks = self._get_frontend_tasks()
            
            # Generate backend focus
            if backend_tasks:
                high_priority_be = [t for t in backend_tasks if t.get("priority") in ["HIGH", "CRITICAL"]]
                if high_priority_be:
                    if any("supabase" in t.get("title", "").lower() for t in high_priority_be):
                        focus_areas.append("Backend to integrate services with Supabase")
                    else:
                        focus_areas.append("Backend to complete high-priority infrastructure tasks")
                else:
                    focus_areas.append("Backend to maintain development momentum")
            
            # Generate frontend focus
            if frontend_tasks:
                high_priority_fe = [t for t in frontend_tasks if t.get("priority") in ["HIGH", "CRITICAL"]]
                if high_priority_fe:
                    if any("ui" in t.get("title", "").lower() or "component" in t.get("title", "").lower() for t in high_priority_fe):
                        focus_areas.append("Frontend to align with UX prototypes")
                    else:
                        focus_areas.append("Frontend to complete critical user interface work")
                else:
                    focus_areas.append("Frontend to continue component development")
            
            # Default focus if no specific areas identified
            if not focus_areas:
                focus_areas.append("Team to maintain sprint momentum and address priority tasks")
            
        except Exception as e:
            self.logger.warning(f"Could not generate key focus: {e}")
            focus_areas.append("Team to review and prioritize current tasks")
        
        return focus_areas

    def _generate_coordination_points(self, day: int) -> List[str]:
        """Generate coordination points for the day."""
        coordination_points = []
        
        try:
            # Generate time-based coordination points
            morning_sync = f"10:30 AM Logs sync"
            afternoon_sync = f"1:30 PM API Integration call"
            
            coordination_points.extend([morning_sync, afternoon_sync])
            
            # Add day-specific coordination if needed
            if day == 1:
                coordination_points.append("3:00 PM Sprint kickoff review")
            elif day % 2 == 0:
                coordination_points.append("4:00 PM Progress review meeting")
            
        except Exception as e:
            self.logger.warning(f"Could not generate coordination points: {e}")
            coordination_points = ["Team sync meetings as scheduled"]
        
        return coordination_points

    def _get_day_briefing_path(self, day: int) -> Path:
        """Get the file path for day-specific briefing."""
        filename = f"day{day}-morning-briefing.md"
        return Path("docs/sprint/briefings") / filename

    def _save_day_briefing(self, content: str, day: int) -> Path:
        """Save day-specific briefing to file."""
        file_path = self._get_day_briefing_path(day)
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Day {day} briefing saved to {file_path}")
        return file_path

    def _generate_day_console_briefing(self, data: Dict[str, Any], day: int) -> str:
        """Generate day-specific console format briefing."""
        output = f"""
{'='*60}
DAY {day} MORNING BRIEFING
{'='*60}

BACKEND TASKS:
{self._format_task_list_console(data.get('backend_tasks', []))}

FRONTEND TASKS:
{self._format_task_list_console(data.get('frontend_tasks', []))}

KEY FOCUS:
{self._format_focus_list_console(data.get('key_focus', []))}

COORDINATION POINTS:
{self._format_coordination_list_console(data.get('coordination_points', []))}

{'='*60}
Generated at {data.get('timestamp', datetime.now().isoformat())}
{'='*60}
"""
        return output

    def _format_task_list_console(self, tasks: List[Dict[str, Any]]) -> str:
        """Format task list for console output."""
        if not tasks:
            return "  No tasks identified"
        
        formatted = []
        for task in tasks:
            formatted.append(f"  - {task.get('id', '')}: {task.get('title', '')}")
        
        return "\n".join(formatted)

    def _format_focus_list_console(self, focus_areas: List[str]) -> str:
        """Format focus areas list for console."""
        if not focus_areas:
            return "  Maintain current development momentum"
        
        return "\n".join([f"  - {area}" for area in focus_areas])

    def _format_coordination_list_console(self, coordination_points: List[str]) -> str:
        """Format coordination points list for console."""
        if not coordination_points:
            return "  Team sync as needed"
        
        return "\n".join([f"  - {point}" for point in coordination_points])

    def _generate_day_markdown_briefing(self, data: Dict[str, Any], day: int) -> str:
        """Generate day-specific markdown format briefing."""
        template = f"""# Day {day} Morning Briefing

## Backend Tasks
{self._format_task_list(data.get('backend_tasks', []))}

## Frontend Tasks
{self._format_task_list(data.get('frontend_tasks', []))}

## Key Focus
{self._format_focus_list(data.get('key_focus', []))}

## Coordination Points
{self._format_coordination_list(data.get('coordination_points', []))}

---
*Generated at {data.get('timestamp', datetime.now().isoformat())} by Daily Automation System*
*Saved to: docs/sprint/briefings/day{day}-morning-briefing.md*
"""
        return template

    def _format_task_list(self, tasks: List[Dict[str, Any]]) -> str:
        """Format task list for day briefing."""
        if not tasks:
            return "- No tasks identified"
        
        formatted = []
        for task in tasks:
            formatted.append(f"- {task.get('id', '')}: {task.get('title', '')}")
        
        return "\n".join(formatted)

    def _format_focus_list(self, focus_areas: List[str]) -> str:
        """Format focus areas list."""
        if not focus_areas:
            return "- Maintain current development momentum"
        
        return "\n".join([f"- {area}" for area in focus_areas])

    def _format_coordination_list(self, coordination_points: List[str]) -> str:
        """Format coordination points list."""
        if not coordination_points:
            return "- Team sync as needed"
        
        return "\n".join([f"- {point}" for point in coordination_points])
    
    def _generate_markdown_briefing(self, data: Dict[str, Any], briefing_type: str) -> str:
        """Generate markdown format briefing."""
        template = f"""# {briefing_type.title()} Briefing - {data['date']}

## Sprint Health Overview
**Status:** {data.get('sprint_health', {}).get('status', 'unknown').replace('_', ' ').title()}
**Completion Rate:** {data.get('sprint_health', {}).get('completion_rate', 0):.1f}%
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
        <div class="metric">Completion: {data.get('sprint_health', {}).get('completion_rate', 0):.1f}%</div>
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
Completion Rate: {data.get('sprint_health', {}).get('completion_rate', 0):.1f}%

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
    parser.add_argument("--day", type=int, help="Generate day-specific briefing (e.g., --day 2)")
    parser.add_argument("--type", choices=["morning", "midday", "eod"], default="morning",
                       help="Type of briefing to generate")
    parser.add_argument("--format", choices=["markdown", "html", "console"], default="markdown",
                       help="Output format")
    parser.add_argument("--no-metrics", action="store_true", help="Exclude metrics")
    parser.add_argument("--no-priorities", action="store_true", help="Exclude priorities")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = BriefingGenerator()
      # Check if day-specific briefing is requested
    if args.day is not None:
        if args.day <= 0:
            print("❌ Error: Day must be a positive integer")
            sys.exit(1)
        
        # Generate day-specific briefing
        result = asyncio.run(generator.generate_day_briefing(day=args.day, output_format=args.format))
        
        if result["status"] == "success":
            print(f"✅ Day {args.day} briefing generated successfully: {result['file_path']}")
            if args.format == "console":
                print(result["output"])
        else:
            print(f"❌ Error generating day {args.day} briefing: {result['message']}")
            sys.exit(1)
    else:
        # Generate regular briefing
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
