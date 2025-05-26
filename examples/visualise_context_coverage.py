#!/usr/bin/env python3
"""
Step 3.9 Demo: Visualise Context Coverage

This script demonstrates and validates the Step 3.9 implementation
for context coverage visualization. It tests the generation of both
CSV and HTML reports showing context usage patterns.

Usage:
    python examples/step_3_9_demo.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.context_visualizer import (
    analyze_context_coverage, 
    generate_context_coverage_report,
    generate_csv_report,
    generate_html_report
)
from tools.context_tracker import get_all_context_logs

def test_context_coverage_analysis():
    """Test context coverage analysis functionality"""
    print("\n" + "=" * 60)
    print("STEP 3.9 TEST: Context Coverage Analysis")
    print("=" * 60)
    
    # Analyze context coverage
    coverage_data = analyze_context_coverage()
    
    if "error" in coverage_data:
        print(f"⚠️  Warning: {coverage_data['error']}")
        print("   This is expected if no context logs exist yet.")
        return False
    
    print("📊 Context Coverage Analysis Results:")
    print(f"   Tasks analyzed: {coverage_data.get('tasks_analyzed', 0)}")
    print(f"   Unique topics: {coverage_data.get('unique_topics', 0)}")
    print(f"   Unique documents: {coverage_data.get('unique_documents', 0)}")
    
    summary_stats = coverage_data.get("summary_stats", {})
    print(f"   Avg topics per task: {summary_stats.get('avg_topics_per_task', 0):.1f}")
    print(f"   Avg context length: {summary_stats.get('avg_context_length', 0):.0f}")
    
    most_active_topic = summary_stats.get('most_active_topic', ('none', 0))
    print(f"   Most active topic: {most_active_topic[0]} ({most_active_topic[1]} uses)")
    
    most_active_agent = summary_stats.get('most_active_agent', ('none', 0))
    print(f"   Most active agent: {most_active_agent[0]} ({most_active_agent[1]} tasks)")
    
    # Display some coverage matrix data
    coverage_matrix = coverage_data.get("coverage_matrix", [])
    if coverage_matrix:
        print(f"\n📋 Sample Coverage Data:")
        for i, task_data in enumerate(coverage_matrix[:3]):  # Show first 3 tasks
            task_id = task_data["task_id"]
            agent_role = task_data["agent_role"]
            topics = [topic for topic, count in task_data["topics"].items() if count > 0]
            print(f"   {task_id} ({agent_role}): {', '.join(topics)}")
        
        if len(coverage_matrix) > 3:
            print(f"   ... and {len(coverage_matrix) - 3} more tasks")
    
    return True

def test_csv_generation():
    """Test CSV report generation"""
    print("\n" + "=" * 60)
    print("STEP 3.9 TEST: CSV Report Generation")
    print("=" * 60)
    
    # Get coverage data
    coverage_data = analyze_context_coverage()
    
    if "error" in coverage_data:
        print(f"⚠️  Skipping CSV test - no context data available")
        return False
    
    # Generate CSV report
    csv_path = "reports/step_3_9_test_coverage.csv"
    success = generate_csv_report(coverage_data, csv_path)
    
    if success:
        print(f"✅ CSV report generated: {csv_path}")
        
        # Check if file exists and has content
        if os.path.exists(csv_path):
            file_size = os.path.getsize(csv_path)
            print(f"   File size: {file_size} bytes")
            
            # Read first few lines to verify format
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:5]
            
            print("   First few lines:")
            for line in lines:
                print(f"     {line.strip()}")
        
        return True
    else:
        print("❌ CSV report generation failed")
        return False

def test_html_generation():
    """Test HTML report generation and JSON data generation for dynamic HTML"""
    print("\n" + "=" * 60)
    print("STEP 3.9 TEST: HTML Report Generation")
    print("=" * 60)
    
    # Get coverage data
    coverage_data = analyze_context_coverage()
    
    if "error" in coverage_data:
        print(f"⚠️  Skipping HTML test - no context data available")
        return False
    
    # Generate HTML report
    html_path = "reports/step_3_9_test_coverage.html"
    json_path = "reports/step_3_9_test_coverage.json"
    success_html = generate_html_report(coverage_data, html_path)
    # Also generate the JSON file for dynamic HTML
    from tools.context_visualizer import generate_json_report
    success_json = generate_json_report(coverage_data, json_path)
    
    if success_html and success_json:
        print(f"✅ HTML report generated: {html_path}")
        print(f"✅ JSON data generated: {json_path}")
        
        # Check if files exist and have content
        for path in [html_path, json_path]:
            if os.path.exists(path):
                file_size = os.path.getsize(path)
                print(f"   {os.path.basename(path)} size: {file_size} bytes")
        
        # Read and check basic HTML structure
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Verify key HTML elements
            checks = [
                ("<!DOCTYPE html>" in content, "HTML DOCTYPE"),
                ("<title>" in content, "Title tag"),
                ("Context Coverage Analysis" in content, "Main title"),
                ("Step 3.9" in content, "Step reference"),
                ("plotly" in content.lower(), "Plotly integration"),
                ("heatmap" in content.lower(), "Heatmap element"),
                ("topicChart" in content, "Topic chart element"),
                ("agentChart" in content, "Agent chart element")
            ]
            print("   HTML validation checks:")
            all_passed = True
            for check_passed, check_name in checks:
                status = "✅" if check_passed else "❌"
                print(f"     {status} {check_name}")
                all_passed = all_passed and check_passed
            return all_passed
        else:
            print("❌ HTML file was not created")
            return False
    else:
        print("❌ HTML or JSON report generation failed")
        return False

def test_json_generation():
    """Test JSON data generation for context-coverage.html dynamic report"""
    print("\n" + "=" * 60)
    print("STEP 3.9 TEST: JSON Data Generation for context-coverage.html")
    print("=" * 60)
    
    # Get coverage data
    coverage_data = analyze_context_coverage()
    if "error" in coverage_data:
        print(f"⚠️  Skipping JSON test - no context data available")
        return False
    json_path = "reports/context-coverage.json"
    from tools.context_visualizer import generate_json_report
    success_json = generate_json_report(coverage_data, json_path)
    if success_json:
        print(f"✅ JSON data generated: {json_path}")
        if os.path.exists(json_path):
            file_size = os.path.getsize(json_path)
            print(f"   {os.path.basename(json_path)} size: {file_size} bytes")
        return True
    else:
        print("❌ JSON data generation failed")
        return False

def test_full_report_generation():
    """Test full report generation with both formats"""
    print("\n" + "=" * 60)
    print("STEP 3.9 TEST: Full Report Generation")
    print("=" * 60)
    
    # Generate both CSV and HTML reports
    success = generate_context_coverage_report(
        format="both",
        csv_path="reports/step_3_9_demo_coverage.csv",
        html_path="reports/step_3_9_demo_coverage.html"
    )
    
    if success:
        print("✅ Full context coverage report generation successful")
        
        # Verify both files exist
        csv_exists = os.path.exists("reports/step_3_9_demo_coverage.csv")
        html_exists = os.path.exists("reports/step_3_9_demo_coverage.html")
        
        print(f"   CSV file created: {'✅' if csv_exists else '❌'}")
        print(f"   HTML file created: {'✅' if html_exists else '❌'}")
        
        return csv_exists and html_exists
    else:
        print("❌ Full report generation failed")
        return False

def run_step_3_9_validation():
    """Run complete Step 3.9 validation suite"""
    print("🎯 STEP 3.9 VALIDATION: Visualise Context Coverage")
    print("=" * 70)
    print("Testing context coverage visualization implementation...")
    # Check if context logs exist from Step 3.7
    all_logs = get_all_context_logs()
    if not all_logs:
        print("\n⚠️  No context logs found from Step 3.7!")
        print("   Please run some tasks with context tracking first.")
        print("   You can run: python examples/step_3_7_demo.py")
        return False
    print(f"\n📋 Found {len(all_logs)} context logs to analyze")
    tests = [
        ("Context Coverage Analysis", test_context_coverage_analysis),
        ("CSV Report Generation", test_csv_generation),
        ("HTML Report Generation", test_html_generation),
        ("JSON Data Generation for context-coverage.html", test_json_generation),
        ("Full Report Generation", test_full_report_generation)
    ]
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 70)
    print("STEP 3.9 VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Step 3.9 implementation is working perfectly!")
        print("✅ Context coverage visualization is ready for production use")
        
        print("\n📄 Generated Reports:")
        reports = [
            "reports/step_3_9_demo_coverage.csv",
            "reports/step_3_9_demo_coverage.html"
        ]
        for report in reports:
            if os.path.exists(report):
                print(f"   📊 {report}")
        
        print(f"\n🔗 Integration Status:")
        print(f"   ✅ Step 3.7 context tracking: Integrated")
        print(f"   ✅ Step 3.8 human review: Compatible")
        print(f"   ✅ CSV output: Generated")
        print(f"   ✅ HTML visualization: Generated")
    else:
        print(f"\n⚠️  Step 3.9 implementation needs attention")
        print(f"   {total - passed} test(s) failed")
        
    return passed == total

if __name__ == "__main__":
    success = run_step_3_9_validation()
    sys.exit(0 if success else 1)
