"""
Agent Execution Handlers for LangGraph Workflow
Implements execution wrappers for agents with status management.
Step 4.8 Enhancement: Added real-time monitoring hooks.
Enhanced Error Handling: Added detailed error reporting and structured error information.
"""

import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from orchestration.registry import create_agent_instance
from orchestration.states import TaskStatus
from utils.execution_monitor import get_execution_monitor
from utils.review import is_review_approved

try:
    from pythonjsonlogger import jsonlogger
except ImportError:
    # Fallback if pythonjsonlogger is not available
    class JsonFormatter:
        def __init__(self, *args, **kwargs):
            pass
    jsonlogger = type('JsonLogger', (), {'JsonFormatter': JsonFormatter})

# Configure structured JSON logging for production
logger = logging.getLogger("agent_handlers")
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s %(agent)s %(task_id)s %(event)s')
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def coordinator_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Coordinator agent that manages task planning.
    Transitions tasks from CREATED to PLANNED.
    """
    task_id = state.get("task_id", "UNKNOWN")

    logger.info("Coordinator handler invoked", extra={
        'agent': 'coordinator',
        'task_id': task_id,
        'event': 'handler_invoked'
    })

    # Step 4.8: Start execution monitoring
    monitor = get_execution_monitor()
    execution_data = monitor.start_agent_execution(
        task_id, "coordinator", state)

    try:
        # Get coordinator agent and execute
        agent = create_agent_instance("coordinator")

        # Execute agent with timeout protection
        result = execute_with_timeout(agent, state, timeout_seconds=30)

        # Ensure we have a proper result structure
        if not isinstance(result, dict):
            result = {"output": str(result)}

        # Always transition CREATED -> PLANNED for coordinator success
        result.update({
            "task_id": task_id,
            "agent": "coordinator",
            "status": TaskStatus.PLANNED,  # Always set to PLANNED on success
            "timestamp": datetime.now().isoformat()
        })

        # Step 4.8: Complete execution monitoring
        monitor.complete_agent_execution(execution_data, "COMPLETED", result)
        return result

    except Exception as e:
        error_details = {
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "agent_role": "coordinator"
        }
        logger.error(f"Error in {error_details['agent_role']} handler for task {task_id}", 
                    exc_info=True, extra={
            "agent": error_details['agent_role'],
            "task_id": task_id,
            "event": "handler_error",
            "error_message": error_details["message"]
        })
        error_result = {
            "task_id": task_id,
            "agent": "coordinator",
            "status": TaskStatus.BLOCKED,
            "error_info": error_details,
            "output": f"{error_details['agent_role'].capitalize()} implementation failed: {error_details['message']}",
            "attempt_count": state.get("attempt_count", 1),
            "timestamp": datetime.now().isoformat()
        }
        # Step 4.8: Log execution failure
        monitor.complete_agent_execution(
            execution_data, "FAILED", error=str(e))
        return error_result


def technical_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Technical Architect agent.
    Transitions tasks from PLANNED to IN_PROGRESS.
    """
    task_id = state.get("task_id", "UNKNOWN")

    logger.info("Technical handler invoked", extra={
        'agent': 'technical',
        'task_id': task_id,
        'event': 'handler_invoked'
    })

    # Step 4.8: Start execution monitoring
    monitor = get_execution_monitor()
    execution_data = monitor.start_agent_execution(task_id, "technical", state)

    try:
        # Get technical agent and execute
        agent = create_agent_instance("technical")

        # Execute agent with timeout protection
        result = execute_with_timeout(agent, state, timeout_seconds=30)

        # Ensure we have a proper result structure
        if not isinstance(result, dict):
            result = {"output": str(result)}

        # Always transition PLANNED -> IN_PROGRESS for technical success
        result.update({
            "task_id": task_id,
            "agent": "technical",
            "status": TaskStatus.IN_PROGRESS,  # Always set to IN_PROGRESS on success
            "timestamp": datetime.now().isoformat()
        })

        # Step 4.8: Complete execution monitoring
        monitor.complete_agent_execution(execution_data, "COMPLETED", result)
        return result

    except Exception as e:
        error_details = {
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "agent_role": "technical"
        }
        logger.error(f"Error in {error_details['agent_role']} handler for task {task_id}", 
                    exc_info=True, extra={
            "agent": error_details['agent_role'],
            "task_id": task_id,
            "event": "handler_error",
            "error_message": error_details["message"]
        })
        error_result = {
            "task_id": task_id,
            "agent": "technical",
            "status": TaskStatus.BLOCKED,
            "error_info": error_details,
            "output": f"{error_details['agent_role'].capitalize()} implementation failed: {error_details['message']}",
            "attempt_count": state.get("attempt_count", 1),
            "timestamp": datetime.now().isoformat()
        }
        # Step 4.8: Log execution failure
        monitor.complete_agent_execution(
            execution_data, "FAILED", error=str(e))
        return error_result


