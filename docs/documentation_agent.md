# Documentation Agent Documentation

**File:** `agents/doc.py`
**Type:** specialized agent
**Purpose:** Generates project documentation using Markdown and GitHub tools.

## Overview
This module builds a `crewai.Agent` that can create README files and technical guides. Context is fetched from `documentation-standards` and `template-patterns` and the prompt from `prompts/doc-agent.md` is loaded.

## Key Functions
- `build_doc_agent(task_metadata=None, **kwargs)` – delegate to the agent builder with role `doc`.
- `get_doc_context(task_id=None)` – obtains documentation context with fallback.
- `create_documentation_agent(...)` – constructs the documentation specialist agent with optional memory and tools.

## Attributes
- `memory` – exposed for testing.

## Tool Usage
Uses `MarkdownTool`, `GitHubTool`, and any additional custom tools provided.

