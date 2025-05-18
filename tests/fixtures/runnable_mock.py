"""
Mock classes that implement the Runnable interface for testing.
"""

from unittest.mock import MagicMock

# Try to import Runnable, with fallback for tests
try:
    from langchain_core.runnables import Runnable
except ImportError:
    try:
        from langchain.schema.runnable import Runnable
    except ImportError:
        # Fallback if neither import works
        class Runnable:
            """Mock Runnable base class if langchain imports aren't available"""
            pass

# Store original isinstance to patch it for Runnable type checking
original_isinstance = isinstance

def patched_isinstance(obj, cls):
    """Patched isinstance that properly detects our mock objects as Runnable instances"""
    if cls is Runnable and (isinstance(obj, (RunnableLLMMock, RunnableChainMock)) or 
                           hasattr(obj, '_lc_kwargs')):
        return True
    return original_isinstance(obj, cls)

class RunnableLLMMock(MagicMock):
    """Mock class for LLMs that implements the Runnable interface"""
    
    # Add LangChain runnable properties
    _lc_kwargs = {"_type": "runnable_llm_mock"}
    _lc_serializable = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Instead of modifying __mro__, we'll override isinstance behavior
        self.return_value = None  # Add explicit return_value attribute for mocking
    
    def invoke(self, input, config=None, **kwargs):
        """Implementation of required Runnable method"""
        if self.return_value is not None:
            return self.return_value
        elif hasattr(self, '_mock_return_value') and self._mock_return_value is not None:
            return self._mock_return_value
        
        # Default behavior based on input type
        if isinstance(input, dict) and "prompt" in input:
            return f"Mock response to: {input['prompt']}"
        elif isinstance(input, str):
            return f"Mock response to: {input}"
        
        return "Default mock LLM response"
        
    def batch(self, inputs, config=None, **kwargs):
        """Implement batch for Runnable interface"""
        return [self.invoke(input) for input in inputs]
    
    def stream(self, input, config=None, **kwargs):
        """Implement stream for Runnable interface"""
        yield self.invoke(input)
        
    def __instancecheck__(self, instance):
        """Support isinstance checks through special method"""
        return isinstance(instance, (self.__class__, Runnable))
        
    # This method helps make the mock appear as a Runnable
    def __runtimeclass__(self):
        return Runnable

class RunnableChainMock(MagicMock):
    """Mock class for chains that implements the Runnable interface"""
    
    # Add LangChain runnable properties
    _lc_kwargs = {"_type": "runnable_chain_mock"}
    _lc_serializable = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Instead of modifying __mro__, we'll override isinstance behavior
        self.return_value = None  # Add explicit return_value attribute for mocking
    
    def invoke(self, input, config=None, **kwargs):
        """Implementation of required Runnable method for chains"""
        if self.return_value is not None:
            return self.return_value
        elif hasattr(self, '_mock_return_value') and self._mock_return_value is not None:
            return self._mock_return_value
        
        # Default behavior depends on input shape
        if isinstance(input, dict):
            if "query" in input:
                return {"result": f"Mock answer for: {input['query']}"}
            elif "question" in input:
                return {"answer": f"Mock answer for: {input['question']}"}
        
        return {"result": "Default mock chain response"}
        
    def batch(self, inputs, config=None, **kwargs):
        """Implement batch for Runnable interface"""
        return [self.invoke(input) for input in inputs]
    
    def stream(self, input, config=None, **kwargs):
        """Implement stream for Runnable interface"""
        yield self.invoke(input)
        
    def __instancecheck__(self, instance):
        """Support isinstance checks through special method"""
        return isinstance(instance, (self.__class__, Runnable))
          # This method helps make the mock appear as a Runnable
    def __runtimeclass__(self):
        return Runnable
        
    def __call__(self, *args, **kwargs):
        """For backwards compatibility with older LangChain versions"""
        if args and isinstance(args[0], dict):
            if "query" in args[0]:
                return {"result": f"Mock answer for: {args[0]['query']}"}
            elif "question" in args[0]:
                return {"answer": f"Mock answer for: {args[0]['question']}"}
        
        return {"result": "Default mock chain response from __call__"}

# Apply the isinstance patch for tests
import builtins
builtins.isinstance = patched_isinstance
