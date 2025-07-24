#!/usr/bin/env python3
"""
Import Validation Script for Post-Migration Architecture

Systematically validates all Python imports across the codebase after
the src/ architecture migration.
"""

# Comprehensive mocks added
import sys
from unittest.mock import MagicMock, Mock


# Mock external dependencies
class MockModule:
    def __init__(self, name):
        self.name = name
    def __getattr__(self, item):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()


# Add common mock attributes

# Original imports with error handling
try:
    import ast
except ImportError:
    pass
try:
    import sys
except ImportError:
    pass
try:
    import importlib
except ImportError:
    pass
try:
    from pathlib import Path
except ImportError:
    pass
try:
    from typing import Dict, List, Tuple
except ImportError:
    pass
try:
    import traceback
except ImportError:
    pass
try:
    import re
except ImportError:
    pass

import os


class ImportValidator:
    def __init__(self, quiet_mode=False):
        self.failed_imports = []
        self.syntax_errors = []
        self.import_errors = []
        self.missing_modules = set()
        self.handled_imports = set()  # Track imports handled by try/except
        self.warning_summary = {}  # Track warnings by category
        self.quiet_mode = quiet_mode
        
        # Add paths to Python path in correct priority order
        # IMPORTANT: Add root_dir FIRST so tools/ package is found before src/tools/
        root_dir = Path(__file__).parent.parent.parent  # Go up from scripts/validation/ to project root
        src_dir = root_dir / "src"
        tests_dir = root_dir / "tests"
        
        # Add in reverse order since we're using insert(0, ...)
        # This ensures root_dir has highest priority
        paths_to_add = [str(tests_dir), str(src_dir), str(root_dir)]
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
    
    def add_warning(self, category, message):
        """Add a warning to the summary."""
        if category not in self.warning_summary:
            self.warning_summary[category] = []
        self.warning_summary[category].append(message)
        
        if not self.quiet_mode:
            print(f"WARNING: {message}")
    
    def print_warning_summary(self):
        """Print a summary of all warnings by category."""
        if not self.warning_summary:
            print("✅ No warnings detected!")
            return
            
        print("\n" + "=" * 60)
        print("WARNING SUMMARY")
        print("=" * 60)
        
        total_warnings = sum(len(warnings) for warnings in self.warning_summary.values())
        print(f"Total warnings: {total_warnings}")
        print()
        
        for category, warnings in self.warning_summary.items():
            print(f"📁 {category} ({len(warnings)} warnings)")
            if len(warnings) <= 3:
                for warning in warnings:
                    print(f"  - {warning}")
            else:
                for warning in warnings[:2]:
                    print(f"  - {warning}")
                print(f"  ... and {len(warnings) - 2} more")
            print()
    
    def validate_syntax(self, py_file: Path) -> bool:
        """Validate Python syntax without executing imports."""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True
        except SyntaxError as e:
            self.syntax_errors.append((py_file, f"Syntax error: {e}"))
            return False
        except Exception as e:
            self.syntax_errors.append((py_file, f"Parse error: {e}"))
            return False
    
    def extract_imports(self, py_file: Path) -> List[str]:
        """Extract all import statements from a Python file."""
        imports = []
        handled_imports = set()  # Track imports handled by try/except
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # First pass: identify imports in try/except blocks
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    # Check if any import statements are in the try block
                    for try_node in node.body:
                        if isinstance(try_node, ast.Import):
                            for alias in try_node.names:
                                handled_imports.add(alias.name)
                        elif isinstance(try_node, ast.ImportFrom):
                            if try_node.module:
                                # For 'from x.y import z', we want to track 'x.y'
                                handled_imports.add(try_node.module)
                                # Also track submodules if they exist
                                module_parts = try_node.module.split('.')
                                for i in range(len(module_parts)):
                                    partial_module = '.'.join(module_parts[:i+1])
                                    handled_imports.add(partial_module)
            
            # Second pass: collect all imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Mark relative imports with a prefix so we can handle them differently
                        if node.level > 0:  # This is a relative import
                            imports.append('.' + node.module)
                        else:
                            imports.append(node.module)
            
            # Store handled imports for later use
            self.handled_imports = handled_imports
                        
        except Exception as e:
            print(f"Could not extract imports from {py_file}: {e}")
        
        return imports
    
    def validate_import(self, import_name: str, source_file: Path) -> bool:
        """Validate a single import statement."""
        try:
            # Handle relative imports
            if import_name.startswith('.'):
                return True  # Skip relative import validation for now
            
            # Check if this import is handled by try/except (graceful failure)
            if hasattr(self, 'handled_imports') and import_name in self.handled_imports:
                try:
                    importlib.import_module(import_name)
                    return True
                except ImportError:
                    # Import fails but it's handled gracefully - treat as warning not error
                    self.add_warning("Optional Dependencies", 
                                   f"Import handled gracefully: {source_file}: '{import_name}' (optional dependency)")
                    return True
            
            # Try to import the module
            importlib.import_module(import_name)
            return True
        
        except ImportError as e:
            self.import_errors.append((source_file, import_name, str(e)))
            self.missing_modules.add(import_name)
            return False
        except Exception as e:
            self.import_errors.append((source_file, import_name, f"Unexpected error: {e}"))
            return False
    
    def validate_file(self, py_file: Path) -> Dict[str, bool]:
        """Validate a single Python file."""
        results = {
            'syntax_valid': False,
            'imports_valid': False
        }
        
        # First check syntax
        if not self.validate_syntax(py_file):
            return results
        
        results['syntax_valid'] = True
        
        # Reset handled imports for this file
        self.handled_imports = set()
        
        # Then check imports (this will populate handled_imports)
        imports = self.extract_imports(py_file)
        all_imports_valid = True
        
        for import_name in imports:
            if not self.validate_import(import_name, py_file):
                all_imports_valid = False
        
        results['imports_valid'] = all_imports_valid
        return results
    
    def validate_all_files(self) -> Dict[str, int]:
        """Validate all Python files across the entire codebase."""
        # Define directories to scan comprehensively
        scan_dirs = [
            "src/",
            "tools/", 
            "scripts/",
            "tests/",
            "config/",
            "visualization/",
            "examples/",
            "orchestration/"
        ]
        
        all_files = []
        for scan_dir in scan_dirs:
            scan_path = Path(scan_dir)
            if scan_path.exists():
                all_files.extend(list(scan_path.rglob("*.py")))
        
        # Also scan root-level Python files (excluding certain patterns)
        root_files = [f for f in Path(".").glob("*.py") 
                     if f.is_file() and not f.name.startswith('.')]
        all_files.extend(root_files)
        stats = {
            'total_files': len(all_files),
            'syntax_valid': 0,
            'imports_valid': 0,
            'completely_valid': 0
        }
        
        print(f"Validating {len(all_files)} Python files...")
        print()
        
        for py_file in all_files:
            if '__pycache__' in str(py_file):
                continue
                
            results = self.validate_file(py_file)
            
            if results['syntax_valid']:
                stats['syntax_valid'] += 1
                print(f"PASS Syntax: {py_file}")
            else:
                print(f"❌ Syntax: {py_file}")
            
            if results['imports_valid']:
                stats['imports_valid'] += 1
                print(f"PASS Imports: {py_file}")
            else:
                print(f"❌ Imports: {py_file}")
            
            if results['syntax_valid'] and results['imports_valid']:
                stats['completely_valid'] += 1
                print(f"PASS Complete: {py_file}")
            
            print()
        
        return stats
    
    def print_summary(self, stats: Dict[str, int]):
        """Print validation summary."""
        print("=" * 80)
        print("IMPORT VALIDATION SUMMARY")
        print("=" * 80)
        print()
        
        print(f"File Statistics:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Syntax valid: {stats['syntax_valid']} ({stats['syntax_valid']/stats['total_files']*100:.1f}%)")
        print(f"  Imports valid: {stats['imports_valid']} ({stats['imports_valid']/stats['total_files']*100:.1f}%)")
        print(f"  Completely valid: {stats['completely_valid']} ({stats['completely_valid']/stats['total_files']*100:.1f}%)")
        print()
        
        if self.syntax_errors:
            print(f"Syntax Errors ({len(self.syntax_errors)}):")
            for file_path, error in self.syntax_errors[:10]:  # Show first 10
                print(f"  X {file_path}: {error}")
            if len(self.syntax_errors) > 10:
                print(f"  ... and {len(self.syntax_errors) - 10} more")
            print()
        
        if self.import_errors:
            print(f"Import Errors ({len(self.import_errors)}):")
            for file_path, import_name, error in self.import_errors[:15]:  # Show first 15
                print(f"  X {file_path}: '{import_name}' - {error}")
            if len(self.import_errors) > 15:
                print(f"  ... and {len(self.import_errors) - 15} more")
            print()
        
        if self.missing_modules:
            print(f"Missing Modules ({len(self.missing_modules)}):")
            for module in sorted(list(self.missing_modules))[:20]:  # Show first 20
                print(f"  - {module}")
            if len(self.missing_modules) > 20:
                print(f"  ... and {len(self.missing_modules) - 20} more")
            print()
        
        # Determine overall status
        if stats['completely_valid'] == stats['total_files']:
            print("SUCCESS: ALL IMPORTS VALIDATED SUCCESSFULLY!")
            return True
        else:
            print(f"X {stats['total_files'] - stats['completely_valid']} files have issues")
            return False

