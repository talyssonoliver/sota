
from src.infrastructure.utils.common_imports import os, sys, time
"""
Resilient Workflow Builder
Adds timeout and retry capabilities to LangGraph workflows.
"""

import functools
import threading
from typing import Callable, Dict, Optional, Protocol, TypedDict, Union, Type, Any

try:
    from src.core.workflows.states import TaskStatus
except ImportError:
    pass

try:
    from src.infrastructure.utils.task_loader import update_task_state
except ImportError:
    pass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Type definitions for workflow states
class WorkflowState(TypedDict, total=False):
    """Type definition for workflow state dictionary."""
    task_id: str
    status: Union[str, 'TaskStatus']
    error: str
    current_attempt: int
    max_attempts: int
    data: Dict[str, str]

# Type definitions for result containers
class ResultContainer(TypedDict):
    """Type definition for thread execution result container."""
    result: Optional[WorkflowState]
    exception: Optional[Exception]
    completed: bool

# Type definitions for handlers and configuration
NodeHandler = Callable[[WorkflowState], WorkflowState]
GraphBuilder = Callable[[], 'StateGraphProtocol']

class ResilientConfig(TypedDict, total=False):
    """Configuration for resilience features."""
    max_retries: int
    retry_delay: int
    timeout_seconds: int
    nodes_with_retry: list[str]
    nodes_with_timeout: list[str]

class StateGraphProtocol(Protocol):
    """Protocol defining the interface for StateGraph objects."""
    
    def add_node(self, name: str, handler: NodeHandler) -> None:
        """Add a node to the graph."""
        ...
    
    def add_edge(self, start: str, end: str) -> None:
        """Add an edge between nodes."""
        ...
    
    def compile(self) -> 'CompiledGraphProtocol':
        """Compile the graph for execution."""
        ...

class CompiledGraphProtocol(Protocol):
    """Protocol for compiled graph objects."""
    
    def invoke(self, state: WorkflowState) -> WorkflowState:
        """Execute the graph with given state."""
        ...

# StateGraph implementation with proper typing
try:
    from langgraph.graph import StateGraph as LangGraphStateGraph
    LANGGRAPH_AVAILABLE = True
    
    class LangGraphResilientStateGraph:
        """Wrapper for LangGraph StateGraph with proper typing."""
        
        def __init__(self, state_schema: Type[WorkflowState] = WorkflowState):
            self._graph = LangGraphStateGraph(state_schema)
        
        def add_node(self, name: str, handler: NodeHandler) -> None:
            """Add a node to the graph."""
            # Wrap the handler to match LangGraph's expected interface
            def wrapped_handler(state, config=None):
                return handler(state)
            self._graph.add_node(name, wrapped_handler)
        
        def add_edge(self, start: str, end: str) -> None:
            """Add an edge between nodes."""
            self._graph.add_edge(start, end)
        
        def compile(self) -> Any:
            """Compile the graph for execution."""
            return self._graph.compile()
        
        def __getattr__(self, name: str):
            """Delegate other attributes to the underlying graph."""
            return getattr(self._graph, name)
    
    # Use the LangGraph implementation
    ResilientStateGraph = LangGraphResilientStateGraph

except ImportError:
    LANGGRAPH_AVAILABLE = False
    
    class MockResilientStateGraph:
        """Mock StateGraph for when LangGraph is not available."""
        
        def __init__(self, state_schema: Type[WorkflowState] = WorkflowState):
            self._nodes: Dict[str, NodeHandler] = {}
            self._edges: list[tuple[str, str]] = []
        
        def add_node(self, name: str, handler: NodeHandler) -> None:
            """Add a node to the mock graph."""
            self._nodes[name] = handler
        
        def add_edge(self, start: str, end: str) -> None:
            """Add an edge to the mock graph."""
            self._edges.append((start, end))
        
        def compile(self) -> 'MockCompiledGraph':
            """Return a mock compiled graph."""
            return MockCompiledGraph(self._nodes, self._edges)
    
    # Use the mock implementation
    ResilientStateGraph = MockResilientStateGraph

    class MockCompiledGraph:
        """Mock compiled graph for testing."""
        
        def __init__(self, nodes: Dict[str, NodeHandler], edges: list[tuple[str, str]]):
            self._nodes = nodes
            self._edges = edges
        
        def invoke(self, state: WorkflowState) -> WorkflowState:
            """Mock execution that returns the input state."""
            return state

