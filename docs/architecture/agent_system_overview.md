# Agent System Overview

This document summarizes the agents implemented in the `agents/` directory and their relationships.

## Agent Inventory
| File | Role/Purpose |
|------|--------------|
| `agents/coordinator.py` | Coordinator agent that plans and delegates sub‑tasks |
| `agents/technical.py` | Technical Lead agent providing architectural oversight |
| `agents/backend.py` | Backend Engineer agent focused on Supabase APIs |
| `agents/frontend.py` | Frontend Engineer agent building React interfaces |
| `agents/doc.py` | Documentation agent generating project docs |
| `agents/qa.py` | QA agent responsible for testing and coverage analysis |
| `agents/__init__.py` | MemoryEnabledAgentBuilder and agent registry |

All specialized agents ultimately instantiate `crewai.Agent` objects using helper functions that load prompt templates, retrieve context from the memory engine and attach tool lists.

## Hierarchy
```
MemoryEnabledAgentBuilder (agents/__init__.py)
    ├─ create_coordinator_agent
    ├─ create_technical_lead_agent
    ├─ create_backend_engineer_agent
    ├─ create_frontend_engineer_agent
    ├─ create_documentation_agent
    └─ create_qa_agent / create_enhanced_qa_workflow
```
Each factory uses the builder to construct a configured CrewAI agent. The base class for all agents is `crewai.Agent`.

## Interaction Matrix
```
             | TechLead | Backend | Frontend | QA | Doc | Coordinator
-------------|----------|---------|----------|----|-----|-------------
TechLead     |    -     |  Tasks  |  Tasks   | Reviews | Reviews | Guides
Backend      | Reports  |    -    |   API    | Works with | Updates | Receives tasks
Frontend     | Reports  |  Uses   |    -     | Works with | Updates | Receives tasks
QA           | Reports  | Tests   |  Tests   | -  | Reports | Receives tasks
Doc          | Reads    | Docs    |  Docs    | Docs | - | Receives tasks
Coordinator  | Plans    | Plans   |  Plans   | Plans | Plans | -
```
The coordinator assigns work; the technical lead oversees architecture; backend and frontend implement features; QA validates them; documentation agent records progress.

