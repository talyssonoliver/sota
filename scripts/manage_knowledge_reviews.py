#!/usr/bin/env python
"""
Knowledge Summary Review Manager

This script helps manage the review process for knowledge summaries in the context-store.
It can list summaries that need review, show summary details, and mark summaries as reviewed.
"""

import argparse
import csv
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Constants
CONTEXT_STORE_DIR = "context-store"
REVIEWS_LOG_FILE = "reviews/knowledge_review_log.csv"
DOMAIN_EXPERTS = {
    "db": "Backend Engineer",
    "patterns": "Backend Engineer",
    "technical": "Technical Lead",
    "frontend": "Frontend Engineer",
    "design": "Frontend Engineer",
    "infra": "Technical Lead",
    "sprint": "Product Manager"
}


def find_unreviewed_summaries() -> List[Dict]:
    """Find all summaries that need review."""
    unreviewed = []

    for root, dirs, files in os.walk(CONTEXT_STORE_DIR):
        for file in files:
            if file.endswith(".md") or file.endswith("-summary.md"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check if the file is marked as needing review
                    if "**Reviewed: Not yet reviewed**" in content or "Reviewed: Not yet reviewed" in content:
                        domain = os.path.relpath(
                            root, CONTEXT_STORE_DIR).split(os.sep)[0]
                        recommended_expert = DOMAIN_EXPERTS.get(
                            domain, "Technical Lead")

                        unreviewed.append({
                            "path": filepath,
                            "filename": file,
                            "domain": domain,
                            "recommended_reviewer": recommended_expert
                        })
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

    return unreviewed


def show_summary_details(filepath: str) -> None:
    """Show details of a specific summary file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"\n{'=' * 80}\n{filepath}\n{'=' * 80}")
        print(content[:2000] + ("..." if len(content) > 2000 else ""))
        print(f"\n{'=' * 80}\n")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")


def mark_as_reviewed(
        filepath: str,
        reviewer_name: str,
        role: Optional[str] = None) -> bool:
    """Mark a summary as reviewed."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Get current date
        today = datetime.now().strftime("%B %d, %Y")

        # Add role if provided
        reviewer_info = f"{reviewer_name}"
        if role:
            reviewer_info += f" ({role})"

        # Replace the review marker
        updated_content = re.sub(
            r"\*\*Reviewed: Not yet reviewed\*\*",
            f"**Reviewed: {reviewer_info}, {today}**",
            content
        )

        # Write updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        # Log the review
        log_review(filepath, reviewer_name, role, today)

        print(
            f"✅ Marked '{filepath}' as reviewed by {reviewer_info} on {today}")
        return True
    except Exception as e:
        print(f"❌ Error marking review for {filepath}: {e}")
        return False


def log_review(
        filepath: str,
        reviewer_name: str,
        role: Optional[str],
        date: str) -> None:
    """Log a review in the reviews log file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(REVIEWS_LOG_FILE), exist_ok=True)

    # Prepare the data
    file_exists = os.path.isfile(REVIEWS_LOG_FILE)
    review_data = {
        "date": date,
        "file": filepath,
        "reviewer": reviewer_name,
        "role": role or "",
        "timestamp": datetime.now().isoformat()
    }

    # Write to CSV
    with open(REVIEWS_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f, fieldnames=["date", "file", "reviewer", "role", "timestamp"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(review_data)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage knowledge summary reviews")
    subparsers = parser.add_subparsers(
        dest="command", help="Command to execute")

    # List command
    list_parser = subparsers.add_parser(
        "list", help="List summaries needing review")
    list_parser.add_argument(
        "--domain", help="Filter by domain (db, patterns, technical, etc.)")

    # Show command
    show_parser = subparsers.add_parser(
        "show", help="Show details of a specific summary")
    show_parser.add_argument("filepath", help="Path to the summary file")

    # Review command
    review_parser = subparsers.add_parser(
        "review", help="Mark a summary as reviewed")
    review_parser.add_argument("filepath", help="Path to the summary file")
    review_parser.add_argument(
        "--reviewer", required=True, help="Name of the reviewer")
    review_parser.add_argument("--role", help="Role of the reviewer")

    args = parser.parse_args()

    if args.command == "list" or not args.command:
        unreviewed = find_unreviewed_summaries()

        # Apply domain filter if specified
        if hasattr(args, "domain") and args.domain:
            unreviewed = [s for s in unreviewed if s["domain"] == args.domain]

        if not unreviewed:
            print("✅ All summaries have been reviewed!")
            return

        print(f"\nFound {len(unreviewed)} summaries that need review:\n")
        for i, summary in enumerate(unreviewed, 1):
            print(
                f"{i}. {summary['path']} - Recommended reviewer: {summary['recommended_reviewer']}")

    elif args.command == "show":
        show_summary_details(args.filepath)

    elif args.command == "review":
        mark_as_reviewed(args.filepath, args.reviewer, args.role)


if __name__ == "__main__":
    main()
