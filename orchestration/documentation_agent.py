#!/usr/bin/env python3
"""
Documentation Agent for Phase 5

Automated documentation generation and task completion reporting.
Creates comprehensive reports for completed tasks with artifacts,
summaries, and next steps.
"""

import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class TaskArtifact:
    """Represents a task artifact"""
    name: str
    path: str
    type: str  # code, documentation, config, test, etc.
    size_bytes: int
    description: str


@dataclass
class TaskSummary:
    """Task completion summary"""
    task_id: str
    title: str
    description: str
    owner: str
    status: str
    start_date: Optional[str]
    completion_date: str
    duration_hours: Optional[float]


@dataclass
class QASummary:
    """QA results summary"""
    overall_status: str
    tests_passed: int
    tests_failed: int
    coverage_percentage: float
    critical_issues: int
    recommendations_count: int


@dataclass
class DocumentationReport:
    """Complete documentation report"""
    task_summary: TaskSummary
    artifacts: List[TaskArtifact]
    qa_summary: QASummary
    implementation_notes: List[str]
    technical_details: Dict[str, Any]
    next_steps: List[str]
    references: List[Dict[str, str]]
    generated_at: str
    version: str = "1.0.0"


class DocumentationAgent:
    """Automated documentation generation system"""

    def __init__(self):
        self.outputs_dir = Path("outputs")
        self.docs_dir = Path("docs/completions")
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.context_store = Path("context-store")
        self.tasks_dir = Path("tasks")

    def generate_documentation(self, task_id: str) -> DocumentationReport:
        """Generate comprehensive documentation for a completed task"""
        print(f"📝 Generating documentation for task {task_id}")

        task_dir = self.outputs_dir / task_id
        if not task_dir.exists():
            raise ValueError(f"Task directory not found: {task_dir}")

        # Load task metadata
        task_summary = self._load_task_summary(task_id)

        # Collect artifacts
        artifacts = self._collect_artifacts(task_id)

        # Load QA summary
        qa_summary = self._load_qa_summary(task_id)

        # Generate implementation notes
        implementation_notes = self._generate_implementation_notes(task_id)

        # Extract technical details
        technical_details = self._extract_technical_details(task_id)

        # Generate next steps
        next_steps = self._generate_next_steps(task_id, qa_summary)

        # Collect references
        references = self._collect_references(task_id)

        # Create documentation report
        doc_report = DocumentationReport(
            task_summary=task_summary,
            artifacts=artifacts,
            qa_summary=qa_summary,
            implementation_notes=implementation_notes,
            technical_details=technical_details,
            next_steps=next_steps,
            references=references,
            generated_at=datetime.now().isoformat()
        )

        # Save documentation
        self._save_documentation(doc_report)

        print(f"✅ Documentation generated for {task_id}")
        return doc_report

    def _load_task_summary(self, task_id: str) -> TaskSummary:
        """Load task summary from declaration and metadata"""
        task_dir = self.outputs_dir / task_id

        # Load task declaration
        declaration_path = task_dir / "task_declaration.json"
        task_data = {}
        if declaration_path.exists():
            with open(declaration_path) as f:
                task_data = json.load(f)

        # Load status information
        status_path = task_dir / "status.json"
        status_data = {}
        if status_path.exists():
            with open(status_path) as f:
                status_data = json.load(f)

        # Calculate duration if possible
        duration_hours = None
        start_date = status_data.get("start_date")
        completion_date = datetime.now().isoformat()

        if start_date:
            try:
                start_dt = datetime.fromisoformat(
                    start_date.replace('Z', '+00:00'))
                completion_dt = datetime.now()
                duration = completion_dt - start_dt
                duration_hours = duration.total_seconds() / 3600
            except BaseException:
                pass

        return TaskSummary(
            task_id=task_id,
            title=task_data.get("title", f"Task {task_id}"),
            description=task_data.get(
                "description", "No description available"),
            owner=task_data.get("owner", "unknown"),
            status=status_data.get("status", "COMPLETED"),
            start_date=start_date,
            completion_date=completion_date,
            duration_hours=duration_hours
        )

    def _collect_artifacts(self, task_id: str) -> List[TaskArtifact]:
        """Collect all artifacts generated for the task"""
        task_dir = self.outputs_dir / task_id
        artifacts = []

        # Define artifact types and patterns
        artifact_patterns = {
            "code": [
                "code/**/*.py",
                "code/**/*.ts",
                "code/**/*.js",
                "code/**/*.tsx",
                "code/**/*.jsx"],
            "documentation": [
                "*.md",
                "docs/**/*.md"],
            "configuration": [
                "*.yaml",
                "*.yml",
                "*.json",
                "*.toml",
                "config/**/*"],
            "tests": [
                "test/**/*",
                "tests/**/*",
                "**/*test*",
                "**/*spec*"],
            "output": [
                "output_*.md",
                "prompt_*.md"],
            "reports": [
                "qa_*.json",
                "qa_*.md",
                "status.json"]}

        for artifact_type, patterns in artifact_patterns.items():
            for pattern in patterns:
                for file_path in task_dir.glob(pattern):
                    if file_path.is_file():
                        try:
                            stat = file_path.stat()
                            # Use safe path calculation
                            try:
                                relative_path = str(
                                    file_path.relative_to(task_dir))
                            except ValueError:
                                # If relative_to fails, use name only
                                relative_path = file_path.name

                            artifacts.append(
                                TaskArtifact(
                                    name=file_path.name,
                                    path=relative_path,
                                    type=artifact_type,
                                    size_bytes=stat.st_size,
                                    description=self._generate_artifact_description(
                                        file_path,
                                        artifact_type)))
                        except Exception as e:
                            print(
                                f"Warning: Could not process artifact {file_path}: {e}")

        return sorted(artifacts, key=lambda x: (x.type, x.name))

    def _load_qa_summary(self, task_id: str) -> QASummary:
        """Load QA summary from QA report"""
        task_dir = self.outputs_dir / task_id
        qa_report_path = task_dir / "qa_report.json"

        if not qa_report_path.exists():
            # Return default QA summary if no QA report exists
            return QASummary(
                overall_status="NOT_RUN",
                tests_passed=0,
                tests_failed=0,
                coverage_percentage=0.0,
                critical_issues=0,
                recommendations_count=0
            )

        try:
            with open(qa_report_path) as f:
                qa_data = json.load(f)

            # Count critical issues
            critical_issues = 0
            for issue_list in [qa_data.get("linting_issues", []),
                               qa_data.get("security_issues", []),
                               qa_data.get("type_check_issues", [])]:
                critical_issues += len([issue for issue in issue_list
                                        if issue.get("severity") in ["error", "critical"]])

            return QASummary(
                overall_status=qa_data.get("overall_status", "UNKNOWN"),
                tests_passed=qa_data.get("tests_passed", 0),
                tests_failed=qa_data.get("tests_failed", 0),
                coverage_percentage=qa_data.get("coverage_percentage", 0.0),
                critical_issues=critical_issues,
                recommendations_count=len(qa_data.get("recommendations", []))
            )

        except Exception as e:
            print(f"Warning: Could not load QA report: {e}")
            return QASummary(
                overall_status="ERROR",
                tests_passed=0,
                tests_failed=0,
                coverage_percentage=0.0,
                critical_issues=1,
                recommendations_count=1
            )

    def _generate_implementation_notes(self, task_id: str) -> List[str]:
        """Generate implementation notes from agent outputs"""
        task_dir = self.outputs_dir / task_id
        notes = []

        # Analyze agent outputs
        output_files = list(task_dir.glob("output_*.md"))
        for output_file in output_files:
            try:
                with open(output_file) as f:
                    content = f.read()

                # Extract key implementation points
                if "implemented" in content.lower():
                    notes.append(
                        f"Implementation details documented in {output_file.name}")

                if "service" in content.lower():
                    notes.append("Service layer implementation completed")

                if "database" in content.lower() or "supabase" in content.lower():
                    notes.append("Database integration implemented")

                if "api" in content.lower():
                    notes.append("API endpoints implemented")

            except Exception as e:
                print(f"Warning: Could not analyze {output_file}: {e}")

        # Analyze code artifacts
        code_dir = task_dir / "code"
        if code_dir.exists():
            code_files = list(code_dir.glob("**/*.ts")) + \
                list(code_dir.glob("**/*.py"))
            if code_files:
                notes.append(f"Generated {len(code_files)} code files")

                # Analyze file types
                service_files = [
                    f for f in code_files if "service" in f.name.lower()]
                if service_files:
                    notes.append(
                        f"Service layer: {', '.join([f.stem for f in service_files])}")

                model_files = [
                    f for f in code_files if "model" in f.name.lower()]
                if model_files:
                    notes.append(
                        f"Data models: {', '.join([f.stem for f in model_files])}")

        if not notes:
            notes.append("Implementation completed with standard approach")

        return notes

    def _extract_technical_details(self, task_id: str) -> Dict[str, Any]:
        """Extract technical implementation details"""
        task_dir = self.outputs_dir / task_id
        details = {
            "technologies": [],
            "patterns": [],
            "dependencies": [],
            "metrics": {}
        }

        # Analyze code for technologies and patterns
        code_dir = task_dir / "code"
        if code_dir.exists():
            # Detect technologies
            if list(code_dir.glob("**/*.ts")):
                details["technologies"].append("TypeScript")
            if list(code_dir.glob("**/*.py")):
                details["technologies"].append("Python")
            if list(code_dir.glob("**/*.js")):
                details["technologies"].append("JavaScript")

            # Detect patterns
            for code_file in code_dir.glob("**/*.ts"):
                try:
                    with open(code_file) as f:
                        content = f.read()

                    if "export class" in content and "Service" in content:
                        details["patterns"].append("Service Layer Pattern")
                    if "interface" in content:
                        details["patterns"].append("Interface Segregation")
                    if "supabase" in content.lower():
                        details["dependencies"].append("Supabase")

                except Exception:
                    continue

        # Calculate metrics
        code_files = list(code_dir.glob("**/*")) if code_dir.exists() else []
        details["metrics"] = {
            "total_files": len([f for f in code_files if f.is_file()]),
            "lines_of_code": self._count_lines_of_code(code_dir) if code_dir.exists() else 0,
            "complexity_estimate": "Low" if len(code_files) < 5 else "Medium"
        }

        return details

    def _generate_next_steps(
            self,
            task_id: str,
            qa_summary: QASummary) -> List[str]:
        """Generate next steps based on task completion and QA results"""
        next_steps = []

        # Based on QA status
        if qa_summary.overall_status == "PASSED":
            next_steps.append("✅ Task ready for integration")
            next_steps.append(
                "Consider code review if required by team process")
        elif qa_summary.overall_status == "PASSED_WITH_WARNINGS":
            next_steps.append("⚠️ Address warning items if time permits")
            next_steps.append(
                "Task can proceed to integration with noted warnings")
        elif qa_summary.overall_status == "FAILED":
            next_steps.append("❌ Fix critical issues identified in QA report")
            next_steps.append("Re-run QA validation after fixes")
        else:
            next_steps.append("Run QA validation if not yet completed")

        # Based on coverage
        if qa_summary.coverage_percentage < 80:
            next_steps.append("Consider adding more comprehensive tests")

        # Generic next steps
        next_steps.append(
            "Update project documentation if this affects architecture")
        next_steps.append("Notify dependent tasks that this task is complete")

        return next_steps

    def _collect_references(self, task_id: str) -> List[Dict[str, str]]:
        """Collect references and links related to the task"""
        references = []

        # Task declaration reference
        references.append({
            "type": "task_declaration",
            "title": f"Task Declaration - {task_id}",
            "url": f"outputs/{task_id}/task_declaration.json"
        })

        # QA report reference
        qa_report_path = self.outputs_dir / task_id / "qa_report.json"
        if qa_report_path.exists():
            references.append({
                "type": "qa_report",
                "title": f"QA Report - {task_id}",
                "url": f"outputs/{task_id}/qa_report.json"
            })

        # Agent outputs
        output_files = list((self.outputs_dir / task_id).glob("output_*.md"))
        for output_file in output_files:
            agent_name = output_file.stem.replace("output_", "")
            try:
                # Try to get relative path from current working directory
                relative_url = str(output_file.relative_to(Path.cwd()))
            except ValueError:
                # If relative_to fails, use relative path from outputs dir
                relative_url = f"outputs/{task_id}/{output_file.name}"

            references.append({
                "type": "agent_output",
                "title": f"{agent_name.title()} Agent Output",
                "url": relative_url
            })

        # Add GitHub PR references for this task
        pr_links = self._collect_github_pr_links(task_id)
        references.extend(pr_links)

        return references

    def _collect_github_pr_links(self, task_id: str) -> List[Dict[str, str]]:
        """Collect GitHub PR links related to this task"""
        pr_links = []

        try:
            # Import GitHub tool to fetch PR information
            from tools.github_tool import GitHubTool
            github_tool = GitHubTool()

            # Check if GitHub token is available
            import os
            if not os.getenv("GITHUB_TOKEN"):
                print(f"Info: GITHUB_TOKEN not set, using manual PR link fallback")
                raise Exception("GitHub token not available")

            # List pull requests and filter for those related to this task
            pr_response = github_tool._run("list pull requests")
            pr_data = json.loads(pr_response)

            if pr_data.get("success") and pr_data.get("data"):
                for pr in pr_data["data"]:
                    # Check if PR is related to this task (by title, body, or
                    # branch name)
                    pr_title = pr.get("title", "").lower()
                    pr_body = pr.get("body", "").lower()
                    pr_branch = pr.get("head", {}).get("ref", "").lower()

                    task_id_lower = task_id.lower()

                    # Match PR if task ID appears in title, body, or branch
                    if (task_id_lower in pr_title or
                        task_id_lower in pr_body or
                        task_id_lower in pr_branch or
                        # Also check for common patterns like "be-07" matching
                        # "BE-07"
                        task_id_lower.replace("-", "") in pr_title.replace("-", "") or
                        task_id_lower.replace("-", "") in pr_body.replace("-", "") or
                            task_id_lower.replace("-", "") in pr_branch.replace("-", "")):

                        pr_links.append({
                            "type": "pull_request",
                            "title": f"PR #{pr.get('number')}: {pr.get('title')}",
                            "url": pr.get("html_url", "#"),
                            "status": pr.get("state", "unknown")
                        })

            # If no PRs found, add manual fallback
            if not pr_links:
                pr_links.append({
                    "type": "pull_request",
                    "title": f"Pull Request for {task_id} (manual entry needed)",
                    "url": f"https://github.com/artesanato-shop/artesanato-ecommerce/pulls?q={task_id}",
                    "status": "pending"
                })

        except Exception as e:
            print(f"Warning: Could not fetch GitHub PR links: {e}")
            # Add a placeholder for manual PR entry
            pr_links.append({
                "type": "pull_request",
                "title": f"Pull Request for {task_id} (manual entry needed)",
                "url": f"https://github.com/artesanato-shop/artesanato-ecommerce/pulls?q={task_id}",
                "status": "pending"
            })

        return pr_links

    def _save_documentation(self, doc_report: DocumentationReport) -> None:
        """Save documentation report in multiple formats"""
        task_id = doc_report.task_summary.task_id

        # Save JSON report
        json_path = self.docs_dir / f"{task_id}.json"
        with open(json_path, 'w') as f:
            json.dump(asdict(doc_report), f, indent=2)

        # Save Markdown report
        md_path = self.docs_dir / f"{task_id}.md"
        self._generate_markdown_report(doc_report, md_path)

        # Save to task directory as well
        task_dir = self.outputs_dir / task_id
        task_md_path = task_dir / "completion_report.md"
        self._generate_markdown_report(doc_report, task_md_path)

        print(f"📄 Documentation saved to {md_path} and {task_md_path}")

    def _generate_markdown_report(
            self,
            doc_report: DocumentationReport,
            output_path: Path) -> None:
        """Generate comprehensive Markdown documentation report"""
        task = doc_report.task_summary
        qa = doc_report.qa_summary

        # Status icons
        status_icons = {
            "PASSED": "✅",
            "PASSED_WITH_WARNINGS": "⚠️",
            "FAILED": "❌",
            "NOT_RUN": "⏳",
            "ERROR": "💥"
        }

        qa_icon = status_icons.get(qa.overall_status, "❓")

        # Duration formatting
        duration_str = "Unknown"
        if task.duration_hours is not None:
            if task.duration_hours < 1:
                duration_str = f"{task.duration_hours * 60:.0f} minutes"
            else:
                duration_str = f"{task.duration_hours:.1f} hours"

        markdown_content = f"""# Task Completion Report: {task.task_id}

## Summary
**Title:** {task.title}
**Owner:** {task.owner}
**Status:** {task.status}
**Completed:** {task.completion_date[:10]}
**Duration:** {duration_str}

{task.description}

## QA Validation {qa_icon}
**Overall Status:** {qa.overall_status}
**Test Results:** {qa.tests_passed} passed, {qa.tests_failed} failed
**Coverage:** {qa.coverage_percentage:.1f}%
**Critical Issues:** {qa.critical_issues}
**Recommendations:** {qa.recommendations_count}

## Implementation Summary

### Key Achievements
{self._format_list(doc_report.implementation_notes)}

### Technical Details
**Technologies Used:** {', '.join(doc_report.technical_details.get('technologies', ['None']))}
**Patterns Applied:** {', '.join(doc_report.technical_details.get('patterns', ['Standard patterns']))}
**Dependencies:** {', '.join(doc_report.technical_details.get('dependencies', ['None']))}

### Metrics
{self._format_metrics(doc_report.technical_details.get('metrics', {}))}

## Artifacts Generated

{self._format_artifacts(doc_report.artifacts)}

## Next Steps
{self._format_list(doc_report.next_steps)}

## References
{self._format_references(doc_report.references)}

---
**Documentation Generated:** {doc_report.generated_at}
**Documentation Version:** {doc_report.version}
*Generated by Documentation Agent*
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

    def _format_list(self, items: List[str]) -> str:
        """Format list items for markdown"""
        if not items:
            return "- None"
        return "\n".join([f"- {item}" for item in items])

    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for markdown"""
        if not metrics:
            return "- No metrics available"

        formatted = []
        for key, value in metrics.items():
            formatted.append(f"- **{key.replace('_', ' ').title()}:** {value}")

        return "\n".join(formatted)

    def _format_artifacts(self, artifacts: List[TaskArtifact]) -> str:
        """Format artifacts list for markdown"""
        if not artifacts:
            return "No artifacts generated."

        # Group by type
        by_type = {}
        for artifact in artifacts:
            if artifact.type not in by_type:
                by_type[artifact.type] = []
            by_type[artifact.type].append(artifact)

        formatted = []
        for artifact_type, artifact_list in sorted(by_type.items()):
            formatted.append(f"\n### {artifact_type.title()}")
            for artifact in artifact_list:
                size_str = self._format_file_size(artifact.size_bytes)
                formatted.append(
                    f"- **{artifact.name}** ({size_str}) - {artifact.description}")

        return "\n".join(formatted)

    def _format_references(self, references: List[Dict[str, str]]) -> str:
        """Format references for markdown"""
        if not references:
            return "- No references available"

        formatted = []
        for ref in references:
            title = ref.get("title", "Unknown")
            url = ref.get("url", "#")
            formatted.append(f"- [{title}]({url})")

        return "\n".join(formatted)

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _generate_artifact_description(
            self,
            file_path: Path,
            artifact_type: str) -> str:
        """Generate description for an artifact"""
        descriptions = {
            "code": f"Source code file implementing {
                file_path.stem} functionality",
            "documentation": f"Documentation for {
                file_path.stem}",
            "configuration": f"Configuration file for {
                file_path.stem}",
            "tests": f"Test file for {
                file_path.stem}",
            "output": f"Agent output containing implementation details",
            "reports": f"Report file containing {
                file_path.stem} results"}

        base_desc = descriptions.get(artifact_type, f"{artifact_type} file")

        # Add specific details based on file extension
        suffix = file_path.suffix.lower()
        if suffix == ".ts":
            base_desc += " (TypeScript)"
        elif suffix == ".py":
            base_desc += " (Python)"
        elif suffix == ".json":
            base_desc += " (JSON data)"
        elif suffix == ".md":
            base_desc += " (Markdown)"

        return base_desc

    def _count_lines_of_code(self, code_dir: Path) -> int:
        """Count total lines of code in the directory"""
        total_lines = 0
        code_extensions = {".py", ".ts", ".js", ".tsx", ".jsx"}

        for file_path in code_dir.glob("**/*"):
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len([line for line in f if line.strip()])
                        total_lines += lines
                except Exception:
                    continue

        return total_lines


def main():
    """CLI interface for documentation generation"""
    import argparse

    parser = argparse.ArgumentParser(description="Documentation Agent")
    parser.add_argument(
        "task_id", help="Task ID to generate documentation for")
    parser.add_argument("--verbose", "-v",
                        action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        doc_agent = DocumentationAgent()
        doc_report = doc_agent.generate_documentation(args.task_id)

        if args.verbose:
            print(f"\nDocumentation Report Summary:")
            print(f"Task: {doc_report.task_summary.title}")
            print(f"Artifacts: {len(doc_report.artifacts)}")
            print(f"QA Status: {doc_report.qa_summary.overall_status}")
            print(f"Next Steps: {len(doc_report.next_steps)}")

        print(f"✅ Documentation completed for {args.task_id}")

    except Exception as e:
        print(f"❌ Documentation generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import sys
    main()
