#!/usr/bin/env python3
"""
Complete Task Workflow for Phase 5

End-to-end task completion orchestration that coordinates QA validation,
documentation generation, archival, and dashboard updates.
"""

import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from documentation_agent import DocumentationAgent, DocumentationReport
from qa_validation import QAResult, QAValidationEngine


@dataclass
class CompletionStep:
    """Represents a step in the completion workflow"""
    name: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None
    output_files: List[str] = None

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []


@dataclass
class CompletionResult:
    """Result of complete task workflow"""
    task_id: str
    overall_status: str
    completion_time: str
    steps: List[CompletionStep]
    qa_result: Optional[QAResult] = None
    documentation_report: Optional[DocumentationReport] = None
    archive_path: Optional[str] = None
    dashboard_updated: bool = False
    next_steps: List[str] = None

    def __post_init__(self):
        if self.next_steps is None:
            self.next_steps = []


class TaskCompletionOrchestrator:
    """Orchestrates the complete task completion workflow"""

    def __init__(self, config_path: Optional[str] = None):
        self.outputs_dir = Path("outputs")
        self.archives_dir = Path("archives")
        self.archives_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = Path("reports/completion")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.dashboard_dir = Path("dashboard")

        # Initialize agents
        self.qa_engine = QAValidationEngine(config_path)
        self.doc_agent = DocumentationAgent()

    def complete_task(
            self,
            task_id: str,
            skip_qa: bool = False,
            skip_archive: bool = False) -> CompletionResult:
        """Execute complete task completion workflow"""
        print(f"🚀 Starting task completion workflow for {task_id}")

        # Initialize completion result
        completion_result = CompletionResult(
            task_id=task_id,
            overall_status="RUNNING",
            completion_time=datetime.now().isoformat(),
            steps=[]
        )

        try:
            # Step 1: Validate prerequisites
            self._execute_step(completion_result, "validate_prerequisites",
                               lambda: self._validate_prerequisites(task_id))

            # Step 2: QA Validation
            if not skip_qa:
                qa_result = self._execute_step(
                    completion_result,
                    "qa_validation",
                    lambda: self.qa_engine.validate_task(task_id))
                completion_result.qa_result = qa_result
            else:
                self._skip_step(completion_result,
                                "qa_validation", "Skipped by user request")

            # Step 3: Documentation Generation
            doc_report = self._execute_step(
                completion_result,
                "documentation_generation",
                lambda: self.doc_agent.generate_documentation(task_id))
            completion_result.documentation_report = doc_report

            # Step 4: Archive Creation
            if not skip_archive:
                archive_path = self._execute_step(
                    completion_result,
                    "archive_creation",
                    lambda: self._create_task_archive(task_id))
                completion_result.archive_path = archive_path
            else:
                self._skip_step(completion_result,
                                "archive_creation", "Skipped by user request")

            # Step 5: Dashboard Update
            dashboard_updated = self._execute_step(
                completion_result,
                "dashboard_update",
                lambda: self._update_dashboard(
                    task_id,
                    completion_result))
            completion_result.dashboard_updated = dashboard_updated

            # Step 6: Status Update
            self._execute_step(
                completion_result,
                "status_update",
                lambda: self._update_task_status(
                    task_id,
                    completion_result))

            # Step 7: Generate Next Steps
            completion_result.next_steps = self._generate_completion_next_steps(
                completion_result)

            # Determine overall status
            completion_result.overall_status = self._determine_overall_status(
                completion_result)

            # Save completion results
            self._save_completion_results(completion_result)

            print(
                f"✅ Task completion workflow finished: {
                    completion_result.overall_status}")
            return completion_result

        except Exception as e:
            print(f"❌ Task completion workflow failed: {e}")
            completion_result.overall_status = "FAILED"
            completion_result.next_steps = [
                f"Fix workflow error: {str(e)}", "Re-run completion workflow"]
            self._save_completion_results(completion_result)
            return completion_result

    def _execute_step(
            self,
            completion_result: CompletionResult,
            step_name: str,
            step_function) -> Any:
        """Execute a single step in the completion workflow"""
        print(f"  📋 Executing step: {step_name}")

        step = CompletionStep(
            name=step_name,
            status="RUNNING",
            start_time=datetime.now().isoformat()
        )
        completion_result.steps.append(step)

        try:
            result = step_function()
            step.status = "COMPLETED"
            step.end_time = datetime.now().isoformat()

            # Record output files if result has file information
            if hasattr(result, '__dict__'):
                # Try to extract file paths from result object
                if hasattr(result, 'output_files'):
                    step.output_files = result.output_files

            print(f"    ✅ {step_name} completed successfully")
            return result

        except Exception as e:
            step.status = "FAILED"
            step.end_time = datetime.now().isoformat()
            step.error_message = str(e)
            print(f"    ❌ {step_name} failed: {e}")
            raise

    def _skip_step(
            self,
            completion_result: CompletionResult,
            step_name: str,
            reason: str):
        """Skip a step in the completion workflow"""
        print(f"  ⏭️ Skipping step: {step_name} ({reason})")

        step = CompletionStep(
            name=step_name,
            status="SKIPPED",
            start_time=datetime.now().isoformat(),
            end_time=datetime.now().isoformat(),
            error_message=reason
        )
        completion_result.steps.append(step)

    def _validate_prerequisites(self, task_id: str) -> bool:
        """Validate that task is ready for completion"""
        task_dir = self.outputs_dir / task_id

        # Check task directory exists
        if not task_dir.exists():
            raise ValueError(f"Task directory not found: {task_dir}")

        # Check required files exist
        required_files = ["task_declaration.json"]
        missing_files = []

        for required_file in required_files:
            if not (task_dir / required_file).exists():
                missing_files.append(required_file)

        if missing_files:
            raise ValueError(f"Missing required files: {missing_files}")

        # Check for agent outputs
        output_files = list(task_dir.glob("output_*.md"))
        if not output_files:
            raise ValueError("No agent output files found")

        print(f"    ✅ Prerequisites validated for {task_id}")
        return True

    def _create_task_archive(self, task_id: str) -> str:
        """Create compressed archive of task data"""
        task_dir = self.outputs_dir / task_id
        archive_path = self.archives_dir / f"{task_id}.tar.gz"

        # Use tar to create archive (cross-platform)
        try:
            import tarfile
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(task_dir, arcname=task_id)

            print(f"    📦 Archive created: {archive_path}")
            return str(archive_path)

        except Exception as e:
            # Fallback to shutil for simple zip
            import zipfile
            zip_path = self.archives_dir / f"{task_id}.zip"

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in task_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(task_dir.parent))
                        zipf.write(file_path, arcname)

            print(f"    📦 Archive created: {zip_path}")
            return str(zip_path)

    def _update_dashboard(
            self,
            task_id: str,
            completion_result: CompletionResult) -> bool:
        """Update dashboard with completion information"""
        try:
            # Update agent status
            agent_status_path = self.dashboard_dir / "agent_status.json"
            agent_status = {}

            if agent_status_path.exists():
                with open(agent_status_path) as f:
                    agent_status = json.load(f)

            # Add completion entry
            agent_status[task_id] = {
                "status": "COMPLETED",
                "completion_time": completion_result.completion_time,
                "qa_status": completion_result.qa_result.overall_status if completion_result.qa_result else "NOT_RUN",
                "documentation_generated": completion_result.documentation_report is not None,
                "archived": completion_result.archive_path is not None}

            with open(agent_status_path, 'w') as f:
                json.dump(agent_status, f, indent=2)

            # Update live execution log
            live_execution_path = self.dashboard_dir / "live_execution.json"
            live_data = {"tasks": {},
                         "last_updated": completion_result.completion_time}

            if live_execution_path.exists():
                with open(live_execution_path) as f:
                    live_data = json.load(f)

            live_data["tasks"][task_id] = {
                "status": "COMPLETED",
                "completion_time": completion_result.completion_time,
                "steps_completed": len([s for s in completion_result.steps if s.status == "COMPLETED"]),
                "total_steps": len(completion_result.steps)
            }
            live_data["last_updated"] = completion_result.completion_time

            with open(live_execution_path, 'w') as f:
                json.dump(live_data, f, indent=2)

            print(f"    📊 Dashboard updated for {task_id}")
            return True

        except Exception as e:
            print(f"    ⚠️ Dashboard update failed: {e}")
            return False

    def _update_task_status(
            self,
            task_id: str,
            completion_result: CompletionResult) -> bool:
        """Update task status to COMPLETED"""
        try:
            task_dir = self.outputs_dir / task_id
            status_path = task_dir / "status.json"

            status_data = {
                "status": "COMPLETED",
                "completion_time": completion_result.completion_time,
                "workflow_status": completion_result.overall_status
            }

            if status_path.exists():
                with open(status_path) as f:
                    existing_status = json.load(f)
                    status_data.update(existing_status)

            status_data["status"] = "COMPLETED"
            status_data["completion_time"] = completion_result.completion_time
            status_data["workflow_status"] = completion_result.overall_status

            with open(status_path, 'w') as f:
                json.dump(status_data, f, indent=2)

            print(f"    ✅ Task status updated to COMPLETED")
            return True

        except Exception as e:
            print(f"    ⚠️ Status update failed: {e}")
            return False

    def _generate_completion_next_steps(
            self, completion_result: CompletionResult) -> List[str]:
        """Generate next steps based on completion results"""
        next_steps = []

        # Based on overall status
        if completion_result.overall_status == "COMPLETED":
            next_steps.append(
                "✅ Task successfully completed and ready for integration")
            next_steps.append(
                "Notify dependent tasks that this task is finished")
            next_steps.append("Update project timeline and milestone tracking")
        elif completion_result.overall_status == "COMPLETED_WITH_WARNINGS":
            next_steps.append(
                "⚠️ Task completed with warnings - review recommendations")
            next_steps.append(
                "Consider addressing warning items before integration")
        else:
            next_steps.append(
                "❌ Fix issues identified during completion workflow")
            next_steps.append("Re-run completion workflow after fixes")

        # Based on QA results
        if completion_result.qa_result:
            if completion_result.qa_result.overall_status == "FAILED":
                next_steps.append(
                    "Address critical QA issues before proceeding")
            elif completion_result.qa_result.coverage_percentage < 80:
                next_steps.append(
                    "Consider improving test coverage for better quality")

        # Based on documentation
        if completion_result.documentation_report:
            next_steps.extend(
                completion_result.documentation_report.next_steps)

        # Archive follow-up
        if completion_result.archive_path:
            next_steps.append(
                f"Archive available at: {completion_result.archive_path}")

        return list(set(next_steps))  # Remove duplicates

    def _determine_overall_status(
            self, completion_result: CompletionResult) -> str:
        """Determine overall completion status"""
        failed_steps = [
            s for s in completion_result.steps if s.status == "FAILED"]
        if failed_steps:
            return "FAILED"

        # Check QA status
        if completion_result.qa_result:
            if completion_result.qa_result.overall_status == "FAILED":
                return "FAILED"
            elif completion_result.qa_result.overall_status == "PASSED_WITH_WARNINGS":
                return "COMPLETED_WITH_WARNINGS"

        return "COMPLETED"

    def _save_completion_results(
            self, completion_result: CompletionResult) -> None:
        """Save completion results to files"""
        # Save to task directory
        task_dir = self.outputs_dir / completion_result.task_id
        completion_path = task_dir / "completion_workflow.json"

        with open(completion_path, 'w') as f:
            json.dump(asdict(completion_result), f, indent=2, default=str)

        # Save to reports directory
        report_path = self.reports_dir / \
            f"{completion_result.task_id}_completion.json"
        with open(report_path, 'w') as f:
            json.dump(asdict(completion_result), f, indent=2, default=str)

        # Generate summary markdown
        self._generate_completion_summary(completion_result)

    def _generate_completion_summary(
            self, completion_result: CompletionResult) -> None:
        """Generate human-readable completion summary"""
        task_dir = self.outputs_dir / completion_result.task_id
        summary_path = task_dir / "completion_summary.md"

        status_icon = {
            "COMPLETED": "✅",
            "COMPLETED_WITH_WARNINGS": "⚠️",
            "FAILED": "❌",
            "RUNNING": "🔄"
        }.get(completion_result.overall_status, "❓")

        # Calculate timing
        total_duration = "Unknown"
        if completion_result.steps:
            first_step = min(completion_result.steps,
                             key=lambda s: s.start_time or "")
            last_step = max(completion_result.steps,
                            key=lambda s: s.end_time or "")

            if first_step.start_time and last_step.end_time:
                try:
                    start_dt = datetime.fromisoformat(first_step.start_time)
                    end_dt = datetime.fromisoformat(last_step.end_time)
                    duration = end_dt - start_dt
                    total_duration = f"{duration.total_seconds():.1f} seconds"
                except BaseException:
                    pass

        markdown_content = f"""# Completion Workflow Summary: {completion_result.task_id}

## Overall Status {status_icon}
**Result:** {completion_result.overall_status}
**Completed:** {completion_result.completion_time}
**Duration:** {total_duration}

## Workflow Steps

{self._format_workflow_steps(completion_result.steps)}

## Results Summary

### QA Validation
{self._format_qa_summary(completion_result.qa_result)}

### Documentation
{self._format_documentation_summary(completion_result.documentation_report)}

### Archive
{self._format_archive_summary(completion_result.archive_path)}

### Dashboard
**Updated:** {"✅ Yes" if completion_result.dashboard_updated else "❌ No"}

## Next Steps
{self._format_list(completion_result.next_steps)}

---
*Generated by Task Completion Orchestrator*
"""

        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

    def _format_workflow_steps(self, steps: List[CompletionStep]) -> str:
        """Format workflow steps for markdown"""
        if not steps:
            return "No steps recorded"

        formatted = []
        for step in steps:
            status_icon = {
                "COMPLETED": "✅",
                "FAILED": "❌",
                "SKIPPED": "⏭️",
                "RUNNING": "🔄",
                "PENDING": "⏳"
            }.get(step.status, "❓")

            duration = "Unknown"
            if step.start_time and step.end_time:
                try:
                    start_dt = datetime.fromisoformat(step.start_time)
                    end_dt = datetime.fromisoformat(step.end_time)
                    duration_sec = (end_dt - start_dt).total_seconds()
                    duration = f"{duration_sec:.1f}s"
                except BaseException:
                    pass

            step_line = f"- {status_icon} **{
                step.name.replace(
                    '_', ' ').title()}** ({duration})"

            if step.error_message:
                step_line += f"\n  - Error: {step.error_message}"

            if step.output_files:
                step_line += f"\n  - Files: {', '.join(step.output_files)}"

            formatted.append(step_line)

        return "\n".join(formatted)

    def _format_qa_summary(self, qa_result: Optional[QAResult]) -> str:
        """Format QA summary for markdown"""
        if not qa_result:
            return "- QA validation not performed"

        return f"""- **Status:** {qa_result.overall_status}
- **Tests:** {qa_result.tests_passed} passed, {qa_result.tests_failed} failed
- **Coverage:** {qa_result.coverage_percentage:.1f}%
- **Issues:** {len(qa_result.linting_issues)} linting, {len(qa_result.security_issues)} security
- **Recommendations:** {len(qa_result.recommendations)}"""

    def _format_documentation_summary(
            self, doc_report: Optional[DocumentationReport]) -> str:
        """Format documentation summary for markdown"""
        if not doc_report:
            return "- Documentation not generated"

        return f"""- **Generated:** ✅ Yes
- **Artifacts:** {len(doc_report.artifacts)} files documented
- **Report:** docs/completions/{doc_report.task_summary.task_id}.md
- **Next Steps:** {len(doc_report.next_steps)} identified"""

    def _format_archive_summary(self, archive_path: Optional[str]) -> str:
        """Format archive summary for markdown"""
        if not archive_path:
            return "- Archive not created"

        try:
            archive_size = Path(archive_path).stat().st_size
            size_str = self._format_file_size(archive_size)
            return f"- **Created:** ✅ Yes\n- **Location:** {archive_path}\n- **Size:** {size_str}"
        except BaseException:
            return f"- **Created:** ✅ Yes\n- **Location:** {archive_path}"

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _format_list(self, items: List[str]) -> str:
        """Format list items for markdown"""
        if not items:
            return "- None"
        return "\n".join([f"- {item}" for item in items])


