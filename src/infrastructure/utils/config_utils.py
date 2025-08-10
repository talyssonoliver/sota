"""
Centralized Configuration Utilities
Handles configuration loading, saving, and management
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from typing import TypeVar
import configparser
from dotenv import load_dotenv

T = TypeVar('T')


def load_config(
    config_path: Union[str, Path],
    config_type: str = "auto",
    default: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Load configuration from file
    
    Args:
        config_path: Path to configuration file
        config_type: Type of config (json, yaml, ini, env, auto)
        default: Default configuration to merge with
        
    Returns:
        Configuration dictionary
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    # Auto-detect type from extension
    if config_type == "auto":
        suffix = config_path.suffix.lower()
        if suffix == ".json":
            config_type = "json"
        elif suffix in [".yaml", ".yml"]:
            config_type = "yaml"
        elif suffix in [".ini", ".cfg"]:
            config_type = "ini"
        elif suffix == ".env":
            config_type = "env"
        else:
            config_type = "json"  # Default
    
    config = {}
    
    if config_type == "json":
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    elif config_type == "yaml":
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    
    elif config_type == "ini":
        parser = configparser.ConfigParser()
        parser.read(config_path)
        config = {section: dict(parser[section]) for section in parser.sections()}
    
    elif config_type == "env":
        load_dotenv(config_path)
        # Load all env vars with a specific prefix
        prefix = os.getenv("CONFIG_PREFIX", "APP_")
        config = {
            key[len(prefix):].lower(): value
            for key, value in os.environ.items()
            if key.startswith(prefix)
        }
    
    # Merge with defaults
    if default:
        merged = default.copy()
        merged.update(config)
        return merged
    
    return config


def save_config(
    config: Dict[str, Any],
    config_path: Union[str, Path],
    config_type: str = "auto",
    pretty: bool = True
) -> None:
    """
    Save configuration to file
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
        config_type: Type of config (json, yaml, ini, auto)
        pretty: Whether to pretty-print the output
    """
    config_path = Path(config_path)
    
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Auto-detect type from extension
    if config_type == "auto":
        suffix = config_path.suffix.lower()
        if suffix == ".json":
            config_type = "json"
        elif suffix in [".yaml", ".yml"]:
            config_type = "yaml"
        elif suffix in [".ini", ".cfg"]:
            config_type = "ini"
        else:
            config_type = "json"  # Default
    
    if config_type == "json":
        with open(config_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(config, f, indent=2, ensure_ascii=False)
            else:
                json.dump(config, f, ensure_ascii=False)
    
    elif config_type == "yaml":
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=not pretty)
    
    elif config_type == "ini":
        parser = configparser.ConfigParser()
        for section, values in config.items():
            parser[section] = {str(k): str(v) for k, v in values.items()}
        with open(config_path, 'w', encoding='utf-8') as f:
            parser.write(f)


def read_config(
    config_path: Union[str, Path],
    section: Optional[str] = None,
    key: Optional[str] = None,
    default: Any = None
) -> Any:
    """
    Read specific value from configuration
    
    Args:
        config_path: Path to configuration file
        section: Optional section name (for INI files)
        key: Optional key to retrieve
        default: Default value if not found
        
    Returns:
        Configuration value or entire config
    """
    config = load_config(config_path, default={})
    
    if section and section in config:
        config = config[section]
    
    if key and key in config:
        return config[key]
    elif key:
        return default
    
    return config


def get_config(
    key: str,
    default: Any = None,
    config_path: Optional[Union[str, Path]] = None
) -> Any:
    """
    Get configuration value with fallback to environment
    
    Args:
        key: Configuration key
        default: Default value
        config_path: Optional config file path
        
    Returns:
        Configuration value
    """
    # Try environment variable first
    env_key = f"APP_{key.upper()}"
    if env_key in os.environ:
        return os.environ[env_key]
    
    # Try config file if provided
    if config_path:
        return read_config(config_path, key=key, default=default)
    
    return default


def update_config(
    config_path: Union[str, Path],
    updates: Dict[str, Any],
    create_if_missing: bool = True
) -> Dict[str, Any]:
    """
    Update configuration file with new values
    
    Args:
        config_path: Path to configuration file
        updates: Dictionary of updates
        create_if_missing: Create file if it doesn't exist
        
    Returns:
        Updated configuration
    """
    config_path = Path(config_path)
    
    if config_path.exists():
        config = load_config(config_path)
    elif create_if_missing:
        config = {}
    else:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    # Deep update
    def deep_update(base: dict, update: dict) -> dict:
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                deep_update(base[key], value)
            else:
                base[key] = value
        return base
    
    config = deep_update(config, updates)
    save_config(config, config_path)
    
    return config
