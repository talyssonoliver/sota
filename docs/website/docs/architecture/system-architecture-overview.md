# AI System Architecture Documentation

## Overview

This document describes the architecture of the AI Agent System. The system implements a unified, maintainable architecture with clear separation of concerns, enterprise-grade capabilities, and comprehensive Claude Code integration for enhanced development workflows.

## Architecture Principles

### 1. Single Source of Truth
- **No Code Duplication**: Each component exists in exactly one location
- **Unified Directory Structure**: All source code follows `/src/` patterns
- **Centralized Configuration**: Shared configurations in dedicated locations

### 2. Clean Import Paths
- **Consistent Imports**: All imports follow `from src.module.submodule import ClassName` pattern
- **No Relative Imports**: Use absolute imports throughout the codebase
- **Fallback Handling**: Graceful degradation when optional dependencies are missing

### 3. Modular Design
- **Separation of Concerns**: Clear boundaries between core, infrastructure, and interfaces
- **Dependency Injection**: Components depend on abstractions, not implementations
- **Plugin Architecture**: Tools and agents can be extended without modifying core code

## Directory Structure

```
src/
├── core/                          # Core business logic
│   ├── agents/                    # Agent implementations
│   │   ├── __init__.py           # Agent exports
│   │   ├── backend.py            # Backend engineer agent
│   │   ├── coordinator.py        # Project coordinator agent
│   │   ├── doc.py               # Documentation writer agent
│   │   ├── factory.py           # Agent factory and creation functions
│   │   ├── frontend.py          # Frontend engineer agent
│   │   ├── human_agents.py      # Human-in-the-loop agents
│   │   ├── qa.py               # QA engineer agent
│   │   └── technical.py        # Technical lead agent
│   └── workflows/               # LangGraph workflow definitions
│       ├── __init__.py         # Workflow exports
│       ├── automation_health_check.py
│       ├── complete_task.py    # Task completion workflows
│       ├── daily_cycle.py      # Daily workflow cycles
│       ├── delegation.py       # Task delegation workflows
│       ├── documentation_agent.py
│       ├── email_integration.py
│       ├── end_of_day_report.py
│       ├── enhanced_workflow.py
│       ├── error_handling.py   # Error handling workflows
│       ├── execute_graph.py    # Graph execution workflows
│       ├── execute_task.py     # Task execution workflows
│       ├── execute_workflow.py # Workflow execution engine
│       ├── extract_code.py     # Code extraction workflows
│       ├── generate_briefing.py
│       ├── hitl_engine.py      # Human-in-the-loop engine
│       ├── langgraph_qa_integration.py
│       ├── notification_handlers.py
│       ├── qa_execution.py     # QA execution workflows
│       ├── register_output.py  # Output registration
│       ├── registry.py         # Agent registry (thread-safe)
│       ├── run_workflow.py     # Workflow runner
│       ├── scalable_storage.py # Storage workflows
│       ├── states.py          # Workflow states
│       ├── summarise_task.py  # Task summarization
│       ├── task_declaration.py # Task declaration workflows
│       └── task_lifecycle.py  # Task lifecycle management
├── infrastructure/               # Infrastructure and platform services
│   ├── memory/                  # Memory engine (unified, enterprise-grade)
│   │   ├── __init__.py         # Memory system exports
│   │   ├── config/
│   │   │   └── factory.py      # Memory configuration factory
│   │   ├── engines/
│   │   │   └── memory_engine.py # Main memory engine implementation
│   │   └── security/
│   │       └── thread_safety.py # Thread-safe memory operations
│   ├── security/               # Security and compliance
│   │   ├── __init__.py
│   │   └── chromadb_telemetry_patch.py
│   ├── tools/                  # Tool implementations (organized by domain)
│   │   ├── core/              # Core tools and base classes
│   │   │   ├── __init__.py
│   │   │   ├── base_tool.py   # Base tool class
│   │   │   └── retrieval_qa_v2.py # Refactored QA retrieval
│   │   ├── development/       # Development and testing tools
│   │   │   ├── __init__.py
│   │   │   ├── coverage_tool.py
│   │   │   ├── cypress_tool.py
│   │   │   └── jest_tool.py
│   │   ├── documentation/     # Documentation tools
│   │   │   ├── __init__.py
│   │   │   └── markdown_tool.py
│   │   ├── external/          # External service integrations
│   │   │   ├── __init__.py
│   │   │   ├── github_tool.py # GitHub API integration
│   │   │   ├── supabase_tool.py # Supabase integration
│   │   │   ├── vercel_tool.py # Vercel deployment tool
│   │   │   └── vercel_tool_refactored.py
│   │   ├── frontend/          # Frontend development tools
│   │   │   ├── __init__.py
│   │   │   ├── design_system_tool.py # Design system utilities
│   │   │   └── tailwind_tool.py # Tailwind CSS utilities
│   │   ├── handlers/          # Event and request handlers
│   │   │   ├── __init__.py
│   │   │   └── qa_handler.py
│   │   └── notifications.py   # Notification system
│   └── utils/                 # Utility functions and helpers
│       ├── completion_metrics.py
│       ├── escalation_system.py
│       ├── execution_monitor.py
│       ├── feedback_system.py
│       ├── input_validation.py
│       └── task_loader.py
├── integrations/              # External integrations
│   └── analytics/
│       └── analyse_feedback.py
└── interfaces/               # User interfaces and APIs
    ├── api/                  # REST APIs
    │   ├── external_integrations.py
    │   └── hitl_routes.py
    ├── cli/                  # Command-line interfaces
    │   ├── feedback_cli.py
    │   ├── gemini_cli.py     # Google Gemini integration
    │   ├── hitl_cli.py       # Human-in-the-loop CLI
    │   ├── hitl_kanban_cli.py
    │   ├── qa_cli.py
    │   └── qa_execution_cli.py
    └── dashboard/           # Web dashboard interfaces
        ├── api/
        │   ├── gantt_api.py
        │   └── routes.py
        ├── components/
        │   ├── hitl_kanban_board.py
        │   └── hitl_widgets.py
        └── config.py
```

