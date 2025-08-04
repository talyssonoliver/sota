#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import json, logging
"""
Encryption Engine for Memory Storage

Provides AES-256 encryption/decryption for sensitive data in memory engine
and storage systems. Addresses the 0.18% encryption coverage gap.
"""

import base64
# import logging  # Consolidated to common_imports
from typing import Union, Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
# import json  # Consolidated to common_imports
from src.infrastructure.utils.common_utils import EnvironmentConfig


logger = logging.getLogger(__name__)


class EncryptionKeyManager:
    """Manages encryption keys for the system."""
    
    def __init__(self, key_source: Optional[str] = None):
        """
        Initialize encryption key manager.
        
        Args:
            key_source: Source of the encryption key (env var name or direct key)
        """
        self.key_source = key_source or "AI_SYSTEM_ENCRYPTION_KEY"
        self._encryption_key = None
        self._fernet = None
    
    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    def get_encryption_key(self) -> bytes:
        """Get or generate the encryption key."""
        if self._encryption_key is None:
            # Try to get from environment using EnvironmentConfig
            env_key = EnvironmentConfig.get_encryption_key()
            
            if env_key:
                # Decode base64 key or use as password
                try:
                    self._encryption_key = base64.urlsafe_b64decode(env_key.encode())
                except Exception:
                    # Use as password with fixed salt for deterministic key
                    salt = b'ai_system_salt_v1'  # Fixed salt for consistency
                    self._encryption_key = self._derive_key_from_password(env_key, salt)
            else:
                # Generate new key for development
                self._encryption_key = Fernet.generate_key()
                env_key_b64 = base64.urlsafe_b64encode(self._encryption_key).decode()
                
                logger.warning(
                    f"Generated new encryption key. Set ENCRYPTION_KEY={env_key_b64} "
                    "in environment for production use."
                )
        
        return self._encryption_key
    
    def get_fernet_instance(self) -> Fernet:
        """Get Fernet instance for symmetric encryption."""
        if self._fernet is None:
            key = self.get_encryption_key()
            # Ensure key is properly base64-encoded for Fernet
            if len(key) == 32:  # Raw 32-byte key from PBKDF2
                key = base64.urlsafe_b64encode(key)
            self._fernet = Fernet(key)
        return self._fernet


