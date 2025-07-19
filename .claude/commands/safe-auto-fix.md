Apply ONLY pre-approved safe auto-fixes to file: $ARGUMENTS with comprehensive safety verification

## 🔒 ENHANCED SAFETY PROTOCOL

### PREREQUISITES (MANDATORY):
1. **Investigation Required**: File must have completed investigation report
2. **Git Clean State**: Working directory must be clean
3. **Tests Passing**: Full test suite must pass before changes
4. **Backup Created**: Feature branch created for rollback capability

### SAFE AUTO-FIX WHITELIST:
🟢 **ALWAYS SAFE** (No investigation needed):
- **Formatting**: Black, isort code formatting
- **Trailing Whitespace**: Remove trailing spaces/newlines
- **Line Length**: Break long lines (non-functional)

🟡 **SAFE AFTER INVESTIGATION** (Requires investigation approval):
- **E402**: Import ordering (if no circular import risk confirmed)
- **F541**: f-strings without placeholders (if no dynamic content)
- **W292**: No newline at end of file

🔴 **NEVER AUTO-FIX** (Always requires manual review):
- **F401**: Unused imports (may be incomplete implementations)
- **F841**: Unused variables (may need return/usage)
- **F821**: Undefined names (require implementation)
- **Function complexity**: Requires architectural decisions
- **Security issues**: Require security review

### ENHANCED SAFETY PROCESS:

#### 1. **Prerequisites Verification**
```bash
# Check investigation status
if [ ! -f "investigation_reports/$(basename $ARGUMENTS .py)_investigation.md" ]; then
  echo "❌ BLOCKED: File must be investigated first"
  echo "Run: /investigate-file $ARGUMENTS"
  exit 1
fi

# Verify git clean state
if [ -n "$(git status --porcelain)" ]; then
  echo "❌ BLOCKED: Git working directory must be clean"
  echo "Commit or stash changes first"
  exit 1
fi

# Verify tests passing
if ! pytest -xvs; then
  echo "❌ BLOCKED: Tests must pass before applying fixes"
  exit 1
fi
```

#### 2. **Create Safety Branch**
```bash
BRANCH_NAME="fix/$(basename $ARGUMENTS .py)-auto-fixes"
git checkout -b $BRANCH_NAME
echo "✅ Created safety branch: $BRANCH_NAME"
```

#### 3. **Apply Safe Fixes (Atomic Commits)**

##### **Step 3a: Formatting Fixes**
```bash
echo "🔧 Applying formatting fixes..."
black $ARGUMENTS
isort $ARGUMENTS

if [ -n "$(git diff $ARGUMENTS)" ]; then
  git add $ARGUMENTS
  git commit -m "style: apply black/isort formatting to $(basename $ARGUMENTS)"
  echo "✅ Formatting committed"
else
  echo "ℹ️ No formatting changes needed"
fi
```

##### **Step 3b: Safe Linting Fixes** 
```bash
echo "🔧 Applying safe linting fixes..."
# Only apply pre-approved safe fixes from investigation
ruff check $ARGUMENTS --fix --select E402,F541,W292

if [ -n "$(git diff $ARGUMENTS)" ]; then
  git add $ARGUMENTS  
  git commit -m "fix: apply safe linting fixes to $(basename $ARGUMENTS)"
  echo "✅ Safe linting fixes committed"
else
  echo "ℹ️ No safe linting fixes available"
fi
```

#### 4. **Verification & Quality Checks**

##### **Test Verification**
```bash
echo "🧪 Running test verification..."
if pytest -xvs; then
  echo "✅ All tests passing after fixes"
else
  echo "❌ TESTS FAILED - Rolling back changes"
  git checkout main
  git branch -D $BRANCH_NAME
  exit 1
fi
```

##### **Quality Verification**
```bash
echo "📊 Running quality checks..."
# Check improvement in issue count
ruff check $ARGUMENTS --output-format=json > after_fixes.json
ISSUES_AFTER=$(jq length after_fixes.json)
echo "📈 Issues after fixes: $ISSUES_AFTER"

# Security check
bandit -r $ARGUMENTS -f json -o bandit_check.json
if [ $? -eq 0 ]; then
  echo "✅ Security check passed"
else
  echo "⚠️ Security warnings present - review required"
fi
```

#### 5. **Documentation Update**
```bash
echo "📝 Updating tracking documentation..."
cat >> investigation_reports/$(basename $ARGUMENTS .py)_investigation.md << EOF

## 🔧 Auto-Fix Results Applied $(date)
- **Formatting**: Black/isort applied
- **Safe Linting**: E402, F541, W292 fixes applied  
- **Tests Status**: ✅ All passing
- **Issues Remaining**: $ISSUES_AFTER (down from previous count)
- **Git Commits**: 
  - Formatting: $(git log --oneline -1 --grep="style:")
  - Linting: $(git log --oneline -1 --grep="fix:")

## ✅ Ready for Manual Review
Remaining issues require manual investigation and fixes.
EOF
```

#### 6. **Merge Strategy**
```bash
echo "🔀 Merging safe fixes to main..."
git checkout main
git merge $BRANCH_NAME --no-ff -m "feat: safe auto-fixes for $(basename $ARGUMENTS)"
git branch -d $BRANCH_NAME
echo "✅ Safe fixes merged successfully"
```

### POST-FIX CHECKLIST:
- [ ] Investigation report exists and approved safe fixes
- [ ] Git working directory was clean before starting
- [ ] Feature branch created for safety
- [ ] Formatting fixes applied and committed
- [ ] Safe linting fixes applied and committed  
- [ ] Full test suite passes after all changes
- [ ] Quality metrics show improvement
- [ ] Security scan shows no new issues
- [ ] Tracking documentation updated
- [ ] Changes merged to main branch
- [ ] Feature branch cleaned up

### ROLLBACK PROCEDURE:
```bash
# If anything goes wrong during process:
git checkout main
git branch -D $BRANCH_NAME  # Remove failed branch
echo "🔄 Rolled back to clean state"

# To revert after merge (if needed):
git revert HEAD --no-edit
echo "🔄 Reverted merged changes"
```

### SUCCESS METRICS:
- **Issue Reduction**: Measurable decrease in linting issues
- **Test Stability**: All tests continue passing
- **No Regressions**: No new security or quality issues
- **Git History**: Clean, atomic commits with clear messages

**CRITICAL**: Only apply fixes explicitly approved in investigation report