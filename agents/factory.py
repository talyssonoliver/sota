"""
Unified Agent Factory Pattern
Eliminates code duplication across agent creation functions
"""

import os
from typing import Any, Dict, List, Optional

from crewai import Agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from prompts.utils import load_and_format_prompt
from tools.memory import get_context_by_keys

# Load environment variables
load_dotenv()


class AgentFactory:
    """
    Unified factory for creating specialized agents.
    Eliminates the 80% code duplication found in individual agent creation functions.
    """
    
    def __init__(self):
        self.default_config = {
            'llm_model': "gpt-4-turbo",
            'temperature': 0.2,
            'max_tokens': 4000,
            'verbose': True
        }
        
        # Agent-specific configurations
        self.agent_configs = {
            'backend': {
                'role': "Senior Backend Developer",
                'goal': "Design and implement robust backend services using Supabase and modern patterns",
                'backstory': """You are a senior backend developer with expertise in:
                - Supabase database design and RLS policies
                - RESTful API design and implementation
                - Modern backend patterns and architecture
                - Database optimization and performance tuning
                
                You focus on creating scalable, secure, and maintainable backend solutions.""",
                'tools': ['supabase_tool', 'github_tool'],
                'context_domains': ['db-schema', 'service-patterns', 'supabase-setup'],
                'prompt_template': 'prompts/backend-agent.md'
            },
            
            'frontend': {
                'role': "Senior Frontend Developer", 
                'goal': "Create beautiful, responsive, and accessible user interfaces using modern frameworks",
                'backstory': """You are a senior frontend developer with expertise in:
                - React, Next.js, and modern JavaScript/TypeScript
                - Responsive design and mobile-first development
                - Accessibility (WCAG) best practices
                - Component-driven development
                - State management and performance optimization
                
                You create user experiences that are both beautiful and functional.""",
                'tools': ['github_tool', 'tailwind_tool'],
                'context_domains': ['design-system', 'ui-patterns', 'component-library'],
                'prompt_template': 'prompts/frontend-agent.md'
            },
            
            'qa': {
                'role': "Senior QA Engineer",
                'goal': "Ensure comprehensive testing coverage and maintain high code quality standards",
                'backstory': """You are a senior QA engineer with expertise in:
                - Test automation frameworks (Jest, Cypress, Playwright)
                - Test-driven development (TDD) and behavior-driven development (BDD)
                - Performance testing and load testing
                - Security testing and vulnerability assessment
                - CI/CD pipeline integration and quality gates
                
                You ensure that every feature meets quality standards before release.""",
                'tools': ['jest_tool', 'cypress_tool', 'coverage_tool'],
                'context_domains': ['testing-patterns', 'quality-standards', 'coverage-requirements'],
                'prompt_template': 'prompts/qa-agent.md'
            },
            
            'technical': {
                'role': "Technical Lead",
                'goal': "Provide technical leadership and ensure architectural consistency across the project",
                'backstory': """You are a technical lead with expertise in:
                - System architecture and design patterns
                - Infrastructure as Code (IaC) and deployment strategies
                - Performance optimization and scalability planning
                - Code review and technical mentoring
                - Risk assessment and technical decision-making
                
                You guide the technical direction and ensure best practices are followed.""",
                'tools': ['github_tool', 'vercel_tool'],
                'context_domains': ['infrastructure', 'deployment', 'architecture'],
                'prompt_template': 'prompts/technical-architect.md'
            },
            
            'doc': {
                'role': "Documentation Specialist",
                'goal': "Create comprehensive, clear, and maintainable documentation for all project aspects",
                'backstory': """You are a documentation specialist with expertise in:
                - Technical writing and documentation best practices
                - API documentation and developer guides
                - User experience documentation
                - Documentation automation and tooling
                - Information architecture and content organization
                
                You ensure that all stakeholders have access to clear, accurate documentation.""",
                'tools': ['markdown_tool', 'github_tool'],
                'context_domains': ['documentation-standards', 'template-patterns'],
                'prompt_template': 'prompts/doc-agent.md'
            },
            
            'coordinator': {
                'role': "Project Manager",
                'goal': "Coordinate tasks across agents and ensure smooth project execution",
                'backstory': """You are a project coordinator with expertise in:
                - Project management and task coordination
                - Cross-functional team collaboration
                - Workflow optimization and process improvement
                - Risk management and issue resolution
                - Communication and stakeholder management
                
                You ensure that all project pieces come together cohesively.""",
                'tools': [],
                'context_domains': ['project-overview', 'workflow-patterns', 'coordination-standards'],
                'prompt_template': 'prompts/coordinator.md'
            }
        }
    
    def create_agent(self, agent_type: str, 
                    llm_model: str = None,
                    temperature: float = None,
                    max_tokens: int = None,
                    memory_config: Optional[Dict[str, Any]] = None,
                    custom_tools: Optional[List] = None,
                    context_keys: Optional[List[str]] = None,
                    **kwargs) -> Agent:
        """
        Create a specialized agent with unified configuration.
        
        Args:
            agent_type: Type of agent to create ('backend', 'frontend', 'qa', etc.)
            llm_model: LLM model to use
            temperature: Temperature for LLM
            max_tokens: Maximum tokens for LLM
            memory_config: Memory configuration (deprecated, kept for compatibility)
            custom_tools: Custom tools to add
            context_keys: Additional context keys to retrieve
            **kwargs: Additional parameters
            
        Returns:
            Configured CrewAI Agent
        """
        if agent_type not in self.agent_configs:
            raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(self.agent_configs.keys())}")
        
        config = self.agent_configs[agent_type]
        
        # Merge configuration
        final_config = self.default_config.copy()
        final_config.update({
            'llm_model': llm_model or final_config['llm_model'],
            'temperature': temperature if temperature is not None else final_config['temperature'],
            'max_tokens': max_tokens or final_config['max_tokens']
        })
        final_config.update(kwargs)
        
        # Create LLM
        llm = ChatOpenAI(
            model=final_config['llm_model'],
            temperature=final_config['temperature'],
            max_tokens=final_config['max_tokens']
        )
        
        # Load tools
        tools = self._load_tools(config['tools'], custom_tools)
        
        # Get context
        context = self._get_agent_context(
            agent_type, 
            config['context_domains'], 
            context_keys
        )
        
        # Load and format prompt
        formatted_prompt = self._load_formatted_prompt(
            config['prompt_template'],
            context,
            agent_type
        )
        
        # Create agent
        agent = Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=tools,
            llm=llm,
            verbose=final_config.get('verbose', True),
            memory=True,
            max_iter=final_config.get('max_iter', 15),
            max_execution_time=final_config.get('max_execution_time', 300)
        )
        
        # Attach additional metadata
        agent._agent_type = agent_type
        agent._context = context
        agent._formatted_prompt = formatted_prompt
        
        return agent
    
    def _load_tools(self, tool_names: List[str], custom_tools: Optional[List] = None) -> List:
        """Load tools for the agent."""
        tools = []
        
        # Skip tool loading in testing environment
        if os.environ.get("TESTING", "0") == "1":
            return tools
        
        # Load configured tools
        tool_map = {
            'supabase_tool': 'tools.supabase_tool:SupabaseTool',
            'github_tool': 'tools.github_tool:GitHubTool', 
            'tailwind_tool': 'tools.tailwind_tool:TailwindTool',
            'jest_tool': 'tools.jest_tool:JestTool',
            'cypress_tool': 'tools.cypress_tool:CypressTool',
            'coverage_tool': 'tools.coverage_tool:CoverageTool',
            'vercel_tool': 'tools.vercel_tool:VercelTool',
            'markdown_tool': 'tools.markdown_tool:MarkdownTool'
        }
        
        for tool_name in tool_names:
            if tool_name in tool_map:
                try:
                    module_path, class_name = tool_map[tool_name].split(':')
                    module = __import__(module_path.replace('/', '.'), fromlist=[class_name])
                    tool_class = getattr(module, class_name)
                    tools.append(tool_class())
                except Exception as e:
                    print(f"Warning: Could not load tool {tool_name}: {e}")
        
        # Add custom tools
        if custom_tools:
            tools.extend(custom_tools)
        
        return tools
    
    def _get_agent_context(self, agent_type: str, context_domains: List[str], 
                          additional_keys: Optional[List[str]] = None) -> str:
        """Get relevant context for the agent."""
        try:
            # Combine context domains with additional keys
            all_keys = context_domains.copy()
            if additional_keys:
                all_keys.extend(additional_keys)
            
            # Get context from memory
            context_items = get_context_by_keys(all_keys)
            
            if context_items:
                return '\n\n'.join(str(item) for item in context_items)
            else:
                return f"# Context for {agent_type} agent\n\nNo specific context available."
                
        except Exception as e:
            print(f"Warning: Could not retrieve context for {agent_type}: {e}")
            return f"# Context for {agent_type} agent\n\nContext retrieval failed: {str(e)}"
    
    def _load_formatted_prompt(self, template_path: str, context: str, agent_type: str) -> str:
        """Load and format the prompt template."""
        try:
            return load_and_format_prompt(
                template_path,
                {'context': context, 'agent_type': agent_type}
            )
        except Exception as e:
            print(f"Warning: Could not load prompt template {template_path}: {e}")
            return f"You are a {agent_type} agent. Use the following context:\n\n{context}"
    
    def get_available_agent_types(self) -> List[str]:
        """Get list of available agent types."""
        return list(self.agent_configs.keys())
    
    def get_agent_info(self, agent_type: str) -> Dict[str, Any]:
        """Get information about a specific agent type."""
        if agent_type not in self.agent_configs:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return self.agent_configs[agent_type].copy()


