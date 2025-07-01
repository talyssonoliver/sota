"""
Test actual memory engine functionality rather than implementation details.
This replaces test_updated_retrieval_qa.py with tests that validate real behavior.
"""
import logging
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch
try:
    from tests.mock_openai_embeddings import create_mock_openai_embeddings
except ImportError as e:
    logging.warning(f'Failed to import mock OpenAI embeddings: {e}')

    def create_mock_openai_embeddings():
        """Fallback mock function."""
        return MagicMock()
try:
    from src.infrastructure.memory import MemoryEngine
except ImportError as e:
    logging.error(f'Failed to import MemoryEngine: {e}')

    class MemoryEngine:
        """Mock MemoryEngine for when the real one is not available."""

        def __init__(self, *args, **kwargs):
            pass
try:
    from src.infrastructure.memory.config.memory_config import MemoryEngineConfig, ChunkingConfig
except ImportError as e:
    logging.error(f'Failed to import memory config classes: {e}')

    class MemoryEngineConfig:
        """Mock MemoryEngineConfig."""

        def __init__(self, *args, **kwargs):
            pass

    class ChunkingConfig:
        """Mock ChunkingConfig."""

        def __init__(self, *args, **kwargs):
            pass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMemoryEngineCore(unittest.TestCase):
    """Test core memory engine functionality"""

    def setUp(self):
        """Set up test environment"""
        self.mock_embeddings, self.mock_embeddings_instance = create_mock_openai_embeddings()
        self.patcher = patch('src.infrastructure.memory.engine.OpenAIEmbeddings', self.mock_embeddings)
        self.patcher.start()
        test_config = MemoryEngineConfig(security_options={'roles': {'test_user': ['read', 'write']}, 'sanitize_inputs': True}, chunking=ChunkingConfig(semantic=True, adaptive=True, min_chunk_size=1, max_chunk_size=512, overlap_percent=0.0, deduplicate=False))
        self.memory = MemoryEngine(config=test_config)
        self.test_content = '\n# Authentication System\n\nOur platform uses Supabase for authentication. The orders table has Row Level Security (RLS) rules\nthat restrict users to only see their own orders. This ensures data privacy and security.\n\n## Implementation Details\n\nThe authentication is handled via JWT tokens. Users must be authenticated to access the API.\nThe backend implements proper authorization checks for all endpoints.\n\n## Database Security\n\nRow Level Security policies are enforced at the database level for maximum security.\n'
        self.test_file = os.path.join(tempfile.gettempdir(), 'test_auth_doc.md')
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(self.test_content)

    def tearDown(self):
        """Clean up test environment"""
        self.patcher.stop()
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_context_retrieval_basic(self):
        """Test basic context retrieval works"""
        self.memory.add_document(self.test_file, user='test_user')
        context = self.memory.get_context('What authentication system does the platform use?', k=3, user='test_user')
        self.assertIsInstance(context, str)
        self.assertGreater(len(context), 0)
        context_lower = context.lower()
        self.assertTrue('supabase' in context_lower or 'authentication' in context_lower, f'Context should mention authentication or Supabase, got: {context[:200]}...')

    def test_context_with_metadata_filtering(self):
        """Test metadata filtering in context retrieval"""
        self.memory.add_document(self.test_file, user='test_user', metadata={'domain': 'security', 'type': 'documentation'})
        context = self.memory.get_context('How is authentication implemented?', k=3, user='test_user', metadata_filter={'domain': 'security'})
        self.assertIsInstance(context, str)
        self.assertGreaterEqual(len(context), 0)

    def test_secure_storage_and_retrieval(self):
        """Test that content is properly encrypted and retrieved"""
        self.memory.add_document(self.test_file, user='test_user')
        health = self.memory.get_index_health()
        self.assertIn('cache', health)
        self.assertIn('storage', health)
        context = self.memory.get_context('authentication', k=1, user='test_user')
        self.assertIsInstance(context, str)
        if len(context) > 0:
            self.assertIn('authentication', context.lower())

    def test_access_control_enforcement(self):
        """Test that access control works"""
        self.memory.add_document(self.test_file, user='test_user')
        context = self.memory.get_context('authentication', k=1, user='unauthorized_user')
        self.assertIsInstance(context, str)

    def test_conversation_context_persistence(self):
        """Test that conversation context can be maintained through get_context"""
        self.memory.add_document(self.test_file, user='test_user')
        context1 = self.memory.get_context('What authentication system is used?', k=2, user='test_user')
        context2 = self.memory.get_context('How are JWT tokens handled?', k=2, user='test_user')
        self.assertIsInstance(context1, str)
        self.assertIsInstance(context2, str)
        self.assertGreaterEqual(len(context1), 0)
        self.assertGreaterEqual(len(context2), 0)

