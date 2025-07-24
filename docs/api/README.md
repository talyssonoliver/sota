# API Documentation

The AI Agent System provides programmatic interfaces through Python modules, CLI commands, and REST endpoints for agent orchestration, memory management, and workflow execution.

## 🌐 API Overview

The system offers multiple interaction methods:

### 1. **Python Module API**
Direct programmatic access through Python imports

### 2. **Command Line Interface (CLI)**
Executable scripts for system operations

### 3. **REST API Endpoints**
HTTP endpoints for web integration

### 4. **Dashboard API**
Web-based management interface

## 📋 Python Module API

### Agent Management

**Agent Factory** (`src/core/agents/factory.py`)
```python
from src.core.agents.factory import AgentFactory

# Create agent instance
agent = AgentFactory.create_agent(
    agent_type="backend_engineer",
    config=config_dict
)

# Execute task
result = agent.execute_task(task_id="BE-07", context=context)
```

**Available Agent Types:**
- `technical_lead` - Architecture and coordination
- `backend_engineer` - Server-side development
- `frontend_engineer` - UI development
- `qa_engineer` - Testing and validation
- `documentation_agent` - Documentation generation
- `coordinator` - Project management

### Memory Engine Operations

**Memory Engine** (`src/infrastructure/memory/engines/memory_engine.py`)
```python
from src.infrastructure.memory.engines.memory_engine import MemoryEngine

# Initialize memory engine
memory = MemoryEngine()

# Store context
success = memory.add_document(
    file_path="document.txt",
    user="system",
    metadata={"content_type": "documentation"}
)

# Retrieve context
context = memory.get_context(
    query="database schema implementation",
    k=5,
    similarity_threshold=0.7,
    user="system"
)

# Get system health
health = memory.index_health()
```

**Memory Engine Methods:**
- `add_document(file_path, user, metadata)` - Store document with encryption
- `get_context(query, k, similarity_threshold, user)` - Semantic search
- `get_context_by_keys(keys, user)` - Direct key-based retrieval
- `build_focused_context(topics, max_tokens, user)` - Multi-topic context
- `scan_for_pii(user)` - PII detection scan
- `index_health()` - System health status
- `clear(user)` - System reset (admin only)

### Tool Integration

**Tool Loader** (`src/infrastructure/tools/core/tool_loader.py`)
```python
from src.infrastructure.tools.core.tool_loader import load_tools_for_agent

# Load tools for specific agent
tools = load_tools_for_agent(
    agent_type="backend_engineer",
    config=configuration
)

# Available tool categories:
# - Development: GitHub, Supabase, Vercel
# - Testing: Jest, Cypress, coverage analysis
# - Utilities: Rate limiting, validation, monitoring
```

### Workflow Execution

**Workflow API** (`src/core/workflows/`)
```python
from src.core.workflows.execute_workflow import execute_workflow
from src.core.workflows.states import WorkflowState

# Execute workflow
result = execute_workflow(
    task_id="BE-07",
    agent_type="backend_engineer",
    context=context_data
)

# Check workflow state
state = result.get('state')
status = result.get('status')
```

## 🖥️ Command Line Interface

### System Operations

```bash
# System validation and health checks
python main.py                    # Core validation tests
python main.py --test            # Comprehensive test suite
python main.py --quiet           # Minimal output

# Task execution
python orchestration/execute_task.py --task BE-07
python orchestration/execute_task.py --task FE-03 --agent frontend_engineer

# Workflow execution
python orchestration/execute_workflow.py --all
python orchestration/execute_workflow.py --task BE-07
python orchestration/execute_workflow.py --agent backend_engineer

# Daily automation
python orchestration/daily_cycle.py --day 1 --start
python orchestration/daily_cycle.py --day 1 --end
```

### CLI Interface Scripts

**Human-in-the-Loop** (`src/interfaces/cli/hitl_cli.py`)
```bash
python src/interfaces/cli/hitl_cli.py
```

**Quality Assurance** (`src/interfaces/cli/qa_cli.py`)
```bash
python src/interfaces/cli/qa_cli.py --task BE-07
```

**Feedback Collection** (`src/interfaces/cli/feedback_cli.py`)
```bash
python src/interfaces/cli/feedback_cli.py --submit
```

**System Monitoring**
```bash
python src/infrastructure/scripts/monitoring/monitor_workflow.py
python src/infrastructure/scripts/monitoring/update_dashboard.py
```

## 🌐 REST API Endpoints

### Dashboard API

**Gantt Chart API** (`src/interfaces/dashboard/api/gantt_api.py`)
```http
GET /api/gantt/data              # Get Gantt chart data
GET /api/gantt/tasks             # Get task timeline
POST /api/gantt/update           # Update task progress
```

**Routes API** (`src/interfaces/dashboard/api/routes.py`)
```http
GET /api/health                  # System health check
GET /api/agents                  # List active agents
GET /api/tasks                   # Get task status
POST /api/tasks/{task_id}/execute # Execute specific task
```

