"""
Test Enhanced Workflow Features
This script tests all PHASE 2 enhancements working together.
"""
import os
import sys
import time
import shutil
import threading
import subprocess
import unittest
import json
from pathlib import Path
from unittest.mock import patch
import time
# Ensure the project root is in the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
# Try to import required modules
try:
    from config.build_paths import TEST_OUTPUTS_DIR
except ImportError:
    TEST_OUTPUTS_DIR = Path('test_outputs')
try:
    from tests.utils.test_utils import Timer
except ImportError:
    # Fallback Timer implementation
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
            return self
        
        def stop(self):
            self.end_time = time.time()
            return self
        
        def elapsed(self):
            if self.start_time is None:
                return 0
            if self.end_time is None:
                return time.time() - self.start_time
            return self.end_time - self.start_time

try:
    from tests.utils.test_utils import FeedbackCollector
except ImportError:
    # Fallback FeedbackCollector implementation
    class FeedbackCollector:
        @staticmethod
        def print_section(title):
            print(f"\n=== {title} ===")

# Try to import required classes
from src.infrastructure.tools.notifications import NotificationLevel
from src.core.workflows.enhanced_workflow import EnhancedWorkflowExecutor

try:
    from src.core.workflows.states import TaskStatus
except ImportError:
    pass
try:
    from tests.run_tests import Timer, FeedbackCollector
except ImportError:
    pass

