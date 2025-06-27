"""LangChain Core Runnables compatibility module."""

from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod

class Runnable(ABC):
    """Base runnable interface."""
    
    @abstractmethod
    def invoke(self, input: Any, config: Optional[Dict] = None) -> Any:
        """Invoke the runnable."""
        pass
    
    def __or__(self, other):
        """Chain runnables with | operator."""
        return RunnableSequence([self, other])
    
    def __ror__(self, other):
        """Chain runnables with | operator (reverse)."""
        return RunnableSequence([other, self])

class RunnablePassthrough(Runnable):
    """Runnable that passes input through unchanged."""
    
    def invoke(self, input: Any, config: Optional[Dict] = None) -> Any:
        """Pass input through unchanged."""
        return input

class RunnableLambda(Runnable):
    """Runnable that applies a lambda function."""
    
    def __init__(self, func):
        """Initialize with function."""
        self.func = func
    
    def invoke(self, input: Any, config: Optional[Dict] = None) -> Any:
        """Apply function to input."""
        return self.func(input)

class RunnableSequence(Runnable):
    """Sequence of runnables."""
    
    def __init__(self, steps: List[Runnable]):
        """Initialize with steps."""
        self.steps = steps
    
    def invoke(self, input: Any, config: Optional[Dict] = None) -> Any:
        """Execute steps in sequence."""
        result = input
        for step in self.steps:
            result = step.invoke(result, config)
        return result

class RunnableParallel(Runnable):
    """Parallel execution of runnables."""
    
    def __init__(self, mapping: Dict[str, Runnable]):
        """Initialize with mapping."""
        self.mapping = mapping
    
    def invoke(self, input: Any, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute runnables in parallel."""
        return {
            key: runnable.invoke(input, config)
            for key, runnable in self.mapping.items()
        }

__all__ = [
    'Runnable', 
    'RunnablePassthrough', 
    'RunnableLambda', 
    'RunnableSequence', 
    'RunnableParallel'
]