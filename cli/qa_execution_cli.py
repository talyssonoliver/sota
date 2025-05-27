#!/usr/bin/env python3
"""
CLI interface for QA Agent Execution (Step 5.3)

Provides command-line interface for manual QA validation and testing.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from orchestration.langgraph_qa_integration import LangGraphQAIntegration
from orchestration.qa_execution import QAExecutionEngine, execute_qa_validation

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def setup_cli_logger(verbose: bool = False) -> logging.Logger:
    """Setup CLI logger with appropriate level"""
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger("qa_cli")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def display_qa_report(report: dict, verbose: bool = False) -> None:
    """Display QA report in a readable format"""
    print("\n" + "=" * 60)
    print(f"🔍 QA VALIDATION REPORT - {report.get('task_id', 'Unknown')}")
    print("=" * 60)

    # Status
    status = report.get('status', 'UNKNOWN')
    status_emoji = {
        'PASSED': '✅',
        'FAILED': '❌',
        'WARNING': '⚠️',
        'ERROR': '💥',
        'SKIPPED': '⏭️'
    }.get(status, '❓')

    print(f"Status: {status_emoji} {status}")

    # Test Results
    tests_passed = report.get('tests_passed', 0)
    tests_failed = report.get('tests_failed', 0)
    total_tests = tests_passed + tests_failed

    print(
        f"Tests: {tests_passed} passed, {tests_failed} failed ({total_tests} total)")

    # Coverage
    coverage = report.get('coverage', 0)
    print(f"Coverage: {coverage:.1f}%")

    # Issues
    issues = report.get('issues', [])
    if issues:
        print(f"\n⚠️  Issues Found ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            severity = issue.get('severity', 'unknown')
            message = issue.get('message', 'No message')
            print(f"  {i}. [{severity.upper()}] {message}")
    else:
        print("\n✅ No critical issues found")

    # Verbose details
    if verbose:
        print(f"\n📊 Detailed Metrics:")
        if 'test_generation' in report:
            gen = report['test_generation']
            print(
                f"  Test Generation: {
                    gen.get(
                        'successful',
                        0)} successful, {
                    gen.get(
                        'failed',
                        0)} failed")

        if 'static_analysis' in report:
            analysis = report['static_analysis']
            print(
                f"  Static Analysis: {
                    analysis.get(
                        'files_analyzed',
                        0)} files analyzed")
            print(f"  Critical Issues: {analysis.get('critical_issues', 0)}")
            print(f"  Warnings: {analysis.get('warnings', 0)}")

        print(f"  Timestamp: {report.get('timestamp', 'Unknown')}")

    print("=" * 60)


def validate_task(
        task_id: str,
        outputs_dir: str,
        verbose: bool = False) -> dict:
    """Execute QA validation for a specific task"""
    logger = setup_cli_logger(verbose)

    try:
        logger.info(f"Starting QA validation for task: {task_id}")

        # Initialize QA execution engine
        qa_engine = QAExecutionEngine(outputs_dir)

        # Execute QA validation
        qa_report = qa_engine.execute_qa_for_task(task_id)

        logger.info(
            f"QA validation completed with status: {qa_report.get('status')}")
        return qa_report

    except Exception as e:
        logger.error(f"QA validation failed: {str(e)}")
        return {
            "task_id": task_id,
            "status": "ERROR",
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage": 0.0,
            "issues": [{"severity": "error", "message": f"Validation failed: {str(e)}"}],
            "timestamp": "error"
        }


def test_langgraph_integration(
        task_id: str,
        outputs_dir: str,
        verbose: bool = False) -> dict:
    """Test LangGraph integration for QA state transitions"""
    logger = setup_cli_logger(verbose)

    try:
        logger.info(f"Testing LangGraph QA integration for task: {task_id}")

        # Initialize LangGraph QA integration
        qa_integration = LangGraphQAIntegration(outputs_dir)

        # Simulate QA_PENDING state handling
        result = qa_integration.handle_qa_pending_state(
            task_id, {"agent": "test"})

        logger.info(f"LangGraph integration test completed")
        return result

    except Exception as e:
        logger.error(f"LangGraph integration test failed: {str(e)}")
        return {
            "task_id": task_id,
            "current_state": "QA_PENDING",
            "next_state": "ERROR",
            "error": str(e)
        }


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="QA Agent Execution CLI (Step 5.3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run QA validation for a task
  python cli/qa_execution_cli.py --task BE-07

  # Run with verbose output
  python cli/qa_execution_cli.py --task BE-07 --verbose

  # Test LangGraph integration
  python cli/qa_execution_cli.py --task BE-07 --test-langgraph

  # Specify custom outputs directory
  python cli/qa_execution_cli.py --task BE-07 --outputs-dir /custom/path

  # Export report to JSON file
  python cli/qa_execution_cli.py --task BE-07 --export report.json
        """
    )

    # Required arguments
    parser.add_argument(
        "--task", "-t",
        required=True,
        help="Task ID to validate (e.g., BE-07)"
    )

    # Optional arguments
    parser.add_argument(
        "--outputs-dir", "-o",
        default="outputs",
        help="Path to outputs directory (default: outputs)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--test-langgraph", "-l",
        action="store_true",
        help="Test LangGraph integration instead of standard QA validation"
    )

    parser.add_argument(
        "--export", "-e",
        help="Export report to JSON file"
    )

    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Skip display output (useful with --export)"
    )

    args = parser.parse_args()

    # Setup logger
    logger = setup_cli_logger(args.verbose)

    try:
        # Validate outputs directory
        outputs_path = Path(args.outputs_dir)
        if not outputs_path.exists():
            logger.error(f"Outputs directory not found: {outputs_path}")
            sys.exit(1)

        # Execute appropriate validation
        if args.test_langgraph:
            result = test_langgraph_integration(
                args.task, str(outputs_path), args.verbose)
            report_type = "LangGraph Integration Test"
        else:
            result = validate_task(args.task, str(outputs_path), args.verbose)
            report_type = "QA Validation Report"

        # Display results
        if not args.no_display:
            if args.test_langgraph:
                print(f"\n🔄 {report_type}")
                print(f"Task: {result.get('task_id')}")
                print(f"Current State: {result.get('current_state')}")
                print(f"Next State: {result.get('next_state')}")
                if 'error' in result:
                    print(f"Error: {result['error']}")
            else:
                display_qa_report(result, args.verbose)

        # Export to file if requested
        if args.export:
            export_path = Path(args.export)
            with open(export_path, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Report exported to: {export_path}")

        # Exit with appropriate code
        if args.test_langgraph:
            exit_code = 0 if result.get('next_state') != 'ERROR' else 1
        else:
            exit_code = 0 if result.get('status') in [
                'PASSED', 'WARNING'] else 1

        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
