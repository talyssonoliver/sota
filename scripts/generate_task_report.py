#!/usr/bin/env python3
"""
Task Report Generation Script for Phase 5

Unified script for generating task reports, updating dashboards, and creating progress summaries.
This script aligns with the Phase 5 specification in system_implementation.txt.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.update_dashboard import DashboardUpdater
from scripts.generate_progress_report import ProgressReportGenerator


def update_dashboard(task_id: Optional[str] = None) -> bool:
    """Update dashboard with latest completion metrics"""
    print("🔄 Updating dashboard...")
    
    updater = DashboardUpdater()
    result = updater.update_completion_dashboard(task_id)
    
    if result:
        print("✅ Dashboard updated successfully")
        print("   📊 Completion metrics refreshed")
        print("   📈 QA coverage trends updated") 
        if task_id:
            print(f"   ✅ {task_id} marked green")
    else:
        print("❌ Dashboard update failed")
    
    return result


def generate_daily_report(day: int) -> bool:
    """Generate daily progress report"""
    print(f"📋 Generating daily report for day {day}...")
    
    generator = ProgressReportGenerator()
    
    # Calculate target date based on day number
    from datetime import date, timedelta
    start_date = date(2025, 4, 1)  # Project start date
    target_date = start_date + timedelta(days=day - 1)
    
    try:
        # Generate daily report
        report_content = generator.generate_daily_report(target_date.strftime('%Y-%m-%d'))
        
        # Save to progress_reports directory
        reports_dir = Path("progress_reports")
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"day{day}_report_{target_date.strftime('%Y-%m-%d')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Daily report generated: {report_file}")
        print("   📊 Summary of completed tasks")
        print("   🧪 QA metrics included")
        print("   ⚠️ Blockers and plan adjustments identified")
        
        return True
        
    except Exception as e:
        print(f"❌ Daily report generation failed: {e}")
        return False


def generate_task_specific_report(task_id: str) -> bool:
    """Generate report for specific task"""
    print(f"📋 Generating report for task {task_id}...")
    
    generator = ProgressReportGenerator()
    
    try:
        # Generate task-specific report
        report_content = generator.generate_task_report(task_id)
        
        # Save to progress_reports directory
        reports_dir = Path("progress_reports")
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = reports_dir / f"task_{task_id}_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Task report generated: {report_file}")
        return True
        
    except Exception as e:
        print(f"❌ Task report generation failed: {e}")
        return False


def main():
    """Main CLI interface matching system_implementation.txt specification"""
    parser = argparse.ArgumentParser(
        description="Generate task reports and update dashboard (Phase 5)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update dashboard after task completion
  python scripts/generate_task_report.py --update-dashboard
  
  # Update dashboard for specific task
  python scripts/generate_task_report.py --update-dashboard --task BE-07
  
  # Generate daily report for day 2
  python scripts/generate_task_report.py --day 2
  
  # Generate report for specific task
  python scripts/generate_task_report.py --task BE-07
        """
    )
    
    parser.add_argument(
        '--update-dashboard',
        action='store_true',
        help='Update dashboard with completion metrics and QA trends'
    )
    
    parser.add_argument(
        '--day',
        type=int,
        help='Generate daily progress report for specified day number'
    )
    
    parser.add_argument(
        '--task',
        type=str,
        help='Task ID for task-specific operations'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.update_dashboard, args.day, args.task]):
        parser.error("Must specify one of: --update-dashboard, --day, or --task")
    
    success = True
    
    # Execute requested operations
    if args.update_dashboard:
        success &= update_dashboard(args.task)
    
    if args.day:
        success &= generate_daily_report(args.day)
    
    if args.task and not args.update_dashboard:
        success &= generate_task_specific_report(args.task)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
