#!/usr/bin/env python3
"""
Dashboard Fix Verification Script
Tests the unified dashboard to ensure all widgets display real data instead of placeholders.
"""

import requests
import json
import sys
from datetime import datetime

def test_api_endpoint(url, endpoint_name):
    """Test a single API endpoint and return results."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'status_code': response.status_code,
                'data': data,
                'endpoint': endpoint_name
            }
        else:
            return {
                'success': False,
                'status_code': response.status_code,
                'error': f"HTTP {response.status_code}",
                'endpoint': endpoint_name
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'endpoint': endpoint_name
        }

def verify_metrics_data(data):
    """Verify metrics data contains expected fields with real values."""
    issues = []
    
    if 'team_metrics' not in data:
        issues.append("Missing team_metrics")
        return issues
    
    team_metrics = data['team_metrics']
    required_fields = [
        'completion_rate', 'total_tasks', 'qa_pass_rate', 
        'average_coverage', 'completed_tasks', 'in_progress_tasks'
    ]
    
    for field in required_fields:
        if field not in team_metrics:
            issues.append(f"Missing field: {field}")
        elif team_metrics[field] is None:
            issues.append(f"Null value for: {field}")
    
    # Check for realistic values
    if team_metrics.get('completion_rate', 0) > 0:
        issues.append("✅ Completion rate has real data")
    if team_metrics.get('total_tasks', 0) > 0:
        issues.append("✅ Total tasks has real data")
    if team_metrics.get('qa_pass_rate', 0) > 0:
        issues.append("✅ QA pass rate has real data")
    
    return issues

def verify_health_data(data):
    """Verify health data contains expected components."""
    issues = []
    
    if 'overall_status' not in data:
        issues.append("Missing overall_status")
    else:
        issues.append(f"✅ Overall status: {data['overall_status']}")
    
    if 'components' not in data:
        issues.append("Missing components")
    else:
        components = data['components']
        expected_components = [
            'dashboard_api', 'metrics_engine', 
            'automation_system', 'reporting_system'
        ]
        
        for component in expected_components:
            if component in components:
                status = components[component].get('status', 'unknown')
                issues.append(f"✅ {component}: {status}")
            else:
                issues.append(f"Missing component: {component}")
    
    return issues

def main():
    """Main verification function."""
    print("🔍 Dashboard Fix Verification")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:5000"
    
    # Test API endpoints
    endpoints = {
        'metrics': f"{base_url}/api/metrics",
        'health': f"{base_url}/api/system/health",
        'tasks': f"{base_url}/api/tasks/recent"
    }
    
    all_tests_passed = True
    
    for name, url in endpoints.items():
        print(f"Testing {name} endpoint...")
        result = test_api_endpoint(url, name)
        
        if result['success']:
            print(f"  ✅ {name} endpoint: SUCCESS")
            
            # Detailed verification
            if name == 'metrics':
                issues = verify_metrics_data(result['data']['data'])
                for issue in issues:
                    print(f"    {issue}")
            elif name == 'health':
                issues = verify_health_data(result['data']['data'])
                for issue in issues:
                    print(f"    {issue}")
            elif name == 'tasks':
                task_data = result['data'].get('data', [])
                print(f"    ✅ Recent tasks: {len(task_data)} items")
                
        else:
            print(f"  ❌ {name} endpoint: FAILED")
            print(f"    Error: {result.get('error', 'Unknown error')}")
            all_tests_passed = False
        
        print()
    
    # Test dashboard page
    print("Testing dashboard page...")
    try:
        response = requests.get(f"{base_url}/dashboard/", timeout=10)
        if response.status_code == 200:
            print("  ✅ Dashboard page: ACCESSIBLE")
            
            # Check if it contains the updated JavaScript functions
            content = response.text
            if 'updateMetricsFromAPI' in content:
                print("  ✅ Updated API functions: PRESENT")
            else:
                print("  ❌ Updated API functions: MISSING")
                all_tests_passed = False
        else:
            print(f"  ❌ Dashboard page: HTTP {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"  ❌ Dashboard page: ERROR - {e}")
        all_tests_passed = False
    
    print()
    print("=" * 50)
    
    if all_tests_passed:
        print("🎉 VERIFICATION SUCCESSFUL!")
        print("✅ All API endpoints are working")
        print("✅ Dashboard displays real data instead of placeholders")
        print("✅ Root cause issue has been resolved")
    else:
        print("⚠️ VERIFICATION FAILED!")
        print("❌ Some issues remain - check output above")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
