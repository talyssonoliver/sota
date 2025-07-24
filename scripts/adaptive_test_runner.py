#!/usr/bin/env python3
"""
Adaptive Test Runner
Intelligently selects and prioritizes tests based on code changes
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Set, Tuple


class AdaptiveTestRunner:
    """Smart test runner that prioritizes tests based on changes."""
    
    def __init__(self, root_path: Path = None):
        self.root_path = root_path or Path.cwd()
        self.src_path = self.root_path / "src"
        self.tests_path = self.root_path / "tests"
        
        # Colors for output
        self.colors = {
            'GREEN': '\033[0;32m', 
            'YELLOW': '\033[1;33m',
            'BLUE': '\033[0;34m',
            'RED': '\033[0;31m',
            'NC': '\033[0m'
        }
    
    def print_colored(self, message: str, color: str = 'NC') -> None:
        """Print colored message."""
        print(f"{self.colors.get(color, '')}{message}{self.colors['NC']}")
    
    def get_changed_files(self, since: str = "HEAD~1") -> Set[Path]:
        """Get files changed since a specific commit."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", since],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                changed_files = set()
                for line in result.stdout.strip().split('\n'):
                    if line:
                        file_path = Path(line)
                        if file_path.exists():
                            changed_files.add(file_path)
                return changed_files
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass
        
        return set()
    
    def get_unstaged_files(self) -> Set[Path]:
        """Get unstaged/modified files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                unstaged_files = set()
                for line in result.stdout.strip().split('\n'):
                    if line:
                        file_path = Path(line)
                        if file_path.exists():
                            unstaged_files.add(file_path)
                return unstaged_files
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass
        
        return set()
    
    def map_source_to_tests(self, source_file: Path) -> List[Path]:
        """Map a source file to its corresponding test files."""
        test_files = []
        
        # Direct mapping: src/core/agents/backend.py -> tests/unit/core/agents/test_backend.py
        if source_file.is_relative_to(self.src_path):
            rel_path = source_file.relative_to(self.src_path)
            
            # Try multiple test patterns
            test_patterns = [
                self.tests_path / "unit" / rel_path.parent / f"test_{rel_path.stem}.py",
                self.tests_path / "integration" / rel_path.parent / f"test_{rel_path.stem}.py",
                self.tests_path / "e2e" / rel_path.parent / f"test_{rel_path.stem}.py",
                self.tests_path / f"test_{rel_path.stem}.py",
            ]
            
            for test_pattern in test_patterns:
                if test_pattern.exists():
                    test_files.append(test_pattern)
        
        # Also check if the file itself is a test
        if source_file.is_relative_to(self.tests_path) and source_file.name.startswith('test_'):
            test_files.append(source_file)
        
        return test_files
    
    def get_priority_tests(self, changed_files: Set[Path]) -> Tuple[List[Path], List[Path]]:
        """Get high priority tests (for changed files) and remaining tests."""
        high_priority = set()
        
        for changed_file in changed_files:
            if changed_file.suffix == '.py':
                # Map to corresponding tests
                related_tests = self.map_source_to_tests(changed_file)
                high_priority.update(related_tests)
        
        # Get all test files
        all_tests = set()
        for test_pattern in ['test_*.py', '**/test_*.py']:
            all_tests.update(self.tests_path.rglob(test_pattern))
        
        # Split into priority and remaining
        high_priority_list = list(high_priority)
        remaining_tests = list(all_tests - high_priority)
        
        return high_priority_list, remaining_tests
    
    def run_tests_with_priority(self, high_priority: List[Path], remaining: List[Path], 
                               max_failures: int = 5, quick_mode: bool = False) -> bool:
        """Run tests with priority ordering."""
        start_time = time.time()
        
        if high_priority:
            self.print_colored(f"🎯 Running {len(high_priority)} priority tests (changed files)...", 'BLUE')
            
            priority_cmd = [
                sys.executable, "-m", "pytest",
                "-n", "auto" if not quick_mode else "2",
                "--dist", "loadscope",
                "--tb=short",
                f"--maxfail={max_failures}",
                "-x" if quick_mode else "",
                "--disable-warnings"
            ] + [str(test) for test in high_priority]
            
            # Remove empty strings
            priority_cmd = [arg for arg in priority_cmd if arg]
            
            try:
                result = subprocess.run(priority_cmd, cwd=self.root_path, timeout=300)
                
                if result.returncode != 0:
                    self.print_colored("❌ Priority tests failed! Stopping early for quick feedback.", 'RED')
                    return False
                else:
                    self.print_colored("✅ Priority tests passed!", 'GREEN')
            except subprocess.TimeoutExpired:
                self.print_colored("⏰ Priority tests timed out", 'YELLOW')
                return False
        
        if not quick_mode and remaining:
            self.print_colored(f"🧪 Running {len(remaining)} remaining tests...", 'BLUE')
            
            remaining_cmd = [
                sys.executable, "-m", "pytest",
                "-n", "auto",
                "--dist", "loadscope", 
                "--tb=line",
                f"--maxfail={max_failures * 2}",
                "--disable-warnings"
            ] + [str(test) for test in remaining[:50]]  # Limit to avoid too long command
            
            try:
                result = subprocess.run(remaining_cmd, cwd=self.root_path, timeout=600)
                if result.returncode != 0:
                    self.print_colored("⚠️ Some remaining tests failed", 'YELLOW')
                    return False
            except subprocess.TimeoutExpired:
                self.print_colored("⏰ Remaining tests timed out", 'YELLOW')
                return False
        
        duration = time.time() - start_time
        self.print_colored(f"✅ Adaptive testing completed in {duration:.1f}s", 'GREEN')
        return True
    
    def run_adaptive_tests(self, quick_mode: bool = False, since: str = "HEAD~1") -> bool:
        """Run tests adaptively based on changes."""
        self.print_colored("🧠 Starting adaptive test runner...", 'BLUE')
        
        # Get changed files
        changed_files = self.get_changed_files(since)
        unstaged_files = self.get_unstaged_files()
        all_changed = changed_files.union(unstaged_files)
        
        if not all_changed:
            self.print_colored("📝 No changes detected, running standard test suite...", 'BLUE')
            # Run standard quick tests
            cmd = [
                sys.executable, "-m", "pytest",
                "-n", "auto",
                "--dist", "loadscope",
                "--tb=line",
                "--maxfail=10",
                "-x" if quick_mode else "",
                "--disable-warnings",
                str(self.tests_path)
            ]
            cmd = [arg for arg in cmd if arg]
            
            try:
                result = subprocess.run(cmd, cwd=self.root_path, timeout=300)
                return result.returncode == 0
            except subprocess.TimeoutExpired:
                self.print_colored("⏰ Tests timed out", 'YELLOW')
                return False
        
        self.print_colored(f"📁 Found {len(all_changed)} changed files", 'BLUE')
        
        # Get priority tests
        high_priority, remaining = self.get_priority_tests(all_changed)
        
        if high_priority:
            self.print_colored(f"🎯 Identified {len(high_priority)} priority tests", 'GREEN')
        else:
            self.print_colored("📝 No specific tests identified for changes", 'YELLOW')
        
        return self.run_tests_with_priority(high_priority, remaining, quick_mode=quick_mode)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Adaptive test runner")
    parser.add_argument("--quick", action="store_true", 
                       help="Quick mode - run priority tests only")
    parser.add_argument("--since", default="HEAD~1",
                       help="Compare changes since this commit (default: HEAD~1)")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    runner = AdaptiveTestRunner()
    success = runner.run_adaptive_tests(quick_mode=args.quick, since=args.since)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()