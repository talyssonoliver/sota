# AI Agent System for Artesanato E-commerce

This project implements a **production-ready multi-agent AI system** that automates end-to-end software development workflows for the Artesanato E-commerce platform. The system orchestrates 7 specialized agents through sophisticated LangGraph workflows, featuring enterprise-grade security, real-time monitoring, and comprehensive automation capabilities.

## 🏗️ Architecture Overview

**Multi-Agent Orchestration**: 7 specialized agents (Technical Lead, Backend, Frontend, QA, Documentation, Product Manager, UX Designer) work collaboratively through LangGraph workflows with dynamic routing and dependency management.

**Enterprise Memory Engine**: ChromaDB-powered vector database with AES-256 encryption, PII detection, multi-tier caching, and tiered storage (hot/warm/cold) for context-aware operations.

**Workflow Automation**: Complete daily cycle automation with morning briefings, real-time execution monitoring, end-of-day reports, and stakeholder notifications.

**Quality Assurance**: Multi-level QA pipeline with automated testing (Jest/Cypress), code quality analysis, and comprehensive coverage tracking.

## 🚀 Recent Updates (December 2024)

### 🔐 Memory Engine Security & Performance Overhaul (COMPLETED)
The Memory Engine has undergone a comprehensive security audit and performance optimization, resulting in a production-ready enterprise-grade system:

**Critical Security Fixes:**
- ✅ **Fixed insecure hash vulnerabilities** - Replaced collision-prone hash() with SHA256
- ✅ **Implemented comprehensive PII detection** - Complete SecurityManager integration
- ✅ **Enhanced encryption & key management** - Proper Fernet/AES-GCM implementation
- ✅ **Added input sanitization** - Protection against injection attacks and XSS

**Major Bug Fixes:**
- ✅ **Fixed core retrieval flow bug** - Restored proper encryption/storage mechanisms
- ✅ **Eliminated duplicate code** - Removed conflicting function definitions
- ✅ **Fixed invalid references** - Corrected all retriever_store → vector_store calls
- ✅ **Resolved syntax errors** - Fixed missing newlines across all classes

**Performance Improvements:**
- ✅ **Multi-tiered caching** - L1 (memory) + L2 (disk) with analytics
- ✅ **Tiered storage management** - Hot/warm/cold with automatic migration
- ✅ **Partition management** - Complete lifecycle with health monitoring
- ✅ **Access pattern optimization** - LRU eviction and smart preloading

**Implementation Completeness:**
- ✅ **100% test success rate** - All 95+ tests passing including 6 memory engine tests
- ✅ **Complete method implementations** - All placeholder methods fully implemented
- ✅ **Comprehensive error handling** - Graceful degradation and recovery
- ✅ **Production monitoring** - Audit logging, health metrics, and alerts

📖 **Documentation**: [Memory Engine Guide](docs/memory_engine.md) | [Security Fixes Report](docs/memory_engine_code_review_fixes.md)

## Overview

The system uses specialized agents for different roles (Technical Lead, Backend Engineer, Frontend Engineer, etc.) to complete pre-Sprint 0 tasks. It follows these design principles:

- **MCP (Model Context Protocol)**: Provides agents with relevant context from the knowledge base
- **A2A (Agent-to-Agent Protocol)**: Enables structured communication between agents
- **LangGraph**: Defines workflows as directed graphs with agents as nodes
- **CrewAI**: Creates role-specialized agents with distinct capabilities
- **Dynamic Workflow**: Adapts to task requirements and dependencies, allowing for flexible execution paths
- **Task Orchestration**: Manages task execution order based on dependencies, ensuring efficient resource utilization
- **LangSmith**: Unifies observation and testing for all agents, providing a consistent interface for monitoring and debugging
- **Tool Loader**: Loads and configures tools for each agent, enabling them to perform specialized tasks
- **Tool Integration**: Connects agents to external tools (e.g., Supabase, GitHub) for enhanced functionality
- **Testing Framework**: Provides a unified test runner for validating agent functionality and system integration
- **Documentation**: Generates comprehensive reports and documentation for each task, ensuring transparency and traceability
- **Progress Tracking**: Monitors task completion and generates reports for each sprint cycle


## 🏗️ Consolidated Architecture (2024 Optimization)

The project has been optimized from 25+ scattered directories to **8 logical modules** with eliminated code duplication:

### 📁 New Consolidated Structure

