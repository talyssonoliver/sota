#!/usr/bin/env python3
"""
Ultra-safe test runner that prevents hanging
"""
import subprocess
import sys
import signal
import os
import psutil
import time
from pathlib import Path

def kill_all_pytest():
    """Kill any existing pytest processes"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and any('pytest' in str(cmd) for cmd in proc.info['cmdline'] or []):
                    print(f"Killing process: {proc.info['pid']}")
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        time.sleep(2)  # Give processes time to die
    except Exception as e:
        print(f"Error killing processes: {e}")

def run_ultra_safe_pytest():
    """Run pytest with ultra-safe settings"""
    
    # Kill any hanging processes first
    kill_all_pytest()
    
    # Use the ultra-safe config
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-c', 'pytest.ultra-safe.ini'
    ]
    
    print(f"Running ultra-safe pytest...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run with aggressive timeout
        result = subprocess.run(cmd, timeout=120, capture_output=True, text=True)
        
        print("\n" + "="*60)
        print("RESULTS:")
        print("="*60)
        print(result.stdout)
        
        if result.stderr:
            print("\nERRORS:")
            print("-"*40)
            print(result.stderr)
        
        print(f"\nExit code: {result.returncode}")
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("Tests timed out after 2 minutes - killing all processes")
        kill_all_pytest()
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        kill_all_pytest()
        return 1

if __name__ == "__main__":
    exit_code = run_ultra_safe_pytest()
    sys.exit(exit_code)
