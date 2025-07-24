#!/usr/bin/env python3
import ast
import sys
from collections import defaultdict
import json

def analyze_file_dependencies(file_paths):
    """Analyze import dependencies between files to prevent parallel conflicts"""
    
    dependencies = defaultdict(set)  # file -> set of files it imports from
    reverse_deps = defaultdict(set)  # file -> set of files that import it
    
    # Create module name mapping
    file_to_module = {}
    for file_path in file_paths:
        # Convert file path to module path
        rel_path = file_path.replace('src/', '').replace('/', '.').replace('.py', '')
        file_to_module[file_path] = rel_path
    
    # Analyze imports in each file
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name
                        # Check if this import refers to another file in our list
                        for other_file, other_module in file_to_module.items():
                            if other_file != file_path and module_name.startswith(other_module):
                                dependencies[file_path].add(other_file)
                                reverse_deps[other_file].add(file_path)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module
                        for other_file, other_module in file_to_module.items():
                            if other_file != file_path and module_name.startswith(other_module):
                                dependencies[file_path].add(other_file)
                                reverse_deps[other_file].add(file_path)
        
        except Exception as e:
            print(f"Warning: Could not analyze dependencies for {file_path}: {e}", file=sys.stderr)
    
    return dependencies, reverse_deps

def create_parallel_groups(file_paths, dependencies):
    """Group files into parallel-safe batches"""
    
    # Files with no dependencies can be processed in parallel
    independent_files = []
    dependent_files = []
    
    for file_path in file_paths:
        if not dependencies[file_path]:
            independent_files.append(file_path)
        else:
            dependent_files.append(file_path)
    
    # Create batches
    batches = []
    
    # Batch 1: All independent files (can run in parallel)
    if independent_files:
        batches.append({
            'type': 'parallel',
            'files': independent_files,
            'description': 'Independent files (no internal dependencies)'
        })
    
    # Batch 2+: Dependent files (process in dependency order)
    if dependent_files:
        # For simplicity, process dependent files sequentially
        # TODO: Could implement topological sort for better parallelization
        batches.append({
            'type': 'sequential',
            'files': dependent_files,
            'description': 'Files with internal dependencies (sequential processing)'
        })
    
    return batches

def main():
    # Read file list
    with open('parallel_safe_fix_files.txt', 'r') as f:
        files = [line.strip() for line in f if line.strip()]
    
    print(f"🔍 Analyzing dependencies for {len(files)} files...")
    
    dependencies, reverse_deps = analyze_file_dependencies(files)
    batches = create_parallel_groups(files, dependencies)
    
    # Save analysis results
    analysis_result = {
        'total_files': len(files),
        'dependencies': {k: list(v) for k, v in dependencies.items()},
        'reverse_dependencies': {k: list(v) for k, v in reverse_deps.items()},
        'parallel_batches': batches,
        'conflict_risk': len([f for f in files if dependencies[f]]) > 0
    }
    
    with open('parallel_dependency_analysis.json', 'w') as f:
        json.dump(analysis_result, f, indent=2)
    
    print("📊 Dependency Analysis Complete:")
    print(f"   📦 Total Batches: {len(batches)}")
    for i, batch in enumerate(batches, 1):
        print(f"   Batch {i} ({batch['type']}): {len(batch['files'])} files - {batch['description']}")
    
    if analysis_result['conflict_risk']:
        print("⚠️ Dependency conflicts detected - using batch processing strategy")
    else:
        print("✅ No dependency conflicts - full parallel processing available")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())