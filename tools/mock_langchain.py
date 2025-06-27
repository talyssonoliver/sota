"""Mock LangChain module."""

class ChatOpenAI:
    def __init__(self, *args, **kwargs):
        pass
    
    def invoke(self, *args, **kwargs):
        return "Mock response"

class BaseTool:
    def __init__(self, *args, **kwargs):
        pass

class StructuredTool:
    @staticmethod
    def from_function(*args, **kwargs):
        return BaseTool()
