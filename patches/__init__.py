"""
Chromadb patches loader.

This script applies patches to fix issues with external libraries.
It should be imported at the start of your application.
"""

import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("patches_loader")


def apply_all_patches():
    """Apply all patches in the patches directory."""
    patches_dir = Path(__file__).parent
    success_count = 0
    failure_count = 0

    # Apply the chromadb telemetry patch
    try:
        from patches.chromadb_telemetry_patch import \
            apply_patch as apply_chromadb_patch
        if apply_chromadb_patch():
            logger.info("Successfully applied ChromaDB telemetry patch")
            success_count += 1
        else:
            logger.warning("Failed to apply ChromaDB telemetry patch")
            failure_count += 1
    except ImportError as e:
        logger.error(f"Could not import ChromaDB telemetry patch: {str(e)}")
        failure_count += 1

    # Add more patches here as needed

    logger.info(
        f"Applied {success_count} patches successfully,
    {failure_count} failed")
    return success_count, failure_count


if __name__ == "__main__":
    apply_all_patches()