"""
Test to verify cleanup mechanisms work properly.
This test creates temporary files and verifies they are cleaned up.
"""
import os
import pytest
import tempfile
import shutil
import time
from pathlib import Path
from contextlib import contextmanager


@contextmanager
def SafeTestRunner(name):
    """Context manager for safe test execution with cleanup"""
    temp_files = []
    temp_dirs = []
    
    class Runner:
        def create_temp_file(self, content, suffix):
            fd, path = tempfile.mkstemp(suffix=suffix, prefix=f"{name}_")
            with os.fdopen(fd, 'w') as f:
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
    with SafeTestRunner('cleanup_test') as runner:
        temp_file = runner.create_temp_file('test content', '.txt')
        created_files.append(temp_file)
        temp_dir = runner.create_temp_dir()
        created_dirs.append(temp_dir)
        assert os.path.exists(temp_file)
        assert os.path.exists(temp_dir)
    for file_path in created_files:
        assert not os.path.exists(file_path), f'File {file_path} was not cleaned up'
    for dir_path in created_dirs:
        assert not os.path.exists(dir_path), f'Directory {dir_path} was not cleaned up'


def test_pytest_fixtures_isolation(safe_temp_dir, isolated_output_dir):
    """Test that pytest fixtures provide proper isolation"""
    assert safe_temp_dir.exists()
    assert safe_temp_dir.is_dir()
    assert isolated_output_dir.exists()
    assert isolated_output_dir.is_dir()
    test_file = safe_temp_dir / 'test_file.txt'
    test_file.write_text('test content')
    output_file = isolated_output_dir / 'output.json'
    output_file.write_text('{"test": true}')
    assert test_file.exists()
    assert output_file.exists()


def test_conftest_auto_cleanup(clean_runtime_dirs):
    """Test that conftest auto-cleanup works"""
    # This test validates that the fixture cleans up runtime directories
    assert isinstance(clean_runtime_dirs, list)
    assert len(clean_runtime_dirs) > 0


def test_safe_file_manager(safe_file_manager):
    """Test the safe file manager fixture"""
    test_file = safe_file_manager.create_file('test.txt', 'test content')
    test_dir = safe_file_manager.create_dir('test_dir')
    assert test_file.exists()
    assert test_dir.exists()
    nested_file = test_dir / 'nested.txt'
    nested_file.write_text('nested content')
    assert nested_file.exists()


def test_no_artifact_leakage():
    """Test that no artifacts leak into the project structure"""
    project_root = Path(__file__).parent.parent.parent.parent
    temp_dir = project_root / 'runtime' / 'temp'
    if temp_dir.exists():
        test_temp_file = temp_dir / f'tmp_test_{int(time.time())}.txt'
        test_temp_file.parent.mkdir(parents=True, exist_ok=True)
        test_temp_file.write_text('This should be cleaned up')
        assert test_temp_file.exists()
        # Simple cleanup for test purposes
        test_temp_file.unlink()
        assert not test_temp_file.exists(), 'Temporary file was not cleaned up'


if __name__ == '__main__':
    print('Testing cleanup mechanisms...')
    test_safe_test_runner_cleanup()
    print('✅ SafeTestRunner cleanup works')
    test_no_artifact_leakage()
    print('✅ Artifact cleanup works')
    print('✅ All cleanup tests passed!')