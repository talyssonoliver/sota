"""
Test environment setup for agent testing.
This module sets up the testing environment to prevent validation errors.
"""

import builtins
import os
import sys
from unittest.mock import MagicMock, patch

# Set the TESTING environment variable to '1'
# This needs to be imported before any agent modules
os.environ["TESTING"] = "1"

# Import necessary langchain components for proper mocking
try:
    from langchain_core.runnables import Runnable
except ImportError:
    # Fallback for older LangChain versions
    class Runnable:
        """Mock Runnable base class if langchain_core isn't available"""
        pass

# Store original isinstance to patch it for Runnable type checking
original_isinstance = isinstance


def patched_isinstance(obj, cls):
    """Patched isinstance that properly detects our mock objects as Runnable instances"""
    if cls is Runnable and (
        hasattr(
            obj,
            '_lc_kwargs') or isinstance(
            obj,
            (RunnableLLMMock,
             RunnableChainMock))):
        return True
    return original_isinstance(obj, cls)


class RunnableLLMMock(MagicMock):
    """A mock that properly inherits from Runnable for testing purposes."""

    # Mark the class as a proper Runnable implementation
    _lc_kwargs = {"_type": "runnable_mock"}
    _lc_serializable = True

    def invoke(self, input, config=None, **kwargs):
        """Implement the required invoke method for Runnable interface."""
        if hasattr(
                self,
                '_mock_return_value') and self._mock_return_value is not None:
            return self._mock_return_value

        # Default behavior based on input type
        if isinstance(input, dict) and "prompt" in input:
            return f"Mock response to: {input['prompt']}"
        elif isinstance(input, dict) and "query" in input:
            return {"result": f"Mock answer for: {input['query']}"}
        elif isinstance(input, str):
            return f"Mock response to: {input}"

        return {"result": "This is a mock response"}

    def batch(self, inputs, config=None, **kwargs):
        """Implement batch for Runnable interface."""
        return [self.invoke(input) for input in inputs]

    def stream(self, input, config=None, **kwargs):
        """Implement stream for Runnable interface."""
        yield self.invoke(input)


class RunnableChainMock(MagicMock):
    """Mock class for chains that implements the Runnable interface"""

    # Add LangChain runnable properties
    _lc_kwargs = {"_type": "runnable_chain_mock"}
    _lc_serializable = True

    def invoke(self, input, config=None, **kwargs):
        """Implementation of required Runnable method for chains"""
        if hasattr(
                self,
                '_mock_return_value') and self._mock_return_value is not None:
            return self._mock_return_value

        # Default behavior depends on input shape
        if isinstance(input, dict):
            if "query" in input:
                return {"result": f"Mock answer for: {input['query']}"}
            elif "question" in input:
                return {"answer": f"Mock answer for: {input['question']}"}

        return {"result": "Mock chain response"}

    def batch(self, inputs, config=None, **kwargs):
        """Implement batch for Runnable interface"""
        return [self.invoke(input) for input in inputs]

    def stream(self, input, config=None, **kwargs):
        """Implement stream for Runnable interface"""
        yield self.invoke(input)


# Mock the prompt loading function

# Create a patched version of the prompt loading functions

def mock_load_prompt_template(template_path):
    """Mock implementation that returns a simple template string."""
    return "You are a {role}. Your task is: {task}."


def mock_load_and_format_prompt(template_path, variables=None):
    """Mock implementation that formats a simple template."""
    if variables is None:
        variables = {}
    elif isinstance(variables, str):
        # Handle the case where a string is passed instead of a dict
        return variables

    role = variables.get('role', 'AI assistant')
    task = variables.get('task', 'Help the user')

    template = mock_load_prompt_template(template_path)
    return template.format(role=role, task=task)


# Apply patches to the prompt loading functions
_original_import = builtins.__import__


def patched_import(name, *args, **kwargs):
    """Patch imports to mock prompt loading functions when needed."""
    module = _original_import(name, *args, **kwargs)

    if name == 'prompts.utils' or getattr(
            module, '__name__', '') == 'prompts.utils':
        module.load_prompt_template = mock_load_prompt_template
        module.load_and_format_prompt = mock_load_and_format_prompt

    return module


builtins.__import__ = patched_import


class MockCrewAIAgent:
    """Mock of CrewAI Agent for testing"""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.role = kwargs.get('role', 'Unknown Agent')
        self.memory = kwargs.get('memory', None)

    def run(self, *args, **kwargs):
        """Mock run method"""
        return {"result": "mock response"}

    def execute(self, *args, **kwargs):
        """Mock execute method"""
        return {
            "output": f"Mock output from {self.role}",
            "task_id": "TEST-01"}
