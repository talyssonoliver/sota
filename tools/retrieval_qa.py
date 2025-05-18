from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from .memory_engine import memory
import logging
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

def get_answer(question: str, use_conversation: bool = False, metadata_filter: Optional[Dict[str, Any]] = None, temperature: float = 0.0, user: Optional[str] = None, chat_history: Optional[List[Tuple[str, str]]] = None):
    """
    Helper function to get an answer from the memory engine using retrieval_qa.
    Passes all relevant parameters including defaults for temperature and user.
    
    Args:
        question (str): Question to ask
        use_conversation (bool): Whether to use conversation mode
        metadata_filter (Optional[Dict[str, Any]]): Optional metadata filter
        temperature (float): Temperature for the LLM
        user (Optional[str]): User identifier
        chat_history (Optional[List[tuple[str, str]]]): List of tuples containing chat history pairs
        
    Returns:
        str: Answer to the question
    """
    try:
        return memory.retrieval_qa(
            question,
            use_conversation=use_conversation,
            metadata_filter=metadata_filter,
            temperature=temperature,
            user=user,
            chat_history=chat_history
        )
    except Exception as e:
        logger.error(f"Error getting answer: {e}")
        return f"Error retrieving answer: {str(e)}"
