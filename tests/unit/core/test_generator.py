"""
Test Generator - Advanced Test File Generation for QA Agent
Automatically generates test files based on code analysis and patterns.
"""
import sys
from unittest.mock import MagicMock

def setup_test_mocks():
    """Setup test mocks when needed"""
    if 'langgraph' not in sys.modules:
        langgraph_mock = MagicMock()
        langgraph_mock.constants = MagicMock()
        langgraph_mock.constants.END = 'END'
        langgraph_mock.graph = MagicMock()
        langgraph_mock.graph.Graph = MagicMock
        langgraph_mock.graph.StateGraph = MagicMock
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
try:
    import re
except ImportError:
    pass
try:
    import ast
except ImportError:
    pass

class QAFramework(Enum):
    """Supported test frameworks."""
    __test__ = False
    JEST = 'jest'
    PYTEST = 'pytest'
    UNITTEST = 'unittest'
    CYPRESS = 'cypress'

class CodeLanguage(Enum):
    """Supported programming languages."""
    __test__ = False
    PYTHON = 'python'
    JAVASCRIPT = 'javascript'
    TYPESCRIPT = 'typescript'
    JSX = 'jsx'
    TSX = 'tsx'

@dataclass
class QATestCase:
    """Represents a single test case."""
    name: str
    description: str
    test_type: str
    code: str
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None
    dependencies: List[str] = None

@dataclass
class QATestSuite:
    """Represents a complete test suite for a file."""
    filename: str
    framework: QAFramework
    language: CodeLanguage
    test_cases: List[QATestCase]
    imports: List[str]
    setup: Optional[str] = None
    teardown: Optional[str] = None