class TestEnhancedWorkflow(unittest.TestCase):
    """Test cases for enhanced workflow features."""

    def setUp(self):
        """Set up test environment."""
        from config.build_paths import TEST_OUTPUTS_DIR
        self.test_output_dir = TEST_OUTPUTS_DIR
        os.makedirs(self.test_output_dir, exist_ok=True)
        self.timer = Timer().start()
        self.test_results = {'tests_run': 0, 'tests_passed': 0, 'tests_failed': 0, 'execution_times': {}}

    def tearDown(self):
        """Clean up after tests."""
        self.timer.stop()
        print(f'Test execution time: {self.timer.elapsed():.2f}s')
        if self.test_output_dir.exists():
            for child in self.test_output_dir.iterdir():
                if child.is_dir():
                    for subchild in child.iterdir():
                        subchild.unlink()
                    child.rmdir()
                else:
                    child.unlink()

    def verify_status_file(self, task_id):
        """Verify status file exists and contains valid JSON."""
        status_path = self.test_output_dir / task_id / 'status.json'
        self.assertTrue(status_path.exists(), f'Status file for {task_id} does not exist')
        try:
            with open(status_path, 'r') as f:
                status_data = json.load(f)
            self.assertIn('task_id', status_data, 'Status file missing task_id field')
            self.assertEqual(status_data['task_id'], task_id, "Task ID in status file doesn't match expected value")
            self.assertIn('timestamp', status_data, 'Status file missing timestamp field')
            return status_data
        except json.JSONDecodeError:
            self.fail(f'Status file for {task_id} contains invalid JSON')
            return None

    def test_basic_workflow(self):
        """Test the basic workflow execution."""
        test_timer = Timer().start()
        FeedbackCollector.print_section('Basic Workflow Test')
        executor = EnhancedWorkflowExecutor(workflow_type='basic', notification_level=NotificationLevel.NONE, output_dir=str(self.test_output_dir))
        task_id = 'TL-01'
        result = executor.execute_task(task_id)
        self.assertEqual(result['task_id'], task_id)
        self.assertTrue((self.test_output_dir / task_id / 'status.json').exists())
        status_data = self.verify_status_file(task_id)
        test_timer.stop()
        self.test_results['tests_run'] += 1
        self.test_results['tests_passed'] += 1
        self.test_results['execution_times']['test_basic_workflow'] = test_timer.elapsed()
        print(f'✅ Basic workflow test passed in {test_timer.elapsed():.2f}s')

    def test_auto_generated_workflow(self):
        """Test the auto-generated workflow."""
        test_timer = Timer().start()
        FeedbackCollector.print_section('Auto-Generated Workflow Test')
        executor = EnhancedWorkflowExecutor(workflow_type='auto', notification_level=NotificationLevel.NONE, output_dir=str(self.test_output_dir))
        task_id = 'BE-07'
        result = executor.execute_task(task_id)
        self.assertEqual(result['task_id'], task_id)
        self.assertTrue((self.test_output_dir / task_id / 'status.json').exists())
        status_data = self.verify_status_file(task_id)
        test_timer.stop()
        self.test_results['tests_run'] += 1
        self.test_results['tests_passed'] += 1
        self.test_results['execution_times']['test_auto_generated_workflow'] = test_timer.elapsed()
        print(f'✅ Auto-generated workflow test passed in {test_timer.elapsed():.2f}s')

    def test_resilient_workflow(self):
        """Test the resilient workflow with retry logic."""
        test_timer = Timer().start()
        FeedbackCollector.print_section('Resilient Workflow Test')
        resilience_config = {'max_retries': 2, 'retry_delay': 1, 'timeout_seconds': 10}
        executor = EnhancedWorkflowExecutor(workflow_type='dynamic', resilience_config=resilience_config, notification_level=NotificationLevel.NONE, output_dir=str(self.test_output_dir))
        task_id = 'QA-01'
        result = executor.execute_task(task_id)
        self.assertEqual(result['task_id'], task_id)
        status_data = self.verify_status_file(task_id)
        test_timer.stop()
        self.test_results['tests_run'] += 1
        self.test_results['tests_passed'] += 1
        self.test_results['execution_times']['test_resilient_workflow'] = test_timer.elapsed()
        print(f'✅ Resilient workflow test passed in {test_timer.elapsed():.2f}s')

    def test_notification_integration(self):
        """Test notification system integration."""
        test_timer = Timer().start()
        FeedbackCollector.print_section('Notification Integration Test')
        with patch('time.sleep'), patch('requests.post') as mock_post, patch('graph.notifications.SlackNotifier.send_notification') as mock_notify:
            mock_post.return_value.status_code = 200
            mock_notify.return_value = {'success': True}
            executor = EnhancedWorkflowExecutor(workflow_type='dynamic', notification_level=NotificationLevel.ERROR, output_dir=str(self.test_output_dir))
            task_id = 'FE-01'
            result = executor.execute_task(task_id)
            self.assertEqual(result['task_id'], task_id)
            status_data = self.verify_status_file(task_id)
        test_timer.stop()
        self.test_results['tests_run'] += 1
        self.test_results['tests_passed'] += 1
        self.test_results['execution_times']['test_notification_integration'] = test_timer.elapsed()
        print(f'✅ Notification integration test passed in {test_timer.elapsed():.2f}s')

    def test_all_components_together(self):
        """Test all components working together."""
        test_timer = Timer().start()
        FeedbackCollector.print_section('All Components Test')
        executor = EnhancedWorkflowExecutor(workflow_type='auto', resilience_config={'max_retries': 2, 'retry_delay': 1, 'timeout_seconds': 15}, notification_level=NotificationLevel.ALL, output_dir=str(self.test_output_dir))
        monitor_process = None
        monitor_thread = None

        def run_monitor():
            nonlocal monitor_process
            try:
                monitor_process = subprocess.Popen(['python', 'scripts/monitor_workflow.py', '--task', 'BE-07', '--output', str(self.test_output_dir), '--simple'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                monitor_process.wait()
            except Exception:
                pass
        monitor_thread = threading.Thread(target=run_monitor)
        monitor_thread.daemon = False
        monitor_thread.start()
        time.sleep(1)
        try:
            task_id = 'BE-07'
            result = executor.execute_task(task_id)
            self.assertEqual(result['task_id'], task_id)
            self.assertTrue((self.test_output_dir / task_id / 'status.json').exists())
            status_data = self.verify_status_file(task_id)
        finally:
            if monitor_process and monitor_process.poll() is None:
                try:
                    monitor_process.terminate()
                    monitor_process.wait(timeout=2)
                except (subprocess.TimeoutExpired, ProcessLookupError):
                    try:
                        monitor_process.kill()
                    except ProcessLookupError:
                        pass
            if monitor_thread and monitor_thread.is_alive():
                try:
                    monitor_thread.join(timeout=3)
                except Exception:
                    pass
        time.sleep(2)
        test_timer.stop()
        self.test_results['tests_run'] += 1
        self.test_results['tests_passed'] += 1
        self.test_results['execution_times']['test_all_components_together'] = test_timer.elapsed()
        print(f'✅ All components test passed in {test_timer.elapsed():.2f}s')

class FeedbackTestRunner:
    """Custom test runner that provides standardized feedback."""

    @staticmethod
    def run():
        """Run all tests with standardized feedback."""
        test_start = time.time()
        FeedbackCollector.print_header('Enhanced Workflow Tests')
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestEnhancedWorkflow))
        result = unittest.TextTestResult(sys.stdout, True, 1)
        print('\nRunning tests...')
        suite.run(result)
        tests_run = result.testsRun
        tests_failed = len(result.failures) + len(result.errors)
        tests_passed = tests_run - tests_failed
        details = {'Tests run': tests_run, 'Tests passed': tests_passed, 'Tests failed': tests_failed, 'Failures': [f'{test[0]._testMethodName}: {test[1]}' for test in result.failures], 'Errors': [f'{test[0]._testMethodName}: {test[1]}' for test in result.errors], 'Test categories': ['Basic workflow', 'Auto-generated workflow', 'Resilient workflow', 'Notification integration', 'Combined components']}
        execution_time = time.time() - test_start
        passed = tests_failed == 0
        return FeedbackCollector.print_result(test_name='Enhanced Workflow Tests', passed=passed, details=details, execution_time=execution_time)

def teardown_module(module):
    """Cleanup test_outputs directory after tests finish."""
    test_output_dir = str(TEST_OUTPUTS_DIR)
    if os.path.exists(test_output_dir):
        for child in os.listdir(test_output_dir):
            child_path = os.path.join(test_output_dir, child)
            if os.path.isdir(child_path):
                shutil.rmtree(child_path)
            else:
                os.remove(child_path)