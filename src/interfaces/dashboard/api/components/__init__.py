"""Dashboard API Components package."""

# Import from the existing hitl_widgets module in the components directory
try:
    from ...components import hitl_widgets
except ImportError:
    hitl_widgets = None

__all__ = ["hitl_widgets"]
