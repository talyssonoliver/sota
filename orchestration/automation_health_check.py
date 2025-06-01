#!/usr/bin/env python3
"""
Automation Health Check - Phase 6 Enhancement

Comprehensive health monitoring for the daily automation system,
providing diagnostics and system status validation.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.completion_metrics import CompletionMetricsCalculator
from utils.execution_monitor import ExecutionMonitor
from orchestration.daily_cycle import DailyCycleOrchestrator


class AutomationHealthChecker:
    """
    Health monitoring system for daily automation infrastructure.
    """
    
    def __init__(self):
        """Initialize the health checker."""
        self.logger = logging.getLogger(__name__)
        self.metrics_calculator = CompletionMetricsCalculator()
        self.execution_monitor = ExecutionMonitor()
        
        # Health check results
        self.health_status = {
            "overall": "unknown",
            "components": {},
            "last_check": None,
            "recommendations": []
        }
    
    async def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """
        Run a comprehensive health check of the automation system.
        
        Returns:
            Dictionary with detailed health status
        """
        self.logger.info("Starting comprehensive automation health check")
        
        try:
            # Initialize results
            results = {
                "timestamp": datetime.now().isoformat(),
                "components": {},
                "overall_status": "healthy",
                "issues": [],
                "recommendations": []
            }
            
            # Check core components
            results["components"]["daily_cycle"] = await self._check_daily_cycle()
            results["components"]["metrics_engine"] = self._check_metrics_engine()
            results["components"]["execution_monitor"] = self._check_execution_monitor()
            results["components"]["dashboard_api"] = await self._check_dashboard_api()
            results["components"]["reporting_system"] = self._check_reporting_system()
            results["components"]["file_system"] = self._check_file_system()
            results["components"]["email_system"] = await self._check_email_system()
            
            # Analyze overall health
            results = self._analyze_overall_health(results)
            
            # Generate recommendations
            results["recommendations"] = self._generate_recommendations(results)
            
            self.health_status = results
            self.logger.info(f"Health check completed - Status: {results['overall_status']}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e),
                "components": {},
                "issues": [f"Health check failed: {e}"],
                "recommendations": ["Investigate health check system failure"]
            }
    
    async def _check_daily_cycle(self) -> Dict[str, Any]:
        """Check daily cycle orchestrator health."""
        try:
            # Test daily cycle initialization
            orchestrator = DailyCycleOrchestrator()
            
            # Check configuration
            config_valid = orchestrator.config is not None
            
            # Check scheduled tasks (would be running in production)
            schedule_status = "configured"  # Simplified for testing
            
            return {
                "status": "healthy" if config_valid else "warning",
                "config_loaded": config_valid,
                "schedule_status": schedule_status,
                "last_run": "manual_test_only",
                "issues": [] if config_valid else ["Configuration not loaded properly"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "issues": [f"Daily cycle check failed: {e}"]
            }
    def _check_metrics_engine(self) -> Dict[str, Any]:
        """Check metrics calculation engine."""
        try:
            # Test metrics calculation
            metrics = self.metrics_calculator.calculate_team_metrics()
            
            # Validate metrics structure (metrics is a dict, not an object)
            required_fields = ['total_tasks', 'completed_tasks', 'completion_rate']
            has_required = all(field in metrics for field in required_fields)
            
            return {
                "status": "healthy" if has_required else "warning",
                "metrics_available": has_required,
                "total_tasks": metrics.get('total_tasks', 0),
                "completion_rate": metrics.get('completion_rate', 0),
                "issues": [] if has_required else ["Missing required metrics fields"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "issues": [f"Metrics engine check failed: {e}"]
            }
    
    def _check_execution_monitor(self) -> Dict[str, Any]:
        """Check execution monitoring system."""
        try:
            # Test execution monitor
            stats = self.execution_monitor.get_execution_stats()
              # Check if logs directory exists
            logs_exist = self.execution_monitor.logs_dir.exists()
            
            return {
                "status": "healthy",
                "logs_directory": str(self.execution_monitor.logs_dir),
                "logs_exist": logs_exist,
                "total_executions": stats.get('total_executions', 0),
                "success_rate": stats.get('success_rate', 0),
                "issues": []
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "issues": [f"Execution monitor check failed: {e}"]
            }
    async def _check_dashboard_api(self) -> Dict[str, Any]:
        """Check dashboard API server status."""
        try:
            # Try to connect to dashboard API
            response = requests.get("http://localhost:5000/health", timeout=5)
            api_running = response.status_code == 200

            return {
                "status": "healthy" if api_running else "warning",
                "api_running": api_running,
                "api_url": "http://localhost:5000",
                "response_code": response.status_code if api_running else None,
                "issues": [] if api_running else ["Dashboard API not responding"]
            }
        except requests.exceptions.RequestException:
            return {
                "status": "warning",
                "api_running": False,
                "api_url": "http://localhost:5000",
                "issues": ["Dashboard API not accessible - may not be running"]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "issues": [f"Dashboard API check failed: {e}"]
            }
    
    def _check_reporting_system(self) -> Dict[str, Any]:
        """Check reporting system health."""
        try:
            # Check critical directories
            reports_dir = Path("docs/sprint/daily_reports")
            briefings_dir = Path("docs/sprint/briefings")
            
            reports_exist = reports_dir.exists()
            briefings_exist = briefings_dir.exists()
            
            # Count recent files
            recent_reports = 0
            recent_briefings = 0
            
            if reports_exist:
                cutoff = datetime.now() - timedelta(days=7)
                recent_reports = len([
                    f for f in reports_dir.glob("*.md*") 
                    if f.stat().st_mtime > cutoff.timestamp()
                ])
            
            if briefings_exist:
                cutoff = datetime.now() - timedelta(days=7)
                recent_briefings = len([
                    f for f in briefings_dir.glob("*.md*")
                    if f.stat().st_mtime > cutoff.timestamp()
                ])
            
            return {
                "status": "healthy" if (reports_exist and briefings_exist) else "warning",
                "reports_directory": str(reports_dir),
                "briefings_directory": str(briefings_dir),
                "reports_exist": reports_exist,
                "briefings_exist": briefings_exist,
                "recent_reports": recent_reports,
                "recent_briefings": recent_briefings,
                "issues": []
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "issues": [f"Reporting system check failed: {e}"]
            }
    
    def _check_file_system(self) -> Dict[str, Any]:
        """Check critical file system components."""
        try:
            critical_paths = [
                "config/daily_cycle.json",
                "tasks/tasks.json",
                "dashboard/completion_metrics.json",
                "logs",
                "reports"
            ]
            
            path_status = {}
            all_exist = True
            
            for path_str in critical_paths:
                path = Path(path_str)
                exists = path.exists()
                path_status[path_str] = {
                    "exists": exists,
                    "type": "directory" if path.is_dir() else "file",
                    "size": path.stat().st_size if exists and path.is_file() else None
                }
                if not exists:
                    all_exist = False
            
            return {
                "status": "healthy" if all_exist else "warning",
                "paths": path_status,
                "all_critical_paths_exist": all_exist,
                "issues": [f"Missing: {p}" for p, s in path_status.items() if not s["exists"]]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "issues": [f"File system check failed: {e}"]
            }
    
    async def _check_email_system(self) -> Dict[str, Any]:
        """Check email integration system."""
        try:
            # Check email configuration
            config_path = "config/daily_cycle.json"
            config_exists = Path(config_path).exists()
            
            email_configured = False
            smtp_settings = {}
            
            if config_exists:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    email_config = config.get('email', {})
                    email_configured = email_config.get('enabled', False)
                    smtp_settings = {
                        "server": email_config.get('smtp_server', ''),
                        "port": email_config.get('smtp_port', 0),
                        "tls": email_config.get('use_tls', False)
                    }
            
            return {
                "status": "healthy" if config_exists else "warning",
                "config_exists": config_exists,
                "email_configured": email_configured,
                "smtp_settings": smtp_settings,
                "issues": [] if config_exists else ["Email configuration not found"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "issues": [f"Email system check failed: {e}"]
            }
    
    def _analyze_overall_health(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall system health based on component checks."""
        component_statuses = [
            comp["status"] for comp in results["components"].values()
        ]
        
        # Count status types
        error_count = component_statuses.count("error")
        warning_count = component_statuses.count("warning")
        healthy_count = component_statuses.count("healthy")
        
        # Determine overall status
        if error_count > 0:
            results["overall_status"] = "error"
        elif warning_count > 2:
            results["overall_status"] = "degraded"
        elif warning_count > 0:
            results["overall_status"] = "warning"
        else:
            results["overall_status"] = "healthy"
        
        # Collect all issues
        all_issues = []
        for comp_name, comp_data in results["components"].items():
            if "issues" in comp_data:
                for issue in comp_data["issues"]:
                    all_issues.append(f"{comp_name}: {issue}")
        
        results["issues"] = all_issues
        results["component_summary"] = {
            "total": len(component_statuses),
            "healthy": healthy_count,
            "warning": warning_count,
            "error": error_count
        }
        
        return results
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on health check results."""
        recommendations = []
        
        # Analyze specific issues
        for comp_name, comp_data in results["components"].items():
            if comp_data["status"] == "error":
                recommendations.append(f"🔥 CRITICAL: Fix {comp_name} immediately")
            elif comp_data["status"] == "warning":
                recommendations.append(f"⚠️  WARNING: Review {comp_name} configuration")
        
        # General recommendations
        if results["overall_status"] == "healthy":
            recommendations.append("✅ System is healthy - maintain current monitoring")
        elif results["overall_status"] == "warning":
            recommendations.append("⚠️  Address warnings to maintain system stability")
        elif results["overall_status"] == "degraded":
            recommendations.append("🔧 Multiple issues detected - prioritize fixes")
        elif results["overall_status"] == "error":
            recommendations.append("🚨 URGENT: Critical issues require immediate attention")
        
        return recommendations


async def main():
    """Main entry point for health check."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automation Health Check")
    parser.add_argument("--output", choices=["console", "json", "file"], 
                       default="console", help="Output format")
    parser.add_argument("--save", help="Save results to file")
    
    args = parser.parse_args()
    
    # Initialize health checker
    checker = AutomationHealthChecker()
    
    # Run health check
    results = await checker.run_comprehensive_health_check()
    
    # Output results
    if args.output == "json":
        print(json.dumps(results, indent=2))
    elif args.output == "file" or args.save:
        output_file = args.save or f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Health check results saved to {output_file}")
    else:
        # Console output
        print(f"\n🏥 AUTOMATION HEALTH CHECK - {results['timestamp']}")
        print("=" * 60)
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(f"Components Checked: {results['component_summary']['total']}")
        print(f"  ✅ Healthy: {results['component_summary']['healthy']}")
        print(f"  ⚠️  Warnings: {results['component_summary']['warning']}")
        print(f"  ❌ Errors: {results['component_summary']['error']}")
        
        if results['issues']:
            print(f"\n🔍 ISSUES DETECTED ({len(results['issues'])}):")
            for issue in results['issues']:
                print(f"  • {issue}")
        
        if results['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in results['recommendations']:
                print(f"  • {rec}")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
