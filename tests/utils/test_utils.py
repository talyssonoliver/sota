"""
Test Utilities

Common utilities and helpers for test setup, execution, and cleanup.
"""
import io
import json
import logging
import os
import shutil
import sys
import tempfile
import time
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Callable, Union
from unittest.mock import Mock, patch

class TestContextManager:
    """Test context manager for setting up and cleaning up test environments."""
    __test__ = False

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.temp_dirs = []
        self.temp_files = []
        self.patches = []
        self.original_env = {}

    def __enter__(self):
        """Enter test context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit test context and cleanup."""
        self.cleanup()

    def create_temp_dir(self, suffix: str='') -> Path:
        """Create a temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp(suffix=f'_{self.test_name}_{suffix}'))
        self.temp_dirs.append(temp_dir)
        return temp_dir

    def create_temp_file(self, content: str='', suffix: str='.txt') -> Path:
        """Create a temporary file for testing."""
        fd, temp_path = tempfile.mkstemp(suffix=f'_{self.test_name}_{suffix}')
        temp_file = Path(temp_path)
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        self.temp_files.append(temp_file)
        return temp_file

    def set_env_var(self, key: str, value: str):
        """Set environment variable and track for cleanup."""
        if key not in self.original_env:
            self.original_env[key] = os.environ.get(key)
        os.environ[key] = value

    def add_patch(self, target: str, **kwargs):
        """Add a mock patch and track for cleanup."""
        patcher = patch(target, **kwargs)
        mock_obj = patcher.start()
        self.patches.append(patcher)
        return mock_obj

    def cleanup(self):
        """Clean up all test resources."""
        for patcher in self.patches:
            try:
                patcher.stop()
            except Exception:
                pass
        for key, original_value in self.original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception:
                pass
        for temp_dir in self.temp_dirs:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except Exception:
                pass

class TemporaryEnvironment:
    """Context manager for temporarily modifying environment variables."""

    def __init__(self, **env_vars):
        self.env_vars = env_vars
        self.original_values = {}

    def __enter__(self):
        """Set temporary environment variables."""
        for key, value in self.env_vars.items():
            self.original_values[key] = os.environ.get(key)
            os.environ[key] = str(value)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original environment variables."""
        for key, original_value in self.original_values.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value

def create_test_context(test_name: str) -> TestContextManager:
    """Create a test context for the given test."""
    return TestContextManager(test_name)

def setup_test_environment(test_name: str='test') -> Dict[str, Any]:
    """Set up a standard test environment."""
    temp_dir = Path(tempfile.mkdtemp(suffix=f'_{test_name}'))
    test_env = {'TESTING': '1', 'TEST_MODE': 'true', 'TEST_TEMP_DIR': str(temp_dir), 'ANONYMIZED_TELEMETRY': 'False', 'LOG_LEVEL': 'DEBUG'}
    test_dirs = {'temp_dir': temp_dir, 'output_dir': temp_dir / 'outputs', 'logs_dir': temp_dir / 'logs', 'data_dir': temp_dir / 'data'}
    for dir_path in test_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    return {'env': test_env, 'dirs': test_dirs, 'cleanup_func': lambda: cleanup_test_environment(temp_dir)}

def cleanup_test_environment(temp_dir: Path):
    """Clean up test environment."""
    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    except Exception as e:
        print(f'Warning: Could not clean up test directory {temp_dir}: {e}')

def create_temporary_file(content: str='', suffix: str='.txt') -> Path:
    """Create a temporary file with the given content."""
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    temp_file = Path(temp_path)
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return temp_file

def create_temporary_directory(suffix: str='') -> Path:
    """Create a temporary directory."""
    return Path(tempfile.mkdtemp(suffix=suffix))

