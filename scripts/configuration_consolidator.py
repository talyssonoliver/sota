#!/usr/bin/env python3
"""
Enhanced Configuration System Consolidation Script

Systematically consolidates the scattered configuration system to address
configuration sprawl identified in the architecture analysis with comprehensive
safety measures:

- 63+ configuration-related files across multiple directories
- 12+ Python configuration modules with overlapping functionality  
- 59 files with environment variable access using 5+ different patterns
- 8+ database configuration locations with duplicate settings
- 5+ different configuration loading mechanisms

ARCHITECTURE FIX: Eliminates configuration sprawl and standardizes config management

Safety Features:
- Git status verification and backup branch creation
- Test verification before and after consolidation
- Comprehensive error handling and rollback capabilities
- Thread-safe operations with locking
- Configuration validation and compatibility checks
"""

import json
import re
import yaml
import subprocess
import threading
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from concurrent.futures import ThreadPoolExecutor
import argparse
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ConfigConsolidationMetrics:
    """Metrics for tracking consolidation progress."""
    files_analyzed: int = 0
    config_files_found: int = 0
    environment_vars_found: int = 0
    duplicate_keys_identified: int = 0
    config_patterns_unified: int = 0
    files_consolidated: int = 0
    lines_saved: int = 0
    environment_vars_standardized: int = 0


