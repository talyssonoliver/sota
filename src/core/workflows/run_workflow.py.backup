"""
Workflow Runner Script
Main entry point for launching agent tasks through the LangGraph workflow.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from orchestration.execute_graph import run_task_graph
from orchestration.execute_workflow import get_dependency_ordered_tasks
from orchestration.generate_prompt import generate_prompt

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_agent_for_task(task_id: str) -> str:
    """
    Determine which agent should handle a given task.

    Args:
        task_id: The task identifier (e.g. BE-07)

    Returns:
        The agent identifier (e.g. backend-agent)
    """
    # Simple mapping based on task prefix
    if task_id.startswith("BE"):
        return "backend-agent"
    elif task_id.startswith("FE"):
        return "frontend-agent"
    elif task_id.startswith("TL"):
        return "technical-architect"
    elif task_id.startswith("DOC"):
        return "doc-agent"
    elif task_id.startswith("QA"):
        return "qa-agent"
    else:
        # Default to coordinator for task delegation
        return "coordinator"


def run_single_task(
        task_id: str,
        generate_only: bool = False,
        dry_run: bool = False,
        output_dir: Optional[str] = None) -> str:
    """
    Run workflow for a single task.

    Args:
        task_id: The task identifier (e.g. BE-07)
        generate_only: If True, only generate prompt without executing
        dry_run: If True, only print execution plan without running
        output_dir: Directory to save outputs to

    Returns:
        Result of the execution or the generated prompt
    """
    # Create output directory if it doesn't exist
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Determine which agent to use
    agent_id = get_agent_for_task(task_id)

    # Generate prompt
    prompt_path = None
    if output_dir:
        prompt_path = os.path.join(output_dir, f"{task_id}_prompt.md")

    prompt = generate_prompt(task_id, agent_id, prompt_path)

    if generate_only:
        print(f"Generated prompt for task {task_id} using agent {agent_id}")
        if prompt_path:
            print(f"Prompt saved to {prompt_path}")
        return {"task_id": task_id, "prompt": prompt}

    # Run the graph
    result = run_task_graph(task_id, dry_run, output_dir)

    return result


def run_task_sequence(
        tasks: Optional[List[str]] = None,
        generate_only: bool = False,
        dry_run: bool = False,
        output_base_dir: str = "outputs") -> None:
    """
    Run a sequence of tasks in dependency order.

    Args:
        tasks: List of task IDs to run (if None, will run all tasks in order)
        generate_only: If True, only generate prompts without executing
        dry_run: If True, only print execution plans without running
        output_base_dir: Base directory for output files
    """
    # Get all tasks in dependency order
    ordered_tasks = get_dependency_ordered_tasks()

    # Filter to requested tasks if specified
    if tasks:
        ordered_tasks = [task for task in ordered_tasks if task["id"] in tasks]

    if not ordered_tasks:
        print("No tasks to execute.")
        return

    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = {}

    print(f"Executing {len(ordered_tasks)} tasks in dependency order")

    for i, task in enumerate(ordered_tasks):
        task_id = task["id"]
        print(
            f"\n[{
                i + 1}/{
                len(ordered_tasks)}] Processing task {task_id}: {
                task.get(
                    'title',
                    '')}")

        # Create output directory for this task
        output_dir = os.path.join(output_base_dir, timestamp, task_id)

        try:
            result = run_single_task(
                task_id, generate_only, dry_run, output_dir)
            results[task_id] = result

            print(f"Completed task {task_id}")

        except Exception as e:
            print(
                f"Error processing task {task_id}: {str(e)}", file=sys.stderr)
            # Continue with next task

    # Save summary of all results
    summary_path = os.path.join(
        output_base_dir, timestamp, "workflow_summary.json")
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)

    with open(summary_path, "w") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "tasks_executed": [t["id"] for t in ordered_tasks],
                "generate_only": generate_only,
                "dry_run": dry_run,
                "results": {k: str(v) for k, v in results.items()}
            },
            f,
            indent=2
        )

    print(f"\nWorkflow execution complete. Summary saved to {summary_path}")


def main() -> None:
    """Command-line interface for running agent workflows."""
    parser = argparse.ArgumentParser(
        description="Run agent tasks through the LangGraph workflow"
    )

    parser.add_argument("--task", "-t", help="Task ID to execute (e.g. BE-07)")
    parser.add_argument(
        "--tasks", help="Comma-separated list of task IDs to execute")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Run all tasks in dependency order")
    parser.add_argument("--generate-only", "-g", action="store_true",
                        help="Only generate prompts without executing")
    parser.add_argument("--dry-run", "-d", action="store_true",
                        help="Print execution plan without running")
    parser.add_argument("--output", "-o", default="outputs",
                        help="Output directory")

    args = parser.parse_args()

    try:
        # Single task mode
        if args.task:
            run_single_task(args.task, args.generate_only, args.dry_run,
                            os.path.join(args.output, args.task))

        # Multiple task mode
        elif args.tasks:
            task_list = args.tasks.split(",")
            run_task_sequence(task_list, args.generate_only,
                              args.dry_run, args.output)

        # All tasks mode
        elif args.all:
            run_task_sequence(None, args.generate_only,
                              args.dry_run, args.output)

        else:
            print(
                "Error: No tasks specified. Use --task, --tasks, or --all",
                file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error running workflow: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
