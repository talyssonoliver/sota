"""
Centralized Validation Utilities
Common validation functions for input checking and verification
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from typing import Callable, TypeVar
import ipaddress
from urllib.parse import urlparse
import email.utils

T = TypeVar('T')


def validate_email(email_str: str) -> bool:
    """Validate email address format"""
    try:
        parsed = email.utils.parseaddr(email_str)
        return '@' in parsed[1] and '.' in parsed[1].split('@')[1]
    except:
        return False


def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
    """Validate URL format and scheme"""
    try:
        result = urlparse(url)
        if allowed_schemes:
            return result.scheme in allowed_schemes and result.netloc != ''
        return all([result.scheme, result.netloc])
    except:
        return False


def validate_ip(ip_str: str, version: Optional[int] = None) -> bool:
    """Validate IP address"""
    try:
        ip = ipaddress.ip_address(ip_str)
        if version:
            return ip.version == version
        return True
    except:
        return False


def validate_port(port: Union[int, str]) -> bool:
    """Validate port number"""
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except:
        return False


def validate_path(path: Union[str, Path], must_exist: bool = False) -> bool:
    """Validate file/directory path"""
    try:
        path_obj = Path(path)
        if must_exist:
            return path_obj.exists()
        return True
    except:
        return False


def validate_json(json_str: str) -> bool:
    """Validate JSON string"""
    try:
        import json
        json.loads(json_str)
        return True
    except:
        return False


def validate_regex(pattern: str) -> bool:
    """Validate regex pattern"""
    try:
        re.compile(pattern)
        return True
    except:
        return False


def validate_date(
    date_str: str,
    format_str: str = "%Y-%m-%d"
) -> bool:
    """Validate date string"""
    try:
        datetime.strptime(date_str, format_str)
        return True
    except:
        return False


def validate_range(
    value: Union[int, float],
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None
) -> bool:
    """Validate numeric range"""
    if min_val is not None and value < min_val:
        return False
    if max_val is not None and value > max_val:
        return False
    return True


def validate_length(
    value: Union[str, list, dict],
    min_len: Optional[int] = None,
    max_len: Optional[int] = None
) -> bool:
    """Validate length of string/collection"""
    length = len(value)
    if min_len is not None and length < min_len:
        return False
    if max_len is not None and length > max_len:
        return False
    return True


def validate_type(
    value: Any,
    expected_type: Union[type, Tuple[type, ...]]
) -> bool:
    """Validate value type"""
    return isinstance(value, expected_type)


def validate_schema(
    data: Dict[str, Any],
    schema: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Validate data against schema
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check required fields
    required_fields = schema.get('required', [])
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Check field types
    properties = schema.get('properties', {})
    for field, value in data.items():
        if field in properties:
            field_schema = properties[field]
            expected_type = field_schema.get('type')
            
            if expected_type:
                type_map = {
                    'string': str,
                    'integer': int,
                    'number': (int, float),
                    'boolean': bool,
                    'array': list,
                    'object': dict
                }
                
                if expected_type in type_map:
                    if not isinstance(value, type_map[expected_type]):
                        errors.append(
                            f"Field '{field}' expected {expected_type}, "
                            f"got {type(value).__name__}"
                        )
    
    return len(errors) == 0, errors


def check_required(
    data: Dict[str, Any],
    required_fields: List[str]
) -> Tuple[bool, List[str]]:
    """Check if all required fields are present"""
    missing = [field for field in required_fields if field not in data]
    return len(missing) == 0, missing


def check_allowed(
    value: Any,
    allowed_values: List[Any]
) -> bool:
    """Check if value is in allowed list"""
    return value in allowed_values


def is_valid_identifier(identifier: str) -> bool:
    """Check if string is valid Python identifier"""
    return identifier.isidentifier()


def is_valid_uuid(uuid_str: str) -> bool:
    """Check if string is valid UUID"""
    try:
        import uuid
        uuid.UUID(uuid_str)
        return True
    except:
        return False


# Decorator for validation
def validate_input(**validators: Callable) -> Callable:
    """
    Decorator to validate function inputs
    
    Usage:
        @validate_input(
            email=validate_email,
            port=lambda p: validate_port(p)
        )
        def my_function(email: str, port: int):
            pass
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Validate each parameter
            for param_name, validator in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not validator(value):
                        raise ValueError(f"Invalid {param_name}: {value}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