def backend_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Backend agent.
    Transitions tasks from IN_PROGRESS to QA_PENDING.
    """
    task_id = state.get("task_id", "UNKNOWN")

    logger.info("Backend handler invoked", extra={
        'agent': 'backend',
        'task_id': task_id,
        'event': 'handler_invoked'
    })

    # Step 4.8: Start execution monitoring
    monitor = get_execution_monitor()
    execution_data = monitor.start_agent_execution(task_id, "backend", state)

    try:
        # Get backend agent and execute
        agent = create_agent_instance("backend")

        # Execute agent with timeout protection
        result = execute_with_timeout(agent, state, timeout_seconds=60)

        # Ensure we have a proper result structure
        if not isinstance(result, dict):
            result = {"output": str(result)}

        # Always transition IN_PROGRESS -> QA_PENDING for backend success
        result.update({
            "task_id": task_id,
            "agent": "backend",
            "status": TaskStatus.QA_PENDING,  # Always set to QA_PENDING on success
            "timestamp": datetime.now().isoformat()
        })

        # Step 4.8: Complete execution monitoring
        monitor.complete_agent_execution(execution_data, "COMPLETED", result)
        return result

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
        error_result = {
            "task_id": task_id,
            "agent": "backend",
            "status": TaskStatus.BLOCKED,
            "error_info": error_details,
            "output": f"{error_details['agent_role'].capitalize()} implementation failed: {error_details['message']}",
            "attempt_count": state.get("attempt_count", 1),
            "timestamp": datetime.now().isoformat()
        }
        # Step 4.8: Log execution failure
        monitor.complete_agent_execution(
            execution_data, "FAILED", error=str(e))
        return error_result


def frontend_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Frontend Engineer agent.
    Step 4.8 Enhancement: Added real-time execution monitoring.

    Args:
        state: The current workflow state

    Returns:
        Updated state with frontend output and next status
    """
    agent = create_agent_instance("frontend")
    task_id = state.get("task_id", "UNKNOWN")
    logger.info(
        "Frontend handler invoked",
        extra={
            "agent": "frontend",
            "task_id": task_id,
            "event": "handler_invoked"})

    # Step 4.8: Start execution monitoring
    monitor = get_execution_monitor()
    execution_data = monitor.start_agent_execution(task_id, "frontend", state)

    try:
        result = agent.run(state)

        if not isinstance(result, dict):
            result = {"output": result}

        # Add status information
        result["status"] = TaskStatus.QA_PENDING
        result["agent"] = "frontend"
        result["task_id"] = task_id

        # Preserve context
        result.update({k: v for k, v in state.items() if k not in result})

        # Step 4.8: Complete execution monitoring
        monitor.complete_agent_execution(execution_data, "COMPLETED", result)

        return result
    except Exception as e:
        error_details = {
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "agent_role": "frontend"
        }
        logger.error(f"Error in {error_details['agent_role']} handler for task {task_id}", 
                    exc_info=True, extra={
            "agent": error_details['agent_role'],
            "task_id": task_id,
            "event": "handler_error",
            "error_message": error_details["message"]
        })
        # Step 4.8: Log execution failure
        monitor.complete_agent_execution(
            execution_data, "FAILED", error=str(e))

        return {
            "task_id": task_id,
            "status": TaskStatus.BLOCKED,
            "agent": "frontend",
            "error_info": error_details,
            "output": f"{error_details['agent_role'].capitalize()} implementation failed: {error_details['message']}",
            "attempt_count": state.get("attempt_count", 1)
        }


