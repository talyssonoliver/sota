"""
Auto Fixer
Automatic code fixing capabilities for validation issues.
"""

import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .issue_model import ValidationIssue


class AutoFixer:
    """Handles automatic fixing of validation issues."""

    def __init__(self, root_path: Path, create_backup: bool = True):
        """Initialize auto fixer."""
        self.root_path = root_path
        self.create_backup = create_backup
        self.fixes_applied: List[Dict] = []
        self.available_tools = self._detect_available_tools()

    def _detect_available_tools(self) -> Dict[str, bool]:
        """Detect available code formatting tools."""
        tools = {
            "black": False,
            "ruff": False,
            "isort": False,
            "autopep8": False,
        }

        for tool in tools.keys():
            try:
                result = subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                tools[tool] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                tools[tool] = False

        return tools

    def can_fix(self, issue: ValidationIssue) -> bool:
        """Check if an issue can be automatically fixed."""
        if not issue.auto_fixable:
            return False

        # Check if we have the required tools for specific fixes
        if issue.issue_type == "CODE_FORMATTING":
            return self.available_tools["black"] or self.available_tools["ruff"]
        elif issue.issue_type == "IMPORT_SORTING":
            return self.available_tools["isort"]
        elif issue.issue_type in [
            "UNUSED_IMPORT",
            "EMPTY_DIRECTORY",
            "FORBIDDEN_PATTERN",
        ]:
            return True  # These don't require external tools
        elif str(issue.issue_type).endswith("_NAMING_CONVENTION"):
            return True  # Basic naming fixes

        return False

    def apply_fix(self, issue: ValidationIssue) -> bool:
        """Apply automatic fix for an issue if possible."""
        if not self.can_fix(issue):
            return False

        # Create backup if requested
        file_path = Path(issue.file_path)
        backup_path = None
        if self.create_backup and file_path.exists():
            backup_path = self._create_backup(file_path)

        fix_applied = False

        try:
            if issue.issue_type == "CODE_FORMATTING":
                fix_applied = self._apply_code_formatting(issue)
            elif issue.issue_type == "IMPORT_SORTING":
                fix_applied = self._apply_import_sorting(issue)
            elif issue.issue_type == "UNUSED_IMPORT":
                fix_applied = self._remove_unused_import(issue)
            elif issue.issue_type == "EMPTY_DIRECTORY":
                fix_applied = self._remove_empty_directory(issue)
            elif issue.issue_type == "FORBIDDEN_PATTERN":
                fix_applied = self._remove_forbidden_pattern(issue)
            elif str(issue.issue_type).endswith("_NAMING_CONVENTION"):
                fix_applied = self._fix_naming_convention(issue)

            if fix_applied:
                self.fixes_applied.append(
                    {
                        "issue": issue.to_dict(),
                        "fix_applied": True,
                        "timestamp": datetime.now().isoformat(),
                        "backup_path": str(backup_path) if backup_path else None,
                    }
                )

        except Exception as e:
            print(f"❌ Failed to apply fix for {issue.file_path}: {e}")
            # Restore backup if fix failed
            if backup_path and backup_path.exists():
                try:
                    shutil.copy2(backup_path, file_path)
                except Exception:
                    pass

        return fix_applied

    def _apply_code_formatting(self, issue: ValidationIssue) -> bool:
        """Apply code formatting using Black or Ruff."""
        file_path = Path(issue.file_path)

        if self.available_tools["black"]:
            try:
                result = subprocess.run(
                    ["black", "--quiet", str(file_path)],
                    capture_output=True,
                    text=True,
                )
                return result.returncode == 0
            except Exception:
                pass

        if self.available_tools["ruff"]:
            try:
                result = subprocess.run(
                    ["ruff", "format", str(file_path)],
                    capture_output=True,
                    text=True,
                )
                return result.returncode == 0
            except Exception:
                pass

        return False

    def _apply_import_sorting(self, issue: ValidationIssue) -> bool:
        """Apply import sorting using isort."""
        if not self.available_tools["isort"]:
            return False

        try:
            result = subprocess.run(
                ["isort", "--quiet", issue.file_path],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _remove_unused_import(self, issue: ValidationIssue) -> bool:
        """Remove unused import from file."""
        try:
            file_path = Path(issue.file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if issue.line and issue.line <= len(lines):
                # Remove the line with the unused import
                lines.pop(issue.line - 1)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                return True
        except Exception:
            pass

        return False

    def _remove_empty_directory(self, issue: ValidationIssue) -> bool:
        """Remove empty directory."""
        try:
            dir_path = Path(issue.file_path)
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                dir_path.rmdir()
                return True
        except Exception:
            pass

        return False

    def _remove_forbidden_pattern(self, issue: ValidationIssue) -> bool:
        """Remove line containing forbidden pattern."""
        try:
            file_path = Path(issue.file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if issue.line and issue.line <= len(lines):
                # Remove the line with the forbidden pattern
                lines.pop(issue.line - 1)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                return True
        except Exception:
            pass

        return False

    def _fix_naming_convention(self, issue: ValidationIssue) -> bool:
        """Fix naming convention violations."""
        try:
            file_path = Path(issue.file_path)

            # Simple case: fix file names
            if issue.issue_type == "FILE_NAMING_CONVENTION" and issue.expected_pattern:
                # Convert CamelCase to snake_case
                if file_path.name.endswith(".py"):
                    new_name = (
                        re.sub(r"([A-Z])", r"_\1", file_path.stem).lower().lstrip("_")
                        + ".py"
                    )
                    new_path = file_path.parent / new_name

                    if not new_path.exists():
                        file_path.rename(new_path)
                        return True

            # Handle class and function naming fixes with AST manipulation
            elif issue.issue_type == "CLASS_NAMING_CONVENTION":
                return self._fix_class_naming(issue)
            elif issue.issue_type == "FUNCTION_NAMING_CONVENTION":
                return self._fix_function_naming(issue)

        except Exception:
            pass

        return False

    def _fix_class_naming(self, issue: ValidationIssue) -> bool:
        """Fix class naming convention violations using AST manipulation."""
        try:
            file_path = Path(issue.file_path)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            import ast

            tree = ast.parse(content)
            lines = content.split("\n")

            # Find the class definition at the specified line
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and hasattr(node, "lineno"):
                    if node.lineno == issue.line:
                        old_name = node.name
                        new_name = (
                            self._snake_to_camel(old_name)
                            if "_" in old_name
                            else self._fix_camel_case(old_name)
                        )

                        # Replace class definition on the specific line
                        line_idx = node.lineno - 1
                        if line_idx < len(lines):
                            lines[line_idx] = lines[line_idx].replace(
                                f"class {old_name}", f"class {new_name}"
                            )

                            # Write back to file
                            new_content = "\n".join(lines)
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(new_content)

                            return True

        except Exception as e:
            print(f"❌ Error fixing class naming: {e}")

        return False

    def _fix_function_naming(self, issue: ValidationIssue) -> bool:
        """Fix function naming convention violations using AST manipulation."""
        try:
            file_path = Path(issue.file_path)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            import ast

            tree = ast.parse(content)
            lines = content.split("\n")

            # Find the function definition at the specified line
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and hasattr(node, "lineno"):
                    if node.lineno == issue.line:
                        old_name = node.name
                        new_name = (
                            self._camel_to_snake(old_name)
                            if any(c.isupper() for c in old_name)
                            else old_name
                        )

                        # Replace function definition on the specific line
                        line_idx = node.lineno - 1
                        if line_idx < len(lines):
                            lines[line_idx] = lines[line_idx].replace(
                                f"def {old_name}", f"def {new_name}"
                            )

                            # Write back to file
                            new_content = "\n".join(lines)
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(new_content)

                            return True

        except Exception as e:
            print(f"❌ Error fixing function naming: {e}")

        return False

    def _camel_to_snake(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        # Handle special cases like HTTPError -> http_error
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        return s2.lower()

    def _snake_to_camel(self, name: str) -> str:
        """Convert snake_case to CamelCase."""
        components = name.split("_")
        return "".join(word.capitalize() for word in components)

    def _fix_camel_case(self, name: str) -> str:
        """Fix improper CamelCase (ensure it starts with capital)."""
        if name and name[0].islower():
            return name[0].upper() + name[1:]
        return name

    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """Create a backup of the file before making changes."""
        try:
            backup_dir = self.root_path / "backup" / "validation_fixes"
            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.name}.backup_{timestamp}"
            backup_path = backup_dir / backup_name

            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"⚠️  Could not create backup for {file_path}: {e}")
            return None

    def get_fix_preview(self, issue: ValidationIssue) -> str:
        """Generate a preview of what the fix would do."""
        preview = f"""
🔍 ISSUE ANALYSIS:
   File: {issue.file_path}
   Line: {issue.line or 'N/A'}
   Type: {issue.issue_type}
   Message: {issue.message}
   
🔧 PROPOSED FIX:
   {issue.fix_suggestion or 'Automatic fix available'}
   
📋 FIX STRATEGY:
"""

        if issue.issue_type == "CODE_FORMATTING":
            preview += "   - Run code formatter (Black/Ruff)\n"
        elif issue.issue_type == "IMPORT_SORTING":
            preview += "   - Sort imports using isort\n"
        elif issue.issue_type == "UNUSED_IMPORT":
            preview += f"   - Remove unused import on line {issue.line}\n"
        elif issue.issue_type == "EMPTY_DIRECTORY":
            preview += "   - Remove empty directory\n"
        elif issue.issue_type == "FORBIDDEN_PATTERN":
            preview += f"   - Remove forbidden pattern on line {issue.line}\n"
        elif str(issue.issue_type).endswith("_NAMING_CONVENTION"):
            preview += "   - Rename to follow naming convention\n"

        if issue.offending_line:
            preview += f"\n📄 CURRENT CODE:\n   {issue.offending_line}"

        return preview

    def get_available_tools(self) -> Dict[str, bool]:
        """Get information about available fixing tools."""
        return self.available_tools.copy()

    def get_fixes_applied(self) -> List[Dict]:
        """Get list of all fixes that have been applied."""
        return self.fixes_applied.copy()

    def install_missing_tools(self) -> bool:
        """Attempt to install missing auto-fix tools."""
        missing_tools = [
            tool for tool, available in self.available_tools.items() if not available
        ]

        if not missing_tools:
            return True

        print(f"🔧 Installing missing tools: {', '.join(missing_tools)}")

        for tool in missing_tools:
            try:
                result = subprocess.run(
                    ["pip", "install", tool], capture_output=True, text=True
                )
                if result.returncode == 0:
                    self.available_tools[tool] = True
                    print(f"✅ Successfully installed {tool}")
                else:
                    print(f"❌ Failed to install {tool}")
            except Exception as e:
                print(f"❌ Error installing {tool}: {e}")

        return all(self.available_tools.values())
