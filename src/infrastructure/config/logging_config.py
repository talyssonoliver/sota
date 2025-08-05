#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import (
    Path,
    datetime,
    logging,
    sys
)
"""
Centralized Logging Configuration

This module provides centralized logging setup to eliminate duplication
of logging configuration patterns throughout the codebase.
"""

# import logging  # Consolidated to common_imports
# import sys  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports

from src.infrastructure.utils.logging_utils import setup_logging as common_setup_logging


def setup_logging(
    name: str = None,
    level: int = logging.INFO,
    format_string: str = None,
    log_file: str = None,
    console_output: bool = True,
    verbose: bool = False
) -> logging.Logger:
    """
    Set up centralized logging configuration.
    
    Args:
        name: Logger name (defaults to caller's __name__)
        level: Logging level (default: INFO)
        format_string: Custom format string
        log_file: Optional log file path
        console_output: Whether to output to console
        verbose: Enable verbose logging (sets level to DEBUG)
        
    Returns:
        Configured logger instance
        
    Note:
        This is a wrapper around the common_utils setup_logging function
        for backward compatibility while providing additional features.
    """
    # For simple cases, use the common setup_logging function
    if (log_file is None and 
        console_output and 
        format_string is None):
        # Convert logging level to string for common_utils
        level_name = logging.getLevelName(level)
        if verbose:
            level_name = "DEBUG"
        return common_setup_logging(name, level_name)
    
    # For complex cases with file logging, keep the original implementation
    # Handle verbose mode
    if verbose:
        level = logging.DEBUG
    
    # Default format string
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Get logger name
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'unknown')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplication
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_project_logger(
    module_name: str,
    level: int = logging.INFO,
    include_file_logging: bool = False
) -> logging.Logger:
    """
    Get a standardized project logger.
    
    Args:
        module_name: Name of the module (typically __name__)
        level: Logging level
        include_file_logging: Whether to include file logging
        
    Returns:
        Configured logger
    """
    log_file = None
    if include_file_logging:
        # Create logs directory in project root
        project_root = Path(__file__).parent.parent.parent.parent
        logs_dir = project_root / "logs"
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = logs_dir / f"{module_name.replace('.', '_')}_{timestamp}.log"
    
    return setup_logging(
        name=module_name,
        level=level,
        log_file=str(log_file) if log_file else None
    )


def setup_test_logging(test_name: str = None) -> logging.Logger:
    """
    Set up logging for tests with appropriate level and format.
    
    Args:
        test_name: Name of the test (optional)
        
    Returns:
        Test logger
    """
    if test_name is None:
        import inspect
        frame = inspect.currentframe().f_back
        test_name = frame.f_globals.get('__name__', 'test')
    
    return setup_logging(
        name=f"test.{test_name}",
        level=logging.WARNING,  # Reduce noise in tests
        format_string='%(name)s - %(levelname)s - %(message)s'
    )


def setup_agent_logging(agent_name: str, task_id: str = None) -> logging.Logger:
    """
    Set up logging for agents with task-specific configuration.
    
    Args:
        agent_name: Name of the agent
        task_id: Optional task ID for context
        
    Returns:
        Agent logger
    """
    logger_name = f"agent.{agent_name}"
    if task_id:
        logger_name += f".{task_id}"
    
    # Agents get file logging by default
    project_root = Path(__file__).parent.parent.parent.parent
    logs_dir = project_root / "logs" / "agents"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"{agent_name}_{timestamp}.log"
    
    return setup_logging(
        name=logger_name,
        level=logging.INFO,
        log_file=str(log_file),
        format_string='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )


def setup_workflow_logging(workflow_name: str) -> logging.Logger:
    """
    Set up logging for workflows.
    
    Args:
        workflow_name: Name of the workflow
        
    Returns:
        Workflow logger
    """
    logger_name = f"workflow.{workflow_name}"
    
    # Workflows get file logging
    project_root = Path(__file__).parent.parent.parent.parent
    logs_dir = project_root / "logs" / "workflows"
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f"{workflow_name}_{timestamp}.log"
    
    return setup_logging(
        name=logger_name,
        level=logging.INFO,
        log_file=str(log_file)
    )


def configure_external_loggers():
    """Configure logging levels for external libraries to reduce noise."""
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


# Pre-configured loggers for common use cases
def get_main_logger() -> logging.Logger:
    """Get the main application logger."""
    return get_project_logger("main", include_file_logging=True)


def get_api_logger() -> logging.Logger:
    """Get the API logger."""
    return get_project_logger("api", include_file_logging=True)


def get_memory_logger() -> logging.Logger:
    """Get the memory engine logger.""" 
    return get_project_logger("memory", include_file_logging=True)


def get_infrastructure_logger() -> logging.Logger:
    """Get the infrastructure logger."""
    return get_project_logger("infrastructure", include_file_logging=True)


# Initialize external logger configuration
configure_external_loggers()