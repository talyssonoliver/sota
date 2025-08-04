
from src.infrastructure.utils.common_imports import Enum, dataclass
"""
Memory Service Interfaces

Abstract interfaces for memory management services, breaking
dependency on specific ChromaDB or caching implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
# from dataclasses import dataclass  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports


class MemoryType(Enum):
    """Types of memory storage"""
    VECTOR = "vector"
    CACHE = "cache"
    PERSISTENT = "persistent"
    TEMPORARY = "temporary"


@dataclass
class MemoryQuery:
    """Memory query specification"""
    query_text: str
    memory_type: MemoryType
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None
    similarity_threshold: float = 0.7


@dataclass
class MemoryItem:
    """Memory item representation"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    score: Optional[float] = None
    timestamp: Optional[str] = None


@dataclass
class MemoryStats:
    """Memory system statistics"""
    total_items: int
    memory_usage_mb: float
    cache_hit_rate: float
    average_retrieval_time_ms: float


class IMemoryProvider(ABC):
    """Interface for memory storage providers"""
    
    @abstractmethod
    async def store(self, key: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store data in memory"""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory"""
        pass
    
    @abstractmethod
    async def search(self, query: MemoryQuery) -> List[MemoryItem]:
        """Search memory with query"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete data from memory"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in memory"""
        pass
    
    @abstractmethod
    async def clear(self, memory_type: Optional[MemoryType] = None) -> bool:
        """Clear memory (optionally by type)"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> MemoryStats:
        """Get memory statistics"""
        pass


class ICacheManager(ABC):
    """Interface for cache management"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache"""
        pass
    
    @abstractmethod
    async def get_ttl(self, key: str) -> Optional[int]:
        """Get TTL for key"""
        pass
    
    @abstractmethod
    async def extend_ttl(self, key: str, ttl: int) -> bool:
        """Extend TTL for key"""
        pass
    
    @abstractmethod
    async def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information and statistics"""
        pass


class IMemoryEngine(ABC):
    """High-level interface for memory engine"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize memory engine with configuration"""
        pass
    
    @abstractmethod
    async def store_context(self, context_id: str, content: str, metadata: Dict[str, Any]) -> bool:
        """Store contextual information"""
        pass
    
    @abstractmethod
    async def retrieve_context(self, context_id: str) -> Optional[MemoryItem]:
        """Retrieve contextual information"""
        pass
    
    @abstractmethod
    async def search_similar_context(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """Search for similar contextual information"""
        pass
    
    @abstractmethod
    async def store_task_memory(self, task_id: str, memory_data: Dict[str, Any]) -> bool:
        """Store task-related memory"""
        pass
    
    @abstractmethod
    async def retrieve_task_memory(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve task-related memory"""
        pass
    
    @abstractmethod
    async def update_memory_item(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing memory item"""
        pass
    
    @abstractmethod
    async def delete_memory_item(self, item_id: str) -> bool:
        """Delete memory item"""
        pass
    
    @abstractmethod
    async def get_memory_by_tags(self, tags: List[str]) -> List[MemoryItem]:
        """Get memory items by tags"""
        pass
    
    @abstractmethod
    async def add_tags_to_memory(self, item_id: str, tags: List[str]) -> bool:
        """Add tags to memory item"""
        pass
    
    @abstractmethod
    async def get_recent_memories(self, limit: int = 10) -> List[MemoryItem]:
        """Get recently stored memories"""
        pass
    
    @abstractmethod
    async def backup_memory(self, backup_path: str) -> bool:
        """Backup memory to specified path"""
        pass
    
    @abstractmethod
    async def restore_memory(self, backup_path: str) -> bool:
        """Restore memory from backup"""
        pass
    
    @abstractmethod
    async def optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory storage and return statistics"""
        pass
    
    @abstractmethod
    async def validate_memory_integrity(self) -> Dict[str, Any]:
        """Validate memory integrity and return report"""
        pass
    
    @abstractmethod
    async def get_health_status(self) -> Dict[str, Any]:
        """Get memory engine health status"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Gracefully shutdown memory engine"""
        pass


class IMemoryIndexer(ABC):
    """Interface for memory indexing and search optimization"""
    
    @abstractmethod
    async def build_index(self, memory_type: MemoryType) -> bool:
        """Build search index for memory type"""
        pass
    
    @abstractmethod
    async def rebuild_index(self, memory_type: MemoryType) -> bool:
        """Rebuild search index for memory type"""
        pass
    
    @abstractmethod
    async def optimize_index(self, memory_type: MemoryType) -> Dict[str, Any]:
        """Optimize search index and return statistics"""
        pass
    
    @abstractmethod
    async def get_index_stats(self, memory_type: MemoryType) -> Dict[str, Any]:
        """Get index statistics"""
        pass


class IMemoryEncryption(ABC):
    """Interface for memory encryption services"""
    
    @abstractmethod
    async def encrypt_data(self, data: Any) -> bytes:
        """Encrypt data for storage"""
        pass
    
    @abstractmethod
    async def decrypt_data(self, encrypted_data: bytes) -> Any:
        """Decrypt data from storage"""
        pass
    
    @abstractmethod
    async def rotate_encryption_key(self) -> bool:
        """Rotate encryption key"""
        pass
    
    @abstractmethod
    async def get_encryption_status(self) -> Dict[str, Any]:
        """Get encryption status and configuration"""
        pass


class IMemoryCompression(ABC):
    """Interface for memory compression services"""
    
    @abstractmethod
    async def compress_data(self, data: Any) -> bytes:
        """Compress data for storage"""
        pass
    
    @abstractmethod
    async def decompress_data(self, compressed_data: bytes) -> Any:
        """Decompress data from storage"""
        pass
    
    @abstractmethod
    async def get_compression_ratio(self) -> float:
        """Get current compression ratio"""
        pass
    
    @abstractmethod
    async def optimize_compression(self) -> Dict[str, Any]:
        """Optimize compression settings"""
        pass