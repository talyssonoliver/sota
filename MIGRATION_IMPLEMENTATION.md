# Migration Implementation Guide

## Pre-Migration Setup

```bash
# Create backup branch
git checkout -b pre-migration-backup
git add -A && git commit -m "Backup before migration"

# Create migration branch
git checkout -b dependency-consolidation
```

## Phase 1: Zero-Impact Migrations (Day 1-2)

These old directories appear to be empty or already migrated based on analysis:

### 1.1 Verify Empty Directories
```bash
# Check if directories exist and are empty
ls -la agents/ analytics/ cli/ api/ dashboard/ 2>/dev/null || echo "Directories don't exist"

# Check for any remaining files
find agents/ analytics/ cli/ api/ dashboard/ -type f 2>/dev/null || echo "No files found"
```

### 1.2 Clean Up Empty Directories (if they exist)
```bash
# Only remove if truly empty
rmdir agents/ analytics/ cli/ api/ dashboard/ 2>/dev/null || echo "Directories not empty or don't exist"
```

## Phase 2: Low-Impact Migrations (Day 3-4)

### 2.1 Security Module Migration
```bash
# Check current security imports
grep -r "from security" . --include="*.py" | head -10
grep -r "import security" . --include="*.py" | head -10

# Move security files (if not already moved)
if [ -d "security/" ]; then
    echo "Moving security/ to src/infrastructure/security/"
    # Files are already in target location, just remove duplicates
    rm -rf security/
fi
```

### 2.2 Patches Migration  
```bash
# Check patches dependencies
grep -r "from patches" . --include="*.py"
grep -r "import patches" . --include="*.py"

# Update main.py patches import
sed -i 's/from patches import/from src.infrastructure.security import/g' main.py
sed -i 's/patches_module = secure_import('\''patches'\'')/patches_module = secure_import('\''src.infrastructure.security'\'')/g' main.py

# Remove old patches directory
rm -rf patches/
```

### 2.3 Handlers Migration
```bash
# Check handlers dependencies  
grep -r "from handlers" . --include="*.py"

# handlers/ content is already in src/infrastructure/tools/handlers/
rm -rf handlers/
```

### 2.4 Graph Module Migration
```bash
# Check graph dependencies
grep -r "from graph" . --include="*.py"
grep -r "import graph" . --include="*.py"

# Update imports pointing to graph/
find . -name "*.py" -exec sed -i 's/from graph\./from src.infrastructure.tools./g' {} \;
find . -name "*.py" -exec sed -i 's/import graph\./import src.infrastructure.tools./g' {} \;

# Move remaining graph files to infrastructure/tools if needed
if [ -d "graph/" ]; then
    for file in graph/*.py; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            if [ ! -f "src/infrastructure/tools/$filename" ]; then
                cp "$file" "src/infrastructure/tools/"
            fi
        fi
    done
    rm -rf graph/
fi
```

### 2.5 Engines Migration
```bash
# Check engines dependencies
grep -r "from engines" . --include="*.py"

# Update any remaining imports
find . -name "*.py" -exec sed -i 's/from engines\./from src.infrastructure.memory.engines./g' {} \;

# Remove old engines directory
rm -rf engines/
```

## Phase 3: Critical Memory Module Migration (Day 5-Week 2)

### 3.1 Create Compatibility Layer
```bash
# Create temporary compatibility module
cat > tools/memory_compat.py << 'EOF'
"""
Temporary compatibility layer for memory module migration.
This file forwards imports to the new location.
"""
import warnings

warnings.warn(
    "Importing from tools.memory is deprecated. Use src.infrastructure.memory instead.",
    DeprecationWarning,
    stacklevel=2
)

# Forward imports to new location
try:
    from src.infrastructure.memory.engines.memory_engine import MemoryEngine
    from src.infrastructure.memory.config.memory_config import MemoryEngineConfig
    from src.infrastructure.memory.config.exceptions import MemoryEngineError
    from src.infrastructure.memory.engines.caching import CacheManager
    from src.infrastructure.memory.engines.storage import StorageManager
    from src.infrastructure.memory.engines.chunking import ChunkProcessor
    
    # Re-export for backward compatibility
    __all__ = [
        'MemoryEngine', 
        'MemoryEngineConfig', 
        'MemoryEngineError',
        'CacheManager',
        'StorageManager', 
        'ChunkProcessor'
    ]
except ImportError as e:
    # Fallback if new modules not available
    from .memory.engine import MemoryEngine
    from .memory.config import MemoryEngineConfig
    from .memory.exceptions import MemoryEngineError
    
    __all__ = ['MemoryEngine', 'MemoryEngineConfig', 'MemoryEngineError']
EOF
```

### 3.2 Update Main Entry Points
```bash
# Update main.py memory imports
sed -i 's/from tools\.memory import/from src.infrastructure.memory.engines.memory_engine import/g' main.py
sed -i 's/from tools\.memory\./from src.infrastructure.memory./g' main.py

# Update any direct memory imports
find . -name "*.py" -not -path "./tools/memory_compat.py" -exec sed -i 's/from tools\.memory\.engine import/from src.infrastructure.memory.engines.memory_engine import/g' {} \;
find . -name "*.py" -not -path "./tools/memory_compat.py" -exec sed -i 's/from tools\.memory\.config import/from src.infrastructure.memory.config.memory_config import/g' {} \;
```

