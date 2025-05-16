"""
Task Execution Script for the AI Agent System
Example script to demonstrate how to execute tasks using the agent registry.
"""

import argparse
import sys
import os
import json
from typing import Dict, Any, Optional

from .delegation import delegate_task
from tools.memory_engine import initialize_memory
from utils.task_loader import load_task_metadata, update_task_state


def load_task_from_file(task_file: str) -> Dict[str, Any]:
    """
    Load task definition from a JSON file.
    
    Args:
        task_file: Path to the task definition file
        
    Returns:
        Task definition as a dictionary
    """
    with open(task_file, 'r') as f:
        return json.load(f)


def main():
    """Execute a task based on command-line arguments."""
    parser = argparse.ArgumentParser(description="Execute a task with the appropriate agent")
    
    # Task specification options (mutually exclusive)
    task_group = parser.add_mutually_exclusive_group(required=True)
    task_group.add_argument("--task", "-t", type=str, help="Task ID (e.g., BE-07, TL-03)")
    task_group.add_argument("--file", "-f", type=str, help="Path to task definition JSON file")
    
    # Optional arguments
    parser.add_argument("--description", "-d", type=str, help="Task description (optional if task ID is provided and YAML exists)")
    parser.add_argument("--agent", "-a", type=str, help="Explicitly specify agent to use")
    parser.add_argument("--context", "-c", type=str, help="Additional context")
    parser.add_argument("--output", "-o", type=str, help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--update-state", "-s", type=str, help="Update task state after execution (e.g., IN_PROGRESS, QA_PENDING)")
    
    args = parser.parse_args()
    
    # Initialize memory engine
    initialize_memory()
    
    try:
        # Load task from file if specified
        if args.file:
            if not os.path.exists(args.file):
                print(f"Error: Task file not found: {args.file}")
                sys.exit(1)
                
            task_def = load_task_from_file(args.file)
            task_id = task_def.get("task_id")
            description = task_def.get("task_description")
            context = task_def.get("context")
            relevant_files = task_def.get("relevant_files")
            agent_id = args.agent or task_def.get("agent_id")
        else:
            # Use command-line arguments or load from YAML
            task_id = args.task
            
            try:
                # Try to load task metadata from YAML
                task_metadata = load_task_metadata(task_id)
                
                # Use metadata as default values, but command-line args take precedence
                description = args.description or task_metadata.get('description')
                context_topics = task_metadata.get('context_topics', [])
                relevant_files = task_metadata.get('artefacts', [])
                agent_id = args.agent or task_metadata.get('owner')
                
                if args.verbose:
                    print(f"Loaded task metadata for {task_id} from YAML")
                    print(f"Title: {task_metadata.get('title')}")
                    print(f"Status: {task_metadata.get('state')}")
                    print(f"Dependencies: {task_metadata.get('depends_on', [])}")
                
            except FileNotFoundError:
                # Fall back to command-line args
                description = args.description
                context_topics = []
                relevant_files = []
                agent_id = args.agent
            
            context = args.context
            
            # Add context topics to context if available
            if context_topics and not context:
                context = f"Relevant context topics: {', '.join(context_topics)}"
        
        # Validate required fields
        if not description:
            print("Error: Task description is required either from YAML metadata or command line")
            parser.print_help()
            sys.exit(1)
            
        # Execute the task
        if args.verbose:
            print(f"Executing task {task_id} with {agent_id or 'auto-detected'} agent...")
            print(f"Description: {description}")
            
        result = delegate_task(
            task_id=task_id,
            task_description=description,
            agent_id=agent_id,
            context=context,
            relevant_files=relevant_files
        )
        
        # Update task state if requested
        if args.update_state:
            try:
                update_task_state(task_id, args.update_state)
                if args.verbose:
                    print(f"Updated task state to {args.update_state}")
            except Exception as e:
                print(f"Warning: Failed to update task state: {e}")
        
        # Output the result
        if args.verbose:
            print("\nTask completed successfully!")
            
        if args.output:
            with open(args.output, "w") as f:
                if isinstance(result, dict):
                    json.dump(result, f, indent=2)
                else:
                    f.write(str(result))
            if args.verbose:
                print(f"Result saved to {args.output}")
                
    except Exception as e:
        print(f"Error executing task: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()