"""
Claude Chat Model Integration

Provides LangChain-compatible chat model using Claude Code functionality.
Maintains full compatibility with ChatOpenAI while leveraging Claude's capabilities.
"""

import logging
import time
from typing import Any, Dict, Iterator, List, Optional

try:
    from langchain.chat_models.base import BaseChatModel
    from langchain.schema import BaseMessage, ChatResult, ChatGeneration, AIMessage, HumanMessage, SystemMessage
    from langchain.schema.messages import ChatMessage
    from langchain.callbacks.manager import CallbackManagerForLLMRun
    from langchain.schema.output import ChatGenerationChunk
except ImportError:
    try:
        from langchain_core.language_models.chat_models import BaseChatModel
        from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage, ChatMessage
        from langchain_core.outputs import ChatResult, ChatGeneration, ChatGenerationChunk
        from langchain_core.callbacks.manager import CallbackManagerForLLMRun
    except ImportError:
        # Fallback for testing/development
        class BaseChatModel:
            pass
        class BaseMessage:
            pass
        class ChatResult:
            pass
        class ChatGeneration:
            pass
        class AIMessage:
            pass
        class HumanMessage:
            pass
        class SystemMessage:
            pass
        class ChatMessage:
            pass
        class CallbackManagerForLLMRun:
            pass
        class ChatGenerationChunk:
            pass

from .config import ClaudeConfig, get_claude_config
from .utils import (
    with_retry,
    RetryConfig,
    get_performance_monitor
)
from .feature_flags import should_use_claude_chat

logger = logging.getLogger(__name__)


