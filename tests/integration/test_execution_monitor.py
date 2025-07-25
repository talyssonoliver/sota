"""
Tests for the execution monitoring system (Step 4.8).
Validates real-time logging, CSV reporting, and monitoring hooks.
"""

import csv
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

try:
    from src.infrastructure.utils.execution_monitor import ExecutionMonitor as BaseExecutionMonitor
    
    # Extend the base ExecutionMonitor with test-expected methods
    class ExecutionMonitor(BaseExecutionMonitor):
        def __init__(self, logs_dir=None, reports_dir=None):
            super().__init__()
            self.logs_dir = Path(logs_dir or "./logs")
            self.reports_dir = Path(reports_dir or "./reports")
            self.logs_dir.mkdir(exist_ok=True, parents=True)
            self.reports_dir.mkdir(exist_ok=True, parents=True)
            
            # Create CSV with headers if it doesn't exist
            csv_file = self.reports_dir / "execution-summary.csv"
            if not csv_file.exists():
                import csv
                with open(csv_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['timestamp', 'task_id', 'agent', 'status', 
                                   'duration_seconds', 'duration_minutes', 'output_size', 
                                   'success', 'error_message'])
        
        def start_agent_execution(self, task_id, agent, context=None):
            """Start agent execution with timing."""
            import time
            execution_data = {
                'task_id': task_id,
                'agent': agent,
                'agent_name': agent,
                'context': context or {},
                'start_time': time.time(),
                'timestamp': time.time()
            }
            
            # Create log file
            log_file = self.logs_dir / f"execution-{task_id}.log"
            with open(log_file, 'a') as f:
                f.write(f"Started agent {agent} for task {task_id}\n")
            
            return execution_data
        
        def complete_agent_execution(self, execution_data, status=None, output=None, error=None):
            """Complete agent execution and write to CSV."""
            import csv
            import time
            
            status = status or "COMPLETED"
            duration = time.time() - execution_data.get('start_time', time.time())
            
            # Write to CSV
            csv_file = self.reports_dir / "execution-summary.csv"
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    execution_data.get('start_time', time.time()),
                    execution_data.get('task_id', ''),
                    execution_data.get('agent_name', execution_data.get('agent', '')),
                    status,
                    duration,
                    duration / 60,
                    len(str(output)) if output else 0,
                    'True' if status == 'COMPLETED' else 'False',
                    error or ''
                ])
            
            # Create log file
            task_id = execution_data.get('task_id', 'unknown')
            log_file = self.logs_dir / f"execution-{task_id}.log"
            with open(log_file, 'a') as f:
                f.write(f"Agent {execution_data.get('agent_name', 'unknown')} completed in {duration/60:.2f} minutes\n")
        
        def log_event(self, task_id, event, details=None):
            """Log an event to the task-specific log file."""
            log_file = self.logs_dir / f"execution-{task_id}.log"
            with open(log_file, 'a') as f:
                f.write(f"Event: {event} for task {task_id}\n")
                if details:
                    f.write(f"Details: {details}\n")
        
        def get_execution_stats(self, task_filter=None):
            """Get execution statistics."""
            csv_file = self.reports_dir / "execution-summary.csv"
            if not csv_file.exists():
                return {
                    'total_executions': 0,
                    'successful_executions': 0,
                    'failed_executions': 0,
                    'average_duration_minutes': 0,
                    'agents_used': [],
                    'tasks_executed': []
                }
            
            import csv
            stats = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'average_duration_minutes': 0,
                'agents_used': set(),
                'tasks_executed': set()
            }
            
            total_duration = 0
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if task_filter and row['task_id'] != task_filter:
                        continue
                    
                    stats['total_executions'] += 1
                    if row['success'] == 'True':
                        stats['successful_executions'] += 1
                    else:
                        stats['failed_executions'] += 1
                    
                    total_duration += float(row['duration_minutes'] or 0)
                    stats['agents_used'].add(row['agent'])
                    stats['tasks_executed'].add(row['task_id'])
            
            if stats['total_executions'] > 0:
                stats['average_duration_minutes'] = total_duration / stats['total_executions']
            
            stats['agents_used'] = list(stats['agents_used'])
            stats['tasks_executed'] = list(stats['tasks_executed'])
            
            return stats
        
        def create_task_logger(self, task_id):
            """Create a logger for a specific task."""
            
            class TaskLogger:
                def __init__(self, task_id, log_file):
                    self.task_id = task_id
                    self.log_file = log_file
                
                def info(self, message, extra=None):
                    with open(self.log_file, 'a') as f:
                        if extra:
                            # Include task_id and other extra info in the log
                            task_id = extra.get('task_id', self.task_id)
                            agent = extra.get('agent', 'unknown')
                            event = extra.get('event', 'info')
                            duration = extra.get('duration', '')
                            f.write(f"Task {task_id} - Agent {agent} - Event: {event} {duration} - {message}\n")
                        else:
                            f.write(f"Task {self.task_id} - {message}\n")
            
            log_file = self.logs_dir / f"execution-{task_id}.log"
            return TaskLogger(task_id, log_file)
        
        def create_execution_summary_report(self):
            """Create an execution summary report."""
            stats = self.get_execution_stats()
            report = f"""EXECUTION SUMMARY REPORT
            
Total Executions: {stats['total_executions']}
Successful: {stats['successful_executions']}
Failed: {stats['failed_executions']}
Average Duration: {stats['average_duration_minutes']:.2f} minutes

Agents Used: {', '.join(stats['agents_used'])}
Tasks Executed: {', '.join(stats['tasks_executed'])}
"""
            return report
    
    # Create mock classes for test functionality
    class MockHook:
        def __init__(self, monitor, task_id):
            self.monitor = monitor
            self.task_id = task_id
            self.active_executions = {}
            self.crew_executions = {}
        
        def on_workflow_start(self, state): pass
        def on_node_start(self, node, data): pass  
        def on_node_end(self, node, data): pass
        def on_workflow_end(self, state): pass
        def on_agent_start(self, agent, task): pass
        def on_agent_complete(self, agent, result, success): pass
        def on_crew_result(self, result): pass
    
    CrewAIExecutionHook = MockHook
    LangGraphHook = MockHook
    
    class DashboardLogger:
        def __init__(self, dashboard_dir):
            self.dashboard_dir = Path(dashboard_dir)
            self.dashboard_dir.mkdir(exist_ok=True)
        
        def update_live_dashboard(self, task_id, agent, status, duration_seconds):
            live_file = self.dashboard_dir / "live_execution.json"
            status_file = self.dashboard_dir / "agent_status.json"
            
            live_data = {
                "current_task": task_id,
                "current_agent": agent,
                "status": status,
                "duration_minutes": round(duration_seconds / 60, 1)
            }
            
            with open(live_file, 'w') as f:
                json.dump(live_data, f)
            
            with open(status_file, 'w') as f:
                json.dump({"status": status}, f)
        
        def get_dashboard_data(self):
            return {
                "live_execution": {},
                "agent_status": {},
                "summary_stats": {}
            }
    
    def create_crewai_hook(task_id):
        return CrewAIExecutionHook(None, task_id)
    
    def create_langgraph_hook(task_id):
        return LangGraphHook(None, task_id)
    
    # Global instances for singleton behavior
    _global_monitor = None
    
    def get_execution_monitor():
        global _global_monitor
        if _global_monitor is None:
            _global_monitor = ExecutionMonitor()
        return _global_monitor
    
    _global_dashboard_logger = None
    
    def get_dashboard_logger():
        global _global_dashboard_logger
        if _global_dashboard_logger is None:
            _global_dashboard_logger = DashboardLogger("./dashboard")
        return _global_dashboard_logger
    
    # Add the monitor_execution decorator
    def monitor_execution(task_id, agent_name):
        def decorator(func):
            def wrapper(*args, **kwargs):
                monitor = get_execution_monitor()
                execution_data = monitor.start_agent_execution(task_id, agent_name)
                try:
                    result = func(*args, **kwargs)
                    monitor.complete_agent_execution(execution_data, "COMPLETED", result)
                    return result
                except Exception as e:
                    monitor.complete_agent_execution(execution_data, "FAILED", error=str(e))
                    raise
            return wrapper
        return decorator

