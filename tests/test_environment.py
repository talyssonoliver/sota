"""
Test environment setup for agent testing.
This module sets up the testing environment to prevent validation errors.
"""

import os

# Set the TESTING environment variable to '1'
# This needs to be imported before any agent modules
os.environ["TESTING"] = "1"

# Mock the prompt loading function
from unittest.mock import patch
import sys

# Create a patched version of the prompt loading functions
def mock_load_prompt_template(template_path):
    """Mock implementation that returns a simple template string."""
    return "You are a {role}. Your task is: {task}."

def mock_load_and_format_prompt(template_path, variables=None):
    """Mock implementation that formats a simple template."""
    if variables is None:
        variables = {}
    
    role = variables.get('role', 'AI assistant')
    task = variables.get('task', 'Help the user')
    
    template = mock_load_prompt_template(template_path)
    return template.format(role=role, task=task)

# Apply patches to the prompt loading functions
import builtins
_original_import = builtins.__import__

def patched_import(name, *args, **kwargs):
    """Patch imports to mock prompt loading functions when needed."""
    module = _original_import(name, *args, **kwargs)
    
    if name == 'prompts.utils' or getattr(module, '__name__', '') == 'prompts.utils':
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
        return {"output": f"Mock output from {self.role}", "task_id": "TEST-01"}