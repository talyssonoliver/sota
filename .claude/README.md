# Claude Code Configuration

This directory contains the Claude Code configuration for the AI System project, optimized for enterprise development workflows.

## Files Overview

### `settings.local.json`
Main Claude Code configuration with:
- **Comprehensive permissions** for development tools
- **Security restrictions** to prevent dangerous operations  
- **AI system-specific settings** for Python paths and commands
- **Enterprise preferences** with hooks and MCP integration
- **Quality assurance hooks** for automated code checks

### `commands/`
Custom slash commands for streamlined development:
- `/check` - Comprehensive code quality validation
- `/test-quick` - Fast test suite for rapid feedback
- `/commit-fast` - Automated git commits with conventional formatting
- `/run-task` - Execute AI system tasks (BE-01, FE-02, etc.)
- `/agent-status` - Check status of all AI agents and components
- `/setup-dev` - Complete development environment setup
- `/create-pr` - Automated pull request creation with analysis

### `.mcp.json`
Model Context Protocol configuration enabling:
- **Filesystem server** for file operations
- **Git server** for version control integration
- **Python server** for code execution
- **GitHub server** for repository operations
- **AI system integration** with memory and workflow engines

### `hooks.json`
Advanced lifecycle management with automated hooks for:
- **Session management** (pre/post session)
- **Code quality** (pre/post commit)  
- **Testing workflow** (pre/post test)
- **Build process** (pre/post build)
- **File monitoring** (on change events)
- **Error handling** (recovery and logging)

## Usage

### Essential Commands

```bash
# Quick development workflow
/setup-dev          # Set up environment
/agent-status       # Check system health
/test-quick         # Run fast tests
/check              # Full quality check

# Task execution
/run-task BE-01     # Execute backend task 1
/run-task FE-02     # Execute frontend task 2

# Git workflow
/commit-fast        # Automated commit
/create-pr          # Create pull request
```

### Development Workflow

1. **Start Session**: Claude automatically runs pre-session hooks
2. **Development**: Use slash commands for common tasks
3. **Quality Check**: `/check` runs comprehensive validation
4. **Commit**: `/commit-fast` creates structured commits
5. **Pull Request**: `/create-pr` generates PR with analysis

### AI System Integration

The configuration integrates deeply with the AI system architecture:

- **Memory Engine**: Context-aware operations with PII detection
- **Agent Factory**: Multi-agent coordination and status monitoring
- **Workflow Engine**: Task orchestration with LangGraph
- **Tool System**: Domain-organized development tools

### Security Features

- **Command whitelisting** with comprehensive development tools
- **Path restrictions** preventing access to system directories
- **Audit logging** for all MCP operations
- **Security scanning** in pre-commit hooks
- **Error recovery** with automatic backup creation

### Customization

To add custom commands:
1. Create new `.md` file in `commands/` directory
2. Follow existing command structure with bash scripts
3. Use environment variables for AI system paths

To modify hooks:
1. Edit `hooks.json` for new lifecycle events
2. Add commands with proper error handling
3. Test with `continue_on_error: true` initially

## Best Practices

### Command Organization
- Use descriptive names with hyphens (kebab-case)
- Include validation steps before main operations
- Provide clear success/failure feedback
- Document usage and examples

### Hook Development
- Always include error handling and timeouts
- Use `continue_on_error` for non-critical operations
- Log important events for debugging
- Test hooks individually before integration

### Security Considerations
- Never add overly permissive bash commands
- Validate inputs in custom commands
- Use environment variables for sensitive data
- Regular audit of permissions and hooks

## Troubleshooting

### Common Issues

**Permission Denied**: Check if command is in `allow` list in `settings.local.json`

**Import Errors**: Verify `PYTHONPATH` is set correctly in environment

**Hook Failures**: Check `logs/hooks.log` for detailed error messages

**MCP Server Issues**: Ensure Node.js and required packages are installed

### Debug Commands

```bash
# Check Claude Code status
claude --version

# Test specific command
/agent-status

# Validate configuration
python3 -c "import json; json.load(open('.claude/settings.local.json'))"

# Check hooks
tail -f logs/hooks.log
```

## Architecture Alignment

This configuration supports the clean `/src/` architecture:

```
src/
├── core/              # Business logic
├── infrastructure/    # Platform services  
├── integrations/      # External services
└── interfaces/        # User interfaces
```

All commands and hooks are designed to work with this structure, providing:
- **Unified imports** via proper PYTHONPATH
- **Architecture validation** in quality checks
- **Component health monitoring** via agent status
- **Task orchestration** through workflow engine

## Enterprise Features

- **Multi-agent coordination** with health monitoring
- **Context-aware operations** via memory engine
- **Automated quality assurance** with comprehensive checks
- **Structured commit workflows** with conventional formatting
- **Advanced error recovery** with backup and logging
- **Performance optimization** with parallel execution options

---

🤖 **Generated with Claude Code Best Practices 2025**

For updates and additional configurations, see: https://docs.anthropic.com/claude-code