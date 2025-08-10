#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import (
    Any,
    Dict,
    Enum,
    List,
    Optional,
    datetime,
    json,
    logging,
    os,
    timedelta
)
"""
Security Monitoring and Logging System

Provides comprehensive security event logging, monitoring, and alerting
for the multi-agent AI system. Addresses security logging gaps.
"""

# import logging  # Consolidated to common_imports
# import json  # Consolidated to common_imports
# import time  # Consolidated to common_imports
# from datetime import datetime, timedelta  # Consolidated to common_imports
# from typing import Any, Dict, List, Optional, Union  # Consolidated to common_imports
from dataclasses import dataclass, asdict
# from enum import Enum  # Consolidated to common_imports
import threading
from collections import defaultdict, deque
# import hashlib  # Consolidated to common_imports
# import os  # Consolidated to common_imports


class SecurityEventType(Enum):
    """Types of security events to monitor."""
    
    AUTHENTICATION_SUCCESS = "auth_success"
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHORIZATION_FAILURE = "auth_denied"
    SUSPICIOUS_ACTIVITY = "suspicious"
    INPUT_VALIDATION_FAILURE = "input_invalid"
    SQL_INJECTION_ATTEMPT = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    DIRECTORY_TRAVERSAL = "path_traversal"
    BRUTE_FORCE_ATTEMPT = "brute_force"
    RATE_LIMIT_EXCEEDED = "rate_limit"
    CONFIGURATION_CHANGE = "config_change"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_ACCESS = "data_access"
    SYSTEM_ERROR = "system_error"
    SECURITY_SCAN = "security_scan"


class SecurityLevel(Enum):
    """Security event severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Represents a security event for logging and monitoring."""
    
    event_type: SecurityEventType
    severity: SecurityLevel
    message: str
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        
        if self.additional_data is None:
            self.additional_data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization."""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict(), sort_keys=True)


class SecurityLogger:
    """Enhanced security logger with structured logging."""
    
    def __init__(self, logger_name: str = "security"):
        """
        Initialize security logger.
        
        Args:
            logger_name: Name of the logger
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        
        # Create security-specific formatter
        formatter = logging.Formatter(
            '%(asctime)s [SECURITY] %(levelname)s: %(message)s'
        )
        
        # Set up file handler for security logs
        if not self.logger.handlers:
            # Create logs directory if it doesn't exist
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            
            # Security log file with proper permissions
            security_log_file = os.path.join(log_dir, "security.log")
            file_handler = logging.FileHandler(security_log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            
            # Set secure file permissions (owner read/write only)
            if os.path.exists(security_log_file):
                os.chmod(security_log_file, 0o600)
            
            self.logger.addHandler(file_handler)
            
            # Console handler for critical events
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.WARNING)
            self.logger.addHandler(console_handler)
    
    def log_event(self, event: SecurityEvent):
        """
        Log a security event with appropriate severity.
        
        Args:
            event: SecurityEvent to log
        """
        log_message = f"{event.event_type.value.upper()}: {event.message}"
        
        if event.user_id:
            log_message += f" [User: {event.user_id}]"
        
        if event.ip_address:
            log_message += f" [IP: {event.ip_address}]"
        
        if event.endpoint:
            log_message += f" [Endpoint: {event.endpoint}]"
        
        # Add structured data as JSON
        structured_data = event.to_dict()
        log_message += f" [Data: {json.dumps(structured_data)}]"
        
        # Log with appropriate level
        if event.severity == SecurityLevel.CRITICAL:
            self.logger.critical(log_message)
        elif event.severity == SecurityLevel.HIGH:
            self.logger.error(log_message)
        elif event.severity == SecurityLevel.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)


