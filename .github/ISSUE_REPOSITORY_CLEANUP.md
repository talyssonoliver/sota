# Repository Cleanup & File Organization

## Priority: MEDIUM  
**Estimated Effort:** 2-3 hours  
**Impact:** Developer experience, maintainability

## Problem Statement
The repository contains numerous temporary development artifacts, test files, and experimental code that should be properly organized, archived, or cleaned up to improve maintainability and developer onboarding.

## Current State Analysis
From recent commits, the following file organization improvements are needed:

### ✅ Recently Completed
- Phase 6 artifacts properly committed and documented
- Test files reorganized under `tests/` directory  
- Dashboard components consolidated
- Sprint completion summaries archived

### 🧹 Cleanup Required

#### 1. Temporary Development Files
```
dashboard/debug_exports_error.html
dashboard/diagnostic_exports.html  
dashboard/test_cdn_scripts.html
dashboard/test_dashboard_minimal.html
dashboard/test_datefns_cdn.html
dashboard/loading_diagnostic.html
dashboard/complete_diagnostic.html
```

#### 2. Duplicate/Backup Files
```
utils/completion_metrics_backup.py
utils/completion_metrics_clean.py  
orchestration/generate_briefing_corrupted.py
dashboard/api_server.py vs api_server_working.py
dashboard/enhanced_dashboard.js vs enhanced_dashboard_working.js
```

#### 3. Validation Scripts (Move to scripts/)
```
tests/validate_*.py files (12 files)
tests/debug_*.py files (3 files)
```

## Implementation Plan

### Phase 1: Archive Development Artifacts (1 hour)
```bash
# Create development archive
mkdir -p archives/development/phase6-artifacts
mv dashboard/debug_* archives/development/phase6-artifacts/
mv dashboard/test_* archives/development/phase6-artifacts/
mv dashboard/diagnostic_* archives/development/phase6-artifacts/
```

### Phase 2: Cleanup Duplicates (30 min)
- [ ] Remove backup files after verifying main versions work
- [ ] Consolidate working vs non-working API server files
- [ ] Remove corrupted/experimental files

### Phase 3: Reorganize Scripts (30 min)  
- [ ] Move validation scripts to `scripts/validation/`
- [ ] Move debug scripts to `scripts/debug/`
- [ ] Update any import references

### Phase 4: Documentation Update (1 hour)
- [ ] Update README.md with new file organization
- [ ] Add development guidelines for temporary files
- [ ] Document archival process for future use

## File Organization Structure
```
archives/
  development/           # Development artifacts
    phase6-artifacts/    # Phase 6 debug/test files  
    experiments/         # Experimental code
scripts/
  debug/                 # Debug utilities
  validation/            # Validation scripts  
  maintenance/           # Cleanup scripts
dashboard/
  [production files only]
tests/
  [actual test files only]
```

## Benefits
- 🧹 Cleaner repository structure
- 📚 Better developer onboarding experience  
- 🔍 Easier to find production vs development files
- 📦 Reduced repository size
- 🎯 Clear separation of concerns

## Acceptance Criteria
- [ ] All temporary debug files archived or removed
- [ ] No duplicate or backup files in main directories
- [ ] Validation/debug scripts properly organized
- [ ] Documentation updated to reflect new structure
- [ ] Repository passes clean-state validation