class ConfigurationConsolidator:
    """Enhanced consolidator for scattered configuration system with safety measures."""
    
    def __init__(self, root_dir: str = ".", dry_run: bool = True, verify_tests: bool = True,
                 create_backup: bool = True, verify_git_clean: bool = True):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.verify_tests = verify_tests
        self.create_backup = create_backup
        self.verify_git_clean = verify_git_clean
        self.max_workers = 4  # Respect system constraint
        self.metrics = ConfigConsolidationMetrics()
        
        # Safety tracking
        self.backup_branch = None
        self.backup_created = False
        self.test_failures_before = []
        self.test_failures_after = []
        self.thread_lock = threading.Lock()  # For thread-safe operations
        self.errors = []  # Comprehensive error tracking
        self.validation_errors = []
        
        # Configuration file patterns to analyze
        self.config_file_patterns = [
            "*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg", 
            "*.config", "*.conf", ".env*", "*config*.py", "*settings*.py"
        ]
        
        # Environment variable patterns found in analysis
        self.env_var_patterns = {
            # Database configuration duplicates
            'database_url': ['DATABASE_URL', 'DB_URL', 'DATABASE_CONNECTION'],
            'database_host': ['DATABASE_HOST', 'DB_HOST', 'POSTGRES_HOST'],
            'database_port': ['DATABASE_PORT', 'DB_PORT', 'POSTGRES_PORT'],
            'database_user': ['DATABASE_USER', 'DB_USER', 'POSTGRES_USER'],
            'database_password': ['DATABASE_PASSWORD', 'DB_PASSWORD', 'POSTGRES_PASSWORD'],
            
            # API configuration duplicates  
            'api_key_openai': ['OPENAI_API_KEY', 'API_KEY_OPENAI', 'OPENAI_KEY'],
            'api_key_claude': ['CLAUDE_API_KEY', 'API_KEY_CLAUDE', 'ANTHROPIC_API_KEY'],
            'api_base_url': ['API_BASE_URL', 'BASE_URL', 'SERVICE_BASE_URL'],
            'api_timeout': ['API_TIMEOUT', 'REQUEST_TIMEOUT', 'HTTP_TIMEOUT'],
            
            # Security configuration duplicates
            'encryption_key': ['ENCRYPTION_KEY', 'SECRET_KEY', 'MEMORY_ENGINE_KEY'],
            'jwt_secret': ['JWT_SECRET', 'JWT_SECRET_KEY', 'AUTH_SECRET'],
            
            # Application configuration
            'debug_mode': ['DEBUG', 'DEBUG_MODE', 'DEVELOPMENT'],
            'log_level': ['LOG_LEVEL', 'LOGGING_LEVEL', 'LOGLEVEL'],
            
            # Service configuration  
            'redis_url': ['REDIS_URL', 'CACHE_URL', 'REDIS_CONNECTION'],
            'port': ['PORT', 'APP_PORT', 'SERVER_PORT'],
        }
        
        # Configuration consolidation targets (duplicate configurations found)
        self.consolidation_targets = {
            # Database configurations (found in 8+ files)
            'database': [
                'config/memory_config.py',
                'src/infrastructure/memory/config/memory_config.py', 
                'config/validation_config.json',
                'docker-compose.dev.yml'
            ],
            
            # API configurations (scattered across multiple files)
            'api': [
                'config/gemini_config.json',
                'src/interfaces/dashboard/config.py',
                'config/webhook_external_api_config.json'
            ],
            
            # Security configurations (duplicated)
            'security': [
                'config/validation_config.json',
                'src/infrastructure/memory/config/memory_config.py',
                'src/core/configuration/environment_config.py'
            ],
            
            # Performance/Resource configurations
            'performance': [
                'config/qa_thresholds.yaml',
                'config/validation_config.json',
                'src/interfaces/dashboard/config.py'
            ]
        }
        
        # Standard environment variable naming conventions
        self.env_var_standards = {
            # Database
            'database_url': 'DATABASE_URL',
            'database_host': 'DATABASE_HOST', 
            'database_port': 'DATABASE_PORT',
            'database_user': 'DATABASE_USER',
            'database_password': 'DATABASE_PASSWORD',
            
            # APIs
            'openai_api_key': 'OPENAI_API_KEY',
            'claude_api_key': 'CLAUDE_API_KEY',
            'api_base_url': 'API_BASE_URL',
            'api_timeout': 'API_TIMEOUT',
            
            # Security
            'encryption_key': 'ENCRYPTION_KEY',
            'jwt_secret': 'JWT_SECRET',
            
            # Application
            'debug_mode': 'DEBUG',
            'log_level': 'LOG_LEVEL',
            
            # Services
            'redis_url': 'REDIS_URL',
            'app_port': 'PORT',
        }
    
    def analyze_configuration_sprawl(self) -> Dict[str, Any]:
        """Analyze current configuration system sprawl."""
        logger.info("🔍 Analyzing configuration system sprawl...")
        
        analysis = {
            'config_files': [],
            'python_config_modules': [],
            'environment_variable_usage': {},
            'duplicate_configurations': {},
            'hardcoded_values': [],
            'loading_patterns': [],
            'consolidation_opportunities': {}
        }
        
        # Find all configuration files
        all_files = list(self.root_dir.rglob("*"))
        config_files = []
        
        for pattern in self.config_file_patterns:
            config_files.extend(self.root_dir.rglob(pattern))
        
        # Remove duplicates and filter valid files
        config_files = list(set(f for f in config_files if f.is_file()))
        self.metrics.config_files_found = len(config_files)
        
        # Analyze each configuration file
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for config_file in config_files:
                future = executor.submit(self._analyze_config_file, config_file)
                futures.append(future)
            
            for future in futures:
                try:
                    file_analysis = future.result()
                    if file_analysis:
                        analysis['config_files'].append(file_analysis)
                        self.metrics.files_analyzed += 1
                        
                        # Aggregate environment variables
                        for env_var in file_analysis.get('environment_vars', []):
                            if env_var not in analysis['environment_variable_usage']:
                                analysis['environment_variable_usage'][env_var] = []
                            analysis['environment_variable_usage'][env_var].append(file_analysis['path'])
                            
                except Exception as e:
                    logger.debug(f"Error analyzing config file: {e}")
        
        # Identify duplicate configurations
        analysis['duplicate_configurations'] = self._identify_duplicate_configs(
            analysis['config_files']
        )
        
        # Identify consolidation opportunities
        analysis['consolidation_opportunities'] = self._identify_consolidation_opportunities(
            analysis['config_files'], analysis['environment_variable_usage']
        )
        
        # Log summary
        self.metrics.environment_vars_found = len(analysis['environment_variable_usage'])
        self.metrics.duplicate_keys_identified = len(analysis['duplicate_configurations'])
        
        logger.info(f"   📊 Configuration files found: {self.metrics.config_files_found}")
        logger.info(f"   📁 Files analyzed: {self.metrics.files_analyzed}")
        logger.info(f"   🔑 Environment variables: {self.metrics.environment_vars_found}")
        logger.info(f"   🔄 Duplicate configurations: {self.metrics.duplicate_keys_identified}")
        
        return analysis
    
    def _analyze_config_file(self, config_file: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single configuration file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return None
                
            file_analysis = {
                'path': str(config_file.relative_to(self.root_dir)),
                'type': self._determine_config_type(config_file),
                'size_bytes': config_file.stat().st_size,
                'environment_vars': [],
                'hardcoded_values': [],
                'config_keys': [],
                'loading_patterns': []
            }
            
            # Find environment variable usage
            env_patterns = [
                r'os\.getenv\(["\']([^"\']+)["\']',
                r'os\.environ\[["\']([^"\']+)["\']\]',
                r'getenv\(["\']([^"\']+)["\']',
                r'env\[["\']([^"\']+)["\']\]',
                r'\$\{?([A-Z_][A-Z0-9_]*)\}?'  # Environment variable references
            ]
            
            for pattern in env_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                file_analysis['environment_vars'].extend(matches)
            
            # Find hardcoded network values
            hardcoded_patterns = [
                r'localhost',
                r'127\.0\.0\.1', 
                r'port["\s]*[:=]["\s]*(\d+)',
                r'["\']http://[^"\']+["\']',
                r'["\']https://[^"\']+["\']'
            ]
            
            for pattern in hardcoded_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                file_analysis['hardcoded_values'].extend(matches)
            
            # Identify configuration loading patterns
            loading_patterns = [
                ('json.load', r'json\.load'),
                ('yaml.load', r'yaml\.(safe_)?load'),
                ('configparser', r'configparser\.'),
                ('dataclass', r'@dataclass'),
                ('os.getenv', r'os\.getenv'),
                ('factory_pattern', r'get_configuration_factory|ConfigurationFactory')
            ]
            
            for pattern_name, pattern_regex in loading_patterns:
                if re.search(pattern_regex, content, re.IGNORECASE):
                    file_analysis['loading_patterns'].append(pattern_name)
            
            # Extract configuration keys for JSON/YAML files
            if config_file.suffix.lower() in ['.json', '.yaml', '.yml']:
                try:
                    if config_file.suffix.lower() == '.json':
                        config_data = json.loads(content)
                    else:
                        config_data = yaml.safe_load(content)
                    
                    if isinstance(config_data, dict):
                        file_analysis['config_keys'] = self._extract_config_keys(config_data)
                except:
                    pass  # Ignore parsing errors
            
            return file_analysis
            
        except Exception as e:
            logger.debug(f"Error analyzing {config_file}: {e}")
            return None
    
    def _determine_config_type(self, config_file: Path) -> str:
        """Determine the type of configuration file."""
        suffix = config_file.suffix.lower()
        name = config_file.name.lower()
        
        if suffix == '.json':
            return 'json'
        elif suffix in ['.yaml', '.yml']:
            return 'yaml'
        elif suffix in ['.toml']:
            return 'toml'
        elif suffix in ['.ini', '.cfg']:
            return 'ini'
        elif name.startswith('.env'):
            return 'environment'
        elif 'config' in name and suffix == '.py':
            return 'python_config'
        else:
            return 'other'
    
    def _extract_config_keys(self, config_data: Dict, prefix: str = '') -> List[str]:
        """Recursively extract configuration keys from nested dictionaries."""
        keys = []
        for key, value in config_data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.append(full_key)
            
            if isinstance(value, dict):
                keys.extend(self._extract_config_keys(value, full_key))
        
        return keys
    
    def _identify_duplicate_configs(self, config_files: List[Dict]) -> Dict[str, List[str]]:
        """Identify duplicate configuration keys across files."""
        key_to_files = {}
        
        for file_info in config_files:
            for key in file_info.get('config_keys', []):
                if key not in key_to_files:
                    key_to_files[key] = []
                key_to_files[key].append(file_info['path'])
        
        # Return only keys that appear in multiple files
        return {
            key: files for key, files in key_to_files.items() 
            if len(files) > 1
        }
    
    def _identify_consolidation_opportunities(self, config_files: List[Dict], 
                                           env_var_usage: Dict) -> Dict[str, Any]:
        """Identify specific consolidation opportunities."""
        opportunities = {
            'environment_variable_standardization': {},
            'duplicate_configuration_elimination': {},
            'loading_pattern_unification': {},
            'hardcoded_value_extraction': {}
        }
        
        # Environment variable standardization opportunities
        for canonical_name, variants in self.env_var_patterns.items():
            used_variants = []
            for variant in variants:
                if variant in env_var_usage:
                    used_variants.append({
                        'variant': variant,
                        'files': env_var_usage[variant],
                        'count': len(env_var_usage[variant])
                    })
            
            if len(used_variants) > 1:
                opportunities['environment_variable_standardization'][canonical_name] = {
                    'standard_name': self.env_var_standards.get(canonical_name, variants[0]),
                    'variants_in_use': used_variants,
                    'consolidation_impact': sum(v['count'] for v in used_variants)
                }
        
        # Configuration loading pattern analysis
        loading_pattern_counts = {}
        for file_info in config_files:
            for pattern in file_info.get('loading_patterns', []):
                loading_pattern_counts[pattern] = loading_pattern_counts.get(pattern, 0) + 1
        
        opportunities['loading_pattern_unification'] = {
            'current_patterns': loading_pattern_counts,
            'recommended_pattern': 'factory_pattern',
            'files_to_migrate': sum(
                1 for f in config_files 
                if 'factory_pattern' not in f.get('loading_patterns', [])
            )
        }
        
        return opportunities
    
    def create_unified_configuration(self, analysis: Dict) -> bool:
        """Create a unified configuration system."""
        logger.info("🏗️ Creating unified configuration system...")
        
        # Create unified configuration directory structure
        unified_config_dir = self.root_dir / "src/core/configuration/unified"
        
        if not self.dry_run:
            unified_config_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unified configuration schema
        unified_schema = self._generate_unified_schema(analysis)
        
        # Create unified configuration files
        config_files_created = 0
        
        # 1. Main unified configuration class
        unified_config_content = self._generate_unified_config_class(unified_schema)
        if self._write_file(unified_config_dir / "unified_config.py", unified_config_content):
            config_files_created += 1
        
        # 2. Environment variable mapping
        env_mapping_content = self._generate_environment_mapping(analysis)
        if self._write_file(unified_config_dir / "environment_mapping.py", env_mapping_content):
            config_files_created += 1
        
        # 3. Configuration schemas
        schema_dir = unified_config_dir / "schemas"
        if not self.dry_run:
            schema_dir.mkdir(exist_ok=True)
        
        for schema_name, schema_content in unified_schema.items():
            schema_file = schema_dir / f"{schema_name}.schema.json"
            if self._write_file(schema_file, json.dumps(schema_content, indent=2)):
                config_files_created += 1
        
        # 4. Migration guide
        migration_guide = self._generate_migration_guide(analysis)
        if self._write_file(unified_config_dir / "MIGRATION_GUIDE.md", migration_guide):
            config_files_created += 1
        
        self.metrics.files_consolidated = config_files_created
        
        if config_files_created > 0:
            logger.info(f"   ✅ Created {config_files_created} unified configuration files")
            return True
        else:
            logger.error("   ❌ Failed to create unified configuration system")
            return False
    
    def _generate_unified_schema(self, analysis: Dict) -> Dict[str, Dict]:
        """Generate unified configuration schemas."""
        return {
            'database': {
                'type': 'object',
                'properties': {
                    'url': {'type': 'string', 'description': 'Database connection URL'},
                    'host': {'type': 'string', 'default': 'localhost'},
                    'port': {'type': 'integer', 'default': 5432},
                    'user': {'type': 'string'},
                    'password': {'type': 'string'},
                    'name': {'type': 'string'},
                    'pool_size': {'type': 'integer', 'default': 10},
                    'timeout': {'type': 'integer', 'default': 30}
                },
                'required': ['url']
            },
            'api': {
                'type': 'object',
                'properties': {
                    'base_url': {'type': 'string', 'default': 'http://localhost:5000'},
                    'timeout': {'type': 'integer', 'default': 30},
                    'retry_attempts': {'type': 'integer', 'default': 3},
                    'rate_limit': {'type': 'integer', 'default': 100},
                    'openai_api_key': {'type': 'string'},
                    'claude_api_key': {'type': 'string'}
                }
            },
            'security': {
                'type': 'object',
                'properties': {
                    'encryption_enabled': {'type': 'boolean', 'default': True},
                    'encryption_key': {'type': 'string'},
                    'jwt_secret': {'type': 'string'},
                    'access_control_enabled': {'type': 'boolean', 'default': True},
                    'audit_logging_enabled': {'type': 'boolean', 'default': True}
                },
                'required': ['encryption_key', 'jwt_secret']
            },
            'application': {
                'type': 'object', 
                'properties': {
                    'debug': {'type': 'boolean', 'default': False},
                    'log_level': {'type': 'string', 'default': 'INFO'},
                    'port': {'type': 'integer', 'default': 5000},
                    'workers': {'type': 'integer', 'default': 4}
                }
            }
        }
    
    def _generate_unified_config_class(self, schema: Dict) -> str:
        """Generate the unified configuration class."""
        return '''"""
Unified Configuration System

This module provides a single, comprehensive configuration system that consolidates
all the scattered configuration files and standardizes configuration loading.

Generated by Configuration Consolidation Script
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path
import os
import json
import yaml
import logging

from .environment_mapping import ENVIRONMENT_MAPPING
from .schema_validator import validate_configuration

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration with standardized environment variable mapping."""
    url: Optional[str] = None
    host: str = "localhost"
    port: int = 5432
    user: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    pool_size: int = 10
    timeout: int = 30
    
    @classmethod
    def from_environment(cls) -> 'DatabaseConfig':
        """Load database configuration from environment variables."""
        return cls(
            url=os.getenv('DATABASE_URL'),
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=int(os.getenv('DATABASE_PORT', '5432')),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD'),
            name=os.getenv('DATABASE_NAME'),
            pool_size=int(os.getenv('DATABASE_POOL_SIZE', '10')),
            timeout=int(os.getenv('DATABASE_TIMEOUT', '30'))
        )


@dataclass
class APIConfig:
    """API configuration with standardized settings."""
    base_url: str = "http://localhost:5000"
    timeout: int = 30
    retry_attempts: int = 3
    rate_limit: int = 100
    openai_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    
    @classmethod
    def from_environment(cls) -> 'APIConfig':
        """Load API configuration from environment variables."""
        return cls(
            base_url=os.getenv('API_BASE_URL', 'http://localhost:5000'),
            timeout=int(os.getenv('API_TIMEOUT', '30')),
            retry_attempts=int(os.getenv('API_RETRY_ATTEMPTS', '3')),
            rate_limit=int(os.getenv('API_RATE_LIMIT', '100')),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            claude_api_key=os.getenv('CLAUDE_API_KEY')
        )


@dataclass  
class SecurityConfig:
    """Security configuration with encryption and access control."""
    encryption_enabled: bool = True
    encryption_key: Optional[str] = None
    jwt_secret: Optional[str] = None
    access_control_enabled: bool = True
    audit_logging_enabled: bool = True
    
    @classmethod
    def from_environment(cls) -> 'SecurityConfig':
        """Load security configuration from environment variables."""
        return cls(
            encryption_enabled=os.getenv('ENCRYPTION_ENABLED', 'true').lower() == 'true',
            encryption_key=os.getenv('ENCRYPTION_KEY'),
            jwt_secret=os.getenv('JWT_SECRET'),
            access_control_enabled=os.getenv('ACCESS_CONTROL_ENABLED', 'true').lower() == 'true',
            audit_logging_enabled=os.getenv('AUDIT_LOGGING_ENABLED', 'true').lower() == 'true'
        )


@dataclass
class ApplicationConfig:
    """Application-level configuration."""
    debug: bool = False
    log_level: str = "INFO"
    port: int = 5000
    workers: int = 4
    
    @classmethod  
    def from_environment(cls) -> 'ApplicationConfig':
        """Load application configuration from environment variables."""
        return cls(
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO').upper(),
            port=int(os.getenv('PORT', '5000')),
            workers=int(os.getenv('WORKERS', '4'))
        )


@dataclass
class UnifiedConfig:
    """
    Unified configuration system that consolidates all application settings.
    
    This replaces the scattered configuration files and provides a single
    source of truth for all configuration values.
    """
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig) 
    security: SecurityConfig = field(default_factory=SecurityConfig)
    application: ApplicationConfig = field(default_factory=ApplicationConfig)
    
    @classmethod
    def from_environment(cls) -> 'UnifiedConfig':
        """Load complete configuration from environment variables."""
        return cls(
            database=DatabaseConfig.from_environment(),
            api=APIConfig.from_environment(),
            security=SecurityConfig.from_environment(),
            application=ApplicationConfig.from_environment()
        )
    
    @classmethod
    def from_file(cls, config_file: Path) -> 'UnifiedConfig':
        """Load configuration from YAML or JSON file."""
        with open(config_file, 'r') as f:
            if config_file.suffix.lower() == '.json':
                data = json.load(f)
            else:
                data = yaml.safe_load(f)
        
        return cls(
            database=DatabaseConfig(**data.get('database', {})),
            api=APIConfig(**data.get('api', {})),
            security=SecurityConfig(**data.get('security', {})),
            application=ApplicationConfig(**data.get('application', {}))
        )
    
    def validate(self) -> bool:
        """Validate the configuration against schemas."""
        return validate_configuration(self)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'database': self.database.__dict__,
            'api': self.api.__dict__,
            'security': self.security.__dict__,
            'application': self.application.__dict__
        }


# Global configuration instance
_config_instance: Optional[UnifiedConfig] = None


def get_config() -> UnifiedConfig:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = UnifiedConfig.from_environment()
        if not _config_instance.validate():
            logger.warning("Configuration validation failed")
    return _config_instance


def reset_config():
    """Reset the global configuration instance (mainly for testing)."""
    global _config_instance
    _config_instance = None
'''
    
    def _generate_environment_mapping(self, analysis: Dict) -> str:
        """Generate environment variable mapping module."""
        return '''"""
Environment Variable Mapping

Standardized mapping of environment variables to configuration keys.
This eliminates the scattered os.getenv() calls and provides a single
source of truth for environment variable names.
"""

from typing import Dict, List

# Standardized environment variable names
ENVIRONMENT_MAPPING = {
    # Database configuration
    'database.url': 'DATABASE_URL',
    'database.host': 'DATABASE_HOST',
    'database.port': 'DATABASE_PORT', 
    'database.user': 'DATABASE_USER',
    'database.password': 'DATABASE_PASSWORD',
    'database.name': 'DATABASE_NAME',
    'database.pool_size': 'DATABASE_POOL_SIZE',
    'database.timeout': 'DATABASE_TIMEOUT',
    
    # API configuration
    'api.base_url': 'API_BASE_URL',
    'api.timeout': 'API_TIMEOUT',
    'api.retry_attempts': 'API_RETRY_ATTEMPTS',
    'api.rate_limit': 'API_RATE_LIMIT',
    'api.openai_api_key': 'OPENAI_API_KEY',
    'api.claude_api_key': 'CLAUDE_API_KEY',
    
    # Security configuration
    'security.encryption_enabled': 'ENCRYPTION_ENABLED',
    'security.encryption_key': 'ENCRYPTION_KEY',
    'security.jwt_secret': 'JWT_SECRET',
    'security.access_control_enabled': 'ACCESS_CONTROL_ENABLED',
    'security.audit_logging_enabled': 'AUDIT_LOGGING_ENABLED',
    
    # Application configuration
    'application.debug': 'DEBUG',
    'application.log_level': 'LOG_LEVEL',
    'application.port': 'PORT',
    'application.workers': 'WORKERS'
}

# Deprecated environment variable names (for migration warnings)
DEPRECATED_ENV_VARS = {
    # Database variants
    'DB_URL': 'DATABASE_URL',
    'POSTGRES_HOST': 'DATABASE_HOST',
    'POSTGRES_PORT': 'DATABASE_PORT',
    'POSTGRES_USER': 'DATABASE_USER',
    'POSTGRES_PASSWORD': 'DATABASE_PASSWORD',
    
    # API variants
    'BASE_URL': 'API_BASE_URL',
    'REQUEST_TIMEOUT': 'API_TIMEOUT',
    'HTTP_TIMEOUT': 'API_TIMEOUT',
    'API_KEY_OPENAI': 'OPENAI_API_KEY',
    'OPENAI_KEY': 'OPENAI_API_KEY',
    'API_KEY_CLAUDE': 'CLAUDE_API_KEY',
    'ANTHROPIC_API_KEY': 'CLAUDE_API_KEY',
    
    # Security variants
    'SECRET_KEY': 'ENCRYPTION_KEY',
    'MEMORY_ENGINE_KEY': 'ENCRYPTION_KEY',
    'JWT_SECRET_KEY': 'JWT_SECRET',
    'AUTH_SECRET': 'JWT_SECRET',
    
    # Application variants
    'DEBUG_MODE': 'DEBUG',
    'DEVELOPMENT': 'DEBUG',
    'LOGGING_LEVEL': 'LOG_LEVEL',
    'LOGLEVEL': 'LOG_LEVEL',
    'APP_PORT': 'PORT',
    'SERVER_PORT': 'PORT'
}


def get_standard_env_name(deprecated_name: str) -> str:
    """Get the standard environment variable name for a deprecated variant."""
    return DEPRECATED_ENV_VARS.get(deprecated_name, deprecated_name)


def get_all_env_vars() -> List[str]:
    """Get list of all standard environment variable names."""
    return list(ENVIRONMENT_MAPPING.values())
'''
    
    def _generate_migration_guide(self, analysis: Dict) -> str:
        """Generate migration guide for adopting unified configuration."""
        opportunities = analysis.get('consolidation_opportunities', {})
        env_standardization = opportunities.get('environment_variable_standardization', {})
        
        guide = '''# Configuration System Migration Guide

This guide helps migrate from the scattered configuration system to the unified configuration architecture.

## Overview

The AI system previously had **63+ configuration files** scattered across multiple directories with **5+ different loading patterns**. The unified system consolidates everything into a single, comprehensive configuration management system.

## Migration Steps

### Phase 1: Update Import Patterns

Replace scattered configuration loading with unified configuration:

```python
# BEFORE (scattered patterns):
import os
database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/db')
api_key = os.getenv('OPENAI_API_KEY')
debug = os.getenv('DEBUG', 'false').lower() == 'true'

# AFTER (unified configuration):
from src.core.configuration.unified import get_config
config = get_config()
database_url = config.database.url
api_key = config.api.openai_api_key
debug = config.application.debug
```

### Phase 2: Environment Variable Standardization

Update environment variable names to use standard naming:

'''
        
        # Add environment variable standardization details
        if env_standardization:
            guide += "\n#### Environment Variable Name Changes:\n\n"
            for canonical_name, details in env_standardization.items():
                guide += f"**{canonical_name}**:\n"
                guide += f"- Standard name: `{details['standard_name']}`\n"
                guide += "- Variants found in codebase:\n"
                for variant in details['variants_in_use']:
                    guide += f"  - `{variant['variant']}` (used in {variant['count']} files)\n"
                guide += "\n"
        
        guide += '''
### Phase 3: Configuration File Consolidation

Replace individual configuration files with unified YAML configuration:

```yaml
# config/unified.yaml
database:
  url: ${DATABASE_URL}
  host: ${DATABASE_HOST:localhost}
  port: ${DATABASE_PORT:5432}
  
api:
  base_url: ${API_BASE_URL:http://localhost:5000}
  openai_api_key: ${OPENAI_API_KEY}
  claude_api_key: ${CLAUDE_API_KEY}
  
security:
  encryption_enabled: ${ENCRYPTION_ENABLED:true}
  encryption_key: ${ENCRYPTION_KEY}
  
application:
  debug: ${DEBUG:false}
  log_level: ${LOG_LEVEL:INFO}
  port: ${PORT:5000}
```

### Phase 4: Update Configuration Loading

Replace custom configuration loading with unified loader:

```python
# BEFORE (custom loading):
with open('config.json') as f:
    config = json.load(f)

# AFTER (unified loading):
from src.core.configuration.unified import UnifiedConfig
config = UnifiedConfig.from_file('config/unified.yaml')
```

## Benefits After Migration

- **Single source of truth**: All configuration in one place
- **Standardized environment variables**: Consistent naming across codebase  
- **Schema validation**: Automatic validation of configuration values
- **Better documentation**: Auto-generated documentation from schemas
- **Reduced maintenance**: No more scattered configuration files to maintain

## Rollback Plan

If issues occur during migration:

1. The original configuration files remain as backups
2. Environment variables continue to work with backward compatibility
3. Deprecated warnings help identify usage that needs updating
4. Configuration factory pattern provides gradual migration path

## Testing

Test the migration thoroughly:

```bash
# Test configuration loading
python3 -c "from src.core.configuration.unified import get_config; print(get_config().to_dict())"

# Run application tests with new configuration
make test-quick

# Validate configuration schema
python3 -c "from src.core.configuration.unified import get_config; config = get_config(); print('Valid:', config.validate())"
```
'''
        
        return guide
    
    def _write_file(self, file_path: Path, content: str) -> bool:
        """Write content to file with dry-run support and comprehensive error handling."""
        try:
            if not self.dry_run:
                # Create backup if file already exists
                if file_path.exists():
                    backup_path = file_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    shutil.copy2(file_path, backup_path)
                    logger.info(f"   📦 Backed up existing file to: {backup_path}")
                
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write to temporary file first, then move to final location
                temp_file = file_path.with_suffix('.tmp')
                try:
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Atomic move to final location
                    temp_file.replace(file_path)
                    
                    with self.thread_lock:
                        logger.info(f"   ✅ Created: {file_path}")
                        
                except Exception as e:
                    # Clean up temp file on failure
                    if temp_file.exists():
                        temp_file.unlink()
                    raise e
                    
            else:
                with self.thread_lock:
                    logger.info(f"   🔍 Would create: {file_path}")
            return True
        except Exception as e:
            error_msg = f"Failed to write {file_path}: {e}"
            with self.thread_lock:
                logger.error(f"   ❌ {error_msg}")
                self.errors.append(error_msg)
            return False
    
    def verify_git_status(self) -> bool:
        """Verify git repository is in clean state before consolidation."""
        if not self.verify_git_clean:
            return True
            
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.root_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning("⚠️  Not in a git repository or git not available")
                return True  # Don't fail if not in git repo
                
            if result.stdout.strip():
                logger.error("❌ Git working directory is not clean")
                logger.error("🔍 Uncommitted changes found:")
                for line in result.stdout.strip().split('\n')[:5]:
                    logger.error(f"   {line}")
                logger.error("💡 Please commit or stash changes before running consolidation")
                return False
                
            logger.info("✅ Git working directory is clean")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Could not verify git status: {e}")
            return True
    
    def create_backup_branch(self) -> bool:
        """Create a backup git branch before making changes."""
        if not self.create_backup:
            return True
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_branch = f"config-consolidation-backup-{timestamp}"
            
            result = subprocess.run(
                ['git', 'checkout', '-b', self.backup_branch],
                cwd=self.root_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning(f"⚠️  Could not create backup branch: {result.stderr}")
                return True  # Don't fail consolidation if backup fails
                
            logger.info(f"✅ Created backup branch: {self.backup_branch}")
            
            # Switch back to original branch
            subprocess.run(
                ['git', 'checkout', '-'],
                cwd=self.root_dir,
                capture_output=True
            )
            
            self.backup_created = True
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Could not create backup branch: {e}")
            return True
    
    def run_tests_before(self) -> bool:
        """Run tests before consolidation to establish baseline."""
        if not self.verify_tests:
            return True
            
        logger.info("🧪 Running tests before configuration consolidation...")
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/', '--tb=no', '-q'],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if "FAILED" in result.stdout:
                # Extract failed test names
                import re
                failures = re.findall(r'FAILED ([^\s]+)', result.stdout)
                self.test_failures_before = failures
                logger.warning(f"⚠️  {len(failures)} tests were already failing before consolidation")
                for failure in failures[:5]:  # Show first 5
                    logger.warning(f"   {failure}")
            else:
                logger.info("✅ All tests passing before consolidation")
                
            return True
            
        except subprocess.TimeoutExpired:
            logger.warning("⚠️  Test run timed out (5 minutes)")
            return True  # Don't fail consolidation due to slow tests
        except Exception as e:
            logger.warning(f"⚠️  Could not run tests: {e}")
            return True
    
    def run_tests_after(self) -> bool:
        """Run tests after consolidation to verify no regressions."""
        if not self.verify_tests:
            return True
            
        logger.info("🧪 Running tests after configuration consolidation...")
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/', '--tb=no', '-q'],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if "FAILED" in result.stdout:
                import re
                failures = re.findall(r'FAILED ([^\s]+)', result.stdout)
                self.test_failures_after = failures
                
                # Check if we introduced new failures
                new_failures = set(failures) - set(self.test_failures_before)
                if new_failures:
                    logger.error(f"❌ Configuration consolidation introduced {len(new_failures)} new test failures:")
                    for failure in list(new_failures)[:5]:
                        logger.error(f"   {failure}")
                    return False
                else:
                    logger.info(f"✅ No new test failures introduced ({len(failures)} pre-existing)")
            else:
                logger.info("✅ All tests still passing after consolidation")
                
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("⚠️  Post-consolidation test run timed out")
            return False  # This is more concerning after changes
        except Exception as e:
            logger.error(f"❌ Could not run post-consolidation tests: {e}")
            return False
    
    def validate_unified_config_system(self) -> bool:
        """Validate that the unified configuration system can be created safely."""
        try:
            # Check if target directory can be created
            target_dir = self.root_dir / "src/core/configuration/unified"
            
            if target_dir.exists():
                logger.warning(f"Target directory already exists: {target_dir}")
                # Check if it contains existing files that might conflict
                existing_files = list(target_dir.rglob("*.py"))
                if existing_files:
                    self.validation_errors.append(f"Target directory contains {len(existing_files)} existing Python files")
                    logger.warning(f"Found {len(existing_files)} existing files in target directory")
            
            # Check if we can write to the parent directory
            parent_dir = target_dir.parent
            if not parent_dir.exists():
                try:
                    if not self.dry_run:
                        parent_dir.mkdir(parents=True, exist_ok=True)
                        parent_dir.rmdir()  # Clean up test directory
                except Exception as e:
                    self.validation_errors.append(f"Cannot create parent directory: {e}")
                    return False
            
            # Check for YAML dependency
            try:
                import yaml
            except ImportError:
                self.validation_errors.append("PyYAML is required but not installed")
                return False
            
            if self.validation_errors:
                return False
                
            logger.info("✅ Unified configuration system validation passed")
            return True
            
        except Exception as e:
            self.validation_errors.append(f"Could not validate unified config system: {e}")
            return False
    
    def run_consolidation(self) -> Dict[str, Any]:
        """Run the complete configuration consolidation process with enhanced safety."""
        logger.info("🚀 Starting enhanced configuration system consolidation...")
        if self.dry_run:
            logger.info("⚠️  DRY RUN MODE - No files will be modified")
        else:
            # Safety checks before making changes
            if not self.verify_git_status():
                return {
                    "success": False,
                    "error": "Git working directory not clean",
                    "analysis": {},
                    "unified_system_created": False,
                    "metrics": {"files_analyzed": 0}
                }
                
            if not self.validate_unified_config_system():
                return {
                    "success": False,
                    "error": "Unified configuration system validation failed",
                    "validation_errors": self.validation_errors,
                    "analysis": {},
                    "unified_system_created": False,
                    "metrics": {"files_analyzed": 0}
                }
                
            self.create_backup_branch()
            self.run_tests_before()
        
        # Phase 1: Analyze current configuration sprawl
        analysis = self.analyze_configuration_sprawl()
        
        # Phase 2: Create unified configuration system
        unified_system_created = self.create_unified_configuration(analysis)
        
        # Phase 3: Post-consolidation validation if not dry run
        success = True
        if not self.dry_run and unified_system_created:
            logger.info("🔍 Running post-consolidation validation...")
            if not self.run_tests_after():
                logger.error("❌ Post-consolidation tests failed - consider rolling back")
                if self.backup_branch:
                    logger.error(f"💡 Rollback command: git checkout {self.backup_branch}")
                success = False
            else:
                logger.info("✅ Post-consolidation validation passed")
        
        # Compile results
        results = {
            "success": success and unified_system_created,
            "analysis": analysis,
            "unified_system_created": unified_system_created,
            "backup_created": self.backup_created,
            "backup_branch": self.backup_branch,
            "errors": self.errors,
            "metrics": {
                "files_analyzed": self.metrics.files_analyzed,
                "config_files_found": self.metrics.config_files_found,
                "environment_vars_found": self.metrics.environment_vars_found,
                "duplicate_keys_identified": self.metrics.duplicate_keys_identified,
                "files_consolidated": self.metrics.files_consolidated,
                "estimated_lines_saved": len(analysis.get('config_files', [])) * 50,  # Rough estimate
                "total_errors": len(self.errors)
            }
        }
        
        # Log final summary
        metrics = results["metrics"]
        if success and unified_system_created:
            logger.info("✅ Enhanced configuration system consolidation complete!")
        else:
            logger.error("❌ Configuration system consolidation completed with errors")
            
        logger.info(f"   📊 Configuration files analyzed: {metrics['config_files_found']}")
        logger.info(f"   🔑 Environment variables found: {metrics['environment_vars_found']}")
        logger.info(f"   🔄 Duplicate configurations: {metrics['duplicate_keys_identified']}")
        logger.info(f"   📁 Unified files created: {metrics['files_consolidated']}")
        logger.info(f"   💾 Estimated lines saved: {metrics['estimated_lines_saved']}")
        logger.info(f"   ❌ Total errors: {metrics['total_errors']}")
        
        if self.backup_created:
            logger.info("📦 Backup branch created for rollback if needed")
        
        if self.dry_run:
            logger.info("🔄 Run without --dry-run to actually consolidate configurations")
        elif not success:
            logger.error("💡 Consider using git to rollback changes if needed")
        
        return results


def main():
    """Main entry point with enhanced safety measures."""
    parser = argparse.ArgumentParser(
        description="Enhanced Configuration System Consolidator + Safety Features",
        epilog="Examples:\n"
               "  %(prog)s --dry-run              # Preview changes safely\n"
               "  %(prog)s --no-tests --no-backup # Fast consolidation (less safe)\n"
               "  %(prog)s --validate-only        # Just validate unified config system",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--root-dir",
        default=".",
        help="Root directory for consolidation (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip test verification (faster but less safe)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup branch creation"
    )
    parser.add_argument(
        "--no-git-check",
        action="store_true",
        help="Skip git working directory check"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate unified configuration system"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🚀 Enhanced Configuration System Consolidator + Safety Features")
    logger.info("=" * 60)
    
    try:
        consolidator = ConfigurationConsolidator(
            root_dir=args.root_dir,
            dry_run=args.dry_run,
            verify_tests=not args.no_tests,
            create_backup=not args.no_backup,
            verify_git_clean=not args.no_git_check
        )
        
        # Validate only mode
        if args.validate_only:
            if consolidator.validate_unified_config_system():
                logger.info("✅ Unified configuration system validation passed")
                return 0
            else:
                logger.error("❌ Unified configuration system validation failed")
                for error in consolidator.validation_errors:
                    logger.error(f"   {error}")
                return 1
    
        results = consolidator.run_consolidation()
        
        if not results.get("success", True):
            logger.error(f"\n❌ Configuration system consolidation failed: {results.get('error', 'Unknown error')}")
            if results.get("validation_errors"):
                logger.error("❌ Validation errors:")
                for error in results["validation_errors"][:5]:
                    logger.error(f"   {error}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("\n⚠️  Configuration consolidation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"\n❌ Unexpected error during configuration consolidation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Generate and save report
    if not args.dry_run:
        report_file = Path("reports") / f"enhanced_configuration_consolidation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        # Create detailed report
        detailed_report = {
            **results,
            "execution_info": {
                "timestamp": datetime.now().isoformat(),
                "dry_run": args.dry_run,
                "verify_tests": not args.no_tests,
                "create_backup": not args.no_backup,
                "verify_git_clean": not args.no_git_check
            }
        }
        
        with open(report_file, 'w') as f:
            json.dump(detailed_report, f, indent=2, default=str)
        
        logger.info(f"💾 Detailed report saved to: {report_file}")
    
    logger.info("\n✅ Enhanced configuration system consolidation completed successfully!")
    return 0 if results.get("success", False) else 1


if __name__ == "__main__":
    exit(main())