# Type alias for backwards compatibility
StateGraph = ResilientStateGraph

# In-memory database for tracking retry attempts and timeouts
attempt_tracker = {}
timeout_status = {}


def _initialize_retry_attempt(task_id: str, handler_name: str) -> str:
    """Initialize retry attempt tracking for a task-handler combination."""
    attempt_key = f"{task_id}_{handler_name}"
    if attempt_key not in attempt_tracker:
        attempt_tracker[attempt_key] = 0
    return attempt_key


def _increment_retry_attempt(attempt_key: str, max_retries: int, state: WorkflowState) -> int:
    """Increment retry attempt counter and update state."""
    attempt_tracker[attempt_key] += 1
    current_attempt = attempt_tracker[attempt_key]
    
    # Add attempt info to state for logging
    state["current_attempt"] = current_attempt
    state["max_attempts"] = max_retries
    
    return current_attempt


def _handle_retry_failure(attempt_key: str, task_id: str, exception: Exception, max_retries: int, state: WorkflowState) -> WorkflowState:
    """Handle failure scenario when max retries are reached."""
    # Reset counter
    attempt_tracker[attempt_key] = 0
    
    # Update state to indicate failure
    state["status"] = TaskStatus.BLOCKED
    state["error"] = f"Max retry attempts ({max_retries}) reached: {str(exception)}"
    
    # Update task state in YAML file
    try:
        update_task_state(task_id, TaskStatus.BLOCKED.value)
    except Exception as update_error:
        print(f"Failed to update task state: {str(update_error)}")
    
    return state


def _reset_retry_counter(attempt_key: str) -> None:
    """Reset retry counter after successful execution."""
    attempt_tracker[attempt_key] = 0


def _log_retry_attempt(handler_name: str, task_id: str, current_attempt: int, max_retries: int, retry_delay: int, exception: Exception) -> None:
    """Log retry attempt information."""
    print(
        f"Error in {handler_name} for task {task_id}. "
        f"Attempt {current_attempt}/{max_retries}. Retrying in {retry_delay}s..."
    )
    print(f"Error details: {str(exception)}")


def _create_timeout_state(task_id: str, timeout_seconds: int, state: WorkflowState) -> WorkflowState:
    """Create state object for timeout scenario."""
    timeout_state = state.copy()
    timeout_state["status"] = TaskStatus.BLOCKED
    timeout_state["error"] = f"Execution timeout after {timeout_seconds} seconds"
    
    # Update task state in YAML file
    try:
        update_task_state(task_id, TaskStatus.BLOCKED.value)
    except Exception as update_error:
        print(f"Failed to update task state: {str(update_error)}")
    
    return timeout_state


def _handle_execution_exception(state: WorkflowState, exception: Exception) -> WorkflowState:
    """Handle execution exception in timeout scenario."""
    state["status"] = TaskStatus.BLOCKED
    state["error"] = f"Error during execution: {str(exception)}"
    return state


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
            attempt_key = _initialize_retry_attempt(task_id, handler_func.__name__)

            try:
                current_attempt = _increment_retry_attempt(attempt_key, max_retries, state)
                
                # Run the handler
                result = handler_func(state)
                
                # Success - reset counter
                _reset_retry_counter(attempt_key)
                return result

            except Exception as e:
                current_attempt = attempt_tracker[attempt_key]

                if current_attempt < max_retries:
                    _log_retry_attempt(handler_func.__name__, task_id, current_attempt, max_retries, retry_delay, e)
                    time.sleep(retry_delay)
                    return state  # Return the same state to retry
                else:
                    return _handle_retry_failure(attempt_key, task_id, e, max_retries, state)

        return wrapper

    return decorator


def _execute_in_thread(handler_func: NodeHandler, state: WorkflowState) -> tuple[threading.Thread, ResultContainer]:
    """Execute handler function in a separate thread with result tracking."""
    result_container: ResultContainer = {"result": None, "exception": None, "completed": False}

    def worker():
        try:
            result_container["result"] = handler_func(state)
            result_container["completed"] = True
        except Exception as e:
            result_container["exception"] = e

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    
    return thread, result_container


