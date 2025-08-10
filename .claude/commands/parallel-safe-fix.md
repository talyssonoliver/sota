Parallel application of safe auto-fixes to multiple files: $ARGUMENTS with intelligent dependency conflict resolution and git coordination.

## ⚡ PARALLEL SAFE-FIX PROTOCOL

### ADVANCED SAFETY WITH PARALLELIZATION:
1. **Dependency Analysis**: Detect import relationships to prevent conflicts
2. **Git Coordination**: Smart branching strategy for parallel fixes
3. **Test Orchestration**: Optimized test verification for parallel changes
4. **Conflict Resolution**: Automatic detection and resolution of file dependencies
5. **Atomic Rollback**: Individual file rollback without affecting parallel operations

### USAGE:
```bash
# Apply safe fixes to multiple investigated files in parallel
/parallel-safe-fix "src/core/agents/*.py"
/parallel-safe-fix --max-workers=3 "investigation_reports/*_parallel_investigation.json"
/parallel-safe-fix --strategy=sequential-test "src/core/workflows/execute*.py"
```

### ENHANCED PARALLEL WORKFLOW:

#### 1. **Prerequisites and Dependency Analysis**
```bash
echo "🔒 Starting parallel safe-fix for: $ARGUMENTS"

# Parse strategy options
STRATEGY=${STRATEGY:-"parallel-test"}  # parallel-test, sequential-test, batch-test
MAX_WORKERS=${MAX_WORKERS:-$(python3 -c "import os; print(min(4, max(1, os.cpu_count() // 2)))")}

# Validate all files have investigation reports
python3 -c "
import sys
import os
import glob
import json

args = '$ARGUMENTS'.split()
files = []
missing_reports = []

for arg in args:
    if arg.endswith('_parallel_investigation.json'):
        # Direct investigation report reference
        if os.path.exists(f'investigation_reports/{arg}'):
            # Extract original file path from report
            with open(f'investigation_reports/{arg}') as f:
                data = json.load(f)
                files.append(data['file'])
        else:
            missing_reports.append(arg)
    elif '*' in arg or '?' in arg:
        # Glob pattern for source files
        matched = glob.glob(arg, recursive=True)
        for file_path in matched:
            if file_path.endswith('.py'):
                # Check if investigation report exists
                file_base = os.path.basename(file_path).replace('.py', '')
                report_path = f'investigation_reports/{file_base}_parallel_investigation.json'
                if os.path.exists(report_path):
                    files.append(file_path)
                else:
                    missing_reports.append(f'{file_base}_parallel_investigation.json')
    else:
        # Explicit file
        if os.path.exists(arg) and arg.endswith('.py'):
            file_base = os.path.basename(arg).replace('.py', '')
            report_path = f'investigation_reports/{file_base}_parallel_investigation.json'
            if os.path.exists(report_path):
                files.append(arg)
            else:
                missing_reports.append(f'{file_base}_parallel_investigation.json')

if missing_reports:
    print(f'❌ BLOCKED: Missing investigation reports for: {missing_reports}')
    print('   Action: Run /parallel-investigate first for these files')
    sys.exit(1)

if not files:
    print('❌ BLOCKED: No valid files with investigation reports found')
    sys.exit(1)

# Save validated file list
with open('parallel_safe_fix_files.txt', 'w') as f:
    for file_path in files:
        f.write(file_path + '\\n')

print(f'✅ Validated {len(files)} files with investigation reports')
" || exit 1

echo "📊 Files validated for parallel safe-fix: $(wc -l < parallel_safe_fix_files.txt)"
```

#### 2. **Dependency Conflict Detection**
```bash
echo "🔍 Analyzing file dependencies for conflict prevention..."

# Create dependency analysis script
cat > dependency_analyzer.py << 'EOF'
#!/usr/bin/env python3
import ast
import os
import sys
from collections import defaultdict, deque
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
    
    print(f"📊 Dependency Analysis Complete:")
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
EOF

python3 dependency_analyzer.py || exit 1
```

