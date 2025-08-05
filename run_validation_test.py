#!/usr/bin/env python3
"""Quick validation test for v3.0 system"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def quick_validation_test():
    """Quick test of validation v3.0 system"""
    print("🚀 Quick Validation System v3.0 Test")
    print("=" * 40)
    
    # Test 1: Import main validator
    try:
        from src.infrastructure.tools.validation.core.validator import Validator
        print("✅ Main Validator import: OK")
    except ImportError as e:
        print(f"❌ Main Validator import failed: {e}")
        return False
    
    # Test 2: Check version
    try:
        from src.infrastructure.tools.validation import __version__
        print(f"✅ Version: {__version__}")
        if __version__ == "3.0.0":
            print("✅ Version correct")
        else:
            print(f"❌ Expected version 3.0.0, got {__version__}")
    except ImportError as e:
        print(f"❌ Version import failed: {e}")
    
    # Test 3: Create validator instance
    try:
        validator = Validator(root_path=project_root)
        print("✅ Validator instance created")
        
        # Check key attributes
        if hasattr(validator, 'run_validation'):
            print("✅ run_validation method exists")
        else:
            print("❌ run_validation method missing")
            
    except Exception as e:
        print(f"❌ Validator creation failed: {e}")
        return False
    
    # Test 4: Check CLI
    try:
        from src.infrastructure.tools.validation.core.validation_cli import ValidationCLI
        cli = ValidationCLI()
        print("✅ CLI creation: OK")
    except Exception as e:
        print(f"❌ CLI creation failed: {e}")
        return False
    
    print("\n🎉 Basic validation tests passed!")
    return True

if __name__ == "__main__":
    success = quick_validation_test()
    sys.exit(0 if success else 1)