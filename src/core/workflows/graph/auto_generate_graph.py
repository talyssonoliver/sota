"""
Auto Graph Generator

Scans task YAML files and dynamically generates a LangGraph workflow based on task dependencies.
"""

from src.infrastructure.utils.common_imports import (
    Any,
    Dict,
    List,
    Optional,
    json,
    logging,
    os,
    yaml
)
import importlib
import inspect
from glob import glob

try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict
# LangGraph imports with error handling
try:
    from langgraph.constants import END
    from langgraph.graph import StateGraph

    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    logging.error(f"LangGraph not available: {e}")
    LANGGRAPH_AVAILABLE = False

    # Create mock classes
    class MockStateGraph:
        def __init__(self, *args, **kwargs):
            self.nodes = {}
            self.edges = []
            self.entry_points = []

        def add_node(self, name, action):
            self.nodes[name] = action
            return self

        def add_edge(self, start, end):
            self.edges.append((start, end))
            return self

        def add_conditional_edges(self, start, condition, mapping):
            # Mock implementation
            return self

        def set_entry_point(self, node):
            self.entry_points.append(node)
            return self

        def compile(self):
            # Return a mock compiled graph
            class MockCompiledGraph:
                def run(self, *args, **kwargs):
                    return {"result": "mocked"}

            return MockCompiledGraph()

    END = "END"
    StateGraph = MockStateGraph

# Local imports with error handling
try:
    from .graph_builder import build_dynamic_workflow_graph
except ImportError as e:
    logging.warning(f"Graph builder not available: {e}")

    def build_dynamic_workflow_graph(*args, **kwargs) -> Any:
        logging.error("Graph builder not available - using fallback")
        # Return a basic StateGraph as fallback
        if LANGGRAPH_AVAILABLE:
            # We need to create a minimal WorkflowState for the fallback
            from typing import TypedDict

            class FallbackState(TypedDict, total=False):
                task_id: str
                agent: str
                output: str
                status: str

            return StateGraph(FallbackState)
        else:
            return MockStateGraph()


try:
    from .handlers import (backend_handler, coordinator_handler,
                           documentation_handler, frontend_handler,
                           human_review_handler, qa_handler, technical_handler)
except ImportError as e:
    logging.warning(f"Handlers not available: {e}")

    # Create mock handlers
    def mock_handler(*args, **kwargs):
        logging.error("Handler not available - using mock")
        return {"status": "error", "message": "Handler not available"}

    backend_handler = mock_handler
    coordinator_handler = mock_handler
    documentation_handler = mock_handler
    frontend_handler = mock_handler
    human_review_handler = mock_handler
    qa_handler = mock_handler
    technical_handler = mock_handler

from src.core.workflows.registry import get_agent
from src.core.workflows.states import TaskStatus

# Standard library imports
try:
    import importlib
    import inspect

    INTROSPECTION_AVAILABLE = True
except ImportError as e:
    logging.error(f"Python introspection modules not available: {e}")
    INTROSPECTION_AVAILABLE = False


def find_all_task_files() -> List[str]:
    """
    Find all task YAML files in the tasks directory.

    Returns:
        List of paths to YAML files
    """
    tasks_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tasks"
    )
    return glob(os.path.join(tasks_dir, "*.yaml"))


