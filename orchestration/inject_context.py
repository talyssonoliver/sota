"""
MCP Context Injection Utility
Injects relevant context from MCP memory into existing prompts or templates.
Enhanced version with agent integration support.
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.memory_engine import get_relevant_context
from utils.task_loader import load_task_metadata

memory = None

class ContextInjector:
    """Handles context injection for task execution"""
    
    def __init__(self):
        # Import here to avoid circular imports
        from agents import agent_builder
        self.agent_builder = agent_builder
        self.logger = logging.getLogger(__name__)

    def inject_task_context(self, task_id: str, agent_role: str) -> Dict[str, Any]:
        """Inject context for specific task and agent"""
        try:
            # Load task metadata
            task_metadata = load_task_metadata(task_id)
            
            # Get context for agent role and task
            context = self.agent_builder._get_context_for_agent(agent_role, task_metadata)
            
            return {
                "task_metadata": task_metadata,
                "context": context,
                "agent_role": agent_role,
                "task_id": task_id
            }
        except Exception as e:
            self.logger.error(f"Failed to inject context for task {task_id}: {e}")
            return {}

    def prepare_agent_with_context(self, agent_or_task, task_metadata=None):
        """Prepare agent with injected context. Accepts agent instance or task id."""
        # If agent_or_task is a string, treat as task_id
        if isinstance(agent_or_task, str):
            task_id = agent_or_task
            if task_metadata is None or not isinstance(task_metadata, dict):
                task_metadata = load_task_metadata(task_id)
            agent_role = task_metadata.get("role") or task_metadata.get("owner") or "coordinator"
            return self.agent_builder.build_agent(role=agent_role, task_metadata=task_metadata)
        # If agent_or_task is an agent instance, inject context
        else:
            # Fallback: just return the agent
            return agent_or_task

# Global context injector
context_injector = ContextInjector()

def inject_context(prompt, query, position="top", marker="{{CONTEXT}}"):
    """
    Injects context from MCP memory into a prompt.
    
    Args:
        prompt: The original prompt text
        query: The query to use for retrieving context
        position: Where to insert context - 'top', 'bottom', or 'marker'
        marker: Marker to replace with context if position is 'marker'
        
    Returns:
        Prompt with context injected
    """
    # Get context from memory engine
    context = get_relevant_context(query)
    
    formatted_context = f"\n\n--- RELEVANT CONTEXT ---\n\n{context}\n\n--- END CONTEXT ---\n\n"
    
    if position == "marker" and marker in prompt:
        # Replace the marker with context
        result = prompt.replace(marker, formatted_context)
    elif position == "bottom":
        # Append context at the end
        result = f"{prompt}\n\n{formatted_context}"
    else:
        # Default: Insert at the top
        result = f"{formatted_context}{prompt}"
    
    return result

def inject_file_context(input_file, output_file, query, position="top", marker="{{CONTEXT}}"):
    """
    Reads a file, injects context, and writes to a new file.
    
    Args:
        input_file: Path to the input prompt file
        output_file: Path to write the output prompt with context
        query: Query to retrieve relevant context
        position: Where to insert context
        marker: Marker to replace with context if position is 'marker'
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    result = inject_context(prompt, query, position, marker)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"Context injected and saved to {output_file}")

def main():
    """Command-line interface for injecting context into prompts."""
    parser = argparse.ArgumentParser(description="Inject MCP context into prompts")
    
    parser.add_argument("--query", "-q", required=True, help="Context query")
    parser.add_argument("--input", "-i", help="Input prompt file (optional)")
    parser.add_argument("--output", "-o", help="Output file path (required if input is provided)")
    parser.add_argument("--position", "-p", choices=["top", "bottom", "marker"], 
                      default="top", help="Position to insert context")
    parser.add_argument("--marker", "-m", default="{{CONTEXT}}", 
                      help="Marker to replace with context when using 'marker' position")
    parser.add_argument("--text", "-t", help="Direct prompt text to inject context into (alternative to file)")
    
    args = parser.parse_args()
    
    try:
        if args.input:
            if not args.output:
                print("Error: --output is required when using --input", file=sys.stderr)
                sys.exit(1)
                
            inject_file_context(args.input, args.output, args.query, args.position, args.marker)
        
        elif args.text:
            result = inject_context(args.text, args.query, args.position, args.marker)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"Context injected and saved to {args.output}")
            else:
                print(result)
        
        else:
            print("Error: Either --input or --text must be provided", file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        print(f"Error injecting context: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()