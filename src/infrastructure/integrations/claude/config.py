"""
Claude Integration Configuration

Manages configuration settings for Claude Code integration including
API settings, model parameters, and feature flags.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ClaudeConfig:
    """Configuration for Claude Code integration."""
    
    # API Configuration
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    
    # Model Configuration
    chat_model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.7
    max_tokens: int = 4096
    
    # Embedding Configuration  
    embedding_model: str = "claude-embedding-v1"  # Placeholder - actual implementation TBD
    embedding_dimensions: int = 1536  # Match OpenAI for compatibility
    batch_size: int = 100
    
    # Performance Configuration
    enable_streaming: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Security Configuration
    enable_pii_detection: bool = True
    enable_content_filtering: bool = True
    
    @classmethod
    def from_environment(cls) -> "ClaudeConfig":
        """Create configuration from environment variables."""
        return cls(
            api_key=os.getenv("CLAUDE_API_KEY"),
            base_url=os.getenv("CLAUDE_BASE_URL"),
            timeout=int(os.getenv("CLAUDE_TIMEOUT", "30")),
            max_retries=int(os.getenv("CLAUDE_MAX_RETRIES", "3")),
            chat_model=os.getenv("CLAUDE_CHAT_MODEL", "claude-3-sonnet-20240229"),
            temperature=float(os.getenv("CLAUDE_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", "4096")),
            embedding_model=os.getenv("CLAUDE_EMBEDDING_MODEL", "claude-embedding-v1"),
            embedding_dimensions=int(os.getenv("CLAUDE_EMBEDDING_DIMENSIONS", "1536")),
            batch_size=int(os.getenv("CLAUDE_BATCH_SIZE", "100")),
            enable_streaming=os.getenv("CLAUDE_ENABLE_STREAMING", "true").lower() == "true",
            enable_caching=os.getenv("CLAUDE_ENABLE_CACHING", "true").lower() == "true",
            cache_ttl=int(os.getenv("CLAUDE_CACHE_TTL", "3600")),
            enable_pii_detection=os.getenv("CLAUDE_ENABLE_PII_DETECTION", "true").lower() == "true",
            enable_content_filtering=os.getenv("CLAUDE_ENABLE_CONTENT_FILTERING", "true").lower() == "true",
        )
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        if not self.api_key:
            logger.error("CLAUDE_API_KEY is required")
            return False
            
        if self.temperature < 0 or self.temperature > 2:
            logger.error(f"Invalid temperature: {self.temperature}. Must be between 0 and 2")
            return False
            
        if self.max_tokens < 1:
            logger.error(f"Invalid max_tokens: {self.max_tokens}. Must be positive")
            return False
            
        if self.embedding_dimensions not in [512, 1024, 1536, 2048]:
            logger.warning(f"Non-standard embedding dimensions: {self.embedding_dimensions}")
            
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "api_key": "***" if self.api_key else None,  # Mask API key
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "chat_model": self.chat_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "embedding_model": self.embedding_model,
            "embedding_dimensions": self.embedding_dimensions,
            "batch_size": self.batch_size,
            "enable_streaming": self.enable_streaming,
            "enable_caching": self.enable_caching,
            "cache_ttl": self.cache_ttl,
            "enable_pii_detection": self.enable_pii_detection,
            "enable_content_filtering": self.enable_content_filtering,
        }


# Global configuration instance
_global_config: Optional[ClaudeConfig] = None


def get_claude_config() -> ClaudeConfig:
    """Get global Claude configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = ClaudeConfig.from_environment()
        if not _global_config.validate():
            logger.warning("Claude configuration validation failed")
    return _global_config


def set_claude_config(config: ClaudeConfig) -> None:
    """Set global Claude configuration instance."""
    global _global_config
    _global_config = config