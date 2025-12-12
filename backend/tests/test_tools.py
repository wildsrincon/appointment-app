"""
Tests for tool implementations in Italian Appointment Scheduling AI Agent.

This module tests the core tools including Google Calendar integration,
Italian NLP parsing, appointment validation, and business rule enforcement.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from ..tools import (
    google_calendar_operations,
    italian_appointment_parser,
    appointment_validator,
    parse_italian_datetime,
    extract_service_type,
    mock_google_calendar_create_event,
    mock_google_calendar_check_availability,
    register_tools
)
from ..dependencies import ScheduleAgentDependencies
from pydantic_ai import Agent, RunContext


@pytest.mark.asyncio
class TestGoogleCalendarOperations:
    """Test cases for Google Calendar operations tool."""

    async def test_create_event_success(self, mock_dependencies):
        """Test successful calendar event creation."""
        # Create a test agent with the mock dependencies
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        # Create mock context
        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_create_event') as mock_create:
            mock_create.return_value = {
                "success": True,
                "event_id": "test_event_123",
                "event_data": {"summary": "test event"}
            }

            result = await google_calendar_operations(
                ctx=ctx,
                operation="create",
                title="consulenza - Mario Rossi",
                start_time="2025-01-20T10:00:00",
                duration_minutes=60,
                client_name="Mario Rossi",
                service_type="consulenza"
            )

            assert result["success"] is True
            assert "event_id" in result
            mock_create.assert_called_once()

    async def test_create_event_missing_required_fields(self, mock_dependencies):
        """Test event creation with missing required fields."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        result = await google_calendar_operations(
            ctx=ctx,
            operation="create",
            # Missing required fields: title, start_time, client_name
            duration_minutes=60,
            service_type="consulenza"
        )

        assert result["success"] is False
        assert "required for create operation" in result["error"]

    async def test_check_availability_success(self, mock_dependencies):
        """Test availability checking functionality."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {
                "success": True,
                "available": True,
                "conflicts": []
            }

            result = await google_calendar_operations(
                ctx=ctx,
                operation="check",
                start_time="2025-01-20T10:00:00"
            )

            assert result["success"] is True
            assert result["available"] is True
            assert len(result["conflicts"]) == 0
            mock_check.assert_called_once()

    async def test_check_availability_missing_time(self, mock_dependencies):
        """Test availability checking without start time."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        result = await google_calendar_operations(
            ctx=ctx,
            operation="check"
            # Missing start_time
        )

        assert result["success"] is False
        assert "start_time required" in result["error"]

    async def test_unsupported_operation(self, mock_dependencies):
        """Test handling of unsupported calendar operations."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        result = await google_calendar_operations(
            ctx=ctx,
            operation="delete",  # Not implemented
            title="test"
        )

        assert result["success"] is False
        assert "not yet implemented" in result["error"]

    async def test_calendar_operation_error_handling(self, mock_dependencies):
        """Test error handling in calendar operations."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_create_event', side_effect=Exception("API Error")):
            result = await google_calendar_operations(
                ctx=ctx,
                operation="create",
                title="test",
                start_time="2025-01-20T10:00:00",
                client_name="Test Client"
            )

            assert result["success"] is False
            assert "API Error" in result["error"]


