#!/usr/bin/env python3
"""
Test cases for the Utility Function Consolidator
"""

import ast
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the scripts directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from utility_consolidator import UtilityConsolidator, FunctionVisitor


class TestUtilityConsolidator(unittest.TestCase):
    """Test cases for UtilityConsolidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.consolidator = UtilityConsolidator()
        
    def test_init(self):
        """Test UtilityConsolidator initialization"""
        self.assertEqual(self.consolidator.src_path, Path("src"))
        self.assertEqual(self.consolidator.utils_path, Path("src/infrastructure/utils"))
        self.assertEqual(self.consolidator.consolidated_modules, [])
        self.assertEqual(self.consolidator.files_modified, [])
        self.assertEqual(self.consolidator.functions_consolidated, 0)
    
    def test_generate_report(self):
        """Test report generation"""
        # Add some test data
        self.consolidator.files_modified = ["file1.py", "file2.py"]
        self.consolidator.functions_consolidated = 5
        
        report = self.consolidator.generate_report()
        
        self.assertIn("Utility Function Consolidation Report", report)
        self.assertIn("Files Modified:** 2", report)
        self.assertIn("Import Replacements:** 5", report)
        self.assertIn("✅ COMPLETED", report)


class TestFunctionVisitor(unittest.TestCase):
    """Test cases for FunctionVisitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.utility_functions = {'validate_email', 'load_config', 'setup_logging'}
        self.visitor = FunctionVisitor(self.utility_functions)
    
    def test_init(self):
        """Test FunctionVisitor initialization"""
        self.assertEqual(self.visitor.utility_functions, self.utility_functions)
        self.assertEqual(self.visitor.utility_functions_found, [])
    
    def test_visit_function_def_utility_function(self):
        """Test visiting a utility function definition"""
        # Create a simple function AST
        code = '''
def validate_email(email_str: str) -> bool:
    """Validate email address format"""
    return '@' in email_str
'''
        tree = ast.parse(code)
        self.visitor.visit(tree)
        
        # Should find the validate_email function
        self.assertEqual(len(self.visitor.utility_functions_found), 1)
        
        found_func = self.visitor.utility_functions_found[0]
        self.assertEqual(found_func['name'], 'validate_email')
        self.assertEqual(found_func['line'], 2)  # Line number where function starts
        self.assertIn('email_str', found_func['args'])
    
    def test_visit_function_def_non_utility_function(self):
        """Test visiting a non-utility function definition"""
        # Create a function that's not a utility function
        code = '''
def some_other_function():
    """Not a utility function"""
    pass
'''
        tree = ast.parse(code)
        self.visitor.visit(tree)
        
        # Should not find any utility functions
        self.assertEqual(len(self.visitor.utility_functions_found), 0)
    
    def test_get_function_signature(self):
        """Test function signature generation"""
        code = '''
def load_config(path: str, default=None) -> dict:
    return {}
'''
        tree = ast.parse(code)
        func_node = tree.body[0]  # Get the function node
        
        signature = self.visitor._get_function_signature(func_node)
        
        self.assertIn("load_config", signature)
        self.assertIn("path", signature)
        self.assertIn("default", signature)
        self.assertIn("defaults: 1", signature)  # One default argument


class TestUtilityConsolidatorIntegration(unittest.TestCase):
    """Integration tests for UtilityConsolidator"""
    
    def setUp(self):
        """Set up test fixtures with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.consolidator = UtilityConsolidator()
        # Override paths for testing
        self.consolidator.src_path = Path(self.test_dir) / "src"
        self.consolidator.utils_path = Path(self.test_dir) / "src" / "infrastructure" / "utils"
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('builtins.open', create=True)
    @patch('pathlib.Path.mkdir')
    def test_create_logging_utils(self, mock_mkdir, mock_open):
        """Test creating logging utilities module"""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = self.consolidator.create_logging_utils()
        
        # Check that the file was created
        expected_path = str(self.consolidator.utils_path / "logging_utils.py")
        self.assertEqual(result, expected_path)
        
        # Check that content was written
        mock_file.write.assert_called_once()
        written_content = mock_file.write.call_args[0][0]
        self.assertIn("setup_logging", written_content)
        self.assertIn("get_logger", written_content)
        self.assertIn("create_logger", written_content)
    
    def test_process_file_for_duplicates_no_duplicates(self):
        """Test processing a file with no duplicate functions"""
        # Create a test file with no utility functions
        test_file = Path(self.test_dir) / "test_file.py"
        test_content = '''
def regular_function():
    return "hello"

class TestClass:
    def method(self):
        pass
'''
        test_file.write_text(test_content)
        
        utility_functions = {'validate_email', 'load_config'}
        central_modules = {'validate_email': 'utils.validation'}
        
        result = self.consolidator._process_file_for_duplicates(
            test_file, utility_functions, central_modules
        )
        
        # Should return 0 as no duplicates found
        self.assertEqual(result, 0)
    
    def test_process_file_for_duplicates_with_duplicates(self):
        """Test processing a file with duplicate functions"""
        # Create a test file with utility functions
        test_file = Path(self.test_dir) / "test_file.py"
        test_content = '''
def validate_email(email: str) -> bool:
    return '@' in email

def load_config(path):
    return {}

def regular_function():
    return "hello"
'''
        test_file.write_text(test_content)
        
        utility_functions = {'validate_email', 'load_config'}
        central_modules = {
            'validate_email': 'utils.validation',
            'load_config': 'utils.config'
        }
        
        result = self.consolidator._process_file_for_duplicates(
            test_file, utility_functions, central_modules
        )
        
        # Should find and process 2 duplicate functions
        self.assertEqual(result, 2)
        
        # Check that the file was modified
        modified_content = test_file.read_text()
        self.assertIn("# REMOVED DUPLICATE:", modified_content)
        self.assertIn("from utils.validation import validate_email", modified_content)
        self.assertIn("from utils.config import load_config", modified_content)


if __name__ == '__main__':
    unittest.main()