def main():
    """CLI interface for task completion workflow"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Task Completion Orchestrator")
    parser.add_argument("task_id", help="Task ID to complete")
    parser.add_argument("--skip-qa", action="store_true",
                        help="Skip QA validation")
    parser.add_argument("--skip-archive", action="store_true",
                        help="Skip archive creation")
    parser.add_argument("--config", help="Path to QA configuration file")
    parser.add_argument("--verbose", "-v",
                        action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        orchestrator = TaskCompletionOrchestrator(config_path=args.config)
        completion_result = orchestrator.complete_task(
            args.task_id,
            skip_qa=args.skip_qa,
            skip_archive=args.skip_archive
        )

        if args.verbose:
            print(f"\nCompletion Workflow Summary:")
            print(f"Overall Status: {completion_result.overall_status}")
            print(
                f"Steps Completed: {len([s for s in completion_result.steps if s.status == 'COMPLETED'])}/{len(completion_result.steps)}")
            print(
                f"QA Status: {
                    completion_result.qa_result.overall_status if completion_result.qa_result else 'N/A'}")
            print(
                f"Documentation: {
                    '✅' if completion_result.documentation_report else '❌'}")
            print(f"Archive: {'✅' if completion_result.archive_path else '❌'}")
            print(
                f"Dashboard: {
                    '✅' if completion_result.dashboard_updated else '❌'}")

        # Exit with appropriate code
        if completion_result.overall_status in [
                "COMPLETED", "COMPLETED_WITH_WARNINGS"]:
            print(f"🎉 Task {args.task_id} completed successfully!")
            sys.exit(0)
        else:
            print(f"❌ Task {args.task_id} completion failed")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Task completion workflow failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
