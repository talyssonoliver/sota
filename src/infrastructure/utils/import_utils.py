#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import (
    Any,
    Dict,
    Path,
    sys
)
"""
Centralized Import Utilities

This module provides centralized import handling to eliminate the duplication
of try/except ImportError patterns throughout the codebase.
"""

import importlib
# import sys  # Consolidated to common_imports
# from typing import Any, Dict  # Consolidated to common_imports


def safe_import(module_name: str, fallback: Any = None) -> Any:
    """
    Safely import a module with a fallback value.
    
    Args:
        module_name: The name of the module to import
        fallback: Value to return if import fails
        
    Returns:
        The imported module or the fallback value
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return fallback


def conditional_import(module_name: str, attribute: str = None, fallback_class: Any = None) -> Any:
    """
    Conditionally import a module attribute with fallback.
    
    Args:
        module_name: The name of the module to import
        attribute: Specific attribute to get from the module
        fallback_class: Fallback class/value if import fails
        
    Returns:
        The imported attribute or fallback class
    """
    try:
        module = importlib.import_module(module_name)
        if attribute:
            return getattr(module, attribute)
        return module
    except (ImportError, AttributeError):
        return fallback_class


def optional_import(module_name: str, globals_dict: Dict[str, Any] = None) -> bool:
    """
    Optionally import a module and add it to globals if successful.
    
    Args:
        module_name: The name of the module to import
        globals_dict: Dictionary to add the module to (typically globals())
        
    Returns:
        True if import was successful, False otherwise
    """
    try:
        module = importlib.import_module(module_name)
        if globals_dict is not None:
            # Extract the last part of the module name for the variable name
            var_name = module_name.split('.')[-1]
            globals_dict[var_name] = module
        return True
    except ImportError:
        return False


def import_with_fallback(primary_module: str, fallback_module: str, attribute: str = None) -> Any:
    """
    Try to import a primary module, falling back to an alternative.
    
    Args:
        primary_module: First choice module to import
        fallback_module: Alternative module if primary fails
        attribute: Specific attribute to get from the module
        
    Returns:
        The imported module/attribute
    """
    for module_name in [primary_module, fallback_module]:
        try:
            module = importlib.import_module(module_name)
            if attribute:
                return getattr(module, attribute)
            return module
        except (ImportError, AttributeError):
            continue
    
    raise ImportError(f"Could not import either {primary_module} or {fallback_module}")


def lazy_import(module_name: str):
    """
    Create a lazy import that only imports when first accessed.
    
    Args:
        module_name: The name of the module to import lazily
        
    Returns:
        A LazyModule instance
    """
    return LazyModule(module_name)


class LazyModule:
    """A module that's imported only when first accessed."""
    
    def __init__(self, module_name: str):
        self._module_name = module_name
        self._module = None
    
    def __getattr__(self, name: str):
        if self._module is None:
            try:
                self._module = importlib.import_module(self._module_name)
            except ImportError as e:
                raise ImportError(f"Failed to import {self._module_name}: {e}")
        return getattr(self._module, name)


def check_dependencies(dependencies: Dict[str, str]) -> Dict[str, bool]:
    """
    Check if multiple dependencies are available.
    
    Args:
        dependencies: Dict mapping dependency names to module names
        
    Returns:
        Dict mapping dependency names to availability status
    """
    status = {}
    for dep_name, module_name in dependencies.items():
        try:
            importlib.import_module(module_name)
            status[dep_name] = True
        except ImportError:
            status[dep_name] = False
    return status


# Common imports with fallbacks for frequently used modules
def get_langchain():
    """Get LangChain imports with fallbacks."""
    return conditional_import('langchain', fallback_class=None)


def get_openai():
    """Get OpenAI imports with fallbacks."""
    return conditional_import('openai', fallback_class=None)


def get_chromadb():
    """Get ChromaDB imports with fallbacks."""
    return conditional_import('chromadb', fallback_class=None)


def get_supabase():
    """Get Supabase imports with fallbacks."""
    return conditional_import('supabase', fallback_class=None)


# Pre-configured common dependency checks
COMMON_DEPENDENCIES = {
    'langchain': 'langchain',
    'openai': 'openai', 
    'chromadb': 'chromadb',
    'supabase': 'supabase',
    'pytest': 'pytest',
    'fastapi': 'fastapi',
    'pydantic': 'pydantic',
    'redis': 'redis',
    'yaml': 'yaml',
    'schedule': 'schedule'
}


def check_common_dependencies() -> Dict[str, bool]:
    """Check availability of commonly used dependencies."""
    return check_dependencies(COMMON_DEPENDENCIES)


def ensure_path_setup():
    """Ensure proper path setup for imports (replaces sys.path.append patterns)."""
#     from pathlib import Path  # Consolidated to common_imports
    
    # Add project root to path if not already present
    project_root = Path(__file__).parent.parent.parent.parent
    project_root_str = str(project_root)
    
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    
    # Add src directory to path if not already present  
    src_path = project_root / "src"
    src_path_str = str(src_path)
    
    if src_path_str not in sys.path:
        sys.path.insert(0, src_path_str)