```
ai-system/
├── 📄 Core Configuration
│   ├── main.py                     # Main entry point
│   ├── README.md                   # Documentation
│   ├── requirements.txt            # Dependencies
│   └── CLAUDE.md                  # AI assistant instructions
│
├── 📁 src/                        # NEW: Consolidated source code
│   ├── core/                      # Core business logic
│   │   ├── agents/               # AI agent implementations
│   │   ├── workflows/            # LangGraph workflow definitions
│   │   └── tasks/                # Task management logic
│   │
│   ├── interfaces/               # User interfaces
│   │   ├── api/                  # REST API endpoints
│   │   ├── cli/                  # Command-line interfaces
│   │   └── dashboard/            # Unified dashboard (was scattered)
│   │       ├── api/             # Dashboard API server
│   │       ├── components/      # Dashboard widgets & components
│   │       └── templates/       # Dashboard templates
│   │
│   └── platform/                # Platform services
│       ├── memory/              # Unified memory system
│       │   ├── engines/        # Memory engine implementations
│       │   ├── knowledge/      # Knowledge repository (was memory-bank/)
│       │   ├── config/         # Memory configuration
│       │   └── security/       # Security & encryption
│       │
│       ├── orchestration/      # Task orchestration
│       ├── tools/              # Agent tools
│       └── utils/              # Shared utilities
│
├── 📁 tests/                     # Optimized test pyramid (75/20/5)
│   ├── unit/                    # 77 unit tests (72%)
│   │   ├── core/               # Core business logic tests
│   │   ├── interfaces/         # Interface tests
│   │   └── platform/           # Platform service tests
│   │
│   ├── integration/            # 20 integration tests (18%)
│   │   ├── api/               # API integration tests
│   │   ├── dashboard/         # Dashboard integration tests
│   │   └── workflows/         # Workflow integration tests
│   │
│   └── e2e/                   # 9 end-to-end tests (8%)
│       ├── system/            # Full system tests
│       ├── workflows/         # Complete workflow tests
│       └── performance/       # Performance benchmarks
│
├── 📁 Legacy (Deprecated - Use src/ instead)
│   ├── agents/                # → src/core/agents/
│   ├── dashboard/             # → src/interfaces/dashboard/
│   ├── memory-bank/          # → src/platform/memory/knowledge/
│   └── tools/memory/         # → src/platform/memory/
│
└── 📁 Data & Runtime
    ├── config/               # Configuration files
    ├── outputs/             # Generated outputs
    ├── logs/                # System logs
    └── storage/             # Persistent data
│   │   ├── context/              # Unified context store (patterns, db schema, etc.)
│   │   ├── storage/              # Tiered storage (hot/warm/cold)
│   │   ├── sprints/              # Sprint planning and execution data
│   │   └── templates/            # Document and code templates
│   │
│   ├── docs/                      # All documentation
│   │   ├── admin/                # Administrative documentation
│   │   ├── completions/          # Task completion reports
│   │   ├── optimizations/        # Performance optimization docs
│   │   └── sprint/               # Sprint documentation
│   │
│   ├── examples/                  # Example code and demos
│   ├── memory-bank/              # Knowledge management system
│   ├── runtime/                  # Runtime artifacts (gitignored)
│   │   ├── cache/                # Multi-tier caching
│   │   ├── chroma_db/            # Vector database
│   │   ├── logs/                 # System logs
│   │   ├── outputs/              # Task execution outputs
│   │   └── temp/                 # Temporary files
│   │
│   └── tests/                    # Comprehensive test suite
│       ├── fixtures/             # Test fixtures and mocks
│       ├── integration/          # Integration tests
│       └── unit/                 # Unit tests
```

### Key Improvements
- **Clean Root**: Reduced from 40+ to 37 organized items
- **Logical Grouping**: Source code, data, build artifacts, and runtime files separated
- **Gitignore Optimization**: Runtime and build artifacts excluded from version control
- **Context Consolidation**: Single source of truth for all context data
- **Professional Structure**: Industry-standard organization for enterprise projects

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   # Edit .env to add your API keys including:
   # - OPENAI_API_KEY (required)
   # - MEMORY_ENGINE_KEY (required for secure encryption)
   ```

5. Generate and set the memory engine encryption key:
   ```bash
   # Generate a secure encryption key
   python -c "from cryptography.fernet import Fernet; print('MEMORY_ENGINE_KEY=' + Fernet.generate_key().decode())"
   # Copy the output and add it to your .env file
   ```

## 🚀 Quick Start

### System Validation
```bash
# Run comprehensive system validation
python main.py

# Run unified test suite (optimized for speed)
python -m pytest -v
```

### Task Execution
```bash
# Execute single task
python orchestration/execute_task.py --task TL-01

# Run LangGraph workflow for specific task
python orchestration/execute_workflow.py --task BE-07

# Execute all tasks in dependency order
python orchestration/execute_workflow.py --all

# Run with dynamic routing (adaptive execution)
python orchestration/execute_workflow.py --all --dynamic

# Agent-specific execution
python orchestration/execute_workflow.py --agent backend_engineer

# Day-based execution
python orchestration/execute_workflow.py --day 2
```

### Daily Automation Cycle
```bash
# Start daily workflow automation
python orchestration/daily_cycle.py --day 1 --start

