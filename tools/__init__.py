"""Tools package for the AI system."""

import sys
from pathlib import Path

# Add compatibility modules to Python path for external library support
compatibility_path = Path(__file__).parent / "compatibility"
if str(compatibility_path) not in sys.path:
    sys.path.insert(0, str(compatibility_path))

__all__ = []
