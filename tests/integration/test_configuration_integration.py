import json

# Add project root to path
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def integration_environment():
    """Set up integration test environment for configuration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create configuration directory structure
        config_root = Path(temp_dir) / "config"
        config_root.mkdir(parents=True, exist_ok=True)

        # Create environment-specific configs
        envs = ["development", "staging", "production"]
        for env in envs:
            env_dir = config_root / env
            env_dir.mkdir(exist_ok=True)

        # Base configuration
        base_config = {
            "system": {"name": "AI System", "version": "1.0.0", "debug": False},
            "paths": {
                "data": "${BASE_DIR}/data",
                "logs": "${BASE_DIR}/logs",
                "cache": "${BASE_DIR}/cache",
            },
            "agents": {
                "default_timeout": 300,
                "max_retries": 3,
                "memory_enabled": True,
            },
            "workflows": {
                "max_concurrent": 5,
                "checkpoint_interval": 100,
                "state_persistence": True,
            },
            "memory": {
                "cache_size_mb": 100,
                "hot_ttl_hours": 24,
                "encryption_enabled": False,
            },
        }

        # Environment-specific overrides
        env_configs = {
            "development": {
                "system": {"debug": True},
                "memory": {"encryption_enabled": False},
                "workflows": {"max_concurrent": 2},
            },
            "staging": {
                "system": {"debug": False},
                "memory": {"encryption_enabled": True},
                "workflows": {"max_concurrent": 3},
            },
            "production": {
                "system": {"debug": False},
                "memory": {"encryption_enabled": True, "cache_size_mb": 500},
                "workflows": {"max_concurrent": 10, "checkpoint_interval": 50},
            },
        }

        # Write base config
        base_file = config_root / "base.yaml"
        with open(base_file, "w") as f:
            yaml.dump(base_config, f)

        # Write environment configs
        for env, config in env_configs.items():
            env_file = config_root / env / "config.yaml"
            with open(env_file, "w") as f:
                yaml.dump(config, f)

        # Create secrets file
        secrets = {
            "api_keys": {"openai": "sk-test-key", "github": "ghp-test-token"},
            "database": {"password": "test-password"},
        }

        secrets_file = config_root / ".secrets.json"
        with open(secrets_file, "w") as f:
            json.dump(secrets, f)

        yield {
            "temp_dir": temp_dir,
            "config_root": config_root,
            "base_config": base_config,
            "env_configs": env_configs,
            "secrets": secrets,
        }
