
from src.infrastructure.utils.common_imports import (
    Path,
    datetime,
    json,
    logging,
    os,
    sys
)
"""
Common Utilities

Provides frequently used utility functions to reduce code duplication
throughout the system.
"""

# import json  # Consolidated to common_imports
# import logging  # Consolidated to common_imports
# import os  # Consolidated to common_imports
# import sys  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
from typing import Dict, List, Any, Union


def setup_logging(name: str = None, level: str = None) -> logging.Logger:
    """
    Setup standardized logging configuration
    
    Args:
        name: Logger name (defaults to __name__ of caller)
        level: Log level (defaults to environment variable or INFO)
    
    Returns:
        Configured logger instance
    """
    if level is None:
        level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level, logging.INFO)
    
    # Setup basic configuration if not already configured
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Get logger with specified name
    logger_name = name or 'ai_system'
    logger = logging.getLogger(logger_name)
    logger.setLevel(numeric_level)
    
    return logger


def get_project_root() -> Path:
    """
    Get the project root directory
    
    Returns:
        Path to project root
    """
    # Try to find project root by looking for key files
    current = Path(__file__).parent
    
    while current != current.parent:
        # Look for project indicators
        if any((current / indicator).exists() for indicator in 
               ['main.py', 'setup.py', 'pyproject.toml', '.git', 'README.md']):
            return current
        current = current.parent
    
    # Fallback to going up from current file location
    return Path(__file__).parent.parent.parent


