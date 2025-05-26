import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from orchestration.documentation_agent import DocumentationAgent, DocumentationReport, TaskSummary, QASummary, TaskArtifact

def test_documentation_report_exists():
    """Test that the documentation report for BE-07 is generated and non-empty."""
    report_path = Path('docs/completions/BE-07.md')
    assert report_path.exists(), f"Report not found: {report_path}"
    content = report_path.read_text(encoding='utf-8')
    assert '# Task Completion Report:' in content or '# Task Completion Summary:' in content
    assert 'Artifacts Generated' in content or 'Generated Artifacts' in content
    assert 'QA Validation' in content or 'Quality Assurance Results' in content
    assert 'Next Steps' in content or 'Recommended Next Steps' in content

def test_documentation_report_structure():
    """Test that the documentation report has the correct structure."""
    report_path = Path('docs/completions/BE-07.md')
    assert report_path.exists(), f"Report not found: {report_path}"
    content = report_path.read_text(encoding='utf-8')
    
    # Check required sections
    required_sections = [
        "## Summary",
        "## QA Validation",
        "## Implementation Summary",
        "## Artifacts Generated",
        "## Next Steps",
        "## References"
    ]
    
    for section in required_sections:
        assert section in content, f"Missing section: {section}"

def test_documentation_agent_initialization():
    """Test that the documentation agent initializes correctly."""
    agent = DocumentationAgent()
    assert agent.outputs_dir == Path("outputs")
    assert agent.docs_dir == Path("docs/completions")
    assert agent.context_store == Path("context-store")
    assert agent.tasks_dir == Path("tasks")

def test_documentation_json_output():
    """Test that JSON documentation is also generated."""
    json_path = Path('docs/completions/BE-07.json')
    assert json_path.exists(), f"JSON report not found: {json_path}"
    
    with open(json_path) as f:
        data = json.load(f)
    
    # Check required top-level keys
    required_keys = [
        "task_summary", "artifacts", "qa_summary", 
        "implementation_notes", "technical_details", 
        "next_steps", "references", "generated_at"
    ]
    
    for key in required_keys:
        assert key in data, f"Missing key in JSON: {key}"

def test_both_output_files_exist():
    """Test that both markdown and task output files are generated."""
    md_path = Path('docs/completions/BE-07.md')
    task_md_path = Path('outputs/BE-07/completion_report.md')
    
    assert md_path.exists(), f"Main report not found: {md_path}"
    assert task_md_path.exists(), f"Task report not found: {task_md_path}"
    
    # Both should have similar content
    main_content = md_path.read_text(encoding='utf-8')
    task_content = task_md_path.read_text(encoding='utf-8')
    
    assert '# Task Completion Report: BE-07' in main_content
    assert '# Task Completion Report: BE-07' in task_content

@pytest.mark.integration
def test_documentation_agent_cli():
    """Test the CLI interface of the documentation agent."""
    # This would be an integration test that actually runs the CLI
    # For now, we'll test that the main function exists and can be imported
    from orchestration.documentation_agent import main
    assert callable(main)

def test_task_summary_creation():
    """Test creation of TaskSummary dataclass"""
    summary = TaskSummary(
        task_id="TEST-01",
        title="Test Task", 
        description="Test description",
        owner="test_agent",
        status="COMPLETED",
        start_date="2025-05-26T10:00:00",
        completion_date="2025-05-26T12:00:00",
        duration_hours=2.0
    )
    assert summary.task_id == "TEST-01"
    assert summary.duration_hours == 2.0

def test_qa_summary_creation():
    """Test creation of QASummary dataclass"""
    qa = QASummary(
        overall_status="PASSED",
        tests_passed=5,
        tests_failed=0,
        coverage_percentage=85.0,
        critical_issues=0,
        recommendations_count=2
    )
    assert qa.overall_status == "PASSED"
    assert qa.coverage_percentage == 85.0

def test_task_artifact_creation():
    """Test creation of TaskArtifact dataclass"""
    artifact = TaskArtifact(
        name="test.py",
        path="code/test.py",
        type="code",
        size_bytes=1024,
        description="Test Python file"
    )
    assert artifact.name == "test.py"
    assert artifact.type == "code"

def test_documentation_agent_error_handling():
    """Test error handling when task directory doesn't exist"""
    agent = DocumentationAgent()
    
    with pytest.raises(ValueError, match="Task directory not found"):
        agent.generate_documentation("NONEXISTENT-TASK")

def test_artifact_collection_empty_directory():
    """Test artifact collection with empty task directory"""
    agent = DocumentationAgent()
    
    # Mock empty directory
    with patch.object(Path, 'exists', return_value=True), \
         patch.object(Path, 'glob', return_value=[]):
        artifacts = agent._collect_artifacts("EMPTY-TASK")
        assert artifacts == []

def test_qa_summary_fallback():
    """Test QA summary fallback when QA report doesn't exist"""
    agent = DocumentationAgent()
    
    with patch.object(Path, 'exists', return_value=False):
        qa_summary = agent._load_qa_summary("NO-QA-TASK")
        assert qa_summary.overall_status == "NOT_RUN"
        assert qa_summary.tests_passed == 0

