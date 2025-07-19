# /test-quick - Fast Test Validation

Run a quick test suite for rapid feedback during development.

## Steps:

1. **Quick Unit Tests**
   ```bash
   echo "⚡ Running quick tests..."
   PYTHONPATH=. python -m pytest tests/unit/ -x --tb=short --no-cov -q
   ```

2. **Memory Engine Validation**
   ```bash
   echo "🧠 Testing memory engine..."
   TESTING=1 PYTHONPATH=. python -c "
   from src.infrastructure.memory.engines.memory_engine import MemoryEngine
   print('✅ Memory engine import successful')
   "
   ```

3. **Core Workflows Test**
   ```bash
   echo "🔄 Testing core workflows..."
   PYTHONPATH=. python -c "
   from src.core.workflows.execute_task import execute_task_with_context
   print('✅ Workflow engine import successful')
   "
   ```

4. **Agent Factory Test**
   ```bash
   echo "🤖 Testing agent factory..."
   PYTHONPATH=. python -c "
   from src.core.agents.factory import create_backend_agent
   print('✅ Agent factory import successful')
   "
   ```

5. **Critical Path Validation**
   ```bash
   echo "🛤️ Validating critical components..."
   python -m pytest tests/unit/core/ tests/unit/platform/memory/ -k "not slow" --tb=short -q
   ```

## Expected Output:
- All imports successful
- Core tests pass
- No critical failures
- Runtime < 60 seconds