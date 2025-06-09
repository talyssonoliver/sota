"""
Tools package initialization.
This makes the tools directory a proper Python package.
"""

import os

# Conditional imports to handle missing dependencies during testing
if os.environ.get("TESTING", "0") != "1":
    try:
        # Import key tools to expose at package level
        from tools.base_tool import ArtesanatoBaseTool
        from tools.tool_loader import (get_tools_for_agent, load_all_tools,
                                       load_tool_config)
    except ImportError:
        # Gracefully handle missing dependencies in test environments
        pass
else:
    # In testing mode, skip problematic imports
    pass