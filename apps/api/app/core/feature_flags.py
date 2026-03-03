"""
Feature flag management for controlled feature rollout.

Provides centralized registry and access to feature flags.
"""

import logging
from enum import Enum
from typing import Dict, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class FeatureFlag(str, Enum):
    """
    Registry of all feature flags in the system.
    
    Flags should follow naming convention: FEATURE_NAME
    """
    CONVERSATION_FOLLOWUP = "conversation_followup"
    # Add future feature flags here
    # Example:
    # SSE_STREAMING = "sse_streaming"
    # LEAD_WEBHOOKS = "lead_webhooks"


class FeatureFlagManager:
    """
    Manages feature flag state and provides access methods.
    
    Features are controlled via environment variables in the format:
    FEATURE_{FLAG_NAME}_ENABLED=true|false
    """

    def __init__(self):
        """Initialize feature flag manager."""
        self._cache: Dict[FeatureFlag, bool] = {}
        self._load_flags()

    def _load_flags(self):
        """Load feature flags from settings."""
        for flag in FeatureFlag:
            attr_name = f"feature_{flag.value}_enabled"
            enabled = getattr(settings, attr_name, False)
            self._cache[flag] = enabled
            logger.info(f"Feature flag loaded: {flag.value} = {enabled}")

    def is_enabled(self, flag: FeatureFlag) -> bool:
        """
        Check if a feature flag is enabled.

        Args:
            flag: Feature flag to check

        Returns:
            True if enabled, False otherwise
        """
        return self._cache.get(flag, False)

    def get_all_flags(self) -> Dict[str, bool]:
        """
        Get all feature flags and their states.

        Returns:
            Dictionary mapping flag names to enabled state
        """
        return {flag.value: enabled for flag, enabled in self._cache.items()}


# Global singleton instance
_flag_manager: Optional[FeatureFlagManager] = None


def get_feature_flag_manager() -> FeatureFlagManager:
    """
    Get the global feature flag manager instance.

    Returns:
        FeatureFlagManager singleton instance
    """
    global _flag_manager
    if _flag_manager is None:
        _flag_manager = FeatureFlagManager()
    return _flag_manager


def reset_feature_flag_manager() -> None:
    """Reset cached feature flag manager (useful for tests)."""
    global _flag_manager
    _flag_manager = None


def is_feature_enabled(flag: FeatureFlag) -> bool:
    """
    Convenience function to check if a feature is enabled.

    Args:
        flag: Feature flag to check

    Returns:
        True if enabled, False otherwise
    """
    return get_feature_flag_manager().is_enabled(flag)