def add_project_to_path():
    """Add project root to Python path if not already present"""
    project_root = str(get_project_root())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def read_json(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Read JSON file safely
    
    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist or is invalid
    
    Returns:
        Parsed JSON data or default value
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not read JSON file {file_path}: {e}")
        return default


def write_json(file_path: Union[str, Path], data: Any, 
               indent: int = 2, ensure_dir: bool = True) -> bool:
    """
    Write data to JSON file safely
    
    Args:
        file_path: Path to write JSON file
        data: Data to serialize
        indent: JSON indentation
        ensure_dir: Create parent directories if needed
    
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(file_path)
        
        if ensure_dir:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
        
        return True
        
    except (PermissionError, OSError, TypeError) as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Could not write JSON file {file_path}: {e}")
        return False


def safe_get_env(key: str, default: str = "", required: bool = False, 
                 env_type: type = str) -> Any:
    """
    Safely get environment variable with type conversion
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Raise error if not found and no default
        env_type: Type to convert to (str, int, bool, float)
    
    Returns:
        Environment variable value converted to specified type
    
    Raises:
        ValueError: If required and not found, or conversion fails
    """
    value = os.environ.get(key)
    
    if value is None:
        if required:
            raise ValueError(f"Required environment variable '{key}' not found")
        return default
    
    # Type conversion
    try:
        if env_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif env_type == int:
            return int(value)
        elif env_type == float:
            return float(value)
        else:
            return str(value)
    except (ValueError, TypeError) as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not convert env var '{key}' to {env_type.__name__}: {e}")
        return default


def is_test_mode() -> bool:
    """
    Check if running in test mode
    
    Returns:
        True if in test mode, False otherwise
    """
    return any([
        os.environ.get("PYTEST_CURRENT_TEST") is not None,
        os.environ.get("TESTING", "0") == "1",
        os.environ.get("TEST_MODE", "false").lower() == "true",
        'pytest' in sys.modules,
        'unittest' in sys.modules
    ])


def is_development_mode() -> bool:
    """
    Check if running in development mode
    
    Returns:
        True if in development mode, False otherwise
    """
    env = os.environ.get("ENVIRONMENT", "development").lower()
    return env in ("development", "dev", "local")


def is_production_mode() -> bool:
    """
    Check if running in production mode
    
    Returns:
        True if in production mode, False otherwise
    """
    env = os.environ.get("ENVIRONMENT", "development").lower()
    return env in ("production", "prod")


def format_api_response(data: Any = None, status: str = "success", 
                       message: str = None, errors: List[str] = None,
                       timestamp: bool = True) -> Dict[str, Any]:
    """
    Format standardized API response
    
    Args:
        data: Response data
        status: Response status (success, error, warning)
        message: Optional message
        errors: List of error messages
        timestamp: Include timestamp in response
    
    Returns:
        Formatted response dictionary
    """
    response = {
        "status": status,
        "data": data
    }
    
    if message:
        response["message"] = message
    
    if errors:
        response["errors"] = errors
    
    if timestamp:
        response["timestamp"] = datetime.now().isoformat()
    
    return response


def safe_execute(func: callable, *args, default=None, 
                log_errors: bool = True, **kwargs) -> Any:
    """
    Execute function safely with error handling
    
    Args:
        func: Function to execute
        *args: Function arguments
        default: Default value on error
        log_errors: Whether to log errors
        **kwargs: Function keyword arguments
    
    Returns:
        Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger = logging.getLogger(__name__)
            logger.error(f"Error executing {func.__name__}: {e}")
        return default


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, creating it if necessary
    
    Args:
        path: Directory path
    
    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Get file size in megabytes
    
    Args:
        file_path: Path to file
    
    Returns:
        File size in MB, or 0 if file doesn't exist
    """
    try:
        return Path(file_path).stat().st_size / (1024 * 1024)
    except (FileNotFoundError, OSError):
        return 0.0


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


class EnvironmentConfig:
    """Centralized environment configuration management"""
    
    @staticmethod
    def get_api_base_url() -> str:
        """Get API base URL"""
        return safe_get_env("API_BASE_URL", "http://localhost:5000")
    
    @staticmethod
    def get_database_url() -> str:
        """Get database URL"""
        return safe_get_env("DATABASE_URL", "")
    
    @staticmethod
    def get_redis_url() -> str:
        """Get Redis URL"""
        return safe_get_env("REDIS_URL", "redis://localhost:6379")
    
    @staticmethod
    def get_encryption_key() -> str:
        """Get encryption key"""
        # Check both AI_SYSTEM_ENCRYPTION_KEY and ENCRYPTION_KEY for compatibility
        key = safe_get_env("AI_SYSTEM_ENCRYPTION_KEY", "")
        if not key:
            key = safe_get_env("ENCRYPTION_KEY", required=is_production_mode())
        return key
    
    @staticmethod
    def get_secret_key() -> str:
        """Get secret key for sessions/auth"""
        # Check both AI_SYSTEM_SECRET_KEY and SECRET_KEY for compatibility
        key = safe_get_env("AI_SYSTEM_SECRET_KEY", "")
        if not key:
            key = safe_get_env("SECRET_KEY", "")
        
        if not key:
            if is_production_mode():
                raise RuntimeError("AI_SYSTEM_SECRET_KEY environment variable is required in production")
            else:
                # In development, use a predictable default key
                return "dev-secret-change-in-production"
        
        return key
    
    @staticmethod
    def get_openai_api_key() -> str:
        """Get OpenAI API key"""
        return safe_get_env("OPENAI_API_KEY", required=not is_test_mode())
    
    @staticmethod
    def get_log_level() -> str:
        """Get logging level"""
        return safe_get_env("LOG_LEVEL", "INFO").upper()
    
    @staticmethod
    def get_github_token() -> str:
        """Get GitHub token"""
        return safe_get_env("GITHUB_TOKEN", "")
    
    @staticmethod
    def get_github_repository() -> str:
        """Get GitHub repository"""
        return safe_get_env("GITHUB_REPOSITORY", "artesanato-shop/artesanato-ecommerce")
    
    @staticmethod
    def get_supabase_url() -> str:
        """Get Supabase URL"""
        return safe_get_env("SUPABASE_URL", "")
    
    @staticmethod
    def get_supabase_key() -> str:
        """Get Supabase key"""
        return safe_get_env("SUPABASE_KEY", "")
    
    @staticmethod
    def is_testing() -> bool:
        """Check if running in testing mode"""
        return safe_get_env("TESTING", "0", env_type=bool) or is_test_mode()


# Create default logger for this module
logger = setup_logging(__name__)