### 3.3 Update Test Files
```bash
# Update memory-related test imports
find tests/ -name "*.py" -exec sed -i 's/from tools\.memory/from src.infrastructure.memory.engines.memory_engine/g' {} \;
find tests/ -name "*.py" -exec sed -i 's/tools\.memory/src.infrastructure.memory/g' {} \;

# Special handling for test_memory_security.py
if [ -f "tests/test_memory_security.py" ]; then
    sed -i 's/tools\.memory\.security/src.infrastructure.memory.security.encryption/g' tests/test_memory_security.py
    sed -i 's/tools\.memory\.config/src.infrastructure.memory.config.memory_config/g' tests/test_memory_security.py
fi
```

## Phase 4: Orchestration Migration (Week 2)

### 4.1 Update Orchestration Imports
```bash
# Check current orchestration imports
grep -r "from orchestration" . --include="*.py" | head -10

# Update orchestration imports to new location
find . -name "*.py" -exec sed -i 's/from orchestration\./from src.core.workflows./g' {} \;
find . -name "*.py" -exec sed -i 's/import orchestration\./import src.core.workflows./g' {} \;

# Update any relative imports within orchestration
find src/core/workflows/ -name "*.py" -exec sed -i 's/from \.\./from src.core.workflows/g' {} \;
```

### 4.2 Remove Old Orchestration Directory
```bash
# Content is already in src/core/workflows/, remove duplicates
rm -rf orchestration/
```

## Phase 5: Tools Migration (Week 2-3)

### 5.1 Update Tools Imports (Critical)
```bash
# This is the most complex migration - update gradually

# Update base tool imports
find . -name "*.py" -exec sed -i 's/from tools\.base_tool import/from src.infrastructure.tools.base_tool import/g' {} \;

# Update specific tool imports
find . -name "*.py" -exec sed -i 's/from tools\.echo_tool import/from src.infrastructure.tools.echo_tool import/g' {} \;
find . -name "*.py" -exec sed -i 's/from tools\.supabase_tool import/from src.infrastructure.tools.supabase_tool import/g' {} \;

# Update tool loader
find . -name "*.py" -exec sed -i 's/from tools\.tool_loader import/from src.infrastructure.tools.tool_loader import/g' {} \;

# Update tools.__init__ imports
find . -name "*.py" -exec sed -i 's/from tools import/from src.infrastructure.tools import/g' {} \;
```

### 5.2 Update Main.py Tools Imports
```bash
# Critical main.py updates
sed -i 's/from tools\.echo_tool import EchoTool/from src.infrastructure.tools.echo_tool import EchoTool/g' main.py
sed -i 's/from tools\.supabase_tool import SupabaseTool/from src.infrastructure.tools.supabase_tool import SupabaseTool/g' main.py
```

## Validation Commands

### After Each Phase
```bash
# Test import resolution
python3 -c "import main" 2>&1 | head -10

# Quick test run
python3 -m pytest tests/ -x -q --tb=short 2>&1 | head -20

# Check for remaining old imports
grep -r "from tools\." . --include="*.py" | grep -v "src/infrastructure/tools" | head -10
grep -r "from orchestration\." . --include="*.py" | head -10
grep -r "from engines\." . --include="*.py" | head -10
```

### Full Validation
```bash
# Run comprehensive tests
python3 main.py --test

# Check for any remaining old import patterns
echo "Checking for old import patterns..."
grep -r "from tools\." . --include="*.py" | grep -v "src/infrastructure/tools" || echo "✅ No old tools imports"
grep -r "from orchestration\." . --include="*.py" || echo "✅ No old orchestration imports"  
grep -r "from engines\." . --include="*.py" || echo "✅ No old engines imports"
grep -r "from handlers\." . --include="*.py" || echo "✅ No old handlers imports"
grep -r "from graph\." . --include="*.py" | grep -v "src/infrastructure/tools" || echo "✅ No old graph imports"
```

## Cleanup (Week 3)

### Remove Compatibility Layers
```bash
# After confirming all imports work, remove compatibility files
rm -f tools/memory_compat.py

# Remove any remaining old directories
rmdir tools/memory/ 2>/dev/null || echo "tools/memory/ already removed"
```

### Final Verification
```bash
# Ensure no broken imports
python3 -m py_compile main.py
python3 -c "import src.core.agents.factory"
python3 -c "import src.infrastructure.memory.engines.memory_engine"
python3 -c "import src.infrastructure.tools.tool_loader"

# Run full test suite
python3 main.py --test

# Verify main functionality
python3 main.py
```

## Rollback Procedures

### If Migration Fails
```bash
# Rollback to pre-migration state
git checkout pre-migration-backup

# Or rollback specific changes
git checkout HEAD~1 -- main.py  # Rollback main.py changes
git checkout HEAD~1 -- tests/    # Rollback test changes
```

### Emergency Import Fix
```bash
# Quick fix for broken imports
cat > fix_imports.py << 'EOF'
import os
import re

def fix_import_paths(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Fix common import issues
                content = re.sub(r'from tools\.', 'from src.infrastructure.tools.', content)
                content = re.sub(r'from orchestration\.', 'from src.core.workflows.', content)
                content = re.sub(r'from engines\.', 'from src.infrastructure.memory.engines.', content)
                
                with open(file_path, 'w') as f:
                    f.write(content)

if __name__ == "__main__":
    fix_import_paths('.')
    print("Import paths fixed")
EOF

python3 fix_imports.py
```

This implementation guide provides step-by-step commands to execute the migration safely with proper validation at each step.