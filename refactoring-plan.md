# Data Processing Modules Migration Checklist

## Overview
This checklist provides a step-by-step migration plan for consolidating duplicated data processing modules between `/tools/`, `/orchestration/`, and `/src/` directories. The plan is ordered by risk level to minimize test disruption.

## Pre-Migration Setup

### [ ] 1. Create Migration Branch
```bash
git checkout -b data-processing-migration
git add -A && git commit -m "Pre-migration snapshot - data processing modules"
```

### [ ] 2. Verify Current Test Status
```bash
python -m pytest tests/run_tests.py --quick
```

### [ ] 3. Document Current Import Dependencies
```bash
# Create backup of current import patterns
grep -r "from tools\." . --include="*.py" > pre-migration-imports.txt
grep -r "from orchestration\." . --include="*.py" >> pre-migration-imports.txt
```

## Phase 1: Zero-Impact Cleanup (Safe - No Dependencies)

### [ ] 4. Remove Already-Migrated Directory Duplicates
```bash
# Verify no active imports exist for these directories
grep -r "from agents\." . --include="*.py" | grep -v ".backup" | wc -l
grep -r "from analytics\." . --include="*.py" | grep -v ".backup" | wc -l
grep -r "from cli\." . --include="*.py" | grep -v ".backup" | wc -l
grep -r "from api\." . --include="*.py" | grep -v ".backup" | wc -l
grep -r "from dashboard\." . --include="*.py" | grep -v ".backup" | wc -l
```

### [ ] 5. Clean Up Empty Legacy Directories (if no imports found)
```bash
# Only execute if step 4 shows 0 imports for each directory
rm -rf agents/ analytics/ cli/ api/ dashboard/
```

### [ ] 6. Validate Phase 1
```bash
python -m pytest tests/run_tests.py --quick
```

## Phase 2: Memory Engine Data Processing (Medium Risk - 22 Dependencies)

### [ ] 7. Fix Duplicate Methods in Memory Engine
```bash
# Fix /src/infrastructure/memory/engines/memory_engine.py duplicate methods
# Remove duplicate clear() method (keep first occurrence)
# Remove duplicate secure_delete() method (keep first occurrence) 
# Remove duplicate get_stats() method (keep first occurrence)
```

### [ ] 8. Backup Current Memory Engine Files
```bash
cp src/infrastructure/memory/engines/memory_engine.py src/infrastructure/memory/engines/memory_engine.py.backup
cp tools/memory/engine.py tools/memory/engine.py.backup
cp src/infrastructure/memory/memory_engine.py src/infrastructure/memory/memory_engine.py.backup
```

### [ ] 9. Consolidate Memory Engine Implementation
```bash
# Copy the most complete version (tools/memory/engine.py) as base
# Merge recent fixes from src/infrastructure/memory/engines/memory_engine.py
# Update import statements to use consolidated location
```

### [ ] 10. Update Memory Factory Imports
```bash
# Update /tools/memory/factory.py to point to consolidated engine
# Update /src/infrastructure/memory/config/factory.py imports
```

### [ ] 11. Test Memory Engine Consolidation
```bash
python -m pytest tests/unit/platform/memory/ -v
python -m pytest tests/integration/memory/ -v
```

### [ ] 12. Update Memory Engine Import References
```bash
# Update all files importing memory engine to use single source
find . -name "*.py" -exec grep -l "from tools.memory.engine\|from src.infrastructure.memory.engines.memory_engine\|from src.infrastructure.memory.memory_engine" {} \;
```

## Phase 3: Data Processing Utilities (Low-Medium Risk)

### [ ] 13. Consolidate Data Handler Modules
```bash
# Consolidate qa_handler.py from 3 locations to 1
cp handlers/qa_handler.py src/infrastructure/tools/handlers/qa_handler.py
rm handlers/qa_handler.py
rm src/infrastructure/tools/qa_handler.py
```

### [ ] 14. Update Handler Import References
```bash
# Update imports from handlers.qa_handler to src.infrastructure.tools.handlers.qa_handler
grep -r "from handlers\." . --include="*.py" -l | xargs sed -i 's/from handlers\./from src.infrastructure.tools.handlers./g'
```

### [ ] 15. Consolidate Data Processing Tools
```bash
# Remove duplicate graph/visualization processing tools
rm -f src/infrastructure/tools/auto_generate_graph.py
rm -f src/infrastructure/tools/build_json.py
rm -f src/infrastructure/tools/critical_path.*
rm -f src/infrastructure/tools/flow.py
rm -f src/infrastructure/tools/graph_builder.py
```

### [ ] 16. Test Data Processing Utilities
```bash
python -m pytest tests/unit/core/ -v
python -m pytest tests/integration/test_analytics.py -v
```

## Phase 4: Workflow Data Processing (Medium Risk - 38 Files)

