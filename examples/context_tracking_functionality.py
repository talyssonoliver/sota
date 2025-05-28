#!/usr/bin/env python3
"""
Step 3.7 Implementation Test and Validation

This script tests the context tracking functionality implemented in Step 3.7.
It validates that context usage is properly tracked and stored per task execution.

Usage:
    python examples/step_3_7_demo.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from tools.context_tracker import (analyze_context_usage,
                                   export_context_usage_report,
                                   get_context_log,
                                   track_context_from_memory_engine,
                                   track_context_usage)
from tools.memory_engine import MemoryEngine
from utils.task_loader import load_task_metadata

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_basic_context_tracking():
    """Test basic context tracking functionality"""
    print("=" * 60)
    print("STEP 3.7 TEST: Basic Context Tracking")
    print("=" * 60)

    task_id = "BE-07"
    context_topics = ["db-schema", "service-pattern", "supabase-setup"]

    # Simulate document usage
    mock_documents = [
        {
            "page_content": "# Database Schema\nThis is a test database schema...",
            "metadata": {
                "source": "context-store/db/schema.md",
                "topic": "db-schema",
                "query_used": "database schema",
                "retrieved_at": datetime.now().isoformat()
            }
        },
        {
            "page_content": "# Service Pattern\nThis describes the service layer pattern...",
            "metadata": {
                "source": "context-store/patterns/service-layer.md",
                "topic": "service-pattern",
                "query_used": "service pattern",
                "retrieved_at": datetime.now().isoformat()
            }
        }
    ]

    print(f"📋 Task: {task_id}")
    print(f"🏷️  Topics: {context_topics}")
    print(f"📄 Documents: {len(mock_documents)}")

    # Track context usage
    success = track_context_usage(
        task_id=task_id,
        context_topics=context_topics,
        documents_used=mock_documents,
        agent_role="backend",
        context_length=sum(len(doc["page_content"]) for doc in mock_documents)
    )

    print(f"✅ Context tracking successful: {success}")

    # Verify the log was created
    log_file = Path("outputs") / task_id / "context_log.json"
    if log_file.exists():
        print(f"✅ Context log created: {log_file}")

        # Load and display the log
        with open(log_file, 'r') as f:
            log_data = json.load(f)

        print("\n📊 Context Log Contents:")
        print(f"   Task: {log_data['task']}")
        print(f"   Context used: {log_data['context_used']}")
        print(f"   Agent role: {log_data['agent_role']}")
        print(f"   Documents retrieved: {log_data['documents_retrieved']}")
        print(f"   Context length: {log_data['context_length']}")
        print(f"   Timestamp: {log_data['timestamp']}")

        return True
    else:
        print(f"❌ Context log not found: {log_file}")
        return False


def test_memory_engine_integration():
    """Test integration with memory engine for automatic tracking"""
    print("\n" + "=" * 60)
    print("STEP 3.7 TEST: Memory Engine Integration")
    print("=" * 60)

    task_id = "BE-07"
    # Load real task metadata
    task_metadata = load_task_metadata(task_id)
    if not task_metadata:
        print(f"❌ Could not load task metadata for {task_id}")
        return False

    context_topics = task_metadata.get('context_topics', [])
    print(f"📋 Task: {task_id}")
    print(f"🏷️  Context Topics: {context_topics}")

    try:
        # Initialize memory engine instance
        memory = MemoryEngine()

        # Use the enhanced build_focused_context with tracking
        focused_context = memory.build_focused_context(
            context_topics=context_topics,
            max_tokens=2000,
            max_per_topic=2,
            user="system",
            task_id=task_id,  # Step 3.7: Enable tracking
            agent_role="backend"  # Step 3.7: Specify agent role
        )

        print(f"✅ Built focused context: {len(focused_context)} characters")
        print(f"🎯 Estimated tokens: ~{len(focused_context) // 4}")

        # Check if context log was created
        log_data = get_context_log(task_id)
        if log_data:
            print("✅ Context tracking integration successful!")
            print(f"   Topics tracked: {log_data['context_used']}")
            print(f"   Documents tracked: {log_data['documents_retrieved']}")
            print(
                f"   Within budget: {
                    log_data.get(
                        'within_budget',
                        'unknown')}")
            print(
                f"   Step 3.5 integration: {
                    log_data.get(
                        'step_3_5_integration',
                        False)}")
            return True
        else:
            print("⚠️  Context log not found - tracking may not be fully integrated")
            return False

    except Exception as e:
        print(f"❌ Memory engine integration test failed: {e}")
        return False


def test_context_analysis():
    """Test context usage analysis functionality"""
    print("\n" + "=" * 60)
    print("STEP 3.7 TEST: Context Usage Analysis")
    print("=" * 60)

    # Create a few more sample logs for analysis
    sample_tasks = ["TL-01", "FE-02", "QA-01"]
    sample_topics = [
        ["technical-architecture", "setup-patterns"],
        ["frontend-patterns", "component-design"],
        ["testing-patterns", "quality-standards"]
    ]

    for i, task_id in enumerate(sample_tasks):
        topics = sample_topics[i]
        mock_docs = [
            {
                "page_content": f"Sample content for {topic}",
                "metadata": {
                    "source": f"context-store/{topic.split('-')[0]}/{topic}.md",
                    "topic": topic,
                    "query_used": topic.replace('-', ' '),
                    "retrieved_at": datetime.now().isoformat()
                }
            } for topic in topics
        ]

        track_context_usage(
            task_id=task_id,
            context_topics=topics,
            documents_used=mock_docs,
            agent_role=task_id.split('-')[0].lower(),
            context_length=sum(len(doc["page_content"]) for doc in mock_docs)
        )

    # Analyze context usage
    analysis = analyze_context_usage()

    print("📊 Context Usage Analysis:")
    print(f"   Total tasks analyzed: {analysis['total_tasks_analyzed']}")
    print(f"   Topic usage frequency: {analysis['topic_usage_frequency']}")
    print(f"   Most used topics: {analysis['most_used_topics']}")
    print(f"   Agent usage: {analysis['agent_usage_frequency']}")

    return analysis['total_tasks_analyzed'] > 0


def test_report_generation():
    """Test context usage report generation"""
    print("\n" + "=" * 60)
    print("STEP 3.7 TEST: Report Generation")
    print("=" * 60)

    # Generate report
    report_path = "reports/step_3_7_context_usage_report.json"
    success = export_context_usage_report(report_path)

    if success:
        print(f"✅ Context usage report generated: {report_path}")

        # Load and display summary
        with open(report_path, 'r') as f:
            report = json.load(f)

        print("📋 Report Summary:")
        summary = report.get('summary', {})
        print(f"   Tasks analyzed: {summary.get('total_tasks_analyzed', 0)}")
        print(
            f"   Unique topics: {len(summary.get('topic_usage_frequency', {}))}")
        print(
            f"   Unique documents: {len(summary.get('document_usage_frequency', {}))}")
        print(f"   Generated at: {report.get('generated_at', 'unknown')}")

        return True
    else:
        print(f"❌ Failed to generate report at {report_path}")
        return False


def validate_step_3_7_complete():
    """Validate that Step 3.7 implementation meets all requirements"""
    print("\n" + "=" * 60)
    print("STEP 3.7 VALIDATION: Complete Implementation Check")
    print("=" * 60)

    requirements = [
        ("Basic context tracking functionality", test_basic_context_tracking),
        ("Memory engine integration", test_memory_engine_integration),
        ("Context usage analysis", test_context_analysis),
        ("Report generation", test_report_generation)
    ]

    results = []
    for name, test_func in requirements:
        try:
            result = test_func()
            results.append((name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {name}")
        except Exception as e:
            results.append((name, False))
            print(f"❌ ERROR: {name} - {e}")

    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\n📊 STEP 3.7 VALIDATION SUMMARY:")
    print(f"   Tests passed: {passed}/{total}")
    print(f"   Success rate: {(passed / total) * 100:.1f}%")

    if passed == total:
        print("🎉 Step 3.7 implementation is COMPLETE and functional!")
        return True
    else:
        print("⚠️  Step 3.7 implementation needs attention.")
        return False


def main():
    """Run all Step 3.7 tests and validation"""
    print("🚀 Starting Step 3.7 Implementation Test Suite")
    print("Context Tracking per Task - Validation and Demo")
    print("=" * 80)

    success = validate_step_3_7_complete()

    if success:
        print("\n✅ Step 3.7 'Context Tracking per Task' is fully implemented!")
        print(
            "📁 Context logs are stored under outputs/[TASK-ID]/context_log.json")
        print("📊 Analysis and reporting tools are available via context_tracker.py")
        print("🔗 Integration with memory engine enables automatic tracking")
    else:
        print("\n❌ Step 3.7 implementation requires fixes")

    return success


if __name__ == "__main__":
    main()