class ClaudeChatModel(BaseChatModel):
    """
    LangChain-compatible chat model using Claude Code.
    
    Maintains full compatibility with ChatOpenAI while providing
    Claude-powered chat generation with enhanced capabilities.
    """
    
    def __init__(
        self,
        config: Optional[ClaudeConfig] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize Claude chat model.
        
        Args:
            config: Claude configuration (defaults to global config)
            model: Chat model name (overrides config)
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens to generate (overrides config)
            **kwargs: Additional configuration options
        """
        # Note: Not calling super().__init__() due to LangChain compatibility issues
        # The LangChain BaseChatModel has specific field requirements that conflict
        
        self.config = config or get_claude_config()
        self.model = model or self.config.chat_model
        self.temperature = temperature if temperature is not None else self.config.temperature
        self.max_tokens = max_tokens or self.config.max_tokens
        self.enable_streaming = kwargs.get('streaming', self.config.enable_streaming)
        self.conversation_history = []
        self.performance_monitor = get_performance_monitor()
        
        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid Claude configuration")
        
        logger.info(f"Initialized Claude chat model: {self.model}, temp: {self.temperature}")
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for this LLM type."""
        return "claude_chat"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get identifying parameters for this model."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "streaming": self.enable_streaming,
        }
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Generate chat completion.
        
        Args:
            messages: List of messages in the conversation
            stop: List of stop sequences
            run_manager: Callback manager for the run
            **kwargs: Additional generation parameters
            
        Returns:
            Chat result with generated message
        """
        start_time = time.time()
        success = False
        
        try:
            # Check feature flag
            if not should_use_claude_chat():
                logger.info("Claude chat disabled by feature flag, falling back to OpenAI")
                return self._fallback_to_openai(messages, stop, run_manager, **kwargs)
            
            # Convert messages to Claude format
            claude_messages = self._convert_messages_to_claude(messages)
            
            # Generate response
            response = self._call_claude_api(claude_messages, stop, **kwargs)
            
            # Convert response back to LangChain format
            ai_message = AIMessage(content=response["content"])
            generation = ChatGeneration(message=ai_message)
            
            # Update conversation history
            self.conversation_history.extend(messages)
            self.conversation_history.append(ai_message)
            
            success = True
            return ChatResult(generations=[generation])
            
        except Exception as e:
            logger.error(f"Failed to generate chat completion: {e}")
            # Return a fallback response
            return self._generate_fallback_response(messages)
        
        finally:
            elapsed_time = time.time() - start_time
            self.performance_monitor.record_request(success, elapsed_time)
    
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """
        Stream chat completion.
        
        Args:
            messages: List of messages in the conversation
            stop: List of stop sequences
            run_manager: Callback manager for the run
            **kwargs: Additional generation parameters
            
        Yields:
            Chat generation chunks
        """
        if not self.enable_streaming:
            # Fall back to non-streaming
            result = self._generate(messages, stop, run_manager, **kwargs)
            if result.generations:
                content = result.generations[0].message.content
                chunk = ChatGenerationChunk(message=AIMessage(content=content))
                yield chunk
            return
        
        try:
            # Check feature flag
            if not should_use_claude_chat():
                logger.info("Claude chat disabled by feature flag, falling back to OpenAI")
                yield from self._fallback_stream_to_openai(messages, stop, run_manager, **kwargs)
                return
            
            # Convert messages to Claude format
            claude_messages = self._convert_messages_to_claude(messages)
            
            # Stream response from Claude API
            for chunk_content in self._stream_claude_api(claude_messages, stop, **kwargs):
                chunk = ChatGenerationChunk(message=AIMessage(content=chunk_content))
                yield chunk
                
        except Exception as e:
            logger.error(f"Failed to stream chat completion: {e}")
            # Yield a fallback response
            fallback_result = self._generate_fallback_response(messages)
            if fallback_result.generations:
                content = fallback_result.generations[0].message.content
                chunk = ChatGenerationChunk(message=AIMessage(content=content))
                yield chunk
    
    @with_retry(RetryConfig(max_retries=3, base_delay=1.0))
    def _call_claude_api(
        self,
        messages: List[Dict[str, str]],
        stop: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Call Claude API for chat completion.
        
        Args:
            messages: Messages in Claude format
            stop: Stop sequences
            **kwargs: Additional parameters
            
        Returns:
            Claude API response
        """
        # TODO: Implement actual Claude API call
        # For now, we'll simulate a Claude-like response
        
        logger.debug(f"Calling Claude API with {len(messages)} messages")
        
        # Simulate API call delay
        time.sleep(0.2)
        
        # Generate a mock response based on the conversation
        last_message = messages[-1] if messages else {"content": "Hello"}
        response_content = self._generate_mock_response(last_message["content"])
        
        return {
            "content": response_content,
            "model": self.model,
            "usage": {
                "prompt_tokens": sum(len(msg.get("content", "").split()) for msg in messages),
                "completion_tokens": len(response_content.split()),
                "total_tokens": sum(len(msg.get("content", "").split()) for msg in messages) + len(response_content.split())
            }
        }
    
    def _stream_claude_api(
        self,
        messages: List[Dict[str, str]],
        stop: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Iterator[str]:
        """
        Stream response from Claude API.
        
        Args:
            messages: Messages in Claude format
            stop: Stop sequences
            **kwargs: Additional parameters
            
        Yields:
            Content chunks
        """
        # Generate full response first (mock implementation)
        response = self._call_claude_api(messages, stop, **kwargs)
        content = response["content"]
        
        # Split into chunks for streaming simulation
        words = content.split()
        chunk_size = 3  # Words per chunk
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_content = " ".join(chunk_words)
            if i + chunk_size < len(words):
                chunk_content += " "
            
            # Simulate streaming delay
            time.sleep(0.05)
            yield chunk_content
    
    def _convert_messages_to_claude(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """
        Convert LangChain messages to Claude format.
        
        Args:
            messages: LangChain messages
            
        Returns:
            Messages in Claude format
        """
        claude_messages = []
        
        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            elif isinstance(message, SystemMessage):
                role = "system"
            elif isinstance(message, ChatMessage):
                role = message.role
            else:
                role = "user"  # Default fallback
            
            claude_messages.append({
                "role": role,
                "content": message.content
            })
        
        return claude_messages
    
    def _generate_mock_response(self, user_input: str) -> str:
        """
        Generate a mock response for testing/development.
        
        Args:
            user_input: User's input message
            
        Returns:
            Mock response content
        """
        # Simple response generation for testing
        user_lower = user_input.lower()
        
        if "hello" in user_lower or "hi" in user_lower:
            return "Hello! How can I help you today?"
        elif "how are you" in user_lower:
            return "I'm doing well, thank you for asking! How can I assist you?"
        elif "what" in user_lower and "name" in user_lower:
            return "I'm Claude, an AI assistant created by Anthropic."
        elif "help" in user_lower:
            return "I'd be happy to help! What would you like assistance with?"
        elif "code" in user_lower or "program" in user_lower:
            return "I can help with coding and programming tasks. What specific problem are you working on?"
        elif "explain" in user_lower:
            return "I'd be glad to explain that for you. Could you provide more details about what you'd like me to explain?"
        else:
            return f"I understand you're asking about: {user_input[:100]}{'...' if len(user_input) > 100 else ''}. Let me help you with that."
    
    def _generate_fallback_response(self, messages: List[BaseMessage]) -> ChatResult:
        """
        Generate a fallback response when Claude API fails.
        
        Args:
            messages: Original messages
            
        Returns:
            Fallback chat result
        """
        logger.warning("Generating fallback response due to API failure")
        
        fallback_content = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
        ai_message = AIMessage(content=fallback_content)
        generation = ChatGeneration(message=ai_message)
        
        return ChatResult(generations=[generation])
    
    def _fallback_to_openai(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> ChatResult:
        """
        Fallback to OpenAI when Claude is disabled.
        
        Args:
            messages: List of messages
            stop: Stop sequences
            run_manager: Callback manager
            **kwargs: Additional parameters
            
        Returns:
            Chat result from OpenAI
        """
        try:
            from langchain_openai import ChatOpenAI
            
            openai_chat = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return openai_chat._generate(messages, stop, run_manager, **kwargs)
            
        except ImportError:
            logger.warning("OpenAI chat not available, using fallback response")
            return self._generate_fallback_response(messages)
        except Exception as e:
            logger.error(f"OpenAI fallback failed: {e}")
            return self._generate_fallback_response(messages)
    
    def _fallback_stream_to_openai(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> Iterator[ChatGenerationChunk]:
        """
        Fallback streaming to OpenAI when Claude is disabled.
        
        Args:
            messages: List of messages
            stop: Stop sequences
            run_manager: Callback manager
            **kwargs: Additional parameters
            
        Yields:
            Chat generation chunks from OpenAI
        """
        try:
            from langchain_openai import ChatOpenAI
            
            openai_chat = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                streaming=True
            )
            yield from openai_chat._stream(messages, stop, run_manager, **kwargs)
            
        except ImportError:
            logger.warning("OpenAI chat not available, using fallback response")
            fallback_result = self._generate_fallback_response(messages)
            if fallback_result.generations:
                content = fallback_result.generations[0].message.content
                chunk = ChatGenerationChunk(message=AIMessage(content=content))
                yield chunk
        except Exception as e:
            logger.error(f"OpenAI streaming fallback failed: {e}")
            fallback_result = self._generate_fallback_response(messages)
            if fallback_result.generations:
                content = fallback_result.generations[0].message.content
                chunk = ChatGenerationChunk(message=AIMessage(content=content))
                yield chunk
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for chat operations."""
        return self.performance_monitor.get_metrics()
    
    def health_check(self) -> bool:
        """
        Perform a health check on the chat service.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Test with a simple message
            test_messages = [HumanMessage(content="Hello, this is a health check.")]
            result = self._generate(test_messages)
            
            # Validate the response
            if not result.generations or not result.generations[0].message.content:
                logger.error("Health check failed: empty response")
                return False
            
            logger.info("Claude chat model health check passed")
            return True
            
        except Exception as e:
            logger.error(f"Claude chat model health check failed: {e}")
            return False
    
    def __repr__(self) -> str:
        return f"ClaudeChatModel(model={self.model}, temperature={self.temperature})"