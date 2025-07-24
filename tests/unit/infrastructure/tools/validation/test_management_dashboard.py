"""
Test suite for Management Dashboard using TDD approach.
"""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.infrastructure.tools.validation.dashboard.management_dashboard import (
    DashboardMetric,
    ManagementDashboard,
    MetricTrend,
)


class TestManagementDashboard:
    """Test management dashboard for engineering teams."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)

        # Create test project structure
        self.create_test_project()

        self.dashboard = ManagementDashboard(self.root_path)

    def create_test_project(self):
        """Create a test project structure."""
        # Main application files
        app_file = self.root_path / "app.py"
        app_file.write_text(
            """
'''Main application module.'''

import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class Application:
    '''Main application class.'''
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.users: List[str] = []
        self.logger = logging.getLogger(__name__)
    
    def add_user(self, username: str) -> bool:
        '''Add a new user.'''
        if not username:
            raise ValueError("Username cannot be empty")
        
        if username in self.users:
            return False
        
        self.users.append(username)
        self.logger.info(f"User {username} added")
        return True
    
    def get_users(self) -> List[str]:
        '''Get all users.'''
        return self.users.copy()
    
    def remove_user(self, username: str) -> bool:
        '''Remove a user.'''
        if username in self.users:
            self.users.remove(username)
            self.logger.info(f"User {username} removed")
            return True
        return False


def process_data(data: List[Dict[str, str]]) -> Dict[str, int]:
    '''Process user data.'''
    if not data:
        return {}
    
    result = {}
    for item in data:
        category = item.get("category", "unknown")
        if category in result:
            result[category] += 1
        else:
            result[category] = 1
    
    return result


def validate_config(config: Dict[str, str]) -> bool:
    '''Validate configuration.'''
    required_keys = ["database_url", "api_key", "environment"]
    
    for key in required_keys:
        if key not in config:
            return False
        
        if not config[key]:
            return False
    
    return True
"""
        )

        # Test files
        test_file = self.root_path / "test_app.py"
        test_file.write_text(
            """
'''Tests for application module.'''

import pytest
from app import Application, process_data, validate_config


class TestApplication:
    '''Test application class.'''
    
    def setup_method(self):
        self.app = Application({"env": "test"})
    
    def test_add_user_success(self):
        '''Test successful user addition.'''
        result = self.app.add_user("testuser")
        assert result is True
        assert "testuser" in self.app.get_users()
    
    def test_add_user_empty_username(self):
        '''Test adding user with empty username.'''
        with pytest.raises(ValueError):
            self.app.add_user("")
    
    def test_add_user_duplicate(self):
        '''Test adding duplicate user.'''
        self.app.add_user("testuser")
        result = self.app.add_user("testuser")
        assert result is False
    
    def test_remove_user_success(self):
        '''Test successful user removal.'''
        self.app.add_user("testuser")
        result = self.app.remove_user("testuser")
        assert result is True
        assert "testuser" not in self.app.get_users()
    
    def test_remove_user_not_found(self):
        '''Test removing non-existent user.'''
        result = self.app.remove_user("nonexistent")
        assert result is False


def test_process_data():
    '''Test data processing.'''
    data = [
        {"category": "type1", "value": "a"},
        {"category": "type1", "value": "b"},
        {"category": "type2", "value": "c"}
    ]
    
    result = process_data(data)
    assert result == {"type1": 2, "type2": 1}
    
    # Test empty data
    result = process_data([])
    assert result == {}


def test_validate_config():
    '''Test configuration validation.'''
    valid_config = {
        "database_url": "postgresql://localhost/test",
        "api_key": "secret123",
        "environment": "development"
    }
    
    assert validate_config(valid_config) is True
    
    # Test missing key
    invalid_config = {"database_url": "postgresql://localhost/test"}
    assert validate_config(invalid_config) is False
    
    # Test empty value
    invalid_config = {
        "database_url": "",
        "api_key": "secret123",
        "environment": "development"
    }
    assert validate_config(invalid_config) is False
"""
        )

        # Configuration files
        requirements_file = self.root_path / "requirements.txt"
        requirements_file.write_text(
            """
