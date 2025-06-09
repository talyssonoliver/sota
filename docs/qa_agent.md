# QA Agent Documentation

**File:** `agents/qa.py`
**Type:** specialized agent
**Purpose:** Implements quality assurance testing and provides utilities for automated test generation.

## Overview
The module defines a factory to build a standard QA `crewai.Agent` and an `EnhancedQAAgent` class that can generate tests and analyze coverage. Context is retrieved from `testing-patterns`, `quality-standards`, and `coverage-requirements` domains.

## Key Functions
- `build_qa_agent(task_metadata=None, **kwargs)` – create an agent via the builder with role `qa`.
- `get_qa_context(task_id=None)` – fetch QA context with safe fallback.
- `create_qa_agent(...)` – constructs the CrewAI QA agent with Jest, Cypress and Coverage tools.
- `create_enhanced_qa_workflow(project_root=".", config_file=None)` – returns an instance of `EnhancedQAAgent`.

## Classes
### `EnhancedQAAgent`
Provides methods for generating comprehensive tests, analyzing coverage, and producing quality metrics. It can discover source files, determine the correct test framework, and validate quality gates.

## Attributes
- `memory` – module level variable used during tests.

