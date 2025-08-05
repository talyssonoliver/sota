# Workflow and Task System Overview

This document provides a comprehensive reference for the task metadata files under `tasks/` and the LangGraph workflows defined in `graph/`. It consolidates information from existing documentation to give a single overview of how work moves through the multi-agent system.

## Task System Architecture

### Task File Inventory

The table below lists all task metadata files found in the `tasks/` directory.

| Task ID | Filename | Agent Type | Title | Dependencies |
|---------|----------|------------|-------|--------------|
| BE-01 | BE-01.yaml | backend | Validate Supabase Setup | TL-09,TL-01 |
| BE-02 | BE-02.yaml | backend | Generate and Insert Seed Data | BE-01 |
| BE-03 | BE-03.yaml | backend | Expand Integration Testing for Supabase | BE-01,TL-01 |
| BE-04 | BE-04.yaml | backend | Validate Local Environment with APIs | TL-01,TL-13 |
| BE-05 | BE-05.yaml | backend | Coordinate with Frontend Developer on Integration Points | FE-05,TL-01 |
| BE-06 | BE-06.yaml | backend | Participate in Final Alignment Meeting | PM-06 |
| BE-07 | BE-07.yaml | backend | Backend Service Layer Implementation |  |
| BE-08 | BE-08.yaml | backend | Implement Error Handling Middleware | TL-01 |
| BE-09 | BE-09.yaml | backend | Create API Documentation | BE-04,BE-07 |
| BE-10 | BE-10.yaml | backend | Update Database Migration Scripts | BE-01 |
| BE-11 | BE-11.yaml | backend | Implement Rate Limiting for APIs | BE-04 |
| BE-12 | BE-12.yaml | backend | Test Stripe Integration | TL-13 |
| BE-13 | BE-13.yaml | backend | Test Cloudinary Integration | TL-13 |
| BE-14 | BE-14.yaml | backend | Implement Authentication Middleware | BE-01,BE-08 |
| FE-01 | FE-01.yaml | frontend | Validate Local Environment Setup | TL-01,TL-13 |
| FE-02 | FE-02.yaml | frontend | Implement Core UI Components | FE-01,TL-01 |
| FE-03 | FE-03.yaml | frontend | Review and Integrate Design Handoff | UX-13 |
| FE-04 | FE-04.yaml | frontend | Establish TypeScript Integration with Backend | BE-05,TL-01 |
| FE-05 | FE-05.yaml | frontend | Coordinate with Backend Developer on API Integration | BE-05,BE-04 |
| FE-06 | FE-06.yaml | frontend | Participate in Final Alignment Meeting | PM-06 |
| LC-01 | LC-01.yaml | product | Conduct Initial Legal and GDPR Compliance Check |  |
| PM-01 | PM-01.yaml | product | Finalise and Document MVP Product Backlog |  |
| PM-02 | PM-02.yaml | product | Create Visual Product Roadmap for 3 Months | PM-01 |
| PM-03 | PM-03.yaml | product | Develop Communication Plan for Stakeholders |  |
| PM-04 | PM-04.yaml | product | Align User Stories with Technical Architecture | TL-01,PM-01 |
| PM-05 | PM-05.yaml | product | Set Up GitHub Projects Board | TL-01 |
| PM-06 | PM-06.yaml | product | Schedule and Conduct Final Alignment Meeting |  |
| PM-07 | PM-07.yaml | product | Establish Sprint 0 Goals and Success Metrics | PM-01,PM-02 |
| PM-08 | PM-08.yaml | product | Confirm External Dependencies and Risks |  |
| PM-09 | PM-09.yaml | product | Prepare Stakeholder Kick-off Presentation | PM-01,PM-02,PM-03 |
| PM-10 | PM-10.yaml | product | Create Sprint 0 Daily Check-in Schedule |  |
| PM-11 | PM-11.yaml | product | Develop User Persona Documentation |  |
| PM-12 | PM-12.yaml | product | Map Customer Journey for Core Flows | PM-11 |
| QA-01 | QA-01.yaml | qa | Draft QA Testing Plan |  |
| QA-02 | QA-02.yaml | qa | Set Up Testing Environment | TL-01,BE-04 |
| QA-03 | QA-03.yaml | qa | Participate in Final Alignment Meeting | PM-06 |
| TL-01 | TL-01.yaml | technical | Verify GitHub Repository and Branch Structure |  |
| TL-02 | TL-02.yaml | technical | Configure Branch Protection Rules | TL-01 |
| TL-03 | TL-03.yaml | technical | Update PR and Issue Templates | TL-01 |
| TL-04 | TL-04.yaml | technical | Verify Next.js Project Structure | TL-01 |
| TL-05 | TL-05.yaml | technical | Enhance ESLint, Prettier, and Husky Configuration | TL-04 |
| TL-06 | TL-06.yaml | technical | Validate Directory Structure | TL-04 |
| TL-07 | TL-07.yaml | technical | Configure Vercel Project and Environments | TL-01 |
| TL-08 | TL-08.yaml | technical | Set Up CI/CD Workflows | TL-01,TL-07 |
| TL-09 | TL-09.yaml | technical | Verify Supabase Project and Schema |  |
| TL-10 | TL-10.yaml | technical | Verify RLS Policies for Supabase | TL-09 |
| TL-11 | TL-11.yaml | technical | Verify Stripe Test Account and Integration |  |
| TL-12 | TL-12.yaml | technical | Verify Cloudinary Configuration |  |
| TL-13 | TL-13.yaml | technical | Distribute Environment Variables | TL-09,TL-11,TL-12 |
| TL-14 | TL-14.yaml | technical | Verify Sentry Configuration | TL-04 |
| TL-15 | TL-15.yaml | technical | Enhance Authentication Boilerplate | TL-09 |
| TL-16 | TL-16.yaml | technical | Expand API Routes Structure | TL-04,TL-09 |
| TL-17 | TL-17.yaml | technical | Document Architecture and Technical Decisions |  |
| TL-18 | TL-18.yaml | technical | Create Type Definitions for Data Models | TL-09 |
| TL-19 | TL-19.yaml | technical | Add Security Headers Configuration | TL-04 |
| TL-20 | TL-20.yaml | technical | Set Up Core Contexts and Providers | TL-15 |
| TL-21 | TL-21.yaml | technical | Enhance Data Fetching Utilities | TL-16 |
| TL-22 | TL-22.yaml | technical | Configure Testing Environment | TL-04 |
| TL-23 | TL-23.yaml | technical | Create Sample Test Cases | TL-22 |
| TL-24 | TL-24.yaml | technical | Set Up Base Project GitHub Wiki | TL-01 |
| TL-25 | TL-25.yaml | technical | Update Development Environment Guide |  |
| TL-26 | TL-26.yaml | technical | Prepare Technical Demo for Team |  |
| TL-27 | TL-27.yaml | technical | Conduct Technical Onboarding Session | TL-26 |
| TL-28 | TL-28.yaml | technical | Review Backend Engineer Initial Setup | BE-01,BE-02,BE-03 |
| TL-29 | TL-29.yaml | technical | Review Frontend Engineer Initial Setup | FE-01,FE-02,FE-03 |
| TL-30 | TL-30.yaml | technical | Participate in Final Alignment Meeting | PM-06 |
| UX-01 | UX-01.yaml | ux | Refine High-Fidelity Prototype for Homepage |  |
| UX-02 | UX-02.yaml | ux | Create High-Fidelity Prototype for Product Listing | BE-01 |
| UX-03 | UX-03.yaml | ux | Create High-Fidelity Prototype for Product Detail | BE-01 |
| UX-04 | UX-04.yaml | ux | Create High-Fidelity Prototype for Cart & Checkout | BE-05 |
| UX-05 | UX-05.yaml | ux | Create High-Fidelity Prototype for Authentication Flows | BE-01 |
| UX-06 | UX-06.yaml | ux | Refine Design System |  |
| UX-07 | UX-07.yaml | ux | Create Component Library | UX-06 |
| UX-08 | UX-08.yaml | ux | Design Animation & Interaction Specifications | UX-06,UX-07 |
| UX-09 | UX-09.yaml | ux | Create Skeleton Loading States | UX-01,UX-02,UX-03,UX-04,UX-05 |
| UX-10 | UX-10.yaml | ux | Design Toast Notification System | UX-06,UX-07 |
| UX-11 | UX-11.yaml | ux | Create User Flow Diagrams |  |
| UX-12 | UX-12.yaml | ux | Design Mobile-Specific Gesture Interactions | UX-01,UX-02,UX-03,UX-04,UX-05 |
| UX-13 | UX-13.yaml | ux | Prepare Design Handoff Documentation | UX-01,UX-02,UX-03,UX-04,UX-05,UX-06,UX-07,UX-08,UX-09,UX-10,UX-11,UX-12 |
| UX-14 | UX-14.yaml | ux | Export Design Tokens for Developer Integration | UX-06,FE-01 |
| UX-15 | UX-15.yaml | ux | Create Responsive Breakpoint Documentation | UX-01,UX-02,UX-03,UX-04,UX-05 |
| UX-16 | UX-16.yaml | ux | Draft Usability Testing Plan | UX-01,UX-02,UX-03,UX-04,UX-05 |
| UX-17 | UX-17.yaml | ux | Create Icon Set for E-commerce | UX-06 |
| UX-18 | UX-18.yaml | ux | Design Brazilian Artisanal Brand Elements | UX-06 |
| UX-19 | UX-19.yaml | ux | Create Accessibility Guidelines Document | UX-06,UX-07 |
| UX-21 | UX-21.yaml | ux | Coordinate with Backend Developer on Data Requirements | BE-05,UX-01,UX-02,UX-03,UX-04,UX-05 |
| UX-21b | UX-21b.yaml | ux | Coordinate with Frontend Developer on Component Implementation | FE-03,UX-07,UX-08 |
| UX-22 | UX-22.yaml | ux | Establish Image Guidelines for Product Photography | UX-06 |
| UX-23 | UX-23.yaml | ux | Create Error State Designs | UX-06,UX-07 |
| UX-24 | UX-24.yaml | ux | Review Analytics Requirements with PM | PM-01 |
| UX-25 | UX-25.yaml | ux | Participate in Final Alignment Meeting | PM-06 |
### Task Naming Convention

