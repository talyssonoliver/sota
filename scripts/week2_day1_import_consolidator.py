#!/usr/bin/env python3
"""
Week 2 Day 1: Enhanced Import Consolidation Script
Systematically replace common imports with consolidated module usage
+ ARCHITECTURE FIX: Remove sys.path.insert patterns
"""

from pathlib import Path
from typing import Dict
import subprocess
import sys


class ImportConsolidator:
    """Enhanced import consolidator with safety measures and comprehensive testing."""
    
    def __init__(self, verify_tests: bool = True, create_backup: bool = True, 
                 verify_git_clean: bool = True):
        self.src_path = Path("src")
        self.common_imports_module = "src.infrastructure.utils.common_imports"
        self.root_path = Path(".")
        self.verify_tests = verify_tests
        self.create_backup = create_backup
        self.verify_git_clean = verify_git_clean
        self.backup_branch = None
        self.test_failures_before = []
        self.test_failures_after = []
        
        # sys.path.insert patterns to remove (ARCHITECTURE FIX)
        self.path_insert_patterns = [
            # Common patterns found in the codebase
            r'sys\.path\.insert\(0,\s*str\(Path\(__file__\)\.parent(?:\.parent)*\)\)',
            r'sys\.path\.insert\(0,\s*str\(Path\(__file__\)\.parent(?:\.parent)*\s*/\s*["\']\w+["\']\)\)',
            r'sys\.path\.insert\(0,\s*["\'][^"\']*["\']\)',
            r'sys\.path\.insert\(0,\s*str\(project_root\)\)',
            r'sys\.path\.insert\(0,\s*str\(project_root\s*/\s*["\']src["\']\)\)',
        ]
        
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
        self.path_inserts_removed = 0
        self.files_with_path_fixes = []
        self.errors = []
        self.validation_errors = []
        
    def consolidate_file(self, file_path: Path) -> Dict[str, any]:
        """Consolidate imports and remove sys.path.insert patterns in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            if not original_content.strip():
                return {"success": True, "changes": 0}
            
            # First pass: Remove sys.path.insert patterns (ARCHITECTURE FIX)
            modified_content, path_changes = self._remove_path_inserts(original_content, file_path)
            
            # Check if file already uses common_imports (but still process path inserts)
            if 'from src.infrastructure.utils.common_imports import' in modified_content and path_changes == 0:
                return {"success": True, "changes": path_changes, "reason": "already_consolidated"}
            
            changes_made = path_changes
            imports_to_add = set()
            
            # Find imports to consolidate
            lines = modified_content.split('\n')
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
                final_content = '\n'.join(new_lines)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                
                self.files_modified.append(str(file_path))
                self.imports_consolidated += (changes_made - path_changes)
                self.path_inserts_removed += path_changes
                
                return {
                    "success": True, 
                    "changes": changes_made,
                    "imports_added": list(imports_to_add),
                    "path_inserts_removed": path_changes
                }
            
            elif path_changes > 0:
                # Only path changes were made
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                self.files_with_path_fixes.append(str(file_path))
                self.path_inserts_removed += path_changes
                
                return {
                    "success": True,
                    "changes": path_changes,
                    "path_inserts_removed": path_changes
                }
            
            return {"success": True, "changes": 0, "path_inserts_removed": 0}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _remove_path_inserts(self, content: str, file_path: Path) -> tuple[str, int]:
        """Remove sys.path.insert patterns and add proper import setup if needed."""
        import re
        
        original_lines = content.split('\n')
        new_lines = []
        changes_made = 0
        has_sys_import = 'import sys' in content or 'from sys import' in content
        project_root_defined = 'project_root' in content
        
        # Calculate the relative path from current file to project root
        try:
            rel_to_root = file_path.relative_to(self.root_path)
            parent_levels = len(rel_to_root.parent.parts)
        except ValueError:
            parent_levels = 1  # Default fallback
        
        for i, line in enumerate(original_lines):
            line_stripped = line.strip()
            
            # Check if this line contains sys.path.insert pattern
            path_insert_found = False
            for pattern in self.path_insert_patterns:
                if re.search(pattern, line_stripped):
                    # Comment out the sys.path.insert line
                    new_lines.append(f"# {line}  # REMOVED: sys.path.insert (architecture fix)")
                    changes_made += 1
                    path_insert_found = True
                    break
            
            if not path_insert_found:
                # Check for project_root definitions that are only used for path manipulation
                if re.match(r'project_root\s*=\s*Path\(__file__\)\.parent(?:\.parent)*', line_stripped):
                    # Check if project_root is only used for sys.path.insert
                    remaining_content = '\n'.join(original_lines[i+1:])
                    if 'sys.path.insert(0, str(project_root))' in remaining_content and 'project_root' not in remaining_content.replace('sys.path.insert(0, str(project_root))', '').replace('project_root = ', ''):
                        new_lines.append(f"# {line}  # REMOVED: only used for sys.path.insert")
                        changes_made += 1
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
        
        # If we removed sys.path.insert and there's no remaining sys usage, remove sys import too
        if changes_made > 0 and has_sys_import:
            # Check if sys is used elsewhere
            remaining_content = '\n'.join(new_lines)
            if 'sys.' not in remaining_content.replace('# ', '') and 'import sys' in remaining_content:
                # Remove standalone sys import
                final_lines = []
                for line in new_lines:
                    if line.strip() == 'import sys':
                        final_lines.append('# import sys  # REMOVED: no longer needed after sys.path.insert removal')
                    else:
                        final_lines.append(line)
                new_lines = final_lines
        
        return '\n'.join(new_lines), changes_made
    
    def verify_git_status(self) -> bool:
        """Verify git repository is in clean state before consolidation."""
        if not self.verify_git_clean:
            return True
            
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.root_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("⚠️  Not in a git repository or git not available")
                return True  # Don't fail if not in git repo
                
            if result.stdout.strip():
                print("❌ Git working directory is not clean")
                print("🔍 Uncommitted changes found:")
                for line in result.stdout.strip().split('\n')[:5]:
                    print(f"   {line}")
                print("💡 Please commit or stash changes before running consolidation")
                return False
                
            print("✅ Git working directory is clean")
            return True
            
        except Exception as e:
            print(f"⚠️  Could not verify git status: {e}")
            return True
    
    def create_backup_branch(self) -> bool:
        """Create a backup git branch before making changes."""
        if not self.create_backup:
            return True
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_branch = f"import-consolidation-backup-{timestamp}"
            
            result = subprocess.run(
                ['git', 'checkout', '-b', self.backup_branch],
                cwd=self.root_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"⚠️  Could not create backup branch: {result.stderr}")
                return True  # Don't fail consolidation if backup fails
                
            print(f"✅ Created backup branch: {self.backup_branch}")
            
            # Switch back to original branch
            subprocess.run(
                ['git', 'checkout', '-'],
                cwd=self.root_path,
                capture_output=True
            )
            
            return True
            
        except Exception as e:
            print(f"⚠️  Could not create backup branch: {e}")
            return True
    
    def run_tests_before(self) -> bool:
        """Run tests before consolidation to establish baseline."""
        if not self.verify_tests:
            return True
            
        print("🧪 Running tests before consolidation...")
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/', '--tb=no', '-q'],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if "FAILED" in result.stdout:
                # Extract failed test names
                import re
                failures = re.findall(r'FAILED ([^\s]+)', result.stdout)
                self.test_failures_before = failures
                print(f"⚠️  {len(failures)} tests were already failing before consolidation")
                for failure in failures[:5]:  # Show first 5
                    print(f"   {failure}")
            else:
                print("✅ All tests passing before consolidation")
                
            return True
            
        except subprocess.TimeoutExpired:
            print("⚠️  Test run timed out (5 minutes)")
            return True  # Don't fail consolidation due to slow tests
        except Exception as e:
            print(f"⚠️  Could not run tests: {e}")
            return True
    
    def run_tests_after(self) -> bool:
        """Run tests after consolidation to verify no regressions."""
        if not self.verify_tests:
            return True
            
        print("🧪 Running tests after consolidation...")
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/', '--tb=no', '-q'],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if "FAILED" in result.stdout:
                import re
                failures = re.findall(r'FAILED ([^\s]+)', result.stdout)
                self.test_failures_after = failures
                
                # Check if we introduced new failures
                new_failures = set(failures) - set(self.test_failures_before)
                if new_failures:
                    print(f"❌ Import consolidation introduced {len(new_failures)} new test failures:")
                    for failure in list(new_failures)[:5]:
                        print(f"   {failure}")
                    return False
                else:
                    print(f"✅ No new test failures introduced ({len(failures)} pre-existing)")
            else:
                print("✅ All tests still passing after consolidation")
                
            return True
            
        except subprocess.TimeoutExpired:
            print("⚠️  Post-consolidation test run timed out")
            return False  # This is more concerning after changes
        except Exception as e:
            print(f"❌ Could not run post-consolidation tests: {e}")
            return False
    
    def validate_common_imports_available(self) -> bool:
        """Validate that the common imports module is available and working."""
        try:
            # Try to import the common imports module
            sys.path.insert(0, str(self.root_path))
            
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "common_imports",
                self.root_path / self.common_imports_module.replace('.', '/') + '.py'
            )
            
            if spec is None or spec.loader is None:
                self.validation_errors.append("Common imports module not found")
                return False
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check that key imports are available
            required_imports = ['Path', 'logging', 'json', 'sys', 'datetime']
            missing_imports = []
            
            for imp in required_imports:
                if not hasattr(module, imp):
                    missing_imports.append(imp)
            
            if missing_imports:
                self.validation_errors.append(f"Missing imports in common_imports: {missing_imports}")
                return False
                
            print("✅ Common imports module is available and functional")
            return True
            
        except Exception as e:
            self.validation_errors.append(f"Could not validate common imports: {e}")
            return False
        finally:
            # Clean up sys.path
            if str(self.root_path) in sys.path:
                sys.path.remove(str(self.root_path))
    
    def consolidate_all_files(self, dry_run: bool = False) -> Dict[str, any]:
        """Consolidate imports across all Python files with enhanced safety."""
        print("🔄 Starting enhanced import consolidation...")
        
        if dry_run:
            print("🧪 DRY RUN MODE - No files will be modified")
        else:
            # Safety checks before making changes
            if not self.verify_git_status():
                return {
                    "success": False,
                    "error": "Git working directory not clean",
                    "total_files": 0,
                    "files_processed": 0,
                    "files_modified": 0,
                    "imports_consolidated": 0,
                    "path_inserts_removed": 0,
                    "files_with_path_fixes": 0,
                    "errors": ["Git working directory not clean"]
                }
                
            if not self.validate_common_imports_available():
                return {
                    "success": False,
                    "error": "Common imports module not available",
                    "total_files": 0,
                    "files_processed": 0,
                    "files_modified": 0,
                    "imports_consolidated": 0,
                    "path_inserts_removed": 0,
                    "files_with_path_fixes": 0,
                    "errors": self.validation_errors
                }
                
            self.create_backup_branch()
            self.run_tests_before()
        
        python_files = list(self.src_path.rglob("*.py"))
        print(f"📁 Found {len(python_files)} Python files to process")
        
        results = {
            "total_files": len(python_files),
            "files_processed": 0,
            "files_modified": 0,
            "imports_consolidated": 0,
            "path_inserts_removed": 0,
            "files_with_path_fixes": 0,
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
                        if 'imports_added' in file_result:
                            results["imports_consolidated"] += file_result["changes"] - file_result.get('path_inserts_removed', 0)
                        if file_result.get('path_inserts_removed', 0) > 0:
                            results["path_inserts_removed"] += file_result['path_inserts_removed']
                            results["files_with_path_fixes"] += 1
                        
                        change_details = []
                        if 'imports_added' in file_result:
                            change_details.append(f"{file_result['changes'] - file_result.get('path_inserts_removed', 0)} imports consolidated")
                        if file_result.get('path_inserts_removed', 0) > 0:
                            change_details.append(f"{file_result['path_inserts_removed']} sys.path.insert removed")
                        
                        print(f"✅ {file_path}: {', '.join(change_details)}")
                else:
                    results["errors"].append(f"{file_path}: {file_result['error']}")
                    print(f"❌ {file_path}: {file_result['error']}")
            else:
                # Dry run - just check what would be done
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    potential_changes = 0
                    potential_path_fixes = 0
                    
                    # Check import consolidations
                    for target in self.consolidation_targets.keys():
                        if target in content:
                            potential_changes += 1
                    
                    # Check sys.path.insert patterns
                    import re
                    for pattern in self.path_insert_patterns:
                        potential_path_fixes += len(re.findall(pattern, content))
                    
                    if potential_changes > 0 or potential_path_fixes > 0:
                        change_details = []
                        if potential_changes > 0:
                            change_details.append(f"{potential_changes} imports could be consolidated")
                        if potential_path_fixes > 0:
                            change_details.append(f"{potential_path_fixes} sys.path.insert could be removed")
                        
                        print(f"🔍 {file_path}: {', '.join(change_details)}")
                        results["files_modified"] += 1
                        results["imports_consolidated"] += potential_changes
                        results["path_inserts_removed"] += potential_path_fixes
                        if potential_path_fixes > 0:
                            results["files_with_path_fixes"] += 1
                        
                except Exception as e:
                    print(f"❌ {file_path}: Error reading file - {e}")
            
            results["files_processed"] += 1
        
        # Post-consolidation validation if not dry run
        if not dry_run:
            print("🔍 Running post-consolidation validation...")
            if not self.run_tests_after():
                print("❌ Post-consolidation tests failed - consider rolling back")
                if self.backup_branch:
                    print(f"💡 Rollback command: git checkout {self.backup_branch}")
                results["success"] = False
                results["errors"].append("Post-consolidation tests failed")
            else:
                print("✅ Post-consolidation validation passed")
                results["success"] = True
        else:
            results["success"] = True
            
        return results
    
    def generate_report(self, results: Dict[str, any]) -> str:
        """Generate consolidation report"""
        report = f"""
