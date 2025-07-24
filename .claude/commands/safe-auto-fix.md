Apply ONLY pre-approved safe auto-fixes to file: $ARGUMENTS with comprehensive safety verification and validation report integration.

## 🔒 ENHANCED SAFETY PROTOCOL v2.0

### MANDATORY PREREQUISITES (ZERO TOLERANCE):
1. **Investigation Report Required**: Must exist with pre-approved safe fixes
2. **Git Clean State**: Working directory must be completely clean
3. **Test Suite Passing**: All tests must pass before any changes
4. **Validation Report Check**: Confirm issues exist in validation report
5. **Backup Branch Created**: Safety rollback capability established

### ENHANCED SAFE AUTO-FIX WHITELIST v2.0:

🟢 **ALWAYS SAFE** (No investigation required):
- **Formatting Only**: Black, isort code formatting
- **Trailing Whitespace**: W292, W291 - Remove trailing spaces/newlines
- **Line Endings**: Standardize line endings (non-functional)

🟡 **CONDITIONALLY SAFE** (Investigation report must explicitly approve):
- **E402**: Import ordering (only if investigation confirms no circular imports)
- **F541**: f-strings without placeholders (only if investigation confirms no dynamic content)
- **E203**: Whitespace before ':' (safe with Black compatibility)

🔴 **NEVER AUTO-FIX** (Always blocked):
- **F401**: Unused imports (require codebase analysis)
- **F841**: Unused variables (require context analysis)  
- **F821**: Undefined names (require implementation)
- **Security Issues**: B*** codes (require security review)
- **Function Complexity**: C901, complex refactoring needed
- **Documentation**: Missing docstrings (require content creation)
- **Performance**: Function length issues (require architectural decisions)

### ENHANCED SAFETY PROCESS v2.0:

#### 1. **Comprehensive Prerequisites Verification**
```bash
echo "🔒 Starting enhanced safety verification for $ARGUMENTS..."

# 1. Check investigation report exists
INVESTIGATION_REPORT="investigation_reports/$(basename $ARGUMENTS .py)_investigation.md"
if [ ! -f "$INVESTIGATION_REPORT" ]; then
  echo "❌ BLOCKED: Investigation report not found"
  echo "   Required: $INVESTIGATION_REPORT"
  echo "   Action: Run /investigate-file $ARGUMENTS first"
  exit 1
fi
echo "✅ Investigation report found"

# 2. Verify investigation approved safe fixes
if ! grep -q "Pre-Approved Safe Fixes" "$INVESTIGATION_REPORT"; then
  echo "❌ BLOCKED: Investigation report lacks pre-approved fixes section"
  echo "   Action: Re-run /investigate-file $ARGUMENTS to generate complete report"
  exit 1
fi
echo "✅ Investigation contains pre-approved fixes"

# 3. Verify git clean state (strict)
GIT_STATUS=$(git status --porcelain)
if [ -n "$GIT_STATUS" ]; then
  echo "❌ BLOCKED: Git working directory must be completely clean"
  echo "   Current uncommitted changes:"
  echo "$GIT_STATUS" | head -5
  echo "   Action: Commit or stash all changes first"
  exit 1
fi
echo "✅ Git working directory clean"

# 4. Verify validation report has issues for this file
echo "🔍 Checking validation report for file issues..."
if ! cat reports/validation_report.json | jq -e --arg file "$ARGUMENTS" '.issues_grouped[].sample_occurrences[]? | select(.file | contains($file))' > /dev/null 2>&1; then
  echo "⚠️ WARNING: No issues found in validation report for this file"
  echo "   This may indicate the file is already clean or validation report is outdated"
  read -p "Continue anyway? (y/N): " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "❌ Aborted by user"
    exit 1
  fi
fi
echo "✅ Validation report contains issues for this file"

# 5. Quick test verification (optimized)
echo "🧪 Running quick test verification..."
if ! python3 -m pytest -x --tb=no -q 2>/dev/null; then
  echo "❌ BLOCKED: Test suite is not passing"
  echo "   Action: Fix failing tests before applying any changes"
  echo "   Run: python3 -m pytest -v to see failures"
  exit 1
fi
echo "✅ Test suite passing"

echo "🔓 All prerequisites verified - proceeding with safe fixes"
```

