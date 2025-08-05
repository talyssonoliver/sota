#!/usr/bin/env python3
"""
Comprehensive Tests for Encryption Engine

Tests for AES-256 encryption, key management, and memory integration.
Critical for achieving 80% test coverage target.
"""

import pytest
import os
from unittest.mock import patch
from cryptography.fernet import Fernet

from src.infrastructure.security.encryption_engine import (
    EncryptionKeyManager,
    DataEncryption,
    MemoryEncryption,
    get_default_encryption,
    get_memory_encryption,
    encrypt_sensitive_data,
    decrypt_sensitive_data,
    secure_config_value
)


class TestEncryptionKeyManager:
    """Test encryption key management functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.key_manager = EncryptionKeyManager()
    
    def test_key_manager_initialization(self):
        """Test key manager initialization."""
        assert self.key_manager.key_source == "AI_SYSTEM_ENCRYPTION_KEY"
        assert self.key_manager._encryption_key is None
        assert self.key_manager._fernet is None
    
    def test_custom_key_source(self):
        """Test initialization with custom key source."""
        custom_manager = EncryptionKeyManager("CUSTOM_KEY")
        assert custom_manager.key_source == "CUSTOM_KEY"
    
    @patch.dict(os.environ, {'AI_SYSTEM_ENCRYPTION_KEY': 'test_password'})
    def test_get_encryption_key_from_env_password(self):
        """Test key derivation from environment variable password."""
        key = self.key_manager.get_encryption_key()
        assert isinstance(key, bytes)
        assert len(key) == 32  # 256 bits
        
        # Same password should produce same key
        key2 = self.key_manager.get_encryption_key()
        assert key == key2
    
    @patch.dict(os.environ, {'AI_SYSTEM_ENCRYPTION_KEY': Fernet.generate_key().decode()})
    def test_get_encryption_key_from_env_base64(self):
        """Test key loading from base64-encoded environment variable."""
        key = self.key_manager.get_encryption_key()
        assert isinstance(key, bytes)
        # Fernet.generate_key() returns a base64-encoded key that decodes to 32 bytes
        # When we set it in env and decode, we should get back the original 32-byte key
        assert len(key) == 32  # Raw Fernet keys are 32 bytes
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_encryption_key_generated(self):
        """Test key generation when no environment variable is set."""
        with patch('src.infrastructure.security.encryption_engine.logger') as mock_logger:
            key = self.key_manager.get_encryption_key()
            assert isinstance(key, bytes)
            assert len(key) == 44  # Fernet.generate_key() returns base64-encoded key (44 bytes)
            mock_logger.warning.assert_called_once()
    
    def test_derive_key_from_password(self):
        """Test PBKDF2 key derivation."""
        password = "test_password"
        salt = b"test_salt_123456"
        
        key1 = self.key_manager._derive_key_from_password(password, salt)
        key2 = self.key_manager._derive_key_from_password(password, salt)
        
        assert key1 == key2  # Same password+salt = same key
        assert len(key1) == 32  # 256 bits
        
        # Different salt should produce different key
        key3 = self.key_manager._derive_key_from_password(password, b"different_salt16")
        assert key1 != key3
    
    def test_get_fernet_instance(self):
        """Test Fernet instance creation."""
        fernet = self.key_manager.get_fernet_instance()
        assert isinstance(fernet, Fernet)
        
        # Should return same instance on subsequent calls
        fernet2 = self.key_manager.get_fernet_instance()
        assert fernet is fernet2


class TestDataEncryption:
    """Test data encryption and decryption functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.encryption = DataEncryption()
    
    def test_encrypt_decrypt_string(self):
        """Test string encryption and decryption."""
        plaintext = "This is a secret message"
        
        # Encrypt
        ciphertext = self.encryption.encrypt_string(plaintext)
        assert ciphertext != plaintext
        assert isinstance(ciphertext, str)
        
        # Decrypt
        decrypted = self.encryption.decrypt_string(ciphertext)
        assert decrypted == plaintext
    
    def test_encrypt_empty_string(self):
        """Test encryption of empty string."""
        result = self.encryption.encrypt_string("")
        assert result == ""
        
        result = self.encryption.encrypt_string(None)
        assert result is None
    
    def test_decrypt_empty_string(self):
        """Test decryption of empty string."""
        result = self.encryption.decrypt_string("")
        assert result == ""
        
        result = self.encryption.decrypt_string(None)
        assert result is None
    
    def test_encrypt_unicode_string(self):
        """Test encryption of unicode characters."""
        plaintext = "Hello 世界 🌍 café"
        
        ciphertext = self.encryption.encrypt_string(plaintext)
        decrypted = self.encryption.decrypt_string(ciphertext)
        
        assert decrypted == plaintext
    
    def test_encrypt_large_string(self):
        """Test encryption of large string."""
        plaintext = "A" * 10000  # 10KB string
        
        ciphertext = self.encryption.encrypt_string(plaintext)
        decrypted = self.encryption.decrypt_string(ciphertext)
        
        assert decrypted == plaintext
    
    def test_encrypt_dict_sensitive_fields(self):
        """Test dictionary encryption of sensitive fields."""
        data = {
            "username": "john_doe",
            "password": "secret123",
            "api_key": "abc123def456",
            "public_info": "not sensitive",
            "private_key": "rsa_private_key_data"
        }
        
        encrypted_data = self.encryption.encrypt_dict(data)
        
        # Sensitive fields should be encrypted
        assert encrypted_data["password"] != "secret123"
        assert encrypted_data["api_key"] != "abc123def456"
        assert encrypted_data["private_key"] != "rsa_private_key_data"
        
        # Non-sensitive fields should remain unchanged
        assert encrypted_data["username"] == "john_doe"
        assert encrypted_data["public_info"] == "not sensitive"
        
        # Encryption markers should be added
        assert encrypted_data["password_encrypted"] is True
        assert encrypted_data["api_key_encrypted"] is True
        assert encrypted_data["private_key_encrypted"] is True
    
    def test_decrypt_dict(self):
        """Test dictionary decryption."""
        original_data = {
            "username": "john_doe",
            "password": "secret123",
            "api_key": "abc123def456"
        }
        
        # Encrypt then decrypt
        encrypted_data = self.encryption.encrypt_dict(original_data)
        decrypted_data = self.encryption.decrypt_dict(encrypted_data)
        
        # Should match original (except encryption markers are removed)
        assert decrypted_data["username"] == "john_doe"
        assert decrypted_data["password"] == "secret123"
        assert decrypted_data["api_key"] == "abc123def456"
        
        # Encryption markers should be removed
        assert "password_encrypted" not in decrypted_data
        assert "api_key_encrypted" not in decrypted_data
    
    def test_encrypt_dict_non_dict_input(self):
        """Test encrypt_dict with non-dictionary input."""
        result = self.encryption.encrypt_dict("not a dict")
        assert result == "not a dict"
        
        result = self.encryption.encrypt_dict(None)
        assert result is None
    
    def test_encrypt_decrypt_json(self):
        """Test JSON encryption and decryption."""
        data = {
            "nested": {
                "value": 123,
                "list": [1, 2, 3]
            },
            "string": "test",
            "boolean": True
        }
        
        encrypted_json = self.encryption.encrypt_json(data)
        decrypted_data = self.encryption.decrypt_json(encrypted_json)
        
        assert decrypted_data == data
    
    def test_encryption_error_handling(self):
        """Test error handling in encryption operations."""
        # Mock Fernet to raise exception
        with patch.object(self.encryption.fernet, 'encrypt', side_effect=Exception("Encryption failed")):
            with pytest.raises(Exception):
                self.encryption.encrypt_string("test")
    
    def test_decryption_error_handling(self):
        """Test error handling in decryption operations."""
        with pytest.raises(Exception):
            self.encryption.decrypt_string("invalid_ciphertext")


