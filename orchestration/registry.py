"""
Agent Registry for the AI Agent System
Maps agent names to their constructor functions for dynamic instantiation.
"""

import json
import logging
try:
    import threading
except ImportError:
    pass
import os
from typing import Any, Callable, Dict, List, Optional

try:
    import yaml
except ImportError:
    # Fallback YAML implementation
    class yaml:
        @staticmethod
        def safe_load(stream):
            return {}
        
        @staticmethod
        def safe_dump(data, stream=None):
            if stream:
                stream.write(str(data))
            return str(data)

try:
    from src.core.agents import (create_backend_engineer_agent, create_coordinator_agent,
                    create_documentation_agent, create_frontend_engineer_agent,
                    create_qa_agent, create_technical_lead_agent)
except ImportError:
    pass
from tools.tool_loader import get_tools_for_agent, load_all_tools

logger = logging.getLogger(__name__)

# Thread-safe registry implementation
class ThreadSafeAgentRegistry:
    """Thread-safe agent registry for concurrent access."""
    
    def __init__(self):
        self._registry_lock = threading.RLock()
        self._config_cache_lock = threading.RLock()
        self._stats_lock = threading.RLock()
        
        # Immutable registry mapping (no need for locks once set)
        self._registry: Dict[str, Callable] = {
            # Agent roles by type
            "coordinator": create_coordinator_agent,
            "technical_lead": create_technical_lead_agent,
            "backend": create_backend_engineer_agent,
            "backend_engineer": create_backend_engineer_agent,
            "frontend": create_frontend_engineer_agent,
            "frontend_engineer": create_frontend_engineer_agent,
            "documentation": create_documentation_agent,
            "qa": create_qa_agent,
            # Task prefix mappings
            "CO": create_coordinator_agent,
            "TL": create_technical_lead_agent,
            "BE": create_backend_engineer_agent,
            "FE": create_frontend_engineer_agent,
            "DOC": create_documentation_agent,
            "QA": create_qa_agent,
        }
        
        # Thread-safe configuration cache
        self._config_cache: Optional[Dict[str, Any]] = None
        
        # Thread-safe statistics
        self._stats = {
            'agents_created': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'config_loads': 0
        }
    
    def get_constructor(self, agent_id: str) -> Optional[Callable]:
        """Get agent constructor function by agent identifier (thread-safe)."""
        # Registry is immutable, no locking needed for reads
        constructor = self._registry.get(agent_id.lower())
        if constructor is not None:
            return constructor
        
        return self._registry.get(agent_id.upper())
    
    def get_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent configuration (thread-safe with caching)."""
        with self._config_cache_lock:
            # Load config if not cached
            if self._config_cache is None:
                self._config_cache = self._load_agent_config()
                with self._stats_lock:
                    self._stats['config_loads'] += 1
            
            with self._stats_lock:
                if agent_id.lower() in self._config_cache:
                    self._stats['cache_hits'] += 1
                    return self._config_cache[agent_id.lower()].copy()
                
                # Try to match task prefix with agent role
                for role, config in self._config_cache.items():
                    if role.upper().startswith(agent_id.upper()):
                        self._stats['cache_hits'] += 1
                        return config.copy()
                
                self._stats['cache_misses'] += 1
                return None
    
    def create_agent(self, agent_id: str, **kwargs) -> Any:
        """Create agent instance (thread-safe)."""
        with self._registry_lock:
            constructor = self.get_constructor(agent_id)
            
            if constructor is None:
                raise ValueError(f"Unknown agent identifier: {agent_id}")
            
            # Get agent configuration
            agent_config = self.get_config(agent_id)
            
            # Load tools if configuration exists
            if agent_config:
                if "custom_tools" not in kwargs:
                    try:
                        custom_tools = get_tools_for_agent(agent_id, agent_config, **kwargs)
                        if custom_tools:
                            kwargs["custom_tools"] = custom_tools
                    except Exception as e:
                        logger.warning(f"Failed to load tools for agent {agent_id}: {e}")
            
            agent = constructor(**kwargs)
            
            # Update statistics
            with self._stats_lock:
                self._stats['agents_created'] += 1
            
            logger.debug(f"Thread-safe agent created: {agent_id} (thread: {threading.get_ident()})")
            return agent
    
    def _load_agent_config(self) -> Dict[str, Any]:
        """Load agent configuration from YAML (internal use)."""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'config', 'agents.yaml'
        )
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Failed to load agent config: {e}")
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics (thread-safe)."""
        with self._stats_lock:
            return {
                'available_agents': list(self._registry.keys()),
                'agents_created': self._stats['agents_created'],
                'config_cache_hits': self._stats['cache_hits'],
                'config_cache_misses': self._stats['cache_misses'],
                'config_loads': self._stats['config_loads'],
                'thread_safety_enabled': True
            }
    
    def clear_cache(self):
        """Clear configuration cache (thread-safe)."""
        with self._config_cache_lock:
            self._config_cache = None
            logger.info("Agent registry configuration cache cleared")