#### 2. **Enhanced Safety Branch Creation**
```bash
# Create descriptive safety branch with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILE_BASE=$(basename $ARGUMENTS .py)
BRANCH_NAME="safe-fix/${FILE_BASE}-${TIMESTAMP}"

echo "🌿 Creating safety branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"
echo "✅ Safety branch created and checked out"

# Record branch creation in investigation report
echo "" >> "$INVESTIGATION_REPORT"
echo "## 🔧 Auto-Fix Session Started $(date)" >> "$INVESTIGATION_REPORT"
echo "- **Branch**: $BRANCH_NAME" >> "$INVESTIGATION_REPORT"
echo "- **Target File**: $ARGUMENTS" >> "$INVESTIGATION_REPORT"
```

#### 3. **Enhanced Safe Fix Application (Atomic & Verified)**

##### **Step 3a: Always-Safe Formatting (Black/isort)**
```bash
echo "🎨 Applying always-safe formatting fixes..."

# Capture before state
BEFORE_HASH=$(git hash-object "$ARGUMENTS")

# Apply formatting
black "$ARGUMENTS" --quiet
isort "$ARGUMENTS" --quiet

# Check if changes were made
AFTER_HASH=$(git hash-object "$ARGUMENTS")
if [ "$BEFORE_HASH" != "$AFTER_HASH" ]; then
  # Verify file still compiles
  if python3 -m py_compile "$ARGUMENTS"; then
    git add "$ARGUMENTS"
    git commit -m "style: apply black/isort formatting to $(basename $ARGUMENTS)

🔧 Safe formatting applied:
- Black code formatting
- Import sorting with isort
- No functional changes

Automated formatting fixes"
    echo "✅ Formatting fixes committed"
    
    # Update investigation report
    echo "  - ✅ Formatting fixes applied and committed" >> "$INVESTIGATION_REPORT"
  else
    echo "❌ CRITICAL: Formatting broke compilation - reverting"
    git checkout HEAD -- "$ARGUMENTS"
    echo "  - ❌ Formatting fixes failed - reverted" >> "$INVESTIGATION_REPORT"
    exit 1
  fi
else
  echo "ℹ️ No formatting changes needed"
  echo "  - ℹ️ No formatting changes required" >> "$INVESTIGATION_REPORT"
fi
```

##### **Step 3b: Conditionally Safe Fixes (Investigation-Approved)**  
```bash
echo "🔧 Applying investigation-approved safe fixes..."

# Only apply fixes explicitly approved in investigation report
APPROVED_FIXES=""

# Check investigation report for specific approvals
if grep -q "Import Ordering.*approved\|E402.*safe" "$INVESTIGATION_REPORT"; then
  APPROVED_FIXES="$APPROVED_FIXES,E402"
  echo "  📦 Import ordering (E402) approved for fixing"
fi

if grep -q "Trailing Whitespace.*approved\|W292.*safe" "$INVESTIGATION_REPORT"; then
  APPROVED_FIXES="$APPROVED_FIXES,W292,W291"
  echo "  📝 Whitespace fixes (W292/W291) approved for fixing"
fi

if [ -n "$APPROVED_FIXES" ]; then
  # Remove leading comma
  APPROVED_FIXES=${APPROVED_FIXES#,}
  
  # Capture before state for verification
  BEFORE_ISSUES=$(python3 -m ruff check "$ARGUMENTS" --output-format=json | jq length)
  
  # Apply only approved fixes
  python3 -m ruff check "$ARGUMENTS" --fix --select "$APPROVED_FIXES" --quiet
  
  # Verify improvements and compilation
  AFTER_ISSUES=$(python3 -m ruff check "$ARGUMENTS" --output-format=json | jq length)
  
  if python3 -m py_compile "$ARGUMENTS"; then
    if [ -n "$(git diff $ARGUMENTS)" ]; then
      git add "$ARGUMENTS"
      git commit -m "fix: apply investigation-approved safe fixes to $(basename $ARGUMENTS)

🔧 Approved fixes applied:
- Codes: $APPROVED_FIXES
- Issues before: $BEFORE_ISSUES
- Issues after: $AFTER_ISSUES

Automated formatting fixes"
      echo "✅ Approved safe fixes committed (reduced $BEFORE_ISSUES → $AFTER_ISSUES issues)"
      echo "  - ✅ Approved fixes applied: $APPROVED_FIXES" >> "$INVESTIGATION_REPORT"
    else
      echo "ℹ️ No changes from approved fixes"
      echo "  - ℹ️ Approved fixes resulted in no changes" >> "$INVESTIGATION_REPORT"
    fi
  else
    echo "❌ CRITICAL: Approved fixes broke compilation - reverting"
    git checkout HEAD -- "$ARGUMENTS"
    echo "  - ❌ Approved fixes failed compilation - reverted" >> "$INVESTIGATION_REPORT"
    exit 1
  fi
else
  echo "ℹ️ No conditionally safe fixes approved in investigation report"
  echo "  - ℹ️ No conditionally safe fixes were pre-approved" >> "$INVESTIGATION_REPORT"
fi
```