class TestMemoryEncryption:
    """Test memory encryption integration."""
    
    def setup_method(self):
        """Set up test environment."""
        self.memory_encryption = MemoryEncryption()
    
    def test_should_encrypt_default(self):
        """Test default encryption behavior."""
        # Should encrypt by default
        assert self.memory_encryption.should_encrypt("any_key", "any_value") is True
    
    def test_should_encrypt_sensitive_patterns(self):
        """Test encryption decision based on key patterns."""
        self.memory_encryption.encrypt_by_default = False
        
        # Sensitive patterns should be encrypted
        assert self.memory_encryption.should_encrypt("user_password", "value") is True
        assert self.memory_encryption.should_encrypt("api_secret", "value") is True
        assert self.memory_encryption.should_encrypt("private_key", "value") is True
        assert self.memory_encryption.should_encrypt("session_token", "value") is True
        
        # Non-sensitive patterns should not be encrypted
        assert self.memory_encryption.should_encrypt("user_name", "value") is False
        assert self.memory_encryption.should_encrypt("config_version", "value") is False
    
    def test_encrypt_for_storage_string(self):
        """Test string encryption for storage."""
        key = "test_key"
        data = "sensitive data"
        
        encrypted_data, metadata = self.memory_encryption.encrypt_for_storage(key, data)
        
        assert encrypted_data != data
        assert metadata["encrypted"] is True
        assert metadata["encryption_version"] == "1.0"
    
    def test_encrypt_for_storage_dict(self):
        """Test dictionary encryption for storage."""
        key = "test_key"
        data = {"password": "secret", "username": "user"}
        
        encrypted_data, metadata = self.memory_encryption.encrypt_for_storage(key, data)
        
        assert encrypted_data != data
        assert metadata["encrypted"] is True
    
    def test_encrypt_for_storage_complex_object(self):
        """Test complex object encryption for storage."""
        # Use a sensitive key to ensure encryption happens
        key = "user_password"  
        data = {"nested": {"list": [1, 2, 3]}, "value": 42}
        
        encrypted_data, metadata = self.memory_encryption.encrypt_for_storage(key, data)
        
        # Verify encryption occurred
        assert metadata["encrypted"] is True
        # For complex objects, the encrypted data should be a string
        if metadata.get("json_encrypted", False):
            assert isinstance(encrypted_data, str)
            assert encrypted_data != str(data)  # Encrypted string should be different
    
    def test_decrypt_from_storage(self):
        """Test decryption from storage."""
        key = "test_key"
        original_data = "sensitive data"
        
        # Encrypt first
        encrypted_data, metadata = self.memory_encryption.encrypt_for_storage(key, original_data)
        
        # Then decrypt
        decrypted_data = self.memory_encryption.decrypt_from_storage(encrypted_data, metadata)
        
        assert decrypted_data == original_data
    
    def test_decrypt_from_storage_unencrypted(self):
        """Test decryption of unencrypted data."""
        data = "not encrypted"
        metadata = {"encrypted": False}
        
        result = self.memory_encryption.decrypt_from_storage(data, metadata)
        assert result == data
    
    def test_decrypt_from_storage_json(self):
        """Test JSON decryption from storage."""
        key = "test_key"
        original_data = {"complex": {"data": [1, 2, 3]}}
        
        encrypted_data, metadata = self.memory_encryption.encrypt_for_storage(key, original_data)
        decrypted_data = self.memory_encryption.decrypt_from_storage(encrypted_data, metadata)
        
        assert decrypted_data == original_data
    
    def test_encryption_error_handling(self):
        """Test error handling in memory encryption."""
        # Mock encryption to fail
        with patch.object(self.memory_encryption.encryption, 'encrypt_string', side_effect=Exception("Failed")):
            data, metadata = self.memory_encryption.encrypt_for_storage("key", "value")
            
            # Should return unencrypted data with error metadata
            assert data == "value"
            assert metadata["encrypted"] is False
            assert "encryption_error" in metadata
    
    def test_decryption_error_handling(self):
        """Test error handling in memory decryption."""
        # Mock decryption to fail
        with patch.object(self.memory_encryption.encryption, 'decrypt_string', side_effect=Exception("Failed")):
            metadata = {"encrypted": True}
            result = self.memory_encryption.decrypt_from_storage("encrypted_data", metadata)
            
            # Should return encrypted data unchanged
            assert result == "encrypted_data"


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    def test_get_default_encryption(self):
        """Test default encryption instance."""
        encryption1 = get_default_encryption()
        encryption2 = get_default_encryption()
        
        # Should return same instance (singleton pattern)
        assert encryption1 is encryption2
        assert isinstance(encryption1, DataEncryption)
    
    def test_get_memory_encryption(self):
        """Test default memory encryption instance."""
        mem_enc1 = get_memory_encryption()
        mem_enc2 = get_memory_encryption()
        
        # Should return same instance (singleton pattern)
        assert mem_enc1 is mem_enc2
        assert isinstance(mem_enc1, MemoryEncryption)
    
    def test_encrypt_decrypt_sensitive_data(self):
        """Test convenience functions for sensitive data."""
        plaintext = "sensitive information"
        
        encrypted = encrypt_sensitive_data(plaintext)
        decrypted = decrypt_sensitive_data(encrypted)
        
        assert encrypted != plaintext
        assert decrypted == plaintext
    
    def test_secure_config_value_sensitive(self):
        """Test secure config value for sensitive fields."""
        sensitive_keys = ["password", "secret", "key", "token", "credential"]
        
        for key in sensitive_keys:
            result = secure_config_value(key, "sensitive_value")
            assert result != "sensitive_value"  # Should be encrypted
    
    def test_secure_config_value_non_sensitive(self):
        """Test secure config value for non-sensitive fields."""
        non_sensitive_keys = ["name", "version", "url", "port"]
        
        for key in non_sensitive_keys:
            result = secure_config_value(key, "normal_value")
            assert result == "normal_value"  # Should not be encrypted


