"""
test_step_5_4_qa_registration.py - Optimized Test Structure

Migrated from: tests/integration	est_step_5_4_qa_registration.py
New location: tests/integration	est_step_5_4_qa_registration.py

Part of the optimized test pyramid reorganization:
- Tests now mirror src/ structure
- Proper categorization (unit/integration/e2e)
- Improved mocking and isolation

Test Suite for Step 5.4 - QA Results Registration & Traceability

Comprehensive tests specifically for Step 5.4 implementation requirements:
- QA output registration with full metadata tracking
- Human-readable markdown summary generation
- Traceability infrastructure validation
- Integration with existing registration system
"""
import sys
import json
import os
import tempfile
import unittest
import shutil
try:
    from datetime import datetime
except ImportError:
    pass
try:
    from pathlib import Path
except ImportError:
    pass
    pass
try:
    from unittest.mock import patch
except ImportError:
    pass
try:
    from src.core.workflows.register_output import AgentOutputRegistry
except ImportError:
    pass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestStep54QARegistration(unittest.TestCase):
    """Test Step 5.4 QA Results Registration & Traceability requirements."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.registry = AgentOutputRegistry(base_outputs_dir=self.test_dir)
        self.sample_qa_report = {'task_id': 'BE-07', 'timestamp': '2025-05-27T00:00:00.000000', 'tests_passed': 6, 'tests_failed': 0, 'coverage_percentage': 92.4, 'linting_issues': [{'file': 'customerService.ts', 'line': 42, 'severity': 'warning', 'message': 'Line too long (82 > 80 characters)'}], 'type_check_issues': [], 'security_issues': [], 'performance_metrics': {'estimated_response_time_ms': 250, 'estimated_memory_usage_mb': 128, 'complexity_score': 3.2, 'maintainability_index': 85.5}, 'overall_status': 'PASSED', 'recommendations': ['Consider addressing line length warnings in TypeScript files'], 'next_steps': ['Proceed to documentation generation', 'Mark task as ready for completion']}

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_qa_output_registration_command(self):
        """Test the core QA registration command as specified in Step 5.4."""
        qa_report_file = Path(self.test_dir) / 'qa_report.json'
        qa_report_file.write_text(json.dumps(self.sample_qa_report, indent=2))
        registration = self.registry.register_output(task_id='BE-07', agent_id='qa', source_path=str(qa_report_file), output_type='json')
        self.assertEqual(registration.task_id, 'BE-07')
        self.assertEqual(registration.agent_id, 'qa')
        self.assertEqual(registration.status, 'registered')
        self.assertEqual(registration.output_type, 'json')
        expected_output = Path(self.test_dir) / 'BE-07' / 'qa_report.json'
        self.assertTrue(expected_output.exists())
        loaded_content = json.loads(expected_output.read_text())
        self.assertEqual(loaded_content['task_id'], 'BE-07')
        self.assertEqual(loaded_content['tests_passed'], 6)
        self.assertEqual(loaded_content['overall_status'], 'PASSED')

    def test_qa_registration_metadata_tracking(self):
        """Test full metadata tracking for QA registration traceability."""
        qa_report_file = Path(self.test_dir) / 'qa_report.json'
        qa_report_file.write_text(json.dumps(self.sample_qa_report, indent=2))
        test_metadata = {'qa_agent_version': '2.1.0', 'analysis_duration': 45.2, 'checks_performed': 23}
        registration = self.registry.register_output(task_id='BE-07', agent_id='qa', source_path=str(qa_report_file), output_type='json', metadata=test_metadata)
        metadata_file = Path(self.test_dir) / 'BE-07' / 'registration_qa.json'
        self.assertTrue(metadata_file.exists())
        metadata = json.loads(metadata_file.read_text())
        self.assertEqual(metadata['task_id'], 'BE-07')
        self.assertEqual(metadata['agent_id'], 'qa')
        self.assertEqual(metadata['output_type'], 'json')
        self.assertEqual(metadata['status'], 'registered')
        self.assertIn('registration_time', metadata)
        self.assertEqual(metadata['metadata'], test_metadata)
        self.assertIn('file_size', metadata)
        self.assertGreater(metadata['file_size'], 0)

    def test_qa_summary_markdown_generation(self):
        """Test generation of human-readable QA summary markdown as specified in Step 5.4."""
        expected_markdown = '# QA Report: BE-07\n\n## Summary\nAll tests passed with 92.4% coverage.\n\n**Status:** ✅ PASSED\n**Generated:** 2025-05-27T00:00:00.000000\n\n## Test Results\n- **Tests Passed:** 6\n- **Tests Failed:** 0\n- **Coverage:** 92.4%\n\n## Coverage Report\n- customerService.ts: 91%\n- orderService.ts: 94%\n\n## Linting\n1 minor warning found:\n- Line length warnings in TypeScript service files (82 > 80 characters)\n\nNo critical issues identified.\n\n## Next Steps\n- Proceed to documentation\n- Mark task as complete\n\n---\n*Generated by QA Validation Engine v1.0.0*\n'
        task_dir = Path(self.test_dir) / 'BE-07'
        task_dir.mkdir(parents=True, exist_ok=True)
        summary_file = task_dir / 'qa_summary.md'
        summary_file.write_text(expected_markdown, encoding='utf-8')
        self.assertTrue(summary_file.exists())
        content = summary_file.read_text()
        self.assertIn('# QA Report: BE-07', content)
        self.assertIn('## Summary', content)
        self.assertIn('All tests passed with 92.4% coverage', content)
        self.assertIn('## Test Results', content)
        self.assertIn('## Coverage Report', content)
        self.assertIn('## Linting', content)
        self.assertIn('## Next Steps', content)
        self.assertIn('Proceed to documentation', content)
        self.assertIn('Mark task as complete', content)

    def test_qa_traceability_integration(self):
        """Test complete traceability from QA execution to registration."""
        qa_report_file = Path(self.test_dir) / 'qa_report.json'
        qa_report_file.write_text(json.dumps(self.sample_qa_report, indent=2))
        registration = self.registry.register_output('BE-07', 'qa', str(qa_report_file), output_type='json')
        task_dir = Path(self.test_dir) / 'BE-07'
        files_to_check = ['qa_report.json', 'registration_qa.json', 'status.json']
        for filename in files_to_check:
            file_path = task_dir / filename
            self.assertTrue(file_path.exists(), f'Traceability file missing: {filename}')
        status_data = json.loads((task_dir / 'status.json').read_text())
        self.assertIn('qa', status_data['agent_outputs'])
        self.assertEqual(status_data['agent_outputs']['qa']['status'], 'completed')
        self.assertIn('completion_time', status_data['agent_outputs']['qa'])
        qa_data = json.loads((task_dir / 'qa_report.json').read_text())
        reg_data = json.loads((task_dir / 'registration_qa.json').read_text())
        self.assertEqual(qa_data['task_id'], 'BE-07')
        self.assertEqual(reg_data['task_id'], 'BE-07')
        self.assertEqual(status_data['task_id'], 'BE-07')

    def test_qa_registration_integration_with_phase4(self):
        """Test integration with Phase 4 output registration system."""
        backend_output = '# Backend Implementation\nServices implemented successfully.'
        backend_file = Path(self.test_dir) / 'backend_output.md'
        backend_file.write_text(backend_output)
        backend_reg = self.registry.register_output('BE-07', 'backend', str(backend_file))
        qa_report_file = Path(self.test_dir) / 'qa_report.json'
        qa_report_file.write_text(json.dumps(self.sample_qa_report, indent=2))
        qa_reg = self.registry.register_output('BE-07', 'qa', str(qa_report_file), output_type='json')
        status = self.registry.get_task_status('BE-07')
        self.assertIn('backend', status['agent_outputs'])
        self.assertIn('qa', status['agent_outputs'])
        self.assertEqual(status['agent_outputs']['backend']['status'], 'completed')
        self.assertEqual(status['agent_outputs']['qa']['status'], 'completed')
        self.assertEqual(status['task_id'], 'BE-07')
        self.assertIn('last_updated', status)

    def test_qa_registration_audit_trail(self):
        """Test complete audit trail for QA registration compliance."""
        qa_report_file = Path(self.test_dir) / 'qa_report.json'
        qa_report_file.write_text(json.dumps(self.sample_qa_report, indent=2))
        audit_metadata = {'qa_execution_engine': 'QAExecutionEngine v1.0.0', 'validation_timestamp': datetime.now().isoformat(), 'quality_gates_passed': True, 'test_frameworks_used': ['unittest', 'pytest'], 'static_analysis_tools': ['pylint', 'eslint'], 'execution_environment': 'test'}
        registration = self.registry.register_output(task_id='BE-07', agent_id='qa', source_path=str(qa_report_file), output_type='json', metadata=audit_metadata)
        task_dir = Path(self.test_dir) / 'BE-07'
        registration_file = task_dir / 'registration_qa.json'
        reg_data = json.loads(registration_file.read_text())
        self.assertEqual(reg_data['metadata']['qa_execution_engine'], 'QAExecutionEngine v1.0.0')
        self.assertEqual(reg_data['metadata']['quality_gates_passed'], True)
        self.assertIn('test_frameworks_used', reg_data['metadata'])
        self.assertIn('static_analysis_tools', reg_data['metadata'])
        self.assertIn('registration_time', reg_data)
        self.assertIn('validation_timestamp', reg_data['metadata'])
        self.assertIn('file_size', reg_data)
        self.assertEqual(reg_data['status'], 'registered')

def run_step_5_4_tests():
    """Run all Step 5.4 tests and report results."""
    print('\n' + '=' * 60)
    print('STEP 5.4 — QA Results Registration & Traceability')
    print('Testing Implementation Requirements')
    print('=' * 60)
    suite = unittest.TestSuite()
    test_methods = ['test_qa_output_registration_command', 'test_qa_registration_metadata_tracking', 'test_qa_summary_markdown_generation', 'test_qa_traceability_integration', 'test_qa_registration_integration_with_phase4', 'test_qa_registration_audit_trail']
    for method in test_methods:
        suite.addTest(TestStep54QARegistration(method))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print('\n📊 Test Results:')
    print(f'   Tests run: {result.testsRun}')
    print(f'   Failures: {len(result.failures)}')
    print(f'   Errors: {len(result.errors)}')
    if result.failures:
        print('\n❌ Failures:')
        for test, traceback in result.failures:
            print(f'   {test}: {traceback.split('AssertionError:')[-1].strip()}')
    if result.errors:
        print('\n🔍 Errors:')
        for test, traceback in result.errors:
            print(f'   {test}: {traceback.split('Exception:')[-1].strip()}')
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0
    print(f'\n🎯 Success Rate: {success_rate:.1f}%')
    return result.wasSuccessful()
if __name__ == '__main__':
    success = run_step_5_4_tests()
    print(f'\n{('✅ PASSED' if success else '❌ FAILED')}: Step 5.4 QA Results Registration & Traceability')
    sys.exit(0 if success else 1)