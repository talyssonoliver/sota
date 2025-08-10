"""
Comprehensive tests for EnhancedQAAgent functionality.

Tests the enhanced QA agent for comprehensive testing and analysis capabilities
including test generation, coverage analysis, quality metrics calculation,
and quality gates validation.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

try:
    from src.core.agents.qa import EnhancedQAAgent, create_enhanced_qa_workflow
except ImportError:
    EnhancedQAAgent = None
    create_enhanced_qa_workflow = None


@pytest.mark.skipif(EnhancedQAAgent is None, reason="EnhancedQAAgent not available")
class TestEnhancedQAAgent:
    """Test the EnhancedQAAgent class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.qa_agent = EnhancedQAAgent(project_root=self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_enhanced_qa_agent_initialization(self):
        """Test EnhancedQAAgent initialization."""
        assert self.qa_agent is not None
        assert self.qa_agent.project_root == Path(self.temp_dir)
        assert self.qa_agent.config_path is None
        assert hasattr(self.qa_agent, 'test_generator')
        assert hasattr(self.qa_agent, 'coverage_analyzer')
        assert hasattr(self.qa_agent, 'integration_analyzer')
        assert hasattr(self.qa_agent, 'config')
        
        # Check default configuration
        assert 'coverage_thresholds' in self.qa_agent.config
        assert 'quality_gates' in self.qa_agent.config
        assert 'test_patterns' in self.qa_agent.config

    def test_enhanced_qa_agent_with_config_path(self):
        """Test EnhancedQAAgent initialization with custom config."""
        # Create temporary config file
        config_file = Path(self.temp_dir) / "qa_config.json"
        custom_config = {
            "coverage_thresholds": {"line_coverage": 90, "branch": 80},
            "quality_gates": {"min_test_coverage": 90}
        }
        config_file.write_text(json.dumps(custom_config))
        
        qa_agent = EnhancedQAAgent(
            project_root=self.temp_dir, 
            config_path=str(config_file)
        )
        
        assert qa_agent.config["coverage_thresholds"]["line_coverage"] == 90
        assert qa_agent.config["quality_gates"]["min_test_coverage"] == 90

    def test_enhanced_qa_agent_with_invalid_config(self):
        """Test EnhancedQAAgent with invalid config file."""
        # Create invalid config file
        config_file = Path(self.temp_dir) / "invalid_config.json"
        config_file.write_text("invalid json content")
        
        # Should handle invalid config gracefully
        qa_agent = EnhancedQAAgent(
            project_root=self.temp_dir,
            config_path=str(config_file)
        )
        
        # Should fall back to default config
        assert qa_agent.config["coverage_thresholds"]["line_coverage"] == 80

    def test_discover_source_files(self):
        """Test discover_source_files method."""
        # Create sample source files
        (Path(self.temp_dir) / "main.py").write_text("def main(): pass")
        (Path(self.temp_dir) / "utils.js").write_text("function utils() {}")
        (Path(self.temp_dir) / "component.ts").write_text("export class Component {}")
        (Path(self.temp_dir) / "README.md").write_text("# Documentation")
        
        # Create test file (should be excluded)
        (Path(self.temp_dir) / "test_main.py").write_text("def test_main(): pass")
        
        source_files = self.qa_agent.discover_source_files()
        
        assert isinstance(source_files, list)
        assert len(source_files) == 3  # Should find 3 source files, excluding test file
        
        # Check that found files are source files
        found_names = [Path(f).name for f in source_files]
        assert "main.py" in found_names
        assert "utils.js" in found_names
        assert "component.ts" in found_names
        assert "test_main.py" not in found_names
        assert "README.md" not in found_names

    def test_determine_test_framework_python(self):
        """Test determine_test_framework for Python files."""
        # Test with Python file extension
        framework = self.qa_agent.determine_test_framework("test_module.py")
        # Handle both enum and string returns
        framework_value = framework.value if hasattr(framework, 'value') else framework
        assert framework_value == "pytest"
        
        # Test with language string
        framework = self.qa_agent.determine_test_framework("python")
        framework_value = framework.value if hasattr(framework, 'value') else framework
        assert framework_value == "pytest"

    def test_determine_test_framework_javascript(self):
        """Test determine_test_framework for JavaScript files."""
        # Test with JavaScript file extension
        framework = self.qa_agent.determine_test_framework("component.js")
        # Handle both enum and string returns
        framework_value = framework.value if hasattr(framework, 'value') else framework
        assert framework_value == "jest"
        
        # Test with language string
        framework = self.qa_agent.determine_test_framework("javascript")
        framework_value = framework.value if hasattr(framework, 'value') else framework
        assert framework_value == "jest"

    def test_get_test_file_path_pytest(self):
        """Test get_test_file_path for pytest framework."""
        source_file = "src/module.py"
        test_path = self.qa_agent.get_test_file_path(source_file, "pytest")
        
        assert isinstance(test_path, Path)
        assert test_path.name == "test_module.py"
        assert "tests" in test_path.parts and "generated" in test_path.parts

    def test_get_test_file_path_jest(self):
        """Test get_test_file_path for Jest framework."""
        source_file = "src/component.js"
        test_path = self.qa_agent.get_test_file_path(source_file, "jest")
        
        assert isinstance(test_path, Path)
        assert test_path.name == "component.test.js"
        assert "tests" in test_path.parts and "generated" in test_path.parts

    def test_calculate_quality_metrics_with_source_files(self):
        """Test calculate_quality_metrics with source files."""
        # Create sample source files
        source_files = []
        for i in range(3):
            file_path = Path(self.temp_dir) / f"module{i}.py"
            file_path.write_text(f"def function{i}(): return {i}")
            source_files.append(str(file_path))
        
        metrics = self.qa_agent.calculate_quality_metrics(source_files)
        
        assert isinstance(metrics, dict)
        assert "test_coverage" in metrics
        assert "code_quality" in metrics
        assert "complexity" in metrics
        assert "duplication" in metrics
        assert "quality_score" in metrics
        
        # Values should be reasonable
        assert 0 <= metrics["test_coverage"] <= 100
        assert 0 <= metrics["code_quality"] <= 100
        assert metrics["complexity"] >= 0
        assert metrics["duplication"] >= 0

    def test_calculate_quality_metrics_empty_files(self):
        """Test calculate_quality_metrics with empty file list."""
        metrics = self.qa_agent.calculate_quality_metrics([])
        
        assert isinstance(metrics, dict)
        assert metrics["test_coverage"] == 0.0
        assert metrics["code_quality"] == 0.0
        assert metrics["complexity"] == 10.0
        assert metrics["duplication"] == 0.0

    def test_calculate_overall_quality_score(self):
        """Test calculate_overall_quality_score method."""
        # Test with metrics dict
        metrics = {
            "test_coverage": 80.0,
            "code_quality": 90.0,
            "complexity": 5.0,
            "duplication": 2.0
        }
        
        score = self.qa_agent.calculate_overall_quality_score(metrics)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
        assert score > 50  # Should be reasonably high for good metrics

    def test_calculate_overall_quality_score_with_results(self):
        """Test calculate_overall_quality_score with test results format."""
        # Test with full results format
        results = {
            "generated_tests": [
                {"status": "success"},
                {"status": "success"},
                {"status": "error"}
            ],
            "coverage_analysis": {"overall_quality_score": 85}
        }
        
        score = self.qa_agent.calculate_overall_quality_score(results)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_generate_recommendations_with_metrics(self):
        """Test generate_recommendations with metrics format."""
        # Test with low coverage
        low_coverage_metrics = {
            "test_coverage": 60.0,  # Below threshold of 80
            "complexity": 15.0,     # Above threshold of 10
            "duplication": 8.0      # Above threshold of 5
        }
        
        recommendations = self.qa_agent.generate_recommendations(low_coverage_metrics)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) >= 3  # Should have recommendations for all issues
        
        rec_text = " ".join(recommendations)
        assert "coverage" in rec_text.lower()
        assert "complexity" in rec_text.lower()
        assert "duplication" in rec_text.lower()

    def test_generate_recommendations_with_good_metrics(self):
        """Test generate_recommendations with good metrics."""
        good_metrics = {
            "test_coverage": 95.0,  # Above threshold
            "complexity": 3.0,      # Below threshold
            "duplication": 1.0      # Below threshold
        }
        
        recommendations = self.qa_agent.generate_recommendations(good_metrics)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) == 1
        assert "meets all standards" in recommendations[0].lower()

    def test_validate_quality_gates_passing(self):
        """Test validate_quality_gates with passing metrics."""
        passing_metrics = {
            "test_coverage": 85.0,      # Above 80 threshold
            "complexity": 5.0,          # Below 10 threshold
            "duplication": 3.0,         # Below 5 threshold
            "integration_coverage": 75.0, # Above 70 threshold
            "overall_score": 85.0       # Above 80 threshold
        }
        
        result = self.qa_agent.validate_quality_gates(passing_metrics)
        
        assert isinstance(result, dict)
        assert result["passed"] is True
        assert result["overall_status"] == "PASSED"
        assert "gate_results" in result
        assert "summary" in result
        
        # All gates should pass
        for gate_name, gate_result in result["gate_results"].items():
            assert gate_result["passed"] is True

    def test_validate_quality_gates_failing(self):
        """Test validate_quality_gates with failing metrics."""
        failing_metrics = {
            "test_coverage": 60.0,      # Below 80 threshold
            "complexity": 15.0,         # Above 10 threshold
            "duplication": 8.0,         # Above 5 threshold
            "integration_coverage": 50.0, # Below 70 threshold
            "overall_score": 60.0       # Below 80 threshold
        }
        
        result = self.qa_agent.validate_quality_gates(failing_metrics)
        
        assert isinstance(result, dict)
        assert result["passed"] is False
        assert result["overall_status"] == "FAILED"
        
        # Should have failed gates
        failed_gates = [
            gate for gate, details in result["gate_results"].items()
            if not details["passed"]
        ]
        assert len(failed_gates) > 0

    @patch('src.core.agents.qa.EnhancedQAAgent._generate_test_for_file')
    def test_generate_comprehensive_tests_success(self, mock_generate):
        """Test generate_comprehensive_tests with successful generation."""
        # Mock test generation
        mock_generate.return_value = {
            "source_file": "test.py",
            "test_file": "test_test.py",
            "status": "success",
            "test_count": 5
        }
        
        # Create sample source file
        source_file = Path(self.temp_dir) / "test.py"
        source_file.write_text("def test_func(): pass")
        
        result = self.qa_agent.generate_comprehensive_tests([str(source_file)])
        
        assert isinstance(result, dict)
        assert "generated_tests" in result
        assert "test_files" in result
        assert "coverage_analysis" in result
        assert "integration_gaps" in result
        assert "quality_metrics" in result
        assert "recommendations" in result
        
        # Should have generated tests
        assert len(result["generated_tests"]) == 1
        assert result["generated_tests"][0]["status"] == "success"

    def test_generate_comprehensive_tests_auto_discovery(self):
        """Test generate_comprehensive_tests with auto source file discovery."""
        # Create sample source files
        (Path(self.temp_dir) / "module1.py").write_text("def func1(): pass")
        (Path(self.temp_dir) / "module2.py").write_text("def func2(): pass")
        
        # Call without source files (should auto-discover)
        result = self.qa_agent.generate_comprehensive_tests(source_files=None)
        
        assert isinstance(result, dict)
        assert "generated_tests" in result
        assert len(result["generated_tests"]) == 2  # Should find 2 files

    def test_generate_comprehensive_tests_empty_files(self):
        """Test generate_comprehensive_tests with empty file list."""
        result = self.qa_agent.generate_comprehensive_tests([])
        
        assert isinstance(result, dict)
        assert "generated_tests" in result
        assert len(result["generated_tests"]) == 0

    def test_fallback_test_generator_creation(self):
        """Test fallback test generator creation."""
        fallback = self.qa_agent._create_fallback_test_generator()
        
        assert hasattr(fallback, 'detect_language')
        assert hasattr(fallback, 'detect_framework')
        assert hasattr(fallback, 'generate_test_file')
        
        # Test language detection
        assert fallback.detect_language("test.py") == "python"
        assert fallback.detect_language("test.js") == "javascript"
        
        # Test framework detection
        assert fallback.detect_framework("python") == "pytest"
        assert fallback.detect_framework("javascript") == "jest"
        
        # Test test file generation
        test_content = fallback.generate_test_file("test.py")
        assert isinstance(test_content, str)
        assert "pytest" in test_content

    def test_fallback_coverage_analyzer_creation(self):
        """Test fallback coverage analyzer creation."""
        fallback = self.qa_agent._create_fallback_coverage_analyzer()
        
        assert hasattr(fallback, 'analyze_coverage')
        
        # Test coverage analysis
        result = fallback.analyze_coverage(["file1.py", "file2.py"])
        assert isinstance(result, dict)
        assert "line_coverage" in result
        assert "branch_coverage" in result
        assert "files_analyzed" in result
        assert result["files_analyzed"] == 2

    def test_fallback_integration_analyzer_creation(self):
        """Test fallback integration analyzer creation."""
        fallback = self.qa_agent._create_fallback_integration_analyzer()
        
        assert hasattr(fallback, 'analyze_integrations')
        assert hasattr(fallback, 'analyze_project')
        
        # Test integration analysis
        result = fallback.analyze_integrations(["comp1", "comp2"])
        assert isinstance(result, dict)
        assert "integration_coverage" in result
        assert "issues" in result
        assert "components_analyzed" in result
        
        # Test project analysis
        project_result = fallback.analyze_project()
        assert isinstance(project_result, dict)
        assert "gaps" in project_result

    def test_backwards_compatibility_methods(self):
        """Test backwards compatibility underscore-prefixed methods."""
        # Test that underscore methods work as aliases
        source_files = self.qa_agent._discover_source_files()
        assert isinstance(source_files, list)
        
        framework = self.qa_agent._determine_test_framework("python")
        framework_value = framework.value if hasattr(framework, 'value') else framework
        assert framework_value == "pytest"
        
        test_path = self.qa_agent._get_test_file_path("test.py", "pytest")
        assert isinstance(test_path, Path)

    def test_quality_metrics_calculation_integration(self):
        """Test integration of quality metrics calculation."""
        # Create realistic test results
        test_results = {
            "generated_tests": [
                {"status": "success", "test_count": 3},
                {"status": "success", "test_count": 2},
                {"status": "error", "test_count": 0}
            ],
            "coverage_analysis": {"overall_quality_score": 82},
            "integration_gaps": ["gap1", "gap2"]
        }
        
        metrics = self.qa_agent._calculate_quality_metrics(test_results)
        
        assert isinstance(metrics, dict)
        assert "test_generation_success_rate" in metrics
        assert "estimated_coverage_improvement" in metrics
        assert "integration_gap_count" in metrics
        assert "total_generated_tests" in metrics
        assert "quality_score" in metrics
        
        # Check calculated values
        assert metrics["test_generation_success_rate"] == (2/3) * 100  # 2 success / 3 total
        assert metrics["integration_gap_count"] == 2
        assert metrics["total_generated_tests"] == 5  # 3 + 2 + 0


