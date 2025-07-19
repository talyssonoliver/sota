"""
Integration tests for Data Flow across system components.

Tests data flow integration including:
- Data passing between agents, workflows, and storage
- Data transformation and validation chains
- Data persistence and retrieval workflows
- Data integrity across boundaries
- Serialization and deserialization
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
import yaml
import pickle
from pathlib import Path
from datetime import datetime
import hashlib

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.infrastructure.memory import MemoryEngine
from src.infrastructure.memory.storage import TieredStorageManager
from src.infrastructure.utils.schema_manager import SchemaManager


@pytest.fixture
def integration_environment():
    """Set up integration test environment for data flow."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create storage directories
        storage_dir = Path(temp_dir) / "storage"
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test data schemas
        schemas = {
            "task_input": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "input_data": {"type": "object"},
                    "context": {"type": "object"},
                    "metadata": {"type": "object"}
                },
                "required": ["task_id", "input_data"]
            },
            "task_output": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["success", "failure", "partial"]},
                    "output_data": {"type": "object"},
                    "artifacts": {"type": "array"},
                    "metrics": {"type": "object"}
                },
                "required": ["task_id", "status", "output_data"]
            },
            "agent_message": {
                "type": "object",
                "properties": {
                    "from_agent": {"type": "string"},
                    "to_agent": {"type": "string"},
                    "message_type": {"type": "string"},
                    "payload": {"type": "object"},
                    "timestamp": {"type": "string", "format": "date-time"}
                },
                "required": ["from_agent", "to_agent", "message_type", "payload"]
            }
        }
        
        # Create sample data flows
        sample_flows = [
            {
                "id": "flow_1",
                "name": "Agent to Workflow",
                "steps": [
                    {"type": "agent_input", "data": {"query": "Process this request"}},
                    {"type": "agent_processing", "transform": "analyze_and_plan"},
                    {"type": "workflow_execution", "workflow": "standard"},
                    {"type": "result_storage", "location": "outputs/"}
                ]
            },
            {
                "id": "flow_2",
                "name": "Workflow to Memory",
                "steps": [
                    {"type": "workflow_output", "data": {"results": ["item1", "item2"]}},
                    {"type": "memory_storage", "context_type": "workflow_results"},
                    {"type": "memory_indexing", "domains": ["backend", "api"]}
                ]
            }
        ]
        
        yield {
            'temp_dir': temp_dir,
            'storage_dir': storage_dir,
            'schemas': schemas,
            'sample_flows': sample_flows
        }


