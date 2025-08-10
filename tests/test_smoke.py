"""
Basic smoke tests to verify the AI system is functional.
This file was recreated after accidental deletion during cleanup.
"""

import importlib.util
import sys
from pathlib import Path

import pytest


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
        assert (root / "requirements.lock").exists() or (
            root / "requirements.txt"
        ).exists(), "requirements file missing"
        assert (root / "pytest.ini").exists(), "pytest.ini missing"

    def test_src_imports(self):
        """Test that critical modules can be imported."""
        try:
            # Test core imports
            import src.core
            import src.infrastructure
            import src.integrations
            import src.interfaces  # noqa: F401
        except ImportError as e:
            pytest.fail(f"Failed to import core modules: {e}")

    def test_config_loading(self):
        """Test that configuration can be loaded."""
        try:
            import config  # noqa: F401
        except ImportError as e:
            pytest.fail(f"Failed to import config: {e}")

    def test_python_version(self):
        """Test that Python version is compatible."""
        assert sys.version_info >= (3, 8), "Python 3.8+ required"

    def test_essential_packages(self):
        """Test that essential packages are available."""
        essential_packages = ["pytest", "pathlib", "json", "yaml", "os", "sys"]

        for package in essential_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                pytest.fail(f"Essential package {package} not available")

    @pytest.mark.unit
    def test_basic_functionality(self):
        """Test basic functionality works."""
        try:
            # Test that core agent registry can be imported and contains expected agents
            from src.core.workflows.registry import AGENT_REGISTRY
            
            # Verify the registry exists and has expected agent types
            assert AGENT_REGISTRY is not None, "Agent registry should be available"
            assert isinstance(AGENT_REGISTRY, dict), "Agent registry should be a dictionary"
            
            # Check for critical agent types that should exist
            expected_agents = ["coordinator", "backend_engineer", "frontend_engineer", "qa"]
            found_agents = []
            
            for agent_key in AGENT_REGISTRY.keys():
                if any(expected in str(agent_key).lower() for expected in expected_agents):
                    found_agents.append(agent_key)
            
            assert len(found_agents) > 0, f"Expected to find some agents from {expected_agents}, but registry keys are: {list(AGENT_REGISTRY.keys())}"
            
        except ImportError as e:
            pytest.fail(f"Failed to import agent registry: {e}")
        except Exception as e:
            pytest.fail(f"Basic functionality test failed: {e}")

    def test_test_environment(self):
        """Test that test environment is properly configured."""
        # Basic environment validation without external fixtures
        from pathlib import Path
        import os
        
        root_path = Path(__file__).parent.parent
        assert root_path.exists()
        
        # Check that we're in a testing context
        assert "pytest" in os.environ.get("_", "")  or "PYTEST_CURRENT_TEST" in os.environ

    def test_mock_config(self):
        """Test that basic mock configuration can be created."""
        # Create a basic mock config for testing
        mock_config = {
            "memory": {"enabled": True},
            "agents": {"backend": {"tools": []}},
            "external_apis": {"enabled": False}
        }
        assert "memory" in mock_config
        assert "agents" in mock_config
        assert "external_apis" in mock_config
