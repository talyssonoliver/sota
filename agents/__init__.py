#!/usr/bin/env python3
"""
Agents Module - Compatibility Layer

This module provides backward compatibility for imports while
the system migrates to the new src/core/agents/ structure.

⚠️  DEPRECATED: Use 'from src.core.agents import ...' instead
"""

import warnings
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Issue deprecation warning
warnings.warn(
    "Importing from 'agents' is deprecated. Use 'from src.core.agents import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new location
try:
    from src.core.agents import *
except ImportError as e:
    print(f"Warning: Could not import from new agents location: {e}")
    # Fallback to empty module
    pass
from .testagent import create_testagent_agent