## Key Components

### Core System

#### Agents (`src/core/agents/`)
- **Factory Pattern**: All agent creation goes through `factory.py`
- **Type Safety**: Agents are strongly typed with clear interfaces
- **Thread Safety**: Agent registry supports concurrent access
- **Configuration**: Agent behavior configured via YAML files

#### Workflows (`src/core/workflows/`)
- **LangGraph Integration**: All workflows use LangGraph for orchestration
- **State Management**: Centralized state handling in `states.py`
- **Error Handling**: Comprehensive error handling across all workflows
- **Registry**: Thread-safe agent registry for dynamic agent creation

### Infrastructure

#### Memory Engine (`src/infrastructure/memory/`)
- **Enterprise Features**: AES-256 encryption, PII detection, tiered storage
- **Thread Safety**: All operations are thread-safe
- **Modular Design**: Separate engines for different storage backends
- **Security**: Built-in security and compliance features

#### Tools (`src/infrastructure/tools/`)
- **Domain Organization**: Tools organized by functional domain
- **Base Class**: All tools inherit from `ArtesanatoBaseTool`
- **Error Handling**: Graceful fallback when dependencies are missing
- **Configuration**: Environment-based configuration with fallbacks

### Interfaces

#### CLI (`src/interfaces/cli/`)
- **User Experience**: Consistent CLI patterns across all interfaces
- **Error Handling**: User-friendly error messages and recovery
- **Integration**: Deep integration with core workflows

#### API (`src/interfaces/api/`)
- **REST Endpoints**: Well-defined REST API for external integrations
- **Authentication**: Secure authentication and authorization
- **Documentation**: Comprehensive API documentation

## Import Patterns

### Correct Import Examples

```python
# Core system imports
from src.core.agents.factory import create_backend_agent
from src.core.workflows.execute_task import execute_task_with_context
from src.core.workflows.states import WorkflowState

# Infrastructure imports
from src.infrastructure.memory.engines.memory_engine import MemoryEngine
from src.infrastructure.tools.external.github_tool import GitHubTool
from src.infrastructure.tools.core.base_tool import ArtesanatoBaseTool

# Interface imports
from src.interfaces.cli.hitl_cli import HumanInTheLoopCLI
from src.interfaces.api.hitl_routes import create_hitl_routes
```

