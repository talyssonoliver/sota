# /check - Comprehensive Code Quality Check

Perform a comprehensive code quality check on the AI system codebase.

## Steps:

1. **Static Analysis**
   ```bash
   echo "🔍 Running static analysis..."
   python -m mypy src/ --ignore-missing-imports --show-error-codes
   ```

2. **Code Formatting**
   ```bash
   echo "🎨 Checking code formatting..."
   python -m black --check src/ tests/
   python -m isort --check-only src/ tests/
   ```

3. **Linting**
   ```bash
   echo "🧹 Running linters..."    python -m ruff check src/ tests/
    ```

4. **Security Scan**
   ```bash
   echo "🔒 Security scanning..."
   python -m bandit -r src/ -f json -o security-report.json
   ```

5. **Test Suite**
   ```bash
   echo "🧪 Running test suite..."
   python -m pytest tests/ --tb=short -v
   ```

6. **Import Validation**
   ```bash
   echo "📦 Validating imports..."
   python -c "
   import sys
   sys.path.append('.')
   try:
       from src.core.agents import factory
       from src.core.workflows import execute_task
       from src.infrastructure.memory.engines import memory_engine
       print('✅ Core imports successful')
   except ImportError as e:
       print(f'❌ Import error: {e}')
   "
   ```

7. **Architecture Compliance**
   ```bash
   echo "🏗️ Checking architecture compliance..."
   python src/infrastructure/tools/validation/validate.py
   ```

## Success Criteria:
- All tests pass
- No linting errors
- No security vulnerabilities
- All imports work correctly
- Architecture guidelines followed