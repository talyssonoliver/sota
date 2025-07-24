#!/usr/bin/env python3
"""
Script to fix legacy import paths in test files
"""

import os
import re
from pathlib import Path

# Define import mappings
IMPORT_MAPPINGS = {
    # Utils imports
    r'from utils\.([a-zA-Z_]+) import': r'from src.infrastructure.utils.\1 import',
    
    # Orchestration imports
    r'from orchestration\.([a-zA-Z_]+) import': r'from src.core.workflows.\1 import',
    
    # Agents imports  
    r'from agents\.([a-zA-Z_]+) import': r'from src.core.agents.\1 import',
    
    # API imports
    r'from api\.([a-zA-Z_]+) import': r'from src.interfaces.api.\1 import',
    
    # Dashboard imports
    r'from dashboard\.([a-zA-Z_]+) import': r'from src.interfaces.dashboard.\1 import',
    
    # Scripts imports
    r'from scripts\.([a-zA-Z_]+) import': r'from src.infrastructure.scripts.\1 import',
    
    # Graph imports
    r'from graph\.([a-zA-Z_]+) import': r'from src.core.graph.\1 import',
    
    # Handlers imports
    r'from handlers\.([a-zA-Z_]+) import': r'from src.core.handlers.\1 import',
    
    # CLI imports
    r'from cli\.([a-zA-Z_]+) import': r'from src.interfaces.cli.\1 import',
}

# Special mappings for specific modules
SPECIAL_MAPPINGS = {
    'from scripts.update_dashboard import': 'from src.infrastructure.scripts.monitoring.update_dashboard import',
    'from scripts.generate_progress_report import': 'from src.infrastructure.scripts.generation.generate_progress_report import',
    'from scripts.generate_task_report import': 'from src.infrastructure.scripts.generation.generate_task_report import',
    'from dashboard.unified_api_server import': 'from src.interfaces.dashboard.api.unified_api_server import',
    'from orchestration.hitl_engine import': 'from src.infrastructure.hitl.hitl_engine import',
}

def fix_imports_in_file(file_path):
    """Fix import statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply special mappings first
        for old_import, new_import in SPECIAL_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # Apply regex mappings
        for old_pattern, new_pattern in IMPORT_MAPPINGS.items():
            content = re.sub(old_pattern, new_pattern, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed imports in {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def find_test_files_with_import_errors():
    """Find all test files that likely have import errors."""
    test_root = Path("/mnt/c/taly/ai-system/tests")
    test_files = []
    
    # Look for test files in the root tests directory
    for file_path in test_root.glob("test_*.py"):
        test_files.append(file_path)
    
    return test_files

def main():
    """Main function to fix all import issues."""
    print("🔧 Starting legacy import fixes...")
    
    test_files = find_test_files_with_import_errors()
    
    if not test_files:
        print("ℹ️  No test files found with potential import issues.")
        return
    
    print(f"📁 Found {len(test_files)} test files to process")
    
    fixed_count = 0
    for test_file in test_files:
        if fix_imports_in_file(test_file):
            fixed_count += 1
    
    print(f"\n✨ Fixed imports in {fixed_count} out of {len(test_files)} files")

if __name__ == "__main__":
    main()