"""
Model providers configuration for Italian Appointment Scheduling AI Agent.

This module provides LLM model configuration with support for OpenAI and proper
environment variable integration.
"""

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel

# Handle both relative and absolute imports
try:
    from .settings import get_settings
except ImportError:
    try:
        from settings import get_settings
    except ImportError:
        # Try adding current directory to path
        import os
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        from settings import get_settings
import logging

logger = logging.getLogger(__name__)


def get_llm_model():
    """Get configured LLM model with proper environment loading."""
    settings = get_settings()

    try:
        provider = OpenAIProvider(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key
        )
        model = OpenAIModel(settings.llm_model, provider=provider)

        logger.info(f"Initialized {settings.llm_provider} model: {settings.llm_model}")
        return model

    except Exception as e:
        logger.error(f"Failed to initialize LLM model: {e}")
        raise


def create_test_model():
    """Create test model for development and testing."""
    from pydantic_ai.models.test import TestModel

    logger.info("Using TestModel for development/testing")
    return TestModel()


def is_test_environment() -> bool:
    """Check if running in test environment."""
    settings = get_settings()
    return settings.app_env == "test" or settings.debug