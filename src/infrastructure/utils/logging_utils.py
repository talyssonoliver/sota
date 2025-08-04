"""
Centralized Logging Utilities
Consolidates logging setup and configuration functions from across the codebase
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging.config
from pythonjsonlogger import jsonlogger


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_json: bool = False
) -> logging.Logger:
    """
    Setup logging configuration with consistent format
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logging
        format_json: Whether to use JSON formatting
        
    Returns:
        Configured logger instance
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    if format_json:
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name (usually __name__)
        level: Optional override for log level
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    if level:
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(log_level)
    
    return logger


def create_logger(
    name: str,
    level: str = "INFO",
    handlers: Optional[List[logging.Handler]] = None
) -> logging.Logger:
    """
    Create a new logger with custom configuration
    
    Args:
        name: Logger name
        level: Logging level
        handlers: Optional list of handlers
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    if handlers:
        for handler in handlers:
            logger.addHandler(handler)
    else:
        # Default console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
    
    return logger


def configure_logging(config_dict: Dict[str, Any]) -> None:
    """
    Configure logging from a dictionary configuration
    
    Args:
        config_dict: Logging configuration dictionary
    """
    logging.config.dictConfig(config_dict)


# Convenience function for module-level logger setup
def get_module_logger(module_name: str = None) -> logging.Logger:
    """Get logger for current module with consistent naming"""
    if module_name is None:
        import inspect
        frame = inspect.currentframe().f_back
        module_name = frame.f_globals.get('__name__', 'unknown')
    
    return get_logger(module_name)
