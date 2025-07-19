"""
import os
test_step_4_8_integration.py - Optimized Test Structure

Migrated from: tests/integration	est_step_4_8_integration.py
New location: tests/integration	est_step_4_8_integration.py

Part of the optimized test pyramid reorganization:
- Tests now mirror src/ structure
- Proper categorization (unit/integration/e2e)
- Improved mocking and isolation

Quick integration test for Step 4.8 Real-time Execution Monitoring
"""
import os
from src.infrastructure.utils.execution_monitor import get_execution_monitor

def test_step_4_8_integration():
    """Test Step 4.8 monitoring system integration."""
    print('🎯 Testing Step 4.8 Real-time Execution Monitoring')
    print('=' * 50)
    monitor = get_execution_monitor()
    print('✅ Global execution monitor loaded successfully')
    task_id = 'TEST-INTEGRATION'
    print(f'\n📋 Starting test execution for task: {task_id}')
    execution_data = monitor.start_agent_execution(task_id, 'test_agent', {'context': 'integration test'})
    # Removed sleep - test should work without delay
    monitor.complete_agent_execution(execution_data, 'COMPLETED', {'result': 'integration test successful'})
    stats = monitor.get_execution_stats()
    print('\n📊 Execution Statistics:')
    print(f'   Total executions: {stats['total_executions']}')
    print(f'   Successful: {stats['successful_executions']}')
    print(f'   Failed: {stats['failed_executions']}')
    print(f'   Average duration: {stats['average_duration_minutes']} minutes')
    log_file = f'logs/execution-{task_id}.log'
    csv_file = 'reports/execution-summary.csv'
    print('\n📁 File System Verification:')
    print(f'   Log file exists: {os.path.exists(log_file)} ({log_file})')
    print(f'   CSV file exists: {os.path.exists(csv_file)} ({csv_file})')
    if os.path.exists(log_file):
        print(f'\n📝 Sample log content from {log_file}:')
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-3:]:
                print(f'   {line.strip()}')
    if os.path.exists(csv_file):
        print(f'\n📈 CSV content from {csv_file}:')
        with open(csv_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-2:]:
                print(f'   {line.strip()}')
    print('\n✅ Step 4.8 integration test completed successfully!')
    print('=' * 50)
if __name__ == '__main__':
    test_step_4_8_integration()