# Agent Architecture Summary
**Reviewed: Not yet reviewed**

## Agent Roles
- **Coordinator Agent**: Central orchestrator, delegates tasks, resolves conflicts
- **Technical Architect Agent**: Designs system architecture, makes technology choices
- **Backend Engineer Agent**: Implements server-side functionality, database interactions, APIs
- **Frontend Engineer Agent**: Implements client-side functionality, user interfaces
- **Documentation Agent**: Creates and maintains documentation, generates summaries
- **QA Agent**: Tests system functionality, ensures quality, identifies bugs

## Implementation Details
- Each agent implemented in dedicated Python module (agents/*.py)
- Factory functions provide agent instances with appropriate configuration
- Communication via message passing through LangGraph workflow
- Configuration via YAML files (config/agents.yaml)
- Each agent has specialized tools based on its role

## Tools & Capabilities
- Database interaction via Supabase
- GitHub integration for code management
- Testing tools (Jest, Cypress)
- Design system tools
- Memory engine for context retrieval
- Dynamic tool loading based on agent configuration

## Workflow Integration
- Agents integrated as nodes in LangGraph directed graph
- Agent run() methods triggered by workflow execution
- Standard patterns for task execution, tool usage, context retrieval

---
*Drafted by doc_agent. Technical lead: please review for accuracy and completeness.*