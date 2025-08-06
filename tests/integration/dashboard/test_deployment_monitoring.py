#!/usr/bin/env python3
"""
Comprehensive Tests for Deployment Monitoring Integration

Tests for the AI assistant deployment monitoring functionality integrated
into the existing dashboard system, including:
- Deployment status tracking
- Team adoption metrics
- Phase timeline management
- Productivity metrics calculation
- Alert system functionality
"""

import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.interfaces.dashboard.api.unified_api_server import UnifiedDashboardAPI
from src.interfaces.dashboard.config import DashboardConfig


class TestDeploymentMonitoringIntegration(unittest.TestCase):
    """Test deployment monitoring integration with existing dashboard system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Create test deployment configuration
        self.deployment_config = {
            "team_members": [
                {
                    "name": "Senior Developer",
                    "role": "senior",
                    "email": "senior@company.com",
                    "specialization": "architecture",
                    "experience_years": 8
                },
                {
                    "name": "Mid-Level Developer",
                    "role": "mid", 
                    "email": "mid@company.com",
                    "specialization": "fullstack",
                    "experience_years": 4
                },
                {
                    "name": "Junior Developer",
                    "role": "junior",
                    "email": "junior@company.com",
                    "specialization": "frontend", 
                    "experience_years": 1
                }
            ],
            "deployment_phases": [
                {
                    "phase": 1,
                    "name": "Foundation Setup",
                    "duration_days": 7,
                    "focus": "CLI Installation & Basic Setup",
                    "key_activities": ["Installation", "Authentication", "Basic commands"]
                },
                {
                    "phase": 2,
                    "name": "Workflow Integration", 
                    "duration_days": 7,
                    "focus": "Custom Commands & Daily Usage",
                    "key_activities": ["Daily workflow", "Custom commands", "Integration"]
                },
                {
                    "phase": 3,
                    "name": "Advanced Features",
                    "duration_days": 7,
                    "focus": "MCP Integration & Advanced Usage", 
                    "key_activities": ["Advanced features", "MCP servers", "CI/CD"]
                },
                {
                    "phase": 4,
                    "name": "Optimization & Mastery",
                    "duration_days": 7,
                    "focus": "Best Practices & Team Knowledge",
                    "key_activities": ["Optimization", "Best practices", "Knowledge sharing"]
                }
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
    
    def test_deployment_monitoring_data_structure(self):
        """Test that deployment monitoring data has correct structure."""
        # Mock the config path resolution
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            deployment_data = api._get_deployment_monitoring_data()
            
            # Verify main structure
            self.assertIn("deployment_status", deployment_data)
            self.assertIn("productivity_metrics", deployment_data)
            self.assertIn("phase_timeline", deployment_data)
            self.assertIn("team_progress", deployment_data)
            self.assertIn("alerts", deployment_data)
            self.assertIn("success_criteria", deployment_data)
    
    def test_deployment_status_calculation(self):
        """Test deployment status metrics calculation."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            # Mock to return path where config directory contains our test config
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            deployment_data = api._get_deployment_monitoring_data()
            
            status = deployment_data["deployment_status"]
            
            # Verify status fields
            self.assertIn("current_phase", status)
            self.assertIn("overall_progress", status)
            self.assertIn("team_adoption_rate", status)
            self.assertIn("active_team_members", status)
            self.assertIn("total_team_members", status)
            
            # Verify data types and ranges
            self.assertIsInstance(status["current_phase"], int)
            self.assertGreaterEqual(status["overall_progress"], 0)
            self.assertLessEqual(status["overall_progress"], 100)
            self.assertEqual(status["total_team_members"], 3)  # Based on test config
    
    def test_productivity_metrics_calculation(self):
        """Test productivity metrics calculation."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            deployment_data = api._get_deployment_monitoring_data()
            
            metrics = deployment_data["productivity_metrics"]
            
            # Verify metrics fields
            required_fields = [
                "average_daily_usage", "productivity_acceleration",
                "automation_efficiency", "code_quality_improvement"
            ]
            
            for field in required_fields:
                self.assertIn(field, metrics)
                self.assertIsInstance(metrics[field], (int, float))
                self.assertGreaterEqual(metrics[field], 0)
    
    def test_phase_timeline_structure(self):
        """Test phase timeline data structure."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            deployment_data = api._get_deployment_monitoring_data()
            
            timeline = deployment_data["phase_timeline"]
            
            # Verify we have 4 phases
            self.assertEqual(len(timeline), 4)
            
            # Verify each phase has required fields
            for phase in timeline:
                required_fields = ["phase", "name", "duration_days", "focus", "status", "progress"]
                for field in required_fields:
                    self.assertIn(field, phase)
                
                # Verify phase numbering
                self.assertIn(phase["phase"], [1, 2, 3, 4])
                
                # Verify status values
                self.assertIn(phase["status"], ["completed", "in_progress", "pending"])
                
                # Verify progress range
                self.assertGreaterEqual(phase["progress"], 0)
                self.assertLessEqual(phase["progress"], 100)
    
    def test_team_progress_tracking(self):
        """Test team member progress tracking."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            deployment_data = api._get_deployment_monitoring_data()
            
            team_progress = deployment_data["team_progress"]
            
            # Verify we have progress for all team members
            self.assertEqual(len(team_progress), 3)
            
            # Verify each member has required fields
            for member in team_progress:
                required_fields = [
                    "name", "role", "adoption_score", "daily_usage_hours",
                    "productivity_improvement", "status"
                ]
                for field in required_fields:
                    self.assertIn(field, member)
                
                # Verify role mapping
                self.assertIn(member["role"], ["senior", "mid", "junior"])
                
                # Verify adoption score range
                self.assertGreaterEqual(member["adoption_score"], 0)
                self.assertLessEqual(member["adoption_score"], 100)
                
                # Verify status values
                self.assertIn(member["status"], ["active", "needs_support"])
    
    def test_alert_system_functionality(self):
        """Test deployment monitoring alert system."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            deployment_data = api._get_deployment_monitoring_data()
            
            alerts = deployment_data["alerts"]
            
            # Alerts should be a list
            self.assertIsInstance(alerts, list)
            
            # If there are alerts, verify structure
            for alert in alerts:
                required_fields = ["type", "message", "severity"]
                for field in required_fields:
                    self.assertIn(field, alert)
                
                # Verify alert types and severities
                self.assertIn(alert["type"], ["info", "warning", "error"])
                self.assertIn(alert["severity"], ["low", "medium", "high"])
    
    def test_success_criteria_mapping(self):
        """Test success criteria mapping from configuration."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            deployment_data = api._get_deployment_monitoring_data()
            
            criteria = deployment_data["success_criteria"]
            
            # Verify criteria are mapped correctly
            expected_criteria = [
                "installation_completion", "daily_usage_target",
                "productivity_target", "satisfaction_target"
            ]
            
            for criterion in expected_criteria:
                self.assertIn(criterion, criteria)
                self.assertIsInstance(criteria[criterion], (int, float))
    
    def test_error_handling_missing_config(self):
        """Test error handling when deployment config is missing."""
        # Use a directory without config file
        empty_temp_dir = tempfile.mkdtemp()
        
        try:
            with patch.object(self.config, 'get_absolute_path') as mock_path:
                mock_path.return_value = Path(empty_temp_dir) / "outputs"
                
                api = UnifiedDashboardAPI(self.config)
                deployment_data = api._get_deployment_monitoring_data()
                
                # Verify fallback behavior
                self.assertIn("deployment_status", deployment_data)
                self.assertEqual(deployment_data["deployment_status"]["total_team_members"], 0)
                self.assertEqual(len(deployment_data["phase_timeline"]), 0)
                self.assertEqual(len(deployment_data["team_progress"]), 0)
                
        finally:
            import shutil
            shutil.rmtree(empty_temp_dir)
    
    def test_error_handling_corrupted_config(self):
        """Test error handling when deployment config is corrupted."""
        # Create corrupted config file
        corrupted_config_dir = Path(self.temp_dir) / "corrupted_config"
        corrupted_config_dir.mkdir(exist_ok=True)
        
        config_file = corrupted_config_dir / "team_deployment.json"
        with open(config_file, 'w') as f:
            f.write("{ invalid json content")
        
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "corrupted_config" / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            deployment_data = api._get_deployment_monitoring_data()
            
            # Should handle error gracefully and provide fallback data
            self.assertIn("deployment_status", deployment_data)
            # In case of JSON decode error, it should fall back to defaults
            self.assertIsInstance(deployment_data["deployment_status"]["total_team_members"], int)


class TestEnhancedMetricsEndpoint(unittest.TestCase):
    """Test enhanced metrics endpoint with deployment data."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = DashboardConfig()
        self.config.debug = True
        self.config.outputs_dir = str(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_metrics_endpoint_includes_deployment_data(self):
        """Test that metrics endpoint includes deployment monitoring data."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            
            with api.app.test_client() as client:
                # Mock authentication for testing
                with patch('src.infrastructure.security.auth_middleware.requires_auth', lambda f: f):
                    response = client.get('/api/metrics')
                    
                    self.assertEqual(response.status_code, 200)
                    data = response.get_json()
                    
                    # Verify response structure
                    self.assertEqual(data["status"], "success")
                    self.assertIn("data", data)
                    
                    metrics_data = data["data"]
                    
                    # Verify deployment data is included
                    self.assertIn("deployment", metrics_data)
                    self.assertIn("team", metrics_data)
                    self.assertIn("sprint", metrics_data)
                    
                    # Verify deployment data structure
                    deployment = metrics_data["deployment"]
                    self.assertIn("deployment_status", deployment)
                    self.assertIn("productivity_metrics", deployment)
    
    def test_metrics_endpoint_caching_with_deployment(self):
        """Test that metrics endpoint caching works with deployment data."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            
            with api.app.test_client() as client:
                with patch('src.infrastructure.security.auth_middleware.requires_auth', lambda f: f):
                    # First request should not be cached
                    response1 = client.get('/api/metrics')
                    data1 = response1.get_json()
                    self.assertEqual(data1["cached"], False)
                    
                    # Second request should be cached
                    response2 = client.get('/api/metrics')
                    data2 = response2.get_json()
                    self.assertEqual(data2["cached"], True)
                    
                    # Both should contain deployment data
                    self.assertIn("deployment", data1["data"])
                    self.assertIn("deployment", data2["data"])


class TestEnhancedAutomationStatus(unittest.TestCase):
    """Test enhanced automation status endpoint with deployment integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = DashboardConfig()
        self.config.debug = True
        self.config.outputs_dir = str(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_automation_status_includes_deployment(self):
        """Test automation status endpoint includes deployment automation data."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            
            with api.app.test_client() as client:
                with patch('src.infrastructure.security.auth_middleware.requires_auth', lambda f: f):
                    response = client.get('/api/automation/status')
                    
                    self.assertEqual(response.status_code, 200)
                    data = response.get_json()
                    
                    automation_data = data["data"]
                    
                    # Verify deployment automation data is included
                    self.assertIn("deployment_automation", automation_data)
                    
                    deployment_automation = automation_data["deployment_automation"]
                    required_fields = [
                        "phase_progress", "team_adoption", "active_users",
                        "automation_efficiency", "alerts_count"
                    ]
                    
                    for field in required_fields:
                        self.assertIn(field, deployment_automation)
                        self.assertIsInstance(deployment_automation[field], (int, float))
    
    def test_automation_status_source_attribution(self):
        """Test automation status correctly attributes data source."""
        with patch.object(self.config, 'get_absolute_path') as mock_path:
            mock_path.return_value = Path(self.temp_dir) / "outputs"
            
            api = UnifiedDashboardAPI(self.config)
            
            with api.app.test_client() as client:
                with patch('src.infrastructure.security.auth_middleware.requires_auth', lambda f: f):
                    response = client.get('/api/automation/status')
                    data = response.get_json()
                    
                    automation_data = data["data"]
                    
                    # Verify source is updated to indicate enhanced data
                    self.assertEqual(automation_data["source"], "enhanced_with_deployment_data")


if __name__ == '__main__':
    unittest.main()