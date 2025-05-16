"""
Agent Execution Handlers for LangGraph Workflow
Implements execution wrappers for agents with status management.
"""

from typing import Dict, Any
from orchestration.registry import create_agent_instance
from orchestration.states import TaskStatus
from utils.review import is_review_approved
import logging
from pythonjsonlogger import jsonlogger

# Configure structured JSON logging for production
logger = logging.getLogger("agent_handlers")
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(agent)s %(task_id)s %(event)s')
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def coordinator_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Coordinator agent that manages task planning.
    
    Args:
        state: The current workflow state
    
    Returns:
        Updated state with coordinator output and next status
    """
    agent = create_agent_instance("coordinator")
    task_id = state.get("task_id", "UNKNOWN")
    logger.info("Coordinator handler invoked", extra={"agent": "coordinator", "task_id": task_id, "event": "handler_invoked"})
    
    # Add custom instructions for the coordinator
    input_state = state.copy()
    input_state["message"] = f"Plan execution for task {task_id}: {state.get('message', '')}"
    
    try:
        result = agent.run(input_state)
        
        # Check if result is a dictionary, if not convert to one
        if not isinstance(result, dict):
            result = {"output": result}
            
        # Add status information
        result["status"] = TaskStatus.PLANNED
        result["agent"] = "coordinator"
        result["task_id"] = task_id
        
        # Combine with previous state to preserve context
        result.update({k: v for k, v in state.items() if k not in result})
        
        return result
    except Exception as e:
        return {
            "status": TaskStatus.BLOCKED,
            "agent": "coordinator",
            "task_id": task_id,
            "error": str(e),
            "output": f"Failed to plan task: {str(e)}"
        }


def technical_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Technical Architect agent.
    
    Args:
        state: The current workflow state
    
    Returns:
        Updated state with technical output and next status
    """
    agent = create_agent_instance("technical")
    task_id = state.get("task_id", "UNKNOWN")
    logger.info("Technical handler invoked", extra={"agent": "technical", "task_id": task_id, "event": "handler_invoked"})
    
    try:
        result = agent.run(state)
        
        if not isinstance(result, dict):
            result = {"output": result}
            
        # Add status information
        result["status"] = TaskStatus.IN_PROGRESS
        result["agent"] = "technical"
        result["task_id"] = task_id
        
        # Preserve context
        result.update({k: v for k, v in state.items() if k not in result})
        
        return result
    except Exception as e:
        return {
            "status": TaskStatus.BLOCKED,
            "agent": "technical",
            "task_id": task_id,
            "error": str(e),
            "output": f"Technical architecture implementation failed: {str(e)}"
        }


def backend_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Backend Engineer agent.
    
    Args:
        state: The current workflow state
    
    Returns:
        Updated state with backend output and next status
    """
    agent = create_agent_instance("backend")
    task_id = state.get("task_id", "UNKNOWN")
    logger.info("Backend handler invoked", extra={"agent": "backend", "task_id": task_id, "event": "handler_invoked"})
    
    try:
        result = agent.run(state)
        
        if not isinstance(result, dict):
            result = {"output": result}
            
        # Add status information
        result["status"] = TaskStatus.QA_PENDING
        result["agent"] = "backend"
        result["task_id"] = task_id
        
        # Preserve context
        result.update({k: v for k, v in state.items() if k not in result})
        
        return result
    except Exception as e:
        return {
            "status": TaskStatus.BLOCKED,
            "agent": "backend",
            "task_id": task_id,
            "error": str(e),
            "output": f"Backend implementation failed: {str(e)}"
        }


def frontend_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Frontend Engineer agent.
    
    Args:
        state: The current workflow state
    
    Returns:
        Updated state with frontend output and next status
    """
    agent = create_agent_instance("frontend")
    task_id = state.get("task_id", "UNKNOWN")
    logger.info("Frontend handler invoked", extra={"agent": "frontend", "task_id": task_id, "event": "handler_invoked"})
    
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
        
        return result
    except Exception as e:
        return {
            "status": TaskStatus.BLOCKED,
            "agent": "frontend",
            "task_id": task_id,
            "error": str(e),
            "output": f"Frontend implementation failed: {str(e)}"
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
    logger.info("QA handler invoked", extra={"agent": "qa", "task_id": task_id, "event": "handler_invoked"})
    
    try:
        # Simulate QA testing
        # In a real implementation, this would run actual tests against the codebase
        
        # For demonstration purposes, always move to human review
        # In a real implementation, this might be conditional
        from handlers.qa_handler import qa_agent
        
        # Pass through to our QA agent implementation
        return qa_agent(state)
        
    except Exception as e:
        return {
            "status": TaskStatus.BLOCKED,
            "agent": "qa",
            "task_id": task_id,
            "error": str(e),
            "output": f"QA testing failed: {str(e)}"
        }


def documentation_handler(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the Documentation agent.
    
    Args:
        state: The current workflow state
    
    Returns:
        Updated state with documentation output and DONE status
    """
    agent = create_agent_instance("documentation")
    task_id = state.get("task_id", "UNKNOWN")
    logger.info("Documentation handler invoked", extra={"agent": "documentation", "task_id": task_id, "event": "handler_invoked"})
    
    try:
        result = agent.run(state)
        
        if not isinstance(result, dict):
            result = {"output": result}
            
        # Add status information
        result["status"] = TaskStatus.DONE
        result["agent"] = "documentation"
        result["task_id"] = task_id
        
        # Preserve context
        result.update({k: v for k, v in state.items() if k not in result})
        
        return result
    except Exception as e:
        return {
            "status": TaskStatus.BLOCKED,
            "agent": "documentation",
            "task_id": task_id,
            "error": str(e),
            "output": f"Documentation generation failed: {str(e)}"
        }


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
    logger.info("Human review handler invoked", extra={"agent": "human_review", "task_id": task_id, "event": "handler_invoked"})
    
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