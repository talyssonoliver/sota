
from src.infrastructure.utils.common_imports import Enum, dataclass, datetime
"""
Storage Service Interfaces

Abstract interfaces for data storage and repository services,
breaking dependency on specific database or file storage implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Generic, TypeVar
# from dataclasses import dataclass  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports

T = TypeVar('T')


class StorageType(Enum):
    """Types of storage backends"""
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    BLOB_STORAGE = "blob_storage"
    OBJECT_STORAGE = "object_storage"
    CACHE = "cache"


class QueryOperator(Enum):
    """Query operators for data filtering"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    IN = "in"
    NOT_IN = "not_in"
    LIKE = "like"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


@dataclass
class QueryFilter:
    """Query filter specification"""
    field: str
    operator: QueryOperator
    value: Any
    case_sensitive: bool = True


@dataclass
class QuerySort:
    """Query sort specification"""
    field: str
    ascending: bool = True


@dataclass
class QueryOptions:
    """Query options specification"""
    filters: Optional[List[QueryFilter]] = None
    sorts: Optional[List[QuerySort]] = None
    limit: Optional[int] = None
    offset: Optional[int] = 0
    include_count: bool = False


@dataclass
class QueryResult(Generic[T]):
    """Query result with metadata"""
    items: List[T]
    total_count: Optional[int] = None
    has_more: bool = False
    offset: int = 0
    limit: Optional[int] = None


@dataclass
class StorageStats:
    """Storage system statistics"""
    total_items: int
    storage_size_bytes: int
    available_space_bytes: Optional[int] = None
    last_backup: Optional[datetime] = None
    health_status: str = "healthy"


