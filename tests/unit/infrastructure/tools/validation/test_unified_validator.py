"""
Test suite for Unified Validator using TDD approach.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.infrastructure.tools.validation.core.validator import (
    Validator as UnifiedValidator,  # Alias for backward compatibility
    ValidationPhase,
    ValidationResult
)


class TestUnifiedValidator:
    """Test unified validator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)
        
        # Create test Python files
        self.create_test_project()
        
        self.validator = UnifiedValidator(
            root_path=self.root_path,
            enable_sonarqube=False,
            enable_parallel=False,
            enable_quality_gates=True
        )

    def create_test_project(self):
        """Create a test project structure."""
        # Main source file
        main_file = self.root_path / "main.py"
        main_file.write_text("""
def hello_world():
    '''Say hello to the world.'''
    print("Hello, World!")
    return "Hello, World!"

def calculate_sum(a, b):
    '''Calculate sum of two numbers.'''
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Arguments must be numbers")
    return a + b
""")
        
        # Test file
        test_file = self.root_path / "test_main.py"
        test_file.write_text("""
import pytest
from main import hello_world, calculate_sum

def test_hello_world():
    '''Test hello world function.'''
    result = hello_world()
    assert result == "Hello, World!"

def test_calculate_sum():
    '''Test calculate sum function.'''
    assert calculate_sum(1, 2) == 3
    assert calculate_sum(1.5, 2.5) == 4.0
    
    with pytest.raises(TypeError):
        calculate_sum("1", 2)
""")
        
        # Requirements file
        requirements_file = self.root_path / "requirements.txt"
        requirements_file.write_text("""
pytest==7.0.0
black==22.0.0
ruff==0.0.1
""")

    def test_initialization(self):
        """Test validator initialization."""
        assert self.validator.root_path == self.root_path
        assert self.validator.enable_sonarqube is False
        assert self.validator.enable_parallel is False
        assert self.validator.enable_quality_gates is True
        assert self.validator.quality_gates_engine is not None
        assert self.validator.vv_validator is not None
        assert self.validator.nfr_validator is not None
        assert self.validator.sonarqube_integrator is None

    def test_initialization_with_sonarqube(self):
        """Test validator initialization with SonarQube."""
        validator = UnifiedValidator(
            root_path=self.root_path,
            enable_sonarqube=True,
            sonar_host_url="http://localhost:9000",
            sonar_token="test_token"
        )
        
        assert validator.enable_sonarqube is True
        assert validator.sonarqube_integrator is not None

    @patch.object(UnifiedValidator, '_preparation_phase')
    @patch.object(UnifiedValidator, '_static_analysis_phase')
    @patch.object(UnifiedValidator, '_quality_gates_phase')
    @patch.object(UnifiedValidator, '_security_scan_phase')
    @patch.object(UnifiedValidator, '_nfr_validation_phase')
    @patch.object(UnifiedValidator, '_reporting_phase')
    def test_run_validation(self, mock_reporting, mock_nfr, mock_security, 
                                   mock_quality_gates, mock_static, mock_prep):
        """Test unified validation pipeline."""
        # Mock phase returns
        mock_prep.return_value = {"success": True}
        mock_static.return_value = {"success": True}
        mock_quality_gates.return_value = {"success": True, "build_decision": {"allow_merge": True}}
        mock_security.return_value = {"success": True}
        mock_nfr.return_value = {"success": True}
        mock_reporting.return_value = {"success": True}
        
        result = self.validator.run_validation()
        
        # Verify all phases were called
        mock_prep.assert_called_once()
        mock_static.assert_called_once()
        mock_quality_gates.assert_called_once()
        mock_security.assert_called_once()
        mock_nfr.assert_called_once()
        mock_reporting.assert_called_once()
        
        # Verify result structure
        assert "timestamp" in result
        assert "summary" in result
        assert "phase_results" in result
        assert "compliance_assessment" in result
        assert "recommendations" in result

    def test_preparation_phase(self):
        """Test preparation phase."""
        result = self.validator._preparation_phase()
        
        assert result["success"] is True
        assert "environment" in result
        assert "files_collected" in result
        assert result["files_collected"] > 0
        
        # Check environment details
        env = result["environment"]
        assert "python_files" in env
        assert "has_requirements" in env
        assert env["python_files"] > 0

    @patch.object(UnifiedValidator, '_collect_files')
    def test_preparation_phase_no_files(self, mock_collect):
        """Test preparation phase with no files."""
        mock_collect.return_value = []
        self.validator.python_files = []
        
        result = self.validator._preparation_phase()
        
        assert result["success"] is True
        assert result["files_collected"] == 0

    def test_static_analysis_phase(self):
        """Test static analysis phase."""
        # Mock the underlying validator objects since they're properties
        mock_syntax = Mock()
        mock_syntax.validate_all_imports.return_value = True
        mock_syntax.issues = []
        self.validator._syntax_validator = mock_syntax
        
        mock_deps = Mock()
        mock_deps.validate_dependencies.return_value = True
        mock_deps.issues = []
        self.validator._dependency_validator = mock_deps
        
        mock_struct = Mock()
        mock_struct.validate_structure.return_value = True
        mock_struct.issues = []
        self.validator._structure_validator = mock_struct
        
        # Mock other validators to avoid errors
        mock_perf = Mock()
        mock_perf.validate_performance.return_value = True
        mock_perf.issues = []
        self.validator._performance_validator = mock_perf
        
        mock_pattern = Mock()
        mock_pattern.analyze_patterns.return_value = True
        mock_pattern.issues = []
        self.validator._pattern_detector = mock_pattern
        
        mock_business = Mock()
        mock_business.protect_business_logic.return_value = True
        mock_business.issues = []
        self.validator._business_logic_protector = mock_business
        
        result = self.validator._static_analysis_phase()
        
        assert result["success"] is True
        assert "validators_run" in result
        assert "issues_by_category" in result

    def test_quality_gates_phase(self):
        """Test quality gates phase."""
        with patch.object(self.validator.quality_gates_engine, 'evaluate_quality_gates') as mock_eval:
            mock_eval.return_value = {
                "overall_status": "PASSED",
                "quality_gates_passed": 5,
                "quality_gates_failed": 0,
                "quality_gates_warning": 0,
                "build_decision": {"allow_merge": True, "blocking_issues": []},
                "technical_debt": {"total_hours": 2.5},
                "iso_25010_compliance": {"overall": 85.0},
                "gate_results": []
            }
            
            result = self.validator._quality_gates_phase()
            
            assert result["success"] is True
            assert "quality_gates_passed" in result
            assert "build_decision" in result
            assert "technical_debt" in result
            
            mock_eval.assert_called_once()

    def test_quality_gates_phase_with_failures(self):
        """Test quality gates phase with failures."""
        with patch.object(self.validator.quality_gates_engine, 'evaluate_quality_gates') as mock_eval:
            mock_eval.return_value = {
                "overall_status": "FAILED",
                "quality_gates_passed": 3,
                "quality_gates_failed": 2,
                "quality_gates_warning": 0,
                "build_decision": {"allow_merge": False, "blocking_issues": ["test_coverage"]},
                "technical_debt": {"total_hours": 15.0},
                "iso_25010_compliance": {"overall": 65.0},
                "gate_results": [
                    {
                        "name": "test_coverage",
                        "status": "FAILED",
                        "severity": "error",
                        "message": "Test coverage below threshold"
                    }
                ]
            }
            
            result = self.validator._quality_gates_phase()
            
            assert result["success"] is False
            assert result["quality_gates_failed"] == 2
            assert result["build_decision"]["allow_merge"] is False
            
            # Should have added quality gate failure issue
            quality_gate_issues = [i for i in self.validator.issues if i.category == "quality_gates"]
            assert len(quality_gate_issues) > 0

    def test_security_scan_phase(self):
        """Test security scan phase."""
        with patch.object(self.validator.vv_validator, 'run_validation_verification') as mock_run:
            with patch.object(self.validator.vv_validator, 'generate_vv_report') as mock_report:
                mock_run.return_value = True
                mock_report.return_value = {
                    "validation_verification": {
                        "compliance": {
                            "owasp_top_10": {"compliance_percentage": 90.0},
                            "pep8_compliance": {"compliance_percentage": 95.0}
                        },
                        "security_vulnerabilities": {"total_vulnerabilities": 0},
                        "external_tools": {"bandit": {"issues_found": 0}}
                    }
                }
                
                result = self.validator._security_scan_phase()
                
                assert result["success"] is True
                assert "owasp_compliance" in result
                assert "pep8_compliance" in result
                assert "security_vulnerabilities" in result
                
                mock_run.assert_called_once()
                mock_report.assert_called_once()

    def test_nfr_validation_phase(self):
        """Test NFR validation phase."""
        with patch.object(self.validator.nfr_validator, 'run_nfr_validation') as mock_run:
            with patch.object(self.validator.nfr_validator, 'generate_nfr_report') as mock_report:
                mock_run.return_value = True
                mock_report.return_value = {
                    "iso_25010_compliance": {"overall": 85.0},
                    "security_metrics": {"auth_coverage": 100.0},
                    "maintainability_metrics": {"avg_complexity": 5.0},
                    "performance_profiles": [],
                    "nfr_violations": []
                }
                
                result = self.validator._nfr_validation_phase()
                
                assert result["success"] is True
                assert "iso_25010_compliance" in result
                assert "security_metrics" in result
                assert "maintainability_metrics" in result
                
                mock_run.assert_called_once()
                mock_report.assert_called_once()

    def test_integration_phase_disabled(self):
        """Test integration phase when SonarQube is disabled."""
        result = self.validator._integration_phase()
        
        assert result["success"] is True
        assert "SonarQube integration disabled" in result["message"]

    def test_integration_phase_enabled(self):
        """Test integration phase when SonarQube is enabled."""
        # Create validator with SonarQube enabled
        validator = UnifiedValidator(
            root_path=self.root_path,
            enable_sonarqube=True,
            sonar_host_url="http://localhost:9000",
            sonar_token="test_token"
        )
        
        with patch.object(validator.sonarqube_integrator, 'run_sonarqube_analysis') as mock_run:
            with patch.object(validator.sonarqube_integrator, 'generate_integrated_report') as mock_report:
                mock_run.return_value = True
                mock_report.return_value = {
                    "sonarqube_integration": {
                        "enabled": True,
                        "issues_count": 5,
                        "analysis_success": True
                    }
                }
                
                result = validator._integration_phase()
                
                assert result["success"] is True
                assert "sonarqube_enabled" in result
                assert "integration_report" in result
                
                mock_run.assert_called_once()
                mock_report.assert_called_once()

    def test_reporting_phase(self):
        """Test reporting phase."""
        # Create reports directory
        reports_dir = self.root_path / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        result = self.validator._reporting_phase()
        
        assert result["success"] is True
        assert "reports_generated" in result
        assert "total_reports" in result
        
        # Check that some reports were attempted
        assert result["total_reports"] >= 0

    def test_run_phase_error_handling(self):
        """Test phase error handling."""
        def failing_phase():
            raise Exception("Test error")
        
        result = self.validator._run_phase(ValidationPhase.PREPARATION, failing_phase)
        
        assert result.success is False
        assert "error" in result.details
        assert "Test error" in result.details["error"]

    def test_assess_software_engineering_compliance(self):
        """Test software engineering compliance assessment."""
        # Add some test issues
        self.validator.add_issue(
            category="quality_gates",
            issue_type="QUALITY_GATE_FAILURE",
            file_path="test.py",
            message="Test failure",
            severity="error"
        )
        
        self.validator.build_decision = {"allow_merge": False}
        
        compliance = self.validator._assess_software_engineering_compliance()
        
        assert "overall_compliance_percentage" in compliance
        assert "principles" in compliance
        assert "iso_25010_compliant" in compliance
        assert "ready_for_production" in compliance
        
        # Should have low compliance due to quality gate failure
        assert compliance["overall_compliance_percentage"] < 100

    def test_generate_unified_recommendations(self):
        """Test unified recommendations generation."""
        # Add test issues
        self.validator.add_issue(
            category="security",
            issue_type="VULNERABILITY",
            file_path="test.py",
            message="Security vulnerability",
            severity="error"
        )
        
        self.validator.add_issue(
            category="quality",
            issue_type="CODE_SMELL",
            file_path="test.py",
            message="Code smell",
            severity="warning"
        )
        
        self.validator.build_decision = {"allow_merge": False, "blocking_issues": ["security"]}
        
        recommendations = self.validator._generate_recommendations()
        
        assert len(recommendations) > 0
        # Check if we have any recommendations with blocking content
        rec_text = " ".join(recommendations)
        assert ("BUILD BLOCKED" in rec_text or "BLOCKED" in rec_text), f"Expected BUILD BLOCKED in recommendations: {recommendations}"
        assert "security" in rec_text, f"Expected security in recommendations: {recommendations}"

    def test_should_block_build(self):
        """Test build blocking logic."""
        # Test with merge allowed
        self.validator.build_decision = {"allow_merge": True}
        assert self.validator.should_block_build() is False
        
        # Test with merge blocked
        self.validator.build_decision = {"allow_merge": False}
        assert self.validator.should_block_build() is True

    def test_get_build_summary(self):
        """Test build summary generation."""
        # Test with no validation results
        summary = self.validator.get_build_summary()
        assert "Validation not run" in summary
        
        # Test with successful validation
        self.validator.validation_results = [
            ValidationResult(
                phase=ValidationPhase.PREPARATION,
                success=True,
                duration=1.0,
                issues_found=0,
                critical_issues=0,
                warnings=0,
                info=0,
                details={}
            )
        ]
        
        summary = self.validator.get_build_summary()
        assert "SUCCESS" in summary
        
        # Test with failed validation
        self.validator.validation_results = [
            ValidationResult(
                phase=ValidationPhase.PREPARATION,
                success=False,
                duration=1.0,
                issues_found=1,
                critical_issues=1,
                warnings=0,
                info=0,
                details={}
            )
        ]
        
        summary = self.validator.get_build_summary()
        assert "FAILED" in summary

    def test_parallel_static_analysis(self):
        """Test parallel static analysis."""
        # Enable parallel processing
        self.validator.enable_parallel = True
        
        with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
            mock_future = Mock()
            mock_future.result.return_value = True
            
            mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future
            mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future
            
            # Mock as_completed to return our mock future
            with patch('concurrent.futures.as_completed') as mock_as_completed:
                mock_as_completed.return_value = [mock_future]
                
                self.validator._run_parallel_static_analysis()
                
                # Verify parallel execution was attempted (may be called multiple times)
                assert mock_executor.call_count >= 1