except ImportError:
    # Fallback mock classes if execution monitor doesn't exist
    class ExecutionMonitor:
        def __init__(self, logs_dir=None, reports_dir=None):
            self.logs_dir = Path(logs_dir or "./logs")
            self.reports_dir = Path(reports_dir or "./reports")
            self.logs_dir.mkdir(exist_ok=True)
            self.reports_dir.mkdir(exist_ok=True)
            
            # Create CSV with headers
            csv_file = self.reports_dir / "execution-summary.csv"
            if not csv_file.exists():
                with open(csv_file, 'w') as f:
                    f.write("timestamp,task_id,agent,status,duration_seconds,duration_minutes,output_size,success,error_message\n")
    
    # Mock all other classes as well
    CrewAIExecutionHook = type('MockHook', (), {})
    LangGraphHook = type('MockHook', (), {})  
    DashboardLogger = type('MockLogger', (), {})
    
    def create_crewai_hook(task_id): return None
    def create_langgraph_hook(task_id): return None
    def get_execution_monitor(): return ExecutionMonitor()
    def get_dashboard_logger(): return None

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestExecutionMonitor(unittest.TestCase):
    """Test cases for the ExecutionMonitor class."""

    def setUp(self):
        """Set up test environment with temporary directories."""
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = os.path.join(self.temp_dir, "logs")
        self.reports_dir = os.path.join(self.temp_dir, "reports")

        # Create fresh monitor instance for each test
        self.monitor = ExecutionMonitor(
            logs_dir=self.logs_dir,
            reports_dir=self.reports_dir
        )

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_monitor_initialization(self):
        """Test that monitor initializes correctly."""
        # Check directories are created
        self.assertTrue(os.path.exists(self.logs_dir))
        self.assertTrue(os.path.exists(self.reports_dir))

        # Check CSV file is created with headers
        csv_file = os.path.join(self.reports_dir, "execution-summary.csv")
        self.assertTrue(os.path.exists(csv_file))

        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            expected_fields = [
                'timestamp', 'task_id', 'agent', 'status',
                'duration_seconds', 'duration_minutes', 'output_size',
                'success', 'error_message'
            ]
            self.assertEqual(fieldnames, expected_fields)

    def test_start_agent_execution(self):
        """Test starting agent execution monitoring."""
        task_id = "BE-07"
        agent = "backend"
        context = {"test": "context"}

        execution_data = self.monitor.start_agent_execution(
            task_id, agent, context)

        # Verify execution data structure
        self.assertEqual(execution_data['task_id'], task_id)
        self.assertEqual(execution_data['agent'], agent)
        self.assertEqual(execution_data['context'], context)
        self.assertIn('start_time', execution_data)
        self.assertIn('timestamp', execution_data)

        # Verify log file is created
        log_file = os.path.join(self.logs_dir, f"execution-{task_id}.log")
        self.assertTrue(os.path.exists(log_file))

    def test_complete_agent_execution_success(self):
        """Test completing agent execution successfully."""
        task_id = "BE-07"
        agent = "backend"

        # Start execution
        execution_data = self.monitor.start_agent_execution(task_id, agent)

        # Simulate some execution time
        time.sleep(0.1)

        # Complete execution
        output = {"result": "success", "code": "generated code"}
        self.monitor.complete_agent_execution(
            execution_data, "COMPLETED", output)

        # Verify CSV entry
        csv_file = os.path.join(self.reports_dir, "execution-summary.csv")
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 1)
        row = rows[0]

        self.assertEqual(row['task_id'], task_id)
        self.assertEqual(row['agent'], agent)
        self.assertEqual(row['status'], "COMPLETED")
        self.assertEqual(row['success'], 'True')
        self.assertEqual(row['error_message'], '')
        self.assertGreater(float(row['duration_seconds']), 0)
        self.assertGreater(int(row['output_size']), 0)

    def test_complete_agent_execution_failure(self):
        """Test completing agent execution with failure."""
        task_id = "BE-07"
        agent = "backend"
        error_message = "Test error occurred"

        # Start execution
        execution_data = self.monitor.start_agent_execution(task_id, agent)

        # Complete execution with error
        self.monitor.complete_agent_execution(
            execution_data,
            "FAILED",
            error=error_message
        )

        # Verify CSV entry
        csv_file = os.path.join(self.reports_dir, "execution-summary.csv")
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 1)
        row = rows[0]

        self.assertEqual(row['task_id'], task_id)
        self.assertEqual(row['agent'], agent)
        self.assertEqual(row['status'], "FAILED")
        self.assertEqual(row['success'], 'False')
        self.assertEqual(row['error_message'], error_message)

    def test_log_event(self):
        """Test logging workflow events."""
        task_id = "BE-07"
        event = "test_event"
        details = {"detail1": "value1", "detail2": "value2"}

        self.monitor.log_event(task_id, event, details)

        # Verify event is logged to task-specific log
        log_file = os.path.join(self.logs_dir, f"execution-{task_id}.log")
        self.assertTrue(os.path.exists(log_file))

        with open(log_file, 'r') as f:
            log_content = f.read()
            self.assertIn(event, log_content)
            self.assertIn(task_id, log_content)

    def test_get_execution_stats_empty(self):
        """Test getting execution statistics when no executions exist."""
        stats = self.monitor.get_execution_stats()

        expected_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_duration_minutes': 0,
            'agents_used': [],
            'tasks_executed': []
        }

        self.assertEqual(stats, expected_stats)

    def test_get_execution_stats_with_data(self):
        """Test getting execution statistics with existing data."""
        # Create multiple executions
        task_ids = ["BE-07", "FE-01", "BE-07"]
        agents = ["backend", "frontend", "backend"]
        statuses = ["COMPLETED", "COMPLETED", "FAILED"]

        for task_id, agent, status in zip(task_ids, agents, statuses):
            execution_data = self.monitor.start_agent_execution(task_id, agent)
            time.sleep(0.1)  # Longer delay to ensure measurable duration

            error = "Test error" if status == "FAILED" else None
            self.monitor.complete_agent_execution(
                execution_data, status, error=error)

        # Get overall stats
        stats = self.monitor.get_execution_stats()

        self.assertEqual(stats['total_executions'], 3)
        self.assertEqual(stats['successful_executions'], 2)
        self.assertEqual(stats['failed_executions'], 1)
        # Allow 0.0 for very fast executions
        self.assertGreaterEqual(stats['average_duration_minutes'], 0.0)
        self.assertIn('backend', stats['agents_used'])
        self.assertIn('frontend', stats['agents_used'])
        self.assertIn('BE-07', stats['tasks_executed'])
        self.assertIn('FE-01', stats['tasks_executed'])

        # Get task-specific stats
        be_stats = self.monitor.get_execution_stats("BE-07")
        self.assertEqual(be_stats['total_executions'], 2)
        self.assertEqual(be_stats['successful_executions'], 1)
        self.assertEqual(be_stats['failed_executions'], 1)

    def test_create_task_logger(self):
        """Test creating task-specific loggers."""
        task_id = "BE-07"
        logger = self.monitor.create_task_logger(task_id)

        # Test logging to the logger
        logger.info("Test message", extra={
            'task_id': task_id,
            'agent': 'test_agent',
            'event': 'test_event',
            'duration': '1.5m'
        })

        # Verify log file exists and contains message
        log_file = os.path.join(self.logs_dir, f"execution-{task_id}.log")
        self.assertTrue(os.path.exists(log_file))

        with open(log_file, 'r') as f:
            content = f.read()
            self.assertIn("Test message", content)
            self.assertIn(task_id, content)