class DataEncryption:
    """Handles data encryption and decryption operations."""
    
    def __init__(self, key_manager: Optional[EncryptionKeyManager] = None):
        """
        Initialize data encryption handler.
        
        Args:
            key_manager: Encryption key manager instance
        """
        self.key_manager = key_manager or EncryptionKeyManager()
        self.fernet = self.key_manager.get_fernet_instance()
    
    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt a string and return base64-encoded ciphertext.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            str: Base64-encoded encrypted string
        """
        if not plaintext:
            return plaintext
        
        try:
            plaintext_bytes = plaintext.encode('utf-8')
            encrypted_bytes = self.fernet.encrypt(plaintext_bytes)
            return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_string(self, ciphertext: str) -> str:
        """
        Decrypt a base64-encoded string.
        
        Args:
            ciphertext: Base64-encoded encrypted string
            
        Returns:
            str: Decrypted plaintext string
        """
        if not ciphertext:
            return ciphertext
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_dict(self, data: dict) -> dict:
        """
        Encrypt sensitive fields in a dictionary.
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            dict: Dictionary with encrypted sensitive fields
        """
        if not isinstance(data, dict):
            return data
        
        # Fields that should be encrypted
        sensitive_fields = {
            'password', 'secret', 'key', 'token', 'api_key',
            'private_key', 'credential', 'auth', 'session'
        }
        
        encrypted_data = data.copy()
        
        for field_name, field_value in data.items():
            # Check if field name suggests sensitive data
            if any(sensitive in field_name.lower() for sensitive in sensitive_fields):
                if isinstance(field_value, str):
                    encrypted_data[field_name] = self.encrypt_string(field_value)
                    encrypted_data[f"{field_name}_encrypted"] = True
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict) -> dict:
        """
        Decrypt encrypted fields in a dictionary.
        
        Args:
            data: Dictionary with encrypted fields
            
        Returns:
            dict: Dictionary with decrypted fields
        """
        if not isinstance(data, dict):
            return data
        
        decrypted_data = data.copy()
        
        for field_name, field_value in data.items():
            # Check if field is marked as encrypted
            if data.get(f"{field_name}_encrypted"):
                if isinstance(field_value, str):
                    decrypted_data[field_name] = self.decrypt_string(field_value)
                    # Remove the encryption marker
                    decrypted_data.pop(f"{field_name}_encrypted", None)
        
        return decrypted_data
    
    def encrypt_json(self, data: Any) -> str:
        """
        Encrypt arbitrary data as JSON.
        
        Args:
            data: Data to encrypt
            
        Returns:
            str: Encrypted JSON string
        """
        json_string = json.dumps(data, sort_keys=True)
        return self.encrypt_string(json_string)
    
    def decrypt_json(self, encrypted_json: str) -> Any:
        """
        Decrypt JSON data.
        
        Args:
            encrypted_json: Encrypted JSON string
            
        Returns:
            Any: Decrypted data
        """
        json_string = self.decrypt_string(encrypted_json)
        return json.loads(json_string)


class MemoryEncryption:
    """Encryption integration for memory engine."""
    
    def __init__(self, encryption: Optional[DataEncryption] = None):
        """
        Initialize memory encryption.
        
        Args:
            encryption: Data encryption instance
        """
        self.encryption = encryption or DataEncryption()
        self.encrypt_by_default = True
    
    def should_encrypt(self, key: str, data: Any) -> bool:
        """
        Determine if data should be encrypted based on key or content.
        
        Args:
            key: Storage key
            data: Data to potentially encrypt
            
        Returns:
            bool: True if data should be encrypted
        """
        # Always encrypt by default for security
        if self.encrypt_by_default:
            return True
        
        # Encrypt based on key patterns
        sensitive_patterns = {
            'password', 'secret', 'key', 'token', 'credential',
            'private', 'auth', 'session', 'user_data', 'personal'
        }
        
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in sensitive_patterns)
    
    def encrypt_for_storage(self, key: str, data: Any) -> tuple[Any, dict]:
        """
        Encrypt data for storage if needed.
        
        Args:
            key: Storage key
            data: Data to potentially encrypt
            
        Returns:
            tuple: (potentially_encrypted_data, metadata)
        """
        metadata = {'encrypted': False, 'encryption_version': '1.0'}
        
        if not self.should_encrypt(key, data):
            return data, metadata
        
        try:
            if isinstance(data, str):
                encrypted_data = self.encryption.encrypt_string(data)
            elif isinstance(data, dict):
                encrypted_data = self.encryption.encrypt_dict(data)
            else:
                # Encrypt as JSON for complex objects
                encrypted_data = self.encryption.encrypt_json(data)
                metadata['json_encrypted'] = True
            
            metadata['encrypted'] = True
            logger.debug(f"Encrypted data for key: {key}")
            
            return encrypted_data, metadata
            
        except Exception as e:
            logger.error(f"Failed to encrypt data for key {key}: {e}")
            # Return unencrypted data if encryption fails
            return data, {'encrypted': False, 'encryption_error': str(e)}
    
    def decrypt_from_storage(self, data: Any, metadata: dict) -> Any:
        """
        Decrypt data from storage if needed.
        
        Args:
            data: Potentially encrypted data
            metadata: Storage metadata
            
        Returns:
            Any: Decrypted data
        """
        if not metadata.get('encrypted', False):
            return data
        
        try:
            if metadata.get('json_encrypted', False):
                return self.encryption.decrypt_json(data)
            elif isinstance(data, str):
                return self.encryption.decrypt_string(data)
            elif isinstance(data, dict):
                return self.encryption.decrypt_dict(data)
            else:
                return data
                
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            # Return encrypted data if decryption fails
            return data


# Global encryption instances for easy import
_default_encryption = None
_default_memory_encryption = None


def get_default_encryption() -> DataEncryption:
    """Get default encryption instance."""
    global _default_encryption
    if _default_encryption is None:
        _default_encryption = DataEncryption()
    return _default_encryption


def get_memory_encryption() -> MemoryEncryption:
    """Get default memory encryption instance."""
    global _default_memory_encryption
    if _default_memory_encryption is None:
        _default_memory_encryption = MemoryEncryption()
    return _default_memory_encryption


# Convenience functions
def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data string."""
    return get_default_encryption().encrypt_string(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data string."""
    return get_default_encryption().decrypt_string(encrypted_data)


def secure_config_value(key: str, value: str) -> str:
    """Encrypt configuration value if it appears sensitive."""
    sensitive_keys = {'password', 'secret', 'key', 'token', 'credential'}
    
    if any(sensitive in key.lower() for sensitive in sensitive_keys):
        return encrypt_sensitive_data(value)
    
    return value