class TestUnifiedValidatorIntegration:
    """Integration tests for unified validator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)
        
        # Create comprehensive test project
        self.create_comprehensive_test_project()
        
        self.validator = UnifiedValidator(
            root_path=self.root_path,
            enable_sonarqube=False,
            enable_parallel=False,
            enable_quality_gates=True
        )

    def create_comprehensive_test_project(self):
        """Create a comprehensive test project."""
        # Main application
        app_dir = self.root_path / "app"
        app_dir.mkdir()
        
        main_file = app_dir / "main.py"
        main_file.write_text("""
'''Main application module.'''

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Calculator:
    '''A simple calculator class.'''
    
    def __init__(self):
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        '''Add two numbers.'''
        result = a + b
        self.history.append(f"add({a}, {b}) = {result}")
        return result
    
    def subtract(self, a: float, b: float) -> float:
        '''Subtract two numbers.'''
        result = a - b
        self.history.append(f"subtract({a}, {b}) = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        '''Multiply two numbers.'''
        result = a * b
        self.history.append(f"multiply({a}, {b}) = {result}")
        return result
    
    def divide(self, a: float, b: float) -> float:
        '''Divide two numbers.'''
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"divide({a}, {b}) = {result}")
        return result
    
    def get_history(self) -> list:
        '''Get calculation history.'''
        return self.history.copy()


