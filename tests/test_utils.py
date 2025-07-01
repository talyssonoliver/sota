"""
Test utilities module - provides common testing utilities.
"""
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

def create_temp_file(content: str='', suffix: str='.py') -> str:
    """Create a temporary file with given content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name

def create_temp_dir() -> str:
    """Create a temporary directory."""
    return tempfile.mkdtemp()

def cleanup_temp_file(file_path: str) -> None:
    """Clean up a temporary file."""
    try:
        os.unlink(file_path)
    except OSError:
        pass

def cleanup_temp_dir(dir_path: str) -> None:
    """Clean up a temporary directory."""
    import shutil
    try:
        shutil.rmtree(dir_path)
    except OSError:
        pass

def mock_function(*args, **kwargs) -> Any:
    """Generic mock function that returns None."""
    return None

def assert_file_exists(file_path: str) -> bool:
    """Assert that a file exists."""
    return os.path.exists(file_path)

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent

def setup_test_environment():
    """Set up test environment with necessary paths."""
    project_root = get_project_root()
    src_dir = project_root / 'src'
    for path in [str(project_root), str(src_dir)]:
        if path not in sys.path:
            sys.path.insert(0, path)
setup_test_environment()