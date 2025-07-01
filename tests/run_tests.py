"""
Enhanced Test Runner Module

This module provides a streamlined interface to the enhanced test runner
while maintaining backward compatibility with existing scripts.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

try:
    from tests.enhanced_test_runner import EnhancedTestRunner
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    import unittest


def run_quick_tests():
    """Run quick validation tests"""
    if ENHANCED_AVAILABLE:
        print('🏃‍♂️ Running quick tests with enhanced runner...')
        runner = EnhancedTestRunner()
        return runner.run_quick_tests()
    else:
        print('⚠️  Enhanced runner not available, falling back to basic tests...')
        return discover_and_run_tests('tests/unit')


def run_full_test_suite():
    """Run the full test suite"""
    if ENHANCED_AVAILABLE:
        print('🎯 Running full test suite with enhanced runner...')
        runner = EnhancedTestRunner()
        return runner.run_full_suite()
    else:
        print('⚠️  Enhanced runner not available, falling back to basic tests...')
        return discover_and_run_tests('tests')


def discover_and_run_tests(test_dir='tests'):
    """Discover and run tests in the given directory (fallback method)"""
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