"""
Real-time execution monitoring system for agent workflows.
Implements Step 4.8 requirements for logging each agent execution.
"""

import base64
import csv
import functools
import hashlib
import json
import logging
import os
import secrets
import stat
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import psutil

try:
    from pythonjsonlogger import jsonlogger
except ImportError:
    # Fallback if pythonjsonlogger is not available
    class JsonFormatter:
        def __init__(self, *args, **kwargs):
            pass
    jsonlogger = type('JsonLogger', (), {'JsonFormatter': JsonFormatter})

# Execution Monitor for AI System

# Provides real-time monitoring and logging of agent executions,
# task progress, and system performance metrics.


class ExecutionMonitor:
    """
    Monitors and tracks agent execution progress and performance.
    """

    def __init__(self, log_dir: str = None):
        """
        Initialize the execution monitor.

        Args:
            log_dir: Directory to store execution logs
        """
        self.log_dir = Path(log_dir) if log_dir else Path("logs/executions")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.executions: Dict[str, Dict] = {}
        self.lock = threading.Lock()

    def start_agent_execution(
            self,
            task_id: str,
            agent_id: str,
            context: Dict = None) -> Dict:
        """
        Start tracking a new agent execution.

        Args:
            task_id: Unique task identifier
            agent_id: Agent performing the task
            context: Additional context data

        Returns:
            Execution data dictionary
        """
        execution_id = f"{task_id}_{agent_id}_{int(time.time())}"

        execution_data = {
            "execution_id": execution_id,
            "task_id": task_id,
            "agent_id": agent_id,
            "start_time": datetime.now().isoformat(),
            "status": "RUNNING",
            "context": context or {},
            "steps": [],
            "metrics": {}
        }

        with self.lock:
            self.executions[execution_id] = execution_data

        self._save_execution_log(execution_data)
        return execution_data

    def complete_agent_execution(
            self,
            execution_data: Dict,
            status: str,
            results: Dict = None,
            error: str = None,
            output: Any = None):
        """
        Mark an agent execution as complete.

        Args:
            execution_data: Execution data from start_agent_execution
            status: Final status (COMPLETED, FAILED, etc.)
            results: Execution results (legacy parameter)
            error: Error message if failed
            output: Agent output (modern parameter)
        """
        execution_id = execution_data["execution_id"]

        with self.lock:
            if execution_id in self.executions:
                self.executions[execution_id].update({
                    "end_time": datetime.now().isoformat(),
                    "status": status,
                    "results": results or {},
                    "output": output,
                    "error": error,
                    "duration_seconds": self._calculate_duration(execution_data["start_time"])
                })

                self._save_execution_log(self.executions[execution_id])

    def log_event(self, task_id: str, event: str,
                  details: Dict[str, Any] = None) -> None:
        """
        Log a workflow event.

        Args:
            task_id: The task identifier
            event: Event name
            details: Additional event details
        """
        try:
            event_data = {
                "task_id": task_id,
                "event": event,
                "details": details or {},
                "timestamp": datetime.now().isoformat()
            }

            # Log to a general events log
            events_log = self.log_dir / "workflow_events.log"
            with open(events_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event_data) + '\n')

        except Exception as e:
            print(
                f"Warning: Could not log event {event} for task {task_id}: {e}")

    def get_execution_stats(self) -> Dict:
        """
        Get summary statistics for all executions.

        Returns:
            Dictionary with execution statistics
        """
        with self.lock:
            total = len(self.executions)
            successful = sum(1 for e in self.executions.values()
                             if e.get("status") == "COMPLETED")

            durations = [
                e.get("duration_seconds", 0)
                for e in self.executions.values()
                if e.get("duration_seconds")
            ]

            avg_duration = sum(durations) / len(durations) if durations else 0

            return {
                "total_executions": total,
                "successful_executions": successful,
                "failed_executions": total - successful,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "average_duration_minutes": avg_duration / 60
            }

    def _calculate_duration(self, start_time_iso: str) -> float:
        """Calculate duration in seconds from start time."""
        start_time = datetime.fromisoformat(start_time_iso)
        return (datetime.now() - start_time).total_seconds()

    def _save_execution_log(self, execution_data: Dict):
        """Save execution data to log file."""
        log_file = self.log_dir / f"{execution_data['execution_id']}.json"
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(execution_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save execution log: {e}")


# Global monitor instance
_monitor_instance: Optional[ExecutionMonitor] = None


def get_execution_monitor() -> ExecutionMonitor:
    """
    Get or create the global execution monitor instance.

    Returns:
        ExecutionMonitor instance
    """
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = ExecutionMonitor()
    return _monitor_instance


def reset_execution_monitor():
    """Reset the global monitor instance (mainly for testing)."""
    global _monitor_instance
    _monitor_instance = None


# LangGraph Integration for Step 4.8
class LangGraphExecutionHook:
    """
    LangGraph callback hook for real-time execution monitoring.
    Integrates with LangGraph's event system for live agent tracking.
    """

    def __init__(self, monitor: ExecutionMonitor, task_id: str):
        self.monitor = monitor
        self.task_id = task_id
        self.active_executions = {}

    def on_node_start(self, node_name: str, state: Dict[str, Any]) -> None:
        """Called when a LangGraph node starts execution."""
        try:
            execution_data = self.monitor.start_agent_execution(
                self.task_id,
                node_name,
                {'node_state': state, 'event': 'node_start'}
            )
            self.active_executions[node_name] = execution_data
        except Exception as e:
            print(
                f"Warning: Failed to start monitoring for node {node_name}: {e}")

    def on_node_end(self, node_name: str, result: Any,
                    error: Optional[str] = None) -> None:
        """Called when a LangGraph node completes execution."""
        try:
            if node_name in self.active_executions:
                execution_data = self.active_executions[node_name]
                status = "FAILED" if error else "COMPLETED"

                self.monitor.complete_agent_execution(
                    execution_data,
                    status=status,
                    output=result,
                    error=error
                )
                del self.active_executions[node_name]
        except Exception as e:
            print(
                f"Warning: Failed to complete monitoring for node {node_name}: {e}")

    def on_workflow_start(self, initial_state: Dict[str, Any]) -> None:
        """Called when LangGraph workflow starts."""
        try:
            self.monitor.log_event(self.task_id, "workflow_start", {
                'initial_state': initial_state,
                'workflow_type': 'langgraph'
            })
        except Exception as e:
            print(f"Warning: Failed to log workflow start: {e}")

    def on_workflow_end(self,
                        final_state: Dict[str,
                                          Any],
                        error: Optional[str] = None) -> None:
        """Called when LangGraph workflow completes."""
        try:
            self.monitor.log_event(self.task_id, "workflow_complete", {
                'final_state': final_state,
                'success': error is None,
                'error': error
            })
        except Exception as e:
            print(f"Warning: Failed to log workflow end: {e}")


class CrewAIExecutionHook:
    """
    CrewAI post-processing hook for real-time execution monitoring.
    Integrates with CrewAI's agent execution lifecycle.
    """

    def __init__(self, monitor: ExecutionMonitor, task_id: str):
        self.monitor = monitor
        self.task_id = task_id
        self.crew_executions = {}

    def on_agent_start(self, agent_name: str, task_description: str) -> None:
        """Called when a CrewAI agent starts task execution."""
        execution_data = self.monitor.start_agent_execution(
            self.task_id,
            agent_name,
            {'task_description': task_description, 'framework': 'crewai'}
        )
        self.crew_executions[agent_name] = execution_data

    def on_agent_complete(
            self,
            agent_name: str,
            result: str,
            success: bool = True) -> None:
        """Called when a CrewAI agent completes task execution."""
        if agent_name in self.crew_executions:
            execution_data = self.crew_executions[agent_name]
            status = "COMPLETED" if success else "FAILED"

            self.monitor.complete_agent_execution(
                execution_data,
                status=status,
                output=result,
                error=None if success else "CrewAI execution failed"
            )
            del self.crew_executions[agent_name]

    def on_crew_result(self, crew_result: Any) -> None:
        """Called when CrewAI crew execution completes."""
        self.monitor.log_event(self.task_id, "crew_execution_complete", {
            'result_type': type(crew_result).__name__,
            'framework': 'crewai'
        })


def create_langgraph_hook(task_id: str) -> LangGraphExecutionHook:
    """Create a LangGraph execution hook for monitoring."""
    monitor = get_execution_monitor()
    return LangGraphExecutionHook(monitor, task_id)


def create_crewai_hook(task_id: str) -> CrewAIExecutionHook:
    """Create a CrewAI execution hook for monitoring."""
    monitor = get_execution_monitor()
    return CrewAIExecutionHook(monitor, task_id)


class DashboardLogger:
    """
    Real-time dashboard logger for agent executions.
    Creates live dashboard data for web interfaces.
    """

    def __init__(self, dashboard_dir: str = "dashboard"):
        self.dashboard_dir = Path(dashboard_dir)
        self.dashboard_dir.mkdir(exist_ok=True)
        self.live_data_file = self.dashboard_dir / "live_execution.json"
        self.status_file = self.dashboard_dir / "agent_status.json"
        self._last_update_time = {}  # Track last update time per task to prevent spam

    def update_live_dashboard(
            self,
            task_id: str,
            agent: str,
            status: str,
            duration: float = 0):
        """Update live dashboard data for real-time monitoring with rate limiting."""
        current_time = time.time()
        update_key = f"{task_id}_{agent}_{status}"

        # Rate limiting: only update every 2 seconds for the same
        # task/agent/status combination
        if update_key in self._last_update_time:
            if current_time - self._last_update_time[update_key] < 2.0:
                return  # Skip this update to prevent spam

        self._last_update_time[update_key] = current_time
        timestamp = datetime.now().isoformat()

        # Update live execution data
        live_data = {
            'timestamp': timestamp,
            'current_task': task_id,
            'current_agent': agent,
            'status': status,
            'duration_minutes': round(duration / 60, 1) if duration > 0 else 0,
            'last_update': timestamp
        }

        try:
            with open(self.live_data_file, 'w', encoding='utf-8') as f:
                json.dump(live_data, f, indent=2)
        except Exception as e:
            # Silent failure to prevent monitoring from breaking workflow
            pass

        # Update agent status tracking
        self._update_agent_status(task_id, agent, status, timestamp)

    def _update_agent_status(
            self,
            task_id: str,
            agent: str,
            status: str,
            timestamp: str):
        """Update agent status tracking for dashboard."""
        status_data = {}

        try:
            # Load existing status data
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)

            # Update status
            if task_id not in status_data:
                status_data[task_id] = {}

            status_data[task_id][agent] = {
                'status': status,
                'timestamp': timestamp,
                'last_seen': timestamp
            }

            # Save updated status
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            # Silent failure to prevent monitoring from breaking workflow
            pass

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data for web interface."""
        dashboard_data = {
            'live_execution': {},
            'agent_status': {},
            'summary_stats': {}
        }

        try:
            # Load live execution data
            if self.live_data_file.exists():
                with open(self.live_data_file, 'r', encoding='utf-8') as f:
                    dashboard_data['live_execution'] = json.load(f)

            # Load agent status data
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    dashboard_data['agent_status'] = json.load(f)

            # Get summary statistics
            monitor = get_execution_monitor()
            dashboard_data['summary_stats'] = monitor.get_execution_stats()
        except Exception as e:
            # Return default data if anything fails
            pass

        return dashboard_data


# Enhanced ExecutionMonitor with dashboard integration
class ExecutionMonitor:
    """
    Monitors and logs agent execution in real-time.
    Creates detailed logs and CSV summaries for dashboard reporting.
    """

    def __init__(self, logs_dir: str = "logs", reports_dir: str = "reports"):
        self.logs_dir = Path(logs_dir)
        self.reports_dir = Path(reports_dir)

        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        # CSV summary file
        self.summary_csv = self.reports_dir / "execution-summary.csv"
        self._init_summary_csv()

        # Configure logger with error handling
        self.logger = logging.getLogger("execution_monitor")
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Step 4.8: Initialize dashboard logger
        self.dashboard_logger = DashboardLogger()

        # Rate limiting for log events
        self._last_event_time = {}

        # Thread safety
        self._lock = threading.Lock()

    def _init_summary_csv(self):
        """Initialize the execution summary CSV file with headers."""
        if not self.summary_csv.exists():
            with open(self.summary_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'task_id', 'agent', 'status',
                    'duration_seconds', 'duration_minutes', 'output_size',
                    'success', 'error_message'
                ])
                writer.writeheader()

    def create_task_logger(self, task_id: str) -> logging.Logger:
        """
        Create a dedicated logger for a specific task execution.

        Args:
            task_id: The task identifier (e.g., BE-07)

        Returns:
            Configured logger for the task
        """
        log_file = self.logs_dir / f"execution-{task_id}.log"

        # Create task-specific logger
        task_logger = logging.getLogger(f"execution_{task_id}")
        task_logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        for handler in task_logger.handlers[:]:
            task_logger.removeHandler(handler)

        # File handler for task-specific log with error handling
        try:
            file_handler = logging.FileHandler(log_file)
            file_formatter = jsonlogger.JsonFormatter(
                '%(asctime)s %(levelname)s %(message)s %(task_id)s %(agent)s %(event)s %(duration)s'
            )
            file_handler.setFormatter(file_formatter)
            task_logger.addHandler(file_handler)
        except Exception as e:
            # Fallback to basic file handler if jsonlogger fails
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s %(levelname)s %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            task_logger.addHandler(file_handler)
            print(f"Warning: Using basic logging format due to: {e}")

        # Console handler for real-time monitoring
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        task_logger.addHandler(console_handler)

        return task_logger

    def start_agent_execution(self,
                              task_id: str,
                              agent: str,
                              context: Dict[str,
                                            Any] = None) -> Dict[str,
                                                                 Any]:
        """
        Log the start of an agent execution with enhanced error handling.

        Args:
            task_id: The task identifier
            agent: The agent name
            context: Additional context information

        Returns:
            Execution tracking data
        """
        start_time = time.time()
        timestamp = datetime.now().isoformat()

        execution_data = {
            'task_id': task_id,
            'agent': agent,
            'start_time': start_time,
            'timestamp': timestamp,
            'context': context or {}
        }

        try:
            # Log to task-specific logger with safe extra parameters
            task_logger = self.create_task_logger(task_id)
            try:
                task_logger.info(
                    f"Starting {agent} agent execution",
                    extra={
                        'task_id': task_id,
                        'agent': agent,
                        'event': 'execution_start',
                        'duration': 0
                    }
                )
            except Exception:
                # Fallback to basic logging if extra parameters cause issues
                task_logger.info(
                    f"Starting {agent} agent execution for task {task_id}")

            # Log to main monitor with safe extra parameters
            try:
                self.logger.info(
                    f"Agent execution started: {task_id} - {agent}",
                    extra={
                        'task_id': task_id,
                        'agent': agent,
                        'event': 'execution_start',
                        'timestamp': timestamp
                    }
                )
            except Exception:
                # Fallback to basic logging
                self.logger.info(
                    f"Agent execution started: {task_id} - {agent}")
        except Exception as e:
            # Ultimate fallback - don't let logging failures break execution
            print(
                f"Warning: Logging failed for task {task_id} agent {agent}: {e}")

        # Step 4.8: Update dashboard (with error handling)
        try:
            self.dashboard_logger.update_live_dashboard(
                task_id, agent, "RUNNING")
        except Exception:
            # Silent failure to prevent monitoring from breaking workflow
            pass

        return execution_data

    def complete_agent_execution(self, execution_data: Dict[str, Any],
                                 status: str = "COMPLETED",
                                 output: Any = None,
                                 error: Optional[str] = None) -> None:
        """
        Log the completion of an agent execution with enhanced error handling.

        Args:
            execution_data: Data from start_agent_execution
            status: Final execution status
            output: Agent output (optional)
            error: Error message if failed (optional)
        """
        try:
            end_time = time.time()
            duration_seconds = end_time - execution_data['start_time']
            duration_minutes = round(duration_seconds / 60, 2)

            task_id = execution_data['task_id']
            agent = execution_data['agent']

            # Determine success
            success = status == "COMPLETED" and error is None

            # Calculate output size safely
            output_size = 0
            try:
                if output:
                    if isinstance(output, str):
                        output_size = len(output)
                    elif isinstance(output, dict):
                        output_size = len(json.dumps(output))
            except Exception:
                output_size = 0  # Safe fallback

            try:
                # Log to task-specific logger with safe extra parameters
                task_logger = self.create_task_logger(task_id)
                try:
                    task_logger.info(
                        f"Agent {agent} completed in {duration_minutes} minutes",
                        extra={
                            'task_id': task_id,
                            'agent': agent,
                            'event': 'execution_complete',
                            'duration': f"{duration_minutes}m",
                            'status': status,
                            'success': success,
                            'error': error})
                except Exception:
                    # Fallback to basic logging
                    task_logger.info(
                        f"Agent {agent} completed in {duration_minutes} minutes - Status: {status}")

                # Log to main monitor with safe extra parameters
                try:
                    self.logger.info(
                        f"Agent execution completed: {task_id} - {agent} in {duration_minutes} minutes",
                        extra={
                            'task_id': task_id,
                            'agent': agent,
                            'event': 'execution_complete',
                            'duration_minutes': duration_minutes,
                            'status': status,
                            'success': success})
                except Exception:
                    # Fallback to basic logging
                    self.logger.info(
                        f"Agent execution completed: {task_id} - {agent} in {duration_minutes} minutes")
            except Exception as e:
                # Ultimate fallback for logging failures
                print(
                    f"Warning: Completion logging failed for task {task_id} agent {agent}: {e}")

            # Write to CSV summary with error handling
            try:
                with self._lock:  # Thread safety
                    self._write_csv_summary({
                        'timestamp': datetime.now().isoformat(),
                        'task_id': task_id,
                        'agent': agent,
                        'status': status,
                        'duration_seconds': round(duration_seconds, 2),
                        'duration_minutes': duration_minutes,
                        'output_size': output_size,
                        'success': success,
                        'error_message': error or ""
                    })
            except Exception as e:
                print(f"Warning: CSV logging failed for task {task_id}: {e}")

            # Print dashboard-style summary (suppress errors)
            try:
                print(f"\n🎯 Agent Execution Summary:")
                print(f"   Task: {task_id}")
                print(f"   Agent: {agent}")
                print(f"   Status: {status}")
                print(f"   Duration: {duration_minutes} minutes")
                print(f"   Success: {'✅' if success else '❌'}")
                if error:
                    print(f"   Error: {error}")
                print(f"   Log: logs/execution-{task_id}.log")
                print(f"   Summary: reports/execution-summary.csv\n")
            except Exception:
                pass

            # Step 4.8: Update dashboard with completion (with error handling)
            try:
                duration = end_time - execution_data['start_time']
                self.dashboard_logger.update_live_dashboard(
                    task_id, agent, status, duration)
            except Exception:
                # Silent failure to prevent monitoring from breaking workflow
                pass

        except Exception as e:
            # Ultimate safety net - don't let monitoring break the workflow
            print(
                f"Warning: Agent execution completion monitoring failed: {e}")

    def _write_csv_summary(self, summary_data: Dict[str, Any]) -> None:
        """Write execution summary to CSV file."""
        with open(self.summary_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=summary_data.keys())
            writer.writerow(summary_data)

    def log_event(self, task_id: str, event: str,
                  details: Dict[str, Any] = None) -> None:
        """
        Log a workflow event with enhanced error handling and rate limiting.

        Args:
            task_id: The task identifier
            event: Event name
            details: Additional event details
        """
        try:
            # Rate limiting: prevent spam logging of the same event
            event_key = f"{task_id}_{event}"
            current_time = time.time()

            if event_key in self._last_event_time:
                # 0.5 second rate limit
                if current_time - self._last_event_time[event_key] < 0.5:
                    return  # Skip this event to prevent spam

            self._last_event_time[event_key] = current_time

            task_logger = self.create_task_logger(task_id)
            try:
                task_logger.info(
                    f"Workflow event: {event}",
                    extra={
                        'task_id': task_id,
                        'event': event,
                        'details': details or {},
                        'duration': ''
                    }
                )
            except Exception:
                # Fallback to basic logging
                task_logger.info(f"Workflow event: {event} for task {task_id}")
        except Exception as e:
            # Don't let event logging break the workflow
            print(f"Warning: Event logging failed for {task_id}/{event}: {e}")

    def get_execution_stats(
            self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get execution statistics from the CSV summary with enhanced error handling.

        Args:
            task_id: Optional task ID to filter stats

        Returns:
            Dictionary with execution statistics
        """
        stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_duration_minutes': 0,
            'agents_used': [],
            'tasks_executed': []
        }

        try:
            if not self.summary_csv.exists():
                return stats

            agents_used = set()
            tasks_executed = set()
            total_duration = 0

            with open(self.summary_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Filter by task_id if specified
                        if task_id and row.get('task_id') != task_id:
                            continue

                        stats['total_executions'] += 1

                        if row.get('success', '').lower() == 'true':
                            stats['successful_executions'] += 1
                        else:
                            stats['failed_executions'] += 1

                        try:
                            duration = float(row.get('duration_minutes', 0))
                            total_duration += duration
                        except (ValueError, TypeError):
                            pass  # Skip invalid duration values

                        agents_used.add(row.get('agent', ''))
                        tasks_executed.add(row.get('task_id', ''))
                    except Exception:
                        # Skip malformed rows
                        continue

            if stats['total_executions'] > 0:
                stats['average_duration_minutes'] = round(
                    total_duration / stats['total_executions'], 2)

            # Convert sets to lists for JSON serialization
            stats['agents_used'] = list(agents_used)
            stats['tasks_executed'] = list(tasks_executed)

        except Exception as e:
            # Return default stats if anything fails
            print(f"Warning: Failed to get execution stats: {e}")

        return stats

    def create_execution_summary_report(
            self, task_id: Optional[str] = None) -> str:
        """Create a comprehensive execution summary report."""
        stats = self.get_execution_stats(task_id)
        dashboard_data = self.dashboard_logger.get_dashboard_data()

        report_lines = [
            "=" * 60,
            "EXECUTION SUMMARY REPORT",
            "=" * 60,
            f"Generated: {datetime.now().isoformat()}",
            f"Task Filter: {task_id or 'ALL TASKS'}",
            "",
            "📊 EXECUTION STATISTICS:",
            f"  Total Executions: {stats['total_executions']}",
            f"  Successful: {stats['successful_executions']} ({(stats['successful_executions'] / max(stats['total_executions'], 1) * 100):.1f}%)",
            f"  Failed: {stats['failed_executions']} ({(stats['failed_executions'] / max(stats['total_executions'], 1) * 100):.1f}%)",
            f"  Average Duration: {stats['average_duration_minutes']} minutes",
            "",
            "🤖 AGENTS USED:",
        ]

        for agent in stats['agents_used']:
            report_lines.append(f"  - {agent}")

        report_lines.extend([
            "",
            "📋 TASKS EXECUTED:",
        ])

        for task in stats['tasks_executed']:
            report_lines.append(f"  - {task}")

        if dashboard_data['live_execution']:
            live = dashboard_data['live_execution']
            report_lines.extend([
                "",
                "🔴 CURRENT EXECUTION:",
                f"  Task: {live.get('current_task', 'None')}",
                f"  Agent: {live.get('current_agent', 'None')}",
                f"  Status: {live.get('status', 'Unknown')}",
                f"  Duration: {live.get('duration_minutes', 0)} minutes",
            ])

        report_lines.extend([
            "",
            "=" * 60,
        ])

        return "\n".join(report_lines)


# Global monitor instance
_execution_monitor = None


def get_execution_monitor() -> ExecutionMonitor:
    """Get the global execution monitor instance."""
    global _execution_monitor
    if _execution_monitor is None:
        _execution_monitor = ExecutionMonitor()
    return _execution_monitor


# Global dashboard logger instance
_dashboard_logger = None


def get_dashboard_logger() -> DashboardLogger:
    """Get the global dashboard logger instance."""
    global _dashboard_logger
    if _dashboard_logger is None:
        _dashboard_logger = DashboardLogger()
    return _dashboard_logger


# Decorator for monitoring agent executions
def monitor_execution(task_id: str, agent: str):
    """
    Decorator to automatically monitor agent execution.

    Usage:
        @monitor_execution("BE-07", "backend")
        def my_agent_function(state):
            # Agent logic here
            return result
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_execution_monitor()
            execution_data = monitor.start_agent_execution(task_id, agent)

            try:
                result = func(*args, **kwargs)
                monitor.complete_agent_execution(
                    execution_data,
                    status="COMPLETED",
                    output=result
                )
                return result
            except Exception as e:
                monitor.complete_agent_execution(
                    execution_data,
                    status="FAILED",
                    error=str(e)
                )
                raise

        return wrapper
    return decorator
