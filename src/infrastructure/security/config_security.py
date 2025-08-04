#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import (
    Any,
    Dict,
    List,
    Optional,
    Path,
    dataclass,
    json,
    logging,
    os,
    yaml
)
"""
Secure Configuration Management System

Provides secure handling of configuration data with encryption for sensitive values,
input validation, and secure storage practices.
"""

# import os  # Consolidated to common_imports
# import json  # Consolidated to common_imports
# import yaml  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
# from typing import Any, Dict, List, Optional, Union  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
# from dataclasses import dataclass  # Consolidated to common_imports
# import re  # Consolidated to common_imports

from .encryption_engine import DataEncryption, get_default_encryption
from .input_validation import InputValidator, ValidationRule, RegexRule


logger = logging.getLogger(__name__)


@dataclass
class ConfigSchema:
    """Schema definition for configuration validation."""
    
    field_name: str
    field_type: type
    required: bool = True
    sensitive: bool = False
    validation_rules: List[ValidationRule] = None
    default_value: Any = None
    description: str = ""
    
    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = []


class SecureConfigManager:
    """
    Secure configuration manager with encryption and validation.
    
    Features:
    - Automatic encryption of sensitive configuration values
    - Input validation for all configuration data
    - Secure storage with proper file permissions
    - Environment variable override support
    - Configuration schema enforcement
    """
    
    def __init__(self, 
                 config_dir: str = "config",
                 encryption: Optional[DataEncryption] = None):
        """
        Initialize secure configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
            encryption: Data encryption instance
        """
        self.config_dir = Path(config_dir)
        self.encryption = encryption or get_default_encryption()
        self.config_cache: Dict[str, Any] = {}
        self.schemas: Dict[str, List[ConfigSchema]] = {}
        self.validator = InputValidator()
        
        # Ensure config directory exists with proper permissions
        self.config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        # Register common validation rules
        self._setup_default_validations()
    
    def _setup_default_validations(self):
        """Set up default validation rules for common config fields."""
        
        # Database connections
        self.validator.add_rule('host', RegexRule(
            r'^[a-zA-Z0-9.-]+$', "Invalid hostname format"
        ))
        self.validator.add_rule('port', ValidationRule())  # Will be validated by NumericRangeRule
        
        # API keys and secrets
        self.validator.add_rule('api_key', RegexRule(
            r'^[a-zA-Z0-9_-]+$', "Invalid API key format"
        ))
        self.validator.add_rule('secret_key', RegexRule(
            r'^[a-zA-Z0-9+/=_-]+$', "Invalid secret key format"
        ))
        
        # URLs
        self.validator.add_rule('url', RegexRule(
            r'^https?://[a-zA-Z0-9.-]+(:[0-9]+)?(/.*)?$', "Invalid URL format"
        ))
    
    def register_schema(self, config_name: str, schema: List[ConfigSchema]):
        """
        Register a configuration schema for validation.
        
        Args:
            config_name: Name of the configuration
            schema: List of ConfigSchema objects
        """
        self.schemas[config_name] = schema
        logger.info(f"Registered schema for config: {config_name}")
    
    def _identify_sensitive_fields(self, data: Dict[str, Any]) -> List[str]:
        """
        Identify potentially sensitive fields based on naming patterns.
        
        Args:
            data: Configuration data dictionary
            
        Returns:
            List of field names that appear sensitive
        """
        sensitive_patterns = {
            'password', 'passwd', 'pwd',
            'secret', 'key', 'token',
            'credential', 'auth', 'api_key',
            'private_key', 'secret_key',
            'database_url', 'connection_string'
        }
        
        sensitive_fields = []
        
        for field_name in data.keys():
            field_lower = field_name.lower()
            if any(pattern in field_lower for pattern in sensitive_patterns):
                sensitive_fields.append(field_name)
        
        return sensitive_fields
    
    def _encrypt_sensitive_values(self, data: Dict[str, Any], 
                                 sensitive_fields: List[str] = None) -> Dict[str, Any]:
        """
        Encrypt sensitive values in configuration data.
        
        Args:
            data: Configuration data
            sensitive_fields: List of fields to encrypt (auto-detected if None)
            
        Returns:
            Dictionary with encrypted sensitive values
        """
        if sensitive_fields is None:
            sensitive_fields = self._identify_sensitive_fields(data)
        
        encrypted_data = data.copy()
        
        for field_name in sensitive_fields:
            if field_name in encrypted_data and isinstance(encrypted_data[field_name], str):
                try:
                    encrypted_value = self.encryption.encrypt_string(encrypted_data[field_name])
                    encrypted_data[field_name] = encrypted_value
                    encrypted_data[f"__{field_name}_encrypted"] = True
                    logger.debug(f"Encrypted sensitive field: {field_name}")
                except Exception as e:
                    logger.error(f"Failed to encrypt field {field_name}: {e}")
        
        return encrypted_data
    
    def _decrypt_sensitive_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive values in configuration data.
        
        Args:
            data: Configuration data with potentially encrypted values
            
        Returns:
            Dictionary with decrypted values
        """
        decrypted_data = data.copy()
        
        # Find encrypted fields
        encrypted_fields = [
            key.replace('__', '').replace('_encrypted', '')
            for key in data.keys()
            if key.startswith('__') and key.endswith('_encrypted')
        ]
        
        for field_name in encrypted_fields:
            if field_name in decrypted_data:
                try:
                    decrypted_value = self.encryption.decrypt_string(decrypted_data[field_name])
                    decrypted_data[field_name] = decrypted_value
                    decrypted_data.pop(f"__{field_name}_encrypted", None)
                    logger.debug(f"Decrypted sensitive field: {field_name}")
                except Exception as e:
                    logger.error(f"Failed to decrypt field {field_name}: {e}")
        
        return decrypted_data
    
    def _validate_config_data(self, config_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration data against registered schema.
        
        Args:
            config_name: Name of the configuration
            data: Configuration data to validate
            
        Returns:
            Validated and sanitized configuration data
            
        Raises:
            ValueError: If validation fails
        """
        schema = self.schemas.get(config_name, [])
        
        if not schema:
            # No schema registered, use basic validation
            is_valid, sanitized_data, errors = self.validator.validate_dict(data)
            if not is_valid:
                raise ValueError(f"Configuration validation failed: {errors}")
            return sanitized_data
        
        validated_data = {}
        errors = []
        
        # Check required fields and validate
        for field_schema in schema:
            field_name = field_schema.field_name
            
            if field_name in data:
                value = data[field_name]
                
                # Type validation
                if not isinstance(value, field_schema.field_type):
                    try:
                        value = field_schema.field_type(value)
                    except (ValueError, TypeError):
                        errors.append(f"Field {field_name} must be of type {field_schema.field_type.__name__}")
                        continue
                
                # Custom validation rules
                for rule in field_schema.validation_rules:
                    if not rule.validate(value, field_name):
                        errors.append(f"{field_name}: {rule.error_message}")
                
                validated_data[field_name] = value
                
            elif field_schema.required:
                if field_schema.default_value is not None:
                    validated_data[field_name] = field_schema.default_value
                else:
                    errors.append(f"Required field {field_name} is missing")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {errors}")
        
        return validated_data
    
    def load_config(self, config_name: str, 
                   config_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file with decryption and validation.
        
        Args:
            config_name: Name of the configuration
            config_file: Path to config file (optional, auto-detected if None)
            
        Returns:
            Decrypted and validated configuration data
        """
        # Check cache first
        if config_name in self.config_cache:
            return self.config_cache[config_name]
        
        # Determine config file path
        if config_file is None:
            # Try different extensions
            for ext in ['.json', '.yaml', '.yml']:
                config_path = self.config_dir / f"{config_name}{ext}"
                if config_path.exists():
                    config_file = str(config_path)
                    break
        else:
            config_path = Path(config_file)
        
        if not config_file or not Path(config_file).exists():
            raise FileNotFoundError(f"Configuration file not found for: {config_name}")
        
        # Load configuration data
        config_path = Path(config_file)
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse configuration file {config_file}: {e}")
        
        # Decrypt sensitive values
        data = self._decrypt_sensitive_values(data)
        
        # Apply environment variable overrides
        data = self._apply_env_overrides(config_name, data)
        
        # Validate configuration
        data = self._validate_config_data(config_name, data)
        
        # Cache the result
        self.config_cache[config_name] = data
        
        logger.info(f"Loaded and validated configuration: {config_name}")
        return data
    
    def save_config(self, config_name: str, data: Dict[str, Any],
                   config_file: Optional[str] = None):
        """
        Save configuration to file with encryption and validation.
        
        Args:
            config_name: Name of the configuration
            data: Configuration data to save
            config_file: Path to config file (optional, auto-generated if None)
        """
        # Validate before saving
        validated_data = self._validate_config_data(config_name, data)
        
        # Encrypt sensitive values
        encrypted_data = self._encrypt_sensitive_values(validated_data)
        
        # Determine save path
        if config_file is None:
            config_file = str(self.config_dir / f"{config_name}.json")
        
        config_path = Path(config_file)
        
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save with proper permissions
        try:
            with open(config_path, 'w') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(encrypted_data, f, default_flow_style=False)
                else:
                    json.dump(encrypted_data, f, indent=2, sort_keys=True)
            
            # Set secure file permissions (owner read/write only)
            os.chmod(config_path, 0o600)
            
            # Update cache
            self.config_cache[config_name] = validated_data
            
            logger.info(f"Saved secure configuration: {config_name}")
            
        except Exception as e:
            raise IOError(f"Failed to save configuration {config_name}: {e}")
    
    def _apply_env_overrides(self, config_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration data.
        
        Environment variables should be named: {CONFIG_NAME}_{FIELD_NAME}
        
        Args:
            config_name: Name of the configuration
            data: Configuration data
            
        Returns:
            Configuration data with environment overrides applied
        """
        env_prefix = f"{config_name.upper()}_"
        overridden_data = data.copy()
        
        for env_var, env_value in os.environ.items():
            if env_var.startswith(env_prefix):
                field_name = env_var[len(env_prefix):].lower()
                
                if field_name in overridden_data:
                    # Try to convert to the same type as the original value
                    original_value = overridden_data[field_name]
                    
                    try:
                        if isinstance(original_value, bool):
                            env_value = env_value.lower() in ('true', '1', 'yes', 'on')
                        elif isinstance(original_value, int):
                            env_value = int(env_value)
                        elif isinstance(original_value, float):
                            env_value = float(env_value)
                        # Strings remain as-is
                        
                        overridden_data[field_name] = env_value
                        logger.info(f"Applied environment override for {config_name}.{field_name}")
                        
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to apply environment override for {field_name}: {e}")
        
        return overridden_data
    
    def get_config_value(self, config_name: str, field_name: str, 
                        default: Any = None) -> Any:
        """
        Get a specific configuration value.
        
        Args:
            config_name: Name of the configuration
            field_name: Name of the field
            default: Default value if field not found
            
        Returns:
            Configuration value
        """
        try:
            config = self.load_config(config_name)
            return config.get(field_name, default)
        except Exception as e:
            logger.error(f"Failed to get config value {config_name}.{field_name}: {e}")
            return default
    
    def clear_cache(self, config_name: Optional[str] = None):
        """
        Clear configuration cache.
        
        Args:
            config_name: Specific config to clear (clear all if None)
        """
        if config_name:
            self.config_cache.pop(config_name, None)
        else:
            self.config_cache.clear()
        
        logger.info(f"Cleared config cache: {config_name or 'all'}")


# Global secure config manager instance
_default_config_manager = None


def get_secure_config_manager() -> SecureConfigManager:
    """Get the default secure configuration manager."""
    global _default_config_manager
    if _default_config_manager is None:
        _default_config_manager = SecureConfigManager()
    return _default_config_manager


# Convenience functions
def load_secure_config(config_name: str) -> Dict[str, Any]:
    """Load configuration using the default secure manager."""
    return get_secure_config_manager().load_config(config_name)


def get_secure_config_value(config_name: str, field_name: str, default: Any = None) -> Any:
    """Get a specific configuration value using the default secure manager."""
    return get_secure_config_manager().get_config_value(config_name, field_name, default)


# Example schemas for common configurations
def register_default_schemas():
    """Register schemas for common configuration types."""
    manager = get_secure_config_manager()
    
    # Database configuration schema
    db_schema = [
        ConfigSchema('host', str, required=True),
        ConfigSchema('port', int, required=True, default_value=5432),
        ConfigSchema('database', str, required=True),
        ConfigSchema('username', str, required=True),
        ConfigSchema('password', str, required=True, sensitive=True),
        ConfigSchema('ssl_mode', str, required=False, default_value='prefer'),
    ]
    manager.register_schema('database', db_schema)
    
    # API configuration schema
    api_schema = [
        ConfigSchema('host', str, required=True, default_value='0.0.0.0'),
        ConfigSchema('port', int, required=True, default_value=8000),
        ConfigSchema('debug', bool, required=False, default_value=False),
        ConfigSchema('secret_key', str, required=True, sensitive=True),
        ConfigSchema('cors_origins', list, required=False, default_value=[]),
    ]
    manager.register_schema('api', api_schema)
    
    # Memory/Redis configuration schema
    memory_schema = [
        ConfigSchema('redis_url', str, required=True, sensitive=True),
        ConfigSchema('max_connections', int, required=False, default_value=10),
        ConfigSchema('timeout', int, required=False, default_value=30),
        ConfigSchema('encryption_enabled', bool, required=False, default_value=True),
    ]
    manager.register_schema('memory', memory_schema)


# Initialize default schemas
register_default_schemas()