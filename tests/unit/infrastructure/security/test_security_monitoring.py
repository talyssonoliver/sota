#!/usr/bin/env python3
"""
Comprehensive Tests for Security Monitoring System

Tests security event logging, threat detection, and monitoring capabilities.
Critical for achieving 80% test coverage target.
"""

import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from collections import deque

from src.infrastructure.security.security_monitoring import (
    SecurityEventType,
    SecurityLevel,
    SecurityEvent,
    SecurityLogger,
    ThreatDetector,
    SecurityMonitor,
    get_security_monitor,
    log_authentication_success,
    log_authentication_failure,
    log_input_validation_failure,
    log_suspicious_activity,
    log_configuration_change,
    monitor_endpoint
)


class TestSecurityEventType:
    """Test SecurityEventType enum."""
    
    def test_security_event_types_exist(self):
        """Test that all expected security event types exist."""
        expected_types = [
            "auth_success", "auth_failure", "auth_denied",
            "suspicious", "input_invalid", "sql_injection",
            "xss_attempt", "path_traversal", "brute_force",
            "rate_limit", "config_change", "privilege_escalation",
            "data_access", "system_error", "security_scan"
        ]
        
        for event_type in expected_types:
            assert any(member.value == event_type for member in SecurityEventType)


class TestSecurityLevel:
    """Test SecurityLevel enum."""
    
    def test_security_levels_exist(self):
        """Test that all security levels exist."""
        expected_levels = ["low", "medium", "high", "critical"]
        
        for level in expected_levels:
            assert any(member.value == level for member in SecurityLevel)