def check_circular_imports():
    """Check for circular import dependencies using graph analysis."""
    print("Checking for circular imports...")
    
    import_graph = {}
    circular_imports = []
    
    # Build import graph
    for file_path in Path('.').rglob("*.py"):
        if any(skip in str(file_path) for skip in ['__pycache__', '.git', 'venv', 'env', 'test']):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract imports
            imports = set()
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('from ') and ' import ' in line:
                    # Extract module name
                    module = line.split('from ')[1].split(' import')[0].strip()
                    if module.startswith('.'):
                        # Relative import - convert to absolute
                        module = str(file_path.parent / module[1:]).replace('\\', '.').replace('/', '.')
                    imports.add(module)
                elif line.startswith('import '):
                    # Direct import
                    module = line.split('import ')[1].split(',')[0].split(' as ')[0].strip()
                    imports.add(module)
            
            # Convert file path to module name
            module_name = str(file_path.with_suffix('')).replace('\\', '.').replace('/', '.')
            if module_name.startswith('.'):
                module_name = module_name[1:]
                
            import_graph[module_name] = imports
            
        except Exception as e:
            print(f"   Warning: Could not analyze {file_path}: {e}")
    
    # Detect cycles using DFS
    def has_cycle(node, visited, rec_stack, path):
        if node not in import_graph:
            return False
            
        visited.add(node)
        rec_stack.add(node)
        current_path = path + [node]
        
        for neighbor in import_graph[node]:
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack, current_path):
                    return True
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = current_path.index(neighbor)
                cycle = current_path[cycle_start:] + [neighbor]
                circular_imports.append(cycle)
                return True
                
        rec_stack.remove(node)
        return False
    
    # Check each module for cycles
    visited = set()
    for module in import_graph:
        if module not in visited:
            has_cycle(module, visited, set(), [])
    
    # Remove duplicates
    unique_cycles = []
    for cycle in circular_imports:
        cycle_str = ' -> '.join(cycle)
        if not any(cycle_str in ' -> '.join(existing) for existing in unique_cycles):
            unique_cycles.append(cycle)
    
    if unique_cycles:
        print("❌ Circular imports detected:")
        for i, cycle in enumerate(unique_cycles, 1):
            print(f"   {i}. {' -> '.join(cycle)}")
    else:
        print("No circular imports detected")
    
    return unique_cycles

