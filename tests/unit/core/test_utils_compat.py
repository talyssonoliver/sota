from tests.utils.test_utils import (
    TestContextManager,
    FeedbackCollector,
    Timer,
    SafeTestRunner,
    TemporaryEnvironment,
    create_test_context,
    setup_test_environment,
    cleanup_test_environment,
    create_temporary_file,
    create_temporary_directory,
    wait_for_condition,
    assert_eventually,
    mock_environment_variables,
    capture_logs,
    create_mock_file_system,
    load_test_data,
    save_test_data,
    create_mock_request,
    create_mock_response,
)

# Re-export all imported items for compatibility
__all__ = [
    "TestContextManager",
    "FeedbackCollector", 
    "Timer",
    "SafeTestRunner",
    "TemporaryEnvironment",
    "create_test_context",
    "setup_test_environment",
    "cleanup_test_environment",
    "create_temporary_file",
    "create_temporary_directory",
    "wait_for_condition",
    "assert_eventually",
    "mock_environment_variables",
    "capture_logs",
    "create_mock_file_system",
    "load_test_data",
    "save_test_data",
    "create_mock_request",
    "create_mock_response",
    "TestFeedback",
]

try:
    pass
except ImportError:
    pass


class TestFeedback:
    """Simple feedback class for test results."""

    @staticmethod
    def print_result(test_name, passed, details=None, execution_time=0):
        """Print test result in a formatted way."""
        status = "PASSED" if passed else "FAILED"
        print(f"\n{'=' * 50}")
        print("TEST RESULTS")
        print(f"{'=' * 50}")
        print(f"test_name: {test_name}")
        print(f"status: {status}")
        print(f"details: {details}")
        print(f"execution_time: {execution_time}")
        print(f"{'=' * 50}")
        return passed