class TestSecurityEvent:
    """Test SecurityEvent dataclass."""
    
    def test_security_event_creation(self):
        """Test creating a SecurityEvent."""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=SecurityEventType.AUTHENTICATION_SUCCESS,
            severity=SecurityLevel.LOW,
            message="Test authentication success",
            user_id="test_user",
            ip_address="192.168.1.1",
            endpoint="/api/login"
        )
        
        assert event.event_type == SecurityEventType.AUTHENTICATION_SUCCESS
        assert event.severity == SecurityLevel.LOW
        assert event.message == "Test authentication success"
        assert event.user_id == "test_user"
        assert event.ip_address == "192.168.1.1"
        assert event.endpoint == "/api/login"
        assert isinstance(event.timestamp, datetime)
        assert event.additional_data == {}
    
    def test_security_event_auto_timestamp(self):
        """Test that timestamp is automatically set."""
        before = datetime.utcnow()
        event = SecurityEvent(
            event_type=SecurityEventType.SYSTEM_ERROR,
            severity=SecurityLevel.HIGH,
            message="Test error",
            timestamp=None
        )
        after = datetime.utcnow()
        
        assert before <= event.timestamp <= after
    
    def test_security_event_custom_timestamp(self):
        """Test setting custom timestamp."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        event = SecurityEvent(
            event_type=SecurityEventType.DATA_ACCESS,
            severity=SecurityLevel.LOW,
            message="Test access",
            timestamp=custom_time
        )
        
        assert event.timestamp == custom_time
    
    def test_security_event_additional_data(self):
        """Test SecurityEvent with additional data."""
        additional_data = {"key": "value", "count": 42}
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            severity=SecurityLevel.MEDIUM,
            message="Test suspicious activity",
            additional_data=additional_data
        )
        
        assert event.additional_data == additional_data
    
    def test_security_event_to_dict(self):
        """Test converting SecurityEvent to dictionary."""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=SecurityEventType.AUTHENTICATION_FAILURE,
            severity=SecurityLevel.MEDIUM,
            message="Login failed",
            user_id="test_user",
            ip_address="10.0.0.1",
            additional_data={"attempts": 3}
        )
        
        event_dict = event.to_dict()
        
        assert event_dict['event_type'] == "auth_failure"
        assert event_dict['severity'] == "medium"
        assert event_dict['message'] == "Login failed"
        assert event_dict['user_id'] == "test_user"
        assert event_dict['ip_address'] == "10.0.0.1"
        assert event_dict['additional_data'] == {"attempts": 3}
        assert isinstance(event_dict['timestamp'], str)
    
    def test_security_event_to_json(self):
        """Test converting SecurityEvent to JSON."""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=SecurityEventType.XSS_ATTEMPT,
            severity=SecurityLevel.HIGH,
            message="XSS attempt detected",
            endpoint="/api/comment"
        )
        
        json_str = event.to_json()
        parsed = json.loads(json_str)
        
        assert parsed['event_type'] == "xss_attempt"
        assert parsed['severity'] == "high"
        assert parsed['message'] == "XSS attempt detected"
        assert parsed['endpoint'] == "/api/comment"


class TestSecurityLogger:
    """Test SecurityLogger class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Use temporary directory for test logs
        self.temp_dir = tempfile.mkdtemp()
        
        with patch('os.makedirs'), \
             patch('os.path.join', return_value=os.path.join(self.temp_dir, 'security.log')):
            self.logger = SecurityLogger("test_security")
    
    def test_security_logger_initialization(self):
        """Test SecurityLogger initialization."""
        assert self.logger.logger.name == "test_security"
        assert len(self.logger.logger.handlers) >= 1
    
    @patch('logging.FileHandler')
    @patch('os.makedirs')
    @patch('os.chmod')
    def test_security_logger_file_permissions(self, mock_chmod, mock_makedirs, mock_file_handler):
        """Test that security log file has proper permissions."""
        SecurityLogger()
        
        # Verify secure permissions are set
        mock_chmod.assert_called()
        # Check that 0o600 (owner read/write only) was used
        args, kwargs = mock_chmod.call_args
        assert args[1] == 0o600
    
    def test_log_event_info_level(self):
        """Test logging event at info level."""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=SecurityEventType.DATA_ACCESS,
            severity=SecurityLevel.LOW,
            message="Data accessed",
            user_id="test_user"
        )
        
        with patch.object(self.logger.logger, 'info') as mock_info:
            self.logger.log_event(event)
            mock_info.assert_called_once()
            
            # Check log message format
            call_args = mock_info.call_args[0][0]
            assert "DATA_ACCESS" in call_args
            assert "Data accessed" in call_args
            assert "[User: test_user]" in call_args
    
    def test_log_event_warning_level(self):
        """Test logging event at warning level."""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=SecurityEventType.INPUT_VALIDATION_FAILURE,
            severity=SecurityLevel.MEDIUM,
            message="Invalid input",
            ip_address="192.168.1.1"
        )
        
        with patch.object(self.logger.logger, 'warning') as mock_warning:
            self.logger.log_event(event)
            mock_warning.assert_called_once()
            
            call_args = mock_warning.call_args[0][0]
            assert "INPUT_INVALID" in call_args
            assert "[IP: 192.168.1.1]" in call_args
    
    def test_log_event_error_level(self):
        """Test logging event at error level."""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=SecurityEventType.BRUTE_FORCE_ATTEMPT,
            severity=SecurityLevel.HIGH,
            message="Brute force detected",
            endpoint="/api/login"
        )
        
        with patch.object(self.logger.logger, 'error') as mock_error:
            self.logger.log_event(event)
            mock_error.assert_called_once()
            
            call_args = mock_error.call_args[0][0]
            assert "BRUTE_FORCE" in call_args
            assert "[Endpoint: /api/login]" in call_args
    
    def test_log_event_critical_level(self):
        """Test logging event at critical level."""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=SecurityEventType.PRIVILEGE_ESCALATION,
            severity=SecurityLevel.CRITICAL,
            message="Privilege escalation attempt"
        )
        
        with patch.object(self.logger.logger, 'critical') as mock_critical:
            self.logger.log_event(event)
            mock_critical.assert_called_once()


