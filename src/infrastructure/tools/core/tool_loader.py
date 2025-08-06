"""
Tool loader module - Dynamically loads tools for agents based on configuration

This module provides functionality to:
- Load all available tools from configuration
- Load specific tools for agent types based on their configuration
- Instantiate tool classes with proper configuration
- Handle tool loading errors gracefully
"""

import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import yaml

from src.infrastructure.tools.core.base_tool import ArtesanatoBaseTool
from src.infrastructure.utils.common_utils import safe_get_env

logger = logging.getLogger(__name__)

# Cache for loaded configurations and tool classes
_tool_config_cache: Dict[str, Any] = {}
_tool_class_cache: Dict[str, Type[ArtesanatoBaseTool]] = {}
_agent_config_cache: Dict[str, Any] = {}


def load_tool_config() -> Dict[str, Any]:
    """Load tool configuration from configuration file.
    
    Returns:
        Dictionary containing tool configurations
    """
    global _tool_config_cache
    
    if _tool_config_cache:
        return _tool_config_cache
    
    try:
        # Get project root directory
        current_dir = Path(__file__).parent
        project_root = current_dir
        
        # Navigate up to find the project root (where config/ exists)
        while project_root.parent != project_root:
            config_dir = project_root / "config"
            if config_dir.exists():
                break
            project_root = project_root.parent
        
        config_path = project_root / "config" / "tools.yaml"
        
        if not config_path.exists():
            logger.warning(f"Tool config file not found: {config_path}")
            _tool_config_cache = {}
            return _tool_config_cache
        
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file) or {}
            _tool_config_cache = config_data
        
        logger.info(f"Loaded {len(_tool_config_cache)} tool configurations")
        return _tool_config_cache
        
    except Exception as e:
        logger.error(f"Error loading tool configuration: {e}")
        _tool_config_cache = {}
        return _tool_config_cache


def load_agent_config() -> Dict[str, Any]:
    """Load agent configuration from agents.yaml file.
    
    Returns:
        Dictionary containing agent configurations
    """
    global _agent_config_cache
    
    if _agent_config_cache:
        return _agent_config_cache
    
    try:
        # Get project root directory
        current_dir = Path(__file__).parent
        project_root = current_dir
        
        # Navigate up to find the project root (where config/ exists)
        while project_root.parent != project_root:
            config_dir = project_root / "config"
            if config_dir.exists():
                break
            project_root = project_root.parent
        
        config_path = project_root / "config" / "agents.yaml"
        
        if not config_path.exists():
            logger.warning(f"Agent config file not found: {config_path}")
            _agent_config_cache = {}
            return _agent_config_cache
        
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file) or {}
            _agent_config_cache = config_data
        
        logger.info(f"Loaded {len(_agent_config_cache)} agent configurations")
        return _agent_config_cache
        
    except Exception as e:
        logger.error(f"Error loading agent configuration: {e}")
        _agent_config_cache = {}
        return _agent_config_cache


def get_tool_class(tool_name: str, tool_config: Dict[str, Any]) -> Optional[Type[ArtesanatoBaseTool]]:
    """Get tool class by name and configuration.
    
    Args:
        tool_name: Name of the tool
        tool_config: Tool configuration dictionary
        
    Returns:
        Tool class if successfully loaded, None otherwise
    """
    if tool_name in _tool_class_cache:
        return _tool_class_cache[tool_name]
    
    try:
        # Get the module path and class name from config
        tool_file = tool_config.get('file', '')
        tool_class_name = tool_config.get('class', '')
        
        if not tool_file or not tool_class_name:
            logger.error(f"Invalid tool configuration for {tool_name}: missing file or class")
            return None
        
        # Convert file path to module path
        # e.g., "tools/github_tool.py" -> "src.infrastructure.tools.external.github_tool"
        if tool_file.startswith('tools/'):
            module_path = f"src.infrastructure.tools.external.{tool_file[6:-3]}"  # Remove 'tools/' and '.py'
        else:
            # Handle other patterns if needed
            module_path = tool_file.replace('/', '.').replace('.py', '')
        
        # Import the module
        module = importlib.import_module(module_path)
        
        # Get the tool class
        tool_class = getattr(module, tool_class_name)
        
        # Verify it's a subclass of ArtesanatoBaseTool
        if not issubclass(tool_class, ArtesanatoBaseTool):
            logger.error(f"Tool class {tool_class_name} is not a subclass of ArtesanatoBaseTool")
            return None
        
        # Cache the class
        _tool_class_cache[tool_name] = tool_class
        return tool_class
        
    except ImportError as e:
        logger.error(f"Failed to import tool module for {tool_name}: {e}")
        return None
    except AttributeError as e:
        logger.error(f"Tool class {tool_class_name} not found in module for {tool_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading tool class for {tool_name}: {e}")
        return None


def instantiate_tool(tool_name: str, tool_class: Type[ArtesanatoBaseTool], 
                    tool_config: Dict[str, Any]) -> Optional[ArtesanatoBaseTool]:
    """Instantiate a tool with proper configuration.
    
    Args:
        tool_name: Name of the tool
        tool_class: Tool class to instantiate
        tool_config: Tool configuration dictionary
        
    Returns:
        Instantiated tool or None if instantiation fails
    """
    try:
        # Prepare initialization arguments
        init_kwargs = {
            'name': tool_name,
            'verbose': True,
            'config': tool_config.copy()
        }
        
        # Add environment variables if specified
        env_vars = tool_config.get('env', [])
        for env_var in env_vars:
            env_value = safe_get_env(env_var)
            if env_value:
                # Convert env var name to lowercase attribute name
                attr_name = env_var.lower().replace('_', '_')
                init_kwargs[attr_name] = env_value
        
        # Add any additional configuration from tool config
        for key, value in tool_config.items():
            if key not in ['type', 'description', 'file', 'class', 'env']:
                init_kwargs[key] = value
        
        # Instantiate the tool
        tool_instance = tool_class(**init_kwargs)
        
        logger.debug(f"Successfully instantiated tool: {tool_name}")
        return tool_instance
        
    except Exception as e:
        logger.error(f"Failed to instantiate tool {tool_name}: {e}")
        return None


