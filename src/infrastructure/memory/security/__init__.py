"""Unified memory platform - security module.

Provides security functionality for the memory platform including:
- Encryption and decryption capabilities
- Security policy management
- Thread-safe operations

Usage:
    from src.infrastructure.memory.security import SecurityManager, SecurityPolicy
    
    # Initialize security manager
    security = SecurityManager()
    policy = SecurityPolicy()
"""

try:
    from .encryption import (
        EncryptionManager,
        decrypt_data,
        encrypt_data,
    )
    from .security_manager import SecurityManager, SecurityPolicy
    from .thread_safety import (
        ThreadSafeMemory,
        get_thread_lock,
    )

    __all__ = [
        "SecurityManager", 
        "SecurityPolicy",
        "EncryptionManager",
        "encrypt_data",
        "decrypt_data",
        "ThreadSafeMemory",
        "get_thread_lock",
    ]
except ImportError:
    # Fallback for missing modules - provide minimal interface
    class SecurityManager:
        def __init__(self):
            pass
    
    class SecurityPolicy:
        def __init__(self):
            pass
    
    __all__ = ["SecurityManager", "SecurityPolicy"]
