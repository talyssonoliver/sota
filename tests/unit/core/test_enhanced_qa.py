"""
test_enhanced_qa.py - Optimized Test Structure

Migrated from: tests/agents	est_enhanced_qa.py
New location: tests/unit\\core	est_enhanced_qa.py

Part of the optimized test pyramid reorganization:
- Tests now mirror src/ structure
- Proper categorization (unit/integration/e2e)
- Improved mocking and isolation

Test suite for Enhanced QA Agent and related components.
"""
import sys
import pytest
import shutil
try:
    from pathlib import Path
except ImportError:
    pass
try:
    from unittest.mock import MagicMock, Mock, patch
except ImportError:
    pass
try:
    from src.core.agents.qa import EnhancedQAAgent, create_enhanced_qa_workflow
except ImportError:
    pass
try:
    from src.infrastructure.utils.coverage_analyzer import CoverageAnalyzer
except ImportError:
    pass
try:
    from tests.components.test_generator import CodeLanguage, QATestFramework, QATestGenerator
except ImportError:
    pass
import json
import tempfile
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestEnhancedQAAgent:
    """Test cases for EnhancedQAAgent."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        (project_path / 'src').mkdir()
        (project_path / 'src' / 'sample.py').write_text('\ndef hello_world():\n    return "Hello, World!"\n\nclass Calculator:\n    def add(self, a, b):\n        return a + b\n\n    def divide(self, a, b):\n        if b == 0:\n            raise ValueError("Cannot divide by zero")\n        return a / b\n')
        (project_path / 'src' / 'utils.js').write_text('\nfunction formatName(first, last) {\n    return `${first} ${last}`;\n}\n\nclass DataProcessor {\n    constructor() {\n        this.data = [];\n    }\n\n    process(item) {\n        this.data.push(item);\n        return item;\n    }\n}\n')
        yield project_path
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def qa_agent(self, temp_project):
        """Create QA agent with temporary project."""
        return EnhancedQAAgent(str(temp_project))

    def test_qa_agent_initialization(self, qa_agent):
        """Test QA agent initializes correctly."""
        assert qa_agent.project_root.exists()
        assert qa_agent.test_generator is not None
        assert qa_agent.coverage_analyzer is not None
        assert qa_agent.config is not None
        assert 'coverage_thresholds' in qa_agent.config
        assert 'quality_gates' in qa_agent.config

    def test_config_loading_default(self, qa_agent):
        """Test default config loading."""
        config = qa_agent.config
        assert config['coverage_thresholds']['line_coverage'] == 80
        assert config['quality_gates']['min_test_coverage'] == 80
        assert config['test_patterns']['unit_test_ratio'] == 0.7

    def test_config_loading_with_file(self, temp_project):
        """Test config loading with custom file."""
        config_file = temp_project / 'custom_qa.json'
        custom_config = {'coverage_thresholds': {'line_coverage': 90}, 'quality_gates': {'min_test_coverage': 85}}
        config_file.write_text(json.dumps(custom_config))
        qa_agent = EnhancedQAAgent(str(temp_project), str(config_file))
        assert qa_agent.config['coverage_thresholds']['line_coverage'] == 90
        assert qa_agent.config['quality_gates']['min_test_coverage'] == 85

    def test_discover_source_files(self, qa_agent):
        """Test source file discovery."""
        source_files = qa_agent._discover_source_files()
        assert len(source_files) > 0
        assert any(('sample.py' in f for f in source_files))
        assert any(('utils.js' in f for f in source_files))
        assert not any(('test_' in f for f in source_files))
        assert not any(('__pycache__' in f for f in source_files))

    def test_determine_test_framework_python(self, qa_agent):
        """Test framework determination for Python files."""
        framework = qa_agent._determine_test_framework('sample.py')
        assert framework in [QATestFramework.PYTEST, QATestFramework.UNITTEST]

    def test_determine_test_framework_javascript(self, qa_agent):
        """Test framework determination for JavaScript files."""
        framework = qa_agent._determine_test_framework('utils.js')
        assert framework == QATestFramework.JEST

    def test_get_test_file_path(self, qa_agent):
        """Test test file path generation."""
        pytest_path = qa_agent._get_test_file_path('src/sample.py', QATestFramework.PYTEST)
        assert 'test_sample.py' in str(pytest_path)
        assert 'tests' in str(pytest_path) and 'generated' in str(pytest_path)
        jest_path = qa_agent._get_test_file_path('src/utils.js', QATestFramework.JEST)
        assert 'utils.test.js' in str(jest_path)
        assert 'tests' in str(jest_path) and 'generated' in str(jest_path)

    @patch('agents.qa.CoverageAnalyzer')
    @patch('agents.qa.IntegrationAnalyzer')
    def test_generate_comprehensive_tests(self, mock_integration, mock_coverage, qa_agent):
        """Test comprehensive test generation."""
        mock_coverage.return_value.analyze_coverage_patterns.return_value = {'overall_quality_score': 75, 'improvement_potential': 25}
        mock_integration.return_value.analyze_project.return_value = {'gaps': ['gap1', 'gap2']}
        results = qa_agent.generate_comprehensive_tests()
        assert 'generated_tests' in results
        assert 'coverage_analysis' in results
        assert 'integration_gaps' in results
        assert 'quality_metrics' in results
        assert 'recommendations' in results
        assert len(results['generated_tests']) > 0

    def test_calculate_quality_metrics(self, qa_agent):
        """Test quality metrics calculation."""
        mock_results = {'generated_tests': [{'status': 'success', 'test_count': 5}, {'status': 'success', 'test_count': 3}, {'status': 'error', 'error': 'Some error'}], 'coverage_analysis': {'improvement_potential': 20}, 'integration_gaps': ['gap1', 'gap2']}
        metrics = qa_agent._calculate_quality_metrics(mock_results)
        assert metrics['test_generation_success_rate'] == 2 / 3 * 100
        assert metrics['total_generated_tests'] == 8
        assert metrics['integration_gap_count'] == 2
        assert 'quality_score' in metrics

    def test_calculate_overall_quality_score(self, qa_agent):
        """Test overall quality score calculation."""
        mock_results = {'quality_metrics': {'test_generation_success_rate': 80}, 'coverage_analysis': {'overall_quality_score': 70}, 'integration_gaps': ['gap1']}
        score = qa_agent._calculate_overall_quality_score(mock_results)
        assert 0 <= score <= 100
        assert score > 0

    def test_generate_recommendations(self, qa_agent):
        """Test recommendation generation."""
        mock_results = {'generated_tests': [{'status': 'error', 'error': 'Error 1'}, {'status': 'success'}], 'coverage_analysis': {'overall_quality_score': 60}, 'integration_gaps': ['gap1', 'gap2', 'gap3', 'gap4', 'gap5', 'gap6'], 'quality_metrics': {'quality_score': 70}}
        recommendations = qa_agent._generate_recommendations(mock_results)
        assert len(recommendations) > 0
        assert any(('Fix test generation errors' in rec for rec in recommendations))
        assert any(('Improve test coverage' in rec for rec in recommendations))
        assert any(('integration gaps' in rec for rec in recommendations))

    def test_validate_quality_gates(self, qa_agent):
        """Test quality gate validation."""
        mock_results = {'quality_metrics': {'test_generation_success_rate': 85, 'integration_gap_count': 5, 'quality_score': 80}}
        validation = qa_agent.validate_quality_gates(mock_results)
        assert 'overall_status' in validation
        assert validation['overall_status'] in ['PASSED', 'FAILED']
        assert 'gates' in validation
        assert 'summary' in validation
        gates = validation['gates']
        assert 'coverage_gate' in gates
        assert 'integration_gate' in gates
        assert 'overall_quality_gate' in gates
        for gate in gates.values():
            assert 'passed' in gate
            assert 'current' in gate
            assert 'threshold' in gate

class TestCoverageAnalyzer:
    """Test cases for CoverageAnalyzer."""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project for testing."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        (project_path / 'covered.py').write_text('def covered_function(): return True')
        (project_path / 'uncovered.py').write_text('def uncovered_function(): return False')
        yield project_path
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def analyzer(self, temp_project):
        """Create analyzer with temporary project."""
        return CoverageAnalyzer(str(temp_project))

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly."""
        assert analyzer.project_root.exists()
        assert hasattr(analyzer, 'logger')

    @patch('subprocess.run')
    def test_collect_coverage_data(self, mock_run, analyzer):
        """Test coverage data collection."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({'totals': {'percent_covered': 85.5}, 'files': {'file1.py': {'summary': {'percent_covered': 90.0}}, 'file2.py': {'summary': {'percent_covered': 80.0}}}})
        mock_run.return_value = mock_result
        data = analyzer._collect_coverage_data()
        assert data is not None
        assert 'totals' in data
        assert data['totals']['percent_covered'] == 85.5

    def test_analyze_coverage_patterns(self, analyzer):
        """Test coverage pattern analysis."""
        with patch.object(analyzer, '_collect_coverage_data') as mock_collect:
            mock_collect.return_value = {'totals': {'percent_covered': 80.0}, 'files': {'file1.py': {'summary': {'percent_covered': 90.0}}, 'file2.py': {'summary': {'percent_covered': 70.0}}}}
            analysis = analyzer.analyze_coverage_patterns(str(analyzer.project_root))
            assert 'overall_coverage' in analysis
            assert 'coverage_gaps' in analysis['analysis']
            assert 'file_metrics' in analysis['analysis']
            assert 'recommendations' in analysis['analysis']
            assert 'quality_score' in analysis['analysis']

class TestQATestGenerator:
    """Test cases for QATestGenerator."""

    @pytest.fixture
    def generator(self):
        """Create test generator."""
        return QATestGenerator()

    def test_generator_initialization(self, generator):
        """Test generator initializes correctly."""
        assert generator.project_root.exists()
        assert generator.patterns is not None
        assert 'jest' in generator.patterns
        assert 'pytest' in generator.patterns

    def test_detect_language_python(self, generator):
        """Test language detection for Python files."""
        python_file = Path('test.py')
        language = generator._detect_language(python_file)
        assert language == CodeLanguage.PYTHON

    def test_detect_language_javascript(self, generator):
        """Test language detection for JavaScript files."""
        js_file = Path('test.js')
        language = generator._detect_language(js_file)
        assert language == CodeLanguage.JAVASCRIPT

    def test_detect_framework_python(self, generator):
        """Test framework detection for Python."""
        language = CodeLanguage.PYTHON
        framework = generator._suggest_framework(language)
        assert framework == QATestFramework.PYTEST

    def test_detect_framework_javascript(self, generator):
        """Test framework detection for JavaScript."""
        language = CodeLanguage.JAVASCRIPT
        framework = generator._suggest_framework(language)
        assert framework == QATestFramework.JEST

    def test_analyze_python_code(self, generator):
        """Test Python code analysis."""
        code = '\ndef test_function(param):\n    return param * 2\n\nclass TestClass:\n    def method1(self):\n        pass\n\n    def method2(self, arg):\n        return arg\n'
        analysis = generator._analyze_python_code(code)
        assert 'functions' in analysis
        assert 'classes' in analysis
        assert len(analysis['functions']) == 1
        assert len(analysis['classes']) == 1
        assert analysis['functions'][0]['name'] == 'test_function'
        assert analysis['classes'][0]['name'] == 'TestClass'

    def test_generate_test_file(self, generator):
        """Test complete test file generation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('\ndef sample_function():\n    return "test"\n\nclass SampleClass:\n    def method(self):\n        return True\n')
            f.flush()
            f.close()
            try:
                test_content = generator.generate_test_file(f.name)
                assert test_content is not None
                assert len(test_content) > 0
                assert 'test_sample_function' in test_content or 'def test_' in test_content
            finally:
                try:
                    Path(f.name).unlink()
                except PermissionError:
                    pass

class TestQAWorkflow:
    """Test cases for complete QA workflow."""

    def test_create_enhanced_qa_workflow(self):
        """Test QA workflow creation."""
        workflow = create_enhanced_qa_workflow()
        assert isinstance(workflow, EnhancedQAAgent)

    @patch('agents.qa.EnhancedQAAgent')
    def test_workflow_integration(self, mock_qa_agent):
        """Test integrated workflow execution."""
        mock_instance = Mock()
        mock_instance.generate_comprehensive_tests.return_value = {'quality_metrics': {'quality_score': 85}, 'recommendations': ['Sample recommendation']}
        mock_instance.validate_quality_gates.return_value = {'overall_status': 'PASSED', 'summary': 'All gates passed'}
        mock_qa_agent.return_value = mock_instance
        workflow = create_enhanced_qa_workflow()
        test_results = workflow.generate_comprehensive_tests()
        gate_results = workflow.validate_quality_gates(test_results)
        assert test_results['quality_metrics']['quality_score'] == 85
        assert gate_results['overall_status'] == 'PASSED'
if __name__ == '__main__':
    pytest.main([__file__, '-v'])