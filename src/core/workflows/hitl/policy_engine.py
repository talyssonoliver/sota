"""
HITL Policy Engine

Core policy engine for managing checkpoints and approvals.
"""

import logging
from typing import Any, Dict, List, Optional

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from .models import HITLCheckpoint

logger = logging.getLogger(__name__)


class HITLPolicyEngine:
    """Core HITL policy engine for managing checkpoints and approvals"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize HITL policy engine"""
        self.config_path = config_path or "config/hitl_policies.yaml"
        self.policies = self._load_policies()
        self.checkpoints: Dict[str, HITLCheckpoint] = {}
        self.audit_log: List[Dict[str, Any]] = []

        # Initialize storage directories
        from config.build_paths import HITL_STORAGE_DIR

        self.storage_dir = HITL_STORAGE_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Initialize notification system
        self.notification_handlers = []
        self._init_notification_handlers()

        logger.info(
            f"HITL Policy Engine initialized with {len(self.policies)} policy groups"
        )

    def _load_policies(self) -> Dict[str, Any]:
        """Load HITL policies from configuration file"""
        if not YAML_AVAILABLE:
            logger.warning("YAML not available, using default policies")
            return self._get_default_policies()

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"HITL policies file not found: {self.config_path}")
            return self._get_default_policies()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing HITL policies: {e}")
            return self._get_default_policies()
        except Exception as e:
            logger.error(f"Unexpected error loading policies: {e}")
            return self._get_default_policies()

    def _get_default_policies(self) -> Dict[str, Any]:
        """Get default HITL policies as fallback"""
        return {
            "hitl_policies": {
                "global_settings": {
                    "enabled": True,
                    "default_timeout_hours": 24,
                    "auto_escalation_enabled": True,
                    "notification_channels": ["dashboard"],
                },
                "checkpoint_triggers": {
                    "output_evaluation": {
                        "enabled": True,
                        "conditions": ["critical_service_changes"],
                        "required_approvals": 1,
                        "reviewers": ["Technical Lead"],
                    }
                },
            }
        }

    def _init_notification_handlers(self):
        """Initialize notification handlers"""
        # Dashboard notification handler
        try:
            from src.core.workflows.notification_handlers import \
                DashboardNotificationHandler

            self.notification_handlers.append(DashboardNotificationHandler())
        except ImportError:
            logger.warning("Dashboard notification handler not available")

        # Email notification handler (if configured)
        if (
            self.policies.get("hitl_policies", {})
            .get("integrations", {})
            .get("notifications", {})
            .get("email", {})
            .get("enabled")
        ):
            try:
                from src.core.workflows.notification_handlers import \
                    EmailNotificationHandler

                self.notification_handlers.append(EmailNotificationHandler())
            except ImportError:
                logger.warning("Email notification handler not available")

        # Slack notification handler (if configured)
        if (
            self.policies.get("hitl_policies", {})
            .get("integrations", {})
            .get("notifications", {})
            .get("slack", {})
            .get("enabled")
        ):
            try:
                from src.core.workflows.notification_handlers import \
                    SlackNotificationHandler

                self.notification_handlers.append(SlackNotificationHandler())
            except ImportError:
                logger.warning("Slack notification handler not available")

    def _normalize_policy_access(self, *keys):
        """Helper method to access policies with fallback for both config formats"""
        # First try with hitl_policies wrapper (production format)
        result = self.policies
        try:
            for key in ["hitl_policies"] + list(keys):
                result = result[key]
            return result
        except (KeyError, TypeError):
            pass

        # Fallback to direct access (test format)
        result = self.policies
        try:
            for key in keys:
                result = result[key]
            return result
        except (KeyError, TypeError):
            return {}
