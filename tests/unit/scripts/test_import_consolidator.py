#!/usr/bin/env python3
"""
Test suite for enhanced import consolidator script

Tests the import consolidation functionality with safety measures,
git integration, and sys.path.insert removal capabilities.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add scripts directory to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

try:
    from week2_day1_import_consolidator import ImportConsolidator
except ImportError as e:
    pytest.skip(f"Could not import import consolidator: {e}", allow_module_level=True)


class TestImportConsolidator:
    """Test suite for enhanced ImportConsolidator."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)
    
    @pytest.fixture
    def consolidator(self, temp_dir):
        """Create a consolidator instance for testing."""
        # Create src directory structure
        src_dir = temp_dir / "src" / "infrastructure" / "utils"
        src_dir.mkdir(parents=True)
        
        # Create a mock common_imports.py
        common_imports = src_dir / "common_imports.py"
        common_imports.write_text('''"""Mock common imports for testing."""
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

__all__ = ['json', 'logging', 'sys', 'Path', 'datetime', 'Dict', 'List', 'Optional']
''')
        
        # Change to temp directory for testing
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        consolidator = ImportConsolidator(
            verify_tests=False,  # Skip tests in unit tests
            create_backup=False,  # Skip git operations in unit tests
            verify_git_clean=False
        )
        consolidator.root_path = temp_dir
        consolidator.src_path = temp_dir / "src"
        
        yield consolidator
        
        # Restore original directory
        os.chdir(original_cwd)
    
    @pytest.fixture
    def sample_python_files(self, temp_dir):
        """Create sample Python files for testing."""
        src_dir = temp_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        files = {}
        
        # File with regular imports to consolidate
        files["regular_imports"] = src_dir / "regular_imports.py"
        files["regular_imports"].write_text('''"""Sample file with regular imports."""
import json
import logging
from pathlib import Path
from typing import Dict, List

def sample_function():
    path = Path("test")
    data = {"key": "value"}
    return json.dumps(data)
''')
        
        # File with sys.path.insert patterns
        files["path_inserts"] = src_dir / "path_inserts.py" 
        files["path_inserts"].write_text('''"""Sample file with sys.path.insert."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from some_module import something

def test_function():
    return sys.version
''')
        
        # File with mixed patterns
        files["mixed_patterns"] = src_dir / "mixed_patterns.py"
        files["mixed_patterns"].write_text('''"""Sample file with mixed import patterns."""
import sys
import json
from pathlib import Path
from typing import Dict

# sys.path manipulation
sys.path.insert(0, str(Path(__file__).parent))

def mixed_function():
    data = {"test": "value"}
    return json.dumps(data)
''')
        
        # File already using common imports
        files["already_consolidated"] = src_dir / "already_consolidated.py"
        files["already_consolidated"].write_text('''"""File already using common imports."""
from src.infrastructure.utils.common_imports import json, Path, Dict

def consolidated_function():
    return {"path": str(Path("test"))}
''')
        
        return files
    
    def test_initialization(self, temp_dir):
        """Test consolidator initialization with various options."""
        consolidator = ImportConsolidator(
            verify_tests=False,
            create_backup=True,
            verify_git_clean=True
        )
        
        assert consolidator.verify_tests is False
        assert consolidator.create_backup is True
        assert consolidator.verify_git_clean is True
        assert consolidator.max_workers == 4
        assert len(consolidator.path_insert_patterns) > 0
        assert len(consolidator.consolidation_targets) > 0
    
    def test_common_imports_validation(self, consolidator):
        """Test validation of common imports module."""
        # Should pass with our mock common_imports.py
        assert consolidator.validate_common_imports_available() is True
        assert len(consolidator.validation_errors) == 0
    
    def test_path_insert_removal(self, consolidator, sample_python_files):
        """Test sys.path.insert pattern removal."""
        file_path = sample_python_files["path_inserts"]
        
        with open(file_path, 'r') as f:
            original_content = f.read()
        
        # Test path insert removal
        modified_content, changes = consolidator._remove_path_inserts(
            original_content, file_path
        )
        
        # Should have removed sys.path.insert
        assert "sys.path.insert" not in modified_content
        assert changes > 0
        assert "# REMOVED: sys.path.insert" in modified_content
    
    def test_import_consolidation_detection(self, consolidator, sample_python_files):
        """Test detection of imports that can be consolidated."""
        # Test regular imports file
        result = consolidator.consolidate_file(sample_python_files["regular_imports"])
        
        assert result["success"] is True
        assert result["changes"] > 0
        assert "imports_added" in result
    
    def test_already_consolidated_file_skip(self, consolidator, sample_python_files):
        """Test that files already using common imports are skipped."""
        result = consolidator.consolidate_file(sample_python_files["already_consolidated"])
        
        assert result["success"] is True
        assert result["changes"] == 0
        assert result.get("reason") == "already_consolidated"
    
    def test_mixed_patterns_handling(self, consolidator, sample_python_files):
        """Test handling of files with both import consolidation and path inserts."""
        result = consolidator.consolidate_file(sample_python_files["mixed_patterns"])
        
        assert result["success"] is True
        assert result["changes"] > 0
        # Should handle both path inserts and regular imports
        assert "path_inserts_removed" in result
    
    def test_dry_run_mode(self, consolidator, sample_python_files):
        """Test that dry run mode doesn't modify files."""
        original_content = sample_python_files["regular_imports"].read_text()
        
        # Run in dry run mode
        results = consolidator.consolidate_all_files(dry_run=True)
        
        # File content should be unchanged
        assert sample_python_files["regular_imports"].read_text() == original_content
        
        # But should report what would be done
        assert results["total_files"] > 0
        assert results["files_processed"] > 0
    
    @patch('subprocess.run')
    def test_git_status_verification(self, mock_run, consolidator):
        """Test git status verification."""
        consolidator.verify_git_clean = True
        
        # Test clean git status
        mock_run.return_value = Mock(returncode=0, stdout="")
        assert consolidator.verify_git_status() is True
        
        # Test dirty git status
        mock_run.return_value = Mock(returncode=0, stdout="M file.py\n")
        assert consolidator.verify_git_status() is False
        
        # Test git not available
        mock_run.return_value = Mock(returncode=128, stderr="not a git repository")
        assert consolidator.verify_git_status() is True
    
    @patch('subprocess.run')
    def test_backup_branch_creation(self, mock_run, consolidator):
        """Test backup branch creation."""
        consolidator.create_backup = True
        
        # Mock successful branch creation
        mock_run.side_effect = [
            Mock(returncode=0, stdout="Switched to a new branch"),
            Mock(returncode=0, stdout="Switched to branch")
        ]
        
        assert consolidator.create_backup_branch() is True
        assert consolidator.backup_branch is not None
        assert "import-consolidation-backup-" in consolidator.backup_branch
    
    @patch('subprocess.run')
    def test_test_verification_before(self, mock_run, consolidator):
        """Test running tests before consolidation."""
        consolidator.verify_tests = True
        
        # Mock passing tests
        mock_run.return_value = Mock(
            returncode=0, 
            stdout="collected 100 items\n100 passed in 10.00s"
        )
        
        assert consolidator.run_tests_before() is True
        assert len(consolidator.test_failures_before) == 0
        
        # Mock failing tests
        mock_run.return_value = Mock(
            returncode=1,
            stdout="collected 100 items\n5 failed, 95 passed\nFAILED test_a.py::test_1\nFAILED test_b.py::test_2"
        )
        
        assert consolidator.run_tests_before() is True  # Still continues with pre-existing failures
        assert len(consolidator.test_failures_before) > 0
    
    @patch('subprocess.run')
    def test_test_verification_after(self, mock_run, consolidator):
        """Test running tests after consolidation."""
        consolidator.verify_tests = True
        consolidator.test_failures_before = ["test_a.py::test_1"]  # Pre-existing failure
        
        # Mock same failures (no new failures introduced)
        mock_run.return_value = Mock(
            returncode=1,
            stdout="collected 100 items\n1 failed, 99 passed\nFAILED test_a.py::test_1"
        )
        
        assert consolidator.run_tests_after() is True  # Same failures, OK
        
        # Mock new failures introduced
        mock_run.return_value = Mock(
            returncode=1,
            stdout="collected 100 items\n2 failed, 98 passed\nFAILED test_a.py::test_1\nFAILED test_b.py::test_2"
        )
        
        assert consolidator.run_tests_after() is False  # New failure introduced
    
    def test_error_handling_in_file_processing(self, consolidator, temp_dir):
        """Test error handling when processing files."""
        # Create a file that will cause an error
        bad_file = temp_dir / "src" / "bad_file.py"
        bad_file.write_text("invalid python syntax $$$ @@@")
        
        # Should handle errors gracefully
        result = consolidator.consolidate_file(bad_file)
        
        # Should not crash, might succeed or fail gracefully
        assert "success" in result
        if not result["success"]:
            assert "error" in result
    
    def test_thread_safety(self, consolidator, temp_dir):
        """Test thread safety of consolidation operations."""
        # Create multiple files for parallel processing
        src_dir = temp_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        files = []
        for i in range(10):
            file_path = src_dir / f"test_{i}.py"
            file_path.write_text(f'''
import json
import logging
from pathlib import Path

def func_{i}():
    return json.dumps({{"id": {i}}})
''')
            files.append(file_path)
        
        # Run consolidation (dry run to avoid actual changes)
        results = consolidator.consolidate_all_files(dry_run=True)
        
        # Should process all files without errors
        assert results["total_files"] >= len(files)
        assert results["files_processed"] >= len(files)
    
    def test_performance_with_large_codebase(self, consolidator, temp_dir):
        """Test performance with a larger number of files."""
        # Create many files to test performance
        src_dir = temp_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        for i in range(50):  # Create 50 files
            file_path = src_dir / f"module_{i}.py"
            file_path.write_text(f'''
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

class Module{i}:
    def __init__(self):
        self.data = {{"module_id": {i}}}
    
    def process(self):
        return json.dumps(self.data)
''')
        
        import time
        start_time = time.time()
        
        # Run consolidation in dry run mode
        results = consolidator.consolidate_all_files(dry_run=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete in reasonable time (less than 30 seconds for 50 files)
        assert execution_time < 30
        assert results["total_files"] >= 50
        assert results["success"] is True
    
    def test_regex_pattern_matching(self, consolidator):
        """Test regex patterns for sys.path.insert detection."""
        test_cases = [
            ("sys.path.insert(0, str(Path(__file__).parent))", True),
            ("sys.path.insert(0, str(project_root))", True),
            ("sys.path.insert(0, '/some/path')", True),
            ("sys.path.insert(0, \"src\")", True),
            ("# sys.path.insert(0, str(project_root))", False),  # Already commented
            ("print('sys.path.insert example')", False),  # Just a string
        ]
        
        import re
        for test_string, should_match in test_cases:
            matches_any = False
            for pattern in consolidator.path_insert_patterns:
                if re.search(pattern, test_string):
                    matches_any = True
                    break
            
            if should_match:
                assert matches_any, f"Pattern should match: {test_string}"
            else:
                assert not matches_any, f"Pattern should not match: {test_string}"


class TestImportConsolidatorIntegration:
    """Integration tests for import consolidator."""
    
    @pytest.fixture
    def integration_temp_dir(self):
        """Create a comprehensive test environment for integration testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_dir = Path(tmp_dir)
            
            # Create realistic src directory structure
            (test_dir / "src" / "core" / "workflows").mkdir(parents=True)
            (test_dir / "src" / "infrastructure" / "tools").mkdir(parents=True)
            (test_dir / "src" / "infrastructure" / "utils").mkdir(parents=True)
            (test_dir / "src" / "interfaces" / "cli").mkdir(parents=True)
            (test_dir / "tests" / "unit").mkdir(parents=True)
            
            # Create common imports module
            common_imports = test_dir / "src" / "infrastructure" / "utils" / "common_imports.py"
            common_imports.write_text('''"""Common imports for testing."""
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
''')
            
            # Create sample files with various import patterns
            files_content = {
                "src/core/workflows/example_workflow.py": '''
import json
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def workflow_function():
    return json.dumps({"status": "running"})
''',
                "src/infrastructure/tools/example_tool.py": '''
from pathlib import Path
import json
from typing import Dict, List

class ExampleTool:
    def __init__(self):
        self.config = {"name": "tool"}
    
    def process(self) -> Dict:
        return json.loads('{"result": "success"}')
''',
                "src/interfaces/cli/example_cli.py": '''
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def cli_main():
    print(json.dumps({"cli": "ready"}))
''',
                "tests/unit/test_example.py": '''
import json
from pathlib import Path
from typing import Dict
import unittest

class TestExample(unittest.TestCase):
    def test_json_processing(self):
        data = {"test": "value"}
        result = json.dumps(data)
        self.assertIsInstance(result, str)
'''
            }
            
            # Write all test files
            for file_path, content in files_content.items():
                full_path = test_dir / file_path
                full_path.write_text(content)
            
            yield test_dir
    
    def test_full_integration_dry_run(self, integration_temp_dir):
        """Test complete integration with realistic codebase structure."""
        original_cwd = os.getcwd()
        try:
            os.chdir(integration_temp_dir)
            
            consolidator = ImportConsolidator(
                verify_tests=False,
                create_backup=False,
                verify_git_clean=False
            )
            
            consolidator.root_path = integration_temp_dir
            consolidator.src_path = integration_temp_dir / "src"
            
            # Validate common imports
            assert consolidator.validate_common_imports_available() is True
            
            # Run full consolidation in dry run mode
            results = consolidator.consolidate_all_files(dry_run=True)
            
            # Should find files to process
            assert results["total_files"] > 0
            assert results["files_processed"] > 0
            
            # Should find imports to consolidate and path inserts to remove
            assert results["imports_consolidated"] > 0
            assert results["path_inserts_removed"] > 0
            
            # Should succeed
            assert results["success"] is True
            
        finally:
            os.chdir(original_cwd)
    
    def test_consolidation_preserves_functionality(self, integration_temp_dir):
        """Test that consolidation preserves code functionality."""
        original_cwd = os.getcwd()
        try:
            os.chdir(integration_temp_dir)
            
            # Read original files
            example_tool = integration_temp_dir / "src/infrastructure/tools/example_tool.py"
            original_content = example_tool.read_text()
            
            consolidator = ImportConsolidator(
                verify_tests=False,
                create_backup=False,
                verify_git_clean=False
            )
            consolidator.root_path = integration_temp_dir
            consolidator.src_path = integration_temp_dir / "src"
            
            # Process the file
            result = consolidator.consolidate_file(example_tool)
            
            if result["changes"] > 0:
                # Verify the file still has the necessary functionality
                new_content = example_tool.read_text()
                
                # Should still have the class definition
                assert "class ExampleTool:" in new_content
                # Should still have the methods
                assert "def process(self)" in new_content
                # Should have common imports instead of individual imports
                if "from src.infrastructure.utils.common_imports import" not in original_content:
                    assert "from src.infrastructure.utils.common_imports import" in new_content
            
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])