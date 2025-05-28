#!/usr/bin/env python
"""
Script to add schema directives to all task YAML files.
"""

import os
import sys
from pathlib import Path


def add_schema_directives(tasks_dir="tasks"):
    """
    Add schema directives to all YAML files in the tasks directory.

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

            # Skip if already has schema directive
            if "yaml-language-server: $schema=" in content:
                print(
                    f"  Skipping {
                        file_path.name} (already has schema directive)")
                skipped += 1
                continue

            # Add schema directive to the beginning
            schema_directive = "# yaml-language-server: $schema=../config/schemas/task.schema.json\n"
            new_content = schema_directive + content

            # Write the updated content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"  Updated {file_path.name}")
            updated += 1

        except Exception as e:
            print(f"  Error updating {file_path.name}: {e}")
            errors += 1

    # Print summary
    print(
        f"\nCompleted: {updated} files updated, {skipped} skipped, {errors} errors")


if __name__ == "__main__":
    # Get tasks directory from command line arguments if provided
    tasks_dir = sys.argv[1] if len(sys.argv) > 1 else "tasks"

    # Run the function
    add_schema_directives(tasks_dir)
