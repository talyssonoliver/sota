from tests.utils.test_utils import *
try:
    pass
except ImportError:
    pass

class TestFeedback:
    """Simple feedback class for test results."""

    @staticmethod
    def print_result(test_name, passed, details=None, execution_time=0):
        """Print test result in a formatted way."""
        status = 'PASSED' if passed else 'FAILED'
        print(f'\n{'=' * 50}')
        print('TEST RESULTS')
        print(f'{'=' * 50}')
        print(f'test_name: {test_name}')
        print(f'passed: {passed}')
        print(f'details: {details}')
        print(f'execution_time: {execution_time}')
        print(f'{'=' * 50}')
        return passed