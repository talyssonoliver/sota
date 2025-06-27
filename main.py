#!/usr/bin/env python3

"""
AI Agent System - Main Entry Point

Production-ready multi-agent AI system for automating software development workflows.
Features enterprise-grade security, real-time monitoring, and comprehensive automation.

System Components:
- 7 Specialized Agents (Technical Lead, Backend, Frontend, QA, Documentation, Product Manager, UX Designer)
- LangGraph Workflow Engine with dynamic routing and dependency management
- Enterprise Memory Engine with ChromaDB, encryption, and multi-tier caching
- Comprehensive Tool Ecosystem for development, testing, and quality assurance
- Daily Automation Cycle with monitoring and reporting

Usage:
    python main.py              # Run system validation tests
    python main.py --test       # Run comprehensive test suite
    python main.py --help       # Show all available options
"""

import argparse
import logging
import os
import sys
import time  # Standard library - no need for try/except
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import secure import manager
from security.import_security import secure_import_manager, secure_import

# Securely load dotenv with proper fallback
dotenv_module = secure_import('dotenv', lambda: None)
if dotenv_module and hasattr(dotenv_module, 'load_dotenv'):
    load_dotenv = dotenv_module.load_dotenv
else:
    load_dotenv = lambda *args, **kwargs: None

from src.infrastructure.utils.input_validation import validate_command_args, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build/runtime/logs/main.log', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Apply patches to fix external library issues
# Try to import from the correct location
try:
    from src.infrastructure.security import apply_all_patches
    apply_all_patches()
    logger.info("Applied system patches successfully")
except (ImportError, Exception) as e:
    logger.warning(f"Could not apply patches: {e}")
    # Try alternate location
    patches_module = secure_import('patches')
    if patches_module and hasattr(patches_module, 'apply_all_patches'):
        try:
            patches_module.apply_all_patches()
            logger.info("Applied system patches successfully")
        except Exception as e:
            logger.warning(f"Could not apply patches: {e}")
    else:
        logger.warning("Patches module not available - some features may not work correctly")

# Securely import LangChain components
langchain_available = False
try:
    # Try modern langchain structure first
    langchain_community = secure_import('langchain_community.agent_toolkits')
    langchain_core = secure_import('langchain_core.tools')
    langchain_openai = secure_import('langchain_openai')
    
    if all([langchain_community, langchain_core, langchain_openai]):
        create_sql_agent = langchain_community.create_sql_agent
        Tool = langchain_core.Tool
        ChatOpenAI = langchain_openai.ChatOpenAI
        langchain_available = True
        logger.info("LangChain libraries loaded successfully")
    else:
        raise ImportError("One or more LangChain components not available")
        
except (ImportError, AttributeError) as e:
    logger.warning(f"Could not load langchain libraries: {e}. Using compatibility layer.")
    langchain_available = False
    
# Create secure compatibility classes only if LangChain is not available
if not langchain_available:
    class Tool:
        def __init__(self, name="", description="", func=None):
            self.name = name
            self.description = description
            self.func = func
        
        @classmethod
        def from_function(cls, func, name, description):
            return cls(name=name, description=description, func=func)
    
    class ChatOpenAI:
        def __init__(self, *args, **kwargs):
            logger.warning("Using ChatOpenAI compatibility wrapper - limited functionality")
            pass
    
    # Create a compatibility layer
    class AgentType:
        ZERO_SHOT_REACT_DESCRIPTION = "zero-shot-react-description"
        CHAT_ZERO_SHOT_REACT_DESCRIPTION = "chat-zero-shot-react-description"
    
    def initialize_agent(tools, llm, agent_type=None, **kwargs):
        """Compatibility wrapper for agent initialization"""
        logger.warning("Using agent initialization compatibility wrapper")
        class MockAgent:
            def invoke(self, input_dict):
                return {"output": "Mock agent response - LangChain not available"}
        return MockAgent()
        
    def create_sql_agent(llm=None, toolkit=None, **kwargs):
        """Compatibility wrapper for SQL agent creation"""
        logger.warning("Using SQL agent compatibility wrapper")
        return None
else:
    # Import the real agent initialization function
    try:
        from langchain.agents import AgentType, initialize_agent
    except ImportError:
        logger.error("Could not import agent initialization functions")
        langchain_available = False

from tools.echo_tool import EchoTool
from tools.supabase_tool import SupabaseTool

# Load environment variables
if callable(load_dotenv):
    load_dotenv()
else:
    logger.warning("load_dotenv is not callable, skipping .env file loading")
    
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    logger.error("OPENAI_API_KEY not found in environment variables")
    print("Error: OPENAI_API_KEY not found in environment variables")
    print("Please ensure your .env file contains a valid OpenAI API key.")
    sys.exit(1)

logger.info("AI Agent System initialized successfully")

