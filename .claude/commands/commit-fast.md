# /commit-fast - Automated Git Commit

Create a structured git commit with automated checks and conventional commit formatting.

## Steps:

1. **Pre-commit Checks**
   ```bash
   echo "🔍 Running pre-commit checks..."
   python -m black . --check
   python -m isort . --check-only
   ```

2. **Stage Changes**
   ```bash
   echo "📝 Staging changes..."
   git add -A
   ```

3. **Generate Status**
   ```bash
   echo "📊 Current status:"
   git status --short
   git diff --cached --stat
   ```

4. **Commit with Convention**
   ```bash
   echo "💾 Creating commit..."
   
   # Analyze changes to determine commit type
   CHANGES=$(git diff --cached --name-only)
   
   if echo "$CHANGES" | grep -q "test"; then
       TYPE="test"
   elif echo "$CHANGES" | grep -q "docs/"; then
       TYPE="docs"
   elif echo "$CHANGES" | grep -q "src/core/"; then
       TYPE="feat"
   elif echo "$CHANGES" | grep -q "src/infrastructure/"; then
       TYPE="refactor"
   elif echo "$CHANGES" | grep -q "config/"; then
       TYPE="config"
   else
       TYPE="chore"
   fi
   
   # Get branch name for context
   BRANCH=$(git branch --show-current)
   
   # Create commit message
   TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
   git commit -m "${TYPE}: ${BRANCH} - automated commit ${TIMESTAMP}"
   ```

5. **Show Result**
   ```bash
   echo "✅ Commit created:"
   git log -1 --oneline
   git show --stat HEAD
   ```

## Usage Notes:
- Automatically determines commit type based on changed files
- Uses conventional commit format
- Includes timestamp and branch context
- Shows summary of committed changes