"""
Step 4.2 Implementation: Prompt Generation with Context

This script implements the Step 4.2 requirements for generating agent prompts with:
- Prompt template loading from prompts/[agent].md
- Task metadata loading from tasks/[task-id].yaml
- Context retrieval via MCP using context_topics
- Placeholder replacement for {context} and {task_description}
- Output saving to outputs/[task-id]/prompt_[agent].md

Usage:
    python orchestration/generate_prompt.py --task BE-07 --agent backend-agent
    python orchestration/generate_prompt.py BE-07 backend-agent --output outputs/BE-07/prompt_backend.md
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from prompts.utils import format_prompt_with_context, load_prompt_template
from tools.memory import get_memory_instance, MemoryEngine
from utils.task_loader import load_task_metadata

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_task_context(task_id: str) -> str:
    """
    Step 4.2: Get MCP context for a specific task using context_topics.

    Args:
        task_id: The task identifier (e.g. BE-07)

    Returns:
        Context relevant to the task from the MCP memory system
    """
    logger = logging.getLogger(__name__)

    try:
        # Load task metadata from YAML
        task_metadata = load_task_metadata(task_id)
        logger.info(
            f"Loaded task metadata for {task_id}: {
                task_metadata.get(
                    'title', 'Unknown')}")

        # Step 4.2: Use context_topics for focused context retrieval
        if 'context_topics' in task_metadata and task_metadata['context_topics']:
            logger.info(
                f"Building context using topics: {
                    task_metadata['context_topics']}")

            # Initialize memory engine for context retrieval
            memory_engine = get_memory_instance()

            # Build focused context using context_topics
            topic_context = memory_engine.build_focused_context(
                context_topics=task_metadata['context_topics'],
                max_tokens=2000,  # Token budget management
                max_per_topic=2,   # Limit documents per topic
                task_id=task_id,  # Enable Step 3.7 context tracking
                agent_role="system"  # Default agent role
            )

            logger.info(f"Generated context: {len(topic_context)} characters")
            return topic_context
        else:
            logger.warning(f"No context_topics found for task {task_id}")
            return f"No context_topics defined for task {task_id}. Please add context_topics to the task YAML file."

    except FileNotFoundError:
        logger.error(f"Task metadata file not found for {task_id}")
        return f"Task metadata not found for {task_id}. Please ensure tasks/{task_id}.yaml exists."
    except Exception as e:
        logger.error(f"Error retrieving context for task {task_id}: {e}")
        return f"Error retrieving context: {str(e)}"


def generate_prompt(task_id, agent_id, output_path=None):
    """
    Step 4.2: Generate a prompt for a specific task and agent.

    Implementation:
    - Loads prompt template: prompts/[agent].md
    - Loads task metadata from tasks/[task-id].yaml
    - Retrieves related memory via MCP
    - Replaces {context} and {task_description} placeholders
    - Saves prompt as: outputs/[task-id]/prompt_[agent].md

    Args:
        task_id: The task identifier (e.g. BE-07)
        agent_id: The agent identifier (e.g. backend-agent)
        output_path: Optional path to save the generated prompt

    Returns:
        The generated prompt with MCP context injected
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Generating prompt for task {task_id} with agent {agent_id}")

    # Step 4.2.1: Load prompt template
    if not agent_id.endswith('.md'):
        agent_id = f"{agent_id}.md"

    prompt_template_path = f"prompts/{agent_id}"

    try:
        prompt_template = load_prompt_template(prompt_template_path)
        logger.info(f"Loaded prompt template from {prompt_template_path}")
    except FileNotFoundError:
        logger.error(f"Prompt template not found: {prompt_template_path}")
        raise FileNotFoundError(
            f"Prompt template not found: {prompt_template_path}")

    # Step 4.2.2: Load task metadata
    try:
        task_metadata = load_task_metadata(task_id)
        logger.info(f"Loaded task metadata for {task_id}")
    except FileNotFoundError:
        logger.error(f"Task metadata not found for {task_id}")
        raise FileNotFoundError(
            f"Task metadata file not found: tasks/{task_id}.yaml")

    # Step 4.2.3: Retrieve context via MCP using context_topics
    context = get_task_context(task_id)

    # Step 4.2.4: Prepare variables for placeholder replacement
    template_vars = {
        "context": context,
        "task_description": task_metadata.get('description', ''),
        "task_id": task_id,
        "title": task_metadata.get('title', ''),
        # Use description as goal if no specific goal
        "goal": task_metadata.get('description', ''),
        "artefacts": "\n".join(f"- {artifact}" for artifact in task_metadata.get('artefacts', [])),
        "priority": task_metadata.get('priority', 'MEDIUM'),
        "estimation_hours": task_metadata.get('estimation_hours', 0),
        "dependencies": ", ".join(task_metadata.get('depends_on', [])),
        "state": task_metadata.get('state', 'PLANNED'),
        # Use artifacts as file references
        "file_references": ", ".join(task_metadata.get('artefacts', []))
    }

    # Step 4.2.5: Replace placeholders in prompt template
    filled_prompt = format_prompt_with_context(
        prompt_template,
        context,
        template_vars
    )

    # Step 4.2.6: Save prompt to outputs/[task-id]/prompt_[agent].md
    if not output_path:
        # Default output path as per Step 4.2 specification
        agent_name = agent_id.replace('.md', '').replace('-agent', '')
        output_path = f"outputs/{task_id}/prompt_{agent_name}.md"

    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(filled_prompt)

    logger.info(f"Prompt saved to {output_path}")
    print(f"✅ Step 4.2 Complete: Prompt generated and saved to {output_path}")

    return filled_prompt