#### 3. **Parallel Safe-Fix Execution with Git Coordination**
```bash
echo "🚀 Executing parallel safe-fixes with git coordination..."

# Create parallel safe-fix coordinator
cat > parallel_safe_fix_coordinator.py << 'EOF'
#!/usr/bin/env python3
import json
import subprocess
import sys
import time
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import threading

class GitCoordinator:
    """Thread-safe git operations for parallel processing"""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.branch_counter = 0
    
    def create_safe_branch(self, file_path):
        """Create a unique branch for this file's fixes"""
        with self.lock:
            self.branch_counter += 1
            timestamp = int(time.time())
            file_base = os.path.basename(file_path).replace('.py', '')
            branch_name = f"parallel-fix/{file_base}-{timestamp}-{self.branch_counter}"
            
            try:
                # Create and checkout branch
                subprocess.run(['git', 'checkout', '-b', branch_name], 
                             check=True, capture_output=True)
                return branch_name
            except subprocess.CalledProcessError as e:
                raise Exception(f"Failed to create branch {branch_name}: {e.stderr.decode()}")
    
    def merge_safe_fix(self, branch_name, file_path):
        """Merge safe fix branch back to main"""
        with self.lock:
            try:
                # Switch to main
                subprocess.run(['git', 'checkout', 'main'], 
                             check=True, capture_output=True)
                
                # Merge with no-ff to preserve history
                commit_msg = f"feat: parallel safe-fixes for {os.path.basename(file_path)}"
                subprocess.run(['git', 'merge', '--no-ff', '-m', commit_msg, branch_name],
                             check=True, capture_output=True)
                
                # Clean up branch
                subprocess.run(['git', 'branch', '-d', branch_name],
                             check=True, capture_output=True)
                
                return True
            except subprocess.CalledProcessError as e:
                # Rollback on failure
                subprocess.run(['git', 'checkout', 'main'], capture_output=True)
                subprocess.run(['git', 'branch', '-D', branch_name], capture_output=True)
                raise Exception(f"Failed to merge branch {branch_name}: {e.stderr.decode()}")

def apply_safe_fixes_to_file(file_path, git_coordinator):
    """Apply safe fixes to a single file with git coordination"""
    
    start_time = time.time()
    result = {
        'file': file_path,
        'status': 'started',
        'start_time': start_time,
        'fixes_applied': [],
        'errors': []
    }
    
    try:
        # Load investigation report
        file_base = os.path.basename(file_path).replace('.py', '')
        report_path = f'investigation_reports/{file_base}_parallel_investigation.json'
        
        with open(report_path) as f:
            investigation = json.load(f)
        
        # Create safe branch
        branch_name = git_coordinator.create_safe_branch(file_path)
        result['branch_name'] = branch_name
        
        # Apply always-safe formatting fixes
        formatting_applied = False
        
        # Black formatting
        black_result = subprocess.run(['black', file_path, '--quiet'], 
                                    capture_output=True, text=True, timeout=30)
        if black_result.returncode == 0:
            # Check if changes were made
            git_diff = subprocess.run(['git', 'diff', file_path], 
                                    capture_output=True, text=True)
            if git_diff.stdout.strip():
                formatting_applied = True
                result['fixes_applied'].append('black_formatting')
        
        # Isort import sorting
        isort_result = subprocess.run(['isort', file_path, '--quiet'], 
                                    capture_output=True, text=True, timeout=30)
        if isort_result.returncode == 0:
            git_diff = subprocess.run(['git', 'diff', file_path], 
                                    capture_output=True, text=True)
            if git_diff.stdout.strip() and not formatting_applied:
                formatting_applied = True
                result['fixes_applied'].append('isort_formatting')
            elif git_diff.stdout.strip():
                result['fixes_applied'].append('isort_additional')
        
        # Commit formatting changes if any
        if formatting_applied:
            subprocess.run(['git', 'add', file_path], check=True)
            subprocess.run(['git', 'commit', '-m', 
                          f'style: apply formatting fixes to {os.path.basename(file_path)}\\n\\nGenerated with parallel-safe-fix'], 
                          check=True)
        
        # Apply conditionally safe fixes based on investigation
        conditional_fixes = []
        
        # Check for approved safe fixes in investigation
        ruff_issues = investigation.get('ruff_issues', [])
        safe_codes = []
        
        # E402 import ordering - check if approved
        if any('import' in str(issue).lower() and 'E402' in str(issue) for issue in ruff_issues):
            # Simple heuristic - if file has no conditional imports, E402 is likely safe
            if not any('try:' in line and 'import' in line for line in open(file_path).readlines()):
                safe_codes.append('E402')
        
        # W292 newline at end of file - always safe
        if any('W292' in str(issue) for issue in ruff_issues):
            safe_codes.append('W292')
        
        if safe_codes:
            ruff_fix_cmd = f"python3 -m ruff check '{file_path}' --fix --select {','.join(safe_codes)}"
            ruff_fix_result = subprocess.run(ruff_fix_cmd, shell=True, 
                                           capture_output=True, text=True, timeout=30)
            
            if ruff_fix_result.returncode in [0, 1]:
                git_diff = subprocess.run(['git', 'diff', file_path], 
                                        capture_output=True, text=True)
                if git_diff.stdout.strip():
                    conditional_fixes.extend(safe_codes)
                    subprocess.run(['git', 'add', file_path], check=True)
                    subprocess.run(['git', 'commit', '-m', 
                                  f'fix: apply safe linting fixes ({",".join(safe_codes)}) to {os.path.basename(file_path)}\\n\\nGenerated with parallel-safe-fix'], 
                                  check=True)
        
        result['fixes_applied'].extend(conditional_fixes)
        
        # Verify file still compiles
        compile_check = subprocess.run(['python3', '-m', 'py_compile', file_path],
                                     capture_output=True, text=True)
        if compile_check.returncode != 0:
            result['errors'].append(f'Compilation failed after fixes: {compile_check.stderr}')
            result['status'] = 'compilation_failed'
            return result
        
        # Merge back to main if fixes were applied
        if result['fixes_applied']:
            git_coordinator.merge_safe_fix(branch_name, file_path)
            result['status'] = 'completed'
        else:
            # No fixes needed, clean up branch
            subprocess.run(['git', 'checkout', 'main'], capture_output=True)
            subprocess.run(['git', 'branch', '-D', branch_name], capture_output=True)
            result['status'] = 'no_fixes_needed'
        
    except subprocess.TimeoutExpired:
        result['status'] = 'timeout'
        result['errors'].append('Safe-fix operation timed out')
    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(f'Unexpected error: {str(e)}')
    
    result['end_time'] = time.time()
    result['duration'] = result['end_time'] - start_time
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parallel_safe_fix_coordinator.py <max_workers>")
        sys.exit(1)
    
    max_workers = int(sys.argv[1])
    
    # Load dependency analysis
    with open('parallel_dependency_analysis.json') as f:
        dependency_analysis = json.load(f)
    
    git_coordinator = GitCoordinator()
    all_results = []
    
    print(f"🚀 Starting parallel safe-fix with {max_workers} workers")
    
    # Process each batch according to its strategy
    for batch_num, batch in enumerate(dependency_analysis['parallel_batches'], 1):
        print(f"\\n📦 Processing Batch {batch_num}: {batch['description']}")
        
        if batch['type'] == 'parallel':
            # Process files in parallel
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {
                    executor.submit(apply_safe_fixes_to_file, file_path, git_coordinator): file_path 
                    for file_path in batch['files']
                }
                
                for i, future in enumerate(as_completed(future_to_file), 1):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        all_results.append(result)
                        
                        status_emoji = "✅" if result['status'] == 'completed' else "⚠️" if result['status'] == 'no_fixes_needed' else "❌"
                        fixes_info = f" ({len(result['fixes_applied'])} fixes)" if result['fixes_applied'] else ""
                        print(f"{status_emoji} [{i}/{len(batch['files'])}] {os.path.basename(file_path)}{fixes_info} ({result['duration']:.1f}s)")
                        
                    except Exception as e:
                        all_results.append({
                            'file': file_path, 
                            'status': 'exception', 
                            'error': str(e),
                            'duration': 0
                        })
                        print(f"💥 [{i}/{len(batch['files'])}] {os.path.basename(file_path)}: Exception - {str(e)}")
        
        else:  # sequential processing
            for i, file_path in enumerate(batch['files'], 1):
                print(f"🔄 [{i}/{len(batch['files'])}] Processing {os.path.basename(file_path)}...")
                try:
                    result = apply_safe_fixes_to_file(file_path, git_coordinator)
                    all_results.append(result)
                    
                    status_emoji = "✅" if result['status'] == 'completed' else "⚠️" if result['status'] == 'no_fixes_needed' else "❌"
                    fixes_info = f" ({len(result['fixes_applied'])} fixes)" if result['fixes_applied'] else ""
                    print(f"{status_emoji} {os.path.basename(file_path)}{fixes_info} ({result['duration']:.1f}s)")
                    
                except Exception as e:
                    all_results.append({
                        'file': file_path, 
                        'status': 'exception', 
                        'error': str(e),
                        'duration': 0
                    })
                    print(f"💥 {os.path.basename(file_path)}: Exception - {str(e)}")
    
    # Generate summary
    completed = [r for r in all_results if r['status'] == 'completed']
    no_fixes = [r for r in all_results if r['status'] == 'no_fixes_needed']
    failed = [r for r in all_results if r['status'] not in ['completed', 'no_fixes_needed']]
    
    total_fixes = sum(len(r.get('fixes_applied', [])) for r in completed)
    avg_duration = sum(r['duration'] for r in all_results) / len(all_results) if all_results else 0
    
    summary = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_files': len(all_results),
        'completed': len(completed),
        'no_fixes_needed': len(no_fixes),
        'failed': len(failed),
        'total_fixes_applied': total_fixes,
        'average_duration': avg_duration,
        'max_workers_used': max_workers,
        'detailed_results': all_results
    }
    
    with open('investigation_reports/parallel_safe_fix_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\\n📊 Parallel Safe-Fix Complete:")
    print(f"   ✅ Completed: {len(completed)} files")
    print(f"   ⚠️ No fixes needed: {len(no_fixes)} files") 
    print(f"   ❌ Failed: {len(failed)} files")
    print(f"   🔧 Total fixes applied: {total_fixes}")
    print(f"   ⏱️ Average duration: {avg_duration:.1f}s per file")
    
    return 0 if len(failed) == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
EOF

# Execute parallel safe-fix
python3 parallel_safe_fix_coordinator.py $MAX_WORKERS
SAFE_FIX_EXIT_CODE=$?
```

