#!/usr/bin/env python3
"""
Benchmark Sequential vs Parallel Execution

Test to determine if pytest-xdist provides actual speedup for the full test suite.
"""

import subprocess
import sys
import time
from pathlib import Path

def run_benchmark():
    """Benchmark sequential vs parallel execution"""
    print("🏁 Benchmarking Sequential vs Parallel Test Execution")
    print("="*70)
    
    # Test commands
    tests = [
        ("Sequential", [
            sys.executable, "-m", "pytest",
            "tests/unit",
            "--tb=no",
            "--disable-warnings",
            "-q",
            "--maxfail=5"
        ]),
        ("Parallel 2 workers", [
            sys.executable, "-m", "pytest", 
            "tests/unit",
            "-n2",
            "--dist=loadfile",
            "--tb=no",
            "--disable-warnings", 
            "-q",
            "--maxfail=5"
        ]),
        ("Parallel 4 workers", [
            sys.executable, "-m", "pytest",
            "tests/unit", 
            "-n4",
            "--dist=loadfile",
            "--tb=no",
            "--disable-warnings",
            "-q", 
            "--maxfail=5"
        ])
    ]
    
    results = []
    
    for name, cmd in tests:
        print(f"\n🧪 Running {name}...")
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, timeout=600, cwd=Path(__file__).parent.parent)
            duration = time.time() - start_time
            success = result.returncode in [0, 1]  # 0=pass, 1=some failed but completed
            
            if success:
                print(f"✅ {name}: {duration:.2f}s")
                results.append((name, duration, True))
            else:
                print(f"❌ {name}: Failed ({result.returncode})")
                results.append((name, float('inf'), False))
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"🚨 {name}: Timed out after {duration:.2f}s")
            results.append((name, float('inf'), False))
            
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append((name, float('inf'), False))
    
    # Results analysis
    print("\n" + "="*70)
    print("📊 BENCHMARK RESULTS")
    print("="*70)
    
    successful_results = [(name, duration) for name, duration, success in results if success]
    
    if len(successful_results) >= 2:
        baseline_name, baseline_time = successful_results[0]
        print(f"Baseline ({baseline_name}): {baseline_time:.2f}s")
        
        for name, duration in successful_results[1:]:
            speedup = baseline_time / duration if duration > 0 else 0
            if speedup > 1:
                print(f"{name}: {duration:.2f}s (🚀 {speedup:.2f}x speedup)")
            else:
                print(f"{name}: {duration:.2f}s (📉 {1/speedup:.2f}x slower)")
        
        # Recommendation
        print("\n💡 RECOMMENDATION:")
        best = min(successful_results, key=lambda x: x[1])
        if best[0] == baseline_name:
            print("   ❌ Parallel execution not beneficial - use sequential mode")
            print("   📝 Overhead of process spawning exceeds benefits")
        else:
            print(f"   ✅ Use {best[0]} for optimal performance")
            print(f"   📈 {baseline_time/best[1]:.2f}x faster than sequential")
    else:
        print("❌ Insufficient successful runs for comparison")
    
    return len(successful_results) > 0

if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
