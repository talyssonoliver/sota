"""
Tool Loader - Dynamically loads tools based on configuration.
"""

import importlib.util
import os
from typing import Any, Callable, Dict, List, Optional, Type, Union

import yaml
from langchain.tools import BaseTool as LangChainBaseTool

# Use absolute import instead of relative import
from tools.base_tool import ArtesanatoBaseTool


class LangChainAdapter(LangChainBaseTool):
    """
    Adapter class that wraps ArtesanatoBaseTool instances to make them compatible with LangChain.
    """

    name: str = ""
    description: str = ""

    def __init__(self, tool: ArtesanatoBaseTool):
        """
        Initialize the adapter with an ArtesanatoBaseTool instance.

        Args:
            tool: The ArtesanatoBaseTool instance to wrap.
        """
        # Initialize with properly defined attributes
        kwargs = {
            "name": tool.name,
            "description": tool.description
        }
        super().__init__(**kwargs)

        # Store the tool as an instance attribute (not a field)
        self._tool = tool

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the wrapped tool using our standardized interface.

        Args:
            *args: Positional arguments to pass to the tool.
            **kwargs: Keyword arguments to pass to the tool.

        Returns:
            Result from the wrapped tool's call method.
        """
        query = args[0] if args else kwargs.get("query", "")
        result = self._tool.call(query)

        return result["data"] if isinstance(
            result, dict) and "data" in result else result

    def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """
        Async execution of the wrapped tool.
        """
        return self._run(*args, **kwargs)


def load_tool_config() -> Dict[str, Any]:
    """
    Load the tools configuration from YAML.

    Returns:
        Dict[str, Any]: The parsed tools configuration.
    """
    config_path = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'config', 'tools.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def import_tool_class(file_path: str, class_name: str) -> type:
    """
    Dynamically import a tool class from a file.

    Args:
        file_path: Path to the file containing the tool class.
        class_name: Name of the class to import.

    Returns:
        type: The imported tool class.
    """
    # Get the absolute path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abs_file_path = os.path.join(base_dir, file_path)

    # Import the module
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, abs_file_path)
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load spec for module {module_name} from {abs_file_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Get the class
    if not hasattr(module, class_name):
        raise ImportError(
            f"Could not find class {class_name} in module {module_name}")

    return getattr(module, class_name)


def instantiate_tool(tool_name: str,
                     tool_config: Dict[str,
                                       Any],
                     **kwargs) -> LangChainBaseTool:
    """
    Instantiate a tool based on its configuration.

    Args:
        tool_name: Name of the tool to instantiate.
        tool_config: Configuration for the tool.
        **kwargs: Additional arguments to pass to the tool constructor.

    Returns:
        LangChainBaseTool: An instance of the tool, wrapped in LangChainAdapter if necessary.
    """
    file_path = tool_config.get('file')
    class_name = tool_config.get('class')

    if not file_path or not class_name:
        raise ValueError(
            f"Tool {tool_name} is missing required configuration: file or class")

    tool_class = import_tool_class(file_path, class_name)
    tool_instance = tool_class(**kwargs)

    if isinstance(tool_instance, ArtesanatoBaseTool):
        return LangChainAdapter(tool_instance)

    return tool_instance


def get_tools_for_agent(agent_id: str,
                        agent_config: Dict[str,
                                           Any],
                        **kwargs) -> List[LangChainBaseTool]:
    """
    Get the tools assigned to a specific agent.

    Args:
        agent_id: ID of the agent.
        agent_config: Configuration for the agent.
        **kwargs: Additional arguments to pass to tool constructors.

    Returns:
        List[LangChainBaseTool]: List of tool instances for the agent.
    """
    tool_config = load_tool_config()
    tools_list = agent_config.get('tools', [])

    if not tools_list:
        return []

    tools = []
    for tool_name in tools_list:
        if tool_name in tool_config:
            try:
                tool = instantiate_tool(
                    tool_name, tool_config[tool_name], **kwargs)
                tools.append(tool)
            except Exception as e:
                print(f"Error loading tool {tool_name}: {e}")
        else:
            print(f"Warning: Tool {tool_name} not found in configuration")

    return tools


def load_all_tools(**kwargs) -> Dict[str, LangChainBaseTool]:
    """
    Load all tools defined in the configuration.

    Args:
        **kwargs: Additional arguments to pass to tool constructors.

    Returns:
        Dict[str, LangChainBaseTool]: Dictionary of tool instances.
    """
    tool_config = load_tool_config()
    tools = {}

    for tool_name, config in tool_config.items():
        try:
            tool = instantiate_tool(tool_name, config, **kwargs)
            tools[tool_name] = tool
        except Exception as e:
            print(f"Error loading tool {tool_name}: {e}")

    return tools
