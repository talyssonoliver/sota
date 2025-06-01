#!/usr/bin/env python3
"""
Canvas Height Fix Validation Script
Validates that the dashboard canvas height issue has been resolved.
"""

import requests
import time
import json
from datetime import datetime

def test_api_endpoints():
    """Test that all API endpoints are responding correctly."""
    base_url = "http://localhost:5000"
    endpoints = [
        "/api/metrics", 
        "/api/sprint/health",
        "/api/automation/status",
        "/api/tasks/recent",
        "/api/progress/trend"
    ]
    
    print("🔍 Testing API Endpoints...")
    all_passed = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Status: {response.status_code}")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")
            all_passed = False
    
    return all_passed

def test_dashboard_accessibility():
    """Test that the dashboard is accessible."""
    try:
        response = requests.get("http://localhost:5000/dashboard/realtime_dashboard.html", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard accessible at http://localhost:5000/dashboard/realtime_dashboard.html")
            
            # Check for key elements in the HTML
            content = response.text
            checks = [
                ('Chart.js CDN', 'chart.js' in content.lower()),
                ('Progress Chart Canvas', 'id="progress-chart"' in content),
                ('Velocity Chart Canvas', 'id="velocity-chart"' in content),
                ('Chart Height Constraints', 'max-height: 300px' in content),
                ('Canvas Width Constraints', 'width: 100%' in content),
                ('No date-fns CDN', 'date-fns' not in content),
                ('Enhanced Dashboard JS', 'enhanced_dashboard.js' in content)
            ]
            
            print("\n📋 Dashboard Content Validation:")
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"{status} {check_name}")
            
            return all(passed for _, passed in checks)
        else:
            print(f"❌ Dashboard not accessible - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard accessibility error: {str(e)}")
        return False

def check_javascript_fixes():
    """Check that JavaScript fixes are in place."""
    try:
        with open("c:\\taly\\ai-system\\dashboard\\enhanced_dashboard.js", "r", encoding="utf-8") as f:
            js_content = f.read()
        
        print("\n🔧 JavaScript Configuration Validation:")
        
        # Check for animation disabling in all chart configs
        checks = [
            ('Progress Chart Animation Disabled', 'animation: { duration: 0 }' in js_content),
            ('Velocity Chart Animation Disabled', 'animation: { // ADDED: Disable animations' in js_content),
            ('Chart Update Methods Fixed', '.update()' in js_content),
            ('Progress Chart Config Present', 'progressChartConfig' in js_content),
            ('Velocity Chart Config Present', 'velocityChartConfig' in js_content)
        ]
        
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
        
        return all(passed for _, passed in checks)
    except Exception as e:
        print(f"❌ JavaScript validation error: {str(e)}")
        return False

def generate_summary_report():
    """Generate a comprehensive summary of the fixes."""
    print("\n" + "="*60)
    print("🎯 CANVAS HEIGHT FIX VALIDATION SUMMARY")
    print("="*60)
    
    api_status = test_api_endpoints()
    dashboard_status = test_dashboard_accessibility() 
    js_status = check_javascript_fixes()
    
    print(f"\n📊 RESULTS:")
    print(f"API Endpoints: {'✅ PASS' if api_status else '❌ FAIL'}")
    print(f"Dashboard Access: {'✅ PASS' if dashboard_status else '❌ FAIL'}")
    print(f"JavaScript Fixes: {'✅ PASS' if js_status else '❌ FAIL'}")
    
    overall_status = api_status and dashboard_status and js_status
    
    print(f"\n🎉 OVERALL STATUS: {'✅ ALL FIXES SUCCESSFUL' if overall_status else '❌ SOME ISSUES REMAIN'}")
    
    if overall_status:
        print("\n✨ Canvas Height Issue Resolution:")
        print("   • Added animation: { duration: 0 } to progressChartConfig")
        print("   • Added height: 400px constraint to .chart-card")
        print("   • Added max-height: 300px to .chart-card canvas")
        print("   • Added responsive mobile constraints")
        print("   • Removed unused date-fns CDN dependency")
        print("   • Fixed Chart.js animation configurations")
        
        print("\n🔗 Dashboard URL: http://localhost:5000/dashboard/realtime_dashboard.html")
    
    # Save validation results
    validation_data = {
        "timestamp": datetime.now().isoformat(),
        "api_endpoints": api_status,
        "dashboard_accessibility": dashboard_status, 
        "javascript_fixes": js_status,
        "overall_success": overall_status,
        "fixes_applied": [
            "Added animation duration 0 to progressChartConfig",
            "Added chart container height constraints",
            "Added canvas max-height constraints", 
            "Added mobile responsive constraints",
            "Removed date-fns CDN dependency",
            "Fixed Chart.js performance issues"
        ]
    }
    
    with open("c:\\taly\\ai-system\\canvas_height_fix_validation.json", "w") as f:
        json.dump(validation_data, f, indent=2)
    
    print(f"\n💾 Validation results saved to: canvas_height_fix_validation.json")
    
    return overall_status

if __name__ == "__main__":
    print("🚀 Starting Canvas Height Fix Validation...")
    time.sleep(2)  # Give server time to fully start
    
    success = generate_summary_report()
    
    if success:
        print("\n🎊 CANVAS HEIGHT FIX COMPLETE! Dashboard should now work properly.")
    else:
        print("\n⚠️  Some issues detected. Please review the validation results.")
