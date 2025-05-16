# Task Orchestration

This document describes the task orchestration system in the AI Agent System, which coordinates task execution across agents.

## Overview

The task orchestration system manages the execution of tasks by different agents, ensuring that tasks are assigned to the appropriate agents, dependencies are respected, and task states are properly managed throughout the workflow. It provides a robust framework for automated AI agent collaboration with human-in-the-loop capabilities when needed.

## Components

### Task Registry

The task registry maintains information about available tasks, their dependencies, and assignments:

- Located in `tasks/` directory as individual YAML files (e.g., `BE-07.yaml`)
- Maps agent roles to their assigned tasks through the `owner` field
- Includes task metadata (ID, title, description, dependencies, etc.)
- Supports task filtering by priority, owner, and dependency order

### Task Metadata System

The Task Metadata system provides a structured way to define tasks with rich metadata:

- **Directory**: `tasks/` contains individual YAML files per task
- **Schema**: Each file follows a standard schema with fields like `id`, `title`, `owner`, etc.
- **Loader**: `utils/task_loader.py` provides utilities for loading and managing task metadata

#### Task Metadata Schema

```yaml
id: BE-07                   # Unique task identifier
title: "Task Title"         # Short description
owner: backend              # Agent role assigned
depends_on:                 # Task-level dependencies
  - TL-09
  - BE-01
state: PLANNED              # Lifecycle state (CREATED, PLANNED, etc.)
priority: HIGH              # Execution urgency (HIGH, MEDIUM, LOW)
estimation_hours: 3         # Effort estimate
description: >              # Rich content for prompt/context enrichment
  Detailed task description with instructions and requirements.
artefacts:                  # Files or directories to be modified
  - lib/services/customerService.ts
  - tests/unit/services/
context_topics:             # Specific memory documents to include
  - db-schema
  - service-pattern
```

#### Task Loader API

```python
# Load task metadata from YAML file
from utils.task_loader import load_task_metadata
task_meta = load_task_metadata("BE-07")

# Get all available tasks
from utils.task_loader import get_all_tasks
all_tasks = get_all_tasks()

# Update task state
from utils.task_loader import update_task_state
update_task_state("BE-07", "IN_PROGRESS")

# Get tasks in a specific state
from utils.task_loader import get_tasks_by_state
in_progress_tasks = get_tasks_by_state("IN_PROGRESS")

# Get tasks that depend on a given task
from utils.task_loader import get_dependent_tasks
dependent_tasks = get_dependent_tasks("TL-09")
```

### Agent Registry

The agent registry maps agent roles to their implementation functions:

- Implemented in `orchestration/registry.py`
- Provides functions to get agent instances by role or task prefix (`create_agent_instance`, `get_agent_for_task`)
- Handles agent configuration and tool loading
- Maintains agent capabilities and specializations

### Task Executor

The task executor runs individual tasks through the appropriate agent:

- Implemented in `orchestration/execute_task.py`
- Provides command-line interface for executing specific tasks
- Handles collecting task inputs and processing outputs
- Supports loading tasks from YAML files in the `tasks/` directory or from command-line arguments
- Automatically updates task state after execution

### Workflow Executor

The workflow executor runs tasks through the LangGraph workflow:

- Implemented in `orchestration/execute_workflow.py` and `orchestration/execute_graph.py`
- Supports executing single tasks or batches of tasks
- Manages task dependencies and execution order with topological sorting
- Generates execution reports and detailed summaries
- Supports filtering tasks by agent role or priority
- Provides multiple workflow types (standard, dynamic, state-based, advanced)
- Now integrates with the Task Metadata system for richer context

### Agent Handlers

Agent handlers manage the interaction between agents in the workflow:

- Implemented in `graph/handlers.py`
- Wrap agent execution with state management
- Handle task status transitions
- Provide error handling and context preservation
- Include specialized handlers for each agent role:
  - `coordinator_handler`
  - `technical_handler`
  - `backend_handler`
  - `frontend_handler`
  - `qa_handler`
  - `documentation_handler`
  - `human_review_handler`

### Task Lifecycle States

Task lifecycle states define the possible states a task can be in and the transitions between them:

- Implemented in `orchestration/states.py` using the `TaskStatus` enum
- Define a comprehensive set of states (CREATED, PLANNED, IN_PROGRESS, etc.)
- Provide utility functions for state transitions and validation
- Support dynamic workflow routing based on task state

## Task Structure

Tasks are structured with the following information in YAML format:

