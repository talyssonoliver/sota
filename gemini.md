# Gemini Agent Instructions

## Core Mandates

This document provides the canonical operating rules for the Gemini agent working on this project. It synthesizes and supersedes instructions from all other documents, including `AGENT.md` and `copilot-instructions.md`.

**If any file or instruction conflicts with this one, this document is the single source of truth.**

## 1. Architecture & System Overview

- **System Type**: Multi-Agent System (7 specialized agents).
- **Orchestration**: LangGraph workflows with dynamic routing.
- **Core Technologies**:
    - **Backend/Agents**: Python 3.9+
    - **Frontend/Dashboard**: TypeScript/React (Next.js App Router)
- **Architecture Style**: Clean Architecture, Domain-Driven Design (DDD), and Hexagonal Architecture.
- **Memory Engine**: ChromaDB vector database with multi-tier caching and AES-256 encryption.

## 2. Quality Gates & CI/CD

All changes are gated by a strict CI pipeline. **No exceptions.**

| Gate                | Requirement                                      | Command/Tool              |
| ------------------- | ------------------------------------------------ | ------------------------- |
| **Test Coverage**   | >= 90% (line and branch)                         | `pytest-cov` / `jest`     |
| **Python Linting**  | 0 errors/warnings                                | `ruff`, `black`, `mypy --strict` |
| **TS/JS Linting**   | 0 errors                                         | `eslint`, `prettier`      |
| **Security Scan**   | 0 high/medium vulnerabilities                    | `OWASP` + `Bandit`        |
| **Agent Tests**     | All specialized agents pass integration tests.   | `pytest`                  |
| **Memory Engine**   | All operations (CRUD, encryption, cache) pass.   | `pytest`                  |

## 3. Development Workflow (TDD)

Follow a strict Test-Driven Development (TDD) cycle for all changes.

1.  **Red Phase**: Write failing tests that clearly define the desired functionality or fix.
2.  **Green Phase**: Write the simplest, most direct code required to make the tests pass.
3.  **Refactor Phase**: Improve the code's structure, readability, and performance while ensuring all tests remain green.

## 4. Coding Standards & Patterns

### Python (Primary - Agents & Backend)

- **Type Safety**: 100% type hints. Use Pydantic models or dataclasses for all data structures.
- **Style**: Follow PEP 8 guidelines strictly.
- **Asynchronous Code**: Use `asyncio` for all I/O-bound operations, implementing robust retry and circuit-breaker patterns.
- **Error Handling**: Implement custom, specific exceptions. Avoid generic `except Exception`.
- **Resource Management**: Use context managers (`with` statements) for any resource that needs setup/teardown (files, connections, etc.).
- **Orchestration**: All agent workflows **must** be defined and managed through LangGraph.

### TypeScript & React (Frontend)

- **Component Model**: Use functional components with Hooks. Mark components with `"use client"` only when necessary (i.e., they use browser-specific APIs).
- **Type Safety**: Use TypeScript interfaces or types for all props, API responses, and data structures.
- **State Management**: Use custom hooks for complex or shared state logic.
- **Styling**: Prioritize Tailwind CSS for all styling. Use semantic HTML for accessibility.
- **Component Design**: Adhere to the single-responsibility principle. Keep components small and focused.

## 5. Testing Strategy

- **Python**:
    - **Framework**: `pytest` with `pytest-asyncio`.
    - **Mocking**: `unittest.mock` and `pytest-mock`.
    - **Test Naming**: Use descriptive names, e.g., `test_should_return_auth_error_when_token_is_invalid`.
- **Frontend**:
    - **Framework**: Jest and React Testing Library.
    - **E2E Tests**: Playwright for critical user workflows.
    - **Focus**: Test user behavior and interactions, not internal implementation details.

## 6. Security (Non-Negotiable)

- **Input Validation**: Sanitize and validate **all** external inputs and API payloads.
- **Output Sanitization**: Prevent XSS by sanitizing all data rendered in the UI.
- **Secrets Management**: Use environment variables exclusively for secrets. Never hardcode credentials, tokens, or PII.
- **Database Security**: Use parameterized queries or an ORM to prevent SQL injection.
- **Data Privacy**: Never log sensitive information. Use the PII scanner before storing data in the memory engine.
- **Dependencies**: Regularly scan for vulnerabilities in third-party packages.

## 7. Performance

- **Frontend**:
    - Minimize re-renders using `React.memo`, `useMemo`, and `useCallback`.
    - Implement code splitting and lazy loading.
    - Optimize asset sizes and delivery.
- **Backend**:
    - Optimize database queries (e.g., use `select_related` or `prefetch_related` in Django if applicable).
    - Use appropriate caching strategies (L1/L2 memory engine caches).
    - Profile and monitor performance bottlenecks in agent workflows.

## 8. Commit & Version Control

- **Branching**: Use short-lived feature branches: `feat|fix|chore/<scope>/<description>`.
    - **Agent-specific scope**: `agent/<agent-name>/<feature>`
    - **Orchestration scope**: `orchestration/<feature>`
    - **Memory scope**: `memory/<feature>`
- **Commit Messages**:
    - **Format**: Imperative mood, max 50 characters in the subject line.
    - **Example**: `feat(agent:backend): Add retry logic for API calls`
    - **Body**: Explain the "why" behind the change, not the "what." Document any breaking changes clearly.
