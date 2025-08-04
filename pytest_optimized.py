#!/usr/bin/env python3
"""
Optimized pytest runner that automatically uses parallel execution when available.
This script provides the same interface as pytest but with performance optimizations.
"""

import subprocess
import sys
import importlib

def check_xdist_available():
    """Check if pytest-xdist is available for parallel execution."""
    try:
        importlib.import_module('xdist')
        return True
    except ImportError:
        return False

def run_pytest_optimized():
    """Run pytest with automatic performance optimizations."""
    
    # Get all command line arguments
    args = sys.argv[1:]  # Skip script name
    
    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add parallel execution if xdist is available
    if check_xdist_available():
        parallel_args = ["-n", "auto", "--dist", "loadscope"]
        
        # Check if user already specified parallel options
        has_parallel = any(arg in args for arg in ["-n", "--numprocesses", "--dist"])
        
        if not has_parallel:
            print("🚀 Using parallel execution for better performance...")
            cmd.extend(parallel_args)
        else:
            print("⚡ Using user-specified parallel configuration...")
    else:
        print("⚠️  pytest-xdist not available, running sequentially. Install with: pip install pytest-xdist")
    
    # Add user arguments
    cmd.extend(args)
    
    # If no arguments provided, use sensible defaults
    if not args:
        cmd.extend(["tests/", "--tb=short"])
    
    print(f"🧪 Running: {' '.join(cmd[2:])}")  # Skip python -m pytest
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_pytest_optimized())