"""
Comprehensive patch for dotenv loading issues.

This script patches multiple places where dotenv files are loaded
to prevent Unicode decoding errors from breaking test execution.
"""

import os
import sys
from pathlib import Path
from functools import wraps

def patch_dotenv():
    """
    Apply patches to prevent dotenv Unicode errors by disabling dotenv loading
    """
    os.environ["PYTHON_DOTENV_SKIP_ERRORS"] = "1"
    
    # Simpler approach: Mock import of litellm
    sys.modules['litellm'] = type('MockLiteLLM', (), {})()
    
    # Patch pydantic environment settings
    try:
        import pydantic.v1.env_settings
        
        # Create empty method that returns no env vars
        def patched_read_env_files(self, case_sensitive):
            print("Bypassing pydantic .env file loading")
            return {}
        
        # Replace the method
        pydantic.v1.env_settings.EnvSettingsSource._read_env_files = patched_read_env_files
        print("Successfully patched pydantic's env_settings")
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not patch pydantic: {e}")
    
    # Simply disable dotenv completely by mocking it
    class MockDotEnv:
        @staticmethod
        def load_dotenv(*args, **kwargs):
            print("Bypassing dotenv.load_dotenv()")
            return False
            
        @staticmethod
        def dotenv_values(*args, **kwargs):
            print("Bypassing dotenv.dotenv_values()")
            return {}
            
    sys.modules['dotenv'] = MockDotEnv()
    sys.modules['python_dotenv'] = MockDotEnv()
    
    print("Successfully replaced dotenv modules with mock implementations")
    return True

if __name__ == "__main__":
    patch_dotenv()