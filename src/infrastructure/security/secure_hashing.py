#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import hashlib
"""
Secure Hashing Utilities

Provides secure alternatives to weak hash functions like MD5.
Fixes Bandit B303 vulnerabilities for security-sensitive hashing.
"""

# import hashlib  # Consolidated to common_imports
from typing import Union


def get_partition_hash(data_key: str) -> str:
    """
    Generate a hash for data partitioning (non-security use).
    
    Uses MD5 with usedforsecurity=False to indicate this is not
    for security purposes, only for data distribution.
    
    Args:
        data_key: The key to hash for partitioning
        
    Returns:
        str: Hexadecimal hash string
    """
    # MD5 is acceptable for non-security purposes like partitioning
    # The usedforsecurity=False parameter tells Python this is not a security use
    return hashlib.md5(data_key.encode(), usedforsecurity=False).hexdigest()


def get_cache_key_hash(cache_key: str) -> str:
    """
    Generate a hash for cache key generation (non-security use).
    
    Uses MD5 with usedforsecurity=False for performance in caching scenarios.
    
    Args:
        cache_key: The key to hash for caching
        
    Returns:
        str: Hexadecimal hash string
    """
    return hashlib.md5(cache_key.encode(), usedforsecurity=False).hexdigest()


def get_secure_hash(data: Union[str, bytes]) -> str:
    """
    Generate a cryptographically secure hash for security-sensitive operations.
    
    Uses SHA-256 for actual security needs like:
    - Password hashing (though you should use bcrypt/scrypt/argon2 for passwords)
    - Data integrity verification
    - Digital signatures
    - Token generation
    
    Args:
        data: The data to hash securely
        
    Returns:
        str: Hexadecimal SHA-256 hash string
    """
    if isinstance(data, str):
        data = data.encode()
    
    return hashlib.sha256(data).hexdigest()


def get_content_hash(content: Union[str, bytes]) -> str:
    """
    Generate a hash for content deduplication or integrity checking.
    
    Uses SHA-256 for reliable content identification.
    
    Args:
        content: The content to hash
        
    Returns:
        str: Hexadecimal SHA-256 hash string
    """
    if isinstance(content, str):
        content = content.encode()
    
    return hashlib.sha256(content).hexdigest()


def verify_content_integrity(content: Union[str, bytes], expected_hash: str) -> bool:
    """
    Verify content integrity by comparing hashes.
    
    Args:
        content: The content to verify
        expected_hash: The expected SHA-256 hash
        
    Returns:
        bool: True if content matches the expected hash
    """
    actual_hash = get_content_hash(content)
    # Use constant-time comparison to prevent timing attacks
    return hashlib.compare_digest(actual_hash, expected_hash)


# Replacement functions for the vulnerable MD5 usages

def fix_partition_manager_hash(data_key: str) -> str:
    """
    Replacement for PartitionManager.get_partition_key hash generation.
    
    Original code:
        hash_value = hashlib.md5(data_key.encode()).hexdigest()
    
    Fixed code uses this function instead.
    """
    return get_partition_hash(data_key)


def fix_memory_storage_hash(data_key: str) -> str:
    """
    Replacement for memory storage hash generation.
    
    Fixes Bandit B303 warning about MD5 usage.
    """
    return get_cache_key_hash(data_key)


def fix_pattern_detector_hash(content: str) -> str:
    """
    Replacement for AI pattern detector hash generation.
    
    Since this is for pattern detection (deduplication), not security,
    we can use MD5 with usedforsecurity=False.
    """
    return get_cache_key_hash(content)


def fix_validation_history_hash(validation_data: str) -> str:
    """
    Replacement for validation history hash generation.
    
    Since this might be used for integrity checking, use SHA-256.
    """
    return get_content_hash(validation_data)


# Example usage in a patched PartitionManager
class SecurePartitionManager:
    """Example of how to use secure hashing in PartitionManager."""
    
    def get_partition_key(self, data_key: str) -> str:
        """
        Determine partition key for data using secure hashing.
        """
        # Use the secure partition hash function
        hash_value = get_partition_hash(data_key)
        partition_id = int(hash_value[:2], 16) % 16  # 16 partitions
        return f"partition_{partition_id:02d}"