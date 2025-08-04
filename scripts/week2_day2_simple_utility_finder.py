#!/usr/bin/env python3
"""
Week 2 Day 2: Simple Utility Function Finder
Find duplicate utility functions using pattern matching
"""

import os
import re
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json


class SimpleUtilityFinder:
    def __init__(self):
        self.src_path = Path("src")
        self.utility_patterns = {
            'logging': [
                r'def\s+setup_logging\s*\(',
                r'def\s+get_logger\s*\(',
                r'def\s+create_logger\s*\(',
                r'def\s+configure_logging\s*\(',
            ],
            'config': [
                r'def\s+load_config\s*\(',
                r'def\s+save_config\s*\(',
                r'def\s+read_config\s*\(',
                r'def\s+get_config\s*\(',
                r'def\s+update_config\s*\(',
            ],
            'validation': [
                r'def\s+validate_\w+\s*\(',
                r'def\s+check_\w+\s*\(',
                r'def\s+is_valid_\w+\s*\(',
                r'def\s+verify_\w+\s*\(',
            ],
            'file_ops': [
                r'def\s+read_file\s*\(',
                r'def\s+write_file\s*\(',
                r'def\s+load_json\s*\(',
                r'def\s+save_json\s*\(',
                r'def\s+load_yaml\s*\(',
                r'def\s+save_yaml\s*\(',
                r'def\s+ensure_directory\s*\(',
                r'def\s+create_directory\s*\(',
            ],
            'time_id': [
                r'def\s+get_timestamp\s*\(',
                r'def\s+generate_id\s*\(',
                r'def\s+create_id\s*\(',
                r'def\s+generate_uuid\s*\(',
                r'def\s+get_current_time\s*\(',
            ],
            'string_ops': [
                r'def\s+normalize_\w+\s*\(',
                r'def\s+sanitize_\w+\s*\(',
                r'def\s+clean_\w+\s*\(',
                r'def\s+format_\w+\s*\(',
                r'def\s+parse_\w+\s*\(',
            ],
            'error_handling': [
                r'def\s+safe_\w+\s*\(',
                r'def\s+retry_\w+\s*\(',
                r'def\s+with_retry\s*\(',
                r'def\s+handle_error\s*\(',
                r'def\s+log_error\s*\(',
            ],
            'crypto': [
                r'def\s+hash_\w+\s*\(',
                r'def\s+encrypt_\w+\s*\(',
                r'def\s+decrypt_\w+\s*\(',
                r'def\s+generate_key\s*\(',
                r'def\s+verify_signature\s*\(',
            ]
        }
        
    def find_functions(self, file_path: Path, category: str, patterns: List[str]) -> List[Dict]:
        """Find functions matching patterns in a file"""
        functions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    # Get function name
                    func_match = re.search(r'def\s+(\w+)', match.group())
                    if func_match:
                        func_name = func_match.group(1)
                        
                        # Get line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Try to get the full function (simple approach)
                        lines = content.split('\n')
                        func_lines = []
                        indent_level = None
                        
                        for i in range(line_num - 1, min(line_num + 50, len(lines))):
                            line = lines[i]
                            if i == line_num - 1:
                                # First line - determine indent
                                indent_level = len(line) - len(line.lstrip())
                                func_lines.append(line)
                            elif line.strip() == '':
                                func_lines.append(line)
                            elif line.startswith(' ' * (indent_level + 1)) or line.startswith('\t'):
                                func_lines.append(line)
                            else:
                                # End of function
                                break
                        
                        functions.append({
                            'name': func_name,
                            'file': str(file_path),
                            'line': line_num,
                            'category': category,
                            'lines': len(func_lines),
                            'preview': '\n'.join(func_lines[:5]) + ('...' if len(func_lines) > 5 else '')
                        })
                        
        except Exception as e:
            pass  # Silently skip files with issues
        
        return functions
    
    def analyze_codebase(self) -> Dict[str, any]:
        """Analyze codebase for utility functions"""
        print("🔍 Searching for utility functions by pattern...")
        
        results = {
            'categories': defaultdict(list),
            'duplicates': defaultdict(list),
            'summary': {}
        }
        
        python_files = list(self.src_path.rglob("*.py"))
        
        # Find all utility functions by category
        for category, patterns in self.utility_patterns.items():
            print(f"  Searching for {category} utilities...")
            for file_path in python_files:
                functions = self.find_functions(file_path, category, patterns)
                results['categories'][category].extend(functions)
        
        # Find duplicates by function name
        all_functions = []
        for category_funcs in results['categories'].values():
            all_functions.extend(category_funcs)
        
        name_groups = defaultdict(list)
        for func in all_functions:
            name_groups[func['name']].append(func)
        
        # Store duplicates
        for name, funcs in name_groups.items():
            if len(funcs) > 1:
                results['duplicates'][name] = funcs
        
        # Calculate summary
        results['summary'] = {
            'total_utility_functions': len(all_functions),
            'unique_function_names': len(name_groups),
            'duplicate_function_names': len(results['duplicates']),
            'total_duplicate_instances': sum(len(funcs) for funcs in results['duplicates'].values()),
            'categories': {
                cat: len(funcs) for cat, funcs in results['categories'].items()
            }
        }
        
        return results
    
    def generate_consolidation_plan(self, results: Dict) -> List[Dict]:
        """Generate specific consolidation plan"""
        plan = []
        
        # 1. Logging utilities
        logging_funcs = results['categories'].get('logging', [])
        if logging_funcs:
            unique_files = set(f['file'] for f in logging_funcs)
            plan.append({
                'module': 'src/infrastructure/utils/logging_utils.py',
                'description': 'Centralized logging utilities',
                'functions_to_consolidate': [
                    'setup_logging', 'get_logger', 'create_logger', 
                    'configure_logging'
                ],
                'affected_files': len(unique_files),
                'instances': len(logging_funcs),
                'estimated_savings': len(logging_funcs) * 20 - 100  # avg 20 lines per func
            })
        
        # 2. Configuration utilities
        config_funcs = results['categories'].get('config', [])
        if config_funcs:
            unique_files = set(f['file'] for f in config_funcs)
            plan.append({
                'module': 'src/infrastructure/utils/config_utils.py',
                'description': 'Configuration management utilities',
                'functions_to_consolidate': [
                    'load_config', 'save_config', 'read_config',
                    'get_config', 'update_config'
                ],
                'affected_files': len(unique_files),
                'instances': len(config_funcs),
                'estimated_savings': len(config_funcs) * 25 - 150
            })
        
        # 3. File operations
        file_funcs = results['categories'].get('file_ops', [])
        if file_funcs:
            unique_files = set(f['file'] for f in file_funcs)
            plan.append({
                'module': 'src/infrastructure/utils/file_utils.py',
                'description': 'File and directory operations',
                'functions_to_consolidate': [
                    'read_file', 'write_file', 'load_json', 'save_json',
                    'load_yaml', 'save_yaml', 'ensure_directory'
                ],
                'affected_files': len(unique_files),
                'instances': len(file_funcs),
                'estimated_savings': len(file_funcs) * 15 - 100
            })
        
        # 4. Validation utilities
        validation_funcs = results['categories'].get('validation', [])
        if validation_funcs:
            unique_files = set(f['file'] for f in validation_funcs)
            plan.append({
                'module': 'src/infrastructure/utils/validation_utils.py',
                'description': 'Input validation and checking utilities',
                'functions_to_consolidate': [
                    'validate_*', 'check_*', 'is_valid_*', 'verify_*'
                ],
                'affected_files': len(unique_files),
                'instances': len(validation_funcs),
                'estimated_savings': len(validation_funcs) * 30 - 200
            })
        
        # 5. Time and ID utilities
        time_funcs = results['categories'].get('time_id', [])
        if time_funcs:
            unique_files = set(f['file'] for f in time_funcs)
            plan.append({
                'module': 'src/infrastructure/utils/time_id_utils.py',
                'description': 'Timestamp and ID generation utilities',
                'functions_to_consolidate': [
                    'get_timestamp', 'generate_id', 'create_id',
                    'generate_uuid', 'get_current_time'
                ],
                'affected_files': len(unique_files),
                'instances': len(time_funcs),
                'estimated_savings': len(time_funcs) * 10 - 50
            })
        
        return plan
    
    def generate_report(self, results: Dict, plan: List[Dict]) -> str:
        """Generate comprehensive report"""
        report = f"""# Week 2 Day 2: Utility Function Analysis Report

## 📊 Summary
- **Total Utility Functions Found:** {results['summary']['total_utility_functions']}
- **Unique Function Names:** {results['summary']['unique_function_names']}
- **Duplicate Function Names:** {results['summary']['duplicate_function_names']}
- **Total Duplicate Instances:** {results['summary']['total_duplicate_instances']}

## 📁 Functions by Category
"""
        
        for category, count in results['summary']['categories'].items():
            if count > 0:
                report += f"- **{category.title()}:** {count} functions\n"
        
        report += "\n## 🔄 Top Duplicate Functions\n"
        
        # Sort duplicates by occurrence count
        sorted_dupes = sorted(
            results['duplicates'].items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        for i, (name, instances) in enumerate(sorted_dupes, 1):
            report += f"\n### {i}. `{name}()` - {len(instances)} occurrences\n"
            report += "Files:\n"
            for inst in instances[:5]:
                report += f"- {inst['file']}:{inst['line']}\n"
            if len(instances) > 5:
                report += f"- ... and {len(instances) - 5} more\n"
        
        report += "\n## 🎯 Consolidation Plan\n"
        
        total_savings = 0
        for item in plan:
            report += f"\n### {item['module']}\n"
            report += f"**{item['description']}**\n"
            report += f"- Functions: {', '.join(item['functions_to_consolidate'][:5])}"
            if len(item['functions_to_consolidate']) > 5:
                report += " ..."
            report += f"\n- Affected Files: {item['affected_files']}\n"
            report += f"- Instances to Consolidate: {item['instances']}\n"
            report += f"- Estimated Line Savings: {item['estimated_savings']}\n"
            total_savings += item['estimated_savings']
        
        report += f"\n## 💡 Total Impact\n"
        report += f"- **New Utility Modules:** {len(plan)}\n"
        report += f"- **Total Line Savings:** ~{total_savings} lines\n"
        report += f"- **Maintenance Improvement:** Significant - single source of truth for utilities\n"
        
        return report


def main():
    """Main execution"""
    print("🚀 Week 2 Day 2: Utility Function Analysis")
    print("=" * 50)
    
    finder = SimpleUtilityFinder()
    results = finder.analyze_codebase()
    plan = finder.generate_consolidation_plan(results)
    
    # Generate report
    report = finder.generate_report(results, plan)
    print(report)
    
    # Save results
    results_file = Path("reports") / "week2_day2_utility_analysis.json"
    results_file.parent.mkdir(exist_ok=True)
    
    # Create serializable results
    serializable_results = {
        'summary': results['summary'],
        'consolidation_plan': plan,
        'duplicate_count': len(results['duplicates']),
        'top_duplicates': [
            {'name': name, 'count': len(instances)}
            for name, instances in list(results['duplicates'].items())[:10]
        ]
    }
    
    with open(results_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Save report
    report_file = Path("reports") / "week2_day2_utility_analysis.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Report saved to: {report_file}")


if __name__ == "__main__":
    main()