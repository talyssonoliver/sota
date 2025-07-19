"""Configuration module for the AI system.

This module provides access to configuration files and settings.
Single source of truth for all system configurations.
"""

from src.infrastructure.utils.input_validation import ValidationError
from src.infrastructure.memory.config.memory_config import MemoryConfig
from .config_manager import (
    ConfigurationManager,
    get_config_manager,
    load_config,
    get_agents_config,
    get_tools_config,
    get_critical_path_config,
    get_qa_thresholds_config,
    get_hitl_policies_config,
)

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

# Export the unified configuration interface
__all__ = [
    "ConfigError", 
    "ValidationError", 
    "MemoryConfig",
    "ConfigurationManager",
    "get_config_manager",
    "load_config",
    "get_agents_config",
    "get_tools_config",
    "get_critical_path_config",
    "get_qa_thresholds_config",
    "get_hitl_policies_config",
]
