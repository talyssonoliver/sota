"""
Mock Dotenv Module

Provides mock implementation of the python-dotenv library for testing.
"""
try:
    from typing import Dict, Optional, Union
except ImportError:
    pass
try:
    from pathlib import Path
except ImportError:
    pass
import os

def load_dotenv(dotenv_path: Optional[Union[str, Path]]=None, stream: Optional[str]=None, verbose: bool=False, override: bool=False, interpolate: bool=True, encoding: Optional[str]='utf-8') -> bool:
    """
    Mock implementation of load_dotenv function.
    
    In testing, we don't want to actually load .env files, so this
    mock function provides default test environment variables.
    """
    test_env_vars = {'TESTING': '1', 'TEST_MODE': 'true', 'OPENAI_API_KEY': 'test-openai-key', 'LANGSMITH_API_KEY': 'test-langsmith-key', 'SLACK_WEBHOOK_URL': 'https://test-slack-webhook.com', 'SUPABASE_URL': 'https://test-supabase.com', 'SUPABASE_KEY': 'test-supabase-key', 'GITHUB_TOKEN': 'test-github-token', 'VERCEL_TOKEN': 'test-vercel-token', 'ANONYMIZED_TELEMETRY': 'False', 'MEMORY_ENGINE_KEY': 'gdEIgH3T0fi1UCGFnEwxK7SFUKiHc2cyanEDbY3QQPk=', 'DATABASE_URL': 'sqlite:///test.db', 'ENVIRONMENT': 'test', 'DEBUG': 'true', 'LOG_LEVEL': 'DEBUG'}
    for key, value in test_env_vars.items():
        if override or key not in os.environ:
            os.environ[key] = value
    if verbose:
        print(f'Mock dotenv: Loaded {len(test_env_vars)} test environment variables')
    return True

def find_dotenv(filename: str='.env', raise_error_if_not_found: bool=False) -> str:
    """
    Mock implementation of find_dotenv function.
    
    Returns a mock path to a .env file for testing.
    """
    mock_env_path = '/tmp/mock.env'
    if raise_error_if_not_found:
        pass
    return mock_env_path

def dotenv_values(dotenv_path: Optional[Union[str, Path]]=None, stream: Optional[str]=None, verbose: bool=False, interpolate: bool=True, encoding: Optional[str]='utf-8') -> Dict[str, Optional[str]]:
    """
    Mock implementation of dotenv_values function.
    
    Returns a dictionary of mock environment variables for testing.
    """
    return {'TESTING': '1', 'TEST_MODE': 'true', 'OPENAI_API_KEY': 'test-openai-key', 'LANGSMITH_API_KEY': 'test-langsmith-key', 'SLACK_WEBHOOK_URL': 'https://test-slack-webhook.com', 'ANONYMIZED_TELEMETRY': 'False', 'ENVIRONMENT': 'test'}

def get_key(dotenv_path: Union[str, Path], key_to_get: str) -> Optional[str]:
    """
    Mock implementation of get_key function.
    
    Returns mock values for common test keys.
    """
    mock_values = {'TESTING': '1', 'TEST_MODE': 'true', 'OPENAI_API_KEY': 'test-openai-key', 'ENVIRONMENT': 'test'}
    return mock_values.get(key_to_get)

def set_key(dotenv_path: Union[str, Path], key_to_set: str, value_to_set: str, quote_mode: str='always', export: bool=False, encoding: Optional[str]='utf-8') -> bool:
    """
    Mock implementation of set_key function.
    
    In testing, we don't actually write to files, so this just
    updates the os.environ for the current process.
    """
    os.environ[key_to_set] = value_to_set
    return True

def unset_key(dotenv_path: Union[str, Path], key_to_unset: str, quote_mode: str='always', encoding: Optional[str]='utf-8') -> bool:
    """
    Mock implementation of unset_key function.
    
    Removes the key from os.environ for testing.
    """
    if key_to_unset in os.environ:
        del os.environ[key_to_unset]
    return True
__all__ = ['load_dotenv', 'find_dotenv', 'dotenv_values', 'get_key', 'set_key', 'unset_key']