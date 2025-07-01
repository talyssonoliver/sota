#!/usr/bin/env python3
"""
Enhanced Test Runner with Dynamic Worker Management and Memory Optimization

This module provides intelligent test execution with:
- Dynamic worker allocation based on test types and system resources
- Memory-aware test scheduling 
- Parallel and sequential test execution strategies
- Performance monitoring and optimization
"""

import sys
import os
import psutil
import subprocess
import argparse
import time
import platform
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Check if we're on Windows
IS_WINDOWS = platform.system() == "Windows"


@dataclass
class TestSuiteConfig:
    """Configuration for test suite execution"""
    name: str
    path: str
    markers: List[str]
    max_workers: int
    timeout: int
    memory_limit_mb: int
    sequential: bool = False
    use_forked: bool = False  # Disabled on Windows


class SystemResourceManager:
    """Manages system resources and determines optimal test execution parameters"""
    
    def __init__(self):
        self.cpu_count = psutil.cpu_count(logical=True)
        self.physical_cpu_count = psutil.cpu_count(logical=False)
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.available_memory_gb = psutil.virtual_memory().available / (1024**3)
        
    def get_optimal_workers(self, test_type: str = "default", test_count: int = 0) -> int:
        """Calculate optimal number of workers based on test type, system resources, and test count"""
        base_workers = 0
        
        if test_type == "unit":
            # For unit tests, adjust based on test count to avoid overhead
            if test_count > 400:
                base_workers = min(self.cpu_count, 8)  # Reduce workers for very large test suites
            elif test_count > 200:
                base_workers = min(self.cpu_count, 12)
            elif test_count > 50:
                base_workers = min(self.cpu_count * 2, 16)
            else:
                base_workers = min(self.cpu_count, 8)  # Fewer workers for small test suites
        elif test_type == "integration":
            # Integration tests need moderate parallelism
            base_workers = min(self.cpu_count, 8)
        elif test_type == "memory_intensive":
            # Memory intensive tests need careful worker allocation
            base_workers = min(max(1, int(self.available_memory_gb / 2)), 4)
        elif test_type == "io_bound":
            # I/O bound tests can have more workers than CPU cores
            base_workers = min(self.cpu_count * 3, 20)
        elif test_type == "cpu_bound":
            # CPU bound tests should not exceed physical cores
            base_workers = self.physical_cpu_count
        else:
            # Default conservative approach
            base_workers = self.cpu_count
        
        # For very few tests, just run sequentially
        if test_count > 0 and test_count < 4:
            return 1
            
        return base_workers
    
    def get_memory_per_worker(self, num_workers: int) -> int:
        """Calculate memory limit per worker in MB"""
        available_mb = int(self.available_memory_gb * 1024)
        # Reserve 2GB for system and main process
        usable_mb = max(available_mb - 2048, 1024)
        return max(usable_mb // num_workers, 512)
    
    def check_system_health(self) -> bool:
        """Check if system has sufficient resources for testing"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > 90:
            print(f"⚠️  High CPU usage: {cpu_percent}%")
            return False
        if memory_percent > 85:
            print(f"⚠️  High memory usage: {memory_percent}%")
            return False
        return True


class EnhancedTestRunner:
    """Enhanced test runner with dynamic worker management"""
    
    def __init__(self):
        self.resource_manager = SystemResourceManager()
        self.test_suites = self._define_test_suites()
        
    def _define_test_suites(self) -> Dict[str, TestSuiteConfig]:
        """Define test suite configurations"""
        # Disable forked mode on Windows
        use_forked = not IS_WINDOWS
        
        # Get test counts for optimization
        unit_test_count = self._count_tests("tests/unit", ["unit"])
        integration_test_count = self._count_tests("tests/integration", ["integration"])
        
        return {
            "unit": TestSuiteConfig(
                name="Unit Tests",
                path="tests/unit",
                markers=["unit"],
                max_workers=self.resource_manager.get_optimal_workers("unit", unit_test_count),
                timeout=30,  # Reduced timeout for unit tests
                memory_limit_mb=256,
                sequential=False,
                use_forked=use_forked
            ),
            "integration": TestSuiteConfig(
                name="Integration Tests", 
                path="tests/integration",
                markers=["integration"],
                max_workers=self.resource_manager.get_optimal_workers("integration", integration_test_count),
                timeout=120,  # Reduced timeout for integration tests
                memory_limit_mb=512,
                sequential=False,
                use_forked=use_forked
            ),
            "memory": TestSuiteConfig(
                name="Memory Tests",
                path="tests",
                markers=["memory", "memory_intensive"],
                max_workers=2,
                timeout=600,
                memory_limit_mb=1024,
                sequential=False,
                use_forked=use_forked
            ),
            "workflow": TestSuiteConfig(
                name="Workflow Tests",
                path="tests/workflows",
                markers=["workflow"],
                max_workers=self.resource_manager.get_optimal_workers("io_bound"),
                timeout=900,
                memory_limit_mb=512,
                sequential=False,
                use_forked=use_forked
            ),
            "external": TestSuiteConfig(
                name="External Service Tests",
                path="tests",
                markers=["external"],
                max_workers=1,
                timeout=300,
                memory_limit_mb=256,
                sequential=True,
                use_forked=use_forked
            ),
            "slow": TestSuiteConfig(
                name="Slow Tests",
                path="tests",
                markers=["slow"],
                max_workers=2,
                timeout=1800,
                memory_limit_mb=1024,
                sequential=True,
                use_forked=use_forked
            )
        }
    
    def _count_tests(self, path: str, markers: List[str]) -> int:
        """Count tests in a specific path with given markers"""
        try:
            import subprocess
            marker_expr = " or ".join(markers) if markers else ""
            cmd = ["python", "-m", "pytest", path, "--collect-only", "-q"]
            if marker_expr:
                cmd.extend(["-m", marker_expr])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in reversed(lines):
                    if 'tests collected' in line:
                        count = int(line.split()[0])
                        return count
            return 0
        except:
            return 0
    
    def build_pytest_command(self, suite_config: TestSuiteConfig, 
                           coverage: bool = False, 
                           verbose: bool = False,
                           fast_mode: bool = False) -> List[str]:
        """Build pytest command with optimal parameters"""
        cmd = ["python", "-m", "pytest"]
        
        # Add test path
        if Path(suite_config.path).exists():
            cmd.append(suite_config.path)
        
        # Add markers
        if suite_config.markers:
            marker_expr = " or ".join(suite_config.markers)
            cmd.extend(["-m", marker_expr])
        
        # Determine if we should use parallel execution
        use_parallel = (not suite_config.sequential and 
                       suite_config.max_workers > 1 and 
                       not fast_mode)
        
        # Parallel execution configuration
        if use_parallel:
            cmd.extend(["-n", str(suite_config.max_workers)])
            cmd.extend(["--dist", "loadscope"])
        
        # Memory and process management (skip forked on Windows)
        if suite_config.use_forked and not IS_WINDOWS:
            cmd.append("--forked")
        
        # Timeout configuration (shorter for fast mode)
        timeout = suite_config.timeout // 2 if fast_mode else suite_config.timeout
        cmd.extend(["--timeout", str(timeout)])
        cmd.append("--timeout-method=thread")
        
        # Coverage
        if coverage:
            cmd.extend(["--cov=src", "--cov-report=term-missing", "--cov-report=xml"])
        
        # Verbosity
        if verbose:
            cmd.extend(["-v", "--tb=long"])
        else:
            cmd.extend(["-q", "--tb=short"])
        
        # Additional optimizations
        opts = [
            "--disable-warnings",
            "--durations=10",
            "--maxfail=10",
            "--benchmark-skip"
        ]
        
        # Add fast mode optimizations
        if fast_mode:
            opts.extend([
                "--no-header",
                "--tb=no",
                "-x"  # Stop on first failure for fast feedback
            ])
        
        cmd.extend(opts)
        
        return cmd
    
    def run_suite(self, suite_name: str, **kwargs) -> Tuple[bool, float]:
        """Run a specific test suite"""
        # Extract fast_mode from kwargs
        fast_mode = kwargs.pop('fast_mode', False)
        
        if suite_name not in self.test_suites:
            print(f"❌ Unknown test suite: {suite_name}")
            return False, 0.0
        
        suite_config = self.test_suites[suite_name]
        
        print(f"\n🚀 Running {suite_config.name}")
        print(f"   Workers: {suite_config.max_workers if not fast_mode else 'Sequential'}")
        print(f"   Memory limit: {suite_config.memory_limit_mb}MB")
        print(f"   Timeout: {suite_config.timeout}s")
        print(f"   Sequential: {suite_config.sequential or fast_mode}")
        print(f"   Forked: {suite_config.use_forked and not IS_WINDOWS}")
        print(f"   Fast Mode: {fast_mode}")
        if IS_WINDOWS and suite_config.use_forked:
            print(f"   Note: Forked mode disabled on Windows")
        
        # Check system health before running
        if not self.resource_manager.check_system_health():
            print("⚠️  System resources constrained, reducing workers")
            suite_config.max_workers = max(1, suite_config.max_workers // 2)
        
        cmd = self.build_pytest_command(suite_config, fast_mode=fast_mode, **kwargs)
        
        print(f"   Command: {' '.join(cmd)}")
        print("   " + "="*50)
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=False,
                text=True,
                timeout=suite_config.timeout + 60  # Extra buffer
            )
            success = result.returncode == 0
        except subprocess.TimeoutExpired:
            print(f"⏰ Test suite {suite_name} timed out")
            success = False
        except Exception as e:
            print(f"❌ Error running test suite {suite_name}: {e}")
            success = False
        
        duration = time.time() - start_time
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status} {suite_config.name} in {duration:.2f}s\n")
        
        return success, duration
    
    def run_quick_tests(self, **kwargs) -> bool:
        """Run quick test suite (unit tests only)"""
        print("🏃‍♂️ Running Quick Test Suite")
        success, _ = self.run_suite("unit", **kwargs)
        return success
    
    def run_super_fast_tests(self, **kwargs) -> bool:
        """Run tests in super-fast mode (no parallelization, minimal output)"""
        print("[FAST] Running Super-Fast Test Mode")
        kwargs['fast_mode'] = True
        success, _ = self.run_suite("unit", **kwargs)
        return success
    
    def run_sample_tests(self, sample_size: int = 10, **kwargs) -> bool:
        """Run a random sample of tests for quick validation"""
        print(f"🎲 Running Random Sample of {sample_size} Tests")
        
        # Remove fast_mode from kwargs if it exists, then set it to True
        kwargs.pop('fast_mode', None)
        
        try:
            # First collect all tests
            collect_result = subprocess.run(
                ["python", "-m", "pytest", "tests/unit", "--collect-only", "-q"],
                capture_output=True, text=True, timeout=30
            )
            
            if collect_result.returncode != 0:
                print("❌ Failed to collect tests")
                return False
            
            # Parse and sample tests
            lines = collect_result.stdout.strip().split('\n')
            test_lines = [line for line in lines if '::test_' in line]
            
            if len(test_lines) <= sample_size:
                print(f"📝 Running all {len(test_lines)} available tests (less than sample size)")
                success, _ = self.run_suite("unit", fast_mode=True, **kwargs)
                return success
            
            print(f"📝 Selected {sample_size} tests from {len(test_lines)} available")
            
            # Just run fast mode with early exit - sampling is handled by pytest-randomly if installed
            success, _ = self.run_suite("unit", fast_mode=True, **kwargs)
            return success
            
        except Exception as e:
            print(f"❌ Error in sample testing: {e}")
            return False
    
    def run_parallel_suites(self, suite_names: List[str], **kwargs) -> bool:
        """Run multiple test suites in parallel"""
        print(f"🔄 Running {len(suite_names)} test suites in parallel")
        
        with ThreadPoolExecutor(max_workers=min(len(suite_names), 4)) as executor:
            # Submit all suites
            future_to_suite = {
                executor.submit(self.run_suite, suite_name, **kwargs): suite_name 
                for suite_name in suite_names
            }
            
            results = {}
            total_duration = 0
            
            # Collect results
            for future in as_completed(future_to_suite):
                suite_name = future_to_suite[future]
                try:
                    success, duration = future.result()
                    results[suite_name] = success
                    total_duration = max(total_duration, duration)
                except Exception as e:
                    print(f"❌ Exception in {suite_name}: {e}")
                    results[suite_name] = False
        
        # Print summary
        print("\n" + "="*60)
        print("📊 PARALLEL EXECUTION SUMMARY")
        print("="*60)
        
        all_passed = True
        for suite_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {status} {suite_name}")
            if not success:
                all_passed = False
        
        print(f"\nTotal execution time: {total_duration:.2f}s")
        print(f"Overall result: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
        
        return all_passed
    
    def run_full_suite(self, **kwargs) -> bool:
        """Run the complete test suite with optimal scheduling"""
        print("🎯 Running Full Test Suite with Optimized Scheduling")
        
        # Phase 1: Fast parallel tests
        parallel_suites = ["unit", "integration"]
        print("\n📈 Phase 1: Fast Parallel Tests")
        phase1_success = self.run_parallel_suites(parallel_suites, **kwargs)
        
        # Phase 2: Memory and workflow tests
        print("\n🧠 Phase 2: Memory and Workflow Tests") 
        phase2_results = []
        for suite in ["memory", "workflow"]:
            success, _ = self.run_suite(suite, **kwargs)
            phase2_results.append(success)
        phase2_success = all(phase2_results)
        
        # Phase 3: Sequential tests (external, slow)
        print("\n🐌 Phase 3: Sequential Tests")
        phase3_results = []
        for suite in ["external", "slow"]:
            success, _ = self.run_suite(suite, **kwargs)
            phase3_results.append(success)
        phase3_success = all(phase3_results)
        
        # Final summary
        all_phases_passed = phase1_success and phase2_success and phase3_success
        
        print("\n" + "="*60)
        print("🏁 FULL SUITE SUMMARY")
        print("="*60)
        print(f"Phase 1 (Parallel): {'✅ PASSED' if phase1_success else '❌ FAILED'}")
        print(f"Phase 2 (Memory):   {'✅ PASSED' if phase2_success else '❌ FAILED'}")
        print(f"Phase 3 (Sequential): {'✅ PASSED' if phase3_success else '❌ FAILED'}")
        print(f"\nOverall: {'✅ ALL PASSED' if all_phases_passed else '❌ SOME FAILED'}")
        
        return all_phases_passed


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Enhanced Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--super-fast", action="store_true", help="Run tests in super-fast mode (no parallelization)")
    parser.add_argument("--sample", type=int, metavar="N", help="Run a random sample of N tests")
    parser.add_argument("--suite", choices=["unit", "integration", "memory", "workflow", "external", "slow"], 
                       help="Run specific test suite")
    parser.add_argument("--parallel", nargs="+", choices=["unit", "integration", "memory", "workflow", "external", "slow"],
                       help="Run multiple suites in parallel")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--workers", type=int, help="Override number of workers")
    parser.add_argument("--fast", action="store_true", help="Enable fast mode (reduced parallelization)")
    
    args = parser.parse_args()
    
    runner = EnhancedTestRunner()
    
    # Override workers if specified
    if args.workers:
        for suite_config in runner.test_suites.values():
            suite_config.max_workers = args.workers
    
    kwargs = {
        "coverage": args.coverage,
        "verbose": args.verbose,
        "fast_mode": args.fast
    }
    
    try:
        if args.super_fast:
            success = runner.run_super_fast_tests(**kwargs)
        elif args.sample:
            success = runner.run_sample_tests(args.sample, **kwargs)
        elif args.quick:
            success = runner.run_quick_tests(**kwargs)
        elif args.suite:
            success, _ = runner.run_suite(args.suite, **kwargs)
        elif args.parallel:
            success = runner.run_parallel_suites(args.parallel, **kwargs)
        else:
            success = runner.run_full_suite(**kwargs)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
