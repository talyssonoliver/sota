"""
Final simple test for RetrievalQA functionality in MemoryEngine.
"""
import unittest
from unittest.mock import patch, MagicMock

class TestRetrievalQA(unittest.TestCase):
    
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
                temperature=0.0,
                user=None,
                chat_history=None
            )
            self.assertEqual(result, "The orders table has RLS rules that restrict users to only see their own orders.")

if __name__ == '__main__':
    unittest.main()
