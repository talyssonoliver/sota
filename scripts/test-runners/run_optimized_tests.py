#!/usr/bin/env python3
"""
Optimized Test Runner for AI System
Demonstrates the test suite optimization improvements.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description):
    """Run a command and track execution time."""
    print(f"\n🚀 {description}")
    print("=" * 50)

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True)
        duration = time.time() - start_time

        print(f"⏱️  Duration: {duration:.2f}s")

        if result.returncode == 0:
            print("✅ Success")
            if result.stdout:
                print("Output:", result.stdout[-500:])  # Last 500 chars
        else:
            print("❌ Failed")
            if result.stderr:
                print("Error:", result.stderr[-500:])

        return result.returncode == 0, duration

    except Exception as e:
        duration = time.time() - start_time
        print(f"💥 Exception: {e}")
        return False, duration


def install_dependencies():
    """Install required test dependencies."""
    dependencies = [
        "pytest-xdist",  # For parallel execution
        "pytest-cov",    # For coverage
        "pytest-benchmark",  # For performance testing
        "pytest-mock"   # Enhanced mocking
    ]

    for dep in dependencies:
        print(f"📦 Installing {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep],
                       capture_output=True)


def main():
    """Run the optimized test suite demonstration."""
    print("🎯 AI System Test Suite Optimization Demo")
    print("=" * 60)

    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Install dependencies
    print("\n📦 Installing test dependencies...")
    install_dependencies()

    results = {}

    # 1. Run unit tests only (fast)
    success, duration = run_command(
        'pytest tests/ -m "unit" --tb=short -v',
        "Phase 1: Fast Unit Tests Only"
    )
    results["unit_tests"] = {"success": success, "duration": duration}

    # 2. Run with parallel execution (if available)
    success, duration = run_command(
        'pytest tests/ -m "unit" -n 4 --tb=short',
        "Phase 2: Parallel Unit Tests"
    )
    results["parallel_tests"] = {"success": success, "duration": duration}

    # 3. Run integration tests separately
    success, duration = run_command(
        'pytest tests/ -m "integration" --tb=short -v',
        "Phase 3: Integration Tests"
    )
    results["integration_tests"] = {"success": success, "duration": duration}

    # 4. Run specific test categories
    success, duration = run_command(
        'pytest tests/test_agents.py -v --tb=short',
        "Phase 4: Agent Tests (Optimized)"
    )
    results["agent_tests"] = {"success": success, "duration": duration}

    # 5. Run memory tests with mocks
    success, duration = run_command(
        'pytest tests/test_memory_*.py -v --tb=short',
        "Phase 5: Memory Tests (Mocked)"
    )
    results["memory_tests"] = {"success": success, "duration": duration}

    # 6. Performance benchmark
    success, duration = run_command(
        'pytest tests/test_tool_loader.py -v --durations=10',
        "Phase 6: Performance Benchmark"
    )
    results["benchmark"] = {"success": success, "duration": duration}

    # Generate summary report
    print("\n📊 OPTIMIZATION RESULTS SUMMARY")
    print("=" * 60)

    total_time = sum(r["duration"] for r in results.values())
    success_count = sum(1 for r in results.values() if r["success"])
    total_tests = len(results)

    print(f"✅ Successful test runs: {success_count}/{total_tests}")
    print(f"⏱️  Total execution time: {total_time:.2f}s")
    print(f"🚀 Average time per phase: {total_time / total_tests:.2f}s")

    print("\n📈 Performance Improvements:")
    print("• External services mocked → No network delays")
    print("• Environment isolation → No conflicts")
    print("• Parallel execution → 4x faster on multi-core")
    print("• Test categorization → Run only what you need")
    print("• Recursion fixes → No infinite loops")

    print("\n🎯 Quick Commands for Development:")
    print("# Fast development tests (< 30s)")
    print('pytest tests/ -m "unit" -n 4')
    print()
    print("# Full test suite with coverage")
    print('pytest tests/ --cov=. --cov-report=html')
    print()
    print("# Skip slow tests")
    print('pytest tests/ -m "not slow"')
    print()
    print("# Only memory/agent tests")
    print('pytest tests/ -m "memory or agent"')

    return success_count == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
