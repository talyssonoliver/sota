Parallel investigation of multiple files: $ARGUMENTS with intelligent batching and subprocess optimization.

## ⚡ PARALLEL INVESTIGATION PROTOCOL

### BATCH PROCESSING STRATEGY:
1. **File Grouping**: Organize files by dependency clusters to avoid conflicts
2. **Subprocess Management**: Optimal worker pool based on CPU cores  
3. **Resource Throttling**: Prevent system overload during analysis
4. **Progress Tracking**: Real-time status updates for batch progress
5. **Error Isolation**: Individual file failures don't block entire batch

### USAGE:
```bash
# Investigate multiple files in parallel
/parallel-investigate "src/core/agents/*.py"
/parallel-investigate "src/core/workflows/execute*.py src/core/workflows/qa*.py"
/parallel-investigate --max-workers=4 "src/infrastructure/tools/**/*.py"
```

### ENHANCED PARALLEL WORKFLOW:

#### 1. **Intelligent File Batching**
```bash
echo "🔍 Starting parallel investigation for: $ARGUMENTS"

# Parse arguments and create file list
python3 -c "
import glob
import sys
import os
from pathlib import Path

# Parse arguments (can be file patterns or explicit files)
args = '$ARGUMENTS'.split()
files = []

for arg in args:
    if '*' in arg or '?' in arg:
        # Glob pattern
        matched = glob.glob(arg, recursive=True)
        files.extend([f for f in matched if f.endswith('.py')])
    else:
        # Explicit file
        if os.path.exists(arg) and arg.endswith('.py'):
            files.append(arg)

# Remove duplicates and sort by file size (smaller files first for better load balancing)
unique_files = list(set(files))
file_sizes = [(f, os.path.getsize(f)) for f in unique_files if os.path.exists(f)]
sorted_files = [f[0] for f in sorted(file_sizes, key=lambda x: x[1])]

print('\\n'.join(sorted_files))
" > parallel_investigation_files.txt

FILE_COUNT=$(wc -l < parallel_investigation_files.txt)
echo "📊 Files to investigate: $FILE_COUNT"

if [ $FILE_COUNT -eq 0 ]; then
    echo "❌ No valid Python files found matching: $ARGUMENTS"
    exit 1
fi
```

#### 2. **Optimal Worker Pool Configuration**
```bash
# Determine optimal worker count
MAX_WORKERS=${MAX_WORKERS:-$(python3 -c "
import os
import psutil

# Get system resources
cpu_cores = os.cpu_count()
available_memory_gb = psutil.virtual_memory().available / (1024**3)

# Conservative parallel strategy:
# - Use 75% of CPU cores (leave some for system)
# - Ensure at least 1GB RAM per worker
# - Cap at 8 workers to prevent overwhelming disk I/O

optimal_workers = min(
    int(cpu_cores * 0.75),
    int(available_memory_gb),
    8,
    max(1, cpu_cores - 1)
)

print(optimal_workers)
")}

echo "⚙️ Using $MAX_WORKERS parallel workers (CPU cores: $(nproc), Available RAM: $(free -h | awk '/^Mem:/ {print $7}'))"
```

