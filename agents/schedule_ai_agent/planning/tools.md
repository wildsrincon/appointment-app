"""
Tools Specification for Italian Appointment Scheduling AI Agent

This document defines the essential tools for the schedule_ai_agent implementation.
Only 2-3 core tools are specified to maintain simplicity and focus on MVP functionality.

Philosophy: Single-purpose tools with 1-3 parameters each, basic error handling, and
Google Calendar API integration for Italian professional consulting businesses.
"""

import logging
from typing import Dict, Any, List, Optional, Literal
from pydantic_ai import RunContext
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


# Tool parameter models for validation
class CalendarEventParams(BaseModel):
    """Parameters for Google Calendar event operations."""
    title: str = Field(..., description="Event title in Italian")
    start_time: str = Field(..., description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)")
    duration_minutes: int = Field(30, ge=15, le=480, description="Duration in minutes")
    client_email: Optional[str] = Field(None, description="Client email for notifications")
    client_name: str = Field(..., description="Client name")
    service_type: str = Field(..., description="Type of service (consulting, meeting, etc.)")
    consultant_id: Optional[str] = Field(None, description="Consultant identifier")


class AvailabilityCheckParams(BaseModel):
    """Parameters for availability checking."""
    start_time: str = Field(..., description="Start time in ISO format")
    end_time: str = Field(..., description="End time in ISO format")
    consultant_id: Optional[str] = Field(None, description="Specific consultant to check")
    service_duration: int = Field(30, ge=15, le=480, description="Service duration in minutes")


class ItalianDateTimeParams(BaseModel):
    """Parameters for Italian date/time parsing."""
    text: str = Field(..., description="Italian text containing date/time reference")
    context_date: Optional[str] = Field(None, description="Reference date for relative expressions")
    timezone: str = Field("Europe/Rome", description="Timezone for interpretation")


# Core tool implementations
async def google_calendar_create_event(
    api_key: str,
    client_id: str,
    client_secret: str,
    refresh_token: str,
    calendar_id: str,
    title: str,
    start_time: str,
    duration_minutes: int,
    client_email: Optional[str] = None,
    client_name: str = "",
    service_type: str = "",
    description: str = ""
) -> Dict[str, Any]:
    """
    Standalone function for creating Google Calendar events.

    Args:
        api_key: Google Calendar API key
        client_id: OAuth client ID
        client_secret: OAuth client secret
        refresh_token: OAuth refresh token
        calendar_id: Calendar ID to create event in
        title: Event title
        start_time: ISO format start time
        duration_minutes: Event duration
        client_email: Client email for notifications
        client_name: Client name
        service_type: Type of service
        description: Event description

    Returns:
        Dictionary with event creation result
    """
    # Mock implementation - would use Google Calendar API
    end_time = (datetime.fromisoformat(start_time) +
                timedelta(minutes=duration_minutes)).isoformat()

    event_data = {
        "summary": title,
        "description": f"{description}\n\nCliente: {client_name}\nServizio: {service_type}",
        "start": {"dateTime": start_time, "timeZone": "Europe/Rome"},
        "end": {"dateTime": end_time, "timeZone": "Europe/Rome"},
        "attendees": []
    }

    if client_email:
        event_data["attendees"].append({"email": client_email})

    # In real implementation, this would call Google Calendar API
    # await google_calendar_service.events().insert(calendarId=calendar_id, body=event_data).execute()

    return {
        "success": True,
        "event_id": f"event_{datetime.now().timestamp()}",
        "event_data": event_data,
        "calendar_id": calendar_id,
        "created_at": datetime.now().isoformat()
    }


async def google_calendar_check_availability(
    api_key: str,
    calendar_id: str,
    start_time: str,
    end_time: str
) -> Dict[str, Any]:
    """
    Check calendar availability for time slots.

    Args:
        api_key: Google Calendar API key
        calendar_id: Calendar ID to check
        start_time: ISO format start time
        end_time: ISO format end time

    Returns:
        Dictionary with availability information
    """
    # Mock implementation - would query Google Calendar API
    # In real implementation: events = calendar_service.events().list(...)

    return {
        "success": True,
        "available": True,
        "conflicts": [],
        "busy_slots": [],
        "checked_range": {
            "start": start_time,
            "end": end_time
        }
    }


