"""
Fixtures for LangChain components testing.
These fixtures provide proper mock objects for LangChain components.
"""

import os
from unittest.mock import patch, MagicMock
import sys

# Use our fixed runnable mocks that properly handle return_value
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    # Try to import from the fixed_runnable_mock module first
    from tests.fixtures.fixed_runnable_mock import RunnableLLMMock, RunnableChainMock
except ImportError:
    # Fall back to the test_environment if fixed mocks aren't available
    from test_environment import RunnableLLMMock, RunnableChainMock

class FakeChatMemory:
    """Mock for chat memory with properly structured chat history"""
    
    def __init__(self, chat_history=None):
        self.chat_history = chat_history or []
        
    def load_memory_variables(self, _):
        """Return chat history in the format expected by LangChain"""
        return {"chat_history": self.chat_history}
    
    def save_context(self, inputs, outputs):
        """Save a message exchange to chat history"""
        self.chat_history.append((inputs.get("input", ""), outputs.get("output", "")))

def create_test_file(content, file_path=None):
    """Create a test file with the specified content"""
    if file_path is None:
        # Default location for test files
        file_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "context-store", "test_doc.md")
        
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write content to file
    with open(file_path, "w") as f:
        f.write(content)
        
    return file_path

class LangChainMockFixture:
    """Fixture for mocking LangChain components"""
    def __init__(self):
        """Initialize with default mocks"""
        # Use RunnableChainMock for RetrievalQA and ConversationalRetrievalChain
        self.mock_llm = RunnableLLMMock()
        self.mock_qa_chain = RunnableChainMock()
        self.mock_conv_chain = RunnableChainMock()
        # .invoke returns .invoke.return_value if set, else default, and handles tuple args
        def qa_invoke(input, *a, **kw):
            if hasattr(self.mock_qa_chain.invoke, 'return_value') and self.mock_qa_chain.invoke.return_value is not None:
                return self.mock_qa_chain.invoke.return_value
            query = input.get('query', input)
            if isinstance(query, tuple):
                query = query[0]
            return {"result": f"Mock answer for: {query}"}
        def conv_invoke(input, *a, **kw):
            if hasattr(self.mock_conv_chain.invoke, 'return_value') and self.mock_conv_chain.invoke.return_value is not None:
                return self.mock_conv_chain.invoke.return_value
            question = input.get('question', input)
            if isinstance(question, tuple):
                question = question[0]
            return {"answer": f"Mock answer for: {question}"}
        # Set .invoke as MagicMock with side_effect for proper test assertions
        from unittest.mock import MagicMock
        self.mock_qa_chain.invoke = MagicMock(side_effect=qa_invoke)
        self.mock_conv_chain.invoke = MagicMock(side_effect=conv_invoke)

        # Create mock for from_chain_type
        mock_from_chain_type = MagicMock(return_value=self.mock_qa_chain)
        mock_from_llm = MagicMock(return_value=self.mock_conv_chain)

        self.mocks = {
            'ChatOpenAI': MagicMock(return_value=self.mock_llm),
            'Chroma': MagicMock(),
            'RetrievalQA': MagicMock(side_effect=lambda *a, **kw: self.mock_qa_chain),
            'ConversationalRetrievalChain': MagicMock(side_effect=lambda *a, **kw: self.mock_conv_chain),
            'from_chain_type': mock_from_chain_type,
            'from_llm': mock_from_llm,
        }

        # Add the from_chain_type method to the RetrievalQA mock
        self.mocks['RetrievalQA'].from_chain_type = mock_from_chain_type
        
        # Add the from_llm method to the ConversationalRetrievalChain mock
        self.mocks['ConversationalRetrievalChain'].from_llm = mock_from_llm
    
        self.patchers = []
            
        def apply(self):
            """Apply all patches and return self as context manager"""
        patch_targets = {
            'ChatOpenAI': 'tools.memory_engine.ChatOpenAI',
            'Chroma': 'tools.memory_engine.Chroma',
            'RetrievalQA': 'langchain.chains.RetrievalQA',
            'ConversationalRetrievalChain': 'langchain.chains.ConversationalRetrievalChain',
            'from_chain_type': 'langchain.chains.RetrievalQA.from_chain_type',
            'from_llm': 'langchain.chains.ConversationalRetrievalChain.from_llm',
        }
        
        # Apply each patch and keep track of patchers
        for key, target in patch_targets.items():
            patcher = patch(target, self.mocks[key])
            self.patchers.append(patcher)
            patcher.start()
        return self

    def __enter__(self):
        return self.mocks

    def __exit__(self, exc_type, exc_val, exc_tb):
        for patcher in self.patchers:
            patcher.stop()
        self.patchers = []

    def replace_memory_vector_store(self, memory):
        original_vector_store = memory.vector_store
        memory.vector_store = self.mocks['Chroma']
        def restore_vector_store():
            memory.vector_store = original_vector_store
        return restore_vector_store
