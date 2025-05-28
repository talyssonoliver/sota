"""
LangGraph Workflow Builder
Constructs various LangGraph workflow configurations for agent orchestration.
"""

import json
import os
from typing import Any, Callable, Dict, List, Optional

import yaml
from langchain.agents import AgentType
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.graph import Graph, StateGraph

from graph.handlers import (backend_handler, coordinator_handler,
                            documentation_handler, frontend_handler,
                            human_review_handler, qa_handler,
                            technical_handler)
from orchestration.registry import create_agent_instance, get_agent
from orchestration.states import (TaskStatus, get_next_status,
                                  get_valid_transitions)


def load_graph_config() -> Dict[str, Any]:
    """
    Load the graph configuration from critical_path.json

    Returns:
        Dict containing the graph configuration
    """
    config_path = os.path.join(os.path.dirname(__file__), "critical_path.json")

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to a default configuration
        return {
            "nodes": [
                {"id": "coordinator", "agent": "coordinator", "depends_on": []},
                {"id": "backend", "agent": "backend",
                    "depends_on": ["coordinator"]},
                {"id": "qa", "agent": "qa", "depends_on": ["backend"]},
                {"id": "doc", "agent": "documentation", "depends_on": ["qa"]}
            ]
        }


def build_workflow_graph() -> StateGraph:
    """
    Build a simple workflow graph based on the configuration in critical_path.json.

    Returns:
        A compiled StateGraph object with support for multiple edges
    """
    config = load_graph_config()

    # Define a state schema for the graph
    from typing import Optional as Opt
    from typing import TypedDict

    class WorkflowState(TypedDict, total=False):
        task_id: str
        agent: str
        output: str
        status: TaskStatus
        error: Opt[str]

    workflow = StateGraph(state_schema=WorkflowState)

    # Create a mapping from agent roles to node IDs
    agent_nodes = {}

    # First pass: Add all nodes
    for node in config["nodes"]:
        node_id = node["id"]
        agent_role = node["agent"]
        agent_nodes[node_id] = agent_role

        # Handle specific agents with predefined handlers
        handler_map = {
            "coordinator": coordinator_handler,
            "technical": technical_handler,
            "backend": backend_handler,
            "frontend": frontend_handler,
            "qa": qa_handler,
            "documentation": documentation_handler,
            "human_review": human_review_handler
        }

        if agent_role in handler_map:
            workflow.add_node(node_id, handler_map[agent_role])
        else:
            # Create a wrapper function for the agent
            def create_agent_node(role=agent_role):
                def node_function(state):
                    agent = get_agent(role)
                    result = agent.run(state)

                    # Ensure result is a dictionary with task_id preserved
                    if isinstance(result, dict):
                        if "task_id" not in result and "task_id" in state:
                            result["task_id"] = state["task_id"]
                        return result
                    else:
                        # Convert simple results to dict format
                        return {
                            "output": result,
                            "task_id": state.get("task_id", "UNKNOWN"),
                            "agent": role
                        }
                return node_function

            # Add the node to the graph
            workflow.add_node(node_id, create_agent_node())

    # Second pass: Add conditional edges to handle multiple paths
    for node in config["nodes"]:
        node_id = node["id"]
        depends_on = node["depends_on"]

        if depends_on:
            # Create a routing function that directs to the appropriate
            # dependency
            def create_router(deps=depends_on):
                def router(state):
                    # For simple routing, just use the first dependency
                    # In a real implementation, you'd have logic to choose the
                    # correct path
                    return deps[0]
                return router

            # Create destinations dictionary with actual node targets
            destinations = {}
            for dep in depends_on:
                destinations[dep] = dep
            # Add END as a potential destination for terminal states
            destinations[END] = END

            workflow.add_conditional_edges(
                node_id,
                create_router(),
                destinations
            )
        else:
            # For terminal nodes, add a direct edge to END
            workflow.add_edge(node_id, END)

    # Set the entry point
    entry_nodes = [node["id"]
                   for node in config["nodes"] if not node["depends_on"]]
    if entry_nodes:
        workflow.set_entry_point(entry_nodes[0])
    else:
        # Default to coordinator if no clear entry point
        workflow.set_entry_point("coordinator")

    return workflow.compile()


