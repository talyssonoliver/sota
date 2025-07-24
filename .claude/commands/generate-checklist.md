Generate comprehensive quality issue checklist from validation report with risk-based prioritization and file-by-file tracking.

## 🎯 ENHANCED CHECKLIST GENERATION

### Data Sources Integration:
1. **Primary**: `/reports/validation_report.json` (6,067 total issues analyzed)
2. **Secondary**: Live ruff output: `python3 -m ruff check . --output-format=json`
3. **Cross-Reference**: Bandit security scan results from validation report
4. **File Discovery**: `find src/ -name "*.py"` for comprehensive file inventory
5. **Git Status**: Current working directory state for safety verification

### Risk Classification Matrix:
- 🟢 **LOW RISK** (Auto-fix safe): E402 import ordering, formatting, empty dirs, trailing whitespace
- 🟡 **MEDIUM RISK** (Investigation required): F401 unused imports, F841 unused variables, function complexity
- 🔴 **HIGH RISK** (Architecture decisions): Security issues, test coverage, code duplication >48%

### Enhanced Process Workflow:

#### 1. **Validation Report Analysis**
```bash
# Extract key metrics from validation report
cat reports/validation_report.json | jq -r '
.issues_grouped[] | 
select(.count > 10) | 
"\(.category):\(.type) - \(.count) issues (\(.severity))"
' | sort -rn -k3

# Extract file-specific issue mapping
cat reports/validation_report.json | jq -r '
.issues_grouped[] | 
.sample_occurrences[] | 
"\(.file):\(.line) - \(.category) - \(.severity)"
' > file_issue_mapping.tmp
```

#### 2. **Live Issue Cross-Reference**
```bash
# Get current ruff status for line-specific details
python3 -m ruff check . --output-format=json > current_ruff_issues.json

# Cross-reference with validation report for accuracy
python3 -c "
import json
with open('reports/validation_report.json') as f:
    validation = json.load(f)
with open('current_ruff_issues.json') as f:
    current = json.load(f)
print(f'Validation issues: {validation[\"total_issues\"]}')
print(f'Current ruff issues: {len(current)}')
"
```

#### 3. **File-by-File Risk Assessment**
```bash
# Generate file list with issue counts
find src/ -name "*.py" | while read file; do
    issue_count=$(grep -c "^$file:" file_issue_mapping.tmp 2>/dev/null || echo "0")
    echo "$file:$issue_count"
done | sort -rn -t: -k2 > files_by_issue_count.txt
```

#### 4. **Master Checklist Generation**
```bash
# Create comprehensive tracking checklist
cat > fix_tracking/master_checklist.md << 'EOF'
# Master Quality Issue Resolution Checklist
**Generated**: $(date)
**Total Issues**: $(cat reports/validation_report.json | jq .total_issues)
**Files Affected**: $(find src/ -name "*.py" | wc -l)

## 📊 Issue Summary by Category
$(cat reports/validation_report.json | jq -r '.issues_by_category | to_entries[] | "- **\(.key)**: \(.value) issues"')

## 📋 File-by-File Execution Plan

EOF

# Append each file with its issues
while IFS=: read -r file issue_count; do
    if [ "$issue_count" -gt 0 ]; then
        cat >> fix_tracking/master_checklist.md << EOF

### File: $file
**Issues**: $issue_count | **Status**: [ ] Not Started | **Risk**: TBD
**Investigation**: [ ] Required | **Fixes Applied**: [ ] None | **Tests**: [ ] Verified

#### Issue Details:
$(grep "^$file:" file_issue_mapping.tmp | head -5)

#### Action Items:
- [ ] Run investigation: \`/investigate-file $file\`
- [ ] Apply safe fixes: \`/safe-auto-fix $file\`
- [ ] Verify tests passing
- [ ] Update status in checklist

---
EOF
    fi
done < files_by_issue_count.txt
```

