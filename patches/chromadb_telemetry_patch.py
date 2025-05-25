"""
Patch for ChromaDB telemetry to fix the is_in_colab import issue.

This patch monkey patches the ClientStartEvent class to handle the case when
the is_in_colab function import fails.
"""

import logging
from types import ModuleType

logger = logging.getLogger(__name__)

def apply_patch():
    """Apply the patch to fix ChromaDB telemetry issues."""
    try:
        # Import the required modules
        import chromadb.telemetry.product.events
        
        # Store the original __init__ method
        original_init = chromadb.telemetry.product.events.ClientStartEvent.__init__
        
        # Create a patched __init__ method
        def patched_init(self):
            try:
                original_init(self)
            except ImportError:
                # If import fails, set in_colab to False
                logger.warning("Could not import is_in_colab, setting in_colab to False")
                self.in_colab = False
        
        # Apply the patch
        chromadb.telemetry.product.events.ClientStartEvent.__init__ = patched_init
        logger.info("Applied patch to ClientStartEvent.__init__")
        
        return True
    except Exception as e:
        logger.error(f"Failed to apply patch: {str(e)}", exc_info=True)
        return False

# For testing the patch directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    apply_patch()
