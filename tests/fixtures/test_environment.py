"""Test environment configuration and setup."""
import os
import sys
from pathlib import Path
from typing import Dict, Any

class EnvironmentManager:
    """Test environment manager."""

    def __init__(self):
        self.config = {}
        self.setup_test_environment()

    def setup_test_environment(self):
        """Setup test environment variables and paths."""
        os.environ['TESTING'] = '1'
        project_root = Path(__file__).parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        self.config.update({'test_data_dir': project_root / 'tests' / 'fixtures' / 'data', 'test_output_dir': project_root / 'tests' / 'output', 'mock_external_apis': True, 'use_memory_engine': False})

    def get_config(self) -> Dict[str, Any]:
        """Get test environment configuration."""
        return self.config.copy()

    def cleanup(self):
        """Cleanup test environment."""
        if 'TESTING' in os.environ:
            del os.environ['TESTING']
test_env = EnvironmentManager()
__all__ = ['EnvironmentManager', 'test_env']