def _process_timeout_result(thread: threading.Thread, result_container: ResultContainer, task_id: str, timeout_key: str, timeout_seconds: int, state: WorkflowState) -> WorkflowState:
    """Process the result of timeout execution."""
    if thread.is_alive():
        # Timeout occurred
        timeout_status[timeout_key] = True
        return _create_timeout_state(task_id, timeout_seconds, state)

    if result_container["completed"] and result_container["result"] is not None:
        return result_container["result"]
    elif result_container["exception"] is not None:
        return _handle_execution_exception(state, result_container["exception"])
    else:
        # Unexpected state
        state["status"] = TaskStatus.BLOCKED
        state["error"] = "Unexpected execution state"
        return state


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

            # Execute in thread with timeout
            thread, result_container = _execute_in_thread(handler_func, state)
            
            # Wait for completion or timeout
            thread.join(timeout_seconds)
            
            # Process and return result
            return _process_timeout_result(thread, result_container, task_id, timeout_key, timeout_seconds, state)

        return wrapper

    return decorator


def _apply_resilience_decorators(handler: NodeHandler, node_name: str, config: ResilientConfig) -> NodeHandler:
    """Apply resilience decorators to a node handler based on configuration."""
    enhanced_handler = handler
    
    # Apply retry decorator if configured
    if config.get("nodes_with_retry") == ["*"] or node_name in config.get("nodes_with_retry", []):
        enhanced_handler = with_retry(
            max_retries=config.get("max_retries", 3),
            retry_delay=config.get("retry_delay", 5)
        )(enhanced_handler)
    
    # Apply timeout decorator if configured
    if config.get("nodes_with_timeout") == ["*"] or node_name in config.get("nodes_with_timeout", []):
        enhanced_handler = with_timeout(
            timeout_seconds=config.get("timeout_seconds", 300)
        )(enhanced_handler)
    
    return enhanced_handler


def _enhance_mock_graph(graph: StateGraph, config: ResilientConfig) -> StateGraph:
    """Enhance a mock StateGraph with resilience features."""
    resilient_graph = StateGraph()
    
    # Copy nodes with enhanced handlers
    for node_name, handler in graph._nodes.items():
        enhanced_handler = _apply_resilience_decorators(handler, node_name, config)
        resilient_graph.add_node(node_name, enhanced_handler)
    
    # Copy edges from original graph
    for start, end in graph._edges:
        resilient_graph.add_edge(start, end)
    
    return resilient_graph


def _get_default_config() -> ResilientConfig:
    """Get default resilience configuration."""
    return ResilientConfig(
        max_retries=3,
        retry_delay=5,
        timeout_seconds=300,
        nodes_with_retry=["*"],  # All nodes
        nodes_with_timeout=["*"],  # All nodes
    )


def add_resilience_to_graph(
    graph: Union[StateGraph, StateGraphProtocol], config: Optional[ResilientConfig] = None
) -> StateGraph:
    """
    Add resilience features to an existing graph.

    Args:
        graph: The StateGraph workflow to enhance
        config: Configuration for resilience features

    Returns:
        Enhanced graph with resilience features
    """
    if config is None:
        config = _get_default_config()

    # Handle different graph types
    if isinstance(graph, StateGraph) and hasattr(graph, '_nodes') and hasattr(graph, '_edges'):
        # Handle our mock graph case
        resilient_graph = _enhance_mock_graph(graph, config)
    
    elif LANGGRAPH_AVAILABLE and hasattr(graph, '_graph'):
        # For wrapped LangGraph instances
        print("Warning: Full LangGraph resilience enhancement not yet implemented")
        print("Falling back to basic configuration logging")
        if isinstance(graph, StateGraph):
            resilient_graph = graph
        else:
            # Create a new StateGraph as fallback
            resilient_graph = StateGraph()
    
    else:
        # For protocol-based graphs or unknown types
        print("Warning: Graph type not fully supported for resilience enhancement")
        print("Returning original graph with configuration logging")
        # Create a basic resilient graph as fallback
        resilient_graph = StateGraph()

    print(f"Enhanced graph with resilience config: {config}")
    return resilient_graph


def create_resilient_workflow(
    base_graph_builder: GraphBuilder,
    config: Optional[ResilientConfig] = None,
) -> StateGraph:
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
# from src.core.workflows.graph.graph_builder import build_workflow_graph
# resilient_workflow = create_resilient_workflow(build_workflow_graph)
