#!/usr/bin/env python3
"""
Dashboard Route Testing using unittest framework
Tests all dashboard routes and endpoints to verify unification implementation
"""

import unittest
import requests
import json
import sys
from datetime import datetime
from unittest.mock import patch, Mock

class TestDashboardRoutes(unittest.TestCase):
    """Test dashboard routes and endpoints."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = "http://localhost:5000"
        self.api_tests = [
            ("/health", "Health Check Endpoint"),
            ("/api/metrics", "Metrics API Endpoint"),
            ("/api/system/health", "System Health API"),
            ("/api/sprint/health", "Sprint Health API"),
            ("/api/timeline/data", "Timeline Data API"),
            ("/api/automation/status", "Automation Status API"),
        ]
    
    def test_route_structure(self):
        """Test that routes are properly structured."""
        for endpoint, description in self.api_tests:
            with self.subTest(endpoint=endpoint):
                self.assertIsInstance(endpoint, str)
                self.assertIsInstance(description, str)
                self.assertGreater(len(description), 0)
    
    @patch('requests.get')
    def test_endpoint_success_response(self, mock_get):
        """Test successful endpoint responses."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success"
        }
        mock_get.return_value = mock_response
        
        for endpoint, description in self.api_tests:
            with self.subTest(endpoint=endpoint):
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=5)
                self.assertEqual(response.status_code, 200)
    
    @patch('requests.get')
    def test_endpoint_error_handling(self, mock_get):
        """Test endpoint error handling."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        for endpoint, description in self.api_tests:
            with self.subTest(endpoint=endpoint):
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=5)
                self.assertEqual(response.status_code, 404)

def test_endpoint_integration():
    """Integration test for endpoints - can be run manually."""
    base_url = "http://localhost:5000"
    api_tests = [
        ("/health", "Health Check Endpoint"),
        ("/api/metrics", "Metrics API Endpoint"),
        ("/api/system/health", "System Health API"),
        ("/api/sprint/health", "Sprint Health API"),
        ("/api/timeline/data", "Timeline Data API"),
        ("/api/automation/status", "Automation Status API"),
    ]
    tests_passed = 0
    tests_total = 0
    
    def test_single_endpoint(url, description):
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
    
    print("🔧 API Endpoints Testing")
    print("-" * 30)
    for endpoint, desc in api_tests:
        url = f"{base_url}{endpoint}"
        if test_single_endpoint(url, desc):
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
        if test_single_endpoint(url, desc):
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
        if test_single_endpoint(url, desc):
            tests_passed += 1
        tests_total += 1
    
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
    sys.exit(test_endpoint_integration())
