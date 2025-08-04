
from src.infrastructure.utils.common_imports import dataclass, re
"""
Validation Configuration

Provides centralized validation rules and schemas for configuration data.
Implements validation boundaries to prevent bad data propagation.
"""

# import re  # Consolidated to common_imports
from typing import Dict, Any, List, Callable
# from dataclasses import dataclass  # Consolidated to common_imports
from .config_interfaces import IConfigurationValidator, ConfigurationValidationResult


@dataclass
class ValidationRule:
    """Single validation rule"""
    name: str
    validator: Callable[[Any], bool]
    error_message: str
    is_required: bool = True


class ConfigurationValidationError(Exception):
    """Exception raised when configuration validation fails"""
    
    def __init__(self, message: str, errors: List[str]):
        super().__init__(message)
        self.errors = errors


class ValidationConfiguration(IConfigurationValidator):
    """Configuration validator with comprehensive validation rules"""
    
    def __init__(self):
        """Initialize validation rules"""
        self._validation_rules = self._build_validation_rules()
        self._schema = self._build_schema()
    
    def _build_validation_rules(self) -> Dict[str, List[ValidationRule]]:
        """Build comprehensive validation rules"""
        return {
            "api": [
                ValidationRule(
                    "base_url_format",
                    lambda x: isinstance(x, str) and (x.startswith("http://") or x.startswith("https://")),
                    "API base URL must be a valid HTTP/HTTPS URL"
                ),
                ValidationRule(
                    "timeout_range",
                    lambda x: isinstance(x, int) and 1 <= x <= 300,
                    "API timeout must be between 1 and 300 seconds"
                ),
                ValidationRule(
                    "retry_attempts",
                    lambda x: isinstance(x, int) and 0 <= x <= 10,
                    "Retry attempts must be between 0 and 10"
                )
            ],
            "dashboard": [
                ValidationRule(
                    "url_format",
                    lambda x: isinstance(x, str) and (x.startswith("http://") or x.startswith("https://")),
                    "Dashboard URL must be a valid HTTP/HTTPS URL"
                ),
                ValidationRule(
                    "refresh_interval",
                    lambda x: isinstance(x, int) and x > 0,
                    "Refresh interval must be a positive integer"
                )
            ],
            "database": [
                ValidationRule(
                    "url_format",
                    lambda x: isinstance(x, str) and len(x.strip()) > 0,
                    "Database URL cannot be empty"
                ),
                ValidationRule(
                    "pool_size",
                    lambda x: isinstance(x, int) and x > 0,
                    "Database pool size must be a positive integer"
                ),
                ValidationRule(
                    "max_overflow",
                    lambda x: isinstance(x, int) and x >= 0,
                    "Database max overflow must be non-negative",
                    is_required=False
                )
            ],
            "security": [
                ValidationRule(
                    "encryption_enabled",
                    lambda x: isinstance(x, bool),
                    "Encryption enabled must be a boolean value"
                ),
                ValidationRule(
                    "auth_required",
                    lambda x: isinstance(x, bool),
                    "Auth required must be a boolean value"
                ),
                ValidationRule(
                    "debug_mode",
                    lambda x: isinstance(x, bool),
                    "Debug mode must be a boolean value"
                )
            ],
            "monitoring": [
                ValidationRule(
                    "metrics_enabled",
                    lambda x: isinstance(x, bool),
                    "Metrics enabled must be a boolean value"
                ),
                ValidationRule(
                    "log_level",
                    lambda x: isinstance(x, str) and x.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    "Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
                )
            ]
        }
    
    def _build_schema(self) -> Dict[str, Any]:
        """Build configuration schema"""
        return {
            "type": "object",
            "properties": {
                "api": {
                    "type": "object",
                    "properties": {
                        "base_url": {"type": "string", "pattern": r"^https?://"},
                        "timeout": {"type": "integer", "minimum": 1, "maximum": 300},
                        "retry_attempts": {"type": "integer", "minimum": 0, "maximum": 10}
                    },
                    "required": ["base_url", "timeout"]
                },
                "dashboard": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "pattern": r"^https?://"},
                        "refresh_interval": {"type": "integer", "minimum": 1}
                    },
                    "required": ["url"]
                },
                "database": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "minLength": 1},
                        "pool_size": {"type": "integer", "minimum": 1},
                        "max_overflow": {"type": "integer", "minimum": 0}
                    },
                    "required": ["url"]
                },
                "security": {
                    "type": "object",
                    "properties": {
                        "encryption_enabled": {"type": "boolean"},
                        "auth_required": {"type": "boolean"},
                        "debug_mode": {"type": "boolean"}
                    },
                    "required": ["encryption_enabled", "auth_required"]
                },
                "monitoring": {
                    "type": "object",
                    "properties": {
                        "metrics_enabled": {"type": "boolean"},
                        "log_level": {
                            "type": "string",
                            "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                        }
                    },
                    "required": ["log_level"]
                }
            },
            "required": ["api", "database"]
        }
    
    def validate(self, config: Dict[str, Any]) -> ConfigurationValidationResult:
        """Validate configuration data"""
        errors = []
        warnings = []
        
        # Validate each section
        for section_name, section_config in config.items():
            if section_name in self._validation_rules:
                section_errors = self._validate_section(
                    section_name, section_config, self._validation_rules[section_name]
                )
                errors.extend(section_errors)
        
        # Cross-section validation
        cross_section_errors, cross_section_warnings = self._validate_cross_sections(config)
        errors.extend(cross_section_errors)
        warnings.extend(cross_section_warnings)
        
        # Security-specific validation
        security_warnings = self._validate_security_configuration(config)
        warnings.extend(security_warnings)
        
        return ConfigurationValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_section(self, section_name: str, section_config: Dict[str, Any], rules: List[ValidationRule]) -> List[str]:
        """Validate a single configuration section"""
        errors = []
        
        # Map rule names to actual field names
        rule_to_field_mapping = {
            "base_url_format": "base_url",
            "timeout_range": "timeout",
            "retry_attempts": "retry_attempts",
            "url_format": "url",
            "refresh_interval": "refresh_interval",
            "pool_size": "pool_size",
            "max_overflow": "max_overflow",
            "encryption_enabled": "encryption_enabled",
            "auth_required": "auth_required",
            "debug_mode": "debug_mode",
            "metrics_enabled": "metrics_enabled",
            "log_level": "log_level"
        }
        
        for rule in rules:
            # Get the actual field name for this rule
            field_name = rule_to_field_mapping.get(rule.name, rule.name)
            
            if field_name in section_config:
                try:
                    if not rule.validator(section_config[field_name]):
                        errors.append(f"{section_name}.{field_name}: {rule.error_message}")
                except Exception as e:
                    errors.append(f"{section_name}.{field_name}: Validation error - {str(e)}")
            elif rule.is_required:
                errors.append(f"{section_name}.{field_name}: Required field is missing")
        
        return errors
    
    def _validate_cross_sections(self, config: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """Validate cross-section dependencies"""
        errors = []
        warnings = []
        
        # Validate that API and dashboard URLs don't conflict
        if "api" in config and "dashboard" in config:
            api_url = config["api"].get("base_url", "")
            dashboard_url = config["dashboard"].get("url", "")
            
            if api_url and dashboard_url:
                # Extract base domains
                api_domain = self._extract_domain(api_url)
                dashboard_domain = self._extract_domain(dashboard_url)
                
                if api_domain != dashboard_domain:
                    warnings.append(
                        "API and dashboard are on different domains, this may cause CORS issues"
                    )
        
        # Validate security configuration consistency
        if "security" in config:
            security_config = config["security"]
            if security_config.get("debug_mode", False) and not security_config.get("encryption_enabled", True):
                warnings.append(
                    "Debug mode is enabled but encryption is disabled - this may expose sensitive data"
                )
        
        return errors, warnings
    
    def _validate_security_configuration(self, config: Dict[str, Any]) -> List[str]:
        """Validate security-specific configuration"""
        warnings = []
        
        if "security" not in config:
            warnings.append("Security configuration section is missing")
            return warnings
        
        security_config = config["security"]
        
        # Check for insecure configurations
        if not security_config.get("encryption_enabled", False):
            warnings.append("Encryption is disabled - consider enabling for sensitive data protection")
        
        if not security_config.get("auth_required", False):
            warnings.append("Authentication is not required - consider enabling for production environments")
        
        if security_config.get("debug_mode", False):
            warnings.append("Debug mode is enabled - ensure this is disabled in production")
        
        # Check if using HTTP in production-like settings
        if "api" in config:
            api_url = config["api"].get("base_url", "")
            if api_url.startswith("http://") and not api_url.startswith("http://localhost"):
                warnings.append("Using HTTP instead of HTTPS for non-localhost API - security risk")
        
        return warnings
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            # Simple domain extraction
            if "://" in url:
                domain_part = url.split("://")[1]
                return domain_part.split("/")[0].split(":")[0]
            return url
        except:
            return ""
    
    def get_schema(self) -> Dict[str, Any]:
        """Get validation schema"""
        return self._schema
    
    def validate_and_raise(self, config: Dict[str, Any]) -> None:
        """Validate configuration and raise exception if invalid"""
        result = self.validate(config)
        if not result.is_valid:
            raise ConfigurationValidationError(
                f"Configuration validation failed with {len(result.errors)} errors",
                result.errors
            )