@pytest.mark.asyncio
class TestItalianAppointmentParserTool:
    """Test cases for Italian appointment parser tool."""

    async def test_parser_with_complete_request(self):
        """Test parser with complete appointment request."""
        text = "Vorrei prenotare una consulenza fiscale per domani alle 14:30"

        result = italian_appointment_parser(text=text)

        assert result["success"] is True
        assert result["service_type"] == "consulenza_fiscale"
        assert result["duration_minutes"] == 90
        assert "datetime" in result
        assert result["time"] == "14:30"

    async def test_parser_with_minimal_request(self):
        """Test parser with minimal appointment request."""
        text = "appunto domani"

        result = italian_appointment_parser(text=text)

        assert result["success"] is True
        assert result["service_type"] == "appunto"
        assert result["duration_minutes"] == 30

    async def test_parser_with_context_date(self):
        """Test parser with reference date context."""
        text = "domani alle 10:00"
        context_date = "2025-01-20T10:00:00"  # Monday

        result = italian_appointment_parser(text=text, context_date=context_date)

        assert result["success"] is True
        assert result["date"] == "2025-01-21"  # Tuesday
        assert result["time"] == "10:00"

    async def test_parser_error_handling(self):
        """Test parser error handling."""
        # Test with problematic input
        result = italian_appointment_parser(text="")

        # Should handle gracefully
        assert isinstance(result, dict)
        assert "success" in result


@pytest.mark.asyncio
class TestAppointmentValidator:
    """Test cases for appointment validation tool."""

    async def test_validate_business_hours_success(self, mock_dependencies):
        """Test validation during business hours."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {"success": True, "available": True}

            result = await appointment_validator(
                ctx=ctx,
                start_time="2025-01-20T10:00:00",  # Monday 10 AM
                duration_minutes=60,
                service_type="consulenza"
            )

            assert result["success"] is True
            assert result["valid"] is True
            assert result["business_hours_valid"] is True
            assert result["working_day_valid"] is True
            assert result["duration_valid"] is True

    async def test_validate_outside_business_hours(self, mock_dependencies):
        """Test validation outside business hours."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        result = await appointment_validator(
            ctx=ctx,
            start_time="2025-01-20T19:00:00",  # Monday 7 PM (after hours)
            duration_minutes=30,
            service_type="appunto"
        )

        assert result["success"] is True
        assert result["valid"] is False
        assert result["business_hours_valid"] is False
        assert "Orario non lavorativo" in result["errors"][0]

    async def test_validate_weekend(self, mock_dependencies):
        """Test validation for weekend appointments."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        result = await appointment_validator(
            ctx=ctx,
            start_time="2025-01-25T10:00:00",  # Saturday
            duration_minutes=30,
            service_type="appunto"
        )

        assert result["success"] is True
        assert result["valid"] is False
        assert result["working_day_valid"] is False
        assert "Giorno non lavorativo" in result["errors"][0]

    async def test_validate_invalid_duration(self, mock_dependencies):
        """Test validation with invalid duration."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        result = await appointment_validator(
            ctx=ctx,
            start_time="2025-01-20T10:00:00",
            duration_minutes=10,  # Too short (minimum 15)
            service_type="appunto"
        )

        assert result["success"] is True
        assert result["valid"] is False
        assert result["duration_valid"] is False
        assert "Durata non valida" in result["errors"][0]

    async def test_validate_calendar_conflict(self, mock_dependencies):
        """Test validation with calendar conflicts."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {
                "success": True,
                "available": False,
                "conflicts": [{"reason": "Existing appointment"}]
            }

            result = await appointment_validator(
                ctx=ctx,
                start_time="2025-01-20T10:00:00",
                duration_minutes=60,
                service_type="consulenza"
            )

            assert result["success"] is True
            assert result["valid"] is False
            assert "conflitto con altro appuntamento" in result["errors"][0]

    async def test_validate_datetime_parsing_error(self, mock_dependencies):
        """Test validation with invalid datetime format."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        result = await appointment_validator(
            ctx=ctx,
            start_time="invalid-datetime",
            duration_minutes=30,
            service_type="appunto"
        )

        assert result["success"] is False
        assert result["valid"] is False