#### 4. **Comprehensive Verification & Quality Assurance**

##### **Enhanced Test Verification**
```bash
echo "🧪 Running comprehensive test verification..."

# Quick syntax verification first
if ! python3 -c "import ast; ast.parse(open('$ARGUMENTS').read())"; then
  echo "❌ CRITICAL: File has syntax errors after fixes"
  echo "  - ❌ Syntax errors detected - rolling back" >> "$INVESTIGATION_REPORT"
  git checkout main
  git branch -D "$BRANCH_NAME"
  exit 1
fi

# Run targeted tests (optimized for speed)
echo "⚡ Running fast test verification..."
if ! python3 -m pytest -x --tb=no -q --maxfail=1 2>/dev/null; then
  echo "❌ CRITICAL: Tests failed after applying fixes"
  echo "  Running detailed test analysis..."
  python3 -m pytest -x --tb=short -v | tee test_failure_log.txt
  echo "  - ❌ Test failures detected - rolling back" >> "$INVESTIGATION_REPORT"
  echo "  - 📋 Test failure log saved to test_failure_log.txt" >> "$INVESTIGATION_REPORT"
  
  # Emergency rollback
  git checkout main
  git branch -D "$BRANCH_NAME"
  exit 1
fi
echo "✅ All tests passing after fixes"
echo "  - ✅ Full test suite verification passed" >> "$INVESTIGATION_REPORT"
```

##### **Advanced Quality & Issue Reduction Verification**
```bash
echo "📊 Running quality improvement verification..."

# Generate comprehensive quality report
QUALITY_REPORT="investigation_reports/$(basename $ARGUMENTS .py)_post_fix_quality.json"

python3 -c "
import json
import subprocess
import sys

try:
    # Get current ruff issues
    ruff_result = subprocess.run(['python3', '-m', 'ruff', 'check', '$ARGUMENTS', '--output-format=json'], 
                                capture_output=True, text=True)
    current_issues = json.loads(ruff_result.stdout) if ruff_result.stdout else []
    
    # Get validation report issues for this file (for comparison)
    with open('reports/validation_report.json') as f:
        validation_data = f.load()
    
    validation_issues = []
    for issue_group in validation_data.get('issues_grouped', []):
        for occurrence in issue_group.get('sample_occurrences', []):
            if '$ARGUMENTS' in occurrence.get('file', ''):
                validation_issues.append({
                    'category': issue_group['category'],
                    'message': issue_group['message_pattern'],
                    'line': occurrence.get('line', 0)
                })
    
    # Security scan
    bandit_result = subprocess.run(['bandit', '-r', '$ARGUMENTS', '-f', 'json'], 
                                  capture_output=True, text=True)
    bandit_issues = json.loads(bandit_result.stdout).get('results', []) if bandit_result.stdout else []
    
    # Compile quality report
    quality_report = {
        'timestamp': '$(date)',
        'file': '$ARGUMENTS',
        'current_ruff_issues': len(current_issues),
        'validation_issues_count': len(validation_issues),
        'security_issues': len(bandit_issues),
        'ruff_details': current_issues,
        'bandit_details': bandit_issues
    }
    
    with open('$QUALITY_REPORT', 'w') as f:
        json.dump(quality_report, f, indent=2)
    
    print(f'📊 Quality Report Generated:')
    print(f'  Current Ruff Issues: {len(current_issues)}')
    print(f'  Original Validation Issues: {len(validation_issues)}')
    print(f'  Security Issues: {len(bandit_issues)}')
    
    # Calculate improvement
    if len(validation_issues) > 0:
        improvement = ((len(validation_issues) - len(current_issues)) / len(validation_issues)) * 100
        print(f'  📈 Quality Improvement: {improvement:.1f}%')
    
except Exception as e:
    print(f'❌ Error generating quality report: {e}', file=sys.stderr)
    sys.exit(1)
"

# Record quality metrics in investigation report
echo "" >> "$INVESTIGATION_REPORT"
echo "## 📊 Post-Fix Quality Metrics" >> "$INVESTIGATION_REPORT"
cat "$QUALITY_REPORT" | jq -r '"- **Current Issues**: \(.current_ruff_issues)", "- **Original Issues**: \(.validation_issues_count)", "- **Security Issues**: \(.security_issues)"' >> "$INVESTIGATION_REPORT"

echo "✅ Quality verification complete - metrics saved to $QUALITY_REPORT"
```

