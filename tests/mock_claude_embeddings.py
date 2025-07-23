"""
Mock Claude Embeddings for Testing

Provides deterministic embeddings for testing purposes, ensuring
consistent test results while maintaining Claude interface compatibility.
"""

import hashlib
import logging
from typing import List

logger = logging.getLogger(__name__)


class MockClaudeEmbeddings:
    """
    Mock Claude embeddings that generate deterministic vectors for testing.
    
    This class ensures test stability by providing consistent embeddings
    based on text content hashing, while maintaining compatibility with
    the actual Claude embeddings interface.
    """
    
    def __init__(self, dimensions: int = 1536):
        """
        Initialize mock Claude embeddings.
        
        Args:
            dimensions: Number of dimensions for embeddings (default: 1536 for OpenAI compatibility)
        """
        self.dimensions = dimensions
        logger.info(f"Initialized MockClaudeEmbeddings with {dimensions} dimensions")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate mock embeddings for multiple documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        return [self._generate_deterministic_embedding(text) for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate mock embedding for a single query.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        return self._generate_deterministic_embedding(text)
    
    def _generate_deterministic_embedding(self, text: str) -> List[float]:
        """
        Generate a deterministic embedding for consistent testing.
        
        This method creates reproducible embeddings based on text content,
        ensuring test stability while maintaining the correct interface.
        
        Args:
            text: Input text
            
        Returns:
            Deterministic embedding vector
        """
        # Create a hash of the text for deterministic generation
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        # Convert hash to embedding vector
        embedding = []
        hash_int = int(text_hash, 16)
        
        for i in range(self.dimensions):
            # Generate values between -1 and 1
            value = ((hash_int >> (i % 128)) & 0xFF) / 255.0 * 2.0 - 1.0
            embedding.append(value)
        
        # Normalize the vector to unit length (like OpenAI embeddings)
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    def health_check(self) -> bool:
        """
        Perform a health check on the mock embeddings.
        
        Returns:
            Always True for mock implementation
        """
        return True
    
    def clear_cache(self) -> None:
        """Clear any cached embeddings (no-op for mock)."""
        pass
    
    def get_performance_metrics(self) -> dict:
        """Get mock performance metrics."""
        return {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
        }


# Compatibility alias for tests that expect specific naming
MockEmbeddings = MockClaudeEmbeddings