```yaml
id: BE-07
title: Implement Missing Service Functions
owner: backend
depends_on:
  - TL-09
  - BE-01
state: PLANNED
priority: HIGH
estimation_hours: 3
description: >
  Implement CRUD service logic for customers and orders in the Supabase backend.
  Follow project service-layer pattern and error handling utilities.
artefacts:
  - lib/services/customerService.ts
  - lib/services/orderService.ts
  - tests/unit/services/
context_topics:
  - db-schema
  - service-pattern
  - supabase-setup
```

## Task Lifecycle States

Tasks progress through a well-defined lifecycle represented by the following states:

### State Definitions

- **CREATED**: Task is created but not yet started
- **PLANNED**: Task is planned and ready to be worked on
- **IN_PROGRESS**: Task is currently being worked on
- **QA_PENDING**: Task is completed and waiting for QA
- **DOCUMENTATION**: Task has passed QA and needs documentation
- **HUMAN_REVIEW**: Task requires human review before proceeding
- **DONE**: Task is completed and passed all checks
- **BLOCKED**: Task is blocked by an issue

### State Transitions

Task states transition based on agent actions and task outcomes:

```
CREATED → PLANNED (via Coordinator)
PLANNED → IN_PROGRESS (via Technical)
IN_PROGRESS → QA_PENDING (via Backend/Frontend)
QA_PENDING → DOCUMENTATION (via QA, if passed)
QA_PENDING → BLOCKED (via QA, if failed)
DOCUMENTATION → DONE (via Documentation)
HUMAN_REVIEW → PLANNED/IN_PROGRESS/DONE (based on review outcome)
Any state → BLOCKED (on error)
BLOCKED → PLANNED (via Coordinator, after fixing)
```

### Agent-State Mapping

Different agents are responsible for transitioning tasks between specific states:

- **Coordinator**: CREATED → PLANNED, BLOCKED → PLANNED
- **Technical**: PLANNED → IN_PROGRESS
- **Backend/Frontend**: IN_PROGRESS → QA_PENDING
- **QA**: QA_PENDING → DOCUMENTATION or BLOCKED
- **Documentation**: DOCUMENTATION → DONE
- **Human Reviewer**: HUMAN_REVIEW → (various states based on review)

## Task Execution Flow

1. **Task Selection**: A task is selected for execution (manually or by the system)
2. **Task Metadata Loading**: The system loads the task metadata from its YAML file
3. **Dependency Resolution**: The system checks if all dependencies are satisfied using topological sorting
4. **Context Loading**: The system loads relevant context based on `context_topics` specified in the task metadata
5. **Agent Selection**: The appropriate agent is selected based on the `owner` field in the task metadata
6. **Task Execution**: The agent executes the task through its handler with enriched context
7. **State Transition**: The task state is updated in the YAML file with the new state
8. **Conditional Routing**: The next agent is selected based on the new task state
9. **Result Recording**: The task result is recorded and shared with dependent tasks
10. **Human Review** (if required): Task is flagged for human review at critical checkpoints

## Task Delegation System

The task delegation system dynamically assigns tasks to appropriate agents and manages their execution:

- Implemented in `orchestration/delegation.py`
- Automatically selects the best agent for a task based on task type and agent capabilities
- Gathers relevant context from task metadata and the memory engine
- Handles passing file references and task details to agents
- Manages task output storage and retrieval

### Delegation Functions

```python
def delegate_task(
    task_id: str,
    task_description: str,
    agent_id: Optional[str] = None,
    context: Optional[str] = None,
    relevant_files: Optional[List[str]] = None,
    memory_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Delegate a task to an appropriate agent.
    
    Args:
        task_id: The task identifier (e.g. BE-07)
        task_description: Description of the task to execute
        agent_id: Optional specific agent to use (if None, best agent is selected)
        context: Optional context to include with the task
        relevant_files: Optional list of files relevant to the task
        memory_config: Optional configuration for the memory engine
        
    Returns:
        The result of the task execution
    """
```

### Output Management

The delegation system handles task output management through functions like:

```python
def save_task_output(task_id: str, output: Any) -> str:
    """
    Save task output to a standardized location.
    
    Args:
        task_id: The task identifier
        output: The output data to save
        
    Returns:
        Path to the saved output
    """
```

## Running Tasks

Tasks can be executed in several ways:

### Individual Task Execution

```bash
# Execute a task using its YAML metadata
python orchestration/execute_task.py --task BE-07

# Update task state after execution
python orchestration/execute_task.py --task BE-07 --update-state IN_PROGRESS
```

### Workflow Execution

```bash
# Execute a task with verbose output showing metadata
python orchestration/execute_graph.py --task BE-07 --verbose
```

### Batch Execution

```bash
python orchestration/execute_workflow.py --all
```

### Filtered Execution

```bash
# By agent
python orchestration/execute_workflow.py --agent backend_engineer

# By day
python orchestration/execute_workflow.py --day 2
```