# Global thread-safe registry instance
_registry_instance: Optional[ThreadSafeAgentRegistry] = None
_registry_lock = threading.RLock()

def get_registry() -> ThreadSafeAgentRegistry:
    """Get the global thread-safe registry instance."""
    global _registry_instance
    
    if _registry_instance is None:
        with _registry_lock:
            if _registry_instance is None:  # Double-check locking
                _registry_instance = ThreadSafeAgentRegistry()
                logger.info("Global thread-safe agent registry created")
    
    return _registry_instance

# Backward compatibility - maintain original registry structure
AGENT_REGISTRY = get_registry()._registry

def load_agent_config() -> Dict[str, Any]:
    """
    Load the agent configuration from YAML (thread-safe).

    Returns:
        Dict[str, Any]: The parsed agent configuration.
    """
    registry = get_registry()
    return registry.get_config("dummy") or registry._load_agent_config()

def get_agent_config(agent_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the configuration for a specific agent (thread-safe).

    Args:
        agent_id: The agent identifier

    Returns:
        Dict[str, Any]: The agent configuration or None if not found
    """
    registry = get_registry()
    return registry.get_config(agent_id)

def get_agent_constructor(agent_id: str) -> Optional[Callable]:
    """
    Get agent constructor function by agent identifier (thread-safe).

    Args:
        agent_id: The agent identifier (can be role name or task prefix)

    Returns:
        The constructor function for the specified agent or None if not found
    """
    registry = get_registry()
    return registry.get_constructor(agent_id)

def create_agent_instance(agent_id: str, **kwargs) -> Any:
    """
    Create an agent instance by agent identifier (thread-safe).

    Args:
        agent_id: The agent identifier (can be role name or task prefix)
        **kwargs: Configuration parameters to pass to the agent constructor

    Returns:
        An instance of the specified agent with appropriate tools

    Raises:
        ValueError: If the agent identifier is not found in the registry
    """
    registry = get_registry()
    return registry.create_agent(agent_id, **kwargs)

def get_agent_for_task(task_id: str, **kwargs) -> Any:
    """
    Create an agent instance based on a task identifier.

    Args:
        task_id: The task identifier (e.g., BE-07, TL-03)
        **kwargs: Configuration parameters to pass to the agent constructor

    Returns:
        An instance of the appropriate agent for the task

    Raises:
        ValueError: If the task prefix is not recognized
    """
    parts = task_id.split("-", 1)

    if len(parts) < 2 or not parts[0]:
        raise ValueError(f"Invalid task ID format: {task_id}")

    task_prefix = parts[0].upper()
    return create_agent_instance(task_prefix, **kwargs)

def get_agent(agent_name: str, **kwargs) -> Any:
    """
    Get an instantiated agent by name.

    Args:
        agent_name: The agent name or role
        **kwargs: Additional parameters to pass to the agent constructor

    Returns:
        An instantiated agent

    Raises:
        ValueError: If the agent name is not found in the registry
    """
    return create_agent_instance(agent_name, **kwargs)
