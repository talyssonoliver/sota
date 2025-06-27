"""
test_analytics.py - Optimized Test Structure

Migrated from: tests/integration	est_analytics.py
New location: tests/integration	est_analytics.py

Part of the optimized test pyramid reorganization:
- Tests now mirror src/ structure
- Proper categorization (unit/integration/e2e)
- Improved mocking and isolation
"""
'\nTests for Analytics Module\n\nTest suite for the analytics/analyse_feedback.py module to validate\nfeedback analysis, pattern recognition, and recommendation generation.\n'
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime
from src.integrations.analytics.analyse_feedback import FeedbackAnalyzer

class TestFeedbackAnalyzer:
    """Test the FeedbackAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = Path(temp_dir)
            self.analyzer = FeedbackAnalyzer(base_dir=str(self.temp_dir))

    def test_feedback_analyzer_initialization(self):
        """Test FeedbackAnalyzer initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = FeedbackAnalyzer(base_dir=temp_dir)
            assert analyzer.base_dir == Path(temp_dir)
            assert analyzer.outputs_dir == Path('outputs')
            assert analyzer.analysis_results == {}
            assert analyzer.analytics_dir.exists()

    def test_analyze_task_feedback_no_feedback(self):
        """Test analyzing task feedback when no feedback exists."""
        with patch.object(self.analyzer.feedback_system, 'get_feedback_by_task', return_value=[]):
            result = self.analyzer.analyze_task_feedback('BE-07')
            assert result['task_id'] == 'BE-07'
            assert result['status'] == 'no_feedback'
            assert result['recommendations'] == []

    def test_analyze_task_feedback_with_data(self):
        """Test analyzing task feedback with actual feedback data."""
        mock_feedback = [Mock(task_id='BE-07', content='The code needs better error handling and documentation', timestamp=datetime.now().isoformat(), overall_score=6, category_scores={'code_quality': 7, 'documentation': 5}), Mock(task_id='BE-07', content='Performance is slow, needs optimization', timestamp=datetime.now().isoformat(), overall_score=5, category_scores={'performance': 4, 'code_quality': 6})]
        with patch.object(self.analyzer.feedback_system, 'get_feedback_by_task', return_value=mock_feedback), patch.object(self.analyzer, '_save_analysis_results'):
            result = self.analyzer.analyze_task_feedback('BE-07')
            assert result['task_id'] == 'BE-07'
            assert result['feedback_count'] == 2
            assert 'summary' in result
            assert 'recurring_edits' in result
            assert 'prompt_modifications' in result
            assert 'tool_improvements' in result

    def test_analyze_all_feedback_no_data(self):
        """Test analyzing all feedback when no feedback exists."""
        with patch.object(self.analyzer.feedback_system, 'get_feedback_by_period', return_value=[]):
            result = self.analyzer.analyze_all_feedback(30)
            assert result['status'] == 'no_feedback'
            assert result['period_days'] == 30

    def test_analyze_all_feedback_with_data(self):
        """Test analyzing all feedback with data."""
        mock_feedback = [Mock(task_id='BE-07', agent_name='backend_agent', content='Error handling needs improvement', timestamp=datetime.now().isoformat(), overall_score=6), Mock(task_id='FE-01', agent_name='frontend_agent', content='Performance optimization required', timestamp=datetime.now().isoformat(), overall_score=7)]
        with patch.object(self.analyzer.feedback_system, 'get_feedback_by_period', return_value=mock_feedback), patch.object(self.analyzer, '_save_analysis_results'):
            result = self.analyzer.analyze_all_feedback(30)
            assert result['total_feedback'] == 2
            assert result['tasks_analyzed'] == 2
            assert result['agents_analyzed'] == 2
            assert 'global_patterns' in result
            assert 'agent_performance' in result

    def test_analyze_feedback_summary(self):
        """Test feedback summary analysis."""
        mock_feedback = [Mock(category_scores={'code_quality': 8, 'documentation': 6}, overall_score=7), Mock(category_scores={'code_quality': 6, 'performance': 5}, overall_score=5)]
        result = self.analyzer._analyze_feedback_summary(mock_feedback)
        assert result['total_feedback'] == 2
        assert 'approval_rates' in result
        assert 'code_quality' in result['approval_rates']
        assert result['approval_rates']['code_quality']['average_score'] == 7.0

    def test_identify_recurring_edits(self):
        """Test identification of recurring edit patterns."""
        mock_feedback = [Mock(task_id='BE-07', content='Need to rename this function for better naming conventions', timestamp=datetime.now().isoformat()), Mock(task_id='BE-08', content='Should refactor this code structure for better organization', timestamp=datetime.now().isoformat()), Mock(task_id='BE-09', content='Add error handling and exception management', timestamp=datetime.now().isoformat())]
        result = self.analyzer._identify_recurring_edits(mock_feedback)
        assert len(result) > 0
        pattern_types = [edit['pattern'] for edit in result]
        assert 'naming_conventions' in pattern_types
        assert 'code_structure' in pattern_types
        assert 'error_handling' in pattern_types

    def test_suggest_prompt_modifications(self):
        """Test prompt modification suggestions."""
        mock_feedback = [Mock(content='The instructions are unclear and confusing'), Mock(content='Missing important context about the requirements'), Mock(content='Need more specific details about the implementation'), Mock(content='The prompt is ambiguous and hard to understand')]
        result = self.analyzer._suggest_prompt_modifications(mock_feedback)
        assert len(result) > 0
        suggestion_types = [suggestion['type'] for suggestion in result]
        assert 'clarity' in suggestion_types
        assert 'context' in suggestion_types

    def test_suggest_tool_improvements(self):
        """Test tool improvement suggestions."""
        mock_feedback = [Mock(content='The tool is slow and has performance issues'), Mock(content='Tool function failed with an error'), Mock(content='Missing functionality in the tool')]
        result = self.analyzer._suggest_tool_improvements(mock_feedback)
        assert len(result) > 0
        improvement_types = [improvement['type'] for improvement in result]
        assert 'performance' in improvement_types or 'reliability' in improvement_types

    def test_suggest_context_adjustments(self):
        """Test context adjustment suggestions."""
        mock_feedback = [Mock(content='Missing context and background information'), Mock(content='Irrelevant context provided, not related to task'), Mock(content='Context is outdated and needs updating')]
        result = self.analyzer._suggest_context_adjustments(mock_feedback)
        assert len(result) > 0
        adjustment_types = [adjustment['type'] for adjustment in result]
        expected_types = ['insufficient_context', 'irrelevant_context', 'outdated_context']
        assert any((adj_type in expected_types for adj_type in adjustment_types))

    def test_generate_fine_tuning_examples(self):
        """Test fine-tuning example generation."""
        mock_feedback = [Mock(task_id='BE-07', content='Excellent implementation with good error handling', agent_output='def process_data(): ...', overall_score=9), Mock(task_id='BE-08', content='Poor implementation needs major improvements', agent_output='def bad_function(): ...', overall_score=3)]
        result = self.analyzer._generate_fine_tuning_examples(mock_feedback)
        assert len(result) == 2
        categories = [example['category'] for example in result]
        assert 'positive_example' in categories
        assert 'improvement_needed' in categories

    def test_analyze_global_patterns(self):
        """Test global pattern analysis."""
        mock_feedback = [Mock(content='Error occurred during processing'), Mock(content='Performance is very slow'), Mock(content='Documentation is missing'), Mock(content='Tests are failing')]
        result = self.analyzer._analyze_global_patterns(mock_feedback)
        assert 'common_issues' in result
        assert result['common_issues']['errors'] >= 1
        assert result['common_issues']['performance'] >= 1
        assert result['common_issues']['documentation'] >= 1
        assert result['common_issues']['testing'] >= 1

    def test_analyze_agent_performance(self):
        """Test agent performance analysis."""
        feedback_by_agent = {'backend_agent': [Mock(overall_score=8, content='Good performance'), Mock(overall_score=6, content='Needs accuracy improvement')], 'frontend_agent': [Mock(overall_score=7, content='Fast but could be better quality')]}
        result = self.analyzer._analyze_agent_performance(feedback_by_agent)
        assert 'backend_agent' in result
        assert 'frontend_agent' in result
        assert result['backend_agent']['average_score'] == 7.0
        assert result['backend_agent']['feedback_count'] == 2
        assert 'improvement_areas' in result['backend_agent']

    def test_analyze_task_patterns(self):
        """Test task pattern analysis."""
        feedback_by_task = {'BE-07': [Mock(overall_score=8), Mock(overall_score=6)], 'BE-08': [Mock(overall_score=7)], 'FE-01': [Mock(overall_score=9)]}
        result = self.analyzer._analyze_task_patterns(feedback_by_task)
        assert 'by_task_type' in result
        assert 'BE' in result['by_task_type']
        assert 'FE' in result['by_task_type']

    def test_suggest_system_improvements(self):
        """Test system improvement suggestions."""
        mock_feedback = [Mock(content='System is slow and has performance issues'), Mock(content='Error occurred and system crashed'), Mock(content='User interface needs improvement')]
        result = self.analyzer._suggest_system_improvements(mock_feedback)
        assert len(result) > 0
        areas = [improvement['area'] for improvement in result]
        expected_areas = ['performance', 'reliability', 'user_experience']
        assert any((area in expected_areas for area in areas))

    def test_generate_training_recommendations(self):
        """Test training recommendation generation."""
        mock_feedback = [Mock(content='Prompt engineering needs improvement'), Mock(content='Code quality is poor'), Mock(content='Documentation standards not followed'), Mock(content='Testing methodology is inadequate')]
        result = self.analyzer._generate_training_recommendations(mock_feedback)
        assert len(result) > 0
        training_areas = [rec['training_area'] for rec in result]
        expected_areas = ['prompt_engineering', 'code_quality', 'documentation', 'testing']
        assert any((area in expected_areas for area in training_areas))

    def test_calculate_average_score(self):
        """Test average score calculation."""
        mock_feedback = [Mock(overall_score=8), Mock(overall_score=6), Mock(overall_score=7)]
        result = self.analyzer._calculate_average_score(mock_feedback)
        assert result == 7.0
        result_empty = self.analyzer._calculate_average_score([])
        assert result_empty == 0.0

    def test_identify_agent_improvement_areas(self):
        """Test agent improvement area identification."""
        mock_feedback = [Mock(content='Accuracy is wrong and needs correction'), Mock(content='Speed is slow and needs to be faster'), Mock(content='Quality is better but still needs improvement')]
        result = self.analyzer._identify_agent_improvement_areas(mock_feedback)
        assert len(result) <= 3
        expected_areas = ['accuracy', 'speed', 'quality']
        assert all((area in expected_areas for area in result))

    def test_generate_report_markdown(self):
        """Test markdown report generation."""
        analysis = {'task_id': 'BE-07', 'analysis_timestamp': '2024-01-01T12:00:00', 'feedback_count': 5, 'summary': {'total_feedback': 5, 'average_overall_score': 7.2}, 'recurring_edits': [{'pattern': 'naming_conventions', 'frequency': 3}], 'overall_recommendations': ['Focus on addressing recurring edit patterns']}
        result = self.analyzer.generate_report(analysis, format='markdown')
        assert '# Feedback Analysis Report - Task BE-07' in result
        assert '**Feedback Entries:** 5' in result
        assert '**Average Score:** 7.20' in result
        assert '## Recurring Edits' in result
        assert '## Overall Recommendations' in result

    def test_generate_report_json(self):
        """Test JSON report generation."""
        analysis = {'task_id': 'BE-07', 'feedback_count': 5}
        result = self.analyzer.generate_report(analysis, format='json')
        parsed_result = json.loads(result)
        assert parsed_result['task_id'] == 'BE-07'
        assert parsed_result['feedback_count'] == 5

    def test_save_analysis_results(self):
        """Test saving analysis results to file."""
        analysis = {'task_id': 'BE-07', 'feedback_count': 5}
        with patch('builtins.open', create=True) as mock_open, patch('json.dump') as mock_dump:
            self.analyzer._save_analysis_results('BE-07', analysis)
            mock_open.assert_called_once()
            mock_dump.assert_called_once_with(analysis, mock_open().__enter__(), indent=2, default=str)

    def test_helper_methods(self):
        """Test various helper methods."""
        assert 'performance' in self.analyzer._get_tool_suggestion('performance')
        assert 'error handling' in self.analyzer._get_tool_suggestion('reliability')
        assert 'context window' in self.analyzer._get_context_suggestion('insufficient_context')
        assert 'filtering' in self.analyzer._get_context_suggestion('irrelevant_context')
        assert 'performance monitoring' in self.analyzer._get_system_improvement_suggestion('performance')
        assert 'error handling' in self.analyzer._get_system_improvement_suggestion('reliability')
        assert 'prompt design' in self.analyzer._get_training_recommendation('prompt_engineering')
        assert 'code quality' in self.analyzer._get_training_recommendation('code_quality')

