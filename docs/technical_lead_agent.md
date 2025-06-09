# Technical Lead Agent Documentation

**File:** `agents/technical.py`
**Type:** specialized agent
**Purpose:** Provides architectural guidance and oversees technical quality across the project.

## Overview
Creates a `crewai.Agent` that uses Vercel and GitHub tools. Context is loaded from `infrastructure`, `deployment`, and `architecture` domains. Prompts come from `prompts/technical-architect.md`.

## Key Functions
- `build_technical_agent(task_metadata=None, **kwargs)` – builder helper for role `technical_lead`.
- `get_technical_context(task_id=None)` – obtains architectural context with error-handling fallback.
- `create_technical_lead_agent(...)` – builds the agent with memory configuration and optional custom tools.

## Attributes
- `memory` – module variable for testing patches.

## Tool Usage
Employs `VercelTool`, `GitHubTool`, and any extra tools supplied via `custom_tools`.

