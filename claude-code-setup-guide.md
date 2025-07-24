# Claude Code CLI Setup Guide

**Goal**: Set up Claude Code CLI for development workflow acceleration

---

## 🎯 What is Claude Code CLI?

Claude Code is Anthropic's $100/month terminal-based AI coding assistant that:
- Lives in your terminal (not an API)
- Uses Model Context Protocol (MCP) for tool integration  
- Accelerates development workflows by 20:1 ROI
- Provides deep codebase awareness and understanding

---

## 📋 Prerequisites

### 1. Claude Code Subscription
- Requires Anthropic Pro subscription ($20/month) + Claude Code ($100/month)
- OR Claude Code through API tokens (pay-per-use)

### 2. System Requirements
- Terminal access (Linux/macOS/WSL recommended)
- Node.js for MCP servers
- Git CLI for repository operations
- Python environment for our codebase

---

## 🚀 Installation Steps

### 1. Install Claude Code CLI
```bash
# Follow official installation guide from Anthropic
# This varies by platform - check docs.anthropic.com/claude-code
```

### 2. Authentication Setup
```bash
# Set up authentication (method depends on subscription type)
claude auth login
```

### 3. Verify Installation
```bash
claude --version
claude "Hello, can you access this directory?"
```

---

## 🔧 Project Configuration

### 1. Create Claude Code Configuration
```bash
# Create .claude.json in project root
cat > .claude.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "mcp-server-filesystem",
      "args": ["--path", "/mnt/c/taly/ai-system"]
    },
    "github": {
      "type": "stdio", 
      "command": "mcp-server-github",
      "args": ["--repo", "your-repo-name"]
    }
  },
  "permissions": {
    "filesystem": ["read", "write"],
    "github": ["read", "write"],
    "terminal": ["read", "write"]
  }
}
EOF
```

### 2. Create Custom Commands Directory
```bash
# Create project-specific commands
mkdir -p .claude/commands

# AI System specific commands
cat > .claude/commands/analyze-architecture.md << 'EOF'
# Analyze Architecture

You are an expert software architect. Analyze the current AI system architecture and provide:

1. **Architecture Overview**: High-level system design analysis
2. **Component Analysis**: Evaluate each major component (agents, memory, workflows, HITL)
3. **Integration Points**: Assess how components interact
4. **Quality Assessment**: Code quality, maintainability, scalability
5. **Improvement Recommendations**: Specific actionable improvements
6. **Risk Assessment**: Potential issues or technical debt

Focus on:
- Multi-agent system design patterns
- Memory engine architecture (ChromaDB, caching, encryption)
- LangGraph workflow orchestration
- HITL system integration
- Testing and validation frameworks

Provide concrete, actionable recommendations with code examples where helpful.
EOF

cat > .claude/commands/generate-tests.md << 'EOF'
# Generate Comprehensive Tests

You are a testing expert. Generate comprehensive tests for the AI system:

1. **Test Strategy**: Overall testing approach for the component
2. **Unit Tests**: Individual component testing with mocks
3. **Integration Tests**: Component interaction testing
4. **End-to-End Tests**: Full workflow testing
5. **Performance Tests**: Load and performance validation
6. **Security Tests**: Security and validation testing

Requirements:
- Use pytest framework
- Include proper mocking for external dependencies (OpenAI, ChromaDB)
- Follow existing test patterns in tests/ directory
- Ensure high coverage for critical paths
- Include both positive and negative test cases
- Add performance benchmarks where appropriate

Generate actual test code, not just descriptions.
EOF

cat > .claude/commands/review-code.md << 'EOF'
# Code Review Assistant

Perform a thorough code review focusing on:

1. **Code Quality**: Clean code principles, SOLID principles
2. **Security**: Input validation, encryption, PII handling
3. **Performance**: Efficiency, caching, resource usage
4. **Maintainability**: Documentation, naming, structure
5. **Testing**: Test coverage, test quality
6. **Architecture**: Design patterns, separation of concerns

For each file reviewed, provide:
- ✅ **Strengths**: What's done well
- ⚠️ **Issues**: Problems that need attention
- 🔧 **Recommendations**: Specific improvements
- 🎯 **Priority**: High/Medium/Low for each issue

Focus on production readiness and enterprise-grade code quality.
EOF

cat > .claude/commands/optimize-performance.md << 'EOF'
# Performance Optimization

You are a performance optimization expert. Analyze and optimize:

1. **Performance Audit**: Identify bottlenecks and inefficiencies
2. **Database Optimization**: ChromaDB queries, indexing, caching
3. **Memory Usage**: Memory leaks, garbage collection, resource management
4. **API Performance**: Response times, concurrent handling
5. **Caching Strategy**: Multi-tier caching, cache invalidation
6. **Parallelization**: Async operations, parallel processing

Provide:
- Benchmark measurements (before/after)
- Specific code improvements
- Configuration optimizations
- Monitoring recommendations
- Performance testing strategies

Generate actual optimized code with performance measurements.
EOF
```