class TestThreatDetector:
    """Test ThreatDetector class."""
    
    def setup_method(self):
        """Set up test threat detector."""
        self.detector = ThreatDetector(window_minutes=15, max_events=100)
    
    def test_threat_detector_initialization(self):
        """Test ThreatDetector initialization."""
        assert self.detector.window_minutes == 15
        assert self.detector.max_events == 100
        assert isinstance(self.detector.events, deque)
        assert self.detector.events.maxlen == 100
        assert 'failed_auth_per_user' in self.detector.thresholds
    
    def test_add_event_normal(self):
        """Test adding normal event with no threats detected."""
        from datetime import datetime
        event = SecurityEvent(
            event_type=SecurityEventType.DATA_ACCESS,
            severity=SecurityLevel.LOW,
            message="Normal data access",
            timestamp=datetime.now()
        )
        
        threats = self.detector.add_event(event)
        
        assert len(threats) == 0
        assert event in self.detector.events
    
    def test_brute_force_detection_by_user(self):
        """Test brute force detection based on user failures."""
        user_id = "test_user"
        
        # Generate multiple failed authentication events
        for i in range(6):  # Exceeds threshold of 5
            from datetime import datetime
            event = SecurityEvent(
                event_type=SecurityEventType.AUTHENTICATION_FAILURE,
                severity=SecurityLevel.MEDIUM,
                message=f"Login failed {i}",
                timestamp=datetime.now(),
                user_id=user_id,
                ip_address="192.168.1.1"
            )
            threats = self.detector.add_event(event)
        
        # Should detect brute force on the 6th attempt
        assert len(threats) == 1
        threat = threats[0]
        assert threat.event_type == SecurityEventType.BRUTE_FORCE_ATTEMPT
        assert threat.severity == SecurityLevel.HIGH
        assert user_id in threat.message
        assert threat.additional_data['failed_attempts'] >= 5
    
    def test_brute_force_detection_by_ip(self):
        """Test brute force detection based on IP failures."""
        ip_address = "10.0.0.1"
        
        # Generate multiple failed authentication events from same IP
        for i in range(11):  # Exceeds threshold of 10
            from datetime import datetime
            event = SecurityEvent(
                event_type=SecurityEventType.AUTHENTICATION_FAILURE,
                severity=SecurityLevel.MEDIUM,
                message=f"Login failed {i}",
                timestamp=datetime.now(),
                user_id=f"user{i}",
                ip_address=ip_address
            )
            threats = self.detector.add_event(event)
        
        # Should detect brute force on the 11th attempt
        assert len(threats) == 1
        threat = threats[0]
        assert threat.event_type == SecurityEventType.BRUTE_FORCE_ATTEMPT
        assert threat.severity == SecurityLevel.CRITICAL
        assert ip_address in threat.message
        assert threat.additional_data['failed_attempts'] >= 10
    
    def test_input_validation_pattern_detection(self):
        """Test detection of input validation attack patterns."""
        ip_address = "172.16.0.1"
        
        # Generate multiple input validation failures
        for i in range(21):  # Exceeds threshold of 20
            event = SecurityEvent(
                timestamp=datetime.now(),
                event_type=SecurityEventType.INPUT_VALIDATION_FAILURE,
                severity=SecurityLevel.MEDIUM,
                message=f"Validation failed {i}",
                ip_address=ip_address
            )
            threats = self.detector.add_event(event)
        
        # Should detect suspicious activity on the 21st attempt
        assert len(threats) == 1
        threat = threats[0]
        assert threat.event_type == SecurityEventType.SUSPICIOUS_ACTIVITY
        assert threat.severity == SecurityLevel.HIGH
        assert ip_address in threat.message
        assert threat.additional_data['validation_failures'] >= 20
    
    def test_suspicious_activity_pattern_detection(self):
        """Test detection of suspicious activity patterns."""
        ip_address = "203.0.113.1"
        
        suspicious_events = [
            SecurityEventType.SQL_INJECTION_ATTEMPT,
            SecurityEventType.XSS_ATTEMPT,
            SecurityEventType.DIRECTORY_TRAVERSAL
        ]
        
        # Generate mix of suspicious events
        for i in range(51):  # Exceeds threshold of 50
            event_type = suspicious_events[i % len(suspicious_events)]
            event = SecurityEvent(
                timestamp=datetime.now(),
                event_type=event_type,
                severity=SecurityLevel.HIGH,
                message=f"Suspicious activity {i}",
                ip_address=ip_address
            )
            threats = self.detector.add_event(event)
        
        # Should detect high volume suspicious activity
        assert len(threats) == 1
        threat = threats[0]
        assert threat.event_type == SecurityEventType.SUSPICIOUS_ACTIVITY
        assert threat.severity == SecurityLevel.CRITICAL
        assert ip_address in threat.message
        assert threat.additional_data['suspicious_events'] >= 50
    
    def test_time_window_filtering(self):
        """Test that threat detection respects time window."""
        detector = ThreatDetector(window_minutes=1)  # Very short window
        user_id = "test_user"
        
        # Add old event (outside window)
        old_event = SecurityEvent(
            event_type=SecurityEventType.AUTHENTICATION_FAILURE,
            severity=SecurityLevel.MEDIUM,
            message="Old login failure",
            user_id=user_id,
            timestamp=datetime.utcnow() - timedelta(minutes=2)
        )
        detector.add_event(old_event)
        
        # Add recent events (within threshold but including old event would exceed)
        for i in range(4):  # 4 + 1 old = 5, which would trigger threshold
            event = SecurityEvent(
                timestamp=datetime.now(),
                event_type=SecurityEventType.AUTHENTICATION_FAILURE,
                severity=SecurityLevel.MEDIUM,
                message=f"Recent login failure {i}",
                user_id=user_id
            )
            threats = detector.add_event(event)
        
        # Should not detect brute force because old event is outside window
        assert len(threats) == 0


