#!/usr/bin/env python3
"""
Debug script to test memory engine context building
"""

import sys
from pathlib import Path

from tools.memory_engine import MemoryEngine

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_memory_engine():
    """Test memory engine context building"""
    print("🧠 Initializing memory engine...")
    memory_engine = MemoryEngine()

    # Test the same context topics from BE-07
    context_topics = ['db-schema', 'service-pattern', 'supabase-setup']

    print(f"🔍 Testing build_focused_context with topics: {context_topics}")

    context_content = memory_engine.build_focused_context(
        context_topics=context_topics,
        max_tokens=2000,
        max_per_topic=3,
        user="debug_test",
        task_id="DEBUG-01",
        agent_role="backend"
    )

    print(f"📊 Context Results:")
    print(f"   Content length: {len(context_content)} characters")
    print(f"   Content type: {type(context_content)}")
    print(f"   Is empty: {context_content == ''}")
    print(f"   Is None: {context_content is None}")

    if context_content:
        print(f"\n📖 Context Preview (first 500 chars):")
        print("─" * 50)
        print(context_content[:500])
        print("─" * 50)
    else:
        print("❌ Context content is empty or None!")

        # Try getting documents directly
        print("\n🔍 Testing get_documents method...")
        documents = memory_engine.get_documents(
            context_topics,
            max_per_topic=3,
            user="debug_test"
        )

        print(f"📊 Documents Retrieved:")
        print(f"   Number of documents: {len(documents)}")
        for i, doc in enumerate(documents[:3]):  # Show first 3
            print(
                f"   Doc {
                    i +
                    1}: {
                    doc.get(
                        'source',
                        'Unknown')} ({
                    len(
                        doc.get(
                            'content',
                            ''))} chars)")


if __name__ == "__main__":
    test_memory_engine()
