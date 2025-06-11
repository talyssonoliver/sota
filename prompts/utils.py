"""
Prompt Loader Utility for AI agents
Handles loading and formatting prompt templates from markdown files
"""

import os
from pathlib import Path
from string import Template
from typing import Any, Dict, Optional


def load_prompt_template(template_path: str) -> str:
    """
    Load a prompt template from a markdown file.

    Args:
        template_path: Relative path to the template file from project root

    Returns:
        The raw content of the template file as a string
    """
    # Get the project root directory (parent of prompts/)
    root_dir = Path(__file__).parent.parent

    # Construct the full path to the template
    full_path = root_dir / template_path

    if not full_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {full_path}")

    with open(full_path, "r", encoding="utf-8") as file:
        return file.read()


def format_prompt_template(template: str, variables: Dict[str, Any]) -> str:
    """
    Format a prompt template by replacing variables with their values.

    Args:
        template: The raw template string
        variables: Dictionary of variable names and their values

    Returns:
        The formatted prompt with variables replaced
    """
    # Handle both {variable} and $variable formats
    formatted = template
    
    # First handle {variable} format
    for key, value in variables.items():
        formatted = formatted.replace(f"{{{key}}}", str(value))
    
    # Then handle $variable format using Template
    template_obj = Template(formatted)
    return template_obj.safe_substitute(variables)


def load_and_format_prompt(
    template_path: str,
    variables: Optional[Dict[str, Any]] = None
) -> str:
    """
    Load a prompt template and format it with variables.

    Args:
        template_path: Path to the template file
        variables: Dictionary of variable names and their values

    Returns:
        The formatted prompt
    """
    if variables is None:
        variables = {}

    # Load the raw template
    template = load_prompt_template(template_path)

    # Format the template with variables
    return format_prompt_template(template, variables)


def load_prompt(prompt_path: str) -> str:
    """Load prompt template with enhanced error handling"""
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to generic prompt
        return load_generic_prompt(prompt_path)


def load_generic_prompt(prompt_path: str) -> str:
    """Load generic prompt template as fallback"""
    agent_role = os.path.basename(prompt_path).replace(
        '.md', '').replace('-agent', '')

    return f"""# {agent_role.title()} Agent

## Role
You are a specialized {agent_role} agent in a multi-agent AI system for the Artesanato E-commerce project.

## Context
{{context}}

## Task
{{task_description}}

## Instructions
Use the provided context to complete the assigned task efficiently and accurately. Follow the patterns and standards outlined in the context when implementing solutions.

## Output Format
Provide clear, implementable solutions with code examples where appropriate. Include explanations of your approach and any assumptions made.
"""


def format_prompt_with_context(prompt_template: str,
                               context: str,
                               task_data: Dict[str,
                                               Any] = None,
                               **kwargs) -> str:
    """Format prompt template with context and task data. Accepts extra kwargs for backward compatibility."""
    formatted_prompt = prompt_template
    # If context is a list, join it
    if isinstance(context, list):
        context_str = '\n'.join(str(x) for x in context)
    else:
        context_str = str(context)
    # Replace context placeholder
    if "{context}" in formatted_prompt:
        formatted_prompt = formatted_prompt.replace("{context}", context_str)
    else:
        # For test compatibility, append context if not present
        formatted_prompt += f"\n{context_str}"
    # Replace task-specific placeholders
    if task_data:
        for key, value in task_data.items():
            placeholder = f"{{{key}}}"
            if placeholder in formatted_prompt:
                formatted_prompt = formatted_prompt.replace(
                    placeholder, str(value))
    # Replace any additional placeholders from kwargs
    for key, value in kwargs.items():
        placeholder = f"{{{key}}}"
        if placeholder in formatted_prompt:
            formatted_prompt = formatted_prompt.replace(
                placeholder, str(value))
    return formatted_prompt


def extract_context_sources(context):
    """Extract context sources from formatted context. Accepts str or list."""
    if isinstance(context, list):
        context = '\n'.join(context)
    sources = []
    for line in context.split('\n'):
        if 'Source:' in line:
            sources += [s.strip() for s in line.split('Source:')
                        [1].split(',') if s.strip()]
    return sources
