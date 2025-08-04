"""
Tests for main validation pipeline - Comprehensive validation system.
"""

import shutil
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.infrastructure.tools.validation.core.validator import (
    ValidationPhase,
    ValidationResult,
    Validator,
)


class TestValidator:
    """Test cases for main Validator class."""
    
    @classmethod
    def setup_class(cls):
        """Set up class-level fixtures to reduce overhead."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.root_path = Path(cls.temp_dir)
        cls.create_test_files()

    def setup_method(self):
        """Set up test fixtures."""
        # Use class-level temp directory and files
        self.temp_dir = self.__class__.temp_dir
        self.root_path = self.__class__.root_path
        
        self.validator = Validator(
            root_path=self.root_path,
            enable_sonarqube=False,
            enable_parallel=False,
            enable_quality_gates=True
        )
    
    @classmethod
    def teardown_class(cls):
        """Clean up class-level fixtures."""
        if hasattr(cls, 'temp_dir') and Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    @classmethod
    def create_test_files(cls):
        """Create test files for validation."""
        # Main Python file
        main_file = cls.root_path / "main.py"
        main_file.write_text(
            """
def hello_world():
    '''Say hello to the world.'''
    print("Hello, World!")
    return "Hello, World!"

def calculate_sum(a, b):
    '''Calculate sum of two numbers.'''
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Arguments must be numbers")
    return a + b
"""
        )

        # Test file
        test_file = cls.root_path / "test_main.py"
        test_file.write_text(
            """
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
"""
        )

        # Requirements file
        requirements_file = cls.root_path / "requirements.txt"
        requirements_file.write_text(
            """
