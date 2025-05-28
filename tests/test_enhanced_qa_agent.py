"""
Test coverage for Enhanced QA Agent components.
This file tests the QA Agent's test generation and coverage analysis capabilities.
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from agents.qa import EnhancedQAAgent, create_enhanced_qa_workflow
from utils.coverage_analyzer import CoverageAnalyzer
from utils.test_generator import (QATestCase, QATestFramework, QATestGenerator,
                                  QATestSuite)

# Add the project root to the path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class TestEnhancedQAAgent:
    """Test suite for EnhancedQAAgent."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)

        # Create sample source files
        (project_path / "src").mkdir()
        (project_path / "src" / "sample.py").write_text("""
class Calculator:
    def add(self, a, b):
        return a + b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Division by zero")
        return a / b

def multiply(x, y):
    return x * y
""")

        (project_path / "src" / "utils.py").write_text("""
def format_output(data):
    return str(data)

def validate_input(value):
    if value is None:
        raise ValueError("Input cannot be None")
    return True
""")

        yield project_path

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def qa_agent(self, temp_project):
        """Create an EnhancedQAAgent instance for testing."""
        return EnhancedQAAgent(str(temp_project))

    def test_qa_agent_initialization(self, temp_project):
        """Test QA agent initialization."""
        agent = EnhancedQAAgent(str(temp_project))

        assert agent.project_root == temp_project
        assert isinstance(agent.test_generator, QATestGenerator)
        assert isinstance(agent.coverage_analyzer, CoverageAnalyzer)
        assert "coverage_thresholds" in agent.config
        assert "quality_gates" in agent.config

    def test_load_config_with_file(self, temp_project):
        """Test loading configuration from file."""
        config_file = temp_project / "qa_config.json"
        config_data = {
            "coverage_thresholds": {"line_coverage": 95},
            "quality_gates": {"min_test_coverage": 90}
        }
        config_file.write_text(json.dumps(config_data))

        agent = EnhancedQAAgent(str(temp_project), str(config_file))

        assert agent.config["coverage_thresholds"]["line_coverage"] == 95
        assert agent.config["quality_gates"]["min_test_coverage"] == 90

    def test_load_config_default(self, temp_project):
        """Test loading default configuration."""
        agent = EnhancedQAAgent(str(temp_project))

        assert agent.config["coverage_thresholds"]["line_coverage"] == 80
        assert agent.config["quality_gates"]["min_test_coverage"] == 80

    def test_discover_source_files(self, qa_agent):
        """Test source file discovery."""
        source_files = qa_agent._discover_source_files()

        assert len(source_files) >= 2
        assert any("sample.py" in f for f in source_files)
        assert any("utils.py" in f for f in source_files)
        # Should not include test files or cache
        assert not any("test_" in f for f in source_files)
        assert not any("__pycache__" in f for f in source_files)

    def test_determine_test_framework_python(self, qa_agent):
        """Test test framework determination for Python files."""
        # Create pytest.ini to indicate pytest usage
        (qa_agent.project_root / "pytest.ini").write_text("[tool:pytest]")

        framework = qa_agent._determine_test_framework("sample.py")
        assert framework == QATestFramework.PYTEST

    def test_determine_test_framework_javascript(self, qa_agent):
        """Test test framework determination for JavaScript files."""
        framework = qa_agent._determine_test_framework("sample.js")
        assert framework == QATestFramework.JEST

    def test_get_test_file_path_pytest(self, qa_agent):
        """Test test file path generation for pytest."""
        test_path = qa_agent._get_test_file_path(
            "src/sample.py", QATestFramework.PYTEST)

        assert test_path.name == "test_sample.py"
        assert "tests" in str(test_path) and "generated" in str(test_path)

    def test_get_test_file_path_jest(self, qa_agent):
        """Test test file path generation for Jest."""
        test_path = qa_agent._get_test_file_path(
            "src/sample.js", QATestFramework.JEST)

        assert test_path.name == "sample.test.js"
        assert "tests" in str(test_path) and "generated" in str(test_path)

    @patch('agents.qa.CoverageAnalyzer')
    @patch('agents.qa.IntegrationAnalyzer')
    def test_generate_comprehensive_tests(
            self, mock_integration, mock_coverage, qa_agent):
        """Test comprehensive test generation."""
        # Mock coverage analyzer
        mock_coverage_instance = Mock()
        mock_coverage_instance.analyze_coverage_patterns.return_value = {
            "overall_quality_score": 75,
            "improvement_potential": 25
        }
        mock_coverage.return_value = mock_coverage_instance

        # Mock integration analyzer
        mock_integration_instance = Mock()
        mock_integration_instance.analyze_project.return_value = {
            "gaps": ["missing_interface_test", "unvalidated_data_flow"]
        }
        mock_integration.return_value = mock_integration_instance

        # Mock test generator to avoid file system operations
        with patch.object(qa_agent, '_generate_test_for_file') as mock_gen:
            mock_gen.return_value = {
                "source_file": "sample.py",
                "test_file": "test_sample.py",
                "framework": "pytest",
                "status": "success",
                "test_count": 5
            }

            results = qa_agent.generate_comprehensive_tests(["sample.py"])

        assert "generated_tests" in results
        assert "coverage_analysis" in results
        assert "integration_gaps" in results
        assert "quality_metrics" in results
        assert "recommendations" in results

        assert len(results["generated_tests"]) == 1
        assert results["generated_tests"][0]["status"] == "success"
        assert len(results["integration_gaps"]) == 2

    def test_calculate_quality_metrics(self, qa_agent):
        """Test quality metrics calculation."""
        test_results = {
            "generated_tests": [
                {"status": "success", "test_count": 5},
                {"status": "success", "test_count": 3},
                {"status": "error", "test_count": 0}
            ],
            "coverage_analysis": {
                "overall_quality_score": 80,
                "improvement_potential": 20
            },
            "integration_gaps": ["gap1", "gap2"]
        }
        metrics = qa_agent._calculate_quality_metrics(test_results)

        assert abs(metrics["test_generation_success_rate"] -
                   (200 / 3)) < 0.01  # 2 success out of 3
        assert metrics["estimated_coverage_improvement"] == 20
        assert metrics["integration_gap_count"] == 2
        assert metrics["total_generated_tests"] == 8
        assert metrics["files_with_tests"] == 2
        assert metrics["total_source_files"] == 3
        assert "quality_score" in metrics

    def test_calculate_overall_quality_score(self, qa_agent):
        """Test overall quality score calculation."""
        results = {
            "quality_metrics": {"test_generation_success_rate": 80},
            "coverage_analysis": {"overall_quality_score": 75},
            "integration_gaps": ["gap1", "gap2", "gap3"]
        }

        score = qa_agent._calculate_overall_quality_score(results)

        # Should be a weighted combination of test success, coverage, and
        # integration
        assert 0 <= score <= 100
        assert isinstance(score, float)

    def test_generate_recommendations(self, qa_agent):
        """Test recommendation generation."""
        results = {
            "generated_tests": [
                {"status": "success"},
                {"status": "error", "error": "Parse error"}
            ],
            "coverage_analysis": {"overall_quality_score": 60},
            "integration_gaps": ["gap1", "gap2", "gap3", "gap4", "gap5", "gap6"],
            "quality_metrics": {"quality_score": 65}
        }

        recommendations = qa_agent._generate_recommendations(results)

        # Should have multiple recommendations
        assert len(recommendations) >= 3
        assert any("test generation errors" in rec for rec in recommendations)
        assert any("test coverage" in rec for rec in recommendations)
        assert any("integration gaps" in rec for rec in recommendations)
        assert any("quality score" in rec for rec in recommendations)

    def test_validate_quality_gates(self, qa_agent):
        """Test quality gates validation."""
        results = {
            "quality_metrics": {
                "test_generation_success_rate": 85,
                "integration_gap_count": 3,
                "quality_score": 80
            }
        }

        validation = qa_agent.validate_quality_gates(results)

        assert "overall_status" in validation
        assert "gates" in validation
        assert "summary" in validation

        gates = validation["gates"]
        assert "coverage_gate" in gates
        assert "integration_gate" in gates
        assert "overall_quality_gate" in gates

        # Check gate structure
        for gate_name, gate_data in gates.items():
            assert "passed" in gate_data
            assert "current" in gate_data
            assert "threshold" in gate_data
            assert isinstance(gate_data["passed"], bool)

    def test_validate_quality_gates_failure(self, qa_agent):
        """Test quality gates validation with failures."""
        results = {
            "quality_metrics": {
                "test_generation_success_rate": 60,  # Below threshold
                "integration_gap_count": 15,  # Above threshold
                "quality_score": 50  # Below threshold
            }
        }

        validation = qa_agent.validate_quality_gates(results)

        assert validation["overall_status"] == "FAILED"
        assert not validation["gates"]["coverage_gate"]["passed"]
        assert not validation["gates"]["integration_gate"]["passed"]
        assert not validation["gates"]["overall_quality_gate"]["passed"]