class ThreatDetector:
    """Detects potential security threats based on event patterns."""
    
    def __init__(self, window_minutes: int = 15, max_events: int = 1000):
        """
        Initialize threat detector.
        
        Args:
            window_minutes: Time window for event analysis
            max_events: Maximum events to keep in memory
        """
        self.window_minutes = window_minutes
        self.max_events = max_events
        
        # Event storage for pattern analysis
        self.events = deque(maxlen=max_events)
        self.user_events = defaultdict(lambda: deque(maxlen=100))
        self.ip_events = defaultdict(lambda: deque(maxlen=100))
        
        # Threat detection thresholds
        self.thresholds = {
            'failed_auth_per_user': 5,
            'failed_auth_per_ip': 10,
            'input_validation_failures': 20,
            'suspicious_requests_per_ip': 50,
        }
        
        self.lock = threading.RLock()
    
    def add_event(self, event: SecurityEvent) -> List[SecurityEvent]:
        """
        Add event and check for threats.
        
        Args:
            event: Security event to analyze
            
        Returns:
            List of additional threat events detected
        """
        with self.lock:
            # Add to main event queue
            self.events.append(event)
            
            # Add to user and IP specific queues
            if event.user_id:
                self.user_events[event.user_id].append(event)
            
            if event.ip_address:
                self.ip_events[event.ip_address].append(event)
            
            # Check for threats
            threats = []
            threats.extend(self._check_brute_force_attacks(event))
            threats.extend(self._check_input_validation_patterns(event))
            threats.extend(self._check_suspicious_activity_patterns(event))
            
            return threats
    
    def _check_brute_force_attacks(self, event: SecurityEvent) -> List[SecurityEvent]:
        """Check for brute force attack patterns."""
        threats = []
        
        if event.event_type != SecurityEventType.AUTHENTICATION_FAILURE:
            return threats
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.window_minutes)
        
        # Check failed authentication attempts per user
        if event.user_id:
            user_failures = [
                e for e in self.user_events[event.user_id]
                if (e.event_type == SecurityEventType.AUTHENTICATION_FAILURE and
                    e.timestamp > cutoff_time)
            ]
            
            if len(user_failures) >= self.thresholds['failed_auth_per_user']:
                threats.append(SecurityEvent(
                    event_type=SecurityEventType.BRUTE_FORCE_ATTEMPT,
                    severity=SecurityLevel.HIGH,
                    message=f"Brute force attack detected for user {event.user_id}",
                    timestamp=datetime.now(),
                    user_id=event.user_id,
                    ip_address=event.ip_address,
                    additional_data={
                        'failed_attempts': len(user_failures),
                        'time_window_minutes': self.window_minutes
                    }
                ))
        
        # Check failed authentication attempts per IP
        if event.ip_address:
            ip_failures = [
                e for e in self.ip_events[event.ip_address]
                if (e.event_type == SecurityEventType.AUTHENTICATION_FAILURE and
                    e.timestamp > cutoff_time)
            ]
            
            if len(ip_failures) >= self.thresholds['failed_auth_per_ip']:
                threats.append(SecurityEvent(
                    event_type=SecurityEventType.BRUTE_FORCE_ATTEMPT,
                    severity=SecurityLevel.CRITICAL,
                    message=f"Brute force attack detected from IP {event.ip_address}",
                    timestamp=datetime.now(),
                    ip_address=event.ip_address,
                    additional_data={
                        'failed_attempts': len(ip_failures),
                        'affected_users': len(set(e.user_id for e in ip_failures if e.user_id)),
                        'time_window_minutes': self.window_minutes
                    }
                ))
        
        return threats
    
    def _check_input_validation_patterns(self, event: SecurityEvent) -> List[SecurityEvent]:
        """Check for input validation attack patterns."""
        threats = []
        
        if event.event_type != SecurityEventType.INPUT_VALIDATION_FAILURE:
            return threats
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.window_minutes)
        
        # Check validation failures per IP
        if event.ip_address:
            validation_failures = [
                e for e in self.ip_events[event.ip_address]
                if (e.event_type == SecurityEventType.INPUT_VALIDATION_FAILURE and
                    e.timestamp > cutoff_time)
            ]
            
            if len(validation_failures) >= self.thresholds['input_validation_failures']:
                threats.append(SecurityEvent(
                    event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                    severity=SecurityLevel.HIGH,
                    message=f"Repeated input validation failures from IP {event.ip_address}",
                    timestamp=datetime.now(),
                    ip_address=event.ip_address,
                    additional_data={
                        'validation_failures': len(validation_failures),
                        'time_window_minutes': self.window_minutes
                    }
                ))
        
        return threats
    
    def _check_suspicious_activity_patterns(self, event: SecurityEvent) -> List[SecurityEvent]:
        """Check for general suspicious activity patterns."""
        threats = []
        
        suspicious_types = {
            SecurityEventType.SQL_INJECTION_ATTEMPT,
            SecurityEventType.XSS_ATTEMPT,
            SecurityEventType.DIRECTORY_TRAVERSAL,
        }
        
        if event.event_type not in suspicious_types:
            return threats
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.window_minutes)
        
        # Check suspicious requests per IP
        if event.ip_address:
            suspicious_events = [
                e for e in self.ip_events[event.ip_address]
                if (e.event_type in suspicious_types and e.timestamp > cutoff_time)
            ]
            
            if len(suspicious_events) >= self.thresholds['suspicious_requests_per_ip']:
                threats.append(SecurityEvent(
                    event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                    severity=SecurityLevel.CRITICAL,
                    message=f"High volume of suspicious activity from IP {event.ip_address}",
                    timestamp=datetime.now(),
                    ip_address=event.ip_address,
                    additional_data={
                        'suspicious_events': len(suspicious_events),
                        'event_types': list(set(e.event_type.value for e in suspicious_events)),
                        'time_window_minutes': self.window_minutes
                    }
                ))
        
        return threats


