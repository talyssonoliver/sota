"""
Claude Code Integration Module

This module provides LangChain-compatible wrappers for Claude Code functionality,
enabling seamless migration from OpenAI while maintaining all existing interfaces.
"""

from .embeddings import ClaudeEmbeddings
from .chat_model import ClaudeChatModel
from .config import ClaudeConfig
from .feature_flags import MigrationFeatureFlags

__all__ = [
    "ClaudeEmbeddings",
    "ClaudeChatModel", 
    "ClaudeConfig",
    "MigrationFeatureFlags"
]

__version__ = "1.0.0"