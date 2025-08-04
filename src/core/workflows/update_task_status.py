#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import (
    Path,
    datetime,
    json,
    sys
)
"""
Update Task Status
Simple utility for updating task status
"""

# import json  # Consolidated to common_imports
# import sys  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports


def update_task_status(task_id, status, output_dir="outputs"):
    """Update task status in status.json file."""
    task_dir = Path(output_dir) / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    
    status_file = task_dir / "status.json"
    
    # Load existing status or create new
    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
    else:
        status_data = {
            "task_id": task_id,
            "created_at": datetime.now().isoformat()
        }
    
    # Update status
    status_data["status"] = status
    status_data["last_updated"] = datetime.now().isoformat()
    
    # Save status
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(status_data, f, indent=2, ensure_ascii=False)
    
    return status_data


def main():
    """CLI interface for updating task status."""
    if len(sys.argv) < 3:
        print("Usage: python update_task_status.py <task_id> <status>")
        sys.exit(1)
    
    task_id = sys.argv[1]
    status = sys.argv[2]
    
    result = update_task_status(task_id, status)
    print(f"Updated task {task_id} status to {status}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()