@pytest.mark.skipif(create_enhanced_qa_workflow is None, reason="create_enhanced_qa_workflow not available")
class TestCreateEnhancedQAWorkflow:
    """Test the create_enhanced_qa_workflow function."""

    def test_create_enhanced_qa_workflow_success(self):
        """Test successful creation of enhanced QA workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = create_enhanced_qa_workflow(temp_dir)
            
            assert isinstance(result, dict)
            assert result["status"] == "initialized"
            assert "agent" in result
            assert "capabilities" in result
            
            # Check capabilities
            expected_capabilities = [
                "test_generation",
                "coverage_analysis", 
                "quality_metrics"
            ]
            assert set(result["capabilities"]) == set(expected_capabilities)
            
            # Check agent is properly initialized
            agent = result["agent"]
            assert hasattr(agent, 'project_root')
            assert agent.project_root == Path(temp_dir)

    def test_create_enhanced_qa_workflow_with_config(self):
        """Test creation with custom config path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config file
            config_file = Path(temp_dir) / "config.json"
            config_file.write_text('{"test": "value"}')
            
            result = create_enhanced_qa_workflow(temp_dir, str(config_file))
            
            assert result["status"] == "initialized"
            assert "agent" in result


class TestEnhancedQAAgentIntegration:
    """Test integration scenarios for EnhancedQAAgent."""

    def test_full_qa_workflow_integration(self):
        """Test complete QA workflow integration."""
        if EnhancedQAAgent is None:
            pytest.skip("EnhancedQAAgent not available")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create realistic project structure
            src_dir = Path(temp_dir) / "src"
            src_dir.mkdir()
            
            # Create sample Python files
            (src_dir / "user_service.py").write_text("""
class UserService:
    def __init__(self):
        self.users = {}
    
    def create_user(self, name, email):
        if not name or not email:
            raise ValueError("Name and email required")
        user_id = len(self.users) + 1
        self.users[user_id] = {"name": name, "email": email}
        return user_id
    
    def validate_email(self, email):
        return "@" in email and "." in email
""")
            
            (src_dir / "auth_service.py").write_text("""
def authenticate_user(username, password):
    if not username or not password:
        return False
    # Mock authentication logic
    return username == "admin" and password == "secret"

def hash_password(password):
    import hashlib
    return hashlib.md5(password.encode(), usedforsecurity=False).hexdigest()
""")
            
            # Initialize QA agent
            qa_agent = EnhancedQAAgent(project_root=temp_dir)
            
            # Run comprehensive test generation
            result = qa_agent.generate_comprehensive_tests()
            
            # Verify comprehensive results
            assert isinstance(result, dict)
            assert "generated_tests" in result
            assert "coverage_analysis" in result
            assert "quality_metrics" in result
            assert "recommendations" in result
            
            # Should have generated tests for both files
            assert len(result["generated_tests"]) >= 2
            
            # Calculate quality metrics
            metrics = qa_agent.calculate_quality_metrics([
                str(src_dir / "user_service.py"),
                str(src_dir / "auth_service.py")
            ])
            
            # Validate quality gates
            gate_results = qa_agent.validate_quality_gates(metrics)
            
            assert isinstance(gate_results, dict)
            assert "passed" in gate_results
            assert "overall_status" in gate_results

    def test_qa_agent_error_handling(self):
        """Test QA agent error handling and resilience."""
        if EnhancedQAAgent is None:
            pytest.skip("EnhancedQAAgent not available")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            qa_agent = EnhancedQAAgent(project_root=temp_dir)
            
            # Test with non-existent files
            result = qa_agent.generate_comprehensive_tests(["/nonexistent/file.py"])
            assert isinstance(result, dict)
            assert "generated_tests" in result
            
            # Test with empty metrics
            metrics = qa_agent.calculate_quality_metrics([])
            assert isinstance(metrics, dict)
            
            # Test quality gates with missing data
            gate_results = qa_agent.validate_quality_gates({})
            assert isinstance(gate_results, dict)
            assert "passed" in gate_results

    def test_qa_agent_with_various_file_types(self):
        """Test QA agent with different source file types."""
        if EnhancedQAAgent is None:
            pytest.skip("EnhancedQAAgent not available")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files of different types
            (Path(temp_dir) / "script.py").write_text("def main(): print('hello')")
            (Path(temp_dir) / "app.js").write_text("function app() { return 'app'; }")
            (Path(temp_dir) / "component.ts").write_text("export class Component {}")
            (Path(temp_dir) / "service.java").write_text("public class Service {}")
            
            qa_agent = EnhancedQAAgent(project_root=temp_dir)
            
            # Discover files
            source_files = qa_agent.discover_source_files()
            
            # Should find multiple file types
            assert len(source_files) >= 3  # py, js, ts, java
            
            # Test framework detection for different languages
            py_framework = qa_agent.determine_test_framework("test.py")
            js_framework = qa_agent.determine_test_framework("test.js")
            
            py_framework_value = py_framework.value if hasattr(py_framework, 'value') else py_framework
            js_framework_value = js_framework.value if hasattr(js_framework, 'value') else js_framework
            assert py_framework_value == "pytest"
            assert js_framework_value == "jest"
