# Cleanup Architecture Artifacts

Execute comprehensive architecture artifact cleanup with intelligent retention policies to address the identified bloat issues.

## 🎯 ARCHITECTURE CLEANUP STRATEGY

### IDENTIFIED ISSUES FROM ULTRA-DEEP ANALYSIS:
- **Output Accumulation**: 219+ directories (PERF-0 through PERF-99, BE-01 through BE-14, etc.)
- **Log Files**: Timestamped execution logs accumulating indefinitely
- **Storage Tiers**: Hot/warm/cold storage without lifecycle management
- **Test Artifacts**: Build outputs and temporary files

### RETENTION POLICIES:
```yaml
perf_outputs: 3 days        # Performance test outputs
be_outputs: 7 days         # Backend task outputs  
fe_outputs: 7 days         # Frontend task outputs
ux_outputs: 7 days         # UX design outputs
tl_outputs: 14 days        # Technical lead outputs
pm_outputs: 14 days        # Product manager outputs
qa_outputs: 7 days         # QA validation outputs
concurrent_outputs: 1 day  # Concurrent test outputs
test_outputs: 1 day        # General test outputs
logs: 3 days              # All log files
hot_storage: 1 day        # Hot storage files
warm_storage: 7 days      # Warm storage files
briefings: 30 days        # Daily briefings
audit_logs: 90 days       # Audit trails (longest retention)
```

## 🔧 EXECUTION COMMANDS

### 1. Analysis Mode (Safe - No Deletions)
```bash
# Quick analysis of current state
python scripts/architecture_cleanup.py --extended-mode --dry-run --verbose

# Or via Makefile
make architecture-cleanup
```

### 2. Actual Cleanup (Removes Files)
```bash
# CAREFUL: This actually deletes files based on retention policies
python scripts/architecture_cleanup.py --extended-mode

# Or via Makefile with confirmation prompt
make architecture-cleanup-force
```

### 3. GitHub Workflow (Automated)
The system includes automated cleanup via `.github/workflows/architecture-cleanup.yml`:
- **Scheduled**: Every Sunday at 2 AM UTC
- **Manual**: Can be triggered via GitHub Actions
- **Monitoring**: Creates issues when storage thresholds exceeded

## 📊 EXPECTED RESULTS

Based on the ultra-deep analysis, this cleanup should:
- **Reduce Storage**: 70% reduction in artifact storage
- **Remove Directories**: Clean 100+ PERF-* directories older than 3 days
- **Clear Logs**: Remove timestamped logs older than 3 days
- **Optimize Performance**: Faster file system operations
- **Maintain Safety**: Preserve audit logs for 90 days

## 🛡️ SAFETY MEASURES

### Built-in Protections:
- **Dry Run Default**: Always shows what would be deleted first
- **4-Worker Limit**: Respects system resource constraints
- **Thread Safety**: Parallel processing with safe counters
- **Error Handling**: Graceful failure handling per file
- **Audit Preservation**: Critical logs retained for compliance

### Backup Strategy:
- **Git Integration**: All important files are version-controlled
- **Selective Cleanup**: Only removes generated artifacts, not source code
- **Rollback Capability**: Can recreate outputs by re-running tasks

## 🔍 MONITORING & ALERTS

### Storage Thresholds:
- **outputs/ > 500MB**: Creates GitHub issue alert
- **>200 output directories**: Triggers cleanup recommendation
- **Weekly Reports**: Automated status via GitHub workflow

### Manual Verification:
```bash
# Check sizes before cleanup
du -sh outputs/ logs/ build/storage/

# Run analysis to see what will be cleaned
make architecture-cleanup

# Check sizes after cleanup
du -sh outputs/ logs/ build/storage/
```

## 🎯 USAGE EXAMPLES

```bash
# 1. Quick check of current bloat
make architecture-cleanup

# 2. Clean only specific types (custom retention)
python scripts/architecture_cleanup.py --extended-mode --dry-run --retention-days 1

# 3. Emergency cleanup (force all expired)
make architecture-cleanup-force

# 4. Verify GitHub workflow locally
python scripts/architecture_cleanup.py --extended-mode --verbose
```

This addresses the critical architecture issues identified in the ultra-deep analysis while maintaining safety and providing comprehensive monitoring.