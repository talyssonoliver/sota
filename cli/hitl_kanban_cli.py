#!/usr/bin/env python3
"""
HITL Kanban CLI - Quick Command Line Interface for HITL Dashboard

Provides quick CLI access to the HITL Kanban board with various display
options and export capabilities.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from dashboard.hitl_kanban_board import HITLKanbanBoard
from dashboard.hitl_widgets import HITLDashboardManager, get_hitl_kanban_data, process_hitl_action
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="HITL Kanban CLI - Human-in-the-Loop Review Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show current Kanban board
  python cli/hitl_kanban_cli.py

  # Show board with completed items
  python cli/hitl_kanban_cli.py --show-completed

  # Watch mode (auto-refresh)
  python cli/hitl_kanban_cli.py --watch

  # Export board data
  python cli/hitl_kanban_cli.py --export board.json

  # Quick status summary
  python cli/hitl_kanban_cli.py --summary

  # Process an approval action
  python cli/hitl_kanban_cli.py --approve checkpoint-123 --reviewer "alice" --comments "LGTM"

  # Show specific task
  python cli/hitl_kanban_cli.py --task BE-07

  # Filter by status
  python cli/hitl_kanban_cli.py --status "Awaiting QA"

  # Show overdue items only
  python cli/hitl_kanban_cli.py --overdue-only
        """
    )
    
    # Display options
    parser.add_argument(
        "--show-completed",
        action="store_true",
        help="Include recently completed items in the display"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show only summary statistics"
    )
    
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Enable watch mode with auto-refresh"
    )
    
    parser.add_argument(
        "--refresh-interval",
        type=int,
        default=30,
        help="Refresh interval in seconds for watch mode (default: 30)"
    )
    
    # Filtering options
    parser.add_argument(
        "--task",
        type=str,
        help="Filter by specific task ID (e.g., BE-07)"
    )
    
    parser.add_argument(
        "--status",
        type=str,
        choices=["Awaiting QA", "Awaiting Human", "In Review", "Escalated", "Approved", "Rejected"],
        help="Filter by specific status"
    )
    
    parser.add_argument(
        "--reviewer",
        type=str,
        help="Filter by assigned reviewer"
    )
    
    parser.add_argument(
        "--overdue-only",
        action="store_true",
        help="Show only overdue items"
    )
    
    parser.add_argument(
        "--high-priority-only",
        action="store_true",
        help="Show only high priority items"
    )
    
    # Export options
    parser.add_argument(
        "--export",
        type=str,
        help="Export board data to JSON file"
    )
    
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)"
    )
    
    # Action options
    parser.add_argument(
        "--approve",
        type=str,
        help="Approve a checkpoint by ID"
    )
    
    parser.add_argument(
        "--reject",
        type=str,
        help="Reject a checkpoint by ID"
    )
    
    parser.add_argument(
        "--escalate",
        type=str,
        help="Escalate a checkpoint by ID"
    )
    
    parser.add_argument(
        "--reviewer-name",
        type=str,
        default="cli_user",
        help="Reviewer name for actions (default: cli_user)"
    )
    
    parser.add_argument(
        "--comments",
        type=str,
        default="",
        help="Comments for approval actions"
    )
    
    # Additional options
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    args = parser.parse_args()
    
    # Create console
    console = Console(no_color=args.no_color)
    
    try:
        # Handle actions first
        if args.approve:
            return handle_approval_action(args.approve, "approve", args.reviewer_name, args.comments, console)
        elif args.reject:
            return handle_approval_action(args.reject, "reject", args.reviewer_name, args.comments, console)
        elif args.escalate:
            return handle_approval_action(args.escalate, "escalate", args.reviewer_name, args.comments, console)
        
        # Create board instance
        board = HITLKanbanBoard()
        
        # Handle export
        if args.export:
            board.export_board_data(args.export)
            return 0
        
        # Handle watch mode
        if args.watch:
            board.watch_mode(args.refresh_interval)
            return 0
        
        # Get board data
        items = board.get_board_data()
        
        # Apply filters
        items = apply_filters(items, args)
        
        # Handle different output formats
        if args.format == "json":
            output_json(items, console)
        elif args.format == "csv":
            output_csv(items, console)
        elif args.summary:
            output_summary(items, console)
        else:
            output_table(items, console, args.show_completed, args.verbose)
        
        return 0
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if args.verbose:
            import traceback
            console.print(f"[red]{traceback.format_exc()}[/red]")
        return 1


def apply_filters(items: List, args) -> List:
    """Apply command line filters to items."""
    filtered_items = items
    
    # Filter by task ID
    if args.task:
        filtered_items = [item for item in filtered_items if item.task_id == args.task]
    
    # Filter by status
    if args.status:
        filtered_items = [item for item in filtered_items if item.status.value == args.status]
    
    # Filter by reviewer
    if args.reviewer:
        filtered_items = [item for item in filtered_items if args.reviewer.lower() in item.pending_reviewer.lower()]
    
    # Filter overdue only
    if args.overdue_only:
        filtered_items = [item for item in filtered_items if item.overdue]
    
    # Filter high priority only
    if args.high_priority_only:
        filtered_items = [item for item in filtered_items if item.priority >= 6]
    
    return filtered_items


