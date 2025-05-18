"""
Comprehensive integration test for RetrievalQA functionality in MemoryEngine.
Tests both RetrievalQA and ConversationalRetrievalChain modes.
"""
from unittest.mock import patch, MagicMock
import unittest
import sys
import os
# Make fixtures directory available
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from fixtures.runnable_mock import RunnableLLMMock, RunnableChainMock
from tools.memory_engine import memory
from tools.retrieval_qa import get_answer # Ensure this is the correct import path

class TestRetrievalQAIntegration(unittest.TestCase):
    def setUp(self):
        """Set up mock objects"""
        # Use our RunnableLLMMock to satisfy Runnable interface
        self.mock_chat_instance = RunnableLLMMock()
        self.patcher_chat = patch('tools.memory_engine.ChatOpenAI') 
        self.mock_chat_class = self.patcher_chat.start()
        self.mock_chat_class.return_value = self.mock_chat_instance

        # Store and mock vector_store on the memory instance for test isolation
        self.original_vector_store = memory.vector_store
        self.mock_vector_store = MagicMock()
        # Setup mock retriever
        self.mock_retriever = MagicMock()
        self.mock_vector_store.as_retriever.return_value = self.mock_retriever
        memory.vector_store = self.mock_vector_store
        
        # Store original llm to restore it later
        self.original_llm = memory.llm if hasattr(memory, 'llm') else None
        # Set the mock llm on memory to ensure it's used
        memory.llm = self.mock_chat_instance
        
    def tearDown(self):
        """Clean up patches"""
        self.patcher_chat.stop()
        memory.vector_store = self.original_vector_store # Restore original vector_store
        # Reset any direct mocks on memory.retrieval_qa if made by a test
        if hasattr(self, '_original_memory_retrieval_qa_method'):
            memory.retrieval_qa = self._original_memory_retrieval_qa_method
            del self._original_memory_retrieval_qa_method
        
    def test_standard_retrieval_qa(self):
        """Test standard RetrievalQA with direct method call"""
        # Set up relevant documents for the retriever
        self.mock_retriever.get_relevant_documents.return_value = [
            type('Document', (), {'page_content': 'The system uses JWT for authentication.'})
        ]
        
        # Use our RunnableChainMock instead of a regular MagicMock
        mock_qa_chain_instance = RunnableChainMock()
        mock_qa_chain_instance.invoke.return_value = {"result": "Authentication is handled via JWT tokens."}

        with patch('tools.memory_engine.RetrievalQA.from_chain_type', return_value=mock_qa_chain_instance) as mock_from_chain_type:
            result = memory.retrieval_qa(
                "How is authentication handled?",
                use_conversation=False,
                temperature=0,
                user="test_user_standard" 
            )
            self.assertEqual(result, "Authentication is handled via JWT tokens.")
            mock_from_chain_type.assert_called_once()
            self.mock_vector_store.as_retriever.assert_called_once()
            # Verify invoke was called with the right parameters
            mock_qa_chain_instance.invoke.assert_called_once()
            call_args = mock_qa_chain_instance.invoke.call_args[0][0]
            self.assertEqual(call_args["query"], "How is authentication handled?")

    def test_conversation_retrieval_qa(self):
        """Test ConversationalRetrievalChain mode"""
        # Set up relevant documents for the retriever
        self.mock_retriever.get_relevant_documents.return_value = [
            type('Document', (), {'page_content': 'The orders table has RLS rules.'})
        ]
        
        # Use our RunnableChainMock for conversation chain
        mock_conv_chain_instance = RunnableChainMock()
        mock_conv_chain_instance.invoke.return_value = {"answer": "The orders table has RLS rules that restrict users to only see their own orders."}
        
        with patch('langchain.chains.ConversationalRetrievalChain.from_llm', return_value=mock_conv_chain_instance) as mock_from_llm:
            result = memory.retrieval_qa(
                "What are the Supabase RLS rules for the orders table?",
                use_conversation=True,
                temperature=0,
                user="test_user_conv"
            )
            self.assertEqual(result, "The orders table has RLS rules that restrict users to only see their own orders.")
            mock_from_llm.assert_called_once()
            self.mock_vector_store.as_retriever.assert_called_once()
            # Verify invoke was called with the right parameters
            mock_conv_chain_instance.invoke.assert_called_once()
            call_args = mock_conv_chain_instance.invoke.call_args[0][0]
            self.assertEqual(call_args["question"], "What are the Supabase RLS rules for the orders table?")
    
    def test_metadata_filtering(self):
        """Test metadata filtering with RetrievalQA"""
        # Set up relevant documents for the retriever
        self.mock_retriever.get_relevant_documents.return_value = [
            type('Document', (), {'page_content': 'The orders table has RLS rules.'})
        ]
        
        # Use our RunnableChainMock
        mock_qa_chain_instance = RunnableChainMock()
        mock_qa_chain_instance.invoke.return_value = {"result": "The orders table has RLS rules."}
        
        metadata_filter = {"domain": "database", "type": "security"}
        
        with patch('langchain.chains.RetrievalQA.from_chain_type', return_value=mock_qa_chain_instance):
            result = memory.retrieval_qa(
                "What are the RLS rules?",
                use_conversation=False,
                metadata_filter=metadata_filter,
                temperature=0,
                user="test_user_filter"
            )
            
            # Default k value might come from MemoryEngineConfig.retrieval.k
            # Assuming a default k, e.g., 5, if not specified or easily accessible here.
            # You might need to access memory.config.retrieval.k if it's set.
            expected_k = getattr(getattr(memory.config, 'retrieval', MagicMock()), 'k', 5)

            self.mock_vector_store.as_retriever.assert_called_once_with(
                search_type="similarity", 
                search_kwargs={"k": expected_k, "filter": metadata_filter}
            )
            self.assertEqual(result, "The orders table has RLS rules.")

    def test_helper_function(self):
        """Test the get_answer helper function"""
        # Store original method if not already done by a broader mechanism
        if not hasattr(self, '_original_memory_retrieval_qa_method'):
             self._original_memory_retrieval_qa_method = memory.retrieval_qa

        memory.retrieval_qa = MagicMock(return_value="Helper function test successful")
        
        result1 = get_answer("Basic question")
        result2 = get_answer("Conversation question", use_conversation=True)
        result3 = get_answer("Filtered question", metadata_filter={"domain": "security"})
        result4 = get_answer("User question", user="specific_user_helper")

        memory.retrieval_qa.assert_any_call("Basic question", use_conversation=False, metadata_filter=None, temperature=0.0, user=None, chat_history=None)
        memory.retrieval_qa.assert_any_call("Conversation question", use_conversation=True, metadata_filter=None, temperature=0.0, user=None, chat_history=None)
        memory.retrieval_qa.assert_any_call("Filtered question", use_conversation=False, metadata_filter={"domain": "security"}, temperature=0.0, user=None, chat_history=None)
        memory.retrieval_qa.assert_any_call("User question", use_conversation=False, metadata_filter=None, temperature=0.0, user="specific_user_helper", chat_history=None)

        self.assertEqual(result1, "Helper function test successful")
        self.assertEqual(result2, "Helper function test successful")
        self.assertEqual(result3, "Helper function test successful")
        self.assertEqual(result4, "Helper function test successful")
        
if __name__ == '__main__':
    unittest.main()
