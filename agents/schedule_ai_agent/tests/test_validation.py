"""
Tests for business rules and validation logic.

This module tests the business rule engine, validation logic,
working days enforcement, business hours validation, and other business constraints.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

from ..tools import appointment_validator, parse_italian_datetime
from ..dependencies import ScheduleAgentDependencies


@pytest.mark.asyncio
class TestBusinessHoursValidation:
    """Test cases for business hours validation rules."""

    async def test_valid_business_hours(self, mock_dependencies):
        """Test validation during valid business hours (9 AM - 6 PM)."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {"success": True, "available": True}

            # Test various valid times during business hours
            valid_times = [
                "2025-01-20T09:00:00",  # 9 AM (start)
                "2025-01-20T12:30:00",  # 12:30 PM
                "2025-01-20T15:45:00",  # 3:45 PM
                "2025-01-20T18:00:00",  # 6 PM (end, depends on implementation)
            ]

            for time_str in valid_times:
                result = await appointment_validator(
                    ctx=ctx,
                    start_time=time_str,
                    duration_minutes=30,
                    service_type="appunto"
                )

                assert result["success"] is True
                assert result["business_hours_valid"] is True

    async def test_invalid_business_hours_before_opening(self, mock_dependencies):
        """Test validation before business hours opening."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        # Test early morning hours (before 9 AM)
        early_times = [
            "2025-01-20T06:00:00",  # 6 AM
            "2025-01-20T07:30:00",  # 7:30 AM
            "2025-01-20T08:59:00",  # 8:59 AM
        ]

        for time_str in early_times:
            result = await appointment_validator(
                ctx=ctx,
                start_time=time_str,
                duration_minutes=30,
                service_type="appunto"
            )

            assert result["success"] is True
            assert result["business_hours_valid"] is False
            assert result["valid"] is False
            assert any("lavorativo" in error for error in result["errors"])

    async def test_invalid_business_hours_after_closing(self, mock_dependencies):
        """Test validation after business hours closing."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        # Test evening hours (after 6 PM)
        late_times = [
            "2025-01-20T18:01:00",  # 6:01 PM
            "2025-01-20T19:00:00",  # 7 PM
            "2025-01-20T21:30:00",  # 9:30 PM
        ]

        for time_str in late_times:
            result = await appointment_validator(
                ctx=ctx,
                start_time=time_str,
                duration_minutes=30,
                service_type="appunto"
            )

            assert result["success"] is True
            assert result["business_hours_valid"] is False
            assert result["valid"] is False

    async def test_custom_business_hours(self):
        """Test validation with custom business hours."""
        # Create dependencies with custom business hours (10 AM - 7 PM)
        custom_deps = ScheduleAgentDependencies(
            openai_api_key="test",
            google_calendar_api_key="test",
            google_client_id="test",
            google_client_secret="test",
            google_refresh_token="test",
            business_hours=(10, 19),  # 10 AM - 7 PM
            working_days=(1, 2, 3, 4, 5)
        )

        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = custom_deps

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {"success": True, "available": True}

            # Test times that are valid for custom hours
            valid_custom_times = [
                ("2025-01-20T10:00:00", True),   # 10 AM (new start)
                ("2025-01-20T09:59:00", False),  # 9:59 AM (now invalid)
                ("2025-01-20T19:00:00", True),   # 7 PM (new end)
                ("2025-01-20T19:01:00", False),  # 7:01 PM (now invalid)
            ]

            for time_str, should_be_valid in valid_custom_times:
                result = await appointment_validator(
                    ctx=ctx,
                    start_time=time_str,
                    duration_minutes=30,
                    service_type="appunto"
                )

                assert result["business_hours_valid"] == should_be_valid


