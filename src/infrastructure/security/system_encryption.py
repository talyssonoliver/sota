#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import logging, os
"""System-wide encryption utilities.

Provides system-level encryption capabilities for sensitive data.
Integrates with MemoryEngine security manager for consistent encryption.
"""

# import logging  # Consolidated to common_imports
# import os  # Consolidated to common_imports
from typing import Dict

from src.infrastructure.memory.config.memory_config import MemoryEngineConfig
from src.infrastructure.memory.security.encryption import SecurityManager

logger = logging.getLogger(__name__)


class SystemEncryption:
    """System-wide encryption utilities.
    
    Provides centralized encryption/decryption services for the entire system.
    Integrates with memory engine security for consistent cryptographic operations.
    """

    def __init__(self):
        """Initialize system encryption.
        
        Sets up security manager with encryption enabled for system-wide use.
        """
        self.security_manager = None
        self._initialize_encryption()

    def _initialize_encryption(self):
        """Initialize encryption with proper configuration.
        
        Creates and configures security manager with encryption and PII detection enabled.
        
        Raises:
            Exception: If encryption initialization fails
        """
        try:
            # Create config with encryption enabled
            config = MemoryEngineConfig()
            config.encryption_enabled = True
            config.pii_detection_enabled = True

            self.security_manager = SecurityManager(config)
            logger.info("System encryption initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize system encryption: {e}")
            raise

    def encrypt_sensitive_data(self, data: str) -> bytes:
        """Encrypt sensitive data.
        
        Args:
            data: Plain text data to encrypt
            
        Returns:
            Encrypted data as bytes
            
        Raises:
            RuntimeError: If encryption is not initialized
        """
        if not self.security_manager:
            raise RuntimeError("Encryption not initialized")
        return self.security_manager.encrypt_data(data)

    def decrypt_sensitive_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data bytes to decrypt
            
        Returns:
            Decrypted plain text data
            
        Raises:
            RuntimeError: If encryption is not initialized
        """
        if not self.security_manager:
            raise RuntimeError("Encryption not initialized")
        return self.security_manager.decrypt_data(encrypted_data)

    def encrypt_config_value(self, value: str) -> str:
        """Encrypt a configuration value for storage.
        
        Automatically detects sensitive values based on common patterns
        and encrypts them for secure storage.
        
        Args:
            value: Configuration value to encrypt
            
        Returns:
            Encrypted value with 'encrypted:' prefix or original value
        """
        if not value or not isinstance(value, str):
            return value

        # Check if value looks like a secret (contains key, token, password, etc.)
        sensitive_indicators = ["key", "token", "password", "secret", "auth"]
        if any(indicator in value.lower() for indicator in sensitive_indicators):
            try:
                encrypted = self.encrypt_sensitive_data(value)
                return f"encrypted:{encrypted.hex()}"
            except Exception as e:
                logger.warning(f"Failed to encrypt config value: {e}")
                return value

        return value

    def decrypt_config_value(self, value: str) -> str:
        """Decrypt a configuration value.
        
        Detects encrypted values by 'encrypted:' prefix and decrypts them.
        
        Args:
            value: Configuration value (encrypted or plain)
            
        Returns:
            Decrypted value or original value if not encrypted
        """
        if not value or not isinstance(value, str):
            return value

        if value.startswith("encrypted:"):
            try:
                hex_data = value[10:]  # Remove "encrypted:" prefix
                encrypted_data = bytes.fromhex(hex_data)
                return self.decrypt_sensitive_data(encrypted_data)
            except Exception as e:
                logger.warning(f"Failed to decrypt config value: {e}")
                return value

        return value

    def secure_environment_variables(self) -> Dict[str, str]:
        """Get all environment variables with sensitive ones masked.
        
        Returns environment variables with sensitive values replaced
        with '[ENCRYPTED]' for secure logging and display.
        
        Returns:
            Dictionary of environment variables with sensitive values masked
        """
        secure_vars = {}

        for key, value in os.environ.items():
            if any(
                sensitive in key.lower()
                for sensitive in ["key", "token", "password", "secret"]
            ):
                secure_vars[key] = "[ENCRYPTED]"
            else:
                secure_vars[key] = value

        return secure_vars


# Global instance
_system_encryption = None


def get_system_encryption() -> SystemEncryption:
    """Get global system encryption instance.
    
    Returns:
        Singleton instance of SystemEncryption
    """
    global _system_encryption
    if _system_encryption is None:
        _system_encryption = SystemEncryption()
    return _system_encryption


def encrypt_sensitive(data: str) -> bytes:
    """Convenience function to encrypt sensitive data.
    
    Args:
        data: Plain text data to encrypt
        
    Returns:
        Encrypted data as bytes
    """
    return get_system_encryption().encrypt_sensitive_data(data)


def decrypt_sensitive(encrypted_data: bytes) -> str:
    """Convenience function to decrypt sensitive data.
    
    Args:
        encrypted_data: Encrypted data bytes to decrypt
        
    Returns:
        Decrypted plain text data
    """
    return get_system_encryption().decrypt_sensitive_data(encrypted_data)
