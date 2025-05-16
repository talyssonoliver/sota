"""
Task Execution with LangGraph Workflow
Runs a task through the agent workflow using the dynamically constructed LangGraph.
"""

import argparse
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set, Optional
import logging
from pythonjsonlogger import jsonlogger

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.graph_builder import (
    build_workflow_graph,
    build_dynamic_workflow_graph,
    build_state_workflow_graph,
    build_advanced_workflow_graph
)

# Configure structured JSON logging for production
logger = logging.getLogger("execute_workflow")
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(agent_role)s %(task_id)s %(event)s')
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def execute_task(task_id, input_message=None, workflow_type="standard", output_dir=None):
    """
    Execute a task through the agent workflow.
    
    Args:
        task_id: The task identifier (e.g. BE-07)
        input_message: Optional input message to include in the initial state
        workflow_type: Type of workflow to use (standard, dynamic, state, advanced)
        output_dir: Directory to save outputs to
    
    Returns:
        The result of the workflow execution
    """
    # Prepare the initial state
    initial_state = {
        "task_id": task_id,
        "message": input_message or f"Execute task {task_id}",
        "timestamp": datetime.now().isoformat(),
    }
    
    # Build the workflow based on the specified type
    if workflow_type == "dynamic":
        logger.info("Building dynamic workflow", extra={"task_id": task_id, "event": "build_workflow"})
        workflow = build_dynamic_workflow_graph(task_id)
    elif workflow_type == "state":
        logger.info("Building state-based workflow", extra={"task_id": task_id, "event": "build_workflow"})
        workflow = build_state_workflow_graph()
    elif workflow_type == "advanced":
        logger.info("Building advanced workflow", extra={"task_id": task_id, "event": "build_workflow"})
        workflow = build_advanced_workflow_graph()
    else:
        logger.info("Building standard workflow", extra={"task_id": task_id, "event": "build_workflow"})
        workflow = build_workflow_graph()
    
    # Execute the workflow
    logger.info("Executing workflow", extra={"task_id": task_id, "event": "execute"})
    result = workflow.invoke(initial_state)
    
    # Save the result if output directory is specified
    if output_dir:
        output_path = Path(output_dir) / task_id
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save the final state
        with open(output_path / "workflow_result.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        logger.info("Results saved", extra={"task_id": task_id, "event": "save_result"})
    
    return result


def load_all_tasks():
    """
    Load all tasks from the agent_task_assignments.json file.
    
    Returns:
        Dict containing all tasks organized by agent role
    """
    tasks_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "context-store", 
        "agent_task_assignments.json"
    )
    
    with open(tasks_file, 'r') as f:
        all_tasks = json.load(f)
    
    return all_tasks


def get_all_tasks_flattened():
    """
    Get all tasks from all agents, flattened into a single list.
    
    Returns:
        List of all tasks with agent role added to each task
    """
    all_tasks = load_all_tasks()
    flattened_tasks = []
    
    for agent_role, tasks in all_tasks.items():
        for task in tasks:
            # Add agent role to the task
            task_with_role = task.copy()
            task_with_role["agent_role"] = agent_role
            flattened_tasks.append(task_with_role)
            
    return flattened_tasks


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
    
    # Topological sort
    ordered_tasks = []
    visited = set()
    temp_visited = set()
    
    def visit(task_id):
        if task_id in temp_visited:
            raise ValueError(f"Cyclic dependency detected for task {task_id}")
        
        if task_id not in visited:
            temp_visited.add(task_id)
            
            # Visit all dependencies first
            for dep in graph.get(task_id, set()):
                if dep in task_map:  # Only visit if the dependency exists
                    visit(dep)
            
            visited.add(task_id)
            temp_visited.remove(task_id)
            ordered_tasks.append(task_map[task_id])
    
    # Visit all tasks
    for task_id in graph:
        if task_id not in visited:
            visit(task_id)
    
    return ordered_tasks


