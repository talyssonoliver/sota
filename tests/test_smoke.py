"""
Basic smoke tests to verify the AI system is functional.
This file was recreated after accidental deletion during cleanup.
"""
import pytest
from pathlib import Path
import importlib.util
import sys

class TestSystemSmoke:
    """Basic smoke tests for the AI system."""
    
    def test_project_structure(self):
        """Test that basic project structure exists."""
        root = Path(__file__).parent.parent
        
        # Check critical directories
        assert (root / "src").exists(), "src directory missing"
        assert (root / "config").exists(), "config directory missing"
        assert (root / "tests").exists(), "tests directory missing"
        
        # Check critical files
        assert (root / "main.py").exists(), "main.py missing"
        # Check for requirements files (project uses requirements.lock instead of requirements.txt)
        assert (root / "requirements.lock").exists() or (root / "requirements.txt").exists(), "requirements file missing"
        assert (root / "pytest.ini").exists(), "pytest.ini missing"
    
    def test_src_imports(self):
        """Test that critical modules can be imported."""
        try:
            # Test core imports
            import src.core
            import src.infrastructure 
            import src.interfaces
            import src.integrations
        except ImportError as e:
            pytest.fail(f"Failed to import core modules: {e}")
    
    def test_config_loading(self):
        """Test that configuration can be loaded."""
        try:
            import config
        except ImportError as e:
            pytest.fail(f"Failed to import config: {e}")
    
    def test_python_version(self):
        """Test that Python version is compatible."""
        assert sys.version_info >= (3, 8), "Python 3.8+ required"
    
    def test_essential_packages(self):
        """Test that essential packages are available."""
        essential_packages = [
            'pytest',
            'pathlib',
            'json',
            'yaml',
            'os',
            'sys'
        ]
        
        for package in essential_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                pytest.fail(f"Essential package {package} not available")
    
    @pytest.mark.unit
    def test_basic_functionality(self):
        """Test basic functionality works."""
        # This is a placeholder - should be replaced with actual functionality tests
        assert True, "Basic functionality test placeholder"
    
    def test_test_environment(self, test_env):
        """Test that test environment is properly configured."""
        assert test_env["testing"] is True
        assert test_env["root_path"].exists()
    
    def test_mock_config(self, mock_config):
        """Test that mock configuration is available."""
        assert "memory" in mock_config
        assert "agents" in mock_config
        assert "external_apis" in mock_config
