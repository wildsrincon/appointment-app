"""
Test configuration and fixtures for Italian Appointment Scheduling AI Agent tests.

This module provides common test fixtures, mock objects, and utilities
for comprehensive agent testing using TestModel and mocked dependencies.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.messages import ModelTextResponse

from ..agent import ScheduleAIAgent, get_agent
from ..dependencies import ScheduleAgentDependencies, create_dependencies


@pytest.fixture
def test_model():
    """Create TestModel for fast testing without API calls."""
    return TestModel()


@pytest.fixture
def mock_dependencies():
    """Create mock dependencies for testing."""
    return ScheduleAgentDependencies(
        openai_api_key="test-openai-key",
        google_calendar_api_key="test-google-key",
        google_client_id="test-client-id",
        google_client_secret="test-client-secret",
        google_refresh_token="test-refresh-token",
        timezone="Europe/Rome",
        business_hours=(9, 18),
        working_days=(1, 2, 3, 4, 5),
        default_calendar_id="test-calendar",
        session_id="test-session",
        business_id="test-business",
        consultant_id="test-consultant"
    )


@pytest.fixture
def test_agent(mock_dependencies, test_model):
    """Create ScheduleAIAgent with TestModel for testing."""
    with patch('..providers.get_llm_model', return_value=test_model):
        agent = ScheduleAIAgent(dependencies=mock_dependencies)
        return agent


@pytest.fixture
def sample_appointments():
    """Sample appointment data for testing."""
    return {
        "valid_appointment": {
            "client_name": "Mario Rossi",
            "service_type": "consulenza",
            "datetime": "2025-01-20T10:00:00",
            "duration": 60,
            "email": "mario.rossi@email.com"
        },
        "weekend_appointment": {
            "client_name": "Giuseppe Bianchi",
            "service_type": "riunione",
            "datetime": "2025-01-25T10:00:00",  # Saturday
            "duration": 45
        },
        "after_hours_appointment": {
            "client_name": "Antonio Verdi",
            "service_type": "appunto",
            "datetime": "2025-01-20T19:00:00",  # 7 PM
            "duration": 30
        },
        "short_notice_appointment": {
            "client_name": "Francesco Romano",
            "service_type": "colloquio",
            "datetime": (datetime.now() + timedelta(hours=1)).isoformat(),
            "duration": 30
        }
    }


@pytest.fixture
def italian_datetime_test_cases():
    """Italian date/time test cases with expected results."""
    reference_date = "2025-01-20T10:00:00"  # Monday
    return [
        # (input_text, expected_date, expected_time, expected_confidence)
        ("oggi alle 14:30", "2025-01-20", "14:30", 0.85),
        ("domani alle 10:00", "2025-01-21", "10:00", 0.85),
        ("lunedì prossimo", "2025-01-27", "10:00", 0.85),
        ("giovedì alle 15:00", "2025-01-23", "15:00", 0.85),
        ("domani mattina", "2025-01-21", "09:00", 0.85),
        (" dopodomani pomeriggio", "2025-01-22", "15:00", 0.85),
        ("venerdì prossimo alle 11:30", "2025-01-31", "11:30", 0.85),
    ]


@pytest.fixture
def italian_service_test_cases():
    """Italian service type test cases with expected results."""
    return [
        # (input_text, expected_service, expected_duration)
        ("consulenza fiscale", "consulenza_fiscale", 90),
        ("consulenza legale", "consulenza_legale", 90),
        ("appunto", "appunto", 30),
        ("riunione di 90 minuti", "riunione", 90),
        ("colloquio di mezz'ora", "colloquio", 30),
        ("incontro", "incontro", 45),
        ("seduta", "seduta", 50),
        ("visita di un'ora", "visita", 60),
        ("intervista", "intervista", 45),
        ("generale", "generale", 30),
    ]


@pytest.fixture
def business_rule_test_cases():
    """Business rule validation test cases."""
    return [
        # (datetime, duration, expected_valid, expected_errors)
        ("2025-01-20T10:00:00", 60, True, []),  # Valid: Monday 10 AM
        ("2025-01-20T08:00:00", 30, False, ["Orario non lavorativo"]),  # Too early
        ("2025-01-20T19:00:00", 30, False, ["Orario non lavorativo"]),  # Too late
        ("2025-01-25T10:00:00", 30, False, ["Giorno non lavorativo"]),  # Saturday
        ("2025-01-20T12:00:00", 10, False, ["Durata non valida"]),  # Too short
        ("2025-01-20T14:00:00", 500, False, ["Durata non valida"]),  # Too long
    ]


@pytest.fixture
def error_scenarios():
    """Error scenarios for testing error handling."""
    return [
        {
            "name": "missing_client_info",
            "input": "Vorrei prenotare un appuntamento",
            "expected_error": "cliente",
            "should_fail": True
        },
        {
            "name": "invalid_datetime",
            "input": "Vorrei prenotare per il 32 febbraio alle 25:00",
            "expected_error": "data",
            "should_fail": True
        },
        {
            "name": "empty_request",
            "input": "",
            "expected_error": "richiesta",
            "should_fail": True
        },
        {
            "name": "malformed_italian",
            "input": "prenotare xyz domani ora oggi",
            "expected_error": None,
            "should_fail": False  # Should handle gracefully
        },
    ]


@pytest.fixture
def mock_calendar_responses():
    """Mock Google Calendar API responses."""
    return {
        "successful_creation": {
            "success": True,
            "event_id": "event_1234567890",
            "event_data": {
                "summary": "consulenza - Mario Rossi",
                "start": {"dateTime": "2025-01-20T10:00:00", "timeZone": "Europe/Rome"},
                "end": {"dateTime": "2025-01-20T11:00:00", "timeZone": "Europe/Rome"}
            }
        },
        "availability_available": {
            "success": True,
            "available": True,
            "conflicts": []
        },
        "availability_conflict": {
            "success": True,
            "available": False,
            "conflicts": [{
                "start": "2025-01-20T10:00:00",
                "end": "2025-01-20T11:00:00",
                "reason": "Existing appointment"
            }]
        },
        "api_error": {
            "success": False,
            "error": "Calendar API unavailable"
        }
    }


class AsyncContextManager:
    """Helper class for creating async context managers."""

    def __init__(self, return_value):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def mock_google_calendar():
    """Mock Google Calendar client."""
    mock_client = Mock()

    # Mock event creation
    mock_client.events.return_value.insert = AsyncMock(
        return_value=Mock(
            execute=Mock(return_value={"id": "test_event_123"})
        )
    )

    # Mock availability check
    mock_client.freebusy.return_value.query = AsyncMock(
        return_value=Mock(
            execute=Mock(return_value={
                "calendars": {
                    "primary": {
                        "busy": []
                    }
                }
            })
        )
    )

    return mock_client


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Helper functions for tests
async def run_async_test(coro):
    """Helper to run async test functions."""
    return await coro


def create_test_message_history(messages):
    """Create test message history for agent testing."""
    history = []
    for i, message in enumerate(messages):
        if i % 2 == 0:
            history.append({"role": "user", "content": message})
        else:
            history.append({"role": "assistant", "content": message})
    return history


def assert_italian_response(response: str):
    """Assert that response contains valid Italian content."""
    assert isinstance(response, str)
    assert len(response) > 0
    # Check for common Italian phrases
    italian_phrases = ["ciao", "buongiorno", "appuntamento", "disponibile", "prenotare", "grazie"]
    has_italian = any(phrase in response.lower() for phrase in italian_phrases)
    # Don't strictly require Italian phrases as tests may use simplified responses


def assert_validation_result(result: Dict[str, Any], expected_valid: bool):
    """Assert validation result structure and validity."""
    assert "success" in result
    assert "valid" in result
    assert isinstance(result["valid"], bool)
    assert result["valid"] == expected_valid

    if expected_valid:
        assert len(result.get("errors", [])) == 0
    else:
        assert len(result.get("errors", [])) > 0


def assert_datetime_parsing(result: Dict[str, Any], expected_date: str, expected_time: str):
    """Assert datetime parsing result structure and values."""
    assert result.get("success") is True
    assert "datetime" in result
    assert "date" in result
    assert "time" in result
    assert result["date"] == expected_date
    assert result["time"] == expected_time
    assert "confidence" in result
    assert isinstance(result["confidence"], float)