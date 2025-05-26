"""
Real-time Workflow Monitoring CLI
Provides a live view of LangGraph workflow execution progress.
"""

import os
import sys
import time
import json
import argparse
import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.states import TaskStatus
from utils.execution_monitor import get_execution_monitor, get_dashboard_logger

# Configure structured JSON logging for production
logger = logging.getLogger("workflow_monitor")
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(event)s %(task_id)s')
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.setLevel(logging.INFO)

# Function to clear terminal screen
def clear_screen():
    """Clear the terminal screen based on the operating system."""
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Linux/Mac
        os.system('clear')

class NodeStatus(str, Enum):
    """Status of a node in the workflow"""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    WAITING = "WAITING"

class WorkflowMonitor:
    """
    Monitor for LangGraph workflow executions.
    """
    
    def __init__(self, task_id=None, output_dir="outputs", simple_mode=False):
        self.task_id = task_id
        self.output_dir = Path(output_dir)
        self.simple_mode = simple_mode
        
        # Step 4.8: Initialize monitoring components
        self.execution_monitor = get_execution_monitor()
        self.dashboard_logger = get_dashboard_logger()
        
        # Current state of the workflow
        self.nodes_status = {}
        self.task_status = {}
        self.current_node = None
        self.start_time = datetime.now()
        self.last_update_time = None
        self.message_log = []
        
        # Last seen files to detect changes
        self.last_seen_files = {}
        # Track last seen status to prevent duplicate updates
        self.last_status = {}
    
    def add_log_message(self, message: str, level: str = "INFO", task_id: Optional[str] = None):
        """
        Add a message to the log.
        
        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)
            task_id: Task ID associated with the log message
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.message_log.append(f"[{timestamp}] [{level}] {message}")
        
        # Create proper extra params dictionary for structured logging
        extra_params = {
            "event": "monitor_event" if level != "ERROR" else "monitor_error",
            "task_id": task_id
        }
        
        if level == "ERROR":
            logger.error(message, extra=extra_params)
        else:
            logger.info(message, extra=extra_params)
        
        # Keep only the last 100 messages
        if len(self.message_log) > 100:
            self.message_log = self.message_log[-100:]
    
    def scan_output_directory(self):
        """
        Scan the output directory for task files and update the status.
        """
        # Check if directory exists
        if not os.path.exists(self.output_dir):
            self.add_log_message(f"Output directory {self.output_dir} does not exist", "WARNING")
            return
        
        # Find all task directories
        task_dirs = []
        if self.task_id:
            # If we're monitoring a specific task, just use that directory
            if os.path.isdir(self.output_dir):
                task_dirs = [self.output_dir]
        else:
            # Otherwise, find all task directories
            try:
                for entry in os.scandir(self.output_dir):
                    if entry.is_dir():
                        task_dirs.append(entry.path)
            except Exception as e:
                self.add_log_message(f"Error scanning output directory: {str(e)}", "ERROR")
                return
        
        # Process each task directory
        for task_dir in task_dirs:
            task_id = os.path.basename(task_dir)
            
            # Check for status.json
            status_file = os.path.join(task_dir, "status.json")
            if os.path.exists(status_file):
                try:
                    # Check if file has changed
                    mtime = os.path.getmtime(status_file)
                    if status_file in self.last_seen_files and self.last_seen_files[status_file] == mtime:
                        # File hasn't changed, skip processing
                        continue
                    
                    # Update last seen time
                    self.last_seen_files[status_file] = mtime
                    
                    with open(status_file, 'r') as f:
                        status_data = json.load(f)
                        
                    current_status = status_data.get("status", "Unknown")
                    
                    # Skip if status hasn't changed for this task
                    if task_id in self.last_status and self.last_status[task_id] == current_status:
                        continue
                    
                    # Update task status and track it
                    self.task_status[task_id] = current_status
                    self.last_status[task_id] = current_status
                    
                    # Update current node
                    agent = status_data.get("agent")
                    if agent:
                        self.current_node = agent
                        self.nodes_status[agent] = NodeStatus.RUNNING
                        
                        # Mark previously running nodes as completed
                        for node, status in self.nodes_status.items():
                            if node != agent and status == NodeStatus.RUNNING:
                                self.nodes_status[node] = NodeStatus.COMPLETED
                    
                    # Update last update time
                    self.last_update_time = datetime.now()
                    
                    # Add log message
                    self.add_log_message(f"Task {task_id} status updated: {self.task_status[task_id]}", task_id=task_id)
                    
                except Exception as e:
                    self.add_log_message(f"Error processing status file {status_file}: {str(e)}", "ERROR", task_id=task_id)
                    # Don't continue processing this task if there was an error
                    continue
            
            # Check for agent output files
            for agent_role in ["coordinator", "technical", "backend", "frontend", "qa", "documentation"]:
                output_file = os.path.join(task_dir, f"output_{agent_role}.md")
                if os.path.exists(output_file):
                    # Check if file has changed
                    mtime = os.path.getmtime(output_file)
                    if output_file in self.last_seen_files and self.last_seen_files[output_file] == mtime:
                        # File hasn't changed, skip processing
                        continue
                    
                    # Update last seen time
                    self.last_seen_files[output_file] = mtime
                    
                    # Update node status
                    if agent_role not in self.nodes_status or self.nodes_status[agent_role] != NodeStatus.RUNNING:
                        self.nodes_status[agent_role] = NodeStatus.COMPLETED
                    
                    # Add log message
                    self.add_log_message(f"Agent {agent_role} completed for task {task_id}", task_id=task_id)
            
            # Check for error files
            error_file = os.path.join(task_dir, "error.log")
            if os.path.exists(error_file):
                # Check if file has changed
                mtime = os.path.getmtime(error_file)
                if error_file in self.last_seen_files and self.last_seen_files[error_file] == mtime:
                    # File hasn't changed, skip processing
                    continue
                
                # Update last seen time
                self.last_seen_files[error_file] = mtime
                
                try:
                    with open(error_file, 'r') as f:
                        error_message = f.read().strip()
                    
                    # Try to parse as JSON if it looks like JSON
                    if error_message.startswith('{'):
                        try:
                            error_data = json.loads(error_message)
                            if isinstance(error_data, dict):
                                # Extract meaningful error message from dict
                                if 'error' in error_data:
                                    error_message = str(error_data['error'])
                                elif 'message' in error_data:
                                    error_message = str(error_data['message'])
                                else:
                                    error_message = json.dumps(error_data)
                        except json.JSONDecodeError:
                            # Not JSON, use as is
                            pass
                    
                    # Add log message
                    self.add_log_message(f"Error in task {task_id}: {error_message}", "ERROR", task_id=task_id)
                    
                    # If the current node is known, mark it as failed
                    if self.current_node:
                        self.nodes_status[self.current_node] = NodeStatus.FAILED
                except Exception as e:
                    self.add_log_message(f"Error processing error file {error_file}: {str(e)}", "ERROR", task_id=task_id)

    def display_dashboard_data(self):
        """Display real-time dashboard data."""
        dashboard_data = self.dashboard_logger.get_dashboard_data()
        
        print("\n" + "="*60)
        print("📊 REAL-TIME EXECUTION DASHBOARD")
        print("="*60)
        
        # Current execution
        if dashboard_data.get('live_execution'):
            live = dashboard_data['live_execution']
            print(f"🔴 CURRENT EXECUTION:")
            print(f"   Task: {live.get('current_task', 'None')}")
            print(f"   Agent: {live.get('current_agent', 'None')}")
            print(f"   Status: {live.get('status', 'Unknown')}")
            print(f"   Duration: {live.get('duration_minutes', 0)} minutes")
            print(f"   Last Update: {live.get('last_update', 'Unknown')}")
        else:
            print("🔴 CURRENT EXECUTION: No active executions")
        
        # Summary statistics
        if dashboard_data.get('summary_stats'):
            stats = dashboard_data['summary_stats']
            print(f"\n📈 EXECUTION STATISTICS:")
            print(f"   Total Executions: {stats.get('total_executions', 0)}")
            print(f"   Success Rate: {stats.get('successful_executions', 0)}/{stats.get('total_executions', 0)}")
            print(f"   Average Duration: {stats.get('average_duration_minutes', 0)} minutes")
            print(f"   Active Agents: {len(stats.get('agents_used', []))}")
        
        # Agent status
        if dashboard_data.get('agent_status'):
            print(f"\n🤖 AGENT STATUS:")
            for task_id, agents in dashboard_data['agent_status'].items():
                print(f"   Task {task_id}:")
                for agent_name, agent_info in agents.items():
                    status_icon = "✅" if agent_info['status'] == "COMPLETED" else "🔄" if agent_info['status'] == "RUNNING" else "❌"
                    print(f"     {status_icon} {agent_name}: {agent_info['status']}")
    
    def run_simple_monitor(self):
        """Run the monitoring in simple console mode with dashboard data."""
        print("🎯 Starting Workflow Monitoring (Simple Mode)")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while True:
                clear_screen()
                print(f"Workflow Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Display dashboard data
                self.display_dashboard_data()
                
                # Display execution summary
                if self.task_id:
                    report = self.execution_monitor.create_execution_summary_report(self.task_id)
                    print(f"\n📋 TASK SUMMARY ({self.task_id}):")
                    print(report)
                
                print(f"\n⏰ Monitoring... (refreshing every 5 seconds)")
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n✅ Monitoring stopped by user")

class OutputDirectoryEventHandler(FileSystemEventHandler):
    """
    Event handler for file system changes in the output directory.
    """
    
    def __init__(self, monitor: WorkflowMonitor):
        """
        Initialize the event handler.
        
        Args:
            monitor: WorkflowMonitor instance to update
        """
        self.monitor = monitor
    
    def on_modified(self, event):
        """
        Called when a file in the output directory is modified.
        
        Args:
            event: File system event
        """
        if not event.is_directory:
            self.monitor.scan_output_directory()
    
    def on_created(self, event):
        """
        Called when a file in the output directory is created.
        
        Args:
            event: File system event
        """
        if not event.is_directory:
            self.monitor.scan_output_directory()

def draw_ui(stdscr, monitor: WorkflowMonitor, curses_module):
    """
    Draw the UI for the workflow monitor.
    
    Args:
        stdscr: Curses screen
        monitor: WorkflowMonitor instance
        curses_module: The imported curses module
    """
    # Clear screen
    stdscr.clear()
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Safety check for minimum dimensions
    if height < 10 or width < 40:
        stdscr.addstr(0, 0, "Terminal too small", curses_module.color_pair(3) | curses_module.A_BOLD)
        stdscr.refresh()
        return
    
    # Set up colors
    curses_module.start_color()
    curses_module.init_pair(1, curses_module.COLOR_WHITE, curses_module.COLOR_BLACK)  # Default
    curses_module.init_pair(2, curses_module.COLOR_GREEN, curses_module.COLOR_BLACK)  # Success
    curses_module.init_pair(3, curses_module.COLOR_RED, curses_module.COLOR_BLACK)    # Error
    curses_module.init_pair(4, curses_module.COLOR_YELLOW, curses_module.COLOR_BLACK) # Warning/Running
    curses_module.init_pair(5, curses_module.COLOR_CYAN, curses_module.COLOR_BLACK)   # Info
    curses_module.init_pair(6, curses_module.COLOR_MAGENTA, curses_module.COLOR_BLACK) # Special
    
    # Draw title
    title = "LangGraph Workflow Monitor"
    stdscr.addstr(0, (width - len(title)) // 2, title, curses_module.color_pair(6) | curses_module.A_BOLD)
    
    # Draw task info
    if monitor.task_id:
        task_info = f"Monitoring task: {monitor.task_id}"
    else:
        task_info = "Monitoring all tasks"
    stdscr.addstr(1, 0, task_info, curses_module.color_pair(5))
    
    # Draw runtime info
    runtime = datetime.now() - monitor.start_time
    runtime_info = f"Runtime: {str(runtime).split('.')[0]}"
    stdscr.addstr(1, width - len(runtime_info) - 1, runtime_info, curses_module.color_pair(5))
    
    # Draw status info
    status_line = 3
    stdscr.addstr(status_line, 0, "Task Status:", curses_module.color_pair(1) | curses_module.A_BOLD)
    status_line += 1
    
    for task_id, status in monitor.task_status.items():
        status_color = curses_module.color_pair(1)
        if status == TaskStatus.DONE:
            status_color = curses_module.color_pair(2)
        elif status == TaskStatus.BLOCKED:
            status_color = curses_module.color_pair(3)
        elif status in [TaskStatus.IN_PROGRESS, TaskStatus.QA_PENDING, TaskStatus.DOCUMENTATION]:
            status_color = curses_module.color_pair(4)
            
        status_text = f"{task_id}: {status}"
        stdscr.addstr(status_line, 2, status_text, status_color)
        status_line += 1
    
    # Draw node status info
    node_line = status_line + 1
    stdscr.addstr(node_line, 0, "Agent Status:", curses_module.color_pair(1) | curses_module.A_BOLD)
    node_line += 1
    
    for node, status in sorted(monitor.nodes_status.items()):
        status_color = curses_module.color_pair(1)
        if status == NodeStatus.COMPLETED:
            status_color = curses_module.color_pair(2)
        elif status == NodeStatus.FAILED:
            status_color = curses_module.color_pair(3)
        elif status == NodeStatus.RUNNING:
            status_color = curses_module.color_pair(4)
            
        # Highlight current node
        if node == monitor.current_node:
            node_text = f"> {node}: {status} <"
        else:
            node_text = f"  {node}: {status}  "
            
        stdscr.addstr(node_line, 2, node_text, status_color)
        node_line += 1
    
    # Draw log messages
    log_line = node_line + 1
    stdscr.addstr(log_line, 0, "Event Log:", curses_module.color_pair(1) | curses_module.A_BOLD)
    log_line += 1
    
    # Calculate how many log messages we can display
    max_log_messages = height - log_line - 1
    if max_log_messages < 0:
        max_log_messages = 0
        
    # Display as many log messages as will fit
    log_messages = monitor.message_log[-max_log_messages:] if max_log_messages > 0 else []
    
    for i, message in enumerate(log_messages):
        if log_line + i >= height:
            break
            
        message_color = curses_module.color_pair(1)
        if "ERROR" in message:
            message_color = curses_module.color_pair(3)
        elif "WARNING" in message:
            message_color = curses_module.color_pair(4)
            
        # Truncate message if it's too wide
        if len(message) > width - 2:
            message = message[:width - 5] + "..."
            
        stdscr.addstr(log_line + i, 2, message, message_color)
    
    # Draw footer
    if height > 2:
        footer = "Press 'q' to quit, 'r' to refresh"
        stdscr.addstr(height - 1, (width - len(footer)) // 2, footer, curses_module.color_pair(5))
    
    stdscr.refresh()

def run_ui_wrapper_fn(stdscr, monitor: WorkflowMonitor, curses_module):
    """
    Run the UI for the workflow monitor.
    
    Args:
        stdscr: Curses screen
        monitor: WorkflowMonitor instance
        curses_module: The imported curses module
    """
    # Don't wait for input
    stdscr.nodelay(True)
    
    # Don't echo keystrokes
    curses_module.noecho()
    
    # Hide cursor
    curses_module.curs_set(0)
    
    # Set up watchdog observer
    observer = Observer()
    handler = OutputDirectoryEventHandler(monitor)
    observer.schedule(handler, monitor.output_dir, recursive=True)
    observer.start()
    
    try:
        # Initial scan
        monitor.scan_output_directory()
        
        # Main UI loop
        while True:
            # Draw UI
            draw_ui(stdscr, monitor, curses_module)
            
            # Check for keypress
            try:
                key = stdscr.getkey()
                if key == 'q':
                    break
                elif key == 'r':
                    monitor.scan_output_directory()
                    monitor.add_log_message("Manually refreshed")
            except curses_module.error:
                pass
            
            # Periodic scan - only scan every 3 seconds instead of every 0.5 seconds
            # to reduce unnecessary updates. Let the watchdog handler handle most updates.
            current_time = time.time()
            if not hasattr(monitor, 'last_scan_time') or current_time - monitor.last_scan_time >= 3:
                monitor.scan_output_directory()
                monitor.last_scan_time = current_time
            
            # Sleep for a bit - reduced from 0.5 to 0.2 for better UI responsiveness
            time.sleep(0.2)
    finally:
        observer.stop()
        observer.join()

def main():
    """Command-line interface for workflow monitoring."""
    parser = argparse.ArgumentParser(description="Monitor LangGraph workflow executions in real-time")
    parser.add_argument("--task", "-t", help="Task ID to monitor (e.g., BE-07)")
    parser.add_argument("--output", "-o", help="Directory where task outputs are stored")
    parser.add_argument("--simple", "-s", action="store_true", help="Use simple output instead of curses UI")
    
    args = parser.parse_args()
    
    monitor = WorkflowMonitor(args.task, args.output)
    
    # Default to simple mode on Windows if not explicitly set
    is_windows = os.name == 'nt'
    use_simple_mode = args.simple or is_windows

    if use_simple_mode:
        # Simple output mode
        print(f"Monitoring workflow for {args.task or 'all tasks'}")
        print(f"Output directory: {monitor.output_dir}")
        print("Press Ctrl+C to stop")
        
        try:
            # Set up watchdog observer
            observer = Observer()
            handler = OutputDirectoryEventHandler(monitor)
            observer.schedule(handler, monitor.output_dir, recursive=True)
            observer.start()
            
            while True:
                try:
                    # Only do periodic scans every 5 seconds rather than continuously
                    # Let the file system watcher handle most updates
                    time.sleep(5)
                    
                    # Clear screen before printing status
                    clear_screen()
                    
                    # Print status
                    print("\nTask Status:")
                    for task_id, status in monitor.task_status.items():
                        print(f"  {task_id}: {status}")
                    
                    print("\nNode Status:")
                    for node, status in sorted(monitor.nodes_status.items()):
                        print(f"  {node}: {status}")
                    
                    print("\nLast 5 Events:")
                    for message in monitor.message_log[-5:]:
                        print(f"  {message}")
                    
                    print("\nPress Ctrl+C to exit")
                except KeyboardInterrupt:
                    break
        except KeyboardInterrupt:
            print("\nStopping monitor")
        finally:
            observer.stop()
            observer.join()
    else:
        # Curses UI mode
        try:
            import curses # Moved import here
            curses.wrapper(lambda scr: run_ui_wrapper_fn(scr, monitor, curses))
        except ImportError:
            print("Curses module not available. Please run in simple mode (--simple) or install curses (e.g., windows-curses on Windows).")
            sys.exit(1)
        except Exception as e:
            print(f"Error running UI: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()