"""
Dependencies for Italian Appointment Scheduling AI Agent.

This module defines the dependency injection structure for the agent,
including Google Calendar integration, database connections, and business context.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any

# Handle both relative and absolute imports
try:
    from .settings import get_settings, get_google_calendar_config
except ImportError:
    try:
        from settings import get_settings, get_google_calendar_config
    except ImportError:
        # Try adding current directory to path
        import os
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        from settings import get_settings, get_google_calendar_config
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScheduleAgentDependencies:
    """Dependencies for appointment scheduling agent execution."""

    # API Credentials (required)
    openai_api_key: str
    google_calendar_api_key: str
    google_client_id: str
    google_client_secret: str
    google_refresh_token: str

    # Business Configuration (with defaults)
    timezone: str = "Europe/Rome"
    business_hours: tuple[int, int] = (9, 18)
    working_days: tuple[int, ...] = (1, 2, 3, 4, 5)
    default_calendar_id: str = "primary"

    # Runtime Context (optional)
    session_id: Optional[str] = None
    business_id: Optional[str] = None
    consultant_id: Optional[str] = None

    # External Clients (initialized lazily)
    _google_client: Optional[Any] = field(default=None, init=False, repr=False)
    _db_client: Optional[Any] = field(default=None, init=False, repr=False)

    @classmethod
    def from_settings(cls, **overrides) -> "ScheduleAgentDependencies":
        """Create dependencies from settings with optional overrides."""
        settings = get_settings()
        google_config = get_google_calendar_config()

        return cls(
            openai_api_key=settings.llm_api_key,
            google_calendar_api_key=google_config["api_key"],
            google_client_id=google_config["client_id"],
            google_client_secret=google_config["client_secret"],
            google_refresh_token=google_config["refresh_token"],
            timezone=settings.default_timezone,
            business_hours=settings.business_hours_tuple,
            working_days=tuple(settings.working_days_list),
            default_calendar_id=google_config["default_calendar_id"],
            **overrides
        )


def create_dependencies(**overrides) -> ScheduleAgentDependencies:
    """Create dependencies instance with proper configuration loading."""
    try:
        return ScheduleAgentDependencies.from_settings(**overrides)
    except Exception as e:
        logger.error(f"Failed to create dependencies: {e}")
        raise