#!/usr/bin/env python3
"""
Week 2 Day 3: Validation Pattern Analysis
Analyze validation patterns across the codebase for standardization
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List
import json


class ValidationPatternAnalyzer:
    def __init__(self):
        self.src_path = Path("src")
        self.validation_patterns = {
            'input_validation': [
                r'def\s+validate_\w+\s*\(',
                r'if\s+not\s+\w+.*:\s*raise\s+\w*Error',
                r'assert\s+\w+.*,\s*["\'].*["\']',
                r'if\s+.*is\s+None.*raise',
                r'if\s+not\s+isinstance\(',
            ],
            'schema_validation': [
                r'schema\s*=\s*\{',
                r'jsonschema\.validate',
                r'\.validate\(',
                r'ValidationError',
                r'schema_validator',
            ],
            'api_validation': [
                r'@validate_\w+',
                r'request\.json\[\w+\]',
                r'request\.args\.get',
                r'abort\(\d+',
                r'return.*400',
            ],
            'security_validation': [
                r'sanitize_\w+',
                r'escape_\w+',
                r'check_\w+_safe',
                r'validate_\w+_security',
                r'sql_injection',
            ],
            'type_validation': [
                r'isinstance\(\w+,\s*\w+\)',
                r'type\(\w+\)\s*==',
                r'hasattr\(\w+,\s*["\']',
                r'callable\(',
                r'@typing\.',
            ],
            'business_validation': [
                r'validate_business_rule',
                r'check_permission',
                r'verify_access',
                r'validate_workflow',
                r'check_constraint',
            ]
        }
        
        self.error_patterns = {
            'validation_errors': [
                r'ValidationError',
                r'ValueError',
                r'TypeError',
                r'AttributeError',
                r'KeyError',
            ],
            'custom_errors': [
                r'class\s+\w*Error\(.*Error\)',
                r'raise\s+\w*Error\(',
                r'except\s+\w*Error',
            ]
        }
        
    def analyze_file_patterns(self, file_path: Path) -> Dict[str, List[Dict]]:
        """Analyze validation patterns in a single file"""
        patterns = defaultdict(list)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Check validation patterns
            for category, regex_patterns in self.validation_patterns.items():
                for pattern in regex_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        patterns[category].append({
                            'pattern': pattern,
                            'match': match.group(),
                            'line': line_num,
                            'context': lines[line_num - 1].strip() if line_num <= len(lines) else ''
                        })
            
            # Check error patterns
            for category, regex_patterns in self.error_patterns.items():
                for pattern in regex_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        patterns[category].append({
                            'pattern': pattern,
                            'match': match.group(),
                            'line': line_num,
                            'context': lines[line_num - 1].strip() if line_num <= len(lines) else ''
                        })
                        
        except Exception:
            pass  # Skip files with issues
        
        return patterns
    
    def analyze_codebase(self) -> Dict[str, any]:
        """Analyze entire codebase for validation patterns"""
        print("🔍 Analyzing validation patterns across codebase...")
        
        results = {
            'file_patterns': {},
            'pattern_summary': defaultdict(int),
            'validation_hotspots': [],
            'inconsistent_patterns': [],
            'standardization_opportunities': []
        }
        
        python_files = list(self.src_path.rglob("*.py"))
        files_with_validation = 0
        
        # Analyze each file
        for file_path in python_files:
            file_patterns = self.analyze_file_patterns(file_path)
            
            if any(file_patterns.values()):
                files_with_validation += 1
                results['file_patterns'][str(file_path)] = file_patterns
                
                # Count patterns
                for category, patterns in file_patterns.items():
                    results['pattern_summary'][category] += len(patterns)
        
        print(f"  📁 Files analyzed: {len(python_files)}")
        print(f"  ✅ Files with validation: {files_with_validation}")
        
        # Identify validation hotspots (files with many validation patterns)
        file_pattern_counts = []
        for file_path, patterns in results['file_patterns'].items():
            total_patterns = sum(len(p) for p in patterns.values())
            if total_patterns > 5:  # Threshold for "hotspot"
                file_pattern_counts.append((file_path, total_patterns, patterns))
        
        results['validation_hotspots'] = sorted(
            file_pattern_counts, 
            key=lambda x: x[1], 
            reverse=True
        )[:20]
        
        # Identify inconsistent patterns
        results['inconsistent_patterns'] = self._find_inconsistent_patterns(results)
        
        # Identify standardization opportunities
        results['standardization_opportunities'] = self._identify_standardization_opportunities(results)
        
        return results
    
    def _find_inconsistent_patterns(self, results: Dict) -> List[Dict]:
        """Find inconsistent validation patterns"""
        inconsistencies = []
        
        # Look for different error handling patterns
        error_types = defaultdict(list)
        validation_styles = defaultdict(list)
        
        for file_path, patterns in results['file_patterns'].items():
            # Group error types
            for error_pattern in patterns.get('validation_errors', []):
                error_type = error_pattern['match']
                error_types[error_type].append(file_path)
            
            # Group validation styles
            for input_pattern in patterns.get('input_validation', []):
                style = self._categorize_validation_style(input_pattern['match'])
                validation_styles[style].append(file_path)
        
        # Find inconsistencies
        if len(error_types) > 3:
            inconsistencies.append({
                'type': 'Mixed Error Types',
                'description': f'Using {len(error_types)} different error types',
                'patterns': list(error_types.keys())[:10],
                'recommendation': 'Standardize on ValidationError with specific subtypes'
            })
        
        if len(validation_styles) > 4:
            inconsistencies.append({
                'type': 'Mixed Validation Styles',
                'description': f'Using {len(validation_styles)} different validation approaches',
                'patterns': list(validation_styles.keys()),
                'recommendation': 'Adopt consistent validation decorator or utility pattern'
            })
        
        return inconsistencies
    
    def _categorize_validation_style(self, pattern: str) -> str:
        """Categorize validation style"""
        if 'assert' in pattern.lower():
            return 'assert_style'
        elif 'if not' in pattern.lower():
            return 'guard_clause'
        elif 'isinstance' in pattern.lower():
            return 'type_check'
        elif 'validate_' in pattern.lower():
            return 'function_call'
        else:
            return 'other'
    
    def _identify_standardization_opportunities(self, results: Dict) -> List[Dict]:
        """Identify opportunities for standardization"""
        opportunities = []
        
        # 1. Input validation standardization
        input_validation_files = []
        for file_path, patterns in results['file_patterns'].items():
            if patterns.get('input_validation'):
                input_validation_files.append(file_path)
        
        if len(input_validation_files) > 10:
            opportunities.append({
                'category': 'Input Validation Standardization',
                'description': 'Many files have custom input validation logic',
                'affected_files': len(input_validation_files),
                'recommendation': 'Create @validate_input decorator and standard validation middleware',
                'estimated_impact': 'High - affects core data flow',
                'implementation': 'Extend validation_utils.py with decorators and middleware'
            })
        
        # 2. Schema validation consolidation
        schema_files = []
        for file_path, patterns in results['file_patterns'].items():
            if patterns.get('schema_validation'):
                schema_files.append(file_path)
        
        if len(schema_files) > 5:
            opportunities.append({
                'category': 'Schema Validation Consolidation',
                'description': 'Multiple files implement schema validation differently',
                'affected_files': len(schema_files),
                'recommendation': 'Create centralized schema registry and validation service',
                'estimated_impact': 'Medium - improves API consistency',
                'implementation': 'Create schema_registry.py and update validation_utils.py'
            })
        
        # 3. API validation middleware
        api_files = []
        for file_path, patterns in results['file_patterns'].items():
            if patterns.get('api_validation') and 'api' in file_path.lower():
                api_files.append(file_path)
        
        if len(api_files) > 3:
            opportunities.append({
                'category': 'API Validation Middleware',
                'description': 'API endpoints have inconsistent validation approaches',
                'affected_files': len(api_files),
                'recommendation': 'Create standard API validation middleware',
                'estimated_impact': 'High - improves security and consistency',
                'implementation': 'Create api_validation_middleware.py'
            })
        
        # 4. Security validation patterns
        security_files = []
        for file_path, patterns in results['file_patterns'].items():
            if patterns.get('security_validation'):
                security_files.append(file_path)
        
        if len(security_files) > 2:
            opportunities.append({
                'category': 'Security Validation Patterns',
                'description': 'Security validation is scattered and inconsistent',
                'affected_files': len(security_files),
                'recommendation': 'Create security validation utilities and patterns',
                'estimated_impact': 'Critical - security implications',
                'implementation': 'Extend validation_utils.py with security-focused validators'
            })
        
        # 5. Error handling standardization
        error_variety = len(set(
            pattern['match'] for patterns in results['file_patterns'].values()
            for pattern in patterns.get('validation_errors', [])
        ))
        
        if error_variety > 5:
            opportunities.append({
                'category': 'Error Handling Standardization',
                'description': f'Using {error_variety} different error types for validation',
                'affected_files': len([f for f, p in results['file_patterns'].items() 
                                    if p.get('validation_errors')]),
                'recommendation': 'Create ValidationError hierarchy and standard error handling',
                'estimated_impact': 'Medium - improves debugging and user experience',
                'implementation': 'Create validation_errors.py with error hierarchy'
            })
        
        return opportunities
    
    def generate_standardization_plan(self, results: Dict) -> List[Dict]:
        """Generate specific standardization plan"""
        plan = []
        
        for opportunity in results['standardization_opportunities']:
            if opportunity['category'] == 'Input Validation Standardization':
                plan.append({
                    'module': 'src/infrastructure/utils/validation_decorators.py',
                    'description': 'Input validation decorators and middleware',
                    'functions_to_create': [
                        '@validate_input', '@validate_json', '@validate_args',
                        'ValidationMiddleware', 'create_validator'
                    ],
                    'affected_files': opportunity['affected_files'],
                    'priority': 'High',
                    'estimated_effort': '4 hours'
                })
            
            elif opportunity['category'] == 'Schema Validation Consolidation':
                plan.append({
                    'module': 'src/infrastructure/utils/schema_registry.py',
                    'description': 'Centralized schema definitions and validation',
                    'functions_to_create': [
                        'SchemaRegistry', 'register_schema', 'validate_against_schema',
                        'load_schema_definitions', 'schema_cache'
                    ],
                    'affected_files': opportunity['affected_files'],
                    'priority': 'Medium',
                    'estimated_effort': '3 hours'
                })
            
            elif opportunity['category'] == 'API Validation Middleware':
                plan.append({
                    'module': 'src/infrastructure/utils/api_validation.py',
                    'description': 'API request/response validation middleware',
                    'functions_to_create': [
                        'APIValidationMiddleware', 'validate_request',
                        'validate_response', 'parameter_validator'
                    ],
                    'affected_files': opportunity['affected_files'],
                    'priority': 'High',
                    'estimated_effort': '3 hours'
                })
            
            elif opportunity['category'] == 'Error Handling Standardization':
                plan.append({
                    'module': 'src/infrastructure/utils/validation_errors.py',
                    'description': 'Standardized validation error hierarchy',
                    'functions_to_create': [
                        'ValidationError', 'InputValidationError', 'SchemaValidationError',
                        'APIValidationError', 'SecurityValidationError'
                    ],
                    'affected_files': opportunity['affected_files'],
                    'priority': 'Medium',
                    'estimated_effort': '2 hours'
                })
        
        return plan
    
    def generate_report(self, results: Dict, plan: List[Dict]) -> str:
        """Generate comprehensive analysis report"""
        report = f"""# Week 2 Day 3: Validation Pattern Analysis Report

