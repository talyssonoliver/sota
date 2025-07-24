#!/usr/bin/env python3
"""
Analyze quality issues from validation report and current ruff output
"""
import json
import subprocess
from collections import defaultdict, Counter

def analyze_current_ruff_issues():
    """Get current ruff issues by file"""
    try:
        result = subprocess.run(['python3', '-m', 'ruff', 'check', '.', '--output-format=json'], 
                               capture_output=True, text=True)
        
        if result.stdout:
            issues = json.loads(result.stdout)
            file_counts = defaultdict(int)
            code_counts = Counter()
            
            for issue in issues:
                file_counts[issue['filename']] += 1
                code_counts[issue['code']] += 1
            
            return file_counts, code_counts, len(issues)
        return {}, {}, 0
    except Exception as e:
        print(f"Error running ruff: {e}")
        return {}, {}, 0

def analyze_validation_report():
    """Extract key metrics from validation report"""
    try:
        with open('reports/validation_report.json', 'r') as f:
            data = json.load(f)
        
        total_issues = data.get('total_issues', 0)
        issues_by_category = data.get('issues_by_category', {})
        issues_by_severity = data.get('issues_by_severity', {})
        
        return total_issues, issues_by_category, issues_by_severity
    except Exception as e:
        print(f"Error reading validation report: {e}")
        return 0, {}, {}

def main():
    print("=== Quality Issue Analysis ===\n")
    
    # Analyze validation report
    total_issues, categories, severities = analyze_validation_report()
    print("Validation Report Summary:")
    print(f"- Total Issues: {total_issues:,}")
    print(f"- By Severity: {severities}")
    print(f"- Top Categories: {dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5])}")
    print()
    
    # Analyze current ruff issues
    file_counts, code_counts, current_total = analyze_current_ruff_issues()
    print(f"Current Ruff Issues: {current_total}")
    print()
    
    print("Top 15 Files by Current Ruff Issue Count:")
    print("-" * 60)
    for i, (file, count) in enumerate(sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:15], 1):
        relative_path = file.replace('/mnt/c/taly/ai-system/', '')
        print(f"{i:2d}. {count:3d} issues: {relative_path}")
    print()
    
    print("Top 10 Ruff Issue Types:")
    print("-" * 40)
    for i, (code, count) in enumerate(code_counts.most_common(10), 1):
        print(f"{i:2d}. {code}: {count:3d} occurrences")
    print()
    
    # Phase classification
    safe_codes = {'E402', 'W292', 'W391'}  # Import ordering, formatting
    investigation_codes = {'F401', 'F841'}  # Unused imports/variables
    high_risk_codes = {'B404', 'B301', 'B603'}  # Security issues
    
    safe_count = sum(count for code, count in code_counts.items() if code in safe_codes)
    investigation_count = sum(count for code, count in code_counts.items() if code in investigation_codes)
    high_risk_count = sum(count for code, count in code_counts.items() if code in high_risk_codes)
    
    print("Phase Classification (Current Ruff Issues):")
    print(f"🟢 Safe Auto-Fix: {safe_count} issues")
    print(f"🟡 Investigation: {investigation_count} issues")  
    print(f"🔴 High Risk: {high_risk_count} issues")
    print(f"🔍 Other: {current_total - safe_count - investigation_count - high_risk_count} issues")

if __name__ == "__main__":
    main()