#### 5. **Enhanced Documentation & Tracking Update**
```bash
echo "📝 Finalizing documentation and tracking..."

# Complete investigation report with session results
echo "" >> "$INVESTIGATION_REPORT"
echo "## ✅ Auto-Fix Session Complete $(date)" >> "$INVESTIGATION_REPORT"
echo "- **Duration**: $((SECONDS/60)) minutes" >> "$INVESTIGATION_REPORT"
echo "- **Commits Created**: $(git rev-list --count HEAD ^main)" >> "$INVESTIGATION_REPORT"
echo "- **Files Modified**: $ARGUMENTS" >> "$INVESTIGATION_REPORT"
echo "- **Test Status**: ✅ All tests passing" >> "$INVESTIGATION_REPORT"
echo "" >> "$INVESTIGATION_REPORT"
echo "### Git Commit Summary:" >> "$INVESTIGATION_REPORT"
git log --oneline HEAD ^main >> "$INVESTIGATION_REPORT"
echo "" >> "$INVESTIGATION_REPORT"
echo "### Next Steps:" >> "$INVESTIGATION_REPORT"
echo "- [ ] Review remaining issues requiring manual fixes" >> "$INVESTIGATION_REPORT"
echo "- [ ] Update master checklist with progress" >> "$INVESTIGATION_REPORT"
echo "- [ ] Consider merging safe fixes to main branch" >> "$INVESTIGATION_REPORT"

# Update master checklist if it exists
if [ -f "fix_tracking/master_checklist.md" ]; then
  # Update file status in master checklist
  sed -i "s|### File: $ARGUMENTS.*|### File: $ARGUMENTS\\n**Issues**: Reduced | **Status**: [x] Safe Fixes Applied | **Risk**: Low-Medium|" fix_tracking/master_checklist.md
  echo "📋 Master checklist updated with progress"
fi

echo "✅ Documentation updates complete"
```

#### 6. **Smart Merge Strategy with User Choice**
```bash
echo "🔀 Safe fixes ready for integration..."
echo ""
echo "📊 Session Summary:"
echo "  - Safe fixes applied to: $(basename $ARGUMENTS)"
echo "  - Commits created: $(git rev-list --count HEAD ^main)"
echo "  - Test status: ✅ All passing"
echo "  - Quality improvements: See $QUALITY_REPORT"
echo ""
echo "🤔 Integration Options:"
echo "  1. Merge to main immediately (recommended for safe fixes)"
echo "  2. Keep in branch for further review"
echo "  3. Create pull request for team review"
echo ""

read -p "Choose integration strategy (1/2/3): " choice

case $choice in
  1)
    echo "🔀 Merging safe fixes to main..."
    git checkout main
    git merge "$BRANCH_NAME" --no-ff -m "feat: safe auto-fixes for $(basename $ARGUMENTS)

🔧 Applied safe fixes:
- Formatting improvements (black/isort)
- Investigation-approved linting fixes
- Zero functional changes
- All tests passing

Automated formatting fixes
Branch: $BRANCH_NAME"
    git branch -d "$BRANCH_NAME"
    echo "✅ Safe fixes merged and branch cleaned up"
    echo "  - ✅ Merged to main and branch cleaned up" >> "$INVESTIGATION_REPORT"
    ;;
  2)
    echo "🌿 Keeping branch for further review: $BRANCH_NAME"
    git checkout main
    echo "  - 🌿 Branch preserved for review: $BRANCH_NAME" >> "$INVESTIGATION_REPORT"
    ;;
  3)
    echo "🔄 Branch ready for pull request: $BRANCH_NAME"
    echo "   Use: git push origin $BRANCH_NAME"
    echo "   Then create PR in your repository interface"
    git checkout main
    echo "  - 🔄 Branch ready for PR creation: $BRANCH_NAME" >> "$INVESTIGATION_REPORT"
    ;;
  *)
    echo "⚠️ Invalid choice - keeping branch for manual decision: $BRANCH_NAME"
    git checkout main
    echo "  - ⚠️ Manual integration decision required for: $BRANCH_NAME" >> "$INVESTIGATION_REPORT"
    ;;
esac
```

