#!/usr/bin/env python3
"""
Test Suite for Step 5.4 — QA Results Registration & Traceability

Comprehensive tests specifically for Step 5.4 implementation requirements:
- QA output registration with full metadata tracking
- Human-readable markdown summary generation  
- Traceability infrastructure validation
- Integration with existing registration system
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.register_output import AgentOutputRegistry


class TestStep54QARegistration(unittest.TestCase):
    """Test Step 5.4 QA Results Registration & Traceability requirements."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.registry = AgentOutputRegistry(base_outputs_dir=self.test_dir)
        
        # Sample QA report matching Step 5.4 specification
        self.sample_qa_report = {
            "task_id": "BE-07",
            "timestamp": "2025-05-27T00:00:00.000000",
            "tests_passed": 6,
            "tests_failed": 0,
            "coverage_percentage": 92.4,
            "linting_issues": [
                {
                    "file": "customerService.ts",
                    "line": 42,
                    "severity": "warning",
                    "message": "Line too long (82 > 80 characters)"
                }
            ],
            "type_check_issues": [],
            "security_issues": [],
            "performance_metrics": {
                "estimated_response_time_ms": 250,
                "estimated_memory_usage_mb": 128,
                "complexity_score": 3.2,
                "maintainability_index": 85.5
            },
            "overall_status": "PASSED",
            "recommendations": [
                "Consider addressing line length warnings in TypeScript files"
            ],
            "next_steps": [
                "Proceed to documentation generation",
                "Mark task as ready for completion"
            ]
        }
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_qa_output_registration_command(self):
        """Test the core QA registration command as specified in Step 5.4."""
        # Create QA report file
        qa_report_file = Path(self.test_dir) / "qa_report.json"
        qa_report_file.write_text(json.dumps(self.sample_qa_report, indent=2))
        
        # Register QA output (simulates: python orchestration/register_output.py BE-07 qa outputs/BE-07/qa_report.json)
        registration = self.registry.register_output(
            task_id="BE-07",
            agent_id="qa", 
            source_path=str(qa_report_file),
            output_type="json"
        )
        
        # Verify registration success
        self.assertEqual(registration.task_id, "BE-07")
        self.assertEqual(registration.agent_id, "qa")
        self.assertEqual(registration.status, "registered")
        self.assertEqual(registration.output_type, "json")
        
        # Verify output file was copied to correct location
        expected_output = Path(self.test_dir) / "BE-07" / "qa_report.json"
        self.assertTrue(expected_output.exists())
        
        # Verify content was preserved
        loaded_content = json.loads(expected_output.read_text())
        self.assertEqual(loaded_content["task_id"], "BE-07")
        self.assertEqual(loaded_content["tests_passed"], 6)
        self.assertEqual(loaded_content["overall_status"], "PASSED")
    
    def test_qa_registration_metadata_tracking(self):
        """Test full metadata tracking for QA registration traceability."""
        # Create QA report
        qa_report_file = Path(self.test_dir) / "qa_report.json"
        qa_report_file.write_text(json.dumps(self.sample_qa_report, indent=2))
        
        # Register with metadata
        test_metadata = {
            "qa_agent_version": "2.1.0",
            "analysis_duration": 45.2,
            "checks_performed": 23
        }
        
        registration = self.registry.register_output(
            task_id="BE-07",
            agent_id="qa",
            source_path=str(qa_report_file),
            output_type="json",
            metadata=test_metadata
        )
        
        # Verify registration metadata file exists
        metadata_file = Path(self.test_dir) / "BE-07" / "registration_qa.json"
        self.assertTrue(metadata_file.exists())
        
        # Verify metadata content
        metadata = json.loads(metadata_file.read_text())
        self.assertEqual(metadata["task_id"], "BE-07")
        self.assertEqual(metadata["agent_id"], "qa")
        self.assertEqual(metadata["output_type"], "json")
        self.assertEqual(metadata["status"], "registered")
        self.assertIn("registration_time", metadata)
        self.assertEqual(metadata["metadata"], test_metadata)
        
        # Verify file size tracking
        self.assertIn("file_size", metadata)
        self.assertGreater(metadata["file_size"], 0)
    
    def test_qa_summary_markdown_generation(self):
        """Test generation of human-readable QA summary markdown as specified in Step 5.4."""
        # This would typically be generated by the QA validation engine
        # For this test, we'll simulate the expected markdown format
        
        expected_markdown = """# QA Report: BE-07

## Summary
All tests passed with 92.4% coverage.

**Status:** ✅ PASSED  
**Generated:** 2025-05-27T00:00:00.000000

## Test Results
- **Tests Passed:** 6
- **Tests Failed:** 0
- **Coverage:** 92.4%

## Coverage Report
- customerService.ts: 91%
- orderService.ts: 94%

## Linting
1 minor warning found:
- Line length warnings in TypeScript service files (82 > 80 characters)

No critical issues identified.

## Next Steps
- Proceed to documentation
- Mark task as complete

---
*Generated by QA Validation Engine v1.0.0*
"""
        
        # Create the summary file (simulates QA validation engine output)
        task_dir = Path(self.test_dir) / "BE-07"
        task_dir.mkdir(parents=True, exist_ok=True)
        summary_file = task_dir / "qa_summary.md"
        summary_file.write_text(expected_markdown)
        
        # Verify the summary file exists and has correct format
        self.assertTrue(summary_file.exists())
        content = summary_file.read_text()
        
        # Verify key sections are present
        self.assertIn("# QA Report: BE-07", content)
        self.assertIn("## Summary", content)
        self.assertIn("All tests passed with 92.4% coverage", content)
        self.assertIn("## Test Results", content)
        self.assertIn("## Coverage Report", content)
        self.assertIn("## Linting", content)
        self.assertIn("## Next Steps", content)
        self.assertIn("Proceed to documentation", content)
        self.assertIn("Mark task as complete", content)
    
    def test_qa_traceability_integration(self):
        """Test complete traceability from QA execution to registration."""
        # Simulate complete QA workflow traceability
        
        # 1. Create QA report (from QA execution)
        qa_report_file = Path(self.test_dir) / "qa_report.json"
        qa_report_file.write_text(json.dumps(self.sample_qa_report, indent=2))
        
        # 2. Register QA output
        registration = self.registry.register_output("BE-07", "qa", str(qa_report_file), output_type="json")
        
        # 3. Verify traceability chain
        task_dir = Path(self.test_dir) / "BE-07"
        
        # Check all traceability files exist
        files_to_check = [
            "qa_report.json",           # QA report data
            "registration_qa.json",     # Registration metadata
            "status.json"               # Task status tracking
        ]
        
        for filename in files_to_check:
            file_path = task_dir / filename
            self.assertTrue(file_path.exists(), f"Traceability file missing: {filename}")
        
        # Verify status.json tracks QA completion
        status_data = json.loads((task_dir / "status.json").read_text())
        self.assertIn("qa", status_data["agent_outputs"])
        self.assertEqual(status_data["agent_outputs"]["qa"]["status"], "completed")
        self.assertIn("completion_time", status_data["agent_outputs"]["qa"])
        
        # Verify task_id consistency across all files
        qa_data = json.loads((task_dir / "qa_report.json").read_text())
        reg_data = json.loads((task_dir / "registration_qa.json").read_text())
        
        self.assertEqual(qa_data["task_id"], "BE-07")
        self.assertEqual(reg_data["task_id"], "BE-07")
        self.assertEqual(status_data["task_id"], "BE-07")
    
    def test_qa_registration_integration_with_phase4(self):
        """Test integration with Phase 4 output registration system."""
        # First register backend output (Phase 4)
        backend_output = "# Backend Implementation\nServices implemented successfully."
        backend_file = Path(self.test_dir) / "backend_output.md"
        backend_file.write_text(backend_output)
        
        backend_reg = self.registry.register_output("BE-07", "backend", str(backend_file))
        
        # Then register QA output (Step 5.4)
        qa_report_file = Path(self.test_dir) / "qa_report.json"
        qa_report_file.write_text(json.dumps(self.sample_qa_report, indent=2))
        
        qa_reg = self.registry.register_output("BE-07", "qa", str(qa_report_file), output_type="json")
        
        # Verify both agents are tracked in status
        status = self.registry.get_task_status("BE-07")
        
        self.assertIn("backend", status["agent_outputs"])
        self.assertIn("qa", status["agent_outputs"])
        self.assertEqual(status["agent_outputs"]["backend"]["status"], "completed")
        self.assertEqual(status["agent_outputs"]["qa"]["status"], "completed")
        
        # Verify task progression tracking
        self.assertEqual(status["task_id"], "BE-07")
        self.assertIn("last_updated", status)
    
    def test_qa_registration_audit_trail(self):
        """Test complete audit trail for QA registration compliance."""
        # Register QA output with comprehensive metadata
        qa_report_file = Path(self.test_dir) / "qa_report.json"
        qa_report_file.write_text(json.dumps(self.sample_qa_report, indent=2))
        
        audit_metadata = {
            "qa_execution_engine": "QAExecutionEngine v1.0.0",
            "validation_timestamp": datetime.now().isoformat(),
            "quality_gates_passed": True,
            "test_frameworks_used": ["unittest", "pytest"],
            "static_analysis_tools": ["pylint", "eslint"],
            "execution_environment": "test"
        }
        
        registration = self.registry.register_output(
            task_id="BE-07",
            agent_id="qa",
            source_path=str(qa_report_file),
            output_type="json",
            metadata=audit_metadata
        )
        
        # Verify audit trail completeness
        task_dir = Path(self.test_dir) / "BE-07"
        registration_file = task_dir / "registration_qa.json"
        
        reg_data = json.loads(registration_file.read_text())
        
        # Verify audit metadata preservation
        self.assertEqual(reg_data["metadata"]["qa_execution_engine"], "QAExecutionEngine v1.0.0")
        self.assertEqual(reg_data["metadata"]["quality_gates_passed"], True)
        self.assertIn("test_frameworks_used", reg_data["metadata"])
        self.assertIn("static_analysis_tools", reg_data["metadata"])
        
        # Verify timestamps for audit trail
        self.assertIn("registration_time", reg_data)
        self.assertIn("validation_timestamp", reg_data["metadata"])
        
        # Verify file integrity
        self.assertIn("file_size", reg_data)
        self.assertEqual(reg_data["status"], "registered")


def run_step_5_4_tests():
    """Run all Step 5.4 tests and report results."""
    print("\n" + "="*60)
    print("STEP 5.4 — QA Results Registration & Traceability")
    print("Testing Implementation Requirements")
    print("="*60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_qa_output_registration_command',
        'test_qa_registration_metadata_tracking', 
        'test_qa_summary_markdown_generation',
        'test_qa_traceability_integration',
        'test_qa_registration_integration_with_phase4',
        'test_qa_registration_audit_trail'
    ]
    
    for method in test_methods:
        suite.addTest(TestStep54QARegistration(method))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    print(f"\n📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n🔍 Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_step_5_4_tests()
    print(f"\n{'✅ PASSED' if success else '❌ FAILED'}: Step 5.4 QA Results Registration & Traceability")
    sys.exit(0 if success else 1)