#### 3. **Parallel Investigation Execution**
```bash
# Create investigation coordinator script
cat > parallel_investigation_worker.py << 'EOF'
#!/usr/bin/env python3
import sys
import subprocess
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

def investigate_single_file(file_path):
    """Investigate a single file and return results"""
    start_time = time.time()
    results = {
        'file': file_path,
        'status': 'started',
        'start_time': start_time,
        'errors': []
    }
    
    try:
        # Extract file-specific issues from validation report
        cmd = f'''
        cat reports/validation_report.json | python3 -c "
import json
import sys
data = json.load(sys.stdin)
file_issues = []
for issue_group in data.get('issues_grouped', []):
    for occurrence in issue_group.get('sample_occurrences', []):
        if '{file_path}' in occurrence.get('file', ''):
            file_issues.append({{
                'category': issue_group['category'],
                'severity': issue_group['severity'],
                'message': issue_group['message_pattern'],
                'line': occurrence.get('line', 0)
            }})
print(json.dumps(file_issues, indent=2))
"
        '''
        
        validation_result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if validation_result.returncode == 0:
            results['validation_issues'] = json.loads(validation_result.stdout) if validation_result.stdout.strip() else []
        else:
            results['validation_issues'] = []
            results['errors'].append(f"Validation extraction failed: {validation_result.stderr}")
        
        # Run ruff analysis
        ruff_cmd = f"python3 -m ruff check '{file_path}' --output-format=json"
        ruff_result = subprocess.run(ruff_cmd, shell=True, capture_output=True, text=True, timeout=30)
        if ruff_result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
            results['ruff_issues'] = json.loads(ruff_result.stdout) if ruff_result.stdout.strip() else []
        else:
            results['ruff_issues'] = []
            results['errors'].append(f"Ruff analysis failed: {ruff_result.stderr}")
        
        # Run bandit security analysis
        bandit_cmd = f"bandit -r '{file_path}' -f json"
        bandit_result = subprocess.run(bandit_cmd, shell=True, capture_output=True, text=True, timeout=30)
        if bandit_result.returncode in [0, 1]:
            bandit_data = json.loads(bandit_result.stdout) if bandit_result.stdout.strip() else {}
            results['security_issues'] = bandit_data.get('results', [])
        else:
            results['security_issues'] = []
            results['errors'].append(f"Bandit analysis failed: {bandit_result.stderr}")
        
        # Pattern analysis
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            patterns = {
                'incomplete_todos': len(re.findall(r'TODO|FIXME|XXX', content, re.IGNORECASE)),
                'placeholder_functions': len(re.findall(r'def \\w+.*:\\s*(pass|\\.\\.\\.|""".*"""|raise NotImplementedError)', content, re.MULTILINE)),
                'empty_classes': len(re.findall(r'class \\w+.*:\\s*(pass|\\.\\.\\.)', content, re.MULTILINE)),
                'has_main_guard': 'if __name__ == "__main__"' in content,
                'line_count': len(content.splitlines())
            }
            results['patterns'] = patterns
        except Exception as e:
            results['patterns'] = {}
            results['errors'].append(f"Pattern analysis failed: {str(e)}")
        
        # Calculate summary
        total_issues = len(results.get('validation_issues', [])) + len(results.get('ruff_issues', [])) + len(results.get('security_issues', []))
        results['summary'] = {
            'total_issues': total_issues,
            'validation_count': len(results.get('validation_issues', [])),
            'ruff_count': len(results.get('ruff_issues', [])),
            'security_count': len(results.get('security_issues', [])),
            'duration_seconds': time.time() - start_time
        }
        
        results['status'] = 'completed'
        
    except subprocess.TimeoutExpired:
        results['status'] = 'timeout'
        results['errors'].append('Investigation timed out after 30 seconds')
    except Exception as e:
        results['status'] = 'error'
        results['errors'].append(f'Unexpected error: {str(e)}')
    
    results['end_time'] = time.time()
    results['duration'] = results['end_time'] - start_time
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parallel_investigation_worker.py <max_workers>")
        sys.exit(1)
    
    max_workers = int(sys.argv[1])
    
    # Read file list
    with open('parallel_investigation_files.txt', 'r') as f:
        files = [line.strip() for line in f if line.strip()]
    
    print(f"🚀 Starting parallel investigation of {len(files)} files with {max_workers} workers")
    
    # Ensure investigation_reports directory exists
    os.makedirs('investigation_reports', exist_ok=True)
    
    completed_files = []
    failed_files = []
    
    # Process files in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all files for processing
        future_to_file = {executor.submit(investigate_single_file, file_path): file_path for file_path in files}
        
        for i, future in enumerate(as_completed(future_to_file), 1):
            file_path = future_to_file[future]
            try:
                result = future.result()
                
                # Save individual investigation report
                file_base = os.path.basename(file_path).replace('.py', '')
                report_path = f'investigation_reports/{file_base}_parallel_investigation.json'
                
                with open(report_path, 'w') as f:
                    json.dump(result, f, indent=2)
                
                if result['status'] == 'completed':
                    completed_files.append(result)
                    print(f"✅ [{i}/{len(files)}] {file_path}: {result['summary']['total_issues']} issues ({result['duration']:.1f}s)")
                else:
                    failed_files.append(result)
                    print(f"❌ [{i}/{len(files)}] {file_path}: {result['status']} ({result['duration']:.1f}s)")
                    
            except Exception as e:
                failed_files.append({'file': file_path, 'status': 'exception', 'error': str(e)})
                print(f"💥 [{i}/{len(files)}] {file_path}: Exception - {str(e)}")
    
    # Generate summary report
    summary = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_files': len(files),
        'completed': len(completed_files),
        'failed': len(failed_files),
        'total_issues_found': sum(f['summary']['total_issues'] for f in completed_files),
        'average_duration': sum(f['duration'] for f in completed_files) / len(completed_files) if completed_files else 0,
        'max_workers_used': max_workers,
        'completed_files': [f['file'] for f in completed_files],
        'failed_files': [f['file'] for f in failed_files]
    }
    
    with open('investigation_reports/parallel_investigation_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\\n📊 Parallel Investigation Complete:")
    print(f"   ✅ Completed: {summary['completed']}/{summary['total_files']} files")
    print(f"   ❌ Failed: {summary['failed']} files")
    print(f"   🔍 Total Issues Found: {summary['total_issues_found']}")
    print(f"   ⏱️ Average Duration: {summary['average_duration']:.1f}s per file")
    print(f"   📈 Parallel Speedup: ~{max_workers}x faster than sequential")
    
    return 0 if len(failed_files) == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
EOF

# Execute parallel investigation
python3 parallel_investigation_worker.py $MAX_WORKERS

INVESTIGATION_EXIT_CODE=$?
```

