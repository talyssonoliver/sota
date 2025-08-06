"""
Core Abstractions Module

Defines abstract interfaces for infrastructure services following
the Dependency Inversion Principle to decouple core business logic
from infrastructure concerns.
"""

from .memory_interfaces import IMemoryEngine, IMemoryProvider, ICacheManager
from .notification_interfaces import INotificationService, IEmailService
from .storage_interfaces import IDataRepository, ITaskRepository, IFileStorageService  
from .monitoring_interfaces import IExecutionMonitor, IMetricsCollector, IHealthChecker
from .workflow_interfaces import IWorkflowEngine, ITaskOrchestrator, IWorkflowState
from .external_interfaces import IExternalAPIClient, IWebhookManager

__all__ = [
    # Memory abstractions
    "IMemoryEngine",
    "IMemoryProvider", 
    "ICacheManager",
    
    # Notification abstractions
    "INotificationService",
    "IEmailService",
    
    # Storage abstractions
    "IDataRepository",
    "ITaskRepository", 
    "IFileStorageService",
    
    # Monitoring abstractions
    "IExecutionMonitor",
    "IMetricsCollector",
    "IHealthChecker",
    
    # Workflow abstractions
    "IWorkflowEngine",
    "ITaskOrchestrator",
    "IWorkflowState",
    
    # External service abstractions
    "IExternalAPIClient",
    "IWebhookManager"
]