# /create-pr - Create Pull Request

Create a pull request with automated analysis and proper formatting.

## Steps:

1. **Pre-PR Validation**
   ```bash
   echo "🔍 Pre-PR validation..."
   
   # Ensure we're not on main branch
   CURRENT_BRANCH=$(git branch --show-current)
   if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
       echo "❌ Cannot create PR from main branch"
       echo "💡 Create a feature branch first: git checkout -b feature/your-feature"
       exit 1
   fi
   
   echo "✅ Current branch: $CURRENT_BRANCH"
   ```

2. **Analyze Changes**
   ```bash
   echo "📊 Analyzing changes..."
   
   # Get changed files
   CHANGED_FILES=$(git diff --name-only origin/main...HEAD)
   COMMIT_COUNT=$(git rev-list --count origin/main...HEAD)
   
   echo "📁 Changed files:"
   echo "$CHANGED_FILES"
   echo "📝 Commits in this branch: $COMMIT_COUNT"
   ```

3. **Run Quality Checks**
   ```bash
   echo "🧪 Running quality checks..."
   
   # Quick test suite
   PYTHONPATH=. python3 -m pytest tests/unit/ -x --tb=short -q
   if [ $? -ne 0 ]; then
       echo "❌ Tests failed - fix before creating PR"
       exit 1
   fi
   
   # Code formatting check
   python3 -m black --check . || {
       echo "⚠️ Code formatting issues found - running black..."
       python3 -m black .
       git add -A
       git commit -m "style: auto-format code with black"
   }
   ```

4. **Generate PR Description**
   ```bash
   echo "📝 Generating PR description..."
   
   # Analyze commit messages for summary
   COMMITS=$(git log --oneline origin/main...HEAD)
   
   # Determine PR type based on changes
   if echo "$CHANGED_FILES" | grep -q "src/core/"; then
       PR_TYPE="feat"
       PR_AREA="Core"
   elif echo "$CHANGED_FILES" | grep -q "src/infrastructure/"; then
       PR_TYPE="refactor"
       PR_AREA="Infrastructure"
   elif echo "$CHANGED_FILES" | grep -q "tests/"; then
       PR_TYPE="test"
       PR_AREA="Testing"
   elif echo "$CHANGED_FILES" | grep -q "docs/"; then
       PR_TYPE="docs"
       PR_AREA="Documentation"
   else
       PR_TYPE="chore"
       PR_AREA="General"
   fi
   
   PR_TITLE="${PR_TYPE}: ${CURRENT_BRANCH} - ${PR_AREA} improvements"
   ```

5. **Create PR with GitHub CLI**
   ```bash
   echo "🚀 Creating pull request..."
   
   gh pr create \
       --title "$PR_TITLE" \
       --body "$(cat <<EOF
   ## Summary
   
   This PR includes ${PR_AREA} improvements on branch \`${CURRENT_BRANCH}\`.
   
   ### Changes
   $(echo "$CHANGED_FILES" | sed 's/^/- /')
   
   ### Commits
   $(echo "$COMMITS" | sed 's/^/- /')
   
   ### Testing
   - [x] Unit tests pass
   - [x] Code formatting applied
   - [x] No linting errors
   
   ### Type of Change
   - $([ "$PR_TYPE" = "feat" ] && echo "[x]" || echo "[ ]") New feature
   - $([ "$PR_TYPE" = "refactor" ] && echo "[x]" || echo "[ ]") Code refactoring
   - $([ "$PR_TYPE" = "test" ] && echo "[x]" || echo "[ ]") Test improvements
   - $([ "$PR_TYPE" = "docs" ] && echo "[x]" || echo "[ ]") Documentation
   - $([ "$PR_TYPE" = "chore" ] && echo "[x]" || echo "[ ]") Maintenance
   
   🤖 Generated with [Claude Code](https://claude.ai/code)
   EOF
   )" \
       --draft=false
   ```

6. **Show PR Details**
   ```bash
   echo "✅ Pull request created!"
   
   # Get PR URL
   PR_URL=$(gh pr view --json url --jq .url)
   echo "🔗 PR URL: $PR_URL"
   
   # Show PR status
   gh pr view
   ```

7. **Post-Creation Tasks**
   ```bash
   echo "📋 Post-creation checklist:"
   echo "1. Review the PR description and edit if needed"
   echo "2. Add reviewers if required"
   echo "3. Link any related issues"
   echo "4. Monitor CI/CD status"
   echo "5. Address any review feedback"
   
   echo ""
   echo "💡 Useful commands:"
   echo "- View PR: gh pr view"
   echo "- Edit PR: gh pr edit"
   echo "- Check status: gh pr status"
   echo "- Merge PR: gh pr merge"
   ```

## Prerequisites:
- GitHub CLI (gh) must be installed and authenticated
- Must be on a feature branch (not main)
- Changes should be committed
- Tests should pass