"""
Test script for the ChromaDB telemetry patch.
This script tests the patch in isolation.
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_patch")

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def test_patch():
    """Test the ChromaDB telemetry patch."""    # Apply the patch
    from patches.chromadb_telemetry_patch import apply_patch as patch_func
    if not patch_func():
        logger.error("Failed to apply patch")
        return False

    # Try to import and use ChromaDB
    try:
        import chromadb
        from chromadb.api.models.Collection import Collection

        # Create a client
        client = chromadb.Client()
        logger.info("Successfully created ChromaDB client")

        # Test successful
        return True
    except Exception as e:
        logger.error(f"Failed to use ChromaDB after patching: {str(e)}")
        return False


if __name__ == "__main__":
    if test_patch():
        logger.info("Patch test successful")
        sys.exit(0)
    else:
        logger.error("Patch test failed")
        sys.exit(1)
