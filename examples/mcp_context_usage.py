#!/usr/bin/env python3
"""
Usage Examples for MCP Context Integration

This script demonstrates how to use the enhanced memory-enabled agents
to execute tasks with contextual knowledge.
"""

import logging
import os
import sys

from agents import agent_builder
from agents.backend import build_backend_agent, get_backend_context
from agents.frontend import build_frontend_agent, get_frontend_context
from orchestration.inject_context import context_injector
from tools.memory_engine import memory

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_basic_context_retrieval():
    """Example 1: Basic context retrieval for different domains"""
    print("=== Example 1: Basic Context Retrieval ===")

    try:
        # Get backend-specific context
        backend_context = get_backend_context()
        print(f"Backend Context Length: {len(backend_context)} characters")
        print(f"Backend Context Preview: {backend_context[:200]}...")

        # Get frontend-specific context
        frontend_context = get_frontend_context()
        print(f"Frontend Context Length: {len(frontend_context)} characters")
        print(f"Frontend Context Preview: {frontend_context[:200]}...")

    except Exception as e:
        logger.error(f"Error in basic context retrieval: {e}")


def example_2_memory_enhanced_agent_creation():
    """Example 2: Creating memory-enhanced agents"""
    print("\n=== Example 2: Memory-Enhanced Agent Creation ===")

    try:
        # Sample task metadata
        task_metadata = {
            "id": "BE-07",
            "title": "Implement User Service Functions",
            "description": "Create Supabase service layer for user management",
            "context_topics": [
                "db-schema",
                "service-patterns",
                "user-management"],
            "owner": "backend_engineer",
            "dependencies": [
                "BE-01",
                "BE-02"],
            "priority": "HIGH"}

        # Create backend agent with context
        backend_agent = build_backend_agent(task_metadata=task_metadata)
        print(f"Backend Agent Created: {backend_agent.role}")
        print(f"Agent has context: {hasattr(backend_agent, '_context')}")
        print(
            f"Agent has memory retriever: {
                hasattr(
                    backend_agent,
                    '_memory_retriever')}")

        if hasattr(backend_agent, '_context'):
            context_length = len(backend_agent._context)
            print(f"Context Length: {context_length} characters")

    except Exception as e:
        logger.error(f"Error in agent creation: {e}")


def example_3_context_injector_usage():
    """Example 3: Using context injector for task execution"""
    print("\n=== Example 3: Context Injector Usage ===")

    try:
        # Prepare agent with context for specific task
        task_id = "BE-07"
        agent_role = "backend_engineer"

        # This would prepare an agent with all relevant context
        print(f"Preparing agent for task {task_id} with role {agent_role}")

        # Get context data without creating agent
        context_data = context_injector.inject_task_context(
            task_id, agent_role)

        if context_data:
            print("Context injection successful!")
            print(f"Task ID: {context_data.get('task_id')}")
            print(f"Agent Role: {context_data.get('agent_role')}")
            print(
                f"Context Length: {len(context_data.get('context', ''))} characters")
        else:
            print("Context injection failed - task metadata not found")

    except Exception as e:
        logger.error(f"Error in context injection: {e}")


def example_4_direct_memory_queries():
    """Example 4: Direct memory engine queries"""
    print("\n=== Example 4: Direct Memory Engine Queries ===")

    try:        # Query specific domains
        domains = ["db-schema", "service-patterns"]
        context = memory.get_context_by_domains(domains, max_results=3)
        print(f"Context for domains {domains}:")
        print(f"Length: {len(context)} characters")
        print(f"Preview: {context[:300]}...")

        # Query for specific task
        task_context = memory.retrieve_context_for_task(
            "BE-07",
            context_topics=["user-management", "authentication"],
            max_results=2
        )
        print(f"\nTask-specific context:")
        print(f"Length: {len(task_context)} characters")
        print(f"Preview: {task_context[:300]}...")

        # Get retriever for agent integration
        retriever = memory.get_retriever({"k": 5})
        print(f"\nRetriever created: {type(retriever)}")

    except Exception as e:
        logger.error(f"Error in direct memory queries: {e}")


def example_5_prompt_enhancement():
    """Example 5: Prompt enhancement with context"""
    print("\n=== Example 5: Prompt Enhancement ===")

    try:
        # Sample prompt template
        prompt_template = """# Backend Development Task

## Role
You are a backend developer specializing in Supabase implementations.

## Context
{context}

## Task
{task_description}

## Instructions
Use the provided context to implement the requested functionality.
Follow the established patterns and ensure proper error handling.
"""

        # Sample context
        context = """
## Database Schema
- users table with id, email, password_hash, created_at
- profiles table with user_id, name, avatar_url

## Service Patterns
- Use repository pattern for data access
- Implement service classes for business logic
- Return Result<T, Error> for error handling
"""

        # Sample task metadata
        task_metadata = {
            "id": "BE-07",
            "title": "User Service Implementation",
            "description": "Create user management service functions",
            "priority": "HIGH"
        }

        # Enhance prompt with context
        enhanced_prompt = agent_builder._enhance_prompt_with_context(
            prompt_template, context, task_metadata
        )

        print("Enhanced prompt created!")
        print(f"Length: {len(enhanced_prompt)} characters")
        print("=" * 50)
        print(enhanced_prompt[:500] + "...")

    except Exception as e:
        logger.error(f"Error in prompt enhancement: {e}")


def example_6_agent_comparison():
    """Example 6: Compare agents with and without context"""
    print("\n=== Example 6: Agent Comparison ===")

    try:
        # Task metadata
        task_metadata = {
            "id": "FE-03",
            "title": "Create Product Listing Component",
            "description": "Build a responsive product grid component",
            "context_topics": ["design-system", "component-patterns"],
            "owner": "frontend_engineer"
        }

        # Create agent with context
        agent_with_context = build_frontend_agent(task_metadata=task_metadata)

        # Create basic agent (would fall back to generic prompt)
        agent_basic = build_frontend_agent()

        print("Agent with context:")
        print(f"- Has context: {hasattr(agent_with_context, '_context')}")
        print(
            f"- Has memory retriever: {hasattr(agent_with_context, '_memory_retriever')}")

        print("\nBasic agent:")
        print(f"- Has context: {hasattr(agent_basic, '_context')}")
        print(
            f"- Has memory retriever: {hasattr(agent_basic, '_memory_retriever')}")

        if hasattr(
                agent_with_context,
                '_context') and hasattr(
                agent_basic,
                '_context'):
            context_diff = len(agent_with_context._context) - \
                len(agent_basic._context)
            print(f"\nContext difference: {context_diff} characters")

    except Exception as e:
        logger.error(f"Error in agent comparison: {e}")


def main():
    """Run all examples"""
    print("MCP Context Integration Usage Examples")
    print("=" * 50)

    # Initialize memory engine
    try:
        print("Initializing memory engine...")
        # The memory engine should auto-initialize
        print("Memory engine ready!")
    except Exception as e:
        logger.error(f"Failed to initialize memory engine: {e}")
        print("Some examples may not work without proper memory engine setup.")

    # Run examples
    example_1_basic_context_retrieval()
    example_2_memory_enhanced_agent_creation()
    example_3_context_injector_usage()
    example_4_direct_memory_queries()
    example_5_prompt_enhancement()
    example_6_agent_comparison()

    print("\n=== Examples Complete ===")
    print("To use in your own code:")
    print("1. Import the agent builders: from agents.backend import build_backend_agent")
    print("2. Create task metadata with context_topics")
    print("3. Build agents with task_metadata parameter")
    print("4. Access agent._context for the retrieved context")


if __name__ == "__main__":
    main()