def load_task_metadata(file_path: str) -> Dict[str, Any]:
    """
    Load task metadata from a YAML file.

    Args:
        file_path: Path to the YAML file

    Returns:
        Dict containing the task metadata
    """
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def extract_tasks_dependency_graph() -> Dict[str, Any]:
    """
    Extract tasks and their dependencies from all task YAML files.

    Returns:
        A structured graph configuration
    """
    task_files = find_all_task_files()
    tasks = {}

    # First pass: load all tasks
    for task_file in task_files:
        try:
            task_data = load_task_metadata(task_file)
            if task_data and "id" in task_data:
                task_id = task_data["id"]
                tasks[task_id] = {
                    "id": task_id,
                    "title": task_data.get("title", ""),
                    "owner": task_data.get("owner", ""),
                    "depends_on": task_data.get("depends_on", []),
                    "state": task_data.get("state", ""),
                    "priority": task_data.get("priority", ""),
                }
        except Exception as e:
            print(f"Error loading task file {task_file}: {e}")

    # Convert to LangGraph configuration format
    nodes = []
    role_to_agent_map = {
        "coordinator": "coordinator",
        "technical": "technical",
        "backend": "backend",
        "frontend": "frontend",
        "qa": "qa",
        "doc": "documentation",
        "ux": "ux",
        "product": "product_manager",
    }

    # Add nodes based on task owners (agents)
    agent_to_tasks = {}
    for task_id, task in tasks.items():
        owner = task.get("owner", "")
        if owner not in agent_to_tasks:
            agent_to_tasks[owner] = []
        agent_to_tasks[owner].append(task_id)

    # Create nodes
    for owner, task_ids in agent_to_tasks.items():
        agent_role = role_to_agent_map.get(owner, owner)
        nodes.append(
            {
                "id": owner,
                "agent": agent_role,
                "depends_on": [],  # Will be filled in the next step
            }
        )

    # Add human review and coordinator nodes if not already present
    if "human_review" not in [node["id"] for node in nodes]:
        nodes.append({"id": "human_review", "agent": "human_review", "depends_on": []})

    if "coordinator" not in [node["id"] for node in nodes]:
        nodes.append({"id": "coordinator", "agent": "coordinator", "depends_on": []})

    # Add dependency edges based on task dependencies
    for task_id, task in tasks.items():
        owner = task.get("owner", "")
        for dep_id in task.get("depends_on", []):
            if dep_id in tasks:
                dep_owner = tasks[dep_id].get("owner", "")
                if (
                    dep_owner
                    and dep_owner != owner
                    and dep_owner
                    not in [d for d in nodes if d["id"] == owner][0]["depends_on"]
                ):
                    # Add dependency edge from dep_owner to owner
                    [d for d in nodes if d["id"] == owner][0]["depends_on"].append(
                        dep_owner
                    )

    return {"nodes": nodes}


def generate_graph_config():
    """
    Generate a graph configuration JSON file based on task dependencies.

    Returns:
        Path to the generated JSON file
    """
    graph_config = extract_tasks_dependency_graph()

    # Save the configuration
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "auto_generated_graph.json"
    )
    with open(output_path, "w") as f:
        json.dump(graph_config, f, indent=2)

    print(f"Generated graph configuration saved to {output_path}")
    return output_path


