#!/usr/bin/env python3
"""
Dashboard Route Testing Script
Tests all dashboard routes and endpoints to verify unification implementation
"""

import requests
import json
import sys
from datetime import datetime

def test_endpoint(url, description):
    """Test a single endpoint and return results."""
    try:
        response = requests.get(url, timeout=5)
        status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
        print(f"{status} | {description}")
        print(f"      URL: {url}")
        if response.status_code != 200:
            print(f"      Error: {response.text[:100]}...")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ERROR | {description}")
        print(f"      URL: {url}")
        print(f"      Error: {str(e)}")
        print()
        return False

def main():
    """Run comprehensive dashboard route testing."""
    print("🧪 Dashboard Unification Route Testing")
    print("=" * 50)
    print(f"Test Date: {datetime.now().isoformat()}")
    print()
    
    base_url = "http://localhost:5000"
    
    # Test results tracking
    tests_passed = 0
    tests_total = 0
    
    # Core API endpoints
    api_tests = [
        (f"{base_url}/health", "Health Check Endpoint"),
        (f"{base_url}/api/metrics", "Metrics API Endpoint"),
        (f"{base_url}/api/system/health", "System Health API"),
        (f"{base_url}/api/sprint/health", "Sprint Health API"),
        (f"{base_url}/api/timeline/data", "Timeline Data API"),
        (f"{base_url}/api/automation/status", "Automation Status API"),
    ]
    
    print("🔧 API Endpoints Testing")
    print("-" * 30)
    for url, desc in api_tests:
        if test_endpoint(url, desc):
            tests_passed += 1
        tests_total += 1
    
    # Dashboard routes
    dashboard_tests = [
        (f"{base_url}/dashboard/", "Unified Dashboard (Main)"),
        (f"{base_url}/dashboard/unified_dashboard.html", "Unified Dashboard (Direct)"),
        (f"{base_url}/dashboard/enhanced_dashboard_working.js", "Enhanced Dashboard JS"),
    ]
    
    print("📊 Dashboard Routes Testing")
    print("-" * 30)
    for url, desc in dashboard_tests:
        if test_endpoint(url, desc):
            tests_passed += 1
        tests_total += 1
    
    # Legacy dashboard routes (should work but show deprecation)
    legacy_tests = [
        (f"{base_url}/legacy/completion_charts", "Legacy Completion Charts"),
        (f"{base_url}/legacy/enhanced_completion_charts", "Legacy Enhanced Charts"),
        (f"{base_url}/legacy/realtime_dashboard", "Legacy Realtime Dashboard"),
    ]
    
    print("⚠️  Legacy Dashboard Routes Testing")
    print("-" * 35)
    for url, desc in legacy_tests:
        if test_endpoint(url, desc):
            tests_passed += 1
        tests_total += 1
    
    # Summary
    print("📋 Test Summary")
    print("=" * 50)
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("\n🎉 ALL TESTS PASSED! Dashboard unification is successful.")
        return 0
    else:
        print(f"\n⚠️  {tests_total - tests_passed} tests failed. Check API server and routes.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