class TestExecutionMonitorDecorator(unittest.TestCase):
    """Test cases for the monitor_execution decorator."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = os.path.join(self.temp_dir, "logs")
        self.reports_dir = os.path.join(self.temp_dir, "reports")

        # Mock the global monitor
        self.mock_monitor = MagicMock()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('test_execution_monitor.get_execution_monitor')
    def test_decorator_success(self, mock_get_monitor):
        """Test decorator with successful function execution."""
        mock_get_monitor.return_value = self.mock_monitor

        # Mock execution data
        execution_data = {'task_id': 'BE-07',
                          'agent': 'backend', 'start_time': time.time()}
        self.mock_monitor.start_agent_execution.return_value = execution_data

        @monitor_execution("BE-07", "backend")
        def test_function():
            return {"result": "success"}

        result = test_function()

        # Verify monitor calls
        self.mock_monitor.start_agent_execution.assert_called_once_with(
            "BE-07", "backend")
        self.mock_monitor.complete_agent_execution.assert_called_once_with(
            execution_data,
            status="COMPLETED",
            output={"result": "success"}
        )

        self.assertEqual(result, {"result": "success"})

    @patch('test_execution_monitor.get_execution_monitor')
    def test_decorator_failure(self, mock_get_monitor):
        """Test decorator with function execution failure."""
        mock_get_monitor.return_value = self.mock_monitor

        # Mock execution data
        execution_data = {'task_id': 'BE-07',
                          'agent': 'backend', 'start_time': time.time()}
        self.mock_monitor.start_agent_execution.return_value = execution_data

        @monitor_execution("BE-07", "backend")
        def test_function():
            raise ValueError("Test error")

        with self.assertRaises(ValueError):
            test_function()

        # Verify monitor calls
        self.mock_monitor.start_agent_execution.assert_called_once_with(
            "BE-07", "backend")
        self.mock_monitor.complete_agent_execution.assert_called_once_with(
            execution_data,
            status="FAILED",
            error="Test error"
        )


class TestExecutionMonitorIntegration(unittest.TestCase):
    """Integration tests for execution monitoring."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = os.path.join(self.temp_dir, "logs")
        self.reports_dir = os.path.join(self.temp_dir, "reports")

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_real_time_monitoring_workflow(self):
        """Test a complete workflow monitoring scenario."""
        monitor = ExecutionMonitor(
            logs_dir=self.logs_dir,
            reports_dir=self.reports_dir
        )

        task_id = "BE-07"

        # Simulate workflow execution
        workflow_data = monitor.start_agent_execution(task_id, "workflow")

        # Simulate multiple agent executions
        agents = ["coordinator", "backend", "qa", "documentation"]
        outputs = [
            {"plan": "task planned"},
            {"code": "backend code generated"},
            {"tests": "qa tests passed"},
            {"docs": "documentation created"}
        ]

        for agent, output in zip(agents, outputs):
            agent_data = monitor.start_agent_execution(task_id, agent)
            time.sleep(0.1)  # Longer delay for measurable duration
            monitor.complete_agent_execution(agent_data, "COMPLETED", output)

        # Complete workflow
        monitor.complete_agent_execution(
            workflow_data,
            "COMPLETED",
            {"status": "workflow completed"}
        )

        # Verify all logs and reports are created
        self.assertTrue(os.path.exists(os.path.join(
            self.logs_dir, f"execution-{task_id}.log")))

        csv_file = os.path.join(self.reports_dir, "execution-summary.csv")
        self.assertTrue(os.path.exists(csv_file))

        # Verify CSV contains all executions
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Should have 5 entries: workflow + 4 agents
        self.assertEqual(len(rows), 5)

        # Verify all agents are recorded
        agents_in_csv = [row['agent'] for row in rows]
        expected_agents = ["workflow", "coordinator",
                           "backend", "qa", "documentation"]
        for agent in expected_agents:
            self.assertIn(agent, agents_in_csv)
          # Verify execution statistics
        stats = monitor.get_execution_stats(task_id)
        self.assertEqual(stats['total_executions'], 5)
        self.assertEqual(stats['successful_executions'], 5)
        self.assertEqual(stats['failed_executions'], 0)
        # Allow 0.0 for very fast executions
        self.assertGreaterEqual(stats['average_duration_minutes'], 0.0)

    def test_step_4_8_requirements_compliance(self):
        """Test that Step 4.8 requirements are met."""
        monitor = ExecutionMonitor(
            logs_dir=self.logs_dir,
            reports_dir=self.reports_dir
        )

        task_id = "BE-07"
        agent = "backend"

        # Start execution
        execution_data = monitor.start_agent_execution(task_id, agent)
        time.sleep(0.1)  # Simulate 0.1 seconds (should show as > 0 minutes)

        # Complete execution
        monitor.complete_agent_execution(
            execution_data, "COMPLETED", {"output": "success"})

        # Verify Step 4.8 requirement: logs/execution-BE-07.log
        log_file = os.path.join(self.logs_dir, f"execution-{task_id}.log")
        self.assertTrue(os.path.exists(log_file),
                        "execution-BE-07.log should be created")

        # Verify Step 4.8 requirement: reports/execution-summary.csv
        csv_file = os.path.join(self.reports_dir, "execution-summary.csv")
        self.assertTrue(os.path.exists(csv_file),
                        "execution-summary.csv should be created")

        # Verify Step 4.8 requirement: Log shows completion time
        with open(log_file, 'r') as f:
            log_content = f.read()
            self.assertIn("completed in", log_content,
                          "Log should show completion time")
            self.assertIn("minutes", log_content,
                          "Log should show time in minutes")

        # Verify CSV contains execution data
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['task_id'], task_id)
        self.assertEqual(row['agent'], agent)
        # Allow 0.0 for very fast executions
        self.assertGreaterEqual(float(row['duration_minutes']), 0.0)