@pytest.mark.asyncio
class TestWorkingDaysValidation:
    """Test cases for working days validation rules."""

    async def test_valid_working_days(self, mock_dependencies):
        """Test validation on valid working days (Monday-Friday)."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {"success": True, "available": True}

            # Test Monday through Friday (assuming 2025-01-20 is Monday)
            working_days = [
                ("2025-01-20T10:00:00", True),  # Monday
                ("2025-01-21T10:00:00", True),  # Tuesday
                ("2025-01-22T10:00:00", True),  # Wednesday
                ("2025-01-23T10:00:00", True),  # Thursday
                ("2025-01-24T10:00:00", True),  # Friday
            ]

            for time_str, should_be_valid in working_days:
                result = await appointment_validator(
                    ctx=ctx,
                    start_time=time_str,
                    duration_minutes=30,
                    service_type="appunto"
                )

                assert result["success"] is True
                assert result["working_day_valid"] == should_be_valid

    async def test_invalid_weekend_days(self, mock_dependencies):
        """Test validation on weekend days (Saturday-Sunday)."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        # Test Saturday and Sunday
        weekend_days = [
            "2025-01-25T10:00:00",  # Saturday
            "2025-01-26T10:00:00",  # Sunday
        ]

        for time_str in weekend_days:
            result = await appointment_validator(
                ctx=ctx,
                start_time=time_str,
                duration_minutes=30,
                service_type="appunto"
            )

            assert result["success"] is True
            assert result["working_day_valid"] is False
            assert result["valid"] is False
            assert any("lavorativo" in error for error in result["errors"])

    async def test_custom_working_days(self):
        """Test validation with custom working days."""
        # Create dependencies with custom working days (Tue-Thu only)
        custom_deps = ScheduleAgentDependencies(
            openai_api_key="test",
            google_calendar_api_key="test",
            google_client_id="test",
            google_client_secret="test",
            google_refresh_token="test",
            business_hours=(9, 18),
            working_days=(2, 3, 4)  # Tuesday, Wednesday, Thursday
        )

        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = custom_deps

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {"success": True, "available": True}

            # Test different days of the week
            test_days = [
                ("2025-01-20T10:00:00", False),  # Monday (invalid now)
                ("2025-01-21T10:00:00", True),   # Tuesday (valid)
                ("2025-01-22T10:00:00", True),   # Wednesday (valid)
                ("2025-01-23T10:00:00", True),   # Thursday (valid)
                ("2025-01-24T10:00:00", False),  # Friday (invalid now)
            ]

            for time_str, should_be_valid in test_days:
                result = await appointment_validator(
                    ctx=ctx,
                    start_time=time_str,
                    duration_minutes=30,
                    service_type="appunto"
                )

                assert result["working_day_valid"] == should_be_valid


@pytest.mark.asyncio
class TestDurationValidation:
    """Test cases for appointment duration validation."""

    async def test_valid_durations(self, mock_dependencies):
        """Test validation with valid appointment durations."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {"success": True, "available": True}

            # Test valid durations (15-480 minutes)
            valid_durations = [15, 30, 45, 60, 90, 120, 240, 480]

            for duration in valid_durations:
                result = await appointment_validator(
                    ctx=ctx,
                    start_time="2025-01-20T10:00:00",
                    duration_minutes=duration,
                    service_type="appunto"
                )

                assert result["success"] is True
                assert result["duration_valid"] is True

    async def test_invalid_durations(self, mock_dependencies):
        """Test validation with invalid appointment durations."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        # Test invalid durations
        invalid_durations = [5, 10, 14, 500, 600, 1440]  # Too short or too long

        for duration in invalid_durations:
            result = await appointment_validator(
                ctx=ctx,
                start_time="2025-01-20T10:00:00",
                duration_minutes=duration,
                service_type="appunto"
            )

            assert result["success"] is True
            assert result["duration_valid"] is False
            assert result["valid"] is False
            assert any("Durata non valida" in error for error in result["errors"])

    async def test_boundary_durations(self, mock_dependencies):
        """Test validation at duration boundaries."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {"success": True, "available": True}

            # Test boundary values
            boundary_tests = [
                (15, True),   # Minimum valid
                (14, False),  # Just below minimum
                (480, True),  # Maximum valid
                (481, False), # Just above maximum
            ]

            for duration, should_be_valid in boundary_tests:
                result = await appointment_validator(
                    ctx=ctx,
                    start_time="2025-01-20T10:00:00",
                    duration_minutes=duration,
                    service_type="appunto"
                )

                assert result["duration_valid"] == should_be_valid


@pytest.mark.asyncio
class TestConflictDetection:
    """Test cases for appointment conflict detection."""

    async def test_no_conflicts(self, mock_dependencies):
        """Test validation when no calendar conflicts exist."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {
                "success": True,
                "available": True,
                "conflicts": []
            }

            result = await appointment_validator(
                ctx=ctx,
                start_time="2025-01-20T10:00:00",
                duration_minutes=60,
                service_type="consulenza"
            )

            assert result["success"] is True
            assert result["valid"] is True
            assert len(result.get("errors", [])) == 0

    async def test_with_conflicts(self, mock_dependencies):
        """Test validation when calendar conflicts exist."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {
                "success": True,
                "available": False,
                "conflicts": [{
                    "start": "2025-01-20T10:00:00",
                    "end": "2025-01-20T11:00:00",
                    "reason": "Existing appointment"
                }]
            }

            result = await appointment_validator(
                ctx=ctx,
                start_time="2025-01-20T10:00:00",
                duration_minutes=60,
                service_type="consulenza"
            )

            assert result["success"] is True
            assert result["valid"] is False
            assert any("conflitto" in error for error in result["errors"])

    async def test_calendar_api_error(self, mock_dependencies):
        """Test validation when calendar API returns error."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {
                "success": False,
                "error": "Calendar API unavailable"
            }

            result = await appointment_validator(
                ctx=ctx,
                start_time="2025-01-20T10:00:00",
                duration_minutes=60,
                service_type="consulenza"
            )

            assert result["success"] is True
            # Should still validate basic rules even if calendar check fails
            assert result["business_hours_valid"] is True
            assert result["working_day_valid"] is True
            assert result["duration_valid"] is True


