# Tools Directory

## Purpose
This directory contains all tools used by the AI system, including external service integrations, development tools, and infrastructure utilities.

## Directory Structure

### Core Infrastructure
- **base_tool.py** - Base class for all tools in the system
- **tool_loader.py** - Dynamic tool loading and management system

### Memory Engine
- **memory/** - Complete unified memory engine implementation
  - Includes caching, chunking, storage, security features
  - Enterprise-grade with encryption and PII detection

### External Service Integrations
- **github_tool.py** - GitHub API integration for code management
- **supabase_tool.py** - Supabase database integration
- **vercel_tool.py** - Vercel deployment integration

### Development & Testing Tools
- **cypress_tool.py** - Cypress E2E testing integration
- **jest_tool.py** - Jest unit testing integration
- **coverage_tool.py** - Code coverage analysis
- **run_code_quality.py** - Code quality checking script

### UI & Design Tools
- **design_system_tool.py** - Design system management
- **tailwind_tool.py** - Tailwind CSS integration
- **markdown_tool.py** - Markdown processing utilities

### Infrastructure Support Tools
- **context_tracker.py** - Tracks context usage across the system
- **context_visualizer.py** - Visualizes context relationships
- **rate_limiter.py** - API rate limiting functionality

### QA & Retrieval Tools
- **qa_cli.py** - QA command-line interface
- **retrieval_qa_refactored.py** - Primary retrieval QA implementation
- **retrieval_qa.py** - Legacy implementation (use refactored version)
- **fixed_retrieval_qa.py** - Compatibility fixes (use refactored version)

### Testing & Compatibility
- **compatibility/** - Mock implementations for external dependencies
  - ChromaDB, LangChain, and LangChain Core mocks
- **mock_crewai.py** - CrewAI mock for testing
- **mock_langchain.py** - Additional LangChain mocks
- **echo_tool.py** - Simple echo tool for testing

## Tool Development Guidelines

### Creating a New Tool
1. Inherit from `base_tool.py`
2. Implement required methods
3. Add to appropriate category
4. Update tool_loader configuration
5. Add tests

### Tool Categories
- **External**: Integrations with external services
- **Development**: Tools for development workflow
- **Infrastructure**: System-level utilities
- **QA**: Quality assurance and testing
- **Design**: UI and design-related tools

## Import Examples

```python
# Import a specific tool
from tools.github_tool import GitHubTool

# Import memory engine
from tools.memory.engine import MemoryEngine

# Import base tool for extension
from tools.base_tool import BaseTool

# Load tools dynamically
from tools.tool_loader import load_tools_for_agent
```

## Architecture Decisions

### Why Keep Everything in /tools/?
1. **Simplicity**: Single location for all tools
2. **Discoverability**: Easy to find all available tools
3. **Import Stability**: No need to update existing imports
4. **Working System**: Current structure is proven and functional

### Relationship to src/infrastructure/tools/
The `src/infrastructure/tools/` directory contains:
- Workflow-specific handlers
- Graph building utilities
- Infrastructure components that are not "tools" in the agent sense

This separation is intentional - agent tools vs infrastructure components.