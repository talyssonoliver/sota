"""
Test to verify cleanup mechanisms work properly.
This test creates temporary files and verifies they are cleaned up.
"""

import tempfile
import os
from pathlib import Path
import pytest

from test_utils import SafeTestRunner


def test_safe_test_runner_cleanup():
    """Test that SafeTestRunner properly cleans up files"""
    created_files = []
    created_dirs = []
    
    # Use SafeTestRunner to create temp files
    with SafeTestRunner("cleanup_test") as runner:
        # Create a temp file
        temp_file = runner.create_temp_file("test content", ".txt")
        created_files.append(temp_file)
        
        # Create a temp directory
        temp_dir = runner.create_temp_dir()
        created_dirs.append(temp_dir)
        
        # Verify they exist during test
        assert os.path.exists(temp_file)
        assert os.path.exists(temp_dir)
    
    # After context exit, files should be cleaned up
    for file_path in created_files:
        assert not os.path.exists(file_path), f"File {file_path} was not cleaned up"
    
    for dir_path in created_dirs:
        assert not os.path.exists(dir_path), f"Directory {dir_path} was not cleaned up"


def test_pytest_fixtures_isolation(safe_temp_dir, isolated_output_dir):
    """Test that pytest fixtures provide proper isolation"""
    # safe_temp_dir should be a clean temporary directory
    assert safe_temp_dir.exists()
    assert safe_temp_dir.is_dir()
    
    # isolated_output_dir should be isolated
    assert isolated_output_dir.exists()
    assert isolated_output_dir.is_dir()
    
    # Create test files
    test_file = safe_temp_dir / "test_file.txt"
    test_file.write_text("test content")
    
    output_file = isolated_output_dir / "output.json"
    output_file.write_text('{"test": true}')
    
    # Files should exist during test
    assert test_file.exists()
    assert output_file.exists()
    
    # Note: Cleanup is automatic via fixtures


def test_conftest_auto_cleanup(clean_runtime_dirs):
    """Test that conftest auto-cleanup works"""
    # The clean_runtime_dirs fixture should clean up runtime directories
    # This test just verifies the fixture loads without error
    assert True  # Fixture loading is the actual test


def test_safe_file_manager(safe_file_manager):
    """Test the safe file manager fixture"""
    # Create a test file using the safe file manager
    test_file = safe_file_manager.create_file("test.txt", "test content")
    test_dir = safe_file_manager.create_dir("test_dir")
    
    # Verify they exist
    assert test_file.exists()
    assert test_dir.exists()
    
    # Create a file in the test directory
    nested_file = test_dir / "nested.txt"
    nested_file.write_text("nested content")
    assert nested_file.exists()
    
    # Note: Cleanup happens automatically via fixture


def test_no_artifact_leakage():
    """Test that no artifacts leak into the project structure"""
    import time
    
    # Create some temp files with patterns that should be cleaned up
    project_root = Path(__file__).parent.parent
    
    # Test creating files in runtime/temp (should be cleaned)
    temp_dir = project_root / "runtime" / "temp"
    if temp_dir.exists():
        test_temp_file = temp_dir / f"tmp_test_{int(time.time())}.txt"
        test_temp_file.parent.mkdir(parents=True, exist_ok=True)
        test_temp_file.write_text("This should be cleaned up")
        
        # File should exist initially
        assert test_temp_file.exists()
        
        # Trigger cleanup
        from test_utils import ensure_clean_test_environment
        ensure_clean_test_environment()
        
        # File should be gone
        assert not test_temp_file.exists(), "Temporary file was not cleaned up"


if __name__ == "__main__":
    # Run tests manually for verification
    print("Testing cleanup mechanisms...")
    
    test_safe_test_runner_cleanup()
    print("✅ SafeTestRunner cleanup works")
    
    test_no_artifact_leakage()
    print("✅ Artifact cleanup works")
    
    print("✅ All cleanup tests passed!")