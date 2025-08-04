#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import Path, os
"""
Secure Task Lifecycle Management with Archive Validation

Fixed security vulnerability: tarfile.extractall validation (B202)
"""

import tarfile
# import os  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
from typing import Dict


def safe_extract_tarfile(tar_path: Path, extract_to: Path) -> bool:
    """
    Safely extract tarfile with member validation to prevent path traversal attacks.
    
    This function validates each member of the tarfile before extraction to ensure:
    1. No absolute paths that could overwrite system files
    2. No path traversal attempts using ../
    3. No symlinks that could point outside the extraction directory
    
    Args:
        tar_path: Path to the tar archive
        extract_to: Directory to extract files to
        
    Returns:
        bool: True if extraction was successful, False otherwise
    """
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            # Get the absolute path of the extraction directory
            extract_to_abs = extract_to.resolve()
            
            # Validate each member before extraction
            for member in tar.getmembers():
                # Get the absolute path where this member would be extracted
                member_path = (extract_to_abs / member.name).resolve()
                
                # Check 1: Ensure the member path is within the extraction directory
                if not str(member_path).startswith(str(extract_to_abs)):
                    print(f"⚠️ Skipping dangerous path: {member.name}")
                    continue
                
                # Check 2: Skip if member is a symlink (could point outside directory)
                if member.issym() or member.islnk():
                    print(f"⚠️ Skipping symlink: {member.name}")
                    continue
                
                # Check 3: Skip if member name contains suspicious patterns
                if ".." in member.name or member.name.startswith("/"):
                    print(f"⚠️ Skipping suspicious path: {member.name}")
                    continue
                
                # Safe to extract this member
                tar.extract(member, extract_to)
                
        return True
        
    except Exception as e:
        print(f"❌ Failed to safely extract archive: {e}")
        return False


def restore_task_from_archive(task_id: str, metadata: Dict, outputs_dir: Path) -> bool:
    """
    Restore a task from archive with security validation.
    
    This is a secure replacement for the vulnerable extractall() usage.
    """
    archive_location = metadata.get(task_id, {}).get('archive_location')
    if not archive_location:
        print(f"⚠️ No archive location found for task: {task_id}")
        return False
        
    archive_path = Path(archive_location)
    
    if not archive_path.exists():
        print(f"⚠️ Archive file not found: {archive_path}")
        return False
    
    # Use secure extraction method
    if safe_extract_tarfile(archive_path, outputs_dir):
        print(f"📂 Safely restored {task_id} from archive")
        return True
    else:
        print(f"❌ Failed to restore {task_id}")
        return False


# Example of how to patch the existing method
def patch_task_lifecycle_restore(lifecycle_instance):
    """
    Monkey patch the restore_from_archive method with secure version.
    
    This can be applied to existing TaskLifecycle instances.
    """
    def secure_restore_from_archive(self, task_id: str) -> bool:
        """Secure version of restore_from_archive."""
        if task_id not in self.metadata:
            print(f"⚠️ No metadata found for task: {task_id}")
            return False
        
        metadata = self.metadata[task_id]
        archive_path = Path(metadata.archive_location)
        
        if not archive_path.exists():
            print(f"⚠️ Archive file not found: {archive_path}")
            return False
        
        # Use secure extraction
        if safe_extract_tarfile(archive_path, self.outputs_dir):
            print(f"📂 Safely restored {task_id} from archive")
            return True
        else:
            return False
    
    # Replace the method
    lifecycle_instance.restore_from_archive = secure_restore_from_archive.__get__(
        lifecycle_instance, 
        lifecycle_instance.__class__
    )