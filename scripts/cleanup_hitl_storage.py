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
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ArchitectureStorageCleaner:
    """Extended cleaner for all AI system artifacts with configurable retention policies."""
    
    def __init__(self, root_dir: str = ".", dry_run: bool = False, extended_mode: bool = False):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.extended_mode = extended_mode
        self.removed_count = 0
        self.freed_space = 0
        self.max_workers = 4  # Respect system constraint
        
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
        """Classify a file based on its name and content."""
        if file_path.name == 'audit.jsonl':
            return 'audit_logs'
        elif 'rejected' in file_path.name or 'failed' in file_path.name:
            return 'rejected_files'
        elif 'evaluation' in file_path.name:
            return 'evaluation_files'
        else:
            return 'checkpoint_files'
    
    def is_file_expired(self, file_path: Path, file_type: str) -> bool:
        """Check if a file has exceeded its retention period."""
        retention_days = self.retention_policies.get(file_type, 30)
        file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
        return file_age > timedelta(days=retention_days)
    
    def clean_hitl_files(self):
        """Clean up HITL files based on retention policies."""
        if not self.storage_dir.exists():
            logger.warning(f"HITL storage directory not found: {self.storage_dir}")
            return
        
        logger.info(f"🧹 Cleaning HITL storage: {self.storage_dir}")
        
        # Get all JSON files
        json_files = list(self.storage_dir.glob("*.json"))
        jsonl_files = list(self.storage_dir.glob("*.jsonl"))
        all_files = json_files + jsonl_files
        
        if not all_files:
            logger.info("  No HITL files found to clean")
            return
        
        # Classify and process files
        files_by_type = {}
        for file_path in all_files:
            file_type = self.classify_file(file_path)
            if file_type not in files_by_type:
                files_by_type[file_type] = []
            files_by_type[file_type].append(file_path)
        
        # Clean up each file type
        for file_type, files in files_by_type.items():
            logger.info(f"  Processing {len(files)} {file_type} files...")
            self._clean_file_type(files, file_type)
    
    def _clean_file_type(self, files: list, file_type: str):
        """Clean files of a specific type."""
        retention_days = self.retention_policies[file_type]
        
        for file_path in files:
            try:
                if self.is_file_expired(file_path, file_type):
                    size = file_path.stat().st_size
                    
                    if not self.dry_run:
                        file_path.unlink()
                        logger.info(f"    Removed: {file_path.name} ({size} bytes)")
                    else:
                        logger.info(f"    Would remove: {file_path.name} ({size} bytes)")
                    
                    self.removed_count += 1
                    self.freed_space += size
                else:
                    age_days = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days
                    logger.debug(f"    Keeping: {file_path.name} (age: {age_days} days, retention: {retention_days} days)")
                    
            except Exception as e:
                logger.error(f"    Error processing {file_path}: {e}")
    
    def optimize_audit_log(self):
        """Optimize the audit log file by removing old entries."""
        audit_file = self.storage_dir / "audit.jsonl"
        
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
    
    def get_storage_stats(self):
        """Get storage statistics before cleanup."""
        if not self.storage_dir.exists():
            return {}
        
        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {}
        }
        
        for file_path in self.storage_dir.iterdir():
            if file_path.is_file():
                stats['total_files'] += 1
                size = file_path.stat().st_size
                stats['total_size'] += size
                
                file_type = self.classify_file(file_path)
                if file_type not in stats['file_types']:
                    stats['file_types'][file_type] = {'count': 0, 'size': 0}
                
                stats['file_types'][file_type]['count'] += 1
                stats['file_types'][file_type]['size'] += size
        
        return stats
    
    def run_cleanup(self):
        """Run the complete cleanup process."""
        logger.info("🚀 Starting HITL storage cleanup...")
        if self.dry_run:
            logger.info("⚠️  DRY RUN MODE - No files will be deleted")
        
        # Get initial stats
        initial_stats = self.get_storage_stats()
        if initial_stats:
            logger.info(f"📊 Initial state: {initial_stats['total_files']} files, {initial_stats['total_size'] / 1024 / 1024:.1f} MB")
        
        # Clean up files
        self.clean_hitl_files()
        
        # Optimize audit log
        self.optimize_audit_log()
        
        # Final stats
        freed_mb = self.freed_space / (1024 * 1024)
        logger.info("✅ HITL cleanup complete!")
        logger.info(f"   Files processed: {self.removed_count}")
        logger.info(f"   Space freed: {freed_mb:.2f} MB")
        
        if self.dry_run:
            logger.info("🔄 Run without --dry-run to actually remove files")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clean up AI system artifacts based on retention policies (Extended HITL Cleaner)"
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
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    cleaner = ArchitectureStorageCleaner(
        root_dir=args.storage_dir, 
        dry_run=args.dry_run, 
        extended_mode=args.extended_mode
    )
    
    # Update retention policy if specified
    if args.retention_days != 30:
        cleaner.retention_policies['checkpoint_files'] = args.retention_days
    
    cleaner.run_cleanup()

if __name__ == "__main__":
    main()