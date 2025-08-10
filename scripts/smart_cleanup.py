#!/usr/bin/env python3
"""
Smart Cleanup Script
Intelligent cleanup that only runs when actually needed to minimize overhead
"""

import shutil
import time
from pathlib import Path
from typing import Dict, List, Tuple


class SmartCleanup:
    """Intelligent cleanup that only runs when needed."""
    
    def __init__(self, root_path: Path = None):
        self.root_path = root_path or Path.cwd()
        self.cache_threshold_mb = 50  # Clean caches > 50MB
        self.file_age_threshold = 3600  # Clean files > 1 hour old
        
        # Colors for output
        self.colors = {
            'GREEN': '\033[0;32m', 
            'YELLOW': '\033[1;33m',
            'BLUE': '\033[0;34m',
            'NC': '\033[0m'
        }
    
    def print_colored(self, message: str, color: str = 'NC') -> None:
        """Print colored message."""
        print(f"{self.colors.get(color, '')}{message}{self.colors['NC']}")
    
    def get_dir_size_mb(self, path: Path) -> float:
        """Get directory size in MB."""
        if not path.exists() or not path.is_dir():
            return 0.0
            
        total_size = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
        except (OSError, PermissionError):
            pass
        
        return total_size / (1024 * 1024)
    
    def should_clean_cache(self, cache_path: Path) -> Tuple[bool, str]:
        """Determine if cache should be cleaned."""
        if not cache_path.exists():
            return False, "Cache doesn't exist"
            
        size_mb = self.get_dir_size_mb(cache_path)
        if size_mb > self.cache_threshold_mb:
            return True, f"Large cache: {size_mb:.1f}MB"
            
        # Check age of cache
        try:
            age_seconds = time.time() - cache_path.stat().st_mtime
            if age_seconds > self.file_age_threshold:
                return True, f"Old cache: {age_seconds/3600:.1f}h"
        except OSError:
            pass
            
        return False, f"Small/recent cache: {size_mb:.1f}MB"
    
    def should_clean_files(self, pattern: str) -> Tuple[bool, List[Path], str]:
        """Check if files matching pattern should be cleaned."""
        import glob
        matches = [Path(p) for p in glob.glob(str(self.root_path / pattern))]
        
        if not matches:
            return False, [], "No files found"
            
        # Check if any files are old enough
        old_files = []
        for path in matches:
            try:
                age_seconds = time.time() - path.stat().st_mtime
                if age_seconds > self.file_age_threshold:
                    old_files.append(path)
            except OSError:
                continue
        
        if old_files:
            return True, old_files, f"Found {len(old_files)} old files"
        else:
            return False, [], f"All {len(matches)} files are recent"
    
    def clean_smart_caches(self) -> int:
        """Clean caches intelligently."""
        caches_cleaned = 0
        cache_dirs = [
            '.ruff_cache',
            '.mypy_cache', 
            '.pytest_cache'
        ]
        
        self.print_colored("🧠 Smart cache cleanup...", 'BLUE')
        
        for cache_name in cache_dirs:
            cache_path = self.root_path / cache_name
            should_clean, reason = self.should_clean_cache(cache_path)
            
            if should_clean:
                try:
                    shutil.rmtree(cache_path)
                    self.print_colored(f"  ✅ Cleaned {cache_name}: {reason}", 'GREEN')
                    caches_cleaned += 1
                except Exception as e:
                    self.print_colored(f"  ❌ Failed to clean {cache_name}: {e}", 'YELLOW')
            else:
                self.print_colored(f"  ⏭️  Skipped {cache_name}: {reason}", 'BLUE')
        
        return caches_cleaned
    
    def clean_smart_files(self) -> int:
        """Clean files intelligently."""
        files_cleaned = 0
        file_patterns = [
            '.coverage*',
            '*.pyc',
            'bandit-report.json',
            '*_ruff_report.json'
        ]
        
        self.print_colored("🧠 Smart file cleanup...", 'BLUE')
        
        for pattern in file_patterns:
            should_clean, files, reason = self.should_clean_files(pattern)
            
            if should_clean:
                for file_path in files:
                    try:
                        file_path.unlink()
                        files_cleaned += 1
                    except Exception:
                        continue
                self.print_colored(f"  ✅ Cleaned {pattern}: {reason}", 'GREEN')
            else:
                self.print_colored(f"  ⏭️  Skipped {pattern}: {reason}", 'BLUE')
        
        return files_cleaned
    
    def clean_python_artifacts(self) -> int:
        """Clean Python bytecode files."""
        files_cleaned = 0
        
        # Always clean __pycache__ as it accumulates quickly
        pycache_dirs = list(self.root_path.rglob('__pycache__'))
        if pycache_dirs:
            self.print_colored("🐍 Cleaning Python artifacts...", 'BLUE')
            for pycache_dir in pycache_dirs:
                try:
                    shutil.rmtree(pycache_dir)
                    files_cleaned += 1
                except Exception:
                    continue
            self.print_colored(f"  ✅ Cleaned {len(pycache_dirs)} __pycache__ directories", 'GREEN')
        
        return files_cleaned
    
    def smart_cleanup(self) -> Dict[str, int]:
        """Run smart cleanup and return stats."""
        start_time = time.time()
        
        self.print_colored("🧠 Starting smart cleanup (only cleaning what's needed)...", 'BLUE')
        
        stats = {
            'caches_cleaned': self.clean_smart_caches(),
            'files_cleaned': self.clean_smart_files(),
            'python_artifacts': self.clean_python_artifacts(),
            'duration': time.time() - start_time
        }
        
        total_cleaned = sum(stats.values()) - stats['duration']  # Exclude duration from total
        
        if total_cleaned > 0:
            self.print_colored(f"\n✅ Smart cleanup completed: {total_cleaned} items cleaned in {stats['duration']:.1f}s", 'GREEN')
        else:
            self.print_colored(f"\n✨ Nothing needed cleaning! System is optimized. ({stats['duration']:.1f}s)", 'BLUE')
        
        return stats


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart cleanup - only clean when needed")
    parser.add_argument("--force", action="store_true", 
                       help="Force cleanup regardless of thresholds")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be cleaned")
    
    args = parser.parse_args()
    
    cleanup = SmartCleanup()
    
    if args.force:
        # Override thresholds for force mode
        cleanup.cache_threshold_mb = 0
        cleanup.file_age_threshold = 0
        print("🚨 Force mode: cleaning everything regardless of size/age")
    
    if args.dry_run:
        print("🔍 Dry run mode: showing what would be cleaned")
        # Would implement dry run logic here
        return
    
    stats = cleanup.smart_cleanup()
    
    # Return appropriate exit code
    if stats['caches_cleaned'] + stats['files_cleaned'] + stats['python_artifacts'] > 0:
        exit(0)  # Success - cleaned something
    else:
        exit(0)  # Success - nothing needed cleaning


if __name__ == "__main__":
    main()