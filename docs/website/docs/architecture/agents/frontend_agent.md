# Frontend Engineer Agent Documentation

**File:** `agents/frontend.py`
**Type:** specialized agent
**Purpose:** Creates the frontend engineer responsible for React and Next.js UI implementation.

## Overview
Builds a `crewai.Agent` with Tailwind and GitHub tools. Pulls context from domains `design-system`, `ui-patterns`, and `component-library` and applies `prompts/frontend-agent.md`.

## Key Functions
- `build_frontend_agent(task_metadata=None, **kwargs)` – delegate to the agent builder using role `frontend_engineer`.
- `get_frontend_context(task_id=None)` – fetches frontend context from memory with testing fallbacks.
- `create_frontend_engineer_agent(...)` – constructs the CrewAI agent with optional memory and custom tool support.

## Attributes
- `memory` – module level variable patched during tests.

## Tool Usage
Utilizes `TailwindTool`, `GitHubTool`, and any additional custom tools.

