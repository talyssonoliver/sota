"""HITL Widgets for Dashboard API Components.

This module provides access to the HITL widgets from the main components directory.
"""

# Import all widgets from the main components directory
try:
    from ...components.hitl_widgets import *
    # Fallback implementation if main widgets not available
    class HITLWidget:
        """Basic HITL widget implementation."""
        def __init__(self, widget_id, title):
            self.widget_id = widget_id
            self.title = title
            self.data = {}
        
        def update_data(self, data):
            self.data = data
        
        def render(self):
            return {
                "id": self.widget_id,
                "title": self.title,
                "data": self.data
            }
except ImportError:
    pass

# Re-export for api.components access
__all__ = ['HITLWidget']