def parse_italian_datetime(
    text: str,
    reference_date: Optional[str] = None,
    timezone: str = "Europe/Rome"
) -> Dict[str, Any]:
    """
    Parse Italian date/time expressions into structured data.

    Args:
        text: Italian text containing date/time
        reference_date: Reference date for relative expressions
        timezone: Target timezone

    Returns:
        Dictionary with parsed datetime information
    """
    # Simplified parsing logic - would use more sophisticated NLP
    ref_date = datetime.fromisoformat(reference_date) if reference_date else datetime.now()

    # Basic Italian time patterns
    patterns = {
        "oggi": ref_date,
        "domani": ref_date + timedelta(days=1),
        "dopodomani": ref_date + timedelta(days=2),
        "lunedì": ref_date + timedelta(days=(0 - ref_date.weekday() + 7) % 7 or 7),
        "martedì": ref_date + timedelta(days=(1 - ref_date.weekday() + 7) % 7 or 7),
        "mercoledì": ref_date + timedelta(days=(2 - ref_date.weekday() + 7) % 7 or 7),
        "giovedì": ref_date + timedelta(days=(3 - ref_date.weekday() + 7) % 7 or 7),
        "venerdì": ref_date + timedelta(days=(4 - ref_date.weekday() + 7) % 7 or 7),
    }

    # Extract time patterns (simplified)
    time_patterns = {
        r"alle (\d{1,2}):(\d{2})": lambda h, m: f"{h.zfill(2)}:{m}",
        r"alle (\d{1,2})": lambda h: f"{h.zfill(2)}:00"
    }

    parsed_date = ref_date
    parsed_time = "10:00"  # Default time

    # Check for date patterns
    for italian_term, date_offset in patterns.items():
        if italian_term.lower() in text.lower():
            parsed_date = date_offset
            break

    # Simple time extraction (would use regex in real implementation)
    if "14:30" in text or "14 e 30" in text:
        parsed_time = "14:30"
    elif "15:00" in text or "15" in text:
        parsed_time = "15:00"
    elif "9:00" in text or "9" in text:
        parsed_time = "09:00"

    datetime_obj = datetime.combine(
        parsed_date.date(),
        datetime.strptime(parsed_time, "%H:%M").time()
    )

    return {
        "success": True,
        "datetime": datetime_obj.isoformat(),
        "date": parsed_date.date().isoformat(),
        "time": parsed_time,
        "timezone": timezone,
        "confidence": 0.8,  # Would be calculated based on pattern matching
        "original_text": text
    }


