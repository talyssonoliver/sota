# Class Dictionary

This reference lists notable classes across the codebase. The list is not exhaustive but covers the most important ones.

## A

### ArtesanatoBaseTool
- **Module:** `tools/base_tool.py`
- **Purpose:** Base class for all custom tools providing a LangChain-compatible interface.

### AgentBuilder
- **Module:** `agent_builder.py`
- **Purpose:** Constructs memory-enabled agents from configuration.

## B

### BackendAgent
- **Module:** `agents/backend.py`
- **Purpose:** Implements API and data layer tasks using Supabase and GitHub tools.

## C

### CoordinatorAgent
- **Module:** `agents/coordinator.py`
- **Purpose:** Oversees multi-agent workflows and delegates tasks.

## D

### DocumentationAgent
- **Module:** `agents/doc.py`
- **Purpose:** Generates markdown reports and updates documentation.

## F

### FrontendAgent
- **Module:** `agents/frontend.py`
- **Purpose:** Builds UI components with Tailwind and React.

## M

### MemoryEngine
- **Module:** `tools/memory_engine.py`
- **Purpose:** Provides persistent vector store with caching and security features.

## Q

### QAAgent
- **Module:** `agents/qa.py`
- **Purpose:** Generates and executes tests, verifying outputs.

### RetrievalQARateLimiter
- **Module:** `tools/rate_limiter.py`
- **Purpose:** Limits retrieval QA requests per user.

