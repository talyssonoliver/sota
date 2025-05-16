"""
Sprint Phases Test Script
Tests core functionality across sprint phases 0, 1 and 2
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Apply patching to fix dotenv loading issues
from scripts.patch_dotenv import patch_dotenv
patch_dotenv()

# Apply patching to provide mock implementations for missing dependencies
from scripts.mock_dependencies import patch_imports
patch_imports()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("sprint-tests")

def test_phase0_setup():
    """Test Phase 0: Project Setup"""
    logger.info("=== Testing Phase 0: Project Setup ===")
    
    # Check if key directories exist
    directories = [
        "agents", "config", "context-store", "docs", 
        "graph", "orchestration", "prompts", "tasks"
    ]
    
    success = True
    for dir_name in directories:
        if os.path.isdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), dir_name)):
            logger.info(f"✓ Directory '{dir_name}' exists")
        else:
            logger.error(f"✗ Directory '{dir_name}' does not exist")
            success = False
    
    # Check if task YAML files exist
    tasks_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tasks")
    yaml_count = len([f for f in os.listdir(tasks_dir) if f.endswith('.yaml')])
    
    if yaml_count > 0:
        logger.info(f"✓ Found {yaml_count} task YAML files")
    else:
        logger.error(f"✗ No task YAML files found")
        success = False
    
    return success

def test_phase1_agents():
    """Test Phase 1: Agent Specialization"""
    logger.info("\n=== Testing Phase 1: Agent Specialization ===")
    
    success = True
    
    # Try to import agent modules
    try:
        from agents.coordinator import create_coordinator_agent
        logger.info("✓ Successfully imported coordinator agent")
    except ImportError as e:
        logger.error(f"✗ Failed to import coordinator agent: {str(e)}")
        success = False
        
    # Check if agent prompt files exist
    prompt_files = [
        "coordinator.md", "backend-agent.md", "frontend-agent.md",
        "technical-architect.md", "qa-agent.md", "doc-agent.md"
    ]
    
    prompts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts")
    for prompt_file in prompt_files:
        if os.path.isfile(os.path.join(prompts_dir, prompt_file)):
            logger.info(f"✓ Prompt file '{prompt_file}' exists")
        else:
            logger.error(f"✗ Prompt file '{prompt_file}' does not exist")
            success = False
    
    return success

def test_phase2_langgraph():
    """Test Phase 2: Task Planning & Workflow Architecture"""
    logger.info("\n=== Testing Phase 2: Task Planning & Workflow Architecture ===")
    
    success = True
    
    # Check core workflow files
    workflow_files = [
        "graph/graph_builder.py",
        "graph/handlers.py", 
        "orchestration/states.py",
        "orchestration/execute_workflow.py"
    ]
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for wf_file in workflow_files:
        if os.path.isfile(os.path.join(base_dir, wf_file)):
            logger.info(f"✓ Workflow file '{wf_file}' exists")
        else:
            logger.error(f"✗ Workflow file '{wf_file}' does not exist")
            success = False
    
    # Check enhanced features
    enhanced_files = [
        "graph/auto_generate_graph.py",
        "graph/resilient_workflow.py",
        "graph/notifications.py",
        "scripts/monitor_workflow.py"
    ]
    
    for enh_file in enhanced_files:
        if os.path.isfile(os.path.join(base_dir, enh_file)):
            logger.info(f"✓ Enhanced feature '{enh_file}' exists")
        else:
            logger.error(f"✗ Enhanced feature '{enh_file}' does not exist")
            success = False
    
    # Check documentation
    doc_files = [
        "docs/langgraph_workflow.md",
        "docs/workflow_monitoring.md",
        "docs/phase2_checklist.md"
    ]
    
    for doc_file in doc_files:
        if os.path.isfile(os.path.join(base_dir, doc_file)):
            logger.info(f"✓ Documentation file '{doc_file}' exists")
        else:
            logger.error(f"✗ Documentation file '{doc_file}' does not exist")
            success = False
    
    # Try to import critical modules
    try:
        from graph.graph_builder import build_workflow_graph
        logger.info("✓ Successfully imported build_workflow_graph")
    except ImportError as e:
        logger.error(f"✗ Failed to import build_workflow_graph: {str(e)}")
        success = False
    
    try:
        from orchestration.enhanced_workflow import EnhancedWorkflowExecutor
        logger.info("✓ Successfully imported EnhancedWorkflowExecutor")
    except ImportError as e:
        logger.error(f"✗ Failed to import EnhancedWorkflowExecutor: {str(e)}")
        success = False
    
    return success

def main():
    """Run tests for specified sprint phases"""
    parser = argparse.ArgumentParser(description="Test AI System Sprint Phases")
    parser.add_argument("--phases", type=str, default="0,1,2", 
                        help="Comma-separated list of phases to test (e.g., 0,1,2)")
    
    args = parser.parse_args()
    phases_to_test = [int(p) for p in args.phases.split(",") if p.strip()]
    
    results = {}
    
    if 0 in phases_to_test:
        results["Phase 0"] = test_phase0_setup()
    
    if 1 in phases_to_test:
        results["Phase 1"] = test_phase1_agents()
    
    if 2 in phases_to_test:
        results["Phase 2"] = test_phase2_langgraph()
    
    # Print summary
    logger.info("\n=== Test Results Summary ===")
    for phase, success in results.items():
        status = "PASSED" if success else "FAILED"
        logger.info(f"{phase}: {status}")

if __name__ == "__main__":
    main()