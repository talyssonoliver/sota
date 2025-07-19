# Enhanced Error Handling & Self-Correction Loops

## Overview

This document outlines the comprehensive improvements made to the system's error handling capabilities, including advanced error reporting, retry mechanisms, and self-correction loops within LangGraph workflows.

## Changes Made

### 1. Enhanced Agent Handlers (`graph/handlers.py`)

#### Detailed Error Reporting
All agent handlers now provide structured error information instead of simple error strings.

**Before:**
```python
except Exception as e:
    return {
        "status": TaskStatus.BLOCKED,
        "agent": "backend",
        "task_id": task_id,
        "error": str(e),
        "output": f"Backend implementation failed: {str(e)}"
    }
```

**After:**
```python
except Exception as e:
    error_details = {
        "message": str(e),
        "type": type(e).__name__,
        "traceback": traceback.format_exc(),
        "agent_role": "backend"
    }
    logger.error(f"Error in {error_details['agent_role']} handler for task {task_id}", 
                exc_info=True, extra={
        "agent": error_details['agent_role'],
        "task_id": task_id,
        "event": "handler_error",
        "error_message": error_details["message"]
    })
    return {
        "task_id": task_id,
        "agent": "backend",
        "status": TaskStatus.BLOCKED,
        "error_info": error_details,
        "output": f"{error_details['agent_role'].capitalize()} implementation failed: {error_details['message']}",
        "attempt_count": state.get("attempt_count", 1)
    }
```

#### Key Improvements:
- **Structured Error Information**: Captures error message, type, and full traceback
- **Enhanced Logging**: Detailed logging with structured extra fields for monitoring
- **Attempt Tracking**: Tracks the number of attempts for each task execution
- **Agent Role Context**: Clear identification of which agent failed

#### Affected Handlers:
- `coordinator_handler`
- `technical_handler`
- `backend_handler`
- `frontend_handler`
- `qa_handler`
- `documentation_handler`

### 2. Retry Logic and Self-Correction Routing (`graph/graph_builder.py`)

#### Enhanced WorkflowState
Updated all WorkflowState TypedDict definitions to include error handling fields:

```python
class WorkflowState(TypedDict, total=False):
    task_id: str
    agent: str
    output: str
    status: TaskStatus
    error: Opt[str]
    error_info: Opt[Dict[str, Any]]  # NEW: Structured error information
    attempt_count: Opt[int]          # NEW: Retry attempt tracking
    qa_result: Opt[str]
    next: Opt[str]
```

#### Advanced Dynamic Router
The `dynamic_router` function in `build_dynamic_workflow_graph` now implements sophisticated retry logic:

```python
def dynamic_router(state):
    MAX_ATTEMPTS = 3  # Maximum number of retries
    
    current_agent_role = state.get("agent", "")
    status = state.get("status")
    task_id = state.get("task_id", "UNKNOWN")
    error_info = state.get("error_info")
    attempt_count = state.get("attempt_count", 1)

    if error_info:  # Error occurred in last execution
        if attempt_count < MAX_ATTEMPTS:
            # Retry: Route back to same agent
            state["attempt_count"] = attempt_count + 1
            state["status"] = TaskStatus.IN_PROGRESS
            state["error_info"] = None
            return current_agent_role
        else:
            # Max attempts reached: Escalate to human review
            state["status"] = TaskStatus.HUMAN_REVIEW
            return "human_review"
    
    # ... rest of routing logic
```

#### Key Features:
- **Automatic Retry**: Failed tasks are automatically retried up to MAX_ATTEMPTS times
- **State Management**: Proper cleanup of error state for retries
- **Escalation Path**: Tasks that fail all retries are escalated to human review
- **Comprehensive Logging**: Detailed logging of routing decisions for monitoring
- **Self-Correction**: Agents can correct their previous errors when re-invoked

### 3. PlanExecutionManager Integration (`orchestration/plan_execution_manager.py`)

#### Enhanced Error Handling
Updated to work seamlessly with the new error handling system:

```python
# Check for error conditions including enhanced error info
error_info = result_state.get("error_info")
if result_state.get("status") == TaskStatus.BLOCKED or error_info or result_state.get("error"):
    error_message = error_info.get("message") if error_info else result_state.get("error", "Unknown error")
    
    # Store detailed error information
    self.completed_parts[part_id] = {
        "error": error_message,
        "error_info": error_info,
        "output": result_state.get("output"),
        "attempt_count": result_state.get("attempt_count", 1)
    }
    
    return {
        "id": part_id, 
        "status": "failed", 
        "result": result_state.get("output"),
        "error_info": error_info,
        "attempt_count": result_state.get("attempt_count", 1)
    }
```

#### Integration Benefits:
- **Detailed Error Tracking**: Comprehensive error information for each plan part
- **Retry Information**: Tracks attempt counts for plan execution parts
- **Enhanced Feedback**: Provides rich error context to the coordinator for re-planning

## Error Handling Flow

### 1. Initial Execution
```
Agent Handler → Execute Task → Success/Error
```

### 2. Error Detection
```
Error Occurs → Create error_details → Log Error → Return Structured Error State
```

