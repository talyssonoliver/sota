
from src.infrastructure.utils.common_imports import Enum, dataclass, datetime
"""
Monitoring Service Interfaces

Abstract interfaces for monitoring, metrics collection, and health checking,
breaking dependency on specific monitoring implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable
# from dataclasses import dataclass  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SUMMARY = "summary"


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricPoint:
    """Single metric data point"""
    name: str
    value: Union[int, float]
    timestamp: datetime
    tags: Optional[Dict[str, str]] = None
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class HealthCheckResult:
    """Health check result"""
    name: str
    status: HealthStatus
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    checked_at: Optional[datetime] = None
    duration_ms: Optional[float] = None


@dataclass
class AlertRule:
    """Alert rule configuration"""
    id: str
    name: str
    metric_name: str
    condition: str  # e.g., "> 100", "< 0.5"
    severity: AlertSeverity
    threshold_duration: int = 60  # seconds
    enabled: bool = True
    tags: Optional[Dict[str, str]] = None


@dataclass
class Alert:
    """Alert instance"""
    id: str
    rule_id: str
    metric_name: str
    current_value: Union[int, float]
    threshold: Union[int, float]
    severity: AlertSeverity
    message: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    tags: Optional[Dict[str, str]] = None


class IMetricsCollector(ABC):
    """Interface for metrics collection"""
    
    @abstractmethod
    async def record_metric(self, metric: MetricPoint) -> bool:
        """Record a single metric point"""
        pass
    
    @abstractmethod
    async def record_batch(self, metrics: List[MetricPoint]) -> bool:
        """Record multiple metric points"""
        pass
    
    @abstractmethod
    async def increment_counter(self, name: str, value: int = 1, 
                               tags: Optional[Dict[str, str]] = None) -> bool:
        """Increment a counter metric"""
        pass
    
    @abstractmethod
    async def set_gauge(self, name: str, value: Union[int, float],
                       tags: Optional[Dict[str, str]] = None) -> bool:
        """Set a gauge metric"""
        pass
    
    @abstractmethod
    async def record_timer(self, name: str, duration_ms: float,
                          tags: Optional[Dict[str, str]] = None) -> bool:
        """Record a timer metric"""
        pass
    
    @abstractmethod
    async def record_histogram(self, name: str, value: Union[int, float],
                              tags: Optional[Dict[str, str]] = None) -> bool:
        """Record a histogram metric"""
        pass
    
    @abstractmethod
    async def get_metric_value(self, name: str, 
                              tags: Optional[Dict[str, str]] = None) -> Optional[Union[int, float]]:
        """Get current metric value"""
        pass
    
    @abstractmethod
    async def get_metrics_by_pattern(self, pattern: str) -> List[MetricPoint]:
        """Get metrics matching pattern"""
        pass
    
    @abstractmethod
    async def clear_metrics(self, pattern: Optional[str] = None) -> bool:
        """Clear metrics (optionally by pattern)"""
        pass
    
    @abstractmethod
    async def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format"""
        pass


class IExecutionMonitor(ABC):
    """Interface for execution monitoring"""
    
    @abstractmethod
    async def start_execution(self, execution_id: str, context: Dict[str, Any]) -> bool:
        """Start monitoring an execution"""
        pass
    
    @abstractmethod
    async def update_execution(self, execution_id: str, updates: Dict[str, Any]) -> bool:
        """Update execution status"""
        pass
    
    @abstractmethod
    async def complete_execution(self, execution_id: str, result: Dict[str, Any]) -> bool:
        """Mark execution as completed"""
        pass
    
    @abstractmethod
    async def fail_execution(self, execution_id: str, error: Dict[str, Any]) -> bool:
        """Mark execution as failed"""
        pass
    
    @abstractmethod
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        pass
    
    @abstractmethod
    async def get_active_executions(self) -> List[Dict[str, Any]]:
        """Get all active executions"""
        pass
    
    @abstractmethod
    async def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history"""
        pass
    
    @abstractmethod
    async def get_execution_metrics(self, execution_id: str) -> Dict[str, Any]:
        """Get metrics for specific execution"""
        pass
    
    @abstractmethod
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel running execution"""
        pass
    
    @abstractmethod
    async def cleanup_old_executions(self, older_than_days: int = 30) -> int:
        """Clean up old execution records"""
        pass