class QATestGenerator:
    """Advanced test file generator."""

    def __init__(self, project_root: str='.'):
        self.project_root = Path(project_root)
        self.patterns = self._load_test_patterns()

    def _load_test_patterns(self) -> Dict[str, Any]:
        """Load test patterns for different frameworks and languages."""
        return {'jest': {'imports': ["import { render, screen, fireEvent, waitFor } from '@testing-library/react';", "import { jest } from '@jest/globals';", "import '@testing-library/jest-dom';"], 'setup': 'beforeEach(() => { jest.clearAllMocks(); });', 'teardown': 'afterEach(() => { cleanup(); });', 'test_wrapper': "describe('{component_name}', () => {{ {tests} }});"}, 'pytest': {'imports': ['import pytest', 'from unittest.mock import Mock, patch, MagicMock', 'from pathlib import Path'], 'setup': '@pytest.fixture\ndef setup():\n    return {}', 'test_wrapper': 'class Test{class_name}:\n{tests}'}, 'unittest': {'imports': ['import unittest', 'from unittest.mock import Mock, patch, MagicMock', 'import sys', 'import os'], 'setup': 'def setUp(self):\n        pass', 'test_wrapper': 'class Test{class_name}(unittest.QATestCase):\n{tests}'}}

    def generate_test_file(self, source_file: str, target_file: str=None, framework: 'QAFramework'=None) -> str:
        """Generate a complete test file for the given source file."""
        source_path = Path(source_file)
        if not source_path.exists():
            raise FileNotFoundError(f'Source file not found: {source_file}')
        language = self._detect_language(source_path)
        if framework is None:
            framework = self._suggest_framework(language)
        analysis = self._analyze_source_code(source_path, language)
        analysis['filename'] = source_path.stem
        test_suite = self._generate_test_suite(analysis, framework, language)
        test_content = self._render_test_file(test_suite)
        if target_file:
            target_path = Path(target_file)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(test_content, encoding='utf-8')
        return test_content

    def _detect_language(self, file_path: Path) -> CodeLanguage:
        """Detect programming language from file extension."""
        suffix = file_path.suffix.lower()
        if suffix == '.py':
            return CodeLanguage.PYTHON
        elif suffix == '.js':
            return CodeLanguage.JAVASCRIPT
        elif suffix == '.ts':
            return CodeLanguage.TYPESCRIPT
        elif suffix == '.jsx':
            return CodeLanguage.JSX
        elif suffix == '.tsx':
            return CodeLanguage.TSX
        else:
            return CodeLanguage.PYTHON

    def _suggest_framework(self, language: CodeLanguage) -> QAFramework:
        """Suggest appropriate test framework based on language."""
        if language in [CodeLanguage.JAVASCRIPT, CodeLanguage.TYPESCRIPT, CodeLanguage.JSX, CodeLanguage.TSX]:
            return QAFramework.JEST
        elif language == CodeLanguage.PYTHON:
            return QAFramework.PYTEST
        else:
            return QAFramework.UNITTEST

    def _analyze_source_code(self, file_path: Path, language: CodeLanguage) -> Dict[str, Any]:
        """Analyze source code to extract testable components."""
        content = file_path.read_text(encoding='utf-8')
        if language == CodeLanguage.PYTHON:
            return self._analyze_python_code(content)
        else:
            return self._analyze_js_ts_code(content)

    def _analyze_python_code(self, content: str) -> Dict[str, Any]:
        """Analyze Python code to extract classes, functions, and patterns."""
        try:
            tree = ast.parse(content)
            analysis = {'classes': [], 'functions': [], 'imports': [], 'constants': [], 'complexity': 'medium'}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    analysis['classes'].append({'name': node.name, 'methods': methods, 'line': node.lineno})
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    analysis['functions'].append({'name': node.name, 'args': [arg.arg for arg in node.args.args], 'line': node.lineno, 'is_async': isinstance(node, ast.AsyncFunctionDef)})
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis['imports'].append(node.module)
            return analysis
        except SyntaxError:
            return self._analyze_with_regex(content, 'python')

    def _analyze_js_ts_code(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code using regex patterns."""
        return self._analyze_with_regex(content, 'js_ts')

    def _analyze_with_regex(self, content: str, language_type: str) -> Dict[str, Any]:
        """Fallback analysis using regex patterns."""
        analysis = {'classes': [], 'functions': [], 'imports': [], 'constants': [], 'complexity': 'medium'}
        if language_type == 'python':
            class_pattern = 'class\\s+(\\w+).*?:'
            function_pattern = 'def\\s+(\\w+)\\s*\\([^)]*\\):'
            import_pattern = '(?:from\\s+\\w+\\s+)?import\\s+([^#\\n]+)'
        else:
            class_pattern = 'class\\s+(\\w+)'
            function_pattern = '(?:function\\s+(\\w+)|(\\w+)\\s*=\\s*(?:async\\s+)?\\([^)]*\\)\\s*=>|(?:async\\s+)?(\\w+)\\s*\\([^)]*\\)\\s*\\{)'
            import_pattern = 'import\\s+.*?from\\s+[\\\'"]([^\\\'"]+)[\\\'"]'
        for match in re.finditer(class_pattern, content):
            analysis['classes'].append({'name': match.group(1), 'methods': [], 'line': content[:match.start()].count('\n') + 1})
        for match in re.finditer(function_pattern, content):
            func_name = match.group(1) or match.group(2) or match.group(3)
            if func_name:
                analysis['functions'].append({'name': func_name, 'args': [], 'line': content[:match.start()].count('\n') + 1, 'is_async': 'async' in match.group(0)})
        for match in re.finditer(import_pattern, content):
            analysis['imports'].append(match.group(1))
        return analysis

    def _generate_test_suite(self, analysis: Dict[str, Any], framework: QAFramework, language: CodeLanguage) -> QATestSuite:
        """Generate complete test suite based on code analysis."""
        test_cases = []
        for class_info in analysis['classes']:
            test_cases.extend(self._generate_class_tests(class_info, framework))
        for func_info in analysis['functions']:
            test_cases.extend(self._generate_function_tests(func_info, framework))
        test_cases.extend(self._generate_edge_case_tests(analysis, framework))
        if len(analysis['classes']) > 1 or len(analysis['functions']) > 3:
            test_cases.extend(self._generate_integration_tests(analysis, framework))
        test_cases.extend(self._generate_error_handling_tests(analysis, framework))
        test_cases.extend(self.generate_security_tests(analysis, framework))
        pattern = self.patterns[framework.value]
        return QATestSuite(filename=f'test_{analysis.get('filename', 'module')}', framework=framework, language=language, test_cases=test_cases, imports=pattern['imports'], setup=pattern.get('setup'), teardown=pattern.get('teardown'))

    def _generate_class_tests(self, class_info: Dict[str, Any], framework: QAFramework) -> List[QATestCase]:
        """Generate test cases for a class."""
        tests = []
        class_name = class_info['name']
        tests.append(QATestCase(name=f'test_{class_name.lower()}_instantiation', description=f'Test {class_name} can be instantiated', test_type='unit', code=self._generate_constructor_test(class_name, framework)))
        for method in class_info.get('methods', []):
            if not method.startswith('_'):
                tests.append(QATestCase(name=f'test_{method}', description=f'Test {class_name}.{method} method', test_type='unit', code=self._generate_method_test(class_name, method, framework)))
        return tests

    def _generate_function_tests(self, func_info: Dict[str, Any], framework: QAFramework) -> List[QATestCase]:
        """Generate test cases for a function."""
        tests = []
        func_name = func_info['name']
        if func_name.startswith('test_') or func_name.startswith('_'):
            return tests
        tests.append(QATestCase(name=f'test_{func_name}', description=f'Test {func_name} function', test_type='unit', code=self._generate_function_test(func_name, func_info, framework)))
        tests.append(QATestCase(name=f'test_{func_name}_edge_cases', description=f'Test {func_name} edge cases', test_type='unit', code=self._generate_edge_case_test(func_name, func_info, framework)))
        return tests

    def _generate_constructor_test(self, class_name: str, framework: QAFramework) -> str:
        """Generate constructor test code."""
        if framework == QAFramework.JEST:
            return f"test('should create {class_name} instance', () => {{\n    const instance = new {class_name}();\n    expect(instance).toBeInstanceOf({class_name});\n\n}});"
        elif framework in [QAFramework.PYTEST, QAFramework.UNITTEST]:
            test_method = 'def test_' if framework == QAFramework.PYTEST else 'def test_'
            return f'{test_method}instantiation(self):\n        """Test {class_name} can be instantiated."""\n        instance = {class_name}()\n        assert isinstance(instance, {class_name})'
        return ''

    def _generate_method_test(self, class_name: str, method_name: str, framework: QAFramework) -> str:
        """Generate method test code."""
        if framework == QAFramework.JEST:
            return f"test('should execute {method_name} method', () => {{\n    const instance = new {class_name}();\n    const result = instance.{method_name}();\n    expect(result).toBeDefined();\n}});"
        elif framework in [QAFramework.PYTEST, QAFramework.UNITTEST]:
            return f'def test_{method_name}(self):\n        """Test {class_name}.{method_name} method."""\n        instance = {class_name}()\n        result = instance.{method_name}()\n        assert result is not None'
        return ''

    def _generate_function_test(self, func_name: str, func_info: Dict[str, Any], framework: QAFramework) -> str:
        """Generate function test code."""
        args = func_info.get('args', [])
        if framework == QAFramework.JEST:
            if func_info.get('is_async'):
                return f"test('should execute {func_name} function', async () => {{\n                    const result = await {func_name}()\n                    expect(result).toBeDefined()\n                }});"
            else:
                return f"test('should execute {func_name} function', () => {{\n    const result = {func_name}();\n    expect(result).toBeDefined();\n}});"
        elif framework in [QAFramework.PYTEST, QAFramework.UNITTEST]:
            if func_info.get('is_async'):
                return f'async def test_{func_name}(self):\n        """Test {func_name} function."""\n        result = await {func_name}()\n        assert result is not None'
            else:
                return f'def test_{func_name}(self):\n        """Test {func_name} function."""\n        result = {func_name}()\n        assert result is not None'
        return ''

    def _generate_edge_case_test(self, func_name: str, func_info: Dict[str, Any], framework: QAFramework) -> str:
        """Generate edge case test code."""
        if framework == QAFramework.JEST:
            return f"test('should handle {func_name} edge cases', () => {{\n    expect(() => {func_name}(null)).not.toThrow();\n    expect(() => {func_name}(undefined)).not.toThrow();\n}});"
        elif framework in [QAFramework.PYTEST, QAFramework.UNITTEST]:
            return f'def test_{func_name}_edge_cases(self):\n        """Test {func_name} edge cases."""\n        # Test with None input\n        try:\n            result = {func_name}(None)\n            assert True  # Should not raise exception\n        except Exception:\n            assert False, "Function should handle None input gracefully"'
        return ''

    def _generate_edge_case_tests(self, analysis: Dict[str, Any], framework: QAFramework) -> List[QATestCase]:
        """Generate edge case test scenarios."""
        tests = []
        for func_info in analysis['functions']:
            if func_info.get('args'):
                tests.append(QATestCase(name=f'test_{func_info['name']}_edge_cases', description=f'Test edge cases for {func_info['name']}', test_type='unit', code=self._generate_edge_case_test(func_info['name'], func_info, framework)))
        return tests

    def _generate_integration_tests(self, analysis: Dict[str, Any], framework: QAFramework) -> List[QATestCase]:
        """Generate integration test scenarios."""
        tests = []
        classes = analysis['classes']
        if len(classes) >= 2:
            tests.append(QATestCase(name='test_component_integration', description='Test integration between components', test_type='integration', code=self._generate_integration_test_code(classes, framework)))
        return tests

    def _generate_error_handling_tests(self, analysis: Dict[str, Any], framework: QAFramework) -> List[QATestCase]:
        """Generate error handling test scenarios."""
        tests = []
        for func_info in analysis['functions']:
            tests.append(QATestCase(name=f'test_{func_info['name']}_error_handling', description=f'Test error handling for {func_info['name']}', test_type='unit', code=self._generate_error_test_code(func_info['name'], framework)))
        return tests

    def _generate_integration_test_code(self, classes: List[Dict[str, Any]], framework: QAFramework) -> str:
        """Generate integration test code for multiple classes."""
        if framework == QAFramework.JEST:
            class1, class2 = (classes[0]['name'], classes[1]['name'])
            return f"test('should integrate {class1} and {class2}', () => {{\n    const instance1 = new {class1}();\n    const instance2 = new {class2}();\n\n    // Test interaction between instances\n    expect(instance1).toBeDefined();\n    expect(instance2).toBeDefined();\n\n    // Add specific integration logic here\n}});"
        elif framework in [QAFramework.PYTEST, QAFramework.UNITTEST]:
            class1, class2 = (classes[0]['name'], classes[1]['name'])
            return f'def test_component_integration(self):\n        """Test integration between {class1} and {class2}."""\n        instance1 = {class1}()\n        instance2 = {class2}()        # Test interaction between instances\n        assert instance1 is not None\n        assert instance2 is not None\n        # Add specific integration logic here'
        return ''

    def _generate_error_test_code(self, func_name: str, framework: QAFramework) -> str:
        """Generate error handling test code."""
        if framework == QAFramework.JEST:
            return f"""test('should handle {func_name} errors gracefully', () => {{\n                // Test with invalid inputs\n                expect(() => {func_name}(null)).not.toThrow();\n                expect(() => {func_name}(undefined)).not.toThrow();\n\n                // Test error scenarios\n                try {{\n                    {func_name}("invalid_input");\n                }} catch(error) {{\n                    expect(error).toBeDefined();\n                }}\n            }});"""
        elif framework in [QAFramework.PYTEST, QAFramework.UNITTEST]:
            return f'def test_{func_name}_error_handling(self):\n        """Test error handling for {func_name}."""\n        # Test with invalid inputs\n        try:\n            result = {func_name}(None)\n        except Exception as e:\n            # Should handle gracefully or raise appropriate error\n            assert isinstance(e, (ValueError, TypeError))\n\n        # Test with invalid data types\n        with pytest.raises((ValueError, TypeError)):\n            {func_name}("invalid_input")'
        return ''

    def generate_performance_tests(self, analysis: Dict[str, Any], framework: QAFramework) -> List[QATestCase]:
        """Generate performance test scenarios."""
        tests = []
        for func_info in analysis['functions']:
            tests.append(QATestCase(name=f'test_{func_info['name']}_performance', description=f'Test performance of {func_info['name']}', test_type='performance', code=self._generate_performance_test_code(func_info['name'], framework)))
        return tests

    def _generate_performance_test_code(self, func_name: str, framework: QAFramework) -> str:
        """Generate performance test code."""
        if framework == QAFramework.JEST:
            return f"test('should execute {func_name} within time limit', () => {{\n                const startTime = Date.now()\n                {func_name}()\n                const endTime = Date.now()\n\n                const executionTime = endTime - startTime\n                expect(executionTime).toBeLessThan(1000)\n                // Should complete within 1 second\n            }});"
        elif framework in [QAFramework.PYTEST, QAFramework.UNITTEST]:
            return f'def test_{func_name}_performance(self):\n        """Test performance of {func_name}."""\ntry:\n    import time\nexcept ImportError:\n    pass\n\n        start_time = time.time()\n        {func_name}()\n        end_time = time.time()\n\n        execution_time = end_time - start_time\n        assert execution_time < 1.0, f"Function took too long: {{execution_time:.2f}}s"'
        return ''

    def generate_security_tests(self, analysis: Dict[str, Any], framework: QAFramework) -> List[QATestCase]:
        """Generate security test scenarios."""
        tests = []
        for func_info in analysis['functions']:
            if any((keyword in func_info['name'].lower() for keyword in ['input', 'parse', 'process', 'handle'])):
                tests.append(QATestCase(name=f'test_{func_info['name']}_security', description=f'Test security aspects of {func_info['name']}', test_type='security', code=self._generate_security_test_code(func_info['name'], framework)))
        return tests

    def _generate_security_test_code(self, func_name: str, framework: QAFramework) -> str:
        """Generate security test code."""
        if framework == QAFramework.JEST:
            return f"""test('should handle {func_name} security scenarios', () => {{\n                // Test with malicious inputs\n                const maliciousInputs = ['<script>alert("xss")</script>', '../../../etc/passwd', 'DROP TABLE users;'];\n\n                maliciousInputs.forEach(input => {{\n                    expect(() => {func_name}(input)).not.toThrow();\n                }});\n            }});"""
        elif framework in [QAFramework.PYTEST, QAFramework.UNITTEST]:
            return f'''def test_{func_name}_security(self):\n        """Test security aspects of {func_name}."""\n        # Test with malicious inputs\n        malicious_inputs = [\n            '<script>alert("xss")</script>',\n            '../../../etc/passwd',\n            'DROP TABLE users;',\n            '{{}}.__class__.__bases__[0].__subclasses__()',\n        ]\n\n        for malicious_input in malicious_inputs:\n            try:\n                result = {func_name}(malicious_input)\n                # Should either handle safely or raise appropriate error\n                assert result is not None or isinstance(result, str)\n            except (ValueError, SecurityError, Exception):\n                # Expected behavior for malicious input\n                pass'''
        return ''

    def _render_test_file(self, test_suite: QATestSuite) -> str:
        """Render the complete test file content."""
        lines = []
        lines.append('"""')
        lines.append(f'Test file for {test_suite.filename}')
        lines.append('Generated automatically by QATestGenerator')
        lines.append(f'Framework: {test_suite.framework.value}')
        lines.append('"""')
        lines.append('')
        lines.extend(test_suite.imports)
        lines.append('')
        if test_suite.language == CodeLanguage.PYTHON:
            lines.append(f'from {test_suite.filename} import *')
        else:
            lines.append(f"import {{ }} from './{test_suite.filename}';")
        lines.append('')
        if test_suite.setup:
            lines.append(test_suite.setup)
            lines.append('')
        if test_suite.framework == QAFramework.JEST:
            lines.append(f"describe('{test_suite.filename}', () => {{")
            for test_case in test_suite.test_cases:
                lines.append('    ' + test_case.code.replace('\n', '\n    '))
                lines.append('')
            lines.append('});')
        elif test_suite.framework in [QAFramework.PYTEST, QAFramework.UNITTEST]:
            if test_suite.framework == QAFramework.UNITTEST:
                lines.append(f'class Test{test_suite.filename.title()}(unittest.QATestCase):')
                indent = '    '
            else:
                lines.append(f'class Test{test_suite.filename.title()}:')
                indent = '    '
            lines.append('')
            for test_case in test_suite.test_cases:
                test_lines = test_case.code.split('\n')
                for line in test_lines:
                    lines.append(indent + line)
                lines.append('')
        if test_suite.teardown:
            lines.append(test_suite.teardown)
            lines.append('')
        if test_suite.language == CodeLanguage.PYTHON and test_suite.framework == QAFramework.UNITTEST:
            lines.append('if __name__ == "__main__":')
            lines.append('    unittest.main()')
        return '\n'.join(lines)

    def suggest_tests_for_task(self, task_id: str, output_dir: str) -> Dict[str, Any]:
        """Suggest tests for a specific task based on its output."""
        output_path = Path(output_dir) / task_id
        if not output_path.exists():
            return {'error': f'Task output directory not found: {output_path}'}
        suggestions = {'task_id': task_id, 'suggested_tests': [], 'coverage_gaps': [], 'integration_points': []}
        code_files = []
        for ext in ['*.py', '*.js', '*.ts', '*.jsx', '*.tsx']:
            code_files.extend(output_path.rglob(ext))
        for code_file in code_files:
            try:
                analysis = self._analyze_source_code(code_file, self._detect_language(code_file))
                suggestions['suggested_tests'].append({'file': str(code_file.relative_to(output_path)), 'test_count': len(analysis['classes']) + len(analysis['functions']), 'complexity': analysis['complexity'], 'priority': 'high' if analysis['complexity'] == 'high' else 'medium'})
            except Exception as e:
                suggestions['coverage_gaps'].append({'file': str(code_file.relative_to(output_path)), 'issue': f'Could not analyze: {str(e)}'})
        return suggestions

def suggest_tests():
    """Legacy function for backward compatibility."""
    return [{'file': 'orchestration/qa_validation.py', 'suggestion': 'Add test for invalid config file'}, {'file': 'agents/qa.py', 'suggestion': 'Test QA agent with malformed state input'}]

def generate_tests_for_task(task_id: str, output_dir: str='outputs') -> Dict[str, Any]:
    """Convenience function to generate tests for a task."""
    generator = QATestGenerator()
    return generator.suggest_tests_for_task(task_id, output_dir)
if __name__ == '__main__':
    generator = QATestGenerator()
    try:
        test_content = generator.generate_test_file('agents/qa.py', 'tests/generated/test_qa_agent.py', QAFramework.PYTEST)
        print('Generated test file successfully')
        print('First 500 characters:')
        print(test_content[:500])
    except Exception as e:
        print(f'Error generating test: {e}')
    suggestions = suggest_tests()
    for s in suggestions:
        print(f'Test suggestion: {s['file']} - {s['suggestion']}')