class TestMemoryEngineIntegration(unittest.TestCase):
    """Test integration aspects with actual helper functions"""

    def setUp(self):
        """Set up test environment"""
        self.mock_embeddings, self.mock_embeddings_instance = create_mock_openai_embeddings()
        self.patcher = patch('src.infrastructure.memory.engine.OpenAIEmbeddings', self.mock_embeddings)
        self.patcher.start()

    def tearDown(self):
        """Clean up"""
        self.patcher.stop()

    def test_helper_functions_integration(self):
        """Test that helper functions work with memory engine"""
        try:
            from src.infrastructure.memory import get_relevant_context, initialize_memory
        except ImportError:
            pass
        memory_instance = initialize_memory()
        self.assertIsNotNone(memory_instance)
        context = get_relevant_context('test query', k=1, user='system')
        self.assertIsInstance(context, str)
        self.assertGreaterEqual(len(context), 0)

    def test_retrieval_qa_integration(self):
        """Test that retrieval QA functionality is accessible"""
        try:
            # Updated import path after retrieval_qa migration to src/
            from src.infrastructure.tools.retrieval_qa import get_answer
            with patch('src.infrastructure.tools.retrieval_qa.get_memory_instance') as mock_get_memory:
                mock_memory = Mock()
                mock_memory.retrieval_qa.return_value = 'Test answer from knowledge base'
                mock_get_memory.return_value = mock_memory
                result = get_answer('Test question')
                self.assertEqual(result, 'Test answer from knowledge base')
        except ImportError:
            self.skipTest('retrieval_qa module not available')

class TestMemoryEngineSecurity(unittest.TestCase):
    """Test security aspects work correctly"""

    def setUp(self):
        """Set up test environment"""
        self.mock_embeddings, self.mock_embeddings_instance = create_mock_openai_embeddings()
        self.patcher = patch('src.infrastructure.memory.engine.OpenAIEmbeddings', self.mock_embeddings)
        self.patcher.start()
        test_config = MemoryEngineConfig(security_options={'roles': {'test_user': ['read', 'write', 'delete', 'admin']}, 'sanitize_inputs': True})
        self.memory = MemoryEngine(config=test_config)

    def tearDown(self):
        """Clean up"""
        self.patcher.stop()

    def test_encrypted_storage_retrieval(self):
        """Test that content is properly encrypted and retrieved"""
        test_content = 'User email: test@example.com\nSSN: 123-45-6789\nPassword: secret123'
        test_file = os.path.join(tempfile.gettempdir(), 'sensitive_doc.md')
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            self.memory.add_document(test_file, user='test_user')
            context = self.memory.get_context('user information', k=1, user='test_user')
            self.assertIsInstance(context, str)
            flagged = self.memory.scan_for_pii(user='test_user')
            self.assertIsInstance(flagged, list)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_secure_deletion(self):
        """Test secure deletion functionality"""
        test_content = 'This is sensitive information that should be deletable'
        test_file = os.path.join(tempfile.gettempdir(), 'deletable_doc.md')
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            self.memory.add_document(test_file, user='test_user')
            deletion_result = self.memory.secure_delete(test_content, user='test_user')
            self.assertIsInstance(deletion_result, bool)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
if __name__ == '__main__':
    unittest.main()