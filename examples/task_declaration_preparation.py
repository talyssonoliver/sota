#!/usr/bin/env python3
"""
Step 4.1 Implementation Demo: Task Declaration & Preparation

This script demonstrates the complete Step 4.1 workflow for transforming 
task plans into live executions using defined agents, prompts, and memory context.

The demo shows:
1. Task declaration with full metadata registration
2. Context loading based on context_topics
3. Prompt generation with task metadata and memory context
4. Dependency validation
5. LangGraph execution plan creation

Usage:
    python examples/step_4_1_demo.py [--task-id BE-07] [--verbose]
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from orchestration.task_declaration import TaskDeclarationManager, TaskPreparationStatus
from tools.memory_engine import MemoryEngine
import logging

def setup_logging(verbose: bool = False):
    """Set up logging configuration"""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def print_section_header(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_task_declaration(manager: TaskDeclarationManager, task_id: str = "BE-07"):
    """Demonstrate task declaration functionality"""
    print_section_header("STEP 4.1 DEMO: Task Declaration & Preparation")
    
    print(f"🎯 Demonstrating with task: {task_id}")
    print(f"📅 Demo started at: {datetime.now().isoformat()}")
    
    # Step 1: Task Declaration
    print_subsection("Step 1: Task Declaration")
    
    try:
        declaration = manager.declare_task(task_id)
        
        print(f"✅ Task {task_id} successfully declared")
        print(f"   📝 Title: {declaration.title}")
        print(f"   👤 Owner: {declaration.owner}")
        print(f"   📊 State: {declaration.state}")
        print(f"   ⚡ Priority: {declaration.priority}")
        print(f"   ⏱️  Estimated Hours: {declaration.estimation_hours}")
        print(f"   📦 Dependencies: {', '.join(declaration.depends_on) if declaration.depends_on else 'None'}")
        print(f"   📄 Artifacts: {len(declaration.artefacts)} items")
        print(f"   🏷️  Context Topics: {', '.join(declaration.context_topics)}")
        
        return declaration
        
    except Exception as e:
        print(f"❌ Error declaring task {task_id}: {e}")
        return None

def demo_task_preparation(manager: TaskDeclarationManager, task_id: str = "BE-07"):
    """Demonstrate complete task preparation"""
    print_subsection("Step 2: Complete Task Preparation")
    
    try:
        declaration = manager.prepare_task_for_execution(task_id)
        
        print(f"⚙️  Task preparation completed with status: {declaration.preparation_status}")
        
        # Show preparation details
        print(f"   🔍 Context Loaded: {'✅' if declaration.context_loaded else '❌'}")
        print(f"   📝 Prompt Generated: {'✅' if declaration.prompt_generated else '❌'}")
        print(f"   🔗 Dependencies Satisfied: {'✅' if declaration.dependencies_satisfied else '❌'}")
        
        if declaration.context_content:
            context_length = len(declaration.context_content)
            print(f"   📊 Context Length: {context_length} characters")
        
        if declaration.agent_assignment:
            print(f"   🤖 Agent Assignment: {declaration.agent_assignment}")
        
        # Show execution plan if available
        if declaration.execution_plan:
            plan = declaration.execution_plan
            print(f"   🎯 Entry Point: {plan.get('entry_point')}")
            print(f"   🔄 Workflow Type: {plan.get('workflow_type')}")
            print(f"   ⏰ Timeout: {plan.get('timeout_minutes')} minutes")
            print(f"   🔁 Retry Count: {plan.get('retry_count')}")
        
        return declaration
        
    except Exception as e:
        print(f"❌ Error preparing task {task_id}: {e}")
        return None

def demo_context_analysis(declaration):
    """Demonstrate context analysis and content preview"""
    if not declaration or not declaration.context_content:
        print("⚠️  No context content available for analysis")
        return
    
    print_subsection("Step 3: Context Analysis")
    
    context = declaration.context_content
    lines = context.split('\n')
    
    print(f"📊 Context Statistics:")
    print(f"   Total lines: {len(lines)}")
    print(f"   Total characters: {len(context)}")
    print(f"   Estimated tokens: ~{len(context) // 4}")
    
    # Show context preview
    print(f"\n📖 Context Preview (first 500 characters):")
    print("─" * 50)
    print(context[:500] + ("..." if len(context) > 500 else ""))
    print("─" * 50)

def demo_prompt_analysis(declaration):
    """Demonstrate prompt analysis and content preview"""
    if not declaration or not declaration.generated_prompt:
        print("⚠️  No generated prompt available for analysis")
        return
    
    print_subsection("Step 4: Generated Prompt Analysis")
    
    prompt = declaration.generated_prompt
    lines = prompt.split('\n')
    
    print(f"📊 Prompt Statistics:")
    print(f"   Total lines: {len(lines)}")
    print(f"   Total characters: {len(prompt)}")
    print(f"   Estimated tokens: ~{len(prompt) // 4}")
    
    # Show prompt preview
    print(f"\n📝 Prompt Preview (first 800 characters):")
    print("─" * 50)
    print(prompt[:800] + ("..." if len(prompt) > 800 else ""))
    print("─" * 50)

def demo_execution_readiness(declaration):
    """Demonstrate execution readiness check"""
    print_subsection("Step 5: Execution Readiness Check")
    
    if not declaration:
        print("❌ No declaration available")
        return False
    
    ready = declaration.preparation_status == TaskPreparationStatus.READY_FOR_EXECUTION
    
    print(f"🎯 Task {declaration.id} execution readiness: {'✅ READY' if ready else '❌ NOT READY'}")
    
    if ready:
        print("🚀 Task is fully prepared for LangGraph execution!")
        print("   The following components are ready:")
        print("   ✓ Task metadata registered")
        print("   ✓ Context loaded and enriched")
        print("   ✓ Prompt generated with full context")
        print("   ✓ Dependencies validated")
        print("   ✓ Execution plan created")
        print("   ✓ Agent assignment completed")
        
        if declaration.execution_plan:
            print(f"\n🎮 Ready to execute with:")
            print(f"   Entry point: {declaration.execution_plan['entry_point']}")
            print(f"   Workflow: {declaration.execution_plan['workflow_type']}")
    else:
        print("⚠️  Task preparation incomplete:")
        if not declaration.context_loaded:
            print("   ❌ Context not loaded")
        if not declaration.prompt_generated:
            print("   ❌ Prompt not generated")
        if not declaration.dependencies_satisfied:
            print("   ❌ Dependencies not satisfied")
    
    return ready

def demo_batch_processing(manager: TaskDeclarationManager):
    """Demonstrate batch processing of multiple tasks"""
    print_section_header("BATCH PROCESSING DEMO")
    
    print("🔄 Processing all available tasks...")
    
    # Declare all tasks
    declarations = manager.declare_all_tasks()
    print(f"📝 Declared {len(declarations)} tasks")
    
    # Show declaration summary
    for task_id, declaration in declarations.items():
        status_icon = "✅" if declaration.preparation_status != TaskPreparationStatus.FAILED else "❌"
        print(f"   {status_icon} {task_id}: {declaration.title[:50]}...")
    
    # Prepare all tasks
    print("\n⚙️  Preparing all tasks for execution...")
    prepared = manager.prepare_all_tasks()
    
    # Show preparation summary
    summary = manager.get_preparation_summary()
    print(f"\n📊 Preparation Summary:")
    print(f"   Total tasks: {summary['total_tasks']}")
    print(f"   Ready for execution: {summary['ready_for_execution']}")
    print(f"   Failed preparation: {summary['failed_preparation']}")
    
    # Show status breakdown
    if "status_breakdown" in summary:
        print("\n📈 Status breakdown:")
        for status, count in summary["status_breakdown"].items():
            print(f"   {status}: {count}")
    
    return summary

def demo_file_outputs(task_id: str = "BE-07"):
    """Demonstrate the file outputs created during preparation"""
    print_subsection("Step 6: Generated File Outputs")
    
    outputs_dir = Path("outputs") / task_id
    
    if not outputs_dir.exists():
        print(f"⚠️  No outputs directory found for task {task_id}")
        return
    
    print(f"📁 Output directory: {outputs_dir}")
    
    # List all files created
    files = list(outputs_dir.glob("*"))
    if files:
        print(f"📄 Generated files ({len(files)}):")
        for file_path in sorted(files):
            size = file_path.stat().st_size if file_path.is_file() else 0
            print(f"   📝 {file_path.name} ({size} bytes)")
    else:
        print("   No files generated yet")
    
    # Show content of key files
    key_files = ["task_declaration.json", "prompt_backend.md", "context_log.json"]
    
    for filename in key_files:
        file_path = outputs_dir / filename
        if file_path.exists():
            print(f"\n📖 Content preview: {filename}")
            print("─" * 30)
            try:
                content = file_path.read_text(encoding='utf-8')
                preview = content[:300] + ("..." if len(content) > 300 else "")
                print(preview)
            except Exception as e:
                print(f"   Error reading file: {e}")
            print("─" * 30)

def main():
    """Main demo function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Step 4.1 Task Declaration & Preparation Demo")
    parser.add_argument("--task-id", "-t", default="BE-07", help="Task ID to demonstrate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--batch", "-b", action="store_true", help="Run batch processing demo")
    parser.add_argument("--skip-memory", action="store_true", help="Skip memory engine initialization")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    try:
        # Initialize memory engine unless skipped
        if not args.skip_memory:
            print("🧠 Initializing memory engine...")
            memory_engine = MemoryEngine()
        else:
            print("⚠️  Skipping memory engine initialization")
            memory_engine = None
        
        # Initialize task declaration manager
        print("⚙️  Initializing Task Declaration Manager...")
        manager = TaskDeclarationManager(memory_engine=memory_engine)
        
        if args.batch:
            # Run batch processing demo
            demo_batch_processing(manager)
        else:
            # Run single task demo
            # Step 1: Declare task
            declaration = demo_task_declaration(manager, args.task_id)
            
            if declaration:
                # Step 2: Prepare task
                declaration = demo_task_preparation(manager, args.task_id)
                
                if declaration:
                    # Step 3: Analyze context
                    demo_context_analysis(declaration)
                    
                    # Step 4: Analyze prompt
                    demo_prompt_analysis(declaration)
                    
                    # Step 5: Check execution readiness
                    ready = demo_execution_readiness(declaration)
                    
                    # Step 6: Show file outputs
                    demo_file_outputs(args.task_id)
                    
                    # Final summary
                    print_section_header("DEMO COMPLETED")
                    if ready:
                        print("🎉 SUCCESS: Task is fully prepared for LangGraph execution!")
                        print(f"✨ Task {args.task_id} is now ready to be executed through the workflow.")
                    else:
                        print("⚠️  Task preparation completed with issues.")
                        print("🔧 Review the preparation steps and resolve any problems before execution.")
        
        print(f"\n📅 Demo completed at: {datetime.now().isoformat()}")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