def output_table(items: List, console: Console, show_completed: bool, verbose: bool):
    """Output items in table format."""
    if not show_completed:
        from dashboard.hitl_kanban_board import ReviewStatus
        items = [item for item in items if item.status not in [ReviewStatus.COMPLETED, ReviewStatus.APPROVED]]
    
    # Create table
    table = Table(
        title="🔄 HITL Kanban Board",
        box=box.ROUNDED,
        title_style="bold blue",
        header_style="bold cyan"
    )
    
    table.add_column("Task ID", style="bold", width=8)
    table.add_column("Status", width=15)
    table.add_column("Reviewer", width=18)
    table.add_column("Deadline", width=12)
    table.add_column("Action", width=12)
    
    if verbose:
        table.add_column("Priority", width=8)
        table.add_column("Type", width=12)
        table.add_column("Risk", width=8)
    
    # Add rows
    for item in items:
        # Determine colors
        status_color = "red" if item.overdue else ("yellow" if "Awaiting" in item.status.value else "green")
        deadline_color = "red" if item.overdue else "yellow"
        
        row = [
            f"[bold]{item.task_id}[/bold]",
            f"[{status_color}]{item.status.value}[/{status_color}]",
            item.pending_reviewer,
            f"[{deadline_color}]{item.time_remaining or '—'}[/{deadline_color}]",
            item.action
        ]
        
        if verbose:
            priority_color = "red" if item.priority >= 10 else ("yellow" if item.priority >= 6 else "green")
            row.extend([
                f"[{priority_color}]{item.priority}[/{priority_color}]",
                item.checkpoint_type or "—",
                item.risk_level or "—"
            ])
        
        table.add_row(*row)
    
    console.print(table)
    
    # Show summary
    total = len(items)
    overdue = len([item for item in items if item.overdue])
    high_priority = len([item for item in items if item.priority >= 6])
    
    summary = f"Total: {total} | Overdue: {overdue} | High Priority: {high_priority}"
    console.print(f"\n[dim]{summary}[/dim]")


def output_summary(items: List, console: Console):
    """Output summary statistics."""
    from collections import Counter
    
    total = len(items)
    overdue = len([item for item in items if item.overdue])
    high_priority = len([item for item in items if item.priority >= 6])
    
    # Status breakdown
    status_counts = Counter(item.status.value for item in items)
    
    # Reviewer breakdown
    reviewer_counts = Counter(item.pending_reviewer for item in items)
    
    # Risk level breakdown
    risk_counts = Counter(item.risk_level for item in items if item.risk_level)
    
    # Create summary panel
    summary_text = f"""
📊 HITL Board Summary:
   • Total Items: {total}
   • Overdue: {overdue} {'🚨' if overdue > 0 else '✅'}
   • High Priority: {high_priority}

📈 Status Breakdown:"""
    
    for status, count in status_counts.most_common():
        summary_text += f"\n   • {status}: {count}"
    
    summary_text += "\n\n👥 Reviewer Workload:"
    for reviewer, count in reviewer_counts.most_common(5):
        summary_text += f"\n   • {reviewer}: {count}"
    
    if risk_counts:
        summary_text += "\n\n⚠️ Risk Levels:"
        for risk, count in risk_counts.most_common():
            summary_text += f"\n   • {risk}: {count}"
    
    console.print(Panel(summary_text, title="Dashboard Summary", border_style="blue"))


def output_json(items: List, console: Console):
    """Output items in JSON format."""
    from dataclasses import asdict
    
    json_data = {
        "timestamp": str(datetime.now()),
        "total_items": len(items),
        "items": []
    }
    
    for item in items:
        item_dict = asdict(item)
        # Convert datetime objects to strings
        if item_dict.get('deadline'):
            item_dict['deadline'] = item_dict['deadline'].isoformat() if hasattr(item_dict['deadline'], 'isoformat') else str(item_dict['deadline'])
        if item_dict.get('created_at'):
            item_dict['created_at'] = item_dict['created_at'].isoformat() if hasattr(item_dict['created_at'], 'isoformat') else str(item_dict['created_at'])
        
        json_data["items"].append(item_dict)
    
    console.print(json.dumps(json_data, indent=2))


def output_csv(items: List, console: Console):
    """Output items in CSV format."""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Task ID", "Status", "Pending Reviewer", "Deadline", "Action",
        "Priority", "Checkpoint Type", "Risk Level", "Overdue"
    ])
    
    # Write data
    for item in items:
        writer.writerow([
            item.task_id,
            item.status.value,
            item.pending_reviewer,
            item.time_remaining or "",
            item.action,
            item.priority,
            item.checkpoint_type or "",
            item.risk_level or "",
            "Yes" if item.overdue else "No"
        ])
    
    console.print(output.getvalue())


def handle_approval_action(checkpoint_id: str, action: str, reviewer: str, comments: str, console: Console) -> int:
    """Handle approval actions."""
    console.print(f"[yellow]Processing {action} for checkpoint {checkpoint_id}...[/yellow]")
    
    try:
        success = process_hitl_action(checkpoint_id, action, reviewer, comments)
        
        if success:
            console.print(f"[green]✅ Successfully {action}d checkpoint {checkpoint_id}[/green]")
            if comments:
                console.print(f"[dim]Comments: {comments}[/dim]")
            return 0
        else:
            console.print(f"[red]❌ Failed to {action} checkpoint {checkpoint_id}[/red]")
            return 1
            
    except Exception as e:
        console.print(f"[red]Error processing {action}: {e}[/red]")
        return 1


if __name__ == "__main__":
    from datetime import datetime
    exit(main())