Task IDs use a prefix to denote the responsible agent type followed by a number. Prefixes include `BE` for Backend, `FE` for Frontend, `TL` for Technical Lead, `QA` for Quality Assurance, `PM` for Product Management, `UX` for User Experience, and `LC` for Legal/Compliance. Numbers increment sequentially. Versions are tracked by Git history rather than encoded in the ID.

### Task Categories

- **Planning Tasks** – largely prefixed with `TL` and `PM` for early coordination and environment verification.
- **Implementation Tasks** – prefixed with `BE` or `FE` for backend and frontend work.
- **Review/QA Tasks** – prefixed with `QA` to validate code and deployments.
- **Documentation Tasks** – mainly included in technical tasks once QA passes.
- **Coordination Tasks** – typically `PM` items that manage schedules and stakeholder communication.

## Task Definition Schema

Tasks follow the JSON schema in `tasks/task-schema.json`. The YAML structure includes:

```yaml
id: BE-07                   # Unique task identifier
title: "Task Title"         # Human-readable name
owner: backend              # Agent role assigned
depends_on:                 # List of prerequisite task IDs
  - TL-01
state: PLANNED              # Current lifecycle state
priority: HIGH              # Execution urgency
estimation_hours: 3         # Effort estimate in hours
description: >              # Detailed description
  ...
artefacts:                  # Files or directories affected
  - src/example.ts
context_topics:             # Memory context keys
  - db-schema
```

