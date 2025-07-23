"""
Migration Feature Flags

Controls the gradual migration from OpenAI to Claude Code by enabling
component-level feature flags for safe rollout and instant rollback.
"""

import os
from typing import Dict, Set, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MigrationComponent(Enum):
    """Components that can be migrated to Claude."""
    EMBEDDINGS = "claude_embeddings"
    CHAT_MODEL = "claude_chat"
    MEMORY_ENGINE = "claude_memory"
    AGENTS = "claude_agents"
    RETRIEVAL_QA = "claude_retrieval_qa"
    ALL = "claude_all"


class MigrationFeatureFlags:
    """Feature flags for controlling Claude migration rollout."""
    
    def __init__(self):
        self._flags: Dict[str, bool] = {}
        self._load_from_environment()
    
    def _load_from_environment(self) -> None:
        """Load feature flags from environment variables."""
        # Individual component flags
        for component in MigrationComponent:
            env_var = f"CLAUDE_ENABLE_{component.value.upper().replace('CLAUDE_', '')}"
            self._flags[component.value] = os.getenv(env_var, "false").lower() == "true"
        
        # Master flag overrides individual flags
        if os.getenv("CLAUDE_ENABLE_ALL", "false").lower() == "true":
            for component in MigrationComponent:
                self._flags[component.value] = True
        
        # Emergency disable flag overrides everything
        if os.getenv("CLAUDE_DISABLE_ALL", "false").lower() == "true":
            for component in MigrationComponent:
                self._flags[component.value] = False
    
    def is_enabled(self, component: MigrationComponent) -> bool:
        """Check if a component migration is enabled."""
        return self._flags.get(component.value, False)
    
    def enable(self, component: MigrationComponent) -> None:
        """Enable a component migration."""
        self._flags[component.value] = True
        logger.info(f"Enabled Claude migration for {component.value}")
    
    def disable(self, component: MigrationComponent) -> None:
        """Disable a component migration."""
        self._flags[component.value] = False
        logger.info(f"Disabled Claude migration for {component.value}")
    
    def enable_all(self) -> None:
        """Enable all component migrations."""
        for component in MigrationComponent:
            self._flags[component.value] = True
        logger.info("Enabled Claude migration for all components")
    
    def disable_all(self) -> None:
        """Disable all component migrations (emergency rollback)."""
        for component in MigrationComponent:
            self._flags[component.value] = False
        logger.warning("Disabled Claude migration for all components (emergency rollback)")
    
    def get_enabled_components(self) -> Set[MigrationComponent]:
        """Get set of currently enabled components."""
        return {
            component for component in MigrationComponent 
            if self._flags.get(component.value, False)
        }
    
    def get_status(self) -> Dict[str, bool]:
        """Get current status of all feature flags."""
        return self._flags.copy()
    
    def validate_configuration(self) -> bool:
        """Validate feature flag configuration for safety."""
        enabled_components = self.get_enabled_components()
        
        # Check for dangerous combinations
        if MigrationComponent.AGENTS in enabled_components and \
           MigrationComponent.CHAT_MODEL not in enabled_components:
            logger.error("Cannot enable agents without chat model migration")
            return False
        
        if MigrationComponent.MEMORY_ENGINE in enabled_components and \
           MigrationComponent.EMBEDDINGS not in enabled_components:
            logger.error("Cannot enable memory engine without embeddings migration")
            return False
        
        if MigrationComponent.RETRIEVAL_QA in enabled_components and \
           (MigrationComponent.EMBEDDINGS not in enabled_components or
            MigrationComponent.CHAT_MODEL not in enabled_components):
            logger.error("Cannot enable retrieval QA without both embeddings and chat model migration")
            return False
        
        return True


# Global feature flags instance
_global_flags: Optional[MigrationFeatureFlags] = None


def get_migration_flags() -> MigrationFeatureFlags:
    """Get global migration feature flags instance."""
    global _global_flags
    if _global_flags is None:
        _global_flags = MigrationFeatureFlags()
        if not _global_flags.validate_configuration():
            logger.warning("Migration feature flags validation failed")
    return _global_flags


def set_migration_flags(flags: MigrationFeatureFlags) -> None:
    """Set global migration feature flags instance."""
    global _global_flags
    _global_flags = flags


# Convenience functions for common checks
def should_use_claude_embeddings() -> bool:
    """Check if Claude embeddings should be used."""
    return get_migration_flags().is_enabled(MigrationComponent.EMBEDDINGS)


def should_use_claude_chat() -> bool:
    """Check if Claude chat model should be used."""
    return get_migration_flags().is_enabled(MigrationComponent.CHAT_MODEL)


def should_use_claude_memory() -> bool:
    """Check if Claude memory engine should be used."""
    return get_migration_flags().is_enabled(MigrationComponent.MEMORY_ENGINE)


def should_use_claude_agents() -> bool:
    """Check if Claude agents should be used."""
    return get_migration_flags().is_enabled(MigrationComponent.AGENTS)


def should_use_claude_retrieval_qa() -> bool:
    """Check if Claude retrieval QA should be used."""
    return get_migration_flags().is_enabled(MigrationComponent.RETRIEVAL_QA)