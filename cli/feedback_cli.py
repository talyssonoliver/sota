"""
CLI interface for the Feedback System
Provides command-line access to feedback operations.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.feedback_system import get_feedback_system, FeedbackCategory
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeedbackCLI:
    """Command-line interface for feedback system"""
    
    def __init__(self):
        """Initialize CLI"""
        self.system = get_feedback_system()
    
    def get_summary(self, task_id: str) -> Dict[str, Any]:
        """Get feedback summary for a task"""
        try:
            summary = self.system.get_feedback_summary(task_id)
            self._print_summary(summary)
            return summary
        except Exception as e:
            logger.error(f"Error getting summary: {str(e)}")
            return None
    
    def generate_report(self, period: str = "7d") -> Dict[str, Any]:
        """Generate analytics report"""
        try:
            report = self.system.generate_analytics_report(period)
            self._print_report(report)
            return report
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return None
    
    def export_data(self, format: str, output_path: str, period: str = "30d") -> bool:
        """Export feedback data"""
        try:
            result = self.system.export_feedback_data(format, output_path, period)
            if result:
                print(f"✅ Data exported to {output_path}")
            else:
                print(f"❌ Failed to export data")
            return result
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            return False
    
    def capture_feedback_interactive(self, task_id: str, reviewer: str) -> str:
        """Interactive feedback capture"""
        print(f"\n📝 Capturing feedback for task: {task_id}")
        print(f"👤 Reviewer: {reviewer}")
        print("=" * 50)
        
        feedback_data = {}
        
        # Approval decision
        while True:
            approval = input("✅ Approve this task? (y/n): ").lower().strip()
            if approval in ['y', 'yes']:
                feedback_data["approved"] = True
                break
            elif approval in ['n', 'no']:
                feedback_data["approved"] = False
                break
            else:
                print("Please enter 'y' for yes or 'n' for no")
        
        print("\n📊 Category Feedback (1-10 scale):")
        
        # Category scores
        for category in FeedbackCategory.get_all_categories():
            category_info = FeedbackCategory.get_category_info(category)
            print(f"\n{category_info['name']}: {category_info['description']}")
            
            while True:
                try:
                    score_input = input(f"Score (1-10) or 'skip': ").strip()
                    if score_input.lower() == 'skip':
                        break
                    
                    score = float(score_input)
                    if FeedbackCategory.is_valid_score(score):
                        comments = input("Comments (optional): ").strip()
                        
                        feedback_data[category] = {
                            "score": score,
                            "comments": comments if comments else ""
                        }
                        break
                    else:
                        print("Score must be between 1 and 10")
                        
                except ValueError:
                    print("Please enter a valid number or 'skip'")
        
        # General comments
        print("\n💬 General Comments:")
        comments = []
        while True:
            comment = input("Add comment (or 'done' to finish): ").strip()
            if comment.lower() == 'done':
                break
            if comment:
                comments.append(comment)
        
        feedback_data["comments"] = comments
        
        # Improvements
        print("\n🔧 Suggested Improvements:")
        improvements = []
        while True:
            improvement = input("Add improvement (or 'done' to finish): ").strip()
            if improvement.lower() == 'done':
                break
            if improvement:
                improvements.append(improvement)
        
        feedback_data["improvements"] = improvements
        
        # Risk level
        print("\n⚠️ Risk Level:")
        print("1. low")
        print("2. medium") 
        print("3. high")
        
        while True:
            risk_choice = input("Select risk level (1-3): ").strip()
            if risk_choice == '1':
                feedback_data["risk_level"] = "low"
                break
            elif risk_choice == '2':
                feedback_data["risk_level"] = "medium"
                break
            elif risk_choice == '3':
                feedback_data["risk_level"] = "high"
                break
            else:
                print("Please enter 1, 2, or 3")
        
        # Capture feedback
        try:
            feedback_id = self.system.capture_feedback(task_id, reviewer, feedback_data)
            print(f"\n✅ Feedback captured successfully!")
            print(f"📝 Feedback ID: {feedback_id}")
            return feedback_id
        except Exception as e:
            print(f"❌ Error capturing feedback: {str(e)}")
            return None
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print feedback summary"""
        print(f"\n📊 Feedback Summary for Task: {summary['task_id']}")
        print("=" * 50)
        print(f"Total Feedback: {summary['total_feedback_count']}")
        print(f"Approval Rate: {summary['approval_rate']:.1f}%")
        
        if summary.get('category_averages'):
            print("\n📈 Category Averages:")
            for category, average in summary['category_averages'].items():
                category_info = FeedbackCategory.get_category_info(category)
                if category_info:
                    print(f"  {category_info['name']}: {average:.1f}/10")
        
        if summary.get('recent_feedback'):
            print("\n📝 Recent Feedback:")
            for feedback in summary['recent_feedback']:
                status = "✅" if feedback['approved'] else "❌"
                score = f"{feedback['overall_score']:.1f}" if feedback['overall_score'] else "N/A"
                print(f"  {status} {feedback['reviewer']} - Score: {score}/10")
    
    def _print_report(self, report: Dict[str, Any]):
        """Print analytics report"""
        print(f"\n📈 Analytics Report - {report['period']}")
        print("=" * 50)
        print(f"Total Feedback: {report['total_feedback']}")
        print(f"Approval Rate: {report['approval_rate']:.1f}%")
        
        if report.get('category_averages'):
            print("\n📊 Category Averages:")
            for category, average in report['category_averages'].items():
                category_info = FeedbackCategory.get_category_info(category)
                if category_info:
                    print(f"  {category_info['name']}: {average:.1f}/10")
        
        if report.get('insights') and report['insights'].get('recommendations'):
            print("\n💡 Recommendations:")
            for rec in report['insights']['recommendations']:
                print(f"  • {rec}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Feedback System CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Get feedback summary for a task')
    summary_parser.add_argument('task_id', help='Task ID to get summary for')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate analytics report')
    report_parser.add_argument('--period', default='7d', help='Time period (e.g., 7d, 30d)')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export feedback data')
    export_parser.add_argument('format', choices=['json', 'csv', 'summary'], help='Export format')
    export_parser.add_argument('output_path', help='Output file path')
    export_parser.add_argument('--period', default='30d', help='Time period (e.g., 7d, 30d)')
    
    # Capture command
    capture_parser = subparsers.add_parser('capture', help='Capture feedback interactively')
    capture_parser.add_argument('task_id', help='Task ID to capture feedback for')
    capture_parser.add_argument('reviewer', help='Reviewer name/ID')
    
    # List categories command
    subparsers.add_parser('categories', help='List available feedback categories')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = FeedbackCLI()
    
    try:
        if args.command == 'summary':
            cli.get_summary(args.task_id)
        
        elif args.command == 'report':
            cli.generate_report(args.period)
        
        elif args.command == 'export':
            cli.export_data(args.format, args.output_path, args.period)
        
        elif args.command == 'capture':
            cli.capture_feedback_interactive(args.task_id, args.reviewer)
        
        elif args.command == 'categories':
            print("\n📋 Available Feedback Categories:")
            print("=" * 50)
            for category in FeedbackCategory.get_all_categories():
                category_info = FeedbackCategory.get_category_info(category)
                print(f"{category_info['name']}: {category_info['description']}")
                print(f"  Weight: {category_info['weight']}")
                print()
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