class TestFeedbackAnalyzerCLI:
    """Test the CLI interface of the feedback analyzer."""

    def test_main_with_task_argument(self):
        """Test main function with task argument."""
        with patch('sys.argv', ['script', '--task', 'BE-07']), patch('src.integrations.analytics.analyse_feedback.FeedbackAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_analyzer.analyze_task_feedback.return_value = {'task_id': 'BE-07', 'feedback_count': 3}
            mock_analyzer.generate_report.return_value = '# Report'
            mock_analyzer_class.return_value = mock_analyzer
            from src.integrations.analytics.analyse_feedback import main
            main()
            mock_analyzer.analyze_task_feedback.assert_called_once_with('BE-07')
            mock_analyzer.generate_report.assert_called_once()

    def test_main_comprehensive_analysis(self):
        """Test main function for comprehensive analysis."""
        with patch('sys.argv', ['script', '--period', '14']), patch('src.integrations.analytics.analyse_feedback.FeedbackAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_analyzer.analyze_all_feedback.return_value = {'total_feedback': 10, 'period_days': 14}
            mock_analyzer.generate_report.return_value = '# Comprehensive Report'
            mock_analyzer_class.return_value = mock_analyzer
            from src.integrations.analytics.analyse_feedback import main
            main()
            mock_analyzer.analyze_all_feedback.assert_called_once_with(14)
            mock_analyzer.generate_report.assert_called_once()

    def test_main_with_output_file(self):
        """Test main function with output file."""
        with patch('sys.argv', ['script', '--task', 'BE-07', '--output', 'report.md']), patch('src.integrations.analytics.analyse_feedback.FeedbackAnalyzer') as mock_analyzer_class, patch('builtins.open', create=True) as mock_open:
            mock_analyzer = Mock()
            mock_analyzer.analyze_task_feedback.return_value = {'task_id': 'BE-07'}
            mock_analyzer.generate_report.return_value = '# Report Content'
            mock_analyzer_class.return_value = mock_analyzer
            from src.integrations.analytics.analyse_feedback import main
            main()
            mock_open.assert_called_once_with('report.md', 'w')
            mock_open().__enter__().write.assert_called_once_with('# Report Content')

class TestFeedbackAnalyzerIntegration:
    """Test integration scenarios."""

    def test_end_to_end_task_analysis(self):
        """Test complete task analysis workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = FeedbackAnalyzer(base_dir=temp_dir)
            mock_feedback = [Mock(task_id='BE-07', content='Code needs better error handling and documentation. Performance is slow.', timestamp=datetime.now().isoformat(), overall_score=6, category_scores={'code_quality': 7, 'documentation': 5, 'performance': 4}, agent_output='def process_data(): return data')]
            with patch.object(analyzer.feedback_system, 'get_feedback_by_task', return_value=mock_feedback):
                result = analyzer.analyze_task_feedback('BE-07')
                assert result['task_id'] == 'BE-07'
                assert result['feedback_count'] == 1
                assert 'summary' in result
                assert 'recurring_edits' in result
                assert 'prompt_modifications' in result
                assert 'tool_improvements' in result
                assert 'context_adjustments' in result
                assert 'fine_tuning_examples' in result
                assert 'overall_recommendations' in result
                report = analyzer.generate_report(result)
                assert 'Feedback Analysis Report' in report
                assert 'BE-07' in report
if __name__ == '__main__':
    pytest.main([__file__])