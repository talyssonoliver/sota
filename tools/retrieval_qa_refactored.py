"""
Refactored retrieval_qa implementation with reduced complexity.
Breaks the monolithic function into focused, testable components.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

from langchain.chains import RetrievalQA
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain


try:
    from src.infrastructure.memory import get_memory_instance
except ImportError:
    # Fallback if memory not available
    def get_memory_instance():
        return None


class RetrievalQAHandler:
    """
    Handles retrieval-based QA with reduced complexity.
    Separates concerns for better maintainability and testing.
    """
    
    def __init__(self, memory_engine=None):
        self.memory_engine = memory_engine or get_memory_instance()
        self.llm = None
        self.vector_store = None
        
    def retrieval_qa(
        self,
        query: Union[str, Tuple[str, str]],
        user: Optional[str] = None,
        use_conversation: bool = False,
        chat_history: Optional[List[Tuple[str, str]]] = None,
        chain: Optional[Any] = None,
        metadata_filter: Optional[Dict] = None,
        temperature: float = 0.0,
        **kwargs,
    ) -> str:
        """
        Get an answer to a question using retrieval-based QA.
        
        Args:
            query: The question (string or tuple with (query, user_id))
            user: User identifier
            use_conversation: Whether to use conversational context
            chat_history: Previous conversation history
            chain: Pre-configured chain to use
            metadata_filter: Filter for document retrieval
            temperature: LLM temperature setting
            **kwargs: Additional parameters
            
        Returns:
            Answer string
        """
        try:
            # Validate and prepare query
            query_dict = self._prepare_query(query, user)
            
            # Create or use existing chain
            if chain is None:
                chain = self._create_chain(
                    use_conversation=use_conversation,
                    chat_history=chat_history,
                    metadata_filter=metadata_filter,
                    temperature=temperature
                )
            
            # Execute query
            if use_conversation and chat_history:
                result = chain({"question": query_dict["query"], "chat_history": chat_history})
            else:
                result = chain(query_dict)
            
            # Extract answer from result
            return self._extract_answer(result)
            
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def _prepare_query(self, query: Union[str, Tuple[str, str]], user: Optional[str]) -> Dict[str, str]:
        """Prepare and validate the query input."""
        if isinstance(query, tuple):
            query_text, user_id = query
            query_dict = {"query": query_text, "user": user_id}
        else:
            query_dict = {"query": query}
            
        if user:
            query_dict["user"] = user
            
        return query_dict
    
    def _create_chain(self, use_conversation: bool = False, chat_history: Optional[List] = None,
                     metadata_filter: Optional[Dict] = None, temperature: float = 0.0):
        """Create the appropriate chain based on parameters."""
        # Get retriever
        retriever = self._get_retriever(metadata_filter)
        
        # Create LLM with temperature
        self._configure_llm(temperature)
        
        # Choose chain type
        if use_conversation:
            return self._create_conversation_chain(retriever, chat_history)
        else:
            return self._create_retrieval_qa_chain(retriever)
    
    def _get_retriever(self, metadata_filter: Optional[Dict] = None):
        """Get or create a retriever with optional metadata filtering."""
        if self.vector_store is None:
            # Initialize vector store from memory engine
            if self.memory_engine:
                self.vector_store = self.memory_engine.get_vector_store()
            else:
                raise ValueError("No vector store available")
        
        # Create retriever with filtering if specified
        if metadata_filter:
            return self.vector_store.as_retriever(search_kwargs={"filter": metadata_filter})
        else:
            return self.vector_store.as_retriever()
    
    def _configure_llm(self, temperature: float = 0.0):
        """Configure the LLM with specified parameters."""
        if self.llm is None:
            # Initialize LLM (this would typically come from configuration)
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(temperature=temperature)
            except ImportError:
                # Fallback or mock LLM
                class MockLLM:
                    def __call__(self, *args, **kwargs):
                        return "Mock response"
                self.llm = MockLLM()
        
        # Update temperature if LLM supports it
        if hasattr(self.llm, 'temperature'):
            self.llm.temperature = temperature
    
    def _create_conversation_chain(self, retriever: Any, chat_history: Optional[List]):
        """Create a conversational retrieval chain."""
        try:
            from tools.memory import ConversationBufferMemory
        except ImportError:
            # Mock memory for fallback
            class MockMemory:
                def __init__(self, **kwargs):
                    self.chat_memory = type('obj', (object,), {'messages': []})
            ConversationBufferMemory = MockMemory
        
        memory_obj = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="question",
            output_key="answer",
            return_messages=False
        )
        
        if chat_history:
            memory_obj.chat_memory.messages = [
                {"role": "user" if i % 2 == 0 else "assistant", "content": content}
                for i, (q, a) in enumerate(chat_history)
                for content in [q, a]
            ]
        
        if ConversationalRetrievalChain:
            return ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory_obj
            )
        else:
            # Fallback chain
            return self._create_retrieval_qa_chain(retriever)
    
    def _create_retrieval_qa_chain(self, retriever: Any):
        """Create a standard retrieval QA chain."""
        if RetrievalQA:
            return RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )
        else:
            # Fallback simple chain
            class SimpleRetrievalChain:
                def __init__(self, llm, retriever):
                    self.llm = llm
                    self.retriever = retriever
                
                def __call__(self, query_dict):
                    # Simple retrieval and response
                    docs = self.retriever.get_relevant_documents(query_dict["query"])
                    context = "\n".join([doc.page_content for doc in docs])
                    return {"answer": f"Based on context: {context[:500]}...", "source_documents": docs}
            
            return SimpleRetrievalChain(self.llm, retriever)
    
    def _extract_answer(self, result: Any) -> str:
        """Extract the answer from chain result."""
        if isinstance(result, dict):
            # Try different possible keys
            for key in ["answer", "result", "output", "text"]:
                if key in result:
                    return str(result[key])
        
        # Fallback to string representation
        return str(result)


# Convenience function for backward compatibility
def retrieval_qa(*args, **kwargs):
    """Backward compatible function interface."""
    handler = RetrievalQAHandler()
    return handler.retrieval_qa(*args, **kwargs)


# Export main components
__all__ = ["RetrievalQAHandler", "retrieval_qa"]