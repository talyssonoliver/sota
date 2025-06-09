"""
Memory Engine Security System
Handles encryption, PII detection, access control, and audit logging
"""

import base64
import hashlib
import logging
import os
import re
import secrets
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from .config import MemoryEngineConfig
from .exceptions import SecurityError, AccessDeniedError, EncryptionError

logger = logging.getLogger(__name__)

# Cryptography imports
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
    
    def __init__(self, config: MemoryEngineConfig):
        self.config = config
        self.encryption_enabled = config.encryption_enabled
        self.pii_detection_enabled = config.pii_detection_enabled
        self.access_control_enabled = config.access_control_enabled
        
        # Initialize encryption
        self.cipher_suite = None
        if self.encryption_enabled and CRYPTO_AVAILABLE:
            self.cipher_suite = self._initialize_encryption()
        
        # Initialize PII patterns
        self.pii_patterns = self._initialize_pii_patterns()
        
        # Thread safety
        self.lock = threading.RLock()
        
        logger.info("SecurityManager initialized")
    
    def _initialize_encryption(self) -> Optional[Fernet]:
        """Initialize encryption cipher suite"""
        try:
            key = self._load_or_generate_key()
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise EncryptionError(f"Encryption initialization failed: {e}")
    
    def _load_or_generate_key(self) -> bytes:
        """Load or generate encryption key"""
        key_file = ".memory_engine_key"
        
        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not load existing key: {e}")
        
        # Generate new key
        logger.info("Generating new encryption key")
        key = Fernet.generate_key()
        
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
        except Exception as e:
            logger.warning(f"Could not save encryption key: {e}")
        
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
    
    def __init__(self, config: MemoryEngineConfig):
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
    
    def __init__(self, config: MemoryEngineConfig):
        self.config = config
        self.enabled = config.audit_logging_enabled
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