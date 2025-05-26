#!/usr/bin/env python3
"""
Test Suite for Step 4.4 — Register Agent Output

Comprehensive tests for the agent output registration system,
including metadata tracking, code extraction, and integration
with existing workflow components.
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.register_output import AgentOutputRegistry, AgentOutputRegistration


class TestAgentOutputRegistry(unittest.TestCase):
    """Test cases for the AgentOutputRegistry class."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.registry = AgentOutputRegistry(base_outputs_dir=self.test_dir)
        
        # Create sample output content
        self.sample_markdown_output = """# Backend Agent Output for BE-07

## Implementation Summary
Successfully implemented the customer service layer for the e-commerce platform.

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
        const { data, error } = await this.supabase
            .from('orders')
            .insert({
                customer_id: customerId,
                items: items,
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

## Database Schema Updates
```sql
-- filename: customer_schema.sql
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Next Steps
- Integration with frontend components
- Add comprehensive test coverage
- Deploy to staging environment
"""

        self.sample_qa_report = {
            "task_id": "BE-07",
            "agent": "qa",
            "timestamp": "2025-01-27T10:30:00Z",
            "tests_passed": 6,
            "tests_failed": 0,
            "coverage": 92.4,
            "issues": [],
            "status": "PASSED",
            "recommendations": [
                "Add error boundary tests",
                "Increase coverage to 95%"
            ]
        }
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_task_directory_creation(self):
        """Test that task directories are created properly."""
        task_dir = self.registry.get_task_directory("BE-07")
        
        self.assertTrue(task_dir.exists())
        self.assertEqual(task_dir.name, "BE-07")
        self.assertTrue(task_dir.is_dir())
    
    def test_register_markdown_output(self):
        """Test registering a markdown output file."""
        # Create source file
        source_file = Path(self.test_dir) / "source_output.md"
        source_file.write_text(self.sample_markdown_output)
        
        # Register the output
        registration = self.registry.register_output(
            task_id="BE-07",
            agent_id="backend",
            source_path=str(source_file),
            output_type="markdown"
        )
        
        # Verify registration
        self.assertEqual(registration.task_id, "BE-07")
        self.assertEqual(registration.agent_id, "backend")
        self.assertEqual(registration.output_type, "markdown")
        self.assertEqual(registration.status, "registered")
        self.assertTrue(registration.file_size > 0)
        
        # Verify file was copied to correct location
        expected_path = Path(self.test_dir) / "BE-07" / "output_backend.md"
        self.assertTrue(expected_path.exists())
        
        # Verify content
        copied_content = expected_path.read_text()
        self.assertEqual(copied_content, self.sample_markdown_output)
    
    def test_register_json_output(self):
        """Test registering a JSON output file."""
        # Create source file
        source_file = Path(self.test_dir) / "qa_report.json"
        source_file.write_text(json.dumps(self.sample_qa_report, indent=2))
        
        # Register the output
        registration = self.registry.register_output(
            task_id="BE-07",
            agent_id="qa",
            source_path=str(source_file),
            output_type="json"
        )
        
        # Verify registration
        self.assertEqual(registration.output_type, "json")
        
        # Verify file was copied with correct naming
        expected_path = Path(self.test_dir) / "BE-07" / "qa_report.json"
        self.assertTrue(expected_path.exists())
        
        # Verify JSON content
        loaded_data = json.loads(expected_path.read_text())
        self.assertEqual(loaded_data["task_id"], "BE-07")
        self.assertEqual(loaded_data["tests_passed"], 6)
    
    def test_code_extraction(self):
        """Test code block extraction from markdown output."""
        # Create source file
        source_file = Path(self.test_dir) / "backend_output.md"
        source_file.write_text(self.sample_markdown_output)
        
        # Register with code extraction
        registration = self.registry.register_output(
            task_id="BE-07",
            agent_id="backend",
            source_path=str(source_file),
            output_type="markdown",
            extract_code=True
        )
        
        # Verify code files were extracted
        self.assertTrue(len(registration.extracted_artifacts) > 0)
        
        # Check specific extracted files
        code_dir = Path(self.test_dir) / "BE-07" / "code"
        self.assertTrue(code_dir.exists())
          # Check for TypeScript files (note: paths are flattened by the registry)
        customer_service = code_dir / "customerService.ts"
        order_service = code_dir / "orderService.ts"
        customer_schema = code_dir / "customer_schema.sql"
        
        self.assertTrue(customer_service.exists())
        self.assertTrue(order_service.exists())
        self.assertTrue(customer_schema.exists())
        
        # Verify content of extracted files
        customer_content = customer_service.read_text()
        self.assertIn("export class CustomerService", customer_content)
        self.assertIn("async getCustomer", customer_content)
        
        order_content = order_service.read_text()
        self.assertIn("export class OrderService", order_content)
        self.assertIn("async createOrder", order_content)
        
        schema_content = customer_schema.read_text()
        self.assertIn("CREATE TABLE IF NOT EXISTS customers", schema_content)
    
    def test_status_file_update(self):
        """Test that status.json is updated correctly."""
        # Create and register an output
        source_file = Path(self.test_dir) / "backend_output.md"
        source_file.write_text(self.sample_markdown_output)
        
        registration = self.registry.register_output(
            task_id="BE-07",
            agent_id="backend",
            source_path=str(source_file),
            metadata={"version": "1.0", "reviewer": "tech_lead"}
        )
        
        # Check status file
        status_file = Path(self.test_dir) / "BE-07" / "status.json"
        self.assertTrue(status_file.exists())
        
        status_data = json.loads(status_file.read_text())
        
        # Verify status structure
        self.assertEqual(status_data["task_id"], "BE-07")
        self.assertIn("agent_outputs", status_data)
        self.assertIn("backend", status_data["agent_outputs"])
        
        backend_status = status_data["agent_outputs"]["backend"]
        self.assertEqual(backend_status["status"], "completed")
        self.assertEqual(backend_status["output_file"], "output_backend.md")
        self.assertTrue(backend_status["file_size"] > 0)
        self.assertEqual(backend_status["metadata"]["version"], "1.0")
        self.assertEqual(backend_status["metadata"]["reviewer"], "tech_lead")
    
    def test_registration_metadata_file(self):
        """Test that registration metadata is saved correctly."""
        # Create and register an output
        source_file = Path(self.test_dir) / "qa_output.json"
        source_file.write_text(json.dumps(self.sample_qa_report))
        
        registration = self.registry.register_output(
            task_id="BE-07",
            agent_id="qa",
            source_path=str(source_file),
            output_type="json"
        )
        
        # Check registration metadata file
        metadata_file = Path(self.test_dir) / "BE-07" / "registration_qa.json"
        self.assertTrue(metadata_file.exists())
        
        metadata = json.loads(metadata_file.read_text())
        self.assertEqual(metadata["task_id"], "BE-07")
        self.assertEqual(metadata["agent_id"], "qa")
        self.assertEqual(metadata["output_type"], "json")
        self.assertEqual(metadata["status"], "registered")
    
    def test_get_task_status(self):
        """Test retrieving task status."""
        # Register multiple outputs
        backend_file = Path(self.test_dir) / "backend_output.md"
        backend_file.write_text(self.sample_markdown_output)
        
        qa_file = Path(self.test_dir) / "qa_report.json"
        qa_file.write_text(json.dumps(self.sample_qa_report))
        
        self.registry.register_output("BE-07", "backend", str(backend_file))
        self.registry.register_output("BE-07", "qa", str(qa_file), output_type="json")
        
        # Get status
        status = self.registry.get_task_status("BE-07")
        
        self.assertEqual(status["task_id"], "BE-07")
        self.assertIn("backend", status["agent_outputs"])
        self.assertIn("qa", status["agent_outputs"])
        
        # Verify both agents show completed
        self.assertEqual(status["agent_outputs"]["backend"]["status"], "completed")
        self.assertEqual(status["agent_outputs"]["qa"]["status"], "completed")
    
    def test_list_task_outputs(self):
        """Test listing all outputs for a task."""
        # Register multiple outputs
        backend_file = Path(self.test_dir) / "backend_output.md"
        backend_file.write_text(self.sample_markdown_output)
        
        qa_file = Path(self.test_dir) / "qa_report.json"
        qa_file.write_text(json.dumps(self.sample_qa_report))
        
        self.registry.register_output("BE-07", "backend", str(backend_file))
        self.registry.register_output("BE-07", "qa", str(qa_file), output_type="json")
        
        # List outputs
        outputs = self.registry.list_task_outputs("BE-07")
        
        self.assertEqual(len(outputs), 1)  # Only output_* files
        self.assertTrue(any("output_backend.md" in output for output in outputs))
    
    def test_prepare_qa_input(self):
        """Test preparing input for QA agent."""
        # Register backend output with code extraction
        backend_file = Path(self.test_dir) / "backend_output.md"
        backend_file.write_text(self.sample_markdown_output)
        
        self.registry.register_output(
            "BE-07", "backend", str(backend_file), 
            extract_code=True
        )
        
        # Prepare QA input
        qa_input = self.registry.prepare_qa_input("BE-07")
        
        # Verify QA input structure
        self.assertEqual(qa_input["task_id"], "BE-07")
        self.assertIn("primary_outputs", qa_input)
        self.assertIn("code_artifacts", qa_input)
        self.assertIn("metadata", qa_input)
        
        # Verify code artifacts were included
        self.assertTrue(len(qa_input["code_artifacts"]) > 0)
        
        # Check for specific code files
        typescript_files = [
            artifact for artifact in qa_input["code_artifacts"]
            if artifact["language"] == "ts"
        ]
        self.assertTrue(len(typescript_files) >= 2)  # customerService.ts and orderService.ts
    
    def test_file_not_found_error(self):
        """Test error handling for non-existent source files."""
        with self.assertRaises(FileNotFoundError):
            self.registry.register_output(
                "BE-07", "backend", "/nonexistent/file.md"
            )
    
    def test_multiple_agent_workflow(self):
        """Test complete workflow with multiple agents."""
        # 1. Register backend output
        backend_file = Path(self.test_dir) / "backend_output.md"
        backend_file.write_text(self.sample_markdown_output)
        
        backend_reg = self.registry.register_output(
            "BE-07", "backend", str(backend_file), extract_code=True
        )
        
        # 2. Register QA output
        qa_file = Path(self.test_dir) / "qa_report.json"
        qa_file.write_text(json.dumps(self.sample_qa_report))
        
        qa_reg = self.registry.register_output(
            "BE-07", "qa", str(qa_file), output_type="json"
        )
        
        # 3. Check final status
        final_status = self.registry.get_task_status("BE-07")
        
        # Verify both agents completed
        self.assertIn("backend", final_status["agent_outputs"])
        self.assertIn("qa", final_status["agent_outputs"])
        
        # Verify code extraction happened
        self.assertTrue(len(backend_reg.extracted_artifacts) > 0)
        
        # Verify QA can access all necessary data
        qa_input = self.registry.prepare_qa_input("BE-07")
        self.assertTrue(len(qa_input["code_artifacts"]) > 0)
        self.assertTrue(len(qa_input["primary_outputs"]) > 0)


