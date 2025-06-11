#!/usr/bin/env python3
"""
HITL Kanban Dashboard - Bonus Feature from System Implementation

Implements the Kanban-style HITL board for tracking Human-in-the-Loop reviews:

Task ID    Status           Pending Reviewer    Deadline    Action
BE-07      Awaiting QA      QA Agent           4 PM        Review
UX-02      Awaiting Human   UX Lead            6 PM        Approve
PM-05      Approved         —                  —           Completed

Live-updated from pending_reviews/ and feedback_logs/
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich import box

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from orchestration.hitl_engine import HITLEngine, CheckpointStatus, RiskLevel
from orchestration.hitl_task_metadata import HITLTaskMetadataManager, HITLStatus
from utils.feedback_system import FeedbackSystem


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
    deadline: Optional[datetime]
    action: str
    checkpoint_id: Optional[str] = None
    checkpoint_type: Optional[str] = None
    risk_level: Optional[str] = None
    created_at: Optional[datetime] = None
    time_remaining: Optional[str] = None
    overdue: bool = False
    priority: int = 0  # Higher numbers = higher priority


class HITLKanbanBoard:
    """
    Kanban-style HITL board for tracking review status.
    
    Features:
    - Real-time status updates from HITL engine
    - Deadline tracking with visual indicators
    - Priority sorting and categorization
    - Action buttons for reviewers
    - Live updates from pending_reviews/ and feedback_logs/
    """
    
    def __init__(self):
        """Initialize the Kanban board."""
        self.console = Console()
        self.hitl_engine = HITLEngine()
        self.metadata_manager = HITLTaskMetadataManager()
        self.feedback_system = FeedbackSystem()
        
        # Directory paths
        self.pending_reviews_dir = Path("pending_reviews")
        self.feedback_logs_dir = Path("feedback_logs")
        self.outputs_dir = Path("outputs")
        
        # Ensure directories exist
        self.pending_reviews_dir.mkdir(exist_ok=True)
        self.feedback_logs_dir.mkdir(exist_ok=True)
        
    def get_board_data(self) -> List[KanbanItem]:
        """
        Get all current board items from multiple sources.
        
        Returns:
            List of KanbanItem objects for the board
        """
        items = []
        
        # Get data from HITL engine (checkpoints)
        items.extend(self._get_checkpoint_items())
        
        # Get data from pending reviews directory
        items.extend(self._get_pending_review_items())
        
        # Get data from feedback logs
        items.extend(self._get_feedback_log_items())
        
        # Sort by priority and deadline
        items = self._prioritize_items(items)
        
        return items
    
    def _get_checkpoint_items(self) -> List[KanbanItem]:
        """Get items from HITL checkpoint system."""
        items = []
        
        try:
            # Get pending checkpoints
            pending_checkpoints = self.hitl_engine.get_pending_checkpoints()
            
            for checkpoint in pending_checkpoints:
                # Determine status based on checkpoint state
                if checkpoint.status == CheckpointStatus.PENDING:
                    if checkpoint.checkpoint_type in ["agent_prompt", "output_evaluation"]:
                        status = ReviewStatus.AWAITING_QA
                        reviewer = "QA Agent"
                        action = "Review"
                    else:
                        status = ReviewStatus.AWAITING_HUMAN
                        reviewer = self._get_assigned_reviewer(checkpoint.task_id, checkpoint.checkpoint_type)
                        action = "Approve"
                elif checkpoint.status == CheckpointStatus.IN_REVIEW:
                    status = ReviewStatus.IN_REVIEW
                    reviewer = self._get_current_reviewer(checkpoint.checkpoint_id)
                    action = "Complete Review"
                elif checkpoint.status == CheckpointStatus.ESCALATED:
                    status = ReviewStatus.ESCALATED
                    reviewer = "Team Lead"
                    action = "Resolve"
                else:
                    continue  # Skip completed items for now
                
                # Calculate time remaining
                time_remaining, overdue = self._calculate_time_remaining(checkpoint.timeout_at)
                
                # Determine priority
                priority = self._calculate_priority(checkpoint.risk_level, overdue, checkpoint.created_at)
                
                items.append(KanbanItem(
                    task_id=checkpoint.task_id,
                    status=status,
                    pending_reviewer=reviewer,
                    deadline=checkpoint.timeout_at,
                    action=action,
                    checkpoint_id=checkpoint.checkpoint_id,
                    checkpoint_type=checkpoint.checkpoint_type,
                    risk_level=checkpoint.risk_level.value if checkpoint.risk_level else None,
                    created_at=checkpoint.created_at,
                    time_remaining=time_remaining,
                    overdue=overdue,
                    priority=priority
                ))
                
        except Exception as e:
            self.console.print(f"[red]Error loading checkpoint items: {e}[/red]")
        
        return items
    
    def _get_pending_review_items(self) -> List[KanbanItem]:
        """Get items from pending_reviews/ directory."""
        items = []
        
        try:
            if not self.pending_reviews_dir.exists():
                return items
            
            for review_file in self.pending_reviews_dir.glob("*.md"):
                # Extract task ID from filename (e.g., qa_BE-07.md -> BE-07)
                task_id = self._extract_task_id_from_filename(review_file.name)
                if not task_id:
                    continue
                
                # Check for metadata file
                meta_file = review_file.with_suffix('.md.meta.json')
                deadline = None
                reviewer = "Unknown"
                
                if meta_file.exists():
                    try:
                        with open(meta_file, 'r') as f:
                            metadata = json.load(f)
                            deadline_str = metadata.get('deadline')
                            if deadline_str:
                                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                            reviewer = metadata.get('assigned_to', reviewer)
                    except Exception:
                        pass
                
                # Determine status and action based on file type
                if review_file.name.startswith('qa_'):
                    status = ReviewStatus.AWAITING_QA
                    reviewer = reviewer if reviewer != "Unknown" else "QA Agent"
                    action = "Review"
                else:
                    status = ReviewStatus.AWAITING_HUMAN
                    action = "Approve"
                
                # Calculate time remaining
                time_remaining, overdue = self._calculate_time_remaining(deadline)
                
                # Default priority
                priority = 5 if overdue else 1
                
                items.append(KanbanItem(
                    task_id=task_id,
                    status=status,
                    pending_reviewer=reviewer,
                    deadline=deadline,
                    action=action,
                    time_remaining=time_remaining,
                    overdue=overdue,
                    priority=priority
                ))
                
        except Exception as e:
            self.console.print(f"[red]Error loading pending review items: {e}[/red]")
        
        return items
    
    def _get_feedback_log_items(self) -> List[KanbanItem]:
        """Get recently completed items from feedback logs."""
        items = []
        
        try:
            # Look for recent completions in outputs directory
            if self.outputs_dir.exists():
                for task_dir in self.outputs_dir.iterdir():
                    if not task_dir.is_dir():
                        continue
                    
                    # Check for recent completion files
                    review_files = list(task_dir.glob("*review*.json"))
                    approval_files = list(task_dir.glob("*approval*.json"))
                    
                    if review_files or approval_files:
                        # Get the most recent file
                        all_files = review_files + approval_files
                        most_recent = max(all_files, key=lambda f: f.stat().st_mtime)
                        
                        # Check if it's from the last 24 hours
                        file_time = datetime.fromtimestamp(most_recent.stat().st_mtime)
                        if datetime.now() - file_time < timedelta(hours=24):
                            try:
                                with open(most_recent, 'r') as f:
                                    data = json.load(f)
                                    
                                approved = data.get('approved', False)
                                reviewer = data.get('reviewer', 'Unknown')
                                
                                items.append(KanbanItem(
                                    task_id=task_dir.name,
                                    status=ReviewStatus.APPROVED if approved else ReviewStatus.REJECTED,
                                    pending_reviewer="—",
                                    deadline=None,
                                    action="Completed",
                                    time_remaining="—",
                                    overdue=False,
                                    priority=0
                                ))
                            except Exception:
                                pass
                
        except Exception as e:
            self.console.print(f"[red]Error loading feedback log items: {e}[/red]")
        
        return items
    
    def _calculate_time_remaining(self, deadline: Optional[datetime]) -> Tuple[str, bool]:
        """Calculate time remaining until deadline."""
        if not deadline:
            return "—", False
        
        now = datetime.now()
        if deadline.tzinfo:
            # Make now timezone-aware to match deadline
            from datetime import timezone
            now = now.replace(tzinfo=timezone.utc)
        
        time_diff = deadline - now
        
        if time_diff.total_seconds() < 0:
            # Overdue
            overdue_time = abs(time_diff)
            if overdue_time.days > 0:
                return f"Overdue by {overdue_time.days} days", True
            else:
                hours = int(overdue_time.total_seconds() // 3600)
                return f"Overdue by {hours}h", True
        else:
            # Time remaining
            if time_diff.days > 0:
                return f"{time_diff.days} days", False
            else:
                hours = int(time_diff.total_seconds() // 3600)
                return f"{hours}h", False
    
    def _calculate_priority(self, risk_level: Optional[RiskLevel], overdue: bool, created_at: Optional[datetime]) -> int:
        """Calculate priority score for sorting."""
        priority = 0
        
        # Overdue items get highest priority
        if overdue:
            priority += 10
        
        # Risk level affects priority
        if risk_level == RiskLevel.CRITICAL:
            priority += 8
        elif risk_level == RiskLevel.HIGH:
            priority += 6
        elif risk_level == RiskLevel.MEDIUM:
            priority += 4
        elif risk_level == RiskLevel.LOW:
            priority += 2
        
        # Age affects priority (older items get higher priority)
        if created_at:
            age_hours = (datetime.now() - created_at).total_seconds() / 3600
            priority += min(int(age_hours / 24), 5)  # Max 5 points for age
        
        return priority
    
    def _prioritize_items(self, items: List[KanbanItem]) -> List[KanbanItem]:
        """Sort items by priority, status, and deadline."""
        def sort_key(item: KanbanItem):
            # Primary: Priority (descending)
            # Secondary: Status importance
            # Tertiary: Deadline (ascending)
            
            status_priority = {
                ReviewStatus.ESCALATED: 10,
                ReviewStatus.AWAITING_QA: 8,
                ReviewStatus.AWAITING_HUMAN: 7,
                ReviewStatus.IN_REVIEW: 6,
                ReviewStatus.REJECTED: 4,
                ReviewStatus.APPROVED: 2,
                ReviewStatus.COMPLETED: 1
            }
            
            deadline_score = 0
            if item.deadline:
                time_to_deadline = (item.deadline - datetime.now()).total_seconds()
                deadline_score = max(0, 86400 - time_to_deadline)  # Earlier deadlines get higher scores
            
            return (
                -item.priority,  # Higher priority first
                -status_priority.get(item.status, 5),  # Important statuses first
                deadline_score  # Earlier deadlines first
            )
        
        return sorted(items, key=sort_key)
    
    def _get_assigned_reviewer(self, task_id: str, checkpoint_type: str) -> str:
        """Get assigned reviewer for a task."""
        try:
            metadata = self.metadata_manager.load_task_metadata(task_id)
            if metadata and metadata.hitl_checkpoints:
                for checkpoint in metadata.hitl_checkpoints:
                    if checkpoint.checkpoint_type == checkpoint_type:
                        return checkpoint.assigned_reviewers[0] if checkpoint.assigned_reviewers else "Unknown"
        except Exception:
            pass
        
        # Default reviewers based on checkpoint type
        defaults = {
            "agent_prompt": "QA Agent",
            "output_evaluation": "Tech Lead",
            "qa": "QA Agent",
            "documentation": "PM",
            "task_transitions": "Team Lead"
        }
        return defaults.get(checkpoint_type, "Unknown")
    
    def _get_current_reviewer(self, checkpoint_id: str) -> str:
        """Get current reviewer for a checkpoint."""
        try:
            checkpoint = self.hitl_engine.get_checkpoint(checkpoint_id)
            if checkpoint and hasattr(checkpoint, 'current_reviewer'):
                return checkpoint.current_reviewer
        except Exception:
            pass
        return "In Progress"
    
    def _extract_task_id_from_filename(self, filename: str) -> Optional[str]:
        """Extract task ID from review filename."""
        # Common patterns: qa_BE-07.md, review_UX-02.md, BE-07_approval.md
        import re
        patterns = [
            r'(?:qa_|review_)?([A-Z]{2}-\d{2})',  # qa_BE-07.md or BE-07
            r'([A-Z]{2,3}-\d{2})',  # Direct task ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        
        return None
    
    def display_board(self, show_completed: bool = False, max_completed: int = 5) -> None:
        """
        Display the Kanban board in a table format.
        
        Args:
            show_completed: Whether to show completed items
            max_completed: Maximum number of completed items to show
        """
        items = self.get_board_data()
        
        # Filter items based on display preferences
        if not show_completed:
            items = [item for item in items if item.status not in [ReviewStatus.COMPLETED, ReviewStatus.APPROVED]]
        else:
            # Limit completed items
            completed_items = [item for item in items if item.status in [ReviewStatus.COMPLETED, ReviewStatus.APPROVED]]
            other_items = [item for item in items if item.status not in [ReviewStatus.COMPLETED, ReviewStatus.APPROVED]]
            items = other_items + completed_items[:max_completed]
        
        # Create the main table
        table = Table(
            title="🔄 HITL Kanban Board - Human-in-the-Loop Review Status",
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
            status_style = self._get_status_style(item.status, item.overdue)
            deadline_style = "red" if item.overdue else "yellow" if item.time_remaining and "h" in item.time_remaining else "green"
            
            # Priority indicator
            if item.priority >= 10:
                priority_indicator = "[red]🔥 HIGH[/red]"
            elif item.priority >= 6:
                priority_indicator = "[yellow]⚠️ MED[/yellow]"
            else:
                priority_indicator = "[green]• LOW[/green]"
            
            table.add_row(
                f"[bold]{item.task_id}[/bold]",
                f"[{status_style}]{item.status}[/{status_style}]",
                item.pending_reviewer,
                f"[{deadline_style}]{item.time_remaining or '—'}[/{deadline_style}]",
                item.action,
                priority_indicator
            )
        
        # Display the table
        self.console.print()
        self.console.print(table)
        
        # Show summary statistics
        self._display_summary_stats(items)
    
    def _get_status_style(self, status: ReviewStatus, overdue: bool) -> str:
        """Get Rich style for status display."""
        if overdue:
            return "bold red"
        
        status_styles = {
            ReviewStatus.ESCALATED: "bold red",
            ReviewStatus.AWAITING_QA: "yellow",
            ReviewStatus.AWAITING_HUMAN: "cyan",
            ReviewStatus.IN_REVIEW: "blue",
            ReviewStatus.APPROVED: "green",
            ReviewStatus.REJECTED: "red",
            ReviewStatus.COMPLETED: "dim green"
        }
        return status_styles.get(status, "white")
    
    def _display_summary_stats(self, items: List[KanbanItem]) -> None:
        """Display summary statistics below the board."""
        # Calculate stats
        total_items = len(items)
        overdue_items = len([item for item in items if item.overdue])
        high_priority = len([item for item in items if item.priority >= 6])
        
        # Status breakdown
        status_counts = {}
        for item in items:
            status_counts[item.status] = status_counts.get(item.status, 0) + 1
        
        # Create summary panel
        summary_text = f"""
