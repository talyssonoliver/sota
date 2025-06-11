"""
Memory Engine Configuration Management
Centralized configuration for all memory system components
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


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
    use_semantic_chunking: bool = True


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
class StorageConfig:
    """Tiered storage configuration"""
    hot_storage_limit_mb: int = 500
    warm_storage_limit_gb: int = 5
    cold_storage_enabled: bool = True
    migration_interval_hours: int = 24


@dataclass
class MemoryEngineConfig:
    """Main memory engine configuration"""
    
    # Core settings
    collection_name: str = "agent_memory"
    knowledge_base_path: str = "data/context/"
    embedding_model: str = "text-embedding-3-small"
    
    # Component configurations
    cache: CacheConfig = field(default_factory=CacheConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    resource: ResourceConfig = field(default_factory=ResourceConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    
    # Security settings
    encryption_enabled: bool = True
    pii_detection_enabled: bool = True
    access_control_enabled: bool = True
    audit_logging_enabled: bool = True
    
    # Performance settings
    enable_caching: bool = True
    enable_tiered_storage: bool = True
    enable_resource_monitoring: bool = True
    
    # Additional settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'MemoryEngineConfig':
        """Create config from dictionary"""
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'collection_name': self.collection_name,
            'knowledge_base_path': self.knowledge_base_path,
            'embedding_model': self.embedding_model,
            'cache': self.cache.__dict__,
            'chunking': self.chunking.__dict__,
            'retrieval': self.retrieval.__dict__,
            'resource': self.resource.__dict__,
            'storage': self.storage.__dict__,
            'encryption_enabled': self.encryption_enabled,
            'pii_detection_enabled': self.pii_detection_enabled,
            'access_control_enabled': self.access_control_enabled,
            'audit_logging_enabled': self.audit_logging_enabled,
            'enable_caching': self.enable_caching,
            'enable_tiered_storage': self.enable_tiered_storage,
            'enable_resource_monitoring': self.enable_resource_monitoring,
            'custom_settings': self.custom_settings
        }