📊 ENHANCED IMPORT CONSOLIDATION REPORT (ARCHITECTURE FIX)
{'='*60}

📁 Files processed: {results['total_files']}
✅ Files modified: {results['files_modified']}
🔄 Imports consolidated: {results['imports_consolidated']}
🏗️ sys.path.insert patterns removed: {results['path_inserts_removed']}
🔧 Files with path fixes: {results['files_with_path_fixes']}
❌ Errors: {len(results['errors'])}

Estimated lines saved: {results['imports_consolidated'] + results['path_inserts_removed']}
Consolidation rate: {(results['files_modified'] / results['total_files'] * 100):.1f}%
Architecture improvement rate: {(results['files_with_path_fixes'] / results['total_files'] * 100):.1f}%

🎯 ARCHITECTURE FIXES:
- Removed {results['path_inserts_removed']} sys.path.insert patterns
- Fixed {results['files_with_path_fixes']} files with path manipulation issues
- Improved import hygiene across codebase

"""
        
        if results['errors']:
            report += "❌ ERRORS:\n"
            for error in results['errors']:
                report += f"  {error}\n"
        
        if results['files_with_path_fixes'] > 0:
            report += "\n🏗️ ARCHITECTURE IMPROVEMENTS:\n"
            report += f"- Eliminated {results['path_inserts_removed']} sys.path.insert statements\n"
            report += f"- Improved import reliability in {results['files_with_path_fixes']} files\n"
            report += "- Reduced path manipulation complexity\n"
            report += "- Better adherence to Python import best practices\n"
        
        return report


def main():
    """Main execution with enhanced safety measures."""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(
        description="Enhanced Import Consolidation + Architecture Fix",
        epilog="Examples:\n"
               "  %(prog)s --dry-run              # Preview changes safely\n"
               "  %(prog)s --no-tests --no-backup # Fast consolidation (less safe)\n"
               "  %(prog)s --validate-only        # Just validate common imports",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--no-tests", action="store_true", help="Skip test verification (faster but less safe)")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup branch creation")
    parser.add_argument("--no-git-check", action="store_true", help="Skip git working directory check")
    parser.add_argument("--validate-only", action="store_true", help="Only validate common imports module")
    
    args = parser.parse_args()
    
    print("🚀 Enhanced Import Consolidation + Architecture Fix")
    print("=" * 60)
    
    try:
        consolidator = ImportConsolidator(
            verify_tests=not args.no_tests,
            create_backup=not args.no_backup,
            verify_git_clean=not args.no_git_check
        )
        
        # Validate only mode
        if args.validate_only:
            if consolidator.validate_common_imports_available():
                print("✅ Common imports module validation passed")
                return 0
            else:
                print("❌ Common imports module validation failed")
                for error in consolidator.validation_errors:
                    print(f"   {error}")
                return 1
        
        results = consolidator.consolidate_all_files(dry_run=args.dry_run)
        
        if not results.get("success", True):
            print(f"\n❌ Import consolidation failed: {results.get('error', 'Unknown error')}")
            if results.get("errors"):
                print("❌ Errors encountered:")
                for error in results["errors"][:5]:  # Show first 5 errors
                    print(f"   {error}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Import consolidation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during import consolidation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    report = consolidator.generate_report(results)
    print(report)
    
    # Save report
    if not args.dry_run:
        report_file = Path("reports") / f"enhanced_import_consolidation_architecture_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"💾 Report saved to: {report_file}")
    
    print("\n✅ Import consolidation completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())