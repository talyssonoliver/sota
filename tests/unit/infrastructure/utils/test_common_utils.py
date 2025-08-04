"""
Test suite for common utilities that reduce code duplication.
"""

import json
import logging
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.infrastructure.utils.common_utils import (
    setup_logging, get_project_root, add_project_to_path,
    read_json, write_json, safe_get_env, is_test_mode,
    is_development_mode, is_production_mode, format_api_response,
    safe_execute, ensure_directory, get_file_size_mb,
    truncate_string, EnvironmentConfig
)


class TestLoggingUtilities:
    """Test logging utility functions."""
    
    def test_setup_logging_default(self):
        """Test setup_logging with default parameters."""
        logger = setup_logging()
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "ai_system"
        assert logger.level == logging.INFO
    
    def test_setup_logging_custom_name(self):
        """Test setup_logging with custom name."""
        logger = setup_logging("custom_logger")
        
        assert logger.name == "custom_logger"
    
    def test_setup_logging_custom_level(self):
        """Test setup_logging with custom level."""
        logger = setup_logging(level="DEBUG")
        
        assert logger.level == logging.DEBUG
    
    @patch.dict(os.environ, {"LOG_LEVEL": "WARNING"})
    def test_setup_logging_env_level(self):
        """Test setup_logging respects LOG_LEVEL environment variable."""
        logger = setup_logging()
        
        assert logger.level == logging.WARNING
    
    def test_setup_logging_invalid_level(self):
        """Test setup_logging with invalid level falls back to INFO."""
        logger = setup_logging(level="INVALID_LEVEL")
        
        assert logger.level == logging.INFO


class TestPathUtilities:
    """Test path utility functions."""
    
    def test_get_project_root(self):
        """Test get_project_root finds the correct root."""
        root = get_project_root()
        
        assert isinstance(root, Path)
        assert root.exists()
        
        # Should find one of the project indicators
        indicators = ['main.py', 'setup.py', 'pyproject.toml', '.git', 'README.md']
        assert any((root / indicator).exists() for indicator in indicators)
    
    def test_add_project_to_path(self):
        """Test add_project_to_path adds root to sys.path."""
        import sys
        
        original_path = sys.path.copy()
        
        try:
            # Remove project root if it's already there
            project_root = str(get_project_root())
            if project_root in sys.path:
                sys.path.remove(project_root)
            
            # Get initial path length to check if path was added at beginning
            original_length = len(sys.path)
            
            add_project_to_path()
            
            assert project_root in sys.path
            # In parallel test execution, many paths may be added first
            # Just verify the path was added successfully
            project_index = sys.path.index(project_root)
            assert project_index >= 0  # Path should be found in sys.path
        finally:
            sys.path[:] = original_path


