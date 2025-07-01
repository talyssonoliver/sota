"""Agent factory for creating different types of agents."""

import logging
from typing import Dict, Any, Optional, List

try:
    import yaml
except ImportError:
    # Fallback YAML implementation
    class yaml:
        @staticmethod
        def safe_load(stream):
            return {}
        
        @staticmethod
        def safe_dump(data, stream=None):
            if stream:
                stream.write(str(data))
            return str(data)

try:
    from crewai import Agent
except ImportError:
    # Mock Agent class for testing
    class Agent:
        def __init__(self, *args, **kwargs):
            pass

try:
    from src.infrastructure.memory import MemoryEngine
except ImportError:
    MemoryEngine = None

logger = logging.getLogger(__name__)

# Configuration for different agent types
AGENT_CONFIGS = {
    "technical_lead": {
        "role": "Technical Lead",
        "goal": "Oversee technical architecture and coordinate development",
        "backstory": "Experienced technical leader with deep knowledge of software architecture",
        "verbose": True,
        "allow_delegation": True
    },
    "backend": {
        "role": "Backend Engineer",
        "goal": "Develop robust backend services and APIs",
        "backstory": "Expert backend developer with strong knowledge of server-side technologies",
        "verbose": True,
        "allow_delegation": False
    },
    "frontend": {
        "role": "Frontend Engineer", 
        "goal": "Create engaging user interfaces and experiences",
        "backstory": "Skilled frontend developer with expertise in modern web technologies",
        "verbose": True,
        "allow_delegation": False
    },
    "qa": {
        "role": "QA Engineer",
        "goal": "Ensure quality through comprehensive testing",
        "backstory": "Quality assurance specialist with expertise in testing methodologies",
        "verbose": True,
        "allow_delegation": False
    },
    "documentation": {
        "role": "Documentation Writer",
        "goal": "Create clear and comprehensive documentation",
        "backstory": "Technical writer with expertise in software documentation",
        "verbose": True,
        "allow_delegation": False
    },
    "coordinator": {
        "role": "Project Coordinator",
        "goal": "Coordinate tasks and ensure smooth project execution",
        "backstory": "Experienced project coordinator with strong organizational skills",
        "verbose": True,
        "allow_delegation": True
    }
}

def create_agent(agent_type: str, tools: Optional[List] = None, **kwargs) -> Agent:
    """Create an agent of the specified type."""
    if agent_type not in AGENT_CONFIGS:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    config = AGENT_CONFIGS[agent_type].copy()
    config.update(kwargs)
    
    if tools:
        config["tools"] = tools
    
    try:
        return Agent(**config)
    except Exception as e:
        logger.error(f"Failed to create {agent_type} agent: {e}")
        print(f"DEBUG: Exception caught in create_agent: {e}")
        raise

def agent_builder(config: Dict[str, Any]) -> Agent:
    """Build an agent from configuration."""
    agent_type = config.get("type", "technical_lead")
    tools = config.get("tools", [])
    
    return create_agent(agent_type, tools=tools, **config)

# Factory functions for backward compatibility
def create_technical_lead_agent(tools: Optional[List] = None, **kwargs) -> Agent:
    """Create a Technical Lead agent."""
    return create_agent("technical_lead", tools=tools, **kwargs)

def create_backend_engineer_agent(tools: Optional[List] = None, **kwargs) -> Agent:
    """Create a Backend Engineer agent."""
    return create_agent("backend", tools=tools, **kwargs)

def create_backend_agent(tools: Optional[List] = None, **kwargs) -> Agent:
    """Alias for create_backend_engineer_agent."""
    return create_backend_engineer_agent(tools=tools, **kwargs)

def create_frontend_engineer_agent(tools: Optional[List] = None, **kwargs) -> Agent:
    """Create a Frontend Engineer agent."""
    return create_agent("frontend", tools=tools, **kwargs)

def create_frontend_agent(tools: Optional[List] = None, **kwargs) -> Agent:
    """Alias for create_frontend_engineer_agent."""
    return create_frontend_engineer_agent(tools=tools, **kwargs)

def create_qa_agent(tools: Optional[List] = None, **kwargs) -> Agent:
    """Create a QA Engineer agent."""
    return create_agent("qa", tools=tools, **kwargs)

def create_documentation_agent(tools: Optional[List] = None, **kwargs) -> Agent:
    """Create a Documentation Writer agent."""
    return create_agent("documentation", tools=tools, **kwargs)

def create_coordinator_agent(tools: Optional[List] = None, **kwargs) -> Agent:
    """Create a Project Coordinator agent."""
    return create_agent("coordinator", tools=tools, **kwargs)

class AgentFactory:
    """Factory class for creating agents with various configurations."""
    
    def __init__(self, memory_engine=None):
        """Initialize the agent factory.
        
        Args:
            memory_engine: Optional memory engine for context integration
        """
        self.memory_engine = memory_engine
        logger.info("AgentFactory initialized")
    
    def create_agent(self, agent_type: str, context_domains: Optional[List[str]] = None, 
                    tools: Optional[List] = None, **kwargs) -> Agent:
        """Create an agent of the specified type.
        
        Args:
            agent_type: Type of agent to create
            context_domains: Optional list of context domains for memory integration
            tools: Optional list of tools for the agent
            **kwargs: Additional arguments for agent creation
            
        Returns:
            Created agent instance
        """
        # If memory engine is available and context domains are specified,
        # retrieve relevant context
        if self.memory_engine and context_domains:
            try:
                relevant_context = self.memory_engine.get_relevant_context(
                    query="agent context",
                    domains=context_domains
                )
                if relevant_context:
                    kwargs['context'] = relevant_context
            except Exception as e:
                logger.warning(f"Failed to retrieve context for agent: {e}")
        
        # Use the existing create_agent function
        return create_agent(agent_type, tools=tools, **kwargs)

# Export all factory functions and classes
__all__ = [
    "AgentFactory",
    "create_agent",
    "agent_builder", 
    "create_technical_lead_agent",
    "create_backend_engineer_agent",
    "create_backend_agent",
    "create_frontend_engineer_agent",
    "create_frontend_agent", 
    "create_qa_agent",
    "create_documentation_agent",
    "create_coordinator_agent"
]