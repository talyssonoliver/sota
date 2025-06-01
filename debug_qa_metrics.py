#!/usr/bin/env python3
"""Debug script to understand QA metrics issue"""

from utils.completion_metrics import CompletionMetricsCalculator

def main():
    calc = CompletionMetricsCalculator()
    metrics = calc.calculate_all_metrics()
    
    print("=== QA METRICS DEBUG ===")
    print(f"Total tasks: {len(metrics['task_metrics'])}")
    
    qa_tasks = [t for t in metrics['task_metrics'] if t['qa_status'] is not None]
    print(f"Tasks with QA status: {len(qa_tasks)}")
    
    # Show first few tasks with QA status
    for task in qa_tasks[:5]:
        print(f"  {task['task_id']}: {task['qa_status']}")
    
    print(f"QA Pass Rate: {metrics['team_metrics']['qa_pass_rate']:.1f}%")
    
    # Let's also check what QA statuses we're seeing
    qa_statuses = {}
    for task in qa_tasks:
        status = task['qa_status']
        qa_statuses[status] = qa_statuses.get(status, 0) + 1
    
    print(f"QA Status breakdown: {qa_statuses}")

if __name__ == "__main__":
    main()