### [ ] 17. Backup Orchestration Files
```bash
mkdir -p backup/orchestration
cp -r orchestration/* backup/orchestration/
```

### [ ] 18. Identify Workflow Files with Differences
```bash
# Compare files between /orchestration/ and /src/core/workflows/
diff -r orchestration/ src/core/workflows/ > workflow-differences.txt
```

### [ ] 19. Merge Workflow Improvements
```bash
# Manually merge improvements from orchestration/ to src/core/workflows/
# Key files to review: daily_cycle.py, execute_workflow.py, qa_execution.py, register_output.py
```

### [ ] 20. Update Workflow Path References
```bash
# Update any scripts or configs referencing orchestration/ paths
grep -r "orchestration/" . --include="*.py" -l | xargs sed -i 's/orchestration\//src\/core\/workflows\//g'
```

### [ ] 21. Test Workflow Data Processing
```bash
python -m pytest tests/unit/core/workflows/ -v
python -m pytest tests/e2e/workflows/ -v
```

### [ ] 22. Remove Orchestration Directory
```bash
# Only after successful testing
rm -rf orchestration/
```

## Phase 5: Security & Patches Data Processing (Low Risk)

### [ ] 23. Consolidate Security Patches
```bash
cp patches/chromadb_telemetry_patch.py src/infrastructure/security/
```

### [ ] 24. Update Security Patch Imports
```bash
grep -r "from patches\." . --include="*.py" -l | xargs sed -i 's/from patches\./from src.infrastructure.security./g'
```

### [ ] 25. Remove Patches Directory
```bash
rm -rf patches/
```

### [ ] 26. Test Security Data Processing
```bash
python -m pytest tests/unit/core/test_chromadb_patch.py -v
```

## Phase 6: Context Data Processing (Medium-High Risk - 22+ Dependencies)

### [ ] 27. Backup Context Processing Files
```bash
cp tools/context_tracker.py tools/context_tracker.py.backup
cp src/infrastructure/tools/context_tracker.py src/infrastructure/tools/context_tracker.py.backup
```

### [ ] 28. Consolidate Context Tracker
```bash
# Keep tools/context_tracker.py as primary (more complete)
rm src/infrastructure/tools/context_tracker.py
```

### [ ] 29. Update Context Processing Imports
```bash
# Ensure all imports point to tools/context_tracker.py
grep -r "from src.infrastructure.tools.context_tracker" . --include="*.py" -l | xargs sed -i 's/from src.infrastructure.tools.context_tracker/from tools.context_tracker/g'
```

### [ ] 30. Test Context Data Processing
```bash
python -m pytest tests/ -k "context" -v
```

## Final Validation

### [ ] 31. Run Complete Test Suite
```bash
python -m pytest tests/run_tests.py --all
```

### [ ] 32. Validate Main Application Functionality
```bash
python -c "
import main
from src.infrastructure.memory.engines.memory_engine import MemoryEngine
from tools.context_tracker import ContextTracker
print('✅ All critical data processing imports successful')
"
```

### [ ] 33. Check Import Consistency
```bash
# Verify no orphaned imports remain
grep -r "from orchestration\." . --include="*.py" | grep -v ".backup"
grep -r "from patches\." . --include="*.py" | grep -v ".backup"
grep -r "from handlers\." . --include="*.py" | grep -v ".backup"
```

### [ ] 34. Performance Validation
```bash
# Ensure data processing performance is maintained
python orchestration/execute_task.py --task BE-01 --validate-only
```

### [ ] 35. Create Migration Summary
```bash
echo "Data Processing Migration Summary:" > migration-summary.txt
echo "- Memory Engine: Consolidated to src/infrastructure/memory/" >> migration-summary.txt
echo "- Workflows: Consolidated to src/core/workflows/" >> migration-summary.txt
echo "- Handlers: Consolidated to src/infrastructure/tools/handlers/" >> migration-summary.txt
echo "- Context Processing: Maintained in tools/" >> migration-summary.txt
echo "- Security: Consolidated to src/infrastructure/security/" >> migration-summary.txt
```

## Rollback Procedure (If Issues Occur)

### [ ] Emergency Rollback
```bash
git stash push -m "Migration in progress - issues encountered"
git reset --hard HEAD
# Restore from pre-migration snapshot
```

## Success Criteria

- [ ] All tests passing (python -m pytest tests/run_tests.py --all)
- [ ] No duplicate data processing modules remaining
- [ ] Consistent import patterns across codebase
- [ ] Main application functionality preserved
- [ ] Memory engine working with single source of truth
- [ ] Data processing performance maintained or improved

## Notes

- Execute checklist items in order
- Validate after each phase before proceeding
- Keep backups until full migration is verified
- Document any deviations from the plan
- Test thoroughly before removing backup files

---

**Migration Status**: Ready to Execute
**Estimated Time**: 3-5 hours with testing
**Risk Level**: Medium (due to memory engine and workflow dependencies)