Optional sections include `context_topics`, `artefacts`, `priority` and `estimation_hours`. A full schema reference is available in `task-schema.json`.

## Workflow Patterns

Workflows are defined in the `graph/` directory. `graph_builder.py` constructs a LangGraph directed acyclic graph from `critical_path.json`. Each node corresponds to an agent handler defined in `graph/handlers.py`. `flow.py` implements a simpler state machine with conditional edges while `resilient_workflow.py` adds retry and timeout support.

Common patterns include:

- **Sequential Pattern** – tasks flow through Technical Lead → Implementation → QA → Documentation.
- **Parallel Pattern** – Backend and Frontend tasks may execute in parallel after the planning stage.
- **Conditional Pattern** – the router in `flow.py` branches based on `TaskStatus` to repeat stages or halt on failure.
- **Iterative Pattern** – resilience wrappers retry failed nodes until the maximum attempts are reached.

## Task Lifecycle

`orchestration/states.py` defines the valid task states:

```python
class TaskStatus(str, Enum):
    CREATED = "CREATED"
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    QA_PENDING = "QA_PENDING"
    DOCUMENTATION = "DOCUMENTATION"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    DONE = "DONE"
    BLOCKED = "BLOCKED"
```

State transitions are managed by each agent handler. For example, the Coordinator moves tasks from `CREATED` to `PLANNED`, while QA moves tasks from `QA_PENDING` to `DOCUMENTATION` when tests pass.

## Execution Examples

A typical feature implementation proceeds as follows:

1. **TL-01** verifies repository structure and outputs a plan.
2. **BE-01** validates Supabase setup after TL-09 is complete.
3. **FE-01** verifies the front-end environment in parallel.
4. **QA-01** drafts and runs tests once implementation tasks finish.
5. **Documentation** tasks finalize API docs before marking the feature as `DONE`.

Complex workflows combine many tasks as specified in `critical_path.json`, with LangGraph handling dependencies and retries.

## LangGraph Integration

The LangGraph workflows convert task metadata into nodes and edges. `build_workflow_graph()` reads configuration to add handlers for each agent. Conditional edges use `status_router()` to choose the next node based on `TaskStatus`. The resulting `StateGraph` is compiled and executed through `execute_workflow()`.

## Best Practices

- Keep tasks small and focused with clear inputs and outputs.
- Declare dependencies explicitly to enable proper ordering.
- Use the standard schema fields for consistency.
- Update task state as work progresses to keep workflows accurate.
- Leverage parallel execution where possible for faster completion.

