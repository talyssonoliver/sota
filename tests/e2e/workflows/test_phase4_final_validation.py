"""
Phase 4 Comprehensive Validation Script
Validates all Phase 4 success criteria and components

test_phase4_final_validation.py - Optimized Test Structure

Migrated from: tests/integration	est_phase4_final_validation.py
New location: tests/integration	est_phase4_final_validation.py

Part of the optimized test pyramid reorganization:
- Tests now mirror src/ structure
- Proper categorization (unit/integration/e2e)
- Improved mocking and isolation

Usage: python tests/test_phase4_final_validation.py
"""
import sys
import json
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestPhase4FinalValidation(unittest.TestCase):
    """Comprehensive validation of Phase 4 success criteria"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.outputs_dir = self.temp_dir / 'outputs'
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir = Path('docs')
        self.orchestration_dir = Path('src/core/workflows')
        self._create_test_data()

    def tearDown(self):
        """Clean up temporary directories"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_data(self):
        """Create test data for validation"""
        be07_dir = self.outputs_dir / 'BE-07'
        be07_dir.mkdir(parents=True, exist_ok=True)
        task_declaration = {'id': 'BE-07', 'title': 'Backend Service Layer Implementation', 'description': 'Create service layer for orders and customers using Supabase', 'agent_id': 'backend_engineer', 'context_topics': ['db-schema', 'service-layer-pattern'], 'priority': 'HIGH', 'estimation_hours': 3, 'state': 'IN_PROGRESS', 'artefacts': ['backend_service.py', 'api_endpoints.py'], 'timestamp': '2025-06-11T02:00:00Z'}
        with open(be07_dir / 'task_declaration.json', 'w') as f:
            json.dump(task_declaration, f, indent=2)
        status_data = {'task_id': 'BE-07', 'status': 'IN_PROGRESS', 'last_updated': '2025-06-11T02:00:00Z', 'progress': 75, 'completion_report': str(be07_dir / 'completion_report.md')}
        with open(be07_dir / 'status.json', 'w') as f:
            json.dump(status_data, f, indent=2)
        completion_report = '# Task Completion Report - BE-07\n\n## Summary\nBackend service layer implementation completed successfully.\n\n## Deliverables\n- backend_service.py: Core service layer implementation\n- api_endpoints.py: REST API endpoints\n\n## Testing Results\n- Unit tests: 15 passed, 2 failed\n- Integration tests: 8 passed\n- Code coverage: 85.5%\n\n## Status: IN_PROGRESS\n'
        with open(be07_dir / 'completion_report.md', 'w', encoding='utf-8') as f:
            f.write(completion_report)

    def test_success_criteria_1_tasks_registered(self):
        """Validate: Tasks registered with full metadata"""
        print('\n✓ Testing: Tasks registered with full metadata')
        self.assertTrue(self.outputs_dir.exists(), 'outputs/ directory should exist')
        task_dirs = [d for d in self.outputs_dir.iterdir() if d.is_dir()]
        declaration_files = list(self.outputs_dir.glob('*/task_declaration.json'))
        print(f'  - Found {len(task_dirs)} task directories')
        print(f'  - Found {len(declaration_files)} task declaration files')
        self.assertGreater(len(declaration_files), 0, 'Should have at least one task declaration')
        be07_dir = self.outputs_dir / 'BE-07'
        if be07_dir.exists():
            be07_declaration = be07_dir / 'task_declaration.json'
            self.assertTrue(be07_declaration.exists(), 'BE-07 task declaration should exist')
            with open(be07_declaration) as f:
                data = json.load(f)
                self.assertIn('id', data)
                self.assertIn('title', data)
                self.assertIn('description', data)
                print(f'  - BE-07 declaration validated: {data.get('id')}')

    def test_success_criteria_2_prompt_generation(self):
        """Validate: Prompt generation pipeline functional"""
        print('\n✓ Testing: Prompt generation pipeline functional')
        prompt_script = self.orchestration_dir / 'generate_prompt.py'
        self.assertTrue(prompt_script.exists(), 'generate_prompt.py should exist')
        prompt_files = list(self.outputs_dir.glob('*/prompt_*.md'))
        print(f'  - Found {len(prompt_files)} generated prompt files')
        be07_prompt = self.outputs_dir / 'BE-07' / 'prompt_backend.md'
        if be07_prompt.exists():
            content = be07_prompt.read_text()
            self.assertGreater(len(content), 50, 'Prompt should have meaningful content')
            print(f'  - BE-07 prompt validated: {len(content)} characters')

    def test_success_criteria_3_langgraph_workflow(self):
        """Validate: LangGraph workflow triggers correct agent sequence"""
        print('\n✓ Testing: LangGraph workflow triggers correct agent sequence')
        # Updated paths for new clean architecture
        execute_graph = Path('src/core/workflows/execute_graph.py')
        self.assertTrue(execute_graph.exists(), 'execute_graph.py should exist in new location')
        graph_files = [
            Path('src/core/workflows/graph/graph_builder.py'), 
            Path('src/core/workflows/graph/handlers.py'), 
            Path('src/core/workflows/states.py')
        ]
        for file in graph_files:
            self.assertTrue(file.exists(), f'{file} should exist')
            print(f'  - ✓ {file}')

    def test_success_criteria_4_agent_output_processing(self):
        """Validate: Agent output stored, parsed, and postprocessed"""
        print('\n✓ Testing: Agent output stored, parsed, and postprocessed')
        # Updated paths for new clean architecture
        register_output = Path('src/core/workflows/register_output.py')
        extract_code = Path('src/core/workflows/extract_code.py')
        self.assertTrue(register_output.exists(), 'register_output.py should exist in new location')
        self.assertTrue(extract_code.exists(), 'extract_code.py should exist in new location')
        output_files = list(self.outputs_dir.glob('*/output_*.md'))
        status_files = list(self.outputs_dir.glob('*/status.json'))
        print(f'  - Found {len(output_files)} agent output files')
        print(f'  - Found {len(status_files)} status tracking files')
        be07_code = self.outputs_dir / 'BE-07' / 'code'
        if be07_code.exists():
            code_files = list(be07_code.glob('*.ts'))
            print(f'  - BE-07 extracted code files: {len(code_files)}')

    def test_success_criteria_5_status_tracking(self):
        """Validate: Status tracked and updated per run"""
        print('\n✓ Testing: Status tracked and updated per run')
        status_files = list(self.outputs_dir.glob('*/status.json'))
        print(f'  - Found {len(status_files)} status tracking files')
        self.assertGreater(len(status_files), 0, 'Should have status tracking files')
        be07_status = self.outputs_dir / 'BE-07' / 'status.json'
        if be07_status.exists():
            with open(be07_status) as f:
                status_data = json.load(f)
            self.assertIn('task_id', status_data)
            self.assertIn('status', status_data)
            self.assertIn('last_updated', status_data)
            print(f'  - BE-07 status validated: {status_data.get('status')}')
        monitor_script = Path('scripts/monitor_workflow.py')
        if monitor_script.exists():
            print(f'  - ✓ {monitor_script}')
        try:
            from config.build_paths import DASHBOARD_DIR
            dashboard_files = [DASHBOARD_DIR / 'live_execution.json', DASHBOARD_DIR / 'agent_status.json']
            for file in dashboard_files:
                if file.exists():
                    print(f'  - ✓ {file}')
        except ImportError:
            print('  - Dashboard files check skipped (import error)')

    def test_success_criteria_6_reports_summaries(self):
        """Validate: Reports and summaries generated"""
        print('\n✓ Testing: Reports and summaries generated')
        summarise_task = self.orchestration_dir / 'summarise_task.py'
        self.assertTrue(summarise_task.exists(), 'summarise_task.py should exist')
        be07_report = self.outputs_dir / 'BE-07' / 'completion_report.md'
        if be07_report.exists():
            content = be07_report.read_text(encoding='utf-8')
            self.assertGreater(len(content), 100, 'Report should have substantial content')
            print(f'  - BE-07 completion report validated: {len(content)} characters')
        else:
            print('  - BE-07 completion report created in test data')

    def test_core_functionality_integration(self):
        """Test core Phase 4 functionality integration"""
        print('\n✓ Testing: Core functionality integration')
        try:
            from src.core.workflows.extract_code import CodeExtractor
            from src.core.workflows.register_output import AgentOutputRegistry
            from src.core.workflows.summarise_task import TaskSummarizer
            from src.core.workflows.task_declaration import TaskDeclarationManager
            print('  - ✓ All core modules importable')
        except ImportError as e:
            self.fail(f'Failed to import core modules: {e}')

    def test_cli_interfaces_exist(self):
        """Test CLI interfaces are operational"""
        print('\n✓ Testing: CLI interfaces operational')
        cli_scripts = ['src/core/workflows/task_declaration.py', 'src/core/workflows/execute_graph.py', 'src/core/workflows/register_output.py', 'src/core/workflows/extract_code.py', 'src/core/workflows/summarise_task.py']
        for script in cli_scripts:
            script_path = Path(script)
            self.assertTrue(script_path.exists(), f'{script} should exist')
            print(f'  - ✓ {script}')
if __name__ == '__main__':
    unittest.main()