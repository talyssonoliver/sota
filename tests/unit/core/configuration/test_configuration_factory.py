"""
Tests for Configuration Factory

Validates the clean architecture configuration system including
environment-specific configuration and validation boundaries.
"""

import os
from unittest.mock import patch
from src.core.configuration import (
    ConfigurationFactory,
    EnvironmentConfiguration,
    ValidationConfiguration
)


class TestConfigurationFactory:
    """Test suite for ConfigurationFactory"""
    
    def setup_method(self):
        """Setup test environment"""
        # Reset any existing factory instance
        ConfigurationFactory._instance = None
        ConfigurationFactory._registry = None
    
    def test_factory_singleton_behavior(self):
        """Test that factory follows singleton pattern"""
        factory1 = ConfigurationFactory()
        factory2 = ConfigurationFactory()
        assert factory1 is factory2
    
    def test_default_providers_registration(self):
        """Test that default providers are registered"""
        factory = ConfigurationFactory()
        registry = factory.get_registry()
        
        # Check that default providers are registered
        providers = registry.list_providers()
        assert "environment" in providers
        assert "security" in providers
        assert "network" in providers
        
        # Check that default validator is registered
        validators = registry.list_validators()
        assert "default" in validators
    
    def test_environment_provider_functionality(self):
        """Test environment configuration provider"""
        factory = ConfigurationFactory()
        env_provider = factory.get_environment_provider()
        
        # Test basic configuration access
        api_url = env_provider.get_api_base_url()
        assert api_url is not None
        assert isinstance(api_url, str)
        assert api_url.startswith("http")
        
        # Test environment detection
        environment = env_provider.get_environment()
        assert environment in ["development", "testing", "production"]
    
    def test_security_provider_functionality(self):
        """Test security configuration provider"""
        factory = ConfigurationFactory()
        security_provider = factory.get_security_provider()
        
        # Test encryption config
        encryption_config = security_provider.get_encryption_config()
        assert "enabled" in encryption_config
        assert "algorithm" in encryption_config
        
        # Test authentication config
        auth_config = security_provider.get_authentication_config()
        assert "required" in auth_config
        assert "method" in auth_config
    
    def test_network_provider_functionality(self):
        """Test network configuration provider"""
        factory = ConfigurationFactory()
        network_provider = factory.get_network_provider()
        
        # Test API endpoints
        endpoints = network_provider.get_api_endpoints()
        assert "base" in endpoints
        assert "health" in endpoints
        assert "metrics" in endpoints
        
        # Test service URLs
        urls = network_provider.get_service_urls()
        assert "api" in urls
        assert "dashboard" in urls
        
        # Test timeout config
        timeouts = network_provider.get_timeout_config()
        assert "api_timeout" in timeouts
        assert isinstance(timeouts["api_timeout"], int)
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        factory = ConfigurationFactory()
        validator = factory.get_validator()
        
        # Test valid configuration
        valid_config = {
            "api": {
                "base_url": "http://localhost:5000",
                "timeout": 30,
                "retry_attempts": 3
            },
            "database": {
                "url": "sqlite:///test.db",
                "pool_size": 5
            },
            "security": {
                "encryption_enabled": True,
                "auth_required": True,
                "debug_mode": False
            },
            "monitoring": {
                "log_level": "INFO",
                "metrics_enabled": True
            }
        }
        
        result = validator.validate(valid_config)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_configuration_validation_errors(self):
        """Test configuration validation with errors"""
        factory = ConfigurationFactory()
        validator = factory.get_validator()
        
        # Test invalid configuration
        invalid_config = {
            "api": {
                "base_url": "invalid-url",  # Invalid URL format
                "timeout": -1,  # Invalid timeout
                "retry_attempts": 20  # Too many retries
            },
            "database": {
                "url": "",  # Empty URL
                "pool_size": 0  # Invalid pool size
            },
            "security": {
                "encryption_enabled": "not_a_boolean",  # Wrong type
                "auth_required": True,
                "debug_mode": False
            },
            "monitoring": {
                "log_level": "INVALID_LEVEL",  # Invalid log level
                "metrics_enabled": True
            }
        }
        
        result = validator.validate(invalid_config)
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    @patch.dict(os.environ, {"ENVIRONMENT": "testing"})
    def test_environment_specific_configuration(self):
        """Test environment-specific configuration"""
        # Reset factory to pick up environment change
        ConfigurationFactory._instance = None
        ConfigurationFactory._registry = None
        
        factory = ConfigurationFactory()
        env_provider = factory.get_environment_provider()
        
        assert env_provider.get_environment() == "testing"
        assert env_provider.is_testing() is True
        assert env_provider.is_development() is False
        assert env_provider.is_production() is False
    
    @patch.dict(os.environ, {"API_BASE_URL": "https://custom-api.com"})
    def test_environment_variable_overrides(self):
        """Test environment variable overrides"""
        # Reset factory to pick up environment changes
        ConfigurationFactory._instance = None
        ConfigurationFactory._registry = None
        
        factory = ConfigurationFactory()
        env_provider = factory.get_environment_provider()
        
        api_url = env_provider.get_api_base_url()
        assert api_url == "https://custom-api.com"
    
    def test_validation_comprehensive_coverage(self):
        """Test comprehensive validation coverage"""
        factory = ConfigurationFactory()
        results = factory.validate_all_configurations()
        
        # Should have validation results for all providers
        assert "environment" in results
        assert "security" in results
        assert "network" in results
        
        # Each result should have validation structure
        for provider_name, result in results.items():
            assert "is_valid" in result
            assert "errors" in result
            assert "warnings" in result
            assert isinstance(result["errors"], list)
            assert isinstance(result["warnings"], list)


