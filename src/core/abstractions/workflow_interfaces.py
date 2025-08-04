
from src.infrastructure.utils.common_imports import Enum, dataclass, datetime
"""
Workflow Service Interfaces

Abstract interfaces for workflow orchestration and task management,
breaking dependency on specific LangGraph or workflow implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable, AsyncGenerator
# from dataclasses import dataclass  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskStatus(Enum):
    """Task execution status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class WorkflowTrigger(Enum):
    """Workflow trigger types"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    WEBHOOK = "webhook"
    API = "api"


@dataclass
class WorkflowContext:
    """Workflow execution context"""
    workflow_id: str
    execution_id: str
    variables: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    started_at: Optional[datetime] = None


@dataclass
class TaskDefinition:
    """Task definition"""
    id: str
    name: str
    description: Optional[str] = None
    handler: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    priority: TaskPriority = TaskPriority.NORMAL


@dataclass
class WorkflowDefinition:
    """Workflow definition"""
    id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    tasks: List[TaskDefinition] = None
    triggers: Optional[List[WorkflowTrigger]] = None
    timeout_seconds: Optional[int] = None
    variables: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []


@dataclass
class TaskExecution:
    """Task execution result"""
    task_id: str
    status: TaskStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    duration_ms: Optional[float] = None


@dataclass
class WorkflowExecution:
    """Workflow execution result"""
    workflow_id: str
    execution_id: str
    status: WorkflowStatus
    context: WorkflowContext
    task_executions: List[TaskExecution] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None
    
    def __post_init__(self):
        if self.task_executions is None:
            self.task_executions = []


class IWorkflowState(ABC):
    """Interface for workflow state management"""
    
    @abstractmethod
    async def save_state(self, execution_id: str, state: Dict[str, Any]) -> bool:
        """Save workflow state"""
        pass
    
    @abstractmethod
    async def load_state(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow state"""
        pass
    
    @abstractmethod
    async def update_state(self, execution_id: str, updates: Dict[str, Any]) -> bool:
        """Update workflow state"""
        pass
    
    @abstractmethod
    async def delete_state(self, execution_id: str) -> bool:
        """Delete workflow state"""
        pass
    
    @abstractmethod
    async def checkpoint_state(self, execution_id: str, checkpoint_name: str) -> bool:
        """Create state checkpoint"""
        pass
    
    @abstractmethod
    async def restore_checkpoint(self, execution_id: str, checkpoint_name: str) -> bool:
        """Restore from checkpoint"""
        pass
    
    @abstractmethod
    async def list_checkpoints(self, execution_id: str) -> List[str]:
        """List available checkpoints"""
        pass
    
    @abstractmethod
    async def cleanup_old_states(self, older_than_days: int = 7) -> int:
        """Clean up old workflow states"""
        pass


class ITaskHandler(ABC):
    """Interface for task execution handlers"""
    
    @abstractmethod
    async def execute(self, task_def: TaskDefinition, context: WorkflowContext) -> TaskExecution:
        """Execute a task"""
        pass
    
    @abstractmethod
    async def validate(self, task_def: TaskDefinition) -> Dict[str, Any]:
        """Validate task definition"""
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> List[str]:
        """Get handler capabilities"""
        pass
    
    @abstractmethod
    async def cleanup(self, execution_id: str) -> bool:
        """Cleanup task resources"""
        pass


