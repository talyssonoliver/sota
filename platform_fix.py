#!/usr/bin/env python3
"""
Platform Module Fix

This module provides a way to preserve the built-in platform module
before our src.platform directory shadows it.
"""

import sys
import os

# Store the original builtin platform module BEFORE adding src/ to path
def preserve_builtin_platform():
    """Preserve the builtin platform module before it gets shadowed."""
    
    # Remove any src paths temporarily to import builtin platform
    original_paths = sys.path.copy()
    src_paths = [p for p in sys.path if 'src' in p.split(os.sep)]
    
    for path in src_paths:
        if path in sys.path:
            sys.path.remove(path)
    
    # Now import the real platform module
    import platform as builtin_platform
    
    # Restore the original sys.path
    sys.path = original_paths
    
    # Store the builtin platform module in sys.modules permanently
    sys.modules['builtin_platform'] = builtin_platform
    sys.modules['platform'] = builtin_platform
    
    return builtin_platform

# Call this before any other imports
builtin_platform = preserve_builtin_platform()