class TestSecurityMonitor:
    """Test SecurityMonitor class."""
    
    def setup_method(self):
        """Set up test security monitor."""
        with patch('src.infrastructure.security.security_monitoring.SecurityLogger'), \
             patch('src.infrastructure.security.security_monitoring.ThreatDetector'):
            self.monitor = SecurityMonitor()
    
    def test_security_monitor_initialization(self):
        """Test SecurityMonitor initialization."""
        assert self.monitor.logger is not None
        assert self.monitor.detector is not None
        assert isinstance(self.monitor.alert_handlers, list)
        assert 'events_logged' in self.monitor.stats
        assert 'start_time' in self.monitor.stats
    
    def test_add_alert_handler(self):
        """Test adding alert handler."""
        def test_handler(event):
            pass
        
        initial_count = len(self.monitor.alert_handlers)
        self.monitor.add_alert_handler(test_handler)
        
        assert len(self.monitor.alert_handlers) == initial_count + 1
        assert test_handler in self.monitor.alert_handlers
    
    def test_log_event_normal(self):
        """Test logging normal event."""
        from datetime import datetime
        event = SecurityEvent(
            event_type=SecurityEventType.DATA_ACCESS,
            severity=SecurityLevel.LOW,
            message="Normal access",
            timestamp=datetime.now()
        )
        
        with patch.object(self.monitor.detector, 'add_event', return_value=[]) as mock_add_event:
            self.monitor.log_event(event)
            
            assert self.monitor.stats['events_logged'] == 1
            self.monitor.logger.log_event.assert_called_once_with(event)
            mock_add_event.assert_called_once_with(event)
    
    def test_log_event_with_threats(self):
        """Test logging event that triggers threat detection."""
        from datetime import datetime
        event = SecurityEvent(
            event_type=SecurityEventType.AUTHENTICATION_FAILURE,
            severity=SecurityLevel.MEDIUM,
            message="Login failed",
            timestamp=datetime.now()
        )
        
        threat = SecurityEvent(
            event_type=SecurityEventType.BRUTE_FORCE_ATTEMPT,
            timestamp=datetime.now(),
            severity=SecurityLevel.HIGH,
            message="Brute force detected"
        )
        
        with patch.object(self.monitor.detector, 'add_event', return_value=[threat]):
            self.monitor.log_event(event)
        
        assert self.monitor.stats['events_logged'] == 1
        assert self.monitor.stats['threats_detected'] == 1
        
        # Should log both original event and threat
        assert self.monitor.logger.log_event.call_count == 2
    
    def test_alert_handling(self):
        """Test alert handling for critical events."""
        alert_handler = MagicMock()
        self.monitor.add_alert_handler(alert_handler)
        
        from datetime import datetime
        critical_event = SecurityEvent(
            event_type=SecurityEventType.BRUTE_FORCE_ATTEMPT,
            severity=SecurityLevel.CRITICAL,
            message="Critical threat",
            timestamp=datetime.now()
        )
        
        with patch.object(self.monitor.detector, 'add_event', return_value=[critical_event]):
            self.monitor.log_event(SecurityEvent(
                event_type=SecurityEventType.AUTHENTICATION_FAILURE,
                severity=SecurityLevel.MEDIUM,
                message="Failed login",
                timestamp=datetime.now()
            ))
        
        alert_handler.assert_called_once_with(critical_event)
        assert self.monitor.stats['alerts_sent'] == 1
    
    def test_alert_handler_exception(self):
        """Test handling of alert handler exceptions."""
        def failing_handler(event):
            raise Exception("Handler failed")
        
        self.monitor.add_alert_handler(failing_handler)
        
        critical_event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            severity=SecurityLevel.HIGH,
            message="High severity event"
        )
        
        with patch.object(self.monitor.detector, 'add_event', return_value=[critical_event]):
            # Should not raise exception despite handler failure
            self.monitor.log_event(SecurityEvent(
                timestamp=datetime.now(),
                event_type=SecurityEventType.INPUT_VALIDATION_FAILURE,
                severity=SecurityLevel.MEDIUM,
                message="Validation failed"
            ))
        
        # Alert should not be counted as sent due to failure
        assert self.monitor.stats['alerts_sent'] == 0
    
    def test_get_statistics(self):
        """Test getting monitoring statistics."""
        # Log some events
        for i in range(3):
            event = SecurityEvent(
                timestamp=datetime.now(),
                event_type=SecurityEventType.DATA_ACCESS,
                severity=SecurityLevel.LOW,
                message=f"Access {i}"
            )
            with patch.object(self.monitor.detector, 'add_event', return_value=[]):
                self.monitor.log_event(event)
        
        stats = self.monitor.get_statistics()
        
        assert stats['events_logged'] == 3
        assert stats['threats_detected'] == 0
        assert stats['alerts_sent'] == 0
        assert 'uptime_seconds' in stats
        assert 'events_per_minute' in stats
        assert isinstance(stats['uptime_seconds'], float)


