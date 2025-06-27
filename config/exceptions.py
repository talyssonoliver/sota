"""Configuration exceptions."""

class ConfigError(Exception):
    """Configuration error."""
    pass

class ValidationError(ConfigError):
    """Validation error."""
    pass
