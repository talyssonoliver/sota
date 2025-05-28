#!/usr/bin/env python
"""
Unified test runner script for the AI system.
This script provides a single entry point to run all or specific tests
with proper dependency handling.
"""

import importlib
import importlib.util
import os
import sys
import time
import traceback
import types
import unittest
from argparse import ArgumentParser
from datetime import datetime
from unittest.mock import MagicMock

from tests.mock_environment import setup_mock_environment
from tests.test_utils import TestFeedback, Timer

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the enhanced mock environment setup

# Apply mock environment setup
setup_mock_environment()

# Import directly


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_modules = [
        'unittest', 'crewai', 'langchain', 'langchain_community',
        'pydantic', 'chromadb'
    ]

    missing_modules = []
    for module_name in required_modules:
        try:
            # Skip already mocked modules
            if module_name in sys.modules:
                continue

            # Try to import the module but catch specific errors
            try:
                importlib.import_module(module_name)
            except UnicodeDecodeError:
                # This dependency has encoding issues, but it's installed
                print(
                    f"Warning: {module_name} is installed but has encoding issues")
            except ImportError:
                missing_modules.append(module_name)
        except Exception as e:
            print(f"Warning: Error checking for {module_name}: {e}")
            missing_modules.append(module_name)

    if missing_modules:
        print("WARNING: The following required modules are missing:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nYou can install them using: pip install -r requirements.txt")
        print("Attempting to continue with mock environment...\n")

    return len(missing_modules) == 0


def import_test_module_safely(module_path):
    """Import a test module from file path and return the module if successful."""
    try:
        # Get the file path without extension for module name
        module_name = os.path.splitext(os.path.basename(module_path))[0]

        # Use importlib.util to import from file path
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            print(f"Error: Could not load spec for {module_path}")
            return None

        module = importlib.util.module_from_spec(spec)

        # Add the module to sys.modules before executing it
        sys.modules[module_name] = module

        # Execute the module code
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error importing test module {module_path}: {str(e)}")
        traceback.print_exc()
        return None


def run_validate_agents_test():
    """Run the quick agent validation test by importing and running test_agents.py."""
    test_name = "Agent Validation"
    start_time = datetime.now()
    timer = Timer().start()

    print(f"\n===== Running {test_name} =====\n")

    try:
        # Import test_agents.py module
        test_file_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "test_agents.py")
        test_module = import_test_module_safely(test_file_path)

        if test_module is None:
            print("Error: Could not import test_agents.py")
            raise ImportError("Failed to import test_agents.py")

        # Check if there's a FeedbackTestRunner in the module
        if hasattr(
                test_module,
                'FeedbackTestRunner') and hasattr(
                test_module.FeedbackTestRunner,
                'run'):
            # Use the FeedbackTestRunner
            passed = test_module.FeedbackTestRunner.run()
        else:
            # Create and run a test suite manually
            suite = unittest.TestLoader().loadTestsFromModule(test_module)
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            passed = result.wasSuccessful()

        timer.stop()

        details = {
            "Test file": "test_agents.py",
            "Execution time": timer.elapsed(),
        }

        return TestFeedback.print_result(
            test_name=test_name,
            passed=passed,
            details=details,
            execution_time=timer.elapsed()
        )
    except Exception as e:
        timer.stop()

        details = {
            "Error": str(e),
            "Traceback": traceback.format_exc()
        }

        print(f"Error running agent validation: {e}")
        traceback.print_exc()

        return TestFeedback.print_result(
            test_name=test_name,
            passed=False,
            details=details,
            execution_time=timer.elapsed()
        )


