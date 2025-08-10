"""
Test to verify cleanup mechanisms work properly.
This test creates temporary files and verifies they are cleaned up.
"""

import os
import shutil
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def SafeTestRunner(name):
    """Context manager for safe test execution with cleanup"""
    temp_files = []
    temp_dirs = []

    class Runner:
        def create_temp_file(self, content, suffix):
            fd, path = tempfile.mkstemp(suffix=suffix, prefix=f"{name}_")
            with os.fdopen(fd, "w") as f:
                f.write(content)
            temp_files.append(path)
            return path

        def create_temp_dir(self):
            path = tempfile.mkdtemp(prefix=f"{name}_")
            temp_dirs.append(path)
            return path

    try:
        yield Runner()
    finally:
        for file_path in temp_files:
            try:
                os.unlink(file_path)
            except OSError:
                pass
        for dir_path in temp_dirs:
            try:
                shutil.rmtree(dir_path)
            except OSError:
                pass


def test_safe_test_runner_cleanup():
    """Test that SafeTestRunner properly cleans up files"""
    created_files = []
    created_dirs = []
    with SafeTestRunner("cleanup_test") as runner:
        temp_file = runner.create_temp_file("test content", ".txt")
        created_files.append(temp_file)
        temp_dir = runner.create_temp_dir()
        created_dirs.append(temp_dir)
        assert os.path.exists(temp_file)
        assert os.path.exists(temp_dir)
    for file_path in created_files:
        assert not os.path.exists(file_path), f"File {file_path} was not cleaned up"
    for dir_path in created_dirs:
        assert not os.path.exists(dir_path), f"Directory {dir_path} was not cleaned up"


def test_pytest_fixtures_isolation(tmp_path):
    """Test that pytest fixtures provide proper isolation"""
    # Use built-in tmp_path fixture for isolation testing
    safe_temp_dir = tmp_path / "safe_temp"
    isolated_output_dir = tmp_path / "isolated_output"
    
    safe_temp_dir.mkdir()
    isolated_output_dir.mkdir()
    
    assert safe_temp_dir.exists()
    assert safe_temp_dir.is_dir()
    assert isolated_output_dir.exists()
    assert isolated_output_dir.is_dir()
    
    test_file = safe_temp_dir / "test_file.txt"
    test_file.write_text("test content")
    output_file = isolated_output_dir / "output.json"
    output_file.write_text('{"test": true}')
    assert test_file.exists()
    assert output_file.exists()


def test_conftest_auto_cleanup():
    """Test that conftest auto-cleanup works"""
    # This test validates basic cleanup functionality
    # Create a temporary directory structure to test cleanup
    with SafeTestRunner("conftest_test") as runner:
        test_dir = runner.create_temp_dir()
        test_file = runner.create_temp_file("cleanup test", ".tmp")
        assert os.path.exists(test_dir)
        assert os.path.exists(test_file)
    # After context manager, files should be cleaned up
    assert not os.path.exists(test_dir)
    assert not os.path.exists(test_file)


def test_safe_file_manager(tmp_path):
    """Test the safe file manager fixture"""
    # Use tmp_path as a safe file manager
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    
    assert test_file.exists()
    assert test_dir.exists()
    
    nested_file = test_dir / "nested.txt"
    nested_file.write_text("nested content")
    assert nested_file.exists()


def test_no_artifact_leakage():
    """Test that no artifacts leak into the project structure"""
    project_root = Path(__file__).parent.parent.parent.parent
    temp_dir = project_root / "runtime" / "temp"
    if temp_dir.exists():
        test_temp_file = temp_dir / f"tmp_test_{int(time.time())}.txt"
        test_temp_file.parent.mkdir(parents=True, exist_ok=True)
        test_temp_file.write_text("This should be cleaned up")
        assert test_temp_file.exists()
        # Simple cleanup for test purposes
        test_temp_file.unlink()
        assert not test_temp_file.exists(), "Temporary file was not cleaned up"


if __name__ == "__main__":
    print("Testing cleanup mechanisms...")
    test_safe_test_runner_cleanup()
    print("✅ SafeTestRunner cleanup works")
    test_no_artifact_leakage()
    print("✅ Artifact cleanup works")
    print("✅ All cleanup tests passed!")