# Generate end-of-day comprehensive report
python orchestration/daily_cycle.py --day 1 --end

# Monitor real-time execution status
python scripts/monitor_workflow.py

# Generate progress reports
python scripts/generate_progress_report.py
```

### Advanced Operations
```bash
# Generate task dependency visualization
python scripts/visualize_task_graph.py

# List pending QA reviews
python scripts/list_pending_reviews.py

# Mark reviews as complete
python scripts/mark_review_complete.py

# Code quality and linting
./lint.bat                          # Windows batch wrapper
powershell -File code-quality.ps1   # Comprehensive analysis
powershell -File code-quality.ps1 -Fix  # Auto-fix issues
```

## Testing

The system includes comprehensive testing for agents, tools, and orchestration using a unified test runner:

### Running Tests

The test system uses a unified test runner that can execute different test suites:

```bash
# Run all tests (quick validation, tool tests, and full suite)
python -m tests.run_tests --all

# Run only the quick validation test (fastest option)
python -m tests.run_tests --quick

# Run only the tool loader tests
python -m tests.run_tests --tools

# Run only the full test suite
python -m tests.run_tests --full

# Show available test options
python -m tests.run_tests --help
```

### Test Watch Mode
Run tests automatically when files change:
```bash
./scripts/test-watch.sh
```

### Test Components

- **run_tests.py**: Unified test runner with multiple test modes
- **mock_environment.py**: Utility for patching external dependencies
- **test_agents.py**: Unit tests for agent instantiation and setup
- **test_agent_orchestration.py**: Tests for agent delegation and task routing
- **test_tool_loader.py**: Tests for tool configuration and loading

The test system uses dependency mocking to ensure tests can run without requiring external API keys or services.

## 🚀 Phase 2 Test Optimizations (COMPLETED)

**Status**: Project Complete - All objectives achieved and cleanup finalized

### Performance Achievements
- **Target Tests**: 4 slowest tests optimized from 49.75s → 0.04s (1244x faster)
- **Overall Suite**: Projected improvement from 81.54s → ~31.8s (2.6x faster)
- **Goal Exceeded**: Achieved 2.6x improvement vs 2.5x target

### Key Optimizations Implemented
1. **Pure Mock Strategy**: Complete isolation from heavy dependencies
2. **Zero I/O Operations**: Eliminated ChromaDB, file system, and network calls
3. **In-Memory Processing**: All data structures mocked in memory
4. **Parallel Execution**: Maintained pytest-xdist compatibility

### Documentation
- **Technical Details**: `docs/optimizations/PHASE2_OPTIMIZATION_FINAL_REPORT.md`
- **Results Summary**: `docs/optimizations/PHASE2_OPTIMIZATION_RESULTS.md`
- **Project Overview**: `docs/optimizations/PHASE2_OPTIMIZATION_PROJECT_COMPLETE.md`
- **Final Cleanup**: `docs/optimizations/PHASE2_PROJECT_CLEANUP_FINAL.md`

## 🎯 Phase 7 Human-in-the-Loop (HITL) Integration (IN PROGRESS)

**Status**: 42.9% Complete (3 of 7 steps) - **Step 7.4 Ready for Implementation** 🚀

### Recent Milestones (June 2025)
- ✅ **Step 7.1**: Enhanced HITL Checkpoint Definition System (June 8)
- ✅ **Step 7.2**: Advanced Human Review Portal CLI (June 9)  
- ✅ **Step 7.3**: HITL Engine Integration & Test Stabilization (June 9)

### Foundation Achievements
- **Configuration System**: Comprehensive `config/hitl_policies.yaml` with 7 task types and 4-level escalation
- **Review Portal**: Multi-modal CLI interface with batch processing and visualization
- **Engine Stability**: 9/9 integration tests passing with policy normalization for test/production compatibility
- **Risk Assessment**: Reliable HIGH/MEDIUM/LOW detection with weighted scoring algorithms
- **Auto-Approval Logic**: Enhanced low-risk task automation with proper escalation paths

### Current Implementation Target
- **Step 7.4**: Intelligent Risk Assessment Engine Enhancement with ML-based algorithms and historical pattern analysis

### Documentation
- **Implementation Status**: `data/sprints/sprint_phase7_Human-in-the-Loop.txt`
- **Steps 7.2-7.3 Completion**: `docs/PHASE7_STEPS7.2-7.3_COMPLETION_SUMMARY.md`
- **Configuration Reference**: `config/hitl_policies.yaml`

### Test Files
- **Optimized Tests**: `tests/test_phase2_optimizations.py` (7 tests, all passing)
- **Test Runners**: `scripts/run_optimized_tests*.py`

**Project successfully completed with clean file organization and comprehensive documentation.**

---

## 🏗️ System Architecture

### Multi-Agent System
**7 Specialized Agents** with distinct roles and capabilities:
- **Coordinator**: Project management and task flow oversight  
- **Technical Lead**: Infrastructure, CI/CD, and DevOps architecture
- **Backend Engineer**: Supabase services, APIs, and database operations
- **Frontend Engineer**: React/Tailwind UI development and components
- **UX Designer**: Interface design and user experience optimization
- **Product Manager**: Requirements definition and business logic
- **QA Engineer**: Testing, validation, and quality assurance
- **Documentation Agent**: Technical writing and comprehensive documentation

### Enterprise Memory Engine (MCP)
**Production-ready context management** with:
- **Vector Database**: ChromaDB for semantic search and retrieval
- **Multi-tier Caching**: L1 (memory) + L2 (disk) with TTL management
- **Tiered Storage**: Hot/warm/cold storage with automatic lifecycle management
- **Security Features**: AES-256 encryption, PII detection, access control
- **Performance**: Optimized chunking, similarity search, and context injection

### LangGraph Workflow Engine (A2A)
**Sophisticated workflow orchestration** featuring:
- **Dynamic Graph Builder**: Builds execution graphs from `critical_path.yaml`
- **State Management**: Task lifecycle with conditional routing and error handling
- **Dependency Resolution**: Topological sorting with cycle detection
- **Adaptive Routing**: Dynamic workflow adaptation based on task requirements
- **Monitoring**: Real-time execution tracking and comprehensive reporting

### Tool Ecosystem
**Specialized tools** providing agent capabilities:
- **Development**: Supabase, GitHub, Vercel for platform integration
- **Testing**: Jest, Cypress for automated testing and validation
- **Design**: Tailwind CSS, design system tools for UI development
- **Documentation**: Markdown generation, README tools for comprehensive docs
- **Quality**: Coverage analysis, code quality metrics, and security scanning

### Task Management System
**YAML-driven task definitions** with:
- **Dependency Management**: Critical path analysis and dependency resolution
- **Status Tracking**: Real-time task status with workflow state transitions
- **Context Domains**: Domain-specific knowledge injection for agents
- **Artifact Management**: Structured output generation and validation

## License

MIT License. See `LICENSE` for details.

## Commit Message Format
This project follows the Conventional Commits standard for commit messages:

feat: - A new feature (triggers a minor version bump)
fix: - A bug fix (triggers a patch version bump)
docs: - Documentation changes
style: - Code style changes (formatting, etc.)
refactor: - Code changes that neither fix bugs nor add features
perf: - Performance improvements
test: - Adding or modifying tests
chore: - Changes to the build process or auxiliary tools
BREAKING CHANGE: - Changes that break backward compatibility (triggers a major version bump)
Automated Releases
When you push to the main branch, the following happens automatically:

A GitHub Action analyzes your commit messages
The version in package.json is bumped based on the commit types
A new tag is created and pushed
A GitHub release is created with the packaged VSIX file
The extension is published to VS Code Marketplace and Open VSX Registry (if tokens are configured)
Repository Secrets for Publishing
To enable automated publishing to the extension marketplaces, set up these repository secrets in your GitHub repository:

GH_TOKEN (optional): Personal Access Token with 'repo' scope (used for pushing version changes)

If not provided, the workflow will use the default GITHUB_TOKEN with write permissions
Create this token at https://github.com/settings/tokens
VSCE_PAT (optional): Personal Access Token for VSCode Marketplace publishing

Create this token at https://dev.azure.com/
Instructions: https://code.visualstudio.com/api/working-with-extensions/publishing-extension#get-a-personal-access-token
OVSX_PAT (optional): Personal Access Token for Open VSX Registry publishing

Create this token at https://open-vsx.org/
Instructions: https://github.com/eclipse/openvsx/wiki/Publishing-Extensions#how-to-publish-an-extension
To add these secrets:

Go to your repository on GitHub
Navigate to Settings > Secrets and variables > Actions
Click "New repository secret"
Add each token with its corresponding name

### Pull Request Process

Fork the repository
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes using the conventional format (git commit -m 'feat: add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
## Development Shortcuts
Use the Makefile for common tasks. Example:
```bash
make setup    # Complete environment setup with git hooks
make dev      # Start development environment with Docker
make test-quick  # Fast validation (<60s)
```

### VSCode Development Setup
The project includes VSCode configuration for optimal development:
- **Extensions**: Recommended Python, testing, and linting extensions
- **Settings**: Auto-formatting with black, ruff linting, pytest integration
- **Debug Config**: Launch configurations for debugging tests and agents
- **Snippets**: Python code snippets for agent development

### Git Hooks Setup
Copy git hooks after cloning for automated validation:
```bash
cp githooks/* .git/hooks/
chmod +x githooks/* scripts/*.sh
```