# Tool registration functions for agent
def register_tools(agent, deps_type):
    """
    Register all tools with the Pydantic AI agent.

    Args:
        agent: Pydantic AI agent instance
        deps_type: Agent dependencies type
    """

    @agent.tool
    async def google_calendar_operations(
        ctx: RunContext[deps_type],
        operation: Literal["create", "check", "modify", "delete"],
        title: Optional[str] = None,
        start_time: Optional[str] = None,
        duration_minutes: int = 30,
        client_name: str = "",
        client_email: Optional[str] = None,
        service_type: str = "",
        consultant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform Google Calendar operations for appointment management.

        Args:
            operation: Type of calendar operation (create, check, modify, delete)
            title: Event title (required for create/modify)
            start_time: Start time in ISO format (required for create/modify/check)
            duration_minutes: Event duration in minutes
            client_name: Client name
            client_email: Client email for notifications
            service_type: Type of service being scheduled
            consultant_id: Consultant identifier for calendar selection

        Returns:
            Dictionary with operation result and relevant data
        """
        try:
            if operation == "create":
                if not all([title, start_time, client_name]):
                    return {
                        "success": False,
                        "error": "Title, start_time, and client_name required for create operation"
                    }

                # Get calendar ID (business calendar or consultant-specific)
                calendar_id = (consultant_id if consultant_id
                             else ctx.deps.default_calendar_id)

                result = await google_calendar_create_event(
                    api_key=ctx.deps.google_calendar_api_key,
                    client_id=ctx.deps.google_client_id,
                    client_secret=ctx.deps.google_client_secret,
                    refresh_token=ctx.deps.google_refresh_token,
                    calendar_id=calendar_id,
                    title=f"{service_type} - {client_name}" if service_type else title,
                    start_time=start_time,
                    duration_minutes=duration_minutes,
                    client_email=client_email,
                    client_name=client_name,
                    service_type=service_type,
                    description=f"Appuntamento per {service_type}"
                )

                logger.info(f"Calendar event created: {result.get('event_id')}")
                return result

            elif operation == "check":
                if not start_time:
                    return {
                        "success": False,
                        "error": "start_time required for check operation"
                    }

                # Calculate end time for availability check
                end_time = (datetime.fromisoformat(start_time) +
                           timedelta(hours=2)).isoformat()  # Check 2-hour window

                calendar_id = (consultant_id if consultant_id
                             else ctx.deps.default_calendar_id)

                result = await google_calendar_check_availability(
                    api_key=ctx.deps.google_calendar_api_key,
                    calendar_id=calendar_id,
                    start_time=start_time,
                    end_time=end_time
                )

                logger.info(f"Availability checked for {start_time}: {result.get('available')}")
                return result

            else:
                return {
                    "success": False,
                    "error": f"Operation '{operation}' not yet implemented"
                }

        except Exception as e:
            logger.error(f"Calendar operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }

    @agent.tool_plain
    def italian_appointment_parser(
        text: str,
        context_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse Italian natural language for appointment details.

        Args:
            text: Italian text containing appointment request
            context_date: Reference date for relative expressions (default: today)

        Returns:
            Dictionary with parsed appointment information
        """
        try:
            # Parse date/time from Italian text
            datetime_result = parse_italian_datetime(
                text=text,
                reference_date=context_date,
                timezone="Europe/Rome"
            )

            # Extract service type patterns
            service_patterns = {
                "consulenza": "consulenza",
                "appunto": "appunto",
                "riunione": "riunione",
                "incontro": "incontro",
                "visita": "visita",
                "seduta": "seduta"
            }

            detected_service = "generale"
            for pattern, service in service_patterns.items():
                if pattern.lower() in text.lower():
                    detected_service = service
                    break

            # Extract duration hints
            duration = 30  # Default
            if "90" in text or "un'ora e mezza" in text:
                duration = 90
            elif "60" in text or "un'ora" in text:
                duration = 60
            elif "120" in text or "due ore" in text:
                duration = 120

            return {
                "success": True,
                "datetime": datetime_result.get("datetime"),
                "date": datetime_result.get("date"),
                "time": datetime_result.get("time"),
                "service_type": detected_service,
                "duration_minutes": duration,
                "confidence": datetime_result.get("confidence", 0.5),
                "original_text": text
            }

        except Exception as e:
            logger.error(f"Italian parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_text": text
            }

    @agent.tool
    async def appointment_validator(
        ctx: RunContext[deps_type],
        start_time: str,
        duration_minutes: int,
        service_type: str,
        consultant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate appointment against business rules and availability.

        Args:
            start_time: Proposed appointment start time (ISO format)
            duration_minutes: Duration in minutes
            service_type: Type of service
            consultant_id: Consultant identifier (optional)

        Returns:
            Dictionary with validation results
        """
        try:
            # Parse and validate datetime
            appointment_dt = datetime.fromisoformat(start_time)

            # Check business hours (default: 9-18, Monday-Friday)
            business_start = appointment_dt.replace(hour=9, minute=0)
            business_end = appointment_dt.replace(hour=18, minute=0)

            validation_results = {
                "success": True,
                "valid": True,
                "warnings": [],
                "errors": [],
                "business_hours_valid": True,
                "working_day_valid": True,
                "duration_valid": True
            }

            # Validate business hours
            if appointment_dt < business_start or appointment_dt > business_end:
                validation_results["business_hours_valid"] = False
                validation_results["errors"].append(
                    f"Orario non lavorativo. Ufficio aperto 9:00-18:00"
                )
                validation_results["valid"] = False

            # Validate working day (Monday=0, Sunday=6)
            if appointment_dt.weekday() >= 5:  # Saturday (5) or Sunday (6)
                validation_results["working_day_valid"] = False
                validation_results["errors"].append(
                    f"Giorno non lavorativo. Lunedì-Venerdì solo"
                )
                validation_results["valid"] = False

            # Validate duration
            if duration_minutes < 15 or duration_minutes > 480:
                validation_results["duration_valid"] = False
                validation_results["errors"].append(
                    f"Durata non valida. Minimo 15 minuti, massimo 8 ore"
                )
                validation_results["valid"] = False

            # Check calendar availability
            if validation_results["valid"]:
                end_time = (appointment_dt +
                           timedelta(minutes=duration_minutes)).isoformat()

                availability_result = await google_calendar_check_availability(
                    api_key=ctx.deps.google_calendar_api_key,
                    calendar_id=(consultant_id if consultant_id
                               else ctx.deps.default_calendar_id),
                    start_time=start_time,
                    end_time=end_time
                )

                if not availability_result.get("available", True):
                    validation_results["valid"] = False
                    validation_results["errors"].append(
                        "Orario non disponibile - conflitto con altro appuntamento"
                    )

            logger.info(f"Appointment validation completed: {validation_results['valid']}")
            return validation_results

        except Exception as e:
            logger.error(f"Appointment validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "valid": False
            }

    logger.info(f"Registered {len(agent.tools)} tools with schedule_ai_agent")


# Error handling utilities
class AppointmentToolError(Exception):
    """Custom exception for appointment tool failures."""
    pass


async def handle_calendar_error(error: Exception, operation: str) -> Dict[str, Any]:
    """
    Standardized error handling for calendar operations.

    Args:
        error: The exception that occurred
        operation: Description of what was being attempted

    Returns:
        Error response dictionary with Italian messages
    """
    logger.error(f"Calendar error in {operation}: {error}")

    italian_errors = {
        "authentication": "Errore di autenticazione con Google Calendar",
        "permission": "Permessi insufficienti per il calendario",
        "quota": "Limite richieste Google Calendar superato",
        "not_found": "Calendario non trovato",
        "invalid": "Dati non validi per l'operazione"
    }

    error_key = "invalid"
    error_str = str(error).lower()
    for key in italian_errors:
        if key in error_str:
            error_key = key
            break

    return {
        "success": False,
        "error": italian_errors.get(error_key, "Errore sconosciuto del calendario"),
        "error_type": error_key,
        "operation": operation,
        "requires_user_action": error_key in ["authentication", "permission"]
    }


# Testing utilities
def create_test_tools():
    """Create mock tools for development and testing."""
    from pydantic_ai.models.test import TestModel

    async def mock_calendar_operation(operation: str, **kwargs):
        if operation == "create":
            return {"success": True, "event_id": f"test_{operation}_{datetime.now().timestamp()}"}
        elif operation == "check":
            return {"success": True, "available": True}
        return {"success": False, "error": f"Operation {operation} not mocked"}

    def mock_italian_parser(text: str):
        return {
            "success": True,
            "datetime": "2025-01-20T10:00:00",
            "service_type": "consulenza",
            "duration_minutes": 30
        }

    async def mock_validator(**kwargs):
        return {"success": True, "valid": True}

    return {
        "calendar": mock_calendar_operation,
        "parser": mock_italian_parser,
        "validator": mock_validator
    }


# Rate limiting utilities
async def create_calendar_semaphore():
    """Create semaphore for rate limiting Google Calendar API calls."""
    return asyncio.Semaphore(5)  # Max 5 concurrent calendar operations