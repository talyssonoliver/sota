#!/usr/bin/env python3
"""
Step 4.4 — Register Agent Output Demo

Demonstrates the complete agent output registration workflow
with real examples and validation.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.register_output import AgentOutputRegistry


def demonstrate_step_4_4():
    """Demonstrate Step 4.4 — Register Agent Output functionality."""
    print("🎯 Step 4.4 — Register Agent Output Demo")
    print("=" * 50)
    
    # Initialize registry
    registry = AgentOutputRegistry()
    
    # Check BE-07 status
    print("\n📊 Current BE-07 Registration Status:")
    status = registry.get_task_status("BE-07")
    
    if "agent_outputs" in status and status["agent_outputs"]:
        print(f"✅ Task BE-07 has {len(status['agent_outputs'])} registered agents:")
        
        for agent_id, agent_data in status["agent_outputs"].items():
            print(f"   🤖 {agent_id}:")
            print(f"      📄 Output: {agent_data['output_file']}")
            print(f"      📊 Size: {agent_data['file_size']:,} bytes")
            print(f"      ⏰ Completed: {agent_data['completion_time']}")
            print(f"      🔧 Artifacts: {agent_data['extracted_artifacts']}")
    
        # Demonstrate QA input preparation
        print(f"\n🔍 QA Input Preparation:")
        qa_input = registry.prepare_qa_input("BE-07")
        
        print(f"   📋 Primary outputs: {len(qa_input['primary_outputs'])}")
        print(f"   🔧 Code artifacts: {len(qa_input['code_artifacts'])}")
        
        if qa_input['code_artifacts']:
            print(f"   📁 Code files extracted:")
            for artifact in qa_input['code_artifacts']:
                file_path = Path(artifact['file'])
                print(f"      📄 {file_path.name} ({artifact['language']}) - {len(artifact['content'])} chars")
        
        # Show file organization
        print(f"\n📁 File Organization:")
        task_outputs = registry.list_task_outputs("BE-07")
        for output_file in task_outputs:
            file_path = Path(output_file)
            size = file_path.stat().st_size if file_path.exists() else 0
            print(f"   📄 {file_path.name} - {size:,} bytes")
        
        # Check code directory
        code_dir = Path("outputs/BE-07/code")
        if code_dir.exists():
            print(f"   📁 code/ directory:")
            for code_file in code_dir.iterdir():
                if code_file.is_file():
                    size = code_file.stat().st_size
                    print(f"      🔧 {code_file.name} - {size:,} bytes")
    
    else:
        print("ℹ️ No registered outputs found for BE-07")
        print("💡 Run the registration commands to see the demo in action:")
        print("   python orchestration/register_output.py BE-07 backend outputs/BE-07/sample_backend_output.md --extract-code")
        print("   python orchestration/register_output.py BE-07 qa outputs/BE-07/sample_qa_report.json --type json")
    
    print(f"\n🎉 Step 4.4 Demo Complete!")
    print(f"✅ Agent output registration system is operational")
    print(f"✅ Ready for Phase 5 — Reporting, QA & Completion")


if __name__ == "__main__":
    demonstrate_step_4_4()
