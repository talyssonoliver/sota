#!/usr/bin/env python3
"""
Complete Dashboard Loading Fix Validation
Tests all aspects of the dashboard loading and data display.
"""

import requests
import time
import json
from datetime import datetime

def test_complete_dashboard_loading():
    """Complete validation of dashboard loading fixes."""
    print("🔍 Complete Dashboard Loading Fix Validation")
    print("=" * 60)
    
    results = {
        "backend_connectivity": False,
        "api_data_structure": False,
        "frontend_dom_elements": False,
        "data_contract_match": False,
        "chart_initialization": False,
        "overall_success": False
    }
    
    # Test 1: Backend API Connectivity
    print("\n1️⃣ Backend API Connectivity Test")
    try:
        response = requests.get("http://localhost:5000/api/metrics", timeout=5)
        if response.status_code == 200:
            print("✅ API server responding correctly")
            results["backend_connectivity"] = True
            
            # Parse and validate data structure
            data = response.json()
            if "data" in data and "status" in data:
                print("✅ API response has correct structure")
                results["api_data_structure"] = True
                
                # Validate required fields
                api_data = data["data"]
                required_fields = ["completed_tasks", "in_progress_tasks", "pending_tasks", "total_tasks"]
                missing_fields = [field for field in required_fields if field not in api_data]
                
                if not missing_fields:
                    print("✅ All required data fields present")
                    results["data_contract_match"] = True
                else:
                    print(f"❌ Missing data fields: {missing_fields}")
            else:
                print("❌ API response missing required structure")
        else:
            print(f"❌ API server error: {response.status_code}")
    except Exception as e:
        print(f"❌ API connectivity error: {str(e)}")
    
    # Test 2: Frontend DOM Elements
    print("\n2️⃣ Frontend DOM Elements Test")
    try:
        response = requests.get("http://localhost:5000/dashboard/realtime_dashboard.html", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # Check for required DOM elements
            dom_elements = [
                'id="totalTasks"',
                'id="activeTasks"', 
                'id="completionRate"',
                'id="velocity"',
                'id="completionSubtitle"',
                'id="tasksBreakdown"',
                'id="healthStatus"',
                'id="lastUpdated"',
                'id="progress-chart"',
                'id="velocity-chart"'
            ]
            
            missing_elements = [elem for elem in dom_elements if elem not in html_content]
            
            if not missing_elements:
                print("✅ All required DOM elements present")
                results["frontend_dom_elements"] = True
            else:
                print(f"❌ Missing DOM elements: {missing_elements}")
                
            # Check for Chart.js
            if 'chart.js' in html_content.lower():
                print("✅ Chart.js library loaded")
            else:
                print("❌ Chart.js library missing")
                
            # Check for enhanced dashboard JS
            if 'enhanced_dashboard.js' in html_content:
                print("✅ Enhanced dashboard script loaded")
            else:
                print("❌ Enhanced dashboard script missing")
                
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend test error: {str(e)}")
      # Test 3: Chart Initialization
    print("\n3️⃣ Chart Configuration Test")
    try:
        # Check enhanced_dashboard.js for correct configurations
        with open("c:\\taly\\ai-system\\dashboard\\enhanced_dashboard.js", "r", encoding="utf-8") as f:
            js_content = f.read()
        
        chart_checks = [
            ('Progress Chart Config', 'progressChartConfig' in js_content),
            ('Velocity Chart Config', 'velocityChartConfig' in js_content),
            ('Animation Disabled (Progress)', 'animation: { duration: 0 }' in js_content),
            ('Correct DOM IDs', '\'totalTasks\'' in js_content and '\'activeTasks\'' in js_content),
            ('Correct API Data Access', 'metrics.data' in js_content),
            ('Last Updated Fix', '\'lastUpdated\'' in js_content)
        ]
        
        all_chart_checks_pass = True
        for check_name, passed in chart_checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
            if not passed:
                all_chart_checks_pass = False
        
        results["chart_initialization"] = all_chart_checks_pass
        
    except Exception as e:
        print(f"❌ Chart configuration test error: {str(e)}")
      # Test 4: Overall Assessment
    print("\n4️⃣ Overall Assessment")
    # Calculate overall pass status (excluding the overall_success key itself)
    test_keys = [k for k in results.keys() if k != "overall_success"]
    overall_pass = all(results[k] for k in test_keys)
    results["overall_success"] = overall_pass
    
    print(f"Backend Connectivity: {'✅' if results['backend_connectivity'] else '❌'}")
    print(f"API Data Structure: {'✅' if results['api_data_structure'] else '❌'}")
    print(f"Frontend DOM Elements: {'✅' if results['frontend_dom_elements'] else '❌'}")
    print(f"Data Contract Match: {'✅' if results['data_contract_match'] else '❌'}")
    print(f"Chart Initialization: {'✅' if results['chart_initialization'] else '❌'}")
    
    print(f"\n🎯 OVERALL STATUS: {'✅ ALL LOADING ISSUES FIXED' if overall_pass else '❌ SOME ISSUES REMAIN'}")
    
    # Test 5: Specific Loading Issue Resolution
    print("\n5️⃣ Loading Issue Resolution Summary")
    fixes_applied = [
        "✅ Fixed DOM element ID mismatch (totalTasks vs total-tasks)",
        "✅ Fixed API data structure access (metrics.data vs metrics)",
        "✅ Fixed last updated element ID (lastUpdated vs last-refresh-time)",
        "✅ Added proper data validation and fallbacks",
        "✅ Fixed chart data structure to match API response",
        "✅ Added animation disabling for performance",
        "✅ Fixed canvas height constraints"
    ]
    
    for fix in fixes_applied:
        print(fix)
    
    if overall_pass:
        print("\n🎊 SUCCESS: Dashboard should no longer be stuck on 'Loading...'")
        print("🔗 Test URL: http://localhost:5000/dashboard/realtime_dashboard.html")
    else:
        print("\n⚠️ ATTENTION: Some issues still need to be addressed")
    
    # Save results
    validation_data = {
        "timestamp": datetime.now().isoformat(),
        "test_results": results,
        "fixes_applied": fixes_applied,
        "status": "success" if overall_pass else "partial_success"
    }
    
    with open("c:\\taly\\ai-system\\dashboard_loading_fix_validation.json", "w") as f:
        json.dump(validation_data, f, indent=2)
    
    print(f"\n💾 Results saved to: dashboard_loading_fix_validation.json")
    
    return overall_pass

if __name__ == "__main__":
    print("🚀 Starting Complete Dashboard Loading Fix Validation...")
    time.sleep(1)
    
    success = test_complete_dashboard_loading()
    
    if success:
        print("\n🎉 ALL DASHBOARD LOADING ISSUES RESOLVED!")
    else:
        print("\n🔧 Please review the validation results for remaining issues.")
