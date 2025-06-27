"""Mock CrewAI module."""

class Agent:
    def __init__(self, *args, **kwargs):
        self.role = kwargs.get('role', 'agent')

class Task:
    def __init__(self, *args, **kwargs):
        self.description = kwargs.get('description', '')

class Crew:
    def __init__(self, *args, **kwargs):
        self.agents = kwargs.get('agents', [])
        self.tasks = kwargs.get('tasks', [])