class IDataRepository(ABC, Generic[T]):
    """Generic interface for data repository operations"""
    
    @abstractmethod
    async def create(self, item: T) -> str:
        """Create new item and return ID"""
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[T]:
        """Get item by ID"""
        pass
    
    @abstractmethod
    async def update(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """Update item by ID"""
        pass
    
    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """Delete item by ID"""
        pass
    
    @abstractmethod
    async def exists(self, item_id: str) -> bool:
        """Check if item exists"""
        pass
    
    @abstractmethod
    async def query(self, options: QueryOptions) -> QueryResult[T]:
        """Query items with filters and sorting"""
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[List[QueryFilter]] = None) -> int:
        """Count items matching filters"""
        pass
    
    @abstractmethod
    async def batch_create(self, items: List[T]) -> List[str]:
        """Create multiple items"""
        pass
    
    @abstractmethod
    async def batch_update(self, updates: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """Update multiple items"""
        pass
    
    @abstractmethod
    async def batch_delete(self, item_ids: List[str]) -> Dict[str, bool]:
        """Delete multiple items"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> StorageStats:
        """Get repository statistics"""
        pass
    
    @abstractmethod
    async def backup(self, backup_path: str) -> bool:
        """Backup repository data"""
        pass
    
    @abstractmethod
    async def restore(self, backup_path: str) -> bool:
        """Restore repository data"""
        pass


class ITaskRepository(IDataRepository[Dict[str, Any]]):
    """Interface for task-specific repository operations"""
    
    @abstractmethod
    async def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get tasks by status"""
        pass
    
    @abstractmethod
    async def get_tasks_by_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get tasks assigned to specific agent"""
        pass
    
    @abstractmethod
    async def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Get overdue tasks"""
        pass
    
    @abstractmethod
    async def get_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently created/updated tasks"""
        pass
    
    @abstractmethod
    async def update_task_status(self, task_id: str, status: str, 
                                metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update task status with optional metadata"""
        pass
    
    @abstractmethod
    async def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign task to agent"""
        pass
    
    @abstractmethod
    async def get_task_history(self, task_id: str) -> List[Dict[str, Any]]:
        """Get task status change history"""
        pass
    
    @abstractmethod
    async def search_tasks(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search tasks by content"""
        pass
    
    @abstractmethod
    async def get_task_dependencies(self, task_id: str) -> List[str]:
        """Get task dependencies"""
        pass
    
    @abstractmethod
    async def set_task_dependencies(self, task_id: str, dependencies: List[str]) -> bool:
        """Set task dependencies"""
        pass
    
    @abstractmethod
    async def get_tasks_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get tasks by priority level"""
        pass
    
    @abstractmethod
    async def get_task_metrics(self) -> Dict[str, Any]:
        """Get task-related metrics"""
        pass


class IFileStorageService(ABC):
    """Interface for file storage operations"""
    
    @abstractmethod
    async def upload_file(self, file_path: str, content: bytes, 
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Upload file and return file ID"""
        pass
    
    @abstractmethod
    async def download_file(self, file_id: str) -> Optional[bytes]:
        """Download file content"""
        pass
    
    @abstractmethod
    async def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file metadata"""
        pass
    
    @abstractmethod
    async def update_file_metadata(self, file_id: str, metadata: Dict[str, Any]) -> bool:
        """Update file metadata"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_id: str) -> bool:
        """Delete file"""
        pass
    
    @abstractmethod
    async def file_exists(self, file_id: str) -> bool:
        """Check if file exists"""
        pass
    
    @abstractmethod
    async def list_files(self, prefix: Optional[str] = None, 
                        limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List files with optional prefix filter"""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_id: str, expires_in: Optional[int] = None) -> Optional[str]:
        """Get temporary URL for file access"""
        pass
    
    @abstractmethod
    async def copy_file(self, source_file_id: str, destination_path: str) -> str:
        """Copy file to new location"""
        pass
    
    @abstractmethod
    async def move_file(self, file_id: str, new_path: str) -> bool:
        """Move file to new location"""
        pass
    
    @abstractmethod
    async def get_file_versions(self, file_id: str) -> List[Dict[str, Any]]:
        """Get file version history"""
        pass
    
    @abstractmethod
    async def restore_file_version(self, file_id: str, version_id: str) -> bool:
        """Restore specific file version"""
        pass
    
    @abstractmethod
    async def get_storage_usage(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        pass
    
    @abstractmethod
    async def cleanup_orphaned_files(self) -> int:
        """Clean up orphaned files and return count"""
        pass


class ITransactionalRepository(ABC):
    """Interface for transactional repository operations"""
    
    @abstractmethod
    async def begin_transaction(self) -> str:
        """Begin new transaction and return transaction ID"""
        pass
    
    @abstractmethod
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Commit transaction"""
        pass
    
    @abstractmethod
    async def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback transaction"""
        pass
    
    @abstractmethod
    async def execute_in_transaction(self, transaction_id: str, 
                                   operations: List[Dict[str, Any]]) -> List[Any]:
        """Execute multiple operations in transaction"""
        pass


class IEventStore(ABC):
    """Interface for event sourcing storage"""
    
    @abstractmethod
    async def append_event(self, stream_id: str, event: Dict[str, Any], 
                          expected_version: Optional[int] = None) -> int:
        """Append event to stream"""
        pass
    
    @abstractmethod
    async def get_events(self, stream_id: str, from_version: int = 0, 
                        to_version: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get events from stream"""
        pass
    
    @abstractmethod
    async def get_stream_version(self, stream_id: str) -> int:
        """Get current stream version"""
        pass
    
    @abstractmethod
    async def stream_exists(self, stream_id: str) -> bool:
        """Check if stream exists"""
        pass
    
    @abstractmethod
    async def delete_stream(self, stream_id: str) -> bool:
        """Delete event stream"""
        pass
    
    @abstractmethod
    async def get_all_streams(self) -> List[str]:
        """Get all stream IDs"""
        pass
    
    @abstractmethod
    async def create_snapshot(self, stream_id: str, snapshot_data: Dict[str, Any], 
                             version: int) -> bool:
        """Create stream snapshot"""
        pass
    
    @abstractmethod
    async def get_latest_snapshot(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get latest snapshot for stream"""
        pass


class ISearchEngine(ABC):
    """Interface for search functionality"""
    
    @abstractmethod
    async def index_document(self, doc_id: str, content: str, 
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Index document for search"""
        pass
    
    @abstractmethod
    async def search(self, query: str, filters: Optional[Dict[str, Any]] = None,
                    limit: int = 10, offset: int = 0) -> QueryResult[Dict[str, Any]]:
        """Search indexed documents"""
        pass
    
    @abstractmethod
    async def suggest(self, partial_query: str, limit: int = 5) -> List[str]:
        """Get search suggestions"""
        pass
    
    @abstractmethod
    async def delete_document(self, doc_id: str) -> bool:
        """Remove document from search index"""
        pass
    
    @abstractmethod
    async def update_document(self, doc_id: str, content: str, 
                            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update indexed document"""
        pass
    
    @abstractmethod
    async def rebuild_index(self) -> bool:
        """Rebuild search index"""
        pass
    
    @abstractmethod
    async def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        pass


class IDataMigration(ABC):
    """Interface for data migration operations"""
    
    @abstractmethod
    async def create_migration(self, migration_id: str, up_script: str, 
                              down_script: str) -> bool:
        """Create new migration"""
        pass
    
    @abstractmethod
    async def run_migration(self, migration_id: str) -> bool:
        """Run migration"""
        pass
    
    @abstractmethod
    async def rollback_migration(self, migration_id: str) -> bool:
        """Rollback migration"""
        pass
    
    @abstractmethod
    async def get_migration_status(self) -> List[Dict[str, Any]]:
        """Get status of all migrations"""
        pass
    
    @abstractmethod
    async def validate_migration(self, migration_id: str) -> Dict[str, Any]:
        """Validate migration before running"""
        pass


class IDataValidator(ABC):
    """Interface for data validation"""
    
    @abstractmethod
    async def validate_item(self, item: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate item against schema"""
        pass
    
    @abstractmethod
    async def validate_batch(self, items: List[Dict[str, Any]], 
                           schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate multiple items"""
        pass
    
    @abstractmethod
    async def register_schema(self, schema_id: str, schema: Dict[str, Any]) -> bool:
        """Register validation schema"""
        pass
    
    @abstractmethod
    async def get_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """Get validation schema"""
        pass
    
    @abstractmethod
    async def validate_repository_integrity(self, repository_type: str) -> Dict[str, Any]:
        """Validate repository data integrity"""
        pass