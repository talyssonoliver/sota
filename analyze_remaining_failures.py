#!/usr/bin/env python3
"""
Analyze remaining import failures to create targeted fixes
"""

import sys
import importlib
from pathlib import Path

# Apply platform fix first
from platform_fix import preserve_builtin_platform
preserve_builtin_platform()

# Setup paths
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
tests_dir = root_dir / "tests"

for path in [str(root_dir), str(src_dir), str(tests_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Setup test imports
from tests.fixtures.test_imports_helper import setup_test_imports
setup_test_imports()

# List of known failing files from previous run
failing_files = [
    "tests/e2e/workflows/test_phase6_automation.py",
    "tests/e2e/workflows/test_phase7_hitl.py", 
    "tests/integration/dashboard/test_dashboard_routes.py",
    "tests/integration/dashboard/test_dashboard_stability.py",
    "tests/unit/interfaces/api/test_hitl_api_routes.py",
    "tests/unit/interfaces/dashboard/test_hitl_api_routes.py",
    "tests/unit/interfaces/dashboard/test_hitl_cli.py",
    "tests/unit/platform/tools/test_tool_loader.py"
]

def analyze_import_failure(file_path):
    """Analyze specific import failure."""
    try:
        # Build full path
        full_path = root_dir / file_path
        if not full_path.exists():
            print(f"\n❓ File not found: {file_path}")
            return False
            
        relative_path = full_path.relative_to(root_dir)
        module_name = str(relative_path).replace('/', '.').replace('\\', '.').replace('.py', '')
        
        print(f"\n🔍 Analyzing: {module_name}")
        
        # Try to import and capture the exact error
        try:
            importlib.import_module(module_name)
            print(f"  ✅ Actually imports successfully now!")
            return True
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print(f"  📄 Error type: {type(e).__name__}")
            
            # Try to get more details
            if hasattr(e, '__cause__') and e.__cause__:
                print(f"  🔗 Caused by: {e.__cause__}")
            
            return False
            
    except Exception as e:
        print(f"  💥 Analysis failed: {e}")
        return False

def main():
    print("🔬 Analyzing Remaining Import Failures")
    print("=" * 50)
    
    fixed_count = 0
    still_failing = []
    
    for file_path in failing_files:
        success = analyze_import_failure(file_path)
        if success:
            fixed_count += 1
        else:
            still_failing.append(file_path)
    
    print(f"\n📊 Analysis Summary:")
    print(f"✅ Now working: {fixed_count}/{len(failing_files)}")
    print(f"❌ Still failing: {len(still_failing)}")
    
    if still_failing:
        print(f"\n🚨 Files still failing:")
        for file_path in still_failing:
            print(f"  - {file_path}")

if __name__ == "__main__":
    main()