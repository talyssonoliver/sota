"""
Fixed implementation of retrieval_qa method to handle different parameter formats.
"""

from typing import Dict, Any, List, Optional, Tuple
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

def retrieval_qa(
    self,
    query: Any,
    use_conversation: bool = False,
    metadata_filter: Optional[Dict[str, Any]] = None,
    temperature: float = 0.0,
    user: Optional[str] = None,
    chat_history: Optional[List[Tuple[str, str]]] = None,
    **kwargs,
):
    """
    Get an answer to a question using either standard RetrievalQA or ConversationalRetrievalChain.
    This version handles both string and tuple formats for query parameter.
    
    Args:
        query: The question to ask (string or tuple with (query, user_id))
        use_conversation: Whether to use ConversationalRetrievalChain instead of RetrievalQA
        metadata_filter: Optional filter to apply on document metadata
        temperature: Temperature for response generation (0-1)
        user: User identifier for access control
        chat_history: Optional conversation history as list of (question, answer) tuples
        **kwargs: Additional keyword arguments to pass to the chain
        
    Returns:
        str: The answer to the question
    """
    try:
        # Handle query parameter that could be a string or tuple
        query_str = query
        if isinstance(query, tuple):
            query_str = query[0]  # Extract just the query string
            if user is None and len(query) > 1:
                user = query[1]  # Use the user_id from the tuple if not explicitly provided
            
        # Sanitize and check permissions
        query_str = self._sanitize_and_check(query_str, user, "read")
        
        # Enforce rate limiting
        if not self.rate_limiter.allow():
            return "Rate limit exceeded. Please try again later."
        
        # Make sure we have an LLM instance to use
        if not hasattr(self, 'llm') or self.llm is None:
            self.llm = ChatOpenAI(temperature=temperature, model_name="gpt-3.5-turbo-16k")
        elif temperature != 0.0:
            # Use the requested temperature if different from default
            self.llm = ChatOpenAI(temperature=temperature, model_name="gpt-3.5-turbo-16k")
        
        # Default k value for retriever
        k = kwargs.get("k", 5)
        
        # Configure search kwargs based on metadata filter
        search_kwargs = {"k": k}
        if metadata_filter:
            search_kwargs["filter"] = metadata_filter
        
        # Get retriever with the right configuration
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs
        )
        
        # Log the retrieval attempt
        self.audit_logger.log(
            who=user or "system",
            what="retrieve",
            how="qa" if not use_conversation else "conversation",
            resource="vector_store",
            success=True
        )
        
        if not use_conversation:
            # Standard retrieval QA
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )
            
            # Execute the chain with the normalized query string
            result = qa_chain.invoke({"query": query_str})
            return result["result"]
        else:
            # Conversational retrieval chain
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Add chat history to memory if provided
            if chat_history:
                for question, answer in chat_history:
                    memory.chat_memory.add_user_message(question)
                    memory.chat_memory.add_ai_message(answer)
            
            # Create conversational chain
            conv_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory
            )
            
            # Execute the chain with history
            result = conv_chain.invoke({"question": query_str, "chat_history": chat_history or []})
            return result["answer"]
            
    except Exception as e:
        self.logger.error(f"Error in retrieval_qa: {str(e)}")
        return f"Error retrieving answer: {str(e)}"

