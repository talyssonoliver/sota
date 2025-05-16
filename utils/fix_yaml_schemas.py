#!/usr/bin/env python
"""
Script to update all task YAML files to use the local schema.
"""

import os
import sys
from pathlib import Path
import re

def fix_yaml_schemas(tasks_dir="tasks"):
    """
    Update schema directives in all YAML files to point to the local schema file.
    
    Args:
        tasks_dir: Path to the tasks directory
    """
    # Get all YAML files
    yaml_files = list(Path(tasks_dir).glob("*.yaml"))
    
    # Track stats
    updated = 0
    skipped = 0
    errors = 0
    
    print(f"Found {len(yaml_files)} YAML files in {tasks_dir}/")
    
    for file_path in yaml_files:
        try:
            # Read the file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Replace existing schema directive or add a new one
            schema_directive = "# yaml-language-server: $schema=./task-schema.json"
            
            # Check if already has our exact schema directive
            if schema_directive in content:
                print(f"  Skipping {file_path.name} (already has correct schema directive)")
                skipped += 1
                continue
            
            # Replace existing schema directive or add new one
            if "# yaml-language-server: $schema=" in content:
                # Replace existing directive
                new_content = re.sub(
                    r"# yaml-language-server: \$schema=[^\n]*\n", 
                    f"{schema_directive}\n", 
                    content
                )
            else:
                # Add new directive at the beginning
                new_content = f"{schema_directive}\n{content}"
            
            # Write the updated content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print(f"  Updated {file_path.name}")
            updated += 1
        
        except Exception as e:
            print(f"  Error updating {file_path.name}: {e}")
            errors += 1
    
    # Print summary
    print(f"\nCompleted: {updated} files updated, {skipped} skipped, {errors} errors")
    
if __name__ == "__main__":
    # Get tasks directory from command line arguments if provided
    tasks_dir = sys.argv[1] if len(sys.argv) > 1 else "tasks"
    
    # Run the function
    fix_yaml_schemas(tasks_dir)