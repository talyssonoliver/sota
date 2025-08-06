#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import (
    Path,
    datetime,
    json,
    re,
    sys
)
"""
Secure Agent Generation Script

Fixed security vulnerability: Jinja2 autoescape for XSS prevention (B701)
"""

import argparse
# from pathlib import Path  # Consolidated to common_imports
from jinja2 import Environment, FileSystemLoader, select_autoescape
from slugify import slugify


def create_secure_jinja_environment(template_dir: str) -> Environment:
    """
    Create a Jinja2 environment with autoescape enabled for security.
    
    This prevents XSS vulnerabilities by automatically escaping variables
    in templates based on file extension.
    
    Args:
        template_dir: Directory containing Jinja2 templates
        
    Returns:
        Environment: Configured Jinja2 environment with autoescape
    """
    return Environment(
        loader=FileSystemLoader(template_dir),
        # Enable autoescape for HTML, XML, and common template extensions
        autoescape=select_autoescape(
            enabled_extensions=('html', 'htm', 'xml', 'xhtml', 'j2', 'jinja', 'jinja2'),
            default_for_string=True,  # Enable autoescape for string templates
            default=True  # Enable autoescape by default for safety
        ),
        # Additional security settings
        trim_blocks=True,
        lstrip_blocks=True
    )


def render_template(env: Environment, template_name: str, context: dict) -> str:
    """
    Render a template with the given context.
    
    Args:
        env: Jinja2 environment
        template_name: Name of the template file
        context: Dictionary of variables for the template
        
    Returns:
        str: Rendered template content
    """
    template = env.get_template(template_name)
    return template.render(**context)


def load_config(config_path: Path) -> dict:
    """Load configuration from file."""
#     import json  # Consolidated to common_imports
    
    with open(config_path, 'r') as f:
        return json.load(f)


def validate_agent_name(name: str) -> str:
    """
    Validate and sanitize agent name to prevent injection attacks.
    
    Args:
        name: Proposed agent name
        
    Returns:
        str: Validated agent name
        
    Raises:
        ValueError: If name contains invalid characters
    """
    # Allow only alphanumeric, spaces, hyphens, and underscores
#     import re  # Consolidated to common_imports
    
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        raise ValueError(
            "Agent name can only contain letters, numbers, spaces, hyphens, and underscores"
        )
    
    return name.strip()


def main():
    """
    Main function for secure agent generation.
    
    Handles command line parsing and orchestrates agent generation
    including code creation, testing, documentation, and validation.
    All user inputs are properly sanitized and templates are rendered
    with autoescape enabled.
    """
    parser = argparse.ArgumentParser(description="Generate a new agent securely")
    parser.add_argument("name", help="Agent name")
    parser.add_argument("description", help="Short description")
    parser.add_argument(
        "--config", 
        default="config/agent_generator.json",
        help="Path to configuration file"
    )
    args = parser.parse_args()
    
    # Validate inputs to prevent injection
    try:
        agent_name = validate_agent_name(args.name)
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        return 1
    
    cfg = load_config(config_path)
    
    # Create secure Jinja2 environment with autoescape
    env = create_secure_jinja_environment(cfg["template_dir"])
    
    # Prepare template context with sanitized values
    name_snake = slugify(agent_name)
    context = {
        "agent_name": agent_name,  # Already validated
        "description": args.description,  # Will be auto-escaped in templates
        "name_snake": name_snake,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    try:
        # Create agent file with secure rendering
        agent_code = render_template(env, "agent.py.j2", context)
        
        # Write agent file
        output_dir = Path(cfg.get("output_dir", "src/core/agents"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        agent_file = output_dir / f"{name_snake}.py"
        agent_file.write_text(agent_code)
        
        print(f"✅ Successfully generated agent: {agent_file}")
        
        # Generate test file if template exists
        if (Path(cfg["template_dir"]) / "agent_test.py.j2").exists():
            test_code = render_template(env, "agent_test.py.j2", context)
            
            test_dir = Path(cfg.get("test_dir", "tests/unit/core/agents"))
            test_dir.mkdir(parents=True, exist_ok=True)
            
            test_file = test_dir / f"test_{name_snake}.py"
            test_file.write_text(test_code)
            
            print(f"✅ Successfully generated test: {test_file}")
        
        # Generate documentation if template exists
        if (Path(cfg["template_dir"]) / "agent_doc.md.j2").exists():
            doc_content = render_template(env, "agent_doc.md.j2", context)
            
            doc_dir = Path(cfg.get("doc_dir", "docs/agents"))
            doc_dir.mkdir(parents=True, exist_ok=True)
            
            doc_file = doc_dir / f"{name_snake}.md"
            doc_file.write_text(doc_content)
            
            print(f"✅ Successfully generated documentation: {doc_file}")
        
        return 0
        
    except Exception as e:
        print(f"Error generating agent: {e}")
        return 1


if __name__ == "__main__":
#     import sys  # Consolidated to common_imports
#     from datetime import datetime  # Consolidated to common_imports
    
    sys.exit(main())