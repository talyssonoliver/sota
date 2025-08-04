#!/usr/bin/env python3
"""
Revert and Fix Syntax Errors
This script identifies and fixes the syntax errors introduced by malformed import blocks.
"""

import ast
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyntaxRevertFixer:
    def __init__(self):
        self.fixed_files = []
        self.failed_files = []

    def fix_malformed_try_blocks(self, content: str) -> str:
        """Fix malformed try/except blocks that are causing syntax errors."""
        lines = content.split("\n")
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Pattern 1: Fix try blocks with import on same line
            if "try:" in line and "import" in line and line.strip() != "try:":
                # Split into two lines
                parts = line.split("import", 1)
                if len(parts) == 2:
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(parts[0].rstrip() + "try:")
                    fixed_lines.append(" " * (indent + 4) + "import" + parts[1])
                else:
                    fixed_lines.append(line)

            # Pattern 2: Fix except blocks without proper indentation
            elif line.strip() == "except ImportError:" and i + 1 < len(lines):
                # Make sure next line is properly indented pass
                fixed_lines.append(line)
                if i + 1 < len(lines) and lines[i + 1].strip() == "pass":
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(" " * (indent + 4) + "pass")
                    i += 1
                else:
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(" " * (indent + 4) + "pass")

            # Pattern 3: Remove import statements in the middle of code blocks
            elif (
                i > 0
                and not line.strip().startswith(
                    ("import ", "from ", "try:", "except", "#", '"""', "'''")
                )
                and " import " in line
            ):
                # This might be an import statement incorrectly placed
                if "import" in line and not any(
                    x in line for x in ["# import", '"import', "'import"]
                ):
                    # Try to fix by removing the import part
                    fixed_lines.append(line.split("import")[0].rstrip())
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

            i += 1

        return "\n".join(fixed_lines)

    def remove_duplicate_imports(self, content: str) -> str:
        """Remove duplicate import statements."""
        lines = content.split("\n")
        seen_imports = set()
        fixed_lines = []

        for line in lines:
            if line.strip().startswith(("import ", "from ")):
                if line.strip() not in seen_imports:
                    seen_imports.add(line.strip())
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_indentation_errors(self, content: str) -> str:
        """Fix indentation errors in the code."""
        lines = content.split("\n")
        fixed_lines = []
        expected_indent = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            if not stripped:  # Empty line
                fixed_lines.append("")
                continue

            # Calculate expected indentation
            if i > 0 and lines[i - 1].strip().endswith(":"):
                expected_indent += 4
            elif stripped in [
                "pass",
                "continue",
                "break",
                "return",
            ] or stripped.startswith("return "):
                # These statements might end a block
                current_indent = len(line) - len(line.lstrip())
                fixed_lines.append(" " * current_indent + stripped)
                if (
                    i + 1 < len(lines)
                    and lines[i + 1].strip()
                    and not lines[i + 1]
                    .strip()
                    .startswith(("elif", "else:", "except", "finally"))
                ):
                    expected_indent = max(0, current_indent - 4)
                continue
            elif stripped.startswith(("elif ", "else:", "except", "finally")):
                expected_indent = max(0, expected_indent - 4)

            # Apply indentation
            if line.strip():
                current_indent = len(line) - len(line.lstrip())
                # Keep original indentation if it seems reasonable
                if abs(current_indent - expected_indent) <= 4:
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(" " * expected_indent + stripped)

            # Update expected indent for certain keywords
            if stripped.startswith(
                (
                    "def ",
                    "class ",
                    "if ",
                    "elif ",
                    "else:",
                    "for ",
                    "while ",
                    "try:",
                    "except",
                    "finally:",
                    "with ",
                )
            ):
                if not stripped.endswith(":"):
                    # Add missing colon
                    fixed_lines[-1] += ":"

        return "\n".join(fixed_lines)

    def fix_file(self, file_path: Path) -> bool:
        """Fix syntax errors in a single file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # Apply fixes
            content = self.fix_malformed_try_blocks(content)
            content = self.remove_duplicate_imports(content)
            content = self.fix_indentation_errors(content)

            # Verify the syntax is valid
            try:
                ast.parse(content)

                if content != original_content:
                    file_path.write_text(content, encoding="utf-8")
                    self.fixed_files.append(str(file_path))
                    logger.info(f"✅ Fixed: {file_path}")

                return True

            except SyntaxError as e:
                # If still has syntax errors, log them
                self.failed_files.append((str(file_path), str(e)))
                logger.error(f"❌ Still has errors: {file_path} - {e}")
                return False

        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            self.failed_files.append((str(file_path), str(e)))
            return False

    def fix_all_syntax_errors(self):
        """Fix all files with syntax errors."""
        # List of files with syntax errors from the validation output
        error_files = [
            "src/core/workflows/automation_health_check.py",
            "src/core/workflows/complete_task.py",
            "src/core/workflows/documentation_agent.py",
            "src/core/workflows/email_integration.py",
            "src/core/workflows/enhanced_workflow.py",
            "src/core/workflows/error_handling.py",
            "src/core/workflows/execute_graph.py",
            "src/core/workflows/execute_task.py",
            "src/core/workflows/hitl_engine.py",
            "src/core/workflows/hitl_task_metadata.py",
            "src/infrastructure/utils/input_validation.py",
            "scripts/archive_task.py",
            "scripts/batch_qa_generation.py",
            "scripts/debug_memory.py",
            "scripts/end_to_end_test.py",
            "scripts/generate_memory_key.py",
            "scripts/github_finalise.py",
            "scripts/list_pending_reviews.py",
            "scripts/manage_knowledge_reviews.py",
            "scripts/mark_review_complete.py",
            "scripts/monitor_workflow.py",
            "scripts/patch_dotenv.py",
            "scripts/run_optimized_tests_enhanced.py",
            "scripts/update_dashboard.py",
            "scripts/validation/validate_chart_fix.py",
            "scripts/validation/validate_hitl_dashboard.py",
            "tests/helpers.py",
            "tests/integration/test_analytics.py",
            "tests/integration/test_api_integration_webhooks.py",
            "tests/integration/test_business_endpoints.py",
            "tests/integration/test_dashboard_integration.py",
            "tests/integration/test_dashboard_routes.py",
            "tests/integration/test_dashboard_stability.py",
            "tests/integration/test_execution_monitor.py",
            "tests/integration/test_hitl_engine_integration.py",
            "tests/integration/test_phase2_optimizations.py",
            "tests/integration/test_step_5_4_qa_registration.py",
            "tests/utils/test_utils.py",
            "tests/utils/workflow_helpers.py",
            "tests/e2e/performance/integration_enhanced_eod_reporting.py",
            "tests/e2e/performance/performance_enhanced_eod_reporting.py",
            "tests/e2e/system/test_escalation_system.py",
            "tests/e2e/workflows/test_phase4_final_validation.py",
            "tests/e2e/workflows/test_phase6_automation.py",
            "tests/e2e/workflows/test_phase7_hitl.py",
            "tests/fixtures/mocks/mock_dotenv.py",
            "tests/integration/api/test_api_integration_webhooks.py",
            "tests/integration/dashboard/test_dashboard_integration.py",
            "tests/integration/dashboard/test_dashboard_routes.py",
            "tests/integration/dashboard/test_dashboard_stability.py",
            "tests/integration/workflows/test_workflow_integration.py",
            "tests/unit/core/test_chromadb_patch.py",
            "tests/unit/core/test_chromadb_patch_optimized.py",
            "tests/unit/core/test_cleanup_verification.py",
            "tests/unit/core/test_config_loading.py",
            "tests/unit/core/test_daily_cycle.py",
            "tests/unit/core/test_enhanced_eod_reporting.py",
            "tests/unit/core/test_enhanced_qa.py",
            "tests/unit/core/test_environment.py",
            "tests/unit/core/test_generate_briefing.py",
            "tests/unit/core/test_generate_briefing_comprehensive.py",
            "tests/unit/core/test_patches.py",
            "tests/unit/core/test_qa_execution.py",
            "tests/unit/core/test_timeline_method.py",
            "tests/unit/core/test_utils.py",
            "tests/unit/core/agents/test_enhanced_qa.py",
            "tests/unit/core/agents/test_qa_agent_decisions.py",
            "tests/unit/core/agents/test_qa_execution.py",
            "tests/unit/core/workflows/test_daily_cycle.py",
            "tests/unit/core/workflows/test_enhanced_eod_reporting.py",
            "tests/unit/core/workflows/test_enhanced_workflow.py",
            "tests/unit/core/workflows/test_generate_briefing.py",
            "tests/unit/core/workflows/test_generate_briefing_comprehensive.py",
            "tests/unit/core/workflows/test_langgraph_workflow.py",
            "tests/unit/core/workflows/test_timeline_method.py",
            "tests/unit/core/workflows/test_workflow_helpers.py",
            "tests/unit/interfaces/dashboard/test_hitl_cli.py",
            "tests/unit/interfaces/dashboard/test_hitl_cli_comprehensive.py",
            "tests/unit/interfaces/dashboard/test_hitl_dashboard_widgets.py",
            "tests/unit/interfaces/dashboard/test_hitl_engine_integration.py",
            "tests/unit/platform/memory/test_memory_config.py",
            "tests/unit/platform/memory/test_memory_engine.py",
            "tests/unit/platform/memory/test_memory_functionality.py",
            "visualization/build_json.py",
            "examples/agent_output_demo.py",
            "examples/annotate_context_tags_tasks.py",
            "examples/complete_validation.py",
            "examples/daily_cycle_demo.py",
            "examples/hitl_cli_demo.py",
            "examples/human-in-the-Loop_context_review.py",
            "examples/mcp_context_usage.py",
            "orchestration/automation_health_check.py",
            "orchestration/complete_task.py",
            "orchestration/daily_cycle.py",
            "orchestration/delegation.py",
            "orchestration/documentation_agent.py",
            "orchestration/email_integration.py",
            "orchestration/error_handling.py",
            "orchestration/execute_task.py",
            "orchestration/extract_code.py",
            "orchestration/generate_briefing.py",
            "orchestration/generate_prompt.py",
            "orchestration/hitl_engine.py",
            "orchestration/langgraph_qa_integration.py",
            "orchestration/notification_handlers.py",
            "orchestration/plan_execution_manager.py",
            "orchestration/qa_execution.py",
            "orchestration/qa_validation.py",
            "orchestration/review_task.py",
            "orchestration/run_workflow.py",
            "orchestration/sprint_visualizer.py",
            "orchestration/summarise_task.py",
            "orchestration/task_declaration.py",
            "orchestration/task_lifecycle.py",
            "main.py",
        ]

        logger.info(
            f"🔧 Attempting to fix {len(error_files)} files with syntax errors..."
        )

        for file_path_str in error_files:
            file_path = Path(file_path_str)
            if file_path.exists():
                self.fix_file(file_path)
            else:
                logger.warning(f"⚠️ File not found: {file_path}")

        # Summary
        logger.info("\n📊 Syntax Fix Summary:")
        logger.info(f"✅ Successfully fixed: {len(self.fixed_files)} files")
        logger.info(f"❌ Still have errors: {len(self.failed_files)} files")

        if self.failed_files:
            logger.info("\n❌ Files that still need manual fixing:")
            for file_path, error in self.failed_files[:10]:  # Show first 10
                logger.info(f"  - {file_path}: {error}")


def main():
    fixer = SyntaxRevertFixer()
    fixer.fix_all_syntax_errors()


if __name__ == "__main__":
    main()