📊 Summary Statistics:
   • Total Items: {total_items}
   • Overdue: {overdue_items} {'🚨' if overdue_items > 0 else '✅'}
   • High Priority: {high_priority}
   
📈 Status Breakdown:"""
        
        for status, count in status_counts.items():
            summary_text += f"\n   • {status}: {count}"
        
        # Add timestamp
        summary_text += f"\n\n🕒 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.console.print(Panel(summary_text, title="Board Summary", border_style="blue"))
    
    def export_board_data(self, output_file: str = "hitl_board_data.json") -> None:
        """Export board data to JSON file."""
        items = self.get_board_data()
        
        # Convert to serializable format
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "total_items": len(items),
            "items": []
        }
        
        for item in items:
            item_data = asdict(item)
            # Convert datetime objects to strings
            if item_data.get('deadline'):
                item_data['deadline'] = item_data['deadline'].isoformat()
            if item_data.get('created_at'):
                item_data['created_at'] = item_data['created_at'].isoformat()
            
            export_data["items"].append(item_data)
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.console.print(f"[green]✅ Board data exported to {output_file}[/green]")
    
    def watch_mode(self, refresh_interval: int = 30) -> None:
        """
        Display board in watch mode with automatic refresh.
        
        Args:
            refresh_interval: Refresh interval in seconds
        """
        import time
        
        try:
            while True:
                # Clear screen
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # Display board
                self.display_board()
                
                # Show refresh info
                self.console.print(f"\n[dim]Refreshing every {refresh_interval}s... Press Ctrl+C to exit[/dim]")
                
                # Wait for next refresh
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Watch mode stopped.[/yellow]")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="HITL Kanban Board - Human-in-the-Loop Review Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dashboard/hitl_kanban_board.py                    # Show current board
  python dashboard/hitl_kanban_board.py --show-completed   # Include completed items
  python dashboard/hitl_kanban_board.py --watch            # Watch mode with auto-refresh
  python dashboard/hitl_kanban_board.py --export board.json # Export to JSON
        """
    )
    
    parser.add_argument(
        "--show-completed",
        action="store_true",
        help="Show recently completed items"
    )
    
    parser.add_argument(
        "--max-completed",
        type=int,
        default=5,
        help="Maximum number of completed items to show"
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
        help="Refresh interval in seconds for watch mode"
    )
    
    parser.add_argument(
        "--export",
        type=str,
        help="Export board data to JSON file"
    )
    
    args = parser.parse_args()
    
    # Create board instance
    board = HITLKanbanBoard()
    
    try:
        if args.export:
            board.export_board_data(args.export)
        elif args.watch:
            board.watch_mode(args.refresh_interval)
        else:
            board.display_board(args.show_completed, args.max_completed)
    
    except Exception as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
# This code is part of the HITL Kanban Board implementation for tracking Human-in-the-Loop reviews.
# It provides a CLI interface for displaying, updating, and exporting the board status.