class SecurityMonitor:
    """Main security monitoring system."""
    
    def __init__(self):
        """Initialize security monitor with logger and threat detector."""
        self.logger = SecurityLogger()
        self.detector = ThreatDetector()
        self.alert_handlers: List[callable] = []
        
        # Statistics tracking
        self.stats = {
            'events_logged': 0,
            'threats_detected': 0,
            'alerts_sent': 0,
            'start_time': datetime.utcnow()
        }
    
    def add_alert_handler(self, handler: callable):
        """
        Add an alert handler for critical events.
        
        Args:
            handler: Function that takes a SecurityEvent and handles alerts
        """
        self.alert_handlers.append(handler)
    
    def log_event(self, event: SecurityEvent):
        """
        Log a security event and check for threats.
        
        Args:
            event: SecurityEvent to log
        """
        # Log the event
        self.logger.log_event(event)
        self.stats['events_logged'] += 1
        
        # Check for threats
        threats = self.detector.add_event(event)
        
        # Process any detected threats
        for threat in threats:
            self.logger.log_event(threat)
            self.stats['threats_detected'] += 1
            
            # Send alerts for critical threats
            if threat.severity in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                self._send_alerts(threat)
    
    def _send_alerts(self, event: SecurityEvent):
        """Send alerts for critical security events."""
        for handler in self.alert_handlers:
            try:
                handler(event)
                self.stats['alerts_sent'] += 1
            except Exception as e:
                self.logger.logger.error(f"Alert handler failed: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        uptime = datetime.utcnow() - self.stats['start_time']
        
        return {
            **self.stats,
            'uptime_seconds': uptime.total_seconds(),
            'events_per_minute': self.stats['events_logged'] / max(uptime.total_seconds() / 60, 1),
        }


# Global security monitor instance
_security_monitor = None


def get_security_monitor() -> SecurityMonitor:
    """Get the global security monitor instance."""
    global _security_monitor
    if _security_monitor is None:
        _security_monitor = SecurityMonitor()
        
        # Set up default alert handler for critical events
        def default_alert_handler(event: SecurityEvent):
            """Default alert handler that logs to console."""
            print(f"🚨 SECURITY ALERT: {event.message}")
            print(f"   Severity: {event.severity.value}")
            print(f"   Time: {event.timestamp}")
            if event.user_id:
                print(f"   User: {event.user_id}")
            if event.ip_address:
                print(f"   IP: {event.ip_address}")
        
        _security_monitor.add_alert_handler(default_alert_handler)
    
    return _security_monitor


# Convenience functions for common security events

def log_authentication_success(user_id: str, ip_address: str = None, 
                              endpoint: str = None, **kwargs):
    """Log successful authentication."""
    event = SecurityEvent(
        event_type=SecurityEventType.AUTHENTICATION_SUCCESS,
        severity=SecurityLevel.LOW,
        message=f"User {user_id} authenticated successfully",
        timestamp=datetime.now(),
        user_id=user_id,
        ip_address=ip_address,
        endpoint=endpoint,
        additional_data=kwargs
    )
    get_security_monitor().log_event(event)


def log_authentication_failure(user_id: str = None, ip_address: str = None,
                              reason: str = "Invalid credentials", **kwargs):
    """Log failed authentication."""
    message = f"Authentication failed: {reason}"
    if user_id:
        message += f" for user {user_id}"
    
    event = SecurityEvent(
        event_type=SecurityEventType.AUTHENTICATION_FAILURE,
        severity=SecurityLevel.MEDIUM,
        message=message,
        timestamp=datetime.now(),
        user_id=user_id,
        ip_address=ip_address,
        additional_data=kwargs
    )
    get_security_monitor().log_event(event)


def log_input_validation_failure(field_name: str, value: str, ip_address: str = None,
                                endpoint: str = None, **kwargs):
    """Log input validation failure."""
    event = SecurityEvent(
        event_type=SecurityEventType.INPUT_VALIDATION_FAILURE,
        severity=SecurityLevel.MEDIUM,
        message=f"Input validation failed for field {field_name}",
        timestamp=datetime.now(),
        ip_address=ip_address,
        endpoint=endpoint,
        additional_data={
            'field_name': field_name,
            'invalid_value': value[:100],  # Truncate for logging
            **kwargs
        }
    )
    get_security_monitor().log_event(event)


def log_suspicious_activity(activity_type: str, description: str, 
                           user_id: str = None, ip_address: str = None, **kwargs):
    """Log suspicious activity."""
    event = SecurityEvent(
        event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
        severity=SecurityLevel.HIGH,
        message=f"Suspicious activity detected: {activity_type} - {description}",
        timestamp=datetime.now(),
        user_id=user_id,
        ip_address=ip_address,
        additional_data=kwargs
    )
    get_security_monitor().log_event(event)


def log_configuration_change(config_name: str, user_id: str, 
                            changes: Dict[str, Any], **kwargs):
    """Log configuration changes."""
    event = SecurityEvent(
        event_type=SecurityEventType.CONFIGURATION_CHANGE,
        severity=SecurityLevel.MEDIUM,
        message=f"Configuration changed: {config_name}",
        timestamp=datetime.now(),
        user_id=user_id,
        additional_data={
            'config_name': config_name,
            'changes': changes,
            **kwargs
        }
    )
    get_security_monitor().log_event(event)


# Security monitoring decorator for Flask routes
def monitor_endpoint(endpoint_name: str = None):
    """
    Decorator to automatically monitor Flask endpoint security.
    
    Args:
        endpoint_name: Custom endpoint name (uses function name if None)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            from flask import request, g
            
            # Get request information
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            endpoint = endpoint_name or func.__name__
            user_id = getattr(g, 'current_user', None)
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Log successful access
                event = SecurityEvent(
                    event_type=SecurityEventType.DATA_ACCESS,
                    severity=SecurityLevel.LOW,
                    message=f"Endpoint accessed: {endpoint}",
                    timestamp=datetime.now(),
                    user_id=user_id,
                    ip_address=ip_address,
                    endpoint=endpoint,
                    additional_data={
                        'user_agent': user_agent,
                        'method': request.method
                    }
                )
                get_security_monitor().log_event(event)
                
                return result
                
            except Exception as e:
                # Log system errors
                event = SecurityEvent(
                    event_type=SecurityEventType.SYSTEM_ERROR,
                    severity=SecurityLevel.HIGH,
                    message=f"System error in {endpoint}: {str(e)}",
                    timestamp=datetime.now(),
                    user_id=user_id,
                    ip_address=ip_address,
                    endpoint=endpoint,
                    additional_data={
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    }
                )
                get_security_monitor().log_event(event)
                raise
        
        return wrapper
    return decorator