### Import Patterns to Avoid

```python
# ❌ Relative imports
from ..memory import MemoryEngine
from ./agents.factory import create_backend_agent

# ❌ Old fragmented paths
from orchestration.execute_task import execute_task
from tools.github_tool import GitHubTool
from memory.memory_engine import MemoryEngine

# ❌ Direct file imports without proper module structure
from memory_engine import MemoryEngine
from github_tool import GitHubTool
```

## Configuration Management

### Environment Variables
- **Development**: `.env` files for local development
- **Production**: Environment-specific configuration
- **Testing**: Isolated test configuration

### Configuration Files
- **agents.yaml**: Agent definitions and tool assignments
- **tools.yaml**: Tool configurations and environment requirements
- **workflows.yaml**: Workflow definitions and dependencies

## Testing Strategy

### Test Organization
```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── core/               # Core system tests
│   ├── infrastructure/     # Infrastructure tests
│   └── interfaces/         # Interface tests
├── integration/            # Integration tests (moderate speed)
│   ├── agents/            # Agent integration tests
│   ├── workflows/         # Workflow integration tests
│   └── memory/            # Memory system integration tests
└── e2e/                   # End-to-end tests (slow, comprehensive)
    └── system/            # Full system tests
```

### Test Patterns
- **Mocking**: Extensive mocking for external dependencies
- **Fixtures**: Reusable test fixtures for common scenarios
- **Parallel Execution**: Tests designed for parallel execution
- **Performance**: Performance tests with benchmarking

## Security Considerations

### Data Protection
- **Encryption**: AES-256 encryption for sensitive data
- **PII Detection**: Automatic detection and redaction of personally identifiable information
- **Access Control**: Role-based access control throughout the system

### Code Security
- **Input Validation**: All inputs validated at system boundaries
- **Error Handling**: Secure error handling that doesn't leak sensitive information
- **Dependency Management**: Regular security audits of dependencies

## Performance Optimization

### Memory Management
- **Lazy Loading**: Components loaded only when needed
- **Memory Pools**: Efficient memory allocation for frequently used objects
- **Garbage Collection**: Proactive garbage collection management

### Execution Optimization
- **Parallel Processing**: Extensive use of parallel processing
- **Caching**: Multi-level caching strategy
- **Connection Pooling**: Efficient connection management for external services

## Migration Guide

### From Old Architecture
If you have code using the old fragmented architecture:

1. **Update Imports**: Change all imports to use the new `src/` structure
2. **Remove Duplicates**: Ensure you're using the consolidated versions
3. **Update Tests**: Update test imports and remove duplicate test files
4. **Configuration**: Update configuration files to reference new paths

### Example Migration
```python
# Before (old fragmented architecture)
from orchestration.execute_task import execute_task
from tools.github_tool import GitHubTool
from memory.memory_engine import MemoryEngine

# After (new consolidated architecture)
from src.core.workflows.execute_task import execute_task_with_context
from src.infrastructure.tools.external.github_tool import GitHubTool
from src.infrastructure.memory.engines.memory_engine import MemoryEngine
```

## Claude Code Integration

### Configuration Structure
The system integrates deeply with Claude Code for enhanced development workflows:

```
.claude/
├── settings.local.json    # Enterprise permissions & AI system settings
├── commands/              # Custom slash commands for development
├── .mcp.json             # Model Context Protocol integration
├── hooks.json            # Advanced lifecycle management
└── README.md             # Configuration documentation
```

### Key Integration Points

#### 1. Custom Commands
- **Development**: `/setup-dev`, `/agent-status`, `/test-quick`, `/check`
- **Task Execution**: `/run-task BE-01`, `/run-task FE-02`
- **Git Workflow**: `/commit-fast`, `/create-pr`