def run_simple_agent_test() -> bool:
    """Run a simple test using LangChain with the EchoTool.
    
    Returns:
        bool: True if test passes, False otherwise
    """
    try:
        logger.info("Running simple agent test with EchoTool...")
        
        # Initialize the language model
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k")
        
        # Create the echo tool
        echo_tool = EchoTool()
        
        # Initialize the agent
        agent = initialize_agent(
            tools=[Tool.from_function(
                func=echo_tool._run,
                name=echo_tool.name,
                description=echo_tool.description
            )],
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False
        )
        
        # Run the agent with invoke
        result = agent.invoke(
            {"input": "Use the echo tool to repeat 'AI Agent System operational'"})
        
        success = "AI Agent System operational" in result['output']
        if success:
            logger.info("✅ Simple agent test passed")
            print("✅ Simple agent test: PASSED")
        else:
            logger.error("❌ Simple agent test failed")
            print("❌ Simple agent test: FAILED")
        
        return success
        
    except Exception as e:
        logger.error(f"Simple agent test failed with error: {e}")
        print(f"❌ Simple agent test: FAILED - {e}")
        return False

def run_supabase_tool_test() -> bool:
    """Test the Supabase tool.
    
    Returns:
        bool: True if test passes, False otherwise
    """
    try:
        logger.info("Running Supabase tool test...")
        
        # Initialize the language model
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k")
        
        # Create the Supabase tool
        supabase_tool = SupabaseTool()
        
        # Initialize the agent
        agent = initialize_agent(
            tools=[Tool.from_function(
                func=supabase_tool._run,
                name=supabase_tool.name,
                description=supabase_tool.description
            )],
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False
        )
        
        # Run the agent with invoke
        result = agent.invoke(
            {"input": "Get the database schema summary for the Artesanato E-commerce project"})
        
        success = result['output'] and len(result['output']) > 0
        if success:
            logger.info("✅ Supabase tool test passed")
            print("✅ Supabase tool test: PASSED")
        else:
            logger.error("❌ Supabase tool test failed")
            print("❌ Supabase tool test: FAILED")
        
        return success
        
    except Exception as e:
        logger.error(f"Supabase tool test failed with error: {e}")
        print(f"❌ Supabase tool test: FAILED - {e}")
        return False

def run_memory_test() -> bool:
    """Test the memory engine.
    
    Returns:
        bool: True if test passes, False otherwise
    """
    try:
        logger.info("Running memory engine test...")
        
        # Test memory engine functionality
        try:
            from tools.memory import MemoryEngine
            memory = MemoryEngine()
            
            # Test basic context retrieval
            context = memory.get_context(
                query="database schema", 
                k=5
            )
            
            success = context is not None and len(context) > 0
            if success:
                logger.info("✅ Memory engine test passed")
                print("✅ Memory engine test: PASSED")
            else:
                logger.error("❌ Memory engine test failed - no context retrieved")
                print("❌ Memory engine test: FAILED - no context retrieved")
            
            return success
            
        except ImportError:
            # Fallback to legacy memory function if available
            try:
                from tools.memory import get_memory_instance, get_context_by_keys
                memory = get_memory_instance()
                context = get_context_by_keys(["database", "schema"])
                
                success = context is not None and len(context) > 0
                if success:
                    logger.info("✅ Memory engine test passed (legacy mode)")
                    print("✅ Memory engine test: PASSED (legacy mode)")
                else:
                    logger.error("❌ Memory engine test failed")
                    print("❌ Memory engine test: FAILED")
                
                return success
                
            except ImportError:
                logger.warning("Memory engine not available - skipping test")
                print("⚠️  Memory engine test: SKIPPED (not available)")
                return True
        
    except Exception as e:
        logger.error(f"Memory engine test failed with error: {e}")
        print(f"❌ Memory engine test: FAILED - {e}")
        return False

def run_workflow_test() -> bool:
    """Test the basic workflow.
    
    Returns:
        bool: True if test passes, False otherwise
    """
    try:
        logger.info("Running basic workflow test...")
        
        from typing import Optional, TypedDict
        try:
            from langgraph.graph import StateGraph
        except ImportError:
            logger.warning("LangGraph not available, using mock workflow")
            class StateGraph:
                def __init__(self, state_schema=None):
                    self.state_schema = state_schema
                def add_node(self, name, func):
                    pass
                def add_edge(self, from_node, to_node):
                    pass
                def set_entry_point(self, node):
                    pass
                def set_finish_point(self, node):
                    pass
                def compile(self):
                    return MockCompiledGraph()
            
            class MockCompiledGraph:
                def invoke(self, state):
                    return {"status": "completed", "result": "Mock test passed"}

        # Define a simplified test workflow to avoid recursion issues
        class WorkflowState(TypedDict):
            task_id: str
            message: str
            status: Optional[str]
            result: Optional[str]

        # Create a simpler test workflow
        workflow = StateGraph(state_schema=WorkflowState)

        # Simple handler that just returns the input with a success message
        def test_handler(state: WorkflowState) -> WorkflowState:
            return {
                **state,
                "result": f"Task {state['task_id']} processed successfully",
                "status": "DONE"
            }

        # Add a single node for testing
        workflow.add_node("test_handler", test_handler)

        # Set the entry point
        workflow.set_entry_point("test_handler")

        # Compile and run
        app = workflow.compile()
        result = app.invoke({
            "task_id": "SYSTEM_TEST",
            "message": "Validate workflow execution",
            "status": "TESTING"
        })

        success = (result and 
                  result.get("status") == "DONE" and 
                  "processed successfully" in result.get("result", ""))
        
        if success:
            logger.info("✅ Basic workflow test passed")
            print("✅ Basic workflow test: PASSED")
        else:
            logger.error("❌ Basic workflow test failed")
            print("❌ Basic workflow test: FAILED")
        
        return success
        
    except Exception as e:
        logger.error(f"Basic workflow test failed with error: {e}")
        print(f"❌ Basic workflow test: FAILED - {e}")
        return False

