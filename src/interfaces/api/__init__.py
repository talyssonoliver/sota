#!/usr/bin/env python3
"""
API Module - Compatibility Layer

⚠️  DEPRECATED: Use 'from src.interfaces.api import ...' instead
"""

import warnings
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

warnings.warn(
    "Importing from 'api' is deprecated. Use 'from src.interfaces.api import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

try:
    from src.interfaces.api import *
except ImportError as e:
    print(f"Warning: Could not import from new api location: {e}")