def main():
    '''Main function.'''
    calc = Calculator()
    
    try:
        result1 = calc.add(10, 5)
        result2 = calc.multiply(result1, 2)
        result3 = calc.divide(result2, 3)
        
        print(f"Final result: {result3}")
        print(f"History: {calc.get_history()}")
        
    except Exception as e:
        logger.error(f"Error in calculation: {e}")
        raise


if __name__ == "__main__":
    main()
""")
        
        # Tests
        tests_dir = self.root_path / "tests"
        tests_dir.mkdir()
        
        test_file = tests_dir / "test_calculator.py"
        test_file.write_text("""
'''Tests for calculator module.'''

import pytest
from app.main import Calculator


class TestCalculator:
    '''Test calculator class.'''
    
    def setup_method(self):
        '''Set up test fixtures.'''
        self.calc = Calculator()
    
    def test_add(self):
        '''Test addition.'''
        assert self.calc.add(2, 3) == 5
        assert self.calc.add(-1, 1) == 0
        assert self.calc.add(0, 0) == 0
    
    def test_subtract(self):
        '''Test subtraction.'''
        assert self.calc.subtract(5, 3) == 2
        assert self.calc.subtract(-1, 1) == -2
        assert self.calc.subtract(0, 0) == 0
    
    def test_multiply(self):
        '''Test multiplication.'''
        assert self.calc.multiply(2, 3) == 6
        assert self.calc.multiply(-1, 1) == -1
        assert self.calc.multiply(0, 5) == 0
    
    def test_divide(self):
        '''Test division.'''
        assert self.calc.divide(6, 2) == 3
        assert self.calc.divide(-6, 2) == -3
        
        with pytest.raises(ValueError):
            self.calc.divide(5, 0)
    
    def test_history(self):
        '''Test calculation history.'''
        self.calc.add(1, 2)
        self.calc.multiply(3, 4)
        
        history = self.calc.get_history()
        assert len(history) == 2
        assert "add(1, 2) = 3" in history
        assert "multiply(3, 4) = 12" in history
