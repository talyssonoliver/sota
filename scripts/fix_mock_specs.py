#!/usr/bin/env python3
"""
Script to systematically fix mock issues in test files.
Adds spec=True to Mock objects and ensures proper mock verification.
"""
import re
import os
from pathlib import Path
from typing import List, Tuple

def find_mock_issues(file_path: Path) -> List[Tuple[int, str, str]]:
    """Find lines with Mock() that need spec parameter."""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        # Find Mock() without spec
        if re.search(r'Mock\(\s*\)', line) and 'spec=' not in line:
            issues.append((i, line, 'mock_without_spec'))
        
        # Find unused mock parameters
        if re.search(r'def test_\w+\(self.*mock_\w+', line):
            # Check if mock is used in the function
            func_start = i
            func_end = i + 1
            while func_end < len(lines) and not lines[func_end].startswith('def '):
                func_end += 1
            
            func_body = ''.join(lines[func_start:func_end])
            mock_params = re.findall(r'mock_(\w+)', line)
            for mock_param in mock_params:
                if f'mock_{mock_param}' not in func_body[len(line):]:
                    issues.append((i, line, f'unused_mock_{mock_param}'))
    
    return issues

def fix_mock_without_spec(line: str) -> str:
    """Add spec to Mock() calls."""
    # Simple Mock() -> Mock(spec=True)
    if 'Mock()' in line:
        return line.replace('Mock()', 'Mock(spec=True)')
    return line

def analyze_test_files() -> dict:
    """Analyze all test files for mock issues."""
    test_dir = Path('tests')
    report = {
        'files_analyzed': 0,
        'mock_without_spec': 0,
        'unused_mocks': 0,
        'files_with_issues': []
    }
    
    for test_file in test_dir.rglob('*.py'):
        if test_file.name.startswith('test_'):
            report['files_analyzed'] += 1
            issues = find_mock_issues(test_file)
            
            if issues:
                report['files_with_issues'].append(str(test_file))
                for _, _, issue_type in issues:
                    if issue_type == 'mock_without_spec':
                        report['mock_without_spec'] += 1
                    elif issue_type.startswith('unused_mock_'):
                        report['unused_mocks'] += 1
    
    return report

def main():
    """Run the mock fix analysis."""
    print("Analyzing test files for mock issues...")
    report = analyze_test_files()
    
    print(f"\nAnalysis complete:")
    print(f"Files analyzed: {report['files_analyzed']}")
    print(f"Mock() without spec: {report['mock_without_spec']}")
    print(f"Unused mock parameters: {report['unused_mocks']}")
    print(f"Files with issues: {len(report['files_with_issues'])}")
    
    if report['files_with_issues']:
        print("\nFiles needing fixes:")
        for file in sorted(report['files_with_issues'])[:10]:
            print(f"  - {file}")
        
        if len(report['files_with_issues']) > 10:
            print(f"  ... and {len(report['files_with_issues']) - 10} more")
    
    return report

if __name__ == '__main__':
    main()