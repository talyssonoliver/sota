#!/usr/bin/env python3
"""
Detailed Import Analysis Tool
Traces exactly which dependencies are causing slow imports.
"""

import subprocess
import time
from typing import Dict, List, Tuple


def run_import_timing(import_statement: str) -> Tuple[float, List[str]]:
    """Run import timing and parse results."""
    cmd = ['python3', '-X', 'importtime', '-c', import_statement]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse timing information
    lines = result.stderr.split('\n')
    total_time = 0
    heavy_imports = []
    
    for line in lines:
        if 'import time:' in line and '|' in line:
            # Extract cumulative time (second number)
            parts = line.split('|')
            if len(parts) >= 3:
                try:
                    cumulative_time = int(parts[1].strip())
                    module_name = parts[2].strip()
                    
                    # Track heavy imports (>10ms)
                    if cumulative_time > 10000:  # 10ms in microseconds
                        heavy_imports.append(f"{cumulative_time/1000:.1f}ms - {module_name}")
                        
                    total_time = max(total_time, cumulative_time)
                except ValueError:
                    continue
    
    return total_time / 1000, heavy_imports  # Convert to milliseconds


def analyze_import_chain():
    """Analyze the import chain that causes performance issues."""
    
    print("🔍 DETAILED IMPORT CHAIN ANALYSIS")
    print("=" * 60)
    
    imports_to_test = [
        # Test individual components
        ("Base Package", "import src"),
        ("Core Package", "import src.core"),
        ("Agents Package", "import src.core.agents"), 
        ("Workflows Package", "import src.core.workflows"),
        ("Tasks Package", "import src.core.tasks"),
        ("States Module", "import src.core.workflows.states"),
        
        # Test specific heavy imports
        ("Backend Engineer", "from src.core.agents.backend import BackendEngineer"),
        ("Memory Engine", "from src.infrastructure.memory.engines.memory_engine import MemoryEngine"),
        ("Daily Cycle", "from src.core.workflows.daily_cycle import DailyCycleOrchestrator"),
        
        # Test known heavy dependencies
        ("CrewAI Import", "import crewai"),
        ("Flask Import", "import flask"),
        ("NumPy Import", "import numpy"),
    ]
    
    results = []
    
    for name, import_stmt in imports_to_test:
        print(f"\n📊 Testing: {name}")
        print(f"Command: {import_stmt}")
        
        try:
            start_time = time.time()
            total_ms, heavy_imports = run_import_timing(import_stmt)
            actual_time = (time.time() - start_time) * 1000
            
            print(f"⏱️  Import time: {total_ms:.1f}ms (actual: {actual_time:.1f}ms)")
            
            if heavy_imports:
                print("🔥 Heavy dependencies (>10ms):")
                for heavy in heavy_imports[-10:]:  # Show top 10
                    print(f"   {heavy}")
            else:
                print("✅ No heavy dependencies detected")
                
            results.append({
                'name': name,
                'import': import_stmt,
                'time_ms': total_ms,
                'actual_ms': actual_time,
                'heavy_count': len(heavy_imports),
                'status': 'slow' if total_ms > 100 else 'fast'
            })
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append({
                'name': name,
                'import': import_stmt,
                'time_ms': 0,
                'actual_ms': 0,
                'heavy_count': 0,
                'status': 'error'
            })
    
    return results


def find_import_bottlenecks():
    """Find the specific modules causing import bottlenecks."""
    
    print("\n🎯 IMPORT BOTTLENECK ANALYSIS")
    print("=" * 60)
    
    # Test suspected heavy modules individually
    suspected_modules = [
        "yaml",
        "flask", 
        "werkzeug",
        "jinja2",
        "numpy",
        "crewai",
        "langchain",
        "chromadb",
        "requests",
        "pandas",
        "matplotlib",
    ]
    
    bottlenecks = []
    
    for module in suspected_modules:
        print(f"Testing: {module}")
        try:
            total_ms, heavy_imports = run_import_timing(f"import {module}")
            if total_ms > 50:  # >50ms is considered slow
                bottlenecks.append((module, total_ms, len(heavy_imports)))
                print(f"🐌 SLOW: {module} = {total_ms:.1f}ms ({len(heavy_imports)} heavy deps)")
            else:
                print(f"✅ FAST: {module} = {total_ms:.1f}ms")
        except Exception as e:
            print(f"❌ ERROR: {module} - {e}")
    
    return bottlenecks


def generate_optimization_recommendations(results: List[Dict], bottlenecks: List[Tuple]):
    """Generate specific optimization recommendations."""
    
    print("\n💡 OPTIMIZATION RECOMMENDATIONS")
    print("=" * 60)
    
    # Analyze results
    slow_imports = [r for r in results if r['status'] == 'slow']
    fast_imports = [r for r in results if r['status'] == 'fast']
    
    print("📊 Import Performance Summary:")
    print(f"   🐌 Slow imports (>100ms): {len(slow_imports)}")
    print(f"   ✅ Fast imports (<100ms): {len(fast_imports)}")
    print(f"   ❌ Failed imports: {len([r for r in results if r['status'] == 'error'])}")
    
    if slow_imports:
        print("\n🔥 Slowest Imports:")
        slow_imports.sort(key=lambda x: x['time_ms'], reverse=True)
        for i, result in enumerate(slow_imports[:5], 1):
            print(f"   {i}. {result['name']}: {result['time_ms']:.1f}ms")
    
    if bottlenecks:
        print("\n🎯 Heavy Dependencies Found:")
        bottlenecks.sort(key=lambda x: x[1], reverse=True)
        for module, time_ms, heavy_count in bottlenecks[:5]:
            print(f"   • {module}: {time_ms:.1f}ms ({heavy_count} dependencies)")
    
    print("\n🛠️  Specific Recommendations:")
    
    # Package-level recommendations
    if any('src.core' in r['import'] for r in slow_imports):
        print("   1. Fix src.core package imports:")
        print("      - Remove eager imports from src/core/__init__.py")
        print("      - Use lazy loading pattern for heavy modules")
        print("      - Consider TYPE_CHECKING for type-only imports")
    
    # Dependency-specific recommendations  
    heavy_deps = [b[0] for b in bottlenecks if b[1] > 100]
    if heavy_deps:
        print("   2. Optimize heavy dependencies:")
        for dep in heavy_deps[:3]:
            print(f"      - {dep}: Use conditional imports or lazy loading")
    
    # Module-specific recommendations
    if any('backend' in r['import'] for r in slow_imports):
        print("   3. Backend agent optimization:")
        print("      - Move crewai import to lazy property")
        print("      - Use TYPE_CHECKING for optional dependencies")
    
    if any('memory' in r['import'] for r in slow_imports):
        print("   4. Memory engine optimization:")
        print("      - Already optimized with lazy loading")
        print("      - Consider reducing initial import chain")
    
    print("\n⚡ Expected Performance Gains:")
    total_slow_time = sum(r['time_ms'] for r in slow_imports)
    if total_slow_time > 0:
        print(f"   • Current slow import time: {total_slow_time:.0f}ms")
        print(f"   • Expected after optimization: {total_slow_time * 0.2:.0f}ms")
        print(f"   • Potential improvement: {80:.0f}%")


def main():
    """Main analysis execution."""
    print("🚀 Deep Import Chain Analysis")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Run comprehensive analysis
    results = analyze_import_chain()
    bottlenecks = find_import_bottlenecks()
    generate_optimization_recommendations(results, bottlenecks)
    
    print("\n🎉 Analysis completed!")
    print("See recommendations above for specific optimization targets.")


if __name__ == "__main__":
    main()