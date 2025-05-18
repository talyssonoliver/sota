"""
Fixed test for RetrievalQA functionality in MemoryEngine
This test file addresses the compatibility issues with newer LangChain versions
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from unittest.mock import patch, MagicMock

# Import necessary classes from memory_engine
from tools.memory_engine import MemoryEngine, MemoryEngineConfig, memory as global_memory
from tools.retrieval_qa import get_answer
from tests.fixtures.langchain_fixtures import LangChainMockFixture, FakeChatMemory
from tests.fixtures.runnable_mock import RunnableLLMMock, RunnableChainMock

class TestFixedRetrievalQA(unittest.TestCase):
    def setUp(self):
        self.memory = global_memory
        
        # Test file setup
        self.test_file_content = "This is a test document about RLS rules in Supabase."
        self.test_file_dir = os.path.join(os.path.dirname(__file__), "test_data", "context-store")
        self.test_file_path = os.path.join(self.test_file_dir, "test_doc.md")
        self.test_file_path_relative = "test_data/context-store/test_doc.md"
        
        # Ensure the test directory exists
        os.makedirs(self.test_file_dir, exist_ok=True)
        
        # Create a test document for the memory engine
        with open(self.test_file_path, "w") as f:
            f.write(self.test_file_content)
        
        # Create fixture for LangChain mocks    
        self.fixture = LangChainMockFixture()
        
        # Apply fixtures and get mocks
        self.mocks = self.fixture.apply()
            
        # Store and replace the vector store in the memory instance
        self.original_vector_store = self.memory.vector_store
        self.memory.vector_store = self.mocks['Chroma']
        
        # Store and update knowledge base path
        self.original_kb_path = self.memory.config.knowledge_base_path
        self.memory.config.knowledge_base_path = os.path.join(os.path.dirname(__file__), "test_data")
        
        # Update security roles to include fixture_tester with write access
        if hasattr(self.memory, 'access_control') and hasattr(self.memory.access_control, 'roles'):
            self.original_roles = self.memory.access_control.roles.copy()
            self.memory.access_control.roles["fixture_tester"] = ["read", "write"]
        
    def tearDown(self):
        # Clean up test file
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
            
        # Clean up empty test directories
        if os.path.exists(self.test_file_dir) and not os.listdir(self.test_file_dir):
            os.rmdir(self.test_file_dir)
            parent_dir = os.path.dirname(self.test_file_dir)
            if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                os.rmdir(parent_dir)
        
        # Stop patches
        self.fixture.__exit__(None, None, None)
        
        # Restore original memory engine state
        self.memory.vector_store = self.original_vector_store
        self.memory.config.knowledge_base_path = self.original_kb_path
        
        # Restore original security roles
        if hasattr(self.memory, 'access_control') and hasattr(self.memory.access_control, 'roles') and hasattr(self, 'original_roles'):
            self.memory.access_control.roles = self.original_roles
            
    def test_retrieval_qa_standard(self):
        """Test standard retrieval QA functionality with correct mocking"""
        # Setup mock retrieval chain
        self.mocks['RetrievalQA'].invoke.return_value = {"result": "The orders table has RLS rules that restrict users to only see their own orders."}
        
        # Setup mock retriever
        mock_retriever = MagicMock()
        self.mocks['Chroma'].as_retriever.return_value = mock_retriever
        
        # Add test document 
        self.memory.add_document(self.test_file_path_relative, user="tester")
        
        # Execute the retrieval_qa method
        result = self.memory.retrieval_qa(
            "What are the RLS rules for the orders table?",
            user="tester"
        )
        
        # Verify the chain setup
        self.mocks['from_chain_type'].assert_called_once_with(
            llm=self.memory.llm,
            chain_type="stuff",
            retriever=mock_retriever,
            return_source_documents=True
        )
        
        # Verify the invoke method was called with the right parameters
        self.mocks['RetrievalQA'].invoke.assert_called_once()
        call_args = self.mocks['RetrievalQA'].invoke.call_args[0][0]
        self.assertEqual(call_args["query"], "What are the RLS rules for the orders table?")
        
        # Check the result
        self.assertEqual(
            result, 
            "The orders table has RLS rules that restrict users to only see their own orders."
        )
        
    def test_conversation_mode(self):
        """Test conversation mode with chat history"""
        # Setup mock conversational chain
        self.mocks['ConversationalRetrievalChain'].invoke.return_value = {"answer": "Orders table uses row-level security."}
        
        # Setup mock retriever
        mock_retriever = MagicMock()
        self.mocks['Chroma'].as_retriever.return_value = mock_retriever
        
        # Create test chat history
        chat_history = [("What security features exist?", "We use RLS in Supabase.")]
        
        # Execute with conversation mode
        result = self.memory.retrieval_qa(
            "How does RLS work for orders?",
            use_conversation=True,
            user="tester",
            chat_history=chat_history
        )
        
        # Verify the conversation chain was created
        self.mocks['from_llm'].assert_called_once()
        
        # Verify invoke was called with question and chat history
        self.mocks['ConversationalRetrievalChain'].invoke.assert_called_once()
        call_args = self.mocks['ConversationalRetrievalChain'].invoke.call_args[0][0]
        self.assertEqual(call_args.get("question"), "How does RLS work for orders?")
        self.assertEqual(call_args.get("chat_history"), chat_history)
        
        # Verify result
        self.assertEqual(result, "Orders table uses row-level security.")
        
    def test_get_answer_helper_function(self):
        """Test the get_answer helper function with proper parameter passing"""
        # Mock the memory.retrieval_qa method
        with patch.object(self.memory, 'retrieval_qa') as mock_retrieval_qa:
            mock_retrieval_qa.return_value = "Helper function test answer"
            
            # Call the helper function
            result = get_answer(
                "Test question",
                use_conversation=False,
                metadata_filter={"domain": "security"},
                temperature=0.2,
                user="helper_test_user",
                chat_history=[("hi", "hello")]
            )
            
            # Verify all parameters were correctly passed
            mock_retrieval_qa.assert_called_once_with(
                "Test question",
                use_conversation=False,
                metadata_filter={"domain": "security"},
                temperature=0.2,
                user="helper_test_user",
                chat_history=[("hi", "hello")]
            )
            
            # Verify the result
            self.assertEqual(result, "Helper function test answer")
    
    def test_metadata_filtering(self):
        """Test metadata filtering works correctly"""
        # Setup the mock chain
        self.mocks['RetrievalQA'].invoke.return_value = {"result": "Filtered result"}
            
        # Setup mock retriever 
        mock_retriever = MagicMock()
        self.mocks['Chroma'].as_retriever.return_value = mock_retriever
        
        # Define metadata filter
        metadata_filter = {"domain": "security", "type": "database"}
        
        # Call with metadata filter
        result = self.memory.retrieval_qa(
            "Security question",
            metadata_filter=metadata_filter
        )
        
        # Verify as_retriever was called with filter parameter
        self.mocks['Chroma'].as_retriever.assert_called_with(
            search_type="similarity",
            search_kwargs={"k": 5, "filter": metadata_filter}
        )
        
        self.assertEqual(result, "Filtered result")

if __name__ == "__main__":
    unittest.main()
