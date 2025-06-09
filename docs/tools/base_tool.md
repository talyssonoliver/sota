# base_tool.py

This module defines the **ArtesanatoBaseTool**, the foundation for all tools in
the project. It extends LangChain's `BaseTool` and standardizes how tools are
initialized and executed.

## ArtesanatoBaseTool

```python
class ArtesanatoBaseTool(LangChainBaseTool):
    """Base class for all project tools."""

    name: str = "base_tool"
    description: str = "Base class for all tools. Do not use directly."
    config: Dict[str, Any] = Field(default_factory=dict)
    verbose: bool = False

    def call(self, query: str) -> Dict[str, Any]:
        """Standard entry point used by agents."""
        plan = self.plan(query)
        result = self.execute(query, plan)
        return self.format_response(data=result, metadata={"plan": plan})
```

### Key Methods

- **`plan(query)`** – Generate an execution plan for the query.
- **`execute(query, plan)`** – Execute the plan (defaults to `_run`).
- **`_run(query)`** – Subclasses implement the core logic here.
- **`_arun(query)`** – Async version of `_run` if needed.
- **`format_response(data, error=None, metadata=None)`** – Consistent return
  structure used by all tools.
- **`handle_error(error, context)`** – Standardized error handling.

Tools subclass this base class to ensure uniform logging, configuration loading
and response formatting across the entire system.
