import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

"""
Unit Test for the RetrievalQA functionality in MemoryEngine
Tests the retrieval_qa method to ensure it can use LangChain's RetrievalQA chain
"""
import unittest
from unittest.mock import patch, MagicMock

# Import necessary classes from memory_engine
from tools.memory_engine import MemoryEngine, MemoryEngineConfig, ChunkingConfig, memory as global_memory
from tools.retrieval_qa import get_answer # Ensure this points to the correct location of get_answer

class TestRetrievalQA(unittest.TestCase):
    def setUp(self):
        self.memory = global_memory

        self.test_file_content = "This is a test document about RLS rules in Supabase."
        # Use an absolute path or a path clearly relative to the test execution directory
        self.test_file_dir = os.path.join(os.path.dirname(__file__), "test_data", "context-store")
        self.test_file_path_relative_to_engine = "test_data/context-store/test_doc.md" # Path MemoryEngine would use
        self.test_file_path_absolute = os.path.join(self.test_file_dir, "test_doc.md")

        os.makedirs(self.test_file_dir, exist_ok=True)
        with open(self.test_file_path_absolute, "w") as f:
            f.write(self.test_file_content)
        
        # Mock MemoryEngine's internal LLM and VectorStore components
        self.patcher_chat_openai = patch('tools.memory_engine.ChatOpenAI')
        self.mock_chat_openai_class = self.patcher_chat_openai.start()
        self.mock_llm_instance = MagicMock()
        self.mock_chat_openai_class.return_value = self.mock_llm_instance
        
        self.patcher_chroma = patch('tools.memory_engine.Chroma')
        self.mock_chroma_class = self.patcher_chroma.start()
        self.mock_vector_store_instance = MagicMock()
        # Mock methods that would be called on Chroma instance
        self.mock_vector_store_instance.as_retriever.return_value = MagicMock()
        self.mock_vector_store_instance.add_texts.return_value = ["doc_id1"]
        self.mock_chroma_class.return_value = self.mock_vector_store_instance # For Chroma()
        self.mock_chroma_class.from_documents.return_value = self.mock_vector_store_instance # For Chroma.from_documents

        # If memory engine loads from disk, ensure the mock is returned
        # And assign the mocked vector_store to the global_memory instance for this test
        self.original_vector_store = self.memory.vector_store
        self.memory.vector_store = self.mock_vector_store_instance
        self.original_kb_path = self.memory.config.knowledge_base_path
        # Point knowledge_base_path to where test_doc.md is, relative to engine's perspective
        self.memory.config.knowledge_base_path = os.path.join(os.path.dirname(__file__), "test_data")
    def tearDown(self):
        if os.path.exists(self.test_file_path_absolute):
            os.remove(self.test_file_path_absolute)
        # Clean up directory if empty, be careful with this
        if os.path.exists(self.test_file_dir) and not os.listdir(self.test_file_dir):
            os.rmdir(self.test_file_dir)
            # If test_data is also empty
            if os.path.exists(os.path.dirname(self.test_file_dir)) and not os.listdir(os.path.dirname(self.test_file_dir)):
                os.rmdir(os.path.dirname(self.test_file_dir))
                
        self.patcher_chat_openai.stop()
        self.patcher_chroma.stop()
        self.memory.vector_store = self.original_vector_store # Restore original vector store
        self.memory.config.knowledge_base_path = self.original_kb_path

    @patch('tools.memory_engine.RetrievalQA.from_chain_type')
    def test_retrieval_qa_chain(self, mock_retrieval_qa_from_chain_type):
        mock_chain_instance = MagicMock()
        mock_chain_instance.invoke.return_value = {"result": "The orders table has RLS rules that restrict users to only see their own orders."}
        # For backwards compatibility with older LangChain versions
        # In newer versions of Python/unittest, __call__ is a method and can't have return_value directly assigned
        mock_chain_instance.__call__ = MagicMock(return_value={"result": "The orders table has RLS rules that restrict users to only see their own orders."})
        mock_retrieval_qa_from_chain_type.return_value = mock_chain_instance

        mock_retriever = MagicMock()
        mock_retriever.get_relevant_documents.return_value = [
            MagicMock(page_content="The orders table has RLS rules.")
        ]
        self.memory.vector_store.as_retriever.return_value = mock_retriever
        
        # add_document expects a path relative to its knowledge_base_path
        self.memory.add_document(self.test_file_path_relative_to_engine, user="tester")

        # Test with default parameters to ensure correct handling of None values
        result = self.memory.retrieval_qa(
            "What are the Supabase RLS rules for the orders table?", 
            user="tester"
        )

        # Verify the chain was created with the right parameters
        mock_retrieval_qa_from_chain_type.assert_called_once_with(
            llm=self.memory.llm,
            chain_type="stuff",
            retriever=mock_retriever,
            return_source_documents=True
        )
        # Verify invoke was called with the right query parameter
        mock_chain_instance.invoke.assert_called_once_with({"query": "What are the Supabase RLS rules for the orders table?"})
        
        self.assertEqual(result, "The orders table has RLS rules that restrict users to only see their own orders.")
        
    def test_get_answer_helper(self):
        with patch.object(self.memory, 'retrieval_qa') as mock_memory_retrieval_qa:
            mock_memory_retrieval_qa.return_value = "Test answer from helper"
            
            # Ensure test directory exists for the test doc
            if not os.path.exists(self.test_file_dir):
                os.makedirs(self.test_file_dir, exist_ok=True)
                
            # Ensure test document exists for any dependencies
            if not os.path.exists(self.test_file_path_absolute):
                with open(self.test_file_path_absolute, "w") as f:
                    f.write(self.test_file_content)
            
            # Test basic usage
            response = get_answer("Test question from helper", user="helper_user")
            mock_memory_retrieval_qa.assert_called_with(
                "Test question from helper",
                use_conversation=False,
                metadata_filter=None,
                temperature=0.0,
                user="helper_user",
                chat_history=None
            )
            self.assertEqual(response, "Test answer from helper")
            
            # Reset mock to test with chat_history
            mock_memory_retrieval_qa.reset_mock()
            
            # Test with chat_history
            chat_history = [("Hello", "Hi there"), ("How are you?", "I'm fine")]
            response2 = get_answer(
                "Another question", 
                use_conversation=True,
                chat_history=chat_history
            )
            
            mock_memory_retrieval_qa.assert_called_with(
                "Another question",
                use_conversation=True,
                metadata_filter=None,
                temperature=0.0,
                user=None,
                chat_history=chat_history
            )
            self.assertEqual(response2, "Test answer from helper")

if __name__ == '__main__':
    unittest.main()