def build_auto_generated_workflow_graph():
    """
    Build the workflow graph from the generated configuration.

    Returns:
        StateGraph: The compiled workflow graph
    """
    # Load the configuration
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "auto_generated_graph.json"
    )
    if not os.path.exists(config_path):
        logging.error(f"Configuration file not found: {config_path}")
        return None

    with open(config_path, "r") as f:
        config = json.load(f)

    # Create workflow schema - TypedDict that's compatible with existing handlers
    class WorkflowState(TypedDict, total=False):
        # Core fields that handlers expect
        task_id: str
        agent: str
        output: str
        status: str
        error: Optional[str]
        timestamp: str
        # Note: TypedDict allows additional fields when total=False

    # Build the graph using StateGraph
    workflow = StateGraph(WorkflowState)

    # Handler map (dynamically extensible)
    handler_map = {
        "coordinator": coordinator_handler,
        "technical": technical_handler,
        "backend": backend_handler,
        "frontend": frontend_handler,
        "qa": qa_handler,
        "documentation": documentation_handler,
        "human_review": human_review_handler,
        # Add other handlers as needed
    }

    # Dynamically add handlers for new roles if present in graph/handlers.py
    handlers_module = importlib.import_module("src.core.workflows.graph.handlers")
    for node in config["nodes"]:
        agent_role = node["agent"]
        if agent_role not in handler_map:
            handler_func_name = f"{agent_role}_handler"
            if hasattr(handlers_module, handler_func_name):
                handler_func = getattr(handlers_module, handler_func_name)
                if inspect.isfunction(handler_func):
                    handler_map[agent_role] = handler_func

    # Add nodes
    for node in config["nodes"]:
        node_id = node["id"]
        agent_role = node["agent"]

        if agent_role in handler_map:
            # Use the existing handler - TypedDict is compatible with Dict[str, Any]
            workflow.add_node(node_id, handler_map[agent_role])  # type: ignore
        else:
            # Create a generic handler function for roles without specific handlers
            def create_generic_handler():
                def handler(state: Dict[str, Any]) -> Dict[str, Any]:
                    role = state.get("agent", "unknown")
                    agent = get_agent(role)

                    # Handle the agent execution properly - get_agent returns dict
                    if isinstance(agent, dict):
                        # For dictionary-based agents, create a simple result
                        result: Dict[str, Any] = {
                            "output": f"Processed by {role} agent",
                            "status": "completed",
                            "agent_type": agent.get("type", role),
                        }
                    else:
                        # Fallback for unknown agent types
                        result: Dict[str, Any] = {
                            "output": f"Processed by {role} agent",
                            "status": "completed",
                        }

                    # Ensure result is a dictionary
                    if not isinstance(result, dict):
                        result = {"output": result}

                    # Set agent identifier and preserve task ID
                    result["agent"] = role
                    if "task_id" not in result and "task_id" in state:
                        result["task_id"] = state["task_id"]

                    # --- Anti-infinite-loop logic ---
                    # Track consecutive IN_PROGRESS iterations
                    in_progress_count = state.get("in_progress_count", 0)
                    output = result.get("output", "").lower()
                    if any(
                        term in output
                        for term in ["done", "completed", "success", "passed"]
                    ) or result.get("status") in [
                        TaskStatus.DONE.value,
                        TaskStatus.BLOCKED.value,
                        TaskStatus.COMPLETED.value,
                    ]:
                        result["status"] = TaskStatus.DONE.value
                        result.pop("in_progress_count", None)
                    elif (
                        "fail" in output
                        or "error" in output
                        or result.get("status") == TaskStatus.BLOCKED.value
                    ):
                        result["status"] = TaskStatus.BLOCKED.value
                        result.pop("in_progress_count", None)
                    else:
                        # If still in progress, increment the counter
                        in_progress_count += 1
                        result["in_progress_count"] = in_progress_count
                        result["status"] = TaskStatus.IN_PROGRESS.value
                        # If we've looped too many times, block the task
                        if in_progress_count >= 3:
                            result["status"] = TaskStatus.BLOCKED.value
                            result["error"] = (
                                "Infinite loop detected: too many consecutive IN_PROGRESS states."
                            )
                            result.pop("in_progress_count", None)

                    # Preserve other context from state
                    result.update({k: v for k, v in state.items() if k not in result})

                    return result

                return handler

            workflow.add_node(node_id, create_generic_handler())  # type: ignore

    # Add edges based on dependencies using conditional routing
    for node in config["nodes"]:
        node_id = node["id"]
        depends_on = node["depends_on"]

        if depends_on:
            # Create destinations dictionary with actual target nodes
            destinations = {}
            for dep in depends_on:
                destinations[dep] = dep
            # Add END as a potential destination for terminal states
            destinations[END] = END

            workflow.add_conditional_edges(
                node_id, create_router(depends_on), destinations
            )
        else:
            # For terminal nodes, add an edge to END
            workflow.add_edge(node_id, END)

    # Set entry point
    entry_nodes = [node["id"] for node in config["nodes"] if not node["depends_on"]]
    if entry_nodes:
        workflow.set_entry_point(entry_nodes[0])
    else:
        # Default to coordinator if no clear entry point
        workflow.set_entry_point("coordinator")

    # Compile and return the workflow
    compiled_workflow = workflow.compile()
    return compiled_workflow


# Create a dynamic router function for handling multiple potential edges
def create_router(dependent_nodes):
    def router(state):
        # Default to the first dependency if available
        if dependent_nodes:
            return dependent_nodes[0]
        # If no dependencies, this is a terminal node, return END
        return END

    return router


# Generate the graph configuration when this module is run
if __name__ == "__main__":
    config_path = generate_graph_config()

    # Print a success message
    print(f"Successfully generated graph configuration at: {config_path}")
    print("You can now use this graph in your workflow with:")
    print(
        "from src.core.workflows.graph.auto_generate_graph import build_auto_generated_workflow_graph"
    )
    print("workflow = build_auto_generated_workflow_graph()")
