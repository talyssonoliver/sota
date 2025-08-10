#!/usr/bin/env python3
"""
Integration Validation Script

Validates that the corrected OpenAI + Claude Code integration is working properly.
"""

import os
import sys
import logging
from typing import Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_openai_integration() -> Tuple[bool, str]:
    """Test that OpenAI integration is working correctly."""
    try:
        from src.infrastructure.memory.engines.memory_engine import _get_embeddings_instance
        
        # Test with mock API key
        embeddings = _get_embeddings_instance(
            embedding_model='text-embedding-ada-002',
            openai_api_key='test-key'
        )
        
        if embeddings and 'OpenAI' in type(embeddings).__name__:
            return True, f"✅ OpenAI embeddings working - {type(embeddings).__name__}"
        else:
            return False, "❌ OpenAI embeddings not working"
            
    except Exception as e:
        return False, f"❌ OpenAI test failed: {e}"

def test_memory_engine_config() -> Tuple[bool, str]:
    """Test that memory engine configuration is correct."""
    try:
        from src.infrastructure.memory.config.memory_config import MemoryEngineConfig
        
        config = MemoryEngineConfig()
        
        # Check that Claude-specific config is removed
        if hasattr(config, 'claude_embedding_model'):
            return False, "❌ Claude embedding config still present"
        
        if hasattr(config, 'use_claude_embeddings'):
            return False, "❌ Claude feature flag still present"
            
        if config.embedding_model == "text-embedding-ada-002":
            return True, "✅ Memory config correctly uses OpenAI model"
        else:
            return False, f"❌ Unexpected embedding model: {config.embedding_model}"
            
    except Exception as e:
        return False, f"❌ Memory config test failed: {e}"

def test_claude_integration_removed() -> Tuple[bool, str]:
    """Test that fake Claude integration files are removed."""
    claude_dir = "src/infrastructure/integrations/claude"
    claude_tests = ["tests/mock_claude_embeddings.py", "tests/mock_claude_chat.py"]
    
    # Check Claude integration directory
    if os.path.exists(claude_dir):
        return False, f"❌ Claude integration directory still exists: {claude_dir}"
    
    # Check Claude test files
    for test_file in claude_tests:
        if os.path.exists(test_file):
            return False, f"❌ Claude test file still exists: {test_file}"
    
    return True, "✅ Fake Claude integration files properly removed"

def test_claude_code_setup() -> Tuple[bool, str]:
    """Test that Claude Code CLI setup files are present."""
    required_files = [
        "claude-code-setup-guide.md",
        "CLAUDE_CODE_INTEGRATION_PLAN.md", 
        ".env.claude.template",
        "docs/development/CLAUDE_CODE_TEAM_ONBOARDING.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        return False, f"❌ Missing Claude Code setup files: {missing_files}"
    
    return True, "✅ Claude Code CLI setup files present"

def test_claude_commands() -> Tuple[bool, str]:
    """Test that custom Claude Code commands are available."""
    commands_dir = ".claude/commands"
    expected_commands = [
        "analyze-architecture.md",
        "generate-tests.md", 
        "review-code.md",
        "optimize-performance.md"
    ]
    
    if not os.path.exists(commands_dir):
        return False, f"❌ Commands directory missing: {commands_dir}"
    
    missing_commands = []
    for command in expected_commands:
        command_path = os.path.join(commands_dir, command)
        if not os.path.exists(command_path):
            missing_commands.append(command)
    
    if missing_commands:
        return False, f"❌ Missing Claude Code commands: {missing_commands}"
    
    return True, "✅ Claude Code custom commands available"

def test_production_stability() -> Tuple[bool, str]:
    """Test that production systems are stable and unchanged."""
    try:
        # Test memory engine can be initialized
        from src.infrastructure.memory.engines.memory_engine import MemoryEngine
        
        # This should work without Claude dependencies
        MemoryEngine()
        
        return True, "✅ Production memory engine stable"
        
    except Exception as e:
        return False, f"❌ Production stability test failed: {e}"

def run_all_tests() -> None:
    """Run all validation tests and report results."""
    tests = [
        ("OpenAI Integration", test_openai_integration),
        ("Memory Engine Config", test_memory_engine_config),
        ("Claude Integration Removal", test_claude_integration_removed),
        ("Claude Code Setup", test_claude_code_setup),
        ("Claude Code Commands", test_claude_commands),
        ("Production Stability", test_production_stability)
    ]
    
    print("🧪 Running Integration Validation Tests...\n")
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            success, message = test_func()
            print(f"{test_name}: {message}")
            
            if success:
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"{test_name}: ❌ Test error: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! Integration is working correctly.")
        print("\n📋 Next Steps:")
        print("1. Install Claude Code CLI for development team")
        print("2. Configure MCP servers using the setup guide")
        print("3. Start using custom commands for development acceleration")
        return True
    else:
        print(f"\n⚠️ {failed} tests failed. Please review and fix issues before proceeding.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)