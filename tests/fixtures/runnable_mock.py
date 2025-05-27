"""
Mock classes that implement the Runnable interface for testing.
"""

import builtins
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
    if cls is Runnable and (
        isinstance(
            obj,
            (RunnableLLMMock,
             RunnableChainMock)) or hasattr(
            obj,
            '_lc_kwargs')):
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
        # This method is now replaced by the MagicMock in __init__
        pass

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
        self.return_value = None  # Add explicit return_value attribute for mocking
        # Make .invoke a MagicMock so .invoke.return_value can be set in tests
        self.invoke = MagicMock(side_effect=self._invoke_side_effect)

    def _invoke_side_effect(self, input, config=None, **kwargs):
        if self.return_value is not None:
            return self.return_value
        elif hasattr(self, '_mock_return_value') and self._mock_return_value is not None:
            return self._mock_return_value
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
builtins.isinstance = patched_isinstance
