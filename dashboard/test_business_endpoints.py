#!/usr/bin/env python3
"""
Test script to validate all business metric endpoints are working correctly.
"""

import requests
import json
import sys
from datetime import datetime

def test_endpoint(endpoint, description):
    """Test a single API endpoint."""
    try:
        url = f"http://localhost:5000{endpoint}"
        print(f"\n📊 Testing {description}")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"   ✅ SUCCESS - Endpoint working correctly")
                print(f"   📈 Data keys: {list(data.get('data', {}).keys())}")
                return True
            else:
                print(f"   ❌ ERROR - API returned error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ HTTP ERROR - Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ CONNECTION ERROR - Server not running on localhost:5000")
        return False
    except Exception as e:
        print(f"   ❌ EXCEPTION - {str(e)}")
        return False

def main():
    """Test all business metric endpoints."""
    print("🚀 Testing Business Metric Endpoints")
    print("=" * 50)
    
    endpoints_to_test = [
        ("/api/qa_pass_rate", "QA Pass Rate Metrics"),
        ("/api/code_coverage", "Code Coverage Metrics"),
        ("/api/sprint_velocity", "Sprint Velocity Metrics"),
        ("/api/completion_trend", "Completion Trend Data"),
        ("/api/qa_results", "Detailed QA Results"),
        ("/api/coverage_trend", "Coverage Trend Data"),
        # Also test existing endpoints to ensure they still work
        ("/api/metrics", "General Metrics"),
        ("/api/system/health", "System Health"),
        ("/api/timeline/data", "Timeline Data")
    ]
    
    results = []
    
    for endpoint, description in endpoints_to_test:
        success = test_endpoint(endpoint, description)
        results.append((endpoint, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY RESULTS:")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {endpoint}")
    
    print(f"\n🎯 Results: {successful}/{total} endpoints working")
    
    if successful == total:
        print("🎉 ALL BUSINESS METRIC ENDPOINTS ARE WORKING!")
        return True
    else:
        print("⚠️  Some endpoints need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
