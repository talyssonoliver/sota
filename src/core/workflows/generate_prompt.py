
from src.infrastructure.utils.common_imports import (
    Path,
    os,
    sys,
    yaml
)
"""Generate prompt workflow."""
# import os  # Consolidated to common_imports
# import sys  # Consolidated to common_imports
# import yaml  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
from typing import Dict, Any, Optional


def load_task_metadata(task_id: str) -> Dict[str, Any]:
    """Load task metadata from YAML file."""
    task_file = Path(f"tasks/{task_id}.yaml")
    if not task_file.exists():
        raise FileNotFoundError(f"Task metadata file not found for {task_id}")
    
    with open(task_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_prompt_template(template_path: str) -> str:
    """Load prompt template from file."""
    template_file = Path(template_path)
    if not template_file.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    with open(template_file, 'r', encoding='utf-8') as f:
        return f.read()


def get_task_context(task_id: str) -> str:
    """Get task context using memory engine."""
    try:
        metadata = load_task_metadata(task_id)
        context_topics = metadata.get('context_topics', [])
        
        if not context_topics:
            return f"No context_topics defined for task {task_id}"
        
        try:
            from src.infrastructure.memory.engines.memory_engine import MemoryEngine
            memory_engine = MemoryEngine()
            context = memory_engine.build_focused_context(
                context_topics=context_topics,
                max_tokens=2000,
                max_per_topic=2,
                task_id=task_id,
                agent_role="system"
            )
            return context
        except ImportError:
            return f"Context for {task_id}: {', '.join(context_topics)}"
            
    except FileNotFoundError:
        return f"Task metadata not found for {task_id}"


def format_prompt_with_context(template, context, template_vars=None) -> str:
    """Format prompt template with context and other variables."""
    # Handle case where template is a dict (from some test scenarios)
    if isinstance(template, dict):
        template = str(template.get('content', template.get('template', str(template))))
    
    # Ensure template is a string
    if not isinstance(template, str):
        template = str(template)
    
    # Handle case where context is a dict
    if isinstance(context, dict):
        context = str(context.get('content', context.get('context', str(context))))
    
    # Ensure context is a string
    if not isinstance(context, str):
        context = str(context)
    
    formatted = template.replace('{context}', context)
    
    # Replace other placeholders from template_vars
    if template_vars:
        for key, value in template_vars.items():
            placeholder = f'{{{key}}}'
            if placeholder in formatted:
                formatted = formatted.replace(placeholder, str(value))
    
    return formatted


def generate_prompt(task_id: str, agent_type: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Generate prompt for task."""
    # Normalize agent type for template path
    agent_normalized = agent_type.replace('-agent', '').replace('_', '-')
    
    # Map common agent types to actual template names
    agent_mapping = {
        'backend': 'backend-agent',
        'frontend': 'frontend-agent', 
        'qa': 'qa-agent',
        'documentation': 'doc-agent',
        'doc': 'doc-agent',
        'coordinator': 'coordinator',
        'technical': 'technical-architect',
        'architect': 'technical-architect',
        'pm': 'product-manager',
        'product-manager': 'product-manager',
        'ux': 'ux-designer',
        'ux-designer': 'ux-designer',
        'default': 'backend-agent'  # Default fallback
    }
    
    # Get mapped template name
    template_name = agent_mapping.get(agent_type, agent_type)
    
    # Handle case where agent_type already has .md extension
    if agent_type.endswith('.md'):
        base_agent_type = agent_type[:-3]  # Remove .md extension
        template_paths = [f"prompts/{agent_type}"]
    else:
        # Try different template path patterns, prioritizing direct agent_type
        template_paths = [
            f"prompts/{agent_type}.md",
            f"prompts/{template_name}.md",
            f"prompts/{agent_normalized}.md", 
            f"prompts/{agent_type}-agent.md",
            f"prompts/{agent_normalized}-agent.md",
            f"{agent_type}-prompts/{agent_type}.md",
            f"{agent_normalized}-prompts/{agent_normalized}.md"
        ]
    
    template_content = None
    for template_path in template_paths:
        try:
            template_content = load_prompt_template(template_path)
            break
        except FileNotFoundError:
            continue
    
    if template_content is None:
        raise FileNotFoundError(f"Prompt template not found for agent type: {agent_type}")
    
    # Get task context and metadata
    context = get_task_context(task_id)
    
    try:
        metadata = load_task_metadata(task_id)
    except FileNotFoundError:
        raise FileNotFoundError(f"Task metadata file not found for {task_id}")
    
    # Prepare template variables including context
    template_vars = metadata.copy()
    template_vars['context'] = context
    # Map 'description' to 'task_description' for backward compatibility
    if 'description' in template_vars:
        template_vars['task_description'] = template_vars['description']
    
    # Format the prompt
    prompt = format_prompt_with_context(
        template_content,
        context,
        template_vars
    )
    
    # Handle output path
    file_was_written = False
    if output_path is not None:
        # Explicitly provided output path
        output_file = Path(output_path)
        os.makedirs(output_file.parent, exist_ok=True)
        with open(str(output_file), 'w', encoding='utf-8') as f:
            f.write(prompt)
        file_was_written = True
    else:
        # No explicit output path - generate default and write file for internal use
        agent_name = agent_type.replace('-agent', '').replace('.md', '')
        default_path = f"outputs/{task_id}/prompt_{agent_name}.md"
        output_file = Path(default_path)
        os.makedirs(output_file.parent, exist_ok=True)
        with open(str(output_file), 'w', encoding='utf-8') as f:
            f.write(prompt)
        file_was_written = True
    
    # Return result dictionary
    return {
        'task_id': task_id,
        'agent_type': agent_type,
        'output_path': output_path,  # Returns None if not explicitly provided
        'prompt': prompt,
        'template_path': next((p for p in template_paths if Path(p).exists()), None)
    }


def main():
    """Main function for CLI."""
#     import sys  # Consolidated to common_imports

    if len(sys.argv) < 2:
        print("Error: Task ID is required")
        sys.exit(1)
        return  # For test compatibility when sys.exit is mocked
    
    # Check for pure named arguments (starts with --task or --agent)
    if len(sys.argv) > 1 and sys.argv[1].startswith('--'):
        import argparse
        parser = argparse.ArgumentParser(description='Generate prompt for task')
        parser.add_argument('--task', '-t', required=True, help='Task ID')
        parser.add_argument('--agent', '-a', default='default', help='Agent type')
        parser.add_argument('--output', '-o', help='Output file path')
        
        args = parser.parse_args()
        task_id = args.task
        agent_type = args.agent
        output_path = args.output
    else:
        # Handle positional arguments with optional --output flag
        task_id = sys.argv[1]
        agent_type = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "default"
        
        # Look for --output flag
        output_path = None
        if '--output' in sys.argv:
            output_idx = sys.argv.index('--output')
            if output_idx + 1 < len(sys.argv):
                output_path = sys.argv[output_idx + 1]
        elif len(sys.argv) > 3 and not sys.argv[3].startswith('--'):
            output_path = sys.argv[3]
    
    try:
        result = generate_prompt(task_id, agent_type, output_path)
        print(f"Generated prompt: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


__all__ = [
    "generate_prompt",
    "load_prompt_template",
    "load_task_metadata",
    "get_task_context",
    "format_prompt_with_context",
    "main",
]
