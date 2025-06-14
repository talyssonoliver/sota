#!/usr/bin/env python3
"""
HITL Kanban Board Demo - Simple Version

Demonstrates the Kanban-style HITL board with mock data for testing.
"""

import sys
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ReviewStatus(str, Enum):
    """Status categories for Kanban board."""
    AWAITING_QA = "Awaiting QA"
    AWAITING_HUMAN = "Awaiting Human"  
    IN_REVIEW = "In Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ESCALATED = "Escalated"
    COMPLETED = "Completed"


@dataclass
class KanbanItem:
    """Represents an item on the Kanban board."""
    task_id: str
    status: ReviewStatus
    pending_reviewer: str
    deadline: Optional[str]
    action: str
    priority: int = 0
    overdue: bool = False
    risk_level: str = "medium"
    checkpoint_type: str = "general"


def get_mock_kanban_data() -> List[KanbanItem]:
    """Get mock data for demonstration."""
    now = datetime.now()
    
    return [
        KanbanItem(
            task_id="BE-07",
            status=ReviewStatus.AWAITING_QA,
            pending_reviewer="QA Agent",
            deadline="4 PM",
            action="Review",
            priority=8,
            overdue=False,
            risk_level="high",
            checkpoint_type="agent_prompt"
        ),
        KanbanItem(
            task_id="UX-02",
            status=ReviewStatus.AWAITING_HUMAN,
            pending_reviewer="UX Lead",
            deadline="6 PM",
            action="Approve",
            priority=6,
            overdue=False,
            risk_level="medium",
            checkpoint_type="task_transitions"
        ),
        KanbanItem(
            task_id="PM-05",
            status=ReviewStatus.APPROVED,
            pending_reviewer="—",
            deadline="—",
            action="Completed",
            priority=0,
            overdue=False,
            risk_level="low",
            checkpoint_type="documentation"
        ),
        KanbanItem(
            task_id="FE-12",
            status=ReviewStatus.ESCALATED,
            pending_reviewer="Team Lead",
            deadline="Overdue by 2h",
            action="Resolve",
            priority=12,
            overdue=True,
            risk_level="critical",
            checkpoint_type="output_evaluation"
        ),
        KanbanItem(
            task_id="DB-03",
            status=ReviewStatus.IN_REVIEW,
            pending_reviewer="DB Admin",
            deadline="8h",
            action="Complete Review",
            priority=4,
            overdue=False,
            risk_level="medium",
            checkpoint_type="qa"
        ),
        KanbanItem(
            task_id="API-09",
            status=ReviewStatus.REJECTED,
            pending_reviewer="—",
            deadline="—",
            action="Fix Issues",
            priority=7,
            overdue=False,
            risk_level="high",
            checkpoint_type="output_evaluation"
        )
    ]


def display_rich_table(items: List[KanbanItem]):
    """Display the board using Rich formatting."""
    console = Console()
    
    # Create table
    table = Table(
        title="HITL Kanban Board - Human-in-the-Loop Review Status",
        box=box.ROUNDED,
        title_style="bold blue",
        header_style="bold cyan"
    )
    
    table.add_column("Task ID", style="bold", width=8)
    table.add_column("Status", width=15)
    table.add_column("Pending Reviewer", width=18)
    table.add_column("Deadline", width=12)
    table.add_column("Action", width=12)
    table.add_column("Priority", width=8, justify="center")
    
    # Add rows
    for item in items:
        # Style based on status and urgency
        if item.status == ReviewStatus.ESCALATED:
            status_style = "bold red"        
        elif item.overdue:
            status_style = "red"
        elif item.status in [ReviewStatus.AWAITING_QA, ReviewStatus.AWAITING_HUMAN]:
            status_style = "yellow"
        elif item.status == ReviewStatus.APPROVED:
            status_style = "green"
        else:
            status_style = "white"
        
        deadline_style = "red" if item.overdue else "yellow" if "h" in str(item.deadline) else "green"
        
        # Priority indicator
        if item.priority >= 10:
            priority_indicator = "[red][H] HIGH[/red]"
        elif item.priority >= 6:
            priority_indicator = "[yellow][!] MED[/yellow]"
        else:
            priority_indicator = "[green]• LOW[/green]"
        
        table.add_row(
            f"[bold]{item.task_id}[/bold]",
            f"[{status_style}]{item.status.value}[/{status_style}]",
            item.pending_reviewer,
            f"[{deadline_style}]{item.deadline}[/{deadline_style}]",
            item.action,
            priority_indicator
        )
    
    console.print()
    console.print(table)
      # Display summary statistics
    total_items = len(items)
    overdue_items = len([item for item in items if item.overdue])
    high_priority = len([item for item in items if item.priority >= 6])
    
    # Status breakdown
    status_counts = {}
    for item in items:
        status_counts[item.status.value] = status_counts.get(item.status.value, 0) + 1
    
    summary_text = f"""
Summary Statistics:
   • Total Items: {total_items}
   • Overdue: {overdue_items} {'[!]' if overdue_items > 0 else '[OK]'}
   • High Priority: {high_priority}
   
Status Breakdown:"""
    
    for status, count in status_counts.items():
        summary_text += f"\n   • {status}: {count}"
    
    summary_text += f"\n\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    console.print(Panel(summary_text, title="Board Summary", border_style="blue"))


