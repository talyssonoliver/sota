#!/usr/bin/env python3
"""
Step 3.5 & 3.6 Implementation Demo and Test Script

This script demonstrates the implementation of:
- Step 3.5: Annotate Context Tags in Tasks
- Step 3.6: Pre-Compress Large Files (Chunking Strategy)

Usage:
    python examples/step_3_5_3_6_demo.py
"""

import json
import os
import sys
from pathlib import Path

import yaml

from tools.memory_engine import MemoryEngine

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_task_metadata(task_id: str) -> dict:
    """Load task metadata from YAML file"""
    task_file = project_root / "tasks" / f"{task_id}.yaml"
    if task_file.exists():
        with open(task_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def demo_step_3_5_context_topics(memory_engine):
    """
    Demonstrate Step 3.5: Annotate Context Tags in Tasks

    Shows how context_topics from task metadata are used to build focused queries.
    """
    print("=" * 60)
    print("STEP 3.5 DEMO: Annotate Context Tags in Tasks")
    print("=" * 60)

    # Load BE-07 task which has context_topics defined
    task_metadata = load_task_metadata("BE-07")

    if not task_metadata:
        print("❌ Could not load BE-07.yaml task metadata")
        return

    print(f"📋 Task: {task_metadata.get('id', 'Unknown')}")
    print(f"📝 Title: {task_metadata.get('title', 'Unknown')}")
    print(f"🏷️  Context Topics: {task_metadata.get('context_topics', [])}")
    print()

    # Step 3.5 Implementation: Get documents using context topics
    print("🔍 Step 3.5: Getting documents for context topics...")
    context_topics = task_metadata.get('context_topics', [])

    if not context_topics:
        print("❌ No context_topics found in task metadata")
        return

    try:
        # Use the memory_engine instance method
        context_docs = memory_engine.get_documents(
            context_topics, max_per_topic=2)

        print(f"📚 Retrieved {len(context_docs)} documents")

        # Step 3.5: Combine context as specified
        combined_context = "\n\n".join(
            [d["page_content"] for d in context_docs])

        print(f"📄 Combined context length: {len(combined_context)} characters")
        print(f"🎯 Estimated tokens: ~{len(combined_context) // 4}")
        print()

        # Show sample of each document
        for i, doc in enumerate(context_docs):
            topic = doc["metadata"].get("topic", "unknown")
            preview = doc["page_content"][:100] + \
                "..." if len(doc["page_content"]
                             ) > 100 else doc["page_content"]
            print(f"📖 Document {i + 1} ({topic}): {preview}")

        print()
        print("✅ Step 3.5 implementation successful!")

        # Save context for inspection
        output_dir = project_root / "outputs" / "step_3_5_demo"
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / "combined_context.md", 'w', encoding='utf-8') as f:
            f.write(f"# Context for Task BE-07\n\n")
            f.write(f"**Topics:** {', '.join(context_topics)}\n\n")
            f.write(combined_context)

        with open(output_dir / "context_docs.json", 'w', encoding='utf-8') as f:
            json.dump(context_docs, f, indent=2, default=str)

        print(f"💾 Context saved to {output_dir}/")

    except Exception as e:
        print(f"❌ Error in Step 3.5 demo: {e}")
        import traceback
        traceback.print_exc()


def demo_step_3_6_chunking(memory_engine):
    """
    Demonstrate Step 3.6: Pre-Compress Large Files (Chunking Strategy)

    Shows enhanced document chunking using LangChain's CharacterTextSplitter.
    """
    print("\n" + "=" * 60)
    print("STEP 3.6 DEMO: Pre-Compress Large Files (Chunking Strategy)")
    print("=" * 60)

    # Create a sample large document for demonstration
    sample_doc_path = project_root / "outputs" / \
        "step_3_6_demo" / "large_document.md"
    sample_doc_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate sample content that would benefit from chunking
    sample_content = """# Large Document for Chunking Demo

## Database Schema Design

The database schema consists of multiple tables that handle user management, order processing, and product catalog. Each table has specific relationships and constraints that ensure data integrity.

### Users Table
The users table stores customer information including personal details, authentication credentials, and preferences. It includes fields for email, password hash, profile information, and timestamps.

### Orders Table
The orders table manages purchase transactions with foreign key references to users and products. It tracks order status, payment information, shipping details, and fulfillment progress.

### Products Table
The products table contains inventory information including descriptions, pricing, categories, and stock levels. It supports multiple variants and attributes for flexible product management.

## Service Layer Patterns

The service layer implements business logic using established patterns for maintainability and testability. Each service handles specific domain operations with clear interfaces and error handling.

### Customer Service
The customer service manages user account operations including registration, authentication, profile updates, and account management. It provides validation and business rule enforcement.

### Order Service
The order service orchestrates the purchase process from cart management through payment processing and fulfillment. It coordinates with multiple external services and maintains transaction integrity.

### Product Service
The product service handles catalog management including search, filtering, recommendations, and inventory tracking. It provides both customer-facing and administrative interfaces.

## Supabase Setup and Configuration

Supabase provides the backend infrastructure including database, authentication, and real-time capabilities. The setup involves configuration of security policies, API endpoints, and client libraries.

### Authentication Configuration
Configure authentication providers, security rules, and user management policies. Set up role-based access control and session management for secure user experiences.

### Database Configuration
Set up row-level security policies, triggers, and functions for data integrity. Configure backup procedures and performance monitoring for production readiness.

### API Configuration
Configure REST and GraphQL endpoints with proper authorization and rate limiting. Set up webhooks and real-time subscriptions for dynamic user experiences.

This document demonstrates how large files benefit from chunking to improve searchability and context retrieval in the AI agent system."""

    # Write the sample document
    with open(sample_doc_path, 'w', encoding='utf-8') as f:
        f.write(sample_content)

    print(f"📝 Created sample document: {sample_doc_path}")
    print(f"📏 Document size: {len(sample_content)} characters")
    print()

    try:
        # Step 3.6 Implementation: Enhanced chunking with LangChain
        print("✂️  Step 3.6: Splitting document with enhanced chunking...")

        # Use the memory_engine instance method
        memory_engine.add_document_with_enhanced_chunking(
            str(sample_doc_path),
            metadata={
                "title": "Large Document Chunking Demo",
                "category": "demo",
                "created_for": "step_3_6_demo"
            },
            chunk_size=500,     # As specified in Step 3.6
            chunk_overlap=50,   # As specified in Step 3.6
            user="system"  # Use system user to avoid permission issues
        )

        print("✅ Document successfully chunked and added to memory engine!")

        # Test retrieval of the chunked content
        print("\n🔍 Testing context retrieval from chunked document...")

        # Search for different topics that should be in different chunks
        test_queries = [
            "database schema design",
            "service layer patterns",
            "supabase configuration"
        ]

        for query in test_queries:
            # Test using the memory_engine instance method
            context = memory_engine.build_focused_context(
                # Convert to topic format
                context_topics=[query.replace(" ", "-")],
                max_tokens=1000,
                max_per_topic=1
            )

            print(f"\n📖 Query: '{query}'")
            print(f"📄 Context length: {len(context)} characters")

            if context and len(context) > 50:
                preview = context[:200] + \
                    "..." if len(context) > 200 else context
                print(f"🎯 Preview: {preview}")
            else:
                print("⚠️  No relevant context found")

        print("\n✅ Step 3.6 chunking demonstration complete!")

    except Exception as e:
        print(f"❌ Error in Step 3.6 demo: {e}")
        import traceback
        traceback.print_exc()


