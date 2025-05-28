"""
Agent Delegation for the AI Agent System
Provides utilities for dynamically delegating tasks to appropriate agents.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from tools.memory_engine import get_relevant_context

from .registry import (create_agent_instance, get_agent_config,
                       get_agent_for_task)


def delegate_task(
    task_id: str,
    task_description: str,
    agent_id: Optional[str] = None,
    context: Optional[str] = None,
    relevant_files: Optional[List[str]] = None,
    memory_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Delegate a task to an agent.

    Args:
        task_id: Unique identifier for the task
        task_description: Description of the task
        agent_id: Optional identifier of the agent to handle the task
        context: Optional context for the task
        relevant_files: Optional list of files relevant to the task
        memory_config: Optional memory configuration for the agent

    Returns:
        The result of the task execution
    """
    # If no agent ID is provided, infer it from the task ID
    if agent_id is None:
        agent = get_agent_for_task(task_id, memory_config=memory_config)
        # Get agent_id from task prefix
        agent_id = task_id.split("-")[0]
    else:
        agent = create_agent_instance(agent_id, memory_config=memory_config)

    # Get context if not provided
    if context is None:
        context = get_relevant_context(task_description)

    # Prepare file references string if available
    file_references = ""
    if relevant_files:
        file_references = "\n".join([f"- {file}" for file in relevant_files])

    # Execute the task with the agent
    try:
        result = agent.execute({
            "task_id": task_id,
            "task_description": task_description,
            "context": context,
            "file_references": file_references
        })

        # Add agent_id to the result if it's not already there
        if isinstance(result, dict) and "agent_id" not in result:
            result["agent_id"] = agent_id

        # Save output
        save_task_output(task_id, result)

        return result
    except Exception as e:
        # Log the exception (in a real system we'd have proper logging)
        print(f"Error executing task {task_id}: {str(e)}")
        # Propagate the exception for proper error handling
        raise


def save_task_output(task_id: str, output: Any) -> str:
    """
    Save the output of a task to a file.

    Args:
        task_id: Unique identifier for the task
        output: The result of the task execution

    Returns:
        Path to the saved output file
    """
    # Create outputs directory if it doesn't exist
    outputs_dir = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)

    # Format timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create filename
    filename = f"{task_id}_{timestamp}.txt"
    file_path = os.path.join(outputs_dir, filename)

    # Write output to file
    with open(file_path, 'w') as f:
        f.write(str(output))

    return file_path