def main():
    """
    Step 4.2 CLI: Command-line interface for generating agent prompts.

    Usage examples:
        python orchestration/generate_prompt.py --task BE-07 --agent backend-agent
        python orchestration/generate_prompt.py BE-07 backend-agent
        python orchestration/generate_prompt.py --task BE-07 --agent backend-agent --output custom/path.md
    """
    parser = argparse.ArgumentParser(
        description="Step 4.2: Generate agent prompts with MCP context",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with named arguments
  python orchestration/generate_prompt.py --task BE-07 --agent backend-agent

  # Positional arguments (task, agent)
  python orchestration/generate_prompt.py BE-07 backend-agent

  # Custom output path
  python orchestration/generate_prompt.py --task BE-07 --agent backend-agent --output custom/prompt.md

  # Verbose output showing context and metadata
  python orchestration/generate_prompt.py --task BE-07 --agent backend-agent --verbose
        """
    )

    # Positional arguments for convenience
    parser.add_argument("task_id", nargs="?", help="Task ID (e.g. BE-07)")
    parser.add_argument("agent_id", nargs="?",
                        help="Agent ID (e.g. backend-agent)")

    # Named arguments (alternative to positional)
    parser.add_argument(
        "--task", "-t", help="Task ID (alternative to positional argument)")
    parser.add_argument(
        "--agent", "-a", help="Agent ID (alternative to positional argument)")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (optional, defaults to outputs/[task]/prompt_[agent].md)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output with detailed logging")

    args = parser.parse_args()

    # Determine task and agent IDs
    task_id = args.task_id or args.task
    agent_id = args.agent_id or args.agent

    if not task_id:
        parser.error(
            "Task ID is required. Use --task or provide as first positional argument.")
    if not agent_id:
        parser.error(
            "Agent ID is required. Use --agent or provide as second positional argument.")

    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger = logging.getLogger(__name__)

    try:
        print(
            f"🔄 Step 4.2: Generating prompt for task {task_id} with agent {agent_id}...")

        if args.verbose:
            try:
                task_metadata = load_task_metadata(task_id)
                print(f"📋 Task title: {task_metadata.get('title')}")
                print(
                    f"📝 Task description: {task_metadata.get('description')}")
                print(
                    f"🏷️  Context topics: {
                        task_metadata.get(
                            'context_topics',
                            [])}")
                print(f"📦 Artifacts: {task_metadata.get('artefacts', [])}")
            except FileNotFoundError:
                print(f"⚠️  No metadata file found for task {task_id}")

        # Generate the prompt
        prompt = generate_prompt(task_id, agent_id, args.output)

        if args.verbose:
            print(f"\n📊 Generated prompt statistics:")
            print(f"   📏 Length: {len(prompt)} characters")
            print(f"   📄 Lines: {len(prompt.split(chr(10)))}")
            print(f"   🔤 Estimated tokens: ~{len(prompt) // 4}")

        if not args.output:
            print(f"\n📋 Generated prompt preview (first 500 characters):")
            print("─" * 60)
            print(prompt[:500] + ("..." if len(prompt) > 500 else ""))
            print("─" * 60)

    except Exception as e:
        logger.error(f"Error generating prompt: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        print(f"❌ Step 4.2 Failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
