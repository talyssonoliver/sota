#!/usr/bin/env python3
"""
Tests for Step 4.6 — Agent Summarisation

Tests the TaskSummarizer class and related functionality for automated
task completion summary generation.
"""

import os
import sys
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from orchestration.summarise_task import (
    TaskSummarizer, TaskSummary, AgentOutput, QAResults, TaskArtifact
)


class TestTaskSummarizer:
    """Test cases for TaskSummarizer class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def sample_task_data(self):
        """Sample task data for testing."""
        return {
            'task_id': 'TEST-01',
            'task_metadata': {
                'id': 'TEST-01',
                'title': 'Test Task Implementation',
                'start_date': '2024-01-01T10:00:00',
                'dependencies': ['PREREQ-01', 'PREREQ-02']
            },
            'agent_outputs': {
                'code_generator': {
                    'status': 'completed',
                    'completion_time': '2024-01-01T12:00:00',
                    'output_file': 'output_code_generator.md',
                    'file_size': 5000,
                    'extracted_artifacts': 2,
                    'metadata': {'lines_added': 150}
                },
                'documentation_agent': {
                    'status': 'completed',
                    'completion_time': '2024-01-01T13:00:00',
                    'output_file': 'output_documentation.md',
                    'file_size': 3000,
                    'extracted_artifacts': 1,
                    'metadata': {'pages_generated': 1}
                }
            },            'qa_results': {
                'analysis_summary': {
                    'overall_status': 'passed',
                    'confidence_score': 92,
                    'critical_issues': 0,
                    'warnings': 3,
                    'recommendations': 2
                },
                'test_coverage': {
                    'estimated_coverage': '85.5%',
                    'critical_paths_covered': True,
                    'error_handling_tested': True
                },
                'tests_passed': 12,
                'tests_failed': 2,
                'detailed_findings': [
                    {
                        'severity': 'warning',
                        'message': 'Missing docstring in function xyz'
                    },
                    {
                        'severity': 'info',
                        'message': 'Code formatting could be improved'
                    }
                ]
            }
        }
    
    @pytest.fixture
    def mock_file_structure(self, temp_dir, sample_task_data):
        """Create mock file structure for testing."""
        task_id = sample_task_data['task_id']
        
        # Create directory structure
        outputs_dir = temp_dir / "outputs" / task_id
        outputs_dir.mkdir(parents=True)
        
        context_store_dir = temp_dir / "context-store"
        context_store_dir.mkdir(parents=True)
        
        code_dir = outputs_dir / "code"
        code_dir.mkdir()
        
        # Create status.json
        status_data = {'agent_outputs': sample_task_data['agent_outputs']}
        with open(outputs_dir / "status.json", 'w') as f:
            json.dump(status_data, f)
        
        # Create qa_report.json
        with open(outputs_dir / "qa_report.json", 'w') as f:
            json.dump(sample_task_data['qa_results'], f)
        
        # Create agent_task_assignments.json
        assignments_data = {'tasks': [sample_task_data['task_metadata']]}
        with open(context_store_dir / "agent_task_assignments.json", 'w') as f:
            json.dump(assignments_data, f)
          # Create some code files
        (code_dir / "src").mkdir()
        (code_dir / "tests").mkdir()
        (code_dir / "docs").mkdir()
        
        # Python code file
        with open(code_dir / "src" / "main_module.py", 'w') as f:
            f.write("# Main module\ndef hello():\n    return 'Hello, World!'\n")
        
        # Test file
        with open(code_dir / "tests" / "test_module_test.py", 'w') as f:
            f.write("import unittest\nclass TestModule(unittest.TestCase):\n    pass\n")
        
        # Documentation
        with open(code_dir / "docs" / "api.md", 'w') as f:
            f.write("# API Documentation\n\nThis is test documentation.\n")
        
        # Config file
        with open(code_dir / "config.json", 'w') as f:
            json.dump({"setting": "value"}, f)
        
        return temp_dir
    
    def test_initialization(self, temp_dir):
        """Test TaskSummarizer initialization."""
        task_id = "TEST-01"
        summarizer = TaskSummarizer(task_id, str(temp_dir))
        
        assert summarizer.task_id == task_id
        assert summarizer.base_dir == temp_dir
        assert summarizer.outputs_dir == temp_dir / "outputs" / task_id
        assert summarizer.completions_dir.exists()
    
    def test_load_task_metadata(self, mock_file_structure, sample_task_data):
        """Test loading task metadata from context store."""
        task_id = sample_task_data['task_id']
        summarizer = TaskSummarizer(task_id, str(mock_file_structure))
        
        metadata = summarizer._load_task_metadata()
        
        assert metadata['id'] == task_id
        assert metadata['title'] == 'Test Task Implementation'
        assert metadata['dependencies'] == ['PREREQ-01', 'PREREQ-02']
    
    def test_load_task_metadata_missing_file(self, temp_dir):
        """Test loading task metadata when file doesn't exist."""
        summarizer = TaskSummarizer("MISSING-01", str(temp_dir))
        
        metadata = summarizer._load_task_metadata()
        assert metadata == {}
    
    def test_analyze_agent_outputs(self, mock_file_structure, sample_task_data):
        """Test analyzing agent outputs from registry."""
        task_id = sample_task_data['task_id']
        summarizer = TaskSummarizer(task_id, str(mock_file_structure))
        
        agent_outputs = summarizer._analyze_agent_outputs()
        
        assert len(agent_outputs) == 2
        
        # Check agent outputs (order may vary)
        agent_ids = {output.agent_id for output in agent_outputs}
        assert 'code_generator' in agent_ids
        assert 'documentation_agent' in agent_ids
        
        # Check that both agents completed
        for output in agent_outputs:
            assert output.status == 'completed'
            assert len(output.files_generated) >= 1  # At least one file generated
    
    def test_analyze_agent_outputs_missing_status(self, temp_dir):
        """Test analyzing agent outputs when status.json doesn't exist."""
        summarizer = TaskSummarizer("MISSING-01", str(temp_dir))
        
        agent_outputs = summarizer._analyze_agent_outputs()
        
        assert agent_outputs == []
    
    def test_analyze_code_artifacts(self, mock_file_structure, sample_task_data):
        """Test analyzing code artifacts from extraction."""
        task_id = sample_task_data['task_id']
        summarizer = TaskSummarizer(task_id, str(mock_file_structure))
        
        artifacts = summarizer._analyze_code_artifacts()
        
        # Should find 4 files: Python, test, doc, config
        assert len(artifacts) == 4
        
        # Check artifact types
        artifact_types = {artifact.type for artifact in artifacts}
        assert 'code' in artifact_types
        assert 'test' in artifact_types
        assert 'doc' in artifact_types
        assert 'config' in artifact_types
        
        # Check languages
        python_artifacts = [a for a in artifacts if a.language == 'Python']
        assert len(python_artifacts) == 2  # src and test files
    
    def test_analyze_qa_results(self, mock_file_structure, sample_task_data):
        """Test analyzing QA results."""
        task_id = sample_task_data['task_id']
        summarizer = TaskSummarizer(task_id, str(mock_file_structure))
        
        qa_results = summarizer._analyze_qa_results()
        
        assert qa_results is not None
        assert qa_results.test_coverage == 85.5
        assert qa_results.tests_passed == 12
        assert qa_results.tests_failed == 2
        assert qa_results.critical_issues == 0
        assert qa_results.warnings == 3
        assert qa_results.overall_status == 'passed'
        assert len(qa_results.detailed_findings) == 2
    
    def test_analyze_qa_results_missing_file(self, temp_dir):
        """Test analyzing QA results when file doesn't exist."""
        summarizer = TaskSummarizer("MISSING-01", str(temp_dir))
        
        qa_results = summarizer._analyze_qa_results()
        
        assert qa_results is None
    
    def test_determine_completion_status_completed_verified(self):
        """Test completion status determination for verified completion."""
        agent_outputs = [
            AgentOutput('agent1', '2024-01-01', 'completed', [], [], {}),
            AgentOutput('agent2', '2024-01-01', 'completed', [], [], {})
        ]
        qa_results = QAResults(85.0, 10, 0, 0, 2, 'passed', [])
        
        summarizer = TaskSummarizer("TEST-01")
        status = summarizer._determine_completion_status(agent_outputs, qa_results)
        
        assert status == "COMPLETED_VERIFIED"
    
    def test_determine_completion_status_with_issues(self):
        """Test completion status determination with critical issues."""
        agent_outputs = [
            AgentOutput('agent1', '2024-01-01', 'completed', [], [], {})
        ]
        qa_results = QAResults(60.0, 5, 3, 2, 5, 'failed', [])
        
        summarizer = TaskSummarizer("TEST-01")
        status = summarizer._determine_completion_status(agent_outputs, qa_results)
        
        assert status == "COMPLETED_WITH_ISSUES"
    
    def test_determine_completion_status_failed(self):
        """Test completion status determination for failed tasks."""
        agent_outputs = [
            AgentOutput('agent1', '2024-01-01', 'failed', [], [], {}),
            AgentOutput('agent2', '2024-01-01', 'completed', [], [], {})
        ]
        
        summarizer = TaskSummarizer("TEST-01")
        status = summarizer._determine_completion_status(agent_outputs, None)
        
        assert status == "FAILED"
    
    def test_determine_completion_status_in_progress(self):
        """Test completion status determination for in-progress tasks."""
        agent_outputs = [
            AgentOutput('agent1', '2024-01-01', 'in_progress', [], [], {})
        ]
        
        summarizer = TaskSummarizer("TEST-01")
        status = summarizer._determine_completion_status(agent_outputs, None)
        
        assert status == "IN_PROGRESS"
    
    def test_determine_completion_status_no_outputs(self):
        """Test completion status determination with no outputs."""
        summarizer = TaskSummarizer("TEST-01")
        status = summarizer._determine_completion_status([], None)
        
        assert status == "NO_OUTPUTS"
    
    def test_generate_next_steps_completed_verified(self):
        """Test next steps generation for verified completion."""
        summarizer = TaskSummarizer("TEST-01")
        qa_results = QAResults(90.0, 15, 0, 0, 1, 'passed', [])
        
        next_steps = summarizer._generate_next_steps("COMPLETED_VERIFIED", qa_results)
        
        assert "completed successfully" in next_steps[0].lower()
        assert "integration" in next_steps[1].lower() or "deployment" in next_steps[1].lower()
    
    def test_generate_next_steps_with_issues(self):
        """Test next steps generation for completion with issues."""
        summarizer = TaskSummarizer("TEST-01")
        qa_results = QAResults(60.0, 8, 4, 3, 5, 'failed', [])
        
        next_steps = summarizer._generate_next_steps("COMPLETED_WITH_ISSUES", qa_results)
        
        assert any("critical issues" in step.lower() for step in next_steps)
        assert any("3 critical issues" in step for step in next_steps)
    
    def test_determine_file_type_code(self):
        """Test file type determination for code files."""
        summarizer = TaskSummarizer("TEST-01")
        
        assert summarizer._determine_file_type(Path("src/module.py")) == 'code'
        assert summarizer._determine_file_type(Path("lib/utils.js")) == 'code'
        assert summarizer._determine_file_type(Path("components/app.ts")) == 'code'
    
    def test_determine_file_type_test(self):
        """Test file type determination for test files."""
        summarizer = TaskSummarizer("TEST-01")
        
        assert summarizer._determine_file_type(Path("tests/test_module.py")) == 'test'
        assert summarizer._determine_file_type(Path("src/test_utils.js")) == 'test'
        assert summarizer._determine_file_type(Path("test/component.spec.ts")) == 'test'
    
    def test_determine_file_type_doc(self):
        """Test file type determination for documentation files."""
        summarizer = TaskSummarizer("TEST-01")
        
        assert summarizer._determine_file_type(Path("README.md")) == 'doc'
        assert summarizer._determine_file_type(Path("docs/api.html")) == 'doc'
        assert summarizer._determine_file_type(Path("guide.txt")) == 'doc'
    
    def test_determine_file_type_config(self):
        """Test file type determination for config files."""
        summarizer = TaskSummarizer("TEST-01")
        
        assert summarizer._determine_file_type(Path("config.json")) == 'config'
        assert summarizer._determine_file_type(Path("settings.yaml")) == 'config'
        assert summarizer._determine_file_type(Path("app.toml")) == 'config'
    
    def test_determine_language(self):
        """Test programming language determination."""
        summarizer = TaskSummarizer("TEST-01")
        
        assert summarizer._determine_language(Path("module.py")) == 'Python'
        assert summarizer._determine_language(Path("app.js")) == 'JavaScript'
        assert summarizer._determine_language(Path("component.ts")) == 'TypeScript'
        assert summarizer._determine_language(Path("Main.java")) == 'Java'
        assert summarizer._determine_language(Path("config.json")) == 'JSON'
        assert summarizer._determine_language(Path("unknown.xyz")) is None
    
    def test_calculate_total_code_lines(self, mock_file_structure, sample_task_data):
        """Test total code lines calculation."""
        task_id = sample_task_data['task_id']
        summarizer = TaskSummarizer(task_id, str(mock_file_structure))
        
        # Create some artifacts
        artifacts = [
            TaskArtifact("src/main_module.py", "code", 100, "Python"),
            TaskArtifact("tests/test_module_test.py", "test", 50, "Python"),
            TaskArtifact("docs/api.md", "doc", 200, None)
        ]
        
        total_lines = summarizer._calculate_total_code_lines(artifacts)
        
        # Should only count code files (not test or doc)
        assert total_lines == 3  # Lines in src/main_module.py
    
    def test_generate_markdown_report(self, sample_task_data):
        """Test markdown report generation."""
        # Create a sample summary
        agent_outputs = [
            AgentOutput('code_gen', '2024-01-01T12:00:00', 'completed', 
                       ['src/module.py'], ['README.md'], {})
        ]
        
        qa_results = QAResults(85.0, 10, 2, 0, 3, 'passed', [
            {'severity': 'warning', 'message': 'Test warning'}
        ])
        
        artifacts = [
            TaskArtifact("src/module.py", "code", 1024, "Python")
        ]
        
        summary = TaskSummary(
            task_id='TEST-01',
            task_title='Test Task',
            completion_status='COMPLETED_VERIFIED',
            start_date='2024-01-01T10:00:00',
            completion_date='2024-01-01T15:00:00',
            agent_outputs=agent_outputs,
            artifacts=artifacts,
            qa_results=qa_results,
            dependencies=['DEP-01'],
            next_steps=['Deploy to production'],
            total_files_created=1,
            total_files_modified=1,
            total_code_lines=50
        )
        
        summarizer = TaskSummarizer("TEST-01")
        markdown = summarizer.generate_markdown_report(summary)
        
        # Check key sections are present
        assert "# Task Completion Summary: TEST-01" in markdown
        assert "**Completion Status:** COMPLETED_VERIFIED" in markdown
        assert "## Agent Execution Summary" in markdown
        assert "## Generated Artifacts" in markdown
        assert "## Quality Assurance Results" in markdown
        assert "## Task Dependencies" in markdown
        assert "## Recommended Next Steps" in markdown
        
        # Check specific content
        assert "code_gen" in markdown
        assert "Test Coverage:** 85.0%" in markdown
        assert "Deploy to production" in markdown
        assert "DEP-01" in markdown
    
    def test_save_completion_report(self, temp_dir, sample_task_data):
        """Test saving completion report to file."""
        task_id = sample_task_data['task_id']
        summarizer = TaskSummarizer(task_id, str(temp_dir))
        
        # Create minimal summary
        summary = TaskSummary(
            task_id=task_id,
            task_title='Test Task',
            completion_status='COMPLETED',
            start_date=None,
            completion_date='2024-01-01T15:00:00',
            agent_outputs=[],
            artifacts=[],
            qa_results=None,
            dependencies=[],
            next_steps=[],
            total_files_created=0,
            total_files_modified=0,
            total_code_lines=0
        )
        
        report_path = summarizer.save_completion_report(summary)
        
        assert report_path.exists()
        assert report_path.name == f"{task_id}.md"
        
        # Check file content
        content = report_path.read_text(encoding='utf-8')
        assert f"# Task Completion Summary: {task_id}" in content
    
    def test_analyze_task_completion_integration(self, mock_file_structure, sample_task_data):
        """Test full task completion analysis integration."""
        task_id = sample_task_data['task_id']
        summarizer = TaskSummarizer(task_id, str(mock_file_structure))
        
        summary = summarizer.analyze_task_completion()
        
        # Check summary properties
        assert summary.task_id == task_id
        assert summary.task_title == 'Test Task Implementation'
        assert summary.completion_status == 'COMPLETED_VERIFIED'
        assert len(summary.agent_outputs) == 2
        assert len(summary.artifacts) == 4
        assert summary.qa_results is not None
        assert summary.total_files_created == 3  # 2 + 1 from agents
        assert summary.total_files_modified == 1
        assert summary.total_code_lines > 0
    
    def test_error_handling(self, temp_dir):
        """Test error handling in various scenarios."""
        summarizer = TaskSummarizer("ERROR-01", str(temp_dir))
        
        # Test with missing directories and files
        summary = summarizer.analyze_task_completion()
        
        # Should not crash, should return defaults
        assert summary.task_id == "ERROR-01"
        assert summary.agent_outputs == []
        assert summary.artifacts == []
        assert summary.qa_results is None