def execute_all_tasks(workflow_type="standard", output_dir=None, by_agent=None, day=None):
    """
    Execute all tasks from the agent_task_assignments.json file.
    
    Args:
        workflow_type: Type of workflow to use (standard, dynamic, state, advanced)
        output_dir: Directory to save outputs to
        by_agent: Optional agent role to filter tasks by
        day: Optional day number to filter tasks by
        
    Returns:
        List of execution results
    """
    all_tasks = get_all_tasks_flattened()
    
    # Filter tasks by agent if specified
    if by_agent:
        all_tasks = [t for t in all_tasks if t["agent_role"] == by_agent]
    
    # Filter tasks by day if specified
    if day is not None:
        all_tasks = [t for t in all_tasks if t["day"] == day]
        
    # Sort by dependencies
    if not by_agent and not day:
        all_tasks = get_dependency_ordered_tasks()
    
    results = []
    
    # Execute each task
    for task in all_tasks:
        task_id = task["id"]
        agent_role = task["agent_role"]
        task_title = task["title"]
        
        logger.info("Starting task execution", extra={"task_id": task_id, "agent_role": agent_role, "event": "start_task"})
        
        try:
            result = execute_task(
                task_id,
                input_message=f"Execute task {task_id}: {task_title}",
                workflow_type=workflow_type,
                output_dir=output_dir
            )
            
            # Add task info to result
            if isinstance(result, dict):
                result["task_id"] = task_id
                result["task_title"] = task_title
                result["agent_role"] = agent_role
            else:
                # Convert to dict if result is not a dictionary
                result = {
                    "task_id": task_id,
                    "task_title": task_title,
                    "agent_role": agent_role,
                    "result": str(result),
                    "status": "COMPLETED"
                }
            
            results.append(result)
            
            logger.info("Task completed", extra={"task_id": task_id, "agent_role": agent_role, "event": "task_completed"})
            
            # Small delay to avoid overwhelming the system
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}", extra={"task_id": task_id, "agent_role": agent_role, "event": "error"})
            results.append({
                "task_id": task_id,
                "task_title": task_title,
                "agent_role": agent_role,
                "status": "ERROR",
                "error": str(e)
            })
    
    # Save summary if output directory is specified
    if output_dir:
        summary_path = os.path.join(output_dir, "execution_summary.json")
        with open(summary_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("Execution summary saved", extra={"event": "summary_saved"})
    
    return results


def main():
    """Command-line interface for executing tasks through the agent workflow."""
    parser = argparse.ArgumentParser(description="Execute tasks through the agent workflow")
    
    # Task execution mode: single task or all tasks
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--task", "-t", help="Single task identifier (e.g. BE-07)")
    mode_group.add_argument("--all", "-a", action="store_true", help="Execute all tasks")
    mode_group.add_argument("--agent", "-g", help="Execute all tasks for a specific agent role")
    mode_group.add_argument("--day", "-y", type=int, help="Execute all tasks for a specific day")
    
    # Additional options
    parser.add_argument("--message", "-m", help="Input message for the task (for single task mode)")
    parser.add_argument("--workflow", "-w", choices=["standard", "dynamic", "state", "advanced"],
                        default="standard", help="Workflow type to use")
    parser.add_argument("--output", "-o", help="Directory to save outputs")
    
    args = parser.parse_args()
    
    # Set default output directory if not specified
    if args.task:
        output_dir = args.output or os.path.join("outputs", args.task)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = args.output or os.path.join("outputs", f"batch_{timestamp}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        if args.task:
            # Single task mode
            result = execute_task(
                args.task,
                input_message=args.message,
                workflow_type=args.workflow,
                output_dir=output_dir
            )
            
            # Print the result
            logger.info("Workflow execution completed", extra={"task_id": args.task, "event": "workflow_completed"})
            print("\nWorkflow execution completed:")
            print(f"Final status: {result.get('status', 'Unknown')}")
            if "result" in result:
                print(f"Result: {result['result']}")
            
            print(f"\nFull result saved to {output_dir}/{args.task}/workflow_result.json")
            
        elif args.all:
            # All tasks mode
            results = execute_all_tasks(
                workflow_type=args.workflow,
                output_dir=output_dir
            )
            
            # Print summary
            logger.info("All tasks execution summary", extra={"event": "all_tasks_completed"})
            print("\nAll tasks execution summary:")
            print(f"Total tasks executed: {len(results)}")
            successful = sum(1 for r in results if r.get("status") == "COMPLETED")
            print(f"Successfully completed: {successful}")
            print(f"Failed: {len(results) - successful}")
            
        elif args.agent:
            # Tasks by agent mode
            results = execute_all_tasks(
                workflow_type=args.workflow,
                output_dir=output_dir,
                by_agent=args.agent
            )
            
            # Print summary
            logger.info("Execution summary for agent", extra={"agent_role": args.agent, "event": "agent_tasks_completed"})
            print(f"\nExecution summary for agent {args.agent}:")
            print(f"Total tasks executed: {len(results)}")
            successful = sum(1 for r in results if r.get("status") == "COMPLETED")
            print(f"Successfully completed: {successful}")
            print(f"Failed: {len(results) - successful}")
            
        elif args.day is not None:
            # Tasks by day mode
            results = execute_all_tasks(
                workflow_type=args.workflow,
                output_dir=output_dir,
                day=args.day
            )
            
            # Print summary
            logger.info("Execution summary for day", extra={"event": "day_tasks_completed"})
            print(f"\nExecution summary for day {args.day}:")
            print(f"Total tasks executed: {len(results)}")
            successful = sum(1 for r in results if r.get("status") == "COMPLETED")
            print(f"Successfully completed: {successful}")
            print(f"Failed: {len(results) - successful}")
            
    except Exception as e:
        logger.error(f"Error: {e}", extra={"event": "fatal_error"})
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()