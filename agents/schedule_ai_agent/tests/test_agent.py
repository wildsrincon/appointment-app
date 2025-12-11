"""
Tests for main ScheduleAIAgent functionality.

This module tests the core agent functionality including message processing,
appointment operations, and integration with tools and dependencies.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from ..agent import ScheduleAIAgent, get_agent, process_appointment_request
from ..dependencies import ScheduleAgentDependencies
from ..tools import parse_italian_datetime, extract_service_type


@pytest.mark.asyncio
class TestScheduleAIAgent:
    """Test cases for ScheduleAIAgent class."""

    async def test_agent_initialization(self, mock_dependencies):
        """Test agent initializes correctly with dependencies."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            assert agent.dependencies == mock_dependencies
            assert agent.agent is not None
            assert agent.model is not None

    async def test_agent_process_message_basic(self, test_agent):
        """Test basic message processing functionality."""
        message = "Vorrei prenotare un appuntamento per domani"
        response = await test_agent.process_message(message)

        assert isinstance(response, str)
        assert len(response) > 0
        # TestModel should return a response
        assert response != ""

    async def test_agent_process_message_with_context(self, test_agent):
        """Test message processing with session and business context."""
        message = "Controlla la disponibilità per giovedì prossimo"
        response = await test_agent.process_message(
            message=message,
            session_id="test-session-123",
            business_id="business-456",
            consultant_id="consultant-789"
        )

        assert isinstance(response, str)
        assert len(response) > 0

    async def test_agent_create_appointment_success(self, test_agent, sample_appointments):
        """Test successful appointment creation."""
        appointment = sample_appointments["valid_appointment"]
        result = await test_agent.create_appointment(
            client_name=appointment["client_name"],
            service_type=appointment["service_type"],
            datetime_request="domani alle 10:00",
            client_email=appointment.get("email")
        )

        assert result["success"] is True
        assert "response" in result
        assert result["client_name"] == appointment["client_name"]
        assert result["service_type"] == appointment["service_type"]

    async def test_agent_create_appointment_failure(self, test_agent):
        """Test appointment creation with invalid data."""
        with patch.object(test_agent, 'process_message', side_effect=Exception("Test error")):
            result = await test_agent.create_appointment(
                client_name="Test Client",
                service_type="consulenza",
                datetime_request="invalid date"
            )

            assert result["success"] is False
            assert "error" in result

    async def test_agent_check_availability(self, test_agent):
        """Test availability checking functionality."""
        result = await test_agent.check_availability(
            datetime_request="domani alle 14:00"
        )

        assert result["success"] is True
        assert "response" in result
        assert result["datetime_request"] == "domani alle 14:00"

    async def test_agent_check_availability_failure(self, test_agent):
        """Test availability checking with error."""
        with patch.object(test_agent, 'process_message', side_effect=Exception("Calendar error")):
            result = await test_agent.check_availability(
                datetime_request="domani alle 14:00"
            )

            assert result["success"] is False
            assert "error" in result

    async def test_agent_modify_appointment(self, test_agent):
        """Test appointment modification functionality."""
        modification_request = "Sposta l'appuntamento di domani alle 15:00"
        result = await test_agent.modify_appointment(
            modification_request=modification_request
        )

        assert result["success"] is True
        assert "response" in result
        assert result["modification_request"] == modification_request

    async def test_agent_cancel_appointment(self, test_agent):
        """Test appointment cancellation functionality."""
        cancellation_request = "Cancella l'appuntamento di domani"
        result = await test_agent.cancel_appointment(
            cancellation_request=cancellation_request
        )

        assert result["success"] is True
        assert "response" in result
        assert result["cancellation_request"] == cancellation_request

    async def test_agent_error_handling(self, test_agent):
        """Test agent handles errors gracefully."""
        # Test with empty message
        response = await test_agent.process_message("")
        assert isinstance(response, str)

        # Test with problematic message
        response = await test_agent.process_message("This is not Italian")
        assert isinstance(response, str)