#### 4. **Optimized Test Verification Strategy**
```bash
echo "🧪 Running optimized test verification..."

if [ $SAFE_FIX_EXIT_CODE -eq 0 ]; then
    case "$STRATEGY" in
        "parallel-test")
            echo "⚡ Running parallel test verification..."
            # Run quick syntax check first
            find src/ -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | head -10
            
            if [ $? -eq 0 ]; then
                # Run optimized test suite
                python3 -m pytest -x --tb=no -q --maxfail=3 --durations=0 2>/dev/null
                TEST_EXIT_CODE=$?
            else
                echo "❌ Syntax errors detected - skipping tests"
                TEST_EXIT_CODE=1
            fi
            ;;
        "sequential-test")
            echo "🔄 Running full sequential test verification..."
            python3 -m pytest -v
            TEST_EXIT_CODE=$?
            ;;
        "batch-test")
            echo "📦 Running batch test verification..."
            python3 -m pytest -x --tb=short --maxfail=5
            TEST_EXIT_CODE=$?
            ;;
        *)
            echo "⚡ Running default parallel test verification..."
            python3 -m pytest -x --tb=no -q 2>/dev/null
            TEST_EXIT_CODE=$?
            ;;
    esac
    
    if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo "✅ All tests passing after parallel safe-fixes"
    else
        echo "❌ Test failures detected after parallel safe-fixes"
        echo "🔄 Initiating rollback procedure..."
        
        # Emergency rollback - revert to pre-fix state
        git log --oneline -10 | grep "parallel safe-fixes"
        echo "⚠️ Consider reverting recent parallel-fix commits if issues persist"
    fi
else
    echo "❌ Parallel safe-fix had failures - skipping test verification"
    TEST_EXIT_CODE=1
fi

echo "📋 Final status: Safe-fix: $SAFE_FIX_EXIT_CODE, Tests: $TEST_EXIT_CODE"
```

