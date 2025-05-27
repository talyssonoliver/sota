#!/usr/bin/env python3
"""
Step 4.4 — Register Agent Output

Unified system for registering agent outputs with proper metadata tracking,
status updates, and integration with downstream agents (QA, Documentation).

This script provides a CLI interface for:
- Registering agent outputs to standardized locations
- Extracting and organizing code artifacts
- Updating task status and metadata
- Preparing outputs for downstream agent consumption

Example Usage:
    python orchestration/register_output.py BE-07 backend outputs/BE-07/output_backend.md
    python orchestration/register_output.py BE-07 qa outputs/BE-07/qa_report.json --type json
    python orchestration/register_output.py --task BE-07 --agent backend --extract-code
"""

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from tools.memory_engine import MemoryEngine

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from orchestration.scalable_storage import ScalableTaskStorage
    from orchestration.task_lifecycle import TaskLifecycleManager
    SCALABLE_STORAGE_AVAILABLE = True
except ImportError:
    SCALABLE_STORAGE_AVAILABLE = False


@dataclass
class AgentOutputRegistration:
    """Metadata for agent output registration."""
    task_id: str
    agent_id: str
    output_path: str
    registration_time: str
    output_type: str  # 'markdown', 'json', 'code', 'mixed'
    file_size: int
    extracted_artifacts: List[str]
    status: str  # 'registered', 'processed', 'error'
    metadata: Dict[str, Any]


