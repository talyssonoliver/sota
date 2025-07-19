"""
HITL Core Engine

Main HITL engine class that brings together all components.
"""

from .policy_engine import HITLPolicyEngine

# Alias for backward compatibility
HITLEngine = HITLPolicyEngine
