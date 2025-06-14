#!/usr/bin/env python3
"""
Dashboard Module - Compatibility Layer

⚠️  DEPRECATED: Use 'from src.interfaces.dashboard import ...' instead
"""

import warnings
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

warnings.warn(
    "Importing from 'dashboard' is deprecated. Use 'from src.interfaces.dashboard import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

try:
    from src.interfaces.dashboard import *
except ImportError as e:
    print(f"Warning: Could not import from new dashboard location: {e}")
