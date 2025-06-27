"""LangChain conversational retrieval compatibility module."""

class ConversationalRetrievalChain:
    """Mock ConversationalRetrievalChain for compatibility."""
    
    @classmethod
    def from_llm(cls, **kwargs):
        """Mock from_llm method."""
        return cls()
    
    def __call__(self, inputs):
        """Mock call method."""
        query = inputs.get('question', 'No question provided')
        return {
            'answer': f"Mock conversational response for: {query}",
            'chat_history': inputs.get('chat_history', [])
        }

__all__ = ['ConversationalRetrievalChain']
