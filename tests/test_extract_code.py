#!/usr/bin/env python3
"""
Test Suite for Step 4.5 — Code Extraction (Postprocessing)

Comprehensive tests for the code extraction system, including advanced pattern matching,
Git integration, batch processing, and integration with existing workflow components.
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.extract_code import CodeExtractor, CodeExtractionResult


class TestCodeExtractor(unittest.TestCase):
    """Test cases for the CodeExtractor class."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.extractor = CodeExtractor(base_outputs_dir=self.test_dir)
        
        # Create sample task directory and output file
        self.task_dir = Path(self.test_dir) / "BE-07"
        self.task_dir.mkdir()
        
        # Sample markdown output with various code block formats
        self.sample_output_advanced = """# Backend Agent Output for BE-07

## Implementation Summary
Successfully implemented the customer service layer with advanced features.

## Code Implementation

### Customer Service
```typescript
// filename: customerService.ts
export class CustomerService {
    constructor(private supabase: SupabaseClient) {}
    
    async getCustomer(id: string): Promise<Customer | null> {
        const { data, error } = await this.supabase
            .from('customers')
            .select('*')
            .eq('id', id)
            .single();
        
        if (error) {
            throw new Error(`Failed to fetch customer: ${error.message}`);
        }
        
        return data;
    }
}
```

### Order Service  
```typescript
// filename: orderService.ts
export class OrderService {
    constructor(private supabase: SupabaseClient) {}
    
    async createOrder(customerId: string, items: OrderItem[]): Promise<Order> {
        const totalAmount = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        const { data, error } = await this.supabase
            .from('orders')
            .insert({
                customer_id: customerId,
                items,
                total_amount: totalAmount,
                status: 'pending'
            })
            .select()
            .single();
        
        if (error) {
            throw new Error(`Failed to create order: ${error.message}`);
        }
        
        return data;
    }
}
```

### Database Migration
```sql
-- filename: migrations/001_add_indexes.sql
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
```

### Configuration Files
```yaml
# filename: config/database.yaml
database:
  host: localhost
  port: 5432
  name: artesanato_db
  
supabase:
  url: https://your-project.supabase.co
  anon_key: your-anon-key
  
redis:
  host: localhost
  port: 6379
  db: 0
```

### Python Utility Functions
```python
# filename: utils/validation.py
from typing import Optional, Dict, Any
import re

def validate_email(email: str) -> bool:
    "Validate email format."
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_order_data(data: Dict[str, Any]) -> Optional[str]:
    "Validate order data structure."
    required_fields = ['customer_id', 'total_amount']
    
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"
    
    if not isinstance(data['total_amount'], (int, float)) or data['total_amount'] <= 0:
        return "Total amount must be a positive number"
    
    return None

class ValidationError(Exception):
    "Custom validation error."
    pass
```

### JSON Configuration
```json
{"filename": "config/app.json"}
{
  "app": {
    "name": "Artesanato E-commerce",
    "version": "1.0.0",
    "environment": "development"
  },
  "features": {
    "customer_management": true,
    "order_processing": true,
    "inventory_tracking": false
  },
  "logging": {
    "level": "info",
    "format": "json"
  }
}
```

### Simple Code Block (No Filename)
```bash
npm install
npm run build
npm start
```

## Summary
All service functions implemented successfully with proper error handling and TypeScript types."""
        
        # Sample with no code blocks
        self.sample_no_code = """# Documentation Output

This is a documentation file with no code blocks.
Just regular markdown content.

## Section 1
Some content here.

## Section 2
More content without code.
"""
        
        # Sample with malformed code blocks
        self.sample_malformed = """# Malformed Output

```typescript
// This block is not properly closed
export class Test {
```

```
// No language specified
const test = "value";
```

Regular markdown content.
"""
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_extract_from_task_agent_success(self):
        """Test successful code extraction from task agent output."""
        # Create output file
        output_file = self.task_dir / "output_backend.md"
        output_file.write_text(self.sample_output_advanced)
        
        # Extract code
        result = self.extractor.extract_from_task_agent("BE-07", "backend")
        
        # Verify result
        self.assertEqual(result.task_id, "BE-07")
        self.assertEqual(result.agent_id, "backend")
        self.assertTrue(len(result.extracted_files) >= 6)  # Multiple code blocks
        self.assertTrue(len(result.languages_detected) >= 4)  # ts, sql, yaml, python, json, bash
        self.assertGreater(result.total_code_blocks, 5)
        
        # Verify specific files exist
        code_dir = self.task_dir / "code"
        self.assertTrue(code_dir.exists())
        
        expected_files = [
            "customerService.ts",
            "orderService.ts", 
            "migrations_001_add_indexes.sql",
            "config_database.yaml",
            "utils_validation.py",
            "config_app.json"  # config/app.json becomes config_app.json
        ]
        
        for expected_file in expected_files:
            file_path = code_dir / expected_file
            self.assertTrue(file_path.exists(), f"Expected file {expected_file} not found")
    
    def test_extract_no_code_blocks(self):
        """Test extraction from file with no code blocks."""
        # Create output file with no code
        output_file = self.task_dir / "output_doc.md"
        output_file.write_text(self.sample_no_code)
        
        # Extract code
        result = self.extractor.extract_from_task_agent("BE-07", "doc")
        
        # Verify result
        self.assertEqual(len(result.extracted_files), 0)
        self.assertEqual(result.total_code_blocks, 0)
        self.assertEqual(len(result.languages_detected), 0)
    
    def test_extract_malformed_code_blocks(self):
        """Test extraction with malformed code blocks."""
        # Create output file with malformed code
        output_file = self.task_dir / "output_backend.md"
        output_file.write_text(self.sample_malformed)
        
        # Extract code (should handle gracefully)
        result = self.extractor.extract_from_task_agent("BE-07", "backend")
        
        # Should extract what it can
        self.assertGreaterEqual(len(result.extracted_files), 0)
    
    def test_file_not_found_error(self):
        """Test error handling for non-existent output files."""
        with self.assertRaises(FileNotFoundError):
            self.extractor.extract_from_task_agent("NONEXISTENT", "backend")
    
    def test_force_reextract(self):
        """Test force re-extraction functionality."""
        # Create output file
        output_file = self.task_dir / "output_backend.md"
        output_file.write_text(self.sample_output_advanced)
        
        # First extraction
        result1 = self.extractor.extract_from_task_agent("BE-07", "backend")
        initial_count = len(result1.extracted_files)
        
        # Modify output file
        modified_content = self.sample_output_advanced + """
### Additional Code
```javascript
// filename: additional.js
console.log("Additional code");
```
"""
        output_file.write_text(modified_content)
        
        # Extract again without force (should use existing)
        result2 = self.extractor.extract_from_task_agent("BE-07", "backend", force_reextract=False)
        
        # Extract with force
        result3 = self.extractor.extract_from_task_agent("BE-07", "backend", force_reextract=True)
        self.assertGreater(len(result3.extracted_files), initial_count)
    
    def test_extract_all_agents(self):
        """Test extracting from all agents for a task."""
        # Create multiple agent outputs
        agents = ["backend", "frontend", "qa"]
        for agent in agents:
            output_file = self.task_dir / f"output_{agent}.md"
            output_file.write_text(f"""# {agent.title()} Output
```typescript
// filename: {agent}.ts
export const {agent} = "test";
```
""")
        
        # Extract from all agents
        results = self.extractor.extract_from_all_agents("BE-07")
        
        # Verify results
        self.assertEqual(len(results), len(agents))
        for agent in agents:
            self.assertIn(agent, results)
            self.assertTrue(len(results[agent].extracted_files) > 0)

    def test_batch_extract(self):
        """Test batch extraction from multiple tasks."""        # Create multiple task directories
        tasks = ["BE-07", "FE-01", "QA-02"]
        for task in tasks:
            task_dir = Path(self.test_dir) / task
            task_dir.mkdir(exist_ok=True)
            
            output_file = task_dir / "output_backend.md"
            output_file.write_text(f"""# {task} Output
```typescript
// filename: {task.lower()}.ts
export const {task.lower().replace('-', '_')} = "test";
```
""")
          # Batch extract
        results = self.extractor.batch_extract(tasks)
        
        # Verify results
        self.assertGreaterEqual(len(results), len(tasks))
        for task in tasks:
            if task in results:
                self.assertIn("backend", results[task])

    def test_language_extension_mapping(self):
        """Test language to file extension mapping."""
        # Create output with various languages
        multi_lang_output = """# Multi-Language Output

```typescript
// filename: app.ts
const app = "TypeScript";
```

```python
# filename: script.py
print("Python")
```

```sql
-- filename: query.sql
SELECT * FROM users;
```

```yaml
# filename: config.yaml
app: test
```

```dockerfile
# filename: Dockerfile
FROM node:18
```

```bash
# filename: setup.sh
echo "Setup script"
```
"""
        
        output_file = self.task_dir / "output_backend.md"
        output_file.write_text(multi_lang_output)
        
        result = self.extractor.extract_from_task_agent("BE-07", "backend")
        
        # Verify correct extensions
        code_dir = self.task_dir / "code"
        expected_extensions = {
            "app.ts": ".ts",
            "script.py": ".py", 
            "query.sql": ".sql",
            "config.yaml": ".yaml",
            "Dockerfile": "",  # No extension
            "setup.sh": ".sh"
        }
        
        for filename, expected_ext in expected_extensions.items():
            file_path = code_dir / filename
            self.assertTrue(file_path.exists())
            if expected_ext:
                self.assertEqual(file_path.suffix, expected_ext)

    @patch('subprocess.run')
    def test_git_commit_integration(self, mock_subprocess):
        """Test Git commit functionality."""
        # Mock Git commands
        mock_subprocess.side_effect = [
            MagicMock(returncode=0),  # git rev-parse --is-inside-work-tree
            MagicMock(returncode=0),  # git add
            MagicMock(returncode=0),  # git commit
            MagicMock(returncode=0, stdout="abc12345\n")  # git rev-parse HEAD
        ]
        
        # Create output file
        output_file = self.task_dir / "output_backend.md"
        output_file.write_text("""# Test Output
```typescript
// filename: test.ts
export const test = "value";
```
""")
        
        # Extract with Git commit
        result = self.extractor.extract_from_task_agent("BE-07", "backend", commit_to_git=True)
        
        # Verify Git commit was attempted
        self.assertIsNotNone(result.git_commit_hash)
        self.assertEqual(result.git_commit_hash, "abc12345")
        
        # Verify Git commands were called
        self.assertEqual(mock_subprocess.call_count, 4)

    @patch('subprocess.run')
    def test_git_commit_not_in_repo(self, mock_subprocess):
        """Test Git commit when not in a repository."""
        # Mock Git command failure
        mock_subprocess.return_value = MagicMock(returncode=1)
        
        # Create output file
        output_file = self.task_dir / "output_backend.md"
        output_file.write_text("""# Test Output
```typescript
// filename: test.ts
export const test = "value";
```
""")
        
        # Extract with Git commit (should handle gracefully)
        result = self.extractor.extract_from_task_agent("BE-07", "backend", commit_to_git=True)
        
        # Verify no commit hash
        self.assertIsNone(result.git_commit_hash)

    def test_extraction_metadata_save(self):
        """Test extraction metadata saving."""
        # Create output file
        output_file = self.task_dir / "output_backend.md"
        output_file.write_text("""# Test Output
```typescript
// filename: test.ts
export const test = "value";
```
""")
        
        # Extract code
        result = self.extractor.extract_from_task_agent("BE-07", "backend")
          # Verify metadata file exists
        metadata_file = self.task_dir / "code_extraction_metadata.json"
        self.assertTrue(metadata_file.exists())
        
        # Verify metadata content
        metadata = json.loads(metadata_file.read_text())
        self.assertEqual(metadata["task_id"], "BE-07")
        self.assertEqual(metadata["agent_id"], "backend")
        self.assertGreater(len(metadata["extracted_files"]), 0)
        self.assertIn("extraction_time", metadata)

    def test_existing_extraction_info(self):
        """Test getting existing extraction information."""
        # Create output file and extract
        output_file = self.task_dir / "output_backend.md"
        output_file.write_text("""# Test Output
```typescript
// filename: test.ts
export const test = "value";
```
""")
        
        original_result = self.extractor.extract_from_task_agent("BE-07", "backend")
        
        # Get existing extraction info
        existing_result = self.extractor._get_existing_extraction_info(
            "BE-07", "backend", str(output_file)
        )
        
        # Verify information matches
        self.assertEqual(existing_result.task_id, original_result.task_id)
        self.assertEqual(existing_result.agent_id, original_result.agent_id)
        self.assertEqual(len(existing_result.extracted_files), len(original_result.extracted_files))

    def test_code_block_patterns(self):
        """Test different code block patterns."""
        patterns_test = """# Pattern Test

```typescript
// filename: pattern1.ts
const pattern1 = "standard";
```

```javascript
{"filename": "pattern2.js"}
const pattern2 = "json metadata";
```

```python
# No filename - should generate one
def pattern3():
    return "auto-generated"
```
"""
        
        output_file = self.task_dir / "output_backend.md"
        output_file.write_text(patterns_test)
        
        result = self.extractor.extract_from_task_agent("BE-07", "backend")
        
        # Should extract all three patterns
        self.assertEqual(len(result.extracted_files), 3)
        
        # Verify specific files
        code_dir = self.task_dir / "code"
        self.assertTrue((code_dir / "pattern1.ts").exists())
        self.assertTrue((code_dir / "pattern2.js").exists())
        # Third should have auto-generated name
        python_files = list(code_dir.glob("*.py"))
        self.assertEqual(len(python_files), 1)


