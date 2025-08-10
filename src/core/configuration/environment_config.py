
from src.infrastructure.utils.common_imports import dataclass, logging, os
"""
Environment Configuration

Manages environment-specific configuration with proper validation and defaults.
Eliminates hardcoded values by providing environment-aware configuration.
"""

# import os  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
from typing import Dict, Any, Optional
# from dataclasses import dataclass  # Consolidated to common_imports
from .config_interfaces import IEnvironmentConfigurationProvider

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentDefaults:
    """Default configuration values for different environments"""
    
    # Development defaults
    development: Dict[str, Any] = None
    
    # Testing defaults
    testing: Dict[str, Any] = None
    
    # Production defaults
    production: Dict[str, Any] = None
    
    def __post_init__(self):
        self.development = {
            "api": {
                "base_url": "http://localhost:5000",
                "timeout": 30,
                "retry_attempts": 3
            },
            "dashboard": {
                "url": "http://localhost:5000/dashboard",
                "refresh_interval": 5
            },
            "database": {
                "url": "sqlite:///dev.db",
                "pool_size": 5,
                "max_overflow": 10
            },
            "security": {
                "encryption_enabled": False,
                "auth_required": False,
                "debug_mode": True
            },
            "monitoring": {
                "metrics_enabled": True,
                "log_level": "DEBUG"
            }
        }
        
        self.testing = {
            "api": {
                "base_url": "http://localhost:5001",
                "timeout": 10,
                "retry_attempts": 1
            },
            "dashboard": {
                "url": "http://localhost:5001/dashboard",
                "refresh_interval": 1
            },
            "database": {
                "url": "sqlite:///test.db",
                "pool_size": 2,
                "max_overflow": 5
            },
            "security": {
                "encryption_enabled": True,
                "auth_required": True,
                "debug_mode": False
            },
            "monitoring": {
                "metrics_enabled": False,
                "log_level": "WARNING"
            }
        }
        
        self.production = {
            "api": {
                "base_url": os.getenv("API_BASE_URL", "https://api.production.com"),
                "timeout": 60,
                "retry_attempts": 5
            },
            "dashboard": {
                "url": os.getenv("DASHBOARD_URL", "https://dashboard.production.com"),
                "refresh_interval": 30
            },
            "database": {
                "url": os.getenv("DATABASE_URL", "postgresql://prod-db:5432/aiSystem"),
                "pool_size": 20,
                "max_overflow": 50
            },
            "security": {
                "encryption_enabled": True,
                "auth_required": True,
                "debug_mode": False
            },
            "monitoring": {
                "metrics_enabled": True,
                "log_level": "INFO"
            }
        }


class EnvironmentConfiguration(IEnvironmentConfigurationProvider):
    """Environment-aware configuration provider"""
    
    def __init__(self, environment: Optional[str] = None):
        """Initialize environment configuration
        
        Args:
            environment: Environment name (development, testing, production)
                        If None, will be determined from environment variables
        """
        self._environment = environment or self._detect_environment()
        self._defaults = EnvironmentDefaults()
        self._config_cache: Dict[str, Any] = {}
        self._load_configuration()
    
    def _detect_environment(self) -> str:
        """Detect environment from environment variables"""
        env = os.getenv("ENVIRONMENT", "").lower()
        if env in ["development", "dev"]:
            return "development"
        elif env in ["testing", "test"]:
            return "testing"
        elif env in ["production", "prod"]:
            return "production"
        else:
            # Default to development if not specified
            logger.warning(f"Unknown environment '{env}', defaulting to development")
            return "development"
    
    def _load_configuration(self):
        """Load configuration for current environment"""
        if self._environment == "development":
            self._config_cache = self._defaults.development.copy()
        elif self._environment == "testing":
            self._config_cache = self._defaults.testing.copy()
        elif self._environment == "production":
            self._config_cache = self._defaults.production.copy()
        else:
            raise ValueError(f"Unknown environment: {self._environment}")
        
        # Override with environment variables
        self._apply_environment_overrides()
        
        logger.info(f"Loaded configuration for environment: {self._environment}")
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides"""
        # API configuration overrides
        if api_url := os.getenv("API_BASE_URL"):
            self._config_cache["api"]["base_url"] = api_url
        
        if api_timeout := os.getenv("API_TIMEOUT"):
            try:
                self._config_cache["api"]["timeout"] = int(api_timeout)
            except ValueError:
                logger.warning(f"Invalid API_TIMEOUT value: {api_timeout}")
        
        # Dashboard configuration overrides
        if dashboard_url := os.getenv("DASHBOARD_URL"):
            self._config_cache["dashboard"]["url"] = dashboard_url
        
        # Database configuration overrides
        if db_url := os.getenv("DATABASE_URL"):
            self._config_cache["database"]["url"] = db_url
        
        # Security configuration overrides
        if encryption_enabled := os.getenv("ENCRYPTION_ENABLED"):
            self._config_cache["security"]["encryption_enabled"] = encryption_enabled.lower() == "true"
        
        # Monitoring configuration overrides
        if log_level := os.getenv("LOG_LEVEL"):
            self._config_cache["monitoring"]["log_level"] = log_level.upper()
    
    def get_environment(self) -> str:
        """Get current environment name"""
        return self._environment
    
    def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """Get configuration for specific environment"""
        if environment == "development":
            return self._defaults.development
        elif environment == "testing":
            return self._defaults.testing
        elif environment == "production":
            return self._defaults.production
        else:
            raise ValueError(f"Unknown environment: {environment}")
    
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split(".")
        value = self._config_cache
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            logger.warning(f"Configuration key not found: {key}")
            return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self._config_cache.get(section, {})
    
    def reload(self) -> None:
        """Reload configuration from source"""
        self._config_cache.clear()
        self._load_configuration()
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self._environment == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self._environment == "testing"
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self._environment == "production"
    
    def get_api_base_url(self) -> str:
        """Get API base URL for current environment"""
        return self.get_configuration("api.base_url", "http://localhost:5000")
    
    def get_dashboard_url(self) -> str:
        """Get dashboard URL for current environment"""
        return self.get_configuration("dashboard.url", "http://localhost:5000/dashboard")
    
    def get_database_url(self) -> str:
        """Get database URL for current environment"""
        return self.get_configuration("database.url", "sqlite:///default.db")
    
    def get_api_timeout(self) -> int:
        """Get API timeout configuration"""
        return self.get_configuration("api.timeout", 30)
    
    def is_encryption_enabled(self) -> bool:
        """Check if encryption is enabled"""
        return self.get_configuration("security.encryption_enabled", False)
    
    def is_auth_required(self) -> bool:
        """Check if authentication is required"""
        return self.get_configuration("security.auth_required", False)
    
    def get_log_level(self) -> str:
        """Get logging level"""
        return self.get_configuration("monitoring.log_level", "INFO")