def get_tools_for_agent(agent_name: str) -> List[ArtesanatoBaseTool]:
    """Get tools for a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., 'backend_engineer', 'qa')
        config: Optional configuration override
        
    Returns:
        List of instantiated tools for the agent
    """
    # Check if we're in testing mode
    if safe_get_env('TESTING', '').lower() in ('true', '1', 'yes'):
        logger.info(f"Testing mode detected, returning empty tools list for {agent_name}")
        return []
    
    agent_config = load_agent_config()
    tool_config = load_tool_config()
    
    # Get agent configuration
    agent_info = agent_config.get(agent_name)
    if not agent_info:
        logger.warning(f"No configuration found for agent: {agent_name}")
        return []
    
    # Get tools list for the agent
    tool_names = agent_info.get('tools', [])
    if not tool_names:
        logger.info(f"No tools configured for agent: {agent_name}")
        return []
    
    tools = []
    
    for tool_name in tool_names:
        try:
            # Get tool configuration
            tool_cfg = tool_config.get(tool_name)
            if not tool_cfg:
                logger.warning(f"Tool configuration not found for: {tool_name}")
                continue
            
            # Get tool class
            tool_class = get_tool_class(tool_name, tool_cfg)
            if not tool_class:
                logger.warning(f"Failed to load tool class for: {tool_name}")
                continue
            
            # Instantiate tool
            tool_instance = instantiate_tool(tool_name, tool_class, tool_cfg)
            if tool_instance:
                tools.append(tool_instance)
                logger.debug(f"Loaded tool {tool_name} for agent {agent_name}")
            else:
                logger.warning(f"Failed to instantiate tool: {tool_name}")
                
        except Exception as e:
            logger.error(f"Error loading tool {tool_name} for agent {agent_name}: {e}")
            continue
    
    logger.info(f"Loaded {len(tools)} tools for agent {agent_name}: {[t.name for t in tools]}")
    return tools


def load_all_tools() -> List[ArtesanatoBaseTool]:
    """Load all available tools from configuration.
    
    Returns:
        List of all instantiated tool instances
    """
    # Check if we're in testing mode
    if safe_get_env('TESTING', '').lower() in ('true', '1', 'yes'):
        logger.info("Testing mode detected, returning empty tools list")
        return []
    
    tool_config = load_tool_config()
    
    if not tool_config:
        logger.warning("No tool configuration found")
        return []
    
    tools = []
    
    for tool_name, tool_cfg in tool_config.items():
        try:
            # Get tool class
            tool_class = get_tool_class(tool_name, tool_cfg)
            if not tool_class:
                logger.warning(f"Failed to load tool class for: {tool_name}")
                continue
            
            # Instantiate tool
            tool_instance = instantiate_tool(tool_name, tool_class, tool_cfg)
            if tool_instance:
                tools.append(tool_instance)
                logger.debug(f"Loaded tool: {tool_name}")
            else:
                logger.warning(f"Failed to instantiate tool: {tool_name}")
                
        except Exception as e:
            logger.error(f"Error loading tool {tool_name}: {e}")
            continue
    
    logger.info(f"Loaded {len(tools)} total tools: {[t.name for t in tools]}")
    return tools


def load_tools_for_agent(agent_type: str, config: Optional[Dict[str, Any]] = None) -> List[ArtesanatoBaseTool]:
    """Load tools for specific agent type.
    
    This is an alias for get_tools_for_agent to maintain backward compatibility.
    
    Args:
        agent_type: Type/name of the agent
        config: Optional configuration override
        
    Returns:
        List of instantiated tools for the agent type
    """
    return get_tools_for_agent(agent_type)


def get_available_tools() -> List[str]:
    """Get list of available tool names.
    
    Returns:
        List of tool names that can be loaded
    """
    tool_config = load_tool_config()
    return list(tool_config.keys())


def get_tools_by_type(tool_type: str) -> List[str]:
    """Get tools by their type (e.g., 'Testing', 'API', 'Utility').
    
    Args:
        tool_type: Type of tools to retrieve
        
    Returns:
        List of tool names matching the specified type
    """
    tool_config = load_tool_config()
    matching_tools = []
    
    for tool_name, tool_cfg in tool_config.items():
        if tool_cfg.get('type') == tool_type:
            matching_tools.append(tool_name)
    
    return matching_tools


def clear_cache():
    """Clear all cached configurations and tool classes.
    
    Useful for testing or when configurations change at runtime.
    """
    global _tool_config_cache, _tool_class_cache, _agent_config_cache
    _tool_config_cache = {}
    _tool_class_cache.clear()
    _agent_config_cache = {}
    logger.info("Tool loader cache cleared")


__all__ = [
    "get_tools_for_agent", 
    "load_all_tools", 
    "load_tools_for_agent",
    "load_tool_config",
    "load_agent_config", 
    "get_available_tools",
    "get_tools_by_type",
    "clear_cache"
]
