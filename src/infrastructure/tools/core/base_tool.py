"""
Base Tool - Foundation for all tools in the AI system

This module defines the ArtesanatoBaseTool, which provides:
- Standardized tool initialization and execution
- Consistent response formatting
- Error handling and logging
- Integration with LangChain's BaseTool
"""
from src.infrastructure.utils.common_imports import logging, time
from typing import Any, Dict, Optional

# Conditional import following the project pattern
try:
    from langchain_core.tools import (
        BaseTool as LangChainBaseTool,  # type: ignore[assignment]
    )
except ImportError:
    logging.warning("LangChain not available, using mock BaseTool")

    class LangChainBaseTool:  # type: ignore[misc]
        """Mock BaseTool for when langchain is not available."""

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


try:
    from pydantic import Field
except ImportError:
    logging.error("Pydantic is required but not available")
    raise


class ArtesanatoBaseTool(LangChainBaseTool):
    """Base class for all project tools.

    Provides standardized tool execution, error handling, and response formatting.
    All tools in the system should inherit from this class.
    """

    name: str = "base_tool"
    description: str = "Base class for all tools. Do not use directly."
    config: Dict[str, Any] = Field(default_factory=dict)
    verbose: bool = False
    logger: Any = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        """Initialize the base tool with configuration."""
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = kwargs.get("config", {})
        self.verbose = kwargs.get("verbose", False)

        # Initialize tool-specific setup
        try:
            self.initialize()
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.__class__.__name__}: {e}")

    def initialize(self):
        """Initialize tool-specific setup. Override in subclasses."""
        pass

    def call(self, query: str) -> Dict[str, Any]:
        """Standard entry point used by agents.

        Args:
            query: The input query/request for the tool

        Returns:
            Standardized response dictionary with data, error, and metadata
        """
        try:
            # Generate execution plan
            plan = self.plan(query)

            # Execute the plan
            result = self.execute(query, plan)

            # Format and return response
            return self.format_response(data=result, metadata={"plan": plan})

        except Exception as e:
            return self.handle_error(e, {"query": query})

    def plan(self, query: str) -> Dict[str, Any]:
        """Generate an execution plan for the query.

        Args:
            query: The input query

        Returns:
            Execution plan dictionary
        """
        return {"action": "execute", "query": query, "timestamp": time.time()}

    def execute(self, query: str, plan: Dict[str, Any]) -> Any:
        """Execute the plan (defaults to _run).

        Args:
            query: The input query
            plan: The execution plan

        Returns:
            Execution result
        """
        return self._run(query)

    def _run(self, query: str) -> Any:
        """Core tool logic. Must be implemented by subclasses.

        Args:
            query: The input query

        Returns:
            Tool execution result
        """
        raise NotImplementedError("Subclasses must implement _run method")

    async def _arun(self, query: str) -> Any:
        """Async version of _run. Override if async execution is needed.

        Args:
            query: The input query

        Returns:
            Tool execution result
        """
        # Default to sync execution
        return self._run(query)

    def format_response(
        self,
        data: Any = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Format tool response in a consistent structure.

        Args:
            data: Successful execution result
            error: Error message if execution failed
            metadata: Additional response metadata

        Returns:
            Standardized response dictionary
        """
        response = {
            "success": error is None,
            "timestamp": time.time(),
            "tool": self.name,
            "data": data,    # Always include data key (None if no data)
            "error": error,  # Always include error key (None if no error)
        }

        if metadata:
            response["metadata"] = metadata

        return response

    def handle_error(
        self, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Standardized error handling.

        Args:
            error: The exception that occurred
            context: Additional context about the error

        Returns:
            Formatted error response
        """
        error_msg = str(error)
        self.logger.error(f"Tool error in {self.name}: {error_msg}")

        if self.verbose and context:
            self.logger.debug(f"Error context: {context}")

        return self.format_response(
            error=error_msg,
            metadata={"error_type": type(error).__name__, "context": context or {}},
        )

    def log(self, message: str, level: str = "info"):
        """Log a message with the appropriate level.

        Args:
            message: Message to log
            level: Log level (debug, info, warning, error)
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"[{self.name}] {message}")

    def get_tool_config(self) -> Dict[str, Any]:
        """Get the tool's configuration.

        Returns:
            Tool configuration dictionary
        """
        return self.config.copy()

    def get_methods(self) -> Dict[str, str]:
        """Get a dictionary of methods this tool provides.

        Returns:
            Dictionary mapping method names to descriptions
        """
        methods = {}
        for attr_name in dir(self):
            if attr_name.startswith("_") or attr_name in [
                "initialize",
                "get_tool_config",
                "get_methods",
                "call",
                "plan",
                "execute",
                "format_response",
                "handle_error",
                "log",
            ]:
                continue

            attr = getattr(self, attr_name)
            if callable(attr):
                methods[attr_name] = attr.__doc__ or "No description provided"

        return methods


# Export the main tool class
__all__ = ["ArtesanatoBaseTool"]

# Compatibility alias for existing code that expects BaseTool
BaseTool = ArtesanatoBaseTool
