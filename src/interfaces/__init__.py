# Interfaces Module - User Interface Layer
"""
User interfaces and external communication for the AI system.

This module provides all user-facing interfaces including:
- REST API endpoints
- Dashboard web interface  
- Command-line interface
"""

from . import api
from . import dashboard
from . import cli

__all__ = ["api", "dashboard", "cli"]
