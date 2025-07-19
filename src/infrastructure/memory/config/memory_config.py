#!/usr/bin/env python3
"""
Unified Memory Configuration

Consolidated configuration for all memory system components.
"""

from typing import Any, Dict

try:
    from dataclasses import dataclass, field
except ImportError:
    pass
try:
    import logging
except ImportError:
    pass


@dataclass
class CacheConfig:
    """LRU and disk cache configuration"""

    lru_maxsize: int = 1000
    disk_maxsize: int = 5000
    disk_cache_dir: str = "runtime/cache/memory_disk_cache"
    ttl_hours: int = 24


@dataclass
class ChunkingConfig:
    """Semantic chunking configuration"""

    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_chunk_size: int = 100
    max_chunk_size: int = 4000
    use_semantic_chunking: bool = True
    semantic: bool = True  # For backward compatibility
    adaptive: bool = False  # For backward compatibility
    overlap_percent: float = 0.2  # For backward compatibility
    deduplicate: bool = True  # For backward compatibility


@dataclass
class StorageConfig:
    """Tiered storage configuration"""

    hot_storage_limit_mb: int = 500
    warm_storage_limit_gb: int = 5
    cold_storage_enabled: bool = True
    migration_interval_hours: int = 24


@dataclass
class RetrievalConfig:
    """Context retrieval configuration"""

    default_k: int = 5
    max_k: int = 20
    similarity_threshold: float = 0.7
    token_budget: int = 8000
    max_tokens: int = 16000


@dataclass
class ResourceConfig:
    """Resource monitoring configuration"""

    memory_limit_mb: int = 2048
    disk_limit_gb: int = 10
    monitor_interval: int = 300


@dataclass
class MemoryEngineConfig:
    """Main memory engine configuration"""

    caching: CacheConfig = field(default_factory=CacheConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    resources: ResourceConfig = field(default_factory=ResourceConfig)

    # Embedding configuration
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimensions: int = 1536
    collection_name: str = "memory_collection"

    # Security settings
    encryption_enabled: bool = False
    pii_detection_enabled: bool = True
    access_control_enabled: bool = True
    audit_logging_enabled: bool = True
    # Caching and storage flags
    enable_caching: bool = True
    enable_tiered_storage: bool = True

    # Security options
    security_options: Dict[str, Any] = field(
        default_factory=lambda: {
            "roles": {"system": ["read", "write"]},
            "sanitize_inputs": True,
        }
    )

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "MemoryEngineConfig":
        """Create config from dictionary."""
        return cls(
            caching=CacheConfig(**config_dict.get("caching", {})),
            chunking=ChunkingConfig(**config_dict.get("chunking", {})),
            storage=StorageConfig(**config_dict.get("storage", {})),
            retrieval=RetrievalConfig(**config_dict.get("retrieval", {})),
            resources=ResourceConfig(**config_dict.get("resources", {})),
            encryption_enabled=config_dict.get("encryption_enabled", False),
            pii_detection_enabled=config_dict.get("pii_detection_enabled", True),
            access_control_enabled=config_dict.get("access_control_enabled", True),
            audit_logging_enabled=config_dict.get("audit_logging_enabled", True),
            enable_caching=config_dict.get("enable_caching", True),
            enable_tiered_storage=config_dict.get("enable_tiered_storage", True),
            security_options=config_dict.get(
                "security_options",
                {
                    "roles": {"system": ["read", "write"]},
                    "sanitize_inputs": True,
                },
            ),
        )


class MemoryConfig:
    """Unified memory system configuration."""

    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.config = self._load_default_config()

        if config_path:
            self._load_config_file(config_path)

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "engines": {
                "chroma": {
                    "enabled": True,
                    "persist_directory": "deployment/runtime/chroma_db",
                    "collection_name": "ai_system_memory",
                },
                "disk_cache": {
                    "enabled": True,
                    "cache_directory": "deployment/runtime/cache/memory_disk_cache",
                    "max_size_mb": 1024,
                },
            },
            "security": {
                "encryption_enabled": False,
                "access_control_enabled": True,
            },
            "performance": {
                "cache_ttl_seconds": 3600,
                "max_concurrent_operations": 10,
                "chunk_size": 1000,
            },
            "knowledge": {
                "context_types": ["active", "product", "technical", "system"],
                "auto_update_enabled": True,
            },
        }

    def _load_config_file(self, config_path: str):
        """Load configuration from file."""
        # Implementation for loading from YAML/JSON config file
        pass

    def get_config(self) -> Dict[str, Any]:
        """Get full configuration."""
        return self.config

    def get_engine_config(self, engine_name: str) -> Dict[str, Any]:
        """Get configuration for specific engine."""
        return self.config.get("engines", {}).get(engine_name, {})

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return self.config.get("security", {})
