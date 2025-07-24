# Testing Best Practices & Cleanup Guide

## 🧹 **Test Cleanup & Isolation**

### **Problem Solved**
Previously, tests were creating hundreds of temporary directories under `runtime/temp/mock-api-key/` and other locations, leaving artifacts that polluted the project structure. This guide ensures tests are isolated and clean up properly.

## **Safe Test Writing Patterns**

### **1. Use SafeTestRunner for File Operations**

```python
from test_utils import SafeTestRunner

def test_file_operations():
    """Example of safe file operations in tests"""
    with SafeTestRunner("my_test") as runner:
        # Create temporary files - automatically cleaned up
        temp_file = runner.create_temp_file("test content", ".json")
        temp_dir = runner.create_temp_dir("test_data")
        
        # Your test logic here
        assert os.path.exists(temp_file)
        
        # No manual cleanup needed - automatic on context exit
```

### **2. Use Pytest Fixtures for Isolation**

```python
def test_with_isolation(safe_temp_dir, isolated_output_dir, clean_runtime_dirs):
    """Example using built-in cleanup fixtures"""
    
    # safe_temp_dir: Clean temporary directory
    test_file = safe_temp_dir / "test.json"
    test_file.write_text('{"test": true}')
    
    # isolated_output_dir: Isolated output directory
    output_file = isolated_output_dir / "result.txt" 
    output_file.write_text("test output")
    
    # clean_runtime_dirs: Ensures runtime dirs are clean
    # All cleanup happens automatically
```

### **3. Use Safe File Manager**

```python
def test_with_file_manager(safe_file_manager):
    """Example using safe file manager fixture"""
    
    # Create files that will be automatically cleaned up
    config_file = safe_file_manager.create_file("config.yaml", "test: true")
    data_dir = safe_file_manager.create_dir("test_data")
    
    # Create nested files
    nested_file = data_dir / "nested.json"
    nested_file.write_text('{"nested": true}')
    
    # All cleanup automatic
```

## **Available Fixtures**

### **Auto-Applied Fixtures**
- `fast_test_environment`: Mocks external services, creates isolated dirs
- `set_log_level`: Configures clean logging output
- `clean_runtime_dirs`: Ensures runtime directories are clean

### **Manual Fixtures**
- `safe_temp_dir`: Provides a clean temporary directory
- `isolated_output_dir`: Isolated output directory with env vars
- `safe_file_manager`: Context manager for safe file operations
- `mock_memory_engine`: Mock memory engine with consistent behavior

## **Cleanup Mechanisms**

### **Automatic Cleanup Locations**
The system automatically cleans up:
- `runtime/temp/mock-api-key/tmp*`
- `runtime/logs/daily_cycle/test_*`
- `runtime/logs/langgraph/test_*` 
- `test_outputs/tmp*`
- `outputs/TEST-*`
- Any files/dirs starting with `tmp`, `test_`, `mock_`

### **Manual Cleanup**
```python
from test_utils import ensure_clean_test_environment

# Call before/after test suites
ensure_clean_test_environment()
```

## **Test Organization**

### **New Directory Structure**
```
tests/
├── core/           # Core system tests (agents, main, config)
├── components/     # Component tests (memory, tools, patches)
├── workflows/      # Workflow tests (daily cycle, orchestration)
├── agents/         # Agent-specific tests (QA, documentation)
├── hitl/          # Human-in-the-loop tests
├── integration/   # Integration & end-to-end tests
├── fixtures/      # Test fixtures
├── test_data/     # Test data files
├── conftest.py    # Pytest configuration with cleanup
├── test_utils.py  # Testing utilities
└── test_environment.py  # Test environment setup
```

## **Running Tests Safely**

### **Using the Test Runner**
```bash
# Includes automatic cleanup
python tests/run_tests.py --quick    # Quick validation
python tests/run_tests.py --all      # All tests with cleanup
```

### **Direct Pytest (if available)**
```bash
# Uses conftest.py fixtures for cleanup
pytest tests/ -v
```

## **Common Patterns to Avoid**

### **❌ DON'T: Create files without cleanup**
```python
def bad_test():
    # Creates files that won't be cleaned up
    with open("temp_file.txt", "w") as f:
        f.write("test")
    os.makedirs("temp_dir", exist_ok=True)
    # No cleanup - files remain!
```

### **✅ DO: Use safe patterns**
```python  
def good_test():
    with SafeTestRunner("test_name") as runner:
        temp_file = runner.create_temp_file("test")
        temp_dir = runner.create_temp_dir()
        # Automatic cleanup on exit
```

### **❌ DON'T: Write to project directories**
```python
def bad_test():
    # Pollutes project structure
    with open("runtime/test_output.json", "w") as f:
        f.write("{}")
```

### **✅ DO: Use isolated directories** 
```python
def good_test(isolated_output_dir):
    # Uses isolated directory
    output_file = isolated_output_dir / "output.json"
    output_file.write_text("{}")
```

## **Debugging Test Cleanup**

### **Check for Leaked Files**
```bash
# Find temp files that may have leaked
find . -name "tmp*" -not -path "./.venv/*"
find . -name "test_*" -not -path "./tests/*" -not -path "./.venv/*"
find . -name "mock_*" -not -path "./.venv/*"
```

### **Monitor Runtime Directories**
```bash
# Check for temporary artifacts
ls -la runtime/temp/
ls -la runtime/logs/daily_cycle/
ls -la runtime/logs/langgraph/
```

### **Manual Cleanup**
```bash
# Clean up manually if needed
rm -rf runtime/temp/mock-api-key/tmp*
rm -rf runtime/logs/*/test_*
rm -rf test_outputs/tmp*
```

## **Integration with CI/CD**

### **Pre-test Cleanup**
```bash
# In CI scripts, clean environment first
python -c "from tests.test_utils import ensure_clean_test_environment; ensure_clean_test_environment()"
```

### **Post-test Verification**
```bash
# Verify no artifacts remain
if find . -name "tmp*" -not -path "./.venv/*" | grep -q .; then
  echo "❌ Test artifacts found - tests not cleaning up properly"
  exit 1
else
  echo "✅ No test artifacts found"
fi
```

## **Summary**

✅ **Always use** safe test patterns with automatic cleanup  
✅ **Leverage fixtures** for isolation and automatic teardown  
✅ **Test in isolated directories** to prevent pollution  
✅ **Clean before and after** test runs  
✅ **Monitor for artifacts** and fix leaky tests immediately  

This ensures a clean, maintainable test suite that doesn't pollute the project structure! 🎯