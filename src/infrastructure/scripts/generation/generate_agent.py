#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import Path, subprocess, yaml
"""SOTA Agent Generator - Creates agent code, tests, and docs.

Generates complete agent implementations including:
- Agent class with SOTA patterns
- Unit tests with comprehensive coverage
- Documentation with usage examples
- Configuration integration
"""

from __future__ import annotations

import argparse
# from pathlib import Path  # Consolidated to common_imports
from typing import Dict

# import yaml  # Consolidated to common_imports
from jinja2 import Environment, FileSystemLoader

CONFIG_PATH = Path("config/agent_generator.yaml")


def load_config(path: Path) -> Dict[str, str]:
    """Load configuration from YAML file.
    
    Args:
        path: Path to configuration file
        
    Returns:
        Configuration dictionary with default values if file not found
    """
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
    """Convert name to snake_case format.
    
    Args:
        name: Input name to convert
        
    Returns:
        Snake case version of the name
    """
    return name.lower().replace(" ", "_")


def render_template(
    env: Environment, template_name: str, context: Dict[str, str]
) -> str:
    """Render Jinja2 template with context.
    
    Args:
        env: Jinja2 environment
        template_name: Name of template file
        context: Template context variables
        
    Returns:
        Rendered template content
    """
    template = env.get_template(template_name)
    return template.render(**context)


def append_import(agent_file: Path, func_name: str) -> None:
    """Append import statement to __init__.py.
    
    Args:
        agent_file: Path to generated agent file
        func_name: Function name to import
    """
    init_file = Path("agents/__init__.py")
    if not init_file.exists():
        return
    import_line = f"from .{agent_file.stem} import {func_name}\n"
    with open(init_file, "a") as f:
        f.write(import_line)


def update_config(agent_key: str, description: str) -> None:
    """Update agents configuration file.
    
    Args:
        agent_key: Unique key for the agent
        description: Agent description
    """
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


def create_agent_files(env: Environment, context: Dict[str, str], cfg: Dict[str, str]) -> tuple[Path, Path, Path]:
    """Create agent, test, and documentation files.
    
    Args:
        env: Jinja2 environment for template rendering
        context: Template context variables
        cfg: Configuration dictionary
        
    Returns:
        Tuple of (agent_path, test_path, doc_path)
        
    Raises:
        OSError: If file creation fails
    """
    name_snake = context["name_snake"]
    
    # Create agent file
    agent_code = render_template(env, "agent.py.j2", context)
    agent_path = Path(cfg["output_dir"]) / f"{name_snake}.py"
    agent_path.parent.mkdir(parents=True, exist_ok=True)
    agent_path.write_text(agent_code, encoding='utf-8')

    # Create test file
    test_code = render_template(env, "test_agent.py.j2", context)
    test_path = Path(cfg["test_dir"]) / f"test_{name_snake}.py"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text(test_code, encoding='utf-8')

    # Create doc file
    doc_code = render_template(env, "doc.md.j2", context)
    doc_path = Path(cfg["doc_dir"]) / f"{name_snake}_agent.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(doc_code, encoding='utf-8')
    
    return agent_path, test_path, doc_path


def format_generated_files(agent_path: Path, test_path: Path) -> bool:
    """Format generated code files using black and ruff.
    
    Args:
        agent_path: Path to generated agent file
        test_path: Path to generated test file
        
    Returns:
        True if formatting succeeded, False otherwise
    """
#     import subprocess  # Consolidated to common_imports
    
    try:
        # Format with black
        result = subprocess.run(
            ["black", str(agent_path), str(test_path)], 
            capture_output=True, 
            text=True,
            check=False
        )
        
        # Fix with ruff
        subprocess.run(
            ["ruff", "check", "--fix", str(agent_path), str(test_path)], 
            capture_output=True, 
            text=True,
            check=False
        )
        
        return True
        
    except FileNotFoundError:
        print("Warning: black or ruff not found, skipping code formatting")
        return False
    except subprocess.SubprocessError as e:
        print(f"Warning: Code formatting failed: {e}")
        return False


def validate_generated_code(agent_code: str, agent_path: Path) -> bool:
    """Validate generated agent code for syntax errors.
    
    Args:
        agent_code: Generated agent code content
        agent_path: Path to agent file for error reporting
        
    Returns:
        True if code is valid, False if syntax errors found
    """
    try:
        compile(agent_code, str(agent_path), "exec")
        return True
    except SyntaxError as e:
        print(f"Syntax error in generated code: {e}")
        return False


def cleanup_on_error(agent_path: Path, test_path: Path, doc_path: Path) -> None:
    """Clean up generated files if validation fails.
    
    Args:
        agent_path: Path to agent file
        test_path: Path to test file  
        doc_path: Path to documentation file
    """
    for path in [agent_path, test_path, doc_path]:
        if path.exists():
            path.unlink(missing_ok=True)


def main() -> None:
    """Main entry point for agent generation.
    
    Orchestrates the complete agent generation process including
    file creation, formatting, and validation.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate a new agent")
    parser.add_argument("name", help="Agent name")
    parser.add_argument("description", help="Short description")
    args = parser.parse_args()

    try:
        # Load configuration and setup environment
        cfg = load_config(CONFIG_PATH) 
        env = Environment(loader=FileSystemLoader(cfg["template_dir"]), autoescape=True)

        # Prepare template context
        name_snake = slugify(args.name)
        context = {
            "agent_name": args.name,
            "description": args.description,
            "name_snake": name_snake,
        }

        # Create all files
        agent_path, test_path, doc_path = create_agent_files(env, context, cfg)
        
        # Update imports and configuration
        append_import(agent_path, f"create_{name_snake}_agent")
        update_config(name_snake, args.description)

        # Format generated code
        format_generated_files(agent_path, test_path)

        # Validate generated code
        agent_code = agent_path.read_text(encoding='utf-8')
        if not validate_generated_code(agent_code, agent_path):
            cleanup_on_error(agent_path, test_path, doc_path)
            return

        print(f"✅ Created agent {args.name} at {agent_path}")
        
    except Exception as e:
        print(f"❌ Agent generation failed: {e}")
        # Attempt cleanup if paths were created
        try:
            cleanup_on_error(agent_path, test_path, doc_path)  
        except NameError:
            pass  # Paths not yet defined


if __name__ == "__main__":
    main()