def validate_directory_imports(directory_path):
    """Validate imports within a specific directory and its subdirectories."""
    print(f"📁 Validating directory: {directory_path}")
    
    validator = ImportValidator()
    directory_files = []
    
    # Collect all Python files in the directory
    for file_path in Path(directory_path).rglob("*.py"):
        if not any(skip in str(file_path) for skip in ['__pycache__', '.git', 'venv', 'env']):
            directory_files.append(file_path)
    
    print(f"   Found {len(directory_files)} Python files")
    
    # Validate each file
    stats = {
        'total_files': 0,
        'valid_files': 0,
        'files_with_issues': 0,
        'total_imports': 0,
        'valid_imports': 0,
        'issues': []
    }
    
    for file_path in directory_files:
        file_stats = validator.validate_file(file_path)
        if file_stats:
            stats['total_files'] += 1
            stats['total_imports'] += file_stats.get('total_imports', 0)
            stats['valid_imports'] += file_stats.get('valid_imports', 0)
            
            if file_stats.get('issues', []):
                stats['files_with_issues'] += 1
                stats['issues'].extend(file_stats['issues'])
            else:
                stats['valid_files'] += 1
    
    return stats

def check_architecture_compliance():
    """Check that files are in correct locations according to architecture."""
    print("🏗️  Checking architecture compliance...")
    violations = []
    
    # Check root directory only has allowed files
    allowed_root = {
        'README.md', 'LICENSE', 'CHANGELOG.md', 'CLAUDE.md', 'AGENT.md',
        'requirements.txt', 'requirements-dev.txt', 'requirements-enterprise.txt',
        'pyproject.toml', 'pytest.ini', 'mypy.ini', 'setup.py',
        '.env.example', 'Makefile', 'main.py', 'validate_imports.py',
        'docker-compose.dev.yml', 'Dockerfile.dev', 'Dockerfile.docs', 'Dockerfile.jupyter',
        'lint.bat', '__init__.py', 'copilot-instructions.md', 'IMPORT_REFACTORING_COMPLETION_REPORT.md'
    }
    
    for item in Path('.').glob('*.py'):
        if item.is_file() and item.name not in allowed_root:
            violations.append(f"Python file {item.name} should not be in root directory")
    
    # Check for backup files (should all be removed)
    backup_files = list(Path('.').rglob('*.backup'))
    if backup_files:
        violations.append(f"Found {len(backup_files)} backup files that should be removed")
    
    return violations

