#!/usr/bin/env python3
"""
Orchestration Module - Compatibility Layer

⚠️  DEPRECATED: Use 'from src.core.workflows import ...' instead
"""

import warnings
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

warnings.warn(
    "Importing from 'orchestration' is deprecated. Use 'from src.core.workflows import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

try:
    from src.core.workflows import *
except ImportError as e:
    print(f"Warning: Could not import from new workflows location: {e}")
