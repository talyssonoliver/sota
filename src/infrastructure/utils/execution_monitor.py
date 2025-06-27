"""Execution monitoring utilities."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import logging

class ExecutionMonitor:
    """Monitor execution of tasks and workflows."""
    
    def __init__(self):
        """Initialize execution monitor."""
        self.executions = []
    
    def start_monitoring(self, task_id):
        """Start monitoring a task execution."""
        execution = {
            "task_id": task_id,
            "status": "running",
            "start_time": "now"
        }
        self.executions.append(execution)
        return execution
    
    def stop_monitoring(self, task_id):
        """Stop monitoring a task execution."""
        for execution in self.executions:
            if execution["task_id"] == task_id:
                execution["status"] = "completed"
                execution["end_time"] = "now"
                break

class DashboardLogger:
    """Logger for dashboard updates and live execution tracking."""
    
    def __init__(self, dashboard_dir: str = "dashboard"):
        """Initialize dashboard logger."""
        self.dashboard_dir = Path(dashboard_dir)
        self.dashboard_dir.mkdir(exist_ok=True)
        
        # Ensure required dashboard files exist
        self.live_execution_file = self.dashboard_dir / "live_execution.json"
        self.agent_status_file = self.dashboard_dir / "agent_status.json"
        
        # Initialize files if they don't exist
        if not self.live_execution_file.exists():
            self._initialize_live_execution()
        if not self.agent_status_file.exists():
            self._initialize_agent_status()
    
    def _initialize_live_execution(self):
        """Initialize live execution JSON file."""
        initial_data = {
            "last_updated": datetime.now().isoformat(),
            "active_tasks": {},
            "completed_tasks": {},
            "failed_tasks": {}
        }
        with open(self.live_execution_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    def _initialize_agent_status(self):
        """Initialize agent status JSON file."""
        initial_data = {
            "last_updated": datetime.now().isoformat(),
            "agents": {},
            "summary": {
                "total_agents": 0,
                "active_agents": 0,
                "idle_agents": 0
            }
        }
        with open(self.agent_status_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    def update_live_dashboard(self, task_id: str, agent: str, status: str, duration: Optional[float] = None):
        """Update live dashboard with task execution data."""
        try:
            # Update live execution data
            self._update_live_execution(task_id, agent, status, duration)
            
            # Update agent status
            self._update_agent_status(agent, status, task_id)
            
        except Exception as e:
            print(f"Warning: Failed to update dashboard: {e}")
    
    def _update_live_execution(self, task_id: str, agent: str, status: str, duration: Optional[float] = None):
        """Update live execution JSON file."""
        try:
            # Load current data
            with open(self.live_execution_file, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"last_updated": "", "active_tasks": {}, "completed_tasks": {}, "failed_tasks": {}}
        
        # Prepare task data
        task_data = {
            "task_id": task_id,
            "agent": agent,
            "status": status,
            "last_updated": datetime.now().isoformat(),
            "duration": duration
        }
        
        # Remove from other categories first
        data["active_tasks"].pop(task_id, None)
        data["completed_tasks"].pop(task_id, None)
        data["failed_tasks"].pop(task_id, None)
        
        # Add to appropriate category
        if status.upper() in ["COMPLETED", "DONE", "SUCCESS"]:
            data["completed_tasks"][task_id] = task_data
        elif status.upper() in ["FAILED", "ERROR", "BLOCKED"]:
            data["failed_tasks"][task_id] = task_data
        else:
            data["active_tasks"][task_id] = task_data
        
        # Update metadata
        data["last_updated"] = datetime.now().isoformat()
        
        # Save updated data
        with open(self.live_execution_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _update_agent_status(self, agent: str, status: str, task_id: str):
        """Update agent status JSON file."""
        try:
            # Load current data
            with open(self.agent_status_file, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"last_updated": "", "agents": {}, "summary": {}}
        
        # Update agent data
        if agent not in data["agents"]:
            data["agents"][agent] = {
                "status": "idle",
                "current_task": None,
                "last_activity": None,
                "tasks_completed": 0,
                "tasks_failed": 0
            }
        
        agent_data = data["agents"][agent]
        agent_data["last_activity"] = datetime.now().isoformat()
        
        if status.upper() in ["COMPLETED", "DONE", "SUCCESS"]:
            agent_data["status"] = "idle"
            agent_data["current_task"] = None
            agent_data["tasks_completed"] = agent_data.get("tasks_completed", 0) + 1
        elif status.upper() in ["FAILED", "ERROR", "BLOCKED"]:
            agent_data["status"] = "error"
            agent_data["current_task"] = task_id
            agent_data["tasks_failed"] = agent_data.get("tasks_failed", 0) + 1
        else:
            agent_data["status"] = "active"
            agent_data["current_task"] = task_id
        
        # Update summary
        total_agents = len(data["agents"])
        active_agents = len([a for a in data["agents"].values() if a["status"] == "active"])
        idle_agents = len([a for a in data["agents"].values() if a["status"] == "idle"])
        
        data["summary"] = {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "idle_agents": idle_agents,
            "error_agents": total_agents - active_agents - idle_agents
        }
        
        data["last_updated"] = datetime.now().isoformat()
        
        # Save updated data
        with open(self.agent_status_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def log_dashboard_event(self, event_type: str, data: Dict[str, Any]):
        """Log dashboard events for debugging."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        log_file = self.dashboard_dir / "dashboard_events.log"
        with open(log_file, 'a') as f:
            f.write(f"{json.dumps(log_entry)}\n")
    
    def get_live_status(self) -> Dict[str, Any]:
        """Get current live execution status."""
        try:
            with open(self.live_execution_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"active_tasks": {}, "completed_tasks": {}, "failed_tasks": {}}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        try:
            with open(self.agent_status_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"agents": {}, "summary": {}}

