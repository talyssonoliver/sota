
from src.infrastructure.utils.common_imports import dataclass
"""
Configuration Interfaces

Defines abstract interfaces for configuration management following
the Interface Segregation and Dependency Inversion principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
# from dataclasses import dataclass  # Consolidated to common_imports


@dataclass
class ConfigurationValidationResult:
    """Result of configuration validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class IConfigurationProvider(ABC):
    """Interface for configuration providers"""
    
    @abstractmethod
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        pass
    
    @abstractmethod
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        pass
    
    @abstractmethod
    def reload(self) -> None:
        """Reload configuration from source"""
        pass


class IConfigurationValidator(ABC):
    """Interface for configuration validation"""
    
    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> ConfigurationValidationResult:
        """Validate configuration data"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get validation schema"""
        pass


class IEnvironmentConfigurationProvider(IConfigurationProvider):
    """Interface for environment-specific configuration"""
    
    @abstractmethod
    def get_environment(self) -> str:
        """Get current environment name"""
        pass
    
    @abstractmethod
    def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """Get configuration for specific environment"""
        pass


class ISecurityConfigurationProvider(IConfigurationProvider):
    """Interface for security-related configuration"""
    
    @abstractmethod
    def get_encryption_config(self) -> Dict[str, Any]:
        """Get encryption configuration"""
        pass
    
    @abstractmethod
    def get_authentication_config(self) -> Dict[str, Any]:
        """Get authentication configuration"""
        pass
    
    @abstractmethod
    def get_api_security_config(self) -> Dict[str, Any]:
        """Get API security configuration"""
        pass


class INetworkConfigurationProvider(IConfigurationProvider):
    """Interface for network-related configuration"""
    
    @abstractmethod
    def get_api_endpoints(self) -> Dict[str, str]:
        """Get API endpoint configurations"""
        pass
    
    @abstractmethod
    def get_service_urls(self) -> Dict[str, str]:
        """Get service URL configurations"""
        pass
    
    @abstractmethod
    def get_timeout_config(self) -> Dict[str, int]:
        """Get timeout configurations"""
        pass