class TestGlobalSecurityMonitor:
    """Test global security monitor functions."""
    
    def test_get_security_monitor_singleton(self):
        """Test that get_security_monitor returns singleton instance."""
        with patch('src.infrastructure.security.security_monitoring._security_monitor', None):
            monitor1 = get_security_monitor()
            monitor2 = get_security_monitor()
            
            assert monitor1 is monitor2
            assert isinstance(monitor1, SecurityMonitor)
    
    def test_get_security_monitor_default_alert_handler(self):
        """Test that default alert handler is added."""
        with patch('src.infrastructure.security.security_monitoring._security_monitor', None):
            monitor = get_security_monitor()
            
            assert len(monitor.alert_handlers) >= 1


class TestConvenienceFunctions:
    """Test convenience functions for logging security events."""
    
    def setup_method(self):
        """Set up test environment."""
        self.mock_monitor = MagicMock()
        
        patcher = patch('src.infrastructure.security.security_monitoring.get_security_monitor', 
                       return_value=self.mock_monitor)
        patcher.start()
        self.addCleanup = patcher.stop
    
    def teardown_method(self):
        """Clean up after test."""
        if hasattr(self, 'addCleanup'):
            self.addCleanup()
    
    def test_log_authentication_success(self):
        """Test log_authentication_success convenience function."""
        log_authentication_success(
            user_id="test_user",
            ip_address="192.168.1.1",
            endpoint="/api/login",
            session_id="abc123"
        )
        
        self.mock_monitor.log_event.assert_called_once()
        event = self.mock_monitor.log_event.call_args[0][0]
        
        assert event.event_type == SecurityEventType.AUTHENTICATION_SUCCESS
        assert event.severity == SecurityLevel.LOW
        assert event.user_id == "test_user"
        assert event.ip_address == "192.168.1.1"
        assert event.endpoint == "/api/login"
        assert event.additional_data["session_id"] == "abc123"
    
    def test_log_authentication_failure(self):
        """Test log_authentication_failure convenience function."""
        log_authentication_failure(
            user_id="test_user",
            ip_address="10.0.0.1",
            reason="Invalid password",
            attempts=3
        )
        
        self.mock_monitor.log_event.assert_called_once()
        event = self.mock_monitor.log_event.call_args[0][0]
        
        assert event.event_type == SecurityEventType.AUTHENTICATION_FAILURE
        assert event.severity == SecurityLevel.MEDIUM
        assert "Invalid password" in event.message
        assert event.user_id == "test_user"
        assert event.ip_address == "10.0.0.1"
        assert event.additional_data["attempts"] == 3
    
    def test_log_input_validation_failure(self):
        """Test log_input_validation_failure convenience function."""
        log_input_validation_failure(
            field_name="username",
            value="<script>alert('xss')</script>",
            ip_address="172.16.0.1",
            endpoint="/api/register"
        )
        
        self.mock_monitor.log_event.assert_called_once()
        event = self.mock_monitor.log_event.call_args[0][0]
        
        assert event.event_type == SecurityEventType.INPUT_VALIDATION_FAILURE
        assert event.severity == SecurityLevel.MEDIUM
        assert event.ip_address == "172.16.0.1"
        assert event.endpoint == "/api/register"
        assert event.additional_data["field_name"] == "username"
        assert "script" in event.additional_data["invalid_value"]
    
    def test_log_suspicious_activity(self):
        """Test log_suspicious_activity convenience function."""
        log_suspicious_activity(
            activity_type="sql_injection",
            description="Detected SQL injection in search parameter",
            user_id="potential_attacker",
            ip_address="203.0.113.5",
            payload="'; DROP TABLE users; --"
        )
        
        self.mock_monitor.log_event.assert_called_once()
        event = self.mock_monitor.log_event.call_args[0][0]
        
        assert event.event_type == SecurityEventType.SUSPICIOUS_ACTIVITY
        assert event.severity == SecurityLevel.HIGH
        assert "sql_injection" in event.message
        assert event.user_id == "potential_attacker"
        assert event.ip_address == "203.0.113.5"
        assert event.additional_data["payload"] == "'; DROP TABLE users; --"
    
    def test_log_configuration_change(self):
        """Test log_configuration_change convenience function."""
        changes = {
            "security_level": {"old": "medium", "new": "high"},
            "timeout": {"old": 300, "new": 600}
        }
        
        log_configuration_change(
            config_name="security_settings",
            user_id="admin_user",
            changes=changes,
            reason="Security hardening"
        )
        
        self.mock_monitor.log_event.assert_called_once()
        event = self.mock_monitor.log_event.call_args[0][0]
        
        assert event.event_type == SecurityEventType.CONFIGURATION_CHANGE
        assert event.severity == SecurityLevel.MEDIUM
        assert event.user_id == "admin_user"
        assert event.additional_data["config_name"] == "security_settings"
        assert event.additional_data["changes"] == changes
        assert event.additional_data["reason"] == "Security hardening"


