#!/usr/bin/env python3
"""
Step 5.8 — Archive Outputs for Long-Term Use

Compress task data for traceability, compliance, and retrospective audits.
Creates compressed archives of complete task outputs including all artifacts.

Usage:
    python scripts/archive_task.py BE-07
    python scripts/archive_task.py --task-id BE-07 --output-dir custom_archives
"""

import argparse
import json
import logging
import shutil
import sys
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskArchiver:
    """Handles archiving of completed task outputs."""
    
    def __init__(self, outputs_dir: str = "outputs", archives_dir: str = "archives"):
        self.outputs_dir = Path(outputs_dir)
        self.archives_dir = Path(archives_dir)
        self.archives_dir.mkdir(exist_ok=True)
    
    def archive_task(self, task_id: str, compression: str = "gzip") -> Optional[Path]:
        """
        Archive all outputs for a completed task.
        
        Args:
            task_id: Task identifier (e.g., "BE-07")
            compression: Compression method ("gzip", "bzip2", "xz")
            
        Returns:
            Path to created archive file, or None if failed
        """
        task_dir = self.outputs_dir / task_id
        
        if not task_dir.exists():
            logger.error(f"Task directory not found: {task_dir}")
            return None
        
        # Generate archive filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if compression == "gzip":
            archive_name = f"{task_id}_{timestamp}.tar.gz"
            mode = "w:gz"
        elif compression == "bzip2":
            archive_name = f"{task_id}_{timestamp}.tar.bz2"  
            mode = "w:bz2"
        elif compression == "xz":
            archive_name = f"{task_id}_{timestamp}.tar.xz"
            mode = "w:xz"
        else:
            archive_name = f"{task_id}_{timestamp}.tar"
            mode = "w"
        
        archive_path = self.archives_dir / archive_name
        
        try:
            print(f"🗜️ Creating archive for task {task_id}...")
            
            # Create archive metadata
            metadata = self._collect_archive_metadata(task_dir, task_id)
            
            # Create tar archive
            with tarfile.open(archive_path, mode) as tar:
                # Add the entire task directory
                tar.add(task_dir, arcname=task_id)
                
                # Add metadata file
                metadata_file = task_dir / "archive_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                
                tar.add(metadata_file, arcname=f"{task_id}/archive_metadata.json")
            
            # Clean up temporary metadata file
            if metadata_file.exists():
                metadata_file.unlink()
            
            # Verify archive
            if self._verify_archive(archive_path):
                file_size = archive_path.stat().st_size
                print(f"✅ Archive created successfully: {archive_path}")
                print(f"   📦 Archive size: {file_size:,} bytes")
                print(f"   🗂️ Files archived: {metadata['file_count']}")
                print(f"   📅 Created: {metadata['archive_created']}")
                return archive_path
            else:
                logger.error("Archive verification failed")
                if archive_path.exists():
                    archive_path.unlink()
                return None
                
        except Exception as e:
            logger.error(f"Archive creation failed: {e}")
            if archive_path.exists():
                archive_path.unlink()
            return None
    
    def _collect_archive_metadata(self, task_dir: Path, task_id: str) -> Dict:
        """Collect metadata about the task being archived."""
        metadata = {
            "task_id": task_id,
            "archive_created": datetime.now().isoformat(),
            "source_directory": str(task_dir),
            "file_count": 0,
            "total_size_bytes": 0,
            "files": [],
            "qa_status": "unknown",
            "completion_status": "unknown"
        }
        
        # Count files and calculate total size
        for file_path in task_dir.rglob("*"):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                metadata["file_count"] += 1
                metadata["total_size_bytes"] += file_size
                
                relative_path = file_path.relative_to(task_dir)
                metadata["files"].append({
                    "path": str(relative_path),
                    "size_bytes": file_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        # Check QA status
        qa_report_file = task_dir / "qa_report.json"
        if qa_report_file.exists():
            try:
                with open(qa_report_file, 'r') as f:
                    qa_data = json.load(f)
                    metadata["qa_status"] = qa_data.get("status", "unknown")
            except Exception:
                pass
        
        # Check completion status
        status_file = task_dir / "status.json"
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    status_data = json.load(f)
                    metadata["completion_status"] = status_data.get("status", "unknown")
            except Exception:
                pass
        
        return metadata
    
    def _verify_archive(self, archive_path: Path) -> bool:
        """Verify that the archive was created successfully and can be read."""
        try:
            with tarfile.open(archive_path, 'r') as tar:
                # Check that we can list the contents
                members = tar.getmembers()
                return len(members) > 0
        except Exception as e:
            logger.error(f"Archive verification failed: {e}")
            return False
    
    def list_archives(self) -> List[Dict]:
        """List all available task archives."""
        archives = []
        
        for archive_file in self.archives_dir.glob("*.tar*"):
            try:
                stat = archive_file.stat()
                archives.append({
                    "filename": archive_file.name,
                    "path": str(archive_file),
                    "size_bytes": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception:
                continue
        
        return sorted(archives, key=lambda x: x["created"], reverse=True)
    
    def extract_archive(self, archive_path: Path, extract_dir: Optional[Path] = None) -> bool:
        """Extract an archive to specified directory."""
        if extract_dir is None:
            extract_dir = Path("extracted_archives")
        
        extract_dir.mkdir(exist_ok=True)
        
        try:
            print(f"📦 Extracting archive: {archive_path}")
            
            with tarfile.open(archive_path, 'r') as tar:
                tar.extractall(extract_dir)
            
            print(f"✅ Archive extracted to: {extract_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Archive extraction failed: {e}")
            return False


def main():
    """CLI interface for task archiving."""
    parser = argparse.ArgumentParser(
        description="Archive completed task outputs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Archive task outputs
    python scripts/archive_task.py BE-07
    
    # Archive with specific compression
    python scripts/archive_task.py BE-07 --compression bzip2
    
    # List all archives
    python scripts/archive_task.py --list
    
    # Extract archive
    python scripts/archive_task.py --extract archives/BE-07_20250528_143000.tar.gz
        """
    )
    
    parser.add_argument(
        "task_id",
        nargs="?",
        help="Task ID to archive (e.g., BE-07)"
    )
    
    parser.add_argument(
        "--compression",
        choices=["gzip", "bzip2", "xz", "none"],
        default="gzip",
        help="Compression method for archive"
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        default="archives",
        help="Directory to store archives"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available archives"
    )
    
    parser.add_argument(
        "--extract",
        type=Path,
        help="Extract specified archive"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    archiver = TaskArchiver(archives_dir=str(args.output_dir))
    
    if args.list:
        archives = archiver.list_archives()
        if archives:
            print("📦 Available Archives:")
            for archive in archives:
                size_mb = archive["size_bytes"] / (1024 * 1024)
                print(f"   {archive['filename']} ({size_mb:.1f} MB) - {archive['created']}")
        else:
            print("No archives found.")
        return
    
    if args.extract:
        success = archiver.extract_archive(args.extract)
        sys.exit(0 if success else 1)
    
    if not args.task_id:
        parser.error("Task ID is required when not using --list or --extract")
    
    # Archive the task
    compression = None if args.compression == "none" else args.compression
    archive_path = archiver.archive_task(args.task_id, compression)
    
    if archive_path:
        print(f"\n✅ Task {args.task_id} archived successfully")
        print(f"Archive: {archive_path}")
        sys.exit(0)
    else:
        print(f"\n❌ Failed to archive task {args.task_id}")
        sys.exit(1)


if __name__ == "__main__":
    main()