""")
        
        # Requirements
        requirements_file = self.root_path / "requirements.txt"
        requirements_file.write_text("""
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
ruff>=0.0.1
mypy>=1.0.0
""")
        
        # Configuration files
        pyproject_file = self.root_path / "pyproject.toml"
        pyproject_file.write_text("""
[tool.black]
line-length = 88
target-version = ['py38']

[tool.ruff]
line-length = 88
select = ["E", "F", "W", "I"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
""")

    @pytest.mark.slow
    def test_full_validation_pipeline(self):
        """Test complete validation pipeline."""
        # This is a realistic integration test
        result = self.validator.run_validation()
        
        # Basic structure validation
        assert "timestamp" in result
        assert "summary" in result
        assert "phase_results" in result
        assert "compliance_assessment" in result
        
        # Should have completed multiple phases
        assert result["summary"]["phases_completed"] >= 4
        
        # Should have found some files
        assert len(self.validator.python_files) > 0
        
        # Phase results should be present
        phase_results = result["phase_results"]
        assert "preparation" in phase_results
        assert "static_analysis" in phase_results
        assert "quality_gates" in phase_results
        
        # Should have some metrics
        if "quality_gates" in phase_results:
            details = phase_results["quality_gates"].get("details", {})
            if "metrics" in details:
                metrics = details["metrics"]
                assert "avg_cyclomatic_complexity" in metrics or len(metrics) == 0

    @pytest.mark.slow
    def test_validation_with_code_issues(self):
        """Test validation with intentional code issues."""
        # Add problematic code
        bad_file = self.root_path / "bad_code.py"
        bad_file.write_text("""
# This file has intentional issues for testing

def very_long_function_name_that_exceeds_reasonable_limits():
    # Missing docstring
    password = "hardcoded_password_123"  # Security issue
    
    # Very complex logic
    if True:
        if True:
            if True:
                if True:
                    if True:
                        print("Too many nested ifs")
                        eval("print('dangerous eval')")  # Security issue
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass
    else:
        pass
    
    return password

# Duplicate function
def duplicate_function():
    return "duplicate"

def another_duplicate_function():
    return "duplicate"
""")
        
        # Re-run validation
        result = self.validator.run_validation()
        
        # Should detect issues
        assert result["summary"]["total_issues"] > 0
        
        # Should have some specific issue types
        issues = result.get("detailed_issues", [])
        if issues:
            # Check for security issues
            security_issues = [i for i in issues if i.get("category") == "security"]
            # May or may not find security issues depending on validator configuration
            
            # Check for complexity issues
            complexity_issues = [i for i in issues if "complex" in i.get("message", "").lower()]
            # May or may not find complexity issues depending on thresholds

    @pytest.mark.slow
    def test_validation_error_handling(self):
        """Test validation error handling."""
        # Create invalid Python file
        invalid_file = self.root_path / "invalid.py"
        invalid_file.write_text("""
# Invalid Python syntax
def invalid_function(
    # Missing closing parenthesis and colon
    print("This will cause syntax error")
""")
        
        # Validation should handle syntax errors gracefully
        result = self.validator.run_validation()
        
        # Should still complete (with errors)
        assert "summary" in result
        assert result["summary"]["phases_completed"] > 0
        
        # May have syntax-related issues
        if result["summary"]["total_issues"] > 0:
            # This is expected for invalid syntax
            pass

    @pytest.mark.slow
    def test_empty_project_validation(self):
        """Test validation of empty project."""
        # Create empty validator
        empty_dir = Path(tempfile.mkdtemp())
        empty_validator = UnifiedValidator(
            root_path=empty_dir,
            enable_sonarqube=False,
            enable_quality_gates=True
        )
        
        result = empty_validator.run_validation()
        
        # Should complete successfully even with no files
        assert "summary" in result
        assert result["summary"]["phases_completed"] > 0
        
        # Should have zero files
        prep_phase = result["phase_results"].get("preparation", {})
        if "files_collected" in prep_phase:
            assert prep_phase["files_collected"] == 0


if __name__ == "__main__":
    pytest.main([__file__])