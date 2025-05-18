"""
Run tests to verify fixes for memory and retrieval QA issues.
"""
import sys
import os
import unittest

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Apply monkey patches for testing
from tests.monkey_patch import apply_agent_memory_patch
apply_agent_memory_patch()

if __name__ == "__main__":
    # Create test suite for agent instantiation tests
    from tests.test_agents import (
        TestAgentInstantiation, 
        TestAgentToolIntegration
    )
    
    # Create test suite for retrieval QA tests
    from tests.test_fixed_retrieval_qa import TestFixedRetrievalQA
    from tests.test_memory_config import TestMemoryConfig
    
    # Create and run the test suite
    test_suite = unittest.TestSuite()
    
    # Add memory-related agent tests
    test_suite.addTest(unittest.makeSuite(TestAgentInstantiation))
    test_suite.addTest(unittest.makeSuite(TestAgentToolIntegration))
    test_suite.addTest(unittest.makeSuite(TestMemoryConfig))
    
    # Add retrieval QA tests
    test_suite.addTest(unittest.makeSuite(TestFixedRetrievalQA))
    
    # Run the tests
    result = unittest.TextTestRunner().run(test_suite)
    
    # Exit with non-zero status if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
