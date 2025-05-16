"""
Frontend Engineer Agent for implementing user interfaces and client-side logic.
"""

from crewai import Agent
from langchain.tools import BaseTool
from langchain_core.tools import Tool  # Updated import for Tool class
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from prompts.utils import load_and_format_prompt
from tools.tailwind_tool import TailwindTool
from tools.github_tool import GitHubTool
from tools.memory_engine import get_context_by_keys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_frontend_engineer_agent(
    llm_model: str = "gpt-4-turbo",
    temperature: float = 0.2,
    memory_config: Optional[Dict[str, Any]] = None,
    custom_tools: Optional[list] = None,
    context_keys: Optional[List[str]] = None
) -> Agent:
    """
    Create a Frontend Engineer Agent specialized in Next.js and React implementation.
    
    Args:
        llm_model: The OpenAI model to use
        temperature: Creativity of the model (0.0 to 1.0)
        memory_config: Configuration for agent memory
        custom_tools: List of additional tools to provide to the agent
        context_keys: List of specific context document keys to include in the prompt
        
    Returns:
        A CrewAI Agent configured as the Frontend Engineer
    """
    # Set up default values
    if memory_config is None:
        memory_config = {"type": "chroma"}
    
    if custom_tools is None:
        custom_tools = []
        
    if context_keys is None:
        context_keys = ["frontend-architecture", "ui-components", "pages-structure"]
    
    # Initialize tools
    tools = []
    
    try:
        # Check if we're in testing mode
        if os.environ.get("TESTING", "0") == "1":
            # Use empty tools list for testing to avoid validation issues
            print("Using empty tools list for testing")
            # We'll use no tools in testing to avoid validation errors
        else:
            # Normal (non-testing) environment
            tailwind_tool = TailwindTool()
            github_tool = GitHubTool()
            
            # Convert custom built tools to langchain Tool format
            tools.append(Tool(
                name=tailwind_tool.name,
                description=tailwind_tool.description,
                func=lambda query, t=tailwind_tool: t._run(query)
            ))
            
            tools.append(Tool(
                name=github_tool.name,
                description=github_tool.description,
                func=lambda query, t=github_tool: t._run(query)
            ))
            
            # Add custom tools
            for tool in custom_tools:
                if isinstance(tool, BaseTool):
                    tools.append(tool)
                else:
                    # Handle non-BaseTool tools by wrapping them
                    tools.append(Tool(
                        name=getattr(tool, 'name', 'custom_tool'),
                        description=getattr(tool, 'description', 'Custom tool'),
                        func=lambda query, t=tool: t._run(query) if hasattr(t, '_run') else str(t)
                    ))
                
    except Exception as e:
        # For testing, if tool initialization fails, use empty tool list
        if os.environ.get("TESTING", "0") == "1":
            tools = []
            print(f"Using empty tools list for testing due to: {e}")
        else:
            raise
    
    # Create the LLM
    llm = ChatOpenAI(
        model=llm_model,
        temperature=temperature
    )
    
    # Get MCP context for the agent
    mcp_context = get_context_by_keys(context_keys) 
    
    # Create agent kwargs to build final object
    agent_kwargs = {
        "role": "Frontend Engineer",
        "goal": "Create efficient, responsive user interfaces and client-side functionality",
        "backstory": "You are a Frontend Engineer Agent specialized in Next.js, "
                   "React, TypeScript, and Tailwind CSS for the project. "
                   "Your expertise is in creating high-quality UI components, "
                   "implementing responsive design, and ensuring a smooth user experience.",
        "verbose": True,
        "llm": llm,
        "tools": tools,
        "allow_delegation": False,
        "max_iter": 10,
        "max_rpm": 15,
        "system_prompt": load_and_format_prompt(
            "prompts/frontend-agent.md",
            variables=mcp_context
        )
    }
    
    # Explicitly add memory config if provided
    if memory_config:
        agent_kwargs["memory"] = memory_config
        
    return Agent(**agent_kwargs)