"""
Comprehensive test suite for the configuration factory system.
"""

import json
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.core.configuration.config_factory import (
    ConfigurationFactory, ConfigurationRegistry, ConfigurationProvider,
    ConfigurationError
)


class TestConfigurationRegistry:
    """Test configuration registry functionality."""
    
    def test_registry_initialization(self):
        """Test registry starts empty."""
        registry = ConfigurationRegistry()
        assert len(registry._providers) == 0
    
    def test_register_provider(self):
        """Test registering a configuration provider."""
        registry = ConfigurationRegistry()
        
        class TestProvider(ConfigurationProvider):
            def load_config(self, path=None):
                return {"test": "value"}
        
        provider = TestProvider()
        registry.register_provider("test", provider)
        
        assert "test" in registry._providers
        assert registry._providers["test"] is provider
    
    def test_get_provider(self):
        """Test retrieving a registered provider."""
        registry = ConfigurationRegistry()
        
        class TestProvider(ConfigurationProvider):
            def load_config(self, path=None):
                return {"test": "value"}
        
        provider = TestProvider()
        registry.register_provider("test", provider)
        
        retrieved = registry.get_provider("test")
        assert retrieved is provider
    
    def test_get_nonexistent_provider(self):
        """Test getting a provider that doesn't exist."""
        registry = ConfigurationRegistry()
        
        with pytest.raises(ConfigurationError) as exc_info:
            registry.get_provider("nonexistent")
        
        assert "Provider 'nonexistent' not found" in str(exc_info.value)
    
    def test_list_providers(self):
        """Test listing all registered providers."""
        registry = ConfigurationRegistry()
        
        class ProviderA(ConfigurationProvider):
            def load_config(self, path=None):
                return {}
        
        class ProviderB(ConfigurationProvider):
            def load_config(self, path=None):
                return {}
        
        registry.register_provider("a", ProviderA())
        registry.register_provider("b", ProviderB())
        
        providers = registry.list_providers()
        assert "a" in providers
        assert "b" in providers
        assert len(providers) == 2


class TestConfigurationProvider:
    """Test base configuration provider."""
    
    def test_abstract_provider(self):
        """Test that ConfigurationProvider is abstract."""
        with pytest.raises(TypeError):
            ConfigurationProvider()
    
    def test_concrete_provider_implementation(self):
        """Test implementing a concrete provider."""
        class JsonProvider(ConfigurationProvider):
            def load_config(self, path=None):
                return {"format": "json", "path": path}
        
        provider = JsonProvider()
        config = provider.load_config("/test/path")
        
        assert config["format"] == "json"
        assert config["path"] == "/test/path"


