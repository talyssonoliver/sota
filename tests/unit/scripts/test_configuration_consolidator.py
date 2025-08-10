#!/usr/bin/env python3
"""
Test suite for enhanced configuration consolidator script

Tests the configuration system consolidation functionality with safety measures,
git integration, and comprehensive error handling.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add scripts directory to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

try:
    from configuration_consolidator import ConfigurationConsolidator, ConfigConsolidationMetrics
except ImportError as e:
    pytest.skip(f"Could not import configuration_consolidator: {e}", allow_module_level=True)


class TestConfigurationConsolidator:
    """Test suite for enhanced ConfigurationConsolidator."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)
    
    @pytest.fixture
    def consolidator(self, temp_dir):
        """Create a consolidator instance for testing."""
        # Change to temp directory for testing
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        consolidator = ConfigurationConsolidator(
            root_dir=str(temp_dir),
            dry_run=True,  # Default to dry run for safety
            verify_tests=False,  # Skip tests in unit tests
            create_backup=False,  # Skip git operations in unit tests
            verify_git_clean=False
        )
        
        yield consolidator
        
        # Restore original directory
        os.chdir(original_cwd)
    
    @pytest.fixture
    def sample_config_files(self, temp_dir):
        """Create sample configuration files for testing."""
        files = {}
        
        # Create config directory structure
        config_dir = temp_dir / "config"
        config_dir.mkdir()
        
        src_dir = temp_dir / "src"
        src_dir.mkdir()
        
        # JSON configuration file
        files["json_config"] = config_dir / "app_config.json"
        files["json_config"].write_text('''{
    "database": {
        "host": "localhost",
        "port": 5432,
        "user": "app_user"
    },
    "api": {
        "base_url": "http://localhost:5000",
        "timeout": 30
    },
    "debug": true
}''')
        
        # YAML configuration file
        files["yaml_config"] = config_dir / "settings.yaml"
        files["yaml_config"].write_text('''database:
  url: ${DATABASE_URL}
  pool_size: 10
api:
  openai_key: ${OPENAI_API_KEY}
  timeout: ${API_TIMEOUT:30}
security:
  encryption_enabled: true
  jwt_secret: ${JWT_SECRET}
''')
        
        # Python configuration module with environment variables
        files["python_config"] = src_dir / "config_module.py"
        files["python_config"].write_text('''"""Sample Python configuration module."""
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/db')
DATABASE_HOST = os.getenv('DB_HOST', 'localhost')  # Variant name
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')  # Another variant

API_KEY_OPENAI = os.getenv('API_KEY_OPENAI')  # Variant name
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Standard name
BASE_URL = os.getenv('BASE_URL', 'http://localhost')  # Variant

DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
LOG_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')  # Variant name

# Hardcoded values that should be extracted
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
DEFAULT_TIMEOUT = 30
''')
        
        # Environment file
        files["env_file"] = temp_dir / ".env"
        files["env_file"].write_text('''DATABASE_URL=postgresql://localhost/testdb
DB_HOST=127.0.0.1
POSTGRES_PORT=5432
OPENAI_API_KEY=sk-test123
DEBUG=true
LOG_LEVEL=DEBUG
''')
        
        # Configuration file with duplicates
        files["duplicate_config"] = config_dir / "duplicate_settings.json"
        files["duplicate_config"].write_text('''{
    "database": {
        "host": "localhost",
        "port": 5432,
        "timeout": 30
    },
    "api": {
        "base_url": "http://localhost:5000",
        "retry_attempts": 3
    }
}''')
        
        # Settings file with hardcoded values
        files["hardcoded_config"] = src_dir / "hardcoded_settings.py"
        files["hardcoded_config"].write_text('''"""Configuration with hardcoded values."""

# Hardcoded network settings
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080
DATABASE_URL = "postgresql://localhost:5432/myapp"
API_ENDPOINT = "https://api.example.com/v1"
CACHE_URL = "redis://localhost:6379"

# Mixed environment and hardcoded
DEBUG = os.getenv('DEBUG', False)
LOG_LEVEL = 'INFO'  # Hardcoded
''')
        
        return files
    
    def test_initialization(self, temp_dir):
        """Test consolidator initialization with various options."""
        consolidator = ConfigurationConsolidator(
            root_dir=str(temp_dir),
            dry_run=False,
            verify_tests=True,
            create_backup=True,
            verify_git_clean=True
        )
        
        assert consolidator.root_dir == temp_dir
        assert consolidator.dry_run is False
        assert consolidator.verify_tests is True
        assert consolidator.create_backup is True
        assert consolidator.verify_git_clean is True
        assert consolidator.max_workers == 4
        assert isinstance(consolidator.metrics, ConfigConsolidationMetrics)
        assert len(consolidator.env_var_patterns) > 0
        assert len(consolidator.env_var_standards) > 0
    
    def test_metrics_initialization(self, consolidator):
        """Test metrics are properly initialized."""
        metrics = consolidator.metrics
        assert metrics.files_analyzed == 0
        assert metrics.config_files_found == 0
        assert metrics.environment_vars_found == 0
        assert metrics.duplicate_keys_identified == 0
        assert metrics.config_patterns_unified == 0
        assert metrics.files_consolidated == 0
        assert metrics.lines_saved == 0
    
    def test_unified_config_system_validation(self, consolidator):
        """Test validation of unified configuration system creation."""
        # Should pass basic validation
        assert consolidator.validate_unified_config_system() is True
        assert len(consolidator.validation_errors) == 0
    
    def test_config_file_discovery(self, consolidator, sample_config_files):
        """Test discovery of configuration files."""
        analysis = consolidator.analyze_configuration_sprawl()
        
        # Should find our sample configuration files
        assert len(analysis['config_files']) > 0
        assert consolidator.metrics.config_files_found > 0
        
        # Check that different file types are detected
        file_types = [f['type'] for f in analysis['config_files']]
        assert 'json' in file_types
        assert 'yaml' in file_types
        assert 'python_config' in file_types
        assert 'environment' in file_types
    
    def test_environment_variable_detection(self, consolidator, sample_config_files):
        """Test detection of environment variables in configuration files."""
        analysis = consolidator.analyze_configuration_sprawl()
        
        # Should find environment variables
        env_vars = analysis['environment_variable_usage']
        assert len(env_vars) > 0
        
        # Should detect standard and variant names
        detected_vars = set(env_vars.keys())
        expected_vars = {
            'DATABASE_URL', 'DB_HOST', 'POSTGRES_PORT',
            'API_KEY_OPENAI', 'OPENAI_API_KEY', 'BASE_URL',
            'DEBUG_MODE', 'LOGGING_LEVEL'
        }
        
        # Should find at least some of the expected variables
        assert len(detected_vars.intersection(expected_vars)) > 0
    
    def test_hardcoded_value_detection(self, consolidator, sample_config_files):
        """Test detection of hardcoded values that should be configurable."""
        analysis = consolidator.analyze_configuration_sprawl()
        
        # Check files for hardcoded values
        files_with_hardcoded = [
            f for f in analysis['config_files'] 
            if f.get('hardcoded_values') and len(f['hardcoded_values']) > 0
        ]
        
        assert len(files_with_hardcoded) > 0
        
        # Should detect localhost, IP addresses, ports, URLs
        all_hardcoded = []
        for file_info in files_with_hardcoded:
            all_hardcoded.extend(file_info['hardcoded_values'])
        
        hardcoded_str = ' '.join(all_hardcoded)
        assert any(pattern in hardcoded_str.lower() for pattern in ['localhost', '127.0.0.1'])
    
    def test_duplicate_configuration_detection(self, consolidator, sample_config_files):
        """Test detection of duplicate configuration keys."""
        analysis = consolidator.analyze_configuration_sprawl()
        
        # Should detect duplicate keys across files
        duplicates = analysis['duplicate_configurations']
        
        # Our sample files have overlapping database and api configurations
        duplicate_keys = set(duplicates.keys())
        expected_duplicates = {'database.host', 'database.port', 'api.base_url'}
        
        # Should find at least some duplicate configurations
        found_duplicates = duplicate_keys.intersection(expected_duplicates)
        assert len(found_duplicates) > 0
        
        # Each duplicate should reference multiple files
        for key, files in duplicates.items():
            assert len(files) >= 2  # Must appear in at least 2 files to be a duplicate
    
    def test_consolidation_opportunities_identification(self, consolidator, sample_config_files):
        """Test identification of consolidation opportunities."""
        analysis = consolidator.analyze_configuration_sprawl()
        
        opportunities = analysis['consolidation_opportunities']
        
        # Should identify environment variable standardization opportunities
        env_standardization = opportunities['environment_variable_standardization']
        assert isinstance(env_standardization, dict)
        
        # Should identify loading pattern unification opportunities
        loading_patterns = opportunities['loading_pattern_unification']
        assert 'current_patterns' in loading_patterns
        assert 'recommended_pattern' in loading_patterns
        assert loading_patterns['recommended_pattern'] == 'factory_pattern'
    
    def test_unified_schema_generation(self, consolidator, sample_config_files):
        """Test generation of unified configuration schema."""
        analysis = consolidator.analyze_configuration_sprawl()
        schema = consolidator._generate_unified_schema(analysis)
        
        # Should generate schemas for main configuration areas
        assert 'database' in schema
        assert 'api' in schema
        assert 'security' in schema
        assert 'application' in schema
        
        # Each schema should have proper structure
        for schema_name, schema_def in schema.items():
            assert 'type' in schema_def
            assert schema_def['type'] == 'object'
            assert 'properties' in schema_def
            assert len(schema_def['properties']) > 0
    
    def test_unified_config_class_generation(self, consolidator):
        """Test generation of unified configuration class."""
        schema = {
            'database': {'type': 'object', 'properties': {'url': {'type': 'string'}}},
            'api': {'type': 'object', 'properties': {'key': {'type': 'string'}}}
        }
        
        config_class_content = consolidator._generate_unified_config_class(schema)
        
        # Should contain required imports and classes
        assert 'from dataclasses import dataclass' in config_class_content
        assert 'class DatabaseConfig:' in config_class_content
        assert 'class APIConfig:' in config_class_content
        assert 'class UnifiedConfig:' in config_class_content
        assert 'def get_config()' in config_class_content
        
        # Should contain environment variable loading
        assert 'from_environment' in config_class_content
        assert 'os.getenv' in config_class_content
    
    def test_environment_mapping_generation(self, consolidator, sample_config_files):
        """Test generation of environment variable mapping."""
        analysis = consolidator.analyze_configuration_sprawl()
        mapping_content = consolidator._generate_environment_mapping(analysis)
        
        # Should contain standard environment mapping
        assert 'ENVIRONMENT_MAPPING' in mapping_content
        assert 'DATABASE_URL' in mapping_content
        assert 'OPENAI_API_KEY' in mapping_content
        
        # Should contain deprecated mappings
        assert 'DEPRECATED_ENV_VARS' in mapping_content
        assert 'DB_HOST' in mapping_content  # Variant of DATABASE_HOST
        assert 'API_KEY_OPENAI' in mapping_content  # Variant of OPENAI_API_KEY
    
    def test_migration_guide_generation(self, consolidator, sample_config_files):
        """Test generation of migration guide."""
        analysis = consolidator.analyze_configuration_sprawl()
        migration_guide = consolidator._generate_migration_guide(analysis)
        
        # Should contain comprehensive migration guidance
        assert '# Configuration System Migration Guide' in migration_guide
        assert 'Phase 1' in migration_guide
        assert 'Phase 2' in migration_guide
        assert 'Phase 3' in migration_guide
        
        # Should contain code examples
        assert '```python' in migration_guide
        assert '```yaml' in migration_guide
        assert 'from src.core.configuration.unified import get_config' in migration_guide
        
        # Should contain rollback plan
        assert 'Rollback Plan' in migration_guide
        assert 'Testing' in migration_guide
    
    def test_unified_configuration_creation_dry_run(self, consolidator, sample_config_files):
        """Test creation of unified configuration system in dry run mode."""
        analysis = consolidator.analyze_configuration_sprawl()
        
        result = consolidator.create_unified_configuration(analysis)
        
        # Should succeed in dry run mode
        assert result is True
        assert consolidator.metrics.files_consolidated > 0
        
        # Files should not actually be created in dry run mode
        unified_dir = consolidator.root_dir / "src/core/configuration/unified"
        assert not unified_dir.exists() or len(list(unified_dir.glob("*.py"))) == 0
    
    @patch('subprocess.run')
    def test_git_status_verification(self, mock_run, consolidator):
        """Test git status verification."""
        # Test clean git status
        mock_run.return_value = Mock(returncode=0, stdout="")
        consolidator.verify_git_clean = True
        assert consolidator.verify_git_status() is True
        
        # Test dirty git status
        mock_run.return_value = Mock(returncode=0, stdout="M file.py\n")
        assert consolidator.verify_git_status() is False
        
        # Test git not available
        mock_run.return_value = Mock(returncode=128, stderr="not a git repository")
        assert consolidator.verify_git_status() is True
    
    @patch('subprocess.run')
    def test_backup_branch_creation(self, mock_run, consolidator):
        """Test backup branch creation."""
        # Mock successful branch creation
        mock_run.side_effect = [
            Mock(returncode=0, stdout="Switched to a new branch"),
            Mock(returncode=0, stdout="Switched to branch")
        ]
        
        consolidator.create_backup = True
        
        assert consolidator.create_backup_branch() is True
        assert consolidator.backup_created is True
        assert consolidator.backup_branch is not None
        assert "config-consolidation-backup-" in consolidator.backup_branch
    
    @patch('subprocess.run')
    def test_test_verification_before(self, mock_run, consolidator):
        """Test running tests before consolidation."""
        consolidator.verify_tests = True
        
        # Mock passing tests
        mock_run.return_value = Mock(
            returncode=0,
            stdout="collected 100 items\n100 passed in 10.00s"
        )
        
        assert consolidator.run_tests_before() is True
        assert len(consolidator.test_failures_before) == 0
        
        # Mock failing tests
        mock_run.return_value = Mock(
            returncode=1,
            stdout="collected 100 items\n5 failed, 95 passed\nFAILED test_a.py::test_1"
        )
        
        assert consolidator.run_tests_before() is True  # Still continues with pre-existing failures
        assert len(consolidator.test_failures_before) > 0
    
    @patch('subprocess.run')
    def test_test_verification_after(self, mock_run, consolidator):
        """Test running tests after consolidation."""
        consolidator.verify_tests = True
        consolidator.test_failures_before = ["test_a.py::test_1"]  # Pre-existing failure
        
        # Mock same failures (no new failures introduced)
        mock_run.return_value = Mock(
            returncode=1,
            stdout="collected 100 items\n1 failed, 99 passed\nFAILED test_a.py::test_1"
        )
        
        assert consolidator.run_tests_after() is True  # Same failures, OK
        
        # Mock new failures introduced
        mock_run.return_value = Mock(
            returncode=1,
            stdout="collected 100 items\n2 failed, 98 passed\nFAILED test_a.py::test_1\nFAILED test_b.py::test_2"
        )
        
        assert consolidator.run_tests_after() is False  # New failure introduced
    
    def test_file_writing_error_handling(self, consolidator, temp_dir):
        """Test error handling during file writing."""
        # Try to write to a protected location (should fail gracefully)
        protected_path = temp_dir / "protected" / "file.txt"
        
        # Create parent as a file instead of directory to cause error
        protected_path.parent.touch()
        
        result = consolidator._write_file(protected_path, "test content")
        
        # Should handle error gracefully
        assert result is False
        assert len(consolidator.errors) > 0
    
    def test_thread_safety(self, consolidator, temp_dir):
        """Test thread safety of consolidation operations."""
        # Create multiple config files for parallel processing
        config_dir = temp_dir / "configs"
        config_dir.mkdir()
        
        for i in range(10):
            config_file = config_dir / f"config_{i}.json"
            config_file.write_text(f'''{{
                "app_name": "test_{i}",
                "database_host": "localhost",
                "api_timeout": {30 + i}
            }}''')
        
        # Run analysis (which uses parallel processing)
        analysis = consolidator.analyze_configuration_sprawl()
        
        # Should process all files without errors
        assert len(analysis['config_files']) >= 10
        assert consolidator.metrics.files_analyzed >= 10
    
    def test_full_consolidation_cycle_dry_run(self, consolidator, sample_config_files):
        """Test complete consolidation cycle in dry run mode."""
        # Should complete successfully
        results = consolidator.run_consolidation()
        
        assert "success" in results
        assert "analysis" in results
        assert "unified_system_created" in results
        assert "metrics" in results
        
        metrics = results["metrics"]
        assert metrics["files_analyzed"] > 0
        assert metrics["config_files_found"] > 0
        assert metrics["environment_vars_found"] > 0
        
        # Should identify consolidation opportunities
        analysis = results["analysis"]
        opportunities = analysis["consolidation_opportunities"]
        assert len(opportunities["environment_variable_standardization"]) > 0
    
    def test_consolidation_with_missing_dependencies(self, temp_dir):
        """Test consolidation behavior when dependencies are missing."""
        # Test without yaml module (mock import error)
        with patch('builtins.__import__', side_effect=ImportError("PyYAML not found")):
            consolidator = ConfigurationConsolidator(
                root_dir=str(temp_dir),
                dry_run=False,  # Not dry run to trigger validation
                verify_tests=False,
                create_backup=False,
                verify_git_clean=False
            )
            
            # Should detect missing dependency
            assert consolidator.validate_unified_config_system() is False
            assert any("PyYAML" in error for error in consolidator.validation_errors)
    
    def test_environment_variable_standardization_detection(self, consolidator, sample_config_files):
        """Test detection of environment variable standardization opportunities."""
        analysis = consolidator.analyze_configuration_sprawl()
        
        opportunities = analysis['consolidation_opportunities']['environment_variable_standardization']
        
        # Should detect variants in use
        for canonical_name, details in opportunities.items():
            assert 'standard_name' in details
            assert 'variants_in_use' in details
            assert 'consolidation_impact' in details
            
            # Should have multiple variants to be worth consolidating
            assert len(details['variants_in_use']) > 1
            
            # Each variant should have file usage information
            for variant in details['variants_in_use']:
                assert 'variant' in variant
                assert 'files' in variant
                assert 'count' in variant
                assert variant['count'] > 0


