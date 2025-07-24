"""
Unified Configuration Manager

Single source of truth for all system configurations.
Provides centralized access to all configuration files and settings.
"""
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConfigPaths:
    """Central registry of all configuration file paths"""
    
    # Core configurations
    agents: Path = Path("config/agents.yaml")
    tools: Path = Path("config/tools.yaml")
    critical_path: Path = Path("config/critical_path.yaml")
    auto_generated_graph: Path = Path("config/auto_generated_graph.json")
    
    # Quality and validation
    qa_thresholds: Path = Path("config/qa_thresholds.yaml")
    validation: Path = Path("config/validation_config.json")
    
    # Policies and workflows
    hitl_policies: Path = Path("config/hitl_policies.yaml")
    daily_cycle: Path = Path("config/daily_cycle.json")
    
    # Integration configs
    gemini: Path = Path("config/gemini_config.json")
    webhook: Path = Path("config/webhook_external_api_config.json")
    prometheus: Path = Path("config/prometheus.yml")
    
    # Schema definitions
    task_schema: Path = Path("config/schemas/task.schema.json")
    
    # Agent generation
    agent_generator: Path = Path("config/agent_generator.yaml")


class ConfigurationManager:
    """Unified configuration manager for the AI system"""
    
    def __init__(self, config_root: Union[str, Path] = None):
        """Initialize configuration manager
        
        Args:
            config_root: Root directory for configuration files
        """
        self.config_root = Path(config_root) if config_root else Path(".")
        self.paths = ConfigPaths()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._validate_config_files()
    
    def _validate_config_files(self):
        """Validate that all required configuration files exist"""
        missing_files = []
        for name, path in self.paths.__dict__.items():
            full_path = self.config_root / path
            if not full_path.exists():
                missing_files.append(str(path))
        
        if missing_files:
            logger.warning(f"Missing configuration files: {missing_files}")
    
    def load_config(self, config_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """Load a configuration file
        
        Args:
            config_name: Name of the configuration (e.g., 'agents', 'tools')
            use_cache: Whether to use cached version if available
            
        Returns:
            Dictionary containing the configuration data
        """
        if use_cache and config_name in self._cache:
            return self._cache[config_name]
        
        if not hasattr(self.paths, config_name):
            raise ValueError(f"Unknown configuration: {config_name}")
        
        config_path = self.config_root / getattr(self.paths, config_name)
        
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
            
            self._cache[config_name] = config_data
            logger.info(f"Loaded configuration: {config_name}")
            return config_data
            
        except Exception as e:
            logger.error(f"Error loading configuration {config_name}: {e}")
            return {}
    
    def get_agents_config(self) -> Dict[str, Any]:
        """Get agents configuration"""
        return self.load_config('agents')
    
    def get_tools_config(self) -> Dict[str, Any]:
        """Get tools configuration"""
        return self.load_config('tools')
    
    def get_critical_path_config(self) -> Dict[str, Any]:
        """Get critical path configuration for workflow execution"""
        return self.load_config('critical_path')
    
    def get_qa_thresholds_config(self) -> Dict[str, Any]:
        """Get QA thresholds configuration"""
        return self.load_config('qa_thresholds')
    
    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration"""
        return self.load_config('validation')
    
    def get_hitl_policies_config(self) -> Dict[str, Any]:
        """Get HITL policies configuration"""
        return self.load_config('hitl_policies')
    
    def get_daily_cycle_config(self) -> Dict[str, Any]:
        """Get daily cycle configuration"""
        return self.load_config('daily_cycle')
    
    def get_auto_generated_graph_config(self) -> Dict[str, Any]:
        """Get auto-generated graph configuration"""
        return self.load_config('auto_generated_graph')
    
    def get_task_schema(self) -> Dict[str, Any]:
        """Get task schema definition"""
        return self.load_config('task_schema')
    
    def get_gemini_config(self) -> Dict[str, Any]:
        """Get Gemini API configuration"""
        return self.load_config('gemini')
    
    def get_webhook_config(self) -> Dict[str, Any]:
        """Get webhook configuration"""
        return self.load_config('webhook')
    
    def get_prometheus_config(self) -> Dict[str, Any]:
        """Get Prometheus configuration"""
        return self.load_config('prometheus')
    
    def get_agent_generator_config(self) -> Dict[str, Any]:
        """Get agent generator configuration"""
        return self.load_config('agent_generator')
    
    def reload_config(self, config_name: Optional[str] = None):
        """Reload configuration from disk
        
        Args:
            config_name: Specific config to reload, or None for all configs
        """
        if config_name:
            if config_name in self._cache:
                del self._cache[config_name]
            self.load_config(config_name, use_cache=False)
        else:
            self._cache.clear()
            logger.info("Cleared all configuration cache")
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all configurations as a single dictionary"""
        all_configs = {}
        for config_name in self.paths.__dict__.keys():
            all_configs[config_name] = self.load_config(config_name)
        return all_configs
    
    def validate_configuration_integrity(self) -> Dict[str, Any]:
        """Validate the integrity of all configuration files
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid_configs': [],
            'invalid_configs': [],
            'missing_configs': [],
            'warnings': []
        }
        
        for config_name in self.paths.__dict__.keys():
            config_path = self.config_root / getattr(self.paths, config_name)
            
            if not config_path.exists():
                results['missing_configs'].append(config_name)
                continue
            
            try:
                config_data = self.load_config(config_name, use_cache=False)
                if config_data:
                    results['valid_configs'].append(config_name)
                    
                    # Specific validation checks
                    if config_name == 'agents' and 'agents' not in config_data:
                        results['warnings'].append(f"{config_name}: missing 'agents' section")
                    elif config_name == 'tools' and 'tool_groups' not in config_data:
                        results['warnings'].append(f"{config_name}: missing 'tool_groups' section")
                        
                else:
                    results['invalid_configs'].append(config_name)
                    
            except Exception as e:
                results['invalid_configs'].append(f"{config_name}: {str(e)}")
        
        return results


# Global configuration manager instance
_config_manager = None


def get_config_manager(config_root: Union[str, Path] = None) -> ConfigurationManager:
    """Get the global configuration manager instance
    
    Args:
        config_root: Root directory for configuration files
        
    Returns:
        ConfigurationManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_root)
    return _config_manager


def load_config(config_name: str) -> Dict[str, Any]:
    """Convenience function to load a configuration
    
    Args:
        config_name: Name of the configuration to load
        
    Returns:
        Configuration dictionary
    """
    return get_config_manager().load_config(config_name)


# Export convenience functions for backward compatibility
def get_agents_config() -> Dict[str, Any]:
    """Get agents configuration"""
    return get_config_manager().get_agents_config()


def get_tools_config() -> Dict[str, Any]:
    """Get tools configuration"""
    return get_config_manager().get_tools_config()


def get_critical_path_config() -> Dict[str, Any]:
    """Get critical path configuration"""
    return get_config_manager().get_critical_path_config()


def get_qa_thresholds_config() -> Dict[str, Any]:
    """Get QA thresholds configuration"""
    return get_config_manager().get_qa_thresholds_config()


def get_hitl_policies_config() -> Dict[str, Any]:
    """Get HITL policies configuration"""
    return get_config_manager().get_hitl_policies_config()