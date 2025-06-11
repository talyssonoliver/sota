#!/usr/bin/env python3
"""
Quick HITL Status - Simple CLI tool for checking HITL board status

A lightweight tool to quickly check the current HITL Kanban board status
without starting the full dashboard server.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


def safe_print(text: str):
    """Print text safely, handling Unicode encoding issues on Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Strip emoji and unicode characters for Windows console
        import re
        safe_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(safe_text)


def get_mock_data() -> List[Dict[str, Any]]:
    """Get mock HITL board data for demonstration."""
    return [
        {
            "task_id": "BE-07",
            "status": "Awaiting QA",
            "pending_reviewer": "QA Agent", 
            "deadline": "4 PM",
            "action": "Review",
            "priority": 8,
            "overdue": False,
            "risk_level": "high"
        },
        {
            "task_id": "UX-02", 
            "status": "Awaiting Human",
            "pending_reviewer": "UX Lead",
            "deadline": "6 PM", 
            "action": "Approve",
            "priority": 6,
            "overdue": False,
            "risk_level": "medium"
        },
        {
            "task_id": "PM-05",
            "status": "Approved", 
            "pending_reviewer": "—",
            "deadline": "—",
            "action": "Completed",
            "priority": 0,
            "overdue": False,
            "risk_level": "low"
        },
        {
            "task_id": "FE-12",
            "status": "Escalated",
            "pending_reviewer": "Team Lead", 
            "deadline": "Overdue by 2h",
            "action": "Resolve",
            "priority": 12,
            "overdue": True,
            "risk_level": "critical"
        }
    ]


def check_pending_reviews_directory() -> List[Dict[str, Any]]:
    """Check the pending_reviews directory for actual pending items."""
    items = []
    pending_dir = Path("pending_reviews")
    
    if not pending_dir.exists():
        return items
    
    for review_file in pending_dir.glob("*.md"):
        # Extract task ID from filename
        task_id = "Unknown"
        if review_file.name.startswith("qa_"):
            task_id = review_file.name[3:-3]  # Remove qa_ and .md
        
        # Check for metadata
        meta_file = review_file.with_suffix('.md.meta.json')
        reviewer = "Unknown"
        deadline = "Unknown"
        
        if meta_file.exists():
            try:
                with open(meta_file, 'r') as f:
                    metadata = json.load(f)
                    reviewer = metadata.get('assigned_to', reviewer)
                    deadline = metadata.get('deadline', deadline)
            except Exception:
                pass
        
        items.append({
            "task_id": task_id,
            "status": "Awaiting QA" if review_file.name.startswith("qa_") else "Awaiting Human",
            "pending_reviewer": reviewer,
            "deadline": deadline,
            "action": "Review" if review_file.name.startswith("qa_") else "Approve",
            "priority": 5,  # Default priority
            "overdue": False,  # Would need more logic to determine
            "risk_level": "medium"
        })
    
    return items


def check_feedback_logs() -> List[Dict[str, Any]]:
    """Check feedback logs for recently completed items."""
    items = []
    outputs_dir = Path("outputs")
    
    if not outputs_dir.exists():
        return items
    
    # Look for recent completion files
    recent_cutoff = datetime.now().timestamp() - (24 * 3600)  # Last 24 hours
    
    for task_dir in outputs_dir.iterdir():
        if not task_dir.is_dir():
            continue
        
        # Check for recent review files
        review_files = list(task_dir.glob("*review*.json")) + list(task_dir.glob("*approval*.json"))
        
        for review_file in review_files:
            if review_file.stat().st_mtime > recent_cutoff:
                try:
                    with open(review_file, 'r') as f:
                        data = json.load(f)
                        
                    approved = data.get('approved', False)
                    reviewer = data.get('reviewer', 'Unknown')
                    
                    items.append({
                        "task_id": task_dir.name,
                        "status": "Approved" if approved else "Rejected",
                        "pending_reviewer": "—",
                        "deadline": "—", 
                        "action": "Completed",
                        "priority": 0,
                        "overdue": False,
                        "risk_level": "low"
                    })
                    break  # Only add one entry per task
                except Exception:
                    continue
    
    return items


def display_status_simple(items: List[Dict[str, Any]]):
    """Display status in simple text format."""
    print("\n" + "=" * 85)
    try:
        print("🔄 HITL KANBAN BOARD - CURRENT STATUS")
    except UnicodeEncodeError:
        print("HITL KANBAN BOARD - CURRENT STATUS")
    print("=" * 85)
    print(f"{'Task ID':<8} {'Status':<15} {'Reviewer':<18} {'Deadline':<12} {'Action':<10}")
    print("-" * 85)
    
    for item in items:
        task_id = item['task_id']
        status = item['status']
        reviewer = item['pending_reviewer'][:17] if len(item['pending_reviewer']) > 17 else item['pending_reviewer']
        deadline = item['deadline'][:11] if len(item['deadline']) > 11 else item['deadline']
        action = item['action']
          # Add priority indicator
        if item['overdue']:
            status += " [!]"  # Was 🚨
        elif item['priority'] >= 8:
            status += " [H]"  # Was 🔥 
        elif item['priority'] >= 6:
            status += " [!]"  # Was ⚠️
        
        print(f"{task_id:<8} {status:<15} {reviewer:<18} {deadline:<12} {action:<10}")
    
    print("-" * 85)
    
    # Summary stats
    total = len(items)
    overdue = len([item for item in items if item['overdue']])
    high_priority = len([item for item in items if item['priority'] >= 6])
    pending = len([item for item in items if item['status'] in ['Awaiting QA', 'Awaiting Human', 'In Review']])
    safe_print(f"Summary: Total: {total} | Pending: {pending} | Overdue: {overdue} | High Priority: {high_priority}")
    safe_print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 85)


def display_status_json(items: List[Dict[str, Any]]):
    """Display status in JSON format."""
    output = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_items": len(items),
            "pending_count": len([item for item in items if item['status'] in ['Awaiting QA', 'Awaiting Human', 'In Review']]),
            "overdue_count": len([item for item in items if item['overdue']]),
            "high_priority_count": len([item for item in items if item['priority'] >= 6])
        },
        "items": items
    }
    
    print(json.dumps(output, indent=2))


def main():
    """Main function."""
    # Parse simple arguments
    show_json = '--json' in sys.argv
    use_mock = '--mock' in sys.argv
    show_help = '--help' in sys.argv or '-h' in sys.argv
    
    if show_help:
        print("""
HITL Status - Quick HITL Board Status Check

Usage: python quick_hitl_status.py [options]

Options:
  --help, -h    Show this help message
  --json        Output in JSON format
  --mock        Use mock data for demonstration
  --real        Use real data from pending_reviews/ and outputs/

Examples:
  python quick_hitl_status.py              # Show current status
  python quick_hitl_status.py --json       # JSON output
  python quick_hitl_status.py --mock       # Demo with mock data
        """)
        return
    
    # Get data
    if use_mock or '--real' not in sys.argv:
        print("Using mock data for demonstration...")
        items = get_mock_data()
    else:
        print("Checking real data from filesystem...")
        items = []
        items.extend(check_pending_reviews_directory())
        items.extend(check_feedback_logs())
        
        if not items:
            print("No pending reviews found. Using mock data for demonstration.")
            items = get_mock_data()
    
    # Display
    if show_json:
        display_status_json(items)
    else:
        display_status_simple(items)


if __name__ == "__main__":
    main()
