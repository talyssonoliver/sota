#!/usr/bin/env python3
"""
Week 2 Day 2: Utility Function Analysis
Identify duplicate utility functions across the codebase for consolidation
"""

import ast
import os
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple
import hashlib
import json


class UtilityAnalyzer:
    def __init__(self):
        self.src_path = Path("src")
        self.function_signatures = defaultdict(list)
        self.function_bodies = defaultdict(list)
        self.duplicate_functions = defaultdict(list)
        self.utility_patterns = [
            # Common utility function patterns
            'setup_logging', 'get_logger', 'create_logger',
            'load_config', 'save_config', 'read_config',
            'validate_input', 'validate_', 'check_',
            'parse_', 'format_', 'convert_',
            'get_timestamp', 'get_current_time',
            'generate_id', 'create_id', 'make_id',
            'ensure_directory', 'create_directory',
            'read_file', 'write_file', 'load_json', 'save_json',
            'hash_', 'encrypt_', 'decrypt_',
            'retry_', 'with_retry', 'safe_',
            'normalize_', 'sanitize_', 'clean_'
        ]
        
    def extract_functions(self, file_path: Path) -> List[Dict]:
        """Extract function definitions from a Python file"""
        functions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip test functions and private methods
                    if node.name.startswith('test_') or node.name.startswith('_'):
                        continue
                    
                    # Check if it matches utility patterns
                    is_utility = any(pattern in node.name.lower() 
                                   for pattern in self.utility_patterns)
                    
                    # Get function signature
                    args = []
                    for arg in node.args.args:
                        args.append(arg.arg)
                    
                    # Get function body hash (for detecting duplicates)
                    body_dump = ast.dump(node.body)
                    body_hash = hashlib.md5(body_dump.encode()).hexdigest()[:8]
                    
                    # Get line count
                    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                        line_count = node.end_lineno - node.lineno + 1
                    else:
                        line_count = len(ast.dump(node).split('\n'))
                    
                    functions.append({
                        'name': node.name,
                        'file': str(file_path),
                        'args': args,
                        'signature': f"{node.name}({', '.join(args)})",
                        'body_hash': body_hash,
                        'line_count': line_count,
                        'is_utility': is_utility,
                        'docstring': ast.get_docstring(node) or ""
                    })
                    
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return functions
    
    def analyze_codebase(self) -> Dict[str, any]:
        """Analyze entire codebase for utility functions"""
        print("🔍 Analyzing codebase for utility functions...")
        
        all_functions = []
        python_files = list(self.src_path.rglob("*.py"))
        
        # Extract all functions
        for file_path in python_files:
            functions = self.extract_functions(file_path)
            all_functions.extend(functions)
        
        # Find duplicates by signature
        signature_groups = defaultdict(list)
        for func in all_functions:
            signature_groups[func['signature']].append(func)
        
        # Find duplicates by body hash
        body_groups = defaultdict(list)
        for func in all_functions:
            body_groups[func['body_hash']].append(func)
        
        # Identify common utility functions
        utility_functions = [f for f in all_functions if f['is_utility']]
        
        # Group by function name pattern
        pattern_groups = defaultdict(list)
        for func in utility_functions:
            base_name = func['name'].lower()
            for pattern in self.utility_patterns:
                if pattern in base_name:
                    pattern_groups[pattern].append(func)
                    break
        
        # Calculate statistics
        results = {
            'total_functions': len(all_functions),
            'utility_functions': len(utility_functions),
            'duplicate_signatures': {
                sig: funcs for sig, funcs in signature_groups.items() 
                if len(funcs) > 1
            },
            'duplicate_bodies': {
                hash_val: funcs for hash_val, funcs in body_groups.items() 
                if len(funcs) > 1
            },
            'pattern_groups': dict(pattern_groups),
            'top_duplicates': self._get_top_duplicates(signature_groups, body_groups),
            'consolidation_opportunities': self._identify_consolidation_opportunities(
                signature_groups, body_groups, pattern_groups
            )
        }
        
        return results
    
    def _get_top_duplicates(self, signature_groups: Dict, body_groups: Dict) -> List[Dict]:
        """Get top duplicate functions by impact"""
        duplicates = []
        
        # Combine signature and body duplicates
        all_duplicates = {}
        
        for sig, funcs in signature_groups.items():
            if len(funcs) > 1:
                total_lines = sum(f['line_count'] for f in funcs)
                all_duplicates[sig] = {
                    'type': 'signature',
                    'functions': funcs,
                    'duplicate_count': len(funcs),
                    'total_lines': total_lines,
                    'potential_savings': total_lines - funcs[0]['line_count']
                }
        
        for hash_val, funcs in body_groups.items():
            if len(funcs) > 1:
                # Check if not already counted by signature
                sig = funcs[0]['signature']
                if sig not in all_duplicates:
                    total_lines = sum(f['line_count'] for f in funcs)
                    all_duplicates[f"body_{hash_val}"] = {
                        'type': 'body',
                        'functions': funcs,
                        'duplicate_count': len(funcs),
                        'total_lines': total_lines,
                        'potential_savings': total_lines - funcs[0]['line_count']
                    }
        
        # Sort by potential savings
        sorted_duplicates = sorted(
            all_duplicates.values(),
            key=lambda x: x['potential_savings'],
            reverse=True
        )
        
        return sorted_duplicates[:20]  # Top 20 duplicates
    
    def _identify_consolidation_opportunities(self, signature_groups: Dict, 
                                            body_groups: Dict, 
                                            pattern_groups: Dict) -> List[Dict]:
        """Identify specific consolidation opportunities"""
        opportunities = []
        
        # 1. Logging setup functions
        logging_funcs = []
        for pattern in ['setup_logging', 'get_logger', 'create_logger']:
            logging_funcs.extend(pattern_groups.get(pattern, []))
        
        if logging_funcs:
            opportunities.append({
                'category': 'Logging Utilities',
                'functions': logging_funcs,
                'count': len(logging_funcs),
                'recommendation': 'Create centralized logging utilities module',
                'estimated_savings': sum(f['line_count'] for f in logging_funcs) - 50
            })
        
        # 2. Configuration management
        config_funcs = []
        for pattern in ['load_config', 'save_config', 'read_config']:
            config_funcs.extend(pattern_groups.get(pattern, []))
        
        if config_funcs:
            opportunities.append({
                'category': 'Configuration Management',
                'functions': config_funcs,
                'count': len(config_funcs),
                'recommendation': 'Create centralized config manager',
                'estimated_savings': sum(f['line_count'] for f in config_funcs) - 100
            })
        
        # 3. Validation utilities
        validation_funcs = []
        for pattern in ['validate_', 'check_']:
            validation_funcs.extend(pattern_groups.get(pattern, []))
        
        if validation_funcs:
            opportunities.append({
                'category': 'Validation Utilities',
                'functions': validation_funcs,
                'count': len(validation_funcs),
                'recommendation': 'Create validation utilities module',
                'estimated_savings': sum(f['line_count'] for f in validation_funcs) - 150
            })
        
        # 4. File operations
        file_funcs = []
        for pattern in ['read_file', 'write_file', 'load_json', 'save_json']:
            file_funcs.extend(pattern_groups.get(pattern, []))
        
        if file_funcs:
            opportunities.append({
                'category': 'File Operations',
                'functions': file_funcs,
                'count': len(file_funcs),
                'recommendation': 'Create file utilities module',
                'estimated_savings': sum(f['line_count'] for f in file_funcs) - 80
            })
        
        # 5. Time/ID generation
        time_id_funcs = []
        for pattern in ['get_timestamp', 'generate_id', 'create_id']:
            time_id_funcs.extend(pattern_groups.get(pattern, []))
        
        if time_id_funcs:
            opportunities.append({
                'category': 'Time & ID Generation',
                'functions': time_id_funcs,
                'count': len(time_id_funcs),
                'recommendation': 'Create time/ID utilities module',
                'estimated_savings': sum(f['line_count'] for f in time_id_funcs) - 40
            })
        
        return opportunities
    
    def generate_report(self, results: Dict[str, any]) -> str:
        """Generate analysis report"""
        report = f"""
# Week 2 Day 2: Utility Function Analysis Report

## 📊 Overview
- **Total Functions Analyzed:** {results['total_functions']}
- **Utility Functions Identified:** {results['utility_functions']}
- **Duplicate Signatures:** {len(results['duplicate_signatures'])}
- **Duplicate Implementations:** {len(results['duplicate_bodies'])}

## 🔍 Top Duplicate Functions
"""
        
        for i, dup in enumerate(results['top_duplicates'][:10], 1):
            report += f"\n### {i}. {dup['functions'][0]['name']}\n"
            report += f"- **Occurrences:** {dup['duplicate_count']}\n"
            report += f"- **Total Lines:** {dup['total_lines']}\n"
            report += f"- **Potential Savings:** {dup['potential_savings']} lines\n"
            report += f"- **Files:**\n"
            for func in dup['functions'][:5]:  # Show first 5 occurrences
                report += f"  - {func['file']}\n"
            if len(dup['functions']) > 5:
                report += f"  - ... and {len(dup['functions']) - 5} more\n"
        
        report += "\n## 🎯 Consolidation Opportunities\n"
        
        total_savings = 0
        for opp in results['consolidation_opportunities']:
            report += f"\n### {opp['category']}\n"
            report += f"- **Functions Found:** {opp['count']}\n"
            report += f"- **Recommendation:** {opp['recommendation']}\n"
            report += f"- **Estimated Savings:** {opp['estimated_savings']} lines\n"
            total_savings += opp['estimated_savings']
        
        report += f"\n## 💡 Summary\n"
        report += f"- **Total Potential Line Savings:** {total_savings}\n"
        report += f"- **Recommended Modules to Create:** {len(results['consolidation_opportunities'])}\n"
        
        return report


def main():
    """Main execution"""
    print("🚀 Week 2 Day 2: Utility Function Analysis")
    print("=" * 50)
    
    analyzer = UtilityAnalyzer()
    results = analyzer.analyze_codebase()
    
    # Generate report
    report = analyzer.generate_report(results)
    print(report)
    
    # Save detailed results
    results_file = Path("reports") / "week2_day2_utility_analysis.json"
    results_file.parent.mkdir(exist_ok=True)
    
    # Convert functions to serializable format
    serializable_results = {
        'total_functions': results['total_functions'],
        'utility_functions': results['utility_functions'],
        'duplicate_count': len(results['duplicate_signatures']),
        'consolidation_opportunities': [
            {
                'category': opp['category'],
                'count': opp['count'],
                'recommendation': opp['recommendation'],
                'estimated_savings': opp['estimated_savings']
            }
            for opp in results['consolidation_opportunities']
        ]
    }
    
    with open(results_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Save report
    report_file = Path("reports") / "week2_day2_utility_analysis.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Report saved to: {report_file}")


if __name__ == "__main__":
    main()