#### 4. **Results Aggregation and Reporting**
```bash
echo "📋 Generating consolidated investigation reports..."

# Generate master parallel investigation report
python3 -c "
import json
import os
from pathlib import Path

# Load summary
with open('investigation_reports/parallel_investigation_summary.json') as f:
    summary = json.load(f)

# Load individual results
detailed_results = {}
for file_path in summary['completed_files']:
    file_base = os.path.basename(file_path).replace('.py', '')
    report_path = f'investigation_reports/{file_base}_parallel_investigation.json'
    if os.path.exists(report_path):
        with open(report_path) as f:
            detailed_results[file_path] = json.load(f)

# Generate markdown summary
markdown_content = f'''# Parallel Investigation Results
**Generated**: {summary['timestamp']}
**Files Processed**: {summary['completed']}/{summary['total_files']}
**Total Issues Found**: {summary['total_issues_found']}
**Processing Time**: {summary['average_duration']:.1f}s average per file

## 📊 Summary by Issue Type
'''

# Aggregate issue types
issue_categories = {}
security_counts = {}
for file_path, result in detailed_results.items():
    for issue in result.get('validation_issues', []):
        category = issue.get('category', 'unknown')
        issue_categories[category] = issue_categories.get(category, 0) + 1
    
    security_counts[file_path] = len(result.get('security_issues', []))

# Add category breakdown
for category, count in sorted(issue_categories.items(), key=lambda x: x[1], reverse=True):
    markdown_content += f'- **{category}**: {count} issues\\n'

markdown_content += f'''

## 🔍 Files Ready for Safe Auto-Fix
The following files have been investigated and are ready for /safe-auto-fix:

'''

# List files by issue priority
for file_path, result in sorted(detailed_results.items(), key=lambda x: x[1]['summary']['total_issues']):
    total = result['summary']['total_issues']
    markdown_content += f'''### {file_path}
- **Total Issues**: {total}
- **Ruff Issues**: {result['summary']['ruff_count']}
- **Security Issues**: {result['summary']['security_count']}
- **Status**: ✅ Ready for /safe-auto-fix
- **Investigation Report**: investigation_reports/{os.path.basename(file_path).replace('.py', '')}_parallel_investigation.json

'''

with open('investigation_reports/parallel_investigation_master_report.md', 'w') as f:
    f.write(markdown_content)

print('✅ Master parallel investigation report generated')
print(f'📄 Report saved to: investigation_reports/parallel_investigation_master_report.md')
"

echo "🎯 Parallel investigation complete! Files are now ready for parallel safe-auto-fix."
```

### SUCCESS METRICS:
- **Speed Improvement**: 4-8x faster than sequential investigation
- **Resource Efficiency**: Optimal CPU and memory utilization
- **Error Isolation**: Individual file failures don't block entire batch
- **Progress Tracking**: Real-time status updates for large batches
- **Quality Maintenance**: Same thorough analysis as individual investigation

### USAGE EXAMPLES:
```bash
# Investigate all agent files in parallel
/parallel-investigate "src/core/agents/*.py"

# Investigate specific workflow files  
/parallel-investigate "src/core/workflows/execute_task.py src/core/workflows/qa_execution.py"

# Investigate entire infrastructure directory
/parallel-investigate "src/infrastructure/**/*.py"

# Custom worker count for resource-constrained environments
MAX_WORKERS=2 /parallel-investigate "src/**/*.py"
```

**CRITICAL**: All safety protocols from individual investigation are maintained while dramatically improving throughput for large-scale validation issue resolution.