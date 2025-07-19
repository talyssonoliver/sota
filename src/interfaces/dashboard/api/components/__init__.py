"""Dashboard API Components package."""

# Import from the existing hitl_widgets module in the components directory
try:
    from ...components.hitl_widgets import *
except ImportError:
    pass

    # Fallback if import fails
    pass

__all__ = ["hitl_widgets"]
