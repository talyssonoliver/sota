"""LangChain chains compatibility module."""

class RetrievalQA:
    """Mock RetrievalQA for compatibility."""
    
    @classmethod
    def from_chain_type(cls, **kwargs):
        """Mock from_chain_type method."""
        return cls()
    
    def run(self, query):
        """Mock run method."""
        return f"Mock response for query: {query}"

__all__ = ['RetrievalQA', 'retrieval_qa']