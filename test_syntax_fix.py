#!/usr/bin/env python3
"""
Quick test to verify syntax validator fix logic.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.infrastructure.tools.validation.core.syntax_validator import SyntaxValidator

def test_syntax_validator_fix():
    """Test that syntax validator no longer fails on optional dependencies."""
    print("🧪 Testing Syntax Validator Fix...")
    
    validator = SyntaxValidator(project_root)
    
    # Test cases that should now pass
    test_cases = [
        ("langchain", "Should pass - optional dependency"),
        ("openai", "Should pass - optional dependency"),  
        ("torch", "Should pass - optional dependency"),
        ("numpy", "Should pass - standard library"),
        ("src.core.agents", "Should pass - local import"),
        (".relative_import", "Should pass - relative import"),
        ("", "Should FAIL - empty import"),
        ("invalid/path", "Should FAIL - invalid characters"),
    ]
    
    passed = 0
    failed = 0
    
    for import_name, description in test_cases:
        result = validator.validate_import(import_name, Path("test_file.py"))
        expected_pass = "FAIL" not in description
        
        if result == expected_pass:
            print(f"  ✅ {import_name:20} - {description}")
            passed += 1
        else:
            print(f"  ❌ {import_name:20} - {description} (got {result}, expected {expected_pass})")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Syntax validator fix should work correctly.")
        return True
    else:
        print("⚠️  Some tests failed. The fix may need adjustment.")
        return False

if __name__ == "__main__":
    test_syntax_validator_fix()