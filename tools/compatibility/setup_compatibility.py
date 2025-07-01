"""Setup script for compatibility modules.

This script ensures compatibility modules are available in the Python path
when external libraries are not installed.
"""

import sys
from pathlib import Path

def setup_compatibility_path():
    """Add compatibility modules to Python path."""
    compatibility_dir = Path(__file__).parent
    
    if str(compatibility_dir) not in sys.path:
        sys.path.insert(0, str(compatibility_dir))
        
    # Verify modules are accessible
    try:
        import chromadb
        import langchain
        import langchain_core
        return True
    except ImportError:
        return False

def initialize_compatibility():
    """Initialize all compatibility modules."""
    success = setup_compatibility_path()
    if success:
        print("Compatibility modules initialized successfully")
    else:
        print("Warning: Some compatibility modules may not be available")
    return success

if __name__ == "__main__":
    initialize_compatibility()