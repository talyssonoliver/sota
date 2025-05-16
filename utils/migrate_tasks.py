#!/usr/bin/env python
"""
Migration script to convert tasks from the centralized JSON file to individual YAML files.
"""

import json
import os
import yaml
import sys
from pathlib import Path

def migrate_tasks(source_file="context-store/agent_task_assignments.json", target_dir="tasks"):
    """
    Migrate tasks from a centralized JSON file to individual YAML files.
    
    Args:
        source_file: Path to the source JSON file
        target_dir: Path to the target directory for YAML files
    """
    # Ensure target directory exists
    os.makedirs(target_dir, exist_ok=True)
    
    # Load the source JSON file
    with open(source_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Track conversion statistics
    created = 0
    skipped = 0
    errors = 0
    
    # Process each agent role
    for role, tasks in data.items():
        print(f"Processing {len(tasks)} tasks for {role}")
        
        # Map agent roles to shorter names for the owner field
        owner_map = {
            "technical_lead": "technical",
            "product_manager": "product",
            "backend_engineer": "backend",
            "frontend_engineer": "frontend",
            "ux_designer": "ux",
            "qa_tester": "qa"
        }
        
        # Default owner if role not in the map
        owner = owner_map.get(role, role)
        
        # Process each task
        for task in tasks:
            task_id = task.get("id")
            if not task_id:
                print("  Warning: Task without ID found, skipping")
                errors += 1
                continue
            
            # Output file path
            file_path = os.path.join(target_dir, f"{task_id}.yaml")
            
            # Skip if file exists
            if os.path.exists(file_path):
                print(f"  Skipping {task_id} (already exists)")
                skipped += 1
                continue
            
            # Create YAML structure
            yaml_data = {
                "id": task_id,
                "title": task.get("title", f"Task {task_id}"),
                "owner": owner,
                "depends_on": task.get("dependencies", []),
                "state": "PLANNED",  # Default state
                "priority": "MEDIUM",  # Default priority
                "estimation_hours": 2,  # Default estimation
                "description": task.get("description", f"Task {task_id}: {task.get('title', '')}"),
                "artefacts": task.get("artefacts", [])
            }
            
            # Add context topics based on role
            if owner == "backend":
                yaml_data["context_topics"] = ["db-schema", "service-pattern", "supabase-setup"]
            elif owner == "frontend":
                yaml_data["context_topics"] = ["design-system", "component-patterns", "ui-standards"]
            elif owner == "technical":
                yaml_data["context_topics"] = ["infrastructure", "ci-cd", "tech-standards"]
            elif owner == "qa":
                yaml_data["context_topics"] = ["test-patterns", "quality-standards", "testing-strategy"]
            elif owner == "doc":
                yaml_data["context_topics"] = ["documentation-standards", "project-overview", "api-references"]
            else:
                yaml_data["context_topics"] = ["project-overview"]
            
            # Write YAML file
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(yaml_data, f, default_flow_style=False, sort_keys=False)
                print(f"  Created {task_id}")
                created += 1
            except Exception as e:
                print(f"  Error creating {task_id}: {e}")
                errors += 1
    
    # Print summary
    print(f"\nMigration complete: {created} created, {skipped} skipped, {errors} errors")
    print(f"Tasks are now available in the {target_dir}/ directory")

if __name__ == "__main__":
    # Get source and target paths from command line arguments if provided
    source = sys.argv[1] if len(sys.argv) > 1 else "context-store/agent_task_assignments.json"
    target = sys.argv[2] if len(sys.argv) > 2 else "tasks"
    
    # Run migration
    migrate_tasks(source, target)