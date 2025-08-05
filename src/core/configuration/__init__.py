"""
Core Configuration Module

This module provides clean architecture-compliant configuration management
following the dependency inversion principle and separation of concerns.
"""

from .config_factory import ConfigurationFactory, get_configuration_factory
from .config_interfaces import IConfigurationProvider, IConfigurationValidator
from .environment_config import EnvironmentConfiguration
from .validation_config import ValidationConfiguration

__all__ = [
    "ConfigurationFactory",
    "get_configuration_factory",
    "IConfigurationProvider", 
    "IConfigurationValidator",
    "EnvironmentConfiguration",
    "ValidationConfiguration"
]