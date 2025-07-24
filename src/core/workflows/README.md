# Core Workflows Directory

## Purpose
This directory contains **library interfaces and core workflow abstractions** for the AI system. These implementations provide programmatic APIs for workflow operations without CLI dependencies.

## When to Use This Directory
- Importing workflow functionality as a library
- Building integrations with other systems
- Creating new workflow implementations
- Testing workflow logic programmatically
- Minimal dependency requirements

## Key Components

### Core Abstractions
- `states.py` - Core workflow state definitions and WorkflowState class
- `__init__.py` - Clean module exports and imports

### Workflow Interfaces
- `execute_workflow.py` - Workflow execution interface
- `execute_task.py` - Task execution interface
- `task_lifecycle.py` - Task lifecycle interface

### Integration Points
- `langgraph_qa_integration.py` - LangGraph integration for QA workflows
- `automation_health_check.py` - Automated health monitoring
- `delegation.py` - Task delegation interfaces

### Simplified Implementations
Most files in this directory are **simplified versions** (0.5-2KB) that provide:
- Clean API interfaces
- Minimal dependencies
- Easy integration points
- Testable abstractions

## Example Usage

```python
# Import as a library
from src.core.workflows import execute_workflow
from src.core.workflows.states import TaskStatus, WorkflowState

# Create workflow state
state = WorkflowState()
state.current_task = "BE-01"
state.status = TaskStatus.IN_PROGRESS

# Execute workflow programmatically
result = execute_workflow(state)
```

## Architecture Notes
- These are **library interfaces** for programmatic use
- Average file size: 0.5-2KB (minimal implementations)
- No CLI dependencies or interactive features
- Designed for import and API usage

## Relationship to orchestration/
The `orchestration/` directory contains the **full production implementations** of these interfaces. 

Use this `src/core/workflows/` directory when you need:
- Clean library imports
- Minimal dependencies
- API-style access
- Integration building blocks

Use `orchestration/` when you need:
- Command-line execution
- Full feature implementations
- Interactive workflows
- Production deployment

## Future Development
When adding new workflows:
1. Create the interface/abstraction here first
2. Implement the full version in `orchestration/`
3. Keep the separation of concerns clear
4. Document both versions appropriately