"""
LangGraph Workflow Executor
Executes the LangGraph for a given task ID using predefined graph config and state handlers.
"""

import argparse
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.graph_builder import build_advanced_workflow_graph
from orchestration.states import TaskStatus
from tools.memory_engine import get_relevant_context, get_context_by_keys
from utils.task_loader import load_task_metadata, update_task_state

def build_task_state(task_id):
    """
    Build the initial state for a task, including MCP context memory.
    
    Args:
        task_id: The task identifier (e.g. BE-07)
        
    Returns:
        A dictionary containing the task's initial state
    """
    try:
        # Try to load task metadata from YAML file first
        task_metadata = load_task_metadata(task_id)
        
        task_title = task_metadata.get('title', f"Task {task_id}")
        task_description = task_metadata.get('description', "")
        dependencies = task_metadata.get('depends_on', [])
        priority = task_metadata.get('priority', "MEDIUM")
        estimation_hours = task_metadata.get('estimation_hours', 0)
        artefacts = task_metadata.get('artefacts', [])
        state = task_metadata.get('state', TaskStatus.PLANNED)
          # Step 3.5 Implementation: Get context using enhanced context_topics retrieval
        task_context = ""
        if 'context_topics' in task_metadata and task_metadata['context_topics']:
            # Use the new Step 3.5 focused context builder
            from tools.memory_engine import build_focused_context
            task_context = build_focused_context(
                task_metadata['context_topics'], 
                max_tokens=2000,  # Token budget management
                max_per_topic=2   # Limit documents per topic
            )
        else:
            # Fall back to vector search
            context_query = f"Task {task_id}: {task_title} - {task_description}"
            task_context = get_relevant_context(context_query)
        
        # Get context for dependencies
        dep_context = ""
        for dep_id in dependencies:
            try:
                # Try to load dependency metadata
                dep_metadata = load_task_metadata(dep_id)
                dep_title = dep_metadata.get('title', f"Task {dep_id}")
                dep_desc = dep_metadata.get('description', "")
                dep_state = dep_metadata.get('state', "")
                
                # Add dependency info to context
                dep_context += f"Dependency {dep_id}: {dep_title}\n"
                dep_context += f"Status: {dep_state}\n"
                dep_context += f"Description: {dep_desc}\n\n"
            except FileNotFoundError:
                # Fall back to vector search for this dependency
                dep_query = f"Details and output of completed task {dep_id}"
                dep_context += get_relevant_context(dep_query) + "\n\n"
        
        # Build the complete task state
        return {
            "task_id": task_id,
            "title": task_title,
            "description": task_description,
            "requirements": task_description.split(". ") if task_description else [],
            "context": task_context,
            "dependencies": dependencies,
            "status": state,
            "priority": priority,
            "estimation_hours": estimation_hours,
            "artefacts": artefacts,
            "dependency_context": dep_context,
            "prior_knowledge": task_context,
            "timestamp": datetime.now().isoformat()
        }
        
    except FileNotFoundError:
        # Fall back to the old method using agent_task_assignments.json
        # Get task details from agent_task_assignments.json
        tasks_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "context-store", 
            "agent_task_assignments.json"
        )
        
        task_data = None
        task_title = f"Task {task_id}"
        task_description = ""
        
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                all_tasks = json.load(f)
                
            # Find task in all agent assignments
            for agent_role, tasks in all_tasks.items():
                for task in tasks:
                    if task.get("id") == task_id:
                        task_data = task
                        task_title = task.get("title", task_title)
                        task_description = task.get("description", "")
                        break
                if task_data:
                    break
        
        # Get relevant context for the task
        context_query = f"Task {task_id}: {task_title} - {task_description}"
        task_context = get_relevant_context(context_query)
        
        # Get dependencies
        dependencies = []
        if task_data and "dependencies" in task_data:
            dependencies = task_data.get("dependencies", [])
            
            # Get context for dependencies
            dep_context = ""
            for dep_id in dependencies:
                dep_query = f"Details and output of completed task {dep_id}"
                dep_context += get_relevant_context(dep_query) + "\n\n"
        
        # Build the complete task state
        return {
            "task_id": task_id,
            "title": task_title,
            "description": task_description,
            "requirements": task_description.split(". "),
            "context": task_context,
            "dependencies": dependencies,
            "status": TaskStatus.PLANNED,
            "prior_knowledge": task_context,
            "timestamp": datetime.now().isoformat()
        }

def run_task_graph(task_id, dry_run=False, output_dir=None):
    """
    Execute the LangGraph workflow for a specific task.
    
    Args:
        task_id: The task identifier (e.g. BE-07)
        dry_run: If True, only print the execution plan without running it
        output_dir: Directory to save outputs to
        
    Returns:
        The result of the workflow execution
    """
    # Build the initial state with MCP context
    initial_state = build_task_state(task_id)
    
    if dry_run:
        print("=== DRY RUN ===")
        print(f"Task: {task_id}")
        print(f"Title: {initial_state['title']}")
        print(f"Initial Status: {initial_state['status']}")
        print(f"Dependencies: {initial_state['dependencies']}")
        print(f"Priority: {initial_state.get('priority', 'MEDIUM')}")
        print(f"Estimation: {initial_state.get('estimation_hours', 0)} hours")
        print(f"Artefacts: {initial_state.get('artefacts', [])}")
        print(f"Context length: {len(initial_state['context'])} characters")
        print("=== END DRY RUN ===")
        return initial_state
    
    print(f"Launching advanced workflow with state-based transitions for task {task_id}...")
    
    # Build the workflow graph with the advanced configuration
    workflow = build_advanced_workflow_graph()
    
    # Execute the workflow
    print(f"Executing workflow for {task_id}...")
    result = workflow.invoke(initial_state)
    
    # Update task state in the YAML file if it changed
    if result.get('status') != initial_state.get('status'):
        try:
            update_task_state(task_id, result.get('status'))
            print(f"Updated task state to {result.get('status')}")
        except Exception as e:
            print(f"Warning: Failed to update task state: {e}")
    
    # Save the result if output directory is specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{task_id}_result.json")
        
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"Result saved to {output_path}")
    
    print("\n--- EXECUTION SUMMARY ---")
    print(f"Task: {task_id}")
    print(f"Title: {initial_state['title']}")
    print(f"Final Status: {result.get('status', 'Unknown')}")
    print(f"Execution Time: {datetime.now().isoformat()}")
    
    return result

def main():
    """Command-line interface for executing tasks through the LangGraph workflow."""
    parser = argparse.ArgumentParser(description="Run agent workflow graph")
    
    parser.add_argument("--task", "-t", required=True, help="Task ID (e.g. BE-07)")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Print execution plan without running")
    parser.add_argument("--output", "-o", help="Directory to save outputs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Default output directory
    output_dir = args.output or os.path.join("outputs", args.task)
    
    try:
        if args.verbose:
            print(f"Loading task metadata for {args.task}...")
            try:
                task_metadata = load_task_metadata(args.task)
                print(f"Title: {task_metadata.get('title')}")
                print(f"Owner: {task_metadata.get('owner')}")
                print(f"State: {task_metadata.get('state')}")
                print(f"Dependencies: {task_metadata.get('depends_on', [])}")
            except FileNotFoundError:
                print(f"No metadata file found for task {args.task}")
        
        result = run_task_graph(args.task, args.dry_run, output_dir)
        
        if args.dry_run:
            print("Dry run completed successfully.")
            sys.exit(0)
            
        # Print final status
        print(f"Workflow completed with status: {result.get('status', 'Unknown')}")
            
    except Exception as e:
        print(f"Error executing workflow: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()