# AI Agent System Overview
**Reviewed: Not yet reviewed**

## Introduction

The AI Agent System is a multi-agent system designed to automate software development tasks for the Artesanato E-commerce platform. It uses specialized agents, each focused on a specific role in the development process, coordinated through a LangGraph workflow system.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                             AI Agent System                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
           ┌──────────────────────┬─┴───────────────┬──────────────────────┐
           ▼                      ▼                 ▼                      ▼
┌─────────────────────┐ ┌───────────────────┐ ┌─────────────┐ ┌───────────────────┐
│   Agent Registry    │ │  Task Orchestrator │ │  LangGraph  │ │   Memory Engine   │
└─────────────────────┘ └───────────────────┘ └─────────────┘ └───────────────────┘
           │                      │                 │                      │
           └───────────┬──────────┴─────────────────┤                      │
                       │                            │                      │
                       ▼                            ▼                      ▼
               ┌────────────────┐           ┌────────────────┐    ┌────────────────┐
               │    Agents      │           │     Tools      │    │ Knowledge Base │
               └────────────────┘           └────────────────┘    └────────────────┘
```

## Core Components

The system consists of five main architectural components, each documented in detail separately:

1. **[Agent System](agent-system-architecture.md)**: Specialized agents for different roles in the development process
2. **[Memory Engine (MCP)](memory-engine-architecture.md)**: Knowledge management system for context retrieval
3. **[LangGraph Workflow (A2A)](langgraph-workflow-architecture.md)**: Agent communication and task flow system
4. **[Tool System](tool-system-architecture.md)**: Extends agent capabilities with specialized functionality
5. **[Task Orchestration](task-orchestration-architecture.md)**: Coordinates task execution and dependencies

## Execution Flow

The typical execution flow through the system follows these steps:

1. Task is defined in the task registry
2. Task orchestration selects a task based on priority and dependencies
3. Memory engine retrieves relevant context for the task
4. LangGraph workflow is created based on task requirements
5. Agents execute their parts of the task using specialized tools
6. Results are collected, validated, and stored
7. Task state is updated based on execution outcome

## Key Principles

- **Agent Specialization**: Each agent has a specific role and expertise
- **Context-Aware Operations**: All agents operate with relevant contextual knowledge
- **Structured Communication**: Agents communicate via a well-defined protocol
- **Task Dependencies**: Tasks are executed in the right order based on dependencies
- **Tool Integration**: External services are integrated via specialized tools

## Configuration System

The system is configured through YAML files:

- `config/agents.yaml`: Agent configuration
- `config/tools.yaml`: Tool configuration
- `graph/critical_path.yaml`: Workflow configuration
- `tasks/*.yaml`: Task definitions

## Integration Points

The system integrates with several external services:

- **Supabase**: For database operations and authentication
- **GitHub**: For code repository management
- **Vercel**: For frontend deployment
- **Testing Frameworks**: For automated testing

## Common Workflows

1. **Task Execution**: Running a specific task through the agent system
2. **Knowledge Curation**: Processing source documents into agent-friendly summaries
3. **Workflow Customization**: Creating specialized workflows for different task types

## Additional Documentation

- [Service Layer Patterns](../patterns/service-layer-overview.md)
- [Database Schema](../db/db-schema-summary.md)
- [Sprint Information](../sprint/sprint-phase0-summary.md)

---
*Drafted by doc_agent on May 16, 2025. Technical lead: please review for accuracy and completeness.*