"""
Enhanced Error Handling for Multi-Agent Workflows
Implements comprehensive error propagation, recovery, and escalation strategies.
"""

try:
    import time
    from datetime import datetime, timedelta
except ImportError:
    pass
try:
    from enum import Enum
except ImportError:
    pass
try:
    from typing import Any, Callable, Dict, List, Optional
except ImportError:
    pass
try:
    from dataclasses import dataclass, field
except ImportError:
    pass
try:
    import logging
except ImportError:
    pass
logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Classification of error types for appropriate handling strategies"""

    # Technical Errors
    INFRASTRUCTURE = "infrastructure"
    RESOURCE = "resource"
    AUTHENTICATION = "authentication"
    TIMEOUT = "timeout"

    # Workflow Errors
    AGENT_FAILURE = "agent_failure"
    TASK_DEPENDENCY = "task_dependency"
    STATE_TRANSITION = "state_transition"
    DATA_VALIDATION = "data_validation"

    # Business Logic Errors
    TASK_EXECUTION = "task_execution"
    CONTEXT_ERROR = "context_error"
    OUTPUT_QUALITY = "output_quality"
    INTEGRATION = "integration"


class ErrorSeverity(str, Enum):
    """Error severity levels for escalation and response prioritization"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecoveryStrategy(str, Enum):
    """Available recovery strategies for different error types"""

    RETRY_EXPONENTIAL = "retry_exponential"
    FALLBACK_AGENT = "fallback_agent"
    DEGRADED_MODE = "degraded_mode"
    CIRCUIT_BREAKER = "circuit_breaker"
    HUMAN_ESCALATION = "human_escalation"
    TASK_SKIP = "task_skip"
    WORKFLOW_ABORT = "workflow_abort"


@dataclass
class RecoveryAttempt:
    """Record of a recovery attempt"""

    strategy: RecoveryStrategy
    timestamp: datetime
    success: bool
    details: str
    duration_seconds: float = 0.0


@dataclass
class ImpactAssessment:
    """Assessment of error impact on workflow"""

    affected_tasks: List[str] = field(default_factory=list)
    blocked_workflows: List[str] = field(default_factory=list)
    estimated_delay_minutes: int = 0
    severity_justification: str = ""
    recovery_feasible: bool = True


@dataclass
class ErrorContext:
    """Comprehensive error context for tracking and recovery"""

    error_id: str
    timestamp: datetime
    task_id: str
    agent_role: str
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    stack_trace: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    recovery_attempts: List[RecoveryAttempt] = field(default_factory=list)
    escalation_path: List[str] = field(default_factory=list)
    impact_assessment: Optional[ImpactAssessment] = None
    resolved: bool = False
    resolution_details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp.isoformat(),
            "task_id": self.task_id,
            "agent_role": self.agent_role,
            "error_type": self.error_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "stack_trace": self.stack_trace,
            "context_data": self.context_data,
            "retry_count": self.retry_count,
            "recovery_attempts": [
                {
                    "strategy": attempt.strategy.value,
                    "timestamp": attempt.timestamp.isoformat(),
                    "success": attempt.success,
                    "details": attempt.details,
                    "duration_seconds": attempt.duration_seconds,
                }
                for attempt in self.recovery_attempts
            ],
            "escalation_path": self.escalation_path,
            "impact_assessment": {
                "affected_tasks": (
                    self.impact_assessment.affected_tasks
                    if self.impact_assessment
                    else []
                ),
                "blocked_workflows": (
                    self.impact_assessment.blocked_workflows
                    if self.impact_assessment
                    else []
                ),
                "estimated_delay_minutes": (
                    self.impact_assessment.estimated_delay_minutes
                    if self.impact_assessment
                    else 0
                ),
                "severity_justification": (
                    self.impact_assessment.severity_justification
                    if self.impact_assessment
                    else ""
                ),
                "recovery_feasible": (
                    self.impact_assessment.recovery_feasible
                    if self.impact_assessment
                    else True
                ),
            },
            "resolved": self.resolved,
            "resolution_details": self.resolution_details,
        }


class RetryPolicy:
    """Configurable retry policy with exponential backoff"""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        backoff_multiplier: float = 2.0,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier

    def should_retry(self, retry_count: int) -> bool:
        """Check if task should be retried based on current retry count"""
        return retry_count < self.max_retries

    def get_delay(self, retry_count: int) -> float:
        """Calculate delay before next retry"""
        delay = self.base_delay * (self.backoff_multiplier**retry_count)
        return min(delay, self.max_delay)