class TestEnvironmentConfiguration:
    """Test suite for EnvironmentConfiguration"""
    
    def test_development_defaults(self):
        """Test development environment defaults"""
        config = EnvironmentConfiguration("development")
        
        assert config.is_development() is True
        assert config.get_api_base_url() == "http://localhost:5000"
        assert config.is_encryption_enabled() is False
        assert config.get_log_level() == "DEBUG"
    
    def test_production_defaults(self):
        """Test production environment defaults"""
        with patch.dict(os.environ, {"API_BASE_URL": "https://prod-api.com"}):
            config = EnvironmentConfiguration("production")
            
            assert config.is_production() is True
            assert config.is_encryption_enabled() is True
            assert config.get_log_level() == "INFO"
    
    def test_configuration_key_access(self):
        """Test configuration access with dot notation"""
        config = EnvironmentConfiguration("development")
        
        # Test valid key access
        api_timeout = config.get_configuration("api.timeout")
        assert isinstance(api_timeout, int)
        
        # Test invalid key access with default
        invalid_value = config.get_configuration("invalid.key", "default")
        assert invalid_value == "default"
    
    def test_configuration_reload(self):
        """Test configuration reload functionality"""
        config = EnvironmentConfiguration("development")
        
        # Get initial value
        initial_url = config.get_api_base_url()
        
        # Reload should work without errors
        config.reload()
        
        # Should get same value after reload
        reloaded_url = config.get_api_base_url()
        assert initial_url == reloaded_url


class TestValidationConfiguration:
    """Test suite for ValidationConfiguration"""
    
    def test_validation_rules_coverage(self):
        """Test that validation rules cover all expected sections"""
        validator = ValidationConfiguration()
        schema = validator.get_schema()
        
        # Check that all expected sections are in schema
        expected_sections = ["api", "dashboard", "database", "security", "monitoring"]
        for section in expected_sections:
            assert section in schema["properties"]
    
    def test_cross_section_validation(self):
        """Test cross-section validation logic"""
        validator = ValidationConfiguration()
        
        # Test configuration with potential CORS issues
        config_with_cors_issue = {
            "api": {"base_url": "http://api.example.com", "timeout": 30, "retry_attempts": 3},
            "dashboard": {"url": "http://dashboard.different.com", "refresh_interval": 30},
            "database": {"url": "sqlite:///test.db", "pool_size": 5},
            "security": {"encryption_enabled": True, "auth_required": True, "debug_mode": False},
            "monitoring": {"log_level": "INFO", "metrics_enabled": True}
        }
        
        result = validator.validate(config_with_cors_issue)
        # Should be valid but have warnings about CORS
        assert result.is_valid is True
        assert any("CORS" in warning for warning in result.warnings)
    
    def test_security_validation_warnings(self):
        """Test security-specific validation warnings"""
        validator = ValidationConfiguration()
        
        # Test insecure configuration
        insecure_config = {
            "api": {"base_url": "http://insecure-api.com", "timeout": 30},
            "database": {"url": "sqlite:///test.db"},
            "security": {
                "encryption_enabled": False,
                "auth_required": False,
                "debug_mode": True
            },
            "monitoring": {"log_level": "DEBUG"}
        }
        
        result = validator.validate(insecure_config)
        # Should have multiple security warnings
        assert len(result.warnings) >= 3
        assert any("encryption" in warning.lower() for warning in result.warnings)
        assert any("authentication" in warning.lower() for warning in result.warnings)
        assert any("debug" in warning.lower() for warning in result.warnings)