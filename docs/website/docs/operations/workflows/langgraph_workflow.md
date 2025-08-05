# LangGraph Workflow Implementation

This document provides detailed information about the LangGraph workflow implementation in the AI Agent System.

## Overview

The system uses LangGraph to define a Directed Acyclic Graph (DAG) workflow for agent collaboration. Each agent is represented as a node in the graph, and the edges represent task dependencies between agents. This structure enables agents to work together in a coordinated manner, passing information through a well-defined workflow with stateful transitions.

## Implementation Files

The LangGraph workflow implementation consists of several main files:

1. **graph_builder.py**: Dynamically constructs workflow graphs from configuration
2. **handlers.py**: Implements agent-specific handlers for state management
3. **execute_workflow.py**: Provides an interface to execute tasks through the workflow
4. **states.py**: Defines task lifecycle states for stateful transitions

## Graph Builder (`graph/graph_builder.py`)

The graph builder is responsible for:
- Loading configuration from `critical_path.json`
- Creating a LangGraph DAG with agents as nodes
- Setting up edges based on dependencies in the configuration
- Implementing conditional routing based on task states
- Compiling the graph for execution

### Key Functions

#### `load_graph_config()`
Loads the graph configuration from JSON file. The configuration defines nodes (agents), their roles, and dependencies.

```python
def load_graph_config():
    """
    Load the graph configuration from critical_path.json
    
    Returns:
        Dict containing the graph configuration
    """
```

#### `get_agent()`
Retrieves an agent instance by role name using the agent registry.

```python
def get_agent(agent_role: str):
    """
    Get an agent instance by role name.
    
    Args:
        agent_role: The role identifier for the agent
        
    Returns:
        An agent instance ready to be used in the graph
    """
```

#### `build_workflow_graph()`
Builds a standard workflow graph from the configuration.

```python
def build_workflow_graph():
    """
    Build a LangGraph workflow from the critical_path.json configuration.
    
    Returns:
        A compiled Graph object with nodes and edges set up
    """
```

#### `build_state_workflow_graph()`
Builds a stateful workflow graph with conditional edges based on task status.

```python
def build_state_workflow_graph():
    """
    Build a stateful workflow graph with conditional edges based on task status.
    
    Returns:
        A compiled StateGraph object
    """
```

#### `build_advanced_workflow_graph()`
Builds an advanced workflow graph with explicit Agent-to-Agent (A2A) communication and stateful transitions.

```python
def build_advanced_workflow_graph():
    """
    Build an advanced workflow graph with explicit A2A (Agent-to-Agent) edges.
    This implements a full Agent-to-Agent protocol with conditional routing
    and task-specific transitions based on task lifecycle states.
    
    Returns:
        A compiled StateGraph object with advanced conditional routing
    """
```

#### `build_dynamic_workflow_graph()`
Builds a dynamic workflow graph that can adapt based on task characteristics and status.

```python
def build_dynamic_workflow_graph(task_id: str = None):
    """
    Build a dynamic workflow graph that can adapt based on task requirements and status.
    
    Args:
        task_id: Optional task ID to customize the graph for a specific task
        
    Returns:
        A compiled Graph object with dynamic routing based on task lifecycle states
    """
```

## Agent Handlers (`graph/handlers.py`)

The handlers module implements agent-specific execution wrappers that manage agent communication and task state transitions:

```python
def coordinator_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Coordinator agent that manages task planning.
    Transitions tasks from CREATED to PLANNED.
    """
    
def technical_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Technical Architect agent.
    Transitions tasks from PLANNED to IN_PROGRESS.
    """
    
def qa_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the QA agent with status-based routing.
    Transitions tasks to either DOCUMENTATION or BLOCKED based on QA results.
    """
    
def documentation_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Documentation agent.
    Transitions tasks from DOCUMENTATION to DONE.
    """
    
def human_review_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for human review checkpoints.
    Transitions tasks to HUMAN_REVIEW status.
    """
```

## Task Lifecycle States (`orchestration/states.py`)

The system implements a comprehensive task lifecycle state management system to enable stateful and conditional routing:

```python
class TaskStatus(str, Enum):
    """
    Enum for tracking task status through the workflow
    Using string enum allows for serialization in state dictionaries
    """
    CREATED = "CREATED"          # Task is created but not yet started
    PLANNED = "PLANNED"          # Task is planned and ready to be worked on
    IN_PROGRESS = "IN_PROGRESS"  # Task is currently being worked on
    QA_PENDING = "QA_PENDING"    # Task is completed and waiting for QA
    DOCUMENTATION = "DOCUMENTATION"  # Task has passed QA and needs documentation
    HUMAN_REVIEW = "HUMAN_REVIEW"    # Task requires human review before proceeding
    DONE = "DONE"                # Task is completed and passed QA
    BLOCKED = "BLOCKED"          # Task is blocked by an issue
```

### State Management Functions