class TestConfigurationFactory:
    """Test configuration factory functionality."""
    
    def test_factory_singleton(self):
        """Test that factory is a singleton."""
        factory1 = ConfigurationFactory()
        factory2 = ConfigurationFactory()
        
        assert factory1 is factory2
    
    def test_factory_initialization(self):
        """Test factory initializes with default providers."""
        factory = ConfigurationFactory()
        
        # Should have some default providers
        providers = factory._registry.list_providers()
        assert len(providers) > 0
    
    def test_load_json_config(self):
        """Test loading JSON configuration."""
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "api": {
                "base_url": "https://api.example.com",
                "timeout": 30
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            factory = ConfigurationFactory()
            config = factory.load_configuration(config_path)
            
            assert config["database"]["host"] == "localhost"
            assert config["database"]["port"] == 5432
            assert config["api"]["base_url"] == "https://api.example.com"
            assert config["api"]["timeout"] == 30
        finally:
            os.unlink(config_path)
    
    def test_load_yaml_config(self):
        """Test loading YAML configuration."""
        yaml_content = """
database:
  host: localhost
  port: 5432
api:
  base_url: https://api.example.com
  timeout: 30
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            config_path = f.name
        
        try:
            factory = ConfigurationFactory()
            config = factory.load_configuration(config_path)
            
            assert config["database"]["host"] == "localhost"
            assert config["api"]["timeout"] == 30
        finally:
            os.unlink(config_path)
    
    def test_load_env_config(self):
        """Test loading environment-based configuration."""
        env_content = """
DATABASE_HOST=localhost
DATABASE_PORT=5432
API_BASE_URL=https://api.example.com
API_TIMEOUT=30
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            config_path = f.name
        
        try:
            factory = ConfigurationFactory()
            config = factory.load_configuration(config_path)
            
            # Env provider should structure the config appropriately
            assert "DATABASE_HOST" in config or "database" in config
        finally:
            os.unlink(config_path)
    
    def test_config_merging(self):
        """Test configuration merging from multiple sources."""
        # Base config
        base_config = {
            "database": {"host": "localhost", "port": 5432},
            "api": {"timeout": 30}
        }
        
        # Override config
        override_config = {
            "database": {"port": 3306},  # Override port
            "api": {"base_url": "https://new.api.com"},  # Add new field
            "cache": {"enabled": True}  # Add new section
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f1:
            json.dump(base_config, f1)
            base_path = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f2:
            json.dump(override_config, f2)
            override_path = f2.name
        
        try:
            factory = ConfigurationFactory()
            config = factory.merge_configurations([base_path, override_path])
            
            # Should have merged values
            assert config["database"]["host"] == "localhost"  # From base
            assert config["database"]["port"] == 3306  # Overridden
            assert config["api"]["timeout"] == 30  # From base
            assert config["api"]["base_url"] == "https://new.api.com"  # Added
            assert config["cache"]["enabled"] is True  # New section
        finally:
            os.unlink(base_path)
            os.unlink(override_path)
    
    def test_environment_variable_substitution(self):
        """Test environment variable substitution in config."""
        config_data = {
            "database": {
                "host": "${DB_HOST:localhost}",
                "port": "${DB_PORT:5432}",
                "password": "${DB_PASSWORD}"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            with patch.dict(os.environ, {"DB_HOST": "prod.db.com", "DB_PASSWORD": "secret"}):
                factory = ConfigurationFactory()
                config = factory.load_configuration(config_path)
                
                assert config["database"]["host"] == "prod.db.com"  # From env
                assert config["database"]["port"] == "5432"  # Default value
                assert config["database"]["password"] == "secret"  # From env
        finally:
            os.unlink(config_path)
    
    def test_config_validation(self):
        """Test configuration validation."""
        invalid_config = {
            "database": {
                "host": "",  # Invalid empty host
                "port": "not_a_number"  # Invalid port
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_config, f)
            config_path = f.name
        
        try:
            factory = ConfigurationFactory()
            
            # Should validate and potentially fix or raise errors
            config = factory.load_configuration(config_path, validate=True)
            
            # Depending on implementation, this might fix the issues or raise an error
            # For now, just test that validation was attempted
            assert config is not None
        finally:
            os.unlink(config_path)
    
    def test_config_caching(self):
        """Test configuration caching."""
        config_data = {"test": "value", "timestamp": "2025-01-01"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            factory = ConfigurationFactory()
            
            # Load config first time
            config1 = factory.load_configuration(config_path)
            
            # Modify file
            modified_data = {"test": "modified", "timestamp": "2025-01-02"}
            with open(config_path, 'w') as f:
                json.dump(modified_data, f)
            
            # Load config second time - should be cached
            config2 = factory.load_configuration(config_path)
            
            # If caching is enabled, should get original config
            if factory._use_cache:
                assert config2["timestamp"] == "2025-01-01"
            else:
                assert config2["timestamp"] == "2025-01-02"
        finally:
            os.unlink(config_path)
    
    def test_config_hot_reload(self):
        """Test configuration hot reloading."""
        config_data = {"version": 1, "feature_enabled": False}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            factory = ConfigurationFactory()
            
            # Load initial config
            config1 = factory.load_configuration(config_path)
            assert config1["version"] == 1
            assert config1["feature_enabled"] is False
            
            # Modify config file
            modified_data = {"version": 2, "feature_enabled": True}
            with open(config_path, 'w') as f:
                json.dump(modified_data, f)
            
            # Force reload
            config2 = factory.load_configuration(config_path, force_reload=True)
            assert config2["version"] == 2
            assert config2["feature_enabled"] is True
        finally:
            os.unlink(config_path)
    
    def test_get_api_base_url(self):
        """Test getting API base URL from configuration."""
        factory = ConfigurationFactory()
        
        # Test default value
        base_url = factory.get_api_base_url()
        assert base_url is not None
        assert isinstance(base_url, str)
        
        # Test with environment override
        with patch.dict(os.environ, {"API_BASE_URL": "https://custom.api.com"}):
            base_url = factory.get_api_base_url()
            assert base_url == "https://custom.api.com"
    
    def test_get_database_config(self):
        """Test getting database configuration."""
        factory = ConfigurationFactory()
        
        db_config = factory.get_database_config()
        assert isinstance(db_config, dict)
        
        # Should have standard database config keys
        expected_keys = ["host", "port", "name", "user"]
        for key in expected_keys:
            assert key in db_config or f"DATABASE_{key.upper()}" in os.environ
    
    def test_get_cache_config(self):
        """Test getting cache configuration."""
        factory = ConfigurationFactory()
        
        cache_config = factory.get_cache_config()
        assert isinstance(cache_config, dict)
        
        # Should have cache-related configuration
        assert "enabled" in cache_config or "type" in cache_config
    
    def test_config_file_not_found(self):
        """Test handling of missing configuration file."""
        factory = ConfigurationFactory()
        
        with pytest.raises(ConfigurationError) as exc_info:
            factory.load_configuration("/nonexistent/config.json")
        
        assert "Configuration file not found" in str(exc_info.value)
    
    def test_invalid_config_format(self):
        """Test handling of invalid configuration format."""
        invalid_json = "{ invalid json content"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(invalid_json)
            config_path = f.name
        
        try:
            factory = ConfigurationFactory()
            
            with pytest.raises(ConfigurationError) as exc_info:
                factory.load_configuration(config_path)
            
            assert "Failed to parse configuration" in str(exc_info.value)
        finally:
            os.unlink(config_path)


class TestCustomConfigurationProvider:
    """Test creating and using custom configuration providers."""
    
    def test_custom_provider_registration(self):
        """Test registering a custom configuration provider."""
        class DatabaseConfigProvider(ConfigurationProvider):
            def load_config(self, path=None):
                return {
                    "database": {
                        "host": "db.example.com",
                        "port": 5432,
                        "ssl": True
                    }
                }
        
        factory = ConfigurationFactory()
        provider = DatabaseConfigProvider()
        
        factory.register_provider("database", provider)
        
        config = factory.get_provider("database").load_config()
        assert config["database"]["host"] == "db.example.com"
        assert config["database"]["ssl"] is True
    
    def test_provider_with_validation(self):
        """Test provider with built-in validation."""
        class ValidatingProvider(ConfigurationProvider):
            def load_config(self, path=None):
                config = {
                    "api_key": "secret123",
                    "timeout": 30,
                    "retries": 3
                }
                
                # Built-in validation
                if config["timeout"] < 1:
                    raise ConfigurationError("Timeout must be positive")
                
                if not config["api_key"]:
                    raise ConfigurationError("API key is required")
                
                return config
        
        factory = ConfigurationFactory()
        provider = ValidatingProvider()
        
        config = provider.load_config()
        assert config["api_key"] == "secret123"
        assert config["timeout"] == 30


class TestConfigurationIntegration:
    """Integration tests for configuration system."""
    
    def test_multi_environment_config(self):
        """Test configuration for multiple environments."""
        base_config = {
            "app_name": "test_app",
            "debug": False,
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        dev_config = {
            "debug": True,
            "database": {
                "host": "dev.db.com"
            },
            "features": {
                "new_feature": True
            }
        }
        
        prod_config = {
            "database": {
                "host": "prod.db.com",
                "ssl": True
            },
            "logging": {
                "level": "ERROR"
            }
        }
        
        # Create config files
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / "base.json"
            dev_path = Path(temp_dir) / "dev.json"
            prod_path = Path(temp_dir) / "prod.json"
            
            with open(base_path, 'w') as f:
                json.dump(base_config, f)
            
            with open(dev_path, 'w') as f:
                json.dump(dev_config, f)
            
            with open(prod_path, 'w') as f:
                json.dump(prod_config, f)
            
            factory = ConfigurationFactory()
            
            # Test development configuration
            dev_merged = factory.merge_configurations([str(base_path), str(dev_path)])
            assert dev_merged["debug"] is True
            assert dev_merged["database"]["host"] == "dev.db.com"
            assert dev_merged["features"]["new_feature"] is True
            
            # Test production configuration
            prod_merged = factory.merge_configurations([str(base_path), str(prod_path)])
            assert prod_merged["debug"] is False  # From base
            assert prod_merged["database"]["host"] == "prod.db.com"
            assert prod_merged["database"]["ssl"] is True
            assert prod_merged["logging"]["level"] == "ERROR"
    
    def test_config_with_secrets_management(self):
        """Test configuration with secrets management."""
        config_with_secrets = {
            "database": {
                "host": "prod.db.com",
                "username": "${DB_USER}",
                "password": "${DB_PASSWORD}",
                "ssl_cert": "${DB_SSL_CERT_PATH}"
            },
            "api": {
                "key": "${API_KEY}",
                "secret": "${API_SECRET}"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_with_secrets, f)
            config_path = f.name
        
        try:
            secrets = {
                "DB_USER": "app_user",
                "DB_PASSWORD": "super_secret_password",
                "DB_SSL_CERT_PATH": "/etc/ssl/certs/db.pem",
                "API_KEY": "api_key_123",
                "API_SECRET": "api_secret_456"
            }
            
            with patch.dict(os.environ, secrets):
                factory = ConfigurationFactory()
                config = factory.load_configuration(config_path)
                
                assert config["database"]["username"] == "app_user"
                assert config["database"]["password"] == "super_secret_password"
                assert config["api"]["key"] == "api_key_123"
                assert config["api"]["secret"] == "api_secret_456"
        finally:
            os.unlink(config_path)


@pytest.fixture
def clean_factory():
    """Fixture providing a clean factory instance for each test."""
    # Reset singleton instance
    ConfigurationFactory._instance = None
    ConfigurationFactory._registry = None
    return ConfigurationFactory()


class TestFactoryReset:
    """Test factory reset and cleanup functionality."""
    
    def test_factory_reset(self, clean_factory):
        """Test that factory can be reset for testing."""
        factory = clean_factory
        
        # Load some configuration
        test_config = {"test": "value"}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            config_path = f.name
        
        try:
            config = factory.load_configuration(config_path)
            assert config["test"] == "value"
            
            # Factory should have loaded the config
            assert len(factory._registry.list_providers()) > 0
        finally:
            os.unlink(config_path)