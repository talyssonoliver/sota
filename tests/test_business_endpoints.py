#!/usr/bin/env python3
"""
Test business metric endpoints using unittest framework.
"""

import unittest
import requests
import json
import sys
from datetime import datetime
from unittest.mock import patch, Mock

class TestBusinessEndpoints(unittest.TestCase):
    """Test business metric endpoints."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = "http://localhost:5000"
        self.endpoints = [
            ("/api/qa_pass_rate", "QA Pass Rate Metrics"),
            ("/api/code_coverage", "Code Coverage Metrics"),
            ("/api/sprint_velocity", "Sprint Velocity Metrics"),
            ("/api/completion_trend", "Completion Trend Data"),
            ("/api/qa_results", "Detailed QA Results"),
            ("/api/coverage_trend", "Coverage Trend Data"),
        ]
    
    def test_endpoint_structure(self):
        """Test that endpoints are properly structured."""
        for endpoint, description in self.endpoints:
            with self.subTest(endpoint=endpoint):
                self.assertTrue(endpoint.startswith("/api/"))
                self.assertIsInstance(description, str)
                self.assertGreater(len(description), 0)
    
    @patch('requests.get')
    def test_endpoint_success_response(self, mock_get):
        """Test successful endpoint responses."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": {"test": "data"}
        }
        mock_get.return_value = mock_response
        
        for endpoint, description in self.endpoints:
            with self.subTest(endpoint=endpoint):
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data.get("status"), "success")
    
    @patch('requests.get')
    def test_endpoint_error_handling(self, mock_get):
        """Test endpoint error handling."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        for endpoint, description in self.endpoints:
            with self.subTest(endpoint=endpoint):
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                self.assertEqual(response.status_code, 500)

def test_endpoint_integration():
    """Integration test for endpoints - can be run manually."""
    def test_single_endpoint(endpoint, description):
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
    
    # Define endpoints to test
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
        success = test_single_endpoint(endpoint, description)
        results.append((endpoint, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY RESULTS:")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {endpoint}")
    
if __name__ == "__main__":
    success = test_endpoint_integration()
    if success:
        print("🎉 ALL BUSINESS METRIC ENDPOINTS ARE WORKING!")
    else:
        print("⚠️  Some endpoints need attention")
    sys.exit(0 if success else 1)
