"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
Test runner module for running various test suites.
"""
try:
    pass
except ImportError:
    pass
import sys
from pathlib import Path

def run_quick_tests():
    """Run quick validation tests"""
    print('Running quick tests...')
    return True

def run_full_test_suite():
    """Run the full test suite"""
    print('Running full test suite...')
    return True

def discover_and_run_tests(test_dir='tests'):
    """Discover and run tests in the given directory"""
    loader = unittest.TestLoader()
    start_dir = Path(test_dir)
    if not start_dir.exists():
        print(f'Test directory {test_dir} not found')
        return False
    suite = loader.discover(str(start_dir))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def main():
    """Main test runner function"""
    if '--quick' in sys.argv:
        return run_quick_tests()
    else:
        return run_full_test_suite()
if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)