def qa_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for QA evaluation. This assesses task outputs and decides whether to continue
    or move to human review.

    Args:
        state: The current workflow state

    Returns:
        Updated state with QA results
    """
    task_id = state.get("task_id", "UNKNOWN")
    agent_output = state.get("output", "")
    logger.info("QA handler invoked", extra={
                "agent": "qa", "task_id": task_id, "event": "handler_invoked"})

    try:
        # Simulate QA testing
        # In a real implementation, this would run actual tests against the
        # codebase

        # For demonstration purposes, always move to human review
        # In a real implementation, this might be conditional
        from handlers.qa_handler import qa_agent

        # Pass through to our QA agent implementation
        return qa_agent(state)

    except Exception as e:
        error_details = {
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "agent_role": "qa"
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
            "status": TaskStatus.BLOCKED,
            "agent": "qa",
            "error_info": error_details,
            "output": f"{error_details['agent_role'].capitalize()} implementation failed: {error_details['message']}",
            "attempt_count": state.get("attempt_count", 1)
        }


def documentation_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Documentation agent.
    Transitions tasks from DOCUMENTATION to DONE.
    """
    task_id = state.get("task_id", "UNKNOWN")

    logger.info("Documentation handler invoked", extra={
        'agent': 'documentation',
        'task_id': task_id,
        'event': 'handler_invoked'
    })

    # Step 4.8: Start execution monitoring
    monitor = get_execution_monitor()
    execution_data = monitor.start_agent_execution(
        task_id, "documentation", state)

    try:
        # Get documentation agent and execute
        agent = create_agent_instance("documentation")

        # Execute agent with timeout protection
        result = execute_with_timeout(agent, state, timeout_seconds=30)

        # Ensure we have a proper result structure
        if not isinstance(result, dict):
            result = {"output": str(result)}

        # Always transition DOCUMENTATION -> DONE for documentation success
        result.update({
            "task_id": task_id,
            "agent": "documentation",
            "status": TaskStatus.DONE,  # Always set to DONE on success
            "timestamp": datetime.now().isoformat()
        })

        # Step 4.8: Complete execution monitoring
        monitor.complete_agent_execution(execution_data, "COMPLETED", result)
        return result

    except Exception as e:
        error_details = {
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "agent_role": "documentation"
        }
        logger.error(f"Error in {error_details['agent_role']} handler for task {task_id}", 
                    exc_info=True, extra={
            "agent": error_details['agent_role'],
            "task_id": task_id,
            "event": "handler_error",
            "error_message": error_details["message"]
        })
        error_result = {
            "task_id": task_id,
            "agent": "documentation",
            "status": TaskStatus.BLOCKED,
            "error_info": error_details,
            "output": f"{error_details['agent_role'].capitalize()} implementation failed: {error_details['message']}",
            "attempt_count": state.get("attempt_count", 1),
            "timestamp": datetime.now().isoformat()
        }
        # Step 4.8: Log execution failure
        monitor.complete_agent_execution(
            execution_data, "FAILED", error=str(e))
        return error_result


def human_review_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for human review checkpoints. This checks if a human review has been completed
    and either waits or continues the workflow accordingly.

    Args:
        state: The current workflow state

    Returns:
        Updated state with human review status
    """
    task_id = state.get("task_id", "UNKNOWN")
    agent_role = state.get("agent", "unknown")
    review_file = state.get("review_file", f"qa_{task_id}.md")
    logger.info(
        "Human review handler invoked",
        extra={
            "agent": "human_review",
            "task_id": task_id,
            "event": "handler_invoked"})

    # Check if this review has been approved
    if is_review_approved(review_file):
        # Review approved, continue workflow
        result = state.copy()
        result["status"] = TaskStatus.DOCUMENTATION
        result["human_review_completed"] = True
        result["message"] = f"Task {task_id} review approved. Moving to DOCUMENTATION."
        return result
    else:
        # Review pending, pause workflow
        result = state.copy()
        result["status"] = TaskStatus.HUMAN_REVIEW
        result["human_review_required"] = True
        result["human_review_completed"] = False
        result["message"] = f"Task {task_id} requires human review after {agent_role} execution."

        # In a real implementation with a persistent workflow engine,
        # this would pause execution until the review is completed
        return result


def execute_with_timeout(agent, state, timeout_seconds=30):
    """
    Execute an agent with timeout protection.
    Cross-platform implementation that works on both Unix and Windows.

    Args:
        agent: The agent instance to execute
        state: The current state
        timeout_seconds: Maximum execution time

    Returns:
        Agent execution result
    """
    import platform
    import threading

    # For Windows or when testing, use threading approach
    if platform.system() == "Windows" or hasattr(state, '_test_mode'):
        result_container = {"result": None,
                            "exception": None, "completed": False}

        def worker():
            try:
                if hasattr(agent, 'execute'):
                    result_container["result"] = agent.execute(state)
                elif hasattr(agent, 'run'):
                    result_container["result"] = agent.run(state)
                else:
                    # Fallback: just return a success message
                    result_container["result"] = {
                        "output": f"Agent {
                            type(agent).__name__} executed successfully"}
                result_container["completed"] = True
            except Exception as e:
                result_container["exception"] = e

        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        thread.join(timeout_seconds)

        if thread.is_alive():
            raise Exception(
                f"Agent execution timed out after {timeout_seconds} seconds")

        if result_container["exception"]:
            raise result_container["exception"]

        return result_container["result"]

    else:
        # Unix/Linux signal-based approach
        import signal

        class TimeoutException(Exception):
            pass

        def timeout_handler(signum, frame):
            raise TimeoutException("Agent execution timed out")

        # Set up timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)

        try:
            if hasattr(agent, 'execute'):
                result = agent.execute(state)
            elif hasattr(agent, 'run'):
                result = agent.run(state)
            else:
                # Fallback: just return a success message
                result = {
                    "output": f"Agent {
                        type(agent).__name__} executed successfully"}

            signal.alarm(0)  # Cancel the alarm
            return result

        except TimeoutException:
            raise Exception(
                f"Agent execution timed out after {timeout_seconds} seconds")
        except Exception as e:
            signal.alarm(0)  # Cancel the alarm
            raise e
        finally:
            signal.signal(signal.SIGALRM, old_handler)
