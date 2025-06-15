# 🚀 Quick Start Guide - Enhanced Development Workflow

Welcome to the enhanced SOTA AI System development environment! This guide will get you up and running with all the new development tools in under 5 minutes.

## 📋 Prerequisites

- Python 3.9+ installed
- Git 2.25+ installed
- (Optional) Docker for containerized development
- (Optional) VSCode for enhanced IDE experience

## 🏃 Quick Start (2 minutes)

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/talyssonoliver/sota.git
cd sota

# Use the new Makefile for instant setup
make setup
```

### 2. Start Development
```bash
# Option A: Traditional Python environment
make test-quick    # Run quick validation
python main.py     # Run the main system

# Option B: Docker environment (recommended)
make dev          # Start full development stack
make logs         # View service logs
```

## 🛠️ Essential Development Commands

### Core Workflow
```bash
make help         # Show all 23+ available commands
make test-quick   # Fast validation (<60s)
make test         # Full test suite
make lint         # Code quality checks
make format       # Auto-format code
```

### Agent Development
```bash
# Generate a new agent with boilerplate code
python scripts/generate_agent.py "AgentName" "Agent description"

# This creates:
# - agents/agentname.py       (agent implementation)
# - tests/agents/test_agentname.py (tests)
# - docs/agentname.md         (documentation template)
```

### Git Hooks (Auto-installed)
The setup automatically installs smart git hooks that:
- ✅ Run linting before commits
- ✅ Sort imports automatically
- ✅ Create backups after commits
- ✅ Skip validation for merge commits

To skip hooks temporarily:
```bash
git commit -m "your message" --no-verify
```

## 💻 VSCode Development

If using VSCode, you now have:
- **Auto-formatting** on save (black + isort)
- **Integrated debugging** for tests and agents
- **Python testing** sidebar integration
- **Recommended extensions** auto-suggested

Just open the project in VSCode and accept the recommended extensions!

## 🧪 Testing Workflow

### Quick Testing Loop
```bash
# Watch mode - tests run automatically on file changes
./scripts/test-watch.sh

# Or use make commands
make test-quick    # Essential tests only
make test-agents   # Agent-specific tests
make test         # Everything
```

### With Coverage
```bash
make test-coverage
# Reports generated in coverage/html/index.html
```

## 🐳 Docker Development

### Full Stack Development
```bash
make dev          # Start all services
make ps           # Check service status
make logs         # View logs
make shell        # Open container shell
make restart      # Restart services
make stop         # Stop everything
```

### Services Included
- **app**: Main Python application
- **redis**: Caching and queues
- **prometheus**: Metrics collection
- **docs**: Documentation server

## 📚 Documentation

### Auto-generate Documentation
```bash
# Generate docs for all modules
python scripts/automated_doc_generator.py docs/

# Build HTML documentation
make docs
```

### Key Documentation
- `CLAUDE.md` - AI assistant instructions
- `AGENT.md` - Agent development guidelines
- `docs/` - Technical documentation
- `README.md` - Project overview

## 🔧 Troubleshooting

### Missing Dependencies
```bash
# The Makefile handles most cases, but if needed:
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Git Hooks Issues
```bash
# Reinstall hooks
cp githooks/* .git/hooks/
chmod +x .git/hooks/*
```

### Permission Errors
```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

## 🎯 Next Steps

1. **Run a task**: `python orchestration/execute_task.py --task TL-01`
2. **Create an agent**: Use the generator tool
3. **Start developing**: Make changes and watch tests run
4. **Contribute**: Create a branch and submit a PR

## 🆘 Getting Help

- Run `make help` for command reference
- Check `docs/development/troubleshooting.md`
- Review `MERGE_VALIDATION_REPORT.md` for infrastructure details
- Submit issues on GitHub

---

**Pro Tip**: Start with `make setup && make test-quick` to verify everything is working, then use `make dev` for the full development experience!

Happy coding! 🚀