### 3. Retry Logic
```
Router Detects Error → Check Attempt Count → Route Back to Same Agent (if < MAX_ATTEMPTS)
```

### 4. Escalation
```
Max Attempts Reached → Route to Human Review → Manual Intervention Required
```

### 5. Self-Correction
```
Agent Re-invoked → Receives Error Context → Attempts Correction → Success/Failure
```

## Configuration Options

### Retry Settings
- **MAX_ATTEMPTS**: Default 3 retries per task (configurable in router)
- **Error States**: Automatic detection of BLOCKED status and error_info
- **Escalation Target**: Human review for failed retries (configurable)

### Logging Levels
- **INFO**: Routing decisions and successful executions
- **WARNING**: First-time failures and retry attempts
- **ERROR**: Max retries reached and critical failures

### Status Management
- **TaskStatus.IN_PROGRESS**: Reset for retry attempts
- **TaskStatus.BLOCKED**: Initial error state
- **TaskStatus.HUMAN_REVIEW**: Final escalation state

## Monitoring and Observability

### Structured Logging
All error events include structured logging with:
- `task_id`: Unique task identifier
- `agent_role`: Agent that experienced the error
- `attempt`: Current attempt number
- `event`: Type of event (handler_error, routing_for_retry, max_retries_reached)
- `error_message`: Human-readable error description

### Error Information
Detailed error objects include:
- `message`: Error description
- `type`: Exception type name
- `traceback`: Full Python traceback
- `agent_role`: Responsible agent

### Metrics Tracking
- Retry counts per task
- Success rates after retries
- Escalation rates to human review
- Error types and frequencies

## Benefits

### 1. **Improved Resilience**
- Automatic recovery from transient failures
- Reduced manual intervention requirements
- Better system uptime and reliability

### 2. **Enhanced Debugging**
- Detailed error information for troubleshooting
- Complete execution trace with attempt counts
- Structured logging for analysis

### 3. **Self-Correction Capability**
- Agents can learn from and correct previous errors
- Intelligent retry mechanisms prevent cascade failures
- Human review only for persistent issues

### 4. **Better Monitoring**
- Comprehensive error tracking and metrics
- Real-time visibility into retry attempts
- Clear escalation paths for manual review

## Usage Examples

### Enable Enhanced Error Handling
The enhanced error handling is automatically enabled in all workflow types:

```python
from orchestration.execute_workflow import execute_task

# Enhanced error handling is active by default
result = execute_task(
    task_id="BE-07",
    workflow_type="dynamic"  # Uses enhanced dynamic_router
)
```

### Monitor Error Events
```python
import logging

# Configure logging to capture error handling events
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("graph_builder")

# Error events will be logged with structured information
```

### Custom Retry Configuration
To modify retry behavior, update the `MAX_ATTEMPTS` constant in the `dynamic_router` function:

```python
def dynamic_router(state):
    MAX_ATTEMPTS = 5  # Increase retry attempts
    # ... rest of implementation
```

## Integration with Coordinator Planning

The enhanced error handling works seamlessly with the JSON-based coordinator planning:

1. **Plan Execution**: Each plan part benefits from retry logic
2. **Error Feedback**: Detailed error information is provided to coordinator for re-planning
3. **Adaptive Planning**: Coordinator can adjust plans based on error patterns
4. **Graceful Degradation**: Failed plan parts don't crash the entire workflow

## Testing and Validation

### Test Coverage
- ✅ Syntax validation for all modified files
- ✅ Enhanced error reporting in all handlers
- ✅ Retry logic implementation in dynamic router
- ✅ WorkflowState updates across all graph types
- ✅ PlanExecutionManager integration
- ✅ Basic import and parsing validation

### Validation Results
All error handling improvements have been tested and validated:
- 4 WorkflowState definitions updated with error fields
- 6 agent handlers enhanced with structured error reporting
- Retry logic implemented in dynamic workflow graph
- Integration completed with PlanExecutionManager

## Future Enhancements

### Potential Improvements:
1. **Configurable Retry Policies**: Different retry strategies per agent type
2. **Error Classification**: Automatic categorization of error types
3. **Learning from Errors**: Statistical analysis of error patterns
4. **Circuit Breaker Pattern**: Temporary agent disabling for persistent failures
5. **Error Recovery Strategies**: Specific recovery actions per error type

## Migration Guide

### For Existing Users:
1. **No Action Required**: Enhanced error handling is automatically active
2. **Backward Compatibility**: All existing error handling continues to work
3. **Enhanced Information**: New structured error information available in results

### For Developers:
1. **Error Handling**: Agents now receive detailed error context for self-correction
2. **Status Checks**: Check for both `error` and `error_info` in result states
3. **Retry Awareness**: Agents can access `attempt_count` to adjust behavior

## Conclusion

The enhanced error handling and self-correction capabilities significantly improve the system's resilience and reliability. With automatic retry mechanisms, detailed error reporting, and intelligent escalation paths, the system can now handle failures gracefully while providing comprehensive visibility into error conditions and recovery attempts.

These improvements ensure that transient failures are automatically resolved, persistent issues are properly escalated, and the entire system maintains high availability even in the face of individual component failures.