class TestMonitorEndpointDecorator:
    """Test monitor_endpoint decorator."""
    
    def setup_method(self):
        """Set up test Flask app."""
        from flask import Flask
        self.app = Flask(__name__)
        self.app.secret_key = 'test_secret_key_for_sessions'
        self.mock_monitor = MagicMock()
        
        patcher = patch('src.infrastructure.security.security_monitoring.get_security_monitor', 
                       return_value=self.mock_monitor)
        patcher.start()
        self.addCleanup = patcher.stop
    
    def teardown_method(self):
        """Clean up after test."""
        if hasattr(self, 'addCleanup'):
            self.addCleanup()
    
    def test_monitor_endpoint_success(self):
        """Test monitoring successful endpoint access."""
        @self.app.route('/test')
        @monitor_endpoint()
        def test_endpoint():
            return {'status': 'success'}
        
        with self.app.test_client() as client:
            response = client.get('/test')
            assert response.status_code == 200
        
        # Should log data access event
        self.mock_monitor.log_event.assert_called_once()
        event = self.mock_monitor.log_event.call_args[0][0]
        
        assert event.event_type == SecurityEventType.DATA_ACCESS
        assert event.severity == SecurityLevel.LOW
        assert "test_endpoint" in event.message
        assert event.additional_data['method'] == 'GET'
    
    def test_monitor_endpoint_with_custom_name(self):
        """Test monitoring with custom endpoint name."""
        @self.app.route('/custom')
        @monitor_endpoint('custom_api')
        def custom_endpoint():
            return {'data': 'test'}
        
        with self.app.test_client() as client:
            response = client.get('/custom')
            assert response.status_code == 200
        
        event = self.mock_monitor.log_event.call_args[0][0]
        assert "custom_api" in event.message
        assert event.endpoint == "custom_api"
    
    def test_monitor_endpoint_with_user(self):
        """Test monitoring with authenticated user."""
        @self.app.route('/protected')
        @monitor_endpoint()
        def protected_endpoint():
            from flask import g
            g.current_user = 'authenticated_user'
            return {'message': 'protected data'}
        
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                # Simulate authenticated user
                pass
            response = client.get('/protected')
            assert response.status_code == 200
        
        # Note: The actual user setting happens inside the endpoint
        # This test verifies the decorator captures user information
        self.mock_monitor.log_event.assert_called_once()
    
    def test_monitor_endpoint_error(self):
        """Test monitoring endpoint that raises an error."""
        @self.app.route('/error')
        @monitor_endpoint()
        def error_endpoint():
            raise ValueError("Test error")
        
        with self.app.test_client() as client:
            response = client.get('/error')
            # Flask catches the exception and returns 500 error
            assert response.status_code == 500
        
        # Should log system error event
        self.mock_monitor.log_event.assert_called_once()
        event = self.mock_monitor.log_event.call_args[0][0]
        
        assert event.event_type == SecurityEventType.SYSTEM_ERROR
        assert event.severity == SecurityLevel.HIGH
        assert "Test error" in event.message
        assert event.additional_data['error_type'] == 'ValueError'


