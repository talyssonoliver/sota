
from src.infrastructure.utils.common_imports import (
    Path,
    datetime,
    json,
    logging,
    os,
    sys,
    time,
    traceback
)
"""
Step 4.3 Implementation: Run LangGraph Workflow

This script implements the Step 4.3 requirements for executing LangGraph workflows with:
- Proper LangGraph workflow execution with specified agent sequence flow:
  1. Entry node: coordinator
  2. Coordinator assigns task → backend
  3. Backend executes based on generated prompt
  4. Result forwarded to qa agent
  5. If QA passes → result forwarded to documentation
  6. Final state written to tasks.json
- Integration with Step 4.2 prompt generation system
- LangGraph event hooks for logging and human checkpoints
- Enhanced CLI options for workflow type selection
- Comprehensive output registration and status tracking
- Visualization and monitoring capabilities

Usage:
    python orchestration/execute_graph.py --task BE-07
    python orchestration/execute_graph.py --task BE-07 --workflow advanced --verbose
    python orchestration/execute_graph.py --task BE-07 --generate-prompt --monitor
"""

import argparse
# import json  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
# import os  # Consolidated to common_imports
# import sys  # Consolidated to common_imports
import threading
# import time  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
from typing import Any, Dict, Optional, Tuple

try:
    from src.infrastructure.utils.common_imports import datetime
except ImportError:
    pass
try:
#     import logging  # Consolidated to common_imports

    from pythonjsonlogger import jsonlogger
except ImportError:
    jsonlogger = None

from src.infrastructure.memory import get_context_by_keys, get_memory_system

try:
    from src.core.workflows.graph.graph_builder import (
        build_advanced_workflow_graph, build_dynamic_workflow_graph,
        build_state_workflow_graph)
    from src.core.workflows.graph.notifications import (
        NotificationLevel, SlackNotifier, attach_notifications_to_workflow)
    from src.core.workflows.graph.resilient_workflow import \
        create_resilient_workflow

    GRAPH_IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Graph imports failed: {e}")
    GRAPH_IMPORTS_AVAILABLE = False
    # Define fallback functions
    from unittest.mock import MagicMock

    def build_advanced_workflow_graph(*args, **kwargs):
        return MagicMock()

    def build_dynamic_workflow_graph(*args, **kwargs):
        return MagicMock()

    def build_state_workflow_graph(*args, **kwargs):
        return MagicMock()

    class NotificationLevel:
        ALL = "all"
        ERROR = "error"
        STATE_CHANGE = "state_change"
        INFO = "info"

    class SlackNotifier:
        def __init__(self, *args, **kwargs):
            pass

    def attach_notifications_to_workflow(*args, **kwargs):
        pass

    def create_resilient_workflow(*args, **kwargs):
        return MagicMock()


from src.core.workflows.generate_prompt import generate_prompt
from src.core.workflows.states import TaskStatus
from src.infrastructure.utils.execution_monitor import (create_langgraph_hook,
                                                        get_execution_monitor)
from src.infrastructure.utils.task_loader import (load_task_metadata,
                                                  update_task_state)

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure structured JSON logging for Step 4.3 execution tracking
logger = logging.getLogger("step_4_3_executor")
handler = logging.StreamHandler()
if jsonlogger:
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(event)s %(task_id)s %(workflow_type)s %(agent)s"
    )