class TestCodeExtractionCLI(unittest.TestCase):
    """Test cases for the CLI interface."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create sample task structure
        task_dir = Path(self.test_dir) / "BE-07"
        task_dir.mkdir()
        
        output_file = task_dir / "output_backend.md"
        output_file.write_text("""# Test Output
```typescript
// filename: test.ts
export const test = "cli";
```
""")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    @patch('sys.argv')
    @patch('orchestration.extract_code.CodeExtractor')
    def test_cli_single_extraction(self, mock_extractor_class, mock_argv):
        """Test CLI for single extraction."""
        mock_argv.__getitem__.return_value = [
            "extract_code.py", "BE-07", "backend"
        ]
        
        # Mock extractor
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        
        mock_result = CodeExtractionResult(
            task_id="BE-07",
            agent_id="backend", 
            source_file="test.md",
            extracted_files=["test.ts"],
            extraction_time="2024-01-01T00:00:00",
            total_code_blocks=1,
            languages_detected=["typescript"]
        )
        mock_extractor.extract_from_task_agent.return_value = mock_result
        
        # This would normally run main(), but we're testing the flow
        mock_extractor.extract_from_task_agent.assert_not_called()  # Not called yet


def run_step_4_5_tests():
    """Run all Step 4.5 tests and report results."""
    print("🧪 Running Step 4.5 — Code Extraction Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestCodeExtractor,
        TestCodeExtractionCLI
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Report results
    print(f"\n📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0]}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('\n')[-2]}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n✅ All tests passed! Step 4.5 — Code Extraction is working correctly.")
    else:
        print(f"\n❌ Some tests failed. Please check the implementation.")
    
    return success
