"""
Input Validation Utilities for AI Agent System

Provides comprehensive input validation and sanitization functions for:
- Task IDs and identifiers
- File paths and directory traversal prevention
- User inputs and content sanitization
- API parameters and JSON/YAML data
- Command line arguments and configuration data

This module centralizes validation logic to prevent injection attacks,
path traversal vulnerabilities, and data integrity issues.
"""

import logging
import re
import os
import inspect
import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from urllib.parse import urlparse

try:
    import yaml
except ImportError:
    # Fallback YAML implementation
    class yaml:
        class YAMLError(Exception):
            pass
        
        @staticmethod
        def safe_load(stream):
            return {}
        
        @staticmethod
        def dump(data, stream=None):
            if stream:
                stream.write(str(data))
            return str(data)

logger = logging.getLogger(__name__)

# Security constants
MAX_FILE_PATH_LENGTH = 1000
MAX_STRING_LENGTH = 10000
MAX_JSON_SIZE = 1000000  # 1MB
ALLOWED_FILE_EXTENSIONS = {'.json', '.yaml', '.yml', '.md', '.txt', '.py', '.js', '.ts', '.css', '.html'}
DANGEROUS_PATTERNS = [
    r'\.\./',  # Path traversal
    r'\.\.\.',  # Alternative path traversal
    r'[<>:"|\?*]',  # Invalid filename characters
    r'<script[^>]*>.*?</script>',  # Script tags
    r'javascript:',  # JavaScript protocol
    r'vbscript:',  # VBScript protocol
    r'on\w+\s*=',  # Event handlers
]

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class InputValidator:
    """Comprehensive input validation and sanitization."""
    
    def __init__(self):
        """Initialize validator with security patterns."""
        self.task_id_pattern = re.compile(r'^[A-Z]{2,4}-\d{1,4}[a-zA-Z]?$')
        self.checkpoint_id_pattern = re.compile(r'^hitl_[A-Z]{2,4}-\d{1,4}_[a-zA-Z0-9]{8,}$')
        self.agent_type_pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
        self.reviewer_name_pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_. -]{0,49}$')
        
        # Compile dangerous patterns for performance
        self.dangerous_compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in DANGEROUS_PATTERNS]
    
    def validate_task_id(self, task_id: str) -> str:
        """
        Validate and normalize task ID.
        
        Args:
            task_id: Task identifier to validate
            
        Returns:
            Normalized task ID
            
        Raises:
            ValidationError: If task ID is invalid
        """
        if not task_id or not isinstance(task_id, str):
            raise ValidationError("Task ID must be a non-empty string")
        
        task_id = task_id.strip().upper()
        
        if len(task_id) > 20:
            raise ValidationError("Task ID too long (max 20 characters)")
        
        if not self.task_id_pattern.match(task_id):
            raise ValidationError(
                f"Invalid task ID format: {task_id}. "
                "Expected format: PREFIX-NUMBER (e.g., BE-07, FE-123, TL-01)"
            )
        
        logger.debug(f"Validated task ID: {task_id}")
        return task_id
    
    def validate_checkpoint_id(self, checkpoint_id: str) -> str:
        """
        Validate checkpoint ID.
        
        Args:
            checkpoint_id: Checkpoint identifier to validate
            
        Returns:
            Validated checkpoint ID
            
        Raises:
            ValidationError: If checkpoint ID is invalid
        """
        if not checkpoint_id or not isinstance(checkpoint_id, str):
            raise ValidationError("Checkpoint ID must be a non-empty string")
        
        checkpoint_id = checkpoint_id.strip()
        
        if len(checkpoint_id) > 100:
            raise ValidationError("Checkpoint ID too long (max 100 characters)")
        
        if not self.checkpoint_id_pattern.match(checkpoint_id):
            raise ValidationError(
                f"Invalid checkpoint ID format: {checkpoint_id}. "
                "Expected format: hitl_TASK-ID_HASH"
            )
        
        logger.debug(f"Validated checkpoint ID: {checkpoint_id}")
        return checkpoint_id
    
    def validate_agent_type(self, agent_type: str) -> str:
        """
        Validate agent type.
        
        Args:
            agent_type: Agent type to validate
            
        Returns:
            Validated agent type
            
        Raises:
            ValidationError: If agent type is invalid
        """
        if not agent_type or not isinstance(agent_type, str):
            raise ValidationError("Agent type must be a non-empty string")
        
        agent_type = agent_type.strip().lower()
        
        if len(agent_type) > 50:
            raise ValidationError("Agent type too long (max 50 characters)")
        
        if not self.agent_type_pattern.match(agent_type):
            raise ValidationError(
                f"Invalid agent type: {agent_type}. "
                "Must contain only letters, numbers, and underscores"
            )
        
        # Validate against known agent types
        valid_agent_types = {
            'backend', 'frontend', 'qa', 'technical', 'doc', 'coordinator',
            'backend_engineer', 'frontend_engineer', 'technical_lead',
            'documentation', 'be', 'fe', 'tl', 'co', 'qa'
        }
        
        if agent_type not in valid_agent_types:
            logger.warning(f"Unknown agent type: {agent_type}")
            # Don't raise error for unknown types, just warn
        
        logger.debug(f"Validated agent type: {agent_type}")
        return agent_type
    
    def validate_reviewer_name(self, reviewer: str) -> str:
        """
        Validate reviewer name.
        
        Args:
            reviewer: Reviewer name to validate
            
        Returns:
            Validated reviewer name
            
        Raises:
            ValidationError: If reviewer name is invalid
        """
        if not reviewer or not isinstance(reviewer, str):
            raise ValidationError("Reviewer name must be a non-empty string")
        
        reviewer = reviewer.strip()
        
        if len(reviewer) > 50:
            raise ValidationError("Reviewer name too long (max 50 characters)")
        
        if not self.reviewer_name_pattern.match(reviewer):
            raise ValidationError(
                f"Invalid reviewer name: {reviewer}. "
                "Must start with letter and contain only letters, numbers, spaces, dots, dashes, underscores"
            )
        
        logger.debug(f"Validated reviewer name: {reviewer}")
        return reviewer
    
    def validate_file_path(self, file_path: str, must_exist: bool = True, 
                          allowed_extensions: Optional[List[str]] = None) -> Path:
        """
        Validate file path for security and existence.
        
        Args:
            file_path: File path to validate
            must_exist: Whether file must exist
            allowed_extensions: List of allowed file extensions
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If file path is invalid or dangerous
        """
        if not file_path or not isinstance(file_path, str):
            raise ValidationError("File path must be a non-empty string")
        
        if len(file_path) > MAX_FILE_PATH_LENGTH:
            raise ValidationError(f"File path too long (max {MAX_FILE_PATH_LENGTH} characters)")
        
        # Check for dangerous patterns (but allow temp files)
        is_temp_file = (
            file_path.startswith('/tmp/') or 
            file_path.startswith('/var/folders/') or
            'temp' in file_path.lower() or
            'tmp' in file_path.lower()
        )
        
        # Check for path traversal patterns specifically
        path_traversal_patterns = [
            r'\.\./',  # ../
            r'\.\.\.',  # ...
            r'\.\.\\',  # ..\
            r'%2e%2e%2f',  # URL encoded ../
            r'%2e%2e\\',   # URL encoded ..\
            r'....//....//....//etc',  # Double encoding attempts
        ]
        
        for pattern in path_traversal_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                raise ValidationError(f"Path traversal pattern detected in file path: {file_path}")
        
        if not is_temp_file:
            for pattern in self.dangerous_compiled_patterns:
                if pattern.search(file_path):
                    raise ValidationError(f"Dangerous pattern detected in file path: {file_path}")
        
        # Normalize path
        try:
            path = Path(file_path).resolve()
        except Exception as e:
            raise ValidationError(f"Invalid file path: {file_path} - {e}")
        
        # Ensure path stays within allowed directories
        import tempfile
        allowed_base_paths = [
            Path.cwd(),
            Path.cwd() / 'data',
            Path.cwd() / 'storage',
            Path.cwd() / 'outputs',
            Path.cwd() / 'tasks',
            Path.cwd() / 'config',
            Path.cwd() / 'tests',
            Path.cwd() / 'build',
            Path('/tmp'),  # For temporary files (Unix)
            Path('/var/folders'),  # macOS temporary files
            Path(tempfile.gettempdir()),  # System temp directory (cross-platform)
        ]
        
        # Check if path is under allowed directories
        path_allowed = False
        for base_path in allowed_base_paths:
            try:
                path.relative_to(base_path.resolve())
                path_allowed = True
                break
            except ValueError:
                continue
        
        if not path_allowed:
            raise ValidationError(f"File path outside allowed directories: {file_path}")
        
        # Check file extension if specified
        if allowed_extensions:
            if path.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
                raise ValidationError(f"File extension not allowed: {path.suffix}")
        elif path.suffix.lower() not in ALLOWED_FILE_EXTENSIONS:
            logger.warning(f"Unusual file extension: {path.suffix}")
        
        # Check existence if required
        if must_exist and not path.exists():
            raise ValidationError(f"File does not exist: {file_path}")
        
        logger.debug(f"Validated file path: {path}")
        return path
    
    def validate_string_content(self, content: str, max_length: int = MAX_STRING_LENGTH,
                               allow_html: bool = False) -> str:
        """
        Validate and sanitize string content.
        
        Args:
            content: String content to validate
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML content
            
        Returns:
            Sanitized string content
            
        Raises:
            ValidationError: If content is invalid
        """
        if not isinstance(content, str):
            raise ValidationError("Content must be a string")
        
        if len(content) > max_length:
            raise ValidationError(f"Content too long (max {max_length} characters)")
        
        # Check for dangerous patterns if HTML not allowed
        if not allow_html:
            # First check for SQL injection patterns
            sql_patterns = [
                r"';?\s*DROP\s+TABLE",
                r"'\s*OR\s+'1'\s*=\s*'1",
                r"UNION\s+SELECT",
                r"';\s*INSERT\s+INTO",
                r"--\s*$"
            ]
            
            for pattern in sql_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    logger.warning(f"SQL injection pattern detected: {pattern}")
                    content = re.sub(pattern, '[FILTERED]', content, flags=re.IGNORECASE)
            
            # Then check other dangerous patterns
            for pattern in self.dangerous_compiled_patterns:
                if pattern.search(content):
                    logger.warning(f"Potentially dangerous content detected: {pattern.pattern}")
                    # Sanitize rather than reject
                    content = pattern.sub('', content)
        
        # Basic sanitization
        content = content.strip()
        
        # Remove null bytes and control characters
        content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
        
        logger.debug(f"Validated string content: {len(content)} characters")
        return content
    
    def validate_json_data(self, data: Union[str, Dict, List], max_size: int = MAX_JSON_SIZE) -> Dict:
        """
        Validate JSON data for size and structure.
        
        Args:
            data: JSON data to validate (string or object)
            max_size: Maximum allowed size in bytes
            
        Returns:
            Parsed JSON object
            
        Raises:
            ValidationError: If JSON is invalid
        """
        if isinstance(data, str):
            if len(data.encode('utf-8')) > max_size:
                raise ValidationError(f"JSON data too large (max {max_size} bytes)")
            
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON: {e}")
        else:
            parsed_data = data
        
        # Validate parsed data size
        try:
            serialized = json.dumps(parsed_data)
            if len(serialized.encode('utf-8')) > max_size:
                raise ValidationError(f"JSON data too large (max {max_size} bytes)")
        except (TypeError, ValueError) as e:
            raise ValidationError(f"JSON serialization error: {e}")
        
        logger.debug(f"Validated JSON data: {len(serialized)} bytes")
        return parsed_data
    
    def validate_yaml_data(self, data: Union[str, Dict], max_size: int = MAX_JSON_SIZE) -> Dict:
        """
        Validate YAML data for size and structure.
        
        Args:
            data: YAML data to validate (string or object)
            max_size: Maximum allowed size in bytes
            
        Returns:
            Parsed YAML object
            
        Raises:
            ValidationError: If YAML is invalid
        """
        if isinstance(data, str):
            if len(data.encode('utf-8')) > max_size:
                raise ValidationError(f"YAML data too large (max {max_size} bytes)")
            
            try:
                parsed_data = yaml.safe_load(data)
            except yaml.YAMLError as e:
                raise ValidationError(f"Invalid YAML: {e}")
        else:
            parsed_data = data
        
        # Validate parsed data size
        try:
            serialized = yaml.dump(parsed_data)
            if len(serialized.encode('utf-8')) > max_size:
                raise ValidationError(f"YAML data too large (max {max_size} bytes)")
        except (TypeError, ValueError) as e:
            raise ValidationError(f"YAML serialization error: {e}")
        
        logger.debug(f"Validated YAML data: {len(serialized)} bytes")
        return parsed_data
    
    def validate_integer_range(self, value: Union[str, int], min_val: int = 0, 
                              max_val: int = 1000000) -> int:
        """
        Validate integer within specified range.
        
        Args:
            value: Integer value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Validated integer
            
        Raises:
            ValidationError: If integer is invalid or out of range
        """
        try:
            if isinstance(value, str):
                int_value = int(value.strip())
            else:
                int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid integer: {value}")
        
        if int_value < min_val or int_value > max_val:
            raise ValidationError(f"Integer out of range: {int_value} (must be {min_val}-{max_val})")
        
        logger.debug(f"Validated integer: {int_value}")
        return int_value
    
    def validate_url(self, url: str, allowed_schemes: Optional[List[str]] = None) -> str:
        """
        Validate URL for security and format.
        
        Args:
            url: URL to validate
            allowed_schemes: List of allowed URL schemes
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If URL is invalid
        """
        if not url or not isinstance(url, str):
            raise ValidationError("URL must be a non-empty string")
        
        url = url.strip()
        
        if len(url) > 2000:
            raise ValidationError("URL too long (max 2000 characters)")
        
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValidationError(f"Invalid URL format: {e}")
        
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError("URL must have scheme and network location")
        
        allowed_schemes = allowed_schemes or ['http', 'https']
        if parsed.scheme.lower() not in allowed_schemes:
            raise ValidationError(f"URL scheme not allowed: {parsed.scheme}")
        
        # Check for dangerous patterns in URL
        for pattern in self.dangerous_compiled_patterns:
            if pattern.search(url):
                raise ValidationError(f"Dangerous pattern detected in URL: {url}")
        
        logger.debug(f"Validated URL: {url}")
        return url
    
    def validate_command_args(self, args: argparse.Namespace) -> argparse.Namespace:
        """
        Validate command line arguments for security.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Validated arguments
            
        Raises:
            ValidationError: If arguments are invalid
        """
        # Validate common argument types
        for attr_name in dir(args):
            if attr_name.startswith('_'):
                continue
            
            value = getattr(args, attr_name)
            if value is None:
                continue
            
            # Validate task IDs
            if 'task_id' in attr_name.lower() and isinstance(value, str):
                try:
                    setattr(args, attr_name, self.validate_task_id(value))
                except ValidationError as e:
                    raise ValidationError(f"Invalid {attr_name}: {e}")
            
            # Validate checkpoint IDs
            elif 'checkpoint_id' in attr_name.lower() and isinstance(value, str):
                try:
                    setattr(args, attr_name, self.validate_checkpoint_id(value))
                except ValidationError as e:
                    raise ValidationError(f"Invalid {attr_name}: {e}")
            
            # Validate reviewer names
            elif 'reviewer' in attr_name.lower() and isinstance(value, str):
                try:
                    setattr(args, attr_name, self.validate_reviewer_name(value))
                except ValidationError as e:
                    raise ValidationError(f"Invalid {attr_name}: {e}")
            
            # Validate file paths
            elif 'path' in attr_name.lower() or 'file' in attr_name.lower() or 'output' in attr_name.lower():
                if isinstance(value, str):
                    try:
                        setattr(args, attr_name, str(self.validate_file_path(value, must_exist=False)))
                    except ValidationError as e:
                        raise ValidationError(f"Invalid {attr_name}: {e}")
            
            # Validate string content
            elif isinstance(value, str):
                try:
                    setattr(args, attr_name, self.validate_string_content(value, max_length=1000))
                except ValidationError as e:
                    raise ValidationError(f"Invalid {attr_name}: {e}")
            
            # Validate integers
            elif isinstance(value, int) and 'level' in attr_name.lower():
                try:
                    setattr(args, attr_name, self.validate_integer_range(value, min_val=0, max_val=10))
                except ValidationError as e:
                    raise ValidationError(f"Invalid {attr_name}: {e}")
        
        logger.debug("Validated command line arguments")
        return args