### Advanced Workflow Execution

To use the advanced workflow with stateful transitions:

```bash
python orchestration/execute_workflow.py --task BE-07 --workflow advanced
```

### Workflow Types

The system supports multiple types of workflows:

- **Standard Workflow**: Basic workflow for sequential task execution
  ```bash
  python orchestration/execute_workflow.py --task BE-07
  ```

- **Dynamic Workflow**: Uses dynamic routing based on task state
  ```bash
  python orchestration/execute_workflow.py --task BE-07 --workflow dynamic
  ```

- **State-based Workflow**: Uses explicit state management with state workflow graphs
  ```bash
  python orchestration/execute_workflow.py --task BE-07 --workflow state
  ```

- **Advanced Workflow**: Uses explicit agent-to-agent protocols with more complex transitions
  ```bash
  python orchestration/execute_workflow.py --task BE-07 --workflow advanced
  ```

### Output Directory Customization

Specify a custom output directory for execution reports:

```bash
python orchestration/execute_workflow.py --task BE-07 --output "reports/sprint2"
```

## Dependency Management

The system manages task dependencies through topological sorting:

```python
def get_dependency_ordered_tasks():
    """
    Get all tasks ordered by dependencies (topological sort).
    
    Returns:
        List of tasks in dependency order
    """
    all_tasks = get_all_tasks_flattened()
    
    # Create a mapping from task ID to task
    task_map = {task["id"]: task for task in all_tasks}
    
    # Build dependency graph
    graph = {task["id"]: set(task.get("dependencies", [])) for task in all_tasks}
    
    # Topological sort implementation
    # ...
```

## State Management Functions

The orchestration system provides several utility functions for state management:

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

## Results Management

Task results are saved to the outputs directory and include:

- Task ID and title
- Agent that executed the task
- Task status and transitions
- Execution status (COMPLETED, ERROR, etc.)
- Result content and output files
- Timestamps for tracking performance
- Error messages (if applicable)

Results are automatically saved as JSON files for both individual tasks and batch executions:
- Individual task: `outputs/{task_id}/workflow_result.json`
- Batch execution: `outputs/batch_{timestamp}/execution_summary.json`

## Integration with Daily Cycles

The orchestration system integrates with daily cycles to organize work:

```bash
# Start a day's workflow
python orchestration/daily_cycle.py --day 1 --start

# End a day and generate reports
python orchestration/daily_cycle.py --day 1 --end
```

Daily workflow operations include:
- Filtering tasks for the current day
- Generating morning briefings for teams
- Creating individual worklists
- Triggering LangGraph workflows for ready tasks
- Generating evening reports and updating dashboards

## Human-in-the-Loop (HITL) Integration

The system supports human review at critical checkpoints:

- Special `HUMAN_REVIEW` state for tasks that require manual review
- Configurable review triggers via `requires_human_review: true` in task definitions
- Review portal to display task details, agent outputs, and QA findings
- Command-line interface for human review:
  ```bash
  python orchestration/review_task.py BE-07
  ```

## Integration with Prompt Generation

Task metadata is used to enrich agent prompts:

```bash
# Generate a prompt for a specific task
python orchestration/generate_prompt.py --task BE-07 --agent backend-agent --verbose
```

The prompt generator will:
1. Load task metadata from the YAML file
2. Retrieve relevant context based on `context_topics` field
3. Fill prompt template with task metadata (title, description, etc.)
4. Generate a comprehensive prompt for the agent

## Benefits of Task Metadata System

- **Structured Task Definitions**: Each task has a clear, structured definition
- **Modular Context**: Task-specific context can be defined in the metadata
- **Rich Prompt Generation**: Task metadata enriches agent prompts for better results
- **State Tracking**: Task state is stored directly in the metadata file
- **Human Readability**: YAML files are easy to read and modify
- **Dependency Management**: Clear dependency specification and tracking
- **Workflow Integration**: Metadata drives workflow execution and routing
- **Dashboard Generation**: Metadata can be used to generate task dashboards

## Best Practices

1. **Use Standard Schema**: Follow the standard task schema for consistency
2. **Include Context Topics**: Specify relevant context topics for each task
3. **List Artefacts**: Include files that will be modified by the task
4. **Realistic Estimations**: Provide realistic estimation hours
5. **Clear Dependencies**: Specify all dependencies accurately
6. **Descriptive Titles**: Use clear, descriptive task titles
7. **Detailed Descriptions**: Provide detailed task descriptions
8. **Regular State Updates**: Keep task state updated during execution
9. **Proper Owner Assignment**: Assign tasks to the appropriate agent role
10. **Priority Setting**: Set appropriate task priorities