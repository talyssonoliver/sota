#!/usr/bin/env python3
"""
Human-in-the-Loop (HITL) CLI Interface - Phase 7

Command-line interface for managing HITL checkpoints, reviews, and approvals.
Provides tools for reviewers to inspect, approve, reject, and escalate checkpoints.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.hitl_engine import HITLPolicyEngine, CheckpointStatus, RiskLevel
from orchestration.hitl_task_metadata import HITLTaskMetadataManager, HITLStatus
from dashboard.hitl_widgets import HITLDashboardManager


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('hitl_cli.log')
        ]
    )


class HITLCLIManager:
    """Main CLI manager for HITL operations."""
    
    def __init__(self):
        """Initialize HITL CLI manager."""
        self.hitl_engine = HITLPolicyEngine()
        self.metadata_manager = HITLTaskMetadataManager()
        self.dashboard_manager = HITLDashboardManager()
        self.logger = logging.getLogger("hitl.cli")

    def list_pending_checkpoints(self, task_id: Optional[str] = None,
                                reviewer: Optional[str] = None) -> List[Dict[str, Any]]:
        """List pending HITL checkpoints."""
        try:
            if task_id:
                checkpoints = self.hitl_engine.get_pending_checkpoints(task_id)
            else:
                checkpoints = self.hitl_engine.get_pending_checkpoints()
            
            # Convert checkpoint objects to dictionaries
            checkpoint_list = []
            for cp in checkpoints:
                if hasattr(cp, 'to_dict'):
                    checkpoint_dict = cp.to_dict()
                else:
                    # If it's already a dict, use it as is
                    checkpoint_dict = cp if isinstance(cp, dict) else vars(cp)
                
                checkpoint_list.append(checkpoint_dict)
            
            # Filter by reviewer if specified
            if reviewer and checkpoint_list:
                checkpoint_list = [cp for cp in checkpoint_list 
                                 if reviewer in cp.get('reviewers', [])]
            
            return checkpoint_list
            
        except Exception as e:
            self.logger.error(f"Failed to list checkpoints: {e}")
            return []
    
    def show_checkpoint_details(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Show detailed information about a checkpoint."""
        try:
            checkpoint = self.hitl_engine.get_checkpoint(checkpoint_id)
            if not checkpoint:
                self.logger.error(f"Checkpoint {checkpoint_id} not found")
                return None
            
            return {
                "checkpoint_id": checkpoint.checkpoint_id,
                "task_id": checkpoint.task_id,
                "checkpoint_type": checkpoint.checkpoint_type,
                "status": checkpoint.status.value,
                "risk_level": checkpoint.risk_level.value,
                "created_at": checkpoint.created_at.isoformat(),
                "deadline": checkpoint.deadline.isoformat() if checkpoint.deadline else None,
                "description": checkpoint.description,
                "reviewers": checkpoint.reviewers,
                "content": checkpoint.content,
                "mitigation_suggestions": checkpoint.mitigation_suggestions,
                "metadata": checkpoint.metadata
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get checkpoint details: {e}")
            return None
    
    def approve_checkpoint(self, checkpoint_id: str, reviewer: str, 
                          comments: str = "") -> bool:
        """Approve a checkpoint."""
        try:
            decision = {
                "decision": "approved",
                "reviewer": reviewer,
                "comments": comments,
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.hitl_engine.process_decision(checkpoint_id, decision)
            if result:
                self.logger.info(f"Checkpoint {checkpoint_id} approved by {reviewer}")
                return True
            else:
                self.logger.error(f"Failed to approve checkpoint {checkpoint_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to approve checkpoint: {e}")
            return False
    
    def reject_checkpoint(self, checkpoint_id: str, reviewer: str, 
                         reason: str, comments: str = "") -> bool:
        """Reject a checkpoint."""
        try:
            decision = {
                "decision": "rejected",
                "reviewer": reviewer,
                "reason": reason,
                "comments": comments,
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.hitl_engine.process_decision(checkpoint_id, decision)
            if result:
                self.logger.info(f"Checkpoint {checkpoint_id} rejected by {reviewer}")
                return True
            else:
                self.logger.error(f"Failed to reject checkpoint {checkpoint_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to reject checkpoint: {e}")
            return False
    
    def escalate_checkpoint(self, checkpoint_id: str, reviewer: str, 
                           reason: str, escalation_level: int = 1) -> bool:
        """Escalate a checkpoint."""
        try:
            escalation_data = {
                "escalated_by": reviewer,
                "reason": reason,
                "escalation_level": escalation_level,
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.hitl_engine.escalate_checkpoint(checkpoint_id, escalation_data)
            if result:
                self.logger.info(f"Checkpoint {checkpoint_id} escalated by {reviewer}")
                return True
            else:
                self.logger.error(f"Failed to escalate checkpoint {checkpoint_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to escalate checkpoint: {e}")
            return False
    def show_audit_trail(self, task_id: Optional[str] = None, 
                        checkpoint_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Show audit trail for checkpoints."""
        try:
            if checkpoint_id:
                audit_entries = self.hitl_engine.get_audit_trail(checkpoint_id=checkpoint_id)
            elif task_id:
                audit_entries = self.hitl_engine.get_audit_trail(task_id=task_id)
            else:
                audit_entries = self.hitl_engine.get_audit_trail()
            
            # Convert HITLAuditEntry objects to dictionaries for CLI compatibility
            result = []
            for entry in audit_entries:
                if hasattr(entry, 'to_dict'):
                    # HITLAuditEntry object - convert to dict
                    entry_dict = entry.to_dict()
                else:
                    # Already a dictionary
                    entry_dict = entry
                result.append(entry_dict)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get audit trail: {e}")
            return []
    
    def show_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Show HITL metrics for the specified period."""
        try:
            metrics = self.hitl_engine.get_metrics(days=days)
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            return {}
    
    def export_checkpoint_data(self, checkpoint_id: str, output_file: str) -> bool:
        """Export checkpoint data to file."""
        try:
            checkpoint_data = self.show_checkpoint_details(checkpoint_id)
            if not checkpoint_data:
                return False
            
            output_path = Path(output_file)
            with open(output_path, 'w') as f:
                if output_path.suffix.lower() == '.json':
                    json.dump(checkpoint_data, f, indent=2)
                elif output_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(checkpoint_data, f, default_flow_style=False)
                else:
                    # Default to JSON
                    json.dump(checkpoint_data, f, indent=2)
            
            self.logger.info(f"Checkpoint data exported to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export checkpoint data: {e}")
            return False


def cmd_list_checkpoints(args):
    """List pending checkpoints command."""
    cli_manager = HITLCLIManager()
    
    checkpoints = cli_manager.list_pending_checkpoints(
        task_id=args.task_id, 
        reviewer=args.reviewer
    )
    
    if not checkpoints:
        print("No pending checkpoints found.")
        return
    
    print(f"\n📋 Pending HITL Checkpoints ({len(checkpoints)})")
    print("=" * 80)
    
    for cp in checkpoints:
        risk_emoji = {
            "low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"
        }.get(cp.get('risk_level', 'low'), "⚪")
        
        deadline = cp.get('deadline', 'No deadline')
        if deadline != 'No deadline':
            deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            if deadline_dt < datetime.now():
                deadline = f"⚠️ OVERDUE: {deadline}"
        
        print(f"{risk_emoji} {cp.get('checkpoint_id', 'N/A')}")
        print(f"   Task: {cp.get('task_id', 'N/A')}")
        print(f"   Type: {cp.get('checkpoint_type', 'N/A')}")
        print(f"   Deadline: {deadline}")
        print(f"   Reviewers: {', '.join(cp.get('reviewers', []))}")
        print("")  # Empty line separator


def cmd_show_checkpoint(args):
    """Show checkpoint details command."""
    cli_manager = HITLCLIManager()
    
    details = cli_manager.show_checkpoint_details(args.checkpoint_id)
    if not details:
        print(f"❌ Checkpoint {args.checkpoint_id} not found.")
        return
    
    print(f"\n🔍 Checkpoint Details: {args.checkpoint_id}")
    print("=" * 80)
    print(f"Task ID: {details['task_id']}")
    print(f"Type: {details['checkpoint_type']}")
    print(f"Status: {details['status']}")
    print(f"Risk Level: {details['risk_level']}")
    print(f"Created: {details['created_at']}")
    print(f"Deadline: {details['deadline'] or 'No deadline'}")
    print(f"Reviewers: {', '.join(details['reviewers'])}")
    
    if details['description']:
        print(f"\nDescription:\n{details['description']}")
    
    if details['mitigation_suggestions']:
        print(f"\nMitigation Suggestions:")
        for i, suggestion in enumerate(details['mitigation_suggestions'], 1):
            print(f"  {i}. {suggestion}")
    
    if details['content']:
        print(f"\nContent:")
        if isinstance(details['content'], dict):
            print(json.dumps(details['content'], indent=2))
        else:
            print(details['content'])


def cmd_approve_checkpoint(args):
    """Approve checkpoint command."""
    cli_manager = HITLCLIManager()
    
    # Get checkpoint details first
    details = cli_manager.show_checkpoint_details(args.checkpoint_id)
    if not details:
        print(f"❌ Checkpoint {args.checkpoint_id} not found.")
        return
    
    # Show checkpoint summary
    print(f"\n🔍 Approving Checkpoint: {args.checkpoint_id}")
    print(f"Task: {details['task_id']}")
    print(f"Type: {details['checkpoint_type']}")
    print(f"Risk Level: {details['risk_level']}")
    
    # Get confirmation if not forced
    if not args.force:
        response = input("\nApprove this checkpoint? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Approval cancelled.")
            return
    
    # Process approval
    success = cli_manager.approve_checkpoint(
        args.checkpoint_id, 
        args.reviewer, 
        args.comments or ""
    )
    
    if success:
        print(f"✅ Checkpoint {args.checkpoint_id} approved by {args.reviewer}")
    else:
        print(f"❌ Failed to approve checkpoint {args.checkpoint_id}")


def cmd_reject_checkpoint(args):
    """Reject checkpoint command."""
    cli_manager = HITLCLIManager()
    
    # Get checkpoint details first
    details = cli_manager.show_checkpoint_details(args.checkpoint_id)
    if not details:
        print(f"❌ Checkpoint {args.checkpoint_id} not found.")
        return
    
    # Show checkpoint summary
    print(f"\n❌ Rejecting Checkpoint: {args.checkpoint_id}")
    print(f"Task: {details['task_id']}")
    print(f"Type: {details['checkpoint_type']}")
    print(f"Risk Level: {details['risk_level']}")
    
    # Ensure reason is provided
    if not args.reason:
        args.reason = input("Rejection reason (required): ")
        if not args.reason.strip():
            print("❌ Rejection reason is required.")
            return
    
    # Get confirmation if not forced
    if not args.force:
        response = input(f"\nReject this checkpoint with reason '{args.reason}'? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Rejection cancelled.")
            return
    
    # Process rejection
    success = cli_manager.reject_checkpoint(
        args.checkpoint_id, 
        args.reviewer, 
        args.reason,
        args.comments or ""
    )
    
    if success:
        print(f"❌ Checkpoint {args.checkpoint_id} rejected by {args.reviewer}")
    else:
        print(f"❌ Failed to reject checkpoint {args.checkpoint_id}")


def cmd_escalate_checkpoint(args):
    """Escalate checkpoint command."""
    cli_manager = HITLCLIManager()
    
    # Get checkpoint details first
    details = cli_manager.show_checkpoint_details(args.checkpoint_id)
    if not details:
        print(f"❌ Checkpoint {args.checkpoint_id} not found.")
        return
    
    # Show checkpoint summary
    print(f"\n⚠️ Escalating Checkpoint: {args.checkpoint_id}")
    print(f"Task: {details['task_id']}")
    print(f"Type: {details['checkpoint_type']}")
    print(f"Risk Level: {details['risk_level']}")
    print(f"Escalation Level: {args.level}")
    
    # Ensure reason is provided
    if not args.reason:
        args.reason = input("Escalation reason (required): ")
        if not args.reason.strip():
            print("❌ Escalation reason is required.")
            return
    
    # Get confirmation if not forced
    if not args.force:
        response = input(f"\nEscalate this checkpoint to level {args.level}? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Escalation cancelled.")
            return
    
    # Process escalation
    success = cli_manager.escalate_checkpoint(
        args.checkpoint_id, 
        args.reviewer, 
        args.reason,
        args.level
    )
    
    if success:
        print(f"⚠️ Checkpoint {args.checkpoint_id} escalated to level {args.level}")
    else:
        print(f"❌ Failed to escalate checkpoint {args.checkpoint_id}")


def cmd_audit_trail(args):
    """Show audit trail command."""
    cli_manager = HITLCLIManager()
    
    audit_entries = cli_manager.show_audit_trail(
        task_id=args.task_id,
        checkpoint_id=args.checkpoint_id
    )
    
    if not audit_entries:
        print("No audit trail entries found.")
        return
    
    print(f"\n📜 HITL Audit Trail ({len(audit_entries)} entries)")
    print("=" * 80)
    
    for entry in audit_entries:
        action_emoji = {
            "created": "🆕", "approved": "✅", "rejected": "❌",
            "escalated": "⚠️", "timeout": "⏰", "updated": "📝"
        }.get(entry.get('action', 'unknown'), "📝")
        
        print(f"{action_emoji} {entry.get('timestamp', 'N/A')}")
        print(f"   Action: {entry.get('action', 'N/A')}")
        print(f"   User: {entry.get('user', 'N/A')}")
        if entry.get('checkpoint_id'):
            print(f"   Checkpoint: {entry['checkpoint_id']}")
        if entry.get('task_id'):
            print(f"   Task: {entry['task_id']}")
        if entry.get('details'):
            print(f"   Details: {entry['details']}")
        print()


def cmd_metrics(args):
    """Show HITL metrics command."""
    cli_manager = HITLCLIManager()
    
    metrics = cli_manager.show_metrics(days=args.days)
    if not metrics:
        print("❌ Failed to retrieve metrics.")
        return
    
    print(f"\n📊 HITL Metrics (Last {args.days} days)")
    print("=" * 50)
    
    # Overall statistics
    if 'checkpoints' in metrics:
        cp_metrics = metrics['checkpoints']
        print(f"📋 Checkpoints:")
        print(f"   Total Created: {cp_metrics.get('total_created', 0)}")
        print(f"   Approved: {cp_metrics.get('approved', 0)}")
        print(f"   Rejected: {cp_metrics.get('rejected', 0)}")
        print(f"   Escalated: {cp_metrics.get('escalated', 0)}")
        print(f"   Pending: {cp_metrics.get('pending', 0)}")
        print()
    
    # Response times
    if 'response_times' in metrics:
        rt_metrics = metrics['response_times']
        print(f"⏱️ Response Times:")
        print(f"   Average: {rt_metrics.get('average_hours', 0):.1f} hours")
        print(f"   Median: {rt_metrics.get('median_hours', 0):.1f} hours")
        print(f"   SLA Breaches: {rt_metrics.get('sla_breaches', 0)}")
        print()
    
    # Risk distribution
    if 'risk_distribution' in metrics:
        risk_dist = metrics['risk_distribution']
        print(f"🎯 Risk Distribution:")
        for risk_level, count in risk_dist.items():
            emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(risk_level, "⚪")
            print(f"   {emoji} {risk_level.capitalize()}: {count}")
        print()


def cmd_export_checkpoint(args):
    """Export checkpoint data command."""
    cli_manager = HITLCLIManager()
    
    success = cli_manager.export_checkpoint_data(args.checkpoint_id, args.output)
    if success:
        print(f"✅ Checkpoint data exported to {args.output}")
    else:
        print(f"❌ Failed to export checkpoint data")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Human-in-the-Loop (HITL) CLI Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/hitl_cli.py list                        # List all pending checkpoints
  python cli/hitl_cli.py list --task-id BE-07       # List checkpoints for specific task
  python cli/hitl_cli.py show hitl_BE-07_abc123     # Show checkpoint details
  python cli/hitl_cli.py approve hitl_BE-07_abc123 --reviewer alice  # Approve checkpoint
  python cli/hitl_cli.py reject hitl_BE-07_abc123 --reviewer bob --reason "needs-fixes"
  python cli/hitl_cli.py metrics --days 7           # Show 7-day metrics
  python cli/hitl_cli.py audit-trail --task-id BE-07  # Show audit trail for task
        """
    )
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest='command', help='HITL commands')
    
    # List checkpoints command
    list_parser = subparsers.add_parser('list', help='List pending checkpoints')
    list_parser.add_argument('--task-id', help='Filter by task ID')
    list_parser.add_argument('--reviewer', help='Filter by reviewer')
    list_parser.set_defaults(func=cmd_list_checkpoints)
    
    # Show checkpoint command
    show_parser = subparsers.add_parser('show', help='Show checkpoint details')
    show_parser.add_argument('checkpoint_id', help='Checkpoint ID')
    show_parser.set_defaults(func=cmd_show_checkpoint)
    
    # Approve checkpoint command
    approve_parser = subparsers.add_parser('approve', help='Approve a checkpoint')
    approve_parser.add_argument('checkpoint_id', help='Checkpoint ID')
    approve_parser.add_argument('--reviewer', required=True, help='Reviewer name')
    approve_parser.add_argument('--comments', help='Approval comments')
    approve_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    approve_parser.set_defaults(func=cmd_approve_checkpoint)
    
    # Reject checkpoint command
    reject_parser = subparsers.add_parser('reject', help='Reject a checkpoint')
    reject_parser.add_argument('checkpoint_id', help='Checkpoint ID')
    reject_parser.add_argument('--reviewer', required=True, help='Reviewer name')
    reject_parser.add_argument('--reason', required=True, help='Rejection reason')
    reject_parser.add_argument('--comments', help='Additional comments')
    reject_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    reject_parser.set_defaults(func=cmd_reject_checkpoint)
    
    # Escalate checkpoint command
    escalate_parser = subparsers.add_parser('escalate', help='Escalate a checkpoint')
    escalate_parser.add_argument('checkpoint_id', help='Checkpoint ID')
    escalate_parser.add_argument('--reviewer', required=True, help='Reviewer name')
    escalate_parser.add_argument('--reason', required=True, help='Escalation reason')
    escalate_parser.add_argument('--level', type=int, default=1, help='Escalation level')
    escalate_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    escalate_parser.set_defaults(func=cmd_escalate_checkpoint)
    
    # Audit trail command
    audit_parser = subparsers.add_parser('audit-trail', help='Show audit trail')
    audit_parser.add_argument('--task-id', help='Filter by task ID')
    audit_parser.add_argument('--checkpoint-id', help='Filter by checkpoint ID')
    audit_parser.set_defaults(func=cmd_audit_trail)
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Show HITL metrics')
    metrics_parser.add_argument('--days', type=int, default=30, help='Days to include')
    metrics_parser.set_defaults(func=cmd_metrics)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export checkpoint data')
    export_parser.add_argument('checkpoint_id', help='Checkpoint ID')
    export_parser.add_argument('--output', required=True, help='Output file path')
    export_parser.set_defaults(func=cmd_export_checkpoint)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Run command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
