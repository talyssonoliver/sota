#!/usr/bin/env python3
"""
Enhanced Test Runner for AI System
Provides parallel test execution with optimized performance
"""

import argparse
import sys
import subprocess
import os
import time
from pathlib import Path


def run_pytest_with_args(args):
    """Run pytest with the provided arguments"""
    cmd = ["python", "-m", "pytest"]
    
    if args.quick:
        # Quick test configuration - fast, parallel, minimal output
        cmd.extend([
            "-n", "4",  # 4 parallel workers
            "--dist", "loadscope",
            "--tb=line",
            "--maxfail=5",
            "-x",  # stop on first failure
            "--disable-warnings",
            "-q",  # quiet output
            "tests/"
        ])
    elif args.suite:
        # Run specific test suite
        if args.suite == "unit":
            cmd.extend(["tests/unit/"])
        elif args.suite == "integration":
            cmd.extend(["tests/integration/"])
        else:
            cmd.extend([f"tests/{args.suite}/"])
            
        if args.verbose:
            cmd.append("-v")
    elif args.parallel:
        # Run specific test suites in parallel
        for suite in args.parallel:
            suite_cmd = cmd + [f"tests/{suite}/"]
            if args.verbose:
                suite_cmd.append("-v")
            subprocess.run(suite_cmd)
        return
    else:
        # Default test run
        cmd.extend(["tests/"])
        if args.verbose:
            cmd.append("-v")
    
    if args.workers:
        cmd.extend(["-n", str(args.workers)])
    
    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=term"])
    
    # Run the command
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Enhanced Test Runner for AI System")
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick tests (parallel, minimal output)")
    parser.add_argument("--suite", choices=["unit", "integration", "e2e"],
                       help="Run specific test suite")
    parser.add_argument("--parallel", nargs='+', 
                       choices=["unit", "integration", "e2e"],
                       help="Run multiple test suites in parallel")
    parser.add_argument("--workers", type=int, default=4,
                       help="Number of parallel workers")
    parser.add_argument("--coverage", action="store_true",
                       help="Include coverage reporting")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Set testing environment variables
    os.environ["TESTING"] = "1"
    os.environ["PYTEST_RUNNING"] = "1"
    os.environ["DISABLE_WORKFLOW_MONITORING"] = "1"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    
    print("🧪 Enhanced Test Runner - AI System")
    print(f"📁 Working directory: {project_root}")
    
    start_time = time.time()
    exit_code = run_pytest_with_args(args)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"\n⏱️  Test execution completed in {duration:.2f} seconds")
    
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
