"""
Prompt Generator for Agent Tasks
Generates a prompt from an agent's template, injecting MCP context for a specific task.
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts.utils import load_and_format_prompt
from tools.memory_engine import get_relevant_context, get_context_by_keys
from utils.task_loader import load_task_metadata

def get_task_context(task_id):
    """
    Get MCP context for a specific task.
    
    Args:
        task_id: The task identifier (e.g. BE-07)
        
    Returns:
        Context relevant to the task from the MCP memory system
    """
    try:
        # Try to load task metadata from YAML
        task_metadata = load_task_metadata(task_id)
        
        # Step 3.5 Implementation: Use enhanced context_topics retrieval
        if 'context_topics' in task_metadata and task_metadata['context_topics']:
            # Use the new Step 3.5 focused context builder
            from tools.memory_engine import build_focused_context
            topic_context = build_focused_context(
                task_metadata['context_topics'], 
                max_tokens=2000,  # Token budget management
                max_per_topic=2   # Limit documents per topic
            )
            return topic_context
    except FileNotFoundError:
        # If no metadata file exists, fall back to the old method
        pass
    
    # Legacy approach - using vector search based on task prefix
    # Query to get task details first
    task_query = f"Details about task {task_id}"
    task_context = get_relevant_context(task_query)
    
    # Get additional context based on the task type
    if task_id.startswith("BE"):
        additional_context = get_relevant_context("Backend architecture and Supabase integration")
    elif task_id.startswith("FE"):
        additional_context = get_relevant_context("Frontend architecture and React components")
    elif task_id.startswith("TL"):
        additional_context = get_relevant_context("Technical architecture and system design")
    elif task_id.startswith("DOC"):
        additional_context = get_relevant_context("Documentation standards and requirements")
    elif task_id.startswith("QA"):
        additional_context = get_relevant_context("Testing frameworks and quality standards")
    else:
        additional_context = ""
    
    # Combine contexts, avoiding duplication
    full_context = f"{task_context}\n\n{additional_context}"
    
    return full_context

def generate_prompt(task_id, agent_id, output_path=None):
    """
    Generate a prompt for a specific task and agent.
    
    Args:
        task_id: The task identifier (e.g. BE-07)
        agent_id: The agent identifier (e.g. backend-agent)
        output_path: Optional path to save the generated prompt
        
    Returns:
        The generated prompt with MCP context injected
    """
    # Get the template path
    if not agent_id.endswith('.md'):
        agent_id = f"{agent_id}.md"
        
    prompt_template_path = f"prompts/{agent_id}"
    
    # Get context for the task
    context = get_task_context(task_id)
    
    # Try to get task metadata for additional template variables
    template_vars = {
        "context": context,
        "task_id": task_id
    }
    
    try:
        task_metadata = load_task_metadata(task_id)
        
        # Add metadata to template variables
        template_vars.update({
            "title": task_metadata.get('title', ''),
            "description": task_metadata.get('description', ''),
            "artefacts": ", ".join(task_metadata.get('artefacts', [])),
            "priority": task_metadata.get('priority', 'MEDIUM'),
            "estimation": task_metadata.get('estimation_hours', 0),
            "dependencies": ", ".join(task_metadata.get('depends_on', [])),
            "state": task_metadata.get('state', 'PLANNED')
        })
        
    except FileNotFoundError:
        # No additional template variables available
        pass
    
    # Format the prompt template with context and metadata
    filled_prompt = load_and_format_prompt(
        prompt_template_path,
        template_vars
    )
    
    # Create output directory if needed
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save to file if output path is provided
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(filled_prompt)
        print(f"Prompt saved to {output_path}")
    
    return filled_prompt

def main():
    """Command-line interface for generating agent prompts."""
    parser = argparse.ArgumentParser(description="Generate agent prompts with MCP context")
    
    parser.add_argument("--task", "-t", required=True, help="Task ID (e.g. BE-07)")
    parser.add_argument("--agent", "-a", required=True, help="Agent ID (e.g. backend-agent)")
    parser.add_argument("--output", "-o", help="Output file path (optional)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    try:
        if args.verbose:
            print(f"Generating prompt for task {args.task} with agent {args.agent}...")
            
            try:
                task_metadata = load_task_metadata(args.task)
                print(f"Task title: {task_metadata.get('title')}")
                print(f"Task description: {task_metadata.get('description')}")
                print(f"Context topics: {task_metadata.get('context_topics', [])}")
            except FileNotFoundError:
                print(f"No metadata file found for task {args.task}")
        
        prompt = generate_prompt(args.task, args.agent, args.output)
        
        if not args.output:
            print(prompt)
    
    except Exception as e:
        print(f"Error generating prompt: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()