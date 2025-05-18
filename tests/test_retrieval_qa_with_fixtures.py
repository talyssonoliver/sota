"""
Test for the RetrievalQA functionality using the new LangChain fixtures.
These tests demonstrate the correct way to mock LangChain components.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from unittest.mock import patch, MagicMock

from tools.memory_engine import memory
from tools.retrieval_qa import get_answer
from tests.fixtures.langchain_fixtures import LangChainMockFixture, create_test_file, FakeChatMemory

class TestRetrievalQAWithFixtures(unittest.TestCase):
    def setUp(self):
        """Set up the test environment with consistent mocks"""
        self.fixture = LangChainMockFixture()
        # Initialize mocks properly - will be populated by fixture.apply()
        self.mocks = None
        
        # Create a test document
        self.test_file = create_test_file(
            content="This is a test document about Supabase RLS rules.",
            file_path=os.path.join(os.path.dirname(__file__), "test_data", "context-store", "test_doc.md")
        )
        self.test_file_relative = os.path.relpath(
            self.test_file, 
            os.path.join(os.path.dirname(__file__), "..")  # Relative to project root
        )
        
        # Keep track of the original memory engine components
        self.restore_funcs = []
        
        # Update security roles to include fixture_tester with write access
        if hasattr(memory, 'access_control') and hasattr(memory.access_control, 'roles'):
            self.original_roles = memory.access_control.roles.copy()
            memory.access_control.roles["fixture_tester"] = ["read", "write"]
    
    def tearDown(self):
        """Clean up resources"""
        # Restore original components
        for restore_func in self.restore_funcs:
            restore_func()
            
        # Remove test file if it exists
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
            
        # Try to remove directories if empty
        test_dir = os.path.dirname(self.test_file)
        if os.path.exists(test_dir) and not os.listdir(test_dir):
            os.rmdir(test_dir)
            parent_dir = os.path.dirname(test_dir)
            if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                os.rmdir(parent_dir)
        
        # Restore original security roles
        if hasattr(memory, 'access_control') and hasattr(memory.access_control, 'roles') and hasattr(self, 'original_roles'):
            memory.access_control.roles = self.original_roles
            
        # Stop all patches
        if hasattr(self.fixture, '__exit__'):
            self.fixture.__exit__(None, None, None)
    
    def test_retrieval_qa_with_fixtures(self):
        """Test retrieval_qa using fixture mocks"""
        # Use the fixture as a context manager
        with self.fixture.apply() as mocks:
            # Store mocks for use in the test
            self.mocks = mocks
            
            # Replace memory engine's vector store with our mock
            self.restore_funcs.append(self.fixture.replace_memory_vector_store(memory))
            
            # Set up specific response for this test case
            mocks['RetrievalQA'].invoke.return_value = {
                "result": "The orders table has RLS rules that restrict users to only see their own orders."
            }
            
            # Add the document to the memory engine
            memory.add_document(self.test_file_relative, user="fixture_tester")
            
            # Make the query
            result = memory.retrieval_qa("What are the RLS rules for the orders table?", user="fixture_tester")
            
            # Verify the result
            self.assertEqual(
                result, 
                "The orders table has RLS rules that restrict users to only see their own orders."
            )
            
            # Verify the retriever was used correctly
            mocks['Chroma'].as_retriever.assert_called()
            
            # Verify RetrievalQA was called correctly
            mocks['from_chain_type'].assert_called_once()
            
            # Verify invoke was called with the expected parameters
            mocks['RetrievalQA'].invoke.assert_called_once()
            call_args = mocks['RetrievalQA'].invoke.call_args[0][0]
            self.assertEqual(call_args["query"], "What are the RLS rules for the orders table?")
    
    def test_conversation_mode_with_fixtures(self):
        """Test conversation mode using fixture mocks"""
        # Use the fixture properly as a context manager
        with self.fixture.apply() as mocks:
            self.mocks = mocks
            self.restore_funcs.append(self.fixture.replace_memory_vector_store(memory))
            
            # Set up conversation response
            mocks['ConversationalRetrievalChain'].invoke.return_value = {
                "answer": "RLS policies ensure users only see their own orders."
            }
            
            # Create chat history
            chat_history = [("How is security implemented?", "We use RLS in Supabase.")]
            
            # Add the document to the memory engine
            memory.add_document(self.test_file_relative, user="fixture_tester")
            
            # Make the conversation query
            result = memory.retrieval_qa(
                "What specific RLS rules apply to orders?",
                use_conversation=True,
                chat_history=chat_history,
                user="fixture_tester"
            )
            
            # Verify the result
            self.assertEqual(result, "RLS policies ensure users only see their own orders.")
            
            # Verify conversation chain was used
            mocks['from_llm'].assert_called_once()
            
            # Verify invoke was called with the expected parameters
            mocks['ConversationalRetrievalChain'].invoke.assert_called_once()
            call_args = mocks['ConversationalRetrievalChain'].invoke.call_args[0][0]
            self.assertEqual(call_args["question"], "What specific RLS rules apply to orders?")
            self.assertEqual(call_args["chat_history"], chat_history)
    
    def test_get_answer_helper_with_fixtures(self):
        """Test the get_answer helper function"""
        # Use a temporary spy instead of applying all fixtures
        with patch('tools.retrieval_qa.memory') as mock_memory:
            mock_memory.retrieval_qa.return_value = "Helper function answer"
            
            # Call the helper with all parameters
            result = get_answer(
                "Test question",
                use_conversation=True,
                metadata_filter={"domain": "security"},
                temperature=0.3,
                user="helper_user",
                chat_history=[("Hello", "Hi there")]
            )
            
            # Verify all parameters were correctly passed through
            mock_memory.retrieval_qa.assert_called_once_with(
                "Test question",
                use_conversation=True,
                metadata_filter={"domain": "security"},
                temperature=0.3,
                user="helper_user",
                chat_history=[("Hello", "Hi there")]
            )
            
            # Verify result
            self.assertEqual(result, "Helper function answer")

if __name__ == "__main__":
    unittest.main()