def display_simple_table(items: List[KanbanItem]):
    """Display the board using simple text formatting."""
    print("\n" + "=" * 100)
    print("HITL KANBAN BOARD - HUMAN-IN-THE-LOOP REVIEW STATUS")
    print("=" * 100)
    
    # Header
    print(f"{'Task ID':<8} {'Status':<15} {'Pending Reviewer':<18} {'Deadline':<12} {'Action':<12} {'Priority':<8}")
    print("-" * 100)
      # Rows
    for item in items:
        priority_icon = "[H]" if item.priority >= 10 else ("[!]" if item.priority >= 6 else "•")
        priority_text = f"{priority_icon} {item.priority}"
        
        status_text = item.status.value
        if item.overdue:
            status_text += " (OVERDUE)"
        
        print(f"{item.task_id:<8} {status_text:<15} {item.pending_reviewer:<18} {item.deadline:<12} {item.action:<12} {priority_text:<8}")
    
    # Summary
    print("-" * 100)
    total_items = len(items)
    overdue_items = len([item for item in items if item.overdue])
    high_priority = len([item for item in items if item.priority >= 6])
    print(f"Summary: Total: {total_items} | Overdue: {overdue_items} | High Priority: {high_priority}")
    
    # Status breakdown
    status_counts = {}
    for item in items:
        status_counts[item.status.value] = status_counts.get(item.status.value, 0) + 1
    
    print("\nStatus Breakdown:")
    for status, count in status_counts.items():
        print(f"   • {status}: {count}")
    
    print(f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)


def export_json(items: List[KanbanItem], filename: str = "hitl_kanban_data.json"):
    """Export board data to JSON."""
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "total_items": len(items),
        "items": []
    }
    
    for item in items:
        export_data["items"].append({
            "task_id": item.task_id,
            "status": item.status.value,
            "pending_reviewer": item.pending_reviewer,
            "deadline": item.deadline,
            "action": item.action,
            "priority": item.priority,
            "overdue": item.overdue,
            "risk_level": item.risk_level,
            "checkpoint_type": item.checkpoint_type
        })
    
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Board data exported to {filename}")


def main():
    """Main demo function."""
    print("HITL Kanban Board Demo")
    print("Live-updated from pending_reviews/ and feedback_logs/")
    
    # Get mock data
    items = get_mock_kanban_data()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--export":
            filename = sys.argv[2] if len(sys.argv) > 2 else "hitl_kanban_data.json"
            export_json(items, filename)
            return
        elif sys.argv[1] == "--json":
            print(json.dumps([{
                "task_id": item.task_id,
                "status": item.status.value,
                "pending_reviewer": item.pending_reviewer,
                "deadline": item.deadline,
                "action": item.action,
                "priority": item.priority,
                "overdue": item.overdue
            } for item in items], indent=2))
            return
        elif sys.argv[1] == "--help":
            print("""
Usage: python hitl_kanban_demo.py [options]

Options:
  --help              Show this help message
  --export [file]     Export data to JSON file
  --json              Output data as JSON
  --simple            Use simple text formatting (default if rich not available)
  --rich              Use rich formatting (if available)

Examples:
  python hitl_kanban_demo.py
  python hitl_kanban_demo.py --export board.json
  python hitl_kanban_demo.py --json
            """)
            return
    
    # Display the board
    if RICH_AVAILABLE and "--simple" not in sys.argv:
        display_rich_table(items)
    else:
        display_simple_table(items)


if __name__ == "__main__":
    main()