class TestMockCalendarFunctions:
    """Test cases for mock calendar functions."""

    async def test_mock_create_event(self):
        """Test mock calendar event creation."""
        result = await mock_google_calendar_create_event(
            title="Test Event",
            start_time="2025-01-20T10:00:00",
            duration_minutes=60,
            client_name="Test Client",
            service_type="consulenza"
        )

        assert result["success"] is True
        assert "event_id" in result
        assert "event_data" in result
        assert result["event_data"]["summary"] == "Test Event"
        assert result["event_data"]["start"]["dateTime"] == "2025-01-20T10:00:00"
        assert result["event_data"]["end"]["dateTime"] == "2025-01-20T11:00:00"

    async def test_mock_check_availability_available(self):
        """Test mock availability check when available."""
        result = await mock_google_calendar_check_availability(
            start_time="2025-01-20T12:00:00",
            end_time="2025-01-20T13:00:00"
        )

        assert result["success"] is True
        assert result["available"] is True
        assert len(result["conflicts"]) == 0

    async def test_mock_check_availability_conflict(self):
        """Test mock availability check with conflicts."""
        result = await mock_google_calendar_check_availability(
            start_time="2025-01-20T10:30:00",
            end_time="2025-01-20T11:30:00"
        )

        # This should conflict with the mock busy time 10:00-11:00
        assert result["success"] is True
        assert result["available"] is False
        assert len(result["conflicts"]) > 0


class TestToolRegistration:
    """Test cases for tool registration system."""

    def test_register_tools_count(self):
        """Test that correct number of tools are registered."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)

        initial_tool_count = len(agent.tools)
        register_tools(agent, ScheduleAgentDependencies)
        final_tool_count = len(agent.tools)

        # Should have added 3 tools
        assert final_tool_count - initial_tool_count == 3

    def test_tool_names(self):
        """Test that expected tool names are registered."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        tool_names = [tool.name for tool in agent.tools]
        expected_tools = [
            "google_calendar_operations",
            "italian_appointment_parser",
            "appointment_validator"
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_tool_signatures(self):
        """Test that tools have correct function signatures."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        # Check that tools are callable and have expected signatures
        for tool in agent.tools:
            assert callable(tool.function)
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')


@pytest.mark.asyncio
class TestToolIntegration:
    """Integration tests for tool combinations."""

    async def test_parse_then_validate_workflow(self, mock_dependencies):
        """Test workflow: parse Italian request, then validate."""
        # Step 1: Parse Italian request
        italian_text = "Vorrei una consulenza per domani alle 10:00"
        parse_result = italian_appointment_parser(text=italian_text)

        assert parse_result["success"] is True
        assert "datetime" in parse_result

        # Step 2: Validate the parsed appointment
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {"success": True, "available": True}

            validate_result = await appointment_validator(
                ctx=ctx,
                start_time=parse_result["datetime"],
                duration_minutes=parse_result["duration_minutes"],
                service_type=parse_result["service_type"]
            )

            assert validate_result["success"] is True
            assert validate_result["valid"] is True

    async def test_validate_then_create_workflow(self, mock_dependencies):
        """Test workflow: validate appointment, then create calendar event."""
        mock_model = Mock()
        agent = Agent(mock_model, deps_type=ScheduleAgentDependencies)
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=RunContext)
        ctx.deps = mock_dependencies

        # Mock both calendar functions
        with patch('..tools.mock_google_calendar_check_availability') as mock_check, \
             patch('..tools.mock_google_calendar_create_event') as mock_create:

            mock_check.return_value = {"success": True, "available": True}
            mock_create.return_value = {
                "success": True,
                "event_id": "test_workflow_event"
            }

            # Step 1: Validate
            validate_result = await appointment_validator(
                ctx=ctx,
                start_time="2025-01-20T10:00:00",
                duration_minutes=60,
                service_type="consulenza"
            )

            assert validate_result["valid"] is True

            # Step 2: Create calendar event
            create_result = await google_calendar_operations(
                ctx=ctx,
                operation="create",
                title="consulenza - Test Client",
                start_time="2025-01-20T10:00:00",
                duration_minutes=60,
                client_name="Test Client",
                service_type="consulenza"
            )

            assert create_result["success"] is True
            assert create_result["event_id"] == "test_workflow_event"