class ITaskOrchestrator(ABC):
    """Interface for task orchestration"""
    
    @abstractmethod
    async def schedule_task(self, task_def: TaskDefinition, context: WorkflowContext) -> str:
        """Schedule a task for execution"""
        pass
    
    @abstractmethod
    async def execute_task(self, task_id: str) -> TaskExecution:
        """Execute a scheduled task"""
        pass
    
    @abstractmethod
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel task execution"""
        pass
    
    @abstractmethod
    async def retry_task(self, task_id: str) -> TaskExecution:
        """Retry failed task"""
        pass
    
    @abstractmethod
    async def get_task_status(self, task_id: str) -> Optional[TaskExecution]:
        """Get task execution status"""
        pass
    
    @abstractmethod
    async def get_pending_tasks(self) -> List[TaskExecution]:
        """Get pending tasks"""
        pass
    
    @abstractmethod
    async def get_running_tasks(self) -> List[TaskExecution]:
        """Get currently running tasks"""
        pass
    
    @abstractmethod
    async def register_handler(self, handler_name: str, handler: ITaskHandler) -> bool:
        """Register task handler"""
        pass
    
    @abstractmethod
    async def unregister_handler(self, handler_name: str) -> bool:
        """Unregister task handler"""
        pass
    
    @abstractmethod
    async def get_task_metrics(self) -> Dict[str, Any]:
        """Get task execution metrics"""
        pass


class IWorkflowEngine(ABC):
    """High-level interface for workflow engine"""
    
    @abstractmethod
    async def register_workflow(self, workflow_def: WorkflowDefinition) -> bool:
        """Register workflow definition"""
        pass
    
    @abstractmethod
    async def unregister_workflow(self, workflow_id: str) -> bool:
        """Unregister workflow definition"""
        pass
    
    @abstractmethod
    async def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow definition"""
        pass
    
    @abstractmethod
    async def list_workflows(self) -> List[WorkflowDefinition]:
        """List all registered workflows"""
        pass
    
    @abstractmethod
    async def start_workflow(self, workflow_id: str, context: WorkflowContext) -> str:
        """Start workflow execution"""
        pass
    
    @abstractmethod
    async def stop_workflow(self, execution_id: str) -> bool:
        """Stop workflow execution"""
        pass
    
    @abstractmethod
    async def pause_workflow(self, execution_id: str) -> bool:
        """Pause workflow execution"""
        pass
    
    @abstractmethod
    async def resume_workflow(self, execution_id: str) -> bool:
        """Resume paused workflow"""
        pass
    
    @abstractmethod
    async def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status"""
        pass
    
    @abstractmethod
    async def get_active_workflows(self) -> List[WorkflowExecution]:
        """Get active workflow executions"""
        pass
    
    @abstractmethod
    async def get_workflow_history(self, workflow_id: Optional[str] = None, 
                                  limit: int = 100) -> List[WorkflowExecution]:
        """Get workflow execution history"""
        pass
    
    @abstractmethod
    async def validate_workflow(self, workflow_def: WorkflowDefinition) -> Dict[str, Any]:
        """Validate workflow definition"""
        pass
    
    @abstractmethod
    async def get_workflow_metrics(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Get workflow execution metrics"""
        pass


class IWorkflowScheduler(ABC):
    """Interface for workflow scheduling"""
    
    @abstractmethod
    async def schedule_workflow(self, workflow_id: str, schedule: str, 
                               context: Optional[WorkflowContext] = None) -> str:
        """Schedule workflow execution"""
        pass
    
    @abstractmethod
    async def unschedule_workflow(self, schedule_id: str) -> bool:
        """Unschedule workflow"""
        pass
    
    @abstractmethod
    async def get_scheduled_workflows(self) -> List[Dict[str, Any]]:
        """Get all scheduled workflows"""
        pass
    
    @abstractmethod
    async def trigger_scheduled_workflow(self, schedule_id: str) -> str:
        """Manually trigger scheduled workflow"""
        pass
    
    @abstractmethod
    async def update_schedule(self, schedule_id: str, new_schedule: str) -> bool:
        """Update workflow schedule"""
        pass
    
    @abstractmethod
    async def pause_schedule(self, schedule_id: str) -> bool:
        """Pause workflow schedule"""
        pass
    
    @abstractmethod
    async def resume_schedule(self, schedule_id: str) -> bool:
        """Resume workflow schedule"""
        pass


