import os
from pathlib import Path
import json

def test_qa_report_exists():
    """Test that the QA report for BE-07 is generated and contains required fields."""
    qa_report_path = Path('outputs/BE-07/qa_report.json')
    assert qa_report_path.exists(), f"QA report not found: {qa_report_path}"
    with qa_report_path.open(encoding='utf-8') as f:
        data = json.load(f)
    # Check for required fields in the QA report
    required_fields = [
        'task_id', 'timestamp', 'tests_passed', 'tests_failed',
        'coverage_percentage', 'linting_issues', 'type_check_issues',
        'security_issues', 'performance_metrics', 'overall_status',
        'recommendations', 'next_steps'
    ]
    for field in required_fields:
        assert field in data, f"Missing field in QA report: {field}"
    assert data['task_id'] == 'BE-07', "QA report task_id mismatch"
    # Accept both 'PASSED' and legacy values for overall_status
    assert data['overall_status'] in ("PASS", "FAIL", "WARN", "PASSED", "FAILED"), "Invalid overall_status in QA report"