**External Integrations** (`src/interfaces/api/external_integrations.py`)
```http
GET /api/integrations            # List available integrations
POST /api/integrations/{service} # Configure service integration
GET /api/integrations/{service}/status # Check integration status
```

## 🔍 System Monitoring

### Health Check API

**System Validation** (`main.py`)
```python
# Health check response format
{
    'simple_agent': True,      # LangChain + EchoTool test
    'supabase_tool': True,     # Database integration test  
    'memory_engine': True,     # Memory system test
    'workflow': True           # LangGraph workflow test
}
```

**Memory Engine Health**
```python
health_status = memory.index_health()
# Returns:
{
    'status': 'healthy',
    'total_documents': 150,
    'vector_store_available': True,
    'encryption_enabled': True,
    'storage_available': True,
    'cache_available': True
}
```

### Progress Monitoring

**Report Generation** (`src/infrastructure/scripts/generation/`)
```bash
python src/infrastructure/scripts/generation/generate_progress_report.py
python src/infrastructure/scripts/generation/generate_task_report.py --task BE-07
```

## 🛠️ Integration Examples

### Complete Agent Workflow

```python
#!/usr/bin/env python3
from src.core.agents.factory import AgentFactory
from src.infrastructure.memory.engines.memory_engine import MemoryEngine
from src.infrastructure.tools.core.tool_loader import load_tools_for_agent

# Initialize components
agent = AgentFactory.create_agent("backend_engineer")
memory = MemoryEngine()
tools = load_tools_for_agent("backend_engineer", config)

# Get relevant context
context = memory.get_context(
    query="user authentication implementation",
    k=10,
    similarity_threshold=0.8
)

# Execute task with context and tools
result = agent.execute_task(
    task_id="BE-07", 
    context=context,
    tools=tools
)

# Store results
memory.add_document(
    file_path=result['output_file'],
    user="backend_engineer",
    metadata={"task_id": "BE-07", "agent": "backend_engineer"}
)
```

### Automated Workflow Execution

```bash
#!/bin/bash
# Daily automation workflow

# System validation
python main.py --quiet

# Start daily cycle
python orchestration/daily_cycle.py --day 1 --start

# Monitor execution
python src/infrastructure/scripts/monitoring/monitor_workflow.py &
MONITOR_PID=$!

# Wait for completion
wait

# Generate end-of-day report
python orchestration/daily_cycle.py --day 1 --end

# Kill monitoring process
kill $MONITOR_PID
```

### Memory Engine Advanced Usage

```python
from src.infrastructure.memory.engines.memory_engine import MemoryEngine

# Initialize with security features
memory = MemoryEngine(config={
    'encryption_enabled': True,
    'pii_detection_enabled': True,
    'access_control_enabled': True,
    'audit_logging_enabled': True
})

# Advanced context search with metadata filtering
results = memory.get_context(
    query="database schema patterns",
    k=15,
    similarity_threshold=0.8,
    metadata_filter={'content_type': 'technical', 'verified': True}
)

# Build focused context for specific task
focused_context = memory.build_focused_context(
    context_topics=['authentication', 'database', 'api-security'],
    max_tokens=2000,
    max_per_topic=3,
    user="backend_engineer",
    task_id="BE-07"
)

# Security scan
pii_findings = memory.scan_for_pii(user="security_admin")
```

## 📊 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key
MEMORY_ENGINE_KEY=your-256-bit-encryption-key

# Optional service integrations
SUPABASE_URL=your-supabase-project-url
SUPABASE_ANON_KEY=your-supabase-anon-key
GITHUB_TOKEN=your-github-token
VERCEL_TOKEN=your-vercel-token
```

### Configuration Files

- `config/agents.yaml` - Agent definitions, tools, and capabilities
- `config/tools.yaml` - Tool configurations and settings
- `src/core/tasks/*.yaml` - Task specifications (70+ files)
- `.env` - Environment variables and secrets

## 🔐 Security

### Authentication
- API key-based authentication for external services
- Role-based access control for memory operations
- Secure environment variable management

### Data Protection
- AES-256 encryption for all stored data
- Automatic PII detection and redaction
- Comprehensive audit logging
- Secure communication protocols

### Security Methods
```python
# Security configuration
memory = MemoryEngine(config={
    'encryption_enabled': True,
    'pii_detection_enabled': True,
    'access_control_enabled': True
})

# User-based access control
context = memory.get_context("sensitive query", user="authorized_user")

# PII scanning
pii_results = memory.scan_for_pii(user="security_admin")
```

## 📚 Error Handling

### Common Error Patterns

```python
try:
    result = agent.execute_task(task_id="BE-07")
except ValidationError as e:
    # Invalid task parameters
    handle_validation_error(e)
except SecurityError as e:
    # Access denied or security violation
    handle_security_error(e)
except ResourceError as e:
    # External service unavailable
    handle_resource_error(e)
```

### Status Codes

- `200` - Success
- `400` - Invalid request parameters
- `401` - Authentication required
- `403` - Access denied
- `404` - Resource not found
- `500` - Internal system error

---

**Note**: This API documentation reflects the current implementation. The system provides both programmatic interfaces and CLI tools for comprehensive workflow automation and agent management.