class IWorkflowEventHandler(ABC):
    """Interface for workflow event handling"""
    
    @abstractmethod
    async def register_event_handler(self, event_type: str, handler: Callable) -> bool:
        """Register event handler"""
        pass
    
    @abstractmethod
    async def unregister_event_handler(self, event_type: str, handler: Callable) -> bool:
        """Unregister event handler"""
        pass
    
    @abstractmethod
    async def emit_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Emit workflow event"""
        pass
    
    @abstractmethod
    async def subscribe_to_events(self, event_types: List[str]) -> AsyncGenerator[Dict[str, Any], None]:
        """Subscribe to workflow events"""
        pass
    
    @abstractmethod
    async def get_event_history(self, event_type: Optional[str] = None, 
                               limit: int = 100) -> List[Dict[str, Any]]:
        """Get event history"""
        pass


class IWorkflowTriggerManager(ABC):
    """Interface for workflow trigger management"""
    
    @abstractmethod
    async def register_trigger(self, workflow_id: str, trigger_config: Dict[str, Any]) -> str:
        """Register workflow trigger"""
        pass
    
    @abstractmethod
    async def unregister_trigger(self, trigger_id: str) -> bool:
        """Unregister workflow trigger"""
        pass
    
    @abstractmethod
    async def enable_trigger(self, trigger_id: str) -> bool:
        """Enable workflow trigger"""
        pass
    
    @abstractmethod
    async def disable_trigger(self, trigger_id: str) -> bool:
        """Disable workflow trigger"""
        pass
    
    @abstractmethod
    async def test_trigger(self, trigger_id: str, test_data: Dict[str, Any]) -> bool:
        """Test workflow trigger"""
        pass
    
    @abstractmethod
    async def get_trigger_status(self, trigger_id: str) -> Optional[Dict[str, Any]]:
        """Get trigger status"""
        pass
    
    @abstractmethod
    async def list_triggers(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List workflow triggers"""
        pass


class IWorkflowValidator(ABC):
    """Interface for workflow validation"""
    
    @abstractmethod
    async def validate_syntax(self, workflow_def: WorkflowDefinition) -> Dict[str, Any]:
        """Validate workflow syntax"""
        pass
    
    @abstractmethod
    async def validate_dependencies(self, workflow_def: WorkflowDefinition) -> Dict[str, Any]:
        """Validate task dependencies"""
        pass
    
    @abstractmethod
    async def validate_handlers(self, workflow_def: WorkflowDefinition) -> Dict[str, Any]:
        """Validate task handlers exist"""
        pass
    
    @abstractmethod
    async def validate_permissions(self, workflow_def: WorkflowDefinition, 
                                  user_id: str) -> Dict[str, Any]:
        """Validate user permissions"""
        pass
    
    @abstractmethod
    async def validate_resources(self, workflow_def: WorkflowDefinition) -> Dict[str, Any]:
        """Validate required resources are available"""
        pass
    
    @abstractmethod
    async def simulate_execution(self, workflow_def: WorkflowDefinition, 
                                context: WorkflowContext) -> Dict[str, Any]:
        """Simulate workflow execution"""
        pass


class IWorkflowOptimizer(ABC):
    """Interface for workflow optimization"""
    
    @abstractmethod
    async def analyze_performance(self, workflow_id: str) -> Dict[str, Any]:
        """Analyze workflow performance"""
        pass
    
    @abstractmethod
    async def suggest_optimizations(self, workflow_id: str) -> List[str]:
        """Suggest workflow optimizations"""
        pass
    
    @abstractmethod
    async def optimize_task_order(self, workflow_def: WorkflowDefinition) -> WorkflowDefinition:
        """Optimize task execution order"""
        pass
    
    @abstractmethod
    async def detect_bottlenecks(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Detect workflow bottlenecks"""
        pass
    
    @abstractmethod
    async def estimate_execution_time(self, workflow_def: WorkflowDefinition) -> float:
        """Estimate workflow execution time"""
        pass
    
    @abstractmethod
    async def get_optimization_recommendations(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive optimization recommendations"""
        pass