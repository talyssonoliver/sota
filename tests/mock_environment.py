"""
Mock environment for tests.
Provides consistent mocking of system dependencies.
"""

import os
import sys
import threading
import time
from unittest.mock import MagicMock, patch


def setup_mock_environment():
    """
    Set up a mock environment for testing.
    Returns a dictionary of applied mocks that can be used in tests.
    """
    mocks = {}

    # Set TESTING environment variable
    os.environ["TESTING"] = "1"

    # Mock expensive or external dependencies
    mocks["threading"] = MagicMock(wraps=threading)
    mocks["time"] = MagicMock(wraps=time)

    # Create a MagicMock version of langchain_openai classes
    if "langchain_openai" not in sys.modules:
        sys.modules["langchain_openai"] = MagicMock()
        mocks["langchain_openai"] = sys.modules["langchain_openai"]

    # Since this module creates test-only mocks, add a cleanup function
    def cleanup():
        for module_name in list(sys.modules.keys()):
            if module_name.startswith("_mock_") and module_name in sys.modules:
                del sys.modules[module_name]

    mocks["cleanup"] = cleanup

    # Create missing files/directories needed for tests
    test_data_dir = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "test_data", "context-store")
    os.makedirs(test_data_dir, exist_ok=True)

    # Create a test document if it doesn't exist yet
    test_doc_path = os.path.join(test_data_dir, "test_doc.md")
    if not os.path.exists(test_doc_path):
        with open(test_doc_path, "w", encoding="utf-8") as f:
            f.write("""# Test Document

This is a test document used for testing the memory engine and retrieval QA functionality.

## Supabase RLS Rules

The orders table has RLS rules that restrict users to only see their own orders.
These rules are implemented using row-level security policies.

## Authentication

Authentication is handled via JWT tokens. When a user logs in, a JWT token is generated
that contains the user's ID and role. This token is then used for all subsequent requests.

## Security

The system uses several security measures:
- Row-level security (RLS) in Supabase
- JWT token authentication
- HTTPS for all communications
- Input sanitization to prevent SQL injection
""")

    return mocks
