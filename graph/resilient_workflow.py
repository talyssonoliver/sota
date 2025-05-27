"""
Resilient Workflow Builder
Adds timeout and retry capabilities to LangGraph workflows.
"""

import functools
import os
import sys
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Union

from langgraph.graph import Graph, StateGraph

from orchestration.states import TaskStatus
from utils.task_loader import update_task_state

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# In-memory database for tracking retry attempts and timeouts
attempt_tracker = {}
timeout_status = {}


def with_retry(max_retries: int = 3, retry_delay: int = 5):
    """
    Decorator that adds retry logic to handler functions.

    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Time to wait between retries in seconds

    Returns:
        Decorated function with retry logic
    """
    def decorator(handler_func):
        @functools.wraps(handler_func)
        def wrapper(state):
            task_id = state.get("task_id", "unknown")
            attempt_key = f"{task_id}_{handler_func.__name__}"

            # Initialize attempts counter
            if attempt_key not in attempt_tracker:
                attempt_tracker[attempt_key] = 0

            try:
                # Increment attempt counter
                attempt_tracker[attempt_key] += 1
                current_attempt = attempt_tracker[attempt_key]

                # Add attempt info to state for logging
                state["current_attempt"] = current_attempt
                state["max_attempts"] = max_retries

                # Run the handler
                result = handler_func(state)

                # Success - reset counter
                attempt_tracker[attempt_key] = 0
                return result

            except Exception as e:
                current_attempt = attempt_tracker[attempt_key]

                if current_attempt < max_retries:
                    # Log retry attempt
                    print(f"Error in {handler_func.__name__} for task {task_id}. "
                          f"Attempt {current_attempt}/{max_retries}. Retrying in {retry_delay}s...")
                    print(f"Error details: {str(e)}")

                    # Wait before retry
                    time.sleep(retry_delay)

                    # Return the same state to retry
                    return state
                else:
                    # Max retries reached - reset counter and mark task as
                    # blocked
                    attempt_tracker[attempt_key] = 0

                    # Update state to indicate failure
                    state["status"] = TaskStatus.BLOCKED
                    state["error"] = f"Max retry attempts ({max_retries}) reached: {
                        str(e)}"

                    # Update task state in YAML file
                    try:
                        update_task_state(task_id, TaskStatus.BLOCKED)
                    except Exception as update_error:
                        print(
                            f"Failed to update task state: {
                                str(update_error)}")

                    return state

        return wrapper
    return decorator


def with_timeout(timeout_seconds: int = 300):
    """
    Decorator that adds timeout capability to handler functions.

    Args:
        timeout_seconds: Maximum execution time in seconds

    Returns:
        Decorated function with timeout logic
    """
    def decorator(handler_func):
        @functools.wraps(handler_func)
        def wrapper(state):
            task_id = state.get("task_id", "unknown")
            timeout_key = f"{task_id}_{handler_func.__name__}"

            # Create result container for thread communication
            result_container = {"result": None,
                                "exception": None, "completed": False}

            # Define worker function to run in thread
            def worker():
                try:
                    result_container["result"] = handler_func(state)
                    result_container["completed"] = True
                except Exception as e:
                    result_container["exception"] = e

            # Create and start thread
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()

            # Wait for completion or timeout
            thread.join(timeout_seconds)

            if thread.is_alive():
                # Timeout occurred
                timeout_status[timeout_key] = True

                # Create timeout error state
                timeout_state = state.copy()
                timeout_state["status"] = TaskStatus.BLOCKED
                timeout_state["error"] = f"Execution timeout after {timeout_seconds} seconds"

                # Update task state in YAML file
                try:
                    update_task_state(task_id, TaskStatus.BLOCKED)
                except Exception as update_error:
                    print(f"Failed to update task state: {str(update_error)}")

                return timeout_state

            if result_container["completed"]:
                return result_container["result"]
            elif result_container["exception"]:
                # Re-raise exception from thread
                state["status"] = TaskStatus.BLOCKED
                state["error"] = f"Error during execution: {
                    str(
                        result_container['exception'])}"
                return state
            else:
                # Unexpected state
                state["status"] = TaskStatus.BLOCKED
                state["error"] = "Unexpected execution state"
                return state

        return wrapper
    return decorator


def add_resilience_to_graph(graph: Union[Graph,
                                         StateGraph],
                            config: Dict[str,
                                         Any] = None) -> Union[Graph,
                                                               StateGraph]:
    """
    Add resilience features to an existing graph.

    Args:
        graph: The LangGraph workflow to enhance
        config: Configuration for resilience features

    Returns:
        Enhanced graph with resilience features
    """
    if config is None:
        config = {
            "max_retries": 3,
            "retry_delay": 5,
            "timeout_seconds": 300,
            "nodes_with_retry": ["*"],  # All nodes
            "nodes_with_timeout": ["*"]  # All nodes
        }

    # This is a simplified approach - in a real implementation, we'd need to:
    # 1. Clone the graph
    # 2. Replace each node's handler with a resilient version
    # 3. Add error handling edges

    # For now, we'll just print that this would modify the graph
    print(f"Adding resilience to graph with config: {config}")
    print("In a real implementation, this would wrap all node handlers with retry/timeout logic")

    # Return the original graph for now
    # In a full implementation, we would return the enhanced graph
    return graph


def create_resilient_workflow(base_graph_builder: Callable[[], Union[Graph, StateGraph]],
                              config: Dict[str, Any] = None) -> Union[Graph, StateGraph]:
    """
    Create a resilient workflow by enhancing an existing graph builder.

    Args:
        base_graph_builder: Function that builds the base graph
        config: Configuration for resilience features

    Returns:
        A workflow graph with added resilience features
    """
    # Build the base graph
    base_graph = base_graph_builder()

    # Add resilience features
    resilient_graph = add_resilience_to_graph(base_graph, config)

    return resilient_graph

# Example usage:
# from graph.graph_builder import build_workflow_graph
# resilient_workflow = create_resilient_workflow(build_workflow_graph)