## 📊 Overview
- **Files Analyzed:** {len(list(self.src_path.rglob('*.py')))}
- **Files with Validation:** {len(results['file_patterns'])}
- **Total Validation Patterns:** {sum(results['pattern_summary'].values())}

## 📋 Pattern Distribution
"""
        
        for category, count in results['pattern_summary'].items():
            if count > 0:
                report += f"- **{category.replace('_', ' ').title()}:** {count} patterns\n"
        
        report += "\n## 🔥 Validation Hotspots (Top 10)\n"
        
        for i, (file_path, count, patterns) in enumerate(results['validation_hotspots'][:10], 1):
            report += f"\n### {i}. {file_path}\n"
            report += f"- **Total Patterns:** {count}\n"
            pattern_breakdown = {k: len(v) for k, v in patterns.items() if v}
            for pattern_type, pattern_count in pattern_breakdown.items():
                report += f"  - {pattern_type.replace('_', ' ').title()}: {pattern_count}\n"
        
        report += "\n## ⚠️ Inconsistent Patterns\n"
        
        for inconsistency in results['inconsistent_patterns']:
            report += f"\n### {inconsistency['type']}\n"
            report += f"- **Issue:** {inconsistency['description']}\n"
            report += f"- **Recommendation:** {inconsistency['recommendation']}\n"
        
        report += "\n## 🎯 Standardization Opportunities\n"
        
        total_impact_files = 0
        for opportunity in results['standardization_opportunities']:
            report += f"\n### {opportunity['category']}\n"
            report += f"- **Description:** {opportunity['description']}\n"
            report += f"- **Affected Files:** {opportunity['affected_files']}\n"
            report += f"- **Impact:** {opportunity['estimated_impact']}\n"
            report += f"- **Implementation:** {opportunity['implementation']}\n"
            total_impact_files += opportunity['affected_files']
        
        report += "\n## 🔧 Standardization Plan\n"
        
        total_effort = 0
        for item in plan:
            report += f"\n### {item['module']}\n"
            report += f"**{item['description']}**\n"
            report += f"- **Functions:** {', '.join(item['functions_to_create'][:3])}"
            if len(item['functions_to_create']) > 3:
                report += f" + {len(item['functions_to_create']) - 3} more"
            report += f"\n- **Priority:** {item['priority']}\n"
            report += f"- **Effort:** {item['estimated_effort']}\n"
            report += f"- **Files to Update:** {item['affected_files']}\n"
            
            # Extract hours from effort estimate
            hours = int(re.search(r'(\d+)', item['estimated_effort']).group(1))
            total_effort += hours
        
        report += "\n## 💡 Summary\n"
        report += f"- **Standardization Modules:** {len(plan)}\n"
        report += f"- **Files to Improve:** {total_impact_files}\n"
        report += f"- **Estimated Total Effort:** {total_effort} hours\n"
        report += "- **Expected Impact:** Significant improvement in code consistency and maintainability\n"
        
        return report


def main():
    """Main execution"""
    print("🚀 Week 2 Day 3: Validation Pattern Analysis")
    print("=" * 50)
    
    analyzer = ValidationPatternAnalyzer()
    results = analyzer.analyze_codebase()
    plan = analyzer.generate_standardization_plan(results)
    
    # Generate report
    report = analyzer.generate_report(results, plan)
    print(report)
    
    # Save results
    results_file = Path("reports") / "week2_day3_validation_analysis.json"
    results_file.parent.mkdir(exist_ok=True)
    
    # Create serializable results
    serializable_results = {
        'pattern_summary': dict(results['pattern_summary']),
        'validation_hotspots_count': len(results['validation_hotspots']),
        'inconsistent_patterns_count': len(results['inconsistent_patterns']),
        'standardization_opportunities': results['standardization_opportunities'],
        'standardization_plan': plan
    }
    
    with open(results_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Save report
    report_file = Path("reports") / "week2_day3_validation_analysis.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Report saved to: {report_file}")


if __name__ == "__main__":
    main()