def build_state_workflow_graph() -> StateGraph:
    """
    Build a stateful workflow graph with conditional edges based on task status.

    Returns:
        A compiled StateGraph object
    """
    config = load_graph_config()

    # Define a state schema for the graph
    from typing import Optional as Opt
    from typing import TypedDict

    class WorkflowState(TypedDict, total=False):
        task_id: str
        agent: str
        output: str
        status: TaskStatus
        error: Opt[str]

    workflow = StateGraph(state_schema=WorkflowState)

    # Create a mapping from node IDs to agent roles
    agent_nodes = {}

    # First pass: Add all nodes with proper agent handlers
    for node in config["nodes"]:
        node_id = node["id"]
        agent_role = node["agent"]
        agent_nodes[node_id] = agent_role

        # Set up the appropriate handler based on agent role
        handler_map = {
            "coordinator": coordinator_handler,
            "technical": technical_handler,
            "backend": backend_handler,
            "frontend": frontend_handler,
            "qa": qa_handler,
            "documentation": documentation_handler
        }

        if agent_role in handler_map:
            workflow.add_node(node_id, handler_map[agent_role])
        else:
            # Generic handler for other roles
            def generic_handler(role=agent_role):
                def handler_fn(state):
                    agent = get_agent(role)
                    result = agent.run(state)

                    if not isinstance(result, dict):
                        result = {"output": result}

                    result["agent"] = role
                    result["task_id"] = state.get("task_id", "UNKNOWN")
                    result["status"] = TaskStatus.IN_PROGRESS

                    result.update(
                        {k: v for k, v in state.items() if k not in result})
                    return result
                return handler_fn

            workflow.add_node(node_id, generic_handler())

    # Add human review node if not present
    if "human_review" not in agent_nodes:
        workflow.add_node("human_review", human_review_handler)

    # Second pass: Add conditional edges based on status
    for node_id, agent_role in agent_nodes.items():
        if agent_role == "qa":
            # Define QA-specific routing based on status
            def qa_router(state):
                status = state.get("status")

                if status == TaskStatus.DOCUMENTATION:
                    return "doc"  # Route to documentation if QA passed
                elif status == TaskStatus.BLOCKED:
                    return "coordinator"  # Route back to coordinator if QA failed
                else:
                    return "human_review"  # Default to human review for uncertain cases

            workflow.add_conditional_edge(node_id, qa_router)
        elif agent_role == "coordinator":
            # Define coordinator routing based on task type
            def coordinator_router(state):
                task_id = state.get("task_id", "")
                status = state.get("status")

                if status == TaskStatus.BLOCKED:
                    return "human_review"
                    # Route based on task ID prefix
                if task_id.startswith("BE-"):
                    return "backend" if "backend" in agent_nodes.values() else "technical"
                elif task_id.startswith("FE-"):
                    return "frontend" if "frontend" in agent_nodes.values() else "technical"
                elif task_id.startswith("TL-"):
                    return "technical" if "technical" in agent_nodes.values() else "human_review"
                else:
                    # Default to technical for other task types if available,
                    # otherwise human_review
                    return "technical" if "technical" in agent_nodes.values() else "human_review"

            workflow.add_conditional_edge(node_id, coordinator_router)
        else:
            # Add standard edge for other nodes based on dependencies
            for node in config["nodes"]:
                if node["id"] == node_id:
                    continue  # Skip self

                if node_id in node["depends_on"]:
                    # This node is a dependency for another node
                    workflow.add_edge(node_id, node["id"])

    # Add catch-all status-based routing
    def status_router(state):
        status = state.get("status")

        if status == TaskStatus.BLOCKED:
            return "coordinator"
        elif status == TaskStatus.HUMAN_REVIEW:
            return "human_review"
        else:
            return None

    workflow.add_state_transition(status_router)

    # Set the entry point
    workflow.set_entry_point("coordinator")
    return workflow.compile()


