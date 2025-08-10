#!/usr/bin/env python3
"""
Architecture Cleanup Script (Extended HITL Storage Cleaner)

This script implements comprehensive retention policies for all AI system artifacts
to prevent unlimited accumulation and address architecture bloat issues.

Features:
- Configurable retention periods for all artifact types
- Safe cleanup with backup option
- Preserves important audit logs
- Statistics reporting
- Extended support for outputs/, logs/, and build/ directories
- 4-worker parallel processing support
"""

import json
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import logging
import shutil
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Optional, Dict, Any
import re
import threading

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class ArchitectureStorageCleaner:
    """Extended cleaner for all AI system artifacts with configurable retention policies."""
    
    def __init__(self, root_dir: str = ".", dry_run: bool = False, extended_mode: bool = False, 
                 create_backup: bool = True, verify_git_clean: bool = True):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.extended_mode = extended_mode
        self.create_backup = create_backup
        self.verify_git_clean = verify_git_clean
        self.removed_count = 0
        self.freed_space = 0
        self.max_workers = 4  # Respect system constraint
        self.backup_created = False
        self.errors = []
        self.thread_lock = threading.Lock()  # For thread-safe operations
        
        # Extended retention policies (in days)
        self.retention_policies = {
            # Original HITL policies
            'checkpoint_files': 30,  # Keep checkpoint files for 30 days
            'audit_logs': 90,        # Keep audit logs for 90 days
            'evaluation_files': 7,   # Keep evaluation files for 7 days
            'rejected_files': 3,     # Keep rejected checkpoints for 3 days
            
            # Extended policies for architecture cleanup
            'perf_outputs': 3,       # Performance test outputs: 3 days
            'be_outputs': 7,         # Backend outputs: 7 days
            'fe_outputs': 7,         # Frontend outputs: 7 days
            'ux_outputs': 7,         # UX outputs: 7 days
            'tl_outputs': 14,        # Tech lead outputs: 14 days
            'pm_outputs': 14,        # Product manager outputs: 14 days
            'qa_outputs': 7,         # QA outputs: 7 days
            'concurrent_outputs': 1, # Concurrent test outputs: 1 day
            'test_outputs': 1,       # Test outputs: 1 day
            'logs': 3,              # All logs: 3 days
            'hot_storage': 1,       # Hot storage: 1 day
            'warm_storage': 7,      # Warm storage: 7 days
            'briefings': 30,        # Briefings: 30 days
        }
    
    def classify_file(self, file_path: Path) -> str:
        """Classify a file based on its name and location."""
        # Get the relative path from root to understand context
        try:
            rel_path = file_path.relative_to(self.root_dir)
            path_parts = rel_path.parts
        except ValueError:
            # File is outside root directory, use absolute path
            path_parts = file_path.parts
        
        # Original HITL classifications
        if file_path.name == 'audit.jsonl':
            return 'audit_logs'
        elif 'rejected' in file_path.name or 'failed' in file_path.name:
            return 'rejected_files'
        elif 'evaluation' in file_path.name:
            return 'evaluation_files'
        
        # Extended classifications for architecture cleanup
        if 'outputs' in path_parts:
            parent_name = path_parts[-1] if file_path.is_file() else path_parts[-2]
            if re.match(r'PERF-\d+', parent_name):
                return 'perf_outputs'
            elif re.match(r'BE-\d+', parent_name):
                return 'be_outputs'
            elif re.match(r'FE-\d+', parent_name):
                return 'fe_outputs'
            elif re.match(r'UX-\d+', parent_name):
                return 'ux_outputs'
            elif re.match(r'TL-\d+', parent_name):
                return 'tl_outputs'
            elif re.match(r'PM-\d+', parent_name):
                return 'pm_outputs'
            elif re.match(r'QA-\d+', parent_name):
                return 'qa_outputs'
            elif re.match(r'CONCURRENT-\d+', parent_name):
                return 'concurrent_outputs'
            elif re.match(r'TEST-', parent_name):
                return 'test_outputs'
            elif 'briefings' in path_parts:
                return 'briefings'
        
        if 'logs' in path_parts:
            return 'logs'
        elif 'build/storage/hot' in str(file_path):
            return 'hot_storage'
        elif 'build/storage/warm' in str(file_path):
            return 'warm_storage'
        
        # Default to checkpoint files for backward compatibility
        return 'checkpoint_files'
    
    def discover_cleanup_targets(self) -> List[Tuple[Path, str]]:
        """Discover all files/directories that need cleanup analysis."""
        targets = []
        
        # Define directories to scan
        scan_dirs = ['build/storage/hitl']  # Original HITL directory
        
        if self.extended_mode:
            scan_dirs.extend([
                'outputs',
                'logs', 
                'build/storage/hot',
                'build/storage/warm',
                'build/storage/cold'
            ])
        
        for scan_dir in scan_dirs:
            scan_path = self.root_dir / scan_dir
            if not scan_path.exists():
                logger.debug(f"Directory not found: {scan_path}")
                continue
                
            logger.info(f"🔍 Scanning directory: {scan_path}")
            
            # Handle different directory structures
            if scan_dir == 'outputs':
                # Outputs contains subdirectories for each task
                for item in scan_path.iterdir():
                    if item.is_dir():
                        targets.append((item, 'directory'))
                    elif item.is_file():
                        targets.append((item, 'file'))
            else:
                # Regular file-based directories
                for pattern in ['*.json', '*.jsonl', '*.txt', '*.log', '*.dat']:
                    targets.extend([(f, 'file') for f in scan_path.glob(pattern)])
        
        return targets
    
    def clean_architecture_files(self):
        """Clean up architecture files based on retention policies."""
        logger.info(f"🧹 Starting architecture cleanup (extended_mode: {self.extended_mode})")
        
        # Discover all cleanup targets
        targets = self.discover_cleanup_targets()
        
        if not targets:
            logger.info("  No files found to clean")
            return
        
        logger.info(f"  Found {len(targets)} cleanup targets")
        
        # Classify files by type
        files_by_type = {}
        for file_path, target_type in targets:
            file_type = self.classify_file(file_path)
            if file_type not in files_by_type:
                files_by_type[file_type] = []
            files_by_type[file_type].append((file_path, target_type))
        
        # Process each file type with parallel workers
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for file_type, files in files_by_type.items():
                if file_type in self.retention_policies:
                    logger.info(f"  Queuing {len(files)} {file_type} items...")
                    future = executor.submit(self._clean_file_type_extended, files, file_type)
                    futures.append(future)
                else:
                    logger.warning(f"  No retention policy for {file_type}, skipping...")
            
            # Wait for all workers to complete
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"  Worker failed: {e}")
    
    def _clean_file_type_extended(self, items: list, file_type: str):
        """Clean files/directories of a specific type (extended version) with error handling."""
        retention_days = self.retention_policies[file_type]
        local_removed = 0
        local_freed = 0
        local_errors = []
        
        logger.info(f"    [Worker] Processing {len(items)} {file_type} items (retention: {retention_days} days)")
        
        for file_path, target_type in items:
            try:
                if self.is_item_expired(file_path, file_type, target_type):
                    size = self.get_item_size(file_path, target_type)
                    
                    if not self.dry_run:
                        # Create backup before deletion if it's a critical file
                        if self._is_critical_file(file_path, file_type):
                            self._create_file_backup(file_path)
                        
                        if target_type == 'directory':
                            shutil.rmtree(file_path)
                            logger.info(f"    [Worker] Removed directory: {file_path.name} ({size / 1024 / 1024:.2f} MB)")
                        else:
                            file_path.unlink()
                            logger.info(f"    [Worker] Removed file: {file_path.name} ({size} bytes)")
                    else:
                        if target_type == 'directory':
                            logger.info(f"    [Worker] Would remove directory: {file_path.name} ({size / 1024 / 1024:.2f} MB)")
                        else:
                            logger.info(f"    [Worker] Would remove file: {file_path.name} ({size} bytes)")
                    
                    local_removed += 1
                    local_freed += size
                else:
                    age_days = self.get_item_age_days(file_path)
                    logger.debug(f"    [Worker] Keeping: {file_path.name} (age: {age_days} days, retention: {retention_days} days)")
                    
            except PermissionError as e:
                error_msg = f"Permission denied: {file_path} - {e}"
                local_errors.append(error_msg)
                logger.warning(f"    [Worker] {error_msg}")
            except OSError as e:
                error_msg = f"OS error processing {file_path}: {e}"
                local_errors.append(error_msg)
                logger.warning(f"    [Worker] {error_msg}")
            except Exception as e:
                error_msg = f"Unexpected error processing {file_path}: {e}"
                local_errors.append(error_msg)
                logger.error(f"    [Worker] {error_msg}")
        
        # Thread-safe update of counters
        with self.thread_lock:
            self.removed_count += local_removed
            self.freed_space += local_freed
            self.errors.extend(local_errors)
        
        logger.info(f"    [Worker] {file_type} complete: removed {local_removed} items, freed {local_freed / 1024 / 1024:.2f} MB, {len(local_errors)} errors")
    
    def is_item_expired(self, item_path: Path, file_type: str, target_type: str) -> bool:
        """Check if an item has exceeded its retention period."""
        retention_days = self.retention_policies.get(file_type, 30)
        age_days = self.get_item_age_days(item_path)
        return age_days > retention_days
    
    def get_item_age_days(self, item_path: Path) -> int:
        """Get the age of an item in days."""
        try:
            mtime = item_path.stat().st_mtime
            age = datetime.now() - datetime.fromtimestamp(mtime)
            return age.days
        except OSError:
            return 0
    
    def get_item_size(self, item_path: Path, target_type: str) -> int:
        """Get the size of an item in bytes."""
        try:
            if target_type == 'directory':
                total_size = 0
                for file_path in item_path.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                return total_size
            else:
                return item_path.stat().st_size
        except OSError:
            return 0
    
    def get_storage_stats(self):
        """Get comprehensive storage statistics before cleanup."""
        stats = {
            'total_files': 0,
            'total_directories': 0,
            'total_size': 0,
            'file_types': {}
        }
        
        # Discover all targets for statistics
        targets = self.discover_cleanup_targets()
        
        for file_path, target_type in targets:
            if target_type == 'directory':
                stats['total_directories'] += 1
            else:
                stats['total_files'] += 1
            
            size = self.get_item_size(file_path, target_type)
            stats['total_size'] += size
            
            file_type = self.classify_file(file_path)
            if file_type not in stats['file_types']:
                stats['file_types'][file_type] = {'count': 0, 'size': 0}
            
            stats['file_types'][file_type]['count'] += 1
            stats['file_types'][file_type]['size'] += size
        
        return stats
    
    def optimize_audit_log(self):
        """Optimize the audit log file by removing old entries."""
        audit_file = self.root_dir / "build" / "storage" / "hitl" / "audit.jsonl"
        
        if not audit_file.exists():
            return
        
        logger.info(f"🔧 Optimizing audit log: {audit_file}")
        
        # Read and filter audit entries
        cutoff_date = datetime.now() - timedelta(days=self.retention_policies['audit_logs'])
        new_entries = []
        removed_entries = 0
        
        try:
            with open(audit_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            entry_date = datetime.fromisoformat(entry.get('timestamp', ''))
                            
                            if entry_date > cutoff_date:
                                new_entries.append(line)
                            else:
                                removed_entries += 1
                        except (json.JSONDecodeError, ValueError) as e:
                            # Keep malformed entries to avoid data loss
                            new_entries.append(line)
                            logger.warning(f"    Keeping malformed entry: {e}")
            
            # Write back optimized log
            if not self.dry_run and removed_entries > 0:
                with open(audit_file, 'w') as f:
                    f.writelines(new_entries)
                
                new_size = audit_file.stat().st_size
                logger.info(f"    Removed {removed_entries} old audit entries")
                logger.info(f"    New audit log size: {new_size / 1024 / 1024:.1f} MB")
            elif removed_entries > 0:
                logger.info(f"    Would remove {removed_entries} old audit entries")
                
        except Exception as e:
            logger.error(f"    Error optimizing audit log: {e}")
    
    def verify_git_status(self) -> bool:
        """Verify git repository is in a clean state before cleanup."""
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
                logger.warning("Not in a git repository or git not available")
                return True  # Don't fail if not in git repo
                
            if result.stdout.strip():
                logger.error("❌ Git working directory is not clean")
                logger.error("🔍 Uncommitted changes found:")
                for line in result.stdout.strip().split('\n')[:5]:  # Show first 5 changes
                    logger.error(f"   {line}")
                logger.error("💡 Please commit or stash changes before running cleanup")
                return False
                
            logger.info("✅ Git working directory is clean")
            return True
            
        except Exception as e:
            logger.warning(f"Could not verify git status: {e}")
            return True  # Don't fail cleanup if git check fails
    
    def create_backup_branch(self) -> bool:
        """Create a backup git branch before making changes."""
        if not self.create_backup or self.dry_run:
            return True
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_branch = f"architecture-cleanup-backup-{timestamp}"
            
            # Create backup branch
            result = subprocess.run(
                ['git', 'checkout', '-b', backup_branch],
                cwd=self.root_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning(f"Could not create backup branch: {result.stderr}")
                return True  # Don't fail cleanup if backup branch creation fails
                
            logger.info(f"✅ Created backup branch: {backup_branch}")
            
            # Switch back to original branch
            subprocess.run(
                ['git', 'checkout', '-'],
                cwd=self.root_dir,
                capture_output=True
            )
            
            self.backup_created = True
            return True
            
        except Exception as e:
            logger.warning(f"Could not create backup branch: {e}")
            return True  # Don't fail cleanup if backup fails
    
    def run_cleanup(self) -> Dict[str, Any]:
        """Run the complete cleanup process with enhanced safety measures."""
        logger.info("🚀 Starting architecture storage cleanup...")
        if self.dry_run:
            logger.info("⚠️  DRY RUN MODE - No files will be deleted")
        
        # Safety checks
        if not self.verify_git_status():
            return {
                "success": False,
                "error": "Git working directory not clean",
                "files_processed": 0,
                "space_freed": 0
            }
        
        # Create backup branch if requested
        if not self.create_backup_branch():
            logger.warning("⚠️  Could not create backup branch, continuing...")
        
        # Get initial stats
        initial_stats = self.get_storage_stats()
        if initial_stats:
            logger.info(f"📊 Initial state: {initial_stats['total_files']} files, {initial_stats['total_directories']} dirs, {initial_stats['total_size'] / 1024 / 1024:.1f} MB")
        
        # Clean up files
        self.clean_architecture_files()
        
        # Optimize audit log
        self.optimize_audit_log()
        
        # Final stats
        freed_mb = self.freed_space / (1024 * 1024)
        success = len(self.errors) == 0
        
        logger.info("✅ Architecture cleanup complete!")
        logger.info(f"   Files processed: {self.removed_count}")
        logger.info(f"   Space freed: {freed_mb:.2f} MB")
        logger.info(f"   Errors encountered: {len(self.errors)}")
        
        if self.backup_created:
            logger.info("📦 Backup branch created for rollback if needed")
        
        if self.errors:
            logger.warning("⚠️  Some errors occurred during cleanup:")
            for error in self.errors[:3]:  # Show first 3 errors
                logger.warning(f"   {error}")
        
        if self.dry_run:
            logger.info("🔄 Run without --dry-run to actually remove files")
        
        return {
            "success": success,
            "files_processed": self.removed_count,
            "space_freed": freed_mb,
            "errors": self.errors,
            "backup_created": self.backup_created
        }


    def _is_critical_file(self, file_path: Path, file_type: str) -> bool:
        """Check if a file is critical and should be backed up before deletion."""
        critical_types = {'audit_logs', 'checkpoint_files'}
        return file_type in critical_types
    
    def _create_file_backup(self, file_path: Path) -> Optional[Path]:
        """Create a backup of a critical file before deletion."""
        try:
            backup_dir = self.root_dir / '.architecture_cleanup_backups'
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"{file_path.name}_{timestamp}"
            
            if file_path.is_dir():
                shutil.copytree(file_path, backup_path)
            else:
                shutil.copy2(file_path, backup_path)
            
            logger.debug(f"    Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.warning(f"    Failed to create backup for {file_path}: {e}")
            return None
    
    def validate_configuration(self) -> bool:
        """Validate cleanup configuration before execution."""
        errors = []
        
        # Check retention policies are reasonable
        for file_type, days in self.retention_policies.items():
            if not isinstance(days, int) or days < 0:
                errors.append(f"Invalid retention policy for {file_type}: {days}")
            elif days > 365:
                errors.append(f"Retention policy for {file_type} seems too long: {days} days")
        
        # Check root directory exists
        if not self.root_dir.exists():
            errors.append(f"Root directory does not exist: {self.root_dir}")
        
        # Check worker count is reasonable
        if self.max_workers > 8 or self.max_workers < 1:
            errors.append(f"Invalid worker count: {self.max_workers}")
        
        if errors:
            logger.error("❌ Configuration validation failed:")
            for error in errors:
                logger.error(f"   {error}")
            return False
        
        logger.info("✅ Configuration validation passed")
        return True


def main():
    """Main entry point with enhanced error handling."""
    parser = argparse.ArgumentParser(
        description="Clean up AI system artifacts based on retention policies (Extended HITL Cleaner)",
        epilog="Examples:\n"
               "  %(prog)s --dry-run --extended-mode --verbose  # Analyze what would be cleaned\n"
               "  %(prog)s --extended-mode                      # Clean with retention policies\n"
               "  %(prog)s --no-backup --no-git-check          # Skip safety measures",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--storage-dir",
        default=".",
        help="Path to root directory for cleanup (default: current directory)"
    )
    parser.add_argument(
        "--extended-mode",
        action="store_true",
        help="Enable extended cleanup mode for outputs/, logs/, and build/ directories"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing files"
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=30,
        help="Number of days to retain checkpoint files (default: 30)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup branch (faster but less safe)"
    )
    parser.add_argument(
        "--no-git-check",
        action="store_true",
        help="Skip git working directory clean check"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate configuration without running cleanup"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        cleaner = ArchitectureStorageCleaner(
            root_dir=args.storage_dir, 
            dry_run=args.dry_run, 
            extended_mode=args.extended_mode,
            create_backup=not args.no_backup,
            verify_git_clean=not args.no_git_check
        )
        
        # Validate configuration
        if not cleaner.validate_configuration():
            logger.error("❌ Configuration validation failed")
            return 1
        
        if args.validate_only:
            logger.info("✅ Configuration is valid")
            return 0
        
        # Update retention policy if specified
        if args.retention_days != 30:
            cleaner.retention_policies['checkpoint_files'] = args.retention_days
        
        # Run cleanup
        result = cleaner.run_cleanup()
        
        if result["success"]:
            logger.info("✅ Architecture cleanup completed successfully")
            return 0
        else:
            logger.error(f"❌ Architecture cleanup failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("⚠️  Cleanup interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1
    


if __name__ == "__main__":
    exit(main())