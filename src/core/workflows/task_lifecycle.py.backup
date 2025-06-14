#!/usr/bin/env python3
"""
Task Lifecycle Management for Scalable QA System

Handles task archival, cleanup, and optimization for high-volume environments:
- Automatic archival of completed tasks
- Compression and cold storage
- Cleanup policies
- Performance optimization
"""

import gzip
import json
import os
import shutil
import tarfile
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TaskLifecyclePolicy:
    """Define lifecycle policies for task management"""
    hot_storage_days: int = 7      # Keep in active outputs for 7 days
    warm_storage_days: int = 30    # Keep in compressed form for 30 days
    cold_storage_days: int = 365   # Archive for 1 year
    auto_cleanup_enabled: bool = True
    compression_level: int = 6     # gzip compression level
    max_hot_tasks: int = 1000      # Maximum tasks in hot storage


@dataclass
class TaskArchiveMetadata:
    """Metadata for archived tasks"""
    task_id: str
    archived_at: str
    original_size_bytes: int
    compressed_size_bytes: int
    archive_location: str
    retention_until: str
    qa_status: str
    completion_status: str


class TaskLifecycleManager:
    """
    Manages task lifecycle from creation to archival/deletion.

    Lifecycle stages:
    1. HOT: Active tasks in outputs/ directory
    2. WARM: Recently completed, compressed but accessible
    3. COLD: Long-term archive, compressed and stored separately
    4. PURGED: Deleted according to retention policy
    """

    def __init__(self,
                 outputs_dir: str = "outputs",
                 archive_dir: str = "archives",
                 policy: Optional[TaskLifecyclePolicy] = None):
        self.outputs_dir = Path(outputs_dir)
        self.archive_dir = Path(archive_dir)
        self.policy = policy or TaskLifecyclePolicy()

        # Create directory structure
        self.warm_dir = self.archive_dir / "warm"
        self.cold_dir = self.archive_dir / "cold"

        for dir_path in [self.archive_dir, self.warm_dir, self.cold_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.archive_dir / "archive_metadata.json"
        self.metadata = self._load_metadata()
        self.lock = threading.Lock()

    def _load_metadata(self) -> Dict[str, TaskArchiveMetadata]:
        """Load archive metadata from disk"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                return {k: TaskArchiveMetadata(**v) for k, v in data.items()}
            except Exception as e:
                print(f"⚠️ Failed to load archive metadata: {e}")

        return {}

    def _save_metadata(self):
        """Save archive metadata to disk"""
        try:
            data = {k: asdict(v) for k, v in self.metadata.items()}
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save archive metadata: {e}")

    def get_task_age_days(self, task_id: str) -> Optional[int]:
        """Get task age in days from last modification"""
        task_dir = self.outputs_dir / task_id
        if not task_dir.exists():
            return None

        # Get most recent modification time in the task directory
        latest_mtime = 0
        for item in task_dir.rglob("*"):
            if item.is_file():
                latest_mtime = max(latest_mtime, item.stat().st_mtime)

        if latest_mtime == 0:
            return None

        age = datetime.now().timestamp() - latest_mtime
        return int(age / 86400)  # Convert to days

    def should_archive_task(self, task_id: str) -> bool:
        """Check if task should be archived based on policy"""
        age_days = self.get_task_age_days(task_id)
        if age_days is None:
            return False

        # Check if task is completed
        status_file = self.outputs_dir / task_id / "status.json"
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    status = json.load(f)

                # Only archive completed tasks
                if status.get("overall_status") != "complete":
                    return False

                # Archive if older than hot storage policy
                return age_days >= self.policy.hot_storage_days
            except Exception:
                pass

        # Fallback: archive old tasks without status
        return age_days >= (self.policy.hot_storage_days * 2)

    def archive_task(self, task_id: str) -> Optional[TaskArchiveMetadata]:
        """Archive a single task to warm storage"""
        task_dir = self.outputs_dir / task_id
        if not task_dir.exists():
            print(f"⚠️ Task directory not found: {task_id}")
            return None

        with self.lock:
            # Skip if already archived
            if task_id in self.metadata:
                return self.metadata[task_id]

            # Calculate original size
            original_size = sum(
                f.stat().st_size for f in task_dir.rglob("*") if f.is_file())

            # Create compressed archive
            archive_name = f"{task_id}_{
                datetime.now().strftime('%Y%m%d')}.tar.gz"
            archive_path = self.warm_dir / archive_name

            try:
                with tarfile.open(archive_path, "w:gz", compresslevel=self.policy.compression_level) as tar:
                    tar.add(task_dir, arcname=task_id)

                compressed_size = archive_path.stat().st_size

                # Create metadata
                retention_until = datetime.now() + timedelta(days=self.policy.warm_storage_days)

                # Get QA status
                qa_status = "unknown"
                qa_file = task_dir / "qa_summary.md"
                if qa_file.exists():
                    try:
                        content = qa_file.read_text()
                        if "✅ PASSED" in content:
                            qa_status = "passed"
                        elif "❌ FAILED" in content:
                            qa_status = "failed"
                        else:
                            qa_status = "pending"
                    except Exception:
                        pass

                metadata = TaskArchiveMetadata(
                    task_id=task_id,
                    archived_at=datetime.now().isoformat(),
                    original_size_bytes=original_size,
                    compressed_size_bytes=compressed_size,
                    archive_location=str(archive_path),
                    retention_until=retention_until.isoformat(),
                    qa_status=qa_status,
                    completion_status="complete"
                )

                # Save metadata
                self.metadata[task_id] = metadata
                self._save_metadata()

                # Remove original directory
                shutil.rmtree(task_dir)

                print(f"📦 Archived {task_id}: {original_size:,} → {compressed_size:,} bytes "
                      f"({compressed_size / original_size * 100:.1f}% compression)")

                return metadata

            except Exception as e:
                print(f"❌ Failed to archive {task_id}: {e}")
                # Clean up partial archive
                if archive_path.exists():
                    archive_path.unlink()
                return None

    def restore_task(self, task_id: str) -> bool:
        """Restore archived task back to hot storage"""
        if task_id not in self.metadata:
            print(f"⚠️ No archive metadata found for {task_id}")
            return False

        metadata = self.metadata[task_id]
        archive_path = Path(metadata.archive_location)

        if not archive_path.exists():
            print(f"⚠️ Archive file not found: {archive_path}")
            return False

        try:
            # Extract to outputs directory
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(self.outputs_dir)

            print(f"📂 Restored {task_id} from archive")
            return True

        except Exception as e:
            print(f"❌ Failed to restore {task_id}: {e}")
            return False

    def run_lifecycle_maintenance(self) -> Dict[str, int]:
        """Run automatic lifecycle maintenance"""
        stats = {
            "tasks_archived": 0,
            "tasks_moved_to_cold": 0,
            "tasks_purged": 0,
            "bytes_freed": 0
        }

        if not self.policy.auto_cleanup_enabled:
            return stats

        print("🔄 Running task lifecycle maintenance...")

        # 1. Archive old hot tasks
        if self.outputs_dir.exists():
            for task_dir in self.outputs_dir.iterdir():
                if task_dir.is_dir() and self.should_archive_task(task_dir.name):
                    metadata = self.archive_task(task_dir.name)
                    if metadata:
                        stats["tasks_archived"] += 1
                        stats["bytes_freed"] += metadata.original_size_bytes

        # 2. Move warm tasks to cold storage
        warm_cutoff = datetime.now() - timedelta(days=self.policy.warm_storage_days)
        for task_id, metadata in list(self.metadata.items()):
            archived_at = datetime.fromisoformat(metadata.archived_at)
            if archived_at < warm_cutoff:
                if self._move_to_cold_storage(task_id, metadata):
                    stats["tasks_moved_to_cold"] += 1

        # 3. Purge old cold storage
        cold_cutoff = datetime.now() - timedelta(days=self.policy.cold_storage_days)
        for task_id, metadata in list(self.metadata.items()):
            retention_until = datetime.fromisoformat(metadata.retention_until)
            if retention_until < cold_cutoff:
                if self._purge_task(task_id, metadata):
                    stats["tasks_purged"] += 1

        # 4. Enforce hot storage limits
        hot_tasks = list(self.outputs_dir.iterdir()
                         ) if self.outputs_dir.exists() else []
        if len(hot_tasks) > self.policy.max_hot_tasks:
            # Archive oldest tasks
            oldest_tasks = sorted(hot_tasks, key=lambda d: d.stat().st_mtime)
            excess_count = len(hot_tasks) - self.policy.max_hot_tasks

            for task_dir in oldest_tasks[:excess_count]:
                metadata = self.archive_task(task_dir.name)
                if metadata:
                    stats["tasks_archived"] += 1
                    stats["bytes_freed"] += metadata.original_size_bytes

        return stats

    def _move_to_cold_storage(
            self,
            task_id: str,
            metadata: TaskArchiveMetadata) -> bool:
        """Move task from warm to cold storage"""
        try:
            warm_path = Path(metadata.archive_location)
            if not warm_path.exists():
                return False

            # Move to cold storage with additional compression
            cold_name = f"{task_id}_cold.tar.gz"
            cold_path = self.cold_dir / cold_name

            shutil.move(warm_path, cold_path)

            # Update metadata
            metadata.archive_location = str(cold_path)
            self._save_metadata()

            return True

        except Exception as e:
            print(f"❌ Failed to move {task_id} to cold storage: {e}")
            return False

    def _purge_task(self, task_id: str, metadata: TaskArchiveMetadata) -> bool:
        """Permanently delete task archive"""
        try:
            archive_path = Path(metadata.archive_location)
            if archive_path.exists():
                archive_path.unlink()

            # Remove from metadata
            del self.metadata[task_id]
            self._save_metadata()

            print(f"🗑️ Purged {task_id} (retention period expired)")
            return True

        except Exception as e:
            print(f"❌ Failed to purge {task_id}: {e}")
            return False

    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics"""
        stats = {
            "hot_storage": {"count": 0, "size_bytes": 0},
            "warm_storage": {"count": 0, "size_bytes": 0},
            "cold_storage": {"count": 0, "size_bytes": 0},
            "total_archived": len(self.metadata),
            "compression_ratio": 0.0
        }

        # Hot storage stats
        if self.outputs_dir.exists():
            hot_tasks = list(self.outputs_dir.iterdir())
            stats["hot_storage"]["count"] = len(hot_tasks)
            for task_dir in hot_tasks:
                if task_dir.is_dir():
                    size = sum(f.stat().st_size for f in task_dir.rglob(
                        "*") if f.is_file())
                    stats["hot_storage"]["size_bytes"] += size

        # Archive stats
        total_original = 0
        total_compressed = 0

        for metadata in self.metadata.values():
            total_original += metadata.original_size_bytes
            total_compressed += metadata.compressed_size_bytes

            archive_path = Path(metadata.archive_location)
            if archive_path.parent.name == "warm":
                stats["warm_storage"]["count"] += 1
                stats["warm_storage"]["size_bytes"] += metadata.compressed_size_bytes
            elif archive_path.parent.name == "cold":
                stats["cold_storage"]["count"] += 1
                stats["cold_storage"]["size_bytes"] += metadata.compressed_size_bytes

        if total_original > 0:
            stats["compression_ratio"] = total_compressed / total_original

        return stats

    def track_task_completion(self, task_id: str, agent_id: str) -> None:
        """Track task completion for lifecycle management"""
        print(f"📋 Tracking completion of task {task_id} by {agent_id}")

        # Update task completion tracking
        task_dir = self.outputs_dir / task_id
        if not task_dir.exists():
            return

        # Update or create completion tracking file
        tracking_file = task_dir / "lifecycle_tracking.json"
        tracking_data = {
            "task_id": task_id,
            "agent_id": agent_id,
            "completion_tracked_at": datetime.now().isoformat(),
            "ready_for_archival": False,
            "archival_check_count": 0
        }

        if tracking_file.exists():
            try:
                with open(tracking_file, 'r') as f:
                    existing_data = json.load(f)
                    tracking_data.update(existing_data)
            except Exception:
                pass

        # Mark as ready for archival check
        tracking_data["completion_tracked_at"] = datetime.now().isoformat()
        tracking_data["agent_id"] = agent_id
        tracking_data["ready_for_archival"] = True

        try:
            with open(tracking_file, 'w') as f:
                json.dump(tracking_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save tracking data for {task_id}: {e}")

    def cleanup_old_tasks(self, force: bool = False) -> Dict[str, int]:
        """
        Clean up old tasks based on lifecycle policies.

        This method is called automatically by the registration system when
        cleanup conditions are met, or can be called manually.

        Args:
            force: If True, ignore policy checks and run cleanup anyway

        Returns:
            Dict with cleanup statistics
        """
        if not force and not self.policy.auto_cleanup_enabled:
            return {
                "tasks_archived": 0,
                "tasks_moved_to_cold": 0,
                "tasks_purged": 0,
                "bytes_freed": 0
            }

        print("🧹 Running automatic task cleanup...")
        stats = self.run_lifecycle_maintenance()

        if stats["tasks_archived"] > 0 or stats["tasks_moved_to_cold"] > 0 or stats["tasks_purged"] > 0:
            print(f"✅ Cleanup completed: {stats['tasks_archived']} archived, "
                  f"{stats['tasks_moved_to_cold']} moved to cold, "
                  f"{stats['tasks_purged']} purged, "
                  f"{stats['bytes_freed']:,} bytes freed")
        else:
            print("✅ Cleanup completed: No tasks needed cleanup")

        return stats

    def should_trigger_cleanup(self) -> bool:
        """Check if cleanup should be triggered based on policy and current state"""
        if not self.policy.auto_cleanup_enabled:
            return False

        # Count current hot tasks
        hot_task_count = 0
        if self.outputs_dir.exists():
            hot_task_count = len(
                [d for d in self.outputs_dir.iterdir() if d.is_dir()])

        # Trigger cleanup if we're approaching the limit
        trigger_threshold = int(self.policy.max_hot_tasks * 0.8)  # 80% of max

        if hot_task_count >= trigger_threshold:
            print(
                f"🔄 Cleanup triggered: {hot_task_count} tasks >= {trigger_threshold} threshold")
            return True

        # Also check for tasks ready for archival
        ready_for_archival = 0
        if self.outputs_dir.exists():
            for task_dir in self.outputs_dir.iterdir():
                if not task_dir.is_dir():
                    continue

                tracking_file = task_dir / "lifecycle_tracking.json"
                if tracking_file.exists():
                    try:
                        with open(tracking_file, 'r') as f:
                            tracking_data = json.load(f)
                            if tracking_data.get("ready_for_archival", False):
                                ready_for_archival += 1
                    except Exception:
                        pass

        # Trigger if we have many tasks ready for archival
        if ready_for_archival >= 10:  # Arbitrary threshold
            print(
                f"🔄 Cleanup triggered: {ready_for_archival} tasks ready for archival")
            return True

        return False


def main():
    """Demo lifecycle management"""
    manager = TaskLifecycleManager()

    # Run maintenance
    stats = manager.run_lifecycle_maintenance()

    print(f"\n📊 Maintenance Results:")
    print(f"   Tasks archived: {stats['tasks_archived']}")
    print(f"   Tasks moved to cold: {stats['tasks_moved_to_cold']}")
    print(f"   Tasks purged: {stats['tasks_purged']}")
    print(f"   Bytes freed: {stats['bytes_freed']:,}")

    # Show storage stats
    storage_stats = manager.get_storage_statistics()
    print(f"\n💾 Storage Statistics:")
    print(f"   Hot storage: {storage_stats['hot_storage']['count']} tasks, "
          f"{storage_stats['hot_storage']['size_bytes']:,} bytes")
    print(f"   Warm storage: {storage_stats['warm_storage']['count']} tasks, "
          f"{storage_stats['warm_storage']['size_bytes']:,} bytes")
    print(f"   Cold storage: {storage_stats['cold_storage']['count']} tasks, "
          f"{storage_stats['cold_storage']['size_bytes']:,} bytes")
    print(f"   Compression ratio: {storage_stats['compression_ratio']:.1%}")


if __name__ == "__main__":
    main()
