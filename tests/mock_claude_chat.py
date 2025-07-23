"""
Mock Claude Chat Model for Testing

Provides deterministic chat responses for testing purposes, ensuring
consistent test results while maintaining Claude interface compatibility.
"""

import logging
from typing import Any, Dict, Iterator, List, Optional

try:
    from langchain.schema import BaseMessage, ChatResult, ChatGeneration, AIMessage, HumanMessage, SystemMessage
    from langchain.schema.messages import ChatMessage
    from langchain.callbacks.manager import CallbackManagerForLLMRun
    from langchain.schema.output import ChatGenerationChunk
except ImportError:
    try:
        from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage, ChatMessage
        from langchain_core.outputs import ChatResult, ChatGeneration, ChatGenerationChunk
        from langchain_core.callbacks.manager import CallbackManagerForLLMRun
    except ImportError:
        # Fallback for testing/development
        class BaseMessage:
            def __init__(self, content=""):
                self.content = content
        class ChatResult:
            def __init__(self, generations=None):
                self.generations = generations or []
        class ChatGeneration:
            def __init__(self, message=None):
                self.message = message
        class AIMessage(BaseMessage):
            pass
        class HumanMessage(BaseMessage):
            pass
        class SystemMessage(BaseMessage):
            pass
        class ChatMessage(BaseMessage):
            def __init__(self, content="", role="user"):
                super().__init__(content)
                self.role = role
        class CallbackManagerForLLMRun:
            pass
        class ChatGenerationChunk:
            def __init__(self, message=None):
                self.message = message

logger = logging.getLogger(__name__)


class MockClaudeChatModel:
    """
    Mock Claude chat model that generates deterministic responses for testing.
    
    This class ensures test stability by providing consistent responses
    based on input patterns, while maintaining compatibility with
    the actual Claude chat model interface.
    """
    
    def __init__(self, temperature: float = 0.7, max_tokens: int = 4096):
        """
        Initialize mock Claude chat model.
        
        Args:
            temperature: Sampling temperature (ignored in mock)
            max_tokens: Maximum tokens to generate (ignored in mock)
        """
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.conversation_history = []
        logger.info(f"Initialized MockClaudeChatModel with temp={temperature}")
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for this LLM type."""
        return "mock_claude_chat"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get identifying parameters for this model."""
        return {
            "model": "mock-claude-3-sonnet",
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Generate mock chat completion.
        
        Args:
            messages: List of messages in the conversation
            stop: List of stop sequences (ignored in mock)
            run_manager: Callback manager for the run (ignored in mock)
            **kwargs: Additional generation parameters (ignored in mock)
            
        Returns:
            Chat result with generated message
        """
        # Extract the last user message for response generation
        last_message = messages[-1] if messages else None
        user_input = last_message.content if last_message else "Hello"
        
        # Generate deterministic response based on input
        response_content = self._generate_mock_response(user_input)
        
        # Create AI message and generation
        ai_message = AIMessage(content=response_content)
        generation = ChatGeneration(message=ai_message)
        
        # Update conversation history
        self.conversation_history.extend(messages)
        self.conversation_history.append(ai_message)
        
        return ChatResult(generations=[generation])
    
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """
        Stream mock chat completion.
        
        Args:
            messages: List of messages in the conversation
            stop: List of stop sequences (ignored in mock)
            run_manager: Callback manager for the run (ignored in mock)
            **kwargs: Additional generation parameters (ignored in mock)
            
        Yields:
            Chat generation chunks
        """
        # Generate full response and split into chunks
        result = self._generate(messages, stop, run_manager, **kwargs)
        if result.generations:
            content = result.generations[0].message.content
            
            # Split into word chunks for streaming simulation
            words = content.split()
            chunk_size = 3  # Words per chunk
            
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_content = " ".join(chunk_words)
                if i + chunk_size < len(words):
                    chunk_content += " "
                
                chunk = ChatGenerationChunk(message=AIMessage(content=chunk_content))
                yield chunk
    
    def _generate_mock_response(self, user_input: str) -> str:
        """
        Generate a mock response based on user input patterns.
        
        Args:
            user_input: User's input message
            
        Returns:
            Mock response content
        """
        user_lower = user_input.lower()
        
        # Pattern-based responses for testing consistency
        if "hello" in user_lower or "hi" in user_lower:
            return "Hello! I'm Claude, your AI assistant. How can I help you today?"
        elif "how are you" in user_lower:
            return "I'm doing well, thank you for asking! I'm here to help with any questions or tasks you have."
        elif "name" in user_lower:
            return "I'm Claude, an AI assistant created by Anthropic."
        elif "help" in user_lower:
            return "I'd be happy to help! What would you like assistance with?"
        elif "code" in user_lower or "program" in user_lower:
            return "I can help with coding and programming tasks. What specific problem are you working on?"
        elif "explain" in user_lower:
            return "I'd be glad to explain that for you. Could you provide more details about what you'd like me to explain?"
        elif "test" in user_lower:
            return "This is a test response from the mock Claude chat model. All systems are functioning correctly."
        elif "health" in user_lower and "check" in user_lower:
            return "Health check successful. Mock Claude chat model is operational."
        elif "error" in user_lower:
            return "I understand you're experiencing an error. Let me help you troubleshoot the issue."
        elif "api" in user_lower:
            return "I can help with API-related questions and implementation details."
        else:
            # Default response with input echo for test predictability
            return f"I understand you're asking about: {user_input[:100]}{'...' if len(user_input) > 100 else ''}. How can I help you with this topic?"
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history.clear()
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def health_check(self) -> bool:
        """
        Perform a health check on the mock chat model.
        
        Returns:
            Always True for mock implementation
        """
        return True
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get mock performance metrics."""
        return {
            'total_requests': len(self.conversation_history) // 2,  # Approximate
            'successful_requests': len(self.conversation_history) // 2,
            'failed_requests': 0,
            'average_response_time': 0.1,  # Mock fast response time
        }


# Compatibility alias for tests that expect specific naming
MockChatModel = MockClaudeChatModel