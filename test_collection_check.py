#!/usr/bin/env python3
"""
Test Collection Verification Script

Verifies that test files can be imported successfully, which is the
critical requirement for pytest collection to work.
"""

import sys
import traceback
from pathlib import Path

# CRITICAL: Fix platform module before any path manipulation
try:
    from platform_fix import preserve_builtin_platform
    preserve_builtin_platform()
    print("✅ Platform module fix applied successfully")
except ImportError:
    # Fallback: do it manually
    original_paths = sys.path.copy()
    import os
    src_paths = [p for p in sys.path if 'src' in p.split(os.sep)]
    for path in src_paths:
        if path in sys.path:
            sys.path.remove(path)
    
    import platform as builtin_platform
    sys.path = original_paths
    sys.modules['builtin_platform'] = builtin_platform
    sys.modules['platform'] = builtin_platform
    print("✅ Platform module fix applied via fallback")

# Setup paths
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
tests_dir = root_dir / "tests"

for path in [str(root_dir), str(src_dir), str(tests_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Setup test imports
try:
    from tests.fixtures.test_imports_helper import setup_test_imports
    setup_test_imports()
    print("✅ Test import helper loaded successfully")
except ImportError as e:
    print(f"❌ Could not load test import helper: {e}")

def test_file_imports():
    """Test that critical test files can be imported."""
    test_files = [
        'tests.components.test_generator',
        'tests.utils.test_utils',
        'tests.utils.workflow_helpers',
        'tests.unit.core.test_agents', 
        'tests.unit.interfaces.api.test_hitl_api_routes',
        'tests.unit.platform.memory.test_memory_engine',
        'tests.integration.dashboard.test_dashboard_integration',
        'tests.e2e.workflows.test_phase6_automation',
    ]
    
    results = {'success': 0, 'failed': 0, 'errors': []}
    
    for test_module in test_files:
        try:
            __import__(test_module)
            print(f"✅ {test_module}")
            results['success'] += 1
        except Exception as e:
            print(f"❌ {test_module}: {e}")
            results['failed'] += 1
            results['errors'].append((test_module, str(e)))
    
    return results

def test_src_imports():
    """Test that critical src modules can be imported."""
    src_modules = [
        'src.core.agents.backend',
        'src.core.agents.qa',
        'src.interfaces.api.hitl_routes',
        'src.platform.memory',
    ]
    
    results = {'success': 0, 'failed': 0, 'errors': []}
    
    for src_module in src_modules:
        try:
            __import__(src_module)
            print(f"✅ {src_module}")
            results['success'] += 1
        except Exception as e:
            print(f"❌ {src_module}: {e}")
            results['failed'] += 1
            results['errors'].append((src_module, str(e)))
    
    return results

def main():
    """Main test function."""
    print("=" * 60)
    print("🔍 Testing Source Module Imports")
    print("=" * 60)
    
    src_results = test_src_imports()
    
    print("\n" + "=" * 60)
    print("🧪 Testing Test Module Imports")  
    print("=" * 60)
    
    test_results = test_file_imports()
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    total_src = src_results['success'] + src_results['failed']
    total_test = test_results['success'] + test_results['failed']
    
    print(f"Source modules: {src_results['success']}/{total_src} successful")
    print(f"Test modules: {test_results['success']}/{total_test} successful")
    
    if src_results['errors'] or test_results['errors']:
        print(f"\n🔴 Critical Errors:")
        for module, error in src_results['errors'] + test_results['errors']:
            print(f"  {module}: {error}")
    
    if src_results['failed'] == 0 and test_results['failed'] == 0:
        print(f"\n✅ All imports working! Test collection should succeed.")
        return True
    else:
        print(f"\n❌ {src_results['failed'] + test_results['failed']} modules have import issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)