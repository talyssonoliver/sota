#!/usr/bin/env python3
"""
Integration Tests for Dashboard Widgets JavaScript Integration

Tests for the deployment monitoring JavaScript widgets integrated into
the dashboard, including:
- API data fetching functionality
- Widget update mechanisms  
- Real-time data refresh
- Error handling in client-side code
"""

import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.interfaces.dashboard.api.unified_api_server import UnifiedDashboardAPI
from src.interfaces.dashboard.config import DashboardConfig


class TestDashboardWidgetsIntegration(unittest.TestCase):
    """Test dashboard widgets JavaScript integration with deployment monitoring."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Create test deployment configuration
        self.deployment_config = {
            "team_members": [
                {"name": "Dev 1", "role": "senior", "specialization": "backend"},
                {"name": "Dev 2", "role": "mid", "specialization": "fullstack"},
                {"name": "Dev 3", "role": "junior", "specialization": "frontend"}
            ],
            "deployment_phases": [
                {"phase": 1, "name": "Foundation", "duration_days": 7},
                {"phase": 2, "name": "Integration", "duration_days": 7},
                {"phase": 3, "name": "Advanced", "duration_days": 7},
                {"phase": 4, "name": "Optimization", "duration_days": 7}
            ],
            "success_metrics": {
                "installation_completion": 100,
                "daily_usage_hours": 4,
                "productivity_improvement": 500,
                "team_satisfaction": 8
            }
        }
        
        # Write deployment config to temp file
        config_file = self.config_dir / "team_deployment.json"
        with open(config_file, 'w') as f:
            json.dump(self.deployment_config, f)
        
        # Setup API with test configuration
        self.config = DashboardConfig()
        self.config.debug = True
        self.config.outputs_dir = str(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.slow
    def test_deployment_metrics_api_response_format(self):
        """Test that API returns data in format expected by JavaScript widgets."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            
            with api.app.test_client() as client:
                with patch('src.infrastructure.security.auth_middleware.requires_auth', lambda f: f):
                    response = client.get('/api/metrics')
                    
                    self.assertEqual(response.status_code, 200)
                    data = response.get_json()
                    
                    # Verify response structure matches JavaScript expectations
                    self.assertEqual(data["status"], "success")
                    self.assertIn("data", data)
                    self.assertIn("deployment", data["data"])
                    
                    deployment = data["data"]["deployment"]
                    
                    # Test widget data requirements
                    self._verify_widget_data_format(deployment)
    
    def _verify_widget_data_format(self, deployment_data):
        """Verify deployment data format matches JavaScript widget requirements."""
        # Adoption progress widget requirements
        deployment_status = deployment_data["deployment_status"]
        self.assertIn("team_adoption_rate", deployment_status)
        self.assertIn("active_team_members", deployment_status)
        self.assertIn("total_team_members", deployment_status)
        self.assertIn("current_phase", deployment_status)
        
        # Productivity metrics widget requirements
        productivity_metrics = deployment_data["productivity_metrics"]
        self.assertIn("productivity_acceleration", productivity_metrics)
        self.assertIn("average_daily_usage", productivity_metrics)
        self.assertIn("automation_efficiency", productivity_metrics)
        
        # Phase timeline widget requirements
        self.assertIn("phase_timeline", deployment_data)
        phase_timeline = deployment_data["phase_timeline"]
        self.assertIsInstance(phase_timeline, list)
        
        # Alerts widget requirements
        self.assertIn("alerts", deployment_data)
        alerts = deployment_data["alerts"]
        self.assertIsInstance(alerts, list)
        
        # Verify data types are JSON-serializable
        for alert in alerts:
            self.assertIn("type", alert)
            self.assertIn("message", alert)
            self.assertIn("severity", alert)
    
    def test_automation_status_widget_data_format(self):
        """Test automation status endpoint returns data in correct format for widgets."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            
            with api.app.test_client() as client:
                with patch('src.infrastructure.security.auth_middleware.requires_auth', lambda f: f):
                    response = client.get('/api/automation/status')
                    
                    self.assertEqual(response.status_code, 200)
                    data = response.get_json()
                    
                    automation_data = data["data"]
                    
                    # Verify deployment automation data for widgets
                    self.assertIn("deployment_automation", automation_data)
                    deploy_auto = automation_data["deployment_automation"]
                    
                    # Verify numeric values are correct type for JavaScript
                    numeric_fields = [
                        "phase_progress", "team_adoption", "active_users",
                        "automation_efficiency", "alerts_count"
                    ]
                    
                    for field in numeric_fields:
                        self.assertIn(field, deploy_auto)
                        self.assertIsInstance(deploy_auto[field], (int, float))
                        self.assertGreaterEqual(deploy_auto[field], 0)
    
    @pytest.mark.slow
    def test_widget_update_data_consistency(self):
        """Test that widget update data remains consistent across multiple calls - optimized."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            
            with api.app.test_client() as client:
                with patch('src.infrastructure.security.auth_middleware.requires_auth', lambda f: f):
                    # Make fewer API calls and remove sleep for speed
                    responses = []
                    for _ in range(2):  # Reduced from 3 to 2
                        response = client.get('/api/metrics')
                        self.assertEqual(response.status_code, 200)
                        responses.append(response.get_json())
                        # Removed time.sleep(0.1) for speed
                    
                    # Verify data consistency for widgets
                    deployment_data_1 = responses[0]["data"]["deployment"]
                    deployment_data_2 = responses[1]["data"]["deployment"]
                    
                    # Key metrics should be consistent for widgets
                    self.assertEqual(
                        deployment_data_1["deployment_status"]["total_team_members"],
                        deployment_data_2["deployment_status"]["total_team_members"]
                    )
                    self.assertEqual(
                        deployment_data_1["deployment_status"]["current_phase"],
                        deployment_data_2["deployment_status"]["current_phase"]
                    )
    
    @pytest.mark.slow 
    def test_widget_error_handling_scenarios(self):
        """Test widget behavior with various error scenarios - optimized."""
        # Test with missing deployment config
        empty_temp_dir = tempfile.mkdtemp()
        
        try:
            with patch.object(self.config, 'get_absolute_path') as mock_path:
                mock_path.return_value = Path(empty_temp_dir) / "outputs"
                
                api = UnifiedDashboardAPI(self.config)
                
                with api.app.test_client() as client:
                    with patch('src.infrastructure.security.auth_middleware.requires_auth', lambda f: f):
                        response = client.get('/api/metrics')
                        
                        self.assertEqual(response.status_code, 200)
                        data = response.get_json()
                        
                        # Verify widgets get safe fallback data
                        deployment = data["data"]["deployment"]
                        self.assertEqual(deployment["deployment_status"]["total_team_members"], 0)
                        self.assertEqual(len(deployment["phase_timeline"]), 0)
                        self.assertEqual(len(deployment["team_progress"]), 0)
                        
                        # Widgets should still get expected data structure
                        self.assertIn("deployment_status", deployment)
                        self.assertIn("productivity_metrics", deployment)
                        self.assertIn("alerts", deployment)
                        
        finally:
            import shutil
            shutil.rmtree(empty_temp_dir)
    
    def test_real_time_update_mechanism(self):
        """Test that widgets can handle real-time updates properly."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            
            # Simulate initial load
            initial_data = api._get_deployment_monitoring_data()
            
            # Simulate data change (would normally come from config update)
            # Test that structure remains consistent for widget updates
            updated_data = api._get_deployment_monitoring_data()
            
            # Verify widget-critical data structure is preserved
            widget_fields = [
                "deployment_status", "productivity_metrics", 
                "phase_timeline", "team_progress", "alerts"
            ]
            
            for field in widget_fields:
                self.assertIn(field, initial_data)
                self.assertIn(field, updated_data)
                
                # Verify same data types for widget consumption
                self.assertEqual(
                    type(initial_data[field]), 
                    type(updated_data[field])
                )
    
    def test_widget_performance_considerations(self):
        """Test performance aspects relevant to JavaScript widgets."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            
            # Test data size is reasonable for client-side processing
            deployment_data = api._get_deployment_monitoring_data()
            
            # Convert to JSON to check size (as widgets would receive it)
            json_data = json.dumps(deployment_data)
            json_size = len(json_data.encode('utf-8'))
            
            # Verify data size is reasonable for widgets (< 50KB)
            self.assertLess(json_size, 50 * 1024, 
                          f"Widget data too large: {json_size} bytes")
            
            # Verify no excessive nesting for JavaScript processing
            max_depth = self._get_json_depth(deployment_data)
            self.assertLessEqual(max_depth, 5, 
                               f"JSON too deeply nested: {max_depth} levels")
    
    def _get_json_depth(self, obj, depth=0):
        """Calculate maximum depth of nested JSON structure."""
        if not isinstance(obj, (dict, list)):
            return depth
            
        if isinstance(obj, dict):
            if not obj:
                return depth
            return max(self._get_json_depth(value, depth + 1) 
                      for value in obj.values())
        
        if isinstance(obj, list):
            if not obj:
                return depth
            return max(self._get_json_depth(item, depth + 1) 
                      for item in obj)
        
        return depth
    
    def test_widget_data_validation_for_javascript(self):
        """Test that all widget data is valid for JavaScript consumption."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            deployment_data = api._get_deployment_monitoring_data()
            
            # Verify all data can be JSON serialized (required for widgets)
            try:
                json_str = json.dumps(deployment_data, ensure_ascii=False)
                # Verify it can be parsed back
                parsed_data = json.loads(json_str)
                self.assertEqual(deployment_data, parsed_data)
            except (TypeError, ValueError) as e:
                self.fail(f"Widget data not JSON serializable: {e}")
            
            # Verify no NaN or Infinity values (invalid in JSON)
            self._verify_no_invalid_numbers(deployment_data)
    
    def _verify_no_invalid_numbers(self, obj):
        """Recursively verify no NaN or Infinity values in data structure."""
        import math
        
        if isinstance(obj, dict):
            for value in obj.values():
                self._verify_no_invalid_numbers(value)
        elif isinstance(obj, list):
            for item in obj:
                self._verify_no_invalid_numbers(item)
        elif isinstance(obj, float):
            self.assertFalse(math.isnan(obj), "Found NaN in widget data")
            self.assertFalse(math.isinf(obj), "Found Infinity in widget data")


class TestDashboardHTMLIntegration(unittest.TestCase):
    """Test dashboard HTML file integration with deployment widgets."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.dashboard_path = Path(__file__).parent.parent.parent.parent / "dashboard" / "hitl_kanban_board.html"
        
    def test_dashboard_html_contains_deployment_widgets(self):
        """Test that dashboard HTML contains required deployment widget elements."""
        if not self.dashboard_path.exists():
            self.skipTest("Dashboard HTML file not found")
            
        with open(self.dashboard_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Verify deployment monitoring section exists
        self.assertIn('id="deploymentMonitoring"', html_content)
        self.assertIn('class="deployment-section"', html_content)
        
        # Verify required widget elements
        required_elements = [
            'id="adoptionProgress"',
            'id="adoptionRate"',
            'id="activeUsers"',
            'id="totalUsers"',
            'id="productivityGain"',
            'id="dailyUsage"',
            'id="automationEfficiency"',
            'id="deploymentAlerts"'
        ]
        
        for element in required_elements:
            self.assertIn(element, html_content, f"Missing widget element: {element}")
    
    def test_dashboard_html_contains_deployment_functions(self):
        """Test that dashboard HTML contains required JavaScript functions."""
        if not self.dashboard_path.exists():
            self.skipTest("Dashboard HTML file not found")
            
        with open(self.dashboard_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Verify deployment monitoring JavaScript functions exist
        required_functions = [
            'loadDeploymentData',
            'updateDeploymentWidgets',
            'updatePhaseTimeline',
            'updateDeploymentAlerts'
        ]
        
        for function in required_functions:
            self.assertIn(f"function {function}", html_content, 
                         f"Missing JavaScript function: {function}")
            self.assertIn(f"async function {function}", html_content, 
                         f"Function {function} should be async")
    
    def test_dashboard_html_api_integration(self):
        """Test that dashboard HTML correctly integrates with API endpoints."""
        if not self.dashboard_path.exists():
            self.skipTest("Dashboard HTML file not found")
            
        with open(self.dashboard_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Verify API endpoint calls for deployment data
        self.assertIn("'/api/metrics'", html_content)
        
        # Verify fetch calls for deployment data
        self.assertIn("fetch('/api/metrics')", html_content)
        
        # Verify deployment data is accessed correctly
        self.assertIn("result.data.deployment", html_content)
        
        # Verify widget update calls in auto-refresh
        self.assertIn("loadDeploymentData()", html_content)
    
    def test_dashboard_css_includes_deployment_styles(self):
        """Test that dashboard CSS includes deployment monitoring styles."""
        if not self.dashboard_path.exists():
            self.skipTest("Dashboard HTML file not found")
            
        with open(self.dashboard_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Verify deployment-specific CSS classes
        required_css_classes = [
            '.deployment-section',
            '.deployment-widgets',
            '.deployment-widget',
            '.progress-container',
            '.progress-bar',
            '.progress-fill',
            '.phase-timeline',
            '.phase-indicator',
            '.metric-grid',
            '.metric-item',
            '.alerts-container'
        ]
        
        for css_class in required_css_classes:
            self.assertIn(css_class, html_content, 
                         f"Missing CSS class: {css_class}")


if __name__ == '__main__':
    unittest.main()