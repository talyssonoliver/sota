#!/usr/bin/env python3
"""
Daily Cycle Automation Orchestrator - Phase 6 Step 6.1

Automated daily task processing orchestrator that manages the complete
daily cycle of task processing, reporting, and dashboard updates.
Integrates with existing Phase 5 infrastructure for seamless automation.
"""

import asyncio
import json
import logging
import os
import schedule
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.completion_metrics import CompletionMetricsCalculator
from utils.execution_monitor import ExecutionMonitor
from orchestration.generate_briefing import BriefingGenerator
from orchestration.end_of_day_report import EndOfDayReportGenerator
from orchestration.email_integration import EmailIntegration
import subprocess


class DailyCycleOrchestrator:
    """
    Orchestrates daily automation tasks including briefings, reports, and dashboard updates.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the daily cycle orchestrator.
        
        Args:
            config_path: Path to configuration file        """
        self.config_path = config_path or "config/daily_cycle.json"
        self.config = self._load_config()
        
        # Initialize logging after config is loaded
        self._setup_logging()
        
        # Initialize components
        self.metrics_calculator = CompletionMetricsCalculator()
        self.execution_monitor = ExecutionMonitor()
        self.briefing_generator = BriefingGenerator()
        self.eod_report_generator = EndOfDayReportGenerator()
        self.email_integration = EmailIntegration(self.config_path)
        self.logger.info("Daily Cycle Orchestrator initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        default_config = self._get_default_config()
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Merge loaded config with defaults, preserving user settings
                merged_config = default_config.copy()
                for section, values in loaded_config.items():
                    if section in merged_config and isinstance(values, dict):
                        merged_config[section].update(values)
                    else:
                        merged_config[section] = values
                
                return merged_config
            else:
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "paths": {
                "logs_dir": "logs/daily_cycle",
                "briefings_dir": "docs/sprint/briefings",
                "reports_dir": "docs/sprint/reports",
                "templates_dir": "templates"
            },            "automation": {
                "enabled": True,
                "morning_briefing_time": "09:00",
                "eod_report_time": "17:00",
                "check_interval": 30,
                "max_retries": 3,
                "auto_dashboard_update": True
            },
            "email": {
                "enabled": False,
                "smtp_server": "localhost",
                "smtp_port": 587,
                "use_tls": False,
                "username": "",
                "password": "",
                "from_address": "ai-system@localhost",
                "recipients": {
                    "team_leads": [],
                    "stakeholders": [],
                    "developers": []
                },
                "retry_attempts": 3,
                "retry_delay": 5
            },
            "dashboard": {
                "api_port": 5000,
                "refresh_interval": 30,
                "cache_duration": 300
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_rotation": True,
                "max_file_size": "10MB",
                "backup_count": 5
            }
        }
    
    def _setup_logging(self):
        """Setup logging for daily cycle operations."""
        logs_dir = Path(self.config["paths"]["logs_dir"])
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = logs_dir / f"daily_cycle_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    async def run_morning_briefing(self):
        """Run the morning briefing generation."""
        self.logger.info("Starting morning briefing generation")
        
        try:
            # Generate briefing using existing Phase 5 infrastructure
            briefing_result = await self.briefing_generator.generate_briefing(
                briefing_type="morning",
                include_metrics=True,
                include_priorities=True
            )
              # Log the outcome
            self.logger.info(f"Morning briefing completed: {briefing_result['status']}")
            
            # Send email briefing if enabled
            if self.config.get("email", {}).get("enabled", False):
                email_result = await self.email_integration.send_morning_briefing(briefing_result)
                self.logger.info(f"Email briefing result: {email_result['status']}")
            
            # Update dashboard if enabled
            if self.config["automation"]["auto_dashboard_update"]:
                await self._update_dashboard()
                
            return briefing_result
            
        except Exception as e:
            self.logger.error(f"Error in morning briefing: {e}")
            return {"status": "error", "message": str(e)}

    async def run_midday_check(self):
        """Run midday progress check."""
        self.logger.info("Starting midday progress check")
        
        try:
            # Calculate current metrics
            metrics = self.metrics_calculator.calculate_team_metrics()
            
            # Generate midday progress report
            report_result = self._run_cli_command([
                "python", "scripts/generate_task_report.py", "--mode", "progress"
            ])
            
            # Log progress status - handle both dict and object types
            if hasattr(metrics, 'completed_tasks'):
                completed_count = metrics.completed_tasks
            elif isinstance(metrics, dict):
                completed_count = metrics.get('completed_tasks', 0)
            else:
                completed_count = 0
                
            self.logger.info(f"Midday check completed - {completed_count} tasks completed today")
            return {
                "status": "success",
                "metrics": metrics,
                "report": report_result,
                "tasks_analyzed": getattr(metrics, 'total_tasks', 0) if hasattr(metrics, 'total_tasks') else 0,
                "issues_count": 0  # Add actual issue detection logic here
            }
            
        except Exception as e:
            self.logger.error(f"Error in midday check: {e}")
            return {"status": "error", "message": str(e)}
    
    async def run_end_of_day_report(self):
        """Run enhanced end-of-day reporting with comprehensive analysis."""
        self.logger.info("Starting enhanced end-of-day report generation")
        
        try:
            # Generate enhanced end-of-day report using new generator
            eod_result = await self.eod_report_generator.generate_eod_report(
                include_automation_stats=True,
                include_detailed_metrics=True,
                output_format="markdown"
            )
              # Update dashboard with daily summary
            await self._update_dashboard()
            
            # Generate traditional progress report for compatibility
            progress_result = self._run_cli_command([
                "python", "scripts/generate_task_report.py", "--day", str(self._get_current_day())
            ])
            
            self.logger.info(f"Enhanced end-of-day report completed: {eod_result.get('output_file')}")
            
            # Send email EOD report if enabled
            email_result = None
            if self.config.get("email", {}).get("enabled", False):
                email_result = await self.email_integration.send_eod_report(eod_result)
                self.logger.info(f"Email EOD report result: {email_result['status']}")
            
            return {
                "status": "success",
                "enhanced_eod_report": eod_result,
                "traditional_report": progress_result,
                "automation_stats": eod_result.get("automation_stats", {}),
                "sprint_health": eod_result.get("sprint_progress", {}).get("sprint_health", {}),
                "email_result": email_result
            }
            
        except Exception as e:
            self.logger.error(f"Error in enhanced end-of-day report: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _update_dashboard(self):
        """Update dashboard with latest metrics."""
        try:
            # Use existing dashboard update functionality
            result = self._run_cli_command([
                "python", "scripts/generate_task_report.py", "--update-dashboard"
            ])
            
            self.logger.info("Dashboard updated successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")
            return None
    
    def _run_cli_command(self, command: List[str]) -> Dict[str, Any]:
        """Run a CLI command and return the result."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                cwd=Path(__file__).parent.parent
            )
            
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),                "success": False
            }
    
    def schedule_daily_tasks(self):
        """Schedule daily automation tasks (deprecated - use schedule_enhanced_tasks)."""
        self.logger.warning("schedule_daily_tasks is deprecated, using schedule_enhanced_tasks")
        self.schedule_enhanced_tasks()
    
    def _run_async_task(self, coro):
        """Helper to run async tasks in sync context."""
        try:
            asyncio.run(coro())
        except Exception as e:
            self.logger.error(f"Error running async task: {e}")
    
    def start_scheduler(self):
        """Start the enhanced daily scheduler."""
        self.logger.info("Starting enhanced daily cycle scheduler")
        
        # Schedule all daily tasks with enhanced features
        self.schedule_enhanced_tasks()
        
        # Log schedule status
        schedule_status = self.get_schedule_status()
        self.logger.info(f"Scheduler started with {schedule_status['total_jobs']} jobs")
        
        # Main scheduler loop with enhanced error handling
        error_count = 0
        max_errors = self.config.get("monitoring", {}).get("error_threshold", 5)
        
        try:
            while True:
                try:
                    schedule.run_pending()
                    error_count = 0  # Reset error count on successful run
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    error_count += 1
                    self.logger.error(f"Scheduler error ({error_count}/{max_errors}): {e}")
                    
                    if error_count >= max_errors:
                        self.logger.critical("Maximum error threshold reached, stopping scheduler")
                        break
                    
                    time.sleep(30)  # Wait before retrying
                
        except KeyboardInterrupt:
            self.logger.info("Daily cycle scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Critical scheduler error: {e}")
        finally:
            # Cleanup
            schedule.clear()
            self.logger.info("Scheduler shutdown completed")
    
    async def run_manual_cycle(self, cycle_type: str = "full"):
        """Run a manual daily cycle for testing."""
        self.logger.info(f"Running manual {cycle_type} cycle")
        
        results = {}
        
        if cycle_type in ["full", "morning"]:
            results["morning_briefing"] = await self.run_morning_briefing()
        
        if cycle_type in ["full", "midday"]:
            results["midday_check"] = await self.run_midday_check()
        
        if cycle_type in ["full", "eod"]:
            results["end_of_day"] = await self.run_end_of_day_report()
        
        self.logger.info(f"Manual {cycle_type} cycle completed")
        return results
    
    def _get_current_day(self) -> int:
        """Calculate current day number based on project start date."""
        from datetime import date
        start_date = date(2025, 4, 1)  # Project start date
        current_date = date.today()
        return (current_date - start_date).days + 1

    async def run_health_check(self):
        """Run system health check."""
        self.logger.info("Starting system health check")
        
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "components": {},
                "overall_status": "healthy"
            }
            
            # Check execution monitor
            try:
                monitor_status = self.execution_monitor.get_system_status()
                health_status["components"]["execution_monitor"] = {
                    "status": "healthy" if monitor_status else "degraded",
                    "details": monitor_status
                }
            except Exception as e:
                health_status["components"]["execution_monitor"] = {
                    "status": "error",
                    "error": str(e)
                }
                health_status["overall_status"] = "degraded"
            
            # Check metrics calculator
            try:
                metrics = self.metrics_calculator.calculate_team_metrics()
                health_status["components"]["metrics_calculator"] = {
                    "status": "healthy",
                    "last_calculation": datetime.now().isoformat()
                }
            except Exception as e:
                health_status["components"]["metrics_calculator"] = {
                    "status": "error",
                    "error": str(e)
                }
                health_status["overall_status"] = "degraded"
            
            # Check dashboard API
            try:
                import requests
                response = requests.get(f"http://localhost:{self.config['dashboard']['api_port']}/api/system/health", timeout=5)
                if response.status_code == 200:
                    health_status["components"]["dashboard_api"] = {
                        "status": "healthy",
                        "response_time": response.elapsed.total_seconds()
                    }
                else:
                    health_status["components"]["dashboard_api"] = {
                        "status": "degraded",
                        "http_status": response.status_code
                    }
                    health_status["overall_status"] = "degraded"
            except Exception as e:
                health_status["components"]["dashboard_api"] = {
                    "status": "unavailable",
                    "error": str(e)
                }
                health_status["overall_status"] = "degraded"
            
            # Check email integration
            if self.config.get("email", {}).get("enabled", False):
                health_status["components"]["email_integration"] = {
                    "status": "configured" if self.email_integration.enabled else "disabled"
                }
            else:
                health_status["components"]["email_integration"] = {
                    "status": "disabled"
                }
            
            self.logger.info(f"Health check completed - Status: {health_status['overall_status']}")
            return health_status
            
        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }

    async def run_performance_check(self):
        """Run performance monitoring check."""
        self.logger.info("Starting performance check")
        
        try:
            performance_metrics = {
                "timestamp": datetime.now().isoformat(),
                "system_metrics": {},
                "process_metrics": {}
            }
            
            # System metrics
            import psutil
            performance_metrics["system_metrics"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('.').percent
            }
            
            # Process metrics
            process = psutil.Process()
            performance_metrics["process_metrics"] = {
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_percent": process.cpu_percent()
            }
            
            # Log directory size
            logs_dir = Path(self.config["paths"]["logs_dir"])
            if logs_dir.exists():
                total_size = sum(f.stat().st_size for f in logs_dir.rglob('*') if f.is_file())
                performance_metrics["logs_size_mb"] = total_size / 1024 / 1024
            
            self.logger.info("Performance check completed")
            return performance_metrics
            
        except Exception as e:
            self.logger.error(f"Error in performance check: {e}")
            return {"error": str(e)}

    def schedule_enhanced_tasks(self):
        """Schedule enhanced daily automation tasks with monitoring."""
        # Clear existing schedules
        schedule.clear()
        
        automation_config = self.config["automation"]
        
        if not automation_config.get("enabled", True):
            self.logger.info("Daily automation is disabled")
            return
        
        # Skip weekends if weekend_mode is disabled
        if not automation_config.get("weekend_mode", False):
            # Schedule only on weekdays
            schedule.every().monday.at(automation_config["morning_briefing_time"]).do(
                self._run_async_task, self.run_morning_briefing
            )
            schedule.every().tuesday.at(automation_config["morning_briefing_time"]).do(
                self._run_async_task, self.run_morning_briefing
            )
            schedule.every().wednesday.at(automation_config["morning_briefing_time"]).do(
                self._run_async_task, self.run_morning_briefing
            )
            schedule.every().thursday.at(automation_config["morning_briefing_time"]).do(
                self._run_async_task, self.run_morning_briefing
            )
            schedule.every().friday.at(automation_config["morning_briefing_time"]).do(
                self._run_async_task, self.run_morning_briefing
            )
            
            # Schedule EOD reports on weekdays
            schedule.every().monday.at(automation_config["eod_report_time"]).do(
                self._run_async_task, self.run_end_of_day_report
            )
            schedule.every().tuesday.at(automation_config["eod_report_time"]).do(
                self._run_async_task, self.run_end_of_day_report
            )
            schedule.every().wednesday.at(automation_config["eod_report_time"]).do(
                self._run_async_task, self.run_end_of_day_report
            )
            schedule.every().thursday.at(automation_config["eod_report_time"]).do(
                self._run_async_task, self.run_end_of_day_report
            )
            schedule.every().friday.at(automation_config["eod_report_time"]).do(
                self._run_async_task, self.run_end_of_day_report
            )
            
            # Schedule midday checks on weekdays if configured
            if "midday_check_time" in automation_config:
                for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                    getattr(schedule.every(), day).at(automation_config["midday_check_time"]).do(
                        self._run_async_task, self.run_midday_check
                    )
        else:
            # Schedule daily tasks including weekends
            schedule.every().day.at(automation_config["morning_briefing_time"]).do(
                self._run_async_task, self.run_morning_briefing
            )
            
            schedule.every().day.at(automation_config["eod_report_time"]).do(
                self._run_async_task, self.run_end_of_day_report
            )
            
            if "midday_check_time" in automation_config:
                schedule.every().day.at(automation_config["midday_check_time"]).do(
                    self._run_async_task, self.run_midday_check
                )
        
        # Schedule periodic health checks
        monitoring_config = self.config.get("monitoring", {})
        if monitoring_config.get("health_check_interval", 0) > 0:
            schedule.every(monitoring_config["health_check_interval"]).seconds.do(
                self._run_async_task, self.run_health_check
            )
        
        # Schedule periodic dashboard updates
        update_interval = self.config["dashboard"]["refresh_interval"]
        schedule.every(update_interval).minutes.do(
            self._run_async_task, self._update_dashboard
        )
        
        self.logger.info(f"Enhanced daily tasks scheduled: {len(schedule.get_jobs())} jobs")

    def get_schedule_status(self) -> Dict[str, Any]:
        """Get current schedule status."""
        jobs = schedule.get_jobs()
        
        return {
            "total_jobs": len(jobs),
            "jobs": [
                {
                    "job_func": str(job.job_func),
                    "next_run": job.next_run.isoformat() if job.next_run else None,
                    "interval": str(job.interval),
                    "unit": job.unit
                }
                for job in jobs
            ],
            "scheduler_running": True
        }

    async def run_emergency_stop(self):
        """Emergency stop procedure for the orchestrator."""
        self.logger.warning("Emergency stop initiated")
        
        try:
            # Clear all scheduled jobs
            schedule.clear()
            
            # Send emergency notification if email is enabled
            if self.config.get("email", {}).get("enabled", False):
                emergency_data = {
                    "timestamp": datetime.now().isoformat(),
                    "reason": "Emergency stop initiated",
                    "system_status": await self.run_health_check()
                }
                
                # Send to all recipients
                recipients = self.email_integration._get_all_recipients()
                await self.email_integration._send_email(
                    recipients=recipients,
                    subject="🚨 AI System Daily Orchestrator - Emergency Stop",
                    html_content=f"<h1>Emergency Stop</h1><p>Emergency stop initiated at {datetime.now()}</p>",
                    text_content=f"Emergency stop initiated at {datetime.now()}"
                )
            
            self.logger.info("Emergency stop completed")
            return {"status": "stopped", "timestamp": datetime.now().isoformat()}
            
        except Exception as e:
            self.logger.error(f"Error during emergency stop: {e}")
            return {"status": "error", "message": str(e)}

    # ...existing code...
def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Daily Cycle Automation Orchestrator")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--mode", choices=["schedule", "manual", "health", "status"], default="manual",
                       help="Run mode: schedule (continuous), manual (one-time), health (health check), status (show status)")
    parser.add_argument("--cycle", choices=["full", "morning", "midday", "eod", "health", "performance"], 
                       default="full", help="Cycle type for manual mode")
    parser.add_argument("--enable-weekend", action="store_true", 
                       help="Enable weekend mode for scheduling")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be scheduled without actually running")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = DailyCycleOrchestrator(config_path=args.config)
    
    # Override weekend mode if specified
    if args.enable_weekend:
        orchestrator.config["automation"]["weekend_mode"] = True
    
    if args.mode == "schedule":
        # Run continuous scheduler
        orchestrator.start_scheduler()
    elif args.mode == "health":
        # Run health check
        asyncio.run(orchestrator.run_health_check())
    elif args.mode == "status":
        # Show schedule status
        if args.dry_run:
            orchestrator.schedule_enhanced_tasks()
            status = orchestrator.get_schedule_status()
            print(f"Schedule Status: {status['total_jobs']} jobs configured")
            for job in status['jobs']:
                print(f"  - {job['job_func']} (next: {job['next_run']})")
        else:
            print("Use --dry-run to see schedule status without running")
    else:
        # Run manual cycle
        if args.cycle == "health":
            asyncio.run(orchestrator.run_health_check())
        elif args.cycle == "performance":
            asyncio.run(orchestrator.run_performance_check())
        else:
            asyncio.run(orchestrator.run_manual_cycle(cycle_type=args.cycle))


if __name__ == "__main__":
    main()
