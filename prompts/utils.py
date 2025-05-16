"""
Prompt Loader Utility for AI agents
Handles loading and formatting prompt templates from markdown files
"""

import os
from pathlib import Path
from string import Template
from typing import Dict, Any, Optional


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
    # Create a Template object for string substitution
    template_obj = Template(template)
    
    # Replace all variables in the template
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