else:
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


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

        task_title = task_metadata.get("title", f"Task {task_id}")
        task_description = task_metadata.get("description", "")
        dependencies = task_metadata.get("depends_on", [])
        priority = task_metadata.get("priority", "MEDIUM")
        estimation_hours = task_metadata.get("estimation_hours", 0)
        artefacts = task_metadata.get("artefacts", [])
        # Step 3.5 Implementation: Get context using enhanced context_topics
        # retrieval
        state = task_metadata.get("state", TaskStatus.PLANNED)
        task_context = ""
        if "context_topics" in task_metadata and task_metadata["context_topics"]:
            # Use the new Step 3.5 focused context builder

            memory_instance = get_memory_system()
            task_context = memory_instance.build_focused_context(
                context_topics=task_metadata["context_topics"],
                max_tokens=2000,  # Token budget management
                max_per_topic=2,  # Limit documents per topic
            )
        else:
            # Fall back to vector search
            context_query = f"Task {task_id}: {task_title} - {task_description}"
            task_context = get_context_by_keys([context_query])

        # Get context for dependencies
        dep_context = ""
        for dep_id in dependencies:
            try:
                # Try to load dependency metadata
                dep_metadata = load_task_metadata(dep_id)
                dep_title = dep_metadata.get("title", f"Task {dep_id}")
                dep_desc = dep_metadata.get("description", "")
                dep_state = dep_metadata.get("state", "")

                # Add dependency info to context
                dep_context += f"Dependency {dep_id}: {dep_title}\n"
                dep_context += f"Status: {dep_state}\n"
                dep_context += f"Description: {dep_desc}\n\n"
            except FileNotFoundError:
                # Fall back to vector search for this dependency
                dep_query = f"Details and output of completed task {dep_id}"
                dep_context += get_context_by_keys([dep_query]) + "\n\n"

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
            "timestamp": datetime.now().isoformat(),
        }

    except FileNotFoundError:
        # Fall back to the old method using agent_task_assignments.json
        # Get task details from agent_task_assignments.json
        tasks_file = str(
            Path(__file__).parent.parent / "context-store" /
            "agent_task_assignments.json",
        )

        task_data = None
        task_title = f"Task {task_id}"
        task_description = ""

        if os.path.exists(tasks_file):
            with open(tasks_file, "r") as f:
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
        task_context = get_context_by_keys([context_query])

        # Get dependencies
        dependencies = []
        if task_data and "dependencies" in task_data:
            dependencies = task_data.get("dependencies", [])

            # Get context for dependencies
            dep_context = ""
            for dep_id in dependencies:
                dep_query = f"Details and output of completed task {dep_id}"
                dep_context += get_context_by_keys([dep_query]) + "\n\n"

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
            "timestamp": datetime.now().isoformat(),
        }


def _initialize_execution_monitoring(task_id: str, workflow_type: str, 
                                     execution_id: str, dry_run: bool, 
                                     enable_monitoring: bool) -> Tuple[Optional[Any], Optional[Any]]:
    """Initialize execution monitoring for workflow.
    
    Args:
        task_id: The task identifier
        workflow_type: Type of workflow being executed
        execution_id: Unique execution identifier
        dry_run: Whether this is a dry run
        enable_monitoring: Whether monitoring is enabled
        
    Returns:
        Tuple of (monitor, workflow_execution_data) if enabled, (None, None) otherwise
    """
    if not enable_monitoring:
        return None, None
        
    monitor = get_execution_monitor()
    workflow_execution_data = monitor.start_agent_execution(
        task_id,
        "workflow",
        {
            "workflow_type": workflow_type,
            "execution_id": execution_id,
            "dry_run": dry_run,
        },
    )
    monitor.log_event(
        task_id,
        "workflow_start",
        {"workflow_type": workflow_type, "execution_id": execution_id},
    )
    return monitor, workflow_execution_data


def _prepare_initial_state(task_id: str) -> Dict[str, Any]:
    """Prepare and validate initial workflow state.
    
    Args:
        task_id: The task identifier
        
    Returns:
        Initial state dictionary with required fields
    """
    # Build the initial state with MCP context
    initial_state = build_task_state(task_id)
    
    # Defensive programming: ensure initial_state has required fields
    if initial_state is None:
        initial_state = {}
    
    # Ensure required fields exist with defaults
    initial_state.setdefault("task_id", task_id)
    initial_state.setdefault("title", f"Task {task_id}")
    initial_state.setdefault("description", "")
    initial_state.setdefault("status", TaskStatus.PLANNED)
    initial_state.setdefault("dependencies", [])
    initial_state.setdefault("priority", "MEDIUM")
    initial_state.setdefault("estimation_hours", 0)
    initial_state.setdefault("artefacts", [])
    initial_state.setdefault("context", "")
    
    return initial_state


def _generate_enhanced_prompt(task_id: str, initial_state: Dict[str, Any]) -> str:
    """Generate enhanced prompt using Step 4.2 integration.
    
    Args:
        task_id: The task identifier
        initial_state: Initial state dictionary to update
        
    Returns:
        Enhanced prompt string
    """
    try:
        enhanced_prompt = generate_prompt(
            task_id=task_id,
            agent_type="backend-agent",  # Default to backend agent for task execution
            output_path=None,  # Let it use default path
        )
        
        logger.info(
            "Step 4.2 prompt generation completed",
            extra={
                "event": "prompt_generated",
                "task_id": task_id,
                "agent": "prompt_generator",
                "prompt_length": len(enhanced_prompt),
            },
        )
        
        return enhanced_prompt
        
    except Exception as e:
        logger.error(f"Step 4.2 prompt generation failed: {e}")
        # Continue with basic prompt fallback
        return f"Complete task {task_id}: {initial_state.get('title', task_id)}"