def validate_entire_codebase():
    """Validate the entire codebase structure and imports."""
    print("Comprehensive Codebase Validation")
    print("=" * 50)
    
    # Standard import validation
    validator = ImportValidator()
    stats = validator.validate_all_files()
    import_success = validator.print_summary(stats)
    
    print("\n" + "=" * 50)
    
    # Check for circular imports
    circular_issues = check_circular_imports()
    
    print()
    # Check architecture compliance
    arch_violations = check_architecture_compliance()
    
    # Print architecture results
    if arch_violations:
        print("❌ Architecture violations found:")
        for violation in arch_violations:
            print(f"  - {violation}")
    else:
        print("✅ Architecture compliance: PASSED")
    
    # Overall summary
    print("\n" + "=" * 50)
    print("📊 Overall Validation Summary:")
    print(f"  Import validation: {'✅ PASSED' if import_success else '❌ FAILED'}")
    print(f"  Circular imports: {'✅ NONE DETECTED' if not circular_issues else f'⚠️  {len(circular_issues)} DETECTED'}")
    print(f"  Architecture: {'✅ COMPLIANT' if not arch_violations else f'❌ {len(arch_violations)} VIOLATIONS'}")
    
    overall_success = import_success and not circular_issues and not arch_violations
    print(f"\n🎯 Overall Result: {'✅ SUCCESS' if overall_success else '❌ NEEDS ATTENTION'}")
    
    return overall_success

