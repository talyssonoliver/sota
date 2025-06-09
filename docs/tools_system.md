# Tools System

This document describes the tools system in the AI Agent System, which extends agent capabilities with specialized functions.

## Overview

The tools system provides agents with the ability to interact with external services, perform specialized tasks, and access information beyond their built-in capabilities. Each tool encapsulates a specific functionality that can be used by agents during task execution.

## Tool Architecture

Tools are implemented as Python classes that inherit from the `BaseTool` class defined in `tools/base_tool.py`. Each tool provides one or more methods that agents can call to perform specific actions.

### BaseTool Class

```python
class BaseTool:
    """Base class for all tools in the system."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.initialize()
    
    def initialize(self):
        """Initialize the tool with any setup required."""
        pass
    
    def get_tool_config(self):
        """Get the tool's configuration."""
        return self.config
        
    def get_methods(self):
        """Get a dictionary of methods this tool provides."""
        methods = {}
        for attr_name in dir(self):
            if attr_name.startswith('_') or attr_name in ['initialize', 'get_tool_config', 'get_methods']:
                continue
            
            attr = getattr(self, attr_name)
            if callable(attr):
                methods[attr_name] = attr.__doc__ or "No description provided"
                
        return methods
```

Tool Architecture Highlights:
- `ArtesanatoBaseTool` extends LangChain's `BaseTool` and defines `call()` for standardized execution
- `tool_loader.py` registers and instantiates tools based on `config/tools.yaml`
- Agents obtain tools via `get_tools_for_agent()` which selects role-specific tools
- Tools load environment variables during `initialize()`
- Methods return structured dictionaries with `data`, `error`, and `metadata` for consistent error handling


## Available Tools

The system includes several specialized tools:

### Tools Inventory

| Tool Name | File | Purpose | Used By Agents |
|-----------|------|---------|----------------|
| BaseTool | `base_tool.py` | Base class for all tools | All tools
| ToolLoader | `tool_loader.py` | Dynamically load and configure tools | Orchestrator
| MemoryEngine | `memory_engine.py` | Persistent context store and retrieval | All agents
| ContextTracker | `context_tracker.py` | Log context usage per task | All agents
| ContextVisualizer | `context_visualizer.py` | Visualize context retrieval results | Documentation
| CoverageTool | `coverage_tool.py` | Generate code coverage reports | QA
| CypressTool | `cypress_tool.py` | Run end-to-end tests via Cypress | QA
| DesignSystemTool | `design_system_tool.py` | Access design system specs | Frontend
| EchoTool | `echo_tool.py` | Debugging and test output | All agents
| FixedRetrievalQA | `fixed_retrieval_qa.py` | Patched retrieval QA function | Memory Engine
| GitHubTool | `github_tool.py` | Manage GitHub issues and repos | Technical Lead, Backend
| JestTool | `jest_tool.py` | Execute Jest unit tests | Frontend
| MarkdownTool | `markdown_tool.py` | Generate and parse markdown | Documentation
| QA CLI | `qa_cli.py` | Command line helper for QA tasks | QA
| RateLimiter | `rate_limiter.py` | Enforce operation rate limits | Memory Engine
| RetrievalQA | `retrieval_qa.py` | Wrapper for retrieval QA chains | Memory Engine
| SupabaseTool | `supabase_tool.py` | Interact with Supabase database | Backend
| TailwindTool | `tailwind_tool.py` | Generate Tailwind CSS classes | Frontend
| VercelTool | `vercel_tool.py` | Deploy applications to Vercel | Frontend
| MemoryEngineExamples | `memory_engine_examples.py` | Example usage scripts | Developers


### Database Tools
- **Supabase Tool** (`supabase_tool.py`): Interact with Supabase for database operations and authentication.

### Development Tools
- **GitHub Tool** (`github_tool.py`): Interact with GitHub repositories, create issues, and manage code.
- **Jest Tool** (`jest_tool.py`): Run Jest tests and process the results.
- **Cypress Tool** (`cypress_tool.py`): Run end-to-end tests using Cypress.

