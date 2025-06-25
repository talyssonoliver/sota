# AGENT.md

> Canonical operating rules for every LLM-based coding agent (Copilot, Claude, Cursor, etc.) working on the SOTA multi-agent AI system.  
> If another file conflicts, **this one wins**.

## 1 Architecture

* **Multi-Agent System**: 7 specialized agents orchestrated through LangGraph workflows with dynamic routing and dependency management
* **Clean Architecture**: Domain-driven design with specialized layers for agents, orchestration, tools, and configuration
* **Memory Engine**: ChromaDB-powered vector database with AES-256 encryption, multi-tier caching (L1/L2), and tiered storage (hot/warm/cold)
* **Multi-runtime**: Python 3.9+ (backend/agents) + TypeScript/React (frontend/dashboard)
* **Hexagonal Architecture**: Pure domain logic with adapter patterns for external integrations (Supabase, GitHub, Vercel)

## 2 Quality Gates (CI blocks on any failure)

| Gate | Target |
|------|--------|
| **Test coverage** | ≥ 90% (line + branch) for both Python and TypeScript runtimes |
| **Lint – Python** | `flake8`, `black`, `mypy --strict` → 0 errors/warnings |
| **Lint – TS/JS** | `eslint`, `prettier` → 0 errors |
| **Security scan** | OWASP + Bandit → 0 high/medium vulnerabilities |
| **Agent tests** | All 7 specialized agents pass integration tests |
| **Memory engine** | ChromaDB operations, encryption, and caching pass validation |

## 3 Workflow

1. **TDD First** – red → green → refactor for every agent, tool, and orchestration change
2. **Agent-Driven Development** – Changes must consider impact across all 7 specialized agents
3. Short-lived branches `feat|fix|chore/<scope>` with agent-specific prefixes when relevant:
   - `agent/<agent-name>/<feature>` for agent-specific changes
   - `orchestration/<feature>` for workflow changes
   - `memory/<feature>` for memory engine changes
4. **CI Pipeline**: tests → lint → security → agent validation → memory engine checks → deploy-staging
5. **HITL (Human-in-the-Loop)**: Mandatory human review with risk assessment engine for HIGH/MEDIUM risk changes
6. Squash-merge to `main` triggers blue/green production deployment

## 4 Agent System Rules

### Core Agents (7 Specialized)
* **Coordinator**: Project management and task orchestration
* **Technical Lead**: Infrastructure, CI/CD, DevOps architecture  
* **Backend Engineer**: Supabase services, APIs, database operations
* **Frontend Engineer**: React/Tailwind UI, component development
* **UX Designer**: Interface design and user experience
* **Product Manager**: Requirements definition and business logic
* **QA Engineer**: Testing, validation, quality assurance
* **Documentation Agent**: Technical writing and comprehensive docs

### Agent Development Standards
* Each agent must have dedicated configuration in `config/agents.yaml`
* Agent-specific tools defined in `tools/` with proper validation
* All inter-agent communication follows A2A (Agent-to-Agent Protocol)
* Context injection from memory engine for domain-aware operations
* **Task Dependencies**: Respect critical path defined in `critical_path.yaml`

## 5 Coding Rules

### Python (Agents & Backend)
* **100% type hints** with dataclasses/Pydantic for agent models
* **LangGraph workflows**: All agent orchestration through graph-based flows
* **ChromaDB integration**: Use memory engine for context-aware operations
* **Security**: No `eval/exec`, secrets managed through environment, AES-256 for sensitive data
* **Async patterns**: All I/O operations with retry + circuit-breaker patterns
* **Agent tools**: Proper tool registration and validation in `tools/` directory

### TypeScript/React (Frontend/Dashboard)
* **Next.js App Router** with functional components and Hooks
* **Tailwind CSS** for styling with design system consistency
* **Agent Monitoring**: Real-time dashboard for agent status and workflow execution
* **Context Display**: UI components for memory engine and agent interaction visualization
* **E2E Testing**: Playwright for critical agent workflow paths

## 6 Memory Engine Standards

* **Vector Database**: ChromaDB with semantic search and context retrieval
* **Encryption**: AES-256 for all stored agent context and sensitive data
* **Caching Strategy**: L1 (memory) + L2 (disk) with TTL management
* **Storage Tiers**: Automatic hot/warm/cold migration based on access patterns
* **PII Detection**: Comprehensive scanning before storage
* **Context Injection**: Domain-specific knowledge delivery to agents

## 7 Testing Requirements

### Agent Testing
* **Unit Tests**: Each agent's core functionality isolated
* **Integration Tests**: Agent-to-agent communication and workflow execution
* **Memory Tests**: ChromaDB operations, encryption, caching validation
* **Tool Tests**: All agent tools with mock external dependencies
* **Workflow Tests**: Complete LangGraph execution paths

### Performance Standards
* **Memory Engine**: < 100ms for context retrieval, < 500ms for complex queries
* **Agent Response**: < 2s for simple tasks, < 10s for complex orchestration
* **Workflow Execution**: Progress tracking with real-time status updates

## 8 Configuration Management

### YAML-Driven Configuration
* `config/agents.yaml`: Agent definitions, capabilities, and tools
* `config/tools.yaml`: Tool configurations and external integrations
* `config/hitl_policies.yaml`: Human-in-the-loop policies and risk thresholds
* `tasks/*.yaml`: Task definitions with dependencies and context domains

### Environment Management
* **Secrets**: All API keys and sensitive config in environment variables
* **Multi-environment**: dev/staging/prod with agent-specific overrides
* **Feature Flags**: Agent capabilities and experimental features

## 9 Security & Performance

### Security Standards
* **Input Validation**: All agent inputs sanitized and validated
* **Memory Encryption**: AES-256 for vector store and caching layers
* **Access Control**: Role-based permissions for agent operations
* **Audit Logging**: Complete trail of agent actions and decisions
* **PII Protection**: Automatic detection and handling of sensitive data

### Performance Optimization
* **Async Orchestration**: Non-blocking agent communication
* **Resource Management**: Memory and CPU limits for agent execution
* **Caching Strategy**: Multi-tier with intelligent prefetching
* **Load Balancing**: Distribute agent workload based on capacity

## 10 Documentation & ADRs

* **Agent Documentation**: Each agent's capabilities, tools, and usage patterns
* **Workflow Documentation**: LangGraph flow diagrams and decision trees
* **API Documentation**: Complete agent API specifications
* **ADRs**: `docs/adr/<YYYYMMDD>-<slug>.md` for architectural decisions
* **Memory Engine Guide**: Comprehensive setup and usage documentation

## 11 Commit Style & Conventions

### Commit Format
* **Subject**: Imperative mood, ≤ 50 chars, agent prefix when relevant
  - `agent(backend): add retry logic for database operations`
  - `memory: implement hot/cold storage migration`
  - `orchestration: add dependency resolution for complex workflows`
* **Body**: Explain **why** and impact on agent system
* **Breaking Changes**: Clearly document agent API or workflow changes

### Agent-Specific Conventions
* **Agent Changes**: Include affected agent names in commit scope
* **Cross-Agent Impact**: Document ripple effects in commit body
* **Memory Changes**: Specify impact on context retrieval and performance
* **Tool Updates**: Note compatibility with existing agent configurations

---

_This AGENT.md defines the canonical operating procedures for the SOTA multi-agent AI system, ensuring consistent development practices across all 7 specialized agents, memory engine operations, and workflow orchestration. All LLM-based coding assistants must follow these rules when contributing to this repository._
