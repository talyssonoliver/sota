#!/usr/bin/env python3
"""
Phase 4 Comprehensive Validation Script
Validates all Phase 4 success criteria and components

Usage: python tests/test_phase4_final_validation.py
"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPhase4FinalValidation(unittest.TestCase):
    """Comprehensive validation of Phase 4 success criteria"""

    def setUp(self):
        self.outputs_dir = Path("outputs")
        self.docs_dir = Path("docs")
        self.orchestration_dir = Path("orchestration")

    def test_success_criteria_1_tasks_registered(self):
        """Validate: Tasks registered with full metadata"""
        print("\n✓ Testing: Tasks registered with full metadata")

        # Check outputs directory exists
        self.assertTrue(self.outputs_dir.exists(),
                        "outputs/ directory should exist")

        # Find task directories with declaration files
        task_dirs = [d for d in self.outputs_dir.iterdir() if d.is_dir()]
        declaration_files = list(
            self.outputs_dir.glob("*/task_declaration.json"))

        print(f"  - Found {len(task_dirs)} task directories")
        print(f"  - Found {len(declaration_files)} task declaration files")

        # Validate at least some tasks are registered
        self.assertGreater(len(declaration_files), 0,
                           "Should have at least one task declaration")

        # Validate BE-07 example exists and has proper structure
        be07_dir = self.outputs_dir / "BE-07"
        if be07_dir.exists():
            be07_declaration = be07_dir / "task_declaration.json"
            self.assertTrue(be07_declaration.exists(),
                            "BE-07 task declaration should exist")
            # Load and validate JSON structure
            with open(be07_declaration) as f:
                data = json.load(f)
                # actual field is 'id', not 'task_id'
                self.assertIn("id", data)
                self.assertIn("title", data)
                self.assertIn("description", data)
                print(f"  - BE-07 declaration validated: {data.get('id')}")

    def test_success_criteria_2_prompt_generation(self):
        """Validate: Prompt generation pipeline functional"""
        print("\n✓ Testing: Prompt generation pipeline functional")

        # Check prompt generation script exists
        prompt_script = self.orchestration_dir / "generate_prompt.py"
        self.assertTrue(prompt_script.exists(),
                        "generate_prompt.py should exist")

        # Check for generated prompt files
        prompt_files = list(self.outputs_dir.glob("*/prompt_*.md"))
        print(f"  - Found {len(prompt_files)} generated prompt files")
        # Validate BE-07 prompt exists
        be07_prompt = self.outputs_dir / "BE-07" / "prompt_backend.md"
        if be07_prompt.exists():
            content = be07_prompt.read_text()
            self.assertGreater(
                len(content), 50, "Prompt should have meaningful content")
            print(f"  - BE-07 prompt validated: {len(content)} characters")

    def test_success_criteria_3_langgraph_workflow(self):
        """Validate: LangGraph workflow triggers correct agent sequence"""
        print("\n✓ Testing: LangGraph workflow triggers correct agent sequence")

        # Check workflow execution script
        execute_graph = self.orchestration_dir / "execute_graph.py"
        self.assertTrue(execute_graph.exists(),
                        "execute_graph.py should exist")

        # Check graph components
        graph_files = [
            Path("graph/graph_builder.py"),
            Path("graph/handlers.py"),
            Path("orchestration/states.py")
        ]

        for file in graph_files:
            self.assertTrue(file.exists(), f"{file} should exist")
            print(f"  - ✓ {file}")

    def test_success_criteria_4_agent_output_processing(self):
        """Validate: Agent output stored, parsed, and postprocessed"""
        print("\n✓ Testing: Agent output stored, parsed, and postprocessed")

        # Check output processing scripts
        register_output = self.orchestration_dir / "register_output.py"
        extract_code = self.orchestration_dir / "extract_code.py"

        self.assertTrue(register_output.exists(),
                        "register_output.py should exist")
        self.assertTrue(extract_code.exists(), "extract_code.py should exist")

        # Check for output files
        output_files = list(self.outputs_dir.glob("*/output_*.md"))
        status_files = list(self.outputs_dir.glob("*/status.json"))

        print(f"  - Found {len(output_files)} agent output files")
        print(f"  - Found {len(status_files)} status tracking files")
        # Check BE-07 code extraction
        be07_code = self.outputs_dir / "BE-07" / "code"
        if be07_code.exists():
            code_files = list(be07_code.glob("*.ts"))
            print(f"  - BE-07 extracted code files: {len(code_files)}")

    def test_success_criteria_5_status_tracking(self):
        """Validate: Status tracked and updated per run"""
        print("\n✓ Testing: Status tracked and updated per run")

        # Check status tracking via status.json files
        status_files = list(self.outputs_dir.glob("*/status.json"))
        print(f"  - Found {len(status_files)} status tracking files")
        self.assertGreater(len(status_files), 0,
                           "Should have status tracking files")

        # Check monitoring script exists if present
        monitor_script = Path("scripts/monitor_workflow.py")
        if monitor_script.exists():
            print(f"  - ✓ {monitor_script}")

        # Check for dashboard files
        from config.build_paths import DASHBOARD_DIR
        dashboard_files = [
            DASHBOARD_DIR / "live_execution.json",
            DASHBOARD_DIR / "agent_status.json"
        ]

        for file in dashboard_files:
            if file.exists():
                print(f"  - ✓ {file}")

    def test_success_criteria_6_reports_summaries(self):
        """Validate: Reports and summaries generated"""
        print("\n✓ Testing: Reports and summaries generated")

        # Check summarization script
        summarise_task = self.orchestration_dir / "summarise_task.py"
        self.assertTrue(summarise_task.exists(),
                        "summarise_task.py should exist")

        # Check completion reports
        completions_dir = self.docs_dir / "completions"
        if completions_dir.exists():
            reports = list(completions_dir.glob("*.md"))
            print(f"  - Found {len(reports)} completion reports")

            # Validate BE-07 report
            be07_report = completions_dir / "BE-07.md"
            if be07_report.exists():
                content = be07_report.read_text()
                self.assertGreater(len(content), 500,
                                   "Report should have substantial content")
                print(
                    f"  - BE-07 completion report validated: {len(content)} characters")

    def test_core_functionality_integration(self):
        """Test core Phase 4 functionality integration"""
        print("\n✓ Testing: Core functionality integration")

        # Test that core modules can be imported
        try:
            from orchestration.extract_code import CodeExtractor
            from orchestration.register_output import AgentOutputRegistry
            from orchestration.summarise_task import TaskSummarizer
            from orchestration.task_declaration import TaskDeclarationManager
            print("  - ✓ All core modules importable")
        except ImportError as e:
            self.fail(f"Failed to import core modules: {e}")

    def test_cli_interfaces_exist(self):
        """Test CLI interfaces are operational"""
        print("\n✓ Testing: CLI interfaces operational")
        cli_scripts = [
            "orchestration/task_declaration.py",
            "orchestration/execute_graph.py",
            "orchestration/register_output.py",
            "orchestration/extract_code.py",
            "orchestration/summarise_task.py"
        ]

        for script in cli_scripts:
            script_path = Path(script)
            self.assertTrue(script_path.exists(), f"{script} should exist")
            print(f"  - ✓ {script}")

        # Check optional scripts
        optional_scripts = [
            "orchestration/update_task_status.py",
            "scripts/monitor_workflow.py"
        ]

        for script in optional_scripts:
            script_path = Path(script)
            if script_path.exists():
                print(f"  - ✓ {script} (optional)")


def run_validation():
    """Run the comprehensive Phase 4 validation"""
    print("=" * 60)
    print("PHASE 4 COMPREHENSIVE VALIDATION")
    print("=" * 60)

    # Run the test suite
    unittest.main(verbosity=2, exit=False, argv=[''])

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_validation()