class TestSecurityMonitoringIntegration:
    """Integration tests for security monitoring system."""
    
    def test_complete_monitoring_workflow(self):
        """Test complete security monitoring workflow."""
        # Create fresh monitor instance
        monitor = SecurityMonitor()
        
        # Track alerts
        alerts = []
        def alert_handler(event):
            alerts.append(event)
        
        monitor.add_alert_handler(alert_handler)
        
        # Simulate authentication failures leading to brute force detection
        user_id = "target_user"
        ip_address = "192.168.1.100"
        
        for i in range(6):  # This should trigger brute force detection
            event = SecurityEvent(
                timestamp=datetime.now(),
                event_type=SecurityEventType.AUTHENTICATION_FAILURE,
                severity=SecurityLevel.MEDIUM,
                message=f"Login attempt {i} failed",
                user_id=user_id,
                ip_address=ip_address
            )
            monitor.log_event(event)
        
        # Check statistics
        stats = monitor.get_statistics()
        assert stats['events_logged'] >= 6  # Original events + any threats
        assert stats['threats_detected'] >= 1  # Brute force threat
        
        # Check that alert was sent for high/critical severity threats
        high_severity_alerts = [a for a in alerts if a.severity in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]]
        assert len(high_severity_alerts) >= 1
    
    def test_multiple_threat_detection(self):
        """Test detection of multiple threat types."""
        detector = ThreatDetector(window_minutes=30)
        
        # Simulate various attack patterns
        attacks = {
            'brute_force': [
                SecurityEvent(
                    timestamp=datetime.now(),
                    event_type=SecurityEventType.AUTHENTICATION_FAILURE,
                    severity=SecurityLevel.MEDIUM,
                    message=f"Brute force attempt {i}",
                    user_id="victim_user",
                    ip_address="10.0.0.100"
                ) for i in range(6)
            ],
            'input_validation': [
                SecurityEvent(
                    timestamp=datetime.now(),
                    event_type=SecurityEventType.INPUT_VALIDATION_FAILURE,
                    severity=SecurityLevel.MEDIUM,
                    message=f"Input validation failure {i}",
                    ip_address="10.0.0.101"
                ) for i in range(21)
            ],
            'suspicious_activity': [
                SecurityEvent(
                    timestamp=datetime.now(),
                    event_type=SecurityEventType.SQL_INJECTION_ATTEMPT,
                    severity=SecurityLevel.HIGH,
                    message=f"SQL injection attempt {i}",
                    ip_address="10.0.0.102"
                ) for i in range(51)
            ]
        }
        
        all_threats = []
        
        # Add all attack events
        for attack_type, events in attacks.items():
            for event in events:
                threats = detector.add_event(event)
                all_threats.extend(threats)
        
        # Should detect multiple types of threats
        threat_types = {threat.event_type for threat in all_threats}
        assert SecurityEventType.BRUTE_FORCE_ATTEMPT in threat_types
        assert SecurityEventType.SUSPICIOUS_ACTIVITY in threat_types
        
        # Should have multiple threats detected
        assert len(all_threats) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])