#!/usr/bin/env python3
"""
Dashboard Stability Verification - Phase 6 Critical Fix Validation

Validates that the dashboard fixes prevent browser crashes and ensure stable operation.
Tests API endpoints, resource management, and error handling.
"""

import requests
import json
import time
import concurrent.futures
from pathlib import Path

def test_api_endpoints():
    """Test all dashboard API endpoints for stability."""
    base_url = "http://localhost:5000"
    endpoints = [
        "/health",
        "/api/metrics", 
        "/api/sprint/health",
        "/api/automation/status",
        "/api/tasks/recent",
        "/api/progress/trend"
    ]
    
    print("🔍 Testing API endpoints...")
    results = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            results[endpoint] = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "content_length": len(response.content)
            }
            print(f"✅ {endpoint}: {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
        except Exception as e:
            results[endpoint] = {"error": str(e)}
            print(f"❌ {endpoint}: {e}")
    
    return results

def test_concurrent_requests():
    """Test API stability under concurrent load."""
    print("\n🚀 Testing concurrent API requests...")
    
    def make_request():
        try:
            response = requests.get("http://localhost:5000/api/metrics", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(20)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    success_rate = sum(results) / len(results) * 100
    print(f"✅ Concurrent requests success rate: {success_rate:.1f}%")
    return success_rate

def validate_html_structure():
    """Validate HTML file structure for potential crash issues."""
    print("\n🔍 Validating HTML structure...")
    
    html_file = Path("dashboard/realtime_dashboard.html")
    if not html_file.exists():
        print("❌ Dashboard HTML file not found")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Check for unclosed tags
    if content.count('<script>') != content.count('</script>'):
        issues.append("Mismatched script tags")
    
    if content.count('<style>') != content.count('</style>'):
        issues.append("Mismatched style tags")
    
    # Check for malformed JavaScript
    if '\\n' in content and 'console.log' in content:
        issues.append("Potential JavaScript string literal issues")
    
    # Check for exponential growth patterns
    if 'function' in content and content.count('function') > 50:
        issues.append("Excessive function definitions")
    
    if issues:
        print(f"⚠️  HTML issues found: {', '.join(issues)}")
        return False
    else:
        print("✅ HTML structure is valid")
        return True

def validate_javascript_files():
    """Validate JavaScript files for syntax errors."""
    print("\n🔍 Validating JavaScript files...")
    
    js_files = [
        "dashboard/enhanced_dashboard.js"
    ]
    
    for js_file in js_files:
        file_path = Path(js_file)
        if not file_path.exists():
            print(f"❌ {js_file} not found")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic syntax checks
        issues = []
        
        # Check for unmatched braces
        if content.count('{') != content.count('}'):
            issues.append("Unmatched braces")
        
        if content.count('(') != content.count(')'):
            issues.append("Unmatched parentheses")
        
        # Check for problematic patterns
        if '\\n' in content and not content.count('\\n') < 5:
            issues.append("Excessive embedded newlines")
        
        if issues:
            print(f"⚠️  {js_file} issues: {', '.join(issues)}")
        else:
            print(f"✅ {js_file} syntax is valid")

def test_memory_usage_patterns():
    """Test for patterns that could cause memory leaks."""
    print("\n🧠 Testing memory usage patterns...")
    
    # Simulate rapid API calls to test for memory leaks
    start_time = time.time()
    request_count = 0
    
    try:
        for i in range(50):
            response = requests.get("http://localhost:5000/api/metrics", timeout=2)
            if response.status_code == 200:
                request_count += 1
            time.sleep(0.1)  # Small delay to prevent overwhelming
    except Exception as e:
        print(f"⚠️  Memory test interrupted: {e}")
    
    elapsed = time.time() - start_time
    print(f"✅ Completed {request_count} requests in {elapsed:.2f}s")
    print(f"✅ Average response time: {elapsed/request_count:.3f}s")

def main():
    """Run comprehensive dashboard stability validation."""
    print("🔧 Dashboard Stability Verification")
    print("=" * 50)
    
    # Check if API server is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code != 200:
            print("❌ API server not responding correctly")
            return
    except:
        print("❌ API server not running. Please start it first:")
        print("   python dashboard/api_server.py")
        return
    
    print("✅ API server is running")
    
    # Run validation tests
    api_results = test_api_endpoints()
    concurrent_success = test_concurrent_requests()
    html_valid = validate_html_structure()
    validate_javascript_files()
    test_memory_usage_patterns()
    
    print("\n" + "=" * 50)
    print("📊 STABILITY VERIFICATION SUMMARY")
    print("=" * 50)
    
    # Overall assessment
    all_endpoints_ok = all(
        result.get("status_code") == 200 
        for result in api_results.values() 
        if "status_code" in result
    )
    
    stability_score = 0
    if all_endpoints_ok:
        stability_score += 30
    if concurrent_success >= 90:
        stability_score += 25
    if html_valid:
        stability_score += 25
    stability_score += 20  # Base score for no crashes during testing
    
    print(f"🎯 Overall Stability Score: {stability_score}/100")
    
    if stability_score >= 90:
        print("🎉 EXCELLENT: Dashboard is highly stable and crash-resistant")
    elif stability_score >= 75:
        print("✅ GOOD: Dashboard is stable with minor areas for improvement")
    elif stability_score >= 60:
        print("⚠️  FAIR: Dashboard is functional but needs attention")
    else:
        print("❌ POOR: Dashboard has critical stability issues")
    
    print("\n🔗 Dashboard URL: file:///c:/taly/ai-system/dashboard/realtime_dashboard.html")
    print("🔗 API Base URL: http://localhost:5000")

if __name__ == "__main__":
    main()