### ENHANCED POST-FIX CHECKLIST v2.0:
- [ ] ✅ Investigation report existed with pre-approved safe fixes
- [ ] ✅ Git working directory was completely clean before starting
- [ ] ✅ All tests passed before any changes
- [ ] ✅ Validation report confirmed issues existed for target file
- [ ] ✅ Safety branch created with timestamp
- [ ] ✅ Always-safe formatting fixes applied (Black/isort)
- [ ] ✅ Investigation-approved conditional fixes applied
- [ ] ✅ Syntax compilation verified after each fix
- [ ] ✅ Full test suite passes after all changes
- [ ] ✅ Quality metrics generated showing improvement
- [ ] ✅ Security scan shows no new critical issues
- [ ] ✅ Investigation report updated with session results
- [ ] ✅ Master checklist updated with progress
- [ ] ✅ Integration strategy chosen and executed
- [ ] ✅ Branch properly managed (merged/preserved/PR-ready)

### ENHANCED ROLLBACK PROCEDURES:

#### **Emergency Rollback (During Session)**
```bash
# If critical failure occurs during auto-fix process:
echo "🚨 EMERGENCY ROLLBACK INITIATED"
git checkout main
git branch -D "$BRANCH_NAME"  # Remove failed branch
echo "🔄 Rolled back to clean state - no changes applied"
echo "📝 Check investigation report for failure details"
```

#### **Post-Merge Rollback (If Issues Discovered)**  
```bash
# If problems discovered after merge:
echo "🔄 POST-MERGE ROLLBACK"
git log --oneline -5  # Show recent commits
read -p "Enter commit hash to revert to: " target_commit
git revert HEAD --no-edit -m "Rollback safe-auto-fix due to issues discovered"
echo "🔄 Reverted merged changes - system restored"
```

#### **Selective Rollback (Individual Commits)**
```bash
# To revert specific commits within the auto-fix:
git log --oneline HEAD~5..HEAD  # Show auto-fix commits
read -p "Enter specific commit hash to revert: " commit_hash
git revert $commit_hash --no-edit
echo "🔄 Selectively reverted commit: $commit_hash"
```

### SUCCESS METRICS & VALIDATION:
- **Issue Reduction**: Measurable decrease in validation report issues (tracked in quality report)
- **Test Stability**: Zero test failures or regressions introduced
- **Compilation Safety**: All files compile successfully after changes
- **No Security Regressions**: No new critical security issues introduced
- **Documentation Completeness**: All changes tracked in investigation reports
- **Git History Cleanliness**: Atomic commits with descriptive messages
- **Rollback Capability**: All changes easily reversible

### VALIDATION THRESHOLDS:
- **Minimum Issue Reduction**: At least 1 issue fixed per session
- **Maximum Risk Tolerance**: Zero breaking changes allowed
- **Test Pass Rate**: 100% (no exceptions)
- **Security Regression**: Zero tolerance for new critical issues
- **Documentation Coverage**: 100% of changes documented

**CRITICAL SAFETY REMINDER**: This command applies ONLY explicitly pre-approved safe fixes from investigation reports. Any deviation from approved fixes is strictly prohibited and will result in automatic rollback.