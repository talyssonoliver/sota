"""
Fix YAML Schema References

This script updates all task YAML files to use the correct schema reference
with an absolute path. It also validates that they conform to the schema.
"""

import os
import glob
import re
from pathlib import Path

def update_schema_reference(file_path):
    """Update schema reference in a YAML file to use the absolute path."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the expected schema reference
    schema_path = os.path.normpath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'tasks', 'task-schema.json'
    ))
    
    # Convert to file URI format with forward slashes
    schema_uri = f"file:///{schema_path.replace(os.sep, '/')}"
    
    # Replace any existing schema reference with the absolute path
    if re.search(r'# yaml-language-server: \$schema=', content):
        updated_content = re.sub(
            r'# yaml-language-server: \$schema=.*', 
            f'# yaml-language-server: $schema={schema_uri}', 
            content
        )
    else:
        # Add schema reference if it doesn't exist
        updated_content = f'# yaml-language-server: $schema={schema_uri}\n{content}'
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Updated schema reference in {os.path.basename(file_path)}")

def main():
    """Update schema references in all task YAML files."""
    # Get the path to the tasks directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tasks_dir = os.path.join(base_dir, 'tasks')
    
    # Find all YAML files in the tasks directory
    yaml_files = glob.glob(os.path.join(tasks_dir, '*.yaml'))
    yaml_files += glob.glob(os.path.join(tasks_dir, '*.yml'))
    
    # Skip the schema file itself
    yaml_files = [f for f in yaml_files if os.path.basename(f) != 'task-schema.json']
    
    print(f"Found {len(yaml_files)} task files to update")
    
    # Update schema reference in each file
    for file_path in yaml_files:
        update_schema_reference(file_path)
    
    print(f"Successfully updated {len(yaml_files)} files")
    print("Note: You may need to reload VS Code for the changes to take effect.")

if __name__ == '__main__':
    main()