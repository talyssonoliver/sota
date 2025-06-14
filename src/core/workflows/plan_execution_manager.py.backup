"""
Plan Execution Manager for orchestrating JSON-based plans from the Coordinator Agent.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from orchestration.states import TaskStatus

logger = logging.getLogger(__name__)


class PlanExecutionManager:
    """
    Manages the execution of JSON-based plans from the Coordinator Agent.
    
    Handles dependency tracking, task execution, and coordinator re-planning loops.
    """
    
    def __init__(self, initial_task_id: str, initial_task_description: str, workflow_engine):
        """
        Initialize the Plan Execution Manager.
        
        Args:
            initial_task_id: The main task identifier
            initial_task_description: Description of the main task
            workflow_engine: The compiled LangGraph workflow
        """
        self.main_task_id = initial_task_id
        self.main_task_description = initial_task_description
        self.workflow_engine = workflow_engine
        self.plan = []
        self.completed_parts = {}  # Store outputs of completed tasks: {id: output}
        self.part_status = {}  # Store status: {id: "pending" | "running" | "completed" | "failed"}

    def _invoke_coordinator(self, feedback_from_completed_tasks: Optional[List[Dict]] = None) -> bool:
        """
        Invoke the Coordinator agent to get a plan or handle re-planning.
        
        Args:
            feedback_from_completed_tasks: Results from completed plan parts
            
        Returns:
            True if coordinator provided valid plan, False otherwise
        """
        logger.info(f"Invoking Coordinator for task: {self.main_task_id}")
        
        coordinator_input_state = {
            "task_id": self.main_task_id,
            "message": self.main_task_description,
            "completed_parts_feedback": feedback_from_completed_tasks or [],
        }
        
        try:
            # Invoke the workflow which should hit the coordinator first
            coordinator_output_state = self.workflow_engine.invoke(coordinator_input_state)
            
            raw_plan_output = coordinator_output_state.get("output", "")
            
            # Try to parse the coordinator's output as JSON
            try:
                if isinstance(raw_plan_output, str):
                    plan_data = json.loads(raw_plan_output)
                elif isinstance(raw_plan_output, dict) and "plan" in raw_plan_output:
                    plan_data = raw_plan_output["plan"]
                else:
                    plan_data = raw_plan_output

                if isinstance(plan_data, list):
                    # Full plan received
                    self.plan = plan_data
                    for task in self.plan:
                        if task["id"] not in self.part_status:
                            self.part_status[task["id"]] = "pending"
                    logger.info("Coordinator provided new/updated full plan.")
                    return True
                elif isinstance(plan_data, dict) and "id" in plan_data:
                    # Single next task received
                    logger.info(f"Coordinator provided next part: {plan_data['id']}")
                    # For now, assume full plan is always re-issued
                    pass

            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON plan from Coordinator: {e}")
                logger.error(f"Raw output: {raw_plan_output}")
                return False
            except TypeError as e:
                logger.error(f"Unexpected plan format from Coordinator: {e}")
                logger.error(f"Raw output: {raw_plan_output}")
                return False
                
        except Exception as e:
            logger.error(f"Error invoking coordinator: {e}")
            return False
            
        return True

    def _execute_part(self, part_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single part of the plan using the appropriate agent.
        
        Args:
            part_details: Dictionary containing part information
            
        Returns:
            Dictionary with execution result
        """
        part_id = part_details["id"]
        logger.info(f"Executing part: {part_id} - {part_details['description']} for agent {part_details['agent_role']}")
        
        self.part_status[part_id] = "running"

        # Prepare input for the specialist agent
        agent_input_data = part_details.get("input_data", "")
        
        agent_input_state = {
            "task_id": part_id,
            "message": part_details["description"],
            "input_data": agent_input_data,
            "main_task_id": self.main_task_id,
            "agent_to_run": part_details["agent_role"]
        }

        try:
            # Execute the workflow for this specific agent/part
            result_state = self.workflow_engine.invoke(agent_input_state)

            # Check for error conditions including enhanced error info
            error_info = result_state.get("error_info")
            if result_state.get("status") == TaskStatus.BLOCKED or error_info or result_state.get("error"):
                error_message = error_info.get("message") if error_info else result_state.get("error", "Unknown error")
                logger.error(f"Part {part_id} FAILED. Error: {error_message}")
                
                # Store detailed error information
                self.completed_parts[part_id] = {
                    "error": error_message,
                    "error_info": error_info,
                    "output": result_state.get("output"),
                    "attempt_count": result_state.get("attempt_count", 1)
                }
                self.part_status[part_id] = "failed"
                return {
                    "id": part_id, 
                    "status": "failed", 
                    "result": result_state.get("output"),
                    "error_info": error_info,
                    "attempt_count": result_state.get("attempt_count", 1)
                }
            else:
                logger.info(f"Part {part_id} COMPLETED.")
                self.completed_parts[part_id] = result_state.get("output")
                self.part_status[part_id] = "completed"
                return {
                    "id": part_id, 
                    "status": "completed", 
                    "result": result_state.get("output"),
                    "attempt_count": result_state.get("attempt_count", 1)
                }
                
        except Exception as e:
            logger.error(f"Critical error executing part {part_id}: {e}")
            self.completed_parts[part_id] = {
                "error": str(e), 
                "output": "Critical execution failure"
            }
            self.part_status[part_id] = "failed"
            return {"id": part_id, "status": "failed", "result": str(e)}

    def run_plan(self) -> Dict[str, Any]:
        """
        Execute the complete plan with coordinator feedback loops.
        
        Returns:
            Final execution result with status and completed tasks
        """
        # 1. Initial call to Coordinator to get the plan
        if not self._invoke_coordinator():
            logger.error("Failed to get initial plan from Coordinator. Aborting.")
            return {"status": "FAILED", "reason": "Initial planning failed"}

        max_iterations = 20  # Prevent infinite loops
        current_iteration = 0

        while current_iteration < max_iterations:
            current_iteration += 1
            logger.info(f"Plan Execution Iteration: {current_iteration}")

            # Find tasks ready to run (dependencies completed)
            next_tasks_to_run = []
            for part_details in self.plan:
                part_id = part_details["id"]
                if self.part_status.get(part_id) == "pending":
                    dependencies = part_details.get("dependencies", [])
                    if all(self.part_status.get(dep_id) == "completed" for dep_id in dependencies):
                        next_tasks_to_run.append(part_details)
            
            if not next_tasks_to_run:
                # Check if all tasks are done
                if all(status in ["completed", "failed"] for status in self.part_status.values()) and \
                   len(self.part_status) == len(self.plan):
                    logger.info("All parts processed.")
                    # Final call to coordinator to confirm completion
                    final_feedback = [
                        {
                            "id": tid, 
                            "status": self.part_status[tid], 
                            "result": self.completed_parts.get(tid)
                        } 
                        for tid in self.part_status
                    ]
                    self._invoke_coordinator(feedback_from_completed_tasks=final_feedback)
                    break 
                else:
                    logger.warning("No tasks ready to run, but not all tasks are done. Possible deadlock.")
                    # Re-invoke coordinator with current state for potential replanning
                    current_state_feedback = [
                        {
                            "id": tid, 
                            "status": self.part_status[tid], 
                            "result": self.completed_parts.get(tid)
                        } 
                        for tid in self.part_status if self.part_status[tid] != "pending"
                    ]
                    if not self._invoke_coordinator(feedback_from_completed_tasks=current_state_feedback):
                        logger.error("Coordinator re-invocation failed.")
                        break

            # Execute ready tasks
            completed_tasks_in_iteration = []
            for part_to_run in next_tasks_to_run:
                # TODO: Handle parallel execution if desired
                execution_result = self._execute_part(part_to_run)
                completed_tasks_in_iteration.append(execution_result)
            
            # Feed results back to Coordinator for re-planning/next steps
            if completed_tasks_in_iteration:
                if not self._invoke_coordinator(feedback_from_completed_tasks=completed_tasks_in_iteration):
                    logger.error("Failed to get updated plan/next steps from Coordinator. Aborting.")
                    return {"status": "FAILED", "reason": "Re-planning failed"}

            # Check if coordinator signals completion
            if not self.plan or (len(self.plan) == 1 and self.plan[0].get("agent_role") == "END_PLAN"):
                logger.info("Coordinator signaled plan completion.")
                break
        
        if current_iteration >= max_iterations:
            logger.warning("Reached max iterations. Exiting plan execution.")

        # Determine final status
        final_status = "COMPLETED" if all(s == "completed" for s in self.part_status.values()) else "PARTIAL"
        if any(s == "failed" for s in self.part_status.values()):
            final_status = "FAILED"
            
        logger.info(f"Plan execution finished with status: {final_status}")
        return {
            "status": final_status, 
            "completed_tasks": self.completed_parts,
            "task_statuses": self.part_status
        }