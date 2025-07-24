#!/usr/bin/env python3
"""
Cleanup script for generated files that shouldn't be in version control.

This script safely removes:
1. Test-generated HITL notification files
2. Coverage measurement files from parallel test runs
3. Temporary Python cache files
4. Empty log files
5. Test artifacts in build directories
"""

from pathlib import Path
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class GeneratedFileCleaner:
    """Cleaner for generated files that accumulate during development."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.removed_count = 0
        self.freed_space = 0
    
    def clean_coverage_files(self):
        """Remove coverage measurement files from parallel test runs."""
        logger.info("🧹 Cleaning coverage files...")
        
        patterns = [".coverage.*", "*.coverage", ".coverage"]
        for pattern in patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    if not self.dry_run:
                        file_path.unlink()
                        logger.info(f"  Removed: {file_path}")
                    else:
                        logger.info(f"  Would remove: {file_path}")
                    self.removed_count += 1
                    self.freed_space += size
    
    def clean_hitl_test_files(self):
        """Remove HITL test-generated files."""
        logger.info("🧹 Cleaning HITL test files...")
        
        # Notification files from tests
        notifications_dir = Path("build/dashboard/notifications")
        if notifications_dir.exists():
            for file_path in notifications_dir.glob("notif_hitl_BE-07_*.json"):
                size = file_path.stat().st_size
                if not self.dry_run:
                    file_path.unlink()
                    logger.info(f"  Removed: {file_path}")
                else:
                    logger.info(f"  Would remove: {file_path}")
                self.removed_count += 1
                self.freed_space += size
        
        # HITL storage files from tests
        hitl_storage_dir = Path("build/storage/hitl")
        if hitl_storage_dir.exists():
            for file_path in hitl_storage_dir.glob("hitl_BE-07_*.json"):
                size = file_path.stat().st_size
                if not self.dry_run:
                    file_path.unlink()
                    logger.info(f"  Removed: {file_path}")
                else:
                    logger.info(f"  Would remove: {file_path}")
                self.removed_count += 1
                self.freed_space += size
    
    def clean_python_cache(self):
        """Remove Python cache files and directories."""
        logger.info("🧹 Cleaning Python cache files...")
        
        # Remove __pycache__ directories
        for cache_dir in Path(".").rglob("__pycache__"):
            if cache_dir.is_dir():
                import shutil
                size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
                if not self.dry_run:
                    shutil.rmtree(cache_dir)
                    logger.info(f"  Removed directory: {cache_dir}")
                else:
                    logger.info(f"  Would remove directory: {cache_dir}")
                self.removed_count += 1
                self.freed_space += size
        
        # Remove .pyc files
        for pyc_file in Path(".").rglob("*.pyc"):
            if pyc_file.is_file():
                size = pyc_file.stat().st_size
                if not self.dry_run:
                    pyc_file.unlink()
                    logger.info(f"  Removed: {pyc_file}")
                else:
                    logger.info(f"  Would remove: {pyc_file}")
                self.removed_count += 1
                self.freed_space += size
    
    def clean_empty_logs(self):
        """Remove empty log files."""
        logger.info("🧹 Cleaning empty log files...")
        
        for log_file in Path(".").rglob("*.log"):
            if log_file.is_file() and log_file.stat().st_size == 0:
                if not self.dry_run:
                    log_file.unlink()
                    logger.info(f"  Removed empty log: {log_file}")
                else:
                    logger.info(f"  Would remove empty log: {log_file}")
                self.removed_count += 1
    
    def clean_test_artifacts(self):
        """Remove test artifacts that shouldn't be committed."""
        logger.info("🧹 Cleaning test artifacts...")
        
        # Patterns for test artifacts
        test_patterns = [
            "test_*.dat",
            "*.tmp",
            "*.temp",
            ".pytest_cache/**/*",
            "htmlcov/**/*",
        ]
        
        for pattern in test_patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    if not self.dry_run:
                        file_path.unlink()
                        logger.info(f"  Removed: {file_path}")
                    else:
                        logger.info(f"  Would remove: {file_path}")
                    self.removed_count += 1
                    self.freed_space += size
    
    def clean_large_files(self):
        """Clean up large files that shouldn't be in repository."""
        logger.info("🧹 Cleaning large files...")
        
        # Check for large coverage and validation files
        large_patterns = [
            "coverage.json",
            "bandit-report.json",
            ".validation_history/validation_history.jsonl",
        ]
        
        for pattern in large_patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    if size > 1024 * 1024:  # Files larger than 1MB
                        if not self.dry_run:
                            file_path.unlink()
                            logger.info(f"  Removed large file: {file_path} ({size / 1024 / 1024:.1f}MB)")
                        else:
                            logger.info(f"  Would remove large file: {file_path} ({size / 1024 / 1024:.1f}MB)")
                        self.removed_count += 1
                        self.freed_space += size

    def run_cleanup(self):
        """Run all cleanup operations."""
        logger.info("🚀 Starting generated file cleanup...")
        if self.dry_run:
            logger.info("⚠️  DRY RUN MODE - No files will be deleted")
        
        self.clean_coverage_files()
        self.clean_hitl_test_files()
        self.clean_python_cache()
        self.clean_empty_logs()
        self.clean_test_artifacts()
        self.clean_large_files()
        
        # Summary
        freed_mb = self.freed_space / (1024 * 1024)
        logger.info("✅ Cleanup complete!")
        logger.info(f"   Files processed: {self.removed_count}")
        logger.info(f"   Space freed: {freed_mb:.2f} MB")
        
        if self.dry_run:
            logger.info("🔄 Run without --dry-run to actually remove files")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clean up generated files that shouldn't be in version control"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be removed without actually removing files"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    cleaner = GeneratedFileCleaner(dry_run=args.dry_run)
    cleaner.run_cleanup()

if __name__ == "__main__":
    main()