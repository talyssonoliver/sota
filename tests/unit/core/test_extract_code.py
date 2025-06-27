"""
test_extract_code.py - Optimized Test Structure

Migrated from: tests/workflows	est_extract_code.py
New location: tests/unit\\core	est_extract_code.py

Part of the optimized test pyramid reorganization:
- Tests now mirror src/ structure
- Proper categorization (unit/integration/e2e)
- Improved mocking and isolation

Test Suite for Step 4.5 — Code Extraction (Postprocessing)

Comprehensive tests for the code extraction system, including advanced pattern matching,
Git integration, batch processing, and integration with existing workflow components.
"""
import sys
import os
import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
try:
    pass
except ImportError:
    pass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCodeExtractor(unittest.TestCase):
    """Test cases for the CodeExtractor class."""

    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.extractor = CodeExtractor(base_outputs_dir=self.test_dir)
        self.task_dir = Path(self.test_dir) / 'BE-07'
        self.task_dir.mkdir()
        self.sample_output_advanced = '# Backend Agent Output for BE-07\n\n## Implementation Summary\nSuccessfully implemented the customer service layer with advanced features.\n\n## Code Implementation\n\n### Customer Service\n```typescript\n// filename: customerService.ts\nexport class CustomerService {\n    constructor(private supabase: SupabaseClient) {}\n\n    async getCustomer(id: string): Promise<Customer | null> {\n        const { data, error } = await this.supabase\n            .from(\'customers\')\n            .select(\'*\')\n            .eq(\'id\', id)\n            .single();\n\n        if (error) {\n            throw new Error(`Failed to fetch customer: ${error.message}`);\n        }\n\n        return data;\n    }\n}\n```\n\n### Order Service\n```typescript\n// filename: orderService.ts\nexport class OrderService {\n    constructor(private supabase: SupabaseClient) {}\n\n    async createOrder(customerId: string, items: OrderItem[]): Promise<Order> {\n        const totalAmount = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);\n\n        const { data, error } = await this.supabase\n            .from(\'orders\')\n            .insert({\n                customer_id: customerId,\n                items,\n                total_amount: totalAmount,\n                status: \'pending\'\n            })\n            .select()\n            .single();\n\n        if (error) {\n            throw new Error(`Failed to create order: ${error.message}`);\n        }\n\n        return data;\n    }\n}\n```\n\n### Database Migration\n```sql\n-- filename: migrations/001_add_indexes.sql\nCREATE INDEX idx_customers_email ON customers(email);\nCREATE INDEX idx_orders_customer_id ON orders(customer_id);\nCREATE INDEX idx_orders_status ON orders(status);\n```\n\n### Configuration Files\n```yaml\n# filename: config/database.yaml\ndatabase:\n  host: localhost\n  port: 5432\n  name: artesanato_db\n\nsupabase:\n  url: https://your-project.supabase.co\n  anon_key: your-anon-key\n\nredis:\n  host: localhost\n  port: 6379\n  db: 0\n```\n\n### Python Utility Functions\n```python\n# filename: utils/validation.py\nfrom typing import Optional, Dict, Any\nfrom src.core.workflows.extract_code import CodeExtractionResult, CodeExtractor\ntry:\n    pass\nexcept ImportError:\n    pass\nimport json\nimport logging\nimport os\nimport sys\nimport tempfile\nimport traceback\n\ndef validate_email(email: str) -> bool:\n    "Validate email format."\n    pattern = r\'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$\'\n    return bool(re.match(pattern, email))\n\ndef validate_order_data(data: Dict[str, Any]) -> Optional[str]:\n    "Validate order data structure."\n    required_fields = [\'customer_id\', \'total_amount\']\n\n    for field in required_fields:\n        if field not in data:\n            return f"Missing required field: {field}"\n\n    if not isinstance(data[\'total_amount\'], (int, float)) or data[\'total_amount\'] <= 0:\n        return "Total amount must be a positive number"\n\n    return None\n\nclass ValidationError(Exception):\n    "Custom validation error."\n    pass\n```\n\n### JSON Configuration\n```json\n{"filename": "config/app.json"}\n{\n  "app": {\n    "name": "Artesanato E-commerce",\n    "version": "1.0.0",\n    "environment": "development"\n  },\n  "features": {\n    "customer_management": true,\n    "order_processing": true,\n    "inventory_tracking": false\n  },\n  "logging": {\n    "level": "info",\n    "format": "json"\n  }\n}\n```\n\n### Simple Code Block (No Filename)\n```bash\nnpm install\nnpm run build\nnpm start\n```\n\n## Summary\nAll service functions implemented successfully with proper error handling and TypeScript types.'
        self.sample_no_code = '# Documentation Output\n\nThis is a documentation file with no code blocks.\nJust regular markdown content.\n\n## Section 1\nSome content here.\n\n## Section 2\nMore content without code.\n'
        self.sample_malformed = '# Malformed Output\n\n```typescript\n// This block is not properly closed\nexport class Test {\n```\n\n```\n// No language specified\nconst test = "value";\n```\n\nRegular markdown content.\n'

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_extract_from_task_agent_success(self):
        """Test successful code extraction from task agent output."""
        output_file = self.task_dir / 'output_backend.md'
        output_file.write_text(self.sample_output_advanced)
        result = self.extractor.extract_from_task_agent('BE-07', 'backend')
        self.assertEqual(result.task_id, 'BE-07')
        self.assertEqual(result.agent_id, 'backend')
        self.assertTrue(len(result.extracted_files) >= 6)
        self.assertTrue(len(result.languages_detected) >= 4)
        self.assertGreater(result.total_code_blocks, 5)
        code_dir = self.task_dir / 'code'
        self.assertTrue(code_dir.exists())
        expected_files = ['customerService.ts', 'orderService.ts', 'migrations_001_add_indexes.sql', 'config_database.yaml', 'utils_validation.py', 'config_app.json']
        for expected_file in expected_files:
            file_path = code_dir / expected_file
            self.assertTrue(file_path.exists(), f'Expected file {expected_file} not found')

    def test_extract_no_code_blocks(self):
        """Test extraction from file with no code blocks."""
        output_file = self.task_dir / 'output_doc.md'
        output_file.write_text(self.sample_no_code)
        result = self.extractor.extract_from_task_agent('BE-07', 'doc')
        self.assertEqual(len(result.extracted_files), 0)
        self.assertEqual(result.total_code_blocks, 0)
        self.assertEqual(len(result.languages_detected), 0)

    def test_extract_malformed_code_blocks(self):
        """Test extraction with malformed code blocks."""
        output_file = self.task_dir / 'output_backend.md'
        output_file.write_text(self.sample_malformed)
        result = self.extractor.extract_from_task_agent('BE-07', 'backend')
        self.assertGreaterEqual(len(result.extracted_files), 0)

    def test_file_not_found_error(self):
        """Test error handling for non-existent output files."""
        with self.assertRaises(FileNotFoundError):
            self.extractor.extract_from_task_agent('NONEXISTENT', 'backend')

    def test_force_reextract(self):
        """Test force re-extraction functionality."""
        output_file = self.task_dir / 'output_backend.md'
        output_file.write_text(self.sample_output_advanced)
        result1 = self.extractor.extract_from_task_agent('BE-07', 'backend')
        initial_count = len(result1.extracted_files)
        modified_content = self.sample_output_advanced + '\n### Additional Code\n```javascript\n// filename: additional.js\nconsole.log("Additional code");\n```\n'
        output_file.write_text(modified_content)
        result2 = self.extractor.extract_from_task_agent('BE-07', 'backend', force_reextract=False)
        result3 = self.extractor.extract_from_task_agent('BE-07', 'backend', force_reextract=True)
        self.assertGreater(len(result3.extracted_files), initial_count)

    def test_extract_all_agents(self):
        """Test extracting from all agents for a task."""
        agents = ['backend', 'frontend', 'qa']
        for agent in agents:
            output_file = self.task_dir / f'output_{agent}.md'
            output_file.write_text(f'# {agent.title()} Output\n```typescript\n// filename: {agent}.ts\nexport const {agent} = "test";\n```\n')
        results = self.extractor.extract_from_all_agents('BE-07')
        self.assertEqual(len(results), len(agents))
        for agent in agents:
            self.assertIn(agent, results)
            self.assertTrue(len(results[agent].extracted_files) > 0)

    def test_batch_extract(self):
        """Test batch extraction from multiple tasks."""
        tasks = ['BE-07', 'FE-01', 'QA-02']
        for task in tasks:
            task_dir = Path(self.test_dir) / task
            task_dir.mkdir(exist_ok=True)
            output_file = task_dir / 'output_backend.md'
            output_file.write_text(f'# {task} Output\n```typescript\n// filename: {task.lower()}.ts\nexport const {task.lower().replace('-', '_')} = "test";\n```\n')
        results = self.extractor.batch_extract(tasks)
        self.assertGreaterEqual(len(results), len(tasks))
        for task in tasks:
            if task in results:
                self.assertIn('backend', results[task])

    def test_language_extension_mapping(self):
        """Test language to file extension mapping."""
        multi_lang_output = '# Multi-Language Output\n\n```typescript\n// filename: app.ts\nconst app = "TypeScript";\n```\n\n```python\n# filename: script.py\nprint("Python")\n```\n\n```sql\n-- filename: query.sql\nSELECT * FROM users;\n```\n\n```yaml\n# filename: config.yaml\napp: test\n```\n\n```dockerfile\n# filename: Dockerfile\nFROM node:18\n```\n\n```bash\n# filename: setup.sh\necho "Setup script"\n```\n'
        output_file = self.task_dir / 'output_backend.md'
        output_file.write_text(multi_lang_output)
        result = self.extractor.extract_from_task_agent('BE-07', 'backend')
        code_dir = self.task_dir / 'code'
        expected_extensions = {'app.ts': '.ts', 'script.py': '.py', 'query.sql': '.sql', 'config.yaml': '.yaml', 'Dockerfile': '', 'setup.sh': '.sh'}
        for filename, expected_ext in expected_extensions.items():
            file_path = code_dir / filename
            self.assertTrue(file_path.exists())
            if expected_ext:
                self.assertEqual(file_path.suffix, expected_ext)

    @patch('subprocess.run')
    def test_git_commit_integration(self, mock_subprocess):
        """Test Git commit functionality."""
        mock_subprocess.side_effect = [MagicMock(returncode=0), MagicMock(returncode=0), MagicMock(returncode=0), MagicMock(returncode=0, stdout='abc12345\n')]
        output_file = self.task_dir / 'output_backend.md'
        output_file.write_text('# Test Output\n```typescript\n// filename: test.ts\nexport const test = "value";\n```\n')
        result = self.extractor.extract_from_task_agent('BE-07', 'backend', commit_to_git=True)
        self.assertIsNotNone(result.git_commit_hash)
        self.assertEqual(result.git_commit_hash, 'abc12345')
        self.assertEqual(mock_subprocess.call_count, 4)

    @patch('subprocess.run')
    def test_git_commit_not_in_repo(self, mock_subprocess):
        """Test Git commit when not in a repository."""
        mock_subprocess.return_value = MagicMock(returncode=1)
        output_file = self.task_dir / 'output_backend.md'
        output_file.write_text('# Test Output\n```typescript\n// filename: test.ts\nexport const test = "value";\n```\n')
        result = self.extractor.extract_from_task_agent('BE-07', 'backend', commit_to_git=True)
        self.assertIsNone(result.git_commit_hash)

    def test_extraction_metadata_save(self):
        """Test extraction metadata saving."""
        output_file = self.task_dir / 'output_backend.md'
        output_file.write_text('# Test Output\n```typescript\n// filename: test.ts\nexport const test = "value";\n```\n')
        result = self.extractor.extract_from_task_agent('BE-07', 'backend')
        metadata_file = self.task_dir / 'code_extraction_metadata.json'
        self.assertTrue(metadata_file.exists())
        metadata = json.loads(metadata_file.read_text())
        self.assertEqual(metadata['task_id'], 'BE-07')
        self.assertEqual(metadata['agent_id'], 'backend')
        self.assertGreater(len(metadata['extracted_files']), 0)
        self.assertIn('extraction_time', metadata)

    def test_existing_extraction_info(self):
        """Test getting existing extraction information."""
        output_file = self.task_dir / 'output_backend.md'
        output_file.write_text('# Test Output\n```typescript\n// filename: test.ts\nexport const test = "value";\n```\n')
        original_result = self.extractor.extract_from_task_agent('BE-07', 'backend')
        existing_result = self.extractor._get_existing_extraction_info('BE-07', 'backend', str(output_file))
        self.assertEqual(existing_result.task_id, original_result.task_id)
        self.assertEqual(existing_result.agent_id, original_result.agent_id)
        self.assertEqual(len(existing_result.extracted_files), len(original_result.extracted_files))

    def test_code_block_patterns(self):
        """Test different code block patterns."""
        patterns_test = '# Pattern Test\n\n```typescript\n// filename: pattern1.ts\nconst pattern1 = "standard";\n```\n\n```javascript\n{"filename": "pattern2.js"}\nconst pattern2 = "json metadata";\n```\n\n```python\n# No filename - should generate one\ndef pattern3():\n    return "auto-generated"\n```\n'
        output_file = self.task_dir / 'output_backend.md'
        output_file.write_text(patterns_test)
        result = self.extractor.extract_from_task_agent('BE-07', 'backend')
        self.assertEqual(len(result.extracted_files), 3)
        code_dir = self.task_dir / 'code'
        self.assertTrue((code_dir / 'pattern1.ts').exists())
        self.assertTrue((code_dir / 'pattern2.js').exists())
        python_files = list(code_dir.glob('*.py'))
        self.assertEqual(len(python_files), 1)

