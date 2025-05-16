"""
Coordinator Agent for orchestrating the work of all specialized agents.
"""

from crewai import Agent
from langchain.tools import BaseTool
from langchain_core.tools import Tool  # Updated import for Tool class
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from prompts.utils import load_and_format_prompt
from tools.memory_engine import get_context_by_keys


def create_coordinator_agent(
    llm_model: str = "gpt-3.5-turbo-16k",
    temperature: float = 0.2,
    memory_config: Optional[Dict[str, Any]] = None,
    custom_tools: Optional[list] = None,
    context_keys: Optional[List[str]] = None
) -> Agent:
    """
    Create a Coordinator Agent that oversees task flow and delegation.
    
    Args:
        llm_model: The OpenAI model to use
        temperature: Creativity of the model (0.0 to 1.0)
        memory_config: Configuration for agent memory
        custom_tools: List of additional tools to provide to the agent
        context_keys: List of specific context document keys to include in the prompt
        
    Returns:
        A CrewAI Agent configured as the Coordinator
    """
    # Set up default values
    if memory_config is None:
        memory_config = {"type": "chroma"}
    
    if custom_tools is None:
        custom_tools = []
        
    if context_keys is None:
        context_keys = ["agent-task-assignments", "project-overview", "workflow-patterns"]
    
    # Initialize the tools
    try:
        # Convert custom tools to valid langchain Tool objects if needed
        tools = []
        
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
        import os
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
    
    # Create the agent
    return Agent(
        role="Project Manager",
        goal="Oversee task flow and assign specialized agents to appropriate tasks",
        backstory="You are the Coordinator Agent for the Artesanato E-commerce project, responsible for orchestrating the work of all specialized agents.",
        verbose=True,
        llm=llm,
        tools=tools,
        memory=memory_config,
        allow_delegation=True,
        max_iter=10,
        max_rpm=20,  # Rate limiting to prevent API overuse
        system_prompt=load_and_format_prompt(
            "prompts/coordinator.md",
            variables=mcp_context
        )
    )