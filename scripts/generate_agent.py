#!/usr/bin/env python3
"""SOTA Agent Generator - Creates agent code, tests, and docs."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader
import yaml

CONFIG_PATH = Path("config/agent_generator.yaml")


def load_config(path: Path) -> Dict[str, str]:
    if path.exists():
        with open(path, "r") as f:
            return yaml.safe_load(f)
    return {
        "template_dir": "templates/agent",
        "output_dir": "agents",
        "test_dir": "tests/agents",
        "doc_dir": "docs",
    }


def slugify(name: str) -> str:
    return name.lower().replace(" ", "_")


def render_template(
    env: Environment, template_name: str, context: Dict[str, str]
) -> str:
    template = env.get_template(template_name)
    return template.render(**context)


def append_import(agent_file: Path, func_name: str) -> None:
    init_file = Path("agents/__init__.py")
    if not init_file.exists():
        return
    import_line = f"from .{agent_file.stem} import {func_name}\n"
    with open(init_file, "a") as f:
        f.write(import_line)


def update_config(agent_key: str, description: str) -> None:
    cfg_file = Path("config/agents.yaml")
    if not cfg_file.exists():
        return
    with open(cfg_file, "r") as f:
        data = yaml.safe_load(f) or {}
    if agent_key in data:
        return
    data[agent_key] = {
        "name": f"{description} Agent",
        "role": description,
        "goal": description,
        "prompt_template": f"prompts/{agent_key}.md",
        "tools": [],
    }
    with open(cfg_file, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a new agent")
    parser.add_argument("name", help="Agent name")
    parser.add_argument("description", help="Short description")
    args = parser.parse_args()

    cfg = load_config(CONFIG_PATH)
    env = Environment(loader=FileSystemLoader(cfg["template_dir"]))

    name_snake = slugify(args.name)
    context = {
        "agent_name": args.name,
        "description": args.description,
        "name_snake": name_snake,
    }

    # Create agent file
    agent_code = render_template(env, "agent.py.j2", context)
    agent_path = Path(cfg["output_dir"]) / f"{name_snake}.py"
    agent_path.write_text(agent_code)

    # Create test file
    test_code = render_template(env, "test_agent.py.j2", context)
    test_path = Path(cfg["test_dir"]) / f"test_{name_snake}.py"
    test_path.write_text(test_code)

    # Create doc file
    doc_code = render_template(env, "doc.md.j2", context)
    doc_path = Path(cfg["doc_dir"]) / f"{name_snake}_agent.md"
    doc_path.write_text(doc_code)

    append_import(agent_path, f"create_{name_snake}_agent")
    update_config(name_snake, args.description)

    os.system(f"black {agent_path} {test_path} >/dev/null")
    os.system(f"ruff check --fix {agent_path} {test_path} >/dev/null")

    try:
        compile(agent_code, str(agent_path), "exec")
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        agent_path.unlink(missing_ok=True)
        test_path.unlink(missing_ok=True)
        doc_path.unlink(missing_ok=True)
        return

    print(f"✅ Created agent {args.name} at {agent_path}")


if __name__ == "__main__":
    main()
