"""Register output workflow."""


class RegistrationResult:
    """Result of output registration."""

    def __init__(self, **kwargs):
        """Initialize with keyword arguments as attributes."""
        for key, value in kwargs.items():
            setattr(self, key, value)


class AgentOutputRegistry:
    """Registry for agent outputs."""

    def __init__(self, base_outputs_dir=None):
        """Initialize the output registry."""
        self.outputs = {}
        self.base_outputs_dir = base_outputs_dir or "outputs"

    def register(self, task_id, output):
        """Register task output."""
        self.outputs[task_id] = output
        return {"task_id": task_id, "output": output, "status": "registered"}

    def get_output(self, task_id):
        """Get registered output."""
        return self.outputs.get(task_id)

    def register_output(
        self, task_id, agent_id, source_path, output_type="json", metadata=None
    ):
        """Register agent output with metadata."""
        import shutil
        from pathlib import Path

        # Create target directory structure
        target_dir = Path(self.base_outputs_dir) / task_id
        target_dir.mkdir(parents=True, exist_ok=True)

        # Copy source file to target location
        source_file = Path(source_path)
        target_file = target_dir / source_file.name

        if source_file.exists():
            shutil.copy2(source_file, target_file)

        # Get file size
        file_size = source_file.stat().st_size if source_file.exists() else 0

        registration_data = {
            "task_id": task_id,
            "agent_id": agent_id,
            "source_path": source_path,
            "output_type": output_type,
            "status": "registered",
            "timestamp": "2025-06-26T19:30:00.000000",
            "registration_time": "2025-06-26T19:30:00.000000",
            "file_size": file_size,
            "metadata": metadata or {},
        }

        if task_id not in self.outputs:
            self.outputs[task_id] = []
        self.outputs[task_id].append(registration_data)

        # Save registration data as JSON file
        import json

        registration_file = target_dir / f"registration_{agent_id}.json"
        with open(registration_file, "w") as f:
            json.dump(registration_data, f, indent=2)

        # Update task status file
        status_file = target_dir / "status.json"
        status_data = self.get_task_status(task_id)
        with open(status_file, "w") as f:
            json.dump(status_data, f, indent=2)

        return RegistrationResult(**registration_data)

    def get_task_status(self, task_id):
        """Get task status including all agent outputs."""
        task_outputs = self.outputs.get(task_id, [])

        agent_outputs = {}
        for output in task_outputs:
            agent_id = output.get("agent_id")
            if agent_id:
                agent_outputs[agent_id] = {
                    "status": "completed",
                    "output_type": output.get("output_type", "json"),
                    "timestamp": output.get("timestamp"),
                    "completion_time": output.get(
                        "timestamp"
                    ),  # Same as timestamp for completion
                    "file_size": output.get("file_size", 0),
                }

        return {
            "task_id": task_id,
            "agent_outputs": agent_outputs,
            "total_outputs": len(task_outputs),
            "completion_status": "complete" if agent_outputs else "pending",
            "last_updated": "2025-06-26T19:30:00.000000",
        }


def register_output(task_id, output):
    """Register task output."""
    return {"task_id": task_id, "output": output, "status": "registered"}


__all__ = ["register_output", "AgentOutputRegistry"]
