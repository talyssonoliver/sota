"""
Agent definitions for the AI Agent System.
These agents are built using CrewAI and connected to their respective tools and prompt templates.
"""

# Import all agent constructors for easy access
from .coordinator import create_coordinator_agent
from .technical import create_technical_lead_agent
from .backend import create_backend_engineer_agent
from .frontend import create_frontend_engineer_agent
from .doc import create_documentation_agent
from .qa import create_qa_agent