# Global validator instance
_validator_instance: Optional[InputValidator] = None

def get_validator() -> InputValidator:
    """Get global validator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = InputValidator()
    return _validator_instance

# Convenience functions for common validations
def validate_task_id(task_id: str) -> str:
    """Validate task ID using global validator."""
    return get_validator().validate_task_id(task_id)

def validate_checkpoint_id(checkpoint_id: str) -> str:
    """Validate checkpoint ID using global validator."""
    return get_validator().validate_checkpoint_id(checkpoint_id)

def validate_file_path(file_path: str, must_exist: bool = True) -> Path:
    """Validate file path using global validator."""
    return get_validator().validate_file_path(file_path, must_exist)

def validate_string_content(content: str, max_length: int = MAX_STRING_LENGTH) -> str:
    """Validate string content using global validator."""
    return get_validator().validate_string_content(content, max_length)

def validate_json_data(data: Union[str, Dict]) -> Dict:
    """Validate JSON data using global validator."""
    return get_validator().validate_json_data(data)

def validate_command_args(args: argparse.Namespace) -> argparse.Namespace:
    """Validate command line arguments using global validator."""
    return get_validator().validate_command_args(args)

def validate_integer_range(value: Union[str, int], min_val: int = 0, max_val: int = 1000000, param_name: str = "value") -> int:
    """Validate integer within specified range using global validator."""
    return get_validator().validate_integer_range(value, min_val, max_val)

def validate_reviewer_name(reviewer: str) -> str:
    """Validate reviewer name using global validator."""
    return get_validator().validate_reviewer_name(reviewer)

# Decorator for automatic validation
def validate_inputs(**validation_rules):
    """
    Decorator to automatically validate function inputs.
    
    Args:
        **validation_rules: Dictionary of parameter names to validation functions
        
    Example:
        @validate_inputs(task_id=validate_task_id, file_path=validate_file_path)
        def process_task(task_id: str, file_path: str):
            # Function will receive validated inputs
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get function argument names
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Apply validation rules
            for param_name, validator in validation_rules.items():
                if param_name in bound_args.arguments:
                    try:
                        bound_args.arguments[param_name] = validator(bound_args.arguments[param_name])
                    except ValidationError as e:
                        raise ValidationError(f"Validation failed for {param_name}: {e}")
            
            return func(*bound_args.args, **bound_args.kwargs)
        return wrapper
    return decorator