class TestCLIInterface:
    """Test cases for CLI interface."""
    
    @patch('orchestration.summarise_task.TaskSummarizer')
    @patch('sys.argv', ['summarise_task.py', 'CLI-01'])
    def test_cli_basic_usage(self, mock_summarizer_class):
        """Test basic CLI usage."""
        mock_summarizer = Mock()
        mock_summarizer.run_full_analysis.return_value = Path("/tmp/CLI-01.md")
        mock_summarizer.analyze_task_completion.return_value = Mock(
            completion_status='COMPLETED',
            total_files_created=5,
            total_files_modified=2,
            total_code_lines=150,
            qa_results=Mock(test_coverage=85.0, tests_passed=10)
        )
        mock_summarizer_class.return_value = mock_summarizer
        
        from orchestration.summarise_task import main
        
        # Should not raise exception
        main()
        
        # Verify summarizer was created and called
        mock_summarizer_class.assert_called_once_with('CLI-01')
        mock_summarizer.run_full_analysis.assert_called_once()
    
    @patch('orchestration.summarise_task.TaskSummarizer')
    @patch('sys.argv', ['summarise_task.py', '--task-id', 'CLI-02', '--verbose'])
    def test_cli_with_options(self, mock_summarizer_class):
        """Test CLI with options."""
        mock_summarizer = Mock()
        mock_summarizer.run_full_analysis.return_value = Path("/tmp/CLI-02.md")
        mock_summarizer.analyze_task_completion.return_value = Mock(
            completion_status='COMPLETED',
            total_files_created=3,
            total_files_modified=1,
            total_code_lines=75,
            qa_results=None
        )
        mock_summarizer_class.return_value = mock_summarizer
        
        from orchestration.summarise_task import main
        
        # Should not raise exception
        main()
        
        # Verify summarizer was created with correct task ID
        mock_summarizer_class.assert_called_once_with('CLI-02')


if __name__ == "__main__":
    pytest.main([__file__])