class TestRegistrationIntegration(unittest.TestCase):
    """Integration tests for registration with existing systems."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.registry = AgentOutputRegistry(base_outputs_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_integration_with_existing_task_structure(self):
        """Test integration with existing task declaration structure."""
        # Create existing task structure (simulating Step 4.1 output)
        task_dir = Path(self.test_dir) / "BE-07"
        task_dir.mkdir(exist_ok=True)
        
        # Create task declaration file (from Step 4.1)
        task_declaration = {
            "task_id": "BE-07",
            "title": "Implement Missing Service Functions",
            "description": "Add customerService and orderService implementations",
            "owner": "backend",
            "preparation_status": "READY_FOR_EXECUTION"
        }
        
        declaration_file = task_dir / "task_declaration.json"
        declaration_file.write_text(json.dumps(task_declaration, indent=2))
        
        # Create prompt file (from Step 4.2)
        prompt_file = task_dir / "prompt_backend.md"
        prompt_file.write_text("# Backend Agent Prompt for BE-07\n\nImplement service layer...")
        
        # Now register agent output
        output_content = "# Backend Implementation Complete\n\nServices implemented successfully."
        source_file = Path(self.test_dir) / "temp_output.md"
        source_file.write_text(output_content)
        
        registration = self.registry.register_output(
            "BE-07", "backend", str(source_file)
        )
        
        # Verify integration
        self.assertTrue(registration.status == "registered")
        
        # Check that existing files are preserved
        self.assertTrue(declaration_file.exists())
        self.assertTrue(prompt_file.exists())
        
        # Check that new files are added
        output_file = task_dir / "output_backend.md"
        status_file = task_dir / "status.json"
        
        self.assertTrue(output_file.exists())
        self.assertTrue(status_file.exists())
    
    @patch('orchestration.register_output.MemoryEngine')
    def test_memory_engine_integration(self, mock_memory_engine):
        """Test potential integration with memory engine."""
        # This test verifies that the registration system can work
        # with memory engine if needed in the future
        
        mock_engine = MagicMock()
        mock_memory_engine.return_value = mock_engine
        
        # Register an output
        source_file = Path(self.test_dir) / "output.md"
        source_file.write_text("# Test Output\n\nContent for memory engine.")
        
        registration = self.registry.register_output(
            "BE-07", "backend", str(source_file)
        )
        
        # Verify registration succeeded
        self.assertEqual(registration.status, "registered")
        
        # This shows how we could integrate with memory engine
        # for indexing registered outputs in the future


def run_step_4_4_tests():
    """Run all Step 4.4 tests and report results."""
    print("🧪 Running Step 4.4 — Register Agent Output Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAgentOutputRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestRegistrationIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report summary
    print(f"\n📊 Test Results Summary:")
    print(f"✅ Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests failed: {len(result.failures)}")
    print(f"⚠️  Tests errored: {len(result.errors)}")
    
    if result.failures:
        print(f"\n🔍 Failures:")
        for test, traceback in result.failures:
            print(f"   ❌ {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n🔍 Errors:")
        for test, traceback in result.errors:
            print(f"   ⚠️  {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_step_4_4_tests()
    sys.exit(0 if success else 1)
