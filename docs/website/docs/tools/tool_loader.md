# tool_loader.py

This module provides dynamic loading of tool classes based on the YAML
configuration in `config/tools.yaml`.

## LangChainAdapter

`LangChainAdapter` wraps an `ArtesanatoBaseTool` instance so it can be used as a
`LangChain` `BaseTool`. Its `_run` method simply delegates to the wrapped tool's
`call()` function.

## Key Functions

- **`load_tool_config()`** – Read `config/tools.yaml` and return a dictionary of
  tool definitions.
- **`import_tool_class(file_path, class_name)`** – Dynamically import a tool
  class from the given Python file.
- **`instantiate_tool(tool_name, tool_config, **kwargs)`** – Create an instance
  of a tool and wrap it with `LangChainAdapter` if it subclasses
  `ArtesanatoBaseTool`.
- **`get_tools_for_agent(agent_id, agent_config, **kwargs)`** – Load and
  instantiate the tools listed for a specific agent role.
- **`load_all_tools(**kwargs)`** – Convenience helper that returns every tool
  defined in the configuration.

Typical usage:

```python
from tools.tool_loader import get_tools_for_agent

agent_tools = get_tools_for_agent(
    agent_id="backend_engineer",
    agent_config={"tools": ["supabase", "github"]}
)
```
