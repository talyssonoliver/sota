#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import Path, sys, time
"""
Fast Pre-commit Validator
Lightweight validation designed for pre-commit hooks.
"""

import argparse
import ast
from typing import List, Optional, Any

from src.infrastructure.utils.base_classes import BaseValidator


class FastPrecommitValidator(BaseValidator):
    """Ultra-fast validator for pre-commit hooks."""

    def __init__(self, files: List[str]):
        # Initialize base validator without a specific root path
        super().__init__(name="FastPrecommitValidator")
        self.files = [Path(f) for f in files if f.endswith(".py")]
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """Run all fast validations."""
        start_time = time.time()

        print(f"🚀 Fast validation on {len(self.files)} files...")

        success = True
        for file_path in self.files:
            if not self._validate_file(file_path):
                success = False

        elapsed = time.time() - start_time
        print(f"⏱️  Validation completed in {elapsed:.2f}s")

        if self.errors:
            print(f"❌ {len(self.errors)} errors found")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"⚠️  {len(self.warnings)} warnings found")
            for warning in self.warnings:
                print(f"  - {warning}")

        return success

    def _validate_file(self, file_path: Path) -> bool:
        """Validate a single file."""
        try:
            # Ensure the file path is resolved and exists
            if not file_path.exists():
                # Try to resolve relative to current directory
                file_path = Path.cwd() / file_path

            if not file_path.exists():
                self.errors.append(f"{file_path}: File does not exist")
                return False

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Quick syntax check
            if not self._check_syntax(file_path, content):
                return False

            # Quick import check
            if not self._check_imports(file_path, content):
                return False

            # Quick architecture check
            if not self._check_architecture(file_path, content):
                return False

            return True

        except Exception as e:
            self.errors.append(f"{file_path}: Failed to read - {str(e)}")
            return False

    def _check_syntax(self, file_path: Path, content: str) -> bool:
        """Quick syntax validation."""
        try:
            ast.parse(content)
            return True
        except SyntaxError as e:
            self.errors.append(f"{file_path}:{e.lineno}: Syntax error - {e.msg}")
            return False

    def _check_imports(self, file_path: Path, content: str) -> bool:
        """Quick import validation."""
        success = True
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            line = line.strip()

            # Check for deprecated imports
            if line.startswith("from memory."):
                self.errors.append(
                    f"{file_path}:{i}: Deprecated import 'from memory.' - use 'from src.infrastructure.memory.'"
                )
                success = False

            if line.startswith("from src.core.workflows."):
                self.errors.append(
                    f"{file_path}:{i}: Deprecated import 'from src.core.workflows.' - use 'from src.core.workflows.'"
                )
                success = False

            if line.startswith("from src.platform.tools.") and "tools.memory." not in line:
                self.errors.append(
                    f"{file_path}:{i}: Deprecated import 'from src.platform.tools.' - use 'from src.infrastructure.tools.'"
                )
                success = False

        return success

    def _check_architecture(self, file_path: Path, content: str) -> bool:
        """Quick architecture validation."""
        success = True

        # Check for deprecated directory locations
        deprecated_dirs = [
            "orchestration",
            "tools", 
            "utils",
            "memory",
            "analytics",
            "api",
            "cli",
            "dashboard",
            "visualization",
            "handlers",
            "graph",
            "examples",
            "scripts",
            "memory-bank",
            "patches"
        ]
        
        # Convert path to string and check if it's in any deprecated directory
        path_str = str(file_path).replace("\\", "/")  # Handle Windows paths
        for deprecated_dir in deprecated_dirs:
            # Check if path starts with deprecated dir or contains it as a directory
            if (path_str.startswith(f"{deprecated_dir}/") or 
                f"/{deprecated_dir}/" in path_str or
                path_str == deprecated_dir):
                self.errors.append(
                    f"{file_path}: File in deprecated directory '{deprecated_dir}' - should be moved to src/ structure"
                )
                success = False
                break

        return success
    
    def _get_default_config(self):
        """Get default configuration for this validator."""
        return {
            "strict_mode": False,
            "auto_fix": False,
            "max_issues": 1000
        }
    
    def _validate_target(self, target: Any):
        """Implementation of abstract method from BaseValidator.
        
        Args:
            target: The target to validate (not used in this implementation)
        """
        # This validator uses validate_all() as the main entry point
        # The actual validation logic is in validate_all() and _validate_file()
        pass


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fast Pre-commit Validator")
    parser.add_argument("files", nargs="*", help="Files to validate")
    parser.add_argument("--staged", action="store_true", help="Validate staged files")

    args = parser.parse_args()

    files = args.files
    if not files:
        print("No files to validate")
        return 0

    validator = FastPrecommitValidator(files)
    success = validator.validate_all()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
