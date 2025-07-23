"""
Claude Integration Utilities

Common utilities and helper functions for Claude Code integration
including error handling, retry logic, and compatibility functions.
"""

import asyncio
import time
from typing import Callable, List, Optional, TypeVar
from functools import wraps
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


class ClaudeError(Exception):
    """Base exception for Claude integration errors."""
    pass


class ClaudeAPIError(ClaudeError):
    """Exception for Claude API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ClaudeRateLimitError(ClaudeAPIError):
    """Exception for Claude API rate limit errors."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


def with_retry(config: Optional[RetryConfig] = None):
    """Decorator for adding retry logic to functions."""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except ClaudeRateLimitError as e:
                    last_exception = e
                    if attempt == config.max_retries:
                        break
                    
                    # Use retry_after if provided, otherwise exponential backoff
                    delay = e.retry_after or min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    if config.jitter:
                        import random
                        delay *= (0.5 + random.random() * 0.5)  # 50-100% of delay
                    
                    logger.warning(f"Rate limited on attempt {attempt + 1}, retrying in {delay:.2f}s")
                    time.sleep(delay)
                    
                except ClaudeAPIError as e:
                    last_exception = e
                    if attempt == config.max_retries:
                        break
                    
                    # Only retry on certain status codes
                    if e.status_code and e.status_code < 500:
                        break
                    
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    logger.warning(f"API error on attempt {attempt + 1}, retrying in {delay:.2f}s: {e}")
                    time.sleep(delay)
                
                except Exception as e:
                    last_exception = e
                    if attempt == config.max_retries:
                        break
                    
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    logger.warning(f"Unexpected error on attempt {attempt + 1}, retrying in {delay:.2f}s: {e}")
                    time.sleep(delay)
            
            # If we get here, all retries failed
            if last_exception:
                raise last_exception
            raise ClaudeError("All retry attempts failed with no exception captured")
        
        return wrapper
    return decorator


async def with_async_retry(config: Optional[RetryConfig] = None):
    """Async version of retry decorator."""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except ClaudeRateLimitError as e:
                    last_exception = e
                    if attempt == config.max_retries:
                        break
                    
                    delay = e.retry_after or min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    if config.jitter:
                        import random
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Rate limited on attempt {attempt + 1}, retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)
                    
                except (ClaudeAPIError, Exception) as e:
                    last_exception = e
                    if attempt == config.max_retries:
                        break
                    
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    logger.warning(f"Error on attempt {attempt + 1}, retrying in {delay:.2f}s: {e}")
                    await asyncio.sleep(delay)
            
            if last_exception:
                raise last_exception
            raise ClaudeError("All retry attempts failed")
        
        return wrapper
    return decorator


def batch_process(items: List[T], batch_size: int) -> List[List[T]]:
    """Split items into batches of specified size."""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def normalize_embedding_dimensions(embeddings: List[List[float]], target_dim: int) -> List[List[float]]:
    """Normalize embedding dimensions to match target (for compatibility)."""
    if not embeddings:
        return embeddings
    
    current_dim = len(embeddings[0])
    if current_dim == target_dim:
        return embeddings
    
    logger.warning(f"Normalizing embeddings from {current_dim} to {target_dim} dimensions")
    
    # Simple truncation or padding for dimension compatibility
    normalized = []
    for embedding in embeddings:
        if len(embedding) > target_dim:
            # Truncate
            normalized.append(embedding[:target_dim])
        elif len(embedding) < target_dim:
            # Pad with zeros
            padded = embedding + [0.0] * (target_dim - len(embedding))
            normalized.append(padded)
        else:
            normalized.append(embedding)
    
    return normalized


def validate_openai_compatibility(embeddings: List[List[float]]) -> bool:
    """Validate that embeddings are compatible with OpenAI format."""
    if not embeddings:
        return True
    
    # Check dimensions
    expected_dim = 1536  # OpenAI text-embedding-ada-002 dimension
    for i, embedding in enumerate(embeddings):
        if len(embedding) != expected_dim:
            logger.error(f"Embedding {i} has {len(embedding)} dimensions, expected {expected_dim}")
            return False
    
    # Check value ranges (embeddings should be normalized)
    for i, embedding in enumerate(embeddings):
        magnitude = sum(x * x for x in embedding) ** 0.5
        if abs(magnitude - 1.0) > 0.1:  # Allow some tolerance
            logger.warning(f"Embedding {i} magnitude {magnitude:.3f} may not be normalized")
    
    return True


def create_compatibility_wrapper(claude_func: Callable, openai_signature: str) -> Callable:
    """Create a wrapper to make Claude functions compatible with OpenAI signatures."""
    @wraps(claude_func)
    def wrapper(*args, **kwargs):
        try:
            # Log compatibility layer usage
            logger.debug(f"Compatibility wrapper called for {openai_signature}")
            return claude_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Compatibility wrapper error for {openai_signature}: {e}")
            raise ClaudeError(f"Compatibility layer failed: {e}") from e
    
    return wrapper


class PerformanceMonitor:
    """Monitor performance metrics for Claude integration."""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'average_response_time': 0.0,
        }
    
    def record_request(self, success: bool, response_time: float) -> None:
        """Record a request and its performance metrics."""
        self.metrics['total_requests'] += 1
        self.metrics['total_response_time'] += response_time
        
        if success:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
        
        # Update average
        if self.metrics['total_requests'] > 0:
            self.metrics['average_response_time'] = (
                self.metrics['total_response_time'] / self.metrics['total_requests']
            )
    
    def get_metrics(self) -> dict:
        """Get current performance metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'average_response_time': 0.0,
        }


# Global performance monitor
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    return _performance_monitor