#!/usr/bin/env python3
"""
Batch QA Report Generation Script

Generates QA reports for all completed tasks that don't have QA reports yet.
This addresses the critical issue where only 1/105 tasks have QA reports.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from orchestration.qa_validation import QAValidationEngine
from utils.completion_metrics import CompletionMetricsCalculator


def find_tasks_needing_qa() -> List[str]:
    """Find all tasks that are completed but lack QA reports."""
    print("🔍 Scanning for tasks needing QA reports...")
    
    outputs_dir = Path("outputs")
    tasks_needing_qa = []
    
    for task_dir in outputs_dir.iterdir():
        if not task_dir.is_dir():
            continue
            
        task_id = task_dir.name
        qa_report_file = task_dir / "qa_report.json"
        task_dir / "status.json"
        
        # Check if task is completed and lacks QA report
        has_completion_artifacts = any([
            (task_dir / "completion_report.md").exists(),
            (task_dir / "status.json").exists(),
            (task_dir / "output_backend.md").exists(),
            (task_dir / "output_qa.md").exists(),
        ])
        
        if has_completion_artifacts and not qa_report_file.exists():
            tasks_needing_qa.append(task_id)
            print(f"  📋 {task_id}: Needs QA report")
    
    print(f"Found {len(tasks_needing_qa)} tasks needing QA reports")
    return tasks_needing_qa


def generate_qa_report_for_task(task_id: str, qa_engine: QAValidationEngine) -> bool:
    """Generate QA report for a single task."""
    try:
        print(f"  🔧 Generating QA report for {task_id}...")
        
        # Run QA validation
        qa_result = qa_engine.validate_task(task_id)
        
        print(f"    ✅ QA completed: {qa_result.overall_status}")
        print(f"    📊 Coverage: {qa_result.coverage_percentage:.1f}%")
        print(f"    🧪 Tests: {qa_result.tests_passed} passed, {qa_result.tests_failed} failed")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Failed to generate QA report for {task_id}: {e}")
        return False


def batch_generate_qa_reports(max_tasks: int = None) -> Dict[str, Any]:
    """Generate QA reports for all tasks needing them."""
    print("🚀 Starting batch QA report generation...")
    
    # Initialize QA engine
    qa_engine = QAValidationEngine()
    
    # Find tasks needing QA
    tasks_needing_qa = find_tasks_needing_qa()
    
    if max_tasks:
        tasks_needing_qa = tasks_needing_qa[:max_tasks]
        print(f"🎯 Processing first {max_tasks} tasks (limited run)")
    
    # Generate reports
    results = {
        "total_tasks": len(tasks_needing_qa),
        "successful": 0,
        "failed": 0,
        "success_tasks": [],
        "failed_tasks": []
    }
    
    for i, task_id in enumerate(tasks_needing_qa, 1):
        print(f"\n📝 Processing {task_id} ({i}/{len(tasks_needing_qa)})")
        
        success = generate_qa_report_for_task(task_id, qa_engine)
        
        if success:
            results["successful"] += 1
            results["success_tasks"].append(task_id)
        else:
            results["failed"] += 1
            results["failed_tasks"].append(task_id)
    
    return results


def update_dashboard_after_qa_generation():
    """Update dashboard metrics after QA generation."""
    print("\n📊 Updating dashboard metrics...")
    
    try:
        calc = CompletionMetricsCalculator()
        metrics = calc.calculate_all_metrics()
        calc.save_metrics_to_dashboard(metrics)
        
        # Display updated metrics
        team_metrics = metrics["team_metrics"]
        qa_pass_rate = team_metrics["qa_pass_rate"]
        qa_tasks = [t for t in metrics["task_metrics"] if t["qa_status"] is not None]
        
        print("  ✅ Dashboard updated")
        print(f"  📈 QA Pass Rate: {qa_pass_rate:.1f}%")
        print(f"  🧪 Tasks with QA: {len(qa_tasks)}/{len(metrics['task_metrics'])}")
        
    except Exception as e:
        print(f"  ❌ Failed to update dashboard: {e}")


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch generate QA reports")
    parser.add_argument("--max-tasks", type=int, help="Maximum tasks to process (for testing)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN: Showing tasks that would get QA reports")
        tasks = find_tasks_needing_qa()
        if args.max_tasks:
            tasks = tasks[:args.max_tasks]
        for task in tasks:
            print(f"  Would generate QA for: {task}")
        return
    
    # Run batch generation
    results = batch_generate_qa_reports(args.max_tasks)
    
    # Display results
    print("\n🎉 Batch QA generation complete!")
    print(f"  ✅ Successful: {results['successful']}")
    print(f"  ❌ Failed: {results['failed']}")
    print(f"  📊 Success rate: {results['successful']/results['total_tasks']*100:.1f}%")
    
    if results["failed_tasks"]:
        print(f"\n❌ Failed tasks: {', '.join(results['failed_tasks'])}")
    
    # Update dashboard
    update_dashboard_after_qa_generation()
    
    print("\n✨ QA automation complete! Check dashboard for updated metrics.")


if __name__ == "__main__":
    main()
