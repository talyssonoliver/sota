"""
Mock Modules for Testing

Provides mock implementations for external dependencies that may not be
available during testing or in development environments.
"""

# Make pytest globally available in tests
try:
    import pytest
    __all__ = ['pytest']
except ImportError:
    __all__ = []
