import sys
import os
import pytest
import tempfile
import shutil
import psutil
import gc
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


# Configure pytest for parallel execution
def pytest_configure(config):
    """Configure pytest for optimal parallel execution"""
    # Add custom markers
    config.addinivalue_line("markers", "parallel: mark test as safe for parallel execution")
    config.addinivalue_line("markers", "sequential: mark test as requiring sequential execution")
    config.addinivalue_line("markers", "memory_intensive: mark test as memory intensive")
    config.addinivalue_line("markers", "io_bound: mark test as I/O bound")
    config.addinivalue_line("markers", "cpu_bound: mark test as CPU bound")


def pytest_collection_modifyitems(config, items):
    """Modify test collection for better parallel execution"""
    # Group tests by markers for better scheduling
    for item in items:
        # Add default parallel marker if no execution type is specified
        markers = [marker.name for marker in item.iter_markers()]
        if not any(m in markers for m in ['sequential', 'parallel', 'memory_intensive']):
            item.add_marker(pytest.mark.parallel)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment with memory management"""
    # Force garbage collection before tests start
    gc.collect()
    
    # Set environment variables for testing
    os.environ["TESTING"] = "1"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    
    yield
    
    # Cleanup after all tests
    gc.collect()


@pytest.fixture(scope="function", autouse=True)
def memory_management():
    """Automatic memory management for each test"""
    # Check memory before test
    initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    yield
    
    # Force garbage collection after test
    gc.collect()
    
    # Check for memory leaks (optional warning)
    final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    if memory_increase > 100:  # More than 100MB increase
        import warnings
        warnings.warn(f"Potential memory leak detected: {memory_increase:.1f}MB increase")


@pytest.fixture
def mock_expensive_operations():
    """Mock expensive operations for faster test execution"""
    mocks = {}
    
    # Mock time-consuming operations
    try:
        import time
        original_sleep = time.sleep
        time.sleep = Mock()
        mocks['time.sleep'] = original_sleep
    except ImportError:
        pass
    
    # Mock network operations  
    try:
        import requests
        original_get = requests.get
        requests.get = Mock()
        mocks['requests.get'] = original_get
    except ImportError:
        pass
    
    yield mocks
    
    # Restore original functions
    for mock_path, original_func in mocks.items():
        module_name, attr_name = mock_path.split('.')
        module = sys.modules.get(module_name)
        if module:
            setattr(module, attr_name, original_func)
import os
import pytest
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class SafeFileManager:
    """Safe file manager for test isolation"""
    
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.created_files = []
        self.created_dirs = []
        
    def create_file(self, name, content):
        file_path = self.base_dir / name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        self.created_files.append(file_path)
        return file_path
        
    def create_dir(self, name):
        dir_path = self.base_dir / name
        dir_path.mkdir(parents=True, exist_ok=True)
        self.created_dirs.append(dir_path)
        return dir_path
        
    def cleanup(self):
        for file_path in self.created_files:
            try:
                file_path.unlink()
            except OSError:
                pass
        for dir_path in self.created_dirs:
            try:
                shutil.rmtree(dir_path)
            except OSError:
                pass


@pytest.fixture
def safe_temp_dir():
    """Create a safe temporary directory for testing"""
    temp_dir = Path(tempfile.mkdtemp(prefix="safe_test_"))
    yield temp_dir
    try:
        shutil.rmtree(temp_dir)
    except OSError:
        pass


@pytest.fixture
def isolated_output_dir():
    """Create an isolated output directory for tests"""
    output_dir = Path(tempfile.mkdtemp(prefix="isolated_output_"))
    yield output_dir
    try:
        shutil.rmtree(output_dir)
    except OSError:
        pass


@pytest.fixture
def clean_runtime_dirs():
    """Fixture to ensure runtime directories are clean"""
    project_root = Path(__file__).parent.parent.parent.parent
    runtime_dirs = [
        project_root / 'runtime' / 'temp',
        project_root / 'runtime' / 'cache',
        project_root / 'test_outputs'
    ]
    
    # Clean up before test
    for dir_path in runtime_dirs:
        if dir_path.exists():
            for item in dir_path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
    
    yield runtime_dirs
    
    # Clean up after test
    for dir_path in runtime_dirs:
        if dir_path.exists():
            for item in dir_path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)


@pytest.fixture
def safe_file_manager():
    """Create a safe file manager for testing"""
    temp_dir = tempfile.mkdtemp(prefix="safe_manager_")
    manager = SafeFileManager(temp_dir)
    yield manager
    manager.cleanup()
    try:
        shutil.rmtree(temp_dir)
    except OSError:
        pass
