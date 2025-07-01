"""
Pytest Configuration Module

Provides dynamic configuration for pytest based on system resources,
test environment, and execution context.
"""

import os
import psutil
from typing import Dict, Any


class PytestConfig:
    """Dynamic pytest configuration based on system resources"""
    
    def __init__(self):
        self.cpu_count = psutil.cpu_count(logical=True)
        self.physical_cpu_count = psutil.cpu_count(logical=False) 
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.is_ci = os.getenv('CI', '').lower() in ('true', '1', 'yes')
        self.is_testing = os.getenv('TESTING', '').lower() in ('true', '1', 'yes')
        
    def get_parallel_config(self) -> Dict[str, Any]:
        """Get optimal parallel execution configuration"""
        if self.is_ci:
            # More conservative settings for CI environments
            return {
                'workers': min(2, self.cpu_count),
                'timeout': 300,
                'memory_per_worker_mb': 512
            }
        
        # Local development settings
        return {
            'workers': min(self.cpu_count, 8),
            'timeout': 600,
            'memory_per_worker_mb': min(1024, int(self.memory_gb * 1024 / 4))
        }
    
    def get_test_markers_config(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration for different test markers"""
        return {
            'unit': {
                'workers': min(self.cpu_count * 2, 16),
                'timeout': 60,
                'dist': 'loadscope',
                'forked': True
            },
            'integration': {
                'workers': min(self.cpu_count, 8),
                'timeout': 300,
                'dist': 'loadscope', 
                'forked': True
            },
            'memory': {
                'workers': min(2, self.cpu_count // 2),
                'timeout': 600,
                'dist': 'loadfile',
                'forked': True
            },
            'slow': {
                'workers': 1,
                'timeout': 1800,
                'dist': 'no',
                'forked': True
            },
            'external': {
                'workers': 1,
                'timeout': 300,
                'dist': 'no',
                'forked': True
            }
        }
    
    def get_addopts(self, test_type: str = 'default') -> str:
        """Get pytest addopts based on test type"""
        base_opts = [
            '-p no:warnings',
            '--tb=short',
            '--disable-warnings',
            '--durations=10',
            '--maxfail=30',
            '--strict-markers',
            '--timeout=300',
            '--timeout-method=thread'
        ]
        
        marker_config = self.get_test_markers_config()
        
        if test_type in marker_config:
            config = marker_config[test_type]
            
            if config['workers'] > 1:
                base_opts.extend([
                    f'-n {config["workers"]}',
                    f'--dist {config["dist"]}'
                ])
            
            if config['forked']:
                base_opts.append('--forked')
            
            base_opts.append(f'--timeout={config["timeout"]}')
        
        return ' '.join(base_opts)


# Global configuration instance
config = PytestConfig()

def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--test-type", 
        action="store", 
        default="default",
        help="Type of tests to run: unit, integration, memory, slow, external"
    )
    parser.addoption(
        "--max-workers",
        action="store", 
        type=int,
        default=0,
        help="Maximum number of worker processes"
    )
    parser.addoption(
        "--memory-limit", 
        action="store",
        type=int,
        default=0,
        help="Memory limit per worker in MB"
    )


def pytest_configure(config_obj):
    """Configure pytest dynamically"""
    test_type = config_obj.getoption("--test-type")
    max_workers = config_obj.getoption("--max-workers")
    
    # Override worker count if specified
    if max_workers > 0:
        os.environ['PYTEST_XDIST_WORKER_COUNT'] = str(max_workers)
    
    # Set environment variables for test execution
    os.environ['PYTEST_TEST_TYPE'] = test_type
    os.environ['PYTEST_CPU_COUNT'] = str(config.cpu_count)
    os.environ['PYTEST_MEMORY_GB'] = str(int(config.memory_gb))


def pytest_sessionstart(session):
    """Session start hook"""
    print(f"\n🔧 Pytest Configuration:")
    print(f"   CPU Cores: {config.cpu_count} (Physical: {config.physical_cpu_count})")
    print(f"   Memory: {config.memory_gb:.1f} GB")
    print(f"   CI Environment: {config.is_ci}")
    print(f"   Testing Mode: {config.is_testing}")
    
    parallel_config = config.get_parallel_config()
    print(f"   Suggested Workers: {parallel_config['workers']}")
    print(f"   Timeout: {parallel_config['timeout']}s")
    print(f"   Memory per Worker: {parallel_config['memory_per_worker_mb']}MB")


def pytest_sessionfinish(session, exitstatus):
    """Session finish hook"""
    if exitstatus == 0:
        print("\n✅ All tests completed successfully!")
    else:
        print(f"\n❌ Tests completed with exit status: {exitstatus}")
