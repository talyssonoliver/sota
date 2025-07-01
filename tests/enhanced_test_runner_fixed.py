#!/usr/bin/env python3
"""
Fixed Enhanced Test Runner - Prevents Hanging and Crashes

This module provides a safe test execution environment that prevents:
- Memory exhaustion leading to system crashes
- Infinite loops in parallel execution
- Resource deadlocks
- Process spawning issues on Windows
"""

import sys
import os
import psutil
import subprocess
import argparse
import time
import platform
import signal
import threading
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Check if we're on Windows
IS_WINDOWS = platform.system() == "Windows"

# Safety limits to prevent crashes
MAX_WORKERS = min(4, psutil.cpu_count())  # Conservative worker limit
MAX_MEMORY_GB = 16  # Maximum memory usage before stopping
TIMEOUT_PER_TEST = 30  # Seconds per test
GLOBAL_TIMEOUT = 300  # 5 minutes total timeout


class SafetyMonitor:
    """Monitors system resources and stops execution if unsafe conditions are detected"""
    
    def __init__(self, max_memory_gb=MAX_MEMORY_GB):
        self.max_memory_bytes = max_memory_gb * 1024 * 1024 * 1024
        self.monitoring = False
        self.should_stop = False
        
    def start_monitoring(self):
        """Start monitoring in a separate thread"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        
    def _monitor_loop(self):
        """Monitor system resources"""
        while self.monitoring:
            try:
                # Check memory usage
                memory_info = psutil.virtual_memory()
                if memory_info.used > self.max_memory_bytes:
                    print(f"🚨 Memory usage too high: {memory_info.used / (1024**3):.1f}GB")
                    self.should_stop = True
                    break
                    
                # Check if system is responsive
                if memory_info.percent > 95:
                    print(f"🚨 System memory at {memory_info.percent}%")
                    self.should_stop = True
                    break
                    
                time.sleep(1)
            except Exception as e:
                print(f"Safety monitor error: {e}")
                break


class SafeTestRunner:
    """Safe test runner that prevents hanging and crashes"""
    
    def __init__(self):
        self.safety_monitor = SafetyMonitor()
        self.processes = []
        
    def run_pytest_safe(self, args: List[str], timeout: int = GLOBAL_TIMEOUT) -> Tuple[int, str, str]:
        """Run pytest with safety measures"""
        
        # Start safety monitoring
        self.safety_monitor.start_monitoring()
        
        try:
            # Construct safe pytest command
            cmd = self._build_safe_command(args)
            print(f"🚀 Running: {' '.join(cmd)}")
            
            # Run with timeout and resource limits
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if IS_WINDOWS else 0
            )
            
            self.processes.append(process)
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                
                if self.safety_monitor.should_stop:
                    return 1, "Test execution stopped due to safety concerns", stderr
                    
                return return_code, stdout, stderr
                
            except subprocess.TimeoutExpired:
                print(f"🚨 Tests timed out after {timeout} seconds")
                self._kill_process_tree(process)
                return 1, "Tests timed out", "Timeout expired"
                
        except Exception as e:
            print(f"🚨 Error running tests: {e}")
            return 1, "", str(e)
            
        finally:
            self.safety_monitor.stop_monitoring()
            self._cleanup_processes()
    
    def _build_safe_command(self, args: List[str]) -> List[str]:
        """Build a safe pytest command with conservative settings"""
        
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add safety flags
        safe_flags = [
            "--tb=short",  # Short traceback
            "--disable-warnings",  # Reduce output
            "--maxfail=5",  # Stop after 5 failures
            "--timeout=30",  # 30 second timeout per test
            "-x",  # Stop on first failure for safety
            "--no-cov",  # Disable coverage for speed
        ]
        
        # Handle parallel execution safely
        if any("--parallel" in str(arg) or "-n" in str(arg) for arg in args):
            # Use minimal workers for safety
            safe_flags.extend(["-n", "2", "--dist", "loadfile"])
        elif not any("-n" in str(arg) for arg in args):
            # Default to sequential execution for safety
            pass
        
        # Add verbosity if requested
        if any("-v" in str(arg) for arg in args):
            safe_flags.append("-v")
            
        # Filter out dangerous flags
        filtered_args = []
        skip_next = False
        for arg in args:
            if skip_next:
                skip_next = False
                continue
                
            if any(dangerous in str(arg) for dangerous in [
                "--forked",  # Can cause issues on Windows
                "--numprocesses",  # We control this
                "--benchmark",  # Can be memory intensive
                "--cov-report=html",  # Can be slow
            ]):
                if "=" not in str(arg):
                    skip_next = True
                continue
                
            filtered_args.append(str(arg))
        
        cmd.extend(safe_flags)
        cmd.extend(filtered_args)
        
        return cmd
    
    def _kill_process_tree(self, process):
        """Kill process and all its children"""
        try:
            if IS_WINDOWS:
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except Exception as e:
            print(f"Error killing process: {e}")
    
    def _cleanup_processes(self):
        """Clean up any remaining processes"""
        for process in self.processes:
            try:
                if process.poll() is None:
                    self._kill_process_tree(process)
            except Exception:
                pass
        self.processes.clear()


def run_quick_tests():
    """Run a quick subset of tests safely"""
    runner = SafeTestRunner()
    
    # Run only unit tests with minimal configuration
    args = [
        "tests/unit",
        "-v",
        "--tb=short",
        "--maxfail=3",
        "-x"  # Stop on first failure
    ]
    
    return_code, stdout, stderr = runner.run_pytest_safe(args, timeout=120)
    
    print("📊 Test Results:")
    print(f"Return code: {return_code}")
    if stdout:
        print("STDOUT:", stdout[-1000:])  # Last 1000 chars
    if stderr:
        print("STDERR:", stderr[-1000:])  # Last 1000 chars
    
    return return_code


def run_safe_tests(test_path: str = "tests", max_workers: int = 2):
    """Run tests with maximum safety measures"""
    runner = SafeTestRunner()
    
    args = [
        test_path,
        "-v",
        "--tb=short",
        "--disable-warnings",
        "--maxfail=5",
        "-x",
        f"-n {max_workers}" if max_workers > 1 else ""
    ]
    
    # Filter empty args
    args = [arg for arg in args if arg]
    
    return_code, stdout, stderr = runner.run_pytest_safe(args, timeout=GLOBAL_TIMEOUT)
    
    print("📊 Safe Test Results:")
    print(f"Return code: {return_code}")
    if return_code == 0:
        print("✅ All tests passed safely!")
    else:
        print("❌ Some tests failed or were stopped for safety")
    
    return return_code


def main():
    """Main entry point with safety measures"""
    parser = argparse.ArgumentParser(description="Safe Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--safe", action="store_true", help="Run with maximum safety")
    parser.add_argument("--workers", type=int, default=2, help="Number of workers (max 4)")
    parser.add_argument("--timeout", type=int, default=GLOBAL_TIMEOUT, help="Global timeout")
    parser.add_argument("test_path", nargs="?", default="tests", help="Test path")
    
    args = parser.parse_args()
    
    # Limit workers for safety
    workers = min(args.workers, MAX_WORKERS)
    
    print(f"🔧 Safe Test Runner Configuration:")
    print(f"   Workers: {workers}")
    print(f"   Timeout: {args.timeout}s")
    print(f"   Memory limit: {MAX_MEMORY_GB}GB")
    print(f"   Platform: {platform.system()}")
    
    if args.quick:
        return run_quick_tests()
    elif args.safe:
        return run_safe_tests(args.test_path, workers)
    else:
        # Default safe mode
        return run_safe_tests(args.test_path, workers)


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"🚨 Unexpected error: {e}")
        sys.exit(1)