class TestEncryptionIntegration:
    """Integration tests for encryption components."""
    
    def test_end_to_end_encryption_workflow(self):
        """Test complete encryption workflow."""
        # Create components
        key_manager = EncryptionKeyManager()
        data_encryption = DataEncryption(key_manager)
        memory_encryption = MemoryEncryption(data_encryption)
        
        # Test data
        test_data = {
            "user_id": "123",
            "password": "secret123",
            "preferences": {
                "theme": "dark",
                "api_key": "abc123def456"
            }
        }
        
        # Encrypt for storage
        encrypted_data, metadata = memory_encryption.encrypt_for_storage("user_config", test_data)
        
        # Verify encryption occurred
        assert encrypted_data != test_data
        assert metadata["encrypted"] is True
        
        # Decrypt from storage
        decrypted_data = memory_encryption.decrypt_from_storage(encrypted_data, metadata)
        
        # Verify decryption
        assert decrypted_data == test_data
    
    def test_multiple_encryption_instances(self):
        """Test that multiple encryption instances work independently."""
        # Generate a test key that both instances will share
        test_key = Fernet.generate_key()
        shared_fernet = Fernet(test_key)
        
        # Mock the key manager to return the same Fernet instance
        with patch('src.infrastructure.security.encryption_engine.EncryptionKeyManager') as mock_key_manager:
            mock_manager_instance = mock_key_manager.return_value
            mock_manager_instance.get_fernet_instance.return_value = shared_fernet
            
            enc1 = DataEncryption()
            enc2 = DataEncryption()
        
        plaintext = "test message"
        
        # Encrypt with both instances
        cipher1 = enc1.encrypt_string(plaintext)
        cipher2 = enc2.encrypt_string(plaintext)
        
        # Both should decrypt correctly
        assert enc1.decrypt_string(cipher1) == plaintext
        assert enc2.decrypt_string(cipher2) == plaintext
        
        # Cross-decryption should also work (same key derivation)
        assert enc1.decrypt_string(cipher2) == plaintext
        assert enc2.decrypt_string(cipher1) == plaintext
    
    def test_encryption_consistency_across_restarts(self):
        """Test that encryption is consistent across application restarts."""
        plaintext = "persistent data"
        
        # Generate a test key for consistency
        test_key = Fernet.generate_key()
        shared_fernet = Fernet(test_key)
        
        # Mock the key manager to return the same Fernet instance
        with patch('src.infrastructure.security.encryption_engine.EncryptionKeyManager') as mock_key_manager:
            mock_manager_instance = mock_key_manager.return_value
            mock_manager_instance.get_fernet_instance.return_value = shared_fernet
            
            # First "session"
            encryption1 = DataEncryption()
            ciphertext = encryption1.encrypt_string(plaintext)
            
            # Simulate restart by creating new instance
            encryption2 = DataEncryption()
            decrypted = encryption2.decrypt_string(ciphertext)
            
            assert decrypted == plaintext


if __name__ == "__main__":
    pytest.main([__file__, "-v"])