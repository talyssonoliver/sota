import os
from pathlib import Path

def test_documentation_report_exists():
    """Test that the documentation report for BE-07 is generated and non-empty."""
    report_path = Path('docs/completions/BE-07.md')
    assert report_path.exists(), f"Report not found: {report_path}"
    content = report_path.read_text(encoding='utf-8')
    assert '# Task Completion Report:' in content or '# Task Completion Summary:' in content
    assert 'Artifacts Generated' in content or 'Generated Artifacts' in content
    assert 'QA Validation' in content or 'Quality Assurance Results' in content
    assert 'Next Steps' in content or 'Recommended Next Steps' in content