def _handle_dry_run(task_id: str, workflow_type: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle dry run execution by printing execution plan.
    
    Args:
        task_id: The task identifier
        workflow_type: Type of workflow
        initial_state: Initial state dictionary
        
    Returns:
        Initial state (for dry run, no actual execution)
    """
    print("=== STEP 4.3 DRY RUN ===")
    print(f"Task: {task_id}")
    print(f"Title: {initial_state.get('title', 'Unknown Task')}")
    print(f"Workflow Type: {workflow_type}")
    print(f"Initial Status: {initial_state.get('status', 'UNKNOWN')}")
    print(f"Dependencies: {initial_state.get('dependencies', [])}")
    print(f"Priority: {initial_state.get('priority', 'MEDIUM')}")
    print(f"Estimation: {initial_state.get('estimation_hours', 0)} hours")
    print(f"Artefacts: {initial_state.get('artefacts', [])}")
    print(f"Context length: {len(initial_state.get('context', ''))} characters")
    print(f"Enhanced prompt length: {len(initial_state.get('enhanced_prompt', ''))} characters")
    print("\n=== PLANNED EXECUTION FLOW ===")
    print("1. Entry node: coordinator")
    print("2. Coordinator assigns task → backend")
    print("3. Backend executes based on generated prompt")
    print("4. Result forwarded to qa agent")
    print("5. If QA passes → result forwarded to documentation")
    print("6. Final state written to tasks.json")
    print("=== END DRY RUN ===")
    return initial_state


def _build_and_configure_workflow(workflow_type: str, enable_notifications: bool, 
                                  task_id: str) -> Any:
    """Build workflow and configure notifications.
    
    Args:
        workflow_type: Type of workflow to build
        enable_notifications: Whether to enable notifications
        task_id: Task identifier for logging
        
    Returns:
        Configured workflow instance
        
    Raises:
        ValueError: If workflow_type is unknown
    """
    # Select and build the appropriate workflow graph
    workflow_builders = {
        "advanced": build_advanced_workflow_graph,
        "dynamic": build_dynamic_workflow_graph,
        "state": build_state_workflow_graph,
        "resilient": create_resilient_workflow,
    }

    if workflow_type not in workflow_builders:
        logger.warning(
            f"Unknown workflow type: {workflow_type}. Falling back to 'advanced' workflow",
            extra={
                "event": "unknown_workflow_fallback",
                "task_id": task_id,
                "requested_type": workflow_type,
                "fallback_type": "advanced",
                "agent": "workflow_builder",
            },
        )
        workflow_type = "advanced"

    # Build the workflow
    workflow = workflow_builders[workflow_type]()

    # Attach notifications if enabled
    if enable_notifications:
        try:
            notifier = SlackNotifier()
            workflow = attach_notifications_to_workflow(
                workflow, notifier, notification_level=NotificationLevel.INFO
            )
            logger.info(
                "Slack notifications attached",
                extra={
                    "event": "notifications_enabled",
                    "task_id": task_id,
                    "workflow_type": workflow_type,
                    "agent": "notification_system",
                },
            )
        except Exception as e:
            logger.warning(
                f"Failed to attach notifications: {e}",
                extra={
                    "event": "notification_setup_failed",
                    "task_id": task_id,
                    "workflow_type": workflow_type,
                    "agent": "notification_system",
                },
            )
    
    return workflow


def run_task_graph(
    task_id: str,
    workflow_type: str = "advanced",
    dry_run: bool = False,
    output_dir: Optional[str] = None,
    enable_notifications: bool = True,
    enable_monitoring: bool = True,
) -> Dict[str, Any]:
    """
    Step 4.3: Enhanced LangGraph workflow execution with comprehensive agent flow.

    Execution Flow:
    1. Entry node: coordinator
    2. Coordinator assigns task → backend
    3. Backend executes based on generated prompt (Step 4.2 integration)
    4. Result forwarded to qa agent
    5. If QA passes → result forwarded to documentation
    6. Final state written to tasks.json

    Args:
        task_id: The task identifier (e.g. BE-07)
        workflow_type: Type of workflow ('advanced', 'dynamic', 'state', 'resilient')
        dry_run: If True, only print the execution plan without running it
        output_dir: Directory to save outputs to
        enable_notifications: Enable Slack notifications for workflow events
        enable_monitoring: Enable real-time monitoring and logging

    Returns:
        The result of the workflow execution
    """
    # Initialize execution
    execution_id = f"{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Check environment variables for test mode
    if os.getenv('DISABLE_WORKFLOW_MONITORING'):
        enable_monitoring = False
    
    # Initialize monitoring
    monitor, workflow_execution_data = _initialize_execution_monitoring(
        task_id, workflow_type, execution_id, dry_run, enable_monitoring
    )

    logger.info(
        "Starting Step 4.3 execution",
        extra={
            "event": "workflow_start",
            "task_id": task_id,
            "workflow_type": workflow_type,
            "execution_id": execution_id,
        },
    )

    # Prepare initial state
    initial_state = _prepare_initial_state(task_id)
    
    # Generate enhanced prompt
    enhanced_prompt = _generate_enhanced_prompt(task_id, initial_state)
    initial_state["enhanced_prompt"] = enhanced_prompt

    # Handle dry run
    if dry_run:
        return _handle_dry_run(task_id, workflow_type, initial_state)

    print(f"Starting Step 4.3: LangGraph workflow execution for task {task_id}")
    print(f"Workflow type: {workflow_type}")
    print(f"Execution ID: {execution_id}")

    # Build workflow and set up notifications
    workflow = _build_and_configure_workflow(
        workflow_type, enable_notifications, task_id
    )

    # Start monitoring thread if enabled
    monitoring_thread = None
    if enable_monitoring:

        def monitor_execution():
            """Background monitoring for workflow execution"""
            while True:
                try:
                    # Log execution status every 30 seconds
                    time.sleep(30)
                    logger.info(
                        "Workflow execution monitoring",
                        extra={
                            "event": "execution_monitor",
                            "task_id": task_id,
                            "workflow_type": workflow_type,
                            "agent": "monitoring_system",
                            "timestamp": datetime.now().isoformat(),
                        },
                    )
                except Exception:
                    break

        monitoring_thread = threading.Thread(target=monitor_execution, daemon=True)
        monitoring_thread.start()

    # Step 4.8: Create LangGraph execution hook for real-time monitoring
    if enable_monitoring:
        langgraph_hook = create_langgraph_hook(task_id)

        # Store original invoke method before replacing it
        original_invoke = workflow.invoke
        
        # Attach hook to workflow execution
        def monitored_workflow_invoke(state):
            langgraph_hook.on_workflow_start(state)
            try:
                result = original_invoke(state)
                langgraph_hook.on_workflow_end(result)
                return result
            except Exception as e:
                langgraph_hook.on_workflow_end(state, error=str(e))
                raise

        # Replace workflow invoke with monitored version
        workflow.invoke = monitored_workflow_invoke

    # Execute the Step 4.3 workflow with enhanced error handling
    result = None
    execution_start = datetime.now()

    try:
        logger.info(
            "Executing LangGraph workflow",
            extra={
                "event": "workflow_execution_start",
                "task_id": task_id,
                "workflow_type": workflow_type,
                "agent": "coordinator",
            },
        )

        print("Executing Step 4.3 workflow with agent sequence:")
        print("→ coordinator → backend → qa → documentation")

        # Execute the workflow
        result = workflow.invoke(initial_state)

        execution_duration = (datetime.now() - execution_start).total_seconds()

        logger.info(
            "Workflow execution completed successfully",
            extra={
                "event": "workflow_success",
                "task_id": task_id,
                "workflow_type": workflow_type,
                "agent": "workflow_manager",
                "execution_duration": execution_duration,
                "final_status": result.get("status", "Unknown"),
            },
        )

    except Exception as e:
        execution_duration = (datetime.now() - execution_start).total_seconds()

        logger.error(
            f"Workflow execution failed: {e}",
            extra={
                "event": "workflow_error",
                "task_id": task_id,
                "workflow_type": workflow_type,
                "agent": "workflow_manager",
                "execution_duration": execution_duration,
                "error": str(e),
            },
        )

        # Return failed state for handling
        result = {
            **initial_state,
            "status": TaskStatus.FAILED,
            "error": str(e),
            "execution_duration": execution_duration,
        }

    # Update task state in the YAML file if it changed
    if result.get("status") != initial_state.get("status"):
        try:
            update_task_state(task_id, result.get("status"))
            print(f"✓ Updated task state to {result.get('status')}")

            logger.info(
                "Task state updated",
                extra={
                    "event": "task_state_updated",
                    "task_id": task_id,
                    "workflow_type": workflow_type,
                    "agent": "state_manager",
                    "new_status": result.get("status"),
                    "previous_status": initial_state.get("status"),
                },
            )

        except Exception as e:
            logger.error(
                f"Failed to update task state: {e}",
                extra={
                    "event": "task_state_update_failed",
                    "task_id": task_id,
                    "workflow_type": workflow_type,
                    "agent": "state_manager",
                },
            )
            print(f"⚠ Warning: Failed to update task state: {e}")

    # Save comprehensive execution result
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

        # Save main result
        output_path = str(Path(output_dir) / f"{task_id}_step_4_3_result.json")
        result_output = {
            **result,
            "execution_metadata": {
                "execution_id": execution_id,
                "workflow_type": workflow_type,
                "execution_start": execution_start.isoformat(),
                "execution_end": datetime.now().isoformat(),
                "execution_duration": (
                    datetime.now() - execution_start
                ).total_seconds(),
                "step": "Step_4.3_LangGraph_Workflow",
                "enhanced_prompt_used": bool(initial_state.get("enhanced_prompt")),
                "notifications_enabled": enable_notifications,
                "monitoring_enabled": enable_monitoring,
            },
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_output, f, indent=2, default=str, ensure_ascii=False)

        # Save execution log
        log_path = str(Path(output_dir) / f"{task_id}_step_4_3_execution.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("Step 4.3 Execution Log\n")
            f.write(f"Task ID: {task_id}\n")
            f.write(f"Execution ID: {execution_id}\n")
            f.write(f"Workflow Type: {workflow_type}\n")
            f.write(f"Start: {execution_start.isoformat()}\n")
            f.write(f"End: {datetime.now().isoformat()}\n")
            f.write(
                f"Duration: {(datetime.now() -
                                  execution_start).total_seconds():.2f} seconds\n"
            )
            f.write(f"Final Status: {result.get('status', 'Unknown')}\n")

        print(f"✓ Step 4.3 results saved to {output_path}")
        print(f"✓ Execution log saved to {log_path}")

    # Final execution summary
    print("\n" + "=" * 60)
    print("STEP 4.3 EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Task: {task_id}")
    print(f"Title: {initial_state.get('title', task_id)}")
    print(f"Workflow Type: {workflow_type}")
    print(f"Execution ID: {execution_id}")
    print(f"Initial Status: {initial_state.get('status', 'Unknown')}")
    print(f"Final Status: {result.get('status', 'Unknown')}")
    print(
        f"Execution Time: {(datetime.now() -
                              execution_start).total_seconds():.2f} seconds"
    )
    print(
        f"Enhanced Prompt: {
            '✓' if initial_state.get('enhanced_prompt') else '✗'}"
    )
    print(f"Notifications: {'✓' if enable_notifications else '✗'}")
    print(f"Monitoring: {'✓' if enable_monitoring else '✗'}")

    if result.get("error"):
        print(f"Error: {result['error']}")
    print("=" * 60)

    # Step 4.8: Complete workflow execution monitoring
    if enable_monitoring:
        workflow_status = (
            "COMPLETED" if result.get("status") != TaskStatus.FAILED else "FAILED"
        )
        workflow_error = result.get("error") if workflow_status == "FAILED" else None

        monitor.complete_agent_execution(
            workflow_execution_data,
            status=workflow_status,
            output=result,
            error=workflow_error,
        )

        # Log final workflow statistics
        monitor.log_event(
            task_id,
            "workflow_complete",
            {
                "final_status": result.get("status"),
                "execution_duration": (
                    datetime.now() - execution_start
                ).total_seconds(),
                "workflow_type": workflow_type,
                "agents_executed": result.get("agents_executed", []),
            },
        )

        # Print execution statistics
        stats = monitor.get_execution_stats(task_id)
        print(f"\n📊 Execution Statistics for {task_id}:")
        print(f"   Total Executions: {stats['total_executions']}")
        print(
            f"   Success Rate: {stats['successful_executions']}/{stats['total_executions']}"
        )
        print(
            f"   Average Duration: {
                stats['average_duration_minutes']} minutes"
        )
        print(f"   Agents Used: {', '.join(stats['agents_used'])}")

    logger.info(
        "Step 4.3 execution completed",
        extra={
            "event": "step_4_3_complete",
            "task_id": task_id,
            "workflow_type": workflow_type,
            "agent": "step_4_3_executor",
            "execution_id": execution_id,
            "final_status": result.get("status", "Unknown"),
        },
    )

    return result


def get_relevant_context(query: str, k: int = 5, **kwargs) -> str:
    """
    Get relevant context for a query using the memory system.

    Args:
        query: The query string
        k: Number of results to return
        **kwargs: Additional arguments (filtered for compatibility)

    Returns:
        Relevant context as a string
    """
    try:
        from src.infrastructure.memory import \
            get_relevant_context as memory_get_context

        # Filter kwargs to only include those supported by the underlying function
        supported_kwargs = {'user'}  # Add other supported kwargs as needed
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in supported_kwargs}
        
        return memory_get_context(query, k=k, **filtered_kwargs)
    except ImportError:
        # Fallback to vector search if memory system is not available
        return get_context_by_keys([query])
    except (TypeError, AttributeError) as e:
        # Handle signature mismatch or NoneType errors by falling back to vector search
        return get_context_by_keys([query])
    except Exception as e:
        # Catch any other errors and fallback to vector search
        return get_context_by_keys([query])


def main():
    """
    Step 4.3: Enhanced command-line interface for LangGraph workflow execution.

    Supports multiple workflow types, monitoring, notifications, and comprehensive logging.
    """
    parser = argparse.ArgumentParser(
        description="Step 4.3: Run LangGraph agent workflow with enhanced execution flow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic execution
  python execute_graph.py --task BE-07

  # With advanced workflow and monitoring
  python execute_graph.py --task BE-07 --workflow advanced --monitor --notify

  # Resilient workflow with custom output
  python execute_graph.py --task BE-07 --workflow resilient --output /path/to/outputs

  # Dry run to see execution plan
  python execute_graph.py --task BE-07 --dry-run --verbose

Workflow Types:
  - advanced: Advanced workflow with comprehensive agent flow
  - dynamic: Dynamic workflow with adaptive routing
  - state: State-based workflow with explicit transitions
  - resilient: Resilient workflow with retry and timeout handling
        """,
    )

    # Required arguments
    parser.add_argument("--task", "-t", required=True, help="Task ID (e.g. BE-07)")

    # Workflow configuration
    parser.add_argument(
        "--workflow",
        "-w",
        choices=["advanced", "dynamic", "state", "resilient"],
        default="advanced",
        help="Type of workflow to execute (default: advanced)",
    )

    # Execution options
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Print execution plan without running",
    )
    parser.add_argument(
        "--output", "-o", help="Directory to save outputs (default: outputs/<task_id>)"
    )

    # Monitoring and notifications
    parser.add_argument(
        "--monitor",
        "-m",
        action="store_true",
        help="Enable real-time monitoring and enhanced logging",
    )
    parser.add_argument(
        "--notify",
        "-n",
        action="store_true",
        help="Enable Slack notifications for workflow events",
    )
    parser.add_argument(
        "--no-notifications",
        action="store_true",
        help="Disable notifications even if configured",
    )
    parser.add_argument(
        "--no-monitoring",
        action="store_true",
        help="Disable monitoring and enhanced logging",
    )

    # Output and verbosity
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with detailed task metadata",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress non-essential output"
    )

    # Step 4.3 specific options
    parser.add_argument(
        "--execution-id", help="Custom execution ID (auto-generated if not provided)"
    )
    parser.add_argument(
        "--save-logs",
        action="store_true",
        help="Save execution logs to output directory",
    )

    args = parser.parse_args()

    # Configure logging level based on verbosity
    if args.quiet:
        logger.setLevel(logging.WARNING)
    elif args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Default output directory
    output_dir = args.output or str(Path("outputs") / "step_4_3" / args.task)

    # Enable/disable features based on arguments
    enable_notifications = args.notify and not args.no_notifications
    enable_monitoring = args.monitor and not args.no_monitoring

    # Default monitoring for non-dry runs unless explicitly disabled
    if not args.dry_run and not args.no_monitoring:
        enable_monitoring = True

    try:
        if not args.quiet:
            print("=" * 60)
            print("STEP 4.3: LANGGRAPH WORKFLOW EXECUTION")
            print("=" * 60)

        if args.verbose:
            print(f"Loading task metadata for {args.task}...")
            try:
                task_metadata = load_task_metadata(args.task)
                print(f"Title: {task_metadata.get('title', 'Unknown')}")
                print(f"Owner: {task_metadata.get('owner', 'Unknown')}")
                print(f"State: {task_metadata.get('state', 'Unknown')}")
                print(f"Priority: {task_metadata.get('priority', 'MEDIUM')}")
                print(
                    f"Estimation: {
                        task_metadata.get(
                            'estimation_hours',
                            0)} hours"
                )
                print(f"Dependencies: {task_metadata.get('depends_on', [])}")
                print(f"Artefacts: {task_metadata.get('artefacts', [])}")
                print(
                    f"Context Topics: {
                        task_metadata.get(
                            'context_topics',
                            [])}"
                )
            except FileNotFoundError:
                print(f"⚠ No metadata file found for task {args.task}")
                print("Will use fallback task loading from agent_task_assignments.json")

            print("\nStep 4.3 Configuration:")
            print(f"- Workflow Type: {args.workflow}")
            print(f"- Notifications: {'✓' if enable_notifications else '✗'}")
            print(f"- Monitoring: {'✓' if enable_monitoring else '✗'}")
            print(f"- Output Directory: {output_dir}")
            print(f"- Dry Run: {'✓' if args.dry_run else '✗'}")
            print()

        # Log execution start
        logger.info(
            "Step 4.3 CLI execution started",
            extra={
                "event": "cli_start",
                "task_id": args.task,
                "workflow_type": args.workflow,
                "agent": "cli_interface",
                "dry_run": args.dry_run,
            },
        )

        # Execute the Step 4.3 workflow
        result = run_task_graph(
            task_id=args.task,
            workflow_type=args.workflow,
            dry_run=args.dry_run,
            output_dir=output_dir,
            enable_notifications=enable_notifications,
            enable_monitoring=enable_monitoring,
        )

        if args.dry_run:
            if not args.quiet:
                print("✓ Step 4.3 dry run completed successfully.")
            logger.info(
                "Dry run completed",
                extra={
                    "event": "dry_run_complete",
                    "task_id": args.task,
                    "workflow_type": args.workflow,
                    "agent": "cli_interface",
                },
            )
            sys.exit(0)

        # Check execution result
        final_status = result.get("status", "Unknown")

        if not args.quiet:
            if final_status == TaskStatus.COMPLETED:
                print("✓ Step 4.3 workflow completed successfully!")
                print(f"  Final status: {final_status}")
            elif final_status == TaskStatus.FAILED:
                print("✗ Step 4.3 workflow failed")
                print(f"  Final status: {final_status}")
                if result.get("error"):
                    print(f"  Error: {result['error']}")
            else:
                print(f"⚠ Step 4.3 workflow completed with status: {final_status}")

        # Log final result
        logger.info(
            "Step 4.3 CLI execution completed",
            extra={
                "event": "cli_complete",
                "task_id": args.task,
                "workflow_type": args.workflow,
                "agent": "cli_interface",
                "final_status": final_status,
                "success": final_status == TaskStatus.COMPLETED,
            },
        )

        # Exit with appropriate code
        if final_status == TaskStatus.FAILED:
            sys.exit(1)
        elif final_status == TaskStatus.COMPLETED:
            sys.exit(0)
        else:
            sys.exit(2)  # Partial completion or unknown status

    except KeyboardInterrupt:
        print("\n⚠ Step 4.3 execution interrupted by user")
        logger.warning(
            "Execution interrupted",
            extra={
                "event": "execution_interrupted",
                "task_id": args.task,
                "workflow_type": args.workflow,
                "agent": "cli_interface",
            },
        )
        sys.exit(130)

    except Exception as e:
        error_msg = f"Step 4.3 execution error: {str(e)}"

        if not args.quiet:
            print(f"✗ {error_msg}", file=sys.stderr)

        if args.verbose:
#             import traceback  # Consolidated to common_imports

            traceback.print_exc()

        logger.error(
            error_msg,
            extra={
                "event": "execution_error",
                "task_id": args.task,
                "workflow_type": args.workflow,
                "agent": "cli_interface",
                "error": str(e),
            },
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