class TestConfigurationConsolidatorIntegration:
    """Integration tests for configuration consolidator."""
    
    @pytest.fixture
    def integration_temp_dir(self):
        """Create a comprehensive test environment for integration testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_dir = Path(tmp_dir)
            
            # Create realistic directory structure
            (test_dir / "config").mkdir()
            (test_dir / "src" / "core" / "config").mkdir(parents=True)
            (test_dir / "src" / "infrastructure" / "config").mkdir(parents=True)
            (test_dir / "tests" / "unit").mkdir(parents=True)
            (test_dir / "reports").mkdir(parents=True)
            
            # Create scattered configuration files (realistic scenario)
            config_files = {
                "config/database.json": '''{
                    "host": "localhost",
                    "port": 5432,
                    "pool_size": 10
                }''',
                "config/api_config.yaml": '''
base_url: ${API_BASE_URL:http://localhost:5000}
timeout: ${REQUEST_TIMEOUT:30}
openai_key: ${OPENAI_API_KEY}
''',
                "src/core/config/app_settings.py": '''
import os
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/db')
DEBUG_MODE = os.getenv('DEBUG', 'false').lower() == 'true'
LOG_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
''',
                "src/infrastructure/config/memory_config.py": '''
import os
ENCRYPTION_KEY = os.getenv('MEMORY_ENGINE_KEY')
CACHE_SIZE = int(os.getenv('CACHE_SIZE', '1000'))
DATABASE_HOST = os.getenv('POSTGRES_HOST', 'localhost')
''',
                ".env": '''DATABASE_URL=postgresql://localhost/testdb
OPENAI_API_KEY=sk-test123
DEBUG=true
LOG_LEVEL=DEBUG
''',
                "config/validation_config.json": '''{
                    "database": {
                        "timeout": 30,
                        "retry_attempts": 3
                    },
                    "security": {
                        "encryption_enabled": true
                    }
                }'''
            }
            
            # Write all configuration files
            for file_path, content in config_files.items():
                full_path = test_dir / file_path
                full_path.write_text(content)
            
            yield test_dir
    
    def test_full_integration_dry_run(self, integration_temp_dir):
        """Test complete integration with realistic configuration sprawl."""
        original_cwd = os.getcwd()
        try:
            os.chdir(integration_temp_dir)
            
            consolidator = ConfigurationConsolidator(
                root_dir=str(integration_temp_dir),
                dry_run=True,
                verify_tests=False,
                create_backup=False,
                verify_git_clean=False
            )
            
            # Validate unified config system
            assert consolidator.validate_unified_config_system() is True
            
            # Run full consolidation
            results = consolidator.run_consolidation()
            
            # Should find significant configuration sprawl
            assert results["success"] is True
            assert results["metrics"]["config_files_found"] >= 6  # Our test files
            assert results["metrics"]["environment_vars_found"] > 0
            assert results["metrics"]["duplicate_keys_identified"] > 0
            assert results["metrics"]["files_consolidated"] > 0
            
            # Should identify standardization opportunities
            analysis = results["analysis"]
            opportunities = analysis["consolidation_opportunities"]["environment_variable_standardization"]
            assert len(opportunities) > 0
            
        finally:
            os.chdir(original_cwd)
    
    def test_performance_with_many_config_files(self, integration_temp_dir):
        """Test consolidation performance with many configuration files."""
        # Create many scattered config files
        for i in range(50):
            config_file = integration_temp_dir / f"config/app_{i}.json"
            config_file.write_text(f'''{{
                "app_id": {i},
                "database_timeout": {30 + i % 10},
                "api_base_url": "http://service{i % 5}.example.com",
                "log_level": "INFO"
            }}''')
        
        # Create Python config modules
        for i in range(20):
            config_module = integration_temp_dir / "src" / f"config_{i}.py"
            config_module.write_text(f'''
import os
DATABASE_HOST = os.getenv('DB_HOST_{i}', 'localhost')
API_KEY = os.getenv('API_KEY_{i}')
DEBUG = os.getenv('DEBUG_{i}', 'false').lower() == 'true'
''')
        
        consolidator = ConfigurationConsolidator(
            root_dir=str(integration_temp_dir),
            dry_run=True,
            verify_tests=False,
            create_backup=False,
            verify_git_clean=False,
            max_workers=4
        )
        
        # Should complete in reasonable time
        import time
        start_time = time.time()
        
        results = consolidator.run_consolidation()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 30 seconds for 70 files
        assert execution_time < 30
        assert results["success"] is True
        assert results["metrics"]["config_files_found"] >= 70
    
    def test_consolidation_preserves_functionality(self, integration_temp_dir):
        """Test that consolidation preserves configuration functionality."""
        original_cwd = os.getcwd()
        try:
            os.chdir(integration_temp_dir)
            
            consolidator = ConfigurationConsolidator(
                root_dir=str(integration_temp_dir),
                dry_run=False,  # Actually create files
                verify_tests=False,
                create_backup=False,
                verify_git_clean=False
            )
            
            # Run consolidation
            results = consolidator.run_consolidation()
            
            if results["success"] and results["unified_system_created"]:
                # Check that unified configuration was created
                unified_dir = integration_temp_dir / "src/core/configuration/unified"
                assert unified_dir.exists()
                
                # Should have created the main configuration files
                assert (unified_dir / "unified_config.py").exists()
                assert (unified_dir / "environment_mapping.py").exists()
                assert (unified_dir / "MIGRATION_GUIDE.md").exists()
                
                # Check that schemas were created
                schema_dir = unified_dir / "schemas"
                if schema_dir.exists():
                    schema_files = list(schema_dir.glob("*.schema.json"))
                    assert len(schema_files) > 0
            
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])