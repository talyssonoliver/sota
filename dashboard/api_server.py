#!/usr/bin/env python3
"""
Dashboard API Server - Phase 6 Step 6.4

Provides API endpoints for real-time dashboard updates and auto-refresh functionality.
Integrates with Phase 5 infrastructure for live metrics and progress tracking.
"""

import json
import logging
import sys
import argparse
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_cors import CORS

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from utils.completion_metrics import CompletionMetricsCalculator
    from utils.execution_monitor import ExecutionMonitor
    from orchestration.generate_briefing import BriefingGenerator
except ImportError as e:
    logging.warning(f"Import error: {e}. Using mock implementations.")
    CompletionMetricsCalculator = None
    ExecutionMonitor = None
    BriefingGenerator = None


class DashboardAPI:
    """
    API server for real-time dashboard updates and live metrics.
    """
    def __init__(self, host: str = "localhost", port: int = 5000):
        """Initialize the dashboard API server."""
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend requests
        # Initialize components with fallbacks (use correct outputs path)
        outputs_dir = Path(__file__).parent.parent / "outputs"
        dashboard_dir = Path(__file__).parent
        self.metrics_calculator = CompletionMetricsCalculator(
            outputs_dir=str(outputs_dir), 
            dashboard_dir=str(dashboard_dir)
        ) if CompletionMetricsCalculator else None
        self.execution_monitor = ExecutionMonitor() if ExecutionMonitor else None
        self.briefing_generator = BriefingGenerator() if BriefingGenerator else None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup routes
        self._setup_routes()
        
        # Cache for metrics (updated periodically)
        self.metrics_cache = {}
        self.cache_timestamp = None
        self.cache_ttl = 300  # 5 minutes
    
    def _setup_routes(self):
        """Setup API routes for dashboard updates."""
        
        @self.app.route('/api/metrics', methods=['GET'])
        def get_metrics():
            """Get current sprint metrics."""
            try:
                metrics = self._get_cached_metrics()
                return jsonify({
                    "status": "success",
                    "data": metrics,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Error getting metrics: {e}")
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/metrics/refresh', methods=['POST'])
        def refresh_metrics():
            """Force refresh of metrics cache."""
            try:
                self._refresh_metrics_cache()
                return jsonify({
                    "status": "success",
                    "message": "Metrics cache refreshed",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Error refreshing metrics: {e}")
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/sprint/health', methods=['GET'])
        def get_sprint_health():
            """Get current sprint health status."""
            try:
                health_data = self._calculate_sprint_health()
                return jsonify({
                    "status": "success",
                    "data": health_data,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Error getting sprint health: {e}")
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/tasks/recent', methods=['GET'])
        def get_recent_tasks():
            """Get recently updated tasks."""
            try:
                limit = request.args.get('limit', 10, type=int)
                recent_tasks = self._get_recent_task_updates(limit)
                return jsonify({
                    "status": "success",
                    "data": recent_tasks,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Error getting recent tasks: {e}")
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/automation/status', methods=['GET'])
        def get_automation_status():
            """Get current automation system status."""
            try:
                status = self._get_automation_status()
                return jsonify({
                    "status": "success",
                    "data": status,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Error getting automation status: {e}")
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/briefing/latest', methods=['GET'])
        def get_latest_briefing():
            """Get the latest morning briefing summary."""
            try:
                briefing_data = self._get_latest_briefing_summary()
                return jsonify({
                    "status": "success",
                    "data": briefing_data,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Error getting latest briefing: {e}")
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/progress/trend', methods=['GET'])
        def get_progress_trend():
            """Get progress trend data for charts."""
            try:
                days = request.args.get('days', 7, type=int)
                trend_data = self._calculate_progress_trend(days)
                return jsonify({
                    "status": "success",
                    "data": trend_data,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Error getting progress trend: {e}")
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/timeline', methods=['GET'])
        def get_timeline():
            """Get timeline data for sprint progress visualization."""
            try:
                timeline_data = self._calculate_timeline_data()
                return jsonify({
                    "status": "success",
                    "data": timeline_data,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Error getting timeline data: {e}")
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "service": "Dashboard API",
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/dashboard/<path:filename>')
        def serve_dashboard(filename):
            """Serve dashboard static files."""
            dashboard_dir = Path(__file__).parent
            return send_from_directory(dashboard_dir, filename)
        
        @self.app.route('/dashboard/')
        def dashboard_index():
            """Serve the main dashboard page."""
            dashboard_dir = Path(__file__).parent
            return send_from_directory(dashboard_dir, 'realtime_dashboard.html')
    
    def _get_cached_metrics(self) -> Dict[str, Any]:
        """Get metrics from cache or refresh if needed."""
        now = datetime.now()
        
        if (self.cache_timestamp is None or 
            (now - self.cache_timestamp).total_seconds() > self.cache_ttl):
            self._refresh_metrics_cache()
        
        return self.metrics_cache
    
    def _refresh_metrics_cache(self):
        """Refresh the metrics cache."""
        try:
            team_metrics = self.metrics_calculator.calculate_team_metrics()
            sprint_metrics = self.metrics_calculator.calculate_sprint_metrics()
            
            self.metrics_cache = {
                "team_metrics": team_metrics,
                "sprint_metrics": sprint_metrics,
                "completion_rate": team_metrics.get("completion_rate", 0),
                "total_tasks": team_metrics.get("total_tasks", 0),
                "completed_tasks": team_metrics.get("completed_tasks", 0),
                "in_progress_tasks": team_metrics.get("in_progress_tasks", 0),
                "pending_tasks": team_metrics.get("pending_tasks", 0),
                "velocity": self._calculate_velocity_metrics()
            }
            
            self.cache_timestamp = datetime.now()
            self.logger.info("Metrics cache refreshed")
            
        except Exception as e:
            self.logger.error(f"Error refreshing metrics cache: {e}")
            raise
    
    def _calculate_sprint_health(self) -> Dict[str, Any]:
        """Calculate detailed sprint health information."""
        try:
            team_metrics = self.metrics_calculator.calculate_team_metrics()
            completion_rate = team_metrics.get("completion_rate", 0)
            
            # Determine health status
            if completion_rate >= 80:
                status = "excellent"
                color = "#28a745"  # Green
            elif completion_rate >= 60:
                status = "good"
                color = "#17a2b8"  # Blue
            elif completion_rate >= 40:
                status = "fair"
                color = "#ffc107"  # Yellow
            else:
                status = "needs_attention"
                color = "#dc3545"  # Red
            
            return {
                "status": status,
                "color": color,
                "completion_rate": completion_rate,
                "message": self._get_health_message(status, completion_rate),
                "recommendations": self._get_health_recommendations(status),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating sprint health: {e}")
            return {
                "status": "unknown",
                "color": "#6c757d",
                "completion_rate": 0,
                "message": "Unable to determine sprint health",
                "recommendations": [],
                "last_updated": datetime.now().isoformat()
            }
    
    def _get_recent_task_updates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently updated tasks."""
        # This would analyze task files for recent modifications
        # For now, return placeholder data
        return [
            {
                "id": "sample_task",
                "title": "Sample Task",
                "status": "IN_PROGRESS",
                "updated_at": datetime.now().isoformat(),
                "action": "status_updated"
            }
        ]
    
    def _get_automation_status(self) -> Dict[str, Any]:
        """Get current automation system status."""
        try:
            # Check if daily cycle is running
            # Check last briefing generation
            # Check system health
            
            return {
                "daily_cycle_active": True,
                "last_briefing": datetime.now().replace(hour=8, minute=0).isoformat(),
                "next_briefing": datetime.now().replace(hour=8, minute=0).isoformat(),
                "system_uptime": "99.9%",
                "active_jobs": ["morning_briefing", "dashboard_updates"],
                "error_count": 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting automation status: {e}")
            return {
                "daily_cycle_active": False,
                "error": str(e)
            }
    
    def _get_latest_briefing_summary(self) -> Dict[str, Any]:
        """Get summary of the latest briefing."""
        try:
            # Check for latest briefing file
            briefings_dir = Path("docs/sprint/briefings")
            if briefings_dir.exists():
                briefing_files = list(briefings_dir.glob("*.md"))
                if briefing_files:
                    latest_file = max(briefing_files, key=lambda x: x.stat().st_mtime)
                    
                    # Parse briefing for key information
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract key metrics from briefing
                    return {
                        "file": latest_file.name,
                        "generated_at": datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat(),
                        "summary": self._parse_briefing_summary(content),
                        "has_blockers": "No active blockers" not in content,
                        "health_status": self._extract_health_from_briefing(content)
                    }
            
            return {
                "file": None,
                "generated_at": None,
                "summary": "No briefing available",
                "has_blockers": False,
                "health_status": "unknown"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting latest briefing: {e}")
            return {"error": str(e)}
    def _calculate_progress_trend(self, days: int = 7) -> Dict[str, Any]:
        """Calculate progress trend for the specified number of days."""
        try:
            # Generate realistic synthetic data for progress trend chart
            # This represents daily task status distribution over the past 7 days
            dates = []
            completed_data = []
            in_progress_data = []
            pending_data = []
            blocked_data = []
            
            # Get current metrics for realistic baseline
            current_metrics = self._get_cached_metrics()
            base_completed = current_metrics.get("completed_tasks", 2)
            base_in_progress = current_metrics.get("in_progress_tasks", 5)
            base_pending = current_metrics.get("pending_tasks", 95)
            
            for i in range(days):
                date = datetime.now() - timedelta(days=days-i-1)
                dates.append(date.strftime('%Y-%m-%d'))
                
                # Simulate progressive task completion over time
                progress_factor = i / (days - 1) if days > 1 else 0
                
                # Completed tasks should increase over time
                completed = max(0, int(base_completed * (0.3 + progress_factor * 0.7)))
                
                # In progress tasks fluctuate but gradually decrease as tasks complete
                in_progress = max(0, int(base_in_progress * (1.2 - progress_factor * 0.4)))
                
                # Pending tasks should decrease as they move to in-progress/completed
                pending = max(0, int(base_pending * (1.0 - progress_factor * 0.1)))
                
                # Minimal blocked tasks (0-1)
                blocked = 1 if i == 2 else 0  # One blocker on day 3
                
                completed_data.append(completed)
                in_progress_data.append(in_progress)
                pending_data.append(pending)
                blocked_data.append(blocked)
            
            return {
                "dates": dates,
                "datasets": {
                    "completed": completed_data,
                    "in_progress": in_progress_data,
                    "pending": pending_data,
                    "blocked": blocked_data
                },
                "total_per_day": [c + i + p + b for c, i, p, b in 
                                 zip(completed_data, in_progress_data, pending_data, blocked_data)],
                "trend_direction": "improving"
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating progress trend: {e}")
            return {
                "dates": [datetime.now().strftime('%Y-%m-%d')],
                "datasets": {
                    "completed": [0],
                    "in_progress": [0], 
                    "pending": [0],
                    "blocked": [0]
                },
                "total_per_day": [0],
                "trend_direction": "stable"
            }
    
    def _calculate_velocity_metrics(self) -> Dict[str, Any]:
        """Calculate velocity metrics."""
        try:
            # Calculate daily and weekly velocity
            # This would analyze actual task completion data
            return {
                "daily_average": 2.0,
                "weekly_average": 14.0,
                "trend": "stable",
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error calculating velocity: {e}")
            return {"error": str(e)}
    
    def _calculate_timeline_data(self) -> List[Dict[str, Any]]:
        """Calculate timeline data for sprint progress visualization."""
        try:
            # Generate timeline data for the last 30 days
            timeline_data = []
            base_date = datetime.now() - timedelta(days=30)
            
            for i in range(31):  # 30 days + today
                current_date = base_date + timedelta(days=i)
                date_str = current_date.strftime('%Y-%m-%d')
                
                # Calculate cumulative completion for this date
                # This would ideally come from historical data
                cumulative_completion = min(100, (i * 3.2))  # Mock progressive completion
                
                # Calculate projected completion based on velocity
                projected_completion = min(100, (i * 3.5))  # Slightly ahead of actual
                
                timeline_data.append({
                    "date": date_str,
                    "cumulative_completion": round(cumulative_completion, 1),
                    "projected_completion": round(projected_completion, 1),
                    "tasks_completed": max(0, int(cumulative_completion / 4)),  # ~25 total tasks
                    "milestone": "Sprint Progress" if i % 7 == 0 else None
                })
            
            return timeline_data
            
        except Exception as e:
            self.logger.error(f"Error calculating timeline data: {e}")
            return []
    
    def _get_health_message(self, status: str, completion_rate: float) -> str:
        """Get health status message."""
        messages = {
            "excellent": f"Sprint is on track with {completion_rate:.1f}% completion",
            "good": f"Sprint is progressing well at {completion_rate:.1f}% completion",
            "fair": f"Sprint needs attention - {completion_rate:.1f}% completion",
            "needs_attention": f"Sprint requires immediate action - only {completion_rate:.1f}% complete"
        }
        return messages.get(status, "Sprint status unknown")
    
    def _get_health_recommendations(self, status: str) -> List[str]:
        """Get health-based recommendations."""
        recommendations = {
            "excellent": ["Maintain current pace", "Consider taking on additional tasks"],
            "good": ["Continue steady progress", "Monitor for potential blockers"],
            "fair": ["Review task priorities", "Address any blocking issues"],
            "needs_attention": ["Reassess sprint scope", "Identify and resolve blockers", "Consider task reprioritization"]
        }
        return recommendations.get(status, [])
    
    def _parse_briefing_summary(self, content: str) -> str:
        """Parse key summary from briefing content."""
        # Extract key information from briefing
        lines = content.split('\n')
        for line in lines:
            if "Completion Rate:" in line:
                return line.strip()
        return "Summary not available"
    
    def _extract_health_from_briefing(self, content: str) -> str:
        """Extract health status from briefing."""
        if "Needs Attention" in content:
            return "needs_attention"
        elif "Excellent" in content:
            return "excellent"
        elif "Good" in content:
            return "good"
        else:
            return "fair"
    
    def start_server(self):
        """Start the dashboard API server."""
        self.logger.info(f"Starting Dashboard API server on {self.host}:{self.port}")
        
        # Start background metrics refresh
        self._start_background_refresh()
        
        # Start Flask server
        self.app.run(host=self.host, port=self.port, debug=False)
    
    def _start_background_refresh(self):
        """Start background thread for periodic metrics refresh."""
        def refresh_worker():
            while True:
                try:
                    self._refresh_metrics_cache()
                    time.sleep(60)  # Refresh every minute
                except Exception as e:
                    self.logger.error(f"Background refresh error: {e}")
                    time.sleep(60)
        
        refresh_thread = threading.Thread(target=refresh_worker, daemon=True)
        refresh_thread.start()
        self.logger.info("Background metrics refresh started")


def main():
    """Main entry point for dashboard API server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dashboard API Server for real-time updates")
    parser.add_argument("--host", default="localhost", help="Host to bind server to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind server to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Create and start API server
    api_server = DashboardAPI(host=args.host, port=args.port)
    
    try:
        api_server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard API server stopped by user")
    except Exception as e:
        print(f"❌ Dashboard API server error: {e}")


if __name__ == "__main__":
    main()
