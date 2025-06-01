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
            
            # Log progress status
            self.logger.info(f"Midday check completed - {metrics.completed_tasks} tasks completed today")
            return {
                "status": "success",
                "metrics": metrics,
                "report": report_result
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
                "stderr": str(e),
                "success": False
            }
    
    def schedule_daily_tasks(self):
        """Schedule daily automation tasks."""
        # Clear existing schedules
        schedule.clear()
        
        # Schedule morning briefing
        schedule.every().day.at(self.config["automation"]["morning_briefing_time"]).do(
            self._run_async_task, self.run_morning_briefing
        )
        
        # Schedule end-of-day report
        schedule.every().day.at(self.config["automation"]["eod_report_time"]).do(
            self._run_async_task, self.run_end_of_day_report
        )
        
        # Schedule periodic dashboard updates
        update_interval = self.config["dashboard"]["refresh_interval"]
        schedule.every(update_interval).minutes.do(
            self._run_async_task, self._update_dashboard
        )
        
        self.logger.info(f"Daily tasks scheduled: {len(schedule.get_jobs())} jobs")
    
    def _run_async_task(self, coro):
        """Helper to run async tasks in sync context."""
        try:
            asyncio.run(coro())
        except Exception as e:
            self.logger.error(f"Error running async task: {e}")
    
    def start_scheduler(self):
        """Start the daily scheduler."""
        self.logger.info("Starting daily cycle scheduler")
        
        # Schedule all daily tasks
        self.schedule_daily_tasks()
        
        # Main scheduler loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("Daily cycle scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}")
    
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


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily Cycle Automation Orchestrator")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--mode", choices=["schedule", "manual"], default="manual",
                       help="Run mode: schedule (continuous) or manual (one-time)")
    parser.add_argument("--cycle", choices=["full", "morning", "midday", "eod"], 
                       default="full", help="Cycle type for manual mode")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = DailyCycleOrchestrator(config_path=args.config)
    
    if args.mode == "schedule":
        # Run continuous scheduler
        orchestrator.start_scheduler()
    else:
        # Run manual cycle
        asyncio.run(orchestrator.run_manual_cycle(cycle_type=args.cycle))


if __name__ == "__main__":
    main()