pytest==7.0.0
black==22.0.0
ruff==0.0.1
"""
        )

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

    @patch('src.infrastructure.tools.validation.core.validator.SonarQubeIntegrator')
    def test_initialization_with_sonarqube(self, mock_sonar_integrator):
        """Test validator initialization with SonarQube - optimized."""
        # Mock SonarQube integrator to avoid expensive initialization
        mock_sonar_integrator.return_value = Mock()
        
        validator = Validator(
            root_path=self.root_path,
            enable_sonarqube=True,
            sonar_host_url="http://localhost:9000",
            sonar_token="test_token",
        )

        assert validator.enable_sonarqube is True
        assert validator.sonarqube_integrator is not None
        mock_sonar_integrator.assert_called_once()

    @patch.object(Validator, "_preparation_phase")
    @patch.object(Validator, "_static_analysis_phase")
    @patch.object(Validator, "_quality_gates_phase")
    @patch.object(Validator, "_security_scan_phase")
    @patch.object(Validator, "_nfr_validation_phase")
    @patch.object(Validator, "_reporting_phase")
    def test_run_validation(
        self,
        mock_reporting,
        mock_nfr,
        mock_security,
        mock_quality_gates,
        mock_static,
        mock_prep,
    ):
        """Test unified validation pipeline."""
        # Mock phase returns
        mock_prep.return_value = {"success": True}
        mock_static.return_value = {"success": True}
        mock_quality_gates.return_value = {
            "success": True,
            "build_decision": {"allow_merge": True},
        }
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

    @patch.object(Validator, "_collect_files")
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
        with patch.object(
            self.validator.quality_gates_engine, "evaluate_quality_gates"
        ) as mock_eval:
            mock_eval.return_value = {
                "overall_status": "PASSED",
                "quality_gates_passed": 5,
                "quality_gates_failed": 0,
                "quality_gates_warning": 0,
                "build_decision": {"allow_merge": True, "blocking_issues": []},
                "technical_debt": {"total_hours": 2.5},
                "iso_25010_compliance": {"overall": 85.0},
                "gate_results": [],
            }

            result = self.validator._quality_gates_phase()

            assert result["success"] is True
            assert "quality_gates_passed" in result
            assert "build_decision" in result
            assert "technical_debt" in result

            mock_eval.assert_called_once()

    def test_quality_gates_phase_with_failures(self):
        """Test quality gates phase with failures."""
        with patch.object(
            self.validator.quality_gates_engine, "evaluate_quality_gates"
        ) as mock_eval:
            mock_eval.return_value = {
                "overall_status": "FAILED",
                "quality_gates_passed": 3,
                "quality_gates_failed": 2,
                "quality_gates_warning": 0,
                "build_decision": {
                    "allow_merge": False,
                    "blocking_issues": ["test_coverage"],
                },
                "technical_debt": {"total_hours": 15.0},
                "iso_25010_compliance": {"overall": 65.0},
                "gate_results": [
                    {
                        "name": "test_coverage",
                        "status": "FAILED",
                        "severity": "error",
                        "message": "Test coverage below threshold",
                    }
                ],
            }

            result = self.validator._quality_gates_phase()

            assert result["success"] is False
            assert result["quality_gates_failed"] == 2
            assert result["build_decision"]["allow_merge"] is False

            # Should have added quality gate failure issue
            quality_gate_issues = [
                i for i in self.validator.issues if i.category == "quality_gates"
            ]
            assert len(quality_gate_issues) > 0

    def test_security_scan_phase(self):
        """Test security scan phase."""
        with patch.object(
            self.validator.vv_validator, "run_validation_verification"
        ) as mock_run:
            with patch.object(
                self.validator.vv_validator, "generate_vv_report"
            ) as mock_report:
                mock_run.return_value = True
                mock_report.return_value = {
                    "validation_verification": {
                        "compliance": {
                            "owasp_top_10": {"compliance_percentage": 90.0},
                            "pep8_compliance": {"compliance_percentage": 95.0},
                        },
                        "security_vulnerabilities": {"total_vulnerabilities": 0},
                        "external_tools": {"bandit": {"issues_found": 0}},
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
        with patch.object(
            self.validator.nfr_validator, "run_nfr_validation"
        ) as mock_run:
            with patch.object(
                self.validator.nfr_validator, "generate_nfr_report"
            ) as mock_report:
                mock_run.return_value = True
                mock_report.return_value = {
                    "iso_25010_compliance": {"overall": 85.0},
                    "security_metrics": {"auth_coverage": 100.0},
                    "maintainability_metrics": {"avg_complexity": 5.0},
                    "performance_profiles": [],
                    "nfr_violations": [],
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

    @patch('src.infrastructure.tools.validation.core.validator.SonarQubeIntegrator')
    def test_integration_phase_enabled(self, mock_sonar_integrator):
        """Test integration phase when SonarQube is enabled - optimized."""
        # Mock SonarQube integrator to avoid expensive initialization
        mock_integrator_instance = Mock()
        mock_integrator_instance.issues = []  # Add empty issues list
        mock_integrator_instance.sonar_issues = []  # Add empty sonar_issues list
        mock_sonar_integrator.return_value = mock_integrator_instance
        
        # Create validator with SonarQube enabled
        validator = Validator(
            root_path=self.root_path,
            enable_sonarqube=True,
            sonar_host_url="http://localhost:9000",
            sonar_token="test_token",
        )

        with patch.object(
            validator.sonarqube_integrator, "run_sonarqube_analysis"
        ) as mock_run:
            with patch.object(
                validator.sonarqube_integrator, "generate_integrated_report"
            ) as mock_report:
                mock_run.return_value = True
                mock_report.return_value = {
                    "sonarqube_integration": {
                        "enabled": True,
                        "issues_count": 5,
                        "analysis_success": True,
                    }
                }

                result = validator._integration_phase()

                assert result["success"] is True
                assert "sonarqube_enabled" in result
                assert "integration_report" in result

                mock_run.assert_called_once()
                mock_report.assert_called_once()

    @patch('src.infrastructure.tools.validation.core.validator.Validator.quality_gates_engine')
    @patch('src.infrastructure.tools.validation.core.validator.Validator.vv_validator')
    @patch('src.infrastructure.tools.validation.core.validator.Validator.nfr_validator')
    @patch('src.infrastructure.tools.validation.core.validator.Validator._generate_final_report')
    def test_reporting_phase(self, mock_generate_report, mock_nfr, mock_vv, mock_quality):
        """Test reporting phase."""
        # Mock all report generators to speed up the test
        mock_generate_report.return_value = {'success': True, 'report_path': 'test.json'}
        mock_quality.generate_quality_report.return_value = True
        mock_vv.generate_vv_report.return_value = {'validation_verification': {}}
        mock_nfr.generate_nfr_report.return_value = {'nfr_metrics': {}}
        
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
            severity="error",
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
            severity="error",
        )

        self.validator.add_issue(
            category="quality",
            issue_type="CODE_SMELL",
            file_path="test.py",
            message="Code smell",
            severity="warning",
        )

        self.validator.build_decision = {
            "allow_merge": False,
            "blocking_issues": ["security"],
        }

        recommendations = self.validator._generate_recommendations()

        assert len(recommendations) > 0
        # Check if we have any recommendations with blocking content
        rec_text = " ".join(recommendations)
        assert (
            "BUILD BLOCKED" in rec_text or "BLOCKED" in rec_text
        ), f"Expected BUILD BLOCKED in recommendations: {recommendations}"
        assert (
            "security" in rec_text
        ), f"Expected security in recommendations: {recommendations}"

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
                details={},
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
                details={},
            )
        ]

        summary = self.validator.get_build_summary()
        assert "FAILED" in summary

    @patch('src.infrastructure.tools.validation.core.validator.Validator.syntax_validator')
    @patch('src.infrastructure.tools.validation.core.validator.Validator.dependency_validator') 
    @patch('src.infrastructure.tools.validation.core.validator.Validator.structure_validator')
    @patch('src.infrastructure.tools.validation.core.validator.Validator.performance_validator')
    @patch('src.infrastructure.tools.validation.core.validator.Validator.pattern_detector')
    @patch('src.infrastructure.tools.validation.core.validator.Validator.business_logic_protector')
    def test_parallel_static_analysis(self, mock_blp, mock_pattern, mock_perf, mock_structure, mock_dependency, mock_syntax):
        """Test parallel static analysis."""
        # Mock all the validators to avoid actual validation work
        mock_syntax.validate_all_imports.return_value = True
        mock_dependency.validate_dependencies.return_value = True
        mock_structure.validate_structure.return_value = True
        mock_perf.validate_performance.return_value = True
        mock_pattern.analyze_patterns.return_value = True
        mock_blp.protect_business_logic.return_value = True
        
        # Enable parallel processing
        self.validator.enable_parallel = True

        # Just test that the method runs without error
        # The actual parallel execution logic is complex and not the focus of this test
        try:
            self.validator._run_parallel_static_analysis()
            # If we get here without exception, the test passes
            assert True
        except Exception as e:
            pytest.fail(f"Parallel static analysis failed with error: {e}")

    def test_lazy_loading_properties(self):
        """Test that validator properties are lazy-loaded."""
        # Properties should be None initially
        assert self.validator._syntax_validator is None
        assert self.validator._dependency_validator is None
        assert self.validator._structure_validator is None

        # Accessing properties should initialize them
        syntax_val = self.validator.syntax_validator
        assert self.validator._syntax_validator is not None
        assert syntax_val is self.validator._syntax_validator

        # Subsequent access should return same instance
        assert self.validator.syntax_validator is syntax_val

    def test_quality_gate_config_usage(self):
        """Test quality gate configuration usage."""
        quality_config = {"coverage_threshold": 95}
        validator = Validator(
            root_path=self.root_path, quality_gate_config=quality_config
        )

        assert validator.quality_gate_config == quality_config

    def test_validation_result_dataclass(self):
        """Test ValidationResult dataclass."""
        result = ValidationResult(
            phase=ValidationPhase.PREPARATION,
            success=True,
            duration=1.5,
            issues_found=5,
            critical_issues=1,
            warnings=3,
            info=1,
            details={"test": "data"},
        )

        assert result.phase == ValidationPhase.PREPARATION
        assert result.success is True
        assert result.duration == 1.5
        assert result.issues_found == 5
        assert result.critical_issues == 1
        assert result.warnings == 3
        assert result.info == 1
        assert result.details == {"test": "data"}

    def test_validation_phase_enum(self):
        """Test ValidationPhase enum values."""
        phases = [
            ValidationPhase.PREPARATION,
            ValidationPhase.STATIC_ANALYSIS,
            ValidationPhase.QUALITY_GATES,
            ValidationPhase.SECURITY_SCAN,
            ValidationPhase.NFR_VALIDATION,
            ValidationPhase.INTEGRATION,
            ValidationPhase.REPORTING,
        ]

        expected_values = [
            "preparation",
            "static_analysis",
            "quality_gates",
            "security_scan",
            "nfr_validation",
            "integration",
            "reporting",
        ]

        for phase, expected in zip(phases, expected_values):
            assert phase.value == expected

    def test_timing_measurement(self):
        """Test that overall timing is measured."""
        # Mock all phases to run quickly
        with patch.object(self.validator, "_preparation_phase") as mock_prep, \
             patch.object(self.validator, "_static_analysis_phase") as mock_static, \
             patch.object(self.validator, "_quality_gates_phase") as mock_quality, \
             patch.object(self.validator, "_security_scan_phase") as mock_security, \
             patch.object(self.validator, "_nfr_validation_phase") as mock_nfr, \
             patch.object(self.validator, "_reporting_phase") as mock_reporting:

            # Mock all phases to return success
            for mock_phase in [mock_prep, mock_static, mock_quality, 
                             mock_security, mock_nfr, mock_reporting]:
                mock_phase.return_value = {"success": True}

            start_time = time.time()
            result = self.validator.run_validation()
            end_time = time.time()

            # Check that timing is reasonable
            assert "summary" in result
            if "total_time" in result["summary"]:
                total_time = result["summary"]["total_time"]
                assert total_time > 0
                assert total_time <= (end_time - start_time + 1)  # Allow some tolerance