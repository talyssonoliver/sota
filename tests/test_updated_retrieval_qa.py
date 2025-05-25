"""
Test for RetrievalQA functionality with updated LangChain imports.
"""
import unittest
from unittest.mock import patch, MagicMock

class TestUpdatedRetrievalQA(unittest.TestCase):
    
    def test_get_answer_helper(self):
        """Test that the get_answer helper function works correctly"""
        # Import here to avoid dependency issues
        from tools.memory_engine import get_answer
        
        # Mock the memory singleton's retrieval_qa method
        with patch('tools.memory_engine.memory') as mock_memory:
            mock_memory.retrieval_qa.return_value = "The orders table has RLS rules that restrict users to only see their own orders."
            
            # Test the get_answer helper function
            result = get_answer("What are the Supabase RLS rules for the orders table?")
              # Verify the helper function calls through to retrieval_qa
            mock_memory.retrieval_qa.assert_called_once_with(
                "What are the Supabase RLS rules for the orders table?",
                use_conversation=False,
                metadata_filter=None,
                temperature=0.0, # Assuming default temperature if not specified
                user=None, # Assuming default user if not specified
                chat_history=None # Include chat_history parameter to match actual call
            )
            self.assertEqual(result, "The orders table has RLS rules that restrict users to only see their own orders.")

    def test_conversation_mode(self):
        """Test the conversation mode of the retrieval_qa method"""
        # Import here to avoid dependency issues
        from tools.memory_engine import get_answer
        
        # Mock the memory singleton's retrieval_qa method
        with patch('tools.memory_engine.memory') as mock_memory:
            mock_memory.retrieval_qa.return_value = "The orders table uses row-level security policies."
            
            # Test the get_answer helper function with conversation mode
            result = get_answer(
                "What security does the orders table use?",
                use_conversation=True
            )
              # Verify the helper function calls through to retrieval_qa with conversation mode
            mock_memory.retrieval_qa.assert_called_once_with(
                "What security does the orders table use?",
                use_conversation=True,
                metadata_filter=None,
                temperature=0.0,
                user=None,
                chat_history=None # Include chat_history parameter to match actual call
            )
            self.assertEqual(result, "The orders table uses row-level security policies.")

    def test_metadata_filtering(self):
        """Test the metadata filtering capability of the retrieval_qa method"""
        # Import here to avoid dependency issues
        from tools.memory_engine import get_answer
        
        # Mock the memory singleton's retrieval_qa method
        with patch('tools.memory_engine.memory') as mock_memory:
            mock_memory.retrieval_qa.return_value = "Authentication is handled via JWT tokens."
            
            # Test the get_answer helper function with metadata filtering
            result = get_answer(
                "How is authentication implemented?",
                metadata_filter={"domain": "security"}
            )
              # Verify the helper function calls through to retrieval_qa with metadata filtering
            mock_memory.retrieval_qa.assert_called_once_with(
                "How is authentication implemented?",
                use_conversation=False,
                metadata_filter={"domain": "security"},
                temperature=0.0,
                user=None,
                chat_history=None # Include chat_history parameter to match actual call
            )
            self.assertEqual(result, "Authentication is handled via JWT tokens.")

if __name__ == '__main__':
    unittest.main()
