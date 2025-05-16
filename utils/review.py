"""
Review Utilities
Contains functions for managing human review workflow.
"""

import os
import json
from datetime import datetime

# Constants
REVIEW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reviews")
APPROVED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".approved")


def save_to_review(filename: str, content: str) -> str:
    """
    Saves content to the review directory for human inspection.
    
    Args:
        filename: The filename to save the content as
        content: The content to save
        
    Returns:
        The full path of the saved file
    """
    os.makedirs(REVIEW_DIR, exist_ok=True)
    filepath = os.path.join(REVIEW_DIR, filename)
    
    with open(filepath, "w") as f:
        f.write(content)
    
    # Also save metadata about this review
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "filename": filename,
        "status": "PENDING",
        "reviewer": None
    }
    
    metadata_path = f"{filepath}.meta.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    return filepath


def is_review_approved(filename: str) -> bool:
    """
    Checks if a review has been approved.
    
    Args:
        filename: The filename of the review
        
    Returns:
        True if the review is approved, False otherwise
    """
    # Check for approval flag file
    os.makedirs(APPROVED_DIR, exist_ok=True)
    approval_flag = os.path.join(APPROVED_DIR, f"{filename}.approved")
    
    return os.path.exists(approval_flag)


def approve_review(filename: str, reviewer: str = "human", comments: str = "") -> bool:
    """
    Marks a review as approved.
    
    Args:
        filename: The filename of the review
        reviewer: The name of the reviewer
        comments: Any comments from the reviewer
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create approval flag
        os.makedirs(APPROVED_DIR, exist_ok=True)
        approval_flag = os.path.join(APPROVED_DIR, f"{filename}.approved")
        
        with open(approval_flag, "w") as f:
            f.write(f"Approved by {reviewer} at {datetime.now().isoformat()}\n")
            if comments:
                f.write(f"Comments: {comments}\n")
        
        # Update metadata
        filepath = os.path.join(REVIEW_DIR, filename)
        metadata_path = f"{filepath}.meta.json"
        
        metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        
        metadata["status"] = "APPROVED"
        metadata["reviewer"] = reviewer
        metadata["approved_at"] = datetime.now().isoformat()
        metadata["comments"] = comments
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error approving review: {e}")
        return False


def reject_review(filename: str, reviewer: str = "human", reason: str = "") -> bool:
    """
    Marks a review as rejected.
    
    Args:
        filename: The filename of the review
        reviewer: The name of the reviewer
        reason: The reason for rejection
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Update metadata
        filepath = os.path.join(REVIEW_DIR, filename)
        metadata_path = f"{filepath}.meta.json"
        
        metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        
        metadata["status"] = "REJECTED"
        metadata["reviewer"] = reviewer
        metadata["rejected_at"] = datetime.now().isoformat()
        metadata["rejection_reason"] = reason
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error rejecting review: {e}")
        return False


def get_pending_reviews() -> list:
    """
    Gets a list of all pending reviews.
    
    Returns:
        A list of pending review filenames
    """
    if not os.path.exists(REVIEW_DIR):
        return []
    
    pending = []
    
    for filename in os.listdir(REVIEW_DIR):
        if filename.endswith(".meta.json"):
            continue
        
        if not is_review_approved(filename):
            pending.append(filename)
    
    return pending