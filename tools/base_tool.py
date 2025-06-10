"""
Base Tool - Foundation class for all agent tools
"""

import os
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from langchain_core.tools import BaseTool as LangChainBaseTool
from pydantic import Field

# Load environment variables
load_dotenv()


class ArtesanatoBaseTool(LangChainBaseTool):
    """
    Base class for all Artesanato E-commerce project tools.
    Extends LangChain's BaseTool with project-specific functionality.
    """

    name: str = "base_tool"
    description: str = "Base class for all tools. Do not use directly."
    config: Dict[str, Any] = Field(default_factory=dict)
    verbose: bool = False

    def __init__(self, **kwargs):
        """Initialize the tool with optional configuration."""
        super().__init__()
        self.config = kwargs.get("config", {})
        self.verbose = kwargs.get("verbose", False)

        # Check for required environment variables
        self._check_env_vars()

    def _check_env_vars(self) -> None:
        """
        Check for required environment variables.
        Override in subclasses to specify required env vars.
        """
        pass

    def call(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for tool execution - designed for agent usage.
        Wraps around the run method and ensures consistent return structure.

        Args:
            query: The input query string

        Returns:
            Dict with standardized format { data, error, metadata }
        """
        try:
            self.log(f"Tool call with query: {query}")

            # First generate a plan if needed
            plan = self.plan(query)

            # Execute the tool based on the plan
            result = self.execute(query, plan)

            return self.format_response(
                data=result,
                error=None,
                metadata={"plan": plan}
            )
        except Exception as e:
            return self.handle_error(e, f"{self.name}.call")

    def plan(self, query: str) -> Dict[str, Any]:
        """
        Generate execution plan based on query.
        Override in subclasses for tool-specific planning.

        Args:
            query: The input query string

        Returns:
            Dict containing the execution plan
        """
        # Default implementation returns a simple plan
        return {
            "action": "default_execution",
            "params": {},
            "description": "Default execution plan"
        }

    def execute(self, query: str,
                plan: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute the tool with the provided query and plan.
        Default implementation calls _run method for LangChain compatibility.

        Args:
            query: The input query string
            plan: Optional execution plan

        Returns:
            The result of tool execution
        """
        # Default implementation delegates to LangChain's _run method
        return self._run(query)

    def _run(self, query: str) -> str:
        """
        Execute the tool. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _run method")

    def _arun(self, query: str) -> str:
        """
        Async version of _run. Uses _run by default but can be overridden.
        """
        return self._run(query)

    def log(self, message: str) -> None:
        """
        Log a message if verbose mode is enabled.
        """
        if self.verbose:
            print(f"[{self.name}] {message}")

    def format_response(self,
                        data: Any,
                        error: Optional[Any] = None,
                        metadata: Optional[Dict[str,
                                                Any]] = None) -> Dict[str,
                                                                      Any]:
        """
        Format the response in a consistent structure.

        Args:
            data: The result data
            error: Error information if applicable
            metadata: Additional metadata about the execution

        Returns:
            Dict with standardized format { data, error, metadata }
        """
        return {
            "data": data,
            "error": error,
            "metadata": metadata or {}
        }

    def handle_error(self, error: Any, context: str) -> Dict[str, Any]:
        """
        Handle errors in a consistent way.

        Args:
            error: The error object or message
            context: Context where the error occurred

        Returns:
            Dict with error information
        """
        error_message = str(error) if error else "An unexpected error occurred"
        self.log(f"Error in {context}: {error_message}")

        return self.format_response(
            data=None,
            error={
                "message": error_message,
                "context": context,
                "type": type(error).__name__ if error else "Unknown"
            }
        )