class TestQAWorkflowIntegration:
    """Integration tests for QA workflow."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)

        # Create sample source files with different patterns
        (project_path / "src").mkdir()
        (project_path / "src" / "models.py").write_text("""
class UserModel:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def validate_email(self):
        return "@" in self.email

    def get_display_name(self):
        return f"{self.name} <{self.email}>"

def create_user(name, email):
    return UserModel(name, email)
""")

        yield project_path
        shutil.rmtree(temp_dir)

    def test_create_enhanced_qa_workflow(self, temp_project):
        """Test creating enhanced QA workflow."""
        workflow = create_enhanced_qa_workflow(str(temp_project))

        assert isinstance(workflow, EnhancedQAAgent)
        assert workflow.project_root == temp_project

    @patch('utils.test_generator.QATestGenerator.generate_test_file')
    def test_end_to_end_test_generation(self, mock_generate, temp_project):
        """Test end-to-end test generation workflow."""
        # Mock test file generation to return realistic content
        mock_generate.return_value = """
import pytest
from models import UserModel, create_user

class TestUserModel:
    def test_user_model_instantiation(self):
        user = UserModel("John Doe", "john@example.com")
        assert user.name == "John Doe"
        assert user.email == "john@example.com"

    def test_validate_email(self):
        user = UserModel("John", "john@example.com")
        assert user.validate_email() == True

    def test_get_display_name(self):
        user = UserModel("John", "john@example.com")
        assert user.get_display_name() == "John <john@example.com>"

def test_create_user():
    user = create_user("Jane", "jane@example.com")
    assert isinstance(user, UserModel)
"""

        qa_agent = EnhancedQAAgent(str(temp_project))

        # Mock the coverage and integration analyzers to avoid complex setup
        with patch.object(qa_agent.coverage_analyzer, 'analyze_coverage_patterns') as mock_coverage:
            with patch.object(qa_agent.integration_analyzer, 'analyze_project') as mock_integration:
                mock_coverage.return_value = {
                    "overall_quality_score": 85,
                    "improvement_potential": 15,
                    "patterns": []
                }
                mock_integration.return_value = {"gaps": []}

                results = qa_agent.generate_comprehensive_tests()

        assert "generated_tests" in results
        assert "quality_metrics" in results
        assert "recommendations" in results

        # Should have attempted to generate tests for discovered source files
        assert len(results["generated_tests"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
