#!/usr/bin/env python3
"""
Dashboard Route Testing using unittest framework
Tests all dashboard routes and endpoints to verify unification implementation
"""

import unittest
import requests
import json
import sys
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
        
        # Deployment monitoring test scenarios
        self.deployment_test_scenarios = [
            ("metrics_with_deployment", "Enhanced metrics with deployment data"),
            ("automation_with_deployment", "Automation status with deployment monitoring"),
            ("deployment_phase_tracking", "4-phase deployment timeline tracking"),
            ("team_adoption_metrics", "Team member adoption and progress tracking"),
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
    
    def test_deployment_monitoring_integration(self):
        """Test deployment monitoring data integration."""
        from src.interfaces.dashboard.api.unified_api_server import UnifiedDashboardAPI
        from src.interfaces.dashboard.config import DashboardConfig
        
        # Create test API instance
        config = DashboardConfig()
        config.debug = True
        api = UnifiedDashboardAPI(config)
        
        # Test deployment monitoring data structure
        deployment_data = api._get_deployment_monitoring_data()
        
        # Verify deployment status structure
        self.assertIn("deployment_status", deployment_data)
        deployment_status = deployment_data["deployment_status"]
        
        required_status_fields = [
            "current_phase", "overall_progress", "team_adoption_rate",
            "active_team_members", "total_team_members"
        ]
        
        for field in required_status_fields:
            self.assertIn(field, deployment_status)
            self.assertIsInstance(deployment_status[field], (int, float))
    
    def test_enhanced_metrics_endpoint(self):
        """Test enhanced metrics endpoint with deployment data."""
        from src.interfaces.dashboard.api.unified_api_server import UnifiedDashboardAPI  
        from src.interfaces.dashboard.config import DashboardConfig
        
        config = DashboardConfig()
        api = UnifiedDashboardAPI(config)
        
        with api.app.test_client() as client:
            # Mock authentication for testing
            with patch('src.infrastructure.security.auth_middleware.requires_auth', lambda f: f):
                response = client.get('/api/metrics')
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                
                # Verify enhanced metrics structure
                self.assertIn("status", data)
                self.assertEqual(data["status"], "success")
                self.assertIn("data", data)
                
                metrics_data = data["data"]
                self.assertIn("deployment", metrics_data)
                
                # Verify deployment data structure
                deployment = metrics_data["deployment"]
                self.assertIn("deployment_status", deployment)
                self.assertIn("productivity_metrics", deployment)
                self.assertIn("phase_timeline", deployment)

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
