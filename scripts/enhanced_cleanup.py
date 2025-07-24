#!/usr/bin/env python3
"""
Enhanced Cleanup Script
Comprehensive cleanup system to prevent file accumulation
"""

import shutil
import subprocess
import time
from pathlib import Path
from typing import List


class EnhancedCleanup:
    """Comprehensive cleanup system."""
    
    def __init__(self, root_path: Path = None):
        self.root_path = root_path or Path.cwd()
        self.total_cleaned = 0
        self.total_size_cleaned = 0
        
        # Colors for output
        self.colors = {
            'RED': '\033[0;31m',
            'GREEN': '\033[0;32m', 
            'YELLOW': '\033[1;33m',
            'BLUE': '\033[0;34m',
            'NC': '\033[0m'  # No Color
        }
    
    def print_colored(self, message: str, color: str = 'NC') -> None:
        """Print colored message."""
        print(f"{self.colors.get(color, '')}{message}{self.colors['NC']}")
    
    def get_size(self, path: Path) -> int:
        """Get size of file or directory in bytes."""
        if not path.exists():
            return 0
            
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            total = 0
            try:
                for item in path.rglob('*'):
                    if item.is_file():
                        total += item.stat().st_size
            except (OSError, PermissionError):
                pass
            return total
        return 0
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
    
    def safe_remove(self, path: Path, description: str = "") -> bool:
        """Safely remove file or directory."""
        if not path.exists():
            return True
            
        size = self.get_size(path)
        
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            
            self.total_cleaned += 1
            self.total_size_cleaned += size
            
            size_str = self.format_size(size) if size > 0 else ""
            desc = f" ({description})" if description else ""
            self.print_colored(f"  ✅ Removed: {path.name}{desc} {size_str}", 'GREEN')
            return True
            
        except Exception as e:
            self.print_colored(f"  ❌ Failed to remove {path.name}: {e}", 'RED')
            return False
    
    def find_and_remove(self, patterns: List[str], description: str = "") -> None:
        """Find and remove files matching patterns."""
        self.print_colored(f"\n🔍 {description}...", 'BLUE')
        
        for pattern in patterns:
            if '*' in pattern or '?' in pattern:
                # Use glob for wildcards
                import glob
                matches = glob.glob(str(self.root_path / pattern), recursive=True)
                for match in matches:
                    self.safe_remove(Path(match), description)
            else:
                # Direct path
                path = self.root_path / pattern
                if path.exists():
                    self.safe_remove(path, description)
    
    def clean_python_artifacts(self) -> None:
        """Clean Python-related artifacts."""
        patterns = [
            "__pycache__",
            "*/__pycache__",
            "**/__pycache__",
            "*.pyc",
            "**/*.pyc",
            "*.pyo",
            "**/*.pyo",
            ".coverage*",
            "coverage.xml"
        ]
        self.find_and_remove(patterns, "Cleaning Python artifacts")
    
    def clean_tool_caches(self) -> None:
        """Clean tool caches."""
        patterns = [
            ".ruff_cache",
            ".mypy_cache", 
            ".pytest_cache",
            ".tox",
            ".nox"
        ]
        self.find_and_remove(patterns, "Cleaning tool caches")
    
    def clean_coverage_reports(self) -> None:
        """Clean coverage reports."""
        patterns = [
            "htmlcov",
            "coverage.xml",
            ".coverage",
            ".coverage.*"
        ]
        self.find_and_remove(patterns, "Cleaning coverage reports")
    
    def clean_security_reports(self) -> None:
        """Clean security and validation reports."""
        patterns = [
            "bandit-report.json",
            "*_ruff_report.json",
            "core_ruff_report.json",
            "infrastructure_ruff_report.json"
        ]
        self.find_and_remove(patterns, "Cleaning security/validation reports")
    
    def clean_log_files(self) -> None:
        """Clean log files."""
        patterns = [
            "*.log",
            "**/*.log",
            "logs/*.log",
            "src/**/logs/*.log"
        ]
        # Only clean log files older than 1 day
        import glob
        for pattern in patterns:
            matches = glob.glob(str(self.root_path / pattern), recursive=True)
            for match in matches:
                path = Path(match)
                if path.exists() and path.is_file():
                    age = time.time() - path.stat().st_mtime
                    if age > 24 * 3600:  # 1 day
                        self.safe_remove(path, "Old log file")
    
    def clean_temporary_files(self) -> None:
        """Clean temporary files."""
        patterns = [
            "*.tmp",
            "*.temp", 
            "*.bak",
            "**/*.tmp",
            "**/*.temp",
            "**/*.bak"
        ]
        self.find_and_remove(patterns, "Cleaning temporary files")
    
    def clean_ide_artifacts(self) -> None:
        """Clean IDE artifacts."""
        patterns = [
            ".vscode/.browse.VC.db*",
            ".vscode/*.log",
            "*.swp",
            "*.swo",
            "*~"
        ]
        self.find_and_remove(patterns, "Cleaning IDE artifacts")
    
    def run_git_cleanup(self) -> None:
        """Run git cleanup commands if in a git repo."""
        if not (self.root_path / ".git").exists():
            return
            
        self.print_colored("\n🔧 Running git cleanup...", 'BLUE')
        
        git_commands = [
            ["git", "gc", "--prune=now"],
            ["git", "remote", "prune", "origin"]
        ]
        
        for cmd in git_commands:
            try:
                result = subprocess.run(
                    cmd, 
                    cwd=self.root_path, 
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    self.print_colored(f"  ✅ {' '.join(cmd)}", 'GREEN')
                else:
                    self.print_colored(f"  ⚠️  {' '.join(cmd)} completed with warnings", 'YELLOW')
            except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                self.print_colored(f"  ❌ Failed: {' '.join(cmd)} - {e}", 'RED')
    
    def analyze_large_files(self, size_threshold_mb: int = 10) -> None:
        """Analyze and report large files."""
        self.print_colored(f"\n📊 Analyzing files larger than {size_threshold_mb}MB...", 'BLUE')
        
        large_files = []
        threshold_bytes = size_threshold_mb * 1024 * 1024
        
        try:
            for path in self.root_path.rglob('*'):
                if path.is_file() and not any(part.startswith('.git') for part in path.parts):
                    try:
                        size = path.stat().st_size
                        if size > threshold_bytes:
                            large_files.append((path, size))
                    except OSError:
                        continue
        except Exception:
            pass
            
        if large_files:
            large_files.sort(key=lambda x: x[1], reverse=True)
            self.print_colored(f"Found {len(large_files)} large files:", 'YELLOW')
            for path, size in large_files[:10]:  # Show top 10
                rel_path = path.relative_to(self.root_path)
                self.print_colored(f"  📁 {rel_path} - {self.format_size(size)}", 'YELLOW')
        else:
            self.print_colored("  ✅ No large files found", 'GREEN')
    
    def full_cleanup(self, include_logs: bool = False, analyze_files: bool = True) -> None:
        """Run full cleanup process."""
        self.print_colored("🧹 Starting enhanced cleanup process...", 'BLUE')
        start_time = time.time()
        
        # Run all cleanup operations
        self.clean_python_artifacts()
        self.clean_tool_caches()
        self.clean_coverage_reports()
        self.clean_security_reports()
        self.clean_temporary_files()
        self.clean_ide_artifacts()
        
        if include_logs:
            self.clean_log_files()
        
        self.run_git_cleanup()
        
        if analyze_files:
            self.analyze_large_files()
        
        # Summary
        duration = time.time() - start_time
        self.print_colored("\n📋 Cleanup Summary:", 'BLUE')
        self.print_colored(f"  • Files/directories cleaned: {self.total_cleaned}", 'GREEN')
        self.print_colored(f"  • Total space freed: {self.format_size(self.total_size_cleaned)}", 'GREEN')
        self.print_colored(f"  • Duration: {duration:.1f}s", 'GREEN')
        
        if self.total_cleaned > 0:
            self.print_colored("✅ Cleanup completed successfully!", 'GREEN')
        else:
            self.print_colored("ℹ️  No files needed cleaning", 'BLUE')


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced cleanup for the AI system")
    parser.add_argument("--include-logs", action="store_true",
                       help="Include old log files in cleanup")
    parser.add_argument("--no-analysis", action="store_true", 
                       help="Skip large file analysis")
    parser.add_argument("--quick", action="store_true",
                       help="Quick cleanup (caches and Python artifacts only)")
    
    args = parser.parse_args()
    
    cleanup = EnhancedCleanup()
    
    if args.quick:
        cleanup.clean_python_artifacts()
        cleanup.clean_tool_caches()
        print(f"✅ Quick cleanup completed - {cleanup.total_cleaned} items cleaned")
    else:
        cleanup.full_cleanup(
            include_logs=args.include_logs,
            analyze_files=not args.no_analysis
        )


if __name__ == "__main__":
    main()