#!/usr/bin/env python3
"""Generate minimal documentation for Python modules.

This utility scans all `.py` files in the repository and extracts
classes and functions using the `ast` module. A short Markdown file is
created for each module under the specified output directory.
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List


def extract_symbols(filepath: Path) -> Dict[str, List[dict]]:
    """Return a dictionary of class and function definitions."""
    with filepath.open("r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    symbols = {"classes": [], "functions": []}

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            symbols["classes"].append({"name": node.name, "line": node.lineno, "methods": methods})
        elif isinstance(node, ast.FunctionDef):
            args = [arg.arg for arg in node.args.args]
            symbols["functions"].append({"name": node.name, "line": node.lineno, "args": args})
    return symbols


def generate_markdown(source: Path, symbols: Dict[str, List[dict]]) -> str:
    """Generate a Markdown summary for the given symbols."""
    lines = [f"# {source}", ""]

    if symbols["classes"]:
        lines.append("## Classes")
        for cls in symbols["classes"]:
            lines.append(f"- **{cls['name']}** (line {cls['line']})")
            if cls["methods"]:
                lines.append(f"  - Methods: {', '.join(cls['methods'])}")
        lines.append("")

    if symbols["functions"]:
        lines.append("## Functions")
        for fn in symbols["functions"]:
            args = ", ".join(fn["args"])
            lines.append(f"- **{fn['name']}({args})** (line {fn['line']})")
        lines.append("")

    return "\n".join(lines)


def main(output_dir: str) -> None:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    for file in Path(".").rglob("*.py"):
        if file.is_symlink() or any(part.startswith(".") for part in file.parts):
            continue
        doc = generate_markdown(file, extract_symbols(file))
        target = out_path / f"{file.stem}.md"
        target.write_text(doc, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python automated_doc_generator.py OUTPUT_DIR")
        sys.exit(1)
    main(sys.argv[1])