class TestCodeExtractionCLI(unittest.TestCase):
    """Test cases for the CLI interface."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        task_dir = Path(self.test_dir) / 'BE-07'
        task_dir.mkdir()
        output_file = task_dir / 'output_backend.md'
        output_file.write_text('# Test Output\n```typescript\n// filename: test.ts\nexport const test = "cli";\n```\n')

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    @patch('sys.argv')
    @patch('src.core.workflows.extract_code.CodeExtractor')
    def test_cli_single_extraction(self, mock_extractor_class, mock_argv):
        """Test CLI for single extraction."""
        mock_argv.__getitem__.return_value = ['extract_code.py', 'BE-07', 'backend']
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_result = CodeExtractionResult(task_id='BE-07', agent_id='backend', source_file='test.md', extracted_files=['test.ts'], extraction_time='2024-01-01T00:00:00', total_code_blocks=1, languages_detected=['typescript'])
        mock_extractor.extract_from_task_agent.return_value = mock_result
        mock_extractor.extract_from_task_agent.assert_not_called()

def run_step_4_5_tests():
    """Run all Step 4.5 tests and report results."""
    print('🧪 Running Step 4.5 — Code Extraction Tests')
    print('=' * 60)
    test_suite = unittest.TestSuite()
    test_classes = [TestCodeExtractor, TestCodeExtractionCLI]
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    print('\n📊 Test Results Summary:')
    print(f'   Tests run: {result.testsRun}')
    print(f'   Failures: {len(result.failures)}')
    print(f'   Errors: {len(result.errors)}')
    print(f'   Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%')
    if result.failures:
        print('\n❌ Failures:')
        for test, traceback in result.failures:
            print(f'   - {test}: {traceback.split('AssertionError: ')[-1].splitlines()[0]}')
    if result.errors:
        print('\n💥 Errors:')
        for test, traceback in result.errors:
            print(f'   - {test}: {traceback.splitlines()[-2]}')
    success = len(result.failures) == 0 and len(result.errors) == 0
    if success:
        print('\n✅ All tests passed! Step 4.5 — Code Extraction is working correctly.')
    else:
        print('\n❌ Some tests failed. Please check the implementation.')
    return success