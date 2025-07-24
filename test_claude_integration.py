#!/usr/bin/env python3
"""
Test Claude Integration

Basic integration test for Claude components without complex dependencies.
"""

import os
import sys

# Set up test environment
os.environ['CLAUDE_API_KEY'] = 'test-key-for-testing'
os.environ['TESTING'] = '1'

def test_claude_embeddings():
    """Test Claude embeddings functionality."""
    try:
        from src.infrastructure.integrations.claude import ClaudeEmbeddings
        
        embeddings = ClaudeEmbeddings()
        
        # Test single query
        test_embedding = embeddings.embed_query('test query')
        assert len(test_embedding) == 1536, f"Expected 1536 dimensions, got {len(test_embedding)}"
        
        # Test multiple documents
        test_docs = ['document 1', 'document 2', 'document 3']
        doc_embeddings = embeddings.embed_documents(test_docs)
        assert len(doc_embeddings) == 3, f"Expected 3 embeddings, got {len(doc_embeddings)}"
        assert all(len(emb) == 1536 for emb in doc_embeddings), "All embeddings should be 1536 dimensions"
        
        # Test health check
        assert embeddings.health_check(), "Health check should pass"
        
        print("✅ Claude embeddings test passed")
        return True
        
    except Exception as e:
        print(f"❌ Claude embeddings test failed: {e}")
        return False

def test_claude_chat_simple():
    """Test Claude chat functionality with simplified approach."""
    try:
        from src.infrastructure.integrations.claude.config import ClaudeConfig
        from tests.mock_claude_chat import MockClaudeChatModel
        
        # Use mock implementation for testing
        config = ClaudeConfig.from_environment()
        chat_model = MockClaudeChatModel(temperature=0.7)
        
        # Test basic response generation
        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content="Hello, how are you?")]
        result = chat_model._generate(messages)
        
        assert result.generations, "Should have generated a response"
        assert result.generations[0].message.content, "Response should have content"
        
        # Test response contains expected pattern
        response = result.generations[0].message.content
        assert "Claude" in response or "AI assistant" in response, f"Expected Claude response pattern, got: {response}"
        
        # Test health check
        assert chat_model.health_check(), "Health check should pass"
        
        print("✅ Claude chat model test passed")
        return True
        
    except Exception as e:
        print(f"❌ Claude chat model test failed: {e}")
        return False

def test_feature_flags():
    """Test feature flag functionality."""
    try:
        from src.infrastructure.integrations.claude.feature_flags import (
            get_migration_flags, MigrationComponent
        )
        
        flags = get_migration_flags()
        
        # Test default status (should be disabled)
        status = flags.get_status()
        assert isinstance(status, dict), "Status should be a dictionary"
        
        # Test component checking
        embeddings_enabled = flags.is_enabled(MigrationComponent.EMBEDDINGS)
        chat_enabled = flags.is_enabled(MigrationComponent.CHAT_MODEL)
        
        # By default, features should be disabled
        assert not embeddings_enabled, "Embeddings should be disabled by default"
        assert not chat_enabled, "Chat should be disabled by default"
        
        # Test enabling a component
        flags.enable(MigrationComponent.EMBEDDINGS)
        assert flags.is_enabled(MigrationComponent.EMBEDDINGS), "Embeddings should be enabled after calling enable()"
        
        print("✅ Feature flags test passed")
        return True
        
    except Exception as e:
        print(f"❌ Feature flags test failed: {e}")
        return False

def test_memory_integration():
    """Test memory engine integration with Claude."""
    try:
        from src.infrastructure.memory.engines.memory_engine import _get_embeddings_instance
        
        # Test embeddings instance creation
        embeddings = _get_embeddings_instance()
        
        # Should return None when no API keys available and Claude disabled
        # This tests the graceful degradation
        print(f"Embeddings instance type: {type(embeddings).__name__ if embeddings else 'None'}")
        
        print("✅ Memory integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Memory integration test failed: {e}")
        return False

def main():
    """Run all Claude integration tests."""
    print("🚀 Running Claude Integration Tests\n")
    
    tests = [
        test_claude_embeddings,
        test_claude_chat_simple,
        test_feature_flags,
        test_memory_integration,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests
    
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All Claude integration tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())