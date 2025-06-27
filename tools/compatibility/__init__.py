"""Compatibility modules for external libraries.

This package provides compatibility layers for external libraries
that may not be installed in all environments.
"""

import sys
import os
from pathlib import Path

# Add compatibility modules to Python path
compatibility_path = Path(__file__).parent
if str(compatibility_path) not in sys.path:
    sys.path.insert(0, str(compatibility_path))

# List of available compatibility modules
AVAILABLE_MODULES = [
    'chromadb',
    'langchain', 
    'langchain_core'
]

__all__ = ['AVAILABLE_MODULES']