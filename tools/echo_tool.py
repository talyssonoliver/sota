"""
Echo Tool - A simple tool for testing agent setup and configuration
"""

import logging
import sys
from typing import Optional

try:
    from langchain_core.tools import BaseTool
except ImportError as e:
    logging.warning(f"Failed to import langchain_core.tools: {e}")
    # Create a mock BaseTool class
    class BaseTool:
        """Mock BaseTool for when langchain is not available."""
        pass

try:
    from pydantic import BaseModel, ValidationError
except ImportError as e:
    logging.error(f"Failed to import pydantic: {e}")
    sys.exit(1)

try:
    from tools.base_tool import ArtesanatoBaseTool
except ImportError as e:
    logging.error(f"Failed to import ArtesanatoBaseTool: {e}")
    sys.exit(1)
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
