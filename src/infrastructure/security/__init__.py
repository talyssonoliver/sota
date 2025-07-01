"""
Security infrastructure module.

This module provides security-related functionality and patches for external libraries.
It should be imported at the start of your application.
"""

import logging
from pathlib import Path

# Import patches so they're available when module is imported
try:
    from . import chromadb_telemetry_patch
except ImportError:
    chromadb_telemetry_patch = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("security")

def apply_all_patches():
    """Apply all security patches in the patches directory."""
    success_count = 0
    failure_count = 0
    
    # Apply the chromadb telemetry patch
    try:
        from src.infrastructure.security.chromadb_telemetry_patch import apply_patch as apply_chromadb_patch
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
        f"Applied {success_count} patches successfully, {failure_count} failed")
    return success_count, failure_count

if __name__ == "__main__":
    apply_all_patches()