class AgentOutputRegistry:
    """Central registry for managing agent outputs and their metadata."""

    def __init__(self, base_outputs_dir: str = "outputs",
                 enable_scalable_storage: bool = False):
        self.base_outputs_dir = Path(base_outputs_dir)
        self.base_outputs_dir.mkdir(exist_ok=True)

        # Initialize scalable storage if available
        self.enable_scalable_storage = enable_scalable_storage and SCALABLE_STORAGE_AVAILABLE
        if self.enable_scalable_storage:
            self.scalable_storage = ScalableTaskStorage(
                str(self.base_outputs_dir))
            self.lifecycle_manager = TaskLifecycleManager(
                str(self.base_outputs_dir))
        else:
            self.scalable_storage = None
            self.lifecycle_manager = None

    def get_task_directory(self, task_id: str) -> Path:
        """Get or create the task output directory using scalable storage if available."""
        if self.enable_scalable_storage and self.scalable_storage:
            return self.scalable_storage.get_task_directory(task_id)
        else:
            # Fallback to original flat structure
            task_dir = self.base_outputs_dir / task_id
            task_dir.mkdir(exist_ok=True)
            return task_dir

    def register_output(
        self,
        task_id: str,
        agent_id: str,
        source_path: str,
        output_type: str = "markdown",
        extract_code: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentOutputRegistration:
        """
        Register an agent output file with proper organization and metadata.

        Args:
            task_id: Task identifier (e.g., 'BE-07')
            agent_id: Agent identifier (e.g., 'backend', 'qa', 'doc')
            source_path: Path to the agent output file
            output_type: Type of output ('markdown', 'json', 'code', 'mixed')
            extract_code: Whether to extract code blocks from the output
            metadata: Additional metadata to store

        Returns:
            AgentOutputRegistration with registration details
        """
        task_dir = self.get_task_directory(task_id)
        source_path = Path(source_path)

        if not source_path.exists():
            raise FileNotFoundError(
                f"Source output file not found: {source_path}")

        # Determine target filename
        target_filename = f"output_{agent_id}.md"
        if output_type == "json":
            target_filename = f"{agent_id}_report.json"
        elif output_type == "code":
            target_filename = f"code_{agent_id}.md"

        target_path = task_dir / target_filename

        # Copy source to target location
        shutil.copy2(source_path, target_path)

        # Extract code artifacts if requested
        extracted_artifacts = []
        if extract_code and output_type in ["markdown", "mixed"]:
            extracted_artifacts = self._extract_code_artifacts(
                target_path, task_dir)

        # Create registration metadata
        registration = AgentOutputRegistration(
            task_id=task_id,
            agent_id=agent_id,
            output_path=str(target_path),
            registration_time=datetime.now().isoformat(),
            output_type=output_type,
            file_size=target_path.stat().st_size,
            extracted_artifacts=extracted_artifacts,
            status="registered",
            metadata=metadata or {}
        )
        # Update task status file
        self._update_task_status(task_id, agent_id, registration)

        # Save registration metadata
        self._save_registration_metadata(task_dir, registration)

        # Apply lifecycle management if enabled
        if self.enable_scalable_storage and self.lifecycle_manager:
            try:
                self.lifecycle_manager.track_task_completion(task_id, agent_id)
                # Check if automatic cleanup should be triggered
                if self.lifecycle_manager.should_trigger_cleanup():
                    self.lifecycle_manager.cleanup_old_tasks()
            except Exception as e:
                # Log warning but don't fail registration
                print(
                    f"Warning: Lifecycle management failed for {task_id}: {e}")

        return registration

    def _extract_code_artifacts(
            self,
            output_path: Path,
            task_dir: Path) -> List[str]:
        """Extract code blocks from markdown output into separate files."""
        extracted_files = []

        try:
            content = output_path.read_text(encoding='utf-8')

            # Create code directory
            code_dir = task_dir / "code"
            code_dir.mkdir(exist_ok=True)
            # Regex pattern for code blocks with optional filename (supports //
            # and -- comments)
            code_block_pattern = r'```(\w+)?\s*(?:(?:\/\/|--)\s*filename:\s*([^\n]+))?\n(.*?)\n```'

            matches = re.finditer(code_block_pattern, content, re.DOTALL)

            for i, match in enumerate(matches):
                language = match.group(1) or 'txt'
                filename = match.group(2)
                code_content = match.group(3)
                # Determine filename
                if filename:
                    # Clean up the filename
                    filename = filename.strip()
                    if filename.startswith('./'):
                        filename = filename[2:]
                    # Replace directory separators with underscores to flatten
                    # structure
                    filename = filename.replace('/', '_').replace('\\', '_')
                else:
                    # Generate filename based on language and index
                    extensions = {
                        'javascript': '.js',
                        'typescript': '.ts',
                        'python': '.py',
                        'sql': '.sql',
                        'yaml': '.yaml',
                        'json': '.json'
                    }
                    ext = extensions.get(language.lower(), '.txt')
                    filename = f"extracted_code_{i + 1}{ext}"

                # Write code to file (ensure we don't create subdirectories)
                code_file_path = code_dir / filename
                code_file_path.write_text(code_content, encoding='utf-8')
                extracted_files.append(str(code_file_path))

        except Exception as e:
            print(f"Warning: Error extracting code artifacts: {e}")

        return extracted_files

    def _update_task_status(
            self,
            task_id: str,
            agent_id: str,
            registration: AgentOutputRegistration):
        """Update the task status JSON file with agent completion info."""
        task_dir = self.get_task_directory(task_id)
        status_file = task_dir / "status.json"

        # Load existing status or create new
        status_data = {}
        if status_file.exists():
            try:
                status_data = json.loads(
                    status_file.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, Exception):
                status_data = {}

        # Initialize structure if needed
        if "agent_outputs" not in status_data:
            status_data["agent_outputs"] = {}

        # Update agent status
        status_data["agent_outputs"][agent_id] = {
            "status": "completed",
            "completion_time": registration.registration_time,
            "output_file": os.path.basename(registration.output_path),
            "file_size": registration.file_size,
            "extracted_artifacts": len(registration.extracted_artifacts),
            "metadata": registration.metadata
        }

        # Update overall task status
        status_data["last_updated"] = datetime.now().isoformat()
        status_data["task_id"] = task_id

        # Save updated status
        status_file.write_text(json.dumps(
            status_data, indent=2), encoding='utf-8')

    def _save_registration_metadata(
            self,
            task_dir: Path,
            registration: AgentOutputRegistration):
        """Save detailed registration metadata."""
        metadata_file = task_dir / f"registration_{registration.agent_id}.json"
        metadata_file.write_text(
            json.dumps(asdict(registration), indent=2),
            encoding='utf-8'
        )

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the current status of a task and its agent outputs."""
        task_dir = self.get_task_directory(task_id)
        status_file = task_dir / "status.json"

        if not status_file.exists():
            return {
                "task_id": task_id,
                "status": "no_outputs",
                "agent_outputs": {}
            }

        try:
            return json.loads(status_file.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, Exception) as e:
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e),
                "agent_outputs": {}
            }

    def list_task_outputs(self, task_id: str) -> List[str]:
        """List all output files for a task."""
        task_dir = self.get_task_directory(task_id)

        if not task_dir.exists():
            return []

        output_files = []
        for file_path in task_dir.iterdir():
            if file_path.is_file() and file_path.name.startswith('output_'):
                output_files.append(str(file_path))

        return sorted(output_files)

    def prepare_qa_input(self, task_id: str) -> Dict[str, Any]:
        """Prepare input data for QA agent based on registered outputs."""
        task_dir = self.get_task_directory(task_id)
        status = self.get_task_status(task_id)

        qa_input = {
            "task_id": task_id,
            "primary_outputs": [],
            "code_artifacts": [],
            "metadata": status.get("agent_outputs", {})
        }

        # Collect primary outputs
        for output_file in self.list_task_outputs(task_id):
            qa_input["primary_outputs"].append({
                "file": output_file,
                # Preview
                "content": Path(output_file).read_text(encoding='utf-8')[:1000] + "..."
            })

        # Collect code artifacts
        code_dir = task_dir / "code"
        if code_dir.exists():
            for code_file in code_dir.iterdir():
                if code_file.is_file():
                    qa_input["code_artifacts"].append({
                        "file": str(code_file),
                        "language": code_file.suffix[1:] if code_file.suffix else "txt",
                        "content": code_file.read_text(encoding='utf-8')
                    })
        return qa_input

    def get_scalability_metrics(self) -> Dict[str, Any]:
        """Get current scalability metrics and performance data."""
        metrics = {
            "storage_backend": "scalable" if self.enable_scalable_storage else "flat",
            "lifecycle_management": self.lifecycle_manager is not None,
            "total_task_directories": 0,
            "storage_efficiency": {},
            "performance_metrics": {}}

        if self.enable_scalable_storage and self.scalable_storage:
            # Get storage metrics
            storage_metrics = self.scalable_storage.get_metrics()
            metrics.update({
                "total_task_directories": storage_metrics.total_tasks,
                "avg_lookup_time_ms": storage_metrics.avg_lookup_time_ms,
                "cache_hit_rate": storage_metrics.cache_hit_rate,
                "directory_depth": storage_metrics.directory_depth,
                "files_per_directory": storage_metrics.files_per_directory
            })

        if self.lifecycle_manager:
            # Get lifecycle metrics
            lifecycle_stats = self.lifecycle_manager.get_storage_statistics()
            metrics["lifecycle_stats"] = lifecycle_stats

        return metrics

    def migrate_to_scalable_storage(
            self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Migrate existing flat directory structure to scalable hierarchy.

        Args:
            dry_run: If True, only report what would be migrated without making changes

        Returns:
            Migration report with statistics and results
        """
        if not self.enable_scalable_storage:
            return {"error": "Scalable storage not enabled"}

        migration_report = {
            "dry_run": dry_run,
            "tasks_to_migrate": [],
            "migration_summary": {},
            "errors": []
        }

        try:
            # Find all existing task directories in flat structure
            flat_dirs = [d for d in self.base_outputs_dir.iterdir()
                         if d.is_dir() and not d.name.startswith('.')]

            for task_dir in flat_dirs:
                task_id = task_dir.name

                # Skip if already in hierarchical structure
                if len(task_id.split('-')) >= 2:  # Assume task IDs like "BE-07"
                    new_path = self.scalable_storage.get_task_directory(
                        task_id)

                    if task_dir != new_path:
                        migration_info = {
                            "task_id": task_id,
                            "current_path": str(task_dir),
                            "new_path": str(new_path),
                            "file_count": len(
                                list(
                                    task_dir.rglob("*"))),
                            "total_size": sum(
                                f.stat().st_size for f in task_dir.rglob("*") if f.is_file())}
                        migration_report["tasks_to_migrate"].append(
                            migration_info)

                        if not dry_run:
                            # Perform actual migration
                            new_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(task_dir), str(new_path))

        except Exception as e:
            migration_report["errors"].append(f"Migration error: {e}")

        migration_report["migration_summary"] = {
            "total_tasks": len(
                migration_report["tasks_to_migrate"]), "total_files": sum(
                t["file_count"] for t in migration_report["tasks_to_migrate"]), "total_size_mb": sum(
                t["total_size"] for t in migration_report["tasks_to_migrate"]) / (
                    1024 * 1024)}

        return migration_report


