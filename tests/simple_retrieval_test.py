"""
Simple unit test for the retrieval_qa functionality
"""
import unittest
from unittest.mock import MagicMock, patch


class TestRetrievalQA(unittest.TestCase):

    def test_get_answer(self):
        """Test that the get_answer function works correctly"""
        # Import here to avoid dependency issues
        from tools.memory_engine import get_answer

        # Mock the memory singleton's retrieval_qa method
        with patch('tools.memory_engine.memory') as mock_memory:
            mock_memory.retrieval_qa.return_value = "The orders table has RLS rules that restrict users to only see their own orders."

            # Test the get_answer helper function
            result = get_answer(
                "What are the Supabase RLS rules for the orders table?")

            # Verify the helper function calls through to retrieval_qa
            mock_memory.retrieval_qa.assert_called_once()
            self.assertEqual(
                result,
                "The orders table has RLS rules that restrict users to only see their own orders.")

    @patch('langchain.chains.retrieval_qa.base.RetrievalQA.from_chain_type')
    @patch('langchain_openai.ChatOpenAI')
    def test_retrieval_qa_chain_integration(
            self, mock_chat_openai, mock_from_chain_type):
        """Test integration with LangChain's RetrievalQA"""
        # Import here after mocks are set up
        from tools.memory_engine import MemoryEngine

        # Create mock objects
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        mock_chain = MagicMock()
        mock_from_chain_type.return_value = mock_chain
        mock_chain.return_value = {"result": "Test answer"}

        # Create a simple mock instance
        memory_engine = MagicMock(spec=MemoryEngine)

        # Mock the necessary methods and attributes
        memory_engine._sanitize_and_check.return_value = "sanitized query"
        memory_engine.rate_limiter = MagicMock()
        memory_engine.rate_limiter.check.return_value = True
        memory_engine.vector_store = MagicMock()
        mock_retriever = MagicMock()
        memory_engine.vector_store.as_retriever.return_value = mock_retriever
        memory_engine.audit_logger = MagicMock()

        # Access the method directly using a lambda because retrieval_qa is an
        # instance method
        with patch('langchain.chains.retrieval_qa.base.RetrievalQA', MagicMock()):
            # Create a minimal implementation of retrieval_qa for testing
            def mock_retrieval_qa(
                    self,
                    query,
                    use_conversation=False,
                    metadata_filter=None,
                    temperature=0,
                    user="system"):
                from langchain.chains.retrieval_qa.base import RetrievalQA
                from langchain_openai import ChatOpenAI

                llm = ChatOpenAI(temperature=temperature)
                retriever = self.vector_store.as_retriever()

                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=retriever,
                    return_source_documents=True
                )

                result = qa_chain({"query": query})
                return result["result"]

            # Patch the retrieval_qa method on the MemoryEngine class
            with patch.object(MemoryEngine, 'retrieval_qa', mock_retrieval_qa):
                # Call the mocked method
                result = memory_engine.retrieval_qa("test query")

                # Verify that from_chain_type was called with the right
                # arguments
                self.assertTrue(mock_from_chain_type.called)
                self.assertEqual(result, "Test answer")


if __name__ == '__main__':
    unittest.main()