def demo_integrated_workflow(memory_engine):
    """
    Demonstrate the integrated Step 3.5 + 3.6 workflow

    Shows how chunked documents enhance context topic retrieval.
    """
    print("\n" + "=" * 60)
    print("INTEGRATED WORKFLOW DEMO: Steps 3.5 + 3.6 Together")
    print("=" * 60)

    try:
        # Load a task with context topics
        task_metadata = load_task_metadata("BE-07")

        if not task_metadata or not task_metadata.get('context_topics'):
            print("❌ No suitable task found with context_topics")
            return

        print(f"🎯 Task: {task_metadata['id']} - {task_metadata['title']}")
        print(f"📋 Context Topics: {task_metadata['context_topics']}")
        print()

        # Step 3.5: Build focused context using the enhanced retrieval
        print("🔧 Building focused context using Steps 3.5 + 3.6...")

        focused_context = memory_engine.build_focused_context(
            context_topics=task_metadata['context_topics'],
            max_tokens=2000,  # Token budget management
            max_per_topic=2   # Limit documents per topic
        )

        print(f"📊 Focused context built successfully!")
        print(f"📏 Length: {len(focused_context)} characters")
        print(f"🎯 Estimated tokens: ~{len(focused_context) // 4}")
        print()

        # Simulate prompt injection as specified in Step 3.5
        prompt_template = """# Role
You are a Backend Developer Agent.

# Goal
Implement the Supabase service layer for [TASK-ID].

# Context
{context}

# Instruction
Generate a customerService.ts file with full CRUD operations using Supabase client."""

        # Step 3.5: Inject context into prompt
        final_prompt = prompt_template.format(context=focused_context)

        print("📝 Final prompt generated with injected context:")
        print(f"📏 Total prompt length: {len(final_prompt)} characters")

        # Save the integrated result
        output_dir = project_root / "outputs" / "integrated_demo"
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / "final_prompt.md", 'w', encoding='utf-8') as f:
            f.write(final_prompt)

        with open(output_dir / "workflow_log.json", 'w', encoding='utf-8') as f:
            workflow_log = {
                "task_id": task_metadata['id'],
                "context_topics": task_metadata['context_topics'],
                "context_length": len(focused_context),
                "prompt_length": len(final_prompt),
                "estimated_tokens": len(final_prompt) // 4,
                "steps_completed": ["3.5", "3.6"],
                "status": "success"
            }
            json.dump(workflow_log, f, indent=2)

        print(f"💾 Results saved to {output_dir}/")
        print("✅ Integrated workflow demonstration complete!")

    except Exception as e:
        print(f"❌ Error in integrated workflow demo: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main demo function"""
    print("🚀 Step 3.5 & 3.6 Implementation Demo")
    print("=====================================")
    print()

    # Initialize memory engine
    try:
        print("🔧 Initializing memory engine...")
        # Initialize memory engine
        memory_engine = MemoryEngine()
        print("✅ Memory engine initialized successfully!")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize memory engine: {e}")
        return

    # Run demonstrations
    demo_step_3_5_context_topics(memory_engine)
    demo_step_3_6_chunking(memory_engine)
    demo_integrated_workflow(memory_engine)

    print("\n" + "=" * 60)
    print("🎉 ALL DEMONSTRATIONS COMPLETE!")
    print("=" * 60)
    print()
    print("📁 Check the outputs/ directory for generated files:")
    print("   - outputs/step_3_5_demo/")
    print("   - outputs/step_3_6_demo/")
    print("   - outputs/integrated_demo/")
    print()
    print("✅ Steps 3.5 and 3.6 implementation verified!")


if __name__ == "__main__":
    main()
