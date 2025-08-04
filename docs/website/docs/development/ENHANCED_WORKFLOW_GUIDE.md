# Enhanced Development Workflow Guide

## Overview

This guide outlines the enhanced development workflows enabled by Claude Code integration, providing streamlined approaches for common development tasks in the AI System project.

## 🚀 Quick Start Workflow

### Initial Setup
```bash
# 1. Clone and setup
git clone <repository>
cd ai-system

# 2. Use Claude Code for automatic setup
/setup-dev

# 3. Verify system health
/agent-status

# 4. Run quick validation
/test-quick
```

## 📋 Development Workflows

### 1. Feature Development Workflow

#### Starting a New Feature
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Check system status
/agent-status

# Run quick tests to ensure clean start
/test-quick
```

#### Development Cycle
```bash
# 1. Make changes to code

# 2. Validate changes automatically
/check

# 3. Run quick tests
/test-quick

# 4. Commit with automated formatting
/commit-fast

# 5. Create PR when ready
/create-pr
```

#### AI Task Execution
```bash
# Execute specific AI system tasks
/run-task BE-01    # Backend task
/run-task FE-02    # Frontend task
/run-task TL-03    # Technical lead task

# Traditional approach (if needed)
python -c "from src.core.workflows.execute_task import execute_task_with_context; execute_task_with_context('BE-01')"
```

### 2. Quality Assurance Workflow

#### Comprehensive Quality Check
```bash
# Full quality validation
/check

# This runs:
# - Static analysis (mypy)
# - Code formatting checks (black, isort)
# - Linting (ruff)
# - Security scanning (bandit)
# - Full test suite
# - Import validation
# - Architecture compliance
```

#### Quick Validation
```bash
# Fast feedback loop (&lt;60s)
/test-quick

# This runs:
# - Unit tests
# - Core component validation
# - Critical path tests
```

### 3. Git Workflow with Automation

#### Automated Commits
```bash
# Let Claude Code handle commit formatting
/commit-fast

# This automatically:
# - Runs pre-commit hooks
# - Stages all changes
# - Analyzes changes to determine commit type
# - Creates conventional commit message
# - Includes timestamp and branch context
```

#### Pull Request Creation
```bash
# Create PR with automated analysis
/create-pr

# This automatically:
# - Validates you're not on main branch
# - Analyzes all changes
# - Runs quality checks
# - Generates PR description
# - Determines PR type and area
# - Creates PR via GitHub CLI
```

### 4. Debugging Workflow

#### System Health Check
```bash
# Check all components
/agent-status

# This shows:
# - Memory Engine status
# - Agent Factory health
# - Workflow Engine status
# - Tool System availability
# - Configuration status
# - Task System metrics
```

#### Error Investigation
When errors occur, the hooks automatically:
1. Log errors to `logs/errors.log`
2. Create git stash backup
3. Show system status for debugging

Manual investigation:
```bash
# Check error logs
tail -f logs/errors.log

# Check hook execution
tail -f logs/hooks.log

# Validate specific components
PYTHONPATH=. python -c "from src.infrastructure.memory.engines.memory_engine import MemoryEngine; print('✅ Memory Engine OK')"
```

## 🔧 Advanced Workflows

### 1. Memory Engine Operations

#### Context Management
```python
# Use memory engine for context-aware operations
from src.infrastructure.memory.engines.memory_engine import MemoryEngine

memory = MemoryEngine()
context = memory.get_relevant_context(
    query="API implementation patterns",
    agent_context_domains=["backend_engineering"]
)
```

#### Secure Storage
```python
# Store sensitive data with encryption
memory.store_memory(
    key="api_credentials",
    content="sensitive_data",
    metadata={"type": "credentials", "service": "external_api"}
)
```

### 2. Multi-Agent Coordination

#### Creating Agents
```python
from src.core.agents.factory import create_backend_agent, create_coordinator_agent

# Create specialized agents
backend = create_backend_agent(tools=["github_tool", "supabase_tool"])
coordinator = create_coordinator_agent()

# Execute coordinated tasks
result = coordinator.coordinate_task(
    task_id="BE-01",
    agents=[backend],
    context=context
)
```

### 3. Workflow Orchestration

#### Complex Task Execution
```python
from src.core.workflows.execute_workflow import execute_workflow