class IHealthChecker(ABC):
    """Interface for health checking"""
    
    @abstractmethod
    async def register_health_check(self, name: str, check_func: Callable[[], HealthCheckResult]) -> bool:
        """Register a health check"""
        pass
    
    @abstractmethod
    async def unregister_health_check(self, name: str) -> bool:
        """Unregister a health check"""
        pass
    
    @abstractmethod
    async def run_health_check(self, name: str) -> HealthCheckResult:
        """Run specific health check"""
        pass
    
    @abstractmethod
    async def run_all_health_checks(self) -> List[HealthCheckResult]:
        """Run all registered health checks"""
        pass
    
    @abstractmethod
    async def get_overall_health(self) -> HealthCheckResult:
        """Get overall system health"""
        pass
    
    @abstractmethod
    async def get_health_history(self, name: str, limit: int = 100) -> List[HealthCheckResult]:
        """Get health check history"""
        pass
    
    @abstractmethod
    async def set_health_check_interval(self, name: str, interval_seconds: int) -> bool:
        """Set health check interval"""
        pass
    
    @abstractmethod
    async def enable_health_check(self, name: str) -> bool:
        """Enable health check"""
        pass
    
    @abstractmethod
    async def disable_health_check(self, name: str) -> bool:
        """Disable health check"""
        pass
    
    @abstractmethod
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary statistics"""
        pass


class IPerformanceProfiler(ABC):
    """Interface for performance profiling"""
    
    @abstractmethod
    async def start_profile(self, profile_id: str, target: str) -> bool:
        """Start profiling a target"""
        pass
    
    @abstractmethod
    async def stop_profile(self, profile_id: str) -> Dict[str, Any]:
        """Stop profiling and return results"""
        pass
    
    @abstractmethod
    async def get_profile_data(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get profile data"""
        pass
    
    @abstractmethod
    async def analyze_performance(self, profile_id: str) -> Dict[str, Any]:
        """Analyze performance profile"""
        pass
    
    @abstractmethod
    async def get_performance_recommendations(self, profile_id: str) -> List[str]:
        """Get performance improvement recommendations"""
        pass
    
    @abstractmethod
    async def compare_profiles(self, profile_id1: str, profile_id2: str) -> Dict[str, Any]:
        """Compare two performance profiles"""
        pass
    
    @abstractmethod
    async def export_profile(self, profile_id: str, format_type: str = "json") -> str:
        """Export profile data"""
        pass


class IAlertManager(ABC):
    """Interface for alert management"""
    
    @abstractmethod
    async def create_alert_rule(self, rule: AlertRule) -> bool:
        """Create new alert rule"""
        pass
    
    @abstractmethod
    async def update_alert_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update alert rule"""
        pass
    
    @abstractmethod
    async def delete_alert_rule(self, rule_id: str) -> bool:
        """Delete alert rule"""
        pass
    
    @abstractmethod
    async def get_alert_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get alert rule"""
        pass
    
    @abstractmethod
    async def list_alert_rules(self) -> List[AlertRule]:
        """List all alert rules"""
        pass
    
    @abstractmethod
    async def trigger_alert(self, alert: Alert) -> bool:
        """Trigger an alert"""
        pass
    
    @abstractmethod
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        pass
    
    @abstractmethod
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        pass
    
    @abstractmethod
    async def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""
        pass
    
    @abstractmethod
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        pass
    
    @abstractmethod
    async def silence_alert(self, alert_id: str, duration_minutes: int) -> bool:
        """Silence an alert for specified duration"""
        pass
    
    @abstractmethod
    async def evaluate_alert_rules(self) -> List[Alert]:
        """Evaluate all alert rules and return triggered alerts"""
        pass


class ILogAggregator(ABC):
    """Interface for log aggregation and analysis"""
    
    @abstractmethod
    async def ingest_log(self, log_entry: Dict[str, Any]) -> bool:
        """Ingest a single log entry"""
        pass
    
    @abstractmethod
    async def ingest_batch(self, log_entries: List[Dict[str, Any]]) -> bool:
        """Ingest multiple log entries"""
        pass
    
    @abstractmethod
    async def search_logs(self, query: str, start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Search logs with query"""
        pass
    
    @abstractmethod
    async def get_log_stats(self, start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get log statistics"""
        pass
    
    @abstractmethod
    async def create_log_alert(self, pattern: str, threshold: int, 
                              window_minutes: int) -> str:
        """Create log-based alert"""
        pass
    
    @abstractmethod
    async def analyze_log_patterns(self, start_time: Optional[datetime] = None,
                                  end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze log patterns for anomalies"""
        pass
    
    @abstractmethod
    async def export_logs(self, query: str, format_type: str = "json") -> str:
        """Export logs matching query"""
        pass


class IResourceMonitor(ABC):
    """Interface for system resource monitoring"""
    
    @abstractmethod
    async def get_cpu_usage(self) -> Dict[str, float]:
        """Get CPU usage statistics"""
        pass
    
    @abstractmethod
    async def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        pass
    
    @abstractmethod
    async def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage statistics"""
        pass
    
    @abstractmethod
    async def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        pass
    
    @abstractmethod
    async def get_process_stats(self, process_id: Optional[int] = None) -> Dict[str, Any]:
        """Get process statistics"""
        pass
    
    @abstractmethod
    async def monitor_resource_usage(self, duration_seconds: int) -> Dict[str, Any]:
        """Monitor resource usage over time"""
        pass
    
    @abstractmethod
    async def set_resource_alerts(self, cpu_threshold: float, memory_threshold: float,
                                 disk_threshold: float) -> bool:
        """Set resource usage alert thresholds"""
        pass
    
    @abstractmethod
    async def get_resource_trends(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get resource usage trends"""
        pass


class IMonitoringDashboard(ABC):
    """Interface for monitoring dashboard"""
    
    @abstractmethod
    async def create_dashboard(self, dashboard_config: Dict[str, Any]) -> str:
        """Create monitoring dashboard"""
        pass
    
    @abstractmethod
    async def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> bool:
        """Update dashboard configuration"""
        pass
    
    @abstractmethod
    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get dashboard data"""
        pass
    
    @abstractmethod
    async def add_widget(self, dashboard_id: str, widget_config: Dict[str, Any]) -> str:
        """Add widget to dashboard"""
        pass
    
    @abstractmethod
    async def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """Remove widget from dashboard"""
        pass
    
    @abstractmethod
    async def export_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """Export dashboard configuration"""
        pass
    
    @abstractmethod
    async def import_dashboard(self, dashboard_config: Dict[str, Any]) -> str:
        """Import dashboard configuration"""
        pass