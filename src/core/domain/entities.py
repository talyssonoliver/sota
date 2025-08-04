
from src.infrastructure.utils.common_imports import (
    Any,
    Dict,
    Enum,
    List,
    Optional,
    dataclass,
    datetime,
    field,
    re,
    uuid
)
"""
Domain Entities

Core business entities that represent the main concepts in the AI agent system.
These entities encapsulate business logic and maintain domain invariants.
"""

# import uuid  # Consolidated to common_imports
from abc import ABC, abstractmethod
# from dataclasses import dataclass, field  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
# from typing import Any, Dict, List, Optional  # Consolidated to common_imports


class EntityStatus(Enum):
    """Common status values for domain entities"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(Enum):
    """Types of agents in the system"""

    COORDINATOR = "coordinator"
    TECHNICAL_LEAD = "technical"
    BACKEND_ENGINEER = "backend"
    FRONTEND_ENGINEER = "frontend"
    QA_ENGINEER = "qa"
    DOCUMENTATION = "documentation"
    PRODUCT_MANAGER = "product_manager"
    UX_DESIGNER = "ux"


class TaskPriority(Enum):
    """Task priority levels"""

    LOW = 1
    MEDIUM = 5
    HIGH = 7
    CRITICAL = 10


class DomainEntity(ABC):
    """Base class for all domain entities"""

    def __init__(self):
        self.id: str = str(uuid.uuid4())
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
        self.version: int = 1

    def update_timestamp(self):
        """Update the entity timestamp"""
        self.updated_at = datetime.now()
        self.version += 1

    @abstractmethod
    def validate(self) -> List[str]:
        """Validate entity business rules"""
        pass

    def is_valid(self) -> bool:
        """Check if entity is valid"""
        return len(self.validate()) == 0


@dataclass
class AgentEntity(DomainEntity):
    """Domain entity representing an AI agent"""

    agent_type: AgentType
    name: str
    description: str
    status: EntityStatus = field(default=EntityStatus.ACTIVE)
    capabilities: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    assigned_tools: List[str] = field(default_factory=list)
    context_domains: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        super().__init__()

    def validate(self) -> List[str]:
        """Validate agent business rules"""
        errors = []

        if not self.name or len(self.name.strip()) == 0:
            errors.append("Agent name cannot be empty")

        if not self.description or len(self.description.strip()) == 0:
            errors.append("Agent description cannot be empty")

        if len(self.capabilities) == 0:
            errors.append("Agent must have at least one capability")

        if (
            self.agent_type == AgentType.COORDINATOR
            and "coordination" not in self.capabilities
        ):
            errors.append("Coordinator agent must have coordination capability")

        if (
            self.agent_type == AgentType.QA_ENGINEER
            and "testing" not in self.capabilities
        ):
            errors.append("QA agent must have testing capability")

        return errors

    def assign_tool(self, tool_name: str) -> bool:
        """Assign a tool to this agent"""
        if tool_name not in self.assigned_tools:
            self.assigned_tools.append(tool_name)
            self.update_timestamp()
            return True
        return False

    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool from this agent"""
        if tool_name in self.assigned_tools:
            self.assigned_tools.remove(tool_name)
            self.update_timestamp()
            return True
        return False

    def add_capability(self, capability: str) -> bool:
        """Add a capability to this agent"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.update_timestamp()
            return True
        return False

    def update_performance_metric(self, metric_name: str, value: float):
        """Update a performance metric"""
        self.performance_metrics[metric_name] = value
        self.update_timestamp()

    def is_available(self) -> bool:
        """Check if agent is available for task assignment"""
        return self.status == EntityStatus.ACTIVE

    def can_handle_task(self, task_requirements: List[str]) -> bool:
        """Check if agent can handle a task based on requirements"""
        return all(req in self.capabilities for req in task_requirements)


@dataclass
class TaskEntity(DomainEntity):
    """Domain entity representing a task"""

    task_id: str
    title: str
    description: str
    task_type: str
    priority: TaskPriority = field(default=TaskPriority.MEDIUM)
    status: EntityStatus = field(default=EntityStatus.PENDING)
    assigned_agent_id: Optional[str] = field(default=None)
    dependencies: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    estimated_duration_minutes: Optional[int] = field(default=None)
    actual_duration_minutes: Optional[int] = field(default=None)
    started_at: Optional[datetime] = field(default=None)
    completed_at: Optional[datetime] = field(default=None)

    def __post_init__(self):
        super().__init__()

    def validate(self) -> List[str]:
        """Validate task business rules"""
        errors = []

        if not self.task_id or len(self.task_id.strip()) == 0:
            errors.append("Task ID cannot be empty")

        if not self.title or len(self.title.strip()) == 0:
            errors.append("Task title cannot be empty")

        if not self.description or len(self.description.strip()) == 0:
            errors.append("Task description cannot be empty")

        if not self.task_type or len(self.task_type.strip()) == 0:
            errors.append("Task type cannot be empty")

        # Validate task type format (e.g., BE-01, FE-02)
        if not self._is_valid_task_id_format(self.task_id):
            errors.append("Task ID must follow format: [PREFIX]-[NUMBER] (e.g., BE-01)")

        # Validate dependencies don't create cycles
        if self.task_id in self.dependencies:
            errors.append("Task cannot depend on itself")

        # Validate status transitions
        if self.status == EntityStatus.COMPLETED and not self.completed_at:
            errors.append("Completed tasks must have completion timestamp")

        if self.status == EntityStatus.ACTIVE and not self.started_at:
            errors.append("Active tasks must have start timestamp")

        return errors

    def start_execution(self, agent_id: str):
        """Start task execution"""
        if self.status != EntityStatus.PENDING:
            raise ValueError(f"Cannot start task in status: {self.status}")

        self.status = EntityStatus.ACTIVE
        self.assigned_agent_id = agent_id
        self.started_at = datetime.now()
        self.update_timestamp()

    def complete_execution(self, outputs: Dict[str, Any]):
        """Complete task execution"""
        if self.status != EntityStatus.ACTIVE:
            raise ValueError(f"Cannot complete task in status: {self.status}")

        self.status = EntityStatus.COMPLETED
        self.completed_at = datetime.now()
        self.outputs = outputs

        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds() / 60
            self.actual_duration_minutes = int(duration)

        self.update_timestamp()

    def fail_execution(self, error_message: str):
        """Mark task as failed"""
        self.status = EntityStatus.FAILED
        self.metadata["error_message"] = error_message
        self.metadata["failed_at"] = datetime.now().isoformat()
        self.update_timestamp()

    def cancel_execution(self, reason: str):
        """Cancel task execution"""
        self.status = EntityStatus.CANCELLED
        self.metadata["cancellation_reason"] = reason
        self.metadata["cancelled_at"] = datetime.now().isoformat()
        self.update_timestamp()

    def add_dependency(self, task_id: str):
        """Add a task dependency"""
        if task_id != self.task_id and task_id not in self.dependencies:
            self.dependencies.append(task_id)
            self.update_timestamp()

    def remove_dependency(self, task_id: str):
        """Remove a task dependency"""
        if task_id in self.dependencies:
            self.dependencies.remove(task_id)
            self.update_timestamp()

    def is_ready_for_execution(self, completed_tasks: List[str]) -> bool:
        """Check if task is ready for execution based on dependencies"""
        return self.status == EntityStatus.PENDING and all(
            dep in completed_tasks for dep in self.dependencies
        )

    def get_execution_duration(self) -> Optional[int]:
        """Get task execution duration in minutes"""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() / 60)
        return None

    def _is_valid_task_id_format(self, task_id: str) -> bool:
        """Validate task ID format"""
#         import re  # Consolidated to common_imports

        pattern = r"^[A-Z]+-\d+$"
        return bool(re.match(pattern, task_id))


@dataclass
class WorkflowEntity(DomainEntity):
    """Domain entity representing a workflow"""

    workflow_id: str
    name: str
    description: str
    status: EntityStatus = field(default=EntityStatus.PENDING)
    tasks: List[str] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = field(default=None)
    completed_at: Optional[datetime] = field(default=None)
    progress_percentage: float = field(default=0.0)

    def __post_init__(self):
        super().__init__()

    def validate(self) -> List[str]:
        """Validate workflow business rules"""
        errors = []

        if not self.workflow_id or len(self.workflow_id.strip()) == 0:
            errors.append("Workflow ID cannot be empty")

        if not self.name or len(self.name.strip()) == 0:
            errors.append("Workflow name cannot be empty")

        if len(self.tasks) == 0:
            errors.append("Workflow must contain at least one task")

        # Validate execution order contains all tasks
        if set(self.execution_order) != set(self.tasks):
            errors.append("Execution order must contain all workflow tasks")

        # Validate status transitions
        if self.status == EntityStatus.COMPLETED and self.progress_percentage != 100.0:
            errors.append("Completed workflows must have 100% progress")

        return errors

    def add_task(self, task_id: str, position: Optional[int] = None):
        """Add a task to the workflow"""
        if task_id not in self.tasks:
            self.tasks.append(task_id)

            if position is not None and position < len(self.execution_order):
                self.execution_order.insert(position, task_id)
            else:
                self.execution_order.append(task_id)

            self.update_timestamp()

    def remove_task(self, task_id: str):
        """Remove a task from the workflow"""
        if task_id in self.tasks:
            self.tasks.remove(task_id)
            if task_id in self.execution_order:
                self.execution_order.remove(task_id)
            self.update_timestamp()

    def start_execution(self):
        """Start workflow execution"""
        if self.status != EntityStatus.PENDING:
            raise ValueError(f"Cannot start workflow in status: {self.status}")

        self.status = EntityStatus.ACTIVE
        self.started_at = datetime.now()
        self.progress_percentage = 0.0
        self.update_timestamp()

    def complete_execution(self):
        """Complete workflow execution"""
        if self.status != EntityStatus.ACTIVE:
            raise ValueError(f"Cannot complete workflow in status: {self.status}")

        self.status = EntityStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress_percentage = 100.0
        self.update_timestamp()

    def update_progress(self, completed_tasks: List[str]):
        """Update workflow progress based on completed tasks"""
        if len(self.tasks) > 0:
            completed_workflow_tasks = [t for t in completed_tasks if t in self.tasks]
            self.progress_percentage = (
                len(completed_workflow_tasks) / len(self.tasks)
            ) * 100
            self.update_timestamp()

    def get_next_task(self, completed_tasks: List[str]) -> Optional[str]:
        """Get the next task that should be executed"""
        for task_id in self.execution_order:
            if task_id not in completed_tasks:
                return task_id
        return None

    def is_blocked(self, task_statuses: Dict[str, EntityStatus]) -> bool:
        """Check if workflow is blocked by failed tasks"""
        for task_id in self.tasks:
            if task_statuses.get(task_id) == EntityStatus.FAILED:
                return True
        return False

    def get_execution_duration(self) -> Optional[int]:
        """Get workflow execution duration in minutes"""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() / 60)
        return None