### 3. Update CLAUDE.md for Project Context
```bash
# Update CLAUDE.md with Claude Code specific instructions
cat >> CLAUDE.md << 'EOF'

## Claude Code CLI Integration

### Development Workflow Commands
- `/analyze-architecture` - Comprehensive architecture analysis
- `/generate-tests` - Create comprehensive test suites
- `/review-code` - Thorough code review and recommendations  
- `/optimize-performance` - Performance analysis and optimization

### Key Project Context
- **Multi-Agent System**: 7 specialized agents (Technical, Backend, Frontend, QA, Doc, PM, UX)
- **Memory Engine**: ChromaDB with encryption, caching, PII detection
- **Workflow Engine**: LangGraph-based orchestration with state management
- **HITL System**: Human-in-the-loop with risk assessment and escalation
- **Testing Framework**: Comprehensive pytest suite with mocks and integration tests

### Development Standards
- Use OpenAI embeddings for production (proven stable)
- Maintain comprehensive test coverage
- Follow security best practices (encryption, PII detection)
- Implement proper error handling and logging
- Use feature flags for gradual rollouts

### Common Tasks
1. **Architecture Review**: Use `/analyze-architecture` for system analysis
2. **Test Generation**: Use `/generate-tests` for comprehensive testing
3. **Code Quality**: Use `/review-code` for thorough reviews
4. **Performance**: Use `/optimize-performance` for optimization analysis
EOF
```

---

## 🛠️ MCP Server Setup

### 1. Install Essential MCP Servers
```bash
# File system operations
npm install -g @modelcontextprotocol/server-filesystem

# GitHub integration
npm install -g @modelcontextprotocol/server-github

# Database operations (if needed)
npm install -g @modelcontextprotocol/server-postgres

# Sequential thinking for complex problems
npm install -g @modelcontextprotocol/server-sequential-thinking
```

### 2. Configure MCP Servers
Update `.claude.json` with additional servers:
```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "mcp-server-filesystem", 
      "args": ["--path", "/mnt/c/taly/ai-system"]
    },
    "github": {
      "type": "stdio",
      "command": "mcp-server-github",
      "args": ["--repo", "your-org/ai-system"]
    },
    "sequential-thinking": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

---

## 🎯 Usage Examples

### 1. Architecture Analysis
```bash
claude /analyze-architecture

# Or direct prompt
claude "Analyze the memory engine architecture and suggest improvements for scalability"
```

### 2. Test Generation
```bash
claude /generate-tests

# Or specific component
claude "Generate comprehensive unit tests for the HITL engine with proper mocking"
```

### 3. Code Review
```bash
claude /review-code src/core/agents/

# Or specific file
claude "Review this file for security issues and performance optimizations" src/infrastructure/memory/engines/memory_engine.py
```

### 4. Performance Optimization
```bash
claude /optimize-performance

# Or specific focus
claude "Optimize the ChromaDB query performance and add better caching strategies"
```

### 5. Development Workflows
```bash
# Generate documentation
claude "Create comprehensive API documentation for the agent factory system"

# Refactor code
claude "Refactor the workflow engine to follow clean architecture principles"

# Debug issues
claude "Analyze why the memory engine is slow and provide optimization recommendations"
```

---

## 📊 Workflow Integration

### 1. Daily Development
```bash
# Morning: Review architecture
claude /analyze-architecture

# Development: Generate tests as you code
claude /generate-tests src/new-feature/

# Before PR: Review code quality
claude /review-code src/modified-files/
```

### 2. Code Review Process
```bash
# Automated pre-review
claude "Review this PR for code quality, security, and performance issues"

# Generate review comments
claude "Create detailed PR review comments with specific line-by-line feedback"
```

### 3. Performance Monitoring
```bash
# Regular performance audits
claude /optimize-performance

# Before deployments
claude "Analyze potential performance bottlenecks before production deployment"
```

---

## 🚀 Advanced Features

### 1. Headless Mode (CI/CD)
```bash
# Use in CI/CD pipelines
claude -p "Analyze code quality and generate report" --output-format stream-json

# Pre-commit hooks
claude -p "Review changes for security issues" --dangerously-skip-permissions
```

### 2. Custom Workflows
Create project-specific automation:
```bash
# Custom deployment checks
claude "Validate all tests pass, code quality meets standards, and security checks pass before deployment"

# Automated documentation updates
claude "Update README and API docs based on recent code changes"
```

---

## 🔧 Team Setup

### 1. Shared Configuration
```bash
# Commit .claude/ directory to git for team sharing
git add .claude/
git commit -m "Add Claude Code team configuration"
```

### 2. Team Standards
- All developers should use the same custom commands
- Shared MCP server configurations
- Consistent CLAUDE.md instructions
- Team-wide coding standards enforced through Claude Code

---

## 📋 Next Steps

1. **Install Claude Code CLI** following official documentation
2. **Configure project-specific settings** using this guide
3. **Set up MCP servers** for enhanced functionality
4. **Train team** on custom commands and workflows
5. **Integrate into CI/CD** for automated code quality

This setup transforms Claude Code from a generic coding assistant into a specialized AI system development accelerator tailored to our multi-agent architecture.