"""
Simple validation test to verify integration test framework is working.

This test validates that our integration test environment is properly set up
and can execute basic integration scenarios.
"""

import json

# Add project root to path
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestIntegrationFramework(unittest.TestCase):
    """Validation tests for integration test framework."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_basic_integration_setup(self):
        """Test that basic integration test setup works."""
        # Create test configuration
        config_data = {"test": "integration_framework", "status": "working"}

        config_file = Path(self.temp_dir) / "test_config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Verify file created and readable
        self.assertTrue(config_file.exists())

        with open(config_file, "r") as f:
            loaded_config = json.load(f)

        self.assertEqual(loaded_config["test"], "integration_framework")
        self.assertEqual(loaded_config["status"], "working")

    def test_mock_integration(self):
        """Test that mocking works properly in integration tests."""
        # Create a simple mock service
        mock_service = Mock()
        mock_service.get_status.return_value = {"status": "healthy"}
        mock_service.process_data.return_value = {"result": "success"}

        # Test mock interactions
        status = mock_service.get_status()
        self.assertEqual(status["status"], "healthy")

        result = mock_service.process_data("test_data")
        self.assertEqual(result["result"], "success")

        # Verify call tracking
        mock_service.get_status.assert_called_once()
        mock_service.process_data.assert_called_once_with("test_data")

    def test_integration_data_flow(self):
        """Test basic data flow between mocked components."""
        # Simulate data flow: Input -> Processing -> Output

        # Input component
        input_data = {
            "id": "TEST-001",
            "data": {"value": 42},
            "timestamp": "2024-01-01T00:00:00Z",
        }

        # Processing component (mocked)
        def process_data(data):
            return {
                "id": data["id"],
                "processed_value": data["data"]["value"] * 2,
                "status": "processed",
            }

        # Output component (mocked)
        def store_result(result):
            return {"stored_id": result["id"], "success": True}

        # Execute flow
        processed = process_data(input_data)
        stored = store_result(processed)

        # Verify flow
        self.assertEqual(processed["processed_value"], 84)
        self.assertEqual(processed["status"], "processed")
        self.assertTrue(stored["success"])
        self.assertEqual(stored["stored_id"], "TEST-001")

    def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""

        # Create service that can fail
        class TestService:
            def __init__(self, should_fail=False):
                self.should_fail = should_fail

            def operation(self):
                if self.should_fail:
                    raise Exception("Service operation failed")
                return {"result": "success"}

        # Test successful operation
        service = TestService(should_fail=False)
        result = service.operation()
        self.assertEqual(result["result"], "success")

        # Test failed operation
        failing_service = TestService(should_fail=True)
        with self.assertRaises(Exception) as context:
            failing_service.operation()

        self.assertIn("Service operation failed", str(context.exception))

    def test_concurrent_integration(self):
        """Test concurrent operations in integration tests."""
        import threading
        import time

        # Shared state
        results = []

        def worker_task(worker_id):
            """Simple worker task."""
            time.sleep(0.01)  # Simulate work
            results.append(f"worker_{worker_id}_completed")

        # Launch concurrent workers
        threads = []
        num_workers = 5

        for i in range(num_workers):
            thread = threading.Thread(target=worker_task, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=1)

        # Verify all workers completed
        self.assertEqual(len(results), num_workers)
        for i in range(num_workers):
            self.assertIn(f"worker_{i}_completed", results)

    def test_file_system_integration(self):
        """Test file system operations in integration tests."""
        # Create directory structure
        test_dir = Path(self.temp_dir) / "integration_test"
        test_dir.mkdir(parents=True, exist_ok=True)

        # Create test files
        test_files = ["file1.txt", "file2.json", "file3.yaml"]

        for filename in test_files:
            test_file = test_dir / filename
            with open(test_file, "w") as f:
                f.write(f"Content of {filename}")

        # Verify files exist
        for filename in test_files:
            test_file = test_dir / filename
            self.assertTrue(test_file.exists())

            with open(test_file, "r") as f:
                content = f.read()
                self.assertIn(filename, content)

        # Test directory listing
        created_files = list(test_dir.iterdir())
        self.assertEqual(len(created_files), 3)


if __name__ == "__main__":
    unittest.main()