### Frontend Tools
- **Tailwind Tool** (`tailwind_tool.py`): Generate Tailwind CSS classes for frontend components.
- **Design System Tool** (`design_system_tool.py`): Access the design system specifications.
- **Vercel Tool** (`vercel_tool.py`): Deploy and manage frontend applications on Vercel.

### Utility Tools
- **Markdown Tool** (`markdown_tool.py`): Generate and parse markdown content.
- **Echo Tool** (`echo_tool.py`): Simple tool for testing and debugging.
- **Coverage Tool** (`coverage_tool.py`): Generate and analyze code coverage reports.

## Tool Configuration

Tools are configured through the `tools.yaml` file in the `config/` directory. Each tool can have its own configuration parameters.

Example configuration:
```yaml
supabase:
  project_url: ${SUPABASE_URL}
  api_key: ${SUPABASE_KEY}
  
github:
  repository: "organization/repo-name"
  auth_token: ${GITHUB_TOKEN}
  
jest:
  project_path: "./frontend"
```

## Tool Loader

The `tool_loader.py` module is responsible for loading and initializing tools based on configuration:

```python
def load_tool(tool_name, config=None):
    """
    Load a specific tool by name with optional configuration.
    
    Args:
        tool_name: The name of the tool to load
        config: Optional configuration for the tool
        
    Returns:
        An instance of the tool
    """
    # Tool loading logic
```

```python
def load_all_tools():
    """
    Load all configured tools from the config file.
    
    Returns:
        A dictionary mapping tool names to tool instances
    """
    # Load all tools from configuration
```

```python
def get_tools_for_agent(agent_role, agent_config, **kwargs):
    """
    Get the appropriate tools for a specific agent role.
    
    Args:
        agent_role: The role of the agent
        agent_config: The agent's configuration
        
    Returns:
        A list of tool instances for the agent
    """
    # Get role-specific tools
```

## Using Tools in Agents

Agents can access tools through a standard interface:

```python
# Example of an agent using a tool
result = self.use_tool("github", "create_issue", {
    "title": "Implement login feature",
    "body": "Need to implement OAuth login using Supabase",
    "labels": ["feature", "auth"]
})
```

## Adding New Tools

To add a new tool to the system:

1. Create a new Python file in the `tools/` directory (e.g., `my_tool.py`)
2. Define a class that inherits from `BaseTool`
3. Implement the tool's methods
4. Update the `tools.yaml` configuration file
5. Register the tool in the tool loader if needed

Example of a new tool:
```python
from tools.base_tool import BaseTool

class MyTool(BaseTool):
    """A new tool for the AI Agent System."""
    
    def initialize(self):
        """Set up the tool."""
        self.api_key = self.config.get("api_key")
        self.client = SomeAPIClient(self.api_key)
    
    def perform_action(self, param1, param2):
        """
        Perform some action with the tool.
        
        Args:
            param1: The first parameter
            param2: The second parameter
            
        Returns:
            The result of the action
        """
        return self.client.do_something(param1, param2)
```


## Tool Integration Patterns

1. **Agent-Tool Binding**
   - Agents declare required tools in their configuration.
   - `get_tools_for_agent()` instantiates these tools before task execution.

2. **Tool Chaining**
   - Tools can be combined in pipelines, passing intermediate results between them.
   - Example: `GitHubTool` creates an issue, followed by `SupabaseTool` updating database records.

3. **Tool Middleware**
   - Common wrappers handle authentication, logging and error capture.
   - The `call()` method in `ArtesanatoBaseTool` standardizes result handling.

4. **Custom Tool Creation**
   - Subclass `ArtesanatoBaseTool` and implement `_run()` for the core logic.
   - Register the tool in `tools.yaml` so the loader can discover it.

## Best Practices

1. **Error Handling**: Tools should handle errors gracefully and provide meaningful error messages.
2. **Documentation**: Each tool method should be well-documented with docstrings.
3. **Configuration**: Use configuration parameters rather than hardcoded values.
4. **Testing**: Create tests for each tool to ensure they work as expected.
5. **Security**: Handle sensitive information (API keys, credentials) securely.