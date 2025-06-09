"""
Memory Engine Storage System
Handles tiered storage (hot/warm/cold) and data lifecycle management
"""

import json
import logging
import os
import shutil
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from .config import StorageConfig
from .exceptions import StorageError

logger = logging.getLogger(__name__)


class TieredStorageManager:
    """
    Manages tiered storage with automatic migration between hot, warm, and cold storage.
    """
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.hot_storage_limit_mb = config.hot_storage_limit_mb
        self.warm_storage_limit_gb = config.warm_storage_limit_gb
        self.cold_storage_enabled = config.cold_storage_enabled
        self.migration_interval_hours = config.migration_interval_hours
        
        # Storage paths
        self.hot_path = Path("storage/hot")
        self.warm_path = Path("storage/warm")
        self.cold_path = Path("storage/cold")
        
        # Create storage directories
        for path in [self.hot_path, self.warm_path, self.cold_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Metadata tracking
        self.storage_metadata = self._load_metadata()
        self.lock = threading.RLock()
        
        # Start background migration
        self._start_migration_thread()
        
        logger.info("TieredStorageManager initialized")
    
    def store_data(self, key: str, data: bytes, metadata: Optional[Dict] = None) -> str:
        """
        Store data in appropriate tier based on size and access patterns.
        
        Returns:
            Storage tier where data was stored ('hot', 'warm', 'cold')
        """
        with self.lock:
            size_mb = len(data) / (1024 * 1024)
            current_time = datetime.now()
            
            # Determine initial storage tier
            if size_mb < 10 and self._get_hot_storage_usage() < self.hot_storage_limit_mb:
                tier = 'hot'
                storage_path = self.hot_path
            elif size_mb < 100 and self._get_warm_storage_usage() < self.warm_storage_limit_gb * 1024:
                tier = 'warm'
                storage_path = self.warm_path
            else:
                tier = 'cold'
                storage_path = self.cold_path
            
            # Store the data
            file_path = storage_path / f"{key}.dat"
            try:
                with open(file_path, 'wb') as f:
                    f.write(data)
                
                # Update metadata
                self.storage_metadata[key] = {
                    'tier': tier,
                    'size_bytes': len(data),
                    'created_at': current_time.isoformat(),
                    'last_accessed': current_time.isoformat(),
                    'access_count': 1,
                    'file_path': str(file_path),
                    'metadata': metadata or {}
                }
                
                self._save_metadata()
                
                logger.debug(f"Stored data {key} in {tier} tier ({size_mb:.2f} MB)")
                return tier
                
            except Exception as e:
                logger.error(f"Failed to store data {key}: {e}")
                raise StorageError(f"Storage failed: {e}")
    
    def retrieve_data(self, key: str) -> Optional[bytes]:
        """
        Retrieve data and update access patterns.
        """
        with self.lock:
            if key not in self.storage_metadata:
                return None
            
            meta = self.storage_metadata[key]
            file_path = Path(meta['file_path'])
            
            try:
                if not file_path.exists():
                    logger.warning(f"Data file missing for key {key}: {file_path}")
                    del self.storage_metadata[key]
                    self._save_metadata()
                    return None
                
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                # Update access metadata
                meta['last_accessed'] = datetime.now().isoformat()
                meta['access_count'] = meta.get('access_count', 0) + 1
                
                # Consider promoting frequently accessed data
                if meta['access_count'] > 10 and meta['tier'] != 'hot':
                    self._promote_data(key)
                
                self._save_metadata()
                
                logger.debug(f"Retrieved data {key} from {meta['tier']} tier")
                return data
                
            except Exception as e:
                logger.error(f"Failed to retrieve data {key}: {e}")
                raise StorageError(f"Retrieval failed: {e}")
    
    def delete_data(self, key: str) -> bool:
        """
        Delete data from storage.
        """
        with self.lock:
            if key not in self.storage_metadata:
                return False
            
            meta = self.storage_metadata[key]
            file_path = Path(meta['file_path'])
            
            try:
                if file_path.exists():
                    file_path.unlink()
                
                del self.storage_metadata[key]
                self._save_metadata()
                
                logger.debug(f"Deleted data {key} from {meta['tier']} tier")
                return True
                
            except Exception as e:
                logger.error(f"Failed to delete data {key}: {e}")
                return False
    
    def _promote_data(self, key: str) -> bool:
        """
        Promote data to a higher tier.
        """
        if key not in self.storage_metadata:
            return False
        
        meta = self.storage_metadata[key]
        current_tier = meta['tier']
        
        # Determine target tier
        if current_tier == 'cold':
            target_tier = 'warm'
            target_path = self.warm_path
        elif current_tier == 'warm':
            target_tier = 'hot'
            target_path = self.hot_path
        else:
            return False  # Already in hot tier
        
        # Check storage limits
        size_mb = meta['size_bytes'] / (1024 * 1024)
        if target_tier == 'hot' and self._get_hot_storage_usage() + size_mb > self.hot_storage_limit_mb:
            return False
        if target_tier == 'warm' and self._get_warm_storage_usage() + size_mb > self.warm_storage_limit_gb * 1024:
            return False
        
        # Move the file
        try:
            old_path = Path(meta['file_path'])
            new_path = target_path / f"{key}.dat"
            
            shutil.move(str(old_path), str(new_path))
            
            # Update metadata
            meta['tier'] = target_tier
            meta['file_path'] = str(new_path)
            
            logger.info(f"Promoted data {key} from {current_tier} to {target_tier}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to promote data {key}: {e}")
            return False
    
    def _demote_data(self, key: str) -> bool:
        """
        Demote data to a lower tier.
        """
        if key not in self.storage_metadata:
            return False
        
        meta = self.storage_metadata[key]
        current_tier = meta['tier']
        
        # Determine target tier
        if current_tier == 'hot':
            target_tier = 'warm'
            target_path = self.warm_path
        elif current_tier == 'warm':
            target_tier = 'cold'
            target_path = self.cold_path
        else:
            return False  # Already in cold tier
        
        # Move the file
        try:
            old_path = Path(meta['file_path'])
            new_path = target_path / f"{key}.dat"
            
            shutil.move(str(old_path), str(new_path))
            
            # Update metadata
            meta['tier'] = target_tier
            meta['file_path'] = str(new_path)
            
            logger.info(f"Demoted data {key} from {current_tier} to {target_tier}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to demote data {key}: {e}")
            return False
    
    def migrate(self) -> Dict[str, int]:
        """
        Perform migration between storage tiers based on access patterns.
        """
        with self.lock:
            migrations = {'promoted': 0, 'demoted': 0}
            current_time = datetime.now()
            
            # Check for data to demote (old, rarely accessed)
            for key, meta in list(self.storage_metadata.items()):
                last_accessed = datetime.fromisoformat(meta['last_accessed'])
                age_days = (current_time - last_accessed).days
                access_count = meta.get('access_count', 1)
                
                # Demote old, rarely accessed data
                if age_days > 30 and access_count < 5 and meta['tier'] == 'hot':
                    if self._demote_data(key):
                        migrations['demoted'] += 1
                elif age_days > 90 and access_count < 10 and meta['tier'] == 'warm':
                    if self._demote_data(key):
                        migrations['demoted'] += 1
            
            # Check storage usage and demote if over limits
            hot_usage = self._get_hot_storage_usage()
            if hot_usage > self.hot_storage_limit_mb:
                # Demote least recently accessed hot data
                hot_data = [(k, v) for k, v in self.storage_metadata.items() if v['tier'] == 'hot']
                hot_data.sort(key=lambda x: x[1]['last_accessed'])
                
                for key, meta in hot_data:
                    if self._demote_data(key):
                        migrations['demoted'] += 1
                        if self._get_hot_storage_usage() <= self.hot_storage_limit_mb:
                            break
            
            self._save_metadata()
            
            if migrations['promoted'] > 0 or migrations['demoted'] > 0:
                logger.info(f"Migration completed: {migrations}")
            
            return migrations
    
    def _get_hot_storage_usage(self) -> float:
        """Get hot storage usage in MB."""
        try:
            total_size = sum(
                meta['size_bytes'] for meta in self.storage_metadata.values()
                if meta['tier'] == 'hot'
            )
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0
    
    def _get_warm_storage_usage(self) -> float:
        """Get warm storage usage in MB."""
        try:
            total_size = sum(
                meta['size_bytes'] for meta in self.storage_metadata.values()
                if meta['tier'] == 'warm'
            )
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0
    
    def _load_metadata(self) -> Dict[str, Dict]:
        """Load storage metadata."""
        metadata_file = "storage/storage_metadata.json"
        
        try:
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load storage metadata: {e}")
        
        return {}
    
    def _save_metadata(self):
        """Save storage metadata."""
        metadata_file = "storage/storage_metadata.json"
        
        try:
            os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.storage_metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save storage metadata: {e}")
    
    def _start_migration_thread(self):
        """Start background migration thread."""
        def migration_worker():
            while True:
                try:
                    time.sleep(self.migration_interval_hours * 3600)
                    self.migrate()
                except Exception as e:
                    logger.error(f"Migration thread error: {e}")
        
        migration_thread = threading.Thread(target=migration_worker, daemon=True)
        migration_thread.start()
        logger.info("Storage migration thread started")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        with self.lock:
            stats = {
                'total_items': len(self.storage_metadata),
                'hot_items': sum(1 for m in self.storage_metadata.values() if m['tier'] == 'hot'),
                'warm_items': sum(1 for m in self.storage_metadata.values() if m['tier'] == 'warm'),
                'cold_items': sum(1 for m in self.storage_metadata.values() if m['tier'] == 'cold'),
                'hot_usage_mb': self._get_hot_storage_usage(),
                'warm_usage_mb': self._get_warm_storage_usage(),
                'total_size_mb': sum(m['size_bytes'] for m in self.storage_metadata.values()) / (1024 * 1024)
            }
            
            return stats


class PartitionManager:
    """
    Manages data partitioning for performance and scalability.
    """
    
    def __init__(self, storage_manager: TieredStorageManager):
        self.storage_manager = storage_manager
        self.partitions: Dict[str, List[str]] = {}
        self.lock = threading.RLock()
        
        logger.info("PartitionManager initialized")
    
    def get_partition_key(self, data_key: str) -> str:
        """
        Determine partition key for data.
        """
        # Simple hash-based partitioning
        import hashlib
        hash_value = hashlib.md5(data_key.encode()).hexdigest()
        partition_id = int(hash_value[:2], 16) % 16  # 16 partitions
        return f"partition_{partition_id:02d}"
    
    def add_to_partition(self, partition_key: str, data_key: str):
        """
        Add data key to partition.
        """
        with self.lock:
            if partition_key not in self.partitions:
                self.partitions[partition_key] = []
            
            if data_key not in self.partitions[partition_key]:
                self.partitions[partition_key].append(data_key)
    
    def remove_from_partition(self, partition_key: str, data_key: str):
        """
        Remove data key from partition.
        """
        with self.lock:
            if partition_key in self.partitions:
                if data_key in self.partitions[partition_key]:
                    self.partitions[partition_key].remove(data_key)
    
    def get_partition_data(self, partition_key: str) -> List[str]:
        """
        Get all data keys in a partition.
        """
        with self.lock:
            return self.partitions.get(partition_key, []).copy()
    
    def get_partition_stats(self) -> Dict[str, Any]:
        """
        Get partition statistics.
        """
        with self.lock:
            stats = {}
            for partition_key, data_keys in self.partitions.items():
                stats[partition_key] = len(data_keys)
            
            return stats