"""
Refactored retrieval_qa implementation with reduced complexity.
Uses the new modular memory system and improved structure.
"""

import logging
import sys

try:
    from tools.retrieval_qa_refactored import retrieval_qa
except ImportError as e:
    logging.error(f"Failed to import retrieval_qa: {e}")
    # Create a mock fallback function
    def retrieval_qa(*args, **kwargs):
        """Mock retrieval_qa function when import fails."""
        logging.warning("Using mock retrieval_qa - functionality not available")
        return {"error": "retrieval_qa functionality not available"}

__all__ = ['retrieval_qa']