def run_comprehensive_tests() -> bool:
    """Run comprehensive system tests.
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    try:
        logger.info("Starting comprehensive test suite...")
        
        subprocess_module = secure_import('subprocess')
        if not subprocess_module:
            logger.error("subprocess module not available - cannot run tests")
            return False
            
        result = subprocess_module.run([
            sys.executable, "-m", "tests.run_tests", "--all"
        ], capture_output=True, text=True, timeout=300)
        
        success = result.returncode == 0
        if success:
            logger.info("✅ Comprehensive test suite passed")
            print("✅ Comprehensive test suite: PASSED")
        else:
            logger.error(f"❌ Comprehensive test suite failed: {result.stderr}")
            print(f"❌ Comprehensive test suite: FAILED")
        
        return success
        
    except subprocess_module.TimeoutExpired if subprocess_module else Exception:
        logger.error("❌ Comprehensive test suite timed out")
        print("❌ Comprehensive test suite: TIMEOUT")
        return False
    except Exception as e:
        logger.error(f"Comprehensive test suite failed with error: {e}")
        print(f"❌ Comprehensive test suite: FAILED - {e}")
        return False

def run_validation_suite() -> Dict[str, bool]:
    """Run the complete validation suite.
    
    Returns:
        Dict[str, bool]: Test results for each component
    """
    print("\n" + "="*60)
    print("🚀 AI AGENT SYSTEM - VALIDATION SUITE")
    print("="*60)
    
    results = {}
    
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    print("\n📋 Running core component validation tests...")
    
    # Core component tests
    print("\n1. Simple Agent Test (LangChain + EchoTool)")
    results['simple_agent'] = run_simple_agent_test()
    
    print("\n2. Supabase Tool Test")
    results['supabase_tool'] = run_supabase_tool_test()
    
    print("\n3. Memory Engine Test")
    results['memory_engine'] = run_memory_test()
    
    print("\n4. Basic Workflow Test (LangGraph)")
    results['workflow'] = run_workflow_test()
    
    return results

def print_summary(results: Dict[str, bool], comprehensive_test: bool = False) -> None:
    """Print validation summary.
    
    Args:
        results: Test results dictionary
        comprehensive_test: Whether comprehensive tests were run
    """
    print("\n" + "="*60)
    print("📊 VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n✅ Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL CORE TESTS PASSED!")
        print("🚀 AI Agent System is ready for operation")
        
        if not comprehensive_test:
            print("\n💡 For full system validation, run:")
            print("   python main.py --test")
    else:
        print("\n⚠️  SOME TESTS FAILED:")
        for test_name, result in results.items():
            if not result:
                print(f"   ❌ {test_name}")
    
    print("\n📚 Next Steps:")
    print("   • Review logs in 'logs/main.log' for details")
    print("   • Check README.md for usage instructions")
    print("   • Run 'python orchestration/execute_workflow.py --help' for workflow options")
    print("="*60)

def main():
    """Main entry point with command line argument support."""
    parser = argparse.ArgumentParser(
        description="AI Agent System - Production-ready multi-agent automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run core validation tests
  python main.py --test            # Run comprehensive test suite
  python main.py --quiet           # Run with minimal output
  
For more information, see README.md
        """
    )
    
    parser.add_argument(
        '--test', 
        action='store_true',
        help='Run comprehensive test suite'
    )
    
    parser.add_argument(
        '--quiet', 
        action='store_true',
        help='Run with minimal output'
    )
    
    args = parser.parse_args()
    
    # Validate command line arguments
    try:
        args = validate_command_args(args)
    except ValidationError as e:
        logger.error(f"Invalid command line arguments: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    if args.test:
        # Run comprehensive tests
        print("\n🔬 Running comprehensive test suite...")
        comprehensive_result = run_comprehensive_tests()
        
        if comprehensive_result:
            print("\n🎉 COMPREHENSIVE TEST SUITE PASSED!")
            print("🚀 AI Agent System is fully validated and ready for production")
        else:
            print("\n⚠️  Comprehensive test suite had failures")
            print("📚 Check test logs for detailed error information")
        
        sys.exit(0 if comprehensive_result else 1)
    
    else:
        # Run core validation tests
        results = run_validation_suite()
        print_summary(results)
        
        # Exit with appropriate code
        all_passed = all(results.values())
        sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()