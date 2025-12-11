"""
Real Google Calendar API integration for Italian Appointment Scheduling AI Agent.

This module provides authentic Google Calendar integration using both OAuth2 flow
and service account authentication for easier setup.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
import json
import os

# Google API imports
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import simple calendar service
try:
    from simple_calendar_service import SimpleGoogleCalendarService
except ImportError:
    SimpleGoogleCalendarService = None

logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_smart_calendar_service():
    """
    Get Google Calendar service using the best available authentication method.
    Tries service account first, then falls back to OAuth.
    """
    # Try service account first (easier and more reliable)
    if SimpleGoogleCalendarService and os.path.exists("service-account.json"):
        try:
            simple_service = SimpleGoogleCalendarService()
            # Test if service account works
            test_result = simple_service.create_event(
                title="Test Event",
                start_time=datetime.now() + timedelta(hours=1),
                duration_minutes=1,
                description="Connection test"
            )
            if test_result.get("success"):
                logger.info("Using service account authentication")
                return simple_service
        except Exception as e:
            logger.warning(f"Service account authentication failed: {e}")

    # Fallback to OAuth
    logger.info("Using OAuth authentication")
    return None


class GoogleCalendarService:
    """Real Google Calendar API service."""

    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        """
        Initialize Google Calendar service with OAuth credentials.

        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            refresh_token: Google OAuth refresh token
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self._service = None
        self._credentials = None

    async def _get_credentials(self) -> Credentials:
        """Get OAuth credentials using refresh token."""
        if self._credentials is None or self._credentials.expired:
            self._credentials = Credentials(
                token=None,  # Will be refreshed
                refresh_token=self.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=SCOPES
            )

            # Refresh the token
            try:
                self._credentials.refresh(Request())
                logger.info("Google Calendar OAuth token refreshed successfully")
            except Exception as e:
                logger.error(f"Failed to refresh Google OAuth token: {e}")
                raise ValueError(
                    f"Failed to authenticate with Google Calendar: {e}\n"
                    "You may need to re-authenticate or check your OAuth credentials"
                )

        return self._credentials

    async def _get_service(self):
        """Get Google Calendar service instance."""
        if self._service is None:
            credentials = await self._get_credentials()
            self._service = build('calendar', 'v3', credentials=credentials)
            logger.info("Google Calendar service initialized")
        return self._service

    async def create_event(
        self,
        title: str,
        start_time: datetime,
        duration_minutes: int = 30,
        description: str = "",
        attendee_emails: Optional[List[str]] = None,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """
        Create a real event in Google Calendar.

        Args:
            title: Event title
            start_time: Start time (datetime object)
            duration_minutes: Duration in minutes
            description: Event description
            attendee_emails: List of attendee emails
            calendar_id: Calendar ID (default: "primary")

        Returns:
            Dictionary with event creation result
        """
        try:
            service = await self._get_service()

            # Calculate end time
            end_time = start_time + timedelta(minutes=duration_minutes)

            # Create event body
            event_body = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Europe/Rome',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Europe/Rome',
                },
                'reminders': {
                    'useDefault': True,
                },
            }

            # Add attendees if provided
            if attendee_emails:
                event_body['attendees'] = [{'email': email} for email in attendee_emails]

            # Create the event
            event = service.events().insert(
                calendarId=calendar_id,
                body=event_body,
                sendUpdates='all'  # Send email notifications to attendees
            ).execute()

            logger.info(f"Created Google Calendar event: {event['id']}")

            return {
                "success": True,
                "event_id": event['id'],
                "html_link": event.get('htmlLink', ''),
                "start_time": event['start']['dateTime'],
                "end_time": event['end']['dateTime'],
                "title": event['summary'],
                "calendar_id": calendar_id,
                "message": f"Evento '{title}' creato con successo nel Google Calendar"
            }

        except HttpError as e:
            error_msg = f"Google Calendar API error: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": e.resp.status
            }
        except Exception as e:
            error_msg = f"Failed to create Google Calendar event: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def check_availability(
        self,
        start_time: datetime,
        duration_minutes: int = 30,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """
        Check availability for a time slot in Google Calendar.

        Args:
            start_time: Start time to check
            duration_minutes: Duration in minutes
            calendar_id: Calendar ID to check

        Returns:
            Dictionary with availability information
        """
        try:
            service = await self._get_service()

            # Calculate time range to check
            end_time = start_time + timedelta(minutes=duration_minutes)
            time_min = start_time.isoformat() + 'Z'
            time_max = end_time.isoformat() + 'Z'

            # Check for events in the time range
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Check if slot is available
            is_available = len(events) == 0

            # Get conflicting events if any
            conflicting_events = []
            for event in events:
                conflicting_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date'))
                })

            logger.info(f"Availability check for {start_time}: {'Available' if is_available else 'Not available'}")

            return {
                "success": True,
                "available": is_available,
                "conflicting_events": conflicting_events,
                "checked_time": start_time.isoformat(),
                "duration_minutes": duration_minutes,
                "calendar_id": calendar_id,
                "message": "Disponibile" if is_available else f"Non disponibile - {len(conflicting_events)} eventi in conflitto"
            }

        except HttpError as e:
            error_msg = f"Google Calendar API error: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": e.resp.status
            }
        except Exception as e:
            error_msg = f"Failed to check availability: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def list_upcoming_events(
        self,
        calendar_id: str = "primary",
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        List upcoming events from Google Calendar.

        Args:
            calendar_id: Calendar ID
            max_results: Maximum number of events to return

        Returns:
            Dictionary with upcoming events
        """
        try:
            service = await self._get_service()

            # Get current time
            now = datetime.utcnow().isoformat() + 'Z'

            # List upcoming events
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Format events
            formatted_events = []
            for event in events:
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'description': event.get('description', ''),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                    'html_link': event.get('htmlLink', '')
                })

            logger.info(f"Listed {len(formatted_events)} upcoming events")

            return {
                "success": True,
                "events": formatted_events,
                "total": len(formatted_events),
                "calendar_id": calendar_id,
                "message": f"Trovati {len(formatted_events)} eventi imminenti"
            }

        except Exception as e:
            error_msg = f"Failed to list events: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }


# Global service instance
_calendar_service: Optional[GoogleCalendarService] = None


def get_calendar_service(
    client_id: str,
    client_secret: str,
    refresh_token: str
) -> GoogleCalendarService:
    """Get or create Google Calendar service instance."""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = GoogleCalendarService(client_id, client_secret, refresh_token)
    return _calendar_service


async def create_google_calendar_event(
    title: str,
    start_time: str,
    duration_minutes: int,
    client_name: str,
    service_type: str,
    description: str = "",
    client_email: Optional[str] = None,
    calendar_id: str = "primary",
    client_id: str = "",
    client_secret: str = "",
    refresh_token: str = ""
) -> Dict[str, Any]:
    """
    Create an event in Google Calendar using the best available authentication method.

    Args:
        title: Event title
        start_time: Start time in ISO format
        duration_minutes: Event duration in minutes
        client_name: Client name
        service_type: Type of service
        description: Event description
        client_email: Client email for notifications
        calendar_id: Calendar ID
        client_id: Google OAuth client ID
        client_secret: Google OAuth client secret
        refresh_token: Google OAuth refresh token

    Returns:
        Dictionary with event creation result
    """
    try:
        # Parse start time
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))

        # Try smart service first (service account preferred)
        smart_service = get_smart_calendar_service()
        if smart_service:
            result = smart_service.create_event(
                title=title,
                start_time=start_dt,
                duration_minutes=duration_minutes,
                description=description,
                calendar_id=calendar_id
            )
            logger.info("Created event using service account authentication")
            return result

        # Fallback to OAuth
        calendar_service = get_calendar_service(client_id, client_secret, refresh_token)
        attendee_emails = [client_email] if client_email else None

        result = await calendar_service.create_event(
            title=title,
            start_time=start_dt,
            duration_minutes=duration_minutes,
            description=description,
            attendee_emails=attendee_emails,
            calendar_id=calendar_id
        )

        logger.info("Created event using OAuth authentication")
        return result

    except Exception as e:
        error_msg = f"Failed to create Google Calendar event: {e}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }


async def check_google_calendar_availability(
    start_time: str,
    end_time: str,
    calendar_id: str = "primary",
    client_id: str = "",
    client_secret: str = "",
    refresh_token: str = ""
) -> Dict[str, Any]:
    """
    Check availability in Google Calendar using the best available authentication method.

    Args:
        start_time: Start time in ISO format
        end_time: End time in ISO format
        calendar_id: Calendar ID
        client_id: Google OAuth client ID
        client_secret: Google OAuth client secret
        refresh_token: Google OAuth refresh token

    Returns:
        Dictionary with availability result
    """
    try:
        # Parse start time
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))

        # Calculate duration
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration_minutes = int((end_dt - start_dt).total_seconds() / 60)

        # Try smart service first (service account preferred)
        smart_service = get_smart_calendar_service()
        if smart_service:
            result = smart_service.check_availability(
                start_time=start_dt,
                duration_minutes=duration_minutes,
                calendar_id=calendar_id
            )
            logger.info("Checked availability using service account authentication")
            return result

        # Fallback to OAuth
        calendar_service = get_calendar_service(client_id, client_secret, refresh_token)

        result = await calendar_service.check_availability(
            start_time=start_dt,
            duration_minutes=duration_minutes,
            calendar_id=calendar_id
        )

        logger.info("Checked availability using OAuth authentication")
        return result

    except Exception as e:
        error_msg = f"Failed to check Google Calendar availability: {e}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }