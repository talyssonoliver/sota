
from src.infrastructure.utils.common_imports import (
    Any,
    Dict,
    List,
    Optional,
    Path,
    datetime,
    json,
    re
)
"""Register output workflow."""
# import json  # Consolidated to common_imports
import shutil
# from datetime import datetime  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
# from typing import Any, Dict, List, Optional  # Consolidated to common_imports

from src.infrastructure.utils.common_utils import read_json, write_json


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
        self.base_outputs_dir = Path(base_outputs_dir or "outputs")
        self.base_outputs_dir.mkdir(parents=True, exist_ok=True)

    def get_task_directory(self, task_id: str) -> Path:
        """Get the directory for a specific task."""
        task_dir = self.base_outputs_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir

    def list_task_outputs(self, task_id: str) -> List[Dict[str, Any]]:
        """List all outputs for a specific task."""
        task_dir = self.get_task_directory(task_id)
        outputs = []
        
        for file_path in task_dir.iterdir():
            if (file_path.is_file() and 
                file_path.name != "status.json" and 
                not file_path.name.startswith("registration_")):
                outputs.append({
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "size_bytes": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        return outputs

    def prepare_qa_input(self, task_id: str) -> Dict[str, Any]:
        """Prepare input data for QA agent."""
        task_outputs = self.list_task_outputs(task_id)
        
        # Collect extracted code blocks from registrations
        code_artifacts = []
        if task_id in self.outputs:
            for registration in self.outputs[task_id]:
                if registration.get("extracted_code"):
                    code_artifacts.extend(registration["extracted_code"])
        
        qa_input = {
            "task_id": task_id,
            "output_files": task_outputs,
            "total_files": len(task_outputs),
            "qa_ready": len(task_outputs) > 0,
            "primary_outputs": [f for f in task_outputs if f["file_name"].endswith(('.md', '.json'))],
            "code_artifacts": code_artifacts,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_output_files": len(task_outputs)
            }
        }
        
        # Save QA input file
        task_dir = self.get_task_directory(task_id)
        qa_input_file = task_dir / "qa_input.json"
        
        write_json(qa_input_file, qa_input)
        
        return qa_input

    def register(self, task_id, output):
        """Register task output."""
        self.outputs[task_id] = output
        return {"task_id": task_id, "output": output, "status": "registered"}

    def get_output(self, task_id):
        """Get registered output."""
        return self.outputs.get(task_id)

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status information."""
        task_dir = self.get_task_directory(task_id)
        status_file = task_dir / "status.json"
        
        if status_file.exists():
            return read_json(status_file, default={})
        
        # Return default status if no status file exists
        return {
            "task_id": task_id,
            "overall_status": "not_started",
            "outputs": {},
            "created_at": None,
            "last_updated": None
        }

    def register_output(
        self, task_id: str, agent_id: str, source_path: str, 
        output_type: Optional[str] = None, metadata: Optional[Dict] = None, 
        extract_code: bool = False
    ) -> RegistrationResult:
        """Register agent output with metadata."""
        
        # Create target directory structure
        target_dir = self.get_task_directory(task_id)

        # Copy source file to target location
        source_file = Path(source_path)
        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Auto-detect output_type from file extension if not provided
        if output_type is None:
            file_extension = source_file.suffix.lower()
            if file_extension in ['.md', '.markdown']:
                output_type = "markdown"
            elif file_extension == '.json':
                output_type = "json"
            else:
                output_type = "file"  # Generic file type
        
        # Generate target filename based on agent_id and output_type
        if output_type == "markdown" or output_type == "md":
            target_filename = f"output_{agent_id}.md"
        else:
            # Use original filename for JSON and other types
            target_filename = source_file.name
            
        target_file = target_dir / target_filename
        shutil.copy2(source_file, target_file)

        # Get file size
        file_size = source_file.stat().st_size

        # Create registration metadata
        registration_data = {
            "task_id": task_id,
            "agent_id": agent_id,
            "source_path": str(source_file),
            "target_path": str(target_file),
            "output_type": output_type,
            "file_size": file_size,
            "registration_time": datetime.now().isoformat(),
            "metadata": metadata or {},
            "extract_code": extract_code,
            "status": "registered",
            "extracted_artifacts": []  # Initialize empty list
        }

        # Extract code if requested
        if extract_code and output_type in ["markdown", "md"]:
            extracted_code = self._extract_code_blocks(source_file)
            registration_data["extracted_code"] = extracted_code
            
            # Save extracted code to separate files and track artifacts
            extracted_artifacts = []
            code_dir = target_dir / "code"
            code_dir.mkdir(exist_ok=True)
            
            for i, code_block in enumerate(extracted_code):
                if code_block.get("filename"):
                    code_file = code_dir / code_block["filename"]
                else:
                    lang = code_block.get("language", "txt")
                    code_file = code_dir / f"extracted_code_{i}.{lang}"
                
                code_file.write_text(code_block["content"], encoding='utf-8')
                extracted_artifacts.append(str(code_file))
            
            registration_data["extracted_artifacts"] = extracted_artifacts

        # Update status file
        self._update_status_file(task_id, agent_id, registration_data)

        # Save individual registration metadata file
        registration_file = target_dir / f"registration_{agent_id}.json"
        with open(registration_file, 'w', encoding='utf-8') as f:
            json.dump(registration_data, f, indent=2, ensure_ascii=False)

        # Store in memory
        if task_id not in self.outputs:
            self.outputs[task_id] = []
        self.outputs[task_id].append(registration_data)

        return RegistrationResult(**registration_data)

    def _extract_code_blocks(self, markdown_file: Path) -> List[Dict[str, Any]]:
        """Extract code blocks from markdown file."""
        content = markdown_file.read_text(encoding='utf-8')
        code_blocks = []
        
        # Language normalization mapping
        language_mapping = {
            "typescript": "ts",
            "javascript": "js", 
            "python": "py",
            "markdown": "md",
            "bash": "sh",
            "shell": "sh"
        }
        
#         import re  # Consolidated to common_imports
        # Pattern to match code blocks with optional language and filename
        # Supports both // filename: and -- filename: comment styles
        pattern = r'```(\w+)?\n?(?:(?://|--) filename: (.+?)\n)?(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            raw_language = match.group(1) or "text"
            filename = match.group(2)
            code_content = match.group(3).strip()
            
            # Normalize language name
            language = language_mapping.get(raw_language.lower(), raw_language.lower())
            
            code_blocks.append({
                "language": language,
                "filename": filename,
                "content": code_content
            })
        
        return code_blocks

    def _update_status_file(self, task_id: str, agent_id: str, registration_data: Dict):
        """Update task status file."""
        task_dir = self.get_task_directory(task_id)
        status_file = task_dir / "status.json"
        
        # Load existing status or create new
        if status_file.exists():
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
        else:
            status = {
                "task_id": task_id,
                "outputs": {},
                "overall_status": "in_progress",
                "created_at": datetime.now().isoformat()
            }
        
        # Update with new output
        status["outputs"][agent_id] = {
            "output_file": registration_data["target_path"],
            "file_size": registration_data["file_size"],
            "output_type": registration_data["output_type"],
            "timestamp": registration_data["registration_time"],
            "extract_code": registration_data["extract_code"]
        }
        
        # Initialize agent_outputs if it doesn't exist
        if "agent_outputs" not in status:
            status["agent_outputs"] = {}
            
        # Update agent_outputs with status
        status["agent_outputs"][agent_id] = {
            "status": "completed",
            "output_file": Path(registration_data["target_path"]).name,
            "completion_time": registration_data["registration_time"],
            "file_size": registration_data["file_size"],
            "metadata": registration_data["metadata"]
        }
        
        status["last_updated"] = datetime.now().isoformat()
        
        # Save updated status
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
