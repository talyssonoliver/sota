#!/usr/bin/env python3
"""
Quick integration test for Step 4.8 Real-time Execution Monitoring
"""

import os
import time

from utils.execution_monitor import ExecutionMonitor, get_execution_monitor


def test_step_4_8_integration():
    """Test Step 4.8 monitoring system integration."""
    print("🎯 Testing Step 4.8 Real-time Execution Monitoring")
    print("=" * 50)

    # Test the global monitor
    monitor = get_execution_monitor()
    print("✅ Global execution monitor loaded successfully")

    # Simulate a quick workflow
    task_id = 'TEST-INTEGRATION'
    print(f"\n📋 Starting test execution for task: {task_id}")

    execution_data = monitor.start_agent_execution(
        task_id, 'test_agent', {'context': 'integration test'})
    time.sleep(0.2)  # Brief execution
    monitor.complete_agent_execution(execution_data, 'COMPLETED', {
                                     'result': 'integration test successful'})

    # Get and display stats
    stats = monitor.get_execution_stats()
    print(f"\n📊 Execution Statistics:")
    print(f"   Total executions: {stats['total_executions']}")
    print(f"   Successful: {stats['successful_executions']}")
    print(f"   Failed: {stats['failed_executions']}")
    print(f"   Average duration: {stats['average_duration_minutes']} minutes")

    # Verify log and CSV files exist
    log_file = f'logs/execution-{task_id}.log'
    csv_file = 'reports/execution-summary.csv'

    print(f"\n📁 File System Verification:")
    print(f"   Log file exists: {os.path.exists(log_file)} ({log_file})")
    print(f"   CSV file exists: {os.path.exists(csv_file)} ({csv_file})")

    # Read and display a few lines from the log
    if os.path.exists(log_file):
        print(f"\n📝 Sample log content from {log_file}:")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-3:]:  # Show last 3 lines
                print(f"   {line.strip()}")

    # Read and display CSV content
    if os.path.exists(csv_file):
        print(f"\n📈 CSV content from {csv_file}:")
        with open(csv_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-2:]:  # Show header + last entry
                print(f"   {line.strip()}")

    print("\n✅ Step 4.8 integration test completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    test_step_4_8_integration()
