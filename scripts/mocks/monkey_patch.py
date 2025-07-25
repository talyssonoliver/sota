"""
Monkey patching utilities for testing purposes.
These help bypass validation in Pydantic models during testing.
"""


def apply_agent_memory_patch():
    """
    Apply a monkey patch to CrewAI Agent class to allow 'memory' property access.
    This is needed for tests that verify memory configuration.
    """
    try:
        from crewai import Agent

        # Only add the patch if it doesn't exist yet
        if not hasattr(Agent, '_memory_config'):
            # Add storage for memory config
            setattr(Agent, '_memory_config', None)

            # Define a property accessor
            def get_memory(self):
                return getattr(self, '_memory_config', None)

            def set_memory(self, value):
                object.__setattr__(self, '_memory_config', value)

            # Add the property to the class
            Agent.memory = property(get_memory, set_memory)
    except ImportError:
        print("WARNING: Could not apply Agent memory patch - crewai not found")