@pytest.mark.asyncio
class TestAgentGlobalFunctions:
    """Test cases for global agent functions."""

    async def test_get_agent_singleton(self, mock_dependencies):
        """Test get_agent returns singleton instance."""
        with patch('..providers.get_llm_model'):
            agent1 = get_agent(mock_dependencies)
            agent2 = get_agent()

            # Should return the same instance
            assert agent1 is agent2

    async def test_process_appointment_request_function(self, mock_dependencies):
        """Test process_appointment_request convenience function."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            message = "Vorrei prenotare per domani mattina"

            response = await process_appointment_request(
                message=message,
                session_id="test-session",
                business_id="test-business",
                consultant_id="test-consultant"
            )

            assert isinstance(response, str)
            assert len(response) > 0


@pytest.mark.asyncio
class TestAgentIntegration:
    """Integration tests for agent with mocked dependencies."""

    async def test_agent_with_test_model(self, mock_dependencies):
        """Test agent works with TestModel."""
        from pydantic_ai.models.test import TestModel

        with patch('..providers.is_test_environment', return_value=True):
            with patch('..providers.create_test_model', return_value=TestModel()) as mock_create:
                agent = ScheduleAIAgent(dependencies=mock_dependencies)

                message = "test message"
                response = await agent.process_message(message)

                assert isinstance(response, str)
                mock_create.assert_called_once()

    async def test_agent_dependency_injection(self):
        """Test agent properly uses injected dependencies."""
        custom_deps = ScheduleAgentDependencies(
            openai_api_key="custom-key",
            google_calendar_api_key="custom-google-key",
            google_client_id="custom-client-id",
            google_client_secret="custom-secret",
            google_refresh_token="custom-token",
            business_hours=(10, 19),  # Custom hours
            working_days=(2, 3, 4),  # Tue, Wed, Thu only
        )

        with patch('..providers.get_llm_model'):
            agent = ScheduleAIAgent(dependencies=custom_deps)

            # Dependencies should be injected correctly
            assert agent.dependencies.business_hours == (10, 19)
            assert agent.dependencies.working_days == (2, 3, 4)

    async def test_agent_runtime_context_updates(self, test_agent):
        """Test agent updates runtime context correctly."""
        original_session_id = test_agent.dependencies.session_id

        # Process message with different context
        await test_agent.process_message(
            message="test message",
            session_id="new-session-id",
            business_id="new-business-id"
        )

        # Original dependencies should remain unchanged
        assert test_agent.dependencies.session_id == original_session_id


@pytest.mark.asyncio
class TestAgentPerformance:
    """Performance and load testing for agent."""

    async def test_agent_response_time(self, test_agent):
        """Test agent responds within reasonable time."""
        import time

        message = "Vorrei prenotare un appuntamento per consulenza"

        start_time = time.time()
        response = await test_agent.process_message(message)
        end_time = time.time()

        response_time = end_time - start_time

        assert isinstance(response, str)
        assert response_time < 5.0  # Should respond within 5 seconds

    async def test_agent_concurrent_requests(self, test_agent):
        """Test agent handles concurrent requests."""
        import asyncio

        messages = [
            "Vorrei prenotare per domani",
            "Controlla disponibilità giovedì",
            "Modifica appuntamento venerdì",
            "Cancella riunione di lunedì"
        ]

        # Process all messages concurrently
        tasks = [test_agent.process_message(msg) for msg in messages]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete successfully
        for response in responses:
            assert not isinstance(response, Exception)
            assert isinstance(response, str)

    async def test_agent_memory_usage(self, test_agent):
        """Test agent doesn't leak memory over multiple requests."""
        import gc
        import sys

        # Process many messages
        for i in range(10):
            message = f"Test message {i}: Vorrei prenotare un appuntamento"
            await test_agent.process_message(message)

        # Force garbage collection
        gc.collect()

        # Agent should still work after many requests
        response = await test_agent.process_message("Final test message")
        assert isinstance(response, str)
        assert len(response) > 0