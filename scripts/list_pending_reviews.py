"""
List Pending Reviews Script
This script lists all pending reviews that require human attention.
"""

import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path to import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.review import get_pending_reviews, REVIEW_DIR

def format_timestamp(timestamp_str):
    """Format a timestamp string into a readable date/time."""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Unknown"

def list_pending_reviews():
    """List all pending reviews that require human attention."""
    pending_reviews = get_pending_reviews()
    
    if not pending_reviews:
        print("No pending reviews found.")
        return
    
    print(f"Found {len(pending_reviews)} pending reviews:")
    print("-" * 60)
    print(f"{'Filename':<20} {'Created At':<20} {'Task ID':<10}")
    print("-" * 60)
    
    for filename in pending_reviews:
        metadata_path = f"{os.path.join(REVIEW_DIR, filename)}.meta.json"
        
        timestamp = "Unknown"
        task_id = "Unknown"
        
        # Extract task ID from filename (assuming format qa_BE-07.md)
        if filename.startswith("qa_") and filename.endswith(".md"):
            task_id = filename[3:-3]  # Remove qa_ and .md
            
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                    timestamp = format_timestamp(metadata.get("timestamp", ""))
            except:
                pass
                
        print(f"{filename:<20} {timestamp:<20} {task_id:<10}")
    
    print("-" * 60)
    print("To approve a review:")
    print("  python scripts/mark_review_complete.py BE-07 --approve")
    print("To reject a review:")
    print("  python scripts/mark_review_complete.py BE-07 --reject --comments \"Needs more tests\"")

if __name__ == "__main__":
    list_pending_reviews()