# Automation Guide

This guide covers all automation features that streamline development workflow, including Makefile commands, git hooks, Docker automation, and agent generation tools.

## 🔧 Makefile Commands

The Makefile provides 23+ commands for complete development automation:

### Environment Management
```bash
make setup      # Complete environment setup (venv + deps + hooks)
make clean      # Clean build artifacts and cache
make reset      # Reset environment completely
make deps       # Install/update dependencies
make dev-deps   # Install development dependencies
```

### Development Workflow
```bash
make dev        # Start full development stack with Docker
make logs       # View development container logs
make ps         # Check container status
make restart    # Restart development containers
make stop       # Stop all containers
```

### Testing & Quality
```bash
make test-quick    # Fast validation tests (<60s)
make test-all      # Complete test suite
make test-watch    # Watch mode for continuous testing
make lint          # Run code linting with ruff
make format        # Format code with black
make typecheck     # Type checking with mypy
make security      # Security vulnerability scan
```

### Code Quality Analysis
```bash
make quality       # Comprehensive code quality report
make complexity    # Cyclomatic complexity analysis
make duplication   # Code duplication detection
make coverage      # Generate test coverage report
```

### Documentation
```bash
make docs-gen      # Generate automated documentation
make docs-serve    # Serve documentation locally
make docs-check    # Validate documentation links
```

### System Operations
```bash
make backup        # Backup critical system data
make restore       # Restore from backup
make health        # System health check
make monitor       # Start monitoring dashboard
```

## 🪝 Git Hooks Automation

Automated git hooks ensure code quality and consistency:

### Pre-commit Hook
Automatically runs before each commit:
```bash
# Code formatting
black . --exclude=".venv"
isort .

# Linting
ruff check . --fix

# Type checking
mypy . --ignore-missing-imports

# Security scanning
bandit -r . -f json

# Test validation
python -m tests.run_tests --quick
```

### Post-commit Hook
Runs after successful commits:
```bash
# Update documentation
python scripts/automated_doc_generator.py

# Generate progress reports
python scripts/generate_progress_report.py

# Update dashboard data
python scripts/update_dashboard.py
```

### Installation
```bash
# Automatic (included in make setup)
make setup

# Manual installation
cp githooks/pre-commit .git/hooks/pre-commit
cp githooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/pre-commit .git/hooks/post-commit
```

## 🐳 Docker Development Automation

Complete containerized development environment:

### Services
- **App Container**: Main application with hot reload
- **ChromaDB**: Vector database for memory engine
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **Nginx**: Reverse proxy and static files

### Commands
```bash
# Start development stack
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Rebuild containers
docker-compose -f docker-compose.dev.yml build

# Clean up
docker-compose -f docker-compose.dev.yml down -v
```

### Configuration
- **Hot Reload**: Automatic code reloading on changes
- **Volume Mounts**: Source code and data persistence
- **Port Mapping**: Standard development ports
- **Environment Variables**: Automatic .env loading

## 🤖 Agent Generation Automation

Automated agent creation with templates:

### Generate New Agent
```bash
python scripts/generate_agent.py "Agent Name" "Agent description"
```

This creates:
- Agent class with role-specific methods
- Configuration in `config/agents.yaml`
- Unit tests with mocking
- Integration tests
- Documentation templates

### Template System
- **Jinja2 Templates**: Flexible agent generation
- **Best Practices**: Pre-configured with error handling
- **Tool Integration**: Automatic tool loading setup
- **Testing**: Complete test suite generation

## 📖 Documentation Automation

Automated documentation generation and maintenance:

### Auto-Documentation
```bash
python scripts/automated_doc_generator.py
```

Generates:
- Module documentation from docstrings
- API endpoint documentation
- Configuration file documentation
- Workflow diagrams
- Code complexity reports

### Features
- **Markdown Generation**: Professional documentation format
- **Code Analysis**: Automatic function and class discovery
- **Cross-References**: Automatic linking between modules
- **Templates**: Consistent documentation structure

## 🔍 Continuous Monitoring

Automated monitoring and health checks:

### System Health
```bash
# Automated health monitoring
python scripts/monitor_workflow.py

# Performance benchmarking
python scripts/performance_monitor.py

# Resource usage tracking
python scripts/resource_monitor.py
```

### Alerts
- **Performance Degradation**: Automatic detection
- **Error Rate Monitoring**: Threshold-based alerts
- **Resource Usage**: Memory and CPU monitoring
- **Service Health**: Dependency health checks

## 🔄 Workflow Automation

Complete task execution automation:

### Daily Cycle
```bash
# Start daily automation
python orchestration/daily_cycle.py --day 1 --start

# End-of-day processing
python orchestration/daily_cycle.py --day 1 --end
```

### Features
- **Morning Briefings**: Automated status generation
- **Task Orchestration**: Dependency-based execution
- **Progress Tracking**: Real-time monitoring
- **End-of-Day Reports**: Comprehensive summaries

## ⚡ Performance Optimizations

Automated performance enhancements:

### Test Optimization
- **Parallel Execution**: pytest-xdist integration
- **Mock Environments**: Fast dependency isolation
- **Selective Testing**: Run only changed modules
- **Coverage Tracking**: Automatic coverage reporting

### Build Optimization
- **Incremental Builds**: Only rebuild changed components
- **Caching**: Multi-layer build caching
- **Dependency Management**: Automatic dependency updates
- **Asset Optimization**: Automatic minification

## 🛠️ Troubleshooting Automation

See [Troubleshooting Guide](troubleshooting.md) for automated debugging and common issue resolution.