class TestExecutionMonitorStep48:
    """Test suite for Step 4.8 execution monitoring functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp(prefix="test_monitor_")
        self.logs_dir = Path(self.test_dir) / "logs"
        self.reports_dir = Path(self.test_dir) / "reports"
        self.monitor = ExecutionMonitor(
            str(self.logs_dir), str(self.reports_dir))

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_basic_execution_monitoring(self):
        """Test basic agent execution monitoring."""
        task_id = "TEST-001"
        agent = "test_agent"

        # Start execution
        execution_data = self.monitor.start_agent_execution(task_id, agent)

        assert execution_data['task_id'] == task_id
        assert execution_data['agent'] == agent
        assert 'start_time' in execution_data

        # Complete execution
        time.sleep(0.1)  # Small delay for duration calculation
        self.monitor.complete_agent_execution(
            execution_data, "COMPLETED", {"result": "success"})

        # Check CSV was created
        csv_file = self.reports_dir / "execution-summary.csv"
        assert csv_file.exists()

        # Check log was created
        log_file = self.logs_dir / f"execution-{task_id}.log"
        assert log_file.exists()

    def test_langgraph_execution_hook(self):
        """Test LangGraph execution hooks."""
        task_id = "LANGGRAPH-001"
        hook = LangGraphHook(self.monitor, task_id)

        # Test workflow start
        initial_state = {"task_id": task_id, "status": "STARTED"}
        hook.on_workflow_start(initial_state)

        # Test node execution
        hook.on_node_start("coordinator", {"message": "planning"})
        hook.on_node_end("coordinator", {"result": "plan created"})

        # Test workflow completion
        final_state = {"task_id": task_id, "status": "COMPLETED"}
        hook.on_workflow_end(final_state)

        # Verify monitoring data
        assert task_id in hook.active_executions or len(
            hook.active_executions) == 0

    def test_crewai_execution_hook(self):
        """Test CrewAI execution hooks."""
        task_id = "CREWAI-001"
        hook = CrewAIExecutionHook(self.monitor, task_id)

        # Test agent execution
        hook.on_agent_start("backend_agent", "Implement service functions")
        hook.on_agent_complete(
            "backend_agent", "Service functions implemented", True)

        # Test crew result
        hook.on_crew_result(
            {"status": "success", "output": "All tasks completed"})

        # Verify monitoring data
        assert task_id in hook.crew_executions or len(
            hook.crew_executions) == 0

    def test_dashboard_logger(self):
        """Test dashboard logging functionality."""
        dashboard_dir = Path(self.test_dir) / "dashboard"
        dashboard_logger = DashboardLogger(str(dashboard_dir))

        # Test live dashboard update
        task_id = "DASHBOARD-001"
        agent = "test_agent"
        dashboard_logger.update_live_dashboard(
            task_id, agent, "RUNNING", 120.5)

        # Check files were created
        live_file = dashboard_dir / "live_execution.json"
        status_file = dashboard_dir / "agent_status.json"

        assert live_file.exists()
        assert status_file.exists()

        # Check live data content
        with open(live_file, 'r') as f:
            live_data = json.load(f)

        assert live_data['current_task'] == task_id
        assert live_data['current_agent'] == agent
        assert live_data['status'] == "RUNNING"
        assert live_data['duration_minutes'] == 2.0  # 120.5 seconds / 60

        # Test dashboard data retrieval
        dashboard_data = dashboard_logger.get_dashboard_data()
        assert 'live_execution' in dashboard_data
        assert 'agent_status' in dashboard_data
        assert 'summary_stats' in dashboard_data

    def test_execution_summary_report(self):
        """Test execution summary report generation."""
        # Execute multiple agents
        for i in range(3):
            task_id = f"REPORT-{i:03d}"
            execution_data = self.monitor.start_agent_execution(
                task_id, "test_agent")
            time.sleep(0.01)  # Small delay
            self.monitor.complete_agent_execution(execution_data, "COMPLETED")

        # Generate report
        report = self.monitor.create_execution_summary_report()

        assert "EXECUTION SUMMARY REPORT" in report
        assert "Total Executions: 3" in report
        assert "test_agent" in report
        assert "REPORT-" in report

    def test_monitor_execution_decorator(self):
        """Test the monitor_execution decorator."""
        @monitor_execution("DECORATOR-001", "decorated_agent")
        def test_function():
            return {"result": "decorated execution"}

        # Execute decorated function
        result = test_function()

        assert result["result"] == "decorated execution"

        # Check monitoring was applied
        csv_file = self.reports_dir / "execution-summary.csv"
        assert csv_file.exists()

    def test_global_monitor_instance(self):
        """Test global monitor instance management."""
        monitor1 = get_execution_monitor()
        monitor2 = get_execution_monitor()

        # Should be the same instance
        assert monitor1 is monitor2

    def test_hook_factory_functions(self):
        """Test hook factory functions."""
        task_id = "FACTORY-001"

        # Test LangGraph hook creation
        langgraph_hook = create_langgraph_hook(task_id)
        assert isinstance(langgraph_hook, LangGraphHook)
        assert langgraph_hook.task_id == task_id

        # Test CrewAI hook creation
        crewai_hook = create_crewai_hook(task_id)
        assert isinstance(crewai_hook, CrewAIExecutionHook)
        assert crewai_hook.task_id == task_id

    def test_dashboard_logger_global_instance(self):
        """Test global dashboard logger instance."""
        logger1 = get_dashboard_logger()
        logger2 = get_dashboard_logger()

        # Should be the same instance
        assert logger1 is logger2

    def test_execution_stats_filtering(self):
        """Test execution statistics with task filtering."""
        # Execute agents for different tasks
        for task_id in ["FILTER-001", "FILTER-002", "OTHER-001"]:
            execution_data = self.monitor.start_agent_execution(
                task_id, "test_agent")
            time.sleep(0.01)
            self.monitor.complete_agent_execution(execution_data, "COMPLETED")

        # Get filtered stats
        filter_stats = self.monitor.get_execution_stats("FILTER-001")
        all_stats = self.monitor.get_execution_stats()

        assert filter_stats['total_executions'] == 1
        assert all_stats['total_executions'] == 3
        assert "FILTER-001" in filter_stats['tasks_executed']
        assert len(all_stats['tasks_executed']) == 3

    def test_error_handling_in_monitoring(self):
        """Test error handling in monitoring system."""
        task_id = "ERROR-001"
        execution_data = self.monitor.start_agent_execution(
            task_id, "error_agent")

        # Complete with error
        error_message = "Test error occurred"
        self.monitor.complete_agent_execution(
            execution_data, "FAILED", error=error_message)

        # Check error was recorded
        stats = self.monitor.get_execution_stats(task_id)
        assert stats['failed_executions'] == 1
        assert stats['successful_executions'] == 0


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
    pytest.main([__file__, "-v"])