pytest>=7.0.0
black>=22.0.0
ruff>=0.0.1
mypy>=1.0.0
"""
        )

    def test_initialization(self):
        """Test dashboard initialization."""
        assert self.dashboard.root_path == self.root_path
        assert self.dashboard.db_path.exists()
        assert self.dashboard.dashboard_path.exists()
        assert self.dashboard.unified_validator is not None
        assert self.dashboard.quality_gates is not None
        assert self.dashboard.vv_validator is not None
        assert self.dashboard.nfr_validator is not None

    def test_init_database(self):
        """Test database initialization."""
        # Check that tables were created
        with sqlite3.connect(self.dashboard.db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            assert "metrics_history" in tables
            assert "validation_runs" in tables
            assert "team_metrics" in tables

    def test_store_validation_metrics(self):
        """Test storing validation metrics."""
        # Mock validation report
        validation_report = {
            "summary": {
                "overall_success": True,
                "total_issues": 5,
                "critical_issues": 1,
                "warnings": 3,
                "total_duration": 120.5,
                "can_merge": True,
            },
            "phase_results": {
                "quality_gates": {"details": {"technical_debt": {"total_hours": 8.5}}}
            },
        }

        self.dashboard._store_validation_metrics(validation_report)

        # Check that data was stored
        with sqlite3.connect(self.dashboard.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM validation_runs")
            assert cursor.fetchone()[0] == 1

            cursor = conn.execute("SELECT COUNT(*) FROM metrics_history")
            assert cursor.fetchone()[0] > 0

    def test_generate_executive_summary(self):
        """Test executive summary generation."""
        validation_report = {
            "summary": {
                "overall_success": True,
                "total_issues": 5,
                "critical_issues": 1,
                "warnings": 8,
                "phases_completed": 6,
                "total_duration": 180.0,
                "can_merge": True,
            }
        }

        summary = self.dashboard._generate_executive_summary(validation_report)

        assert "overall_health_score" in summary
        assert "status" in summary
        assert "status_color" in summary
        assert "can_deploy" in summary
        assert "total_issues" in summary
        assert "critical_issues" in summary
        assert "recommendation" in summary

        # Health score should be calculated correctly
        assert 0 <= summary["overall_health_score"] <= 100

        # Status should be appropriate
        assert summary["status"] in ["Excellent", "Good", "Needs Attention", "Critical"]
        assert summary["status_color"] in ["green", "yellow", "orange", "red"]

    def test_get_executive_recommendation(self):
        """Test executive recommendation generation."""
        summary = {"critical_issues": 0, "warnings": 5, "can_merge": True}

        # Test excellent health
        recommendation = self.dashboard._get_executive_recommendation(95, summary)
        assert "production-ready" in recommendation

        # Test good health
        recommendation = self.dashboard._get_executive_recommendation(80, summary)
        assert "Good overall quality" in recommendation

        # Test needs attention
        recommendation = self.dashboard._get_executive_recommendation(60, summary)
        assert "Quality issues detected" in recommendation

        # Test critical
        recommendation = self.dashboard._get_executive_recommendation(30, summary)
        assert "Critical issues found" in recommendation

    def test_generate_key_metrics(self):
        """Test key metrics generation."""
        validation_report = {
            "summary": {"total_issues": 10, "critical_issues": 2, "warnings": 5},
            "phase_results": {
                "quality_gates": {
                    "details": {
                        "metrics": {"coverage_percentage": 85.0},
                        "technical_debt": {"total_hours": 12.5},
                    }
                },
                "security_scan": {
                    "details": {
                        "security_vulnerabilities": {"total_vulnerabilities": 1},
                        "owasp_compliance": {"compliance_percentage": 90.0},
                    }
                },
                "nfr_validation": {
                    "details": {"maintainability_metrics": {"average_complexity": 6.0}}
                },
            },
        }

        metrics = self.dashboard._generate_key_metrics(validation_report)

        assert len(metrics) > 0

        # Check metric structure
        for metric in metrics:
            assert isinstance(metric, DashboardMetric)
            assert metric.name is not None
            assert metric.current_value is not None
            assert metric.trend in [
                MetricTrend.IMPROVING,
                MetricTrend.STABLE,
                MetricTrend.DECLINING,
            ]
            assert metric.target_value is not None
            assert metric.unit is not None
            assert metric.category is not None
            assert metric.priority in ["high", "medium", "low"]

    def test_calculate_security_score(self):
        """Test security score calculation."""
        validation_report = {
            "phase_results": {
                "security_scan": {
                    "details": {
                        "security_vulnerabilities": {"total_vulnerabilities": 2},
                        "owasp_compliance": {"compliance_percentage": 85.0},
                    }
                }
            }
        }

        score = self.dashboard._calculate_security_score(validation_report)

        assert 0 <= score <= 100
        assert score == 65.0  # 85 - (2 * 10)

        # Test with no security data
        empty_report = {"phase_results": {}}
        score = self.dashboard._calculate_security_score(empty_report)
        assert score == 50.0

    def test_calculate_maintainability_score(self):
        """Test maintainability score calculation."""
        validation_report = {
            "phase_results": {
                "nfr_validation": {
                    "details": {
                        "maintainability_metrics": {
                            "average_complexity": 8.0,
                            "duplication_percentage": 5.0,
                            "documentation_coverage": 80.0,
                        }
                    }
                }
            }
        }

        score = self.dashboard._calculate_maintainability_score(validation_report)

        assert 0 <= score <= 100
        # Score = 80 - (8 * 2) - (5 * 3) = 80 - 16 - 15 = 49
        assert score == 49.0

    def test_calculate_trend(self):
        """Test trend calculation."""
        # Test improving trend (higher is better)
        trend = self.dashboard._calculate_trend(85.0, 80.0, 90.0)
        assert trend == MetricTrend.IMPROVING

        # Test declining trend (higher is better)
        trend = self.dashboard._calculate_trend(75.0, 80.0, 90.0)
        assert trend == MetricTrend.DECLINING

        # Test stable trend
        trend = self.dashboard._calculate_trend(80.2, 80.0, 90.0)
        assert trend == MetricTrend.STABLE

        # Test improving trend (lower is better)
        trend = self.dashboard._calculate_trend(2.0, 5.0, 0.0)
        assert trend == MetricTrend.IMPROVING

        # Test declining trend (lower is better)
        trend = self.dashboard._calculate_trend(8.0, 5.0, 0.0)
        assert trend == MetricTrend.DECLINING

        # Test no previous value
        trend = self.dashboard._calculate_trend(85.0, None, 90.0)
        assert trend == MetricTrend.STABLE

    def test_generate_quality_trends(self):
        """Test quality trends generation."""
        # Add some historical data
        with sqlite3.connect(self.dashboard.db_path) as conn:
            # Add sample validation runs
            for i in range(10):
                conn.execute(
                    """
                    INSERT INTO validation_runs 
                    (total_issues, critical_issues, warnings, duration, can_merge, overall_success, report_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (5 + i, 1, 3 + i, 120.0, True, True, "{}"),
                )

        trends = self.dashboard._generate_quality_trends()

        assert "data" in trends
        assert "period" in trends
        assert "trend_direction" in trends
        assert trends["period"] == "30 days"
        assert trends["trend_direction"] in ["improving", "stable", "declining"]

    def test_generate_technical_debt_analysis(self):
        """Test technical debt analysis generation."""
        validation_report = {
            "phase_results": {
                "quality_gates": {
                    "details": {
                        "technical_debt": {
                            "total_hours": 24.5,
                            "total_days": 3.0,
                            "bugs": 5.0,
                            "vulnerabilities": 8.0,
                            "code_smells": 10.0,
                            "security_hotspots": 1.5,
                        }
                    }
                }
            }
        }

        analysis = self.dashboard._generate_technical_debt_analysis(validation_report)

        assert "total_hours" in analysis
        assert "total_days" in analysis
        assert "breakdown" in analysis
        assert "priority_actions" in analysis

        assert analysis["total_hours"] == 24.5
        assert analysis["total_days"] == 3.0

        breakdown = analysis["breakdown"]
        assert breakdown["bugs"] == 5.0
        assert breakdown["vulnerabilities"] == 8.0
        assert breakdown["code_smells"] == 10.0
        assert breakdown["security_hotspots"] == 1.5

        # Should have priority actions
        assert len(analysis["priority_actions"]) > 0

    def test_generate_compliance_overview(self):
        """Test compliance overview generation."""
        validation_report = {
            "compliance_assessment": {
                "iso_25010_compliant": True,
                "ready_for_production": True,
                "overall_compliance_percentage": 85.0,
                "principles": {
                    "Quality Engineering": {"compliance": True},
                    "Security": {"compliance": False},
                },
            }
        }

        overview = self.dashboard._generate_compliance_overview(validation_report)

        assert "iso_25010_compliant" in overview
        assert "ready_for_production" in overview
        assert "overall_compliance_percentage" in overview
        assert "principles_compliance" in overview
        assert "recommendations" in overview

        assert overview["iso_25010_compliant"] is True
        assert overview["ready_for_production"] is True
        assert overview["overall_compliance_percentage"] == 85.0
        assert len(overview["recommendations"]) > 0

    def test_generate_management_recommendations(self):
        """Test management recommendations generation."""
        validation_report = {
            "summary": {
                "critical_issues": 2,
                "can_merge": False,
                "total_duration": 350.0,  # Over 5 minutes
                "warnings": 25,
            }
        }

        recommendations = self.dashboard._generate_management_recommendations(
            validation_report
        )

        assert len(recommendations) > 0
        assert any("EXECUTIVE ACTION REQUIRED" in rec for rec in recommendations)
        assert any("DEPLOYMENT BLOCKED" in rec for rec in recommendations)
        assert any("PROCESS" in rec for rec in recommendations)
        assert any("TEAM" in rec for rec in recommendations)

    def test_generate_alerts(self):
        """Test alerts generation."""
        validation_report = {
            "summary": {"critical_issues": 3, "can_merge": False, "warnings": 20}
        }

        alerts = self.dashboard._generate_alerts(validation_report)

        assert len(alerts) > 0

        # Check alert structure
        for alert in alerts:
            assert "level" in alert
            assert "message" in alert
            assert "action" in alert
            assert "impact" in alert
            assert alert["level"] in ["critical", "high", "medium", "low"]

        # Should have critical alert for critical issues
        critical_alerts = [a for a in alerts if a["level"] == "critical"]
        assert len(critical_alerts) > 0

    def test_generate_charts_data(self):
        """Test charts data generation."""
        # Add some historical data
        with sqlite3.connect(self.dashboard.db_path) as conn:
            # Add sample validation runs
            for i in range(5):
                conn.execute(
                    """
                    INSERT INTO validation_runs 
                    (total_issues, critical_issues, warnings, duration, can_merge, overall_success, report_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (5 + i, i, 3 + i, 120.0, True, True, "{}"),
                )

        charts_data = self.dashboard._generate_charts_data()

        assert "issues_over_time" in charts_data
        assert "quality_distribution" in charts_data

        # Check quality distribution
        distribution = charts_data["quality_distribution"]
        assert "healthy" in distribution
        assert "warning" in distribution
        assert "critical" in distribution
        assert all(isinstance(v, int) for v in distribution.values())

    def test_generate_html_dashboard(self):
        """Test HTML dashboard generation."""
        # Mock dashboard data
        dashboard_data = {
            "timestamp": "2023-01-01 12:00:00",
            "executive_summary": {
                "overall_health_score": 85.0,
                "status": "Good",
                "can_deploy": True,
                "recommendation": "System ready for deployment",
            },
            "key_metrics": [
                DashboardMetric(
                    name="Test Coverage",
                    current_value=85.0,
                    previous_value=80.0,
                    trend=MetricTrend.IMPROVING,
                    target_value=90.0,
                    unit="%",
                    category="quality",
                    priority="high",
                )
            ],
            "alerts": [
                {
                    "level": "medium",
                    "message": "Test alert",
                    "action": "Review code",
                    "impact": "Minor issue",
                }
            ],
            "technical_debt": {
                "total_hours": 12.5,
                "total_days": 1.5,
                "priority_actions": ["Fix critical bugs"],
            },
            "recommendations": ["Improve test coverage"],
            "quality_trends": {"period": "30 days", "trend_direction": "improving"},
            "compliance_overview": {
                "iso_25010_compliant": True,
                "ready_for_production": True,
                "overall_compliance_percentage": 85.0,
            },
        }

        self.dashboard._generate_html_dashboard(dashboard_data)

        # Check that HTML file was created
        html_file = self.dashboard.dashboard_path / "index.html"
        assert html_file.exists()

        # Check HTML content
        html_content = html_file.read_text(encoding="utf-8")
        assert "Code Quality Management Dashboard" in html_content
        assert "Executive Summary" in html_content
        assert "Technical Debt Analysis" in html_content
        assert "Management Recommendations" in html_content
        assert "Quality Trends" in html_content
        assert "Compliance Overview" in html_content

    def test_get_dashboard_url(self):
        """Test getting dashboard URL."""
        url = self.dashboard.get_dashboard_url()

        assert url.startswith("file://")
        assert "index.html" in url
        assert str(self.dashboard.dashboard_path) in url

    def test_generate_metric_cards_html(self):
        """Test metric cards HTML generation."""
        metrics = [
            DashboardMetric(
                name="Test Coverage",
                current_value=85.0,
                previous_value=80.0,
                trend=MetricTrend.IMPROVING,
                target_value=90.0,
                unit="%",
                category="quality",
                priority="high",
            ),
            DashboardMetric(
                name="Critical Issues",
                current_value=2.0,
                previous_value=5.0,
                trend=MetricTrend.DECLINING,
                target_value=0.0,
                unit="count",
                category="issues",
                priority="high",
            ),
        ]

        html = self.dashboard._generate_metric_cards_html(metrics)

        assert "Test Coverage" in html
        assert "Critical Issues" in html
        assert "85%" in html  # Updated: whole number percentages show without decimal
        assert "2.0 count" in html
        assert "trend-improving" in html
        assert "trend-declining" in html
        assert "📈" in html
        assert "📉" in html

    def test_generate_alerts_html(self):
        """Test alerts HTML generation."""
        alerts = [
            {
                "level": "critical",
                "message": "Critical issue found",
                "action": "Fix immediately",
                "impact": "System down",
            },
            {
                "level": "medium",
                "message": "Warning detected",
                "action": "Review code",
                "impact": "Minor issue",
            },
        ]

        html = self.dashboard._generate_alerts_html(alerts)

        assert "Critical issue found" in html
        assert "Warning detected" in html
        assert "alert-critical" in html
        assert "alert-medium" in html
        assert "Fix immediately" in html
        assert "Review code" in html

        # Test no alerts
        html = self.dashboard._generate_alerts_html([])
        assert "No alerts - all systems healthy" in html

    def test_generate_list_html(self):
        """Test list HTML generation."""
        items = ["Item 1", "Item 2", "Item 3"]

        html = self.dashboard._generate_list_html(items)

        assert "<li>Item 1</li>" in html
        assert "<li>Item 2</li>" in html
        assert "<li>Item 3</li>" in html


class TestManagementDashboardIntegration:
    """Integration tests for management dashboard."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)

        # Create comprehensive test project
        self.create_comprehensive_test_project()

        self.dashboard = ManagementDashboard(self.root_path)

    def create_comprehensive_test_project(self):
        """Create a comprehensive test project."""
        # Create multiple modules with different characteristics

        # High-quality module
        quality_module = self.root_path / "quality_module.py"
        quality_module.write_text(
            """
'''High-quality module with comprehensive documentation and testing.'''

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    '''A well-designed data processor with proper error handling.'''
    
    def __init__(self, config: Dict[str, str]):
        '''Initialize processor with configuration.
        
        Args:
            config: Configuration dictionary with processor settings.
            
        Raises:
            ValueError: If configuration is invalid.
        '''
        self._validate_config(config)
        self.config = config
        self.processed_count = 0
        self.error_count = 0
    
    def _validate_config(self, config: Dict[str, str]) -> None:
        '''Validate configuration parameters.
        
        Args:
            config: Configuration to validate.
            
        Raises:
            ValueError: If configuration is invalid.
        '''
        required_keys = ['input_format', 'output_format', 'batch_size']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")
    
    def process_batch(self, data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        '''Process a batch of data items.
        
        Args:
            data: List of data items to process.
            
        Returns:
            List of processed data items.
            
        Raises:
            ValueError: If data format is invalid.
        '''
        if not data:
            logger.warning("Empty data batch received")
            return []
        
        try:
            result = []
            for item in data:
                processed_item = self._process_item(item)
                if processed_item:
                    result.append(processed_item)
                    self.processed_count += 1
            
            logger.info(f"Processed {len(result)} items successfully")
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error processing batch: {e}")
            raise
    
    def _process_item(self, item: Dict[str, str]) -> Optional[Dict[str, str]]:
        '''Process a single data item.
        
        Args:
            item: Data item to process.
            
        Returns:
            Processed item or None if processing failed.
        '''
        if not isinstance(item, dict):
            return None
        
        # Simulate processing
        processed = {
            'id': item.get('id', ''),
            'processed_data': item.get('data', '').upper(),
            'timestamp': '2023-01-01T12:00:00Z'
        }
        
        return processed
    
    def get_stats(self) -> Dict[str, int]:
        '''Get processing statistics.
        
        Returns:
            Dictionary with processing statistics.
        '''
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'success_rate': self.processed_count / max(self.processed_count + self.error_count, 1) * 100
        }
"""
        )

        # Module with some quality issues
        issues_module = self.root_path / "issues_module.py"
        issues_module.write_text(
            """
# Module with various quality issues for testing

def process_data(data):
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                if item < 100:
                    result.append(item * 2)
                else:
                    result.append(item)
            else:
                result.append(item + 1)
        else:
            result.append(0)
    return result

def another_function(x, y, z, a, b, c):
    if x > 0:
        if y > 0:
            if z > 0:
                if a > 0:
                    if b > 0:
                        if c > 0:
                            return x + y + z + a + b + c
                        else:
                            return x + y + z + a + b
                    else:
                        return x + y + z + a
                else:
                    return x + y + z
            else:
                return x + y
        else:
            return x
    else:
        return 0

def duplicate_logic():
    result = []
    for i in range(10):
        result.append(i * 2)
    return result

def another_duplicate_logic():
    result = []
    for i in range(10):
        result.append(i * 2)
    return result

def insecure_function(user_input):
    # Security issue - eval usage
    return eval(user_input)

def hardcoded_secret():
    api_key = "secret_key_123"  # Hardcoded secret
    return api_key
"""
        )

        # Test files
        test_quality = self.root_path / "test_quality_module.py"
        test_quality.write_text(
            """
'''Comprehensive tests for quality module.'''

import pytest
from quality_module import DataProcessor


class TestDataProcessor:
    '''Test data processor class.'''
    
    def setup_method(self):
        '''Set up test fixtures.'''
        self.config = {
            'input_format': 'json',
            'output_format': 'json',
            'batch_size': '100'
        }
        self.processor = DataProcessor(self.config)
    
    def test_initialization_valid_config(self):
        '''Test initialization with valid configuration.'''
        assert self.processor.config == self.config
        assert self.processor.processed_count == 0
        assert self.processor.error_count == 0
    
    def test_initialization_invalid_config(self):
        '''Test initialization with invalid configuration.'''
        invalid_config = {'input_format': 'json'}
        with pytest.raises(ValueError):
            DataProcessor(invalid_config)
    
    def test_process_batch_valid_data(self):
        '''Test processing valid data batch.'''
        data = [
            {'id': '1', 'data': 'hello'},
            {'id': '2', 'data': 'world'}
        ]
        
        result = self.processor.process_batch(data)
        
        assert len(result) == 2
        assert result[0]['processed_data'] == 'HELLO'
        assert result[1]['processed_data'] == 'WORLD'
        assert self.processor.processed_count == 2
    
    def test_process_batch_empty_data(self):
        '''Test processing empty data batch.'''
        result = self.processor.process_batch([])
        
        assert result == []
        assert self.processor.processed_count == 0
    
    def test_get_stats(self):
        '''Test getting processing statistics.'''
        data = [{'id': '1', 'data': 'test'}]
        self.processor.process_batch(data)
        
        stats = self.processor.get_stats()
        
        assert stats['processed_count'] == 1
        assert stats['error_count'] == 0
        assert stats['success_rate'] == 100.0
"""
        )

        test_issues = self.root_path / "test_issues_module.py"
        test_issues.write_text(
            """
'''Basic tests for issues module.'''

from issues_module import process_data, another_function


def test_process_data():
    '''Test data processing.'''
    data = [1, 2, 3, 4, 5]
    result = process_data(data)
    assert len(result) == 5

def test_another_function():
    '''Test another function.'''
    result = another_function(1, 2, 3, 4, 5, 6)
    assert result == 21
"""
        )

    def test_comprehensive_dashboard_generation(self):
        """Test comprehensive dashboard generation."""
        with patch.object(
            self.dashboard.unified_validator, "run_validation"
        ) as mock_validate:
            # Mock comprehensive validation results
            mock_validate.return_value = {
                "summary": {
                    "overall_success": True,
                    "total_issues": 15,
                    "critical_issues": 2,
                    "warnings": 8,
                    "phases_completed": 7,
                    "total_duration": 145.5,
                    "can_merge": False,
                },
                "phase_results": {
                    "quality_gates": {
                        "details": {
                            "metrics": {
                                "coverage_percentage": 78.5,
                                "avg_cyclomatic_complexity": 6.2,
                                "duplication_percentage": 8.5,
                            },
                            "technical_debt": {
                                "total_hours": 18.5,
                                "total_days": 2.3,
                                "bugs": 6.0,
                                "vulnerabilities": 4.0,
                                "code_smells": 12.0,
                                "security_hotspots": 2.0,
                            },
                        }
                    },
                    "security_scan": {
                        "details": {
                            "security_vulnerabilities": {"total_vulnerabilities": 4},
                            "owasp_compliance": {"compliance_percentage": 75.0},
                        }
                    },
                    "nfr_validation": {
                        "details": {
                            "maintainability_metrics": {
                                "average_complexity": 7.5,
                                "duplication_percentage": 8.5,
                                "documentation_coverage": 65.0,
                            }
                        }
                    },
                },
                "compliance_assessment": {
                    "iso_25010_compliant": False,
                    "ready_for_production": False,
                    "overall_compliance_percentage": 72.5,
                    "principles": {
                        "Quality Engineering": {"compliance": True},
                        "Security": {"compliance": False},
                        "Maintainability": {"compliance": True},
                    },
                },
            }

            # Generate dashboard
            dashboard_data = self.dashboard.generate_management_dashboard()

            # Should have all required sections
            assert "timestamp" in dashboard_data
            assert "executive_summary" in dashboard_data
            assert "key_metrics" in dashboard_data
            assert "quality_trends" in dashboard_data
            assert "technical_debt" in dashboard_data
            assert "compliance_overview" in dashboard_data
            assert "recommendations" in dashboard_data
            assert "alerts" in dashboard_data
            assert "charts_data" in dashboard_data

            # Check executive summary
            exec_summary = dashboard_data["executive_summary"]
            assert exec_summary["overall_health_score"] < 100  # Should reflect issues
            assert exec_summary["status"] in ["Good", "Needs Attention", "Critical"]
            assert exec_summary["can_deploy"] is False

            # Check key metrics
            key_metrics = dashboard_data["key_metrics"]
            assert len(key_metrics) > 0
            assert all(isinstance(metric, DashboardMetric) for metric in key_metrics)

            # Check technical debt
            tech_debt = dashboard_data["technical_debt"]
            assert tech_debt["total_hours"] == 18.5
            assert tech_debt["total_days"] == 2.3
            assert len(tech_debt["priority_actions"]) > 0

            # Check compliance
            compliance = dashboard_data["compliance_overview"]
            assert compliance["iso_25010_compliant"] is False
            assert compliance["ready_for_production"] is False
            assert compliance["overall_compliance_percentage"] == 72.5

            # Check recommendations
            recommendations = dashboard_data["recommendations"]
            assert len(recommendations) > 0
            assert any("EXECUTIVE ACTION" in rec for rec in recommendations)

            # Check alerts
            alerts = dashboard_data["alerts"]
            assert len(alerts) > 0
            assert any(alert["level"] == "critical" for alert in alerts)

    def test_dashboard_with_excellent_quality(self):
        """Test dashboard with excellent code quality."""
        with patch.object(
            self.dashboard.unified_validator, "run_validation"
        ) as mock_validate:
            # Mock excellent validation results
            mock_validate.return_value = {
                "summary": {
                    "overall_success": True,
                    "total_issues": 0,
                    "critical_issues": 0,
                    "warnings": 0,
                    "phases_completed": 7,
                    "total_duration": 95.0,
                    "can_merge": True,
                },
                "phase_results": {
                    "quality_gates": {
                        "details": {
                            "metrics": {
                                "coverage_percentage": 95.0,
                                "avg_cyclomatic_complexity": 3.2,
                                "duplication_percentage": 1.5,
                            },
                            "technical_debt": {
                                "total_hours": 2.0,
                                "total_days": 0.25,
                                "bugs": 0.0,
                                "vulnerabilities": 0.0,
                                "code_smells": 2.0,
                                "security_hotspots": 0.0,
                            },
                        }
                    },
                    "security_scan": {
                        "details": {
                            "security_vulnerabilities": {"total_vulnerabilities": 0},
                            "owasp_compliance": {"compliance_percentage": 100.0},
                        }
                    },
                    "nfr_validation": {
                        "details": {
                            "maintainability_metrics": {
                                "average_complexity": 3.2,
                                "duplication_percentage": 1.5,
                                "documentation_coverage": 95.0,
                            }
                        }
                    },
                },
                "compliance_assessment": {
                    "iso_25010_compliant": True,
                    "ready_for_production": True,
                    "overall_compliance_percentage": 95.0,
                    "principles": {
                        "Quality Engineering": {"compliance": True},
                        "Security": {"compliance": True},
                        "Maintainability": {"compliance": True},
                    },
                },
            }

            # Generate dashboard
            dashboard_data = self.dashboard.generate_management_dashboard()

            # Should reflect excellent quality
            exec_summary = dashboard_data["executive_summary"]
            assert exec_summary["overall_health_score"] >= 90
            assert exec_summary["status"] == "Excellent"
            assert exec_summary["can_deploy"] is True

            # Should have minimal technical debt
            tech_debt = dashboard_data["technical_debt"]
            assert tech_debt["total_hours"] == 2.0

            # Should be compliant
            compliance = dashboard_data["compliance_overview"]
            assert compliance["iso_25010_compliant"] is True
            assert compliance["ready_for_production"] is True

            # Should have positive recommendations
            recommendations = dashboard_data["recommendations"]
            assert any("EXCELLENT" in rec for rec in recommendations)

            # Should have minimal alerts
            alerts = dashboard_data["alerts"]
            assert len(alerts) == 0 or all(
                alert["level"] != "critical" for alert in alerts
            )

    def test_html_dashboard_generation(self):
        """Test HTML dashboard generation with real data."""
        with patch.object(
            self.dashboard.unified_validator, "run_validation"
        ) as mock_validate:
            mock_validate.return_value = {
                "summary": {
                    "overall_success": True,
                    "total_issues": 5,
                    "critical_issues": 1,
                    "warnings": 3,
                    "phases_completed": 7,
                    "total_duration": 120.0,
                    "can_merge": True,
                },
                "phase_results": {
                    "quality_gates": {
                        "details": {
                            "metrics": {"coverage_percentage": 85.0},
                            "technical_debt": {"total_hours": 8.0, "total_days": 1.0},
                        }
                    }
                },
                "compliance_assessment": {
                    "iso_25010_compliant": True,
                    "ready_for_production": True,
                    "overall_compliance_percentage": 85.0,
                },
            }

            # Generate dashboard
            dashboard_data = self.dashboard.generate_management_dashboard()
            
            # Verify dashboard data structure
            assert isinstance(dashboard_data, dict), "Dashboard data should be a dictionary"
            assert len(dashboard_data) > 0, "Dashboard data should not be empty"

            # Check that HTML file was created
            html_file = self.dashboard.dashboard_path / "index.html"
            assert html_file.exists()

            # Read and verify HTML content
            html_content = html_file.read_text(encoding="utf-8")

            # Should contain all major sections
            assert "Code Quality Management Dashboard" in html_content
            assert "Executive Summary" in html_content
            assert "Technical Debt Analysis" in html_content
            assert "Management Recommendations" in html_content
            assert "Quality Trends" in html_content
            assert "Compliance Overview" in html_content

            # Should contain actual data
            assert "85%" in html_content  # Health score
            assert "8.0 hours" in html_content  # Technical debt
            assert "85.0%" in html_content  # Compliance

            # Should have proper styling
            assert "font-family: Arial" in html_content
            assert "background-color: #f5f5f5" in html_content
            assert 'class="dashboard"' in html_content

    def test_dashboard_persistence(self):
        """Test dashboard data persistence in database."""
        with patch.object(
            self.dashboard.unified_validator, "run_validation"
        ) as mock_validate:
            mock_validate.return_value = {
                "summary": {
                    "overall_success": True,
                    "total_issues": 3,
                    "critical_issues": 1,
                    "warnings": 2,
                    "phases_completed": 7,
                    "total_duration": 100.0,
                    "can_merge": True,
                },
                "phase_results": {
                    "quality_gates": {
                        "details": {"technical_debt": {"total_hours": 5.0}}
                    }
                },
            }

            # Generate dashboard multiple times
            self.dashboard.generate_management_dashboard()
            self.dashboard.generate_management_dashboard()

            # Check that data was stored in database
            with sqlite3.connect(self.dashboard.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM validation_runs")
                validation_runs = cursor.fetchone()[0]
                assert validation_runs == 2

                cursor = conn.execute("SELECT COUNT(*) FROM metrics_history")
                metrics_count = cursor.fetchone()[0]
                assert metrics_count > 0

                # Check specific data
                cursor = conn.execute(
                    "SELECT total_issues, critical_issues FROM validation_runs ORDER BY timestamp DESC LIMIT 1"
                )
                row = cursor.fetchone()
                assert row[0] == 3  # total_issues
                assert row[1] == 1  # critical_issues


if __name__ == "__main__":
    pytest.main([__file__])