def main():
    """CLI interface for agent output registration."""
    parser = argparse.ArgumentParser(
        description="Register agent outputs with metadata tracking and artifact extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Register backend agent output
  %(prog)s BE-07 backend outputs/BE-07/output_backend.md

  # Register QA report with JSON type
  %(prog)s BE-07 qa outputs/BE-07/qa_report.json --type json

  # Register output and extract code artifacts
  %(prog)s BE-07 backend outputs/BE-07/output_backend.md --extract-code

  # Check task status
  %(prog)s --status BE-07

  # Prepare QA input
  %(prog)s --prepare-qa BE-07
        """)

    # Main command arguments
    parser.add_argument("task_id", nargs="?", help="Task ID (e.g., BE-07)")
    parser.add_argument("agent_id", nargs="?",
                        help="Agent ID (e.g., backend, qa, doc)")
    parser.add_argument("source_path", nargs="?",
                        help="Path to agent output file")

    # Options
    parser.add_argument("--type", default="markdown",
                        choices=["markdown", "json", "code", "mixed"],
                        help="Type of output content")
    parser.add_argument("--extract-code", action="store_true",
                        help="Extract code blocks from markdown output")
    parser.add_argument(
        "--metadata", help="Additional metadata as JSON string")
    # Status and utility commands
    parser.add_argument("--status", metavar="TASK_ID",
                        help="Show status of a task")
    parser.add_argument("--list-outputs", metavar="TASK_ID",
                        help="List all outputs for a task")
    parser.add_argument("--prepare-qa", metavar="TASK_ID",
                        help="Prepare QA input for a task")
    parser.add_argument("--scalability-metrics", action="store_true",
                        help="Show scalability metrics and performance data")
    parser.add_argument("--migrate-storage", action="store_true",
                        help="Migrate to scalable storage (dry run)")
    parser.add_argument("--migrate-storage-execute", action="store_true",
                        help="Migrate to scalable storage (execute)")
    parser.add_argument(
        "--enable-scalable-storage",
        action="store_true",
        default=True,
        help="Enable scalable hierarchical storage (default: True)")
    parser.add_argument("--disable-scalable-storage", action="store_true",
                        help="Disable scalable storage, use flat structure")

    args = parser.parse_args()

    # Determine scalable storage setting
    enable_scalable = not args.disable_scalable_storage

    # Initialize registry with appropriate storage configuration
    registry = AgentOutputRegistry(enable_scalable_storage=enable_scalable)

    # Handle status and utility commands
    if args.status:
        status = registry.get_task_status(args.status)
        print("📊 Task Status:")
        print(json.dumps(status, indent=2))
        return

    if args.list_outputs:
        outputs = registry.list_task_outputs(args.list_outputs)
        print(f"📁 Outputs for {args.list_outputs}:")
        for output in outputs:
            print(f"  📄 {output}")
        return

    if args.prepare_qa:
        qa_input = registry.prepare_qa_input(args.prepare_qa)
        print(f"🔍 QA Input for {args.prepare_qa}:")
        print(json.dumps(qa_input, indent=2))
        return

    # Handle scalability commands
    if args.scalability_metrics:
        metrics = registry.get_scalability_metrics()
        print("📈 Scalability Metrics:")
        print(json.dumps(metrics, indent=2))
        return

    if args.migrate_storage or args.migrate_storage_execute:
        dry_run = not args.migrate_storage_execute
        migration_report = registry.migrate_to_scalable_storage(
            dry_run=dry_run)
        print(
            f"🔄 Storage Migration {
                '(DRY RUN)' if dry_run else '(EXECUTING)'}:")
        print(json.dumps(migration_report, indent=2))
        return

    # Validate main command arguments
    if not all([args.task_id, args.agent_id, args.source_path]):
        parser.error(
            "task_id, agent_id, and source_path are required for registration")

    # Parse metadata if provided
    metadata = {}
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing metadata JSON: {e}")
            sys.exit(1)

    # Register the output
    try:
        print(
            f"📝 Registering {args.agent_id} output for task {args.task_id}...")

        registration = registry.register_output(
            task_id=args.task_id,
            agent_id=args.agent_id,
            source_path=args.source_path,
            output_type=args.type,
            extract_code=args.extract_code,
            metadata=metadata
        )

        print(f"✅ Successfully registered output:")
        print(f"   📁 Task: {registration.task_id}")
        print(f"   🤖 Agent: {registration.agent_id}")
        print(f"   📄 Output: {registration.output_path}")
        print(f"   📊 Size: {registration.file_size} bytes")
        print(f"   ⏰ Time: {registration.registration_time}")

        if registration.extracted_artifacts:
            print(
                f"   📦 Extracted {len(registration.extracted_artifacts)} code artifacts:")
            for artifact in registration.extracted_artifacts:
                print(f"      🔧 {artifact}")

        # Show next steps
        print(f"\n🔄 Step 4.4 Complete: Agent output registered successfully")
        print(f"   📊 Status file: outputs/{args.task_id}/status.json")
        print(f"   🔍 Ready for QA agent input preparation")

    except Exception as e:
        print(f"❌ Error registering output: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