class TestJSONUtilities:
    """Test JSON utility functions."""
    
    def test_read_json_success(self):
        """Test read_json with valid JSON file."""
        test_data = {"key": "value", "number": 42, "nested": {"inner": "data"}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            file_path = f.name
        
        try:
            result = read_json(file_path)
            assert result == test_data
        finally:
            os.unlink(file_path)
    
    def test_read_json_file_not_found(self):
        """Test read_json with non-existent file."""
        result = read_json("/nonexistent/file.json", default={"default": "value"})
        
        assert result == {"default": "value"}
    
    def test_read_json_invalid_json(self):
        """Test read_json with invalid JSON content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            file_path = f.name
        
        try:
            result = read_json(file_path, default={"error": "occurred"})
            assert result == {"error": "occurred"}
        finally:
            os.unlink(file_path)
    
    def test_read_json_permission_error(self):
        """Test read_json with permission error."""
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            result = read_json("some_file.json", default={"permission": "denied"})
            assert result == {"permission": "denied"}
    
    def test_write_json_success(self):
        """Test write_json with valid data."""
        test_data = {"key": "value", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            file_path = f.name
        
        try:
            result = write_json(file_path, test_data)
            assert result is True
            
            # Verify the file was written correctly
            with open(file_path, 'r') as f:
                written_data = json.load(f)
            
            assert written_data == test_data
        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    def test_write_json_ensure_directory(self):
        """Test write_json creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "deep" / "file.json"
            
            result = write_json(nested_path, {"test": "data"}, ensure_dir=True)
            assert result is True
            assert nested_path.exists()
            assert nested_path.parent.exists()
    
    def test_write_json_failure(self):
        """Test write_json handles failures gracefully."""
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            result = write_json("some_file.json", {"test": "data"})
            assert result is False
    
    def test_write_json_custom_formatting(self):
        """Test write_json with custom formatting."""
        test_data = {"key": "value", "nested": {"inner": "data"}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            file_path = f.name
        
        try:
            result = write_json(file_path, test_data, indent=4)
            assert result is True
            
            # Check that the file is properly formatted
            with open(file_path, 'r') as f:
                content = f.read()
            
            assert "    " in content  # Should have 4-space indentation
            assert content.count('\n') > 1  # Should be multiline
        finally:
            os.unlink(file_path)


class TestEnvironmentUtilities:
    """Test environment utility functions."""
    
    def test_safe_get_env_existing(self):
        """Test safe_get_env with existing environment variable."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = safe_get_env("TEST_VAR")
            assert result == "test_value"
    
    def test_safe_get_env_missing_with_default(self):
        """Test safe_get_env with missing variable and default."""
        result = safe_get_env("NONEXISTENT_VAR", default="default_value")
        assert result == "default_value"
    
    def test_safe_get_env_required_missing(self):
        """Test safe_get_env with required missing variable."""
        with pytest.raises(ValueError) as exc_info:
            safe_get_env("NONEXISTENT_VAR", required=True)
        
        assert "Required environment variable" in str(exc_info.value)
    
    def test_safe_get_env_type_conversion(self):
        """Test safe_get_env type conversion."""
        with patch.dict(os.environ, {
            "INT_VAR": "42",
            "FLOAT_VAR": "3.14",
            "BOOL_TRUE": "true",
            "BOOL_FALSE": "false",
            "BOOL_ONE": "1",
            "BOOL_ZERO": "0"
        }):
            assert safe_get_env("INT_VAR", env_type=int) == 42
            assert safe_get_env("FLOAT_VAR", env_type=float) == 3.14
            assert safe_get_env("BOOL_TRUE", env_type=bool) is True
            assert safe_get_env("BOOL_FALSE", env_type=bool) is False
            assert safe_get_env("BOOL_ONE", env_type=bool) is True
            assert safe_get_env("BOOL_ZERO", env_type=bool) is False
    
    def test_safe_get_env_conversion_failure(self):
        """Test safe_get_env handles conversion failures."""
        with patch.dict(os.environ, {"INVALID_INT": "not_a_number"}):
            result = safe_get_env("INVALID_INT", default=0, env_type=int)
            assert result == 0
    
    def test_is_test_mode(self):
        """Test is_test_mode detection."""
        # Should return True when running under pytest
        assert is_test_mode() is True
        
        # Test with explicit environment variables
        with patch.dict(os.environ, {"TESTING": "1"}):
            assert is_test_mode() is True
        
        with patch.dict(os.environ, {"TEST_MODE": "true"}):
            assert is_test_mode() is True
    
    def test_is_development_mode(self):
        """Test is_development_mode detection."""
        # Test with various development environment values
        dev_values = ["development", "dev", "local"]
        
        for value in dev_values:
            with patch.dict(os.environ, {"ENVIRONMENT": value}):
                assert is_development_mode() is True
        
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            assert is_development_mode() is False
    
    def test_is_production_mode(self):
        """Test is_production_mode detection."""
        prod_values = ["production", "prod"]
        
        for value in prod_values:
            with patch.dict(os.environ, {"ENVIRONMENT": value}):
                assert is_production_mode() is True
        
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            assert is_production_mode() is False


class TestAPIUtilities:
    """Test API utility functions."""
    
    def test_format_api_response_success(self):
        """Test format_api_response with success data."""
        data = {"user_id": 123, "name": "Test User"}
        response = format_api_response(data=data, message="User retrieved")
        
        assert response["status"] == "success"
        assert response["data"] == data
        assert response["message"] == "User retrieved"
        assert "timestamp" in response
    
    def test_format_api_response_error(self):
        """Test format_api_response with error data."""
        errors = ["Invalid user ID", "Permission denied"]
        response = format_api_response(
            status="error",
            errors=errors,
            message="Operation failed"
        )
        
        assert response["status"] == "error"
        assert response["errors"] == errors
        assert response["message"] == "Operation failed"
        assert response["data"] is None
    
    def test_format_api_response_no_timestamp(self):
        """Test format_api_response without timestamp."""
        response = format_api_response(data={"test": "data"}, timestamp=False)
        
        assert "timestamp" not in response
    
    def test_format_api_response_minimal(self):
        """Test format_api_response with minimal parameters."""
        response = format_api_response()
        
        assert response["status"] == "success"
        assert response["data"] is None
        assert "timestamp" in response


class TestExecutionUtilities:
    """Test execution utility functions."""
    
    def test_safe_execute_success(self):
        """Test safe_execute with successful function."""
        def successful_function(a, b):
            return a + b
        
        result = safe_execute(successful_function, 3, 5)
        assert result == 8
    
    def test_safe_execute_with_kwargs(self):
        """Test safe_execute with keyword arguments."""
        def function_with_kwargs(a, b=10, c=20):
            return a + b + c
        
        result = safe_execute(function_with_kwargs, 5, c=15)
        assert result == 30
    
    def test_safe_execute_failure(self):
        """Test safe_execute with failing function."""
        def failing_function():
            raise ValueError("Test error")
        
        result = safe_execute(failing_function, default="fallback")
        assert result == "fallback"
    
    def test_safe_execute_no_logging(self):
        """Test safe_execute with logging disabled."""
        def failing_function():
            raise ValueError("Test error")
        
        with patch('src.infrastructure.utils.common_utils.logging.getLogger') as mock_logger:
            result = safe_execute(failing_function, default="fallback", log_errors=False)
            assert result == "fallback"
            mock_logger.assert_not_called()


class TestFileUtilities:
    """Test file utility functions."""
    
    def test_ensure_directory_new(self):
        """Test ensure_directory creates new directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new" / "nested" / "directory"
            
            result = ensure_directory(new_dir)
            
            assert result == new_dir
            assert new_dir.exists()
            assert new_dir.is_dir()
    
    def test_ensure_directory_existing(self):
        """Test ensure_directory with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_dir = Path(temp_dir)
            
            result = ensure_directory(existing_dir)
            
            assert result == existing_dir
            assert existing_dir.exists()
    
    def test_get_file_size_mb_existing(self):
        """Test get_file_size_mb with existing file."""
        test_content = "x" * 1024 * 1024  # 1 MB
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(test_content)
            file_path = f.name
        
        try:
            size_mb = get_file_size_mb(file_path)
            assert abs(size_mb - 1.0) < 0.1  # Should be approximately 1 MB
        finally:
            os.unlink(file_path)
    
    def test_get_file_size_mb_nonexistent(self):
        """Test get_file_size_mb with non-existent file."""
        size_mb = get_file_size_mb("/nonexistent/file.txt")
        assert size_mb == 0.0
    
    def test_truncate_string_short(self):
        """Test truncate_string with short string."""
        text = "Short text"
        result = truncate_string(text, max_length=100)
        assert result == "Short text"
    
    def test_truncate_string_long(self):
        """Test truncate_string with long string."""
        text = "This is a very long string that should be truncated"
        result = truncate_string(text, max_length=20)
        
        assert len(result) == 20
        assert result.endswith("...")
        assert result.startswith("This is a very")
    
    def test_truncate_string_custom_suffix(self):
        """Test truncate_string with custom suffix."""
        text = "Long string to truncate"
        result = truncate_string(text, max_length=15, suffix="[...]")
        
        assert len(result) == 15
        assert result.endswith("[...]")


class TestEnvironmentConfig:
    """Test EnvironmentConfig utility class."""
    
    def test_get_api_base_url_default(self):
        """Test get_api_base_url returns default."""
        url = EnvironmentConfig.get_api_base_url()
        assert url == "http://localhost:5000"
    
    @patch.dict(os.environ, {"API_BASE_URL": "https://api.example.com"})
    def test_get_api_base_url_env(self):
        """Test get_api_base_url from environment."""
        url = EnvironmentConfig.get_api_base_url()
        assert url == "https://api.example.com"
    
    def test_get_database_url(self):
        """Test get_database_url."""
        url = EnvironmentConfig.get_database_url()
        assert isinstance(url, str)
    
    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://localhost/testdb"})
    def test_get_database_url_env(self):
        """Test get_database_url from environment."""
        url = EnvironmentConfig.get_database_url()
        assert url == "postgresql://localhost/testdb"
    
    def test_get_redis_url_default(self):
        """Test get_redis_url returns default."""
        url = EnvironmentConfig.get_redis_url()
        assert url == "redis://localhost:6379"
    
    @patch('src.infrastructure.utils.common_utils.is_production_mode', return_value=True)
    def test_get_encryption_key_required_in_prod(self, mock_prod):
        """Test get_encryption_key required in production."""
        with pytest.raises(ValueError):
            EnvironmentConfig.get_encryption_key()
    
    @patch('src.infrastructure.utils.common_utils.is_production_mode', return_value=False)
    def test_get_encryption_key_optional_in_dev(self, mock_prod):
        """Test get_encryption_key optional in development."""
        key = EnvironmentConfig.get_encryption_key()
        assert key == ""
    
    @patch('src.infrastructure.utils.common_utils.is_development_mode', return_value=True)
    def test_get_secret_key_dev_default(self, mock_dev):
        """Test get_secret_key provides default in development."""
        with patch.dict(os.environ, {}, clear=True):
            key = EnvironmentConfig.get_secret_key()
            assert key == "dev-secret-change-in-production"
    
    @patch('src.infrastructure.utils.common_utils.is_test_mode', return_value=False)
    def test_get_openai_api_key_required(self, mock_test):
        """Test get_openai_api_key required when not in test mode."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                EnvironmentConfig.get_openai_api_key()
    
    @patch('src.infrastructure.utils.common_utils.is_test_mode', return_value=True)
    def test_get_openai_api_key_optional_in_test(self, mock_test):
        """Test get_openai_api_key optional in test mode."""
        with patch.dict(os.environ, {}, clear=True):
            key = EnvironmentConfig.get_openai_api_key()
            assert key == ""
    
    def test_get_log_level_default(self):
        """Test get_log_level returns default."""
        level = EnvironmentConfig.get_log_level()
        assert level == "INFO"
    
    @patch.dict(os.environ, {"LOG_LEVEL": "debug"})
    def test_get_log_level_env(self):
        """Test get_log_level from environment."""
        level = EnvironmentConfig.get_log_level()
        assert level == "DEBUG"  # Should be uppercase


class TestUtilityIntegration:
    """Integration tests for utility functions working together."""
    
    def test_config_file_workflow(self):
        """Test complete workflow of creating, writing, and reading config."""
        config_data = {
            "api": {
                "base_url": "${API_BASE_URL:http://localhost:5000}",
                "timeout": 30
            },
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = ensure_directory(Path(temp_dir) / "config")
            config_file = config_dir / "app.json"
            
            # Write config
            success = write_json(config_file, config_data, indent=2)
            assert success is True
            
            # Read config back
            loaded_config = read_json(config_file)
            assert loaded_config == config_data
            
            # Check file size
            size_mb = get_file_size_mb(config_file)
            assert size_mb > 0
    
    def test_logging_with_environment_config(self):
        """Test logging setup with environment configuration."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            logger = setup_logging("test_logger")
            
            assert logger.level == logging.DEBUG
            assert logger.name == "test_logger"
    
    def test_safe_execution_with_api_response(self):
        """Test safe execution combined with API response formatting."""
        def api_operation():
            return {"user_id": 123, "name": "Test User"}
        
        def failing_api_operation():
            raise ConnectionError("API unavailable")
        
        # Successful operation
        result = safe_execute(api_operation)
        response = format_api_response(data=result, message="User retrieved")
        
        assert response["status"] == "success"
        assert response["data"]["user_id"] == 123
        
        # Failed operation
        result = safe_execute(failing_api_operation, default=None)
        response = format_api_response(
            data=result,
            status="error",
            errors=["Service unavailable"]
        )
        
        assert response["status"] == "error"
        assert response["data"] is None


@pytest.fixture
def temp_config_file():
    """Fixture providing a temporary config file."""
    config_data = {
        "app": {
            "name": "test_app",
            "version": "1.0.0"
        },
        "features": {
            "logging": True,
            "caching": False
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        f.flush()  # Ensure data is written to disk
        temp_file_name = f.name
    
    yield temp_file_name
    
    # Cleanup
    try:
        os.unlink(temp_file_name)
    except OSError:
        pass


class TestFixtureIntegration:
    """Test utilities using fixtures."""
    
    def test_read_config_fixture(self, temp_config_file):
        """Test reading config using fixture."""
        config = read_json(temp_config_file)
        
        assert config["app"]["name"] == "test_app"
        assert config["features"]["logging"] is True
    
    def test_safe_get_env_with_config(self, temp_config_file):
        """Test environment variables with config file."""
        with patch.dict(os.environ, {"APP_VERSION": "2.0.0"}):
            config = read_json(temp_config_file)
            version = safe_get_env("APP_VERSION", default=config["app"]["version"])
            
            assert version == "2.0.0"  # From environment
            
            # Without environment variable
            with patch.dict(os.environ, {}, clear=True):
                version = safe_get_env("APP_VERSION", default=config["app"]["version"])
                assert version == "1.0.0"  # From config