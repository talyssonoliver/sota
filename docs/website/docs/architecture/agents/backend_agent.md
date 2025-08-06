# Backend Engineer Agent Documentation

**File:** `agents/backend.py`
**Type:** specialized agent
**Purpose:** Implements the backend engineer role with Supabase and GitHub integration.

## Overview
Creates a `crewai.Agent` configured for backend tasks. It loads the Supabase and GitHub tools, retrieves memory context, and builds a prompt from `prompts/backend-agent.md`.

## Key Functions
- `build_backend_agent(task_metadata=None, **kwargs)` – delegates to `agent_builder.build_agent` with role `backend_engineer`.
- `get_backend_context(task_metadata=None)` – retrieves context from memory domains `db-schema`, `service-patterns`, and `supabase-setup` with safe fallbacks.
- `create_backend_engineer_agent(...)` – factory function that constructs the agent using `ChatOpenAI`, tools, and optional memory configuration.

## Attributes
- `memory` – module level variable used for patching during tests.

## Tool Usage
Uses `SupabaseTool` and `GitHubTool` plus any `custom_tools` provided.