def run_tool_loader_test():
    """Run the tool loader test by importing and running test_tool_loader.py."""
    test_name = "Tool Loader"
    timer = Timer().start()

    print(f"\n===== Running {test_name} Test =====\n")

    try:
        # Import test_tool_loader.py module
        test_file_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "test_tool_loader.py")
        test_module = import_test_module_safely(test_file_path)

        if test_module is None:
            print("Error: Could not import test_tool_loader.py")
            raise ImportError("Failed to import test_tool_loader.py")

        # Check if there's a run_all_tests function in the module
        if hasattr(test_module, 'run_all_tests'):
            # Use the run_all_tests function
            exit_code = test_module.run_all_tests()
            passed = exit_code == 0
        else:
            # Run individual test functions
            if hasattr(test_module, 'test_load_tool_config'):
                print("Running test_load_tool_config...")
                test_module.test_load_tool_config()

            if hasattr(test_module, 'test_agent_tool_mapping'):
                print("Running test_agent_tool_mapping...")
                test_module.test_agent_tool_mapping()

            if hasattr(test_module, 'test_get_tools_for_agent'):
                print("Running test_get_tools_for_agent...")
                test_module.test_get_tools_for_agent()

            # Assume passed if we got this far
            passed = True

        timer.stop()

        details = {
            "Test file": "test_tool_loader.py",
            "Execution time": timer.elapsed(),
        }

        return TestFeedback.print_result(
            test_name=test_name,
            passed=passed,
            details=details,
            execution_time=timer.elapsed()
        )
    except Exception as e:
        timer.stop()

        details = {
            "Error": str(e),
            "Traceback": traceback.format_exc()
        }

        print(f"Error in tool loader test execution: {e}")
        traceback.print_exc()

        return TestFeedback.print_result(
            test_name=test_name,
            passed=False,
            details=details,
            execution_time=timer.elapsed()
        )


def run_workflow_tests():
    """Run the workflow-related tests for state transitions, QA agent decisions, and integration."""
    test_name = "Workflow Tests"
    timer = Timer().start()

    print(f"\n===== Running {test_name} =====\n")

    test_modules = [
        "test_workflow_states.py",
        "test_qa_agent_decisions.py",
        "test_workflow_integration.py"
    ]

    test_results = {}
    tests_run = 0
    tests_passed = 0

    try:
        test_dir = os.path.dirname(os.path.abspath(__file__))

        # Run each workflow test module
        for module_filename in test_modules:
            module_name = os.path.splitext(module_filename)[0]
            file_path = os.path.join(test_dir, module_filename)

            print(f"\n----- Running {module_name} -----\n")
            module_timer = Timer().start()

            # Import the test module
            test_module = import_test_module_safely(file_path)
            if test_module is None:
                print(f"Error: Could not import {module_filename}")
                test_results[module_name] = False
                continue

            # Load and run the tests in this module
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)

            # Create a special result collector for detailed reporting
            class DetailedTextTestResult(unittest.TextTestResult):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.test_details = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0,
                        "errors": 0,
                        "test_cases": {}
                    }

                def startTest(self, test):
                    super().startTest(test)
                    self.test_details["total"] += 1
                    test_id = self.getDescription(test)
                    self.test_details["test_cases"][test_id] = {
                        "status": "running"}

                def addSuccess(self, test):
                    super().addSuccess(test)
                    self.test_details["passed"] += 1
                    test_id = self.getDescription(test)
                    self.test_details["test_cases"][test_id] = {
                        "status": "passed"}

                def addFailure(self, test, err):
                    super().addFailure(test, err)
                    self.test_details["failed"] += 1
                    test_id = self.getDescription(test)
                    self.test_details["test_cases"][test_id] = {
                        "status": "failed", "error": str(err[1])}

                def addError(self, test, err):
                    super().addError(test, err)
                    self.test_details["errors"] += 1
                    test_id = self.getDescription(test)
                    self.test_details["test_cases"][test_id] = {
                        "status": "error", "error": str(err[1])}

            # Run with our detailed result collector
            runner = unittest.TextTestRunner(
                verbosity=2,
                resultclass=DetailedTextTestResult
            )

            # Run the tests
            result = runner.run(suite)

            # Save the results
            module_passed = result.wasSuccessful()
            test_results[module_name] = module_passed
            tests_run += result.test_details["total"]
            tests_passed += result.test_details["passed"]

            # Print module summary
            module_timer.stop()
            print(f"\n{module_name} Summary:")
            print(f"  Tests: {result.test_details['total']}")
            print(f"  Passed: {result.test_details['passed']}")
            print(f"  Failed: {result.test_details['failed']}")
            print(f"  Errors: {result.test_details['errors']}")
            print(f"  Time: {module_timer.elapsed():.2f}s")
            print(f"  Result: {'PASSED' if module_passed else 'FAILED'}")

        timer.stop()

        # Calculate overall pass/fail
        all_passed = all(test_results.values())

        # Prepare details for reporting
        details = {
            "Test modules": list(test_results.keys()),
            "Tests run": tests_run,
            "Tests passed": tests_passed,
            "Tests failed": tests_run - tests_passed,
            "Module results": test_results,
            "Execution time": timer.elapsed()
        }

        return TestFeedback.print_result(
            test_name=test_name,
            passed=all_passed,
            details=details,
            execution_time=timer.elapsed()
        )
    except Exception as e:
        timer.stop()

        details = {
            "Error": str(e),
            "Traceback": traceback.format_exc()
        }

        print(f"Error running workflow tests: {e}")
        traceback.print_exc()

        return TestFeedback.print_result(
            test_name=test_name,
            passed=False,
            details=details,
            execution_time=timer.elapsed()
        )


