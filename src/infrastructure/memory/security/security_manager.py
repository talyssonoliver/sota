"""
Security Manager for Memory Engine

Centralized security management for memory operations.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..exceptions import MemoryEngineSecurityError

logger = logging.getLogger(__name__)


@dataclass
class SecurityPolicy:
    """Security policy configuration"""

    encryption_enabled: bool = True
    pii_detection_enabled: bool = True
    audit_logging_enabled: bool = True
    access_control_enabled: bool = True
    allowed_roles: List[str] = None

    def __post_init__(self):
        if self.allowed_roles is None:
            self.allowed_roles = ["system", "user", "admin"]


class SecurityManager:
    """Manages security policies and operations for memory engine"""

    def __init__(self, policy: Optional[SecurityPolicy] = None):
        """Initialize security manager

        Args:
            policy: Security policy configuration
        """
        self.policy = policy or SecurityPolicy()
        self.audit_log: List[Dict[str, Any]] = []

    def validate_access(self, operation: str, role: str = "user") -> bool:
        """Validate access for an operation

        Args:
            operation: Operation being attempted
            role: User role

        Returns:
            True if access allowed

        Raises:
            MemoryEngineSecurityError: If access denied
        """
        if not self.policy.access_control_enabled:
            return True

        if role not in self.policy.allowed_roles:
            self._audit_log(
                "access_denied",
                {"operation": operation, "role": role, "reason": "invalid_role"},
            )
            raise MemoryEngineSecurityError(f"Access denied for role: {role}")

        self._audit_log("access_granted", {"operation": operation, "role": role})
        return True

    def sanitize_data(self, data: str) -> str:
        """Sanitize data for storage

        Args:
            data: Data to sanitize

        Returns:
            Sanitized data
        """
        if not self.policy.pii_detection_enabled:
            return data

        # Basic PII detection and masking
        import re

        # Mask email addresses
        data = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]", data
        )

        # Mask phone numbers
        data = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE]", data)

        # Mask SSN patterns
        data = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]", data)

        # Mask credit card patterns
        data = re.sub(
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[CREDIT_CARD]", data
        )

        return data

    def encrypt_if_required(self, data: str) -> str:
        """Encrypt data if encryption is enabled

        Args:
            data: Data to potentially encrypt

        Returns:
            Encrypted or original data
        """
        if not self.policy.encryption_enabled:
            return data

        # Simple encryption placeholder
        # In production, use proper encryption like AES
        try:
            import base64

            encrypted = base64.b64encode(data.encode("utf-8")).decode("utf-8")
            self._audit_log("data_encrypted", {"size": len(data)})
            return f"ENCRYPTED:{encrypted}"
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data

    def decrypt_if_required(self, data: str) -> str:
        """Decrypt data if it's encrypted

        Args:
            data: Data to potentially decrypt

        Returns:
            Decrypted or original data
        """
        if not data.startswith("ENCRYPTED:"):
            return data

        try:
            import base64

            encrypted_data = data[10:]  # Remove "ENCRYPTED:" prefix
            decrypted = base64.b64decode(encrypted_data.encode("utf-8")).decode("utf-8")
            self._audit_log("data_decrypted", {"size": len(decrypted)})
            return decrypted
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return data

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log entries

        Returns:
            List of audit log entries
        """
        return self.audit_log.copy()

    def clear_audit_log(self):
        """Clear audit log"""
        self.audit_log.clear()

    def _audit_log(self, event_type: str, details: Dict[str, Any]):
        """Add entry to audit log

        Args:
            event_type: Type of event
            details: Event details
        """
        if not self.policy.audit_logging_enabled:
            return

        from datetime import datetime

        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
        }

        self.audit_log.append(entry)

        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get the global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager
