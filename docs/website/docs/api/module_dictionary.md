# Module Dictionary

This document provides a high-level alphabetical listing of project modules. Only key modules are described here; see individual documentation files for full details.

## A

### agents
Location: `agents/`
Purpose: Implements the system's AI agents such as backend, frontend, QA, and coordinator.
Exports: multiple agent classes (e.g., `BackendAgent`, `FrontendAgent`).

### agent_builder
Location: `agent_builder.py`
Purpose: Factory for creating memory-enabled agents.

## D

### dashboard
Location: `dashboard/`
Purpose: Flask server and frontend assets for monitoring workflows.

## G

### graph
Location: `graph/`
Purpose: Workflow definitions and execution graphs.

## M

### main
Location: `main.py`
Purpose: Entry point that initializes the system and launches workflows.

### memory_engine
Location: `tools/memory_engine.py`
Purpose: Persistent vector-based memory used by all agents.

## O

### orchestration
Location: `orchestration/`
Purpose: Workflow executor and daily cycle orchestrator modules.

## T

### tasks
Location: `tasks/`
Purpose: YAML task definitions referenced by workflows.

### tools
Location: `tools/`
Purpose: Collection of reusable tools (Supabase, GitHub, Vercel, etc.).

## U

### utils
Location: `utils/`
Purpose: Helper utilities such as completion metrics, execution monitoring, and QA coverage analysis.

