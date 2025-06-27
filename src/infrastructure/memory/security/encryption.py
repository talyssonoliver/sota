#!/usr/bin/env python3
"""
Memory Engine Security System

Advanced Encryption Module for Memory Engine

Provides secure encryption/decryption capabilities with key management,
thread safety, and security monitoring.

Unified encryption and security utilities for the AI system.
Handles encryption, PII detection, access control, and audit logging.

Consolidated from tools/memory/security.py
New location: src/platform/memory/security/encryption.py

Part of the unified memory architecture eliminating fragmentation
across tools/memory/, memory-bank/, and runtime/ locations.
"""

import logging
import threading
import os
import re
import hashlib
import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

# Import configuration with proper error handling
try:
    from ..config.memory_config import MemoryEngineConfig
except ImportError as e:
    logging.error(f"CRITICAL: Cannot import MemoryEngineConfig: {e}")
    raise ImportError("Critical memory configuration not available") from e

from ..config.exceptions import SecurityError, AccessDeniedError, EncryptionError

logger = logging.getLogger(__name__)

# Cryptography imports with proper error handling
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("cryptography library not available, falling back to insecure encryption")

class SecurityManager:
    """Manages encryption, access control, and security policies"""
    
    def __init__(self, config: Any):
        self.config = config
        self.encryption_enabled = getattr(config, 'encryption_enabled', False)
        self.pii_detection_enabled = getattr(config, 'pii_detection_enabled', False)
        self.access_control_enabled = getattr(config, 'access_control_enabled', False)
        
        # Initialize encryption
        self.cipher_suite = None
        if self.encryption_enabled and CRYPTO_AVAILABLE:
            self.cipher_suite = self._initialize_encryption()
        
        # Initialize PII patterns
        self.pii_patterns = self._initialize_pii_patterns()
          # Thread safety
        self.lock = threading.RLock()
        
        logger.info("SecurityManager initialized")
    
    def _initialize_encryption(self) -> Optional[Any]:
        """Initialize encryption cipher suite"""
        try:
            if not CRYPTO_AVAILABLE:
                logger.warning("Cryptography not available, encryption disabled")
                return None
            key = self._load_or_generate_key()
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise EncryptionError(f"Encryption initialization failed: {e}")
    
    def _load_or_generate_key(self) -> bytes:
        """Load encryption key from environment variable or generate a new one"""
        # Try to load from environment variable
        env_key = os.environ.get('MEMORY_ENGINE_KEY')
        if env_key:
            try:
                # Fernet keys are base64 encoded strings, use them directly as bytes
                return env_key.encode('utf-8')
            except Exception as e:
                logger.error(f"Invalid MEMORY_ENGINE_KEY environment variable: {e}")
                raise EncryptionError(f"Invalid encryption key in environment: {e}")
        
        # No key found - this is a security issue in production
        if os.environ.get('ENVIRONMENT', '').lower() == 'production':
            logger.error("MEMORY_ENGINE_KEY environment variable is required in production")
            raise EncryptionError("Missing encryption key in production environment")
        
        # Development/testing: Generate new key but warn about it
        logger.warning("No MEMORY_ENGINE_KEY found in environment. Generating temporary key for development.")
        logger.warning("SECURITY WARNING: This key is NOT persistent and will change on restart!")
        logger.warning("For production or persistent development, set MEMORY_ENGINE_KEY in your .env file.")
        
        key = Fernet.generate_key()
        
        # Log the generated key for development convenience
        key_str = key.decode('utf-8')
        logger.info(f"Generated temporary key: MEMORY_ENGINE_KEY={key_str}")
        logger.info("To make this key persistent, add it to your .env file")
        logger.info("Or generate a new one with: python scripts/generate_memory_key.py")
        
        return key
    
    def _initialize_pii_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize PII detection patterns"""
        patterns = {}
        
        # Email addresses
        patterns['email'] = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone numbers (US format)
        patterns['phone'] = re.compile(
            r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        )
        
        # Social Security Numbers
        patterns['ssn'] = re.compile(
            r'\b\d{3}-?\d{2}-?\d{4}\b'
        )
        
        # Credit card numbers (basic pattern)
        patterns['credit_card'] = re.compile(
            r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        )
        
        # IP addresses
        patterns['ip_address'] = re.compile(
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        )
        
        # API keys (common patterns)
        patterns['api_key'] = re.compile(
            r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|bearer[_-]?token)[\s]*[:=][\s]*["\']?([a-zA-Z0-9\-_]{20,})["\']?'
        )
        
        return patterns
    
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt string data to bytes"""
        if not self.encryption_enabled or not self.cipher_suite:
            return data.encode('utf-8')
        
        try:
            return self.cipher_suite.encrypt(data.encode('utf-8'))
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionError(f"Failed to encrypt data: {e}")
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt bytes data to string"""
        if not self.encryption_enabled or not self.cipher_suite:
            return encrypted_data.decode('utf-8')
        
        try:
            return self.cipher_suite.decrypt(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise EncryptionError(f"Failed to decrypt data: {e}")
    
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII in text and return findings"""
        if not self.pii_detection_enabled:
            return []
        
        findings = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                findings.append({
                    'type': pii_type,
                    'value': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.9  # Static confidence for pattern matches
                })
        
        return findings
    
    def sanitize_text(self, text: str, redact_pii: bool = True) -> str:
        """Sanitize text by removing or redacting PII"""
        if not self.pii_detection_enabled or not redact_pii:
            return text
        
        sanitized = text
        pii_findings = self.detect_pii(text)
        
        # Sort by position in reverse order to maintain positions during replacement
        pii_findings.sort(key=lambda x: x['start'], reverse=True)
        
        for finding in pii_findings:
            redacted_value = f"[REDACTED_{finding['type'].upper()}]"
            sanitized = (
                sanitized[:finding['start']] + 
                redacted_value + 
                sanitized[finding['end']:]
            )
        
        return sanitized
    
    def check_access(self, user: str, resource: str, operation: str) -> bool:
        """Check if user has access to perform operation on resource"""
        if not self.access_control_enabled:
            return True
        
        # Basic access control - can be extended
        # For now, allow all operations for authenticated users
        if user and user != "anonymous":
            return True
        
        # Deny access for anonymous users to sensitive operations
        sensitive_operations = {'delete', 'modify', 'admin'}
        if operation.lower() in sensitive_operations:
            return False
        
        return True
    
    def audit_operation(self, user: str, operation: str, resource: str, 
                       success: bool, details: Optional[Dict] = None) -> None:
        """Log audit entry for operation"""
        if not self.config.audit_logging_enabled:
            return
        
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'operation': operation,
            'resource': resource,
            'success': success,
            'details': details or {}
        }
        
        # For now, log to standard logger
        # In production, this would go to a dedicated audit log
        logger.info(f"AUDIT: {audit_entry}")
    
    def generate_secure_hash(self, data: str) -> str:
        """Generate secure hash of data"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def secure_delete(self, file_path: str) -> bool:
        """Securely delete a file by overwriting it"""
        try:
            if not os.path.exists(file_path):
                return True
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Overwrite with random data multiple times
            with open(file_path, 'r+b') as f:
                for _ in range(3):  # 3 passes
                    f.seek(0)
                    f.write(secrets.token_bytes(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Finally delete the file
            os.remove(file_path)
            return True
            
        except Exception as e:
            logger.error(f"Secure delete failed for {file_path}: {e}")
            return False

class AccessControlManager:
    """Manages user access control and permissions"""
    
    def __init__(self, config: Any):
        self.config = config
        self.user_permissions: Dict[str, Set[str]] = {}
        self.role_permissions: Dict[str, Set[str]] = {}
        self.user_roles: Dict[str, Set[str]] = {}
        self.lock = threading.RLock()
        
        self._initialize_default_permissions()
    
    def _initialize_default_permissions(self):
        """Initialize default roles and permissions"""
        # Default roles
        self.role_permissions['admin'] = {
            'read', 'write', 'delete', 'modify', 'admin'
        }
        self.role_permissions['user'] = {
            'read', 'write'
        }
        self.role_permissions['readonly'] = {
            'read'
        }
    
    def add_user_permission(self, user: str, permission: str):
        """Add permission to user"""
        with self.lock:
            if user not in self.user_permissions:
                self.user_permissions[user] = set()
            self.user_permissions[user].add(permission)
    
    def add_user_role(self, user: str, role: str):
        """Add role to user"""
        with self.lock:
            if user not in self.user_roles:
                self.user_roles[user] = set()
            self.user_roles[user].add(role)
    
    def has_permission(self, user: str, permission: str) -> bool:
        """Check if user has specific permission"""
        with self.lock:
            # Check direct user permissions
            user_perms = self.user_permissions.get(user, set())
            if permission in user_perms:
                return True
            
            # Check role-based permissions
            user_roles = self.user_roles.get(user, set())
            for role in user_roles:
                role_perms = self.role_permissions.get(role, set())
                if permission in role_perms:
                    return True
            
            return False

class AuditLogger:
    """Handles audit logging for security events"""
    
    def __init__(self, config: Any):
        self.config = config
        self.enabled = getattr(config, 'audit_logging_enabled', False)
        self.audit_file = "memory_engine_audit.log"
        self.lock = threading.RLock()
    
    def log_event(self, event_type: str, user: str, details: Dict[str, Any]):
        """Log audit event"""
        if not self.enabled:
            return
        
        with self.lock:
            timestamp = datetime.now().isoformat()
            event = {
                'timestamp': timestamp,
                'event_type': event_type,
                'user': user,
                'details': details
            }
            
            # Log to file
            try:
                with open(self.audit_file, 'a', encoding='utf-8') as f:
                    f.write(f"{timestamp} - {event_type} - {user} - {details}\n")
            except Exception as e:
                logger.error(f"Failed to write audit log: {e}")
            
            # Also log to standard logger
            logger.info(f"AUDIT: {event}")
    
    def log_access_attempt(self, user: str, resource: str, success: bool):
        """Log access attempt"""
        self.log_event('access_attempt', user, {
            'resource': resource,
            'success': success
        })
    
    def log_data_operation(self, user: str, operation: str, resource: str):
        """Log data operation"""
        self.log_event('data_operation', user, {
            'operation': operation,
            'resource': resource
        })