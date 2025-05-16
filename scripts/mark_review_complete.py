"""
Review Completion Script
This script marks a review as complete and resumes workflow.
"""

import sys
import os
import argparse
from typing import Optional

# Add the parent directory to the path to import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.review import approve_review, reject_review
from orchestration.states import TaskStatus
from utils.task_loader import update_task_state


def approve(task_id: str, reviewer: str = "human", comments: str = "") -> None:
    """
    Approve a task review and resume the workflow.
    
    Args:
        task_id: The ID of the task to approve
        reviewer: The name of the reviewer
        comments: Any comments from the reviewer
    """
    print(f"Task {task_id} marked as approved by {reviewer}.")
    
    # Approve the review file
    review_filename = f"qa_{task_id}.md"
    approve_result = approve_review(review_filename, reviewer, comments)
    
    if approve_result:
        # Update task state
        update_task_state(task_id, TaskStatus.DOCUMENTATION)
        print(f"Task state updated to {TaskStatus.DOCUMENTATION}.")
        print("Workflow will resume from DOCUMENTATION state.")
    else:
        print("Error approving review. Workflow not resumed.")


def reject(task_id: str, reviewer: str = "human", reason: str = "") -> None:
    """
    Reject a task review and mark it as blocked.
    
    Args:
        task_id: The ID of the task to reject
        reviewer: The name of the reviewer
        reason: The reason for rejection
    """
    print(f"Task {task_id} marked as rejected by {reviewer}.")
    
    # Reject the review file
    review_filename = f"qa_{task_id}.md"
    reject_result = reject_review(review_filename, reviewer, reason)
    
    if reject_result:
        # Update task state
        update_task_state(task_id, TaskStatus.BLOCKED)
        print(f"Task state updated to {TaskStatus.BLOCKED}.")
        print(f"Reason: {reason}")
    else:
        print("Error rejecting review.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mark a task review as complete.")
    parser.add_argument("task_id", help="The ID of the task (e.g. BE-07)")
    parser.add_argument("--approve", action="store_true", help="Approve the review")
    parser.add_argument("--reject", action="store_true", help="Reject the review")
    parser.add_argument("--reviewer", default="human", help="The name of the reviewer")
    parser.add_argument("--comments", default="", help="Comments or reason for decision")
    
    args = parser.parse_args()
    
    if args.approve and args.reject:
        print("Error: Cannot both approve and reject a review.")
        sys.exit(1)
    
    if args.approve:
        approve(args.task_id, args.reviewer, args.comments)
    elif args.reject:
        reject(args.task_id, args.reviewer, args.comments)
    else:
        print("Error: Must specify either --approve or --reject.")
        sys.exit(1)