### Enhanced File Entry Format:
```markdown
## File: src/core/agents/backend.py
**Priority**: 🟡 MEDIUM | **Issues**: 12 total | **Risk**: Investigation Required
**Git Status**: [ ] Ready for commit | **Tests**: [ ] Verified passing | **Last Updated**: $(date)

### Issue Breakdown (from validation report):
- **Security** (7): B404 subprocess usage warnings  
- **Code Quality** (3): E402 import ordering, F841 unused variables
- **Documentation** (2): Missing docstrings for classes
- **Performance** (0): No function length issues detected

### Risk Assessment Matrix:
- 🟢 **Safe Auto-Fix** (3): Import ordering, formatting fixes
- 🟡 **Requires Investigation** (2): Unused variables, security context
- 🔴 **Manual Review** (7): Subprocess security implications

### Investigation Checklist:
- [ ] **Security B404**: Analyze subprocess usage context and necessity
- [ ] **F841 Variables**: Check if variables should be returned/used  
- [ ] **Import Analysis**: Verify no incomplete implementations
- [ ] **Test Dependencies**: Check if any tests mock/use affected functions

### Execution Strategy:
1. **Investigation First**: `/investigate-file src/core/agents/backend.py`
2. **Safe Fixes**: Import ordering, formatting (if approved)
3. **Security Review**: Manual analysis of subprocess usage
4. **Documentation**: Add missing docstrings
5. **Final Verification**: Full test suite + manual testing

### Git Strategy:
- **Branch**: `fix/core-agents-backend-quality`
- **Commit Sequence**: 
  1. `style: apply formatting fixes`
  2. `fix: resolve import ordering issues`  
  3. `security: review and document subprocess usage`
  4. `docs: add missing docstrings`
- **Rollback Plan**: Individual commit reversion capability
```

#### 5. **Phase Classification & Prioritization**
```bash
# Classify files into execution phases based on issue types and counts
python3 -c "
import json
import sys

# Load validation report
with open('reports/validation_report.json') as f:
    data = json.load(f)

# Phase classification logic
phase1_files = []  # Low risk: <5 issues, mostly formatting
phase2_files = []  # Medium risk: 5-15 issues, imports/variables  
phase3_files = []  # High risk: 15+ issues, complex/security

for issue_group in data.get('issues_grouped', []):
    for occurrence in issue_group.get('sample_occurrences', []):
        file_path = occurrence['file']
        category = issue_group['category']
        count = issue_group['count']
        
        # Simple classification logic (to be refined)
        if 'src/' in file_path:
            if count < 5 and category in ['structure', 'code_quality']:
                if file_path not in [f[0] for f in phase1_files]:
                    phase1_files.append((file_path, count, category))
            elif count < 15:
                if file_path not in [f[0] for f in phase2_files]:
                    phase2_files.append((file_path, count, category))
            else:
                if file_path not in [f[0] for f in phase3_files]:
                    phase3_files.append((file_path, count, category))

print('Phase 1 (Low Risk):', len(phase1_files), 'files')
print('Phase 2 (Medium Risk):', len(phase2_files), 'files') 
print('Phase 3 (High Risk):', len(phase3_files), 'files')
"
```

### Execution Phase Strategy:

#### 🟢 **Phase 1: Low-Risk Auto-Fixes** (Sessions 1-3)
**Target**: 208 structure + 140 code quality = ~348 safe issues
**Files**: ~30-50 files with minimal complexity
**Strategy**: Automated fixes with verification
- Empty directory cleanup
- Import ordering (E402 - safe cases only)
- Formatting (Black/isort application)
- Trailing whitespace removal

#### 🟡 **Phase 2: Investigation & Medium Fixes** (Sessions 4-8) 
**Target**: 499 import + variable issues requiring analysis
**Files**: ~40-60 files with moderate complexity
**Strategy**: Investigation-first, then targeted fixes
- F401 unused imports (with codebase analysis)
- F841 unused variables (with context analysis)
- Basic documentation additions
- Simple function refactoring

#### 🔴 **Phase 3: Complex & Security Issues** (Sessions 9-15)
**Target**: 3,881 security + 843 performance issues
**Files**: ~20-30 most complex files
**Strategy**: Architectural review and comprehensive fixes
- Subprocess security analysis (B404)
- Function complexity reduction
- Test coverage improvements
- Authentication & validation gaps

### Enhanced Safety Protocols:
- **Pre-Phase Git Checkpoint**: Backup branch before each phase
- **File-Level Verification**: Tests must pass after each file
- **Issue Count Tracking**: Monitor reduction in validation issues
- **Rollback Capability**: Atomic commits enable individual file reversion
- **Progress Documentation**: Continuous checklist updates

### Success Metrics Per Phase:
- **Phase 1**: 50% issue reduction, zero test failures
- **Phase 2**: 70% issue reduction, improved code clarity  
- **Phase 3**: 80% issue reduction, production readiness

**CRITICAL**: This generates comprehensive tracking and execution strategy - NO auto-fixes applied without explicit investigation approval