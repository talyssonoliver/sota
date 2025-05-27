"""
LangGraph Flow Definition
This module defines the LangGraph workflow with conditional edges for human checkpoints.
"""

from typing import Any, Dict

from langgraph.graph import StateGraph

from graph.handlers import (backend_handler, coordinator_handler,
                            documentation_handler, frontend_handler,
                            human_review_handler, qa_handler,
                            technical_handler)
from orchestration.states import TaskStatus


def status_router(state: Dict[str, Any]) -> str:
    """
    Routes the workflow based on the current task status.

    Args:
        state: The current workflow state

    Returns:
        The next node to route to
    """
    from orchestration.states import TaskStatus

    status = state.get("status", TaskStatus.CREATED)

    # Convert string to TaskStatus if needed
    if isinstance(status, str):
        try:
            status = TaskStatus(status)
        except ValueError:
            status = TaskStatus.CREATED

    # Define routing logic based on status
    routing = {
        TaskStatus.CREATED: "coordinator",
        TaskStatus.PLANNED: "technical",
        TaskStatus.IN_PROGRESS: get_implementation_agent(state),
        TaskStatus.QA_PENDING: "qa",
        TaskStatus.DOCUMENTATION: "documentation",
        TaskStatus.HUMAN_REVIEW: "human_review",
        TaskStatus.DONE: None,  # Terminal state
        TaskStatus.BLOCKED: None  # Terminal state
    }

    next_node = routing.get(status, "coordinator")
    if next_node is None:
        return "coordinator"  # Default to coordinator if None is returned

    return next_node


def get_implementation_agent(state: Dict[str, Any]) -> str:
    """
    Determine which implementation agent to use based on task metadata.

    Args:
        state: The current workflow state

    Returns:
        The appropriate implementation agent
    """
    task_id = state.get("task_id", "")

    # Default to backend for demo
    # In a real implementation, this would check the task metadata
    if task_id.startswith("FE-"):
        return "frontend"
    else:
        return "backend"


def build_workflow_graph() -> StateGraph:
    """
    Build the LangGraph workflow with human checkpoint integration.

    Returns:
        The configured LangGraph StateGraph
    """
    # Define the state schema
    from typing import Optional, TypedDict

    class WorkflowState(TypedDict):
        task_id: str
        message: str
        status: Optional[str]
        result: Optional[str]

    # Initialize the graph with the state schema
    workflow = StateGraph(state_schema=WorkflowState)

    # Add nodes for each agent handler
    workflow.add_node("coordinator", coordinator_handler)
    workflow.add_node("technical", technical_handler)
    workflow.add_node("backend", backend_handler)
    workflow.add_node("frontend", frontend_handler)
    workflow.add_node("qa", qa_handler)
    workflow.add_node("documentation", documentation_handler)
    workflow.add_node("human_review", human_review_handler)

    # Add conditional edges based on the router
    workflow.add_conditional_edges("coordinator", status_router)
    workflow.add_conditional_edges("technical", status_router)
    workflow.add_conditional_edges("backend", status_router)
    workflow.add_conditional_edges("frontend", status_router)
    workflow.add_conditional_edges("qa", status_router)
    workflow.add_conditional_edges("documentation", status_router)
    workflow.add_conditional_edges("human_review", status_router)

    # Set entry point
    workflow.set_entry_point("coordinator")

    return workflow


def execute_workflow(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the workflow with the given initial state.

    Args:
        state: The initial workflow state

    Returns:
        The final workflow state
    """
    graph = build_workflow_graph()
    app = graph.compile()

    # Execute the graph
    result = app.invoke(state)
    return result