# Global factory instance
agent_factory = AgentFactory()


# Convenience functions that maintain backward compatibility
def create_backend_engineer_agent(**kwargs) -> Agent:
    """Create backend engineer agent."""
    return agent_factory.create_agent('backend', **kwargs)


def create_frontend_engineer_agent(**kwargs) -> Agent:
    """Create frontend engineer agent."""
    return agent_factory.create_agent('frontend', **kwargs)


def create_qa_agent(**kwargs) -> Agent:
    """Create QA agent."""
    return agent_factory.create_agent('qa', **kwargs)


def create_technical_lead_agent(**kwargs) -> Agent:
    """Create technical lead agent."""
    return agent_factory.create_agent('technical', **kwargs)


def create_documentation_agent(**kwargs) -> Agent:
    """Create documentation agent."""
    return agent_factory.create_agent('doc', **kwargs)


def create_coordinator_agent(**kwargs) -> Agent:
    """Create coordinator agent."""
    return agent_factory.create_agent('coordinator', **kwargs)


# Enhanced QA workflow (preserved from original)
def create_enhanced_qa_workflow(**kwargs) -> Dict[str, Agent]:
    """Create enhanced QA workflow with multiple specialized agents."""
    return {
        'qa_lead': create_qa_agent(**kwargs),
        'test_automation': create_qa_agent(
            goal="Focus on test automation and framework development",
            **kwargs
        ),
        'performance_qa': create_qa_agent(
            goal="Focus on performance testing and optimization",
            **kwargs
        )
    }