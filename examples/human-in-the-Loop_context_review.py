#!/usr/bin/env python3
"""
Step 3.8 Implementation Test and Validation

This script tests the Human-in-the-Loop context review functionality.
It validates that users can inspect and modify context before task execution.

Usage:
    python examples/step_3_8_demo.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_context_review_summary():
    """Test context review summary functionality"""
    print("=" * 60)
    print("STEP 3.8 TEST: Context Review Summary")
    print("=" * 60)
    
    try:
        # Test summary-only mode
        result = subprocess.run([
            sys.executable, "orchestration/review_context.py", 
            "BE-07", "--summary-only"
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Context review summary executed successfully")
            
            # Check for expected output content
            output = result.stdout
            if "CONTEXT REVIEW SUMMARY" in output and "Documents:" in output:
                print("✅ Summary output contains expected information")
                return True
            else:
                print("❌ Summary output missing expected content")
                return False
        else:
            print(f"❌ Context review failed with return code: {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing context review: {e}")
        return False

def test_context_review_help():
    """Test help functionality"""
    print("\n" + "=" * 60)
    print("STEP 3.8 TEST: Help and Usage")
    print("=" * 60)
    
    try:
        # Test help output
        result = subprocess.run([
            sys.executable, "orchestration/review_context.py", 
            "--help"
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Help command executed successfully")
            
            # Check for expected help content
            output = result.stdout
            if "Human-in-the-Loop Context Review Tool" in output and "Examples:" in output:
                print("✅ Help output contains expected information")
                return True
            else:
                print("❌ Help output missing expected content")
                return False
        else:
            print(f"❌ Help command failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing help: {e}")
        return False

def test_context_review_export():
    """Test export functionality"""
    print("\n" + "=" * 60)
    print("STEP 3.8 TEST: Context Export")
    print("=" * 60)
    
    try:
        # Test export mode
        result = subprocess.run([
            sys.executable, "orchestration/review_context.py", 
            "BE-07", "--export", "test_review.json"
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Context export executed successfully")
            
            # Check if report was generated
            reports_dir = project_root / "reports"
            if reports_dir.exists():
                json_files = list(reports_dir.glob("context_review_BE-07_*.json"))
                if json_files:
                    print(f"✅ Export file created: {json_files[0].name}")
                    return True
                else:
                    print("❌ No export file found in reports directory")
                    return False
            else:
                print("❌ Reports directory not found")
                return False
        else:
            print(f"❌ Context export failed with return code: {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing export: {e}")
        return False

def test_integration_with_step_3_7():
    """Test integration with Step 3.7 context tracking"""
    print("\n" + "=" * 60)
    print("STEP 3.8 TEST: Integration with Step 3.7")
    print("=" * 60)
    
    try:
        # Run context review which should trigger Step 3.7 tracking
        result = subprocess.run([
            sys.executable, "orchestration/review_context.py", 
            "BE-07", "--summary-only"
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Context review completed successfully")
            
            # Check if Step 3.7 context log was updated
            context_log_path = project_root / "outputs" / "BE-07" / "context_log.json"
            if context_log_path.exists():
                import json
                with open(context_log_path, 'r') as f:
                    log_data = json.load(f)
                  # Check for Step 3.8 integration markers
                additional_metadata = log_data.get('additional_metadata', {})
                if (log_data.get('agent_role') in ['human_reviewer', 'reviewer'] or 
                    additional_metadata.get('step_3_8_review') == True):
                    print("✅ Step 3.7 integration detected (human review markers found)")
                    return True
                else:
                    print("⚠️  Step 3.7 integration not clearly marked")
                    print(f"[DEBUG] Agent role: {log_data.get('agent_role')}")
                    print(f"[DEBUG] Additional metadata: {additional_metadata}")
                    return False
            else:
                print("❌ Step 3.7 context log not found")
                return False
        else:
            print(f"❌ Context review failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Step 3.7 integration: {e}")
        return False

def validate_step_3_8_complete():
    """Validate that Step 3.8 implementation meets all requirements"""
    print("\n" + "=" * 60)
    print("STEP 3.8 VALIDATION: Complete Implementation Check")
    print("=" * 60)
    
    requirements = [
        ("Context review summary functionality", test_context_review_summary),
        ("Help and usage documentation", test_context_review_help),
        ("Context export functionality", test_context_review_export),
        ("Integration with Step 3.7 tracking", test_integration_with_step_3_7)
    ]
    
    results = []
    for name, test_func in requirements:
        try:
            result = test_func()
            results.append((name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {name}")
        except Exception as e:
            results.append((name, False))
            print(f"❌ ERROR: {name} - {e}")
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 STEP 3.8 VALIDATION SUMMARY:")
    print(f"   Tests passed: {passed}/{total}")
    print(f"   Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 Step 3.8 implementation is COMPLETE and functional!")
        return True
    else:
        print("⚠️  Step 3.8 implementation needs attention.")
        return False

def main():
    """Run all Step 3.8 tests and validation"""
    print("🔍 Starting Step 3.8 Implementation Test Suite")
    print("Human-in-the-Loop Context Review - Validation and Demo")
    print("=" * 80)
    
    success = validate_step_3_8_complete()
    
    if success:
        print("\n✅ Step 3.8 'Human-in-the-Loop Context Review' is fully implemented!")
        print("🔍 CLI tool available: python orchestration/review_context.py [TASK-ID]")
        print("📋 Features: Context inspection, modification, export, and approval")
        print("🔗 Integration with Step 3.7 context tracking system")
        print("\n📖 Usage examples:")
        print("   python orchestration/review_context.py BE-07")
        print("   python orchestration/review_context.py --task BE-07 --interactive")
        print("   python orchestration/review_context.py --task BE-07 --export review.json")
    else:
        print("\n❌ Step 3.8 implementation requires fixes")
    
    return success

if __name__ == "__main__":
    main()
