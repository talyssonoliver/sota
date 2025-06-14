"""
CLI Interface for Automated Escalation System
Provides command-line access to escalation functionality and management.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add parent directory to path for imports
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.escalation_system import (
    EscalationEngine, 
    EscalationLevel,
    EscalationEvent
)


class EscalationCLI:
    """Command-line interface for escalation system"""
    
    def __init__(self):
        self.engine = EscalationEngine()
    
    def list_active_escalations(self) -> Dict[str, Any]:
        """List currently active escalations"""
        try:
            active_escalations = self.engine.get_active_escalations()
            
            if not active_escalations:
                print("✅ No active escalations")
                return {"escalations": []}
            
            print(f"🚨 Active Escalations ({len(active_escalations)})")
            print("=" * 60)
            
            for escalation in active_escalations:
                print(f"Task: {escalation['task_id']}")
                print(f"Level: {escalation['level']}")
                print(f"Trigger: {escalation['trigger']}")
                print(f"Started: {escalation['triggered_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Context: {json.dumps(escalation['context'], indent=2)}")
                print("-" * 40)
            
            return {"escalations": active_escalations}
            
        except Exception as e:
            print(f"❌ Error listing escalations: {e}")
            return {"escalations": [], "error": str(e)}
    
    def get_escalation_status(self, task_id: str) -> Dict[str, Any]:
        """Get escalation status for a specific task"""
        try:
            events = self.engine.tracker.get_events_for_task(task_id)
            
            if not events:
                print(f"ℹ️  No escalations found for task {task_id}")
                return {"task_id": task_id, "escalations": []}
            
            print(f"📊 Escalation Status for {task_id}")
            print("=" * 50)
            
            for event in events:
                status = "RESOLVED" if event.resolved_at else "ACTIVE"
                print(f"Status: {status}")
                print(f"Level: {event.level.value['name']}")
                print(f"Trigger: {event.trigger}")
                print(f"Triggered: {event.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}")
                if event.resolved_at:
                    print(f"Resolved: {event.resolved_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Resolution: {event.resolution}")
                print(f"Context: {json.dumps(event.context, indent=2)}")
                print("-" * 30)
            
            return {
                "task_id": task_id,
                "escalations": [event.to_dict() for event in events]
            }
            
        except Exception as e:
            print(f"❌ Error getting escalation status: {e}")
            return {"task_id": task_id, "escalations": [], "error": str(e)}
    
    def trigger_manual_escalation(self, task_id: str, reason: str, level: str) -> Dict[str, Any]:
        """Trigger manual escalation for a task"""
        try:
            # Map level string to EscalationLevel
            level_mapping = {
                "level_1": EscalationLevel.LEVEL_1,
                "level_2": EscalationLevel.LEVEL_2,
                "level_3": EscalationLevel.LEVEL_3,
                "level_4": EscalationLevel.LEVEL_4
            }
            
            if level not in level_mapping:
                raise ValueError(f"Invalid escalation level: {level}")
            
            escalation_level = level_mapping[level]
            
            # Create manual escalation event
            event = EscalationEvent(
                task_id=task_id,
                trigger="manual",
                level=escalation_level,
                triggered_at=datetime.now(),
                triggered_by="cli_user",
                context={
                    "reason": reason,
                    "manual_trigger": True,
                    "cli_initiated": True
                }
            )
            
            # Send notifications
            notification_result = self.engine.notifier.send_notification(
                event, escalation_level.recipients, escalation_level.notification_channels
            )
            
            # Track event
            self.engine.tracker.track_event(event)
            print(f"✅ Manual escalation triggered for {task_id}")
            print(f"Level: {escalation_level.config['name']}")
            print(f"Reason: {reason}")
            print(f"Notifications sent: {notification_result['channels_used']}")
            
            return {
                "success": True,
                "task_id": task_id,
                "level": level,
                "event_id": f"{task_id}_{int(event.triggered_at.timestamp())}",
                "notification_result": notification_result
            }
            
        except Exception as e:
            print(f"❌ Error triggering manual escalation: {e}")
            return {"success": False, "task_id": task_id, "error": str(e)}
    
    def show_escalation_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Show escalation metrics and analytics"""
        try:
            metrics = self.engine.get_escalation_metrics(days)
            
            print(f"📈 Escalation Metrics (Last {days} days)")
            print("=" * 50)
            
            print(f"Total Escalations: {metrics['total_escalations']}")
            print(f"Timeout Escalations: {metrics['timeout_escalations']}")
            print(f"Rejection Escalations: {metrics['rejection_escalations']}")
            print()
            
            print("Escalations by Level:")
            print(f"  Level 1: {metrics['level_1_escalations']}")
            print(f"  Level 2: {metrics['level_2_escalations']}")
            print(f"  Level 3: {metrics['level_3_escalations']}")
            print(f"  Level 4: {metrics['level_4_escalations']}")
            print()
            
            if metrics['avg_resolution_time']:
                print(f"Average Resolution Time: {metrics['avg_resolution_time']:.2f} hours")
            else:
                print("Average Resolution Time: No resolved escalations")
            print()
            
            if metrics['escalations_by_task_type']:
                print("Escalations by Task Type:")
                for task_type, count in metrics['escalations_by_task_type'].items():
                    print(f"  {task_type.upper()}: {count}")
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error showing escalation metrics: {e}")
            return {"error": str(e)}
    
    def check_pending_reviews(self) -> Dict[str, Any]:
        """Check pending reviews for escalation conditions"""
        try:
            escalations = self.engine.check_pending_reviews_for_escalation()
            
            if not escalations:
                print("✅ No pending reviews require escalation")
                return {"pending_escalations": []}
            
            print(f"⚠️  Found {len(escalations)} reviews requiring escalation")
            print("=" * 60)
            
            for escalation in escalations:
                print(f"Task: {escalation['task_id']}")
                print(f"Timeout Duration: {escalation['timeout_duration']:.2f} hours")
                print(f"Reviewer: {escalation['reviewer']}")
                print("-" * 40)
            
            return {"pending_escalations": escalations}
            
        except Exception as e:
            print(f"❌ Error checking pending reviews: {e}")
            return {"pending_escalations": [], "error": str(e)}
    
    def resolve_escalation(self, task_id: str, resolution: str) -> Dict[str, Any]:
        """Mark an escalation as resolved"""
        try:
            events = self.engine.tracker.get_events_for_task(task_id)
            unresolved_events = [e for e in events if not e.resolved_at]
            
            if not unresolved_events:
                print(f"ℹ️  No active escalations found for task {task_id}")
                return {"success": False, "reason": "no_active_escalations"}
            
            # Resolve the most recent escalation
            latest_event = max(unresolved_events, key=lambda e: e.triggered_at)
            latest_event.resolved_at = datetime.now()
            latest_event.resolution = resolution
            
            # Save updated events
            self.engine.tracker._save_events()
            
            print(f"✅ Escalation resolved for {task_id}")
            print(f"Resolution: {resolution}")
            print(f"Resolved at: {latest_event.resolved_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return {
                "success": True,
                "task_id": task_id,
                "resolution": resolution,
                "resolved_at": latest_event.resolved_at.isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error resolving escalation: {e}")
            return {"success": False, "task_id": task_id, "error": str(e)}


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Escalation System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List active escalations
    list_parser = subparsers.add_parser("list", help="List active escalations")
    
    # Get escalation status
    status_parser = subparsers.add_parser("status", help="Get escalation status for a task")
    status_parser.add_argument("task_id", help="Task ID to check")
    
    # Trigger manual escalation
    trigger_parser = subparsers.add_parser("trigger", help="Trigger manual escalation")
    trigger_parser.add_argument("task_id", help="Task ID to escalate")
    trigger_parser.add_argument("reason", help="Reason for escalation")
    trigger_parser.add_argument("--level", choices=["level_1", "level_2", "level_3", "level_4"],
                               default="level_1", help="Escalation level")
    
    # Show metrics
    metrics_parser = subparsers.add_parser("metrics", help="Show escalation metrics")
    metrics_parser.add_argument("--days", type=int, default=7, help="Number of days to analyze")
    
    # Check pending reviews
    check_parser = subparsers.add_parser("check", help="Check pending reviews for escalation")
    
    # Resolve escalation
    resolve_parser = subparsers.add_parser("resolve", help="Resolve an escalation")
    resolve_parser.add_argument("task_id", help="Task ID to resolve")
    resolve_parser.add_argument("resolution", help="Resolution description")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = EscalationCLI()
    
    try:
        if args.command == "list":
            cli.list_active_escalations()
        elif args.command == "status":
            cli.get_escalation_status(args.task_id)
        elif args.command == "trigger":
            cli.trigger_manual_escalation(args.task_id, args.reason, args.level)
        elif args.command == "metrics":
            cli.show_escalation_metrics(args.days)
        elif args.command == "check":
            cli.check_pending_reviews()
        elif args.command == "resolve":
            cli.resolve_escalation(args.task_id, args.resolution)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


# Direct function exports for testing
def list_active_escalations() -> Dict[str, Any]:
    """List active escalations (for testing)"""
    cli = EscalationCLI()
    return cli.list_active_escalations()


def get_escalation_status(task_id: str) -> Dict[str, Any]:
    """Get escalation status (for testing)"""
    cli = EscalationCLI()
    return cli.get_escalation_status(task_id)


def trigger_manual_escalation(task_id: str, reason: str, level: str) -> Dict[str, Any]:
    """Trigger manual escalation (for testing)"""
    cli = EscalationCLI()
    return cli.trigger_manual_escalation(task_id, reason, level)


if __name__ == "__main__":
    main()
