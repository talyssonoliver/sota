#!/usr/bin/env python3
"""
Fast Pre-commit Validator
Lightweight validation designed for pre-commit hooks.
"""

import argparse
import ast
import sys
import time
from pathlib import Path
from typing import List


class FastPrecommitValidator:
    """Ultra-fast validator for pre-commit hooks."""

    def __init__(self, files: List[str]):
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

            if line.startswith("from orchestration."):
                self.errors.append(
                    f"{file_path}:{i}: Deprecated import 'from orchestration.' - use 'from src.core.workflows.'"
                )
                success = False

            if line.startswith("from tools.") and "tools.memory." not in line:
                self.errors.append(
                    f"{file_path}:{i}: Deprecated import 'from tools.' - use 'from src.infrastructure.tools.'"
                )
                success = False

        return success

    def _check_architecture(self, file_path: Path, content: str) -> bool:
        """Quick architecture validation."""
        success = True

        # Check if file is in deprecated directory
        deprecated_dirs = [
            "orchestration/",
            "tools/memory/",
            "handlers/",
            "memory-bank/",
            "patches/",
        ]
        file_str = str(file_path).replace("\\", "/")

        for deprecated_dir in deprecated_dirs:
            if deprecated_dir in file_str:
                self.errors.append(
                    f"{file_path}: File in deprecated directory - move to /src/ structure"
                )
                success = False
                break

        return success


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
