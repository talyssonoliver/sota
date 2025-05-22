"""
Mock for OpenAIEmbeddings that returns consistent vector embeddings for testing.
"""
import numpy as np
from unittest.mock import MagicMock

class MockOpenAIEmbeddings:
    """A mock for OpenAIEmbeddings that returns consistent vector embeddings."""
    
    def __init__(self, model="text-embedding-3-small", **kwargs):
        self.model = model
        self.dimension = 1536  # Standard embedding dimension
        self.kwargs = kwargs
        self._embed_query_called = False
        self._embed_documents_called = False
    
    def embed_query(self, text):
        """Return a consistent mock embedding vector for a query text."""
        self._embed_query_called = True
        # Create a deterministic embedding based on the hash of the text
        np.random.seed(hash(text) % 2**32)
        return list(np.random.uniform(-1, 1, self.dimension))
    
    def embed_documents(self, texts):
        """Return consistent mock embedding vectors for document texts."""
        self._embed_documents_called = True
        results = []
        for text in texts:
            # Create a deterministic embedding based on the hash of the text
            np.random.seed(hash(text) % 2**32)
            results.append(list(np.random.uniform(-1, 1, self.dimension)))
        return results
    
    def was_embed_query_called(self):
        return self._embed_query_called
    
    def was_embed_documents_called(self):
        return self._embed_documents_called

def create_mock_openai_embeddings():
    """Create and configure a MagicMock for OpenAIEmbeddings with appropriate behavior."""
    mock_embeddings = MagicMock()
    mock_instance = MockOpenAIEmbeddings()
    
    # Set up the mock to return our MockOpenAIEmbeddings instance
    mock_embeddings.return_value = mock_instance
    
    # Set up the instance methods
    mock_embeddings.return_value.embed_query = mock_instance.embed_query
    mock_embeddings.return_value.embed_documents = mock_instance.embed_documents
    
    return mock_embeddings, mock_instance
