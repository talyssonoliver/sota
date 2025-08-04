#!/usr/bin/env python3
"""
Advanced Test Performance Optimizer for AI System Test Suite

Optimizes ~2000 tests with intelligent strategies:
- Parallel execution with optimized worker allocation
- Smart test selection and collection filtering
- Heavy fixture optimization with session scoping
- I/O bottleneck elimination
- Memory and resource management
"""

import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psutil

logger = logging.getLogger(__name__)


class TestPerformanceOptimizer:
    """Optimizes test suite performance with intelligent resource management."""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.cwd()
        self.results_file = self.base_dir / "test_performance_results.json"
        self.config_file = self.base_dir / "pytest_optimized.ini"
        
    def analyze_system_resources(self) -> Dict[str, int]:
        """Analyze system resources for optimal worker allocation."""
        cpu_count = psutil.cpu_count(logical=True)
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Optimal worker calculation based on system resources
        if memory_gb < 4:
            workers = max(2, cpu_count // 2)
        elif memory_gb < 8:
            workers = max(4, cpu_count)
        else:
            workers = min(cpu_count * 2, 16)  # Cap at 16 workers
            
        return {
            "cpu_count": cpu_count,
            "memory_gb": int(memory_gb),
            "optimal_workers": workers,
            "recommended_batch_size": workers * 4
        }
    
    def create_optimized_pytest_config(self) -> Path:
        """Create optimized pytest configuration."""
        system_info = self.analyze_system_resources()
        
        config_content = f"""[pytest]
# Optimized configuration for ~2000 tests
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Performance optimizations
addopts = 
    -n {system_info['optimal_workers']}
    --dist loadscope
    --tb=short
    --disable-warnings
    -q
    --durations=20
    --maxfail=10
    -x
    --strict-markers
    --strict-config

# Environment variables for test isolation
env =
    ANONYMIZED_TELEMETRY=False
    TESTING=1
    PYTEST_RUNNING=1
    DISABLE_WORKFLOW_MONITORING=1
    PYTHONDONTWRITEBYTECODE=1
    PYTEST_CURRENT_TEST={{item.nodeid}}

# Path configuration
pythonpath = .

# Test markers for intelligent selection
markers =
    unit: Fast unit tests (< 1 second)
    integration: Integration tests (1-5 seconds)  
    slow: Tests that take > 5 seconds
    external: Tests requiring external services
    workflow: Workflow execution tests
    memory: Memory engine tests
    agent: Agent instantiation tests
    asyncio: Async test marker
    expensive: Resource-intensive tests
    network: Tests requiring network access
    database: Tests requiring database
    ai_model: Tests using AI models

# Asyncio configuration
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function

# Collection optimizations
collect_ignore = [
    "node_modules",
    ".tox",
    ".venv",
    "venv",
    "build",
    "dist",
    "__pycache__",
    ".git",
    "site-packages"
]

# Timeout configuration
timeout = 300
timeout_method = thread

# Memory management
cache_dir = .pytest_cache
"""
        
        self.config_file.write_text(config_content)
        logger.info(f"Created optimized pytest config: {self.config_file}")
        return self.config_file
    
    def create_test_selection_strategies(self) -> Dict[str, str]:
        """Create different test selection strategies for various scenarios."""
        return {
            "smoke": "tests/test_smoke.py -m 'not slow and not expensive'",
            "unit_only": "tests/unit/ -m 'unit or not slow'",
            "integration": "tests/integration/ -m 'not expensive'",
            "fast": "-m 'unit' --maxfail=3",
            "changed_files": "--lf --ff",  # Last failed, then failed first
            "parallel_unit": "tests/unit/ -n auto --dist loadscope",
            "critical_path": "tests/ -k 'test_workflow or test_agent or test_memory' -m 'not slow'",
            "regression": "--lf --tb=short -v",
            "full": "tests/ --maxfail=50"
        }
    
    def optimize_fixtures_and_mocks(self) -> str:
        """Generate optimized fixtures configuration."""
        return """
# Enhanced fixture optimizations for conftest.py
import asyncio
import functools
from typing import Dict, Any
from unittest.mock import MagicMock, patch
import pytest

# Session-scoped expensive fixtures
@pytest.fixture(scope="session")
def optimized_chromadb_client():
    '''Single ChromaDB client for entire test session.'''
    with patch("chromadb.Client") as mock_client:
        mock_client.return_value = MagicMock()
        yield mock_client.return_value

@pytest.fixture(scope="session") 
def optimized_openai_client():
    '''Single OpenAI client mock for entire session.'''
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        mock_openai.return_value = MagicMock()
        yield mock_openai.return_value

@pytest.fixture(scope="session")
def optimized_supabase_client():
    '''Single Supabase client for entire session.'''
    with patch("supabase.create_client") as mock_supabase:
        yield mock_supabase.return_value

# Cached expensive operations
@functools.lru_cache(maxsize=128)
def get_cached_yaml_data(file_path: str) -> Dict[str, Any]:
    '''Cache YAML loading operations.'''
    import yaml
    with open(file_path) as f:
        return yaml.safe_load(f)

# Fast temporary file fixtures
@pytest.fixture
def fast_temp_file(tmp_path):
    '''Use in-memory temporary files when possible.'''
    import tempfile
    return tempfile.SpooledTemporaryFile(max_size=1024*1024)  # 1MB threshold

# Network isolation
@pytest.fixture(autouse=True)
def isolate_network():
    '''Prevent accidental network calls.'''
    import socket
    original_getaddrinfo = socket.getaddrinfo
    
    def mock_getaddrinfo(*args):
        raise OSError("Network disabled in tests")
    
    socket.getaddrinfo = mock_getaddrinfo
    yield
    socket.getaddrinfo = original_getaddrinfo
"""
    
    def run_performance_benchmark(self, strategy: str = "fast") -> Dict[str, Any]:
        """Run performance benchmark with specified strategy."""
        strategies = self.create_test_selection_strategies()
        test_command = strategies.get(strategy, strategies["fast"])
        
        start_time = time.time()
        system_before = {
            "memory": psutil.virtual_memory().percent,
            "cpu": psutil.cpu_percent(interval=1)
        }
        
        try:
            # Run tests with optimized configuration
            result = subprocess.run([
                "python3", "-m", "pytest",
                "-c", str(self.config_file),
                *test_command.split()
            ], capture_output=True, text=True, timeout=1800)  # 30min timeout
            
            execution_time = time.time() - start_time
            system_after = {
                "memory": psutil.virtual_memory().percent,
                "cpu": psutil.cpu_percent(interval=1)
            }
            
            # Parse pytest output for detailed metrics
            lines = result.stdout.split('\n')
            test_results = self._parse_pytest_output(lines)
            
            benchmark_data = {
                "strategy": strategy,
                "execution_time": execution_time,
                "return_code": result.returncode,
                "system_impact": {
                    "memory_delta": system_after["memory"] - system_before["memory"],
                    "avg_cpu": (system_before["cpu"] + system_after["cpu"]) / 2
                },
                "test_results": test_results,
                "timestamp": time.time()
            }
            
            self._save_benchmark_results(benchmark_data)
            return benchmark_data
            
        except subprocess.TimeoutExpired:
            return {
                "strategy": strategy,
                "error": "Timeout after 30 minutes",
                "execution_time": 1800,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "strategy": strategy,
                "error": str(e),
                "timestamp": time.time()
            }
    
    def _parse_pytest_output(self, lines: List[str]) -> Dict[str, Any]:
        """Parse pytest output for metrics."""
        results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "warnings": 0,
            "slowest_tests": []
        }
        
        for line in lines:
            if "passed" in line and "failed" in line:
                # Extract test counts from summary line
                words = line.split()
                for i, word in enumerate(words):
                    if word == "passed":
                        results["passed"] = int(words[i-1])
                    elif word == "failed":
                        results["failed"] = int(words[i-1])
                    elif word == "skipped":
                        results["skipped"] = int(words[i-1])
            elif line.startswith("SLOWEST"):
                # Parse slowest tests
                pass  # Could parse durations if needed
                
        return results
    
    def _save_benchmark_results(self, data: Dict[str, Any]):
        """Save benchmark results to file."""
        if self.results_file.exists():
            with open(self.results_file) as f:
                results = json.load(f)
        else:
            results = []
            
        results.append(data)
        
        with open(self.results_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def generate_optimization_recommendations(self) -> List[str]:
        """Generate specific optimization recommendations based on analysis."""
        system_info = self.analyze_system_resources()
        
        recommendations = [
            f"💡 Use {system_info['optimal_workers']} parallel workers for optimal performance",
            "🚀 Enable session-scoped fixtures for ChromaDB, OpenAI, and Supabase clients",
            "⚡ Use --lf (last-failed) and --ff (failed-first) for incremental testing",
            "🎯 Implement smart test selection with markers (unit, integration, slow)",
            "🧹 Add automated cleanup with smart-cleanup target",
            "📊 Use --durations=20 to identify slowest tests for optimization",
            "🔄 Implement test result caching with pytest-cache",
            "🎭 Mock network calls and external dependencies in fixtures",
            "💾 Use SpooledTemporaryFile for large test data to reduce I/O",
            "🔧 Set PYTHONDONTWRITEBYTECODE=1 to skip .pyc generation"
        ]
        
        if system_info["memory_gb"] < 8:
            recommendations.append("⚠️  Limited memory detected - reduce parallel workers during heavy tests")
        
        if system_info["cpu_count"] > 8:
            recommendations.append("🔥 High CPU count - consider load balancing with --dist=loadscope")
            
        return recommendations
    
    def create_makefile_targets(self) -> str:
        """Generate optimized Makefile targets for test execution."""
        system_info = self.analyze_system_resources()
        
        return f"""
# Optimized test targets for ~2000 tests
test-ultra-fast: ## Unit tests only (<30s)
\t@echo "$(BLUE)🚀 Running ultra-fast unit tests...$(NC)"
\t@$(PYTHON) -m pytest -c pytest_optimized.ini tests/unit/ -m "unit" --maxfail=3 -x

test-smoke: ## Smoke tests for critical functionality (<60s)
\t@echo "$(BLUE)💨 Running smoke tests...$(NC)"
\t@$(PYTHON) -m pytest -c pytest_optimized.ini tests/test_smoke.py -m "not slow" --maxfail=5

test-parallel: ## Full parallel execution ({system_info['optimal_workers']} workers)
\t@echo "$(BLUE)⚡ Running parallel tests with {system_info['optimal_workers']} workers...$(NC)"
\t@$(PYTHON) -m pytest -c pytest_optimized.ini tests/ -n {system_info['optimal_workers']} --dist loadscope

test-changed: ## Test only changed/failed tests
\t@echo "$(BLUE)🎯 Running changed/failed tests...$(NC)"
\t@$(PYTHON) -m pytest -c pytest_optimized.ini --lf --ff -x

test-profile: ## Profile test performance
\t@echo "$(BLUE)📊 Profiling test performance...$(NC)"
\t@$(PYTHON) -m pytest -c pytest_optimized.ini tests/ --durations=20 --profile-svg

test-memory: ## Memory-optimized testing for low-resource environments
\t@echo "$(BLUE)💾 Running memory-optimized tests...$(NC)"
\t@$(PYTHON) -m pytest -c pytest_optimized.ini tests/ -n 2 --dist loadscope -m "not expensive"

benchmark-tests: ## Benchmark test suite performance
\t@echo "$(BLUE)🏃 Benchmarking test performance...$(NC)"
\t@$(PYTHON) scripts/test_performance_optimizer.py --benchmark
"""


def main():
    """Main entry point for test performance optimization."""
    optimizer = TestPerformanceOptimizer()
    
    print("🚀 AI System Test Performance Optimizer")
    print("=" * 50)
    
    # Analyze system
    system_info = optimizer.analyze_system_resources()
    print(f"💻 System Analysis:")
    print(f"   CPU Cores: {system_info['cpu_count']}")
    print(f"   Memory: {system_info['memory_gb']}GB")
    print(f"   Optimal Workers: {system_info['optimal_workers']}")
    
    # Create optimized configuration
    config_file = optimizer.create_optimized_pytest_config()
    print(f"⚙️  Created optimized config: {config_file}")
    
    # Generate recommendations
    recommendations = optimizer.generate_optimization_recommendations()
    print(f"\n📋 Optimization Recommendations:")
    for rec in recommendations:
        print(f"   {rec}")
    
    # Show test strategies
    strategies = optimizer.create_test_selection_strategies()
    print(f"\n🎯 Available Test Strategies:")
    for name, command in strategies.items():
        print(f"   {name:15} → pytest {command}")
    
    print(f"\n✅ Test suite optimization complete!")
    print(f"💡 Next steps:")
    print(f"   1. Run: make test-ultra-fast (quick validation)")
    print(f"   2. Run: make test-parallel (full suite)")
    print(f"   3. Monitor: tail -f test_performance_results.json")


if __name__ == "__main__":
    main()