def build_advanced_workflow_graph() -> StateGraph:
    """
    Build an advanced workflow graph with explicit A2A (Agent-to-Agent) edges.
    This implements a full Agent-to-Agent protocol with conditional routing
    and task-specific transitions based on task lifecycle states.

    Returns:
        A compiled StateGraph object with advanced conditional routing
    """
    # Define a state schema for the graph
    from typing import Optional as Opt
    from typing import TypedDict

    class WorkflowState(TypedDict, total=False):
        task_id: str
        agent: str
        output: str
        status: TaskStatus
        error: Opt[str]
        qa_result: Opt[str]

    workflow = StateGraph(state_schema=WorkflowState)

    # Add nodes with handlers for stateful transitions
    workflow.add_node("coordinator", coordinator_handler)
    workflow.add_node("technical", technical_handler)
    workflow.add_node("backend", backend_handler)
    workflow.add_node("frontend", frontend_handler)
    workflow.add_node("qa", qa_handler)
    workflow.add_node("doc", documentation_handler)
    workflow.add_node("human_review", human_review_handler)
    # Define status-based conditional routing with cycle detection

    def status_based_router(state):
        status = state.get("status")
        agent = state.get("agent", "")
        task_id = state.get("task_id", "UNKNOWN")

        # Track routing attempts to prevent infinite loops
        routing_history = state.get("routing_history", [])
        current_route = f"{agent}->{status}"

        # Check for potential infinite loops (same route repeated more than 3
        # times)
        if routing_history.count(current_route) >= 3:
            # Force completion to prevent infinite loops
            return END

        # Add current route to history
        routing_history.append(current_route)
        state["routing_history"] = routing_history

        # First, route based on explicit task status
        if status == TaskStatus.CREATED:
            return "coordinator"
        elif status == TaskStatus.PLANNED:
            # Route based on task type
            if task_id.startswith("BE-"):
                return "backend"
            elif task_id.startswith("FE-"):
                return "frontend"
            else:
                return "technical"
        elif status == TaskStatus.IN_PROGRESS:
            # For tasks in progress, route based on task type
            if task_id.startswith("BE-"):
                return "backend"
            elif task_id.startswith("FE-"):
                return "frontend"
            else:
                return "technical"
        elif status == TaskStatus.QA_PENDING:
            return "qa"
        elif status == TaskStatus.DOCUMENTATION:
            return "doc"
        elif status == TaskStatus.HUMAN_REVIEW:
            return "human_review"
        elif status == TaskStatus.BLOCKED:
            return END  # End workflow for blocked tasks to prevent loops
        elif status in [TaskStatus.DONE, TaskStatus.COMPLETED]:
            return END

        # If no explicit status routing matched, use agent-based routing
        if agent == "coordinator":
            # Route coordinator output based on task type
            if task_id.startswith("BE-"):
                return "backend"
            elif task_id.startswith("FE-"):
                return "frontend"
            else:
                return "technical"
        elif agent == "technical":
            if task_id.startswith("BE-"):
                return "backend"
            elif task_id.startswith("FE-"):
                return "frontend"
            else:
                return "qa"
        elif agent in ["backend", "frontend"]:
            return "qa"
        elif agent == "qa":
            # QA results determine next step
            qa_result = state.get("qa_result", "")
            qa_retry_count = state.get("qa_retry_count", 0)

            if qa_result in ["passed", "approve", "correct"]:
                return "doc"
            else:
                # Limit QA retries to prevent infinite loops
                if qa_retry_count >= 2:
                    # Too many QA failures, escalate to human review
                    return "human_review"
                else:
                    # Increment retry count and send back for rework
                    state["qa_retry_count"] = qa_retry_count + 1
                    if task_id.startswith("BE-"):
                        return "backend"
                    elif task_id.startswith("FE-"):
                        return "frontend"
                    else:
                        return "coordinator"
        elif agent == "doc":
            return END
        elif agent == "human_review":
            return END

        # Default fallback - end workflow instead of routing to coordinator
        return END

    # Add explicit multi-path conditional edge for all nodes
    # Define all potential destinations, including END for terminal states
    all_destinations = {
        "coordinator": "coordinator",
        "technical": "technical",
        "backend": "backend",
        "frontend": "frontend",
        "qa": "qa",
        "doc": "doc",
        "human_review": "human_review",
        END: END  # Support for workflow termination
    }

    # Add conditional edges for each node
    workflow.add_conditional_edges(
        "coordinator", status_based_router, all_destinations)
    workflow.add_conditional_edges(
        "technical", status_based_router, all_destinations)
    workflow.add_conditional_edges(
        "backend", status_based_router, all_destinations)
    workflow.add_conditional_edges(
        "frontend", status_based_router, all_destinations)
    workflow.add_conditional_edges("qa", status_based_router, all_destinations)
    workflow.add_conditional_edges(
        "doc", status_based_router, all_destinations)
    workflow.add_conditional_edges(
        "human_review", status_based_router, all_destinations)

    # Add global state transition for handling blocked/error states
    def error_handler(state):
        if "error" in state:
            # Update state to reflect the error
            state["status"] = TaskStatus.BLOCKED
            return "coordinator"
        return None

    workflow.add_state_transition(error_handler)

    # Set entry point
    workflow.set_entry_point("coordinator")

    return workflow.compile()