#### 2. Lifecycle Hooks
- **Pre-commit**: Auto-formatting, linting, security scanning
- **Post-commit**: Logging, changelog updates
- **Pre/Post Test**: Environment setup, coverage reporting
- **Error Recovery**: Automatic backups and system status

#### 3. MCP Integration
```json
{
  "mcpServers": {
    "filesystem": { /* File operations */ },
    "git": { /* Version control */ },
    "python": { /* Python execution */ },
    "github": { /* GitHub API */ }
  },
  "aiSystemIntegration": {
    "memoryEngine": { /* Context management */ },
    "workflowEngine": { /* Task orchestration */ },
    "agentSystem": { /* Multi-agent coordination */ }
  }
}
```

### Architectural Benefits
1. **Automated Quality Assurance**: Hooks ensure code quality automatically
2. **Streamlined Workflows**: Slash commands reduce complex operations
3. **Deep Integration**: Direct access to AI system components
4. **Enhanced Monitoring**: Real-time system health checks
5. **Error Prevention**: Proactive validation and recovery

## Development Guidelines

### Adding New Components

#### New Agent
1. Create agent class in `src/core/agents/`
2. Add factory function in `src/core/agents/factory.py`
3. Register in `src/core/workflows/registry.py`
4. Add configuration to `config/agents.yaml`
5. Write comprehensive tests

#### New Tool
1. Choose appropriate domain directory under `src/infrastructure/tools/`
2. Inherit from `ArtesanatoBaseTool`
3. Implement proper error handling and fallbacks
4. Add to tool registry
5. Write tests with mocking for external dependencies

#### New Workflow
1. Create workflow in `src/core/workflows/`
2. Use LangGraph patterns for orchestration
3. Integrate with state management
4. Add comprehensive error handling
5. Write integration tests

### Code Quality Standards
- **Type Hints**: All functions must have type hints
- **Documentation**: Comprehensive docstrings for all public APIs
- **Testing**: Minimum 80% code coverage
- **Linting**: Code must pass all linting checks
- **Security**: Security review for all new components

## Monitoring and Observability

### Logging
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Log Levels**: Appropriate log levels throughout the system
- **Context**: Rich context in all log messages

### Metrics
- **Performance Metrics**: Response times, throughput, error rates
- **Business Metrics**: Task completion rates, agent utilization
- **System Metrics**: Memory usage, CPU utilization, disk I/O

### Tracing
- **Distributed Tracing**: End-to-end request tracing
- **Correlation IDs**: Request correlation across system boundaries
- **Performance Profiling**: Regular performance profiling

## Troubleshooting

### Common Issues

#### Import Errors
- **Check Path**: Ensure you're using the correct `src/` structure
- **Virtual Environment**: Verify you're in the correct virtual environment
- **PYTHONPATH**: Check that PYTHONPATH includes the project root

#### Agent Creation Failures
- **Dependencies**: Verify all required dependencies are installed
- **Configuration**: Check agent configuration in `config/agents.yaml`
- **Registry**: Ensure agent is properly registered

#### Memory Engine Issues
- **Permissions**: Check file system permissions for storage directories
- **Encryption**: Verify encryption keys are properly configured
- **Storage**: Ensure adequate disk space for vector storage

### Debugging Tips
1. **Enable Debug Logging**: Set log level to DEBUG for detailed information
2. **Check Dependencies**: Verify all optional dependencies are installed
3. **Validate Configuration**: Use configuration validation tools
4. **Test in Isolation**: Test components in isolation to identify issues

## Future Roadmap

### Planned Improvements
- **Microservices**: Evolution toward microservices architecture
- **Container Support**: Enhanced Docker and Kubernetes support
- **Cloud Integration**: Deeper cloud provider integrations
- **Performance**: Continued performance optimizations

### Breaking Changes
- **API Versioning**: Proper API versioning for backward compatibility
- **Migration Tools**: Automated migration tools for major changes
- **Deprecation Warnings**: Clear deprecation warnings before breaking changes

---

This architecture documentation reflects the current state after the successful cleanup that eliminated 89% code duplication and consolidated the codebase into a clean, maintainable structure. All 823 tests now collect successfully, and the system follows modern software architecture principles.