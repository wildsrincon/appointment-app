"""
Configuration settings for Italian Appointment Scheduling AI Agent.

This module provides secure configuration management with environment variable support,
API key validation, and business settings for the scheduling agent.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict, field_validator
from dotenv import load_dotenv
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class ScheduleSettings(BaseSettings):
    """Configuration for Italian appointment scheduling AI agent."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # LLM Configuration (REQUIRED)
    llm_provider: str = Field(default="openai", description="LLM provider")
    llm_api_key: str = Field(..., description="API key for the LLM provider")
    llm_model: str = Field(default="gpt-4o-mini", description="Model name to use")
    llm_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL for the LLM API"
    )

    # Google Calendar Configuration (REQUIRED)
    google_calendar_api_key: str = Field(
        ...,
        description="Google Calendar API key"
    )
    google_calendar_client_id: str = Field(
        ...,
        description="Google OAuth client ID"
    )
    google_calendar_client_secret: str = Field(
        ...,
        description="Google OAuth client secret"
    )
    google_calendar_refresh_token: Optional[str] = Field(
        default=None,
        description="Google OAuth refresh token"
    )
    default_calendar_id: str = Field(
        default="primary",
        description="Default Google Calendar ID"
    )

    # Business Configuration
    default_timezone: str = Field(default="Europe/Rome", description="Default timezone")
    business_hours_start: str = Field(default="09:00", description="Business hours start")
    business_hours_end: str = Field(default="18:00", description="Business hours end")
    working_days: str = Field(default="1,2,3,4,5", description="Working days (Monday=1)")

    # Database Configuration (REQUIRED for production)
    database_url: Optional[str] = Field(
        default=None,
        description="Full database connection URL (overrides other db settings)"
    )
    db_host: str = Field(default="localhost", description="Database host")
    db_port: str = Field(default="5432", description="Database port")
    db_name: str = Field(default="scheduleai", description="Database name")
    db_user: str = Field(default="postgres", description="Database user")
    db_password: str = Field(default="password", description="Database password")
    db_ssl_mode: str = Field(default="prefer", description="Database SSL mode")

    # Application Settings
    app_env: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")

    @field_validator("llm_api_key")
    @classmethod
    def validate_llm_key(cls, v):
        """Ensure LLM API key is not empty."""
        if not v or v.strip() == "":
            raise ValueError("LLM API key cannot be empty")
        return v.strip()

    @field_validator("google_calendar_api_key")
    @classmethod
    def validate_google_key(cls, v):
        """Ensure Google Calendar API key is not empty."""
        if not v or v.strip() == "":
            raise ValueError("Google Calendar API key cannot be empty")
        return v.strip()

    @property
    def working_days_list(self) -> list[int]:
        """Parse working days string to list of integers."""
        try:
            return [int(day.strip()) for day in self.working_days.split(",")]
        except ValueError as e:
            logger.error(f"Invalid working_days format: {self.working_days}")
            return [1, 2, 3, 4, 5]  # Default to Monday-Friday

    @property
    def business_hours_tuple(self) -> tuple[int, int]:
        """Parse business hours to tuple of (start_hour, end_hour)."""
        try:
            start = int(self.business_hours_start.split(":")[0])
            end = int(self.business_hours_end.split(":")[0])
            return (start, end)
        except (ValueError, IndexError) as e:
            logger.error(f"Invalid business hours format: {self.business_hours_start}-{self.business_hours_end}")
            return (9, 18)  # Default to 9-18


def load_settings() -> ScheduleSettings:
    """Load settings with proper error handling and environment loading."""
    try:
        settings = ScheduleSettings()
        # Warn about missing refresh token in production
        if (not settings.google_calendar_refresh_token and
            settings.app_env == "production"):
            logger.warning(
                "Google Calendar refresh token not configured. "
                "Calendar integration will not work without OAuth setup."
            )
        return settings
    except Exception as e:
        error_msg = f"Failed to load settings: {e}"
        if "llm_api_key" in str(e).lower():
            error_msg += "\nMake sure to set LLM_API_KEY in your .env file"
        elif "google_calendar" in str(e).lower():
            error_msg += "\nMake sure to set GOOGLE_CALENDAR_* variables in your .env file"
        raise ValueError(error_msg) from e


# Global settings instance
_settings: Optional[ScheduleSettings] = None


def get_settings() -> ScheduleSettings:
    """Get cached settings instance."""
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


def get_google_calendar_config() -> Dict[str, str]:
    """Get Google Calendar configuration as dictionary."""
    settings = get_settings()
    return {
        "api_key": settings.google_calendar_api_key,
        "client_id": settings.google_calendar_client_id,
        "client_secret": settings.google_calendar_client_secret,
        "refresh_token": settings.google_calendar_refresh_token,
        "default_calendar_id": settings.default_calendar_id
    }