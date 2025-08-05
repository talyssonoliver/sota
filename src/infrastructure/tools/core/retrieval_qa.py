
from src.infrastructure.utils.common_imports import logging
"""
Retrieval QA Tool

Provides question-answering capabilities using retrieval-augmented generation (RAG)
with support for conversational context and metadata filtering.
"""

# import logging  # Consolidated to common_imports
from typing import Any, Dict, List, Optional, Tuple

# External dependencies with error handling
try:
    from langchain.chains import ConversationalRetrievalChain, RetrievalQA

    LANGCHAIN_CHAINS_AVAILABLE = True
except ImportError as e:
    logging.error(f"LangChain chains not available: {e}")
    LANGCHAIN_CHAINS_AVAILABLE = False

    # Create mock classes
    class ConversationalRetrievalChain:
        @staticmethod
        def from_llm(*args, **kwargs):
            logging.error("ConversationalRetrievalChain not available - using mock")
            return MockChain()

    class RetrievalQA:
        @staticmethod
        def from_llm(*args, **kwargs):
            logging.error("RetrievalQA not available - using mock")
            return MockChain()


try:
    from langchain_core.runnables import RunnableParallel, RunnablePassthrough

    LANGCHAIN_CORE_AVAILABLE = True
except ImportError as e:
    logging.error(f"LangChain core runnables not available: {e}")
    LANGCHAIN_CORE_AVAILABLE = False

    class RunnableParallel:
        def __init__(self, *args, **kwargs):
            pass

    class RunnablePassthrough:
        def __init__(self, *args, **kwargs):
            pass


try:
    from langchain_openai import ChatOpenAI

    OPENAI_AVAILABLE = True
except ImportError as e:
    logging.error(f"LangChain OpenAI not available: {e}")
    OPENAI_AVAILABLE = False

    class ChatOpenAI:
        def __init__(self, *args, **kwargs):
            pass


# Local imports with error handling
try:
    from src.infrastructure.memory import get_memory_instance

    MEMORY_AVAILABLE = True
except ImportError as e:
    logging.error(f"Memory module not available: {e}")
    MEMORY_AVAILABLE = False

    def get_memory_instance():
        logging.error("Memory not available - using mock")
        return MockMemory()


class MockChain:
    def run(self, *args, **kwargs):
        return {"answer": "Service unavailable - required dependencies not installed"}


class MockMemory:
    def get_retriever(self, *args, **kwargs):
        logging.error("Memory retriever not available")
        return None

    def retrieval_qa(self, *args, **kwargs):
        logging.error("Memory retrieval_qa not available")
        return "Service unavailable - memory not available"


logger = logging.getLogger(__name__)


def get_answer(
    question: str,
    use_conversation: bool = False,
    metadata_filter: Optional[Dict[str, Any]] = None,
    temperature: float = 0.0,
    user: Optional[str] = None,
    chat_history: Optional[List[Tuple[str, str]]] = None,
):
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
        # Get memory instance dynamically so patches work correctly
        memory = get_memory_instance()
        return memory.retrieval_qa(
            question,
            use_conversation=use_conversation,
            metadata_filter=metadata_filter,
            temperature=temperature,
            user=user,
            chat_history=chat_history,
        )
    except Exception as e:
        logger.error(f"Error getting answer: {e}")
        return f"Error retrieving answer: {str(e)}"