# Execute with dependencies
result = execute_workflow(
    task_id="BE-07",
    output_dir="outputs",
    include_dependencies=True,
    parallel_execution=True
)
```

## 🎯 Best Practices

### 1. Development Practices

- **Use Slash Commands First**: Leverage `/check`, `/test-quick` for rapid feedback
- **Let Hooks Handle QA**: Pre-commit hooks automatically format and validate
- **Monitor Agent Health**: Regular `/agent-status` checks prevent issues
- **Commit Often**: Use `/commit-fast` for consistent commit messages

### 2. Testing Practices

- **Quick Validation**: Run `/test-quick` frequently during development
- **Full Validation**: Use `/check` before creating PRs
- **Component Testing**: Test specific components when making focused changes
- **Performance Testing**: Monitor test execution times

### 3. Code Organization

- **Follow Architecture**: Maintain `/src/` structure conventions
- **Clean Imports**: Use `src.module.submodule` import patterns
- **Component Isolation**: Keep core, infrastructure, and interfaces separate
- **Tool Organization**: Place tools in appropriate domain directories

### 4. Security Practices

- **Encryption**: Always use memory engine for sensitive data
- **PII Detection**: Let the system automatically detect and redact PII
- **Audit Logging**: Monitor `logs/mcp-audit.log` for security events
- **Input Validation**: Use built-in validation utilities

## 📊 Monitoring & Analytics

### Performance Monitoring
```bash
# View execution metrics
python src/infrastructure/scripts/monitoring/monitor_workflow.py

# Analyze task dependencies
python src/infrastructure/scripts/monitoring/visualize_task_graph.py

# Check coverage metrics
python -m coverage report --show-missing
```

### System Analytics
```bash
# Generate progress reports
python src/infrastructure/scripts/generation/generate_progress_report.py

# View task completion status
ls -la outputs/

# Check system logs
tail -f logs/daily_cycle_*.log
```

## 🔄 Continuous Integration

### Local CI Simulation
```bash
# Run full CI pipeline locally
make ci

# Or manually:
/check              # Full quality checks
make test           # Complete test suite
make build          # Build artifacts
```

### Pre-Push Validation
```bash
# Before pushing to remote
/check              # Ensure quality
/test-quick         # Quick validation
git push            # Push changes
```

## 🛠️ Troubleshooting

### Common Issues

**Import Errors**
```bash
# Fix PYTHONPATH
export PYTHONPATH=/mnt/c/taly/ai-system:$PYTHONPATH

# Verify imports
/agent-status
```

**Permission Denied**
```bash
# Check Claude Code permissions
cat .claude/settings.local.json | grep -A5 "permissions"

# Add missing permission if needed
```

**Hook Failures**
```bash
# Check hook logs
tail -f logs/hooks.log

# Disable problematic hook temporarily
# Edit .claude/hooks.json and set continue_on_error: true
```

**Memory Engine Issues**
```bash
# Verify encryption key
echo $MEMORY_ENGINE_KEY

# Test memory engine
PYTHONPATH=. python -c "from src.infrastructure.memory.engines.memory_engine import MemoryEngine; MemoryEngine()"
```

## 📚 Additional Resources

- **Claude Code Configuration** - See CLAUDE.md in project root for configuration
- [Architecture Guide](../architecture/system-overview.md)
- [Memory Engine Guide](../architecture/memory_engine.md)
- [Testing Best Practices](./testing/testing_best_practices.md)

## 🚦 Quick Reference

| Task | Claude Code | Traditional |
|------|------------|-------------|
| Setup | `/setup-dev` | `pip install -r requirements.txt` |
| Test | `/test-quick` | `python -m pytest` |
| Quality | `/check` | `make lint && make test` |
| Run Task | `/run-task BE-01` | `python -c "..."` |
| Commit | `/commit-fast` | `git add . && git commit` |
| PR | `/create-pr` | `gh pr create` |
| Status | `/agent-status` | Multiple manual checks |

---

🤖 **Enhanced with Claude Code Enterprise Integration**

This workflow guide provides streamlined approaches for development, testing, and deployment with the AI System's Claude Code integration.