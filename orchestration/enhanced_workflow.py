"""
Enhanced Workflow Executor
Integrates all PHASE 2 enhancements: auto-generated graphs, resilience features,
notifications, and support for monitoring.
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from pythonjsonlogger import jsonlogger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.auto_generate_graph import build_auto_generated_workflow_graph
from graph.graph_builder import (
    build_workflow_graph,
    build_advanced_workflow_graph,
    build_dynamic_workflow_graph
)
from graph.resilient_workflow import create_resilient_workflow
from graph.notifications import SlackNotifier, attach_notifications_to_workflow, NotificationLevel
from orchestration.states import TaskStatus
from utils.task_loader import load_task_metadata, update_task_state

# Configure structured JSON logging for production
logger = logging.getLogger("enhanced_workflow")
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(agent)s %(task_id)s %(event)s')
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.setLevel(logging.INFO)

# LangSmith tracing integration
try:
    from langsmith import traceable
    import os
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    tracing_enabled = True
except ImportError:
    tracing_enabled = False

class EnhancedWorkflowExecutor:
    """
    Executor for LangGraph workflows with enhanced features.
    Integrates auto-generated graphs, resilience, notifications, and monitoring support.
    """
    
    def __init__(
        self,
        workflow_type: str = "dynamic",
        resilience_config: Optional[Dict[str, Any]] = None,
        notification_level: NotificationLevel = NotificationLevel.ALL,
        output_dir: Optional[str] = None
    ):
        """
        Initialize the enhanced workflow executor.
        
        Args:
            workflow_type: Type of workflow to use ('basic', 'advanced', 'dynamic', or 'auto')
            resilience_config: Configuration for resilience features
            notification_level: Level of notifications to send
            output_dir: Directory to store execution outputs
        """
        self.workflow_type = workflow_type
        self.resilience_config = resilience_config or {
            "max_retries": 3,
            "retry_delay": 5,
            "timeout_seconds": 300
        }
        self.notification_level = notification_level
        
        # Set up output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.output_dir = base_dir / "outputs"
            
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        """
        Build and enhance the workflow with all features.
        
        Returns:
            Enhanced workflow with resilience and notifications
        """
        # Step 1: Build the base workflow based on type
        logger.info(f"Building {self.workflow_type} workflow")
        if self.workflow_type == "basic":
            base_workflow = build_workflow_graph()
        elif self.workflow_type == "advanced":
            base_workflow = build_advanced_workflow_graph()
        elif self.workflow_type == "dynamic":
            base_workflow = build_dynamic_workflow_graph()
        elif self.workflow_type == "auto":
            base_workflow = build_auto_generated_workflow_graph()
        else:
            raise ValueError(f"Unknown workflow type: {self.workflow_type}")
        
        # Step 2: Add resilience features
        logger.info("Adding resilience features")
        resilient_workflow = create_resilient_workflow(
            lambda: base_workflow,
            config=self.resilience_config
        )
        
        # Step 3: Add notification support
        logger.info(f"Adding notifications with level: {self.notification_level}")
        notifier = SlackNotifier(notification_level=self.notification_level)
        enhanced_workflow = attach_notifications_to_workflow(
            resilient_workflow,
            notifier,
            self.notification_level
        )
        
        return enhanced_workflow
    
    def prepare_task_directory(self, task_id: str) -> Path:
        """
        Prepare the output directory for a task.
        
        Args:
            task_id: ID of the task to prepare for
            
        Returns:
            Path to the task output directory
        """
        task_dir = self.output_dir / task_id
        os.makedirs(task_dir, exist_ok=True)
        return task_dir
    
    def save_task_status(self, task_id: str, status: Dict[str, Any]):
        """
        Save the task status to a file for monitoring.
        
        Args:
            task_id: ID of the task
            status: Current status information
        """
        task_dir = self.prepare_task_directory(task_id)
        status_path = task_dir / "status.json"
        
        # Add timestamp
        status_with_time = status.copy()
        status_with_time["timestamp"] = datetime.now().isoformat()
        
        with open(status_path, 'w') as f:
            json.dump(status_with_time, f, indent=2)
    
    def save_agent_output(self, task_id: str, agent: str, output: Union[str, dict, Any]):
        """
        Save agent output to a file for monitoring and review.
        
        Args:
            task_id: ID of the task
            agent: Name of the agent
            output: Output content (string or dictionary)
        """
        task_dir = self.prepare_task_directory(task_id)
        output_path = task_dir / f"output_{agent}.md"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {agent.capitalize()} Output for {task_id}\n\n")
                # Convert dictionary to formatted JSON string if needed
                if isinstance(output, dict):
                    f.write("```json\n")
                    f.write(json.dumps(output, indent=2))
                    f.write("\n```")
                elif isinstance(output, str):
                    # If it's already a string, write it directly
                    f.write(output)
                else:
                    # Convert any non-string output to string
                    f.write(str(output))
        except Exception as e:
            logger.error(f"Error saving agent output for {task_id}: {str(e)}")
            # Write a simplified error output if the original attempt fails
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Error saving output for {agent} on task {task_id}\n\n")
                    f.write(f"Error: {str(e)}")
            except Exception:
                pass  # Silently fail if we can't even write the error
    
    def check_dependencies(self, task_id: str) -> tuple[bool, str]:
        """
        Check if all dependencies for a task are satisfied.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Tuple of (is_satisfied, message)
        """
        try:
            # Load task metadata
            task_data = load_task_metadata(task_id)
            dependencies = task_data.get("depends_on", [])
            
            # If no dependencies, return satisfied
            if not dependencies:
                return True, "No dependencies"
            
            # Check each dependency
            unsatisfied = []
            for dep_id in dependencies:
                try:
                    dep_data = load_task_metadata(dep_id)
                    dep_state = dep_data.get("state", "")
                    
                    # Only DONE state is considered satisfied
                    if dep_state != "DONE" and dep_state != TaskStatus.DONE:
                        unsatisfied.append(dep_id)
                except Exception:
                    # If we can't load the dependency, consider it unsatisfied
                    unsatisfied.append(dep_id)
            
            # Return result
            if unsatisfied:
                return False, f"Missing dependencies: {', '.join(unsatisfied)}"
            else:
                return True, "All dependencies satisfied"
                
        except Exception as e:
            logger.error(f"Error checking dependencies for task {task_id}: {str(e)}")
            return False, f"Error checking dependencies: {str(e)}"
    
    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """
        Execute a task through the enhanced workflow.
        
        Args:
            task_id: ID of the task to execute
            
        Returns:
            Result of the workflow execution
        """
        logger.info(f"Executing task {task_id}")
        
        # Load task metadata
        try:
            task_data = load_task_metadata(task_id)
        except Exception as e:
            logger.error(f"Failed to load task metadata for {task_id}: {str(e)}")
            task_data = {"id": task_id}
        
        # Prepare initial state
        initial_state = {
            "task_id": task_id,
            "status": TaskStatus.CREATED,
            "title": task_data.get("title", ""),
            "description": task_data.get("description", ""),
            "context_keys": task_data.get("context", []),
            "start_time": datetime.now().isoformat()
        }
        
        # Save initial status for monitoring
        self.save_task_status(task_id, initial_state)
        
        def agent_run(agent, input_state):
            if tracing_enabled:
                @traceable(name="Agent Run")
                def traced_run(agent, input_state):
                    return agent.run(input_state)
                return traced_run(agent, input_state)
            else:
                return agent.run(input_state)
        
        try:
            # Execute the workflow
            result = self.workflow.invoke(initial_state)
            
            # Ensure task_id is in the result (required by tests)
            if "task_id" not in result:
                result["task_id"] = task_id
            
            # Save final status
            self.save_task_status(task_id, result)
            
            # Save agent outputs
            if "output" in result:
                agent = result.get("agent", "unknown")
                self.save_agent_output(task_id, agent, result["output"])
            
            return result
        except Exception as e:
            # Handle execution error
            error_state = {
                "task_id": task_id,
                "status": TaskStatus.BLOCKED,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            # Save error status
            self.save_task_status(task_id, error_state)
            
            # Save error to log file
            task_dir = self.prepare_task_directory(task_id)
            error_path = task_dir / "error.log"
            try:
                with open(error_path, 'w', encoding='utf-8') as f:
                    # Handle both string and dictionary error objects
                    if isinstance(e, dict):
                        f.write(json.dumps(e))  # Convert dict to JSON string
                    else:
                        f.write(str(e))
            except Exception as write_error:
                logger.error(f"Error writing to error log: {str(write_error)}")
            
            logger.error(f"Error executing task {task_id}: {str(e)}")
            return error_state

def main():
    """Command-line interface for the enhanced workflow executor."""
    parser = argparse.ArgumentParser(description="Execute tasks with enhanced LangGraph workflow")
    parser.add_argument("--task", "-t", help="Task ID to execute (e.g., BE-07)")
    parser.add_argument("--workflow", "-w", default="dynamic", 
                        choices=["basic", "advanced", "dynamic", "auto"],
                        help="Workflow type to use")
    parser.add_argument("--notifications", "-n", default="all",
                        choices=["all", "error", "state_change", "completion", "none"],
                        help="Notification level")
    parser.add_argument("--output", "-o", help="Output directory for task results")
    
    args = parser.parse_args()
    
    if not args.task:
        parser.error("Task ID is required")
    
    # Map notification level
    notification_level_map = {
        "all": NotificationLevel.ALL,
        "error": NotificationLevel.ERROR,
        "state_change": NotificationLevel.STATE_CHANGE,
        "completion": NotificationLevel.COMPLETION,
        "none": NotificationLevel.NONE
    }
    notification_level = notification_level_map.get(args.notifications, NotificationLevel.ALL)
    
    # Create and run the enhanced workflow
    executor = EnhancedWorkflowExecutor(
        workflow_type=args.workflow,
        notification_level=notification_level,
        output_dir=args.output
    )
    
    result = executor.execute_task(args.task)
    
    # Print result summary
    print(f"\nTask Execution Summary for {args.task}:")
    print(f"Status: {result.get('status', 'Unknown')}")
    if "error" in result:
        print(f"Error: {result['error']}")
    print(f"Agent: {result.get('agent', 'Unknown')}")
    print(f"Output saved to: {executor.output_dir / args.task}")
    print("\nFor real-time monitoring, run:")
    print(f"python scripts/monitor_workflow.py --task {args.task}")

if __name__ == "__main__":
    main()