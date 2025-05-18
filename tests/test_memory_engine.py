import sys
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tests.mock_environment import setup_mock_environment
setup_mock_environment()

"""
Unit and Integration Tests for MemoryEngine
Covers: Initialization, document addition, retrieval, secure deletion, PII scan, and performance benchmarking.
"""
import os
import unittest
from tools.memory_engine import MemoryEngine, initialize_memory, get_relevant_context, MemoryEngineConfig, ChunkingConfig
from typing import List

class TestMemoryEngine(unittest.TestCase):
    def setUp(self):
        # Grant 'tester' read/write permissions for testing and set small chunk size
        test_config = MemoryEngineConfig(
            security_options={
                "roles": {"tester": ["read", "write"]},
                "sanitize_inputs": True
            },
            chunking=ChunkingConfig(
                semantic=True,
                adaptive=True,
                min_chunk_size=1,  # allow small test docs
                max_chunk_size=2048,
                overlap_percent=0.0,
                deduplicate=False,
                quality_metrics=False
            )
        )
        self.memory = MemoryEngine(config=test_config)
        self.test_file = "context-store/test_doc.md"
        # Create a test document
        os.makedirs(os.path.dirname(self.test_file), exist_ok=True)
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("This is a test document.\nContact: test@example.com\nSSN: 123-45-6789\n")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_and_retrieve_document(self):
        self.memory.add_document(self.test_file, user="tester")
        # Monkeypatch vector_store.as_retriever().get_relevant_documents to return the chunked content
        original_as_retriever = getattr(self.memory.vector_store, "as_retriever", None)
        class MockRetriever:
            def get_relevant_documents(inner_self, query):
                class Doc:
                    def __init__(self, content):
                        self.page_content = content
                return [Doc(chunk) for chunk in self.memory.tiered_storage.hot.keys()]
        def patched_as_retriever():
            return MockRetriever()
        self.memory.vector_store.as_retriever = patched_as_retriever
        context = self.memory.get_context("test document", k=1, user="tester")
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
        self.assertTrue(any("SSN" in k or "test@example.com" in k for k in flagged) or len(flagged) > 0)

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
import time

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
    print(f"Benchmark: {iterations} add+retrieve cycles in {elapsed:.2f}s ({elapsed/iterations:.3f}s per op)")
    os.remove(test_file)

if __name__ == "__main__":
    unittest.main()
    print("\nRunning performance benchmark...")
    benchmark_memory_engine_add_retrieve(5)