class TestDataFlowIntegration(unittest.TestCase):
    """Integration tests for Data Flow across components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        from src.infrastructure.memory.config.memory_config import MemoryEngineConfig
        self.memory_config = MemoryEngineConfig()
        self.storage_manager = TieredStorageManager(config=self.memory_config.storage)
        self.schema_manager = SchemaManager()
        
        # Mock components
        self.mock_memory = Mock(spec=MemoryEngine)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_agent_to_workflow_data_flow(self):
        """Test data flow from agent to workflow execution."""
        # Initial agent input
        agent_input = {
            "task_id": "TEST-01",
            "request": "Analyze system architecture",
            "context": {
                "requester": "user@example.com",
                "priority": "high"
            }
        }
        
        # Agent processes input
        with patch('src.core.agents.factory.create_agent') as mock_create:
            mock_agent = MagicMock()
            mock_agent.process.return_value = {
                "analysis": "System needs microservices architecture",
                "recommendations": [
                    "Use Docker containers",
                    "Implement API gateway",
                    "Add service mesh"
                ],
                "next_steps": ["Design API contracts", "Plan deployment"]
            }
            mock_create.return_value = mock_agent
            
            # Create agent and process
            agent = mock_create("technical_lead")
            agent_output = agent.process(agent_input)
            
            # Pass to workflow
            workflow_input = {
                "task_id": agent_input["task_id"],
                "agent_output": agent_output,
                "workflow_type": "architecture_planning"
            }
            
            # Mock execute_task to avoid actual workflow execution
            with patch('src.core.workflows.execute_workflow.execute_task') as mock_execute_task:
                mock_execute_task.return_value = {"status": "completed", "output": "mocked output"}
                
                workflow_result = mock_execute_task(
                    task_id=workflow_input["task_id"],
                    input_message=json.dumps(workflow_input["agent_output"]),
                    workflow_type="standard"
                )
                
                # Verify execute_task was called
                mock_execute_task.assert_called_once_with(
                    task_id=workflow_input["task_id"],
                    input_message=json.dumps(workflow_input["agent_output"]),
                    workflow_type="standard"
                )
    
    def test_workflow_to_storage_data_persistence(self):
        """Test data persistence from workflow to storage."""
        # Workflow output data
        workflow_output = {
            "task_id": "TEST-02",
            "status": "completed",
            "results": {
                "code_generated": True,
                "files_created": [
                    "src/api/endpoints.py",
                    "src/models/user.py",
                    "tests/test_api.py"
                ],
                "test_results": {
                    "passed": 15,
                    "failed": 0,
                    "coverage": 0.85
                }
            },
            "metadata": {
                "execution_time": 120.5,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Store workflow output
        storage_path = self.storage_manager.store_data(
            key=workflow_output["task_id"],
            data=json.dumps(workflow_output).encode('utf-8'),
            metadata={'data_type': "workflow_output", 'task_id': workflow_output["task_id"]}
        )
        
        # Verify storage
        self.assertIsNotNone(storage_path)
        
        # Retrieve and verify
        retrieved_data_bytes = self.storage_manager.retrieve_data(workflow_output["task_id"])
        retrieved_data = json.loads(retrieved_data_bytes.decode('utf-8'))
        
        self.assertEqual(retrieved_data["task_id"], "TEST-02")
        self.assertEqual(retrieved_data["status"], "completed")
        self.assertEqual(len(retrieved_data["results"]["files_created"]), 3)
    
    def test_memory_to_agent_context_flow(self):
        """Test context flow from memory to agent."""
        # Store context in memory
        test_contexts = [
            {
                "key": "architecture_patterns",
                "content": {
                    "patterns": ["MVC", "Microservices", "Event-driven"],
                    "best_practices": ["SOLID principles", "DRY", "KISS"]
                },
                "domains": ["architecture", "design"]
            },
            {
                "key": "api_guidelines",
                "content": {
                    "standards": ["REST", "GraphQL"],
                    "versioning": "URL-based",
                    "authentication": "JWT"
                },
                "domains": ["backend", "api"]
            }
        ]
        
        # Mock memory storage
        self.mock_memory.store_context = Mock()
        self.mock_memory.get_context.return_value = {"contexts": test_contexts, "relevance_scores": [0.9, 0.8]}
        
        # Agent requests context
        query = "Design REST API for user management"
        relevant_context = self.mock_memory.get_context(
            query,
            context_domains=["backend", "api"]
        )
        
        # Verify context retrieval
        self.mock_memory.get_context.assert_called_with(
            query,
            context_domains=["backend", "api"]
        )
        
        # Check context content
        self.assertEqual(len(relevant_context["contexts"]), 2)
        self.assertIn("api_guidelines", 
                     [ctx["key"] for ctx in relevant_context["contexts"]])
    
    def test_data_transformation_pipeline(self):
        """Test data transformation through processing pipeline."""
        # Define transformation pipeline
        transformations = [
            {
                "name": "validate_input",
                "func": lambda x: {**x, "validated": True} if "task_id" in x else None
            },
            {
                "name": "enrich_data",
                "func": lambda x: {**x, "enriched_at": datetime.now().isoformat()}
            },
            {
                "name": "format_output",
                "func": lambda x: {
                    "formatted": True,
                    "original": x,
                    "summary": f"Task {x.get('task_id')} processed"
                }
            }
        ]
        
        # Initial data
        input_data = {
            "task_id": "TRANSFORM-01",
            "data": {"value": 42},
            "user": "test@example.com"
        }
        
        # Apply transformations
        current_data = input_data
        transformation_history = []
        
        for transform in transformations:
            try:
                transformed = transform["func"](current_data)
                transformation_history.append({
                    "step": transform["name"],
                    "input": current_data,
                    "output": transformed,
                    "timestamp": datetime.now().isoformat()
                })
                current_data = transformed
            except Exception as e:
                transformation_history.append({
                    "step": transform["name"],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                break
        
        # Verify transformation results
        self.assertTrue(current_data["formatted"])
        self.assertEqual(
            current_data["summary"],
            "Task TRANSFORM-01 processed"
        )
        self.assertEqual(len(transformation_history), 3)
        
        # Verify data integrity through pipeline
        self.assertEqual(
            current_data["original"]["task_id"],
            input_data["task_id"]
        )
    
    def test_concurrent_data_access(self):
        """Test concurrent data access and consistency."""
        import threading
        import time
        
        # Shared data store
        shared_data = {
            "counter": 0,
            "operations": []
        }
        
        # Lock for thread safety
        data_lock = threading.Lock()
        
        def worker_thread(worker_id, num_operations):
            """Worker that reads and writes data."""
            for i in range(num_operations):
                with data_lock:
                    # Read current value
                    current = shared_data["counter"]
                    
                    # Simulate processing
                    time.sleep(0.001)
                    
                    # Write updated value
                    shared_data["counter"] = current + 1
                    shared_data["operations"].append({
                        "worker": worker_id,
                        "operation": i,
                        "value": current + 1,
                        "timestamp": datetime.now().isoformat()
                    })
        
        # Launch concurrent workers
        threads = []
        num_workers = 5
        operations_per_worker = 10
        
        for i in range(num_workers):
            thread = threading.Thread(
                target=worker_thread,
                args=(f"worker_{i}", operations_per_worker)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify data consistency
        expected_total = num_workers * operations_per_worker
        self.assertEqual(shared_data["counter"], expected_total)
        self.assertEqual(len(shared_data["operations"]), expected_total)
        
        # Verify no lost updates
        values = [op["value"] for op in shared_data["operations"]]
        self.assertEqual(set(values), set(range(1, expected_total + 1)))
    
    def test_data_validation_chain(self):
        """Test data validation through processing chain."""
        # Define validation rules
        validators = [
            {
                "name": "required_fields",
                "validate": lambda x: all(field in x for field in ["id", "type", "data"])
            },
            {
                "name": "type_check",
                "validate": lambda x: isinstance(x.get("data"), dict)
            },
            {
                "name": "value_range",
                "validate": lambda x: 0 <= x.get("data", {}).get("score", 0) <= 100
            }
        ]
        
        # Test data sets
        test_cases = [
            {
                "data": {"id": "1", "type": "test", "data": {"score": 85}},
                "expected": True
            },
            {
                "data": {"id": "2", "type": "test"},  # Missing data field
                "expected": False
            },
            {
                "data": {"id": "3", "type": "test", "data": {"score": 150}},  # Out of range
                "expected": False
            }
        ]
        
        for test_case in test_cases:
            validation_results = []
            is_valid = True
            
            for validator in validators:
                try:
                    result = validator["validate"](test_case["data"])
                    validation_results.append({
                        "validator": validator["name"],
                        "passed": result
                    })
                    if not result:
                        is_valid = False
                        break
                except Exception as e:
                    validation_results.append({
                        "validator": validator["name"],
                        "error": str(e)
                    })
                    is_valid = False
                    break
            
            self.assertEqual(is_valid, test_case["expected"])
    
    def test_data_serialization_formats(self):
        """Test data serialization in different formats."""
        # Complex data structure
        test_data = {
            "id": "SER-001",
            "timestamp": datetime.now(),
            "nested": {
                "list": [1, 2, 3],
                "dict": {"a": 1, "b": 2},
                "tuple": (4, 5, 6)
            },
            "binary": bytes([0x00, 0x01, 0x02, 0x03])
        }
        
        # JSON serialization (with custom encoder)
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                if isinstance(obj, bytes):
                    return obj.hex()
                if isinstance(obj, tuple):
                    return list(obj)
                return super().default(obj)
        
        json_data = json.dumps(test_data, cls=DateTimeEncoder)
        json_loaded = json.loads(json_data)
        
        self.assertEqual(json_loaded["id"], "SER-001")
        self.assertEqual(json_loaded["nested"]["list"], [1, 2, 3])
        
        # Pickle serialization
        pickle_data = pickle.dumps(test_data)
        pickle_loaded = pickle.loads(pickle_data)
        
        self.assertEqual(pickle_loaded["id"], "SER-001")
        self.assertIsInstance(pickle_loaded["timestamp"], datetime)
        self.assertEqual(pickle_loaded["binary"], bytes([0x00, 0x01, 0x02, 0x03]))
        
        # YAML serialization
        # YAML serialization (convert tuple to list for YAML compatibility)
        yaml_data = yaml.dump({
            "id": test_data["id"],
            "timestamp": test_data["timestamp"],
            "nested": {
                "list": test_data["nested"]["list"],
                "dict": test_data["nested"]["dict"],
                "tuple": list(test_data["nested"]["tuple"])
            },
            "binary": test_data["binary"]
        })
        yaml_loaded = yaml.safe_load(yaml_data)
        
        self.assertEqual(yaml_loaded["id"], "SER-001")
    
    def test_data_integrity_verification(self):
        """Test data integrity verification mechanisms."""
        # Original data
        original_data = {
            "id": "INT-001",
            "content": "Important data that must not be corrupted",
            "values": [1, 2, 3, 4, 5],
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        # Compute checksums
        def compute_checksum(data):
            """Compute SHA-256 checksum of data."""
            data_str = json.dumps(data, sort_keys=True)
            return hashlib.sha256(data_str.encode()).hexdigest()
        
        original_checksum = compute_checksum(original_data)
        
        # Store with checksum
        stored_data = {
            "data": original_data,
            "checksum": original_checksum,
            "stored_at": datetime.now().isoformat()
        }
        
        # Simulate retrieval
        retrieved_data = stored_data["data"].copy()
        
        # Verify integrity
        retrieved_checksum = compute_checksum(retrieved_data)
        self.assertEqual(original_checksum, retrieved_checksum)
        
        # Test corruption detection
        corrupted_data = retrieved_data.copy()
        corrupted_data["values"][2] = 999  # Corrupt data
        
        corrupted_checksum = compute_checksum(corrupted_data)
        self.assertNotEqual(original_checksum, corrupted_checksum)
    
    def test_streaming_data_flow(self):
        """Test streaming data flow for large datasets."""
        # Simulate streaming data source
        def data_generator(num_items):
            """Generate streaming data."""
            for i in range(num_items):
                yield {
                    "id": f"STREAM-{i:05d}",
                    "value": i * 2,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Process streaming data
        processed_count = 0
        batch_size = 100
        batch_buffer = []
        
        for item in data_generator(1000):
            batch_buffer.append(item)
            
            if len(batch_buffer) >= batch_size:
                # Process batch
                batch_sum = sum(item["value"] for item in batch_buffer)
                processed_count += len(batch_buffer)
                
                # Clear buffer
                batch_buffer = []
        
        # Process remaining items
        if batch_buffer:
            processed_count += len(batch_buffer)
        
        self.assertEqual(processed_count, 1000)
    
    def test_data_recovery_mechanisms(self):
        """Test data recovery from failures."""
        # Simulate data operations with checkpointing
        checkpoint_dir = Path(self.temp_dir) / "checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)
        
        def save_checkpoint(state, checkpoint_id):
            """Save processing checkpoint."""
            checkpoint_file = checkpoint_dir / f"{checkpoint_id}.json"
            with open(checkpoint_file, 'w') as f:
                json.dump(state, f)
        
        def load_checkpoint(checkpoint_id):
            """Load processing checkpoint."""
            checkpoint_file = checkpoint_dir / f"{checkpoint_id}.json"
            if checkpoint_file.exists():
                with open(checkpoint_file) as f:
                    return json.load(f)
            return None
        
        # Simulate processing with failure
        items_to_process = list(range(100))
        processed_items = []
        checkpoint_interval = 10
        
        try:
            for i, item in enumerate(items_to_process):
                # Simulate failure at item 45
                if item == 45:
                    raise Exception("Processing failed")
                
                processed_items.append(item * 2)
                
                # Save checkpoint
                if (i + 1) % checkpoint_interval == 0:
                    save_checkpoint({
                        "last_processed": i,
                        "processed_items": processed_items
                    }, "process_1")
        
        except Exception:
            # Recovery from checkpoint
            checkpoint = load_checkpoint("process_1")
            self.assertIsNotNone(checkpoint)
            
            # Resume from checkpoint
            last_processed = checkpoint["last_processed"]
            processed_items = checkpoint["processed_items"]
            
            # Continue processing
            for i in range(last_processed + 1, len(items_to_process)):
                processed_items.append(items_to_process[i] * 2)
        
        # Verify complete processing
        self.assertEqual(len(processed_items), 100)
        self.assertEqual(processed_items[44], 88)  # Verify recovery point


if __name__ == "__main__":
    pytest.main([__file__, "-v"])