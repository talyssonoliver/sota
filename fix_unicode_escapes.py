#!/usr/bin/env python3
"""Fix Unicode escape issues in test files."""

import os
import re
from pathlib import Path

def fix_unicode_escapes_in_file(file_path):
    """Fix Unicode escape issues in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and fix backslash issues in file paths within docstrings
        # Pattern: tests\something\file.py -> tests/something/file.py
        updated_content = re.sub(
            r'(tests)\\([^"\']*?)\.py',
            r'\1/\2.py',
            content
        )
        
        # Only write if content changed
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Find and fix all test files with Unicode escape issues."""
    test_dirs = [
        "tests/unit",
        "tests/integration", 
        "tests/e2e"
    ]
    
    fixed_count = 0
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        if fix_unicode_escapes_in_file(file_path):
                            fixed_count += 1
    
    print(f"Fixed {fixed_count} files with Unicode escape issues.")

if __name__ == "__main__":
    main()
