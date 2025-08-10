# Dependency Map

This document summarizes external and internal dependencies.

## External Packages

Key packages from `requirements.txt`:

- **langchain** 0.3.25 – core language chain framework
- **langchain_openai** 0.3.16 – OpenAI integration
- **langgraph** 0.4.1 – graph-based workflow engine
- **crewai** 0.118.0 – multi-agent orchestration
- **chromadb** – vector store backend for the memory engine
- **supabase** 2.15.1 – database and auth services
- **flask** 3.1.0 – dashboard API server
- **pytest** 8.3.5 – test framework

See `requirements.txt` for the full list.

## Internal Module Dependencies

```
main.py
├── orchestration.workflow_executor
├── orchestration.task_loader
└── agents (via agent_builder)

agents/* -> tools.memory_engine
agents/backend -> tools.supabase_tool, tools.github_tool
agents/frontend -> tools.tailwind_tool, tools.github_tool
agents/qa -> tools.jest_tool, tools.cypress_tool

orchestration.workflow_executor -> graph/*, utils.execution_monitor
```

This simplified graph shows that most agents depend on `tools/memory_engine.py` and at least one additional tool. Workflow execution modules depend on graph definitions and utilities.

