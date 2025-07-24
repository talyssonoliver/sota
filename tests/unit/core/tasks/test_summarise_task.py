"""
Comprehensive tests for task summarization functionality.

Tests TaskSummarizer class and all related dataclasses and functions.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.core.workflows.summarise_task import (
    AgentOutput,
    QAResults,
    TaskArtifact,
    TaskSummarizer,
    TaskSummary,
    main,
)


class TestTaskArtifact:
    """Test the TaskArtifact dataclass."""

    def test_task_artifact_creation(self):
        """Test basic TaskArtifact creation."""
        artifact = TaskArtifact(
            path="/path/test.py",
            type="code", 
            size_bytes=1024,
            language="python",
            description="Test file"
        )
        
        assert artifact.path == "/path/test.py"
        assert artifact.type == "code"
        assert artifact.size_bytes == 1024
        assert artifact.language == "python"
        assert artifact.description == "Test file"

    def test_task_artifact_minimal(self):
        """Test TaskArtifact with minimal required fields."""
        artifact = TaskArtifact(
            path="/minimal.txt",
            type="doc",
            size_bytes=512
        )
        
        assert artifact.path == "/minimal.txt"
        assert artifact.type == "doc"
        assert artifact.size_bytes == 512
        assert artifact.language is None
        assert artifact.description is None

    def test_task_artifact_types(self):
        """Test different artifact types."""
        types = ["code", "test", "doc", "config"]
        
        for artifact_type in types:
            artifact = TaskArtifact(
                path=f"/test.{artifact_type}",
                type=artifact_type,
                size_bytes=100
            )
            assert artifact.type == artifact_type


class TestAgentOutput:
    """Test the AgentOutput dataclass."""

    def test_agent_output_creation(self):
        """Test basic AgentOutput creation."""
        output = AgentOutput(
            agent_id="test_agent",
            timestamp="2024-01-01T12:00:00",
            status="completed",
            files_generated=["file1.py", "file2.py"],
            files_modified=["existing.py"],
            metadata={"key": "value"}
        )
        
        assert output.agent_id == "test_agent"
        assert output.timestamp == "2024-01-01T12:00:00"
        assert output.status == "completed"
        assert output.files_generated == ["file1.py", "file2.py"]
        assert output.files_modified == ["existing.py"]
        assert output.metadata == {"key": "value"}

    def test_agent_output_different_statuses(self):
        """Test AgentOutput with different status values."""
        statuses = ["completed", "failed", "in_progress", "unknown"]
        
        for status in statuses:
            output = AgentOutput(
                agent_id="agent",
                timestamp="2024-01-01T12:00:00", 
                status=status,
                files_generated=[],
                files_modified=[],
                metadata={}
            )
            assert output.status == status


class TestQAResults:
    """Test the QAResults dataclass."""

    def test_qa_results_creation(self):
        """Test basic QAResults creation."""
        results = QAResults(
            test_coverage=85.5,
            tests_passed=10,
            tests_failed=2,
            critical_issues=1,
            warnings=5,
            overall_status="passed",
            detailed_findings=[{"issue": "test"}]
        )
        
        assert results.test_coverage == 85.5
        assert results.tests_passed == 10
        assert results.tests_failed == 2
        assert results.critical_issues == 1
        assert results.warnings == 5
        assert results.overall_status == "passed"
        assert results.detailed_findings == [{"issue": "test"}]

    def test_qa_results_edge_cases(self):
        """Test QAResults with edge case values."""
        # Perfect test results
        perfect_results = QAResults(
            test_coverage=100.0,
            tests_passed=50,
            tests_failed=0,
            critical_issues=0,
            warnings=0,
            overall_status="perfect",
            detailed_findings=[]
        )
        
        assert perfect_results.test_coverage == 100.0
        assert perfect_results.tests_failed == 0
        assert perfect_results.critical_issues == 0


class TestTaskSummary:
    """Test the TaskSummary dataclass."""

    def test_task_summary_creation(self):
        """Test basic TaskSummary creation."""
        agent_output = AgentOutput(
            agent_id="test",
            timestamp="2024-01-01T12:00:00",
            status="completed",
            files_generated=[],
            files_modified=[],
            metadata={}
        )
        
        artifact = TaskArtifact(
            path="/test.py",
            type="code",
            size_bytes=100
        )
        
        qa_results = QAResults(
            test_coverage=80.0,
            tests_passed=5,
            tests_failed=1,
            critical_issues=0,
            warnings=2,
            overall_status="passed",
            detailed_findings=[]
        )
        
        summary = TaskSummary(
            task_id="TEST-01",
            task_title="Test Task",
            completion_status="completed",
            start_date="2024-01-01",
            completion_date="2024-01-02",
            agent_outputs=[agent_output],
            artifacts=[artifact],
            qa_results=qa_results,
            dependencies=["DEP-01"],
            next_steps=["Review code"],
            total_files_created=5,
            total_files_modified=2,
            total_code_lines=150
        )
        
        assert summary.task_id == "TEST-01"
        assert summary.task_title == "Test Task"
        assert summary.completion_status == "completed"
        assert len(summary.agent_outputs) == 1
        assert len(summary.artifacts) == 1
        assert summary.qa_results is not None
        assert summary.total_files_created == 5


class TestTaskSummarizer:
    """Test the TaskSummarizer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.task_id = "TEST-01"
        self.summarizer = TaskSummarizer(self.task_id, self.temp_dir)

    def test_initialization(self):
        """Test TaskSummarizer initialization."""
        assert self.summarizer.task_id == "TEST-01"
        assert self.summarizer.base_dir == Path(self.temp_dir)
        
        # Check directory setup
        expected_dirs = [
            self.summarizer.outputs_dir,
            self.summarizer.context_store_dir,
            self.summarizer.docs_dir,
            self.summarizer.completions_dir
        ]
        
        for dir_path in expected_dirs:
            assert isinstance(dir_path, Path)

    def test_initialization_with_default_base_dir(self):
        """Test TaskSummarizer with default base directory."""
        summarizer = TaskSummarizer("DEFAULT-01")
        assert summarizer.task_id == "DEFAULT-01"
        assert isinstance(summarizer.base_dir, Path)

    def test_completions_directory_creation(self):
        """Test that completions directory is created."""
        # The directory should be created during initialization
        assert self.summarizer.completions_dir.exists()

    def test_load_task_metadata_file_exists(self):
        """Test loading task metadata when file exists."""
        # Create mock assignments file
        assignments_file = self.summarizer.context_store_dir / "agent_task_assignments.json"
        assignments_file.parent.mkdir(parents=True, exist_ok=True)
        
        test_data = {
            "tasks": [
                {
                    "id": "TEST-01",
                    "title": "Test Task",
                    "dependencies": ["DEP-01"],
                    "start_date": "2024-01-01"
                },
                {
                    "id": "OTHER-01", 
                    "title": "Other Task"
                }
            ]
        }
        
        with open(assignments_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)
        
        metadata = self.summarizer._load_task_metadata()
        
        assert metadata["id"] == "TEST-01"
        assert metadata["title"] == "Test Task"
        assert metadata["dependencies"] == ["DEP-01"]

    def test_load_task_metadata_file_not_exists(self):
        """Test loading task metadata when file doesn't exist."""
        metadata = self.summarizer._load_task_metadata()
        assert metadata == {}

    def test_load_task_metadata_task_not_found(self):
        """Test loading metadata when task is not in file."""
        assignments_file = self.summarizer.context_store_dir / "agent_task_assignments.json"
        assignments_file.parent.mkdir(parents=True, exist_ok=True)
        
        test_data = {
            "tasks": [
                {"id": "OTHER-01", "title": "Other Task"}
            ]
        }
        
        with open(assignments_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)
        
        metadata = self.summarizer._load_task_metadata()
        assert metadata == {}

    def test_analyze_agent_outputs_no_status_file(self):
        """Test analyzing agent outputs when status file doesn't exist."""
        outputs = self.summarizer._analyze_agent_outputs()
        assert outputs == []

    def test_analyze_agent_outputs_with_status_file(self):
        """Test analyzing agent outputs with valid status file."""
        # Create status file
        status_file = self.summarizer.outputs_dir / "status.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        
        status_data = {
            "agent_outputs": {
                "test_agent": {
                    "status": "completed",
                    "completion_time": "2024-01-01T12:00:00",
                    "metadata": {"key": "value"}
                },
                "code_generator": {
                    "status": "success",
                    "completion_time": "2024-01-01T13:00:00",
                    "metadata": {}
                }
            }
        }
        
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status_data, f)
        
        # Mock the _extract_generated_files method
        with patch.object(self.summarizer, '_extract_generated_files') as mock_extract:
            mock_extract.return_value = ["generated_file.py"]
            
            outputs = self.summarizer._analyze_agent_outputs()
            
            assert len(outputs) == 2
            
            # Check first agent output
            test_agent_output = next(o for o in outputs if o.agent_id == "test_agent")
            assert test_agent_output.status == "completed"
            assert test_agent_output.timestamp == "2024-01-01T12:00:00"
            assert test_agent_output.files_generated == ["generated_file.py"]
            
            # Check code_generator has modified files (per the logic in the code)
            code_gen_output = next(o for o in outputs if o.agent_id == "code_generator")
            assert code_gen_output.files_modified == ["existing_file.py"]

    def test_analyze_code_artifacts_no_code_dir(self):
        """Test analyzing code artifacts when code directory doesn't exist."""
        artifacts = self.summarizer._analyze_code_artifacts()
        assert artifacts == []

    def test_analyze_code_artifacts_with_files(self):
        """Test analyzing code artifacts with actual files."""
        # Create code directory with test files
        code_dir = self.summarizer.outputs_dir / "code"
        code_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test files
        test_files = [
            ("test.py", "def test():\n    pass\n"),
            ("config.json", '{"key": "value"}'),
            ("README.md", "# Test README\n\nContent here.")
        ]
        
        for filename, content in test_files:
            file_path = code_dir / filename
            file_path.write_text(content, encoding="utf-8")
        
        artifacts = self.summarizer._analyze_code_artifacts()
        
        assert len(artifacts) == 3
        
        # Check Python file artifact
        py_artifact = next(a for a in artifacts if a.path.endswith("test.py"))
        assert py_artifact.type == "code"
        assert py_artifact.language == "python"
        assert py_artifact.size_bytes > 0
        
        # Check JSON file artifact
        json_artifact = next(a for a in artifacts if a.path.endswith("config.json"))
        assert json_artifact.type == "config"
        
        # Check markdown file artifact
        md_artifact = next(a for a in artifacts if a.path.endswith("README.md"))
        assert md_artifact.type == "doc"

    def test_determine_file_type(self):
        """Test file type determination logic."""
        test_cases = [
            (Path("test.py"), "code"),
            (Path("test.js"), "code"),
            (Path("test_file.py"), "test"),
            (Path("spec.js"), "test"),
            (Path("config.json"), "config"),
            (Path("settings.yaml"), "config"),
            (Path("README.md"), "doc"),
            (Path("unknown.xyz"), "code"),  # default
        ]
        
        for file_path, expected_type in test_cases:
            result = self.summarizer._determine_file_type(file_path)
            assert result == expected_type

    def test_determine_language(self):
        """Test programming language determination."""
        test_cases = [
            (Path("test.py"), "python"),
            (Path("test.js"), "javascript"),
            (Path("test.ts"), "typescript"),
            (Path("test.java"), "java"),
            (Path("test.cpp"), "cpp"),
            (Path("test.c"), "c"),
            (Path("test.go"), "go"),
            (Path("test.rs"), "rust"),
            (Path("test.php"), "php"),
            (Path("test.rb"), "ruby"),
            (Path("test.unknown"), None),
        ]
        
        for file_path, expected_lang in test_cases:
            result = self.summarizer._determine_language(file_path)
            assert result == expected_lang

    def test_calculate_total_code_lines(self):
        """Test total code lines calculation."""
        artifacts = [
            TaskArtifact("/test1.py", "code", 100, "python"),
            TaskArtifact("/test2.js", "code", 200, "javascript"),
            TaskArtifact("/config.json", "config", 50),  # Non-code file
            TaskArtifact("/test3.py", "test", 150, "python"),
        ]
        
        # Mock file reading
        with patch("builtins.open") as mock_open:
            # Mock different files returning different line counts
            def mock_file_content(*args, **kwargs):
                filename = str(args[0])
                if "test1.py" in filename:
                    return ["line1\n", "line2\n", "line3\n"]  # 3 lines
                elif "test2.js" in filename:
                    return ["line1\n", "line2\n"]  # 2 lines
                elif "test3.py" in filename:
                    return ["line1\n"]  # 1 line
                return []
            
            mock_open.return_value.__enter__.return_value.__iter__ = mock_file_content
            
            total_lines = self.summarizer._calculate_total_code_lines(artifacts)
            # Should only count code and test files: 3 + 2 + 1 = 6
            assert total_lines == 6

    def test_determine_completion_status(self):
        """Test completion status determination logic."""
        # Create test agent outputs
        successful_outputs = [
            AgentOutput("agent1", "2024-01-01T12:00:00", "completed", [], [], {}),
            AgentOutput("agent2", "2024-01-01T12:00:00", "success", [], [], {})
        ]
        
        failed_outputs = [
            AgentOutput("agent1", "2024-01-01T12:00:00", "failed", [], [], {}),
            AgentOutput("agent2", "2024-01-01T12:00:00", "completed", [], [], {})
        ]
        
        # Test with successful QA results
        good_qa = QAResults(90.0, 10, 0, 0, 1, "passed", [])
        status = self.summarizer._determine_completion_status(successful_outputs, good_qa)
        assert status == "completed"
        
        # Test with failed QA results
        bad_qa = QAResults(50.0, 5, 5, 3, 10, "failed", [])
        status = self.summarizer._determine_completion_status(successful_outputs, bad_qa)
        assert status == "completed_with_issues"
        
        # Test with failed agents
        status = self.summarizer._determine_completion_status(failed_outputs, good_qa)
        assert status == "failed"

    def test_generate_next_steps(self):
        """Test next steps generation."""
        # Test with completion status "failed"
        qa_results = QAResults(60.0, 3, 2, 1, 5, "failed", [])
        steps = self.summarizer._generate_next_steps("failed", qa_results)
        
        assert "Debug and resolve agent failures" in steps
        assert len(steps) > 0
        
        # Test with completion status "completed"
        good_qa = QAResults(95.0, 10, 0, 0, 1, "passed", [])
        steps = self.summarizer._generate_next_steps("completed", good_qa)
        
        assert "Task completed successfully" in steps

    def test_generate_markdown_report(self):
        """Test markdown report generation."""
        # Create a complete TaskSummary
        agent_output = AgentOutput(
            "test_agent", "2024-01-01T12:00:00", "completed", 
            ["file1.py"], ["file2.py"], {"key": "value"}
        )
        
        artifact = TaskArtifact("/test.py", "code", 100, "python", "Test file")
        qa_results = QAResults(85.0, 8, 2, 1, 3, "passed", [])
        
        summary = TaskSummary(
            task_id="TEST-01",
            task_title="Test Task",
            completion_status="completed",
            start_date="2024-01-01",
            completion_date="2024-01-02",
            agent_outputs=[agent_output],
            artifacts=[artifact],
            qa_results=qa_results,
            dependencies=["DEP-01"],
            next_steps=["Review"],
            total_files_created=1,
            total_files_modified=1,
            total_code_lines=20
        )
        
        markdown = self.summarizer.generate_markdown_report(summary)
        
        # Check key sections are present
        assert "# Task Completion Report: TEST-01" in markdown
        assert "## Overview" in markdown
        assert "## Agent Outputs" in markdown
        assert "## Code Artifacts" in markdown
        assert "## QA Results" in markdown
        assert "## Summary Statistics" in markdown
        assert "## Next Steps" in markdown
        
        # Check specific content is included
        assert "Test Task" in markdown
        assert "test_agent" in markdown
        assert "85.0%" in markdown

    @patch('src.core.workflows.summarise_task.logger')
    def test_analyze_task_completion_integration(self, mock_logger):
        """Test the main analyze_task_completion method."""
        # Mock all the sub-methods
        with patch.object(self.summarizer, '_load_task_metadata') as mock_metadata, \
             patch.object(self.summarizer, '_analyze_agent_outputs') as mock_outputs, \
             patch.object(self.summarizer, '_analyze_code_artifacts') as mock_artifacts, \
             patch.object(self.summarizer, '_analyze_qa_results') as mock_qa, \
             patch.object(self.summarizer, '_determine_completion_status') as mock_status, \
             patch.object(self.summarizer, '_generate_next_steps') as mock_steps, \
             patch.object(self.summarizer, '_calculate_total_code_lines') as mock_lines:
            
            # Set up mock returns
            mock_metadata.return_value = {"title": "Test Task", "dependencies": []}
            mock_outputs.return_value = []
            mock_artifacts.return_value = []
            mock_qa.return_value = None
            mock_status.return_value = "completed"
            mock_steps.return_value = ["Review"]
            mock_lines.return_value = 100
            
            # Call the main method
            summary = self.summarizer.analyze_task_completion()
            
            # Verify the result
            assert isinstance(summary, TaskSummary)
            assert summary.task_id == "TEST-01"
            assert summary.task_title == "Test Task"
            assert summary.completion_status == "completed"
            assert summary.total_code_lines == 100


class TestMainFunction:
    """Test the main CLI function."""

    @patch('sys.argv', ['summarise_task.py', 'CLI-01'])
    @patch('src.core.workflows.summarise_task.TaskSummarizer')
    def test_main_with_task_id(self, mock_summarizer_class):
        """Test main function with task ID argument."""
        mock_summarizer = Mock()
        mock_summarizer.run_full_analysis.return_value = Path("/test/report.md")
        mock_summarizer_class.return_value = mock_summarizer
        
        main()
        
        mock_summarizer_class.assert_called_once_with("CLI-01")
        mock_summarizer.run_full_analysis.assert_called_once()

    @patch('sys.argv', ['summarise_task.py'])
    @patch('builtins.print')
    def test_main_no_arguments(self, mock_print):
        """Test main function with no arguments."""
        main()
        
        mock_print.assert_called()
        call_args = mock_print.call_args[0][0]
        assert "Usage:" in call_args

    @patch('sys.argv', ['summarise_task.py', '--help'])
    @patch('builtins.print')
    def test_main_help_flag(self, mock_print):
        """Test main function with help flag."""
        main()
        
        mock_print.assert_called()
        call_args = mock_print.call_args[0][0]
        assert "Usage:" in call_args