class CircuitBreaker:
    """Circuit breaker pattern implementation for external service failures"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
        self.half_open_attempts = 0

    def call_allowed(self) -> bool:
        """Check if call is allowed based on circuit breaker state"""
        current_time = datetime.now()

        if self.state == "closed":
            return True
        elif self.state == "open":
            if current_time - self.last_failure_time > timedelta(
                seconds=self.recovery_timeout
            ):
                self.state = "half_open"
                self.half_open_attempts = 0
                return True
            return False
        elif self.state == "half_open":
            return self.half_open_attempts < self.half_open_max_calls

        return False

    def record_success(self):
        """Record successful call"""
        if self.state == "half_open":
            self.failure_count = 0
            self.state = "closed"
        self.half_open_attempts = 0

    def record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == "half_open":
            self.state = "open"
        elif self.failure_count >= self.failure_threshold:
            self.state = "open"


class ErrorPropagationManager:
    """Manages error propagation and recovery across multi-agent workflows"""

    def __init__(self):
        self.error_contexts: Dict[str, ErrorContext] = {}
        self.retry_policies: Dict[ErrorType, RetryPolicy] = (
            self._default_retry_policies()
        )
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.recovery_strategies: Dict[ErrorType, RecoveryStrategy] = (
            self._default_recovery_strategies()
        )

    def _default_retry_policies(self) -> Dict[ErrorType, RetryPolicy]:
        """Default retry policies for different error types"""
        return {
            ErrorType.INFRASTRUCTURE: RetryPolicy(
                max_retries=3, base_delay=1.0, max_delay=30.0
            ),
            ErrorType.RESOURCE: RetryPolicy(
                max_retries=2, base_delay=5.0, max_delay=60.0
            ),
            ErrorType.TIMEOUT: RetryPolicy(
                max_retries=3, base_delay=2.0, max_delay=30.0
            ),
            ErrorType.INTEGRATION: RetryPolicy(
                max_retries=2, base_delay=1.0, max_delay=15.0
            ),
            ErrorType.AGENT_FAILURE: RetryPolicy(
                max_retries=1, base_delay=0.5, max_delay=5.0
            ),
        }

    def _default_recovery_strategies(
        self,
    ) -> Dict[ErrorType, RecoveryStrategy]:
        """Default recovery strategies for different error types"""
        return {
            ErrorType.INFRASTRUCTURE: RecoveryStrategy.CIRCUIT_BREAKER,
            ErrorType.RESOURCE: RecoveryStrategy.RETRY_EXPONENTIAL,
            ErrorType.AUTHENTICATION: RecoveryStrategy.HUMAN_ESCALATION,
            ErrorType.TIMEOUT: RecoveryStrategy.RETRY_EXPONENTIAL,
            ErrorType.AGENT_FAILURE: RecoveryStrategy.FALLBACK_AGENT,
            ErrorType.TASK_DEPENDENCY: RecoveryStrategy.HUMAN_ESCALATION,
            ErrorType.STATE_TRANSITION: RecoveryStrategy.HUMAN_ESCALATION,
            ErrorType.DATA_VALIDATION: RecoveryStrategy.HUMAN_ESCALATION,
            ErrorType.TASK_EXECUTION: RecoveryStrategy.RETRY_EXPONENTIAL,
            ErrorType.CONTEXT_ERROR: RecoveryStrategy.DEGRADED_MODE,
            ErrorType.OUTPUT_QUALITY: RecoveryStrategy.RETRY_EXPONENTIAL,
            ErrorType.INTEGRATION: RecoveryStrategy.CIRCUIT_BREAKER,
        }

    def classify_error(
        self, exception: Exception, task_id: str, agent_role: str
    ) -> ErrorType:
        """Classify error based on exception type and context"""
        error_message = str(exception).lower()
        exception_type = type(exception).__name__.lower()

        # Infrastructure errors
        if any(
            keyword in error_message
            for keyword in ["connection", "network", "timeout", "unavailable"]
        ) or exception_type in ["connectionerror", "timeouterror"]:
            return ErrorType.INFRASTRUCTURE

        # Resource errors
        if any(
            keyword in error_message
            for keyword in ["memory", "disk", "rate limit", "quota"]
        ) or exception_type in ["memoryerror", "oserror"]:
            return ErrorType.RESOURCE

        # Authentication errors
        if any(
            keyword in error_message
            for keyword in ["auth", "permission", "unauthorized", "forbidden"]
        ) or exception_type in ["permissionerror"]:
            return ErrorType.AUTHENTICATION

        # Agent-specific errors
        if any(
            keyword in error_message for keyword in ["agent", "tool", "initialization"]
        ) or exception_type in ["attributeerror", "importerror", "modulenotfounderror"]:
            return ErrorType.AGENT_FAILURE

        # Default to task execution error
        return ErrorType.TASK_EXECUTION

    def determine_severity(
        self, error_type: ErrorType, task_id: str, agent_role: str
    ) -> ErrorSeverity:
        """Determine error severity based on type and context"""
        # Critical errors that halt system operation
        if error_type in [
            ErrorType.AUTHENTICATION,
            ErrorType.STATE_TRANSITION,
        ]:
            return ErrorSeverity.CRITICAL

        # High severity for infrastructure and agent failures
        if error_type in [
            ErrorType.INFRASTRUCTURE,
            ErrorType.AGENT_FAILURE,
            ErrorType.TASK_DEPENDENCY,
        ]:
            return ErrorSeverity.HIGH

        # Medium severity for most execution errors
        if error_type in [
            ErrorType.TASK_EXECUTION,
            ErrorType.INTEGRATION,
            ErrorType.RESOURCE,
        ]:
            return ErrorSeverity.MEDIUM

        # Low severity for quality and context issues
        return ErrorSeverity.LOW

    def create_error_context(
        self,
        exception: Exception,
        task_id: str,
        agent_role: str,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> ErrorContext:
        """Create comprehensive error context from exception"""
        import traceback
        import uuid

        error_id = f"ERR_{task_id}_{uuid.uuid4().hex[:8]}"
        error_type = self.classify_error(exception, task_id, agent_role)
        severity = self.determine_severity(error_type, task_id, agent_role)

        # Assess impact
        impact = self._assess_impact(error_type, severity, task_id, agent_role)

        error_context = ErrorContext(
            error_id=error_id,
            timestamp=datetime.now(),
            task_id=task_id,
            agent_role=agent_role,
            error_type=error_type,
            severity=severity,
            message=str(exception),
            stack_trace=traceback.format_exc(),
            context_data=context_data or {},
            impact_assessment=impact,
        )

        self.error_contexts[error_id] = error_context
        logger.error(
            f"Error context created: {error_id}",
            extra={
                "error_id": error_id,
                "task_id": task_id,
                "agent_role": agent_role,
                "error_type": error_type.value,
                "severity": severity.value,
            },
        )

        return error_context

    def _assess_impact(
        self,
        error_type: ErrorType,
        severity: ErrorSeverity,
        task_id: str,
        agent_role: str,
    ) -> ImpactAssessment:
        """Assess the impact of an error on the workflow"""
        impact = ImpactAssessment()

        # Estimate affected tasks based on error type and severity
        if severity == ErrorSeverity.CRITICAL:
            impact.affected_tasks = ["all_dependent_tasks"]
            impact.estimated_delay_minutes = 60
            impact.recovery_feasible = False
            impact.severity_justification = "Critical error affecting system operation"
        elif severity == ErrorSeverity.HIGH:
            impact.affected_tasks = [f"{task_id}_dependents"]
            impact.estimated_delay_minutes = 30
            impact.recovery_feasible = True
            impact.severity_justification = (
                "High impact error with automated recovery possible"
            )
        else:
            impact.estimated_delay_minutes = 5
            impact.recovery_feasible = True
            impact.severity_justification = (
                "Low impact error with quick recovery expected"
            )

        return impact

    def determine_recovery_strategy(
        self, error_context: ErrorContext
    ) -> RecoveryStrategy:
        """Determine appropriate recovery strategy for the error"""
        # Check if we've exceeded retry limits
        retry_policy = self.retry_policies.get(error_context.error_type)
        if retry_policy and not retry_policy.should_retry(error_context.retry_count):
            if error_context.severity in [
                ErrorSeverity.CRITICAL,
                ErrorSeverity.HIGH,
            ]:
                return RecoveryStrategy.HUMAN_ESCALATION
            else:
                return RecoveryStrategy.TASK_SKIP

        # Use default strategy for error type
        return self.recovery_strategies.get(
            error_context.error_type, RecoveryStrategy.HUMAN_ESCALATION
        )

    def execute_recovery(
        self,
        error_context: ErrorContext,
        recovery_function: Optional[Callable] = None,
    ) -> bool:
        """Execute recovery strategy for the error"""
        strategy = self.determine_recovery_strategy(error_context)
        start_time = datetime.now()
        success = False
        details = ""

        try:
            if strategy == RecoveryStrategy.RETRY_EXPONENTIAL:
                if recovery_function:
                    retry_policy = self.retry_policies.get(error_context.error_type)
                    if retry_policy and retry_policy.should_retry(
                        error_context.retry_count
                    ):
                        delay = retry_policy.get_delay(error_context.retry_count)
                        time.sleep(delay)
                        success = recovery_function()
                        details = f"Retry after {delay}s delay"
                        error_context.retry_count += 1

            elif strategy == RecoveryStrategy.CIRCUIT_BREAKER:
                service_name = (
                    f"{error_context.agent_role}_{error_context.error_type.value}"
                )
                circuit_breaker = self.circuit_breakers.get(service_name)
                if not circuit_breaker:
                    circuit_breaker = CircuitBreaker()
                    self.circuit_breakers[service_name] = circuit_breaker

                if circuit_breaker.call_allowed():
                    if recovery_function:
                        success = recovery_function()
                    if success:
                        circuit_breaker.record_success()
                        details = "Circuit breaker: call succeeded"
                    else:
                        circuit_breaker.record_failure()
                        details = "Circuit breaker: call failed"
                else:
                    details = "Circuit breaker: calls blocked"

            elif strategy == RecoveryStrategy.HUMAN_ESCALATION:
                success = self._escalate_to_human(error_context)
                details = "Escalated to human for resolution"

            elif strategy == RecoveryStrategy.DEGRADED_MODE:
                success = True  # Continue with degraded functionality
                details = "Continuing in degraded mode"

            elif strategy == RecoveryStrategy.TASK_SKIP:
                success = True  # Skip the failed task
                details = "Task skipped due to repeated failures"

            else:
                details = f"Unknown recovery strategy: {strategy}"

        except Exception as recovery_error:
            details = f"Recovery failed: {str(recovery_error)}"
            logger.error(f"Recovery execution failed: {recovery_error}")

        # Record recovery attempt
        duration = (datetime.now() - start_time).total_seconds()
        attempt = RecoveryAttempt(
            strategy=strategy,
            timestamp=start_time,
            success=success,
            details=details,
            duration_seconds=duration,
        )
        error_context.recovery_attempts.append(attempt)

        if success:
            error_context.resolved = True
            error_context.resolution_details = details
            logger.info(
                f"Recovery successful for error {error_context.error_id}: {details}"
            )
        else:
            logger.warning(
                f"Recovery failed for error {error_context.error_id}: {details}"
            )

        return success

    def _escalate_to_human(self, error_context: ErrorContext) -> bool:
        """Escalate error to human administrators"""
        # In a real implementation, this would:
        # 1. Create human review task
        # 2. Send notifications (email, Slack, etc.)
        # 3. Update task status to require human intervention

        error_context.escalation_path.append("human_admin")
        logger.critical(
            f"Error escalated to human: {error_context.error_id}",
            extra={
                "error_id": error_context.error_id,
                "task_id": error_context.task_id,
                "severity": error_context.severity.value,
            },
        )

        # For now, return True to indicate escalation was successful
        return True

    def get_error_context(self, error_id: str) -> Optional[ErrorContext]:
        """Retrieve error context by ID"""
        return self.error_contexts.get(error_id)

    def get_error_metrics(self) -> Dict[str, Any]:
        """Get error handling metrics for monitoring"""
        total_errors = len(self.error_contexts)
        resolved_errors = sum(1 for ctx in self.error_contexts.values() if ctx.resolved)
        escalated_errors = sum(
            1
            for ctx in self.error_contexts.values()
            if "human_admin" in ctx.escalation_path
        )

        error_by_type = {}
        error_by_severity = {}

        for ctx in self.error_contexts.values():
            error_by_type[ctx.error_type.value] = (
                error_by_type.get(ctx.error_type.value, 0) + 1
            )
            error_by_severity[ctx.severity.value] = (
                error_by_severity.get(ctx.severity.value, 0) + 1
            )

        return {
            "total_errors": total_errors,
            "resolved_errors": resolved_errors,
            "escalated_errors": escalated_errors,
            "resolution_rate": (
                resolved_errors / total_errors if total_errors > 0 else 0
            ),
            "escalation_rate": (
                escalated_errors / total_errors if total_errors > 0 else 0
            ),
            "errors_by_type": error_by_type,
            "errors_by_severity": error_by_severity,
            "circuit_breaker_states": {
                name: cb.state for name, cb in self.circuit_breakers.items()
            },
        }


# Global error propagation manager instance
error_manager = ErrorPropagationManager()


def handle_task_error(
    exception: Exception,
    task_id: str,
    agent_role: str,
    context_data: Optional[Dict[str, Any]] = None,
    recovery_function: Optional[Callable] = None,
) -> ErrorContext:
    """
    Handle task error with comprehensive error propagation and recovery.

    Args:
        exception: The exception that occurred
        task_id: ID of the task that failed
        agent_role: Role of the agent that encountered the error
        context_data: Additional context data
        recovery_function: Optional function to call for recovery

    Returns:
        ErrorContext object with error details and recovery status
    """
    error_context = error_manager.create_error_context(
        exception, task_id, agent_role, context_data
    )

    # Attempt recovery
    if recovery_function:
        error_manager.execute_recovery(error_context, recovery_function)

    return error_context
