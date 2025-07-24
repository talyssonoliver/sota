#!/usr/bin/env python3
"""
Global Import Fix Script - Updates all Python imports after architecture cleanup

This script systematically updates all import statements to reflect the new
clean architecture structure after removing duplicate directories.

Import Mappings:
- orchestration.* → src.core.workflows.*
- tools.* → src.infrastructure.tools.* (with special cases)
- tools.memory.* → src.infrastructure.memory.*
- handlers.* → src.infrastructure.tools.handlers.*
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Define import mappings
IMPORT_MAPPINGS = {
    # Orchestration to workflows
    r"from orchestration\.": "from src.core.workflows.",
    r"import orchestration\.": "import src.core.workflows.",
    r"from src.core.workflows import": "from src.core.workflows import",
    # Tools memory to infrastructure memory
    r"from tools\.memory\.": "from src.infrastructure.memory.",
    r"import tools\.memory\.": "import src.infrastructure.memory.",
    r"from tools\.memory import": "from src.infrastructure.memory import",
    # Specific tool mappings
    r"from tools\.base_tool": "from src.infrastructure.tools.core.base_tool",
    r"from tools\.rate_limiter": "from src.infrastructure.tools.core.rate_limiter",
    r"from tools\.coverage_tool": "from src.infrastructure.tools.development.coverage_tool",
    r"from tools\.cypress_tool": "from src.infrastructure.tools.development.cypress_tool",
    r"from tools\.jest_tool": "from src.infrastructure.tools.development.jest_tool",
    r"from tools\.github_tool": "from src.infrastructure.tools.external.github_tool",
    r"from tools\.vercel_tool": "from src.infrastructure.tools.external.vercel_tool",
    r"from tools\.design_system_tool": "from src.infrastructure.tools.frontend.design_system_tool",
    r"from tools\.tailwind_tool": "from src.infrastructure.tools.frontend.tailwind_tool",
    r"from tools\.markdown_tool": "from src.infrastructure.tools.documentation.markdown_tool",
    # General tools mappings (for files already in src/infrastructure/tools)
    r"from tools\.context_tracker": "from src.infrastructure.tools.context_tracker",
    r"from tools\.context_visualizer": "from src.infrastructure.tools.context_visualizer",
    r"from tools\.echo_tool": "from src.infrastructure.tools.echo_tool",
    r"from tools\.retrieval_qa": "from src.infrastructure.tools.retrieval_qa",
    r"from tools\.supabase_tool": "from src.infrastructure.tools.supabase_tool",
    r"from tools\.tool_loader": "from src.infrastructure.tools.tool_loader",
    # Import statements
    r"import tools\.": "import src.infrastructure.tools.",
    # Handlers
    r"from handlers\.": "from src.infrastructure.tools.handlers.",
    r"import handlers\.": "import src.infrastructure.tools.handlers.",
    # Tasks (if any direct imports)
    r"from tasks\.": "from src.core.tasks.",
    r"import tasks\.": "import src.core.tasks.",
}

# Files to skip
SKIP_PATTERNS = [
    "__pycache__",
    ".git",
    ".pytest_cache",
    "backup/",
    "build/",
    ".pyc",
    ".pyo",
    ".pyd",
    "node_modules",
    "venv/",
    ".venv/",
]


def should_skip_file(filepath: str) -> bool:
    """Check if file should be skipped."""
    for pattern in SKIP_PATTERNS:
        if pattern in filepath:
            return True
    return False


def fix_imports_in_file(filepath: Path) -> Tuple[bool, List[str]]:
    """Fix imports in a single file. Returns (modified, changes_made)."""
    if should_skip_file(str(filepath)):
        return False, []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False, []

    original_content = content
    changes = []

    # Apply all import mappings
    for old_pattern, new_pattern in IMPORT_MAPPINGS.items():
        matches = re.findall(old_pattern, content)
        if matches:
            content = re.sub(old_pattern, new_pattern, content)
            changes.append(
                f"{old_pattern} → {new_pattern} ({len(matches)} occurrences)"
            )

    # Write back if modified
    if content != original_content:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True, changes
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False, []

    return False, []


def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python files in directory tree."""
    python_files = []
    for path in root_dir.rglob("*.py"):
        if not should_skip_file(str(path)):
            python_files.append(path)
    return python_files


def main():
    """Main execution function."""
    print("🔧 Global Import Fix Script")
    print("=" * 60)

    # Get project root
    if len(sys.argv) > 1:
        root_dir = Path(sys.argv[1])
    else:
        root_dir = Path.cwd()

    print(f"📁 Scanning directory: {root_dir}")

    # Find all Python files
    python_files = find_python_files(root_dir)
    print(f"📊 Found {len(python_files)} Python files")

    # Process each file
    modified_count = 0
    total_changes = []

    for i, filepath in enumerate(python_files, 1):
        if i % 50 == 0:
            print(f"Progress: {i}/{len(python_files)} files...")

        modified, changes = fix_imports_in_file(filepath)
        if modified:
            modified_count += 1
            relative_path = filepath.relative_to(root_dir)
            print(f"\n✅ Modified: {relative_path}")
            for change in changes:
                print(f"   → {change}")
                total_changes.append((str(relative_path), change))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"   Total files scanned: {len(python_files)}")
    print(f"   Files modified: {modified_count}")
    print(f"   Total import fixes: {len(total_changes)}")

    # Save detailed report
    report_path = root_dir / "import_fixes_report.txt"
    with open(report_path, "w") as f:
        f.write("Import Fixes Report\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total files scanned: {len(python_files)}\n")
        f.write(f"Files modified: {modified_count}\n")
        f.write(f"Total import fixes: {len(total_changes)}\n\n")
        f.write("Detailed Changes:\n")
        f.write("-" * 60 + "\n")

        current_file = None
        for filepath, change in total_changes:
            if filepath != current_file:
                f.write(f"\n{filepath}:\n")
                current_file = filepath
            f.write(f"  - {change}\n")

    print(f"\n📄 Detailed report saved to: {report_path}")
    print("\n✅ Import fix complete!")


if __name__ == "__main__":
    main()
