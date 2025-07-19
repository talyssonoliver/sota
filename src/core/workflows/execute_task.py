"""
Task Execution Script for the AI Agent System
Example script to demonstrate how to execute tasks using the agent registry.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

try:
    from src.infrastructure.prompts.utils import extract_context_sources
except ImportError:
    pass
try:
    from src.infrastructure.memory.engines.memory_engine import MemoryEngine

    def get_memory_instance():
        return MemoryEngine()

except ImportError:

    def get_memory_instance():
        return None


from src.core.workflows.delegation import delegate_task
from src.core.workflows.inject_context import context_injector
from src.infrastructure.utils.input_validation import (ValidationError,
                                                       validate_command_args,
                                                       validate_file_path,
                                                       validate_string_content,
                                                       validate_task_id)
from src.infrastructure.utils.task_loader import (load_task_metadata,
                                                  update_task_state)

memory = None


def initialize_memory():
    """Initialize memory system - placeholder for now"""
    global memory
    memory = get_memory_instance()


def load_task_from_file(task_file: str) -> Dict[str, Any]:
    """
    Load task definition from a JSON file.

    Args:
        task_file: Path to the task definition file

    Returns:
        Task definition as a dictionary
    """
    # Validate file path
    validated_path = validate_file_path(task_file, must_exist=True)

    with open(validated_path, "r") as f:
        return json.load(f)


def execute_task_with_context(task_id: str, agent_role: str = None):
    """Execute task with memory-enhanced context"""
    try:
        # Validate inputs
        task_id = validate_task_id(task_id)
        if agent_role:
            agent_role = validate_string_content(agent_role, max_length=50)

        # Determine agent role from task if not provided
        if not agent_role:
            task_metadata = load_task_metadata(task_id)
            agent_role = task_metadata.get("owner", "coordinator")

        # Prepare agent with context
        agent = context_injector.prepare_agent_with_context(task_id, agent_role)

        # Log context usage
        logging.info(f"Executing task {task_id} with {agent_role} agent")

        # Execute task (integrate with existing execution logic)
        result = agent.execute(task_id)

        # Log context usage for analysis
        log_context_usage(task_id, agent_role, agent._context)

        return result

    except Exception as e:
        logging.error(f"Failed to execute task {task_id} with context: {e}")
        raise


def log_context_usage(task_id: str, agent_role: str, context: str):
    """Log context usage for analysis and optimization. Handles mocks gracefully for tests."""
    try:
        if hasattr(context, "split") or isinstance(context, (str, list)):
            context_length = len(context)
            context_sources = extract_context_sources(context)
        else:
            context_length = 0
            context_sources = []
    except Exception:
        context_length = 0
        context_sources = []
    # Coerce task_id to string for file operations and sanitize for filesystem
    task_id_str = str(task_id)
    # Remove characters not allowed in filenames (e.g., <, >, :, ", /, \, |,
    # ?, *)
    try:
        import re

        task_id_str = re.sub(r'[<>:"/\\|?*]', "_", task_id_str)
    except ImportError:
        # Fallback: replace common problematic characters manually
        for char in '<>:"/\\|?*':
            task_id_str = task_id_str.replace(char, "_")

    usage_log = {
        "task_id": task_id_str,
        "agent_role": agent_role,
        "context_length": context_length,
        "context_sources": context_sources,
        "timestamp": datetime.now().isoformat(),
    }

    # Save to context usage log
    from config.build_paths import LOGS_DIR

    context_logs_dir = LOGS_DIR / "context_usage"
    context_logs_dir.mkdir(parents=True, exist_ok=True)
    with open(context_logs_dir / f"{task_id_str}_context.json", "w") as f:
        json.dump(usage_log, f, indent=2)


def main():
    """Execute a task based on command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Execute a task with the appropriate agent"
    )

    # Task specification options (mutually exclusive)
    task_group = parser.add_mutually_exclusive_group(required=True)
    task_group.add_argument(
        "--task", "-t", type=str, help="Task ID (e.g., BE-07, TL-03)"
    )
    task_group.add_argument(
        "--file", "-f", type=str, help="Path to task definition JSON file"
    )

    # Optional arguments
    parser.add_argument(
        "--description",
        "-d",
        type=str,
        help="Task description (optional if task ID provided and YAML exists)",
    )
    parser.add_argument(
        "--agent", "-a", type=str, help="Explicitly specify agent to use"
    )
    parser.add_argument("--context", "-c", type=str, help="Additional context")
    parser.add_argument("--output", "-o", type=str, help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--update-state",
        "-s",
        type=str,
        help="Update task state after execution (e.g., IN_PROGRESS)",
    )

    args = parser.parse_args()

    # Validate command line arguments
    try:
        args = validate_command_args(args)
    except ValidationError as e:
        print(f" Invalid arguments: {e}")
        sys.exit(1)  # Initialize memory engine
    initialize_memory()

    try:
        # Load task from file if specified
        if args.file:
            task_def = load_task_from_file(args.file)
            task_id = task_def.get("task_id")
            description = task_def.get("task_description")
            context = task_def.get("context")
            relevant_files = task_def.get("relevant_files")
            agent_id = args.agent or task_def.get("agent_id")
        else:
            # Use command-line arguments or load from YAML
            try:
                # Try to load task metadata from YAML
                task_id = args.task
                task_metadata = load_task_metadata(task_id)
                description = args.description or task_metadata.get("description")
                context_topics = task_metadata.get("context_topics", [])
                relevant_files = task_metadata.get("artefacts", [])
                agent_id = args.agent or task_metadata.get("owner")

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
                context = f"Relevant context topics: {
                    ', '.join(context_topics)}"

        # Validate required fields
        if not description:
            print(
                "Error: Task description is required either from YAML metadata or command line"
            )
            parser.print_help()
            sys.exit(1)

        # Execute the task
        if args.verbose:
            print(
                f"Executing task {task_id} with {
                    agent_id or 'auto-detected'} agent..."
            )
            print(f"Description: {description}")

        result = delegate_task(
            task_id=task_id,
            task_description=description,
            agent_id=agent_id,
            context=context,
            relevant_files=relevant_files,
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
            # Validate output path
            output_path = validate_file_path(args.output, must_exist=False)
            with open(output_path, "w") as f:
                if isinstance(result, dict):
                    json.dump(result, f, indent=2)
                else:
                    f.write(str(result))
            if args.verbose:
                print(f"Result saved to {output_path}")

    except Exception as e:
        print(f"Error executing task: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