def wait_for_condition(condition_func: Callable[[], bool], timeout: float=5.0, interval: float=0.1, error_message: str='Condition not met within timeout') -> bool:
    """Wait for a condition to be true within a timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    raise TimeoutError(error_message)

def assert_eventually(condition_func: Callable[[], bool], timeout: float=5.0, interval: float=0.1, message: str=None):
    """Assert that a condition becomes true within a timeout."""
    error_message = message or 'Condition not met within timeout'
    wait_for_condition(condition_func, timeout, interval, error_message)

@contextmanager
def mock_environment_variables(**env_vars):
    """Context manager to temporarily set environment variables."""
    with TemporaryEnvironment(**env_vars):
        yield

@contextmanager
def capture_logs(logger_name: str=None, level: int=logging.DEBUG):
    """Context manager to capture log messages for testing."""
    log_buffer = io.StringIO()
    handler = logging.StreamHandler(log_buffer)
    handler.setLevel(level)
    logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()
    original_level = logger.level
    logger.setLevel(level)
    logger.addHandler(handler)
    try:
        yield log_buffer
    finally:
        logger.removeHandler(handler)
        logger.setLevel(original_level)

def create_mock_file_system(file_structure: Dict[str, Union[str, Dict]]) -> Path:
    """
    Create a mock file system structure for testing.
    
    Args:
        file_structure: Dict representing files and directories
                       String values are file contents
                       Dict values are subdirectories
    
    Returns:
        Path to the root of the created structure
    """
    root_dir = create_temporary_directory()

    def create_structure(current_dir: Path, structure: Dict):
        for name, content in structure.items():
            path = current_dir / name
            if isinstance(content, dict):
                path.mkdir(exist_ok=True)
                create_structure(path, content)
            else:
                path.write_text(str(content))
    create_structure(root_dir, file_structure)
    return root_dir

def load_test_data(filename: str) -> Any:
    """Load test data from a JSON file in the test data directory."""
    test_data_dir = Path(__file__).parent.parent / 'test_data'
    file_path = test_data_dir / filename
    if not file_path.exists():
        raise FileNotFoundError(f'Test data file not found: {file_path}')
    with open(file_path, 'r') as f:
        return json.load(f)

def save_test_data(data: Any, filename: str):
    """Save test data to a JSON file in the test data directory."""
    test_data_dir = Path(__file__).parent.parent / 'test_data'
    test_data_dir.mkdir(exist_ok=True)
    file_path = test_data_dir / filename
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def create_mock_request(method: str='GET', path: str='/', **kwargs):
    """Create a mock HTTP request for testing."""
    mock_request = Mock()
    mock_request.method = method
    mock_request.path = path
    mock_request.args = kwargs.get('args', {})
    mock_request.json = kwargs.get('json', {})
    mock_request.headers = kwargs.get('headers', {})
    return mock_request

def create_mock_response(status_code: int=200, data: Any=None):
    """Create a mock HTTP response for testing."""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = data or {}
    mock_response.text = json.dumps(data) if data else ''
    return mock_response

class FeedbackCollector:
    """Test feedback utility for testing feedback collection and processing."""

    def __init__(self):
        self.feedback_data = []

    def collect_feedback(self, data):
        """Collect test feedback data."""
        self.feedback_data.append(data)
        return True

    def get_feedback(self):
        """Get collected feedback."""
        return self.feedback_data.copy()

    def clear_feedback(self):
        """Clear collected feedback."""
        self.feedback_data.clear()

    @staticmethod
    def print_header(title):
        """Print a test header."""
        print('\n' + '=' * 60)
        print(f' {title.upper()} ')
        print('=' * 60)

    @staticmethod
    def print_section(title):
        """Print a test section header."""
        print('\n' + '-' * 50)
        print(f' {title} ')
        print('-' * 50)

    @staticmethod
    def print_result(result_data=None, **kwargs):
        """Print test result data."""
        if result_data is None and kwargs:
            result_data = kwargs
        if isinstance(result_data, dict):
            print('\n' + '=' * 50)
            print('TEST RESULTS')
            print('=' * 50)
            for key, value in result_data.items():
                print(f'{key}: {value}')
            print('=' * 50)
        else:
            print(f'Test Result: {result_data}')
        return kwargs.get('passed', result_data)

    @staticmethod
    def print_summary(test_results, start_time):
        """Print test summary."""
        total_time = time.time() - start_time
        print('\n' + '=' * 60)
        print(' TEST SUMMARY ')
        print('=' * 60)
        total_tests = len(test_results) if isinstance(test_results, list) else 1
        print(f'Total tests: {total_tests}')
        print(f'Execution time: {total_time:.2f}s')
        if isinstance(test_results, list):
            passed = sum((1 for result in test_results if isinstance(result, dict) and result.get('passed', False)))
            print(f'Passed: {passed}')
            print(f'Failed: {total_tests - passed}')
        print('=' * 60)
        return 0

class Timer:
    """Simple timer utility for testing performance."""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        return self

    def stop(self):
        """Stop the timer."""
        self.end_time = time.time()
        return self

    def elapsed(self):
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

class SafeTestRunner:
    """Safe test runner that provides enhanced error handling and test isolation."""

    def __init__(self, verbosity=1):
        self.verbosity = verbosity
        self.results = []

    def run_test_suite(self, test_suite, test_name='Test Suite'):
        """Run a test suite with safe error handling."""
        start_time = time.time()
        try:
            result = unittest.TextTestResult(sys.stdout, verbosity=self.verbosity, stream=sys.stdout)
            test_suite.run(result)
            tests_run = result.testsRun
            errors = len(result.errors)
            failures = len(result.failures)
            passed = tests_run - errors - failures
            test_result = {'test_name': test_name, 'tests_run': tests_run, 'passed': passed, 'failed': failures, 'errors': errors, 'success': errors == 0 and failures == 0, 'execution_time': time.time() - start_time}
            self.results.append(test_result)
            return test_result
        except Exception as e:
            error_result = {'test_name': test_name, 'tests_run': 0, 'passed': 0, 'failed': 0, 'errors': 1, 'success': False, 'error': str(e), 'execution_time': time.time() - start_time}
            self.results.append(error_result)
            return error_result

    def run_single_test(self, test_class, test_method=None):
        """Run a single test class or method safely."""
        try:
            if test_method:
                suite = unittest.TestSuite()
                suite.addTest(test_class(test_method))
                test_name = f'{test_class.__name__}.{test_method}'
            else:
                suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
                test_name = test_class.__name__
            return self.run_test_suite(suite, test_name)
        except Exception as e:
            return {'test_name': test_class.__name__, 'tests_run': 0, 'passed': 0, 'failed': 0, 'errors': 1, 'success': False, 'error': str(e), 'execution_time': 0}

    def get_summary(self):
        """Get summary of all test runs."""
        total_tests = sum((r.get('tests_run', 0) for r in self.results))
        total_passed = sum((r.get('passed', 0) for r in self.results))
        total_failed = sum((r.get('failed', 0) for r in self.results))
        total_errors = sum((r.get('errors', 0) for r in self.results))
        total_time = sum((r.get('execution_time', 0) for r in self.results))
        return {'total_suites': len(self.results), 'total_tests': total_tests, 'total_passed': total_passed, 'total_failed': total_failed, 'total_errors': total_errors, 'success_rate': total_passed / max(total_tests, 1) * 100, 'total_time': total_time}
__all__ = ['TestContextManager', 'FeedbackCollector', 'Timer', 'SafeTestRunner', 'TemporaryEnvironment', 'create_test_context', 'setup_test_environment', 'cleanup_test_environment', 'create_temporary_file', 'create_temporary_directory', 'wait_for_condition', 'assert_eventually', 'mock_environment_variables', 'capture_logs', 'create_mock_file_system', 'load_test_data', 'save_test_data', 'create_mock_request', 'create_mock_response']