def test_file_size_formatting():
    """Test file size formatting utility"""
    agent = DocumentationAgent()
    
    assert agent._format_file_size(500) == "500 B"
    assert agent._format_file_size(2048) == "2.0 KB"
    assert agent._format_file_size(2097152) == "2.0 MB"

def test_lines_of_code_counting():
    """Test lines of code counting functionality"""
    agent = DocumentationAgent()
    
    # Create a temporary directory structure for testing
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        code_dir = Path(temp_dir)
        
        # Create test files
        (code_dir / "test.py").write_text("print('hello')\n# comment\n\n")
        (code_dir / "test.ts").write_text("console.log('hello');\n// comment\n")
        (code_dir / "readme.txt").write_text("not code")  # Should be ignored
        
        loc = agent._count_lines_of_code(code_dir)
        assert loc == 4  # Only non-empty lines from .py and .ts files

def test_artifact_description_generation():
    """Test artifact description generation"""
    agent = DocumentationAgent()
    
    test_file = Path("test.py")
    desc = agent._generate_artifact_description(test_file, "code")
    assert "Source code file" in desc
    assert "(Python)" in desc
    
    test_file = Path("config.json")
    desc = agent._generate_artifact_description(test_file, "configuration")
    assert "Configuration file" in desc
    assert "(JSON data)" in desc

def test_next_steps_generation():
    """Test next steps generation based on QA status"""
    agent = DocumentationAgent()
    
    # Test with passed QA
    qa_passed = QASummary("PASSED", 5, 0, 90.0, 0, 1)
    steps = agent._generate_next_steps("TEST-01", qa_passed)
    assert any("ready for integration" in step for step in steps)
    
    # Test with failed QA
    qa_failed = QASummary("FAILED", 2, 3, 60.0, 2, 5)
    steps = agent._generate_next_steps("TEST-01", qa_failed)
    assert any("Fix critical issues" in step for step in steps)
    
    # Test with low coverage
    qa_low_coverage = QASummary("PASSED", 5, 0, 70.0, 0, 1)
    steps = agent._generate_next_steps("TEST-01", qa_low_coverage)
    assert any("more comprehensive tests" in step for step in steps)

def test_github_pr_links_collection():
    """Test GitHub PR links collection with mocked GitHub tool"""
    agent = DocumentationAgent()
    
    # Test fallback when GitHub token is not available
    with patch.dict(os.environ, {}, clear=True):
        pr_links = agent._collect_github_pr_links("BE-07")
        assert len(pr_links) == 1
        assert "manual entry needed" in pr_links[0]["title"]

def test_markdown_report_generation():
    """Test complete markdown report generation"""
    # Create a complete documentation report
    task = TaskSummary("TEST-01", "Test Task", "Test description", "test_agent", 
                      "COMPLETED", "2025-05-26T10:00:00", "2025-05-26T12:00:00", 2.0)
    qa = QASummary("PASSED", 5, 0, 85.0, 0, 2)
    artifacts = [TaskArtifact("test.py", "code/test.py", "code", 1024, "Test file")]
    
    doc_report = DocumentationReport(
        task_summary=task,
        artifacts=artifacts,
        qa_summary=qa,
        implementation_notes=["Implementation completed"],
        technical_details={"technologies": ["Python"], "metrics": {"total_files": 1}},
        next_steps=["Deploy to production"],
        references=[{"type": "task", "title": "Task", "url": "#"}],
        generated_at="2025-05-26T12:00:00"
    )
    
    agent = DocumentationAgent()
    
    # Test markdown generation doesn't crash
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        agent._generate_markdown_report(doc_report, temp_path)
        content = temp_path.read_text(encoding='utf-8')
        
        # Verify content
        assert "# Task Completion Report: TEST-01" in content
        assert "## Summary" in content
        # Check for QA section with checkmark (may be rendered as different encoding)
        assert "## QA Validation" in content and ("✅" in content or "âœ…" in content)
        assert "Test Task" in content
        assert "85.0%" in content
        
    finally:
        temp_path.unlink()  # Clean up

@pytest.mark.integration
def test_complete_documentation_workflow():
    """Integration test for complete documentation workflow"""
    # This test requires BE-07 to exist
    outputs_dir = Path("outputs/BE-07")
    if not outputs_dir.exists():
        pytest.skip("BE-07 outputs not found for integration test")
    
    agent = DocumentationAgent()
    
    # Should not raise an exception
    doc_report = agent.generate_documentation("BE-07")
    
    # Verify report structure
    assert doc_report.task_summary.task_id == "BE-07"
    assert isinstance(doc_report.artifacts, list)
    assert isinstance(doc_report.qa_summary, QASummary)
    assert isinstance(doc_report.implementation_notes, list)
    assert isinstance(doc_report.next_steps, list)
    assert isinstance(doc_report.references, list)
    
    # Verify files were created
    assert Path("docs/completions/BE-07.md").exists()
    assert Path("docs/completions/BE-07.json").exists()
    assert Path("outputs/BE-07/completion_report.md").exists()