```python
def get_next_status(current_status: Union[str, TaskStatus], agent_role: str, success: bool = True) -> TaskStatus:
    """
    Determine the next status for a task based on current status, agent role, and success.
    """
    
def is_terminal_status(status: Union[str, TaskStatus]) -> bool:
    """
    Check if a status is terminal (no further processing needed).
    """
    
def get_valid_transitions(current_status: Union[str, TaskStatus]) -> Dict[str, TaskStatus]:
    """
    Get all valid transitions from the current status.
    """
```

## Workflow Execution (`orchestration/execute_workflow.py`)

The workflow executor provides a command-line interface for running tasks through the LangGraph workflow.

### Key Functions

#### `execute_task()`
Executes a single task through the workflow.

```python
def execute_task(task_id, input_message=None, dynamic=False, output_dir=None):
    """
    Execute a task through the agent workflow.
    
    Args:
        task_id: The task identifier (e.g. BE-07)
        input_message: Optional input message to include in the initial state
        dynamic: Whether to use dynamic workflow routing
        output_dir: Directory to save outputs to
    
    Returns:
        The result of the workflow execution
    """
```

#### `execute_all_tasks()`
Executes all tasks from the agent_task_assignments.json file.

```python
def execute_all_tasks(dynamic=False, output_dir=None, by_agent=None, day=None):
    """
    Execute all tasks from the agent_task_assignments.json file.
    
    Args:
        dynamic: Whether to use dynamic workflow routing
        output_dir: Directory to save outputs to
        by_agent: Optional agent role to filter tasks by
        day: Optional day number to filter tasks by
        
    Returns:
        List of execution results
    """
```

### Advanced Features

#### Dependency Ordering
Tasks are executed in dependency order using topological sorting:

```python
def get_dependency_ordered_tasks():
    """
    Get all tasks ordered by dependencies (topological sort).
    
    Returns:
        List of tasks in dependency order
    """
```

#### Task Filtering
Tasks can be filtered by agent role or day:

```python
# Filter tasks by agent
all_tasks = [t for t in all_tasks if t["agent_role"] == by_agent]

# Filter tasks by day
all_tasks = [t for t in all_tasks if t["day"] == day]
```

## Configuration Structure (`graph/critical_path.json`)

The workflow is defined in a JSON configuration file with the following structure:

```json
{
  "nodes": [
    {
      "id": "product_manager",
      "agent": "product",
      "depends_on": []
    },
    {
      "id": "technical_architect",
      "agent": "technical",
      "depends_on": ["product_manager"]
    },
    {
      "id": "backend_engineer",
      "agent": "backend",
      "depends_on": ["technical_architect"]
    },
    {
      "id": "frontend_engineer",
      "agent": "frontend",
      "depends_on": ["technical_architect"]
    }
  ]
}
```

Each node has:
- **id**: Unique identifier for the node
- **agent**: The agent role to use for this node
- **depends_on**: List of node IDs that this node depends on

## Conditional Routing

The advanced workflow implementation supports conditional routing based on task status:

```python
def status_based_router(state):
    status = state.get("status")
    agent = state.get("agent", "")
    task_id = state.get("task_id", "UNKNOWN")
    
    # Route based on status
    if status == TaskStatus.BLOCKED:
        return "coordinator"
    elif status == TaskStatus.HUMAN_REVIEW:
        return "human_review"
    # ...other status-based routing
```

This enables the workflow to dynamically adapt based on task progress and outcomes.

## Usage Examples

### Run a Single Task

```bash
python orchestration/execute_workflow.py --task BE-07
```

### Run All Tasks

```bash
python orchestration/execute_workflow.py --all
```

### Run Tasks for a Specific Agent

```bash
python orchestration/execute_workflow.py --agent backend_engineer
```

### Run Tasks for a Specific Day

```bash
python orchestration/execute_workflow.py --day 2
```

### Use Dynamic Workflow Routing

```bash
python orchestration/execute_workflow.py --all --dynamic
```

### Custom Output Directory

```bash
python orchestration/execute_workflow.py --all --output "reports/sprint1"
```

## Diagram

The workflow can be visualized using the built-in visualization feature:

```python
workflow = build_workflow_graph()
workflow.visualize("critical_path_graph.png")
```

This generates a diagram showing all nodes and their dependencies.

## Common Patterns

### Running Tasks in Order

The system automatically determines the correct execution order based on dependencies.

### Handling Task Output

Each task execution generates a result that can be passed to dependent tasks.

### Error Handling

When a task fails, the system records the error and continues with remaining tasks.

### Reporting

Execution results are saved to an output directory for later analysis.

## Integration with Agent Registry

The workflow integrates with the agent registry to dynamically create nodes from agent definitions:

```python
def get_agent(agent_role: str):
    return create_agent_instance(agent_role)
```

This allows for flexibility in agent implementation while maintaining a consistent workflow structure.