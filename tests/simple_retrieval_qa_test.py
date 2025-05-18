"""
Unit Test for the RetrievalQA functionality in MemoryEngine
Tests that the retrieval_qa method is properly implemented.
"""
import unittest
from unittest.mock import patch, MagicMock

class TestRetrievalQA(unittest.TestCase):
    
    @patch('langchain.chains.retrieval_qa.base.RetrievalQA')
    @patch('langchain_openai.ChatOpenAI')
    def test_retrieval_qa_functionality(self, mock_chat_openai, mock_retrieval_qa):
        """Test that the retrieval_qa method is properly implemented"""
        # Import here to avoid dependency issues before patching
        from tools.memory_engine import get_answer
        
        # Set up mock chain
        mock_chain = MagicMock()
        mock_retrieval_qa.from_chain_type.return_value = mock_chain
        mock_chain.return_value = {"result": "The orders table has RLS rules that restrict users to only see their own orders."}
        
        # Mock the memory singleton instance
        with patch('tools.memory_engine.memory') as mock_memory:
            mock_memory.retrieval_qa.return_value = "The orders table has RLS rules that restrict users to only see their own orders."
            
            query = "What are the Supabase RLS rules for the orders table?"
            # Test the get_answer helper function
            result = get_answer(query)
            
            # Verify the helper function calls through to retrieval_qa
            mock_memory.retrieval_qa.assert_called_once_with(
                query,
                use_conversation=False,
                metadata_filter=None,
                temperature=0.0,
                user=None,
                chat_history=None
            )
            self.assertEqual(result, "The orders table has RLS rules that restrict users to only see their own orders.")
        
if __name__ == '__main__':
    unittest.main()