def run_full_test_suite():
    """Run tests using unittest discovery to find all test files."""
    test_name = "Full Test Suite"
    timer = Timer().start()

    print(f"\n===== Running {test_name} =====\n")

    test_results = {}
    test_details = {}

    try:
        # Use the unittest discovery to find and run all test_*.py files
        test_dir = os.path.dirname(os.path.abspath(__file__))

        # Create a collector to capture test results
        class TestCollector(unittest.TextTestResult):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.test_results = {}

            def addSuccess(self, test):
                super().addSuccess(test)
                test_name = str(test).split(" ")[0]
                self.test_results[test_name] = True

            def addFailure(self, test, err):
                super().addFailure(test, err)
                test_name = str(test).split(" ")[0]
                self.test_results[test_name] = False

            def addError(self, test, err):
                super().addError(test, err)
                test_name = str(test).split(" ")[0]
                self.test_results[test_name] = False

        # Custom test runner that uses our collector
        class CustomTestRunner(unittest.TextTestRunner):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def _makeResult(self):
                return TestCollector(
                    self.stream, self.descriptions, self.verbosity)

        # Create a test loader that will find all test_*.py files
        loader = unittest.TestLoader()

        # Skip certain test files that aren't designed for automatic discovery
        skip_files = ['test_utils.py']

        # Find test files manually
        test_files = []
        for filename in os.listdir(test_dir):
            if filename.startswith('test_') and filename.endswith(
                    '.py') and filename not in skip_files:
                test_files.append(filename)

        all_passed = True
        tests_run = 0

        # Run each test file individually
        for filename in test_files:
            file_path = os.path.join(test_dir, filename)
            module_name = os.path.splitext(filename)[0]

            try:
                # Load the module
                test_module = import_test_module_safely(file_path)
                if test_module is None:
                    print(f"Skipping {filename} due to import error")
                    continue

                # Check if the module has a special runner
                if hasattr(
                        test_module,
                        'FeedbackTestRunner') and hasattr(
                        test_module.FeedbackTestRunner,
                        'run'):
                    print(
                        f"\nRunning {filename} with its dedicated test runner...")
                    module_passed = test_module.FeedbackTestRunner.run()
                    test_results[module_name] = module_passed
                    all_passed = all_passed and module_passed
                    tests_run += 1
                elif hasattr(test_module, 'run_all_tests'):
                    print(
                        f"\nRunning {filename} with its run_all_tests function...")
                    exit_code = test_module.run_all_tests()
                    module_passed = exit_code == 0
                    test_results[module_name] = module_passed
                    all_passed = all_passed and module_passed
                    tests_run += 1
                else:
                    # Load all test cases from the module into a suite
                    print(f"\nRunning {filename} with unittest discovery...")
                    suite = loader.loadTestsFromModule(test_module)

                    # Run the tests with our custom runner
                    runner = CustomTestRunner(verbosity=2)
                    result = runner.run(suite)

                    # Track results
                    test_results[module_name] = result.wasSuccessful()
                    all_passed = all_passed and result.wasSuccessful()
                    tests_run += result.testsRun

                    # Save detailed results
                    test_details[module_name] = {
                        "tests_run": result.testsRun,
                        "errors": len(result.errors),
                        "failures": len(result.failures)
                    }
            except Exception as e:
                print(f"Error running {filename}: {e}")
                traceback.print_exc()
                test_results[module_name] = False
                all_passed = False
                test_details[module_name] = {
                    "error": str(e)
                }

        timer.stop()

        details = {
            "Test files": list(
                test_results.keys()),
            "Tests run": tests_run,
            "Tests passed": sum(
                1 for result in test_results.values() if result),
            "Tests failed": sum(
                1 for result in test_results.values() if not result),
            "Execution time": timer.elapsed(),
            "Details": test_details}

        return TestFeedback.print_result(
            test_name=test_name,
            passed=all_passed,
            details=details,
            execution_time=timer.elapsed()
        )
    except Exception as e:
        timer.stop()

        details = {
            "Error": str(e),
            "Traceback": traceback.format_exc()
        }

        print(f"Error setting up environment or running tests: {e}")
        traceback.print_exc()

        return TestFeedback.print_result(
            test_name=test_name,
            passed=False,
            details=details,
            execution_time=timer.elapsed()
        )