def validate_entire_codebase_enhanced():
    """Enhanced comprehensive codebase validation with directory-specific checks."""
    print("Enhanced Comprehensive Codebase Validation")
    print("=" * 60)
    
    # 1. Standard import validation
    print("1️⃣  Standard Import Validation")
    validator = ImportValidator()
    stats = validator.validate_all_files()
    import_success = validator.print_summary(stats)
    
    print("\n" + "=" * 60)
    
    # 2. Directory-specific validation
    print("2️⃣  Directory-Specific Validation")
    key_directories = ['src', 'engines', 'tools', 'handlers', 'orchestration', 'config']
    directory_stats = {}
    
    for directory in key_directories:
        if Path(directory).exists():
            print(f"\n📁 Validating {directory}/")
            dir_stats = validate_directory_imports(directory)
            directory_stats[directory] = dir_stats
            
            # Summary for this directory
            if dir_stats['total_files'] > 0:
                success_rate = (dir_stats['valid_files'] / dir_stats['total_files']) * 100
                print(f"   📊 Files: {dir_stats['valid_files']}/{dir_stats['total_files']} ({success_rate:.1f}% success)")
                print(f"   📦 Imports: {dir_stats['valid_imports']}/{dir_stats['total_imports']}")
                if dir_stats['issues']:
                    print(f"   ⚠️  Issues: {len(dir_stats['issues'])}")
    
    print("\n" + "=" * 60)
    
    # 3. Check for circular imports
    print("3️⃣  Circular Import Detection")
    circular_issues = check_circular_imports()
    
    print("\n" + "=" * 60)
    
    # 4. Check architecture compliance
    print("4️⃣  Architecture Compliance")
    arch_violations = check_architecture_compliance()
    
    # Print architecture results
    if arch_violations:
        print("❌ Architecture violations found:")
        for violation in arch_violations:
            print(f"  - {violation}")
    else:
        print("✅ Architecture compliance: PASSED")
    
    # 5. Cross-directory dependency analysis
    print("\n" + "=" * 60)
    print("5️⃣  Cross-Directory Dependency Analysis")
    analyze_cross_directory_dependencies()
    
    # Overall summary
    print("\n" + "=" * 60)
    print("📊 Enhanced Validation Summary:")
    print(f"  Import validation: {'✅ PASSED' if import_success else '❌ FAILED'}")
    
    # Directory summary
    total_dir_files = sum(stats.get('total_files', 0) for stats in directory_stats.values())
    valid_dir_files = sum(stats.get('valid_files', 0) for stats in directory_stats.values())
    if total_dir_files > 0:
        dir_success_rate = (valid_dir_files / total_dir_files) * 100
        print(f"  Directory validation: {'✅' if dir_success_rate > 90 else '⚠️' if dir_success_rate > 70 else '❌'} {dir_success_rate:.1f}% ({valid_dir_files}/{total_dir_files})")
    
    print(f"  Circular imports: {'✅ NONE DETECTED' if not circular_issues else f'⚠️  {len(circular_issues)} DETECTED'}")
    print(f"  Architecture: {'✅ COMPLIANT' if not arch_violations else f'❌ {len(arch_violations)} VIOLATIONS'}")
    
    overall_success = (import_success and 
                      not circular_issues and 
                      not arch_violations and 
                      (total_dir_files == 0 or dir_success_rate > 80))
    
    print(f"\n🎯 Overall Result: {'✅ SUCCESS' if overall_success else '❌ NEEDS ATTENTION'}")
    
    return overall_success

