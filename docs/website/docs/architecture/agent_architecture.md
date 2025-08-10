# Agent Architecture

This document describes the architecture of the agent system used in the AI Agent System for Artesanato E-commerce.

## Overview

The system uses multiple specialized agents, each with a specific role in the software development process. These agents collaborate to complete tasks for the Artesanato E-commerce project.

## Agent Roles

### Coordinator Agent
Acts as the central coordinator for the multi-agent system. Delegates tasks, resolves conflicts, and ensures that all agents are working together effectively.

### Technical Architect Agent
Designs the overall system architecture, makes technology choices, and ensures that the technical implementation aligns with the project requirements.

### Backend Engineer Agent
Implements server-side functionality, database interactions, and API endpoints according to the technical architecture.

### Frontend Engineer Agent
Implements client-side functionality, user interfaces, and interactions according to the design specifications.

### Documentation Agent
Creates and maintains documentation for the system, including API documentation, user guides, and developer documentation.

### QA Agent
Tests the system to ensure quality, identifies bugs, and verifies that the implementation meets requirements.

## Agent Implementation

Each agent is implemented as a class in the `agents/` directory:

- `agents/coordinator.py`: Coordinator Agent
- `agents/technical.py`: Technical Architect Agent
- `agents/backend.py`: Backend Engineer Agent
- `agents/frontend.py`: Frontend Engineer Agent
- `agents/doc.py`: Documentation Agent
- `agents/qa.py`: QA Agent

## Agent Creation

Agents are created through factory functions defined in each agent module. For example:

```python
def create_coordinator_agent(custom_tools=None, **kwargs):
    """
    Create a coordinator agent instance.
    
    Args:
        custom_tools: Optional list of tools to provide to the agent
        **kwargs: Additional configuration parameters
        
    Returns:
        A coordinator agent instance
    """
    # Agent creation logic
```

## Agent Communication

Agents communicate using a message passing system implemented through the LangGraph workflow. Messages are passed between agents according to the defined workflow structure.

## Agent Configuration

Agents are configured through YAML files in the `config/` directory:

- `config/agents.yaml`: Defines agent roles, capabilities, and configurations

Each agent can be configured with different parameters, including:

- Model to use (e.g., GPT-4)
- Temperature setting
- Tools available to the agent
- Prompt template to use

## Agent Tools

Agents have access to various tools that extend their capabilities:

- Database tools (Supabase)
- GitHub integration
- Testing tools (Jest, Cypress)
- Design tools
- Memory engine for context retrieval

Tools are loaded dynamically based on the agent's configuration using the tool loader system.

## Integration with Workflow

Agents are integrated into the LangGraph workflow as nodes in the graph. Each agent's `run()` method is called when its node is executed in the workflow.

## Common Patterns

### Task Execution
```python
agent = get_agent("backend")
result = agent.run({
    "task_id": "BE-07",
    "message": "Implement customer service functions"
})
```

### Tool Usage
```python
# Inside an agent's execution
result = self.use_tool("supabase", "query_database", {
    "table": "products",
    "query": {"category": "handicrafts"}
})
```

### Context Retrieval
```python
context = self.memory_engine.retrieve_context("database schema")
```