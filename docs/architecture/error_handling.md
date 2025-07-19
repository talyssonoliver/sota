# orchestration/error_handling.py

## Classes
- **ErrorType** (line 17)
- **ErrorSeverity** (line 38)
- **RecoveryStrategy** (line 46)
- **RecoveryAttempt** (line 58)
- **ImpactAssessment** (line 68)
- **ErrorContext** (line 78)
  - Methods: to_dict
- **RetryPolicy** (line 132)
  - Methods: __init__, should_retry, get_delay
- **CircuitBreaker** (line 152)
  - Methods: __init__, call_allowed, record_success, record_failure
- **ErrorPropagationManager** (line 201)
  - Methods: __init__, _default_retry_policies, _default_recovery_strategies, classify_error, determine_severity, create_error_context, _assess_impact, determine_recovery_strategy, execute_recovery, _escalate_to_human, get_error_context, get_error_metrics

## Functions
- **handle_task_error(exception, task_id, agent_role, context_data, recovery_function)** (line 481)