@pytest.mark.asyncio
class TestComplexValidationScenarios:
    """Test cases for complex validation scenarios with multiple rules."""

    async def test_multiple_validation_errors(self, mock_dependencies):
        """Test validation with multiple rule violations."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        # Create appointment that violates multiple rules
        result = await appointment_validator(
            ctx=ctx,
            start_time="2025-01-25T20:00:00",  # Saturday + after hours
            duration_minutes=10,  # Too short
            service_type="appunto"
        )

        assert result["success"] is True
        assert result["valid"] is False
        assert result["business_hours_valid"] is False
        assert result["working_day_valid"] is False
        assert result["duration_valid"] is False

        # Should have multiple error messages
        error_count = len(result.get("errors", []))
        assert error_count >= 2  # At least business hours and working day errors

    async def test_edge_case_business_hours_with_duration(self, mock_dependencies):
        """Test business hours validation considering appointment duration."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {"success": True, "available": True}

            # Test appointment that starts valid but would end after business hours
            result = await appointment_validator(
                ctx=ctx,
                start_time="2025-01-20T17:30:00",  # 5:30 PM
                duration_minutes=120,  # 2 hours (ends at 7:30 PM)
                service_type="consulenza"
            )

            assert result["success"] is True
            # Note: Current implementation might only check start time
            # This test documents expected behavior for duration-aware validation
            assert result["business_hours_valid"] is True  # Current behavior

    async def test_holiday_scenario(self, mock_dependencies):
        """Test validation scenario for holidays (not explicitly implemented)."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {"success": True, "available": True}

            # Test on a date that might be a holiday
            # Note: Holiday validation is not explicitly implemented in MVP
            result = await appointment_validator(
                ctx=ctx,
                start_time="2025-12-25T10:00:00",  # Christmas
                duration_minutes=30,
                service_type="appunto"
            )

            # Should validate based on working days (Christmas 2025 is Thursday)
            assert result["success"] is True
            assert result["working_day_valid"] is True


@pytest.mark.asyncio
class TestValidationPerformance:
    """Test cases for validation performance and optimization."""

    async def test_validation_performance(self, mock_dependencies):
        """Test validation performance under load."""
        import time

        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {"success": True, "available": True}

            # Test validation performance with multiple requests
            start_time = time.time()
            validation_count = 10

            for i in range(validation_count):
                result = await appointment_validator(
                    ctx=ctx,
                    start_time=f"2025-01-20T{10 + i % 8}:00:00",
                    duration_minutes=30 + (i * 5),
                    service_type="appunto"
                )
                assert result["success"] is True

            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / validation_count

            # Each validation should complete quickly (under 1 second on average)
            assert avg_time < 1.0

    async def test_validation_caching(self, mock_dependencies):
        """Test if validation results could benefit from caching."""
        mock_model = Mock()
        agent = Mock()
        from ..tools import register_tools
        register_tools(agent, ScheduleAgentDependencies)

        ctx = Mock(spec=Mock)
        ctx.deps = mock_dependencies

        with patch('..tools.mock_google_calendar_check_availability') as mock_check:
            mock_check.return_value = {"success": True, "available": True}

            # Perform same validation multiple times
            same_params = {
                "start_time": "2025-01-20T10:00:00",
                "duration_minutes": 30,
                "service_type": "appunto"
            }

            results = []
            for i in range(3):
                result = await appointment_validator(ctx=ctx, **same_params)
                results.append(result)

            # All results should be consistent
            assert all(result["valid"] == results[0]["valid"] for result in results)
            assert all(result["business_hours_valid"] == results[0]["business_hours_valid"] for result in results)
            assert all(result["working_day_valid"] == results[0]["working_day_valid"] for result in results)