class LangGraphHook:
    """Hook for monitoring LangGraph workflow execution."""
    
    def __init__(self, task_id: str):
        """Initialize the hook."""
        self.task_id = task_id
        
    def on_workflow_start(self, state: Dict[str, Any]):
        """Called when workflow starts."""
        print(f"Workflow started for task {self.task_id}")
        
    def on_workflow_end(self, state: Dict[str, Any]):
        """Called when workflow ends."""
        print(f"Workflow ended for task {self.task_id}")
        
    def on_error(self, error: Exception):
        """Called when workflow errors."""
        print(f"Workflow error for task {self.task_id}: {error}")

def create_langgraph_hook(task_id: str) -> LangGraphHook:
    """Create a LangGraph monitoring hook for a task."""
    return LangGraphHook(task_id)

class CrewAIExecutionHook:
    """Hook for monitoring CrewAI execution."""
    
    def __init__(self, task_id: str):
        """Initialize the CrewAI hook."""
        self.task_id = task_id
        self.start_time = None
        self.end_time = None
        
    def on_crew_start(self, crew_data: Dict[str, Any]):
        """Called when CrewAI crew starts."""
        self.start_time = datetime.now()
        print(f"CrewAI crew started for task {self.task_id}")
        
    def on_crew_end(self, crew_data: Dict[str, Any]):
        """Called when CrewAI crew ends."""
        self.end_time = datetime.now()
        print(f"CrewAI crew completed for task {self.task_id}")
        
    def on_agent_start(self, agent_name: str, agent_data: Dict[str, Any]):
        """Called when an agent starts."""
        print(f"Agent {agent_name} started for task {self.task_id}")
        
    def on_agent_end(self, agent_name: str, agent_data: Dict[str, Any]):
        """Called when an agent ends."""
        print(f"Agent {agent_name} completed for task {self.task_id}")
        
    def on_error(self, error: Exception):
        """Called when CrewAI encounters an error."""
        print(f"CrewAI error for task {self.task_id}: {error}")
    
    def get_execution_time(self) -> Optional[float]:
        """Get total execution time in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

def create_crewai_hook(task_id: str) -> CrewAIExecutionHook:
    """Create a CrewAI monitoring hook for a task."""
    return CrewAIExecutionHook(task_id)

def get_execution_monitor() -> ExecutionMonitor:
    """Get the global execution monitor instance."""
    if not hasattr(get_execution_monitor, '_instance'):
        get_execution_monitor._instance = ExecutionMonitor()
    return get_execution_monitor._instance

__all__ = ["ExecutionMonitor", "DashboardLogger", "LangGraphHook", "CrewAIExecutionHook", 
           "create_langgraph_hook", "create_crewai_hook", "get_execution_monitor"]