def analyze_cross_directory_dependencies():
    """Analyze dependencies between different directories to identify coupling."""
    print("🔗 Analyzing cross-directory dependencies...")
    
    dependencies = {}
    key_directories = ['src', 'engines', 'tools', 'handlers', 'orchestration', 'config']
    
    for directory in key_directories:
        if not Path(directory).exists():
            continue
            
        dependencies[directory] = set()
        
        for file_path in Path(directory).rglob("*.py"):
            if any(skip in str(file_path) for skip in ['__pycache__', '.git', 'test']):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for imports from other key directories
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('from ') and ' import ' in line:
                        module = line.split('from ')[1].split(' import')[0].strip()
                        for other_dir in key_directories:
                            if other_dir != directory and module.startswith(other_dir):
                                dependencies[directory].add(other_dir)
                                break
                    elif line.startswith('import '):
                        module = line.split('import ')[1].split(',')[0].split(' as ')[0].strip()
                        for other_dir in key_directories:
                            if other_dir != directory and module.startswith(other_dir):
                                dependencies[directory].add(other_dir)
                                break
                                
            except Exception as e:
                continue
    
    # Report dependencies
    for directory, deps in dependencies.items():
        if deps:
            print(f"   📁 {directory}/ depends on: {', '.join(sorted(deps))}")
        else:
            print(f"   📁 {directory}/ has no cross-directory dependencies")
    
    # Check for circular dependencies at directory level
    circular_deps = []
    for dir1 in dependencies:
        for dir2 in dependencies[dir1]:
            if dir2 in dependencies and dir1 in dependencies[dir2]:
                pair = tuple(sorted([dir1, dir2]))
                if pair not in circular_deps:
                    circular_deps.append(pair)
    
    if circular_deps:
        print("⚠️  Directory-level circular dependencies detected:")
        for dep in circular_deps:
            print(f"     {dep[0]} ↔ {dep[1]}")
    else:
        print("✅ No directory-level circular dependencies")

def main():
    """Main validation function with enhanced codebase validation."""
    import sys

    # Check command line arguments for enhanced mode
    if len(sys.argv) > 1 and sys.argv[1] in ['--enhanced', '-e']:
        print("🚀 Running ENHANCED validation mode...")
        return 0 if validate_entire_codebase_enhanced() else 1
    elif len(sys.argv) > 1 and sys.argv[1] in ['--directory', '-d'] and len(sys.argv) > 2:
        print(f"Running DIRECTORY-SPECIFIC validation for: {sys.argv[2]}")
        directory = sys.argv[2]
        if Path(directory).exists():
            stats = validate_directory_imports(directory)
            success = stats['files_with_issues'] == 0
            return 0 if success else 1
        else:
            print(f"❌ Directory '{directory}' does not exist")
            return 1
    elif len(sys.argv) > 1 and sys.argv[1] in ['--quiet', '-q']:
        print("Running QUIET validation mode (suppressing warnings)...")
        return 0 if validate_entire_codebase() else 1
    elif len(sys.argv) > 1 and sys.argv[1] in ['--warnings-only', '-w']:
        print("Running WARNINGS-ONLY mode...")
        # Create a validator just to show warnings
        validator = ImportValidator(quiet_mode=False)
        validator.validate_all_files()
        validator.print_warning_summary()
        return 0
    elif len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Import Validation Tool")
        print("=" * 40)
        print("Usage:")
        print("  python validate_imports.py           # Basic validation")
        print("  python validate_imports.py -e       # Enhanced validation")
        print("  python validate_imports.py -d DIR   # Directory-specific validation")
        print("  python validate_imports.py -q       # Quiet mode (suppress warnings)")
        print("  python validate_imports.py -w       # Show warnings only")
        print("  python validate_imports.py -h       # Show this help")
        print()
        print("Options:")
        print("  -e, --enhanced       Run enhanced validation with cross-directory analysis")
        print("  -d, --directory      Validate specific directory")
        print("  -q, --quiet          Suppress warning messages")
        print("  -w, --warnings-only  Show only warning summary")
        print("  -h, --help           Show this help message")
        return 0
    else:
        print("Running BASIC validation mode (use -e for enhanced, -h for help)...")
        return 0 if validate_entire_codebase() else 1

if __name__ == "__main__":
    sys.exit(main())
