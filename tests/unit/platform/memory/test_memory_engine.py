import os
import shutil
import sys
import time
import unittest
from unittest.mock import patch, MagicMock


from tests.helpers import cleanup_test_files
from scripts.mocks.mock_environment import setup_mock_environment
from scripts.mocks.mock_openai_embeddings import create_mock_openai_embeddings
from src.infrastructure.memory import MemoryEngine, MemoryEngineConfig

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))
setup_mock_environment()

"""
Unit and Integration Tests for MemoryEngine
Covers: Initialization, document addition, retrieval, secure deletion, PII scan, and performance benchmarking.
"""


class TestMemoryEngine(unittest.TestCase):
    def setUp(self):
        # Create mock OpenAI embeddings
        self.mock_embeddings, self.mock_embeddings_instance = create_mock_openai_embeddings()

        # Patch OpenAIEmbeddings to use our mock
        self.openai_patcher = patch(
            'src.infrastructure.memory.engines.memory_engine.OpenAIEmbeddings', self.mock_embeddings)
        self.openai_patcher.start()
        
        # Mock security system to avoid encryption key errors - patch where it's imported
        self.security_patcher = patch('src.infrastructure.memory.engines.memory_engine.SecurityManager')
        mock_security = self.security_patcher.start()
        mock_security_instance = MagicMock()
        mock_security_instance.encrypt_data.return_value = b'encrypted_data'
        mock_security_instance.decrypt_data.return_value = 'decrypted_data'
        mock_security_instance.encryption_enabled = True
        # Make sure get_index_health returns proper structure
        mock_security_instance.get_index_health.return_value = {
            'cache': {'l1': {'size': 0}, 'l2': {'size': 0}},
            'storage': {'status': 'healthy'}
        }
        mock_security.return_value = mock_security_instance
        
        # Mock Fernet to avoid key generation issues  
        self.fernet_patcher = patch('src.infrastructure.memory.security.encryption.Fernet')
        mock_fernet = self.fernet_patcher.start()
        mock_fernet_instance = MagicMock()
        mock_fernet_instance.encrypt.return_value = b'encrypted_data'
        mock_fernet_instance.decrypt.return_value = b'decrypted_data'
        mock_fernet.return_value = mock_fernet_instance
        mock_fernet.generate_key.return_value = b'a' * 44  # 44 bytes base64 encoded = 32 bytes raw
        # Grant 'tester' read/write/delete/admin permissions for testing and
        # set small chunk size
        test_config = MemoryEngineConfig(
            collection_name="test_collection"
        )        # Update chunking config for testing
        test_config.chunking.min_chunk_size = 1  # allow small test docs
        test_config.chunking.chunk_size = 2048
        test_config.chunking.chunk_overlap = 0
        self.memory = MemoryEngine(config=test_config)
        from config.build_paths import TEST_OUTPUTS_DIR
        self.test_file = str(TEST_OUTPUTS_DIR / "test_doc.md")        # Create a test document
        os.makedirs(os.path.dirname(self.test_file), exist_ok=True)
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write(
                "This is a test document.\nContact: test@example.com\nSSN: 123-45-6789\n")

    def tearDown(self):
        # Stop patching
        self.openai_patcher.stop()
        self.security_patcher.stop()
        self.fernet_patcher.stop()

        # Clear memory engine to release file handles
        try:
            if hasattr(self, 'memory'):
                self.memory.clear(user="test_cleanup")
        except Exception:
            pass

        # Remove test file with retry for Windows file locking
        if hasattr(self, 'test_file') and os.path.exists(self.test_file):
            try:
                os.remove(self.test_file)
            except PermissionError:
                # File is still in use, try after brief delay
                import time
                time.sleep(0.1)
                try:
                    os.remove(self.test_file)
                except (PermissionError, FileNotFoundError):
                    # Still locked or already deleted, skip for now - cleanup will handle it
                    pass

        # Clean up all test files and directories
        cleanup_test_files()

    def test_add_and_retrieve_document(self):
        self.memory.add_document(self.test_file, user="tester")
        # Monkeypatch vector_store.as_retriever().get_relevant_documents to        # return the chunked content
        original_as_retriever = None
        if self.memory.vector_store is not None:
            original_as_retriever = getattr(self.memory.vector_store, "as_retriever", None)

        class MockRetriever:
            def get_relevant_documents(inner_self, query):
                class Doc:
                    def __init__(self, content):
                        self.page_content = content
                return [Doc(chunk)
                        for chunk in self.memory.tiered_storage.hot.keys()]

        def patched_as_retriever():
            return MockRetriever()
        
        if self.memory.vector_store is not None:
            self.memory.vector_store.as_retriever = patched_as_retriever
            
        context = self.memory.get_context("test document", k=1, user="tester")
        
        if self.memory.vector_store is not None:
            if original_as_retriever:
                self.memory.vector_store.as_retriever = original_as_retriever
            else:
                del self.memory.vector_store.as_retriever
                
        self.assertIn("test document", context)

    def test_secure_delete(self):
        self.memory.add_document(self.test_file, user="tester")
        # Use the chunk key directly for test (simulate chunking)
        chunk_key = "This is a test document.\nContact: test@example.com\nSSN: 123-45-6789"
        result = self.memory.secure_delete(chunk_key, user="tester")
        self.assertTrue(result)

    def test_scan_for_pii(self):
        self.memory.add_document(self.test_file, user="tester")
        flagged = self.memory.scan_for_pii(user="tester")
        # At least one flagged chunk should contain PII
        self.assertTrue(
            any("SSN" in k or "test@example.com" in k for k in flagged) or len(flagged) > 0)

    def test_index_health(self):
        health = self.memory.get_index_health()
        self.assertIn("cache", health)
        self.assertIn("storage", health)

    def test_profiler_stats(self):
        stats = self.memory.profiler.stats()
        self.assertIsInstance(stats, list)

    def test_clear(self):
        self.memory.clear(user="tester")
        # After clear, caches should be empty
        health = self.memory.get_index_health()
        self.assertEqual(health["cache"]["l1"]["size"], 0)
        self.assertEqual(health["cache"]["l2"]["size"], 0)


# Performance Benchmarking


def benchmark_memory_engine_add_retrieve(iterations: int = 10):
    """Benchmark add and retrieve operations."""
    memory = MemoryEngine()
    test_file = "context-store/benchmark_doc.md"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Benchmarking document.\n" * 100)
    start = time.time()
    for _ in range(iterations):
        memory.add_document(test_file, user="bench")
        _ = memory.get_context("Benchmarking document", k=1, user="bench")
    elapsed = time.time() - start
    print(
        f"Benchmark: {iterations} add+retrieve cycles in {elapsed:.2f}s ({elapsed / iterations:.3f}s per op)")
    os.remove(test_file)


def teardown_module(module):
    """Cleanup test_outputs directory after tests finish."""
    from config.build_paths import TEST_OUTPUTS_DIR
    test_output_dir = str(TEST_OUTPUTS_DIR)
    if os.path.exists(test_output_dir):
        for child in os.listdir(test_output_dir):
            child_path = os.path.join(test_output_dir, child)
            if os.path.isdir(child_path):
                shutil.rmtree(child_path)
            else:
                os.remove(child_path)


if __name__ == "__main__":
    unittest.main()
    print("\nRunning performance benchmark...")
    benchmark_memory_engine_add_retrieve(5)
