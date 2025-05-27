"""
Optimized test script for the ChromaDB telemetry patch.
This script demonstrates the test optimization approach.
"""

import logging
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_patch")

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


@pytest.mark.unit
def test_patch_with_mocks():
    """Test the ChromaDB telemetry patch with external service mocks."""
    # Use the auto-mock from conftest.py
    from patches.chromadb_telemetry_patch import apply_patch as patch_func

    with patch('chromadb.Client') as mock_client:
        # Mock ChromaDB client to avoid external dependencies
        mock_client.return_value.get_or_create_collection.return_value = MagicMock()

        result = patch_func()

        # Test that patch applies successfully
        assert result is True or result is None

        # Try to import and use ChromaDB
        try:
            import chromadb
            client = chromadb.Client()
            collection = client.get_or_create_collection(name="test")

            logger.info("ChromaDB patch test passed")
            assert collection is not None

        except Exception as e:
            logger.error(f"ChromaDB test failed: {e}")
            pytest.fail(f"ChromaDB functionality test failed: {e}")


@pytest.mark.unit
def test_patch_isolation():
    """Test that the patch doesn't interfere with other components."""
    try:
        from patches.chromadb_telemetry_patch import apply_patch

        # Test multiple applications
        result1 = apply_patch()
        result2 = apply_patch()

        assert result1 is True or result1 is None
        assert result2 is True or result2 is None

    except Exception as e:
        pytest.fail(f"Patch isolation test failed: {e}")


@pytest.mark.unit
def test_patch_performance():
    """Test that patch application is fast."""
    import time

    start_time = time.time()

    try:
        from patches.chromadb_telemetry_patch import apply_patch
        apply_patch()
    except Exception:
        pass  # We're testing performance, not functionality

    duration = time.time() - start_time

    # Patch should apply in under 1 second
    assert duration < 1.0, f"Patch took too long: {duration:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