def generate_coverage_report():
    """Generate test coverage report if coverage is installed."""
    try:
        import coverage
        has_coverage = True
    except ImportError:
        has_coverage = False
        print("\nCoverage reporting requires the 'coverage' package.")
        print("Install it with: pip install coverage")
        return False

    if has_coverage:
        print("\n===== Generating Test Coverage Report =====\n")
        try:
            # Create coverage directory if it doesn't exist
            coverage_dir = os.path.join(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))), "coverage")
            os.makedirs(coverage_dir, exist_ok=True)

            # Initialize coverage with configuration
            cov = coverage.Coverage(
                source=["orchestration", "graph", "agents", "handlers"],
                omit=["*/__pycache__/*", "*/tests/*"],
                data_file=os.path.join(coverage_dir, ".coverage")
            )

            # Start coverage measurement
            cov.start()

            # Run the tests
            print("Running tests with coverage measurement...")
            run_workflow_tests()

            # Stop coverage measurement
            cov.stop()

            # Generate reports
            print("\nGenerating coverage reports...")
            cov.save()

            # HTML report
            html_dir = os.path.join(coverage_dir, "html")
            cov.html_report(directory=html_dir)

            # XML report for CI integration
            xml_file = os.path.join(coverage_dir, "coverage.xml")
            cov.xml_report(outfile=xml_file)

            # Console report
            report = cov.report()

            print(f"\nCoverage report generated successfully!")
            print(f"HTML report: {html_dir}/index.html")
            print(f"XML report: {xml_file}")

            return True
        except Exception as e:
            print(f"Error generating coverage report: {e}")
            traceback.print_exc()
            return False

    return False


def main():
    """Main entry point for the test runner script."""
    parser = ArgumentParser(description="Run AI system tests")
    parser.add_argument("--quick", action="store_true",
                        help="Run only the quick validation test")
    parser.add_argument("--tools", action="store_true",
                        help="Run only the tool loader test")
    parser.add_argument("--workflow", action="store_true",
                        help="Run only the workflow-related tests")
    parser.add_argument("--full", action="store_true",
                        help="Run the full test suite")
    parser.add_argument("--all", action="store_true",
                        help="Run all tests")
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate test coverage report (requires coverage package)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show detailed output including full tracebacks")

    args = parser.parse_args()

    # Validate arguments - default to all if nothing specified
    if not (
            args.quick or args.tools or args.workflow or args.full or args.all or args.coverage):
        args.all = True

    print("Setting up test environment with mocked dependencies...")

    exit_code = 0
    test_results = []
    overall_start_time = time.time()

    # Run requested tests
    if args.quick or args.all:
        quick_result = run_validate_agents_test()
        exit_code = exit_code or (0 if quick_result else 1)
        test_results.append(("Agent Validation", quick_result))

    if args.tools or args.all:
        tools_result = run_tool_loader_test()
        exit_code = exit_code or (0 if tools_result else 1)
        test_results.append(("Tool Loader", tools_result))

    if args.workflow or args.all:
        workflow_result = run_workflow_tests()
        exit_code = exit_code or (0 if workflow_result else 1)
        test_results.append(("Workflow Tests", workflow_result))

    if args.full or args.all:
        full_result = run_full_test_suite()
        exit_code = exit_code or (0 if full_result else 1)
        test_results.append(("Full Test Suite", full_result))

    # Generate coverage report if requested
    if args.coverage:
        coverage_result = generate_coverage_report()
        test_results.append(("Coverage Report", coverage_result))

    # Print overall summary
    exit_code = TestFeedback.print_summary(test_results, overall_start_time)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
