# Proposed Directory Structure Reorganization

## Current Issues
- 40+ items in root directory (way too cluttered)
- Mixed concerns (source code, build artifacts, logs, cache)
- Duplicate directories (context-source vs context-store)
- Massive cache/temp directories taking up space

## Proposed Clean Structure

```
ai-system/
├── 📁 src/                          # Core source code
│   ├── agents/
│   ├── api/
│   ├── cli/
│   ├── config/
│   ├── graph/
│   ├── handlers/
│   ├── orchestration/
│   ├── patches/
│   ├── prompts/
│   ├── scripts/
│   ├── tasks/
│   ├── templates/
│   ├── tools/
│   ├── utils/
│   └── visualization/
│
├── 📁 docs/                         # All documentation
│   ├── admin/                       # Administrative docs
│   │   ├── CODE_QUALITY_IMPROVEMENTS_SUMMARY.md
│   │   ├── MEMORY_ENGINE_REFACTORING_SUMMARY.md
│   │   └── projectContentAiSystem.txt
│   ├── architecture/                # System architecture docs
│   ├── api/                         # API documentation  
│   ├── completions/                 # Task completion docs
│   ├── optimizations/               # Performance docs
│   └── sprint/                      # Sprint documentation
│
├── 📁 data/                         # All data and context
│   ├── context/                     # Unified context (merge context-source + context-store)
│   │   ├── db/
│   │   ├── design/
│   │   ├── infra/
│   │   ├── patterns/
│   │   ├── product/
│   │   ├── sprint/
│   │   └── technical/
│   ├── memory-bank/                 # Knowledge management
│   └── sprints/                     # Sprint data
│
├── 📁 runtime/                      # Runtime artifacts (gitignored)
│   ├── cache/
│   ├── chroma_db/
│   ├── logs/
│   ├── outputs/
│   ├── reports/
│   ├── reviews/
│   └── temp/                        # Temporary files
│
├── 📁 tests/                        # All testing
│   ├── fixtures/
│   ├── integration/
│   ├── mock/
│   └── unit/
│
├── 📁 build/                        # Build artifacts
│   ├── archives/
│   ├── dashboard/
│   ├── static/
│   └── progress_reports/
│
├── 📁 examples/                     # Example code and demos
│
├── 📁 storage/                      # Persistent storage
│
├── 📄 Core files (keep in root)
├── CLAUDE.md
├── LICENSE  
├── README.md
├── main.py
├── requirements.txt
├── requirements-enterprise.txt
├── pyproject.toml
├── pytest.ini
├── mypy.ini
├── .gitignore (updated)
└── Package management files
```

## Benefits of This Structure

### 1. **Clean Root Directory** 
- Only 10-12 essential files in root
- Clear separation of concerns
- Professional project appearance

### 2. **Logical Grouping**
- **`src/`**: All source code in one place
- **`docs/`**: All documentation centralized
- **`data/`**: All data and context unified
- **`runtime/`**: All runtime artifacts (can be gitignored)
- **`build/`**: All build outputs

### 3. **Context Unification**
- Merge `context-source/` and `context-store/` into `data/context/`
- Eliminate duplication and confusion
- Single source of truth for context

### 4. **Cache Management**
- Move all cache/temp to `runtime/`
- Add to `.gitignore` to reduce repo size
- Clear separation of persistent vs temporary data

## Migration Strategy

### Phase 1: Create New Structure
1. Create new top-level directories
2. Move administrative docs to `docs/admin/`
3. Consolidate context directories

### Phase 2: Relocate Runtime Files  
1. Move `cache/`, `chroma_db/`, `logs/` to `runtime/`
2. Update `.gitignore` to exclude runtime artifacts
3. Clean up massive `mock-api-key/` directory

### Phase 3: Organize Source Code
1. Move all source directories under `src/`
2. Update import paths in code
3. Update configuration files

### Phase 4: Update Documentation
1. Update README.md with new structure
2. Update CLAUDE.md paths
3. Update memory-bank references

## Impact Assessment

### ✅ **Minimal Breaking Changes**
- Most imports are relative within modules
- Configuration files can be updated easily
- Docker/deployment scripts need path updates

### ⚠️ **Attention Required**
- Update import paths in main.py and entry points
- Update tool_loader.py paths
- Update workflow configuration paths
- Test all functionality after migration

### 🔧 **Configuration Updates Needed**
- `config/agents.yaml` - prompt template paths
- `config/tools.yaml` - tool paths  
- `pytest.ini` - test discovery paths
- `pyproject.toml` - package paths
- Any CI/CD scripts

## Implementation Priority

1. **High Priority**: Move runtime/cache files (immediate cleanup)
2. **Medium Priority**: Consolidate documentation  
3. **Low Priority**: Source code reorganization (more complex)

This reorganization will transform the project from a cluttered 40+ item root to a clean, professional 10-12 item structure that's much easier to navigate and maintain.