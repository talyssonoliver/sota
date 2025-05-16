"""
Echo Tool - A simple tool for testing agent setup and configuration
"""

from langchain.tools import BaseTool
from typing import Optional
from tools.base_tool import ArtesanatoBaseTool
from pydantic import BaseModel, ValidationError

class EchoTool(ArtesanatoBaseTool):
    """A simple tool that echoes back the input, used for testing agent functionality."""
    
    name: str = "echo_tool"
    description: str = "A simple tool that echoes back the input. Use this when you need to test if the tool system is working."
    
    class InputSchema(BaseModel):
        query: str

    def _run(self, query: str) -> str:
        """Execute the echo tool."""
        try:
            validated = self.InputSchema(query=query)
            query = validated.query
            return f"ECHO: {query}"
        except ValidationError as ve:
            return self.handle_error(ve, f"{self.name}._run.input_validation")
        except Exception as e:
            return self.handle_error(e, f"{self.name}._run")

    def _arun(self, query: str) -> str:
        """Async version of _run."""
        return self._run(query)