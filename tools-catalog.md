# Tools Directory Catalog

## Overview
This document catalogs all tools in the `/tools/` directory and recommends organization strategy.

## Current Structure

### Core Infrastructure Tools (Should stay in /tools/)
These are foundational tools used across the system:

1. **base_tool.py** - Base class for all tools
2. **tool_loader.py** - Dynamic tool loading system
3. **memory/** - Unified memory engine (already optimized)
   - engine.py - Main memory engine
   - caching.py, chunking.py, storage.py - Memory subsystems
   - config.py, exceptions.py, factory.py - Configuration
   - security.py, thread_safe.py - Security features

### External Service Integration Tools (Should stay in /tools/)
Tools that integrate with external services:

4. **github_tool.py** - GitHub API integration
5. **supabase_tool.py** - Supabase database integration
6. **vercel_tool.py** - Vercel deployment integration
7. **vercel_tool_refactored.py** - Updated Vercel integration

### Development/Testing Tools (Should stay in /tools/)
Tools used for development and testing:

8. **cypress_tool.py** - Cypress E2E testing integration
9. **jest_tool.py** - Jest unit testing integration
10. **coverage_tool.py** - Code coverage analysis
11. **run_code_quality.py** - Code quality checker

### UI/Design Tools (Should stay in /tools/)
Tools for UI and design work:

12. **design_system_tool.py** - Design system management
13. **tailwind_tool.py** - Tailwind CSS integration
14. **markdown_tool.py** - Markdown processing

### Infrastructure Support Tools (Consider moving to src/infrastructure/tools/)
These provide infrastructure-level functionality:

15. **context_tracker.py** - Context usage tracking
16. **context_visualizer.py** - Context visualization
17. **rate_limiter.py** - API rate limiting

### QA/Retrieval Tools (Consider consolidating)
Multiple implementations of similar functionality:

18. **qa_cli.py** - QA command-line interface
19. **retrieval_qa.py** - Original retrieval QA
20. **retrieval_qa_refactored.py** - Refactored version
21. **fixed_retrieval_qa.py** - Fixed implementation

### Compatibility Layer (Should stay in /tools/compatibility/)
Mock implementations for testing:

22. **compatibility/** - Compatibility layer for external dependencies
    - chromadb/ - ChromaDB mocks
    - langchain/ - LangChain mocks
    - langchain_core/ - LangChain core mocks
23. **mock_crewai.py** - CrewAI mocks
24. **mock_langchain.py** - LangChain mocks

### Utility Tools
25. **echo_tool.py** - Simple echo tool for testing

## Recommendations

### 1. Keep in /tools/ Directory ✅
- All external service integrations (GitHub, Supabase, Vercel)
- Development/testing tools
- UI/design tools
- Base tool infrastructure
- Memory engine (already optimized)
- Compatibility layer

### 2. Move to src/infrastructure/tools/ 🔄
- context_tracker.py (infrastructure-level tracking)
- context_visualizer.py (infrastructure visualization)
- rate_limiter.py (infrastructure rate limiting)

### 3. Consolidate QA Tools 🔀
- Keep retrieval_qa_refactored.py as the primary implementation
- Archive retrieval_qa.py and fixed_retrieval_qa.py
- Update imports to use the refactored version

### 4. Directory Structure After Organization

```
tools/                          # User-facing and external integration tools
├── __init__.py
├── base_tool.py               # Base class
├── tool_loader.py             # Tool loading system
├── memory/                    # Memory engine (complete)
├── external/                  # External integrations (NEW)
│   ├── github_tool.py
│   ├── supabase_tool.py
│   └── vercel_tool.py
├── development/               # Dev/test tools (NEW)
│   ├── cypress_tool.py
│   ├── jest_tool.py
│   ├── coverage_tool.py
│   └── run_code_quality.py
├── design/                    # UI/design tools (NEW)
│   ├── design_system_tool.py
│   ├── tailwind_tool.py
│   └── markdown_tool.py
├── qa/                        # QA tools (NEW)
│   ├── qa_cli.py
│   └── retrieval_qa.py       # Refactored version only
└── compatibility/             # Mock implementations

src/infrastructure/tools/       # Infrastructure-level tools
├── context_tracker.py         # Moved from /tools/
├── context_visualizer.py      # Moved from /tools/
├── rate_limiter.py           # Moved from /tools/
└── handlers/                  # Existing handlers
```

## Benefits of This Organization

1. **Clear Separation**: Infrastructure vs user-facing tools
2. **Logical Grouping**: Tools organized by purpose
3. **Easier Discovery**: Developers can find tools quickly
4. **Maintainability**: Related tools are grouped together
5. **Import Clarity**: Clear import paths based on tool type