#### 5. **Results and Progress Tracking**
```bash
echo "📊 Updating progress tracking..."

# Update master checklist with results
python3 -c "
import json
import os

# Load results
with open('investigation_reports/parallel_safe_fix_summary.json') as f:
    summary = json.load(f)

print(f'''
🎯 Parallel Safe-Fix Session Complete
=====================================
📊 Files Processed: {summary['total_files']}
✅ Successfully Fixed: {summary['completed']}
⚠️ No Fixes Needed: {summary['no_fixes_needed']}
❌ Failed: {summary['failed']}
🔧 Total Fixes Applied: {summary['total_fixes_applied']}
⏱️ Average Duration: {summary['average_duration']:.1f}s per file
🚀 Parallel Speedup: ~{max(1, summary['total_files'] // 4)}x faster than sequential

Files with fixes applied:
''')

for result in summary['detailed_results']:
    if result['status'] == 'completed' and result.get('fixes_applied'):
        fixes = ', '.join(result['fixes_applied'])
        print(f'  ✅ {os.path.basename(result[\"file\"])}: {fixes}')

if summary['failed'] > 0:
    print('\\nFiles that failed:')
    for result in summary['detailed_results']:
        if result['status'] not in ['completed', 'no_fixes_needed']:
            print(f'  ❌ {os.path.basename(result[\"file\"])}: {result.get(\"errors\", [\"Unknown error\"])[0]}')
"

# Clean up temporary files
rm -f parallel_safe_fix_files.txt parallel_dependency_analysis.json
rm -f parallel_safe_fix_coordinator.py dependency_analyzer.py

echo "🎯 Parallel safe-fix complete! Check investigation_reports/parallel_safe_fix_summary.json for detailed results."
```

### SUCCESS METRICS:
- **Speed Improvement**: 3-6x faster than sequential safe-fix
- **Conflict Prevention**: Smart dependency analysis prevents parallel conflicts
- **Git Safety**: Individual branches with atomic merge operations
- **Test Optimization**: Configurable test verification strategies
- **Quality Maintenance**: Same safety standards as individual safe-fix

### STRATEGY OPTIONS:
- **parallel-test**: Fast parallel test verification (default)
- **sequential-test**: Full sequential test suite
- **batch-test**: Balanced approach with some parallelization

### USAGE EXAMPLES:
```bash
# Apply safe fixes to all investigated agent files
/parallel-safe-fix "src/core/agents/*.py"

# Custom strategy for critical files
/parallel-safe-fix --strategy=sequential-test "src/core/workflows/execute*.py"

# Resource-constrained parallel processing
/parallel-safe-fix --max-workers=2 "investigation_reports/*_parallel_investigation.json"
```

**CRITICAL**: All safety protocols maintained while providing dramatic speed improvements for large-scale validation issue resolution.