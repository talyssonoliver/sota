#!/usr/bin/env python3
"""
Claude Migration Production Monitoring

Monitors the health, performance, and status of the Claude migration
in production environment with real-time alerting and metrics.
"""

import os
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
import asyncio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/claude_migration_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""
    component: str
    healthy: bool
    response_time_ms: float
    details: Dict[str, Any]
    timestamp: datetime


@dataclass
class MigrationMetrics:
    """Migration-specific metrics and KPIs."""
    claude_requests_count: int = 0
    openai_fallback_count: int = 0
    error_count: int = 0
    avg_response_time_ms: float = 0.0
    success_rate: float = 0.0
    cost_per_request: float = 0.0


class ClaudeMigrationMonitor:
    """Production monitoring for Claude migration."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = MigrationMetrics()
        self.health_history: List[HealthCheckResult] = []
        self.alert_thresholds = {
            'error_rate': 0.05,  # 5% error rate threshold
            'response_time': 5000,  # 5 second response time threshold
            'fallback_rate': 0.10,  # 10% fallback rate threshold
        }
    
    async def check_claude_api_health(self) -> HealthCheckResult:
        """Check Claude API health and connectivity."""
        start_time = time.time()
        
        try:
            # Import Claude integration
            from src.infrastructure.integrations.claude import ClaudeEmbeddings
            from src.infrastructure.integrations.claude.feature_flags import should_use_claude_chat
            
            # Test embeddings
            if should_use_claude_chat():
                embeddings = ClaudeEmbeddings()
                health_ok = embeddings.health_check()
                
                response_time = (time.time() - start_time) * 1000
                
                return HealthCheckResult(
                    component="claude_api",
                    healthy=health_ok,
                    response_time_ms=response_time,
                    details={
                        "embeddings_healthy": health_ok,
                        "api_key_configured": bool(os.getenv("CLAUDE_API_KEY")),
                        "feature_flags_enabled": should_use_claude_chat()
                    },
                    timestamp=datetime.now()
                )
            else:
                return HealthCheckResult(
                    component="claude_api",
                    healthy=True,
                    response_time_ms=0,
                    details={
                        "status": "disabled",
                        "reason": "Feature flags disabled"
                    },
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Claude API health check failed: {e}")
            
            return HealthCheckResult(
                component="claude_api",
                healthy=False,
                response_time_ms=response_time,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                timestamp=datetime.now()
            )
    
    async def check_feature_flags_status(self) -> HealthCheckResult:
        """Check feature flags configuration and status."""
        start_time = time.time()
        
        try:
            from src.infrastructure.integrations.claude.feature_flags import (
                MigrationFeatureFlags, 
                should_use_claude_embeddings,
                should_use_claude_chat
            )
            
            flags = MigrationFeatureFlags()
            validation_ok = flags.validate_configuration()
            enabled_components = flags.get_enabled_components()
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                component="feature_flags",
                healthy=validation_ok,
                response_time_ms=response_time,
                details={
                    "validation_passed": validation_ok,
                    "embeddings_enabled": should_use_claude_embeddings(),
                    "chat_enabled": should_use_claude_chat(),
                    "enabled_components": [comp.value for comp in enabled_components],
                    "emergency_disable": os.getenv("CLAUDE_DISABLE_ALL", "false").lower() == "true"
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Feature flags health check failed: {e}")
            
            return HealthCheckResult(
                component="feature_flags",
                healthy=False,
                response_time_ms=response_time,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                timestamp=datetime.now()
            )
    
    async def check_memory_engine_integration(self) -> HealthCheckResult:
        """Check memory engine Claude integration health."""
        start_time = time.time()
        
        try:
            from src.infrastructure.memory.engines.memory_engine import MemoryEngine
            from src.infrastructure.integrations.claude.feature_flags import should_use_claude_embeddings
            
            # Test memory engine initialization
            MemoryEngine()
            claude_enabled = should_use_claude_embeddings()
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                component="memory_engine",
                healthy=True,
                response_time_ms=response_time,
                details={
                    "claude_embeddings_enabled": claude_enabled,
                    "memory_engine_initialized": True,
                    "integration_working": True
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Memory engine health check failed: {e}")
            
            return HealthCheckResult(
                component="memory_engine",
                healthy=False,
                response_time_ms=response_time,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                timestamp=datetime.now()
            )
    
    async def run_comprehensive_health_check(self) -> List[HealthCheckResult]:
        """Run all health checks in parallel."""
        logger.info("Starting comprehensive health check...")
        
        tasks = [
            self.check_claude_api_health(),
            self.check_feature_flags_status(),
            self.check_memory_engine_integration()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Health check task failed: {result}")
                health_results.append(HealthCheckResult(
                    component="unknown",
                    healthy=False,
                    response_time_ms=0,
                    details={"error": str(result)},
                    timestamp=datetime.now()
                ))
            else:
                health_results.append(result)
        
        self.health_history.extend(health_results)
        
        # Keep only recent history (last 100 checks)
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
        
        return health_results
    
    def analyze_health_trends(self) -> Dict[str, Any]:
        """Analyze health check trends and patterns."""
        if not self.health_history:
            return {"status": "no_data"}
        
        recent_checks = [
            check for check in self.health_history 
            if check.timestamp > datetime.now() - timedelta(hours=1)
        ]
        
        if not recent_checks:
            return {"status": "no_recent_data"}
        
        # Calculate success rates by component
        component_stats = {}
        for check in recent_checks:
            if check.component not in component_stats:
                component_stats[check.component] = {"total": 0, "healthy": 0}
            
            component_stats[check.component]["total"] += 1
            if check.healthy:
                component_stats[check.component]["healthy"] += 1
        
        # Calculate success rates
        for component, stats in component_stats.items():
            stats["success_rate"] = stats["healthy"] / stats["total"]
        
        # Overall health score
        overall_healthy = sum(stats["healthy"] for stats in component_stats.values())
        overall_total = sum(stats["total"] for stats in component_stats.values())
        overall_success_rate = overall_healthy / overall_total if overall_total > 0 else 0
        
        return {
            "status": "analyzed",
            "overall_success_rate": overall_success_rate,
            "component_stats": component_stats,
            "recent_checks_count": len(recent_checks),
            "analysis_period_hours": 1
        }
    
    def check_alert_conditions(self, health_results: List[HealthCheckResult]) -> List[Dict[str, Any]]:
        """Check if any alert conditions are met."""
        alerts = []
        
        # Check for component failures
        for result in health_results:
            if not result.healthy:
                alerts.append({
                    "type": "component_failure",
                    "severity": "high",
                    "component": result.component,
                    "details": result.details,
                    "timestamp": result.timestamp.isoformat()
                })
        
        # Check response time thresholds
        for result in health_results:
            if result.response_time_ms > self.alert_thresholds['response_time']:
                alerts.append({
                    "type": "slow_response",
                    "severity": "medium",
                    "component": result.component,
                    "response_time_ms": result.response_time_ms,
                    "threshold_ms": self.alert_thresholds['response_time'],
                    "timestamp": result.timestamp.isoformat()
                })
        
        return alerts
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report."""
        uptime = datetime.now() - self.start_time
        health_trends = self.analyze_health_trends()
        
        recent_health = self.health_history[-10:] if self.health_history else []
        
        return {
            "monitor_status": {
                "uptime_seconds": uptime.total_seconds(),
                "start_time": self.start_time.isoformat(),
                "last_check": recent_health[-1].timestamp.isoformat() if recent_health else None
            },
            "migration_health": {
                "overall_status": "healthy" if all(check.healthy for check in recent_health) else "degraded",
                "recent_checks": len(recent_health),
                "health_trends": health_trends
            },
            "feature_flags": {
                "embeddings_enabled": os.getenv("CLAUDE_ENABLE_EMBEDDINGS", "false").lower() == "true",
                "chat_enabled": os.getenv("CLAUDE_ENABLE_CHAT", "false").lower() == "true",
                "all_enabled": os.getenv("CLAUDE_ENABLE_ALL", "false").lower() == "true",
                "emergency_disabled": os.getenv("CLAUDE_DISABLE_ALL", "false").lower() == "true"
            },
            "configuration": {
                "api_key_configured": bool(os.getenv("CLAUDE_API_KEY")),
                "model": os.getenv("CLAUDE_CHAT_MODEL", "claude-3-sonnet-20240229"),
                "temperature": float(os.getenv("CLAUDE_TEMPERATURE", "0.7")),
                "max_tokens": int(os.getenv("CLAUDE_MAX_TOKENS", "4096"))
            }
        }
    
    async def monitoring_loop(self, interval_seconds: int = 60):
        """Main monitoring loop."""
        logger.info(f"Starting Claude migration monitoring loop (interval: {interval_seconds}s)")
        
        while True:
            try:
                # Run health checks
                health_results = await self.run_comprehensive_health_check()
                
                # Check for alerts
                alerts = self.check_alert_conditions(health_results)
                
                # Log status
                healthy_count = sum(1 for result in health_results if result.healthy)
                total_count = len(health_results)
                
                logger.info(f"Health check complete: {healthy_count}/{total_count} components healthy")
                
                # Log alerts
                for alert in alerts:
                    logger.warning(f"ALERT: {alert['type']} - {alert['component']} - {alert.get('details', '')}")
                
                # Generate and save status report
                status_report = self.generate_status_report()
                
                # Save status report to file
                os.makedirs("logs", exist_ok=True)
                with open("logs/claude_migration_status.json", "w") as f:
                    json.dump(status_report, f, indent=2, default=str)
                
                # Wait for next iteration
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(interval_seconds)


async def main():
    """Main entry point for the monitoring script."""
    monitor = ClaudeMigrationMonitor()
    
    # Run one immediate health check
    logger.info("Running initial health check...")
    initial_results = await monitor.run_comprehensive_health_check()
    
    for result in initial_results:
        status = "✅" if result.healthy else "❌"
        logger.info(f"{status} {result.component}: {result.response_time_ms:.1f}ms")
    
    # Generate initial status report
    status_report = monitor.generate_status_report()
    print("\n📊 Claude Migration Status:")
    print(f"Overall Status: {status_report['migration_health']['overall_status']}")
    print(f"Embeddings Enabled: {status_report['feature_flags']['embeddings_enabled']}")
    print(f"Chat Enabled: {status_report['feature_flags']['chat_enabled']}")
    print(f"API Key Configured: {status_report['configuration']['api_key_configured']}")
    
    # Ask user if they want to start continuous monitoring
    try:
        start_monitoring = input("\nStart continuous monitoring? (y/N): ").lower().startswith('y')
        if start_monitoring:
            await monitor.monitoring_loop()
        else:
            logger.info("Single health check completed. Exiting.")
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")


if __name__ == "__main__":
    asyncio.run(main())