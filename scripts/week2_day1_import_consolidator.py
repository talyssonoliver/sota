#!/usr/bin/env python3
"""
Week 2 Day 1: Import Consolidation Script
Systematically replace common imports with consolidated module usage
"""

from pathlib import Path
from typing import Dict


class ImportConsolidator:
    def __init__(self):
        self.src_path = Path("src")
        self.common_imports_module = "src.infrastructure.utils.common_imports"
        
        # High-frequency imports to consolidate (from analysis)
        self.consolidation_targets = {
            'from pathlib import Path': 'Path',
            'import logging': 'logging', 
            'import json': 'json',
            'import sys': 'sys',
            'from datetime import datetime': 'datetime',
            'from datetime import datetime, timedelta': 'datetime, timedelta',
            'import os': 'os',
            'import time': 'time',
            'import uuid': 'uuid',
            'import re': 're',
            'import asyncio': 'asyncio',
            'import hashlib': 'hashlib',
            'import subprocess': 'subprocess',
            'import tempfile': 'tempfile',
            'import traceback': 'traceback',
            'from collections import Counter, defaultdict': 'Counter, defaultdict',
            'from dataclasses import dataclass': 'dataclass',
            'from dataclasses import dataclass, field': 'dataclass, field',
            'from enum import Enum': 'Enum',
            'import yaml': 'yaml',
            'import requests': 'requests',
        }
        
        # Type import consolidations
        self.type_consolidations = {
            'from typing import Any, Dict, List, Optional': 'Any, Dict, List, Optional',
            'from typing import Any, Dict': 'Any, Dict',
            'from typing import Dict, List': 'Dict, List',
            'from typing import List, Optional': 'List, Optional',
            'from typing import Any, Dict, List': 'Any, Dict, List',
            'from typing import Any, Dict, List, Optional, Union': 'Any, Dict, List, Optional, Union',
        }
        
        self.files_modified = []
        self.imports_consolidated = 0
        
    def consolidate_file(self, file_path: Path) -> Dict[str, any]:
        """Consolidate imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            if not original_content.strip():
                return {"success": True, "changes": 0}
            
            # Check if file already uses common_imports
            if 'from src.infrastructure.utils.common_imports import' in original_content:
                return {"success": True, "changes": 0, "reason": "already_consolidated"}
            
            modified_content = original_content
            changes_made = 0
            imports_to_add = set()
            
            # Find imports to consolidate
            lines = original_content.split('\n')
            new_lines = []
            
            for line in lines:
                line_stripped = line.strip()
                
                # Check if this line matches a consolidation target
                consolidated = False
                for old_import, items in self.consolidation_targets.items():
                    if line_stripped == old_import or line_stripped.startswith(old_import + ' '):
                        # Mark this import for consolidation
                        imports_to_add.update(items.split(', '))
                        # Comment out the old import
                        new_lines.append(f"# {line}  # Consolidated to common_imports")
                        changes_made += 1
                        consolidated = True
                        break
                
                # Check type imports
                if not consolidated:
                    for old_import, items in self.type_consolidations.items():
                        if line_stripped == old_import:
                            imports_to_add.update(items.split(', '))
                            new_lines.append(f"# {line}  # Consolidated to common_imports")
                            changes_made += 1
                            consolidated = True
                            break
                
                if not consolidated:
                    new_lines.append(line)
            
            # Add consolidated import if we made changes
            if changes_made > 0 and imports_to_add:
                # Find the best place to add the import (after existing imports)
                insert_index = 0
                for i, line in enumerate(new_lines):
                    if line.strip() and not line.strip().startswith(('#', 'import', 'from')):
                        insert_index = i
                        break
                
                # Create the consolidated import statement
                items_list = sorted(list(imports_to_add))
                if len(items_list) <= 3:
                    import_statement = f"from {self.common_imports_module} import {', '.join(items_list)}"
                else:
                    # Multi-line import for readability
                    import_statement = f"from {self.common_imports_module} import (\n"
                    for i, item in enumerate(items_list):
                        import_statement += f"    {item}"
                        if i < len(items_list) - 1:
                            import_statement += ","
                        import_statement += "\n"
                    import_statement += ")"
                
                new_lines.insert(insert_index, import_statement)
                new_lines.insert(insert_index, "")  # Add blank line
                
                # Write the modified file
                modified_content = '\n'.join(new_lines)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                self.files_modified.append(str(file_path))
                self.imports_consolidated += changes_made
                
                return {
                    "success": True, 
                    "changes": changes_made,
                    "imports_added": list(imports_to_add)
                }
            
            return {"success": True, "changes": 0}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def consolidate_all_files(self, dry_run: bool = False) -> Dict[str, any]:
        """Consolidate imports across all Python files"""
        print("🔄 Starting import consolidation...")
        
        if dry_run:
            print("🧪 DRY RUN MODE - No files will be modified")
        
        python_files = list(self.src_path.rglob("*.py"))
        print(f"📁 Found {len(python_files)} Python files to process")
        
        results = {
            "total_files": len(python_files),
            "files_processed": 0,
            "files_modified": 0,
            "imports_consolidated": 0,
            "errors": []
        }
        
        for file_path in python_files:
            # Skip common_imports.py itself
            if file_path.name == "common_imports.py":
                continue
                
            # Skip __init__.py files (they're usually minimal)
            if file_path.name == "__init__.py":
                continue
            
            if not dry_run:
                file_result = self.consolidate_file(file_path)
                
                if file_result["success"]:
                    if file_result["changes"] > 0:
                        results["files_modified"] += 1
                        results["imports_consolidated"] += file_result["changes"]
                        print(f"✅ {file_path}: {file_result['changes']} imports consolidated")
                else:
                    results["errors"].append(f"{file_path}: {file_result['error']}")
                    print(f"❌ {file_path}: {file_result['error']}")
            else:
                # Dry run - just check what would be done
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    potential_changes = 0
                    for target in self.consolidation_targets.keys():
                        if target in content:
                            potential_changes += 1
                    
                    if potential_changes > 0:
                        print(f"🔍 {file_path}: {potential_changes} imports could be consolidated")
                        results["files_modified"] += 1
                        results["imports_consolidated"] += potential_changes
                        
                except Exception as e:
                    print(f"❌ {file_path}: Error reading file - {e}")
            
            results["files_processed"] += 1
        
        return results
    
    def generate_report(self, results: Dict[str, any]) -> str:
        """Generate consolidation report"""
        report = f"""
📊 IMPORT CONSOLIDATION REPORT
{'='*50}

📁 Files processed: {results['total_files']}
✅ Files modified: {results['files_modified']}
🔄 Imports consolidated: {results['imports_consolidated']}
❌ Errors: {len(results['errors'])}

Estimated lines saved: {results['imports_consolidated']}
Consolidation rate: {(results['files_modified'] / results['total_files'] * 100):.1f}%

"""
        
        if results['errors']:
            report += "❌ ERRORS:\n"
            for error in results['errors']:
                report += f"  {error}\n"
        
        return report


def main():
    """Main execution"""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Week 2 Day 1: Import Consolidation")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    
    args = parser.parse_args()
    
    print("🚀 Week 2 Day 1: Import Consolidation")
    print("=" * 50)
    
    consolidator = ImportConsolidator()
    results = consolidator.consolidate_all_files(dry_run=args.dry_run)
    
    report = consolidator.generate_report(results)
    print(report)
    
    # Save report
    if not args.dry_run:
        report_file = Path("reports") / f"week2_day1_import_consolidation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"💾 Report saved to: {report_file}")
    
    return 0 if len(results['errors']) == 0 else 1


if __name__ == "__main__":
    exit(main())