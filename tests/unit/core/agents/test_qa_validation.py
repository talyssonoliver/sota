import json
from pathlib import Path


def test_qa_report_exists():
    """Test that a QA report is generated and contains basic required fields."""
    qa_report_path = Path('outputs/BE-01/qa_report.json')
    assert qa_report_path.exists(), f"QA report not found: {qa_report_path}"
    with qa_report_path.open(encoding='utf-8') as f:
        data = json.load(f)
    # Check for basic fields that should exist in any QA report
    required_fields = [
        'task_id', 'timestamp', 'tests_passed', 'tests_failed',
        'status', 'message'
    ]
    for field in required_fields:
        assert field in data, f"Missing field in QA report: {field}"
    assert data['task_id'] == 'BE-01', "QA report task_id mismatch"
    # Accept valid status values
    assert data['status'] in (
        "PASS", "FAIL", "WARN", "PASSED", "FAILED", "SKIPPED"), "Invalid status in QA report"
