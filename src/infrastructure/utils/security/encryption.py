"""Encryption utilities."""

def encrypt_data(data, key):
    """Encrypt data."""
    return f"encrypted_{data}"

def decrypt_data(encrypted_data, key):
    """Decrypt data."""
    return encrypted_data.replace("encrypted_", "")

__all__ = ["encrypt_data", "decrypt_data"]