def build_dynamic_workflow_graph(task_id: str = None) -> StateGraph:
    """
    Build a dynamic workflow graph that can adapt based on task requirements and status.

    Args:
        task_id: Optional task ID to customize the graph for a specific task

    Returns:
        A compiled StateGraph object with dynamic routing based on task lifecycle states
    """
    config = load_graph_config()

    # Define a state schema for the graph
    from typing import Optional as Opt
    from typing import TypedDict

    class WorkflowState(TypedDict, total=False):
        task_id: str
        agent: str
        output: str
        status: TaskStatus
        error: Opt[str]
        qa_result: Opt[str]
        next: Opt[str]

    workflow = StateGraph(state_schema=WorkflowState)

    # Handler map for standard handlers
    handler_map = {
        "coordinator": coordinator_handler,
        "technical": technical_handler,
        "backend": backend_handler,
        "frontend": frontend_handler,
        "qa": qa_handler,
        "documentation": documentation_handler,
        "doc": documentation_handler,
        "human_review": human_review_handler
    }

    # Ensure we have all the necessary nodes that might be referenced in the
    # router
    required_nodes = [
        "coordinator", "technical", "backend", "frontend", "qa", "doc",
        "human_review", "product_manager", "ux_designer"
    ]

    # Add all required nodes directly to the workflow
    for node_id in required_nodes:
        if node_id in handler_map:
            workflow.add_node(node_id, handler_map[node_id])
        else:
            # Create a generic handler for this role
            def create_generic_handler(role=node_id):
                def handler(state):
                    try:
                        agent = get_agent(role)
                        result = agent.run(state)

                        # Ensure result is a dictionary
                        if not isinstance(result, dict):
                            result = {"output": result}

                        # Set agent identifier and preserve task ID
                        result["agent"] = role
                        if "task_id" not in result and "task_id" in state:
                            result["task_id"] = state["task_id"]

                        # Update the status
                        current_status = state.get(
                            "status", TaskStatus.CREATED)
                        result["status"] = get_next_status(
                            current_status, role, True)

                        # Preserve other context from state
                        result.update(
                            {k: v for k, v in state.items() if k not in result})

                        return result
                    except Exception as e:
                        return {
                            "status": TaskStatus.BLOCKED,
                            "agent": role,
                            "task_id": state.get("task_id", "UNKNOWN"),
                            "error": str(e),
                            "output": f"{role} handler failed: {str(e)}"
                        }
                return handler

            workflow.add_node(node_id, create_generic_handler())

    # Create a dynamic router based on task type and current agent
    def dynamic_router(state):
        current_agent = state.get("agent", "")
        status = state.get("status", TaskStatus.CREATED)
        task = state.get("task_id", "")

        # First check if a specific next step was set
        if "next" in state:
            next_step = state["next"]
            # If next is "done", return END to terminate the workflow
            if next_step == "done" or next_step is None:
                return END
            return next_step

        # Route based on task status
        if status == TaskStatus.BLOCKED:
            return "coordinator"
        elif status == TaskStatus.HUMAN_REVIEW:
            return "human_review"
        elif status == TaskStatus.DONE:
            return END

        # Route based on agent and task type
        if current_agent == "coordinator":
            if task.startswith("BE-"):
                return "backend"
            elif task.startswith("FE-"):
                return "frontend"
            else:
                return "technical"
        elif current_agent == "technical":
            if task.startswith("BE-"):
                return "backend"
            elif task.startswith("FE-"):
                return "frontend"
            else:
                return "qa"
        elif current_agent in ["backend", "frontend"]:
            return "qa"
        elif current_agent == "qa":
            return "doc"
        elif current_agent == "doc" or current_agent == "documentation":
            return END  # End of workflow
        elif current_agent == "product_manager":
            # End of workflow        elif current_agent == "ux_designer":
            return END
            return END  # End of workflow

        # Default fallback - end workflow to prevent infinite loops
        return END

    # Add conditional edges for all nodes
    # Define all potential destinations with valid target values
    all_destinations = {
        "coordinator": "coordinator",
        "technical": "technical",
        "backend": "backend",
        "frontend": "frontend",
        "qa": "qa",
        "doc": "doc",
        "human_review": "human_review",
        "product_manager": "product_manager",
        "ux_designer": "ux_designer",
        END: END
    }

    # Add conditional edges for all required nodes
    for node_id in required_nodes:
        workflow.add_conditional_edges(
            node_id, dynamic_router, all_destinations)

    # Set the entry point (always